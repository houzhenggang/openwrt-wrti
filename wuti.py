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

from pywuti.ui import Application

from pywuti.spokes.welcome import WelcomeSpoke
from pywuti.spokes.storage import StorageSpoke
from pywuti.spokes.install import InstallSpoke
from pywuti.spokes.finish import FinishSpoke

if __name__ == "__main__":
    print("Starting installer, one moment...")

    app = Application("Install Mode")
    spoke = WelcomeSpoke(app, 'Openwrt')
    storage = StorageSpoke(app, 'Storage')
    install = InstallSpoke(app)
    finsh = FinishSpoke(app)
    app.schedule_screen(spoke)
    app.schedule_screen(storage)
    app.schedule_screen(install)
    app.schedule_screen(finsh)
    app.run()
