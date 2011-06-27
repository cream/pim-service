import os
import time
import gobject
import datetime
import icalendar

import atom
import gdata.calendar.service
from gdata.service import RequestError

from _calendar.backends import CalendarSource, BackendError, Calendar
from _calendar.util import Event, to_unicode

TIME_TEMPLATE1 = '%Y-%m-%dT%H:%M:%S.000'
TIME_TEMPLATE2 = '%Y-%m-%d'


class GcalEvent(Event):

    def __init__(self, g_event, calendar_uid):
    
        self.g_event = g_event
    
        uid = g_event.uid.value
        title = g_event.title.text
        description = g_event.content.text or ''
        
        #*_time[:-6] strips off unneeded timezone information
        when = g_event.when[0]
        try:
            tuple_start = time.strptime(when.start_time[:-6], TIME_TEMPLATE1)
            start = datetime.datetime.fromtimestamp(time.mktime(tuple_start))
        except ValueError:
            try:
                tuple_start = time.strptime(when.start_time, TIME_TEMPLATE2)
                start = datetime.datetime.fromtimestamp(time.mktime(tuple_start))
            except ValueError:
                start = None
        try:
            tuple_end = time.strptime(when.end_time[:-6], TIME_TEMPLATE1)
            end = datetime.datetime.fromtimestamp(time.mktime(tuple_end))
        except ValueError:
            try:
                tuple_end = time.strptime(when.end_time, TIME_TEMPLATE2)
                end = datetime.datetime.fromtimestamp(time.mktime(tuple_end))
            except ValueError:
                end = None
        
        location = g_event.where[0].text or ''
        
        Event.__init__(self, uid, title, description, start, end, location,
                       calendar_uid=calendar_uid)



class GcalSource(CalendarSource):
    type = 'gcal'

    def __init__(self, uid, email, calendars):

        CalendarSource.__init__(self, uid, email, calendars)
        
        self.calendar_service = gdata.calendar.service.CalendarService()
        self.calendar_service.email = email
        self.calendar_service.source = 'Chronos'
        
        
    def add_calendar(self, uid, name):
        
        pass
        
    
    def authenticate(self, username, password):
     
        self.calendar_service.password = password
        self.calendar_service.ProgrammaticLogin()

        for calendar in self._calendars:
            if 'Wochennummern' in calendar.name:
                continue
            url = self.get_url_for_name(calendar.name)
            calendar = GcalCalendar(calendar.uid, calendar.name, url, self.calendar_service)
            CalendarSource._add_calendar_instance(self, calendar)
            
        for calendar in self.calendar_service.GetAllCalendarsFeed().entry:
            name = calendar.title.text
            if 'Wochennummern' in name:
                continue
            uid = calendar.id.text
            url = calendar.link[0].href
            cal = GcalCalendar(uid, name, url, self.calendar_service)
            CalendarSource._add_calendar_instance(self, cal)

    
    def get_url_for_name(self, name):
    
        for calendar in self.calendar_service.GetAllCalendarsFeed().entry:
            if to_unicode(calendar.title.text) == name:
                return calendar.link[0].href
            
        
class GcalCalendar(Calendar):
    requires_auth = True

    def __init__(self, uid, name, url, calendar_service):

        Calendar.__init__(self, uid, name)
        
        self.url = url
        self.calendar_service = calendar_service
        
        self.events = {}
        for event in self.calendar_service.GetCalendarEventFeed(self.url).entry:            
            ev = GcalEvent(event, self.uid)
            self.events[ev.uid] = ev


    def update(self):

        pass


    def add_event(self, event, save=True):
    
        g_event = gdata.calendar.CalendarEventEntry()
        g_event.title = atom.Title(text=event.title)
        g_event.content = atom.Content(text=event.description)
        g_event.where.append(gdata.calendar.Where(value_string=event.location))
        
        start = event.start.strftime(TIME_TEMPLATE1)
        end = event.end.strftime(TIME_TEMPLATE1)
        g_event.when.append(gdata.calendar.When(start_time=start, end_time=end))

        try:
            event = self.calendar_service.InsertEvent(g_event, 
                                        '/calendar/feeds/default/private/full')
        except RequestError:
            return False

        return True


    def remove_event(self, uid):
            
        g_event = self.events[uid].g_event
        
        try:
            ret = self.calendar_service.DeleteEvent(g_event.GetEditLink().href)
        except RequestError:
            return False
        
        self.events.pop(uid)
        
        return True
        

    def update_event(self, uid, fields):
    
        for key, value in fields.iteritems():
            self.events[uid][key] = value
    
        g_event = self.events[uid].g_event
        
        title = fields.get('title')
        if title:
            g_event.title.text = title
        
        description = fields.get('description')
        if description:
            g_event.content.text = description
        
        when = g_event.when[0]
        start = fields.get('start')
        if start:
            when.start_time = start.strftime(TIME_TEMPLATE1)
        end = fields.get('end')
        if end:
            when.end_time = end.strftime(TIME_TEMPLATE1)
        g_event.when[0] = when
        
        location = fields.get('location')
        if location:
            g_event.where[0].text = location
        

        try:
            self.calendar_service.UpdateEvent(g_event.GetEditLink().href, g_event)
        except RequestError:
            return False

        return True
        

    def get_events(self):

        return self.events.values()
        

    def sync_events(self, events):

        for event in events:
            if event.deleted:
                synced = self.remove_event(event.uid)
                if synced:
                    self.emit('event-synced', event.uid)
                    
            for g_event in self.events.itervalues():    
                if event.uid == g_event.uid:
                    if event != g_event:
                        synced = self.update_event(event.uid, event.to_dict)
                        if synced:
                            self.emit('event-synced', event.uid)
                    break
            else:
                synced = self.add_event(event)
                if synced:
                    self.emit('event-synced', event.uid)
        
