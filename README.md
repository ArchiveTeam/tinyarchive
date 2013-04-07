# Introduction
The _tinyarchive_ repository is a loose collection of scripts to help with
backing up URL shorteners. Most scripts are written in Python.

# Concepts
## Tinyarchive database
The very core of the whole thing. It consists of multiple [Berkely
DB](https://en.wikipedia.org/wiki/Berkeley_DB) B-Tree databases that contain
mappings from short url codes to long URLs. For each shortener there is one
database. For example, the database bitly.db might contain the following
mappings:

* a -> http://apple.com
* b -> http://bit.ly/2lkCBm
* c -> http://www.timwilson.us

## Tracker
The tracker is a completely separate application that hands out tasks to
[tinyback](https://github.com/soult/tinyback) instances.

## trim-old
When tr.im shut down, part of it's database [was preserved](http://urlte.am/).
In 2013 tr.im was relaunched by [Matthew Kelly](https://twitter.com/mattkel),
but all the old shortlinks were lost. With a little magic, it was possible to
refill the new tr.im database with links from the old tr.im database. One such
magic trick is trim-old.tinyarchive.org: Since tr.im had trouble with some URLs
(for whatever reason), instead of directly linking to the URL, it was created
to redirect to trim-old.tinyarchive.org/$UUID and then is redirected to the
real URL from there.
