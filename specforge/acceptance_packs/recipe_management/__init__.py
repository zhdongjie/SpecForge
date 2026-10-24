"""Real recipe acceptance: ownership, publication, search, favorites and statistics."""

import concurrent.futures
import copy
from ...spec import load
from ..support import AcceptanceClient


def validate_spec(spec):
    if spec.get("application") != "recipe-management":
        raise ValueError(
            "recipe-management pack requires explicit application extension"
        )
    from ...applications.recipe_management import validate_spec as validate

    validate(spec)


def accept(origin, password, project, source, reports):
    validate_spec(load(source / "specforge/project.yaml"))
    c = AcceptanceClient(origin, password, project, reports)
    check, call, sql = c.check, c.call, c.sql
    admin = c.login("sfadmin")
    normal = sql("SELECT id FROM system_role WHERE role_code='normal';")
    chef = c.create_user("sfchef", [normal], admin)
    reader = c.create_user("sfguest", [normal], admin)
    admin_role = sql("SELECT id FROM system_role WHERE role_code='admin';")
    other_admin = c.create_user("sfjudge", [admin_role], admin)
    personal = sql(
        "SELECT id FROM system_permission WHERE authority IN ('business','business:personal','business:personal:me');"
    ).splitlines()
    read_ids = sql(
        "SELECT id FROM system_permission WHERE authority IN ('business:sf','business:recipes','business:recipes:browse');"
    ).splitlines()
    read_role = c.create_role("recipe_read", "食谱只读", personal + read_ids, admin)
    readonly = c.create_user("sfread", [read_role], admin)
    none_role = c.create_role("recipe_none", "无食谱权限", personal, admin)
    none = c.create_user("sfnone", [none_role], admin)
    root = "recipes"
    check(call(root + "/page")["code"] == 40100, "anonymous recipes denied")
    check(call(root + "/page", token=none)["code"] == 40300, "no-access recipes denied")
    check(
        call(root + "/statistics", token=reader)["code"] == 40300,
        "normal user statistics denied",
    )
    check(
        call(root + "/page?view=review", token=reader)["code"] == 40300,
        "normal user review queue denied",
    )
    for token in (chef, admin):
        for entity in ("recipe", "recipe_ingredient", "recipe_step", "recipe_favorite"):
            check(
                call("business/" + entity + "/page", token=token)["code"] == 40300,
                "raw table bypass denied " + entity,
            )
    categories = call(root + "/categories", token=chef)["data"]
    check(len(categories) == 4, "initial categories available")
    cat = categories[0]["id"]
    base = {
        "title": "葱香番茄炒蛋",
        "summary": "家常快手菜，酸甜鲜香",
        "category_id": cat,
        "servings": 2,
        "prep_minutes": 10,
        "cover_url": "",
        "ingredients": [
            {"name": "番茄", "amount": "2 个"},
            {"name": "鸡蛋", "amount": "3 个"},
        ],
        "steps": ["番茄切块，鸡蛋打散。", "热锅炒熟鸡蛋，加入番茄翻炒调味。"],
    }

    def data(**overrides):
        result = copy.deepcopy(base)
        result.update(overrides)
        return result

    def create(token=chef, **overrides):
        result = call(root, "POST", data(**overrides), token)
        check(
            result["code"] == 20000,
            "create recipe " + overrides.get("title", base["title"]),
        )
        return result["data"]["id"]

    def get(id, token=chef):
        return call(f"{root}/{id}", token=token)

    def action(id, action, token=admin, **extra):
        revision = get(id, token)["data"]["revision"]
        return call(
            f"{root}/{id}/actions/{action}",
            "POST",
            {"revision": revision, **extra},
            token,
        )

    def page(view="published", token=reader, extra=""):
        return call(root + "/page?view=" + view + extra, token=token)

    check(
        call(root, "POST", data(author_id=1), chef)["code"] != 20000,
        "author identity spoof rejected",
    )
    check(
        call(root, "POST", data(publication_state="PUBLISHED"), chef)["code"] != 20000,
        "publication state spoof rejected",
    )
    check(
        call(root, "POST", data(ingredients=[]), chef)["code"] != 20000,
        "empty ingredients rejected",
    )
    check(
        call(root, "POST", data(steps=["x" * 256]), chef)["code"] != 20000,
        "oversized instruction rejected",
    )
    check(
        call(root, "POST", data(cover_url="javascript:alert(1)"), chef)["code"]
        != 20000,
        "unsafe cover URL rejected",
    )
    check(
        call(root, "POST", data(servings=0), chef)["code"] != 20000,
        "zero servings rejected",
    )
    check(
        call(root, "POST", data(prep_minutes=-1), chef)["code"] != 20000,
        "negative preparation time rejected",
    )
    check(
        call(root, "POST", data(), readonly)["code"] == 40300,
        "readonly publishing denied",
    )
    rid = create()
    check(get(rid)["data"]["publication_state"] == "DRAFT", "new recipe starts draft")
    check(get(rid, reader)["code"] == 40300, "other user cannot read draft")
    check(page()["data"]["total"] == 0, "draft absent from public browsing")
    check(page("mine", chef)["data"]["total"] == 1, "author sees own draft")
    check(page("mine", reader)["data"]["total"] == 0, "my recipes ownership filter")
    check(
        call(f"{root}/{rid}", "PUT", data(revision=1), reader)["code"] == 40300,
        "other author cannot edit",
    )
    check(
        call(f"{root}/{rid}", "PUT", data(revision=99), chef)["code"] != 20000,
        "stale update rejected",
    )
    check(
        call(f"{root}/{rid}", "PUT", data(revision=1, steps=[]), chef)["code"] != 20000,
        "invalid detail edit rejected atomically",
    )
    check(len(get(rid)["data"]["steps"]) == 2, "invalid edit preserves prior children")
    check(
        call(f"{root}/{rid}", "PUT", data(revision=1, summary="家常快手菜"), chef)[
            "code"
        ]
        == 20000,
        "author edits draft",
    )
    check(action(rid, "submit", chef)["code"] == 20000, "author submits draft")
    pending = get(rid)["data"]
    check(
        call(f"{root}/{rid}", "PUT", data(revision=pending["revision"]), chef)["code"]
        != 20000,
        "pending recipe not editable",
    )
    check(
        call(f"{root}/{rid}", "DELETE", token=chef)["code"] != 20000,
        "delete requires explicit revision",
    )
    check(
        call(f"{root}/{rid}?revision={pending['revision']}", "DELETE", token=chef)[
            "code"
        ]
        != 20000,
        "pending recipe cannot be deleted",
    )
    check(action(rid, "approve", chef)["code"] == 40300, "normal author cannot approve")
    check(page("review", admin)["data"]["total"] == 1, "manager sees pending queue")
    revision = pending["revision"]
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        responses = list(
            pool.map(
                lambda token: call(
                    f"{root}/{rid}/actions/approve",
                    "POST",
                    {"revision": revision},
                    token,
                ),
                [admin, other_admin],
            )
        )
    check(
        sum(result["code"] == 20000 for result in responses) == 1,
        "competing approvals exactly one success",
    )
    check(
        get(rid, reader)["data"]["publication_state"] == "PUBLISHED",
        "approved recipe publicly readable",
    )
    check(page()["data"]["total"] == 1, "published listing includes approved recipe")
    from urllib.parse import quote

    check(
        page(extra="&keyword=" + quote("番茄"))["data"]["total"] == 1,
        "keyword searches recipe title",
    )
    check(
        page(extra="&keyword=" + quote("家常快手"))["data"]["total"] == 1,
        "keyword searches recipe summary",
    )
    check(
        page(extra="&keyword=" + quote("%"))["data"]["total"] == 0,
        "search wildcard escaped literally",
    )
    check(
        page(extra="&keyword=" + quote("' OR 1=1 --"))["data"]["total"] == 0,
        "search is parameterized",
    )
    check(
        page(extra="&categoryId=" + str(categories[1]["id"]))["data"]["total"] == 0,
        "category filter isolates recipes",
    )
    check(page(extra="&pageSize=0")["code"] != 20000, "invalid pagination rejected")
    with concurrent.futures.ThreadPoolExecutor(3) as pool:
        responses = list(
            pool.map(
                lambda _: call(f"{root}/{rid}/favorite", "POST", {}, reader), range(3)
            )
        )
    check(
        all(result["code"] == 20000 for result in responses),
        "concurrent favorite idempotent",
    )
    check(
        sql(
            f"SELECT COUNT(*) FROM sf_recipe_favorite WHERE recipe_id={rid} AND sf_deleted=0;"
        )
        == "1",
        "database uniqueness prevents duplicate favorite",
    )
    check(page("favorites")["data"]["total"] == 1, "own favorites visible")
    check(page("favorites", chef)["data"]["total"] == 0, "favorites isolated by user")
    check(
        call(f"{root}/{rid}/favorite", "POST", {}, readonly)["code"] == 40300,
        "readonly cannot favorite",
    )
    check(
        call(f"{root}/{rid}/favorite", "DELETE", token=reader)["code"] == 20000,
        "cancel favorite",
    )
    check(
        call(f"{root}/{rid}/favorite", "DELETE", token=reader)["code"] == 20000,
        "cancel favorite idempotent",
    )
    check(
        call(f"{root}/{rid}/favorite", "POST", {}, reader)["code"] == 20000,
        "restore favorite reuses unique record",
    )
    published = get(rid)["data"]
    check(
        call(
            f"{root}/{rid}",
            "PUT",
            data(revision=published["revision"], title="改良番茄炒蛋"),
            chef,
        )["code"]
        == 20000,
        "published edit withdraws to draft",
    )
    check(
        get(rid, reader)["code"] == 40300, "withdrawn content hidden from prior reader"
    )
    check(
        page("favorites")["data"]["total"] == 0,
        "favorites do not leak withdrawn content",
    )
    check(
        call(f"{root}/{rid}/favorite", "POST", {}, reader)["code"] != 20000,
        "cannot favorite draft",
    )
    check(
        call(f"{root}/{rid}/actions/approve", "POST", {"revision": revision}, admin)[
            "code"
        ]
        != 20000,
        "old review revision cannot approve updated content",
    )
    check(action(rid, "submit", chef)["code"] == 20000, "updated author resubmits")
    check(action(rid, "reject", admin)["code"] != 20000, "rejection requires reason")
    check(
        action(rid, "reject", admin, reason="请补充调味说明")["code"] == 20000,
        "manager rejects with explanation",
    )
    check(
        get(rid)["data"]["review_reason"] == "请补充调味说明",
        "author sees rejection reason",
    )
    check(action(rid, "submit", chef)["code"] == 20000, "rejected recipe can resubmit")
    check(action(rid, "approve", admin)["code"] == 20000, "resubmitted recipe approved")
    check(
        page("favorites")["data"]["total"] == 1,
        "favorite visible again after republishing",
    )
    own = create(admin, title="管理员的清汤")
    check(
        action(own, "submit", admin)["code"] == 20000,
        "administrator may publish own content",
    )
    check(
        action(own, "approve", admin)["code"] != 20000,
        "administrator self-approval denied",
    )
    check(
        action(own, "reject", admin, reason="self")["code"] != 20000,
        "administrator self-rejection denied",
    )
    check(
        action(own, "approve", other_admin)["code"] == 20000,
        "other administrator reviews admin author",
    )
    detail = get(rid)["data"]
    check(
        call(f"{root}/{rid}?revision={detail['revision']}", "DELETE", token=reader)[
            "code"
        ]
        == 40300,
        "other author delete denied",
    )
    check(
        call(f"{root}/{rid}?revision={detail['revision']}", "DELETE", token=chef)[
            "code"
        ]
        == 20000,
        "author can delete published recipe",
    )
    check(get(rid, reader)["code"] != 20000, "deleted recipe cannot be read")
    check(
        page("favorites")["data"]["total"] == 0, "deleted recipe hidden from favorites"
    )
    stats = call(root + "/statistics", token=admin)
    check(stats["code"] == 20000, "manager statistics accessible")
    check(
        int(stats["data"]["published"]) == 1 and int(stats["data"]["pending"]) == 0,
        "publication counts correct",
    )
    check(
        int(stats["data"]["favorites"]) == 0,
        "statistics excludes deleted recipe favorites",
    )
    check(
        sum(int(item["count"]) for item in stats["data"]["categories"]) == 1,
        "category distribution matches published count",
    )
    check(
        page(token=readonly)["code"] == 20000, "readonly can browse published content"
    )
    check(
        call(root + "/statistics", token=readonly)["code"] == 40300,
        "readonly statistics denied",
    )
    # Leave three complete, approved recipes for discovery screenshots and manual review.
    for title, summary in [
        ("清爽黄瓜拌木耳", "清爽开胃，适合搭配家常餐桌。"),
        ("南瓜小米粥", "一碗温热，开启舒服的一天。"),
    ]:
        dish = create(title=title, summary=summary)
        check(action(dish, "submit", chef)["code"] == 20000, "seed dish submitted")
        check(action(dish, "approve", admin)["code"] == 20000, "seed dish approved")
    return {"recipe_title": "浏览器番茄炒蛋", "category": "家常菜"}
