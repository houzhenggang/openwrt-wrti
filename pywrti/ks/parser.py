#!/usr/bin/python
#
# Copyright 2005-2016 Red Hat, Inc.
# Copyright 2016 Openwrt x86_64 Unity Project
#
# Chris Lumens <clumens@redhat.com>
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

import shlex

from collections import Iterator

from pywrti.ks.handler import KickstartHandler

STATE_END = "end"
STATE_COMMANDS = "commands"

class PutBackIterator(Iterator):
    def __init__(self, iterable):
        self._iterable = iter(iterable)
        self._buf = None

    def __iter__(self):
        return self

    def put(self, s):
        self._buf = s

    def next(self):
        if self._buf:
            retval = self._buf
            self._buf = None
            return retval
        else:
            return next(self._iterable)

    def __next__(self):
        return self.next()

class KickstartParser(object):
    def __init__(self):
        self.handler = KickstartHandler()

        self._state = STATE_COMMANDS

    def _reset(self):
        self._state = STATE_COMMANDS

    def _handleCommand(self, lineno, args):
        if self.handler:
            self.handler.currentLine = self._line
            self.handler.dispatchCommand(args, lineno)

    def _handleSectionHeader(self, lineno, args):
        if self.handler:
            self.handler.handleSectionHeader(self._state, lineno, args)

    def _handleSectionLine(self, lineno, line):
        if self.handler:
            self.handler.handleSectionLine(self._state, lineno, line)

    def _finalize(self):
        if self.handler:
            self.handler.finalizeSection(self._state)
        self._state = STATE_COMMANDS

    def _readSection(self, lineIter, lineno):        
        while True:
            try:
                line = next(lineIter)
                if line == "":
                    self._finalize()
            except StopIteration:
                break

            lineno += 1

            if line.lstrip().startswith("%"):
                args = shlex.split(line)
                
                if args and args[0] == "%end":
                    self._finalize()
                    break

                elif args and self._validSectionState(args[0]):
                    lineIter.put(line)
                    lineno -= 1
                    self._finalize()
                    break
            else:
                self._handleSectionLine(lineno, line)

        return lineno

    def _isBlankOrComment(self, line):
        return line.isspace() or line == "" or line.lstrip()[0] == '#'

    def _stateMachine(self, lineIter):
        lineno = 0

        while True:
            try:
                self._line = next(lineIter)
                if self._line == "":
                    break
            except StopIteration:
                break

            lineno += 1

            if self._isBlankOrComment(self._line):
                continue

            args = shlex.split(self._line, comments=True)

            if self._state == STATE_COMMANDS:
                if args[0][0] == '%':
                    newSection = args[0]
                    self._state = newSection
                    self._handleSectionHeader(lineno, args)

                    lineno = self._readSection(lineIter, lineno)
                else:
                    self._handleCommand(lineno, args)
            elif self._state == STATE_END:
                break

    def readKickstartFromString(self, s, reset=True):
        if reset:
            self._reset()

        i = PutBackIterator(s.splitlines(True) + [""])
        self._stateMachine (i)

    def readKickstart(self, f, reset=True):
        if reset:
            self._reset()

        with open(f, 'r') as fh:
            contents = fh.read()
            self.readKickstartFromString(contents, reset)

    def get(self, item=None, val=None):
        if not item == None:
            if hasattr(self.handler, item):
                if not val is None:
                    if hasattr(getattr(self.handler, item), val):
                        return getattr(getattr(self.handler, item), val)
                    elif isinstance(getattr(self.handler, item), dict):
                        return getattr(self.handler, item)[val]
                    else:
                        return None
                else:
                    return getattr(self.handler, item)
            elif hasattr(self.handler, val):
                return getattr(self.handler, val)
        else:
            return self.handler

