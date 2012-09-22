#!/usr/bin/env python

import json
import uuid

import tinyarchive.tracker
import tinyback.generators

def count_sequence(charset, count, start):
    for i, code in enumerate(tinyback.generators.factory("sequence", {"charset": charset, "start": start, "stop": ""})):
        if i == count - 1:
            return code

service = "tinyurl"

if service == "bitly":
    generator_type = "chain"
    generator_options = {
        "count": 600,
        "length": 6,
        "charset": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "seed": str(uuid.uuid4())
    }
elif service == "isgd":
    generator_type = "chain"
    generator_options = {
        "count": 300,
        "length": 5,
        "charset": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    }
elif service == "tinyurl":
    generator_type = "chain"
    generator_options = {
        "charset": "0123456789abcdefghijklmnopqrstuvwxyz",
        "start": "a00000"
    }
    generator_options["stop"] = count_sequence(generator_options["charset"], 2, generator_options["start"])
elif service == "ur1ca":
    generator_type = "sequence"
    generator_options = {
        "charset": "0123456789abcdefghijklmnopqrstuvwxyz",
        "start": "",
        "stop":  ""
    }

if generator_type == "chain":
    generator_options["seed"] = str(uuid.uuid4())

tracker = tinyarchive.tracker.Tracker("http://tracker.tinyarchive.org/v1/")
print tracker.admin_create(service, generator_type, generator_options)
