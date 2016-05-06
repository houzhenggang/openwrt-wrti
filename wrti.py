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

from pywrti.ui import Application
from pywrti.storage import DeviceTree

from pywrti.spokes.welcome import WelcomeSpoke
from pywrti.spokes.partition import PartitionSpoke
from pywrti.spokes.install import InstallSpoke
from pywrti.spokes.finish import FinishSpoke

class Wrti(object):
    def __init__(self):
        self._devicetree = DeviceTree()

    def getDisks(self):
        self._devicetree.reset()

    @property
    def devicetree(self):
        return self._devicetree

if __name__ == "__main__":
    print("Starting installer, one moment...")

    wrti = Wrti()

    app = Application(wrti, "Install Mode")
    spoke = WelcomeSpoke(app, 'Openwrt')
    partition = PartitionSpoke(app)
    install = InstallSpoke(app)
    finsh = FinishSpoke(app)
    app.schedule_screen(spoke)
    app.schedule_screen(partition)
    app.schedule_screen(install)
    app.schedule_screen(finsh)
    app.run()
