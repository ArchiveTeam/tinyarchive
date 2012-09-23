#!/usr/bin/env python

import os.path
import sys
import time

import tinyarchive.database
import tinyback.services

database_directory = sys.argv[1]
service = sys.argv[2]
filename = sys.argv[3]

print("DB dir:      %s" % database_directory)
print("Service:     %s" % service)
print("Filename:    %s" % filename)

db_manager = tinyarchive.database.DBManager(database_directory)
database = db_manager.get(service)

for line in sys.stdin:
    assert line[-1] == "\n"
    code, url = line[:-1].split("|", 1)
    try:
        database.set(code, url)
    except ValueError as e:
        print e
        database.delete(code)
        try:
            real_url = tinyback.services.factory(service).fetch(code)
        except tinyback.exceptions.NoRedirectException:
            print "No real URL"
        else:
            print "Real URL: %s" % real_url
            database.set(code, real_url)

db_manager.close()
