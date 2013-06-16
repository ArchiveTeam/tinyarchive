#!/usr/bin/env python

# TinyArchive - A tiny web archive
# Copyright (C) 2013 David Triendl
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

import csv
import logging
import sys

import tinyarchive.database

logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

db_manager = tinyarchive.database.DBManager(sys.argv[1])
db = db_manager.get("tnyim")

for line in csv.reader(sys.stdin, delimiter=';', quotechar='"', escapechar='\\'):
    if len(line) == 0:
        continue
    code = line[0]
    url = line[1]
    db.set(code, url)

db_manager.close()
