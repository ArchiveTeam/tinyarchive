#!/usr/bin/env python

import json
import os
import re
import tempfile
import time
import uuid
import web

urls = (
    "/", "index",
    "/data/(current|alltime)", "data",
    "/task/(clear|get|put)", "task",
    "/admin/(cleanup|create|delete|fetch|list)", "admin"
)
app = web.application(urls, globals())

directory = os.path.dirname(__file__)
db = web.database(dbn="sqlite", db=os.path.join(directory, "tasks.sqlite"), pooling=False)
data_directory = os.path.abspath(os.path.join(directory, "files"))

class index:

    def GET(self):
        render = web.template.render('templates')
        return render.index()

class data:

    def GET(self, which):
        if which == "current":
            data = self._current()
        else:
            data = self._alltime()
        return json.dumps(data, indent=4, sort_keys=True)

    def _current(self):
        data = {
            "tasks_available": self.get_tasks("available"),
            "tasks_assigned": self.get_tasks("assigned"),
            "tasks_finished": self.get_tasks("finished"),
            "user_ranking": self.user_ranking()
        }
        return data

    def _alltime(self):
        return None

    def get_tasks(self, status):
        result = db.query("""
            SELECT
                service.name AS service,
                COUNT(*) AS task_count
            FROM task
            JOIN service ON task.service_id = service.id
            WHERE status = $status
            GROUP BY service.id;
        """, {"status": status})
        data = {}
        for row in result:
            data[row["service"]] = row["task_count"]
        return data

    def user_ranking(self):
        result = db.query("""
            SELECT
                username,
                COUNT(*) as task_count
            FROM task
            WHERE
                status = 'finished' AND
                username IS NOT NULL
            GROUP BY username;
        """)
        data = {}
        for row in result:
            data[row["username"]] = row["task_count"]
        return data

class task:

    def GET(self, action):
        self.check_version()

        if action == "get":
            return self.get_task()
        elif action == "clear":
            return self.clear_tasks()

        raise web.HTTPError("405 Method Not Allowed")

    def POST(self, action):
        self.check_version()

        if action == "put":
            return self.put_task()
        raise web.HTTPError("405 Method Not Allowed")

    def check_version(self):
        allowed_versions = ["2.2"]
        parameters = web.input(_method='GET')
        if not "version" in parameters or parameters["version"] not in allowed_versions:
            raise web.HTTPError("403 Forbidden", data="Client version too old. Please update!")

    def clear_tasks(self):
        db.update("task", "status = 'assigned' AND ip_address = $ip", vars={"ip": web.ctx.ip}, status="available", timestamp=None, ip_address=None)
        return ""

    def get_task(self):
        t = db.transaction()
        result = db.query("""
            SELECT
                task.id AS id,
                service.name AS service,
                generator_type,
                generator_options
            FROM task
            JOIN service ON task.service_id = service.id
            WHERE
                status = 'available' AND
                service_id NOT IN (
                    SELECT service_id FROM task WHERE ip_address = $ip
                )
            LIMIT 1;
        """,
            {"ip": web.ctx.ip})
        try:
            task = result[0]
        except IndexError:
            return "null"
        else:
            task["generator_options"] = json.loads(task["generator_options"])
            db.update("task", "id=$id", vars=task, status="assigned", timestamp=int(time.time()), ip_address=web.ctx.ip)
            return json.dumps(task, sort_keys=True, indent=4)
        finally:
            t.commit()

    def put_task(self):
        parameters = web.input(_method='GET')
        if not "id" in parameters or not web.data():
            raise web.BadRequest()

        # Find out username
        username = None
        try:
            if re.search("^[-_a-zA-Z0-9]{3,30}$", parameters["username"]):
                username = parameters["username"]
        except KeyError:
            pass

        # Create output file
        fileobj = tempfile.NamedTemporaryFile(dir=data_directory, delete=False)
        fileobj.write(web.data())
        fileobj.close()
        data_file = os.path.relpath(fileobj.name, data_directory)

        # Mark task as finished
        t = db.transaction()
        count = db.update("task",
            "id = $id AND status = 'assigned' AND ip_address = $ip",
            vars = {"id": parameters["id"], "ip": web.ctx.ip},
            status="finished", timestamp=int(time.time()), ip_address=None, username=username, data_file=data_file
        )

        # If task was not properly assigned, we get 0 changed rows
        if count != 1:
            t.rollback()
            raise web.Conflict()

        # Update statistics
        if username:
            data = db.select("task", what="username, service_id", where="id = $id", vars={"id": parameters["id"]})[0]
            count = db.update("statistics",
                "username = $username AND service_id = $service_id",
                data,
                count=web.SQLLiteral("count + 1"))
            if count == 0:
                db.insert("statistics", username=data["username"], service_id=data["service_id"], count=1)

        t.commit()
        return ""

class admin:

    def GET(self, action):
        if web.ctx.ip != "127.0.0.1":
            raise web.Forbidden()

        if action == "cleanup":
            return self.cleanup()
        elif action == "create":
            return self.create_task()
        elif action == "delete":
            return self.delete_task()
        elif action == "fetch":
            return self.fetch_data()
        elif action == "list":
            return self.list_tasks()

    def POST(self, action):
        return self.GET(action)

    def cleanup(self):
        dir_files = set(os.listdir(data_directory))
        db_files = map(lambda x: x["data_file"], db.select("task", what="data_file", where="data_file IS NOT NULL"))

        for name in dir_files.difference(db_files):
            os.unlink(os.path.join(data_directory, name))

        db.update("task", "status = 'assigned' AND timestamp < $timestamp", vars={"timestamp": int(time.time()) - 1800}, timestamp=None, ip_address=None, status="available")

        db.delete("task", "status = 'deleted' AND timestamp < $timestamp", vars={"timestamp": int(time.time()) - 86400})

        return ""

    def create_task(self):
        parameters = web.input()
        if not ("service" in parameters and "generator_type" in parameters and "generator_options" in parameters):
            raise web.BadRequest()

        t = db.transaction()

        result = db.select("service", what="id", where="name = $name", vars={"name": parameters["service"]})
        try:
            service_id = result[0]["id"]
        except IndexError:
            service_id = db.insert("service", name=parameters["service"])

        task_id = str(uuid.uuid1())
        db.insert("task", id=task_id, service_id=service_id, generator_type=parameters["generator_type"], generator_options=parameters["generator_options"])

        t.commit()

        return task_id

    def delete_task(self):
        parameters = web.input()
        if not "id" in parameters:
            raise web.BadRequest()

        db.update("task", where="id = $id", vars={"id": parameters["id"]}, status="deleted", data_file=None)

        return ""

    def fetch_data(self):
        parameters = web.input()
        if not "id" in parameters:
            raise web.BadRequest()

        result = db.select("task", what="data_file", where="id = $id", vars={"id": parameters["id"]})
        try:
            data_file = result[0]["data_file"]
        except IndexError:
            raise web.Conflict()
        else:
            if data_file == None:
                raise web.Conflict()
            with open(os.path.join(data_directory, data_file)) as fileobj:
                return fileobj.read()

    def list_tasks(self):
        result = db.query("""
            SELECT
                task.id AS id,
                service.name AS service,
                generator_type,
                generator_options
            FROM task
            JOIN service ON task.service_id = service.id
            WHERE
                status = 'finished';
        """)

        tasks = []
        for task in result:
            task["generator_options"] = json.loads(task["generator_options"])
            tasks.append(task)

        return json.dumps(tasks, sort_keys=True, indent=4)

application = app.wsgifunc()
