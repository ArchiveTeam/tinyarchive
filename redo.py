#!/usr/bin/env python

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
