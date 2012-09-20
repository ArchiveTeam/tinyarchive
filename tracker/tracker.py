#!/usr/bin/env python

import json
import os
import tempfile
import uuid
import web

urls = (
    "/", "index",
    "/task/(clear|get|put)", "task",
    "/admin/(cleanup|create|delete|fetch|list)", "admin"
)
app = web.application(urls, globals())

directory = os.path.dirname(__file__)
db = web.database(dbn="sqlite", db=os.path.join(directory, "tasks.sqlite"), pooling=False)
data_directory = os.path.abspath(os.path.join(directory, "files"))

class index:

    def GET(self):
        return 'Hello there. May I offer you an UUID? Here you go: %s' % (uuid.uuid1())

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
        parameters = web.input(_method='GET')
        if not "version" in parameters or parameters["version"] != "2.0":
            raise web.HTTPError("403 Forbidden", data="Client version too old. Please update!")

    def clear_tasks(self):
        db.update("task", "status = 'assigned' AND assigned_to = $ip", vars={"ip": web.ctx.ip}, status="free", assigned_when=None, assigned_to=None)
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
                status = 'free' AND
                service_id NOT IN (
                    SELECT service_id FROM task WHERE assigned_to = $ip
                )
            LIMIT 1;
        """,
            {"ip": web.ctx.ip})
        try:
            task = result[0]
        except IndexError:
            t.rollback()
            return "null"
        else:
            db.update("task", "id=$id", vars=task, status="assigned", assigned_when=0, assigned_to=web.ctx.ip)
            try:
                t.commit()
            except:
                return "null"
            else:
                task["generator_options"] = json.loads(task["generator_options"])
                return json.dumps(task, sort_keys=True, indent=4)

    def put_task(self):
        parameters = web.input(_method='GET')
        if not "id" in parameters or not web.data():
            raise web.BadRequest()

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
                task.id = $id AND
                status = 'assigned' AND
                assigned_to = $ip;
        """,
            {"id": parameters["id"], "ip": web.ctx.ip})
        try:
            task = result[0]
        except IndexError:
            raise web.Conflict()
        else:
            fileobj = tempfile.NamedTemporaryFile(dir=data_directory, delete=False)
            fileobj.write(web.data())
            fileobj.close()
            data_file = os.path.relpath(fileobj.name, data_directory)
            try:
                finished_by = parameters["username"][:100]
            except KeyError:
                finished_by = None
            db.update("task", "id=$id", vars=task, status="done", assigned_when=None, assigned_to=None, finished_by=finished_by, data_file=data_file)
            return ""
        finally:
            t.commit()

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

        db.delete("task", where="id = $id", vars={"id": parameters["id"]})

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
                status = 'done';
        """)

        tasks = []
        for task in result:
            task["generator_options"] = json.loads(task["generator_options"])
            tasks.append(task)

        return json.dumps(tasks, sort_keys=True, indent=4)

application = app.wsgifunc()
