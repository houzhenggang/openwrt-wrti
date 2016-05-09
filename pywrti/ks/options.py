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

from argparse import ArgumentParser

class KSOptionParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        ArgumentParser.__init__(self, add_help=False, conflict_handler="resolve", *args, **kwargs)
        self.lineno = None

    def add_argument(self, *args, **kwargs):
        action = ArgumentParser.add_argument(self, *args, **kwargs)
        return action

    def error(self, message):
        raise TypeError()
        if self.lineno != None:
            raise TypeError("Line %d: %s" % (self.lineno, message))
        else:
            raise TypeError(message)

    def exit(self, status=0, message=None):
        pass

    def parse_args(self, *args, **kwargs):
        if "lineno" in kwargs:
            self.lineno = kwargs.pop("lineno")

        return ArgumentParser.parse_args(self, *args, **kwargs)

    def parse_known_args(self, *args, **kwargs):
        if "lineno" in kwargs:
            self.lineno = kwargs.pop("lineno")

        return ArgumentParser.parse_known_args(self, *args, **kwargs)
