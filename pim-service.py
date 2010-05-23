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
import gtk.gdk
import thread
import weakref

import cream
import cream.ipc

from tasks import TaskManager

class PIMService(cream.Module, cream.ipc.Object):

    def __init__(self):

        cream.Module.__init__(self)
        cream.ipc.Object.__init__(self,
            'org.cream.PIM',
            '/org/cream/PIM'
            )

        self.todo_manager = TaskManager()


if __name__ == '__main__':
    pim_service = PIMService()
    pim_service.main()
