#!/usr/bin/python
#
# Copyright 2005-2016 Red Hat, Inc.
# Copyright (C) 2016 Openwrt x86_64 Unity Project
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
from pywrti.ks.constants import KS_SCRIPT_PRE, KS_SCRIPT_POST

class KickstartSection(KickstartObject):
    allLines = False
    sectionOpen = ""
    timesSeen = 0

    def __init__(self, handler, **kwargs):
        self.handler = handler
        
        self.dataObj = kwargs.get("dataObj", None)

    def finalize(self):
        pass

    def handleLine(self, line):
        pass

    def handleHeader(self, lineno, args):
        self.timesSeen += 1

    @property
    def seen(self):
        return self.timesSeen > 0

class Packages(KickstartObject):
    def __init__(self, *args, **kwargs):
        KickstartObject.__init__(self, *args, **kwargs)

        self.excludedList = []
        self.packageList = []

    def __str__(self):
        pkgs = ""

        p = self.packageList
        p.sort()
        for pkg in p:
            pkgs += "%s\n" % pkg

        p = self.excludedList
        p.sort()
        for pkg in p:
            pkgs += "-%s\n" % pkg

        return "\n%packages" + "\n" + pkgs + "\n%end\n"

    def add(self, pkgList):
        newExcludedSet = []
        newPackageSet = []

        for pkg in pkgList:
            stripped = pkg.strip()

            if stripped[0] == "-":
                newExcludedSet.append(stripped[1:])
            else:
                newPackageSet.append(stripped)

        for pkg in newExcludedSet:
            if pkg in self.packageList:
                self.packageList.remove(pkg)
        for pkg in newPackageSet:
            if not pkg in self.packageList:
                self.packageList.append(pkg)

        for pkg in self.excludedList:
            if pkg in self.packageList:
                self.excludedList.remove(pkg)
        for pkg in newExcludedSet:
            if not pkg in self.excludedList:
                self.excludedList.append(pkg)

class PackageSection(KickstartSection):
    sectionOpen = "%packages"

    def handleLine(self, line):
        h = line.partition('#')[0]
        line = h.rstrip()
        self.handler.packages.add([line])

class Script(KickstartObject):
    def __init__(self, script, *args , **kwargs):
        KickstartObject.__init__(self, *args, **kwargs)
        self.script = "".join(script)

        self.lineno = kwargs.get("lineno", None)
        self.type = kwargs.get("type", KS_SCRIPT_PRE)

    def __str__(self):
        retval = ""

        if self.type == KS_SCRIPT_PRE:
            retval += '\n%pre'
        elif self.type == KS_SCRIPT_POST:
            retval += '\n%post'

        if self.script.endswith("\n"):
            return retval + "\n%s%%end\n" % self.script
        else:
            return retval + "\n%s\n%%end\n" % self.script

class ScriptSection(KickstartSection):
    allLines = True

    def __init__(self, *args, **kwargs):
        KickstartSection.__init__(self, *args, **kwargs)
        self._script = {}
        self._resetScript()

    def _resetScript(self):
        self._script = {"lineno": None, "body": []}

    def handleLine(self, line):
        self._script["body"].append(line)

    def finalize(self):
        if " ".join(self._script["body"]).strip() == "":
            return

        kwargs = {"lineno": self._script["lineno"],
                  "type": self._script["type"]}

        if self.dataObj is not None:
            s = self.dataObj(self._script["body"], **kwargs)
            self._resetScript()
            self.handler.scripts[self.sectionOpen[1:]] = s

    def handleHeader(self, lineno, args):
        KickstartSection.handleHeader(self, lineno, args)
        self._script["lineno"] = lineno

class PreScriptSection(ScriptSection):
    sectionOpen = "%pre"

    def _resetScript(self):
        ScriptSection._resetScript(self)
        self._script["type"] = KS_SCRIPT_PRE

class PostScriptSection(ScriptSection):
    sectionOpen = "%post"

    def _resetScript(self):
        ScriptSection._resetScript(self)
        self._script["type"] = KS_SCRIPT_POST

