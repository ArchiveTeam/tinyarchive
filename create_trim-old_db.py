#!/usr/bin/env python

from bsddb3 import db
import logging
import optparse
import os.path
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

    mappingdb = db.DB()
    flags = db.DB_CREATE | db.DB_TRUNCATE
    mappingdb.open(os.path.abspath(options.output_file), dbtype=db.DB_HASH, flags=flags)

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
            if real_url:
                mapping = code + "|" + real_url
            else:
                mapping = code
            mappingdb.put(internal_code, mapping, flags=db.DB_NOOVERWRITE)

    mappingdb.close()
    db_manager.close()

if __name__ == "__main__":
    main()
