#!/usr/bin/env python

import gzip
import json
import logging
import optparse
import os.path
import sqlite3
import time

import tinyarchive.database
import tinyback.generators

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
    print("Importing %s from %s" % (metadata["id"], data_file))

    generator = tinyback.generators.factory(metadata["generator_type"], metadata["generator_options"])
    fileobj = gzip.GzipFile(data_file)

    for row in fileobj:
        assert row[-1] == "\n"
        code, url = row[:-1].split("|", 1)

        try:
            while code != next(generator):
                pass
            database.set(code, url)
        except StopIteration:
            print("Task %s does not match generator" % metadata["id"])
            return False

    return True

def main():
    options, files = parse_options()

    logging.basicConfig(level=options.loglevel,
        format="%(name)s: %(message)s")

    db_manager = tinyarchive.database.DBManager(options.database_directory)
    import_db = sqlite3.connect(os.path.join(options.database_directory, "imports.sqlite"))

    for input_file in files:
        with open(input_file) as fileobj:
            metadata = json.load(fileobj)

        data_file = os.path.join(os.path.dirname(input_file), metadata["id"] + ".txt.gz")
        if not os.path.isfile(data_file):
            print("Could not find data file for task %s" % metadata["id"])
            sys.exit(1)

        cursor = import_db.cursor()
        cursor.execute("SELECT id FROM service WHERE name = ?", (metadata["service"], ))
        row = cursor.fetchone()
        if row:
            service_id = row[0]
        else:
            cursor.execute("INSERT INTO service (name) VALUES (?)", (metadata["service"], ))
            service_id = cursor.lastrowid

        cursor.execute("INSERT INTO import (imported, status, service_id, filename, generator_type, generator_options) VALUES (?, ?, ?, ?, ?, ?)", (
            int(time.time()),
            "pending",
            service_id,
            os.path.basename(data_file),
            metadata["generator_type"],
            json.dumps(metadata["generator_options"])))
        import_id = cursor.lastrowid
        import_db.commit()
        cursor.close()

        if import_file(metadata, data_file, db_manager.get(metadata["service"])):
            status = "done"
        else:
            status = "conflict"

        cursor = import_db.cursor()
        cursor.execute("Update import SET status = ? WHERE id = ?", (status, import_id))
        import_db.commit()
        cursor.close()

    import_db.close()
    db_manager.close()

if __name__ == "__main__":
    main()
