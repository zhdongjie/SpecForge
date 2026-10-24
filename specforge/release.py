import difflib, hashlib, os, zipfile
from pathlib import Path
from .workspace import read_json, write_json, inventory, digest
from .verification import artifact_hashes, verify
from .errors import RepairNotApplicable, VerificationError


def repair(run):
    """Only a proven, lexical rule is enabled. Unknown failures never trigger speculative edits."""
    run = Path(run)
    source = run / "source"
    report_path = run / "reports/verify.json"
    report = read_json(report_path) if report_path.exists() else {}

    def reject(reason):
        write_json(
            run / "reports/repair.json",
            {"status": "STOPPED", "reason": reason, "attempts": []},
        )
        raise RepairNotApplicable(reason)

    if report.get("status") != "FAIL" or report.get("failed_stage") != "backend":
        reject("Automatic repair only handles a recorded backend compile failure")
    if report.get("source_sha256") != inventory(source):
        reject(
            "Source changed since compiler failure; rerun verification before repair"
        )
    acceptance_pack = report.get("acceptance_pack")
    build_only = report.get("build_only", False)
    attempts = []
    for number in range(1, 3):
        log = run / "reports/backend.log"
        text = log.read_text(errors="replace") if log.exists() else ""
        changed = []
        # Existing generated record imports can be repaired deterministically, without touching platform code.
        if "cannot find symbol" in text and "LocalDateTime" in text:
            for p in (
                source / "backend/src/main/java/com/original/business/generated"
            ).glob("*Input.java"):
                before = p.read_text()
                if (
                    "LocalDateTime" in before
                    and "import java.time.LocalDateTime;" not in before
                ):
                    after = before.replace(
                        "package com.original.business.generated;",
                        "package com.original.business.generated;\nimport java.time.LocalDateTime;",
                    )
                    p.write_text(after)
                    changed += list(
                        difflib.unified_diff(
                            before.splitlines(True),
                            after.splitlines(True),
                            fromfile=str(p.relative_to(source)),
                            tofile=str(p.relative_to(source)),
                        )
                    )
        if not changed:
            write_json(
                run / "reports/repair.json",
                {
                    "status": "STOPPED",
                    "reason": "unknown or repeated failure; no applicable proven repair",
                    "attempts": attempts,
                },
            )
            raise RepairNotApplicable(
                "No safe deterministic repair; inspect reports/verify.json and build logs"
            )
        patch = run / "reports" / f"repair-{number}.patch"
        patch.write_text("".join(changed))
        attempts.append({"rule": "missing-java-time-import", "patch": patch.name})
        try:
            result = verify(run, build_only=build_only, acceptance_pack=acceptance_pack)
            write_json(
                run / "reports/repair.json", {"status": "PASS", "attempts": attempts}
            )
            return result
        except VerificationError as exc:
            if exc.stage != "backend":
                write_json(
                    run / "reports/repair.json",
                    {"status": "STOPPED", "reason": str(exc), "attempts": attempts},
                )
                raise
            continue
    write_json(run / "reports/repair.json", {"status": "STOPPED", "attempts": attempts})
    raise RuntimeError("Repair limit reached")


def package(run, workspace):
    run = Path(run)
    workspace = Path(workspace)
    source = run / "source"
    report = read_json(run / "reports/verify.json")
    if report.get("status") != "PASS" or set(report.get("checks", {})) != {
        "backend",
        "frontend",
        "compose",
        "api",
        "browser",
    }:
        raise ValueError("Full acceptance PASS required before publication")
    if any(v != "PASS" for v in report["checks"].values()):
        raise ValueError("Acceptance incomplete")
    if report["source_sha256"] != inventory(source) or report[
        "artifacts_sha256"
    ] != artifact_hashes(source):
        raise ValueError("Source or compiled artifacts changed after verification")
    manifest = read_json(run / "manifest.json")
    files = {name: source / name for name in report["source_sha256"]}
    files.update({name: source / name for name in report["artifacts_sha256"]})
    if not any(n.startswith("frontend/dist/assets/") for n in files):
        raise ValueError("frontend production assets missing")
    identity = manifest["identity"]
    name = identity["project"]["id"] + "-" + run.name + ".zip"
    releases = workspace / "releases"
    releases.mkdir(exist_ok=True)
    dest = releases / name
    tmp = dest.with_suffix(".tmp")
    bundle = {
        "identity": identity,
        "sha256": {n: digest(p) for n, p in sorted(files.items())},
        "verification": report,
    }
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n, p in sorted(files.items()):
            z.write(p, "admin-platform/" + n)
        import json

        z.writestr(
            "admin-platform/MANIFEST.json",
            json.dumps(bundle, ensure_ascii=False, indent=2),
        )
    os.replace(tmp, dest)
    checksum = digest(dest)
    dest.with_suffix(".zip.sha256").write_text(checksum + "  " + dest.name + "\n")
    result = {
        "status": "PASS",
        "run_id": run.name,
        "archive": str(dest),
        "sha256": checksum,
    }
    write_json(workspace / "published.json", result)
    write_json(run / "reports/package.json", result)
    return result
