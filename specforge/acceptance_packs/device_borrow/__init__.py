"""Device-borrow acceptance pack. Only the verifier's disposable Compose stack is targeted."""

import concurrent.futures
import secrets
from pathlib import Path
from ...workspace import write_json


def accept(origin, password, project, source, reports):
    from ...spec import load
    from ..support import AcceptanceClient

    validate_spec(load(source / "specforge/project.yaml"))
    spec = load(source / "specforge/project.yaml")
    client = AcceptanceClient(origin, password, project, reports)
    check, call, login, sql = client.check, client.call, client.login, client.sql
    checks = client.checks
    admin = login("sfadmin")

    normal = sql("SELECT id FROM system_role WHERE role_code='normal';")
    for name in ["sfa", "sfb"]:
        check(
            call(
                "system/user",
                "POST",
                {"username": name, "password": password, "roleIds": [normal]},
                admin,
            )["code"]
            == 20000,
            "create applicant " + name,
        )
    personal_ids = sql(
        "SELECT id FROM system_permission WHERE authority IN ('business','business:personal','business:personal:me');"
    ).splitlines()
    check(
        call(
            "system/role",
            "POST",
            {
                "roleCode": "sf_none",
                "roleName": "无业务权限",
                "roleStatus": "ENABLED",
                "sort": 30,
                "permissionIds": personal_ids,
            },
            admin,
        )["code"]
        == 20000,
        "create no-access role",
    )
    no_role = sql("SELECT id FROM system_role WHERE role_code='sf_none';")
    check(
        call(
            "system/user",
            "POST",
            {"username": "sfnone", "password": password, "roleIds": [no_role]},
            admin,
        )["code"]
        == 20000,
        "create no-access user",
    )
    # Read-only grant set deliberately excludes create and all workflow actions.
    readonly_ids = sql(
        "SELECT id FROM system_permission WHERE authority IN ('business:sf','business:sf_device','business:sf_device:page','business:sf_device:detail','business:sf_borrow','business:sf_borrow:page','business:sf_borrow:detail');"
    ).splitlines()
    check(
        call(
            "system/role",
            "POST",
            {
                "roleCode": "sf_readonly",
                "roleName": "业务只读",
                "roleStatus": "ENABLED",
                "sort": 31,
                "permissionIds": readonly_ids,
            },
            admin,
        )["code"]
        == 20000,
        "create readonly role",
    )
    readonly_role = sql("SELECT id FROM system_role WHERE role_code='sf_readonly';")
    check(
        call(
            "system/user",
            "POST",
            {"username": "sfread", "password": password, "roleIds": [readonly_role]},
            admin,
        )["code"]
        == 20000,
        "create readonly user",
    )
    a, b, none, readonly = [login(n) for n in ["sfa", "sfb", "sfnone", "sfread"]]

    def sample(e, **overrides):
        value = {}
        for f in e["fields"]:
            if "default" in f:
                value[f["name"]] = f["default"]
            elif f.get("required"):
                value[f["name"]] = {
                    "string": "验收-" + secrets.token_hex(4),
                    "integer": 7,
                    "boolean": True,
                    "datetime": "2026-10-24T12:00:00",
                    "enum": (f.get("values") or [""])[0],
                    "foreign": 1,
                }[f["type"]]
        value.update(overrides)
        return value

    device = next(e for e in spec["entities"] if e["name"] == "device")
    borrow = next(e for e in spec["entities"] if e["name"] == "borrow")
    payload = sample(device, code="API-" + secrets.token_hex(4), name="接口验收设备")
    check(
        call("business/device", "POST", payload, a)["code"] == 40300,
        "applicant cannot create devices",
    )
    check(
        call("business/device/page", token=none)["code"] == 40300,
        "no-access page denied",
    )
    check(
        call("business/borrow", "POST", {"device_id": 1, "reason": "越权"}, readonly)[
            "code"
        ]
        == 40300,
        "readonly mutation denied",
    )
    check(call("business/device/page")["code"] == 40100, "anonymous denied")
    created = call("business/device", "POST", payload, admin)
    check(created["code"] == 20000, "device create")
    did = created["data"]["id"]
    check(
        call("business/device", "POST", payload, admin)["code"] != 20000,
        "duplicate unique code rejected",
    )
    check(
        call("business/device", "POST", {}, admin)["code"] != 20000,
        "required validation",
    )
    check(
        call(
            "business/device",
            "POST",
            {**payload, "code": "bad", "enabled": "yes"},
            admin,
        )["code"]
        != 20000,
        "boolean validation",
    )
    changed = {**payload, "name": "接口验收设备更新"}
    check(
        call("business/device/" + str(did), "PUT", changed, admin)["code"] == 20000,
        "device update",
    )
    check(
        call("business/device/" + str(did), token=a)["data"]["name"] == changed["name"],
        "device detail",
    )
    check(
        call("business/device/page?currentPage=0", token=admin)["code"] != 20000,
        "invalid page rejected",
    )

    def request(token):
        v = sample(borrow, device_id=did, reason="验收用途")
        x = call("business/borrow", "POST", v, token)
        check(x["code"] == 20000, "create borrow")
        return x["data"]["id"]

    own = request(admin)
    check(
        call(f"business/borrow/{own}/actions/approve", "POST", token=admin)["code"]
        != 20000,
        "self approval rejected",
    )
    check(
        call(f"business/borrow/{own}/actions/reject", "POST", token=admin)["code"]
        != 20000,
        "self rejection rejected",
    )
    first = request(a)
    second = request(b)
    check(
        call(f"business/borrow/{first}", token=b)["code"] == 40300,
        "other applicant detail denied",
    )
    page = call("business/borrow/page", token=b)["data"]["items"]
    check(all(str(x["id"]) == str(second) for x in page), "list owner isolation")
    check(
        call(f"business/borrow/{first}/actions/approve", "POST", token=a)["code"]
        == 40300,
        "applicant action denied",
    )
    check(
        call(f"business/borrow/{first}/actions/return_device", "POST", token=admin)[
            "code"
        ]
        != 20000,
        "invalid transition rejected",
    )
    check(
        call(f"business/device/{did}", "DELETE", token=admin)["code"] != 20000,
        "unfinished requests block deletion",
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda i: call(
                    f"business/borrow/{i}/actions/approve", "POST", token=admin
                ),
                [first, second],
            )
        )
    write_json(reports / "concurrent-approvals.json", results)
    check(
        sql(
            "SELECT COUNT(*) FROM sf_borrow WHERE device_id="
            + str(did)
            + " AND status='APPROVED';"
        )
        == "1",
        "database has exactly one active borrow",
    )
    check(
        sum(x["code"] == 20000 for x in results) == 1,
        "concurrent approvals exactly one succeeds: " + str(results),
    )
    winner = [first, second][
        next(i for i, x in enumerate(results) if x["code"] == 20000)
    ]
    loser = second if winner == first else first
    check(
        call(f"business/borrow/{winner}/actions/approve", "POST", token=admin)["code"]
        != 20000,
        "repeat approval rejected",
    )
    check(
        call(f"business/borrow/{winner}/actions/return_device", "POST", token=admin)[
            "code"
        ]
        == 20000,
        "return approved device",
    )
    check(
        call(f"business/borrow/{winner}/actions/return_device", "POST", token=admin)[
            "code"
        ]
        != 20000,
        "repeat return rejected",
    )
    check(
        call(f"business/borrow/{loser}/actions/approve", "POST", token=admin)["code"]
        == 20000,
        "device reusable after return",
    )
    check(
        call(f"business/borrow/{loser}/actions/return_device", "POST", token=admin)[
            "code"
        ]
        == 20000,
        "second return",
    )
    # Resolve the administrator-owned pending request with another explicitly authorized administrator.
    admin_role = sql("SELECT id FROM system_role WHERE role_code='admin';")
    check(
        call(
            "system/user",
            "POST",
            {"username": "sfother", "password": password, "roleIds": [admin_role]},
            admin,
        )["code"]
        == 20000,
        "create second admin",
    )
    other = login("sfother")
    check(
        call(f"business/borrow/{own}/actions/reject", "POST", token=other)["code"]
        == 20000,
        "reject pending request",
    )
    check(
        call(f"business/device/{did}", "DELETE", token=admin)["code"] == 20000,
        "delete after all requests ended",
    )
    check(
        call(f"business/device/{did}", token=admin)["code"] != 20000,
        "deleted device hidden",
    )
    check(
        call(
            "business/borrow", "POST", sample(borrow, device_id=did, reason="已删除"), a
        )["code"]
        != 20000,
        "deleted reference rejected",
    )
    write_json(reports / "api.json", checks)
    return {
        "device": sample(
            device, code="UI-" + secrets.token_hex(4), name="浏览器验收设备"
        ),
        "entities": spec["entities"],
    }


