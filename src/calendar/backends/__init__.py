import gobject

import ical

CALENDAR_SOURCES = {
    'icalendar': ical.ICalendarSource
}


class CalendarManager(gobject.GObject):

    __gsignals__ = {
        'calendar-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }


    def __init__(self):

        gobject.GObject.__init__(self)

        self._calendars = {}


    @property
    def calendars(self):

        return self._calendars.values()

    def add_calendar(self, calendar):

        calendar_source = CALENDAR_SOURCES[calendar['type']]
        calendar_instance = calendar_source(calendar['name'],
                                            calendar['id'],
                                            calendar['type'],
                                            calendar['source'])
        self._calendars[calendar['id']] = calendar_instance

        self.emit('calendar-added', calendar)


    def add_event(self, event, calendar_id):

        calendar = self._calendars[calendar_id]
        calendar.add_event(event)


    def delete_event(self, event, calendar_id):

        calendar = self._calendars[calendar_id]
        calendar.delete_event(event)


    def update_event(self, old_event, new_event, calendar_id):

        calendar = self._calendars[calendar_id]
        calendar.update_event(old_event, new_event)
