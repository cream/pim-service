import time
import socket
import datetime

import icalendar

from cream.util import random_hash

HASH_LENGTH = 26


class CalendarSource(object):
    """An internal representation of a calendar source."""

    def __init__(self, uid, type, data, calendars):

        self.uid = uid
        self.type = type
        self.data = data
        self.calendars = calendars


    def to_dict(self):

        return {
            'uid': self.uid,
            'type': self.type,
            'data': self.data,
            'calendars': self.calendars
        }


class Calendar(object):
    """An internal representation of a calendar."""

    def __init__(self, source_uid, name='', uid=None):

        self.uid = uid
        self.name = name
        self.source_uid = source_uid


    def to_dict(self):

        return {
            'uid': self.uid,
            'name': self.name,
            'source_uid': self.source_uid
        }


class Event(object):
    """An internal representation of an event."""

    def __init__(self, uid=None,
                        title='',
                        description='',
                        start=None,
                        end=None,
                        location='',
                        recurrence=None,
                        synced=False,
                        deleted=False,
                        calendar_uid=''):

        self.uid = uid
        self.title = to_unicode(title)
        self.description = to_unicode(description)
        self.start = start
        self.end = end
        self.location = to_unicode(location)
        self.recurrence = recurrence
        self.synced = synced
        self.deleted = deleted
        self.calendar_uid = calendar_uid

        if isinstance(start, (float, int)):
            self.start = datetime.datetime.fromtimestamp(start)
        elif isinstance(start, datetime.datetime):
            self.start = start.replace(tzinfo=None)
        if isinstance(end, (float, int)):
            self.end = datetime.datetime.fromtimestamp(end)
        elif isinstance(start, datetime.datetime):
            self.end = end.replace(tzinfo=None)


    def __eq__(self, other):

        if (self.uid == other.uid and
           self.title == other.title and
           self.description == other.description and
           self.start == other.start and
           self.end == other.end and
           self.location == other.location and
           self.recurrence == other.recurrence and
           self.calendar_uid == other.calendar_uid):
            return True
        else:
            return False


    def __ne__(self, other):
        return not self.__eq__(other)



    @classmethod
    def from_ical(self, ical, calendar_uid=None):
        """Create an event from an ical string."""

        event = icalendar.Event.from_string(ical)

        uid = str(event.get('uid'))
        title = event.get('summary', '')
        description = event.get('description', '')
        start = event.get('dtstart', None)
        end = event.get('dtend', None)
        location = event.get('location', '')
        recurrence = event.get('rrule', '')

        if title:
            title = str(title)
        if description:
            description = str(description)
        if start:
            start = icalendar.vDDDTypes.from_ical(start.ical())
        if end:
            end = icalendar.vDDDTypes.from_ical(end.ical())
        if location:
            location = str(location)
        if recurrence:
            recurrence = icalendar.vRecur.from_ical(recurrence.ical())

        return Event(
            uid = uid,
            title = title,
            description = description,
            start = start,
            end = end,
            location = location,
            recurrence = recurrence,
            calendar_uid = calendar_uid
        )


    def to_dict(self):

        return {
            'uid': self.uid,
            'title': self.title,
            'description': self.description,
            'start': self.start,
            'end': self.end,
            'location': self.location,
            #'recurrence': self.recurrence,
            'synced': self.synced,
            'deleted': self.deleted,
            'calendar_uid': self.calendar_uid
        }

    def to_dbus(self):

        return {
            'uid': self.uid,
            'title': self.title,
            'description': self.description,
            'start': time.mktime(self.start.timetuple()) if self.start else 1,
            'end': time.mktime(self.end.timetuple()) if self.end else 1,
            'location': self.location,
            #'recurrence': self.recurrence,
            'calendar_uid': self.calendar_uid
        }


def generate_uid():

    return random_hash()[:HASH_LENGTH] + '@' + socket.gethostname()


def convert_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def convert_to_timestamp(dtime):
    return time.mktime(dtime.timetuple())

def to_unicode(s):
    if isinstance(s, unicode):
        return s
    try:
        return s.decode('utf-8')
    except UnicodeDecodeError:
        return s.decode('latin-1')
