"""Quantity-based book lending: domain fixtures are separate from generic allocation rules."""

import concurrent.futures
import secrets
from ...spec import load
from ...workspace import write_json
from ..support import AcceptanceClient


def validate_spec(spec):
    entities = {e["name"]: e for e in spec["entities"]}
    if set(entities) != {"book", "loan"}:
        raise ValueError("book-lending pack requires book and loan entities")
    expected = {
        "book": {"code": "string", "name": "string", "stock": "integer"},
        "loan": {"book_id": "foreign", "quantity": "integer", "reason": "string"},
    }
    for name, fields in expected.items():
        entity = entities[name]
        actual = {f["name"]: f for f in entity["fields"]}
        if any(
            key not in actual or actual[key]["type"] != kind
            for key, kind in fields.items()
        ):
            raise ValueError("book-lending pack incompatible fields: " + name)
        if not set(fields) <= set(entity["page"]["form"]):
            raise ValueError("book-lending pack missing form fields")
        for f in entity["fields"]:
            if f["name"] not in fields and f.get("required") and "default" not in f:
                raise ValueError(
                    "book-lending fixture needs defaults for extra required fields"
                )
    catalog, loan = entities["book"], entities["loan"]
    if catalog["access"] != "admin" or set(catalog["crud"]) != {
        "create",
        "update",
        "delete",
        "page",
        "detail",
    }:
        raise ValueError("book-lending pack requires catalog CRUD")
    code = next(f for f in catalog["fields"] if f["name"] == "code")
    if not code.get("unique") or not code.get("required"):
        raise ValueError("book-lending requires unique book code")
    if not {"code", "stock"} <= set(catalog["page"]["list"]) or not {
        "reason",
        "quantity",
    } <= set(loan["page"]["list"]):
        raise ValueError("book-lending incompatible list fields")
    ref = next(f for f in loan["fields"] if f["name"] == "book_id")
    if ref.get("reference") != "book":
        raise ValueError("book-lending requires book relation")
    w = loan.get("workflow", {})
    expected_ref = {
        "field": "book_id",
        "capacity_field": "stock",
        "quantity_field": "quantity",
        "active_state": "APPROVED",
        "terminal_states": ["REJECTED", "RETURNED"],
    }
    if w.get("initial") != "PENDING" or w.get("capacity_reference") != expected_ref:
        raise ValueError("book-lending requires quantity capacity workflow")
    actions = {a["name"]: a for a in w.get("transitions", [])}
    expected_actions = {
        "approve": ("PENDING", "APPROVED", True),
        "reject": ("PENDING", "REJECTED", True),
        "return_books": ("APPROVED", "RETURNED", False),
    }
    if set(actions) != set(expected_actions) or any(
        (actions[n]["from"], actions[n]["to"], actions[n].get("forbid_self", False))
        != value
        for n, value in expected_actions.items()
    ):
        raise ValueError("book-lending incompatible actions")


