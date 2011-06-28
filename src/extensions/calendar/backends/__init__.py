import gobject

from extensions.calendar.util import to_unicode


class BackendError(Exception):
    pass



class CalendarSource(gobject.GObject):
    type = None

    __gsignals__ = {
        'source-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'calendar-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'calendar-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'calendar-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-synced': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING,)),
    }

    def __init__(self, uid, data, calendars):

        gobject.GObject.__init__(self)

        self.uid = uid
        self.data = data

        # These are calendars stored in the database
        self._calendars = calendars

        self.calendar_instances = {}



    @property
    def calendars(self):
        return self.calendar_instances.itervalues()


    def _add_calendar_instance(self, calendar_instance):

        self.calendar_instances[calendar_instance.uid] = calendar_instance

        calendar_instance.connect('event-added', self.on_event_added)
        calendar_instance.connect('event-removed', self.on_event_removed)
        calendar_instance.connect('event-updated', self.on_event_updated)
        calendar_instance.connect('event-synced', self.on_event_synced)

        self.emit('calendar-added', calendar_instance.uid, calendar_instance)


    def add_calendar(self, uid, name):
        """
        Add a calendar to the backend.
        Returns the calendar
        """


    def remove_calendar(self):
        pass


    def update_calendar(self):
        pass


    def on_event_added(self, calendar, uid, event):

        self.emit('event-added', calendar, uid, event)


    def on_event_removed(self,  calendar, uid, event):

        self.emit('event-removed', calendar, uid, event)


    def on_event_updated(self, calendar, uid, event):

        self.emit('event-updated', calendar, uid, event)


    def on_event_synced(self, calendar, uid):

        self.emit('event-synced', calendar, uid)



class Calendar(gobject.GObject):

    __gsignals__ = {
        'event-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-synced': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }

    def __init__(self, uid, name):

        gobject.GObject.__init__(self)

        self.uid = uid
        self.name = to_unicode(name)


    def to_dict(self):

        return {
            'uid': self.uid,
            'name': self.name
        }


    def add_event(self, event):
        """
        Add an event to the backend. Returns ``True`` if the operation succeded,
        else False. Should not emit a signal.
        """


    def remove_event(self, uid):
        """
        Remove an event from the backend. Returns ``True`` if the operation succeded,
        else False. Should not emit a signal.
        """


    def update_event(self, uid, fields):
        """
        Update an event. Returns ``True`` if the operation succeded, else False.
        Should not emit a signal.
        """


    def get_events(self):
        """
        Returns all events in the calendar.
        """

    def sync_events(self, events):
        """
        Retrieves events from the database to be synced with the backend.
        """
