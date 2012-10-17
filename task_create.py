#!/usr/bin/env python

import json
import uuid

import tinyarchive.tracker
import tinyarchive.utils
import tinyback.generators

def count_sequence(charset, count, start):
    for i, code in enumerate(tinyback.generators.factory("sequence", {"charset": charset, "start": start, "stop": ""})):
        if i == count - 1:
            return code

def sequence_from_to(tracker, service, charset, start, stop, count):
    generator_options = {
        "charset": charset,
        "start": start,
        "stop": None
    }
    while generator_options["stop"] != stop:
        generator_options["stop"] = count_sequence(generator_options["charset"], count, generator_options["start"])
        if tinyarchive.utils.shortcode_compare(generator_options["stop"], stop) > 0:
            generator_options["stop"] = stop
        print tracker.admin_create(service, "sequence", generator_options)
        generator_options["start"] = generator_options["stop"]

def chain_multiple(tracker, service, charset, length, count):
    generator_options = {
        "charset": charset,
        "count": count,
        "length": length
    }
    for i in range(count):
        generator_options["seed"] = str(uuid.uuid4())
        print tracker.admin_create(service, "chain", generator_options)

tracker = tinyarchive.tracker.Tracker("http://tracker.tinyarchive.org/v1/")