def accept(origin, password, project, source, reports):
    spec = load(source / "specforge/project.yaml")
    validate_spec(spec)
    entities = {e["name"]: e for e in spec["entities"]}
    client = AcceptanceClient(origin, password, project, reports)
    check, call, sql = client.check, client.call, client.sql
    admin = client.login("sfadmin")
    normal = sql("SELECT id FROM system_role WHERE role_code='normal';")
    a = client.create_user("liba", [normal], admin)
    b = client.create_user("libb", [normal], admin)
    admin_role = sql("SELECT id FROM system_role WHERE role_code='admin';")
    other = client.create_user("libmgr", [admin_role], admin)
    readonly_ids = sql(
        "SELECT id FROM system_permission WHERE authority IN ('business:sf','business:sf_book','business:sf_book:page','business:sf_book:detail','business:sf_loan','business:sf_loan:page','business:sf_loan:detail');"
    ).splitlines()
    readonly_role = client.create_role("lib_readonly", "借阅只读", readonly_ids, admin)
    readonly = client.create_user("libread", [readonly_role], admin)
    personal = sql(
        "SELECT id FROM system_permission WHERE authority IN ('business','business:personal','business:personal:me');"
    ).splitlines()
    none_role = client.create_role("lib_none", "无借阅权限", personal, admin)
    none = client.create_user("libnone", [none_role], admin)

    def sample(entity, **values):
        result = {
            f["name"]: f["default"]
            for f in entities[entity]["fields"]
            if "default" in f
        }
        result.update(values)
        return result

    data = sample(
        "book", code="API-" + secrets.token_hex(4), name="数量借阅验收图书", stock=3
    )
    check(call("business/book/page")["code"] == 40100, "anonymous catalog denied")
    check(
        call("business/book/page", token=none)["code"] == 40300,
        "no-access catalog denied",
    )
    check(
        call("business/book", "POST", data, a)["code"] == 40300,
        "applicant cannot create catalog",
    )
    created = call("business/book", "POST", data, admin)
    check(created["code"] == 20000, "book CRUD create")
    bid = created["data"]["id"]
    path = "business/book/" + str(bid)
    check(
        call("business/book", "POST", data, admin)["code"] != 20000,
        "unique book code enforced",
    )
    check(
        call(
            "business/book",
            "POST",
            sample("book", code="negative", name="bad", stock=-1),
            admin,
        )["code"]
        != 20000,
        "negative stock rejected",
    )
    check(
        call("business/book", "POST", {}, admin)["code"] != 20000,
        "required catalog fields enforced",
    )
    for method in ("PUT", "DELETE"):
        check(
            call(path, method, data if method == "PUT" else None, a)["code"] == 40300,
            "applicant catalog mutation denied " + method,
        )
    check(call(path, token=readonly)["code"] == 20000, "readonly catalog detail")

    def detail():
        return call(path, token=admin)["data"]

    def available(value, label):
        check(int(detail()["stock_available"]) == value, label)

    def request(token, quantity=1, **extra):
        result = call(
            "business/loan",
            "POST",
            sample(
                "loan", book_id=bid, quantity=quantity, reason="API借阅用途", **extra
            ),
            token,
        )
        check(result["code"] == 20000, "submit quantity request " + str(quantity))
        return result["data"]["id"]

    def action(identifier, name, token=admin):
        return call(f"business/loan/{identifier}/actions/{name}", "POST", token=token)

    def used():
        return int(
            sql(
                "SELECT COALESCE(SUM(quantity),0) FROM sf_loan WHERE book_id="
                + str(bid)
                + " AND status='APPROVED';"
            )
        )

    available(3, "initial available capacity")
    for bad in (0, -1, 1.5, "1e2", 9223372036854775808):
        check(
            call(
                "business/loan",
                "POST",
                sample("loan", book_id=bid, quantity=bad, reason="bad"),
                a,
            )["code"]
            != 20000,
            "invalid loan quantity rejected " + str(bad),
        )
    check(
        call(
            "business/loan",
            "POST",
            sample("loan", book_id=bid, quantity=1, reason="readonly"),
            readonly,
        )["code"]
        == 40300,
        "readonly request denied",
    )
    check(
        call(
            "business/loan",
            "POST",
            sample("loan", book_id=bid, quantity=1, reason="spoof", owner_id=1),
            a,
        )["code"]
        != 20000,
        "owner spoof rejected",
    )
    self_request = request(admin)
    check(action(self_request, "approve")["code"] != 20000, "self approval rejected")
    check(action(self_request, "reject")["code"] != 20000, "self rejection rejected")
    first = request(a, 2)
    second = request(b, 2)
    available(3, "pending requests do not consume capacity")
    check(
        call(f"business/loan/{first}", token=b)["code"] == 40300,
        "other reader detail denied",
    )
    own = call("business/loan/page", token=b)["data"]["items"]
    check(len(own) == 1 and str(own[0]["id"]) == str(second), "reader list ownership")
    check(action(first, "approve", a)["code"] == 40300, "reader approval denied")
    check(action(first, "return_books")["code"] != 20000, "pending return denied")
    check(
        call(path, "DELETE", token=admin)["code"] != 20000,
        "pending loan blocks catalog deletion",
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda i: action(i, "approve"), [first, second]))
    write_json(reports / "quantity-approvals.json", results)
    check(
        sum(x["code"] == 20000 for x in results) == 1,
        "competing quantity approvals exactly one succeeds",
    )
    check(used() == 2, "database active quantity is two, never four")
    winner = [first, second][
        next(i for i, x in enumerate(results) if x["code"] == 20000)
    ]
    loser = second if winner == first else first
    available(1, "availability decreases by requested quantity")
    check(action(winner, "approve")["code"] != 20000, "repeat approval denied")
    check(
        action(loser, "approve")["code"] != 20000,
        "request exceeding remaining quantity denied",
    )
    one = request(a, 1)
    check(
        action(one, "approve")["code"] == 20000,
        "another loan shares remaining inventory",
    )
    check(
        used() == 3
        and sql(
            "SELECT COUNT(*) FROM sf_loan WHERE book_id="
            + str(bid)
            + " AND status='APPROVED';"
        )
        == "2",
        "multiple active loans share one book without overselling",
    )
    available(0, "all stock allocated")
    extra = request(b, 1)
    check(
        action(extra, "approve")["code"] != 20000,
        "zero remaining stock denies approval",
    )
    check(
        call(path, "PUT", {**data, "name": "must roll back", "stock": 2}, admin)["code"]
        != 20000,
        "cannot reduce stock below active quantity",
    )
    check(
        detail()["name"] == data["name"] and int(detail()["stock"]) == 3,
        "failed stock update is atomic",
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        returned = list(pool.map(lambda _: action(winner, "return_books"), range(2)))
    write_json(reports / "quantity-returns.json", returned)
    check(
        sum(x["code"] == 20000 for x in returned) == 1,
        "competing returns exactly one succeeds",
    )
    check(
        used() == 1 and int(detail()["stock"]) == 3,
        "return releases usage without increasing total stock",
    )
    available(2, "quantity return restores exactly two units")
    check(
        action(loser, "approve")["code"] == 20000,
        "freed inventory can be borrowed again",
    )
    check(used() == 3, "reborrow still bounded by total")
    check(action(loser, "return_books")["code"] == 20000, "second quantity return")
    check(
        call(path, "PUT", {**data, "stock": 1}, admin)["code"] == 20000,
        "stock can be reduced to current active quantity",
    )
    available(0, "remaining quantity after stock reduction")
    check(action(extra, "reject")["code"] == 20000, "reject unallocated pending loan")
    check(
        action(self_request, "reject", other)["code"] == 20000,
        "other manager rejects admin-owned loan",
    )
    check(
        call(path, "DELETE", token=admin)["code"] != 20000,
        "active quantity prevents deletion",
    )
    check(action(one, "return_books")["code"] == 20000, "last active loan returned")
    available(1, "last return restores all remaining stock")
    check(
        action(one, "return_books")["code"] != 20000,
        "duplicate final return does not over-release",
    )
    check(
        call(path, "PUT", {**data, "stock": 0}, admin)["code"] == 20000,
        "empty catalog stock allowed",
    )
    zero = request(a, 1)
    check(action(zero, "approve")["code"] != 20000, "zero total stock denies approval")
    check(
        action(zero, "reject")["code"] == 20000,
        "zero-stock pending loan can be rejected",
    )
    check(
        call(path, "DELETE", token=admin)["code"] == 20000,
        "catalog deletable after all loans ended",
    )
    check(call(path, token=admin)["code"] != 20000, "deleted book hidden")
    check(
        call(
            "business/loan",
            "POST",
            sample("loan", book_id=bid, quantity=1, reason="deleted"),
            a,
        )["code"]
        != 20000,
        "deleted catalog relation rejected",
    )
    check(
        call(f"business/loan/{first}", token=a)["code"] == 20000,
        "completed loan history survives catalog removal",
    )
    return {
        "book": sample(
            "book",
            code="UI-" + secrets.token_hex(4),
            name="浏览器借阅验收图书",
            stock=2,
        ),
        "entities": spec["entities"],
    }
