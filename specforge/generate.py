import json, shutil
from pathlib import Path
from .spec import load, SQL, JAVA, workflow_reference
from .workspace import inventory, digest, write_json, read_json, git_revision, new_run

ASSETS = Path(__file__).parent / "assets"


def literal(value):
    if value is None:
        return "NULL"
    if type(value) is bool:
        return "1" if value else "0"
    if type(value) is int:
        return str(value)
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def emit(root, name, text):
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def permissions(s):
    result = []
    n = 890000000000001

    def add(
        parent, authority, label, kind, route=None, component=None, roles=("admin",)
    ):
        nonlocal n
        item = dict(
            id=n,
            parent_id=parent,
            authority=authority,
            label=label,
            kind=kind,
            route=route,
            component=component,
            roles=list(roles),
        )
        result.append(item)
        n += 1
        return item["id"]

    root = add(0, "business:sf", "业务管理", "GROUP", roles=("admin", "normal"))
    for e in s["entities"]:
        name = e["name"]
        scope = "business:sf_" + name
        roles = ("admin", "normal") if e["access"] == "owner" else ("admin",)
        # Reference catalogs must be readable by applicants to select related records.
        referenced = any(
            any(f.get("reference") == name for f in other["fields"])
            and other["access"] == "owner"
            for other in s["entities"]
        )
        page_roles = ("admin", "normal") if referenced else roles
        parent = add(
            root,
            scope,
            e["label"],
            "TEMPLATE",
            "/business/sf_" + name,
            "/business/sf_" + name + "/index.vue",
            page_roles,
        )
        for a in e["crud"]:
            grants = page_roles if a in ("page", "detail") else roles
            add(
                parent,
                scope + ":" + a,
                {
                    "create": "新增",
                    "update": "编辑",
                    "delete": "删除",
                    "page": "查询",
                    "detail": "详情",
                }[a]
                + e["label"],
                "BUTTON",
                roles=grants,
            )
        if e.get("workflow"):
            add(parent, scope + ":manage", "查看全部申请", "BUTTON")
            for a in e["workflow"]["transitions"]:
                add(parent, scope + ":" + a["name"], a["label"], "BUTTON")
    return result


