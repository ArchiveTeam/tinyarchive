#!/usr/bin/env python

# TinyArchive - A tiny web archive
# Copyright (C) 2012 David Triendl
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
import logging
import optparse
import os.path

import tinyarchive.tracker

def parse_options():
    parser = optparse.OptionParser()

    parser.add_option("-t", "--tracker", dest="tracker",
        help="Connect to tracker at URL", metavar="URL")
    parser.add_option("-d", "--debug", action="store_const", dest="loglevel",
        const=logging.DEBUG, default=logging.INFO, help="Enable debug output")
    parser.add_option("-o", "--output-directory", dest="output_directory",
        default=".", help="Output directory")
    parser.add_option("-c", "--cleanup", action="store_true", dest="cleanup",
        help="Perform cleanup afterwards")

    options, args = parser.parse_args()
    if args:
        parser.error("Unexpected argument %s" % args[0])
    if not options.tracker:
        parser.error("Missing required option --tracker")
    if not os.path.isdir(options.output_directory):
        parser.error("Output directory does not exist")

    return options

def main():
    options = parse_options()

    logging.basicConfig(level=options.loglevel,
        format="%(name)s: %(message)s")

    tracker = tinyarchive.tracker.Tracker(options.tracker)

    for task in tracker.admin_list():
        prefix = os.path.join(options.output_directory, task["id"])
        if os.path.exists(prefix + ".json") or os.path.exists(prefix + ".txt.gz"):
            raise Exception("Target file already exists for task %s" % task["id"])

        with open(prefix + ".json", "w") as fileobj:
            json.dump(task, fileobj, sort_keys=True, indent=4)
        with open(prefix + ".txt.gz", "w") as fileobj:
            fileobj.write(tracker.admin_fetch(task))

        tracker.admin_delete(task)

    if options.cleanup:
        tracker.admin_cleanup()

if __name__ == "__main__":
    main()
