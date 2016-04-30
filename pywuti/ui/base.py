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

__all__ = ["Application", "BaseWidget", "UIScreen"]

import snack

class ExitMainLoop(Exception):
    pass

class ExitAllMainLoops(ExitMainLoop):
    pass

class Application(object):

    START_MAINLOOP = True
    STOP_MAINLOOP = False
    NOP = None

    def __init__(self, title):
        self._screen = snack.SnackScreen()
        self._screens = []

    def __del__(self):
        if self._screen:
            self._screen.finish()

    @property
    def screen(self):
        return self._screen

    def schedule_screen(self, ui, args=None):
        self._screens.insert(0, (ui, args, self.NOP))

    def close_screen(self, scr=None):
        oldscr, _oldattr, oldloop = self._screens.pop()
        if scr is not None:
            assert oldscr == scr

        # this cannot happen, if we are closing the window,
        # the loop must have been running or not be there at all
        assert oldloop != self.START_MAINLOOP

        if oldloop == self.STOP_MAINLOOP:
            raise ExitMainLoop()

        if not self._screens:
            raise ExitMainLoop()

    def run(self):
        try:
            self._mainloop()
            return True
        except ExitAllMainLoops:
            return False
            

    def _mainloop(self):
        last_screen = None

        while self._screens:
            try:
                last_screen = self._screens[-1][0]

                last_screen.setup()
                last_screen.redraw()
                last_screen.run(self._screens[-1][1])
                last_screen.close()
            except ExitAllMainLoops:
                raise

            # end just this loop
            except ExitMainLoop:
                break

class BaseWidget(object):
    def __init__(self):
        self._widget = None
        self._padding = (0, 0, 0, 0)
        self._anchorLeft = 0
        self._anchorTop = 0
        self._anchorRight = 0
        self._anchorBottom = 0
        self._growx = 0
        self._growy = 0
        self._col = 0
        self._row = 0

    @property
    def widget(self):
        return self._widget

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, row):
        self._row = row

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, col):
        self._col = col

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, padding):
        self._padding = padding

    @property
    def anchorLeft(self):
        return self._anchorLeft

    @anchorLeft.setter
    def anchorLeft(self, left):
        self._anchorLeft = left

    @property
    def anchorTop(self):
        return self._anchorTop

    @anchorTop.setter
    def anchorTop(self, top):
        self._anchorTop = top

    @property
    def anchorRight(self):
        return self._anchorRight

    @anchorRight.setter
    def anchorRight(self, right):
        self._anchorRight = right

    @property
    def anchorBottom(self):
        return self._anchorBottom

    @anchorBottom.setter
    def anchorBottom(self, bottom):
        self._anchorBottom = bottom

    @property
    def growx(self):
        return self._growx

    @growx.setter
    def growx(self, x):
        self._growx = x

    @property
    def growy(self):
        return self._growx

    @growy.setter
    def growy(self, y):
        self._growy = y

    def setxy(self, row, col):
        self._row = row
        self._col = col

    def setgrowxy(self, x, y):
        self._growx = x
        self._growy = y

    def setanchor(self, left, top, right, bottom):
        self._anchorLeft = left
        self._anchorTop = top
        self._anchorRight = right
        self._anchorBottom = bottom

    def extend(self, args):
        if isinstance(args, dict):
            for key in args:
                if hasattr(self, key):
                    setattr(self, key, args[key])

class UIScreen(object):
    def __init__(self, app, title):
        self._app = app
        self._title = title
        self._form = snack.Form()
        self._widgets = []
        self._cols = 0
        self._rows = 0
        self._grid = None
        

    @property
    def app(self):
        return self._app

    def setup(self):
        pass

    def add(self, widget, args = None):
        widget.col = self._cols
        widget.row = self._rows
        widget.extend(args)
        self._widgets.append(widget)

    def addWidget(self, widget, args = None):
        self.add(widget, args)
        self._rows += 1

    def addWidgetColumn(self, widget, args = None):
        self.add(widget)
        self._cols += 1

    def redraw(self):
        if self._grid is None:
            self._grid = snack.Grid(self._cols + 1, self._rows + 1)
            self._form.add(self._grid)
            for w in self._widgets:
                self._grid.setField(w.widget, w.col, w.row, w.padding,
                           w.anchorLeft, w.anchorTop, w.anchorRight, w.anchorBottom,
                           w.growx, w.growy)
                self._form.add(w.widget)

            self._app.screen.gridWrappedWindow(self._grid, self._title)
        self._form.draw()

    def run(self, args = None):
        return self._form.run()

    def refresh(self):
        self._app.screen.refresh()

    def close(self):
        self._app.screen.popWindow()
        self._app.close_screen(self)
