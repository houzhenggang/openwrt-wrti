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

import warnings

from pywrti.ks.base import KickstartObject
from pywrti.ks.options import KSOptionParser

class KickstartCommand(KickstartObject):
    commandName = ""

    def __init__(self, *args, **kwargs):
        KickstartObject.__init__(self, *args, **kwargs)

        self.lineno = 0
        self.seen = False

        self.dataClass = kwargs.get("dataClass", None)

    def __str__(self):
        return KickstartObject.__str__(self)

    def parse(self, args):
        raise TypeError("parse() not implemented for KickstartCommand")

    def set_to_obj(self, namespace, obj):
        for (key, val) in vars(namespace).items():
            if val != None:
                setattr(obj, key, val)

class BaseData(KickstartObject):
    def __init__(self, *args, **kwargs):
        if self.__class__ is BaseData:
            raise TypeError("BaseData is an abstract class.")

        KickstartObject.__init__(self, *args, **kwargs)
        self.lineno = 0

    def __str__(self):
        return ""

    def __call__(self, *args, **kwargs):
        for (key, val) in list(kwargs.items()):
            if hasattr(self, key):
                setattr(self, key, val)

class PartitionData(BaseData):
    def __init__(self, *args, **kwargs):
        BaseData.__init__(self, *args, **kwargs)

        self.end = kwargs.get("end", 0)
        self.fstype = kwargs.get("fstype", "")
        self.grow = kwargs.get("grow", False)
        self.maxSizeMB = kwargs.get("maxSizeMB", 0)
        self.format = kwargs.get("format", True)
        self.size = kwargs.get("size", None)
        self.start = kwargs.get("start", 0)
        self.mountpoint = kwargs.get("mountpoint", "")

    def _getArgsAsStr(self):
        retval = ""

        if hasattr(self, "end") and self.end != 0:
            retval += " --end=%s" % self.end
        if self.fstype != "":
            retval += " --fstype=\"%s\"" % self.fstype
        if self.grow:
            retval += " --grow"
        if self.maxSizeMB > 0:
            retval += " --maxsize=%d" % self.maxSizeMB
        if not self.format:
            retval += " --noformat"
        if self.size and self.size != 0:
            retval += " --size=%s" % self.size
        if hasattr(self, "start") and self.start != 0:
            retval += " --start=%s" % self.start

        return retval

    def __str__(self):
        retval = BaseData.__str__(self)
        retval += "part %s%s\n" % (self.mountpoint, self._getArgsAsStr())
        return retval

class PartitionCommand(KickstartCommand):
    commandName = "part"

    def __init__(self, *args, **kwargs):
        KickstartCommand.__init__(self, *args, **kwargs)

        self.op = self._getParser()

        self.partitions = kwargs.get("partitions", [])

        self.dataClass = PartitionData

    def __str__(self):
        retval = ""

        for part in self.partitions:
            retval += part.__str__()

        return retval

    def _getParser(self):
        def part_cb(value):
            if value.startswith("/dev/"):
                return value[5:]
            else:
                return value

        op = KSOptionParser()
        op.add_argument("--end", type=int)
        op.add_argument("--fstype", "--type", dest="fstype")
        op.add_argument("--grow", action="store_true", default=False)
        op.add_argument("--maxsize", dest="maxSizeMB", type=int)
        op.add_argument("--noformat", dest="format", action="store_false", default=True)
        op.add_argument("--size", type=int)
        op.add_argument("--start", type=int)

        return op

    def parse(self, args):
        (ns, extra) = self.op.parse_known_args(args=args, lineno=self.lineno)

        if len(extra) != 1:
            raise TypeError("Line %d: Mount point required for partition", self.lineno)
        elif any(arg for arg in extra if arg.startswith("-")):
            mapping = {"command": "partition", "options": extra}
            raise TypeError("Unexpected arguments to %(command)s command: %(options)s" % mapping)

        pd = self.dataClass()
        self.set_to_obj(ns, pd)
        pd.lineno = self.lineno
        pd.mountpoint=extra[0]

        # Check for duplicates in the data list.
        if pd.mountpoint != "swap" and pd in self.dataList():
            warnings.warn(_("A partition with the mountpoint %s has already been defined.") % pd.mountpoint)

        return pd

    def dataList(self):
        return self.partitions
