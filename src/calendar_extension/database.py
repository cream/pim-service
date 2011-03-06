import os

from models import *

from calendar_extension.util import generate_uid, Event as _Event, Calendar as _Calendar, \
                                     convert_to_datetime

class Database(object):

    def __init__(self, path):

        database_path = os.path.join(path, 'events.sqlite')
        metadata.bind = 'sqlite:///{0}'.format(database_path)
        metadata.bind.echo = False
        setup_all(True)


    def query(self, query):

        uid = query.pop('uid', None)
        if uid:
            event = Event.get_by(uid=uid)
            if event:
                return [event.to_internal().to_dbus()]

        events = Event.query
        for key, value in query.iteritems():
            if key == 'start':
                events = events.filter(Event.start > convert_to_datetime(value))
            elif key == 'end':
                events = events.filter(Event.end < convert_to_datetime(value))
            elif key in ['title', 'location', 'description']:
                events = events.filter(getattr(Event, key).contains(value))
            elif key == 'synced':
                events = events.filter_by(synced=value)
            elif key == 'deleted':
                events = events.filter_by(deleted=value)

        return [event.to_internal().to_dbus() for event in events]


    def get_calendars(self):

        return [calendar.to_internal() for calendar in Calendar.query.all()]


    def set_synced(self, uid, synced):

        event = Event.get_by(uid=uid):
        event.synced = synced
        session.commit()


    def add_calendar(self, calendar):

        cal = Calendar(
                name = calendar.name,
                source = calendar.source,
                type = calendar.type,
        )

        if calendar.uid:
            cal.uid = calendar.uid
        else:
            cal.uid = generate_uid()

        session.commit()

        return cal.to_internal()


    def remove_calendar(self, uid):

        calendar = Calendar.get_by(uid=uid)
        if calendar:
            calendar.delete()

        session.commit()

        return calendar.to_internal()


    def update_calendar(self, uid, fields):

        calendar = Calendar.get_by(uid=uid)
        if calendar:
            for key, value in fields.iteritems():
                setattr(calendar, key, value)

        session.commit()

        return calendar.to_internal()


    def add_event(self, event, calendar_uid):

        calendar = Calendar.get_by(uid=calendar_uid)

        ev = Event(
                title = event.title,
                description = event.description,
                start = event.start,
                end = event.end,
                location = event.location,
                synced = event.synced,
                deleted = event.deleted,
                calendar = calendar
        )

        if event.uid:
            ev.uid = event.uid
        else:
            ev.uid = generate_uid()

        session.commit()

        return ev.to_internal()


    def remove_event(self, uid, synced=False):

        event = Event.get_by(uid=uid)
        if not event:
            return

        event.deleted = True
        if synced:
            # only delete when already deleted in the backend
            event.delete()

        session.commit()

        return event.to_internal()


    def update_event(self, uid, fields, synced=False):

        event = Event.get_by(uid=uid)
        if not event:
            return

        for key, value in fields.iteritems():
            setattr(event, key, value)

        event.synced = synced
        session.commit()

        return event.to_internal()


    def sync_events(self, events, calendar_uid):

        calendar = Calendar.get_by(uid=calendar_uid)

        for db_event in calendar.events:
            for event in events:
                if db_event.uid == event.uid:
                    break
            else:
                self.remove_event(event.uid, synced=True)

        for event in events:
            db_event = Event.get_by(uid=event.uid)
            if db_event is None:
                event.synced = True
                self.add_event(event, calendar_uid)
            elif db_event.to_internal() != event:
                self.update_event(event.uid, event.to_dict(), synced=True)
