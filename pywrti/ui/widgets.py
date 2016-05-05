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

__all__ = ["TextWidget", "TextboxWidget", "LabelWidget", "ButtonWidget",
           "ColumnWidget", "ListWidget", "ProcessWidget"]

import snack

from .base import BaseWidget

class TextWidget(BaseWidget):
    def __init__(self, width, text):
        BaseWidget.__init__(self)
        self._widget = snack.TextboxReflowed(width, text)

class TextboxWidget(BaseWidget):
    def __init__(self, width, height, text, scroll = 0, wrap = 0):
        BaseWidget.__init__(self)
        self._widget = snack.Textbox(width, height, text, scroll, wrap)

    def setText(self, text):
        self._widget.setText(text)

class LabelWidget(BaseWidget):
    def __init__(self, text):
        BaseWidget.__init__(self)
        self._widget = snack.Label(text)

    def setText(self, text):
        self._widget.setText(text)

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

class ListWidget(BaseWidget):
    def __init__(self, height, scroll = 0, returnExit = 0, width = 0, showCursor = 0, multiple = 0, border = 0):
        BaseWidget.__init__(self)
        self._widget = snack.Listbox(height, scroll, returnExit, width, showCursor, multiple, border)

    def append(self, text, item):
        self._widget.append(text, item)

class ProcessWidget(BaseWidget):
    def __init__(self, width, total):
        BaseWidget.__init__(self)
        self._widget = snack.Scale(width, total)

    def setprocess(self, amount):
        self._widget.set(amount)
