import cream.ipc
import cream.extensions

from calendar_extension.events import EventManager
from calendar_extension.util import Event, Calendar

@cream.extensions.register
class CalendarExtension(cream.extensions.Extension, cream.ipc.Object):

    __ipc_signals__ = {
        'event_added': ('sa{sv}', 'org.cream.PIM.Calendar'),
        'event_removed': ('sa{sv}', 'org.cream.PIM.Calendar'),
        'event_updated': ('sa{sv}', 'org.cream.PIM.Calendar'),
        'calendar_added': ('sa{sv}', 'org.cream.PIM.Calendar'),
        'calendar_removed': ('sa{sv}', 'org.cream.PIM.Calendar'),
        'calendar_updated': ('sa{sv}', 'org.cream.PIM.Calendar'),
    }


    def __init__(self, extension_interface):

        cream.extensions.Extension.__init__(self, extension_interface)
        cream.ipc.Object.__init__(self,
            'org.cream.PIM',
            '/org/cream/PIM/Calendar'
        )


        self.events_manager = EventManager(extension_interface.context.get_path())

        self.events_manager.connect('event-added', self.on_event_added)
        self.events_manager.connect('event-removed', self.on_event_removed)
        self.events_manager.connect('event-updated', self.on_event_updated)
        self.events_manager.connect('calendar-added', self.on_calendar_added)
        self.events_manager.connect('calendar-removed', self.on_calendar_removed)
        self.events_manager.connect('calendar-updated', self.on_calendar_updated)


    @cream.ipc.method('a{sv}', 'aa{sv}')
    def query(self, query):
        """
        Query the database. Return all events which match the query dict ``query``.

        :type query: dict
        """
        return self.events_manager.query(query)


    @cream.ipc.method('', 'aa{sv}')
    def get_calendars(self):
        """
        Returns a list of all available calendars.
        """
        return self.events_manager.get_calendars()


    @cream.ipc.method('a{sv}', '')
    def add_calendar(self, calendar):
        """
        Add a calendar specified by ``calendar``.

        :type calendar: dict
        """

        calendar = Calendar(**calendar)
        self.events_manager.add_calendar(calendar)


    @cream.ipc.method('a{sv}i', '')
    def add_event(self, event, calendar_uid):
        """
        Add an event to a calendar specified by ``calendar_uid``.

        :type event: dict
        :type calendar_uid: int
        """

        event = Event(**event)
        self.events_manager.add_event(event, calendar_uid)


    @cream.ipc.method('s', '')
    def remove_event(self, uid):
        """
        Remove the event specified by ``uid``.

        :type event: dict
        """
        self.events_manager.remove_event(uid)


    @cream.ipc.method('sa{sv}', '')
    def update_event(self, uid, fields):
        """
        Update an event specified by ``uid`` by setting the fields provided by
        ``fields``.

        :type uid: string
        :type fields: dict
        """
        self.events_manager.update_event(uid, fields)



    def on_event_added(self, source, uid, event):

        self.emit_signal('event_added', uid, event.to_dbus())


    def on_event_removed(self, source, uid, event):

        self.emit_signal('event_removed', uid, event.to_dbus())


    def on_event_updated(self, source, uid, event):

        self.emit_signal('event_updated', uid, event.to_dbus())


    def on_calendar_added(self, source, calendar_uid, calendar):

        self.emit_signal('calendar_added', calendar_uid, calendar.to_dict())


    def on_calendar_removed(self, source, calendar_uid, calendar):

        self.emit_signal('calendar_removed', calendar_uid, calendar.to_dict())


    def on_calendar_updated(self, source, calendar_uid, calendar):

        self.emit_signal('calendar_updated', calendar_uid, calendar.to_dict())
