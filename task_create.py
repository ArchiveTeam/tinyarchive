#!/usr/bin/env python

import json
import uuid

import tinyarchive.tracker

service = "isgd"
generator_type = "chain"

if generator_type == "chain":
    generator_options = {
        "count": 10000,
        "length": 5,
        "charset": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_",
        "seed": str(uuid.uuid4())
    }
elif generator_type == "sequence":
    generator_options = {
        "start": "0",
        "stop":  "z",
        "charset": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    }

tracker = tinyarchive.tracker.Tracker("http://tracker.tinyarchive.org/v1/")
print tracker.admin_create(service, generator_type, generator_options)
