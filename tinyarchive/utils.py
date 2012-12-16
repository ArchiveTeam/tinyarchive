import hashlib
import itertools
import json
import logging
import os
import os.path
import shutil
import subprocess

def _code_order(char):
    if char >= '0' and char <= '9':
        return 0
    elif char >= 'a' and char <= 'z':
        return 1
    elif char >= 'A' and char <= 'Z':
        return 2
    return 3

def shortcode_compare(a, b):
    diff = len(a) - len(b)
    if diff:
        return diff
    for a, b in itertools.izip(a, b):
        if a != b:
            diff = _code_order(a) - _code_order(b)
            if diff:
                return diff
            else:
                return ord(a) - ord(b)
    return 0

class CodeToFileMap:

    def __init__(self, input_file):
        with open(input_file) as fileobj:
            unsorted_map = json.load(fileobj)

        self._map = {}
        for (service, service_map) in unsorted_map.iteritems():
            if len(service_map) == 1:
                self._map[service] = service_map
            else:
                self._map[service] = sorted(service_map, cmp=self._compare_mapping)

        self.check()

    def check(self):
        output_files = set()
        for (service, service_map) in self._map.iteritems():
            for (i, mapping) in enumerate(service_map):
                if not "file" in mapping:
                    raise ValueError("No file specified for service '%s', mapping %i" % (service, i+1))
                if mapping["file"] in output_files:
                    raise ValueError("Duplicate output file '%s'" % mapping["file"])
                output_files.add(mapping["file"])
            if len(service_map) == 1:
                if len(service_map[0]) != 1:
                    raise ValueError("Additional data for service '%s', mapping 1" % service)
            else:
                previous = ""
                for i, mapping in enumerate(service_map):
                    if not "start" in mapping or not "stop" in mapping:
                        raise ValueError("Start or stop not given for service '%s', mapping %i" % (service, i+1))
                    if len(mapping) != 3:
                        raise ValueError("Additional data for service '%s', mapping %i" % (service, i+1))
                    if shortcode_compare(mapping["start"], mapping["stop"]) > 0:
                        raise ValueError("Start is bigger than stop for service '%s', mapping %i" % (service, i+1))
                    if shortcode_compare(previous, mapping["start"]) >= 0:
                        print previous
                        print mapping
                        raise ValueError("Overlap detected for service '%s', code '%s'" % (service, previous))
                    previous = mapping["stop"]

    def get_mapping(self, service, start):
        service_map = self._map[service]
        if len(service_map) == 1:
            return service_map[0]
        else:
            for mapping in service_map:
                if shortcode_compare(start, mapping["start"]) >= 0 and shortcode_compare(start, mapping["stop"]) <= 0:
                    return mapping
        raise ValueError("No mapping for service '%s', code '%s' found" % (service, start))

    def check_mapping(self, mapping, stop):
        if not "stop" in mapping:
            return True
        return shortcode_compare(stop, mapping["stop"]) <= 0

    def _compare_mapping(self, x, y):
        return shortcode_compare(x["start"], y["start"])

class OutputFile:

    def __init__(self, old_release_directory, new_release_directory, output_file):
        self._log = logging.getLogger("tinyarchive.utils.OutputFile")
        self._log.info("Opening output file %s" % output_file)

        self._old_file = os.path.join(old_release_directory, output_file)
        self._new_file = os.path.join(new_release_directory, output_file)
        if not os.path.isdir(os.path.dirname(self._new_file)):
            os.makedirs(os.path.dirname(self._new_file))

        self._fileobj = open(self._new_file + ".txt", "wb")
        self._hash = hashlib.md5()

    def write(self, code, url):
        self._hash.update(code + "|")
        self._hash.update(url)
        self._hash.update("\n")
        self._fileobj.write(code + "|")
        self._fileobj.write(url)
        self._fileobj.write("\n")

    def close(self):
        self._log.debug("Closing output file")
        self._fileobj.close()

        self._log.debug("Calculating output file hash")
        new_hash = self._hash.hexdigest()
        s = subprocess.Popen(["md5sum", self._new_file + ".txt"], stdout=subprocess.PIPE)
        s.wait()
        assert s.communicate()[0][:32] == new_hash

        if os.path.isfile(self._old_file + ".txt.xz") and False:
            s = subprocess.Popen("xzcat '%s.txt.xz' | md5sum" % self._old_file, shell=True, stdout=subprocess.PIPE)
            s.wait()
            old_hash = s.communicate()[0][:32]
            self._log.debug("Hash of old previous release file: %s" % old_hash)
        else:
            self._log.debug("No previous release file found")
            old_hash = None

        if old_hash == new_hash:
            self._log.info("File did not change since last release")
            os.unlink(self._new_file + ".txt")
            shutil.copyfile(self._old_file + ".txt.xz", self._new_file + ".txt.xz")
        else:
            self._log.info("File changed since last release")
            subprocess.check_call(["xz", "-1", self._new_file + ".txt"])
