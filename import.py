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

import gzip
import json
import logging
import optparse
import os.path

import tinyarchive.database
import tinyback.generators
import tinyback.services

def parse_options():
    parser = optparse.OptionParser()

    parser.add_option("-d", "--debug", action="store_const", dest="loglevel",
        const=logging.DEBUG, default=logging.INFO, help="Enable debug output")
    parser.add_option("-s", "--database-directory", dest="database_directory",
        help="Database directory")

    options, args = parser.parse_args()
    if not args:
        parser.error("At least one input file is required")
    if not options.database_directory:
        parser.error("Option --database-directory is required")
    if not os.path.isdir(options.database_directory):
        parser.error("Database directory does not exist")

    return (options, args)

def import_file(metadata, data_file, database):
    log = logging.getLogger("import_file")
    log.debug("Importing %s from %s for service %s" % (metadata["id"], data_file, metadata["service"]))

    generator = tinyback.generators.factory(metadata["generator_type"], metadata["generator_options"])
    fileobj = gzip.GzipFile(data_file)

    for row in fileobj:
        assert row[-1] == "\n"
        code, url = row[:-1].split("|", 1)

        try:
            while code != next(generator):
                pass
            try:
                database.set(code, url)
            except Exception as e:
                log.fatal("Caught exception: %s" % e)
                return False
        except StopIteration:
            log.fatal("Task %s does not match generator" % metadata["id"])
            return False

    os.remove(data_file)
    return True

def main():
    options, files = parse_options()

    logging.basicConfig(level=options.loglevel,
        format="%(name)s: %(message)s")

    db_manager = tinyarchive.database.DBManager(options.database_directory)
    log = logging.getLogger("main")

    failed = 0
    log.info("Importing %i files" % len(files))
    for input_file in files:
        with open(input_file) as fileobj:
            metadata = json.load(fileobj)

        data_file = os.path.join(os.path.dirname(input_file), metadata["id"] + ".txt.gz")
        if not os.path.isfile(data_file):
            log.warn("Could not find data file for task %s" % metadata["id"])
            break

        if not import_file(metadata, data_file, db_manager.get(metadata["service"])):
            log.error("Error while importing file")
            failed += 1
        else:
            os.remove(input_file)
    else:
        log.info("Finished import with %i files failing import" % failed)

    db_manager.close()

if __name__ == "__main__":
    main()
