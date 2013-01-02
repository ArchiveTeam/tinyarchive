#!/usr/bin/env python

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
