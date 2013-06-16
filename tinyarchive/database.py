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

from bsddb3 import db
import itertools
import logging
import os
import urlparse

import tinyarchive.conflictsolver
import tinyarchive.utils

class DBManager:

    def __init__(self, database_directory):
        self._log = logging.getLogger("tinyarchive.database.DBManager")
        self._log.info("Opening database environment at %s" % database_directory)
        self._database_directory = os.path.abspath(database_directory)
        self._env = db.DBEnv()
        self._env.set_data_dir(os.path.join(self._database_directory, "data"))
        self._env.open(os.path.join(self._database_directory, "dbenv"), db.DB_INIT_LOCK | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_CREATE)
        self._databases = {}

    def list(self):
        databases = []
        for filename in os.listdir(os.path.join(self._database_directory, "data")):
            if filename[-3:] != ".db":
                continue
            databases.append(filename[:-3])
        self._log.info("Found %i databases" % len(databases))
        return databases

    def get(self, name):
        if not self._env:
            raise ValueError("Trying to use closed DBManager")
        if not name in self._databases:
            self._databases[name] = Database(name, self._env)
        return self._databases[name]

    def close(self):
        self._log.info("Closing DBManager")
        if self._env:
            for database in self._databases.values():
                database.close()
            self._env.close()
            self._env = None

class Database:

    @property
    def service(self):
        return self._service

    def __init__(self, service, db_env):
        self._log = logging.getLogger("tinyarchive.database.Database")
        self._log.info("Opening database for service '%s'" % service)
        self._service = service
        self._db = db.DB(dbEnv=db_env)
        self._db.set_bt_compare(tinyarchive.utils.shortcode_compare)
        self._db.open("%s.db" % service, dbname=service, dbtype=db.DB_BTREE, flags=db.DB_CREATE)
        self._cursor = None

    def get(self, code):
        if self._db == None:
            raise ValueError("Trying to use closed Database")
        try:
            return self._db.get(code)
        except db.DBNotFoundError:
            raise AttributeError("Code %s not found" % code)

    def set(self, code, url):
        if self._db == None:
            raise ValueError("Trying to use closed Database")
        try:
            self._db.put(code, url, flags=db.DB_NOOVERWRITE)
        except db.DBKeyExistError:
            stored_url = self._db.get(code)
            if stored_url == url:
                return
            solver = tinyarchive.conflictsolver.factory(self._service)
            real_url = solver.solve(code, stored_url, url)
            if stored_url != real_url:
                self.delete(code)
                if real_url != None:
                    self.set(code, real_url)

    def delete(self, code):
        self._db.delete(code)

    def close(self):
        if self._cursor != None:
            self._log.debug("Closing cursor for service '%s'" % self._service)
            self._cursor.close()
            self._cursor = None
        if self._db != None:
            self._log.debug("Closing database for service '%s'" % self._service)
            self._db.close()
            self._db = None

    def __len__(self):
        if self._db == None:
            raise ValueError("Trying to use closed Database")
        return len(self._db)

    def __iter__(self):
        if self._db == None:
            raise ValueError("Trying to use closed Database")
        if self._cursor != None:
            raise ValueError("Only one Cursor can be used at a time")
        self._cursor = self._db.cursor()
        return self

    def next(self):
        if self._cursor == None:
            print("asd")
            raise StopIteration()
        try:
            result = self._cursor.get(flags=db.DB_NEXT)
            # According to BerkeleyDB docs, this should throw a DBNotFoundError
            # when we are at the last entry. Python BSDDB3 4.8.3-3 however does
            # return None instead, so we just pretend it is throwing that
            # error.
            if result == None:
                raise db.DBNotFoundError
            return result
        except db.DBNotFoundError:
            raise StopIteration()
            self._cursor = None
