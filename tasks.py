#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os

import gobject
import weakref

import cream
import cream.ipc

from elixir import *

metadata.bind = "sqlite:///tasks.db"
metadata.bind.echo = False

STATUS_TODO = 0
STATUS_WIP = 1
STATUS_DONE = 2

PRIORITY_LOW = 0
PRIORITY_MEDIUM = 1
PRIORITY_HIGH = 2

class Task(Entity):

    title = Field(Unicode)
    description = Field(UnicodeText)
    category = Field(Unicode)
    priority = Field(Integer)
    deadline = Field(Integer)
    status = Field(Integer)
    
    def __repr__(self):
        return '<Task "%s">' % (self.title)


setup_all()
create_all()


class TaskManager(cream.ipc.Object):

    __ipc_signals__ = {
        }

    def __init__(self):

        cream.ipc.Object.__init__(self,
            'org.cream.PIM',
            '/org/cream/pim/Tasks'
            )


    @cream.ipc.method('sssii', 'a{sv}', interface='org.cream.pim.Tasks')
    def add_task(self, title, description, category, priority, deadline):

        t = Task(
            title = title,
            description = description,
            category = category,
            priority = priority,
            deadline = deadline,
            status = STATUS_TODO
            )

        session.commit()

        return {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'category': t.category,
            'priority': t.priority,
            'deadline': t.deadline,
            'status': t.status
            }


    @cream.ipc.method('isssii', 'a{sv}', interface='org.cream.pim.Tasks')
    def edit_task(self, id, title, description, category, priority, deadline):

        t = Task.filter_by(id=id).one()

        t.title = title
        t.description = description
        t.category = category
        t.priority = priority
        t.deadline = deadline

        session.commit()

        return {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'category': t.category,
            'priority': t.priority,
            'deadline': t.deadline,
            'status': t.status
            }


    @cream.ipc.method('ii', 'a{sv}', interface='org.cream.pim.Tasks')
    def set_task_status(self, id, status):

        t = Task.filter_by(id=id).one()

        t.status = status

        session.commit()

        return {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'category': t.category,
            'priority': t.priority,
            'deadline': t.deadline,
            'status': t.status
            }


    @cream.ipc.method('i', '', interface='org.cream.pim.Tasks')
    def delete_task(self, id):

        t = Task.filter_by(id=id).one()
        t.delete()

        session.commit()


    @cream.ipc.method('i', 'a{sv}', interface='org.cream.pim.Tasks')
    def get_task(self, id):

        t = Task.filter_by(id=id).one()

        return {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'category': t.category,
            'priority': t.priority,
            'deadline': t.deadline,
            'status': t.status
            }


    @cream.ipc.method('', 'aa{sv}', interface='org.cream.pim.Tasks')
    def list_tasks(self):

        tasks = Task.query.all()

        return [{
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'category': t.category,
            'priority': t.priority,
            'deadline': t.deadline,
            'status': t.status
            } for t in tasks]
