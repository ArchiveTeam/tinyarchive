#!/usr/bin/env python

import json
import logging
import optparse
import os
import os.path

import tinyarchive.database

def parse_options():
    parser = optparse.OptionParser()

    parser.add_option("-d", "--debug", action="store_const", dest="loglevel",
        const=logging.DEBUG, default=logging.INFO, help="Enable debug output")
    parser.add_option("-s", "--database-directory", dest="database_directory",
        help="Database directory")
    parser.add_option("-o", "--old-release", dest="old_release",
        help="Directory containing old release")
    parser.add_option("-n", "--new-release", dest="new_release",
        help="Directory containing new release")
    parser.add_option("-m", "--map", dest="code_to_file_map",
        help="JSON file containing code to file map")

    options, args = parser.parse_args()
    if not options.database_directory:
        parser.error("Option --database-directory is required")
    if not os.path.isdir(options.database_directory):
        parser.error("Database directory does not exist")
    if not options.old_release:
        parser.error("Option --old-release is requrired")
    if not os.path.isdir(options.old_release):
        parser.error("Old release directory does not exist")
    if not options.new_release:
        parser.error("Option --new-release is requrired")
    if not os.path.isdir(options.new_release):
        parser.error("New release directory does not exist")
    if not options.code_to_file_map:
        parser.error("Option --map is required")
    if not os.path.isfile(options.code_to_file_map):
        parser.error("Code to file map does not exist")

    return options

def load_directories(directory):
    directory = os.path.abspath(directory)
    files = set()
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            files.add(os.path.join(dirpath, filename)[len(directory)+1:])
    return files

def main():
    options = parse_options()

    logging.basicConfig(level=options.loglevel, format="%(name)s: %(message)s")

    db_manager = tinyarchive.database.DBManager(options.database_directory)

    old_release_files = load_directories(options.old_release)
    code_to_file_map = tinyarchive.utils.CodeToFileMap(options.code_to_file_map)

    for service in db_manager.list():
        if service in ["owly"]:
            continue
        db = db_manager.get(service)
        mapping = None
        output = None
        for (key, value) in db:
            if mapping == None or not code_to_file_map.check_mapping(mapping, key):
                if output:
                    output.close()
                mapping = code_to_file_map.get_mapping(service, key)
                files.remove(mapping["file"])
                output = tinyarchive.utils.OutputFile(options.old_release, options.new_release, mapping["file"])
            output.write(key, value)
        if output:
            output.close()

    print "Remainig files: %s" % repr(list(files))
    db_manager.close()

if __name__ == "__main__":
    main()
