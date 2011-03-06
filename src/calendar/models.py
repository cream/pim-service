from elixir import *


class Event(Entity):

    title = Field(Unicode)
    description = Field(UnicodeText)
    start = Field(DateTime)
    end = Field(DateTime)
    location = Field(Unicode)
    synced = Field(Boolean, default=False)
    calendar = ManyToOne('Calendar')
    #recurrence = Field()


    def __repr__(self):
        return '<Event "%s">' % (self.title)


class Calendar(Entity):

    name = Field(Unicode)
    source = Field(Unicode)
    type = Field(Unicode)
    events = OneToMany('Event')

    def __repr__(self):
        return '<Calendar "%s">' % (self.name)