def sql(s, perms):
    lines = [
        "SET NAMES utf8mb4;\n-- SpecForge v1: fresh database extension only. Do not apply to an existing database."
    ]
    references = []
    for e in s["entities"]:
        cols = [
            "id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY",
            "sf_deleted BOOLEAN NOT NULL DEFAULT FALSE",
            "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        ]
        for f in e["fields"]:
            col = (
                "`"
                + f["name"]
                + "` "
                + SQL[f["type"]]
                + (" NOT NULL" if f.get("required") else "")
            )
            if "default" in f:
                col += " DEFAULT " + literal(f["default"])
            if f.get("unique"):
                col += " UNIQUE"
            if f["type"] == "enum":
                col += (
                    " CHECK (`"
                    + f["name"]
                    + "` IN ("
                    + ",".join(map(literal, f["values"]))
                    + "))"
                )
            if "min" in f:
                col += " CHECK (`" + f["name"] + "` >= " + str(f["min"]) + ")"
            cols.append(col)
            if f["type"] == "foreign":
                references.append(
                    (
                        e["name"],
                        f["name"],
                        (
                            "system_user"
                            if f["reference"] == "system_user"
                            else "sf_" + f["reference"]
                        ),
                    )
                )
        if e.get("workflow"):
            cols += [
                "owner_id BIGINT NOT NULL",
                "status VARCHAR(64) NOT NULL",
                "INDEX sf_owner (owner_id)",
                "FOREIGN KEY (owner_id) REFERENCES system_user(id)",
            ]
            x = workflow_reference(e["workflow"])
            cols.append("INDEX sf_resource (`" + x["field"] + "`,status)")
            if "exclusive_reference" in e["workflow"]:
                cols += [
                    "sf_active_reference BIGINT GENERATED ALWAYS AS (CASE WHEN status="
                    + literal(x["active_state"])
                    + " THEN `"
                    + x["field"]
                    + "` ELSE NULL END) STORED",
                    "UNIQUE KEY sf_one_active (sf_active_reference)",
                ]
        lines.append(
            "CREATE TABLE sf_"
            + e["name"]
            + " (\n "
            + ",\n ".join(cols)
            + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        )
    for entity, field, target in references:
        lines.append(
            f"ALTER TABLE sf_{entity} ADD FOREIGN KEY (`{field}`) REFERENCES {target}(id);"
        )
    for p in perms:
        cols = [
            "id",
            "parent_id",
            "authority",
            "sort",
            "permission_type",
            "router_path",
            "component_path",
            "keep_alive",
            "visible",
            "permission_status",
            "created_time",
            "last_modified_time",
            "permission_name",
        ]
        vals = [
            p["id"],
            p["parent_id"],
            p["authority"],
            1,
            p["kind"],
            p["route"],
            p["component"],
            0,
            p["kind"] in ("GROUP", "TEMPLATE"),
            "ENABLED",
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:00",
            p["label"],
        ]
        lines.append(
            "INSERT INTO system_permission ("
            + ",".join(cols)
            + ") VALUES ("
            + ",".join(map(literal, vals))
            + ");"
        )
        for role in p["roles"]:
            lines.append(
                "INSERT INTO system_role_permission (role_id,permission_id) SELECT id,"
                + str(p["id"])
                + " FROM system_role WHERE role_code="
                + literal(role)
                + ";"
            )
    return "\n".join(lines) + "\n"


def generate(spec_path, template, workspace):
    spec_path = Path(spec_path).resolve()
    s = load(spec_path)
    template = Path(template).resolve()
    workspace = Path(workspace).resolve()
    if (
        workspace == template
        or template in workspace.parents
        or workspace in template.parents
    ):
        raise ValueError("workspace and template must not contain one another")
    required = [
        "backend/pom.xml",
        "frontend/pnpm-lock.yaml",
        "frontend/src/stores/user.ts",
        "deploy/compose.yaml",
        "backend/src/main/resources/sql/schema.sql",
    ]
    for p in required:
        if not (template / p).is_file():
            raise ValueError("template contract missing: " + p)
    project = workspace / "project.json"
    if project.exists() and read_json(project)["id"] != s["project"]["id"]:
        raise ValueError("workspace belongs to another project")
    template_files = inventory(template)
    run = new_run(workspace)
    source = run / "source"
    source.mkdir()
    for name in template_files:
        src = template / name
        if any(p.is_symlink() for p in [src, *src.parents] if p != template.parent):
            raise ValueError("template symlink rejected: " + name)
        dst = source / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    shutil.copyfile(spec_path, run / "input/project.yaml")
    identity = {
        "template_path": str(template),
        "template_git": git_revision(template),
        "template_sha256": template_files,
        "spec_sha256": digest(spec_path),
        "project": s["project"],
        "format_version": 1,
    }
    write_json(run / "input/identity.json", identity)
    emit(
        source,
        "backend/src/main/java/com/original/business/generated/BusinessResource.java",
        (ASSETS / "BusinessResource.java").read_text(),
    )
    emit(
        source,
        "backend/src/main/resources/specforge/entities.json",
        json.dumps(s["entities"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    )
    emit(
        source,
        "frontend/src/components/BusinessPanel.vue",
        (ASSETS / "BusinessPanel.vue").read_text(),
    )
    types = (ASSETS / "business-types.ts").read_text(encoding="utf-8")
    for e in s["entities"]:
        cls = "".join(x.title() for x in e["name"].split("_"))
        fields = ", ".join(JAVA[f["type"]] + " " + f["name"] for f in e["fields"])
        emit(
            source,
            f"backend/src/main/java/com/original/business/generated/{cls}Input.java",
            "package com.original.business.generated;\nimport java.time.LocalDateTime;\npublic record "
            + cls
            + "Input("
            + fields
            + ") {}\n",
        )
        ts = {
            "string": "string",
            "enum": "string",
            "datetime": "string",
            "integer": "number",
            "foreign": "string",
            "boolean": "boolean",
        }
        types += (
            "export interface "
            + cls
            + "Input {\n"
            + "".join(
                " "
                + f["name"]
                + ("" if f.get("required") else "?")
                + ":"
                + ts[f["type"]]
                + " | null;\n"
                for f in e["fields"]
            )
            + "}\n"
        )
        view = {**e, "availability": availability_fields(s, e)}
        cfg = json.dumps(view, ensure_ascii=False, sort_keys=True).replace(
            "<", r"\u003c"
        )
        emit(
            source,
            f'frontend/src/pages/business/sf_{e["name"]}/index.vue',
            "<script setup lang=\"ts\">\nimport BusinessPanel from '@/components/BusinessPanel.vue'\nimport type {BusinessConfig} from '@/api/business/generated'\nconst config:BusinessConfig="
            + cfg
            + '\n</script>\n<template><BusinessPanel :config="config" /></template>\n',
        )
    emit(source, "frontend/src/api/business/generated.ts", types)
    perms = permissions(s)
    application = None
    if "application" in s:
        from .applications import get_application

        application = get_application(s["application"])
        perms = application.permissions(s, perms)
    migration = sql(s, perms)
    if application:
        migration += application.emit(source)
    emit(
        source, "backend/src/main/resources/db/migration/SF001__business.sql", migration
    )
    schema = source / "backend/src/main/resources/sql/schema.sql"
    schema.write_text(schema.read_text() + "\n" + migration, encoding="utf-8")
    emit(source, "specforge/project.yaml", (run / "input/project.yaml").read_text())
    write_json(source / "specforge/identity.json", identity)
    write_json(source / "specforge/permissions.json", perms)
    emit(
        source,
        "SPEC_FORGE.md",
        "Generated from the included specforge/project.yaml. Fresh database deployment only.\nConfigure .env from .env.example and follow README.md.\nBusiness tables are soft deleted to preserve completed request history.\nNormal users receive applicant permissions; admins receive management permissions.\nNo test accounts or credentials are included.\n",
    )
    write_json(
        run / "manifest.json",
        {"source_sha256": inventory(source), "identity": identity},
    )
    write_json(run / "reports/generate.json", {"status": "PASS", "run_id": run.name})
    write_json(workspace / "project.json", s["project"])
    write_json(workspace / "latest.json", {"run_id": run.name})
    return run


def availability_fields(spec, entity):
    fields = {}
    for child in spec["entities"]:
        w = child.get("workflow", {})
        ref = w.get("capacity_reference")
        if not ref:
            continue
        fk = next(f for f in child["fields"] if f["name"] == ref["field"])
        if fk["reference"] != entity["name"]:
            continue
        name = ref["capacity_field"]
        label = next(f["label"] for f in entity["fields"] if f["name"] == name)
        fields[name] = {
            "field": name,
            "available_field": name + "_available",
            "label": "可用" + label,
        }
    return list(fields.values())
