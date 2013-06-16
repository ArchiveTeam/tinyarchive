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

import logging
import optparse
import os
import os.path
import subprocess

import tinyarchive.database

def parse_options():
    parser = optparse.OptionParser()

    parser.add_option("-d", "--debug", action="store_const", dest="loglevel",
        const=logging.DEBUG, default=logging.INFO, help="Enable debug output")
    parser.add_option("-s", "--database-directory", dest="database_directory",
        help="Database directory")
    parser.add_option("-r", "--release", dest="release",
        help="Directory containing the release")
    parser.add_option("-m", "--map", dest="code_to_file_map",
        help="JSON file containing code to file map")

    options, args = parser.parse_args()
    if not options.database_directory:
        parser.error("Option --database-directory is required")
    if not os.path.isdir(options.database_directory):
        parser.error("Database directory does not exist")
    if not options.release:
        parser.error("Option --release is requrired")
    if not os.path.isdir(options.release):
        parser.error("Release directory does not exist")
    if not options.code_to_file_map:
        parser.error("Option --map is required")
    if not os.path.isfile(options.code_to_file_map):
        parser.error("Code to file map does not exist")

    return options

def import_file(filename, db):
    s = subprocess.Popen(["xzcat", filename], stdout=subprocess.PIPE)
    for line in s.stdout:
        assert line[-1] == "\n"
        code, url = line[:-1].split("|", 1)
        db.set(code, url)
    assert s.wait() == 0

def main():
    options = parse_options()

    logging.basicConfig(level=options.loglevel, format="%(name)s: %(message)s")
    log = logging.getLogger("release_import")

    db_manager = tinyarchive.database.DBManager(options.database_directory)

    code_to_file_map = tinyarchive.utils.CodeToFileMap(options.code_to_file_map)

    directory = os.path.abspath(options.release)
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            if not filename.endswith(".txt.xz"):
                log.info("Skipping file %s" % filename)
                continue
            release_filename = os.path.join(dirpath, filename)[len(directory)+1:]
            try:
                service = code_to_file_map.get_service(release_filename[:-7])
            except ValueError:
                log.error("Could not get mapping for file %s" % filename)
                continue
            log.debug("Importing file %s for service %s" % (filename, service))
            db = db_manager.get(service)
            import_file(os.path.join(dirpath, filename), db)

    db_manager.close()

if __name__ == "__main__":
    main()
