import gobject

from models import *

from calendar.event import Event as CalendarEvent


class DatabaseManager(gobject.GObject):

    __gsignals__ = {
        'event-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'event-deleted': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'event-updated': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT)),
    }

    def __init__(self):

        gobject.GObject.__init__(self)

        metadata.bind = u'sqlite:///events.sqlite'
        metadata.bind.echo = False
        setup_all(True)


    def query_event(self, event):

        return Event.get_by(
                    title = event.title,
                    description = event.description,
                    start = event.start,
                    end = event.end,
                    location = event.location
                )


    def get_calendars(self):

        return [calendar.to_dict() for calendar in Calendar.query.all()]


    def add_event(self, event, calendar_id):

        calendar = Calendar.get_by(id=calendar_id)

        if self.query_event(event):
            # don't add the same event twice
            return

        event = Event(
                title = event.title,
                description = event.description,
                start = event.start,
                end = event.end,
                location = event.location,
                synced = event.synced,
                calendar = calendar)

        session.commit()

        self.emit('event-added', CalendarEvent(**event.to_dict()))


    def delete_event(self, event):

        event = self.query_event(event)
        if not event:
            return

        self.emit('event-deleted', CalendarEvent(**event.to_dict()))

        event.delete()
        session.commit()


    def update_event(self, old_event, new_event):

        event = self.query_event(old_event)
        if not event:
            return

        event.title = new_event.title
        event.description = new_event.description
        event.start = new_event.start
        event.end = new_event.end
        event.location = new_event.location
        event.synced = new_event.synced

        session.commit()

        self.emit('event-updated', old_event, CalendarEvent(**event.to_dict()))
