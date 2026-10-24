"""Real multipart and platform cleanup checks, only on the disposable recipe stack."""

import base64
import json
import struct
import time
import urllib.error
import urllib.request
import uuid
import zlib


def png(width=2, height=2):
    def chunk(kind, data):
        return (
            struct.pack("!I", len(data))
            + kind
            + data
            + struct.pack("!I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    pixels = b"".join(b"\x00" + b"\x80\xb0\x60" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(pixels))
        + chunk(b"IEND", b"")
    )


def jpeg():
    return base64.b64decode(
        "/9j/4AAQSkZJRgABAgAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAACAAIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5/ooooA//2Q=="
    )


def upload(client, token, content=None, filename="cover.png"):
    boundary = "sf" + uuid.uuid4().hex
    content = png() if content is None else content
    body = (
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: image/png\r\n\r\n'
        ).encode()
        + content
        + f"\r\n--{boundary}--\r\n".encode()
    )
    headers = {"Content-Type": "multipart/form-data; boundary=" + boundary}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(
        client.origin + "/api/v1/recipes/cover", body, headers, method="POST"
    )
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        data = response.read()
        try:
            return json.loads(data)
        except ValueError:
            return {
                "code": response.status * 100,
                "message": "non-JSON upload rejection",
            }


def accept(client, admin, chef, reader, readonly, none, data):
    check, call, sql = client.check, client.call, client.sql
    for token, label, code in [
        (None, "anonymous", 40100),
        (readonly, "readonly", 40300),
        (none, "no-access", 40300),
    ]:
        check(upload(client, token)["code"] == code, label + " cover upload denied")
    # A platform upload permission alone must not confer recipe-publish authority.
    ids = sql(
        "SELECT id FROM system_permission WHERE authority IN ('business','business:file','business:file:upload','business:personal','business:personal:me');"
    ).splitlines()
    role = client.create_role("file_only", "仅通用上传", ids, admin)
    limited = client.create_user("sffile", [role], admin)
    check(
        upload(client, limited)["code"] == 40300,
        "generic upload permission cannot replace recipe publish permission",
    )
    check(
        upload(client, chef, b"not an image")["code"] != 20000,
        "spoofed PNG payload rejected",
    )
    check(
        upload(client, chef, png(4097, 1))["code"] != 20000,
        "oversized image dimensions rejected",
    )
    check(
        upload(client, chef, b"x" * (5 * 1024 * 1024 + 1))["code"] != 20000,
        "oversized upload rejected",
    )

    def image(token, content=None, filename="cover.png"):
        result = upload(client, token, content, filename)
        check(result["code"] == 20000, "platform image upload works")
        return result["data"]["url"]

    first, second, unused = image(chef), image(chef, jpeg(), "cover.jpg"), image(chef)
    alien = image(reader)

    def relative(url):
        return url.removeprefix("/api/files")

    def refs(url):
        return sql(
            "SELECT COUNT(*) FROM system_file_reference WHERE business_type='recipe_cover' AND file_url='"
            + relative(url)
            + "';"
        )

    check(
        sql(
            "SELECT mime_type FROM system_file WHERE file_url='"
            + relative(first)
            + "';"
        )
        == "image/png",
        "platform MIME detection and metadata agree",
    )
    check(
        call("recipes", "POST", data(cover_url=alien), chef)["code"] != 20000,
        "cannot attach another user image",
    )
    check(
        call("recipes", "POST", data(cover_url="/api/files/../missing.png"), chef)[
            "code"
        ]
        != 20000,
        "forged local image path rejected",
    )
    check(
        call(
            "recipes", "POST", data(cover_url="https://example.invalid" + alien), chef
        )["code"]
        != 20000,
        "absolute URL cannot disguise system image path",
    )

    def create(title, cover):
        result = call("recipes", "POST", data(title=title, cover_url=cover), chef)
        check(result["code"] == 20000, "create recipe with uploaded cover")
        return result["data"]["id"]

    rid = create("上传关联验收", first)
    check(refs(first) == "1", "recipe save creates platform file reference")
    check(
        sql(
            "SELECT mime_type FROM system_file WHERE file_url='"
            + relative(second)
            + "';"
        )
        == "image/jpeg",
        "real JPEG upload and MIME policy work",
    )
    check(
        call(
            f"recipes/{rid}",
            "PUT",
            data(title="上传关联验收", cover_url=second, revision=999),
            chef,
        )["code"]
        != 20000,
        "failed cover update rejected",
    )
    check(
        refs(first) == "1" and refs(second) == "0",
        "failed edit preserves original references",
    )
    check(
        call(
            f"recipes/{rid}",
            "PUT",
            data(title="上传关联验收", cover_url=second, revision=1),
            chef,
        )["code"]
        == 20000,
        "replace cover succeeds",
    )
    check(
        refs(first) == "0" and refs(second) == "1",
        "replacement releases old reference and protects new cover",
    )
    # Real transaction rollback: a trigger fails AFTER reference writes, rather than before validation.
    sql(
        "CREATE TRIGGER sf_cover_rollback BEFORE INSERT ON system_file_reference FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='acceptance rollback';"
    )
    try:
        failed = call(
            f"recipes/{rid}",
            "PUT",
            data(title="不得提交", cover_url=unused, revision=2),
            chef,
        )
        check(failed["code"] != 20000, "injected reference write failure rejected")
    finally:
        sql("DROP TRIGGER sf_cover_rollback;")
    old = call(f"recipes/{rid}", token=chef)["data"]
    check(
        old["title"] == "上传关联验收"
        and old["cover_url"] == second
        and int(old["revision"]) == 2,
        "reference failure rolls back recipe write",
    )
    check(
        refs(second) == "1" and refs(unused) == "0",
        "reference failure rolls back reference replacement",
    )
    another = create("同一图片多处引用", second)
    check(refs(second) == "2", "same owner can share image across recipes")
    check(
        call(
            f"recipes/{rid}",
            "PUT",
            data(title="移除封面", cover_url="", revision=2),
            chef,
        )["code"]
        == 20000,
        "remove cover succeeds",
    )
    check(refs(second) == "1", "removing one cover preserves other recipe reference")
    # Backdate only test files inside the isolated DB, then invoke the template's real cleanup task.
    for url in (first, second, unused):
        sql(
            "UPDATE system_file SET created_time=DATE_SUB(NOW(),INTERVAL 2 MONTH) WHERE file_url='"
            + relative(url)
            + "';"
        )
    task = sql(
        "SELECT id FROM system_scheduled_task WHERE invoke_target='clearFileProcess.clearUnreferencedFile(1)';"
    )
    check(bool(task), "platform cleanup task discovered")
    check(
        call("system/task/status/" + task, "PUT", {}, admin)["code"] == 20000,
        "enable isolated cleanup task",
    )

    def cleanup():
        check(
            call("system/task/execute/" + task, "PUT", {}, admin)["code"] == 20000,
            "invoke platform cleanup task",
        )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if (
                sql(
                    "SELECT COUNT(*) FROM system_file WHERE file_url='"
                    + relative(first)
                    + "';"
                )
                == "0"
            ):
                return
            time.sleep(0.2)
        raise AssertionError("platform cleanup did not finish")

    cleanup()
    check(
        sql(
            "SELECT COUNT(*) FROM system_file WHERE file_url='"
            + relative(unused)
            + "';"
        )
        == "0",
        "cancelled unused upload is cleaned",
    )
    check(
        sql(
            "SELECT COUNT(*) FROM system_file WHERE file_url='"
            + relative(second)
            + "';"
        )
        == "1",
        "referenced cover survives real cleanup",
    )
    with urllib.request.urlopen(client.origin + second, timeout=10) as response:
        check(
            response.read().startswith(b"\xff\xd8\xff"),
            "referenced cover remains physically readable",
        )
    check(
        call(f"recipes/{another}?revision=1", "DELETE", token=chef)["code"] == 20000,
        "delete recipe releases cover",
    )
    check(refs(second) == "0", "last recipe deletion releases last reference")
    check(
        call(f"recipes/{rid}?revision=3", "DELETE", token=chef)["code"] == 20000,
        "media fixture recipe cleanup",
    )
    check(
        call("system/task/execute/" + task, "PUT", {}, admin)["code"] == 20000,
        "cleanup after last reference release",
    )
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if (
            sql(
                "SELECT COUNT(*) FROM system_file WHERE file_url='"
                + relative(second)
                + "';"
            )
            == "0"
        ):
            break
        time.sleep(0.2)
    check(
        sql(
            "SELECT COUNT(*) FROM system_file WHERE file_url='"
            + relative(second)
            + "';"
        )
        == "0",
        "unreferenced replaced cover eventually cleaned",
    )
    check(
        call("system/task/status/" + task, "PUT", {}, admin)["code"] == 20000,
        "pause isolated cleanup task",
    )
    return base64.b64encode(png()).decode()
