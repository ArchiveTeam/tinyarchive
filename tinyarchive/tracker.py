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

import httplib
import json
import urllib

import tinyback.tracker

class Tracker(tinyback.tracker.Tracker):

    def admin_list(self):
        self._log.info("Fetching list of all tasks")
        status, tasks = self._request("GET", "admin/list")
        if status != httplib.OK:
            raise Exception("Unexpected status %i" % status)
        return json.loads(tasks)

    def admin_fetch(self, task):
        self._log.info("Fetching task %s data" % task["id"])
        status, data = self._request("GET", "admin/fetch", {"id": task["id"]})
        if status != httplib.OK:
            raise Exception("Unexpected status %i" % status)
        return data

    def admin_delete(self, task):
        self._log.info("Deleting task %s" % task["id"])
        status, data = self._request("GET", "admin/delete?id=%s", {"id": task["id"]})
        if status != httplib.OK:
            raise Exception("Unexpected status %i" % status)

    def admin_cleanup(self):
        self._log.info("Running cleanup")
        status, data = self._request("GET", "admin/cleanup")
        if status != httplib.OK:
            raise Exception("Unexpected status %i" % status)

    def admin_create(self, service, generator_type, generator_options):
        self._log.info("Creating new task for service %s" % service)
        params = {
            "service": service,
            "generator_type": generator_type,
            "generator_options": json.dumps(generator_options)
        }
        status, task_id = self._request("POST", "admin/create", body=urllib.urlencode(params))
        if status != httplib.OK:
            raise Exception("Unexpected status %i" % status)

        self._log.debug("Created task has ID %s" % task_id)
        return task_id
