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

__all__ = ["TextWidget", "LabelWidget", "ButtonWidget", "ColumnWidget"]

import snack

from .base import BaseWidget

class TextWidget(BaseWidget):
    def __init__(self, width, text):
        BaseWidget.__init__(self)
        self._widget = snack.TextboxReflowed(width, text)

class LabelWidget(BaseWidget):
    def __init__(self, text):
        BaseWidget.__init__(self)
        self._widget = snack.Label(text)

class ButtonWidget(BaseWidget):
    def __init__(self, text):
        BaseWidget.__init__(self)
        self._widget = snack.Button(text)

class ColumnWidget(BaseWidget):
    def __init__(self, cols):
        BaseWidget.__init__(self)
        self._widget = snack.Grid(cols, 1)
        self._item = 0
        self._list = []
    
    def addWidget(self, w):
        w.col = self._item
        self._widget.setField(w.widget, self._item, 0, (1, 0, 1, 0))
        self._item = self._item  + 1
