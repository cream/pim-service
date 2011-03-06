import os
import gobject
import icalendar

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from calendar.source import CalendarSource
from calendar.event import Event

def are_equal(event1, event2):

    if event1['summary'] == event2['summary'] and \
        event1['description'] == event2['description'] and \
        event1['dtstart'].dt == event2['dtstart'].dt and \
        event1['dtend'].dt == event2['dtend'].dt and \
        event1['location'] == event2['location']:
        return True
    else:
        return False

def diff_calendar(old, new):

    old_components = [comp for comp in old.walk('VEVENT')]
    new_components = [comp for comp in new.walk('VEVENT')]

    old_components.sort(key=lambda comp: comp['dtstart'].dt)
    new_components.sort(key=lambda comp: comp['dtstart'].dt)

    added_components = []
    deleted_components = []

    for old_comp in old_components:
        for new_comp in new_components:
            if are_equal(old_comp, new_comp):
                break
        else:
            deleted_components.append(old_comp)

    for new_comp in new_components:
        for old_comp in old_components:
            if are_equal(new_comp, old_comp):
                break
        else:
            added_components.append(new_comp)

    return added_components, deleted_components



class ICalendarSource(CalendarSource, FileSystemEventHandler):

    def __init__(self, name, id, type, source):

        CalendarSource.__init__(self, name, id, type, source)

        self.icalendar_file = source
        self.calendar = None
        self.timeout_id = None

        self.observer = Observer()
        self.watch = self.observer.schedule(self, os.path.dirname(self.icalendar_file))
        self.observer.start()

        self._read()


    def on_modified(self, event):

        if not event.src_path == self.icalendar_file:
            return

        # the modified event is triggered twice, so cancel the first call to
        # update_calendar
        if self.timeout_id:
            gobject.source_remove(self.timeout_id)

        self.timeout_id = gobject.timeout_add(1000, self.update_calendar)


    def update_calendar(self):

        old_calendar = self.calendar
        self._read()
        added, deleted = diff_calendar(old_calendar, self.calendar)

        for added_event in added:
            event = Event.from_ical(added_event.as_string())
            event.synced = True
            self.emit('event-added', event, self.id)
        for deleted_event in deleted:
            event = Event.from_ical(deleted_event.as_string())
            event.synced = True
            self.emit('event-deleted', event)

        return False


    def _deactivate_observer(self):
            self.observer.remove_handler_for_watch(self, self.watch)

    def _activate_observer(self):
        def add_handler():
            self.observer.add_handler_for_watch(self, self.watch)
            return False

        gobject.timeout_add(1000, add_handler)


    def _save(self):

        with open(self.icalendar_file, 'w') as file_handle:
            file_handle.write(self.calendar.as_string())



    def _read(self):
        self._deactivate_observer()
        with open(self.icalendar_file) as file_handle:
            self.calendar = icalendar.Calendar.from_string(file_handle.read())
        self._activate_observer()


    def _get_event(self, event):

        for component in self.calendar.walk('VEVENT'):
            if component['summary'] == event.summary and \
                component['description'] == event.description and \
                component['dtstart'].dt == event.start and \
                component['dtend'].dt == event.end and \
                component['location'] == event.location:
                return component


    def add_event(self, event):

        ev = icalendar.Event()
        ev.add('summary', event.title)
        ev.add('description', event.description)
        ev.add('dtstart', event.start)
        ev.add('dtend', event.end)
        ev.add('location', event.location)

        self.calendar.add_component(ev)

        self._save()


    def delete_event(self, event):

        cal = icalendar.Calendar()
        for component in self.calendar.walk():
            if component.name == 'VEVENT':
                if component['summary'] != event.summary:
                    cal.add_component(component)
            else:
                cal.add_component(component)

        self.calendar = cal
        self._save()


    def update_event(self, old_event, new_event):

        event = self._get_event(old_event)

        event['summary'] = new_event.title
        event['description'] = new_event.description
        event['dtstart'] = new_event.start
        event['dtend'] = new_event.end
        event['location'] = new_event.location

        self._save()
