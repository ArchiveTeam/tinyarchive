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

# Scripts
## Database scripts
### create\_release.py
Creates a new release from the database. By specifying the location of a
previous release, the create\_release.py script can check which files have not
changed and avoid recompressing them, which would waste time and possibly
change their hashsum. The code\_to\_file.json file is used to map from a
shortener name and code to a specific output file.
### create\_trim-old\_db.py
Creates the sqlite3 database used by the trim-old website.
### import.py
Imports finished tasks from the tracker into the database.
### import\_tnyim.py
One-off script to import CSV dumps from the URL shortener at
[tny.im](http://tny.im/).
### release\_import.py
Opposite of create\_release.py: Takes a release and imports it into the
database, using the code\_to\_file.json file to map from input file to URL
shortener name.
### stats.py
Outputs a JSON structure containing a mapping from URL shortener name to number
of shorturls in the database.
## Tracker scripts
### cleanup.py
Calls the tracker's cleanup admin function, which removes finished tasks and
resets assignments for tasks assigned over 30 minutes ago.
### fetch\_finished.py
Fetches a list of finished tasks from the tracker, then for each task first
downloads the payload and then tells the tracker to mark the task as deleted.
For each task, a JSON file with the task metadata and a corresponding txt.gz
with the payload is stored in the output directory.
### redo.py
Takes a JSON file containing task metadata and registers a new task with the
same parameters at the tracker.
### task\_create.py
File with some helper functions to create new tasks at the tracker.
