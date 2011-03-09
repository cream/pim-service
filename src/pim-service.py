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


class PIMService(cream.Module, cream.ipc.Object):

    extension_interface = None

    def __init__(self):

        cream.Module.__init__(self, 'org.cream.PIM')
        cream.ipc.Object.__init__(self,
            'org.cream.PIM',
            '/org/cream/PIM'
            )

        self.tasks = self.extension_manager.load_by_name('Tasks', self)


if __name__ == '__main__':
    pim_service = PIMService()
    pim_service.main()
