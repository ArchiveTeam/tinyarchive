#!/usr/bin/env python

import sys

previous_code = None
previous_url = None

for line in sys.stdin:
    assert line[-1] == "\n"
    code, url = line[:-1].split("|", 1)
    if code == previous_code and url != previous_url:
        print "----------------------------------"
        print "Code: %s" % code
        print "1st URL: %s" % previous_url
        print "2nd URL: %s" % url
    previous_code = code
    previous_url = url
