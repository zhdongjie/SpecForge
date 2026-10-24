"""Recipe application owns its author/publication semantics and custom UI."""

import re
from pathlib import Path
from .definition import ENTITIES

ASSETS = Path(__file__).with_name("assets")


def validate_spec(spec):
    if spec["entities"] != ENTITIES:
        raise ValueError(
            "recipe-management requires the explicit recipe application entity contract"
        )


def permissions(spec, standard):
    # Only category CRUD uses the generic engine. Never grant raw recipe table access.
    result = [
        p
        for p in standard
        if p["authority"] == "business:sf"
        or p["authority"].startswith("business:sf_recipe_category")
    ]
    root = next(p["id"] for p in result if p["authority"] == "business:sf")

    def add(
        number, authority, label, kind, roles, route=None, component=None, parent=root
    ):
        result.append(
            dict(
                id=891000000000000 + number,
                parent_id=parent,
                authority=authority,
                label=label,
                kind=kind,
                route=route,
                component=component,
                roles=roles,
            )
        )

    both = ["admin", "normal"]
    add(
        1,
        "business:recipes",
        "食谱厨房",
        "TEMPLATE",
        both,
        "/business/recipes",
        "/business/recipes/index.vue",
    )
    for i, (action, label, roles) in enumerate(
        [
            ("browse", "浏览菜谱", both),
            ("publish", "发布菜谱", both),
            ("favorite", "收藏菜谱", both),
            ("review", "审核菜谱", ["admin"]),
        ],
        2,
    ):
        add(
            i,
            "business:recipes:" + action,
            label,
            "BUTTON",
            roles,
            parent=891000000000001,
        )
    add(
        10,
        "business:recipe_stats",
        "食谱统计",
        "TEMPLATE",
        ["admin"],
        "/business/recipe_stats",
        "/business/recipe_stats/index.vue",
    )
    add(
        11,
        "business:recipes:statistics",
        "查看统计",
        "BUTTON",
        ["admin"],
        parent=891000000000010,
    )
    return result


def emit(source):
    # appConfig is the template's explicit application branding configuration.
    config = source / "frontend/src/appConfig.ts"
    content, count = re.subn(
        r"name:\s*'[^']*'", "name: '食谱管理系统'", config.read_text(), count=1
    )
    if count != 1:
        raise ValueError(
            "recipe application requires the template appConfig.name extension"
        )
    config.write_text(content)
    for asset, destination in [
        (
            "RecipeResource.java",
            "backend/src/main/java/com/original/business/recipes/RecipeResource.java",
        ),
        ("RecipePanel.vue", "frontend/src/pages/business/recipes/index.vue"),
        ("RecipeStats.vue", "frontend/src/pages/business/recipe_stats/index.vue"),
    ]:
        target = source / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((ASSETS / asset).read_text())
    (source / "RECIPE_SYSTEM.md").write_text((ASSETS / "RECIPE_SYSTEM.md").read_text())
    return """
ALTER TABLE sf_recipe ADD INDEX recipe_browse(publication_state,sf_deleted,category_id,id), ADD INDEX recipe_author(author_id,sf_deleted,id);
ALTER TABLE sf_recipe_ingredient ADD UNIQUE KEY recipe_ingredient_position(recipe_id,position);
ALTER TABLE sf_recipe_step ADD UNIQUE KEY recipe_step_position(recipe_id,position);
ALTER TABLE sf_recipe_favorite ADD UNIQUE KEY recipe_user_favorite(recipe_id,user_id), ADD INDEX favorite_user(user_id,sf_deleted);
INSERT INTO sf_recipe_category(name) VALUES ('家常菜'),('素食'),('汤羹'),('烘焙');
"""
