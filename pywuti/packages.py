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
import re
import subprocess

class Packages(object):
    def __init__(self, reporoot, instroot):
        self._reporoot = reporoot
        self._instroot = instroot

        self._source = '/dev/sr0'
        self._repoconf = '/tmp/repositories.conf'

        self.packages = {}

    def setup_repositories(self):
        s = ""
        for repo in ['base', 'kernel', 'luci', 'packages']:
            s += "src/gz %s file://%s/packages/%s\n" % (repo, self._reporoot, repo)
        cfg = open(self._repoconf, "w")
        cfg.write(s)
        cfg.close()

    def setup(self):
        if not os.path.exists(self._reporoot):
            os.makedirs(self._reporoot)
        
        if os.path.exists('/dev/sr0'):
            subprocess.call(["/bin/mount", self._source, self._reporoot])

        self.setup_repositories()
        
        if not os.path.exists(os.path.join(self._instroot, 'tmp')):
            os.makedirs(os.path.join(self._instroot, 'tmp'))

        if not os.path.exists(os.path.join(self._instroot, 'var', 'lock')):
            os.makedirs(os.path.join(self._instroot, 'var', 'lock'))

        if not os.path.exists('/tmp/ipkgtmp'):
            os.makedirs('/tmp/ipkgtmp')

        if not os.path.exists('/tmp/dl'):
            os.makedirs('/tmp/dl')

        self._cmdbase = "IPKG_NO_SCRIPT=1 IPKG_TMP='/tmp/ipkgtmp' "
        self._cmdbase += "IPKG_INSTROOT='%s' IPKG_CONF_DIR='/tmp' " % self._instroot
        self._cmdbase += "IPKG_OFFLINE_ROOT='%s' " % self._instroot
        self._cmdbase += "/bin/opkg -f %s " % self._repoconf
        self._cmdbase += "--force-depends --force-overwrite --force-postinstall "
        self._cmdbase += "--cache /tmp/dl --lists-dir /tmp/dl "
        self._cmdbase += "--offline-root %s " % self._instroot
        self._cmdbase += "--add-dest root:/ --add-arch all:100 --add-arch x86_64:200"

        self.execute_shell("%s update" % self._cmdbase)

    def cleanup(self):
        try:
            subprocess.call(["/bin/umount", self._reporoot])
        except:
            pass

    def execute_shell(self, args):
        if isinstance(args, basestring):
            print args
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
        shellOut = shelllog.communicate()[0]
    
        lines = shellOut.split("\n")
        lines = lines[0:-1]

        return lines

    def package_from_file(self, pkg):
        cmd = "find %s/packages/ -name %s_[0-9]*" % (self._reporoot, pkg)
        lines = self.execute_shell(cmd)

        pkginfo = {}
        if len(lines) == 1:
            pkginfo['name'] = pkg
            pkginfo['size'] = os.path.getsize(lines[0])
            pkginfo['file'] = lines[0]
            pkginfo['version'] = lines[0][len(pkg):-4]
            pkginfo['description'] = pkg
            pkginfo['depends'] = []

        return pkginfo

    def opkg_info(self, pkg):
        if pkg in ['kernel', 'libc']:
            return self.package_from_file(pkg)

        pkginfo = {}
        isdescription = False
        for line in self.execute_shell("%s info %s" % (self._cmdbase, pkg)):
            if re.match("^Package:", line):
                pkginfo['name'] = line.split(' ')[1]
            elif re.match("^Version:", line):
                pkginfo['version'] = line.split(' ')[1]
            elif re.match("^Depends:", line):
                pkginfo['depends'] = line[9:].split(', ')
            elif re.match("^Section:", line):
                pkginfo['section'] = line.split(' ')[1]
            elif re.match("^Size:", line):
                pkginfo['size'] = line.split(' ')[1]
            elif re.match("^Description:", line):
                pkginfo['description'] = line.split(' ')[1]
                isdescription = True
            elif isdescription is True:
                pkginfo['description'] += line

        return pkginfo

    def check_opkg_info(self, package):
        self.packages[package] = self.opkg_info(package)
        if 'depends' in self.packages[package]:
            for dep in self.packages[package]['depends']:
                dep = dep.split(' ')[0]
                if dep in self.packages:
                    continue
                self.check_opkg_info(dep)

    def update(self, packages):
        for package in packages:
            self.check_opkg_info(package)

    def download(self, package):
        pass

    def total(self):
        return len(self.packages)

    def install(self, package):
        pass