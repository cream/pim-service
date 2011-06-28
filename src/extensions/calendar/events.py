import gobject

from extensions.calendar.database import Database
from extensions.calendar.backends import CalendarSource, BackendError

import extensions.calendar.backends.ical
import extensions.calendar.backends.evo
import extensions.calendar.backends.gcal


def get_source_for_type(type):

    for source in CalendarSource.__subclasses__():
        if source.type == type:
            return source


class EventManager(gobject.GObject):

    __gsignals__ = {
        'event-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'calendar-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'calendar-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'calendar-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
    }

    def __init__(self, path):

        gobject.GObject.__init__(self)

        self.path = path

        self.database = Database(path)

        self.sources = {}

        for source in self.database.get_sources():
            self.init_source(source, source.data)


    def query(self, query):

        return self.database.query(query)


    def get_calendars(self):

        calendars = []
        for calendar in self.database.get_calendars():
            calendars.append(calendar.to_dict())
        return calendars


    def add_source(self, type, data):

        source = self.database.add_source(type, data)
        if not source.uid in self.sources:
            self.init_source(source, data)

        return source


    def add_calendar(self, source_uid, name):

        calendar = self.database.add_calendar(source_uid, name)

        if calendar:
            source = self.sources[source_uid]
            source.add_calendar(calendar.uid, calendar.name)

            return calendar


    def init_source(self, source, data):

        if not source.uid in self.sources:
            cal_source = get_source_for_type(source.type)(source.uid, data,
                                                          source.calendars)
            self.sources[source.uid] = cal_source

            cal_source.connect('source-updated', self.on_source_updated)
            cal_source.connect('calendar-added', self.on_calendar_added)
            cal_source.connect('calendar-removed', self.on_calendar_removed)
            cal_source.connect('calendar-updated', self.on_calendar_updated)
            cal_source.connect('event-added', self.on_event_added)
            cal_source.connect('event-removed', self.on_event_removed)
            cal_source.connect('event-updated', self.on_event_updated)
            cal_source.connect('event-synced', self.on_event_synced)


    def add_event(self, event, calendar_uid):

        event = self.database.add_event(event, calendar_uid)

        calendar = self._get_calendar_for_uid(calendar_uid)
        synced = calendar.add_event(event)
        self.database.set_synced(synced)

        self.emit('event-added', event.uid, event)


    def remove_event(self, uid):

        event = self.database.remove_event(uid)

        calendar = self._get_calendar_for_uid(event.calendar_uid)
        synced = calendar.remove_event(uid)
        self.database.set_synced(synced)

        self.emit('event-removed', uid, event)


    def update_event(self, uid, fields):

        event = self.database.update_event(uid, fields)

        calendar = self._get_calendar_for_uid(event.calendar_uid)
        synced = calendar.update_event(uid, fields)
        self.database.set_synced(synced)

        self.emit('event-updated', uid, event)



    def on_source_updated(self, source, uid, fields):

        self.database.update_source(uid, fields)


    def on_calendar_added(self, source, calendar_uid, calendar):

        self.database.add_calendar(source.uid, calendar.name, calendar_uid)

        events = calendar.get_events()
        self.database.sync_events(events, calendar_uid)

        unsynced_events = self.database.query({'synced': False,
                                               'calendar_uid': calendar.uid})
        calendar.sync_events(unsynced_events)

        self.emit('calendar-added', calendar_uid, calendar)


    def on_calendar_removed(self, source, uid, calendar):

        #self.database.remove_calendar(calendar) TODO

        self.emit('calendar-removed', uid, calendar)


    def on_calendar_updated(self, source, uid, calendar):

        #self.database.update_calendar(calendar) TODO

        self.emit('calendar-updated', uid, calendar)


    def on_event_added(self, source, calendar, uid, event):

        event.synced = True
        event.uid = uid
        event = self.database.add_event(event, calendar.uid)

        self.emit('event-added', event.uid, event)


    def on_event_removed(self, source, calendar, uid, event):

        event = self.database.remove_event(uid, synced=True)

        self.emit('event-removed', uid, event)


    def on_event_updated(self, source, calendar, uid, fields):

        event = self.database.update_event(uid, fields, synced=True)

        self.emit('event-updated', uid, event)


    def on_event_synced(self, source, calendar, uid):

        self.database.set_synced(uid, True)
