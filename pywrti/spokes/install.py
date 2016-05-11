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

import time

from pywrti.ui import UIScreen, LabelWidget, TextboxWidget, ProcessWidget
from pywrti.storage import Storage
from pywrti.packages import Packages

class InstallSpoke(UIScreen):
    def __init__(self, app, title = 'Package Installation'):
        UIScreen.__init__(self, app, title)
        self._amount = 0

    def setup(self):
        self._process = ProcessWidget(65, 100)
        #self._process.setprocess(20)
        self.addWidget(self._process, {'padding': (0, 1, 0, 0)})
        self._label = LabelWidget("Wating for processing install packages")
        self.addWidget(self._label, {'padding': (0, 1, 0, 0)})
        self._info = TextboxWidget(65, 4, "", wrap = 1)
        self.addWidget(self._info, {'padding': (0, 1, 0, 0)})

        self.setup_instroot()
        self.setup_packages()

    def setup_partition(self, total):
        used = 0
        grow = 0
        left = 0

        for part in self.app.wrti.partitions:
            used += part.size
            if part.grow:
                grow += part.size

        if total > used:
            left= total - used

        for part in self.app.wrti.partitions:
            if part.grow:
                size = part.size + int(left * part.size / grow)
            else:
                size = part.size

            self.storage.add_partition(size, part.mountpoint, part.fstype)

    def setup_instroot(self):
        self.app.wrti.mount_source()
        self.app.wrti.parse_kickstart()

        if len(self.app.wrti.instdisks) > 0:
            disk = self.app.wrti.instdisks[0]
        else:
            disk = 'sda'

        device = self.app.wrti.devicetree.getdiskbyname(disk)
        totalsize = int(device.size) / 2048 - 1

        self.storage = Storage('/dev/%s' % disk, self.app.wrti.instroot)
        self.setup_partition(totalsize)

    def setup_packages(self):
        self.packages = Packages(self.app.wrti.reporoot, self.app.wrti.instroot)

    def install_package(self, package):
        total = self.packages.total()
        self._amount = self._amount + 1
        self._process.setprocess(int(self._amount * 100 / total))

        self._label.setText("Packages completed %d of %d" % (self._amount, total))
        self._info.setText("Installing %s_%s (%s)\n%s" % (package['name'],
                               package['version'], package['size'], package['description']))
        self.redraw()
        self.refresh()

        self.packages.install(package['name'])

    def cleanup(self):
        self.app.wrti.umount_source()

    def run(self, args = None):
        self.storage.mount()
        self.packages.setup()

        pkgs = self.app.wrti.packages

        # libc and kernel must be install
        for pkg in ['libc', 'kernel']:
            if not pkg in pkgs:
                pkgs.append(pkg)

        self.packages.update(pkgs)

        # install libc package
        package = self.packages.packages['libc']
        self.install_package(package)
        # install kernel package
        package = self.packages.packages['kernel']
        self.install_package(package)

        for pkg in self.packages.dependencies:
            package = self.packages.packages[pkg]
            if not 'name' in package:
                print 'package %s not found' % pkg
                continue

            if pkg in ['libc', 'kernel']:
                continue

            self.install_package(package)

            time.sleep(1)

        self.packages.postinst()
        self.packages.create_bootconfig(self.storage.rootdev, self.storage.rootfs)

        self.packages.cleanup()
        self.storage.unmount()
        self.cleanup()

if __name__ == "__main__":
    storage = Storage('/dev/sda', '/mnt/sysimage')
    storage.add_partition(100, '/boot', 'ext4')
    storage.add_partition(200, '/', 'ext4')
    storage.add_partition(200, '/var', 'ext4')
    storage.mount()
    
    packages = Packages('/mnt/isodir', '/mnt/sysimage')
    packages.setup()
    packages.update(['base-files',
                'busybox',
                'dnsmasq',
                'dropbear',
                'firewall',
                'fstools',
                'ip6tables',
                'iptables',
                'kernel',
                'kmod-e1000',
                'kmod-e1000e',
                'libc',
                'libgcc',
                'mtd',
                'netifd',
                'odhcp6c',
                'odhcpd',
                'opkg',
                'ppp',
                'ppp-mod-pppoe',
                'uci'])
    packages.cleanup()
    
    storage.unmount()
