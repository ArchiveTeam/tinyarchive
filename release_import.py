#!/usr/bin/env python

import os.path
import sys
import sqlite3
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

import_db = sqlite3.connect(os.path.join(database_directory, "imports.sqlite"))
cursor = import_db.cursor()

cursor.execute("SELECT id FROM service WHERE name = ?", (service, ))
row = cursor.fetchone()
if row:
    service_id = row[0]
else:
    cursor.execute("INSERT INTO service (name) VALUES (?)", (service, ))
    service_id = cursor.lastrowid

cursor.execute("INSERT INTO import (imported, status, service_id, filename) VALUES (?, ?, ?, ?)", (
    int(time.time()),
    "pending",
    service_id,
    filename))
import_id = cursor.lastrowid
import_db.commit()
cursor.close()

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

cursor = import_db.cursor()
cursor.execute("Update import SET status = ? WHERE id = ?", ("done", import_id))
import_db.commit()
cursor.close()
