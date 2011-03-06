import os

from calendar_extension.backends import CalendarBackend
from calendar_extension.backends.ical import IcalBackend

CALENDAR_BASE_PATH = os.path.join(os.path.expanduser('~'), '.local/share/evolution/calendar')

class EvolutionBackend(CalendarBackend):


    def __init__(self, *args, **kwargs):

        CalendarBackend.__init__(self, *args, **kwargs)

        path = os.path.join(CALENDAR_BASE_PATH, self.source)
        calendar_file = os.listdir(path)[0]
        self.path = os.path.join(path, calendar_file)

        self.ical = IcalBackend(self.uid, self.name, self.type, self.path)

        self.ical.connect('event-added', lambda _, *x: self.emit('event-added', *x))
        self.ical.connect('event-removed', lambda _, *x: self.emit('event-removed', *x))
        self.ical.connect('event-updated', lambda _, *x: self.emit('event-updated', *x))
        self.ical.connect('event-synced', lambda _, *x: self.emit('event-synced', *x))

    def add_event(self, event):

        return self.ical.add_event(event)


    def remove_event(self, uid):

        return self.ical.remove_event(uid)


    def update_event(self, uid, fields):

        return self.ical.update_event(uid, fields)


    def get_events(self):

        return self.ical.get_events()


    def sync_events(self, events):

        self.ical.sync_events(events)
