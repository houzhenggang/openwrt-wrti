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

import os

from pywrti.ui import UIScreen, TextWidget, ButtonWidget

class FinishSpoke(UIScreen):
        def __init__(self, app, title = 'Complete'):
            UIScreen.__init__(self, app, title)
            
        def setup(self):
            wtext = TextWidget(40, 'Congratulations, your Openwrt installation is complete.\n'
                               '\nPlease reboot to use the installed system.')
            self.addWidget(wtext, {'padding': (0, 0, 0, 1)})
            self.addWidget(ButtonWidget('Reboot'))

        def run(self, args = None):
            UIScreen.run(self, args)
            #os.system('/sbin/reboot')