def validate_spec(spec):
    """Fail before building if this domain fixture cannot meaningfully verify the input."""
    entities = {e["name"]: e for e in spec["entities"]}
    if set(entities) != {"device", "borrow"}:
        raise ValueError("device-borrow pack requires device and borrow entities")
    expected = {
        "device": {"code": "string", "name": "string", "enabled": "boolean"},
        "borrow": {"device_id": "foreign", "reason": "string"},
    }
    for name, fields in expected.items():
        actual = {f["name"]: f for f in entities[name]["fields"]}
        if any(
            n not in actual or actual[n]["type"] != kind for n, kind in fields.items()
        ):
            raise ValueError("device-borrow pack incompatible fields: " + name)
        for f in actual.values():
            if f["name"] not in fields and f.get("required") and "default" not in f:
                raise ValueError(
                    "device-borrow browser fixture needs a default for extra required field: "
                    + f["name"]
                )
    device, borrow = entities["device"], entities["borrow"]
    for name, required_form, required_list in [
        ("device", {"code", "name"}, {"code"}),
        ("borrow", {"device_id", "reason"}, {"reason"}),
    ]:
        page = entities[name]["page"]
        if not required_form <= set(page["form"]) or not required_list <= set(
            page["list"]
        ):
            raise ValueError("device-borrow pack incompatible page fields: " + name)
    if device["access"] != "admin" or set(device["crud"]) != {
        "create",
        "update",
        "delete",
        "page",
        "detail",
    }:
        raise ValueError("device-borrow pack requires device management CRUD")
    code = next(f for f in device["fields"] if f["name"] == "code")
    if not code.get("unique") or not code.get("required"):
        raise ValueError("device-borrow pack requires unique required device code")
    ref = next(f for f in borrow["fields"] if f["name"] == "device_id")
    if ref.get("reference") != "device" or not ref.get("required"):
        raise ValueError("device-borrow pack requires a device reference")
    w = borrow.get("workflow", {})
    if w.get("initial") != "PENDING" or set(w.get("states", [])) != {
        "PENDING",
        "APPROVED",
        "REJECTED",
        "RETURNED",
    }:
        raise ValueError("device-borrow pack incompatible workflow states")
    expected_actions = {
        "approve": ("PENDING", "APPROVED", True),
        "reject": ("PENDING", "REJECTED", True),
        "return_device": ("APPROVED", "RETURNED", False),
    }
    actions = {a["name"]: a for a in w.get("transitions", [])}
    if set(actions) != set(expected_actions) or any(
        (actions[n]["from"], actions[n]["to"], actions[n].get("forbid_self", False))
        != values
        for n, values in expected_actions.items()
    ):
        raise ValueError("device-borrow pack incompatible workflow actions")
    exclusive = w.get("exclusive_reference", {})
    if (
        exclusive.get("field") != "device_id"
        or exclusive.get("active_state") != "APPROVED"
        or set(exclusive.get("terminal_states", [])) != {"REJECTED", "RETURNED"}
    ):
        raise ValueError("device-borrow pack incompatible exclusivity")
