"""Reviewed adaptations in the generated copy; source template remains untouched."""

import difflib
import hashlib
import json
from pathlib import Path

ENUM = "backend/src/main/java/com/original/core/enums/FileBusinessType.java"
CLEANER = "backend/src/main/java/com/original/system/task/process/ClearFileProcess.java"
ENUM_MARKER = 'SYSTEM_USER_AVATAR("system_user_avatar", "avatar");'
CLEANER_FIELD = "    private FileService fileService;"
CLEANER_LOOP = "        for (FileEntity fileEntity : unreferencedFiles) {"


def adapt(source):
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
    # Both attaching and maintenance acquire the same file row before checking references.
    # Recheck after the lock: the initial candidate list can become stale.
    patch(
        CLEANER,
        [
            (
                CLEANER_FIELD,
                CLEANER_FIELD
                + "\n\n    @Resource\n    private org.apache.ibatis.session.SqlSessionFactory fileCleanupSessions;",
            ),
            (
                CLEANER_LOOP,
                "        org.springframework.jdbc.core.JdbcTemplate fileCleanupJdbc = new org.springframework.jdbc.core.JdbcTemplate(fileCleanupSessions.getConfiguration().getEnvironment().getDataSource());\n"
                + CLEANER_LOOP
                + """
            if (fileCleanupJdbc.queryForList("SELECT id FROM system_file WHERE id=? FOR UPDATE",fileEntity.getId()).isEmpty()
                || !fileCleanupJdbc.queryForList("SELECT id FROM system_file_reference WHERE file_url=(SELECT file_url FROM system_file WHERE id=?) FOR UPDATE",fileEntity.getId()).isEmpty()) {
                continue;
            }
""",
            ),
        ],
    )
    target = source / "specforge/adaptations/template-reuse.json"
    target.write_text(
        json.dumps(
            {
                "reason": "recipe upload association and cleanup protection",
                "files": evidence,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
