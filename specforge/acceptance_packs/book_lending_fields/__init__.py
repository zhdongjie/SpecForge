"""Explicit fixed field-change scenarios; reuse all book-lending business assertions."""

from pathlib import Path
import secrets
from .. import book_lending
from ..support import AcceptanceClient
from ...spec import load
from ...workspace import read_json

BROWSER_SCRIPT = Path(book_lending.__file__).with_name("browser.cjs")
CASES = {
    "book_fields_v1": {"field": "isbn", "value": "978-000000001", "shelf": True},
    "book_fields_v2": {
        "field": "catalog_number",
        "value": "CAT-000000001",
        "shelf": False,
    },
}


def scenario(spec):
    case = CASES.get(spec["project"]["id"])
    if case is None:
        raise ValueError(
            "book-lending-fields requires explicit project id book_fields_v1 or book_fields_v2"
        )
    return case


def validate_spec(spec):
    book_lending.validate_spec(spec)
    case = scenario(spec)
    book = spec["entities"][0]
    book = next(e for e in spec["entities"] if e["name"] == "book")
    fields = {f["name"]: f for f in book["fields"]}
    expected = {"code", "name", "stock", case["field"]} | (
        {"shelf_number"} if case["shelf"] else set()
    )
    if (
        set(fields) != expected
        or fields[case["field"]]["type"] != "string"
        or fields[case["field"]].get("required")
    ):
        raise ValueError("field scenario does not match fixed contract")
    if case["shelf"] and any(
        fields["shelf_number"].get(k) != value
        for k, value in {"type": "integer", "min": 0, "default": 0}.items()
    ):
        raise ValueError("shelf_number must have integer min zero and default zero")
    if not case["shelf"] and fields["name"]["label"] != "馆藏名称":
        raise ValueError("v2 requires changed name label")
    if any(not expected <= set(book["page"][key]) for key in ("list", "form")):
        raise ValueError("field scenario requires all book fields in list and form")


def accept(origin, password, project, source, reports):
    spec = load(source / "specforge/project.yaml")
    validate_spec(spec)
    case = scenario(spec)
    payload = book_lending.accept(origin, password, project, source, reports)
    client = AcceptanceClient(origin, password, project, reports)
    client.checks = read_json(reports / "api.json")
    check, call, sql = client.check, client.call, client.sql
    admin = client.login("sfadmin")
    suffix = secrets.token_hex(4)
    data = {
        "code": "FIELDS-" + suffix,
        "name": "字段验收",
        "stock": 1,
        case["field"]: case["value"],
    }
    created = call("business/book", "POST", data, admin)
    check(created["code"] == 20000, "field scenario create")
    bid = created["data"]["id"]
    path = "business/book/" + str(bid)
    row = call(path, token=admin)["data"]
    check(row[case["field"]] == case["value"], "new or renamed field persisted")
    old = {"isbn", "shelf_number"} if not case["shelf"] else {"catalog_number"}
    check(not old.intersection(row), "removed fields absent from detail")
    columns = set(
        sql(
            "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='admin_platform' AND TABLE_NAME='sf_book';"
        ).splitlines()
    )
    check(
        case["field"] in columns and not old.intersection(columns),
        "database added renamed removed columns synchronized",
    )
    if case["shelf"]:
        check(
            row["shelf_number"] == 0, "API omitted optional integer uses default zero"
        )
        check(
            sql(
                "SELECT COLUMN_DEFAULT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='admin_platform' AND TABLE_NAME='sf_book' AND COLUMN_NAME='shelf_number';"
            )
            == "0",
            "SQL default zero",
        )
        bad = {**data, "code": "NEG-" + suffix, "shelf_number": -1}
        check(
            call("business/book", "POST", bad, admin)["code"] != 20000,
            "negative shelf rejected on create",
        )
        check(
            call(path, "PUT", {**data, "shelf_number": -1}, admin)["code"] != 20000,
            "negative shelf rejected on update",
        )
        check(
            call(path, token=admin)["data"]["shelf_number"] == 0,
            "failed update leaves shelf unchanged",
        )
        check(
            "CHECK" in sql("SHOW CREATE TABLE sf_book;"),
            "SQL check constraints present",
        )
    changed = {**data, case["field"]: case["value"] + "-EDIT"}
    if case["shelf"]:
        changed["shelf_number"] = 7
    check(call(path, "PUT", changed, admin)["code"] == 20000, "field scenario update")
    row = call(path, token=admin)["data"]
    check(
        row[case["field"]] == changed[case["field"]]
        and (not case["shelf"] or row["shelf_number"] == 7),
        "updated fields round trip",
    )
    check(call(path, "DELETE", token=admin)["code"] == 20000, "field scenario cleanup")
    payload["field_case"] = case
    return payload
