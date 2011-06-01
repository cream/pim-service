import os
import gobject
import icalendar

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from calendar_extension.backends import CalendarBackend
from calendar_extension.util import Event


class IcalBackend(CalendarBackend, FileSystemEventHandler):

    def __init__(self, *args, **kwargs):

        CalendarBackend.__init__(self, *args, **kwargs)
        FileSystemEventHandler.__init__(self)

        self.timeout_id = None

        with open(self.source) as file_handle:
            self.calendar = icalendar.Calendar.from_string(file_handle.read())

        self.observer = Observer()
        self.watch = self.observer.schedule(self, os.path.dirname(self.source))
        self.observer.start()


    def _activate_observer(self):

        def add_handler():
            self.observer.add_handler_for_watch(self, self.watch)
            return False

        # add a timeout to prevent event from being triggered to early
        gobject.timeout_add(1000, add_handler)

    def _deactivate_observer(self):

        if self.observer._handlers[self.watch]:
            self.observer.remove_handler_for_watch(self, self.watch)


    def _save(self):

        self._deactivate_observer()
        with open(self.source, 'w') as file_handle:
            file_handle.write(self.calendar.as_string())
        self._activate_observer()


    def on_modified(self, event):

        if event.src_path.endswith('~'):
            src_path = event.src_path[:-1]
        else:
            src_path = event.src_path

        if not src_path == self.source:
            return

        # the modified event is triggered twice, so cancel the first call to
        # update_calendar
        if self.timeout_id:
            gobject.source_remove(self.timeout_id)

        self.timeout_id = gobject.timeout_add(1000, self.update)


    def update(self):

        old_calendar = self.calendar
        with open(self.source) as file_handle:
            self.calendar = icalendar.Calendar.from_string(file_handle.read())

        for old_event in old_calendar.walk('VEVENT'):
            for new_event in self.calendar.walk('VEVENT'):
                if old_event['uid'] == new_event['uid']:
                    break
            else:
                event = Event.from_ical(old_event.as_string(), self.uid)
                event.synced = True
                self.emit('event-removed', event.uid, event)


        for new_event in self.calendar.walk('VEVENT'):
            for old_event in old_calendar.walk('VEVENT'):
                if old_event['uid'] == new_event['uid']:
                    n_event = Event.from_ical(new_event.as_string(), self.uid)
                    old_event = Event.from_ical(old_event.as_string(), self.uid)
                    if n_event != old_event:
                        self.emit('event-updated', n_event.uid, n_event.to_dict())

                    break
            else:
                event = Event.from_ical(new_event.as_string(), self.uid)
                event.synced = True
                self.emit('event-added', event, self.uid)



    def add_event(self, event, save=True):

        ev = icalendar.Event()
        ev.add('summary', event.title)
        ev.add('description', event.description)
        ev.add('dtstart', event.start)
        ev.add('dtend', event.end)
        ev.add('location', event.location)
        ev['uid'] = event.uid

        self.calendar.add_component(ev)
        if save:
            self._save()

        return True


    def remove_event(self, uid, save=True):

        cal = icalendar.Calendar()
        for component in self.calendar.walk():
            if component.get('uid', None) == uid:
                pass
            else:
                cal.add_component(component)

        self.calendar = cal
        if save:
            self._save()

        return True


    def update_event(self, uid, fields, save=True):

        cal = icalendar.Calendar()
        for component in self.calendar.walk():
            if component.get('uid', None) == uid:
                for key, value in fields.iteritems():
                    if key == 'title':
                        component['summary'] = value
                    else:
                        if key in component:
                            component[key] = value
            cal.add_component(component)

        self.calendar = cal
        if save:
            self._save()

        return True


    def get_events(self):

        return [Event.from_ical(event.as_string(), self.uid) for event in self.calendar.walk('VEVENT')]



    def sync_events(self, events):

        for event in events:
            if event.deleted:
                synced = self.remove_event(event.uid, save=False)
                if synced:
                    self.emit('event-synced', event.uid)

            for cal_event in self.calendar.walk('VEVENT'):
                if event.uid == cal_event['uid']:
                    cal_event = Event.from_ical(cal_event.as_string(), self.uid)
                    if event != cal_event:
                        synced = self.update_event(event.uid, event.to_dict(), save=False)
                        if synced:
                            self.emit('event-synced', event.uid)
                    break
            else:
                synced = self.add_event(event, save=False)
                if synced:
                    self.emit('event-synced', event.uid)


        self._save()