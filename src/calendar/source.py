import gobject


class CalendarSource(gobject.GObject):

    __gsignals__ = {
        'event-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_INT)),
        'event-deleted': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'event-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))
    }

    def __init__(self, name, id, type, source):

        gobject.GObject.__init__(self)

        self.name = name
        self.id = id
        self.type = type
        self.source = source


    def add_event(self, event):
        """
        Add an event to the source. Should not emit a signal.
        """


    def delete_event(self, event):
        """
        Delete an event. Should not emit a signal.
        """


    def update_event(self, old_event, new_event):
        """
        Update an event. Should not emit a signal.
        """


    def to_dict(self):

        return {
            'name': self.name,
            'id': self.id,
            'type': self.type,
            'source': self.source
        }
