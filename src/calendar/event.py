import time
import datetime

import icalendar
from icalendar import vDDDTypes, vRecur


class Event(object):
    """
    An internal representation of an event.
    """

    def __init__(self, title, description, start, end, location, recurrence=None, id=0, synced=False, calendar_id=0, **kwargs):

        self.title = title
        self.description = description
        self.start = start
        self.end = end
        self.location = location
        self.recurrence = recurrence
        self.id = id
        self.synced = synced
        self.calendar_id = calendar_id

        if not isinstance(start, datetime.datetime):
            self.start = datetime.datetime.fromtimestamp(start)
        if not isinstance(end, datetime.datetime):
            self.end = datetime.datetime.fromtimestamp(end)


    @classmethod
    def from_ical(self, ical):
        """
        Create an event from an ical string.
        """

        event = icalendar.Event.from_string(ical)

        title = event.get('summary', None)
        description = event.get('description', None)
        start = event.get('dtstart', None)
        end = event.get('dtend', None)
        location = event.get('location', None)
        recurrence = event.get('rrule', None)

        return Event(
            title = str(title),
            description = str(description),
            start = vDDDTypes.from_ical(start.ical()) if start else None,
            end = vDDDTypes.from_ical(end.ical()) if end else None,
            location = str(location),
            recurrence = vRecur.from_ical(recurrence.ical()) if recurrence else None
        )


    def to_dict(self):

        return {
            'title': self.title,
            'description': self.description,
            'start': self.start,
            'end': self.end,
            'location': self.location,
            'id': self.id
        }


    def to_dbus_dict(self):

        return {
            'title': self.title,
            'description': self.description,
            'start': time.mktime(self.start.timetuple()) + self.start.microsecond / 1e6,
            'end': time.mktime(self.end.timetuple()) + self.end.microsecond / 1e6,
            'location': self.location,
            'id': self.id
        }
