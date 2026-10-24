"""Closed v1 business specification. Reject unsupported semantics before writing files."""

import re
from pathlib import Path
import yaml


class SpecError(ValueError):
    pass


IDENT = re.compile(r"^[a-z][a-z0-9_]{0,39}$")
TYPES = {"string", "integer", "boolean", "datetime", "enum", "foreign"}
OPERATIONS = {"create", "update", "delete", "page", "detail"}
JAVA = {
    "string": "String",
    "integer": "Long",
    "boolean": "Boolean",
    "datetime": "LocalDateTime",
    "enum": "String",
    "foreign": "Long",
}
SQL = {
    "string": "VARCHAR(255)",
    "integer": "BIGINT",
    "boolean": "BOOLEAN",
    "datetime": "DATETIME",
    "enum": "VARCHAR(64)",
    "foreign": "BIGINT",
}
RESERVED = {
    "id",
    "owner_id",
    "created_at",
    "status",
    "sf_deleted",
    "sf_active_reference",
}


def require(ok, message):
    if not ok:
        raise SpecError(message)


def keys(value, allowed, label):
    require(isinstance(value, dict), label + " must be an object")
    require(
        not (set(value) - set(allowed)),
        label + " unknown keys: " + str(set(value) - set(allowed)),
    )


def ident(value):
    require(
        isinstance(value, str) and IDENT.fullmatch(value),
        "invalid identifier: " + str(value),
    )
    require(
        value
        not in {
            "class",
            "public",
            "private",
            "package",
            "return",
            "default",
            "new",
            "null",
            "true",
            "false",
            "abstract",
            "assert",
            "boolean",
            "break",
            "byte",
            "case",
            "catch",
            "char",
            "const",
            "continue",
            "do",
            "double",
            "else",
            "enum",
            "extends",
            "final",
            "finally",
            "float",
            "for",
            "goto",
            "if",
            "implements",
            "import",
            "instanceof",
            "int",
            "interface",
            "long",
            "native",
            "protected",
            "short",
            "static",
            "strictfp",
            "super",
            "switch",
            "synchronized",
            "this",
            "throw",
            "throws",
            "transient",
            "try",
            "void",
            "volatile",
            "while",
            "record",
            "var",
            "yield",
        },
        "reserved identifier: " + value,
    )
    return value


def load(path):
    try:
        value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SpecError(str(exc)) from exc
    return validate(value)


