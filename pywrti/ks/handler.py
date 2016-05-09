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

from pywrti.ks.base import KickstartObject
from pywrti.ks.sections import Packages, Script, PackageSection, PostScriptSection
from pywrti.ks.commands import PartitionCommand

class KickstartHandler(KickstartObject):
    def __init__(self, *args, **kwargs):
        KickstartObject.__init__(self, *args, **kwargs)

        self.scripts = {}
        self.packages = Packages()

        self._commands = {}
        self._sections = {}

        self.currentLine = ""

        self.setupCommands()
        self.setupSections()

    def _isBlankOrComment(self, line):
        return line.isspace() or line == "" or line.lstrip()[0] == '#'

    def _tryFunc(self, fn):
        try:
            fn()
        except Exception as msg:
            print(msg)

    def _validCommand(self, cmd):
        return cmd in list(self._commands.keys())

    def dispatchCommand(self, args, lineno):
        cmd = args[0]
        if self._validCommand(cmd):
            cmdObj = self._commands[cmd]

            cmdObj.lineno = lineno
            cmdObj.seen = True

            obj = cmdObj.parse(args[1:])

            lst = cmdObj.dataList()
            if lst is not None:
                lst.append(obj)

            return True
        else:
            raise TypeError("Line %d: Unknown kickstart command: %s" % (lineno, cmd))

    def _validSectionState(self, st):
        return st in list(self._sections.keys())

    def handleSectionHeader(self, state, lineno, args):
        if self._validSectionState(state):
            obj = self._sections[state]
            self._tryFunc(lambda: obj.handleHeader(lineno, args))
        else:
            raise TypeError("Line %d: Unknown kickstart section: %s" % (lineno, state))

    def handleSectionLine(self, state, lineno, line):
        obj = self._sections[state]
        if obj.allLines or not self._isBlankOrComment(line):
            self._tryFunc(lambda: obj.handleLine(line))

    def finalizeSection(self, state):
        obj = self._sections[state]
        obj.finalize()

    def registerCommand(self, obj):
        if not obj.commandName:
            raise TypeError("no commandName given for command %s" % obj)

        self._commands[obj.commandName] = obj

        setattr(self, obj.commandName.lower(), obj)

    def setupCommands(self):
        self._commands = {}

        self.registerCommand(PartitionCommand())

    def registerSection(self, obj):
        if not obj.sectionOpen:
            raise TypeError("no sectionOpen given for section %s" % obj)

        if not obj.sectionOpen.startswith("%"):
            raise TypeError("section %s tag does not start with a %%" % obj.sectionOpen)

        self._sections[obj.sectionOpen] = obj

    def setupSections(self):
        self._sections = {}

        self.registerSection(PackageSection(self))
        self.registerSection(PostScriptSection(self, dataObj=Script))

