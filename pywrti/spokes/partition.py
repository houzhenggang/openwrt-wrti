#!/usr/bin/python
#
# Copyright (C) 2016 Openwrt x86_64 Unity Project
#
# Wei Yongjun <weiyj.lk@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

from pywrti.ui import UIScreen, TextWidget, CheckboxTreeWidget, ButtonGroupWidget

class PartitionSpoke(UIScreen):
    def __init__(self, app, title = 'Partitioning'):
        UIScreen.__init__(self, app, title)

    def setup(self):
        wtext = TextWidget(65, "Installation requires partitioning of your "
                               "hard drive. Please choose which drive(s) "
                               "you would like to use. WARNING! All data on "
                               "the selected drive(s) will be lost.")
        self.addWidget(wtext, {'padding': (0, 0, 0, 1)})

        wtext = TextWidget(55, "Which drive(s) do you want to "
                               "use for this installation?")
        self.addWidget(wtext)

        self._wlist = CheckboxTreeWidget(height = 2, scroll = 1)

        disks = self.app.wrti.getDisks()
        for disk in disks:
            # skip cdrom
            if re.match("sr[0-9]", disk.name):
                continue

            model = disk.model

            size = int(disk.size)
            if size >= 1024 * 2048:
                sizestr = "%6.0f GB" % (size / (1024 * 2048))
            else:
                sizestr = "%6.0f MB" % (size / 2048)

            diskdesc = "%6s %s (%s)" % (disk.name, sizestr, model[:23])

            self._wlist.append(diskdesc, disk.name, 0)

        self.addWidget(self._wlist, {'padding': (0, 0, 0, 1)})

        self._btngrp = ButtonGroupWidget(['OK', 'BACK'])
        self.addWidget(self._btngrp)

    def run(self, args = None):
        UIScreen.run(self, args)
        self.app.wrti.instdisks = self._wlist.getSelection()
        return True
