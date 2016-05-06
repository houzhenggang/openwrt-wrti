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

from pywrti.ui import UIScreen, TextWidget, CheckboxTreeWidget, ColumnWidget, ButtonWidget

class PartitionSpoke(UIScreen):
        def __init__(self, app, title = 'Partitioning Type'):
            UIScreen.__init__(self, app, title)
            
        def setup(self):
            wtext = TextWidget(65, _("Installation requires partitioning of "
                                     "your hard drive.  The default layout is "
                                     "suitable for most users.  Select what "
                                     "space to use and which drives to use as "
                                     "the install target."))
            self.addWidget(wtext)
            
            wtext = TextWidget(55, _("Which drive(s) do you want to "
                                     "use for this installation?"))
            self.addWidget(wtext)

            wlist = CheckboxTreeWidget(height = 4, scroll = 1)
            
            disks = self.app.wrti.devicetree
            for disk in disks:
                model = disk.model
                sizestr = "%8.0f MB" % (disk.size / (1024 * 1024))
                diskdesc = "%6s %s (%s)" % (disk.name, sizestr, model[:23])
                
                wlist.append(diskdesc, disk.name, 0)

            self.addWidget(wlist)

            wcols = ColumnWidget(2)
            wcols.addWidget(ButtonWidget('OK'))
            wcols.addWidget(ButtonWidget('BACK'))
            self.addWidget(wcols)
