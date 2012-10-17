from bsddb3 import db
import itertools
import os

import tinyarchive.utils

class DBManager:

    def __init__(self, database_directory):
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
        return databases

    def get(self, name):
        if not self._env:
            raise ValueError("Trying to use closed DBManager")
        if not name in self._databases:
            self._databases[name] = Database(name, self._env)

        return self._databases[name]

    def close(self):
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
        self._service = service
        self._db = db.DB(dbEnv=db_env)
        self._db.set_bt_compare(tinyarchive.utils.shortcode_compare)
        self._db.open("%s.db" % service, dbname=service, dbtype=db.DB_BTREE, flags=db.DB_CREATE)

    def get(self, code):
        if self._db == None:
            raise ValueError("Trying to use closed Database")
        try:
            return self._db.get(code)
        except db.DBNoutFoundError:
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
            if self._service == "bitly":
                if len(stored_url) > 1000 and stored_url[:1000] == url:
                    return
            raise ValueError("Code %s has two URLs: %s (stored) and %s (new)" % (code, stored_url, url))

    def delete(self, code):
        self._db.delete(code)

    def close(self):
        if self._db != None:
            self._db.close()
            self._db = None

    def __len__(self):
        return len(self._db)
