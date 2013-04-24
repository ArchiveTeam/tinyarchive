#!/usr/bin/env python

import os.path
import sys
import time

import tinyarchive.database
import tinyback.services

database_directory = sys.argv[1]
service = sys.argv[2]

print("DB dir:      %s" % database_directory)
print("Service:     %s" % service)

db_manager = tinyarchive.database.DBManager(database_directory)
database = db_manager.get(service)

for line in sys.stdin:
    assert line[-1] == "\n"
    code, url = line[:-1].split("|", 1)
    database.set(code, url)

db_manager.close()
