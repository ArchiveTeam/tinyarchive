#!/usr/bin/env python

# TinyArchive - A tiny web archive
# Copyright (C) 2012-2013 David Triendl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    if tinyarchive.utils.shortcode_compare(start, stop) > 0:
        raise ValueError("Start must not be bigger than stop")

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

def chain_multiple(tracker, service, charset, length, count, number_of_tasks):
    generator_options = {
        "charset": charset,
        "count": count,
        "length": length
    }
    for i in range(number_of_tasks):
        generator_options["seed"] = str(uuid.uuid4())
        print tracker.admin_create(service, "chain", generator_options)

tracker = tinyarchive.tracker.Tracker("http://urlteam.terrywri.st/")
