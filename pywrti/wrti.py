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
import subprocess
import shlex

from pywrti.storage import DeviceTree
from pywrti.ks.parser import KickstartParser

class Wrti(object):
    def __init__(self):
        self._devicetree = DeviceTree()
        self._instdisks = []
        self._reporoot = '/mnt/isodir'
        self._instroot = '/mnt/sysimage'
        self._imgdevice = 'sr0'
        self._kickstart = None

        self.packages = []
        self.partitions = []

        self.cmdlineDict = {}

    def getDisks(self):
        self._devicetree.reset()
        return self._devicetree.disks

    @property
    def devicetree(self):
        return self._devicetree

    @property
    def reporoot(self):
        return self._reporoot

    @property
    def instroot(self):
        return self._instroot

    @property
    def instdisks(self):
        return self._instdisks

    @instdisks.setter
    def instdisks(self, d):
        self._instdisks = d

    def parse_cmdline(self):
        proc_cmdline = open("/proc/cmdline", "r").read()
        args = shlex.split(proc_cmdline, comments=True)

        for i in args:
            try:
                (key, val) = i.split("=", 1)
            except:
                key = i
                val = None

            self.cmdlineDict[key] = val

        if 'ks' in self.cmdlineDict:
            self.parse_image_source(self.cmdlineDict['ks'])

    def parse_image_source(self, ks):
        args = ks.split(':')

        self._kickstart = args[-1]

        if len(args) == 2:
            if args[0] == 'cdrom':
                self._imgdevice = 'sr0'
            else:
                self._imgdevice = args[0]
        elif len(args) == 3 and args[0] == 'hd':
            self._imgdevice = args[1]
        else:
            print "ks parameter error!"

        if self._imgdevice.startswith("/dev/"):
                self._imgdevice = self._imgdevice[5:]

        if not os.path.exists('/dev/%s' % self._imgdevice):
            print "source not found!"
            self._kickstart = None
            self._imgdevice = 'sr0'
        else:
            subprocess.call(["/usr/sbin/modprobe", 'sr_mod'])

    def mount_source(self):
        self.parse_cmdline()

        if not os.path.exists(self._reporoot):
            os.makedirs(self._reporoot)

        if os.path.exists('/dev/%s' % self._imgdevice):
            subprocess.call(["/bin/mount", '/dev/%s' % self._imgdevice, self._reporoot])

    def umount_source(self):
        try:
            subprocess.call(["/bin/umount", self._reporoot])
        except:
            pass

    def parse_kickstart(self):
        if self._kickstart:
            self.ksdata = KickstartParser()
            self.ksdata.readKickstart('%s/%s' % (self._reporoot, self._kickstart))

            self.packages = self.ksdata.get("packages",  "packageList")
            self.partitions = self.ksdata.get("part", "partitions")

