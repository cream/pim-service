import gobject

from calendar_extension.database import Database
from calendar_extension.calendars import Calendars

from calendar_extension.backends.ical import IcalBackend
from calendar_extension.backends.evo import EvolutionBackend

BACKENDS = {
    'icalendar': IcalBackend,
    'evolution': EvolutionBackend
}

class EventManager(gobject.GObject):

    __gsignals__ = {
        'event-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'calendar-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
    }

    def __init__(self, path):

        gobject.GObject.__init__(self)

        self.path = path

        self.database = Database(path)

        self.calendars = {}

        for calendar in self.database.get_calendars():
            backend = BACKENDS.get(calendar.type)
            backend_instance = backend(**calendar.to_dict())

            self.calendars[calendar.uid] = backend_instance

            backend_instance.connect('event-added', self.on_event_added)
            backend_instance.connect('event-removed', self.on_event_removed)
            backend_instance.connect('event-updated', self.on_event_updated)
            backend_instance.connect('event-synced', self.on_event_synced)

            events = backend_instance.get_events()
            self.database.sync_events(events, calendar.uid)

            self.emit('calendar-added', calendar_uid, calendar)

        for uid, calendar in self.calendars.iteritems():
            unsynced_events = self.database.query({'synced': False})
            calendar.sync_events(unsynced_events)


    def query(self, query):

        return self.database.query(query)


    def get_calendars(self):

        return [calendar.to_dict() for calendar in self.calendars.itervalues()]


    def add_calendar(self, calendar):

        calendar = self.database.add_calendar(calendar)
        self.calendars.add_calendar(calendar)


    def add_event(self, event, calendar_uid):

        event = self.database.add_event(event, calendar_uid)

        calendar = self.calendars.get(calendar_uid)
        synced = calendar.add_event(event)
        self.database.set_synced(synced)

        self.emit('event-added', event.uid, event)


    def remove_event(self, uid):

        event = self.database.remove_event(uid)

        calendar = self.calendars.get(event.calendar_uid)
        synced = calendar.remove_event(uid)
        self.database.set_synced(synced)

        self.emit('event-removed', uid, event)


    def update_event(self, uid, fields):

        event = self.database.update_event(uid, fields)

        calendar = self.calendars.get(event.calendar_uid)
        synced = calendar.update_event(uid, fields)
        self.database.set_synced(synced)

        self.emit('event-updated', uid, event)


    def on_event_added(self, calendar, uid, event):

        event.synced = True
        event.uid = uid
        event = self.database.add_event(event, calendar.uid)

        self.emit('event-added', event.uid, event)


    def on_event_removed(self, calendar, uid, event):

        event = self.database.remove_event(uid, synced=True)

        self.emit('event-removed', uid, event)


    def on_event_updated(self, calendar, uid, fields):

        event = self.database.update_event(uid, fields, synced=True)

        self.emit('event-updated', uid, event)


    def on_event_synced(self, calendar, uid, synced):

        self.database.set_synced(uid, synced)
