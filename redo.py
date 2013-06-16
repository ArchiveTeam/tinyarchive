#!/usr/bin/env python

# TinyArchive - A tiny web archive
# Copyright (C) 2012 David Triendl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import sys

import tinyarchive.tracker

tracker = tinyarchive.tracker.Tracker("http://tracker.tinyarchive.org/v1/")

for i, filename in enumerate(sys.argv):
    if i == 0:
        continue
    fileobj = open(filename)
    data = json.load(fileobj)
    fileobj.close()
    print tracker.admin_create(data["service"], data["generator_type"], data["generator_options"])
