from elixir import *
from _calendar.util import Event as _Event, Calendar as _Calendar, \
                          CalendarSource as _CalendarSource


class Event(Entity):

    uid = Field(Unicode, primary_key=True)
    title = Field(Unicode)
    description = Field(UnicodeText)
    start = Field(DateTime)
    end = Field(DateTime)
    location = Field(Unicode)
    synced = Field(Boolean, default=False)
    deleted = Field(Boolean, default=False)
    calendar = ManyToOne('Calendar')


    def to_internal(self):
        return _Event(**self.to_dict())

    def __repr__(self):
        return '<Event "%s">' % (self.title)



class CalendarSource(Entity):

    uid = Field(Unicode, primary_key=True)
    
    type = Field(Unicode)
    data = Field(Unicode)
    calendars = OneToMany('Calendar')
    
    def to_internal(self):
        return _CalendarSource(calendars=self.calendars, **self.to_dict())

    def __repr__(self):
        return '<CalendarSource "%s">' % (self.type)
        

class Calendar(Entity):

    uid = Field(Unicode, primary_key=True)
    name = Field(Unicode)
    source = ManyToOne('CalendarSource')
    events = OneToMany('Event')
    
    def to_internal(self):
        print self.to_dict()
        return _Calendar(**self.to_dict())

    def __repr__(self):
        return '<Calendar "%s">' % (self.name)
