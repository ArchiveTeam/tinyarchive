#!/usr/bin/env python

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
