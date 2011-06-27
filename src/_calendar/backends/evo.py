from _calendar.backends import CalendarSource
from _calendar.backends.ical import IcalSource, IcalCalendar


class EvolutionSource(IcalSource, CalendarSource):
    type = 'evolution'


    def __init__(self, uid, data, calendars):

        IcalSource.__init__(self, uid, data, calendars)
        
        
   # def add_calendar(self, uid, name, type, source):
        
    #    calendar = EvolutionCalendar(uid, name, type, source)
      #  self.calendars[uid] = calendar
     #   
       # return calendar
        

