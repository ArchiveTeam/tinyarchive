#!/usr/bin/env python

import sys
import tinyarchive.database

db_manager = tinyarchive.database.DBManager("database")
db = db_manager.get("isgd")

try:
    for line in sys.stdin:
        assert line[-1] == "\n"
        line = line[:-1]
        code, url = line.split("|", 1)
        db.set(code, url)
finally:
    db_manager.close()
