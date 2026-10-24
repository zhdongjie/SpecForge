"""Requirement coverage evidence, independent of generator capability completeness."""

from pathlib import Path
import re
import yaml
from .workspace import read_json, write_json, digest

LEGACY_SAMPLES = {"device_borrow", "book_lending", "book_fields_v1", "book_fields_v2"}


def needs_plan(source):
    source = Path(source)
    spec = source / "specforge/project.yaml"
    if not spec.is_file():
        return True
    value = yaml.safe_load(spec.read_text()) or {}
    return (
        bool(value.get("application"))
        or value.get("project", {}).get("id") not in LEGACY_SAMPLES
    )


def check_requirements(source, reports, checks=None):
    source, reports = Path(source), Path(reports)
    plan = source / "specforge/requirements.yaml"
    spec = source / "specforge/project.yaml"
    if not plan.is_file() and not needs_plan(source):
        return None  # Only the four frozen historical sample identities are exempt.
    result = {"status": "FAIL", "items": []}
    try:
        if not plan.is_file():
            raise ValueError("application requirement coverage plan missing")
        definition = yaml.safe_load(plan.read_text())
        if (
            not isinstance(definition, dict)
            or definition.get("version") != 1
            or not definition.get("requirements")
        ):
            raise ValueError("invalid requirement coverage plan")
        api = read_json(reports / "api.json")
        browser = read_json(reports / "browser.json")
        if browser.get("status") != "PASS":
            raise ValueError("browser acceptance incomplete")
        passed = {c["name"] for c in api if c.get("passed") is True}
        failed = {c["name"] for c in api if c.get("passed") is not True}
        browser_checks = set(browser["checks"])
        ids = set()
        for item in definition["requirements"]:
            id = item.get("id", "")
            if not re.fullmatch(r"REQ-[A-Z0-9-]+", id) or id in ids:
                raise ValueError("invalid or duplicate requirement id")
            ids.add(id)
            if (
                not item.get("need")
                or not item.get("rationale")
                or item.get("mode") not in {"reuse", "adapt", "custom"}
            ):
                raise ValueError(
                    "requirement needs decision and implementation rationale: " + id
                )
            files = item.get("sources", [])
            if not isinstance(files, list) or not files:
                raise ValueError("requirement implementation sources missing: " + id)
            template = item.get("template_evidence", [])
            if item["mode"] != "custom" and not template:
                raise ValueError("template evidence missing: " + id)
            for name in [*files, *template]:
                path = source / name
                if (
                    not path.resolve().is_relative_to(source.resolve())
                    or not path.is_file()
                ):
                    raise ValueError(
                        "requirement source evidence missing or unsafe: " + id
                    )
            expected_api = item.get("api", [])
            expected_browser = item.get("browser", [])
            expected_stages = item.get("stages", [])
            if (
                not isinstance(expected_api, list)
                or not isinstance(expected_browser, list)
                or not isinstance(expected_stages, list)
                or not expected_api + expected_browser + expected_stages
            ):
                raise ValueError("requirement acceptance criteria missing: " + id)
            missing = (
                {name for name in expected_stages if (checks or {}).get(name) != "PASS"}
                | (set(expected_api) - passed)
                | (set(expected_api) & failed)
                | (set(expected_browser) - browser_checks)
            )
            if missing:
                raise ValueError(
                    "requirement not verified: "
                    + id
                    + "; "
                    + ", ".join(sorted(missing))
                )
            result["items"].append(
                {
                    "id": id,
                    "need": item["need"],
                    "mode": item["mode"],
                    "status": "PASS",
                    "api": expected_api,
                    "browser": expected_browser,
                    "stages": expected_stages,
                }
            )
        result.update(status="PASS", plan_sha256=digest(plan))
        return result
    except Exception as exc:
        result["error"] = str(exc)
        raise ValueError("requirement coverage failed: " + str(exc)) from exc
    finally:
        write_json(reports / "requirements.json", result)


def require_verified_plan(source, report):
    source = Path(source)
    plan = source / "specforge/requirements.yaml"
    spec = source / "specforge/project.yaml"
    if plan.is_file() or needs_plan(source):
        proof = report.get("requirements", {})
        if (
            not plan.is_file()
            or proof.get("status") != "PASS"
            or proof.get("plan_sha256") != digest(plan)
        ):
            raise ValueError(
                "verified requirement coverage required before publication"
            )
