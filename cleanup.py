#!/usr/bin/env python

import json
import uuid

import tinyarchive.tracker

tracker = tinyarchive.tracker.Tracker("http://tracker.tinyarchive.org/v1/")
tracker.admin_cleanup()
