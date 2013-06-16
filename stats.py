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

import tinyarchive.database


if len(sys.argv) != 2:
    print "%s <database directory>" % sys.argv[0]
    sys.exit(1)

count = {}

database_manager = tinyarchive.database.DBManager(sys.argv[1])
for service in database_manager.list():
    database = database_manager.get(service)
    count[service] = len(database)
database_manager.close()

print json.dumps(count, sort_keys=True, indent=4)
