from extensions.calendar.backends import CalendarSource
from extensions.calendar.backends.ical import IcalSource, IcalCalendar


class EvolutionSource(IcalSource, CalendarSource):
    type = 'evolution'


    def __init__(self, uid, data, calendars):

        IcalSource.__init__(self, uid, data, calendars)
