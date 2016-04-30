#!/usr/bin/python
#
# Copyright (C) 2016
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

import time

from pywuti.ui import UIScreen, LabelWidget, TextboxWidget, ProcessWidget

class InstallSpoke(UIScreen):
        def __init__(self, app, title = 'Package Installation'):
            UIScreen.__init__(self, app, title)
            self._amount = 0
            
        def setup(self):
            self._process = ProcessWidget(65, 100)
            #self._process.setprocess(20)
            self.addWidget(self._process, {'padding': (0, 1, 0, 0)})
            self._label = LabelWidget("Packages completed 184 of 255")
            self.addWidget(self._label, {'padding': (0, 1, 0, 0)})
            self._info = TextboxWidget(65, "Installing libc-1.3.4-ipk (2K)\nA library for text mode user interfaces")
            self.addWidget(self._info, { "wrap": 1, 'padding': (0, 1, 0, 0)})

        def run(self, args = None):
            while self._amount < 100:
                self._amount = self._amount + 10
                self._process.setprocess(self._amount)
                self.redraw()
                self.refresh()
                time.sleep(1)
