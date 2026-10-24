"""Shared transport and fixture primitives for disposable acceptance environments."""

import json
import re
import subprocess
import urllib.request
import urllib.error
from urllib.parse import urlsplit
from ..workspace import write_json


class AcceptanceClient:
    def __init__(self, origin, password, project, reports):
        parsed = urlsplit(origin)
        if (
            not re.fullmatch(r"sf-accept-[a-z0-9-]+", project)
            or parsed.scheme != "http"
            or parsed.hostname != "127.0.0.1"
            or not parsed.port
            or parsed.path
        ):
            raise ValueError("disposable loopback acceptance target required")
        self.origin = origin
        self.password = password
        self.project = project
        self.reports = reports
        self.checks = []

    def check(self, ok, label):
        self.checks.append({"name": label, "passed": bool(ok)})
        write_json(self.reports / "api.json", self.checks)
        if not ok:
            raise AssertionError(label)

    def call(self, path, method="GET", data=None, token=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        request = urllib.request.Request(
            self.origin + "/api/v1/" + path,
            None if data is None else json.dumps(data).encode(),
            headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            return json.load(exc)

    def login(self, name):
        result = self.call(
            "authorize/login", "POST", {"username": name, "password": self.password}
        )
        self.check(result["code"] == 20000, "login " + name)
        return result["data"]["accessToken"]

    def sql(self, query):
        env = json.loads(
            subprocess.check_output(["docker", "inspect", self.project + "-db-1"])
        )[0]["Config"]["Env"]
        password = next(
            value.split("=", 1)[1]
            for value in env
            if value.startswith("MYSQL_ROOT_PASSWORD=")
        )
        return (
            subprocess.check_output(
                [
                    "docker",
                    "exec",
                    "-i",
                    "-e",
                    "MYSQL_PWD=" + password,
                    self.project + "-db-1",
                    "mysql",
                    "--default-character-set=utf8mb4",
                    "-N",
                    "-B",
                    "-uroot",
                    "admin_platform",
                ],
                input=query.encode(),
            )
            .decode()
            .strip()
        )

    def create_user(self, name, role_ids, admin):
        self.check(
            self.call(
                "system/user",
                "POST",
                {"username": name, "password": self.password, "roleIds": role_ids},
                admin,
            )["code"]
            == 20000,
            "create user " + name,
        )
        return self.login(name)

    def create_role(self, code, label, permission_ids, admin):
        self.check(
            self.call(
                "system/role",
                "POST",
                {
                    "roleCode": code,
                    "roleName": label,
                    "roleStatus": "ENABLED",
                    "sort": 32,
                    "permissionIds": permission_ids,
                },
                admin,
            )["code"]
            == 20000,
            "create role " + code,
        )
        safe = code.replace("'", "''")
        return self.sql("SELECT id FROM system_role WHERE role_code='" + safe + "';")