def validate(s):
    keys(s, {"version", "project", "entities", "acceptance", "application"}, "spec")
    require(
        type(s.get("version")) is int and s["version"] == 1, "unsupported spec version"
    )
    keys(s.get("project"), {"id", "name"}, "project")
    ident(s["project"].get("id"))
    require(
        isinstance(s["project"].get("name"), str)
        and 0 < len(s["project"]["name"]) <= 64,
        "project name required",
    )
    entities = s.get("entities")
    require(
        isinstance(entities, list) and 0 < len(entities) <= 50,
        "entities must be a nonempty list (max 50)",
    )
    names = []
    for e in entities:
        keys(
            e,
            {"name", "label", "fields", "crud", "access", "workflow", "page"},
            "entity",
        )
        name = ident(e.get("name"))
        require(name not in names, "duplicate entity: " + name)
        names.append(name)
        require(
            isinstance(e.get("label"), str) and 0 < len(e["label"]) <= 50,
            "entity label required",
        )
        require(e.get("access") in {"admin", "owner"}, "access must be admin or owner")
        require(
            isinstance(e.get("crud"), list)
            and set(e["crud"]) <= OPERATIONS
            and "page" in e["crud"],
            "unsupported CRUD operation",
        )
        require(len(e["crud"]) == len(set(e["crud"])), "duplicate CRUD operation")
        require(
            isinstance(e.get("fields"), list) and 0 < len(e["fields"]) <= 50,
            "fields required",
        )
        fieldnames = []
        for f in e["fields"]:
            keys(
                f,
                {
                    "name",
                    "label",
                    "type",
                    "required",
                    "unique",
                    "values",
                    "reference",
                    "default",
                    "min",
                },
                "field",
            )
            n = ident(f.get("name"))
            require(
                n not in RESERVED and n not in fieldnames,
                "duplicate or reserved field: " + n,
            )
            fieldnames.append(n)
            require(
                isinstance(f.get("label"), str) and 0 < len(f["label"]) <= 50,
                "field label required",
            )
            require(
                f.get("type") in TYPES, "unsupported field type: " + str(f.get("type"))
            )
            for flag in ("required", "unique"):
                require(type(f.get(flag, False)) is bool, flag + " must be boolean")
            if f["type"] == "enum":
                vals = f.get("values")
                require(isinstance(vals, list) and bool(vals), "enum values required")
                require(
                    all(
                        isinstance(v, str) and re.fullmatch(r"[A-Z][A-Z0-9_]{0,39}", v)
                        for v in vals
                    ),
                    "invalid enum value",
                )
                require(len(set(vals)) == len(vals), "duplicate enum value")
            else:
                require("values" not in f, "values only valid for enum")
            if f["type"] == "foreign":
                require(
                    isinstance(f.get("reference"), str), "foreign reference required"
                )
            else:
                require("reference" not in f, "reference only valid for foreign")
            if "min" in f:
                require(
                    f["type"] == "integer"
                    and type(f["min"]) is int
                    and -(2**63) <= f["min"] < 2**63,
                    "min requires a signed 64-bit integer field",
                )
            if "default" in f:
                v = f["default"]
                t = f["type"]
                require(
                    (t in {"string", "enum"} and isinstance(v, str) and len(v) <= 255)
                    or (t == "integer" and type(v) is int and -(2**63) <= v < 2**63)
                    or (t == "boolean" and type(v) is bool),
                    "unsupported default",
                )
                if t == "enum":
                    require(v in f["values"], "default outside enum")
                if "min" in f:
                    require(v >= f["min"], "default below minimum")
        page = e.get("page")
        keys(page, {"list", "form"}, "page")
        for group in ("list", "form"):
            require(
                isinstance(page.get(group), list)
                and len(set(page[group])) == len(page[group])
                and set(page[group]) <= set(fieldnames),
                "invalid page " + group + " fields",
            )
        writable = {
            f["name"] for f in e["fields"] if f.get("required") and "default" not in f
        }
        require(writable <= set(page["form"]), "required fields missing from form")
        w = e.get("workflow")
        if w:
            keys(
                w,
                {
                    "initial",
                    "states",
                    "state_labels",
                    "transitions",
                    "exclusive_reference",
                    "capacity_reference",
                },
                "workflow",
            )
            require(
                e["access"] == "owner"
                and set(e["crud"]) == {"create", "page", "detail"},
                "workflow must use owner create/page/detail",
            )
            require(
                isinstance(w.get("states"), list)
                and len(w["states"]) == len(set(w["states"]))
                and all(
                    isinstance(v, str) and re.fullmatch(r"[A-Z][A-Z0-9_]{0,39}", v)
                    for v in w["states"]
                ),
                "invalid workflow states",
            )
            require(w.get("initial") in w["states"], "invalid initial state")
            require(
                isinstance(w.get("transitions"), list) and bool(w["transitions"]),
                "transitions required",
            )
            labels = w.get("state_labels", {})
            require(
                isinstance(labels, dict)
                and set(labels) <= set(w["states"])
                and all(
                    isinstance(v, str) and 0 < len(v) <= 50 for v in labels.values()
                ),
                "invalid state labels",
            )
            actions = []
            for a in w["transitions"]:
                keys(
                    a,
                    {"name", "label", "from", "to", "forbid_self", "exclusive"},
                    "transition",
                )
                ident(a.get("name"))
                require(
                    a["name"] not in actions and a["name"] not in OPERATIONS,
                    "duplicate or reserved action",
                )
                actions.append(a["name"])
                require(
                    a.get("from") in w["states"]
                    and a.get("to") in w["states"]
                    and a["from"] != a["to"],
                    "invalid transition states",
                )
                require(
                    isinstance(a.get("label"), str) and 0 < len(a["label"]) <= 50,
                    "transition label required",
                )
                require(
                    type(a.get("forbid_self", False)) is bool
                    and type(a.get("exclusive", False)) is bool,
                    "invalid transition flags",
                )
            modes = [
                key for key in ("exclusive_reference", "capacity_reference") if key in w
            ]
            require(
                len(modes) == 1, "workflow requires exactly one resource reference mode"
            )
            mode = modes[0]
            x = w[mode]
            allowed = {"field", "active_state", "terminal_states"}
            if mode == "capacity_reference":
                allowed |= {"capacity_field", "quantity_field"}
            keys(x, allowed, mode)
            require(
                any(
                    f["name"] == x.get("field") and f["type"] == "foreign"
                    for f in e["fields"]
                ),
                "exclusive field must reference entity",
            )
            require(
                x.get("active_state") in w["states"]
                and isinstance(x.get("terminal_states"), list)
                and bool(x["terminal_states"])
                and set(x["terminal_states"]) <= set(w["states"]),
                "invalid exclusive states",
            )
            require(
                x["active_state"] != w["initial"]
                and x["active_state"] not in x["terminal_states"]
                and w["initial"] not in x["terminal_states"],
                "active/initial cannot be terminal",
            )
            for a in w["transitions"]:
                if mode == "exclusive_reference":
                    require(
                        a.get("exclusive", False) == (a["to"] == x["active_state"]),
                        "entering active state must be exclusive",
                    )
                else:
                    require(
                        "exclusive" not in a,
                        "capacity allocation is inferred from the active state; exclusive flag is only for single-item workflows",
                    )
        else:
            require(e["access"] == "admin", "owner entities require workflow")
    for e in entities:
        for f in e["fields"]:
            if f["type"] == "foreign":
                require(
                    f["reference"] in names + ["system_user"]
                    and f["reference"] != e["name"],
                    "unknown/self reference: " + f["reference"],
                )
        if e.get("workflow"):
            w = e["workflow"]
            x = workflow_reference(w)
            f = next(f for f in e["fields"] if f["name"] == x["field"])
            require(
                f["reference"] != "system_user" and f.get("required"),
                "resource reference must be required business entity",
            )
            if "capacity_reference" in w:
                target = next(
                    item for item in entities if item["name"] == f["reference"]
                )
                capacity = next(
                    (
                        item
                        for item in target["fields"]
                        if item["name"] == x.get("capacity_field")
                    ),
                    None,
                )
                quantity = next(
                    (
                        item
                        for item in e["fields"]
                        if item["name"] == x.get("quantity_field")
                    ),
                    None,
                )
                require(
                    capacity is not None
                    and capacity["type"] == "integer"
                    and capacity.get("required")
                    and capacity.get("min", -1) >= 0,
                    "capacity field must be a required nonnegative integer",
                )
                require(
                    quantity is not None
                    and quantity["type"] == "integer"
                    and quantity.get("required")
                    and quantity.get("min", 0) >= 1,
                    "quantity field must be a required positive integer",
                )
                require(
                    x["capacity_field"] + "_available"
                    not in {item["name"] for item in target["fields"]},
                    "computed availability field conflicts with stored field",
                )
                require(
                    target["access"] == "admin",
                    "capacity catalog must be admin-managed",
                )
    # Two capability types cannot claim the same resource with incompatible accounting semantics.
    modes = {}
    for e in entities:
        w = e.get("workflow")
        if not w:
            continue
        x = workflow_reference(w)
        target = next(f["reference"] for f in e["fields"] if f["name"] == x["field"])
        modes.setdefault(target, set()).add(
            "capacity" if "capacity_reference" in w else "exclusive"
        )
    require(
        all(len(value) == 1 for value in modes.values()),
        "resource cannot mix exclusive and capacity workflows",
    )
    require(
        isinstance(s.get("acceptance"), list)
        and bool(s["acceptance"])
        and all(isinstance(x, str) and x for x in s["acceptance"]),
        "acceptance scenarios required",
    )
    if "application" in s:
        from .applications import get_application

        try:
            get_application(s["application"]).validate_spec(s)
        except ValueError as exc:
            raise SpecError(str(exc)) from exc
    return s


def workflow_reference(workflow):
    """Resource allocation protocol shared by validation and generation."""
    return workflow.get("exclusive_reference", workflow.get("capacity_reference"))
