"""Reviewed adaptations in the generated copy; source template remains untouched."""

import difflib
import hashlib
import json
from pathlib import Path

ENUM = "backend/src/main/java/com/original/core/enums/FileBusinessType.java"
CLEANER = "backend/src/main/java/com/original/system/task/process/ClearFileProcess.java"
ENUM_MARKER = 'SYSTEM_USER_AVATAR("system_user_avatar", "avatar");'
LIFECYCLE_GUARD = "backend/src/main/java/com/original/system/file/service/FileLifecycleGuard.java"
CLEANER_MARKER = "fileLifecycleGuard.lockUnreferencedFile"


def adapt(source):
    if not (source / LIFECYCLE_GUARD).is_file() or not (source / CLEANER).is_file() or CLEANER_MARKER not in (source / CLEANER).read_text() or "READ_COMMITTED" not in (source / CLEANER).read_text():
        raise ValueError("template reuse contract changed; shared file lifecycle cleanup required")
    evidence = []

    def patch(name, changes):
        path = source / name
        before_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        before = path.read_text()
        after = before
        for old, new in changes:
            if after.count(old) != 1:
                raise ValueError("template reuse contract changed; inspect " + name)
            after = after.replace(old, new)
        path.write_text(after)
        patch_name = Path(name).name + ".patch"
        target = source / "specforge/adaptations" / patch_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "".join(
                difflib.unified_diff(
                    before.splitlines(True),
                    after.splitlines(True),
                    fromfile=name,
                    tofile=name,
                )
            )
        )
        evidence.append(
            {
                "path": name,
                "before_sha256": before_hash,
                "after_sha256": hashlib.sha256(after.encode()).hexdigest(),
                "patch": patch_name,
            }
        )

    patch(
        ENUM,
        [
            (
                ENUM_MARKER,
                'SYSTEM_USER_AVATAR("system_user_avatar", "avatar"),\n    RECIPE_COVER("recipe_cover", "cover_url");',
            )
        ],
    )
    target = source / "specforge/adaptations/template-reuse.json"
    target.write_text(
        json.dumps(
            {
                "reason": "recipe file business type; cleanup supplied by template",
                "template_capabilities": {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in (LIFECYCLE_GUARD, CLEANER)},
                "files": evidence,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
