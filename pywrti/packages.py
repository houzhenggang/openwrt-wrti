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

        #self._source = '/dev/sr0'
        self._repoconf = '/tmp/repositories.conf'

        self.packages = {}
        self.dependencies = []

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
        
        self.setup_repositories()

        if not os.path.exists(os.path.join(self._instroot, 'tmp')):
            os.makedirs(os.path.join(self._instroot, 'tmp'))

        # NOTE: first boot need /var is link to /tmp
        subprocess.call(["ln", "-s", "tmp", "%s/var" % self._instroot])

        if not os.path.exists(os.path.join(self._instroot, 'var', 'lock')):
            os.makedirs(os.path.join(self._instroot, 'var', 'lock'))

        if not os.path.exists(os.path.join(self._instroot, 'boot')):
            os.makedirs(os.path.join(self._instroot, 'boot'))

        if not os.path.exists('/tmp/ipkgtmp'):
            os.makedirs('/tmp/ipkgtmp')

        if not os.path.exists('/tmp/dl'):
            os.makedirs('/tmp/dl')

        self._cmdbase = "IPKG_NO_SCRIPT=1 IPKG_TMP='/tmp/ipkgtmp' "
        self._cmdbase += "IPKG_INSTROOT='%s' IPKG_CONF_DIR='/tmp' " % self._instroot
        self._cmdbase += "IPKG_OFFLINE_ROOT='%s' " % self._instroot
        self._cmdbase += "/bin/opkg -f %s " % self._repoconf
        #self._cmdbase += "--force-depends --force-overwrite --force-postinstall "
        #self._cmdbase += "--cache /tmp/dl --lists-dir /tmp/dl "
        self._cmdbase += "--offline-root %s " % self._instroot
        self._cmdbase += "--add-dest root:/ --add-arch all:100 --add-arch x86_64:200"

        self.execute_shell("%s update" % self._cmdbase)

    def cleanup(self):
        #try:
        #    subprocess.call(["/bin/umount", self._reporoot])
        #except:
        pass

    def execute_shell(self, args):
        if isinstance(args, basestring):
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
        shellOut = shelllog.communicate()[0]
    
        lines = shellOut.split("\n")
        lines = lines[0:-1]

        return lines

    def package_from_file(self, pkg):
        sinfo = {
            'kernel': 'Virtual kernel package',
            'libc': 'GCC support library'
        }

        cmd = "find %s/packages/ -name %s_[0-9]*" % (self._reporoot, pkg)
        lines = self.execute_shell(cmd)

        pkginfo = {}
        if len(lines) >= 1:
            pkginfo['name'] = pkg
            pkginfo['size'] = os.path.getsize(lines[0])
            pkginfo['file'] = lines[0]
            pkginfo['version'] = lines[0][len(pkg):-4]
            pkginfo['depends'] = []

            if pkg in sinfo:
                pkginfo['description'] = sinfo[pkg]
            else:
                pkginfo['description'] = pkg

        return pkginfo

    def opkg_info(self, pkg):
        if pkg in ['kernel', 'libc']:
            return self.package_from_file(pkg)

        pkginfo = {}
        isdescription = False
        for line in self.execute_shell("%s info %s" % (self._cmdbase, pkg)):
            if re.match("^Package:", line):
                pkginfo['name'] = line[9:].strip()
            elif re.match("^Version:", line):
                pkginfo['version'] = line[9:].strip()
            elif re.match("^Depends:", line):
                pkginfo['depends'] = line[9:].split(', ')
            elif re.match("^Section:", line):
                pkginfo['section'] = line[9:].strip()
            elif re.match("^Size:", line):
                pkginfo['size'] = line[6:].strip()
            elif re.match("^Filename:", line):
                pkginfo['file'] = line[10:].strip()
            elif re.match("^Description:", line):
                pkginfo['description'] = line[12:].strip()
                isdescription = True
            elif isdescription is True:
                pkginfo['description'] += " %s" % line.strip()

        return pkginfo

    def check_opkg_info(self, package):
        pkginfo = self.opkg_info(package)
        if 'depends' in pkginfo:
            for dep in pkginfo['depends']:
                dep = dep.split(' ')[0]
                if dep in self.packages:
                    continue
                self.check_opkg_info(dep)
        self.packages[package] = pkginfo

        if not package in self.dependencies:
            self.dependencies.append(package)

    def update(self, packages):
        for package in packages:
            self.check_opkg_info(package)

    def download(self, package):
        pass

    def total(self):
        return len(self.packages)

    def install(self, package):
        if isinstance(package, basestring):
            if package in ['kernel', 'libc']:
                self.execute_shell("%s install %s" % (self._cmdbase, self.packages[package]['file']))
            else:
                self.execute_shell("%s install %s" % (self._cmdbase, package))
        else:
            package.remove('kernel')
            package.remove('libc')
            self.execute_shell("%s install %s" % (self._cmdbase, ' '.join(package)))

    def postinst(self):
        cmd = "cd %s; " % self._instroot
        cmd += "for script in ./usr/lib/opkg/info/*.postinst; "
        cmd += "do IPKG_INSTROOT=%s $(which bash) $script; done" % self._instroot
        self.execute_shell(cmd)
        cmd = "rm -f %s/usr/lib/opkg/info/*.postinst" % self._instroot
        self.execute_shell(cmd)

    def _create_grub_devices(self, dev):
        grubdir = os.path.join(self._instroot, 'boot', 'grub')
        if not os.path.exists(grubdir):
            os.makedirs(grubdir)

        devmap = "(hd%-d) %s\n" % (0, dev)
        cfg = open("%s/device.map" % grubdir, "w")
        cfg.write(devmap)
        cfg.close()

    def _install_grub(self, root):
        grubdir = os.path.join(self._instroot, 'boot', 'grub')

        cfg = "serial --unit=0 --speed=115200 --word=8 --parity=no --stop=1 --rtscts=off\n"
        cfg += "terminal_input console serial; terminal_output console serial\n\n"
        cfg += "set default=\"0\"\n"
        cfg += "set timeout=\"5\"\n"
        cfg += "set root='(hd0,msdos1)'\n\n"
        cfg += "menuentry \"OpenWrt\" {\n"
        cfg += "    linux /boot/vmlinuz root=%s rootfstype=ext4 rootwait console=tty0 console=ttyS0,115200n8 noinitrd\n" % root
        cfg += "}\n"

        grub = open("%s/grub.cfg" % grubdir, "w")
        grub.write(cfg)
        grub.close()

        cmd = "/usr/sbin/grub-bios-setup --device-map=\"%s/device.map\" " % grubdir
        cmd += "-d /usr/lib/grub/i386-pc -r \"hd0,msdos1\" /dev/sda"
        self.execute_shell(cmd)

    def create_bootconfig(self, dev = '/dev/sda', root = '/dev/sda1'):
        self.execute_shell("cp %s/isolinux/vmlinuz %s/boot/" % (self._reporoot, self._instroot))
        
        self._create_grub_devices(dev)

        self._install_grub(root)
