from elixir import *
from calendar.util import Event as _Event, Calendar as _Calendar


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



class Calendar(Entity):

    uid = Field(Unicode, primary_key=True)
    name = Field(Unicode)
    source = Field(Unicode)
    type = Field(Unicode)
    events = OneToMany('Event')

    def to_internal(self):
        return _Calendar(**self.to_dict())

    def __repr__(self):
        return '<Calendar "%s">' % (self.name)
