import os
import time
import gobject
import datetime
import icalendar

import atom
import gdata.gauth
import gdata.calendar.client
from gdata.service import RequestError

from extensions.calendar.backends import CalendarSource, BackendError, Calendar
from extensions.calendar.util import Event, to_unicode

TIME_TEMPLATE1 = '%Y-%m-%dT%H:%M:%S.000'
TIME_TEMPLATE2 = '%Y-%m-%d'

UPDATE_INTERVAL = 5 * 60 * 1000


class GcalEvent(Event):

    def __init__(self, g_event, calendar_uid):

        self.g_event = g_event
        uid = g_event.uid.value
        title = g_event.title.text or ''
        description = g_event.content.text or ''

        when = g_event.when[0]
        try:
            tuple_start = time.strptime(when.start, TIME_TEMPLATE2)
            start = datetime.datetime.fromtimestamp(time.mktime(tuple_start))
        except ValueError:
            start = None
        try:
            tuple_end = time.strptime(when.end, TIME_TEMPLATE2)
            end = datetime.datetime.fromtimestamp(time.mktime(tuple_end))
        except ValueError:
            end = None

        location = g_event.where[0].text or ''

        Event.__init__(self, uid, title, description, start, end, location,
                       calendar_uid=calendar_uid)



class GcalSource(CalendarSource):
    type = 'gcal'

    def __init__(self, uid, data, calendars):

        CalendarSource.__init__(self, uid, data, calendars)

        self.client = gdata.calendar.client.CalendarClient(source='Chronos')

        if isinstance(data, dict):
            self.client.ClientLogin(data['username'], data['password'], self.client.source)

            auth_token = self.client.auth_token.token_string

            def update_source():
                self.emit('source-updated', self.uid, {'data': auth_token})

            gobject.timeout_add(1000, update_source)

        else:
            auth_token = gdata.gauth.ClientLoginToken(data)
            self.client.auth_token = auth_token

        self.calendar_feed = self.client.GetAllCalendarsFeed().entry

        gobject.timeout_add(500, self.setup_calendars)


    def setup_calendars(self):

        for calendar in self._calendars:
            url = self.get_url_for_name(calendar.name)
            calendar = GcalCalendar(calendar.uid, calendar.name, url, self.client)
            CalendarSource._add_calendar_instance(self, calendar)

        for calendar in self.calendar_feed:
            name = calendar.title.text
            uid = calendar.id.text
            if uid in self.calendar_instances:
                # calendar is already added
                continue

            url = calendar.link[0].href
            cal = GcalCalendar(uid, name, url, self.client)
            CalendarSource._add_calendar_instance(self, cal)


    def add_calendar(self, uid, name):

        pass


    def get_url_for_name(self, name):

        for calendar in self.calendar_feed:
            if to_unicode(calendar.title.text) == name:
                return calendar.link[0].href


class GcalCalendar(Calendar):

    def __init__(self, uid, name, url, client):

        Calendar.__init__(self, uid, name)

        self.url = url
        self.client = client

        self.get_remote_events()

        gobject.timeout_add(UPDATE_INTERVAL, self.update)


    def get_remote_events(self):

        self.feed = self.client.GetCalendarEventFeed(self.url).entry

        self.events = {}
        for event in self.feed:
            ev = GcalEvent(event, self.uid)
            self.events[ev.uid] = ev


    def update(self):

        old_events = self.events
        self.get_remote_events()

        for old_event in old_events.itervalues():
            for new_event in self.events.itervalues():
                if old_event.uid == new_event.uid:
                    break
            else:
                old_event.synced = True
                self.emit('event-removed', old_event.uid, old_event)

        for new_event in self.events.itervalues():
            for old_event in old_events.itervalues():
                if old_event.uid == new_event.uid and old_event != new_event:
                    self.emit('event-updated', new_event.uid, new_event.to_dict())
                break
            else:
                new_event.synced = True
                self.emit('event-added', new_event.uid, new_event)


    def add_event(self, event):

        g_event = gdata.calendar.CalendarEventEntry()
        g_event.title = atom.Title(text=event.title)
        g_event.content = atom.Content(text=event.description)
        g_event.where.append(gdata.calendar.Where(value_string=event.location))

        start = event.start.strftime(TIME_TEMPLATE1)
        end = event.end.strftime(TIME_TEMPLATE1)
        g_event.when.append(gdata.calendar.When(start_time=start, end_time=end))

        try:
            event = self.client.InsertEvent(g_event,
                                        '/calendar/feeds/default/private/full')
        except RequestError:
            return False

        return True


    def remove_event(self, uid):

        g_event = self.events[uid].g_event

        try:
            ret = self.client.DeleteEvent(g_event.GetEditLink().href)
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
            self.client.UpdateEvent(g_event.GetEditLink().href, g_event)
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
