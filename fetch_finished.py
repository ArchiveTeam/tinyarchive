#!/usr/bin/env python

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
    parser.add_options("-o", "--output-directory", dest="output_directory",
        default=".", help="Output directory")

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

if __name__ == "__main__":
    main()
