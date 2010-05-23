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
        'task_added': ('a{sv}', 'org.cream.pim.Tasks'),
        'task_deleted': ('i', 'org.cream.pim.Tasks'),
        'task_changed': ('a{sv}', 'org.cream.pim.Tasks')
        }

    def __init__(self):

        cream.ipc.Object.__init__(self,
            'org.cream.PIM',
            '/org/cream/pim/Tasks'
            )


    @cream.ipc.method('sssii', 'a{sv}', interface='org.cream.pim.Tasks')
    def add_task(self, title, description, category, priority, deadline):

        task = Task(
            title = title,
            description = description,
            category = category,
            priority = priority,
            deadline = deadline,
            status = STATUS_TODO
            )

        session.commit()

        self.emit_signal('task_added', task.to_dict())

        return task.to_dict()



    @cream.ipc.method('isssii', 'a{sv}', interface='org.cream.pim.Tasks')
    def edit_task(self, id, title, description, category, priority, deadline):

        task = Task.query.filter_by(id=id).one()

        task.title = title
        task.description = description
        task.category = category
        task.priority = priority
        task.deadline = deadline

        session.commit()

        self.emit_signal('task_changed', task.to_dict())

        return task.to_dict()


    @cream.ipc.method('ii', 'a{sv}', interface='org.cream.pim.Tasks')
    def set_task_status(self, id, status):

        task = Task.query.filter_by(id=id).one()
        task.status = status

        session.commit()

        self.emit_signal('task_changed', task.to_dict())

        return task.to_dict()


    @cream.ipc.method('i', '', interface='org.cream.pim.Tasks')
    def delete_task(self, id):

        task = Task.query.filter_by(id=id).one()

        self.emit_signal('task_deleted', task.id)

        task.delete()
        session.commit()


    @cream.ipc.method('i', 'a{sv}', interface='org.cream.pim.Tasks')
    def get_task(self, id):
        return Task.query.filter_by(id=id).one().to_dict()


    @cream.ipc.method('', 'aa{sv}', interface='org.cream.pim.Tasks')
    def list_tasks(self):
        return [task.to_dict() for task in Task.query.all()]
