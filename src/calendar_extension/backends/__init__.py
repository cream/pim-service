import gobject


class CalendarBackend(gobject.GObject):

    __gsignals__ = {
        'event-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)),
        'event-synced': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
    }

    def __init__(self, uid, name, type, source):

        gobject.GObject.__init__(self)


        self.uid = uid
        self.name = name
        self.type = type
        self.source = source


    def to_dict(self):

        return {
            'uid': self.uid,
            'name': self.name,
            'type': self.type,
            'source': self.source
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
