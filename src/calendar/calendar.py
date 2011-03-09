import cream.ipc
import cream.extensions

from calendar.database import DatabaseManager
from calendar.backends import CalendarManager

from calendar.event import Event

@cream.extensions.register
class CalendarExtension(cream.extensions.Extension, cream.ipc.Object):

    __ipc_signals__ = {
        'event_added': ('a{sv}', 'org.cream.PIM.Calendar'),
        'event_deleted': ('a{sv}', 'org.cream.PIM.Calendar'),
        'event_updated': ('a{sv}', 'org.cream.PIM.Calendar'),
        'calendar_added': ('a{sv}', 'org.cream.PIM.Calendar'),
        }

    def __init__(self, extension_interface):

        cream.extensions.Extension.__init__(self, extension_interface)
        cream.ipc.Object.__init__(self,
            'org.cream.PIM',
            '/org/cream/PIM/Calendar'
        )

        self.calendars = CalendarManager()

        self.database = DatabaseManager()
        self.database.connect('event-added', self.on_event_added)
        self.database.connect('event-deleted', self.on_event_deleted)
        self.database.connect('event-updated', self.on_event_updated)

        for calendar in self.list_calendars():
            self.calendars.add_calendar(calendar)

        self.calendars.connect('calendar-added', lambda _, calendar: self.on_calendar_added(calendar))

        for calendar in self.calendars.calendars:
            self.on_calendar_added(calendar)


    @cream.ipc.method('', '')
    def query(self, query):
        pass


    @cream.ipc.method('', 'aa{sv}')
    def list_calendars(self):
        """
        Returns a list of all available calendars.
        """

        return self.database.get_calendars()


    @cream.ipc.method('a{sv}i', '')
    def add_event(self, event, calendar_id):
        """
        Add an event to a calendar specified by ``calendar_id``.

        :type event: dict
        :type calendar_id: int
        """

        event = Event(**event)
        self.database.add_event(event, calendar_id)


    @cream.ipc.method('a{sv}', '')
    def delete_event(self, event):
        """
        Delete an event which has to be unique specified by ``event``.

        :type event: dict
        """

        event = Event(**event)
        self.database.delete_event(event)


    @cream.ipc.method('a{sv}a{sv}', '')
    def update_event(self, old_event, new_event):
        """
        Update an event specified be ``event``.

        :type event: dict
        """

        old_event = Event(**old_event)
        new_event = Event(**new_event)
        self.database.update_event(old_event, new_event)


    def on_event_added(self, sender, event):

        self.emit_signal('event_added', event.to_dbus_dict())
        if not event.synced:
            self.calendars.add_event(event, event.calendar_id)


    def on_event_deleted(self, sender, event):

        self.emit_signal('event_deleted', event.to_dbus_dict())
        if not event.synced:
            self.calendars.delete_event(event, event.calendar_id)


    def on_event_updated(self, sender, old_event, new_event):

        self.emit_signal('event_updated', event.to_dbus_dict())
        if not event.synced:
            self.calendars.update_event(old_event, new_event, new_event.calendar_id)


    def on_calendar_added(self, calendar):
        calendar.connect('event-added',
            lambda _, event, id: self.database.add_event(event, id))
        calendar.connect('event-deleted',
            lambda _, event: self.database.delete_event(event))
        calendar.connect('event-updated',
            lambda _, old_event, new_event: self.database.update_event(old_event, new_event))

        self.emit_signal('calendar_added', calendar.to_dict())
