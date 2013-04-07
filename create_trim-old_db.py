#!/usr/bin/env python

from bsddb3 import db
import logging
import optparse
import os
import os.path
import sqlite3
from urlparse import urlparse

import tinyarchive.database

def parse_options():
    parser = optparse.OptionParser()

    parser.add_option("-d", "--debug", action="store_const", dest="loglevel",
        const=logging.DEBUG, default=logging.INFO, help="Enable debug output")
    parser.add_option("-s", "--database-directory", dest="database_directory",
        help="Database directory")
    parser.add_option("-o", "--output-file", dest="output_file",
        help="Database file for trim-old.tinyarchive.org")

    options, args = parser.parse_args()
    if not options.database_directory:
        parser.error("Option --database-directory is required")
    if not os.path.isdir(options.database_directory):
        parser.error("Database directory does not exist")
    if not options.output_file:
        parser.error("Option --output_file is requrired")

    return options

def main():
    options = parse_options()

    logging.basicConfig(level=options.loglevel, format="%(name)s: %(message)s")

    db_manager = tinyarchive.database.DBManager(options.database_directory)

    trim_old = db_manager.get("trim")
    trim_new = db_manager.get("trimnew")

    if os.path.exists(options.output_file):
        os.unlink(options.output_file)
    mappingdb = sqlite3.connect(options.output_file)
    cursor = mappingdb.cursor()
    cursor.execute("CREATE TABLE trim_link (internal_code TEXT, trim_code TEXT, url BLOB)")

    for (code, url) in trim_new:
        try:
            parsed_url = urlparse(url)
        except:
            continue
        if parsed_url.hostname == "trim-old.tinyarchive.org":
            internal_code = parsed_url.path[1:]
            if not internal_code:
                continue
            real_url = trim_old.get(code)
            if not real_url:
                continue
            cursor.execute("INSERT INTO trim_link VALUES (?, ?, ?)", (internal_code, code, buffer(real_url)))

    cursor.execute("CREATE INDEX trim_link_internal_code_idx ON trim_link(internal_code)")
    cursor.execute("VACUUM")
    mappingdb.commit()
    cursor.close()
    mappingdb.close()

    db_manager.close()

if __name__ == "__main__":
    main()
