#!/usr/bin/env python3
"""Validate a released archive and deploy only its extracted production artifacts.

This is development acceptance tooling, not an application dependency or core CLI.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import socket
import stat
import subprocess
import sys
import tempfile
import traceback
import uuid
import zipfile

# Permit direct execution without installing the source checkout as a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from specforge.acceptance_packs import get_pack
from specforge.browser import BrowserRunner
from specforge.coverage import check_requirements, require_verified_plan
from specforge.spec import load
from specforge.workspace import digest, read_json, write_json

REQUIRED = {
    "deploy/compose.yaml",
    "deploy/Dockerfile.backend",
    "deploy/Dockerfile.frontend",
    "deploy/nginx.conf",
    "backend/target/original-service-0.0.1-SNAPSHOT.jar",
    "backend/src/main/resources/sql/schema.sql",
    "specforge/project.yaml",
    "specforge/identity.json",
    "frontend/dist/index.html",
}


def validate_extract(archive, destination):
    archive, destination = Path(archive), Path(destination)
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    expected = checksum.read_text().split()[0]
    if not re.fullmatch(r"[0-9a-f]{64}", expected) or digest(archive) != expected:
        raise ValueError("archive checksum mismatch")
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len(entries) > 20000 or sum(i.file_size for i in entries) > 1024**3:
            raise ValueError("archive exceeds extraction limits")
        names = set()
        for item in entries:
            name = item.filename
            path = PurePosixPath(name)
            if (
                "\\" in name
                or "\x00" in name
                or path.is_absolute()
                or any(p in {"", ".", ".."} or ":" in p for p in name.split("/"))
                or not name.startswith("admin-platform/")
                or len(path.parts) < 2
                or name in names
                or item.is_dir()
            ):
                raise ValueError("unsafe or duplicate archive path: " + name)
            mode = item.external_attr >> 16
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError("archive links or special files rejected")
            names.add(name)
        manifest_name = "admin-platform/MANIFEST.json"
        manifest = json.loads(bundle.read(manifest_name))
        hashes = manifest.get("sha256")
        if not isinstance(hashes, dict) or not REQUIRED <= set(hashes):
            raise ValueError("required deployment files missing")
        if names != {"admin-platform/" + n for n in hashes} | {manifest_name}:
            raise ValueError("archive inventory mismatch")
        for name, expected_hash in hashes.items():
            if (
                hashlib.sha256(bundle.read("admin-platform/" + name)).hexdigest()
                != expected_hash
            ):
                raise ValueError("manifest hash mismatch: " + name)
        if not any(n.startswith("frontend/dist/assets/") for n in hashes):
            raise ValueError("frontend production assets missing")
        proof = manifest.get("verification", {})
        if proof.get("status") != "PASS" or any(
            proof.get("checks", {}).get(k) != "PASS"
            for k in ("backend", "frontend", "compose", "api", "browser")
        ):
            raise ValueError("archive has no full acceptance proof")
        destination.mkdir(parents=True, exist_ok=False)
        for item in entries:
            target = destination / item.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(bundle.read(item))
    source = destination / "admin-platform"
    if read_json(source / "specforge/identity.json") != manifest["identity"]:
        raise ValueError("archive identity mismatch")
    if digest(source / "specforge/project.yaml") != manifest["identity"]["spec_sha256"]:
        raise ValueError("spec identity hash mismatch")
    require_verified_plan(source, manifest["verification"])
    return source, manifest


def validate_compose(config, source, project=None):
    """No host mounts outside extraction; no external volumes/networks."""
    source = source.resolve()
    services = config.get("services", {})
    if set(services) != {"db", "redis", "backend", "frontend"}:
        raise ValueError("unexpected deployment services")
    for kind in ("volumes", "networks"):
        if any(v and v.get("external") for v in config.get(kind, {}).values()):
            raise ValueError("external deployment resources rejected")
        if project and any(
            v and v.get("name") != project + "_" + key
            for key, v in config.get(kind, {}).items()
        ):
            raise ValueError("deployment resource name outside isolated project")
    for name, service in services.items():
        if (
            service.get("privileged")
            or service.get("network_mode")
            or service.get("volumes_from")
        ):
            raise ValueError("unsafe deployment service configuration")
        for mount in service.get("volumes", []):
            if mount["type"] == "bind":
                path = Path(mount["source"]).resolve()
                if not path.is_relative_to(source):
                    raise ValueError("deployment bind outside extracted release")
        build = service.get("build")
        if build:
            if not Path(build["context"]).resolve().is_relative_to(source):
                raise ValueError("build context outside extracted release")
            dockerfile = Path(build["context"]) / build.get("dockerfile", "Dockerfile")
            if not dockerfile.resolve().is_relative_to(source):
                raise ValueError("Dockerfile outside extracted release")
            text = dockerfile.read_text().lower()
            if re.search(r"\b(mvn|mvnw|pnpm|npm|specforge)\b", text):
                raise ValueError(
                    "release deployment must not rebuild application source"
                )
        for port in service.get("ports", []):
            if port.get("host_ip") != "127.0.0.1":
                raise ValueError("deployment port must bind loopback")


def verify_release(archive, reports, acceptance_pack):
    archive, reports = Path(archive).resolve(), Path(reports).resolve()
    reports.mkdir(parents=True, exist_ok=False)
    result = {
        "status": "FAIL",
        "archive": str(archive),
        "acceptance_pack": acceptance_pack,
        "checks": {},
    }
    stage = "archive"
    values = {}

    def clean_text(text):
        for value in values.values():
            if len(value) >= 12:
                text = text.replace(value, "[REDACTED]")
        return text

    def command(args, source, logfile, env, timeout=600):
        # File streaming avoids holding verbose docker logs in memory.
        path = reports / logfile
        try:
            with path.open("w") as out:
                completed = subprocess.run(
                    args,
                    cwd=source,
                    env=env,
                    stdout=out,
                    stderr=subprocess.STDOUT,
                    timeout=timeout,
                )
        finally:
            if path.exists():
                path.write_text(clean_text(path.read_text(errors="replace")))
        if completed.returncode:
            raise RuntimeError("command failed; inspect " + logfile)

    try:
        pack = get_pack(acceptance_pack)
        with tempfile.TemporaryDirectory(prefix="sf-release-") as temp:
            source, manifest = validate_extract(archive, Path(temp) / "extracted")
            result.update(
                identity=manifest["identity"],
                archive_sha256=digest(archive),
                extraction_root=str(source),
                extraction_temporary=True,
            )
            result["checks"]["archive"] = "PASS"
            pack.validate(load(source / "specforge/project.yaml"))
            stage = "preflight"
            browser = BrowserRunner.from_environment()
            project = "sf-accept-release-" + uuid.uuid4().hex[:16]
            result["compose_project"] = project
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            password = "Sf" + secrets.token_hex(6) + "9"
            values = {
                "APP_MYSQL_ROOT_PASSWORD": secrets.token_hex(24),
                "APP_DATABASE_PASSWORD": secrets.token_hex(24),
                "APP_REDIS_PASSWORD": secrets.token_hex(24),
                "APP_HTTP_PORT": str(port),
                "APP_PUBLIC_URL": f"http://127.0.0.1:{port}",
                "APP_BOOTSTRAP_ENABLED": "true",
                "APP_BOOTSTRAP_USERNAME": "sfadmin",
                "APP_BOOTSTRAP_PASSWORD": password,
            }
            envfile = Path(temp) / "acceptance.env"
            envfile.write_text("".join(k + "=" + v + "\n" for k, v in values.items()))
            envfile.chmod(0o600)
            env = {
                k: v
                for k, v in os.environ.items()
                if not k.startswith(("APP_", "SPRING_MAIL_", "COMPOSE_"))
            }
            compose = [
                "docker",
                "compose",
                "-p",
                project,
                "--env-file",
                str(envfile),
                "-f",
                str(source / "deploy/compose.yaml"),
            ]
            primary = None
            cleanup_errors = []
            started = False
            try:
                stage = "compose-config"
                config = json.loads(
                    subprocess.check_output(
                        compose + ["config", "--format", "json"], cwd=source, env=env
                    )
                )
                validate_compose(config, source, project)
                stage = "compose"
                started = True
                command(
                    compose
                    + ["up", "-d", "--build", "--wait", "--wait-timeout", "300"],
                    source,
                    "compose.log",
                    env,
                )
                result["checks"]["compose"] = "PASS"
                stage = "mounts"
                ids = subprocess.check_output(
                    compose + ["ps", "-q"], cwd=source, env=env, text=True
                ).split()
                containers = json.loads(
                    subprocess.check_output(["docker", "inspect", *ids], text=True)
                )
                if len(containers) != 4:
                    raise ValueError("expected four isolated release services")
                mounts = []
                for container in containers:
                    if (
                        container["Config"]["Labels"].get("com.docker.compose.project")
                        != project
                    ):
                        raise ValueError("container project mismatch")
                    for mount in container["Mounts"]:
                        if mount["Type"] == "bind" and not Path(
                            mount["Source"]
                        ).resolve().is_relative_to(source):
                            raise ValueError("runtime mount outside extracted release")
                        if mount["Type"] == "volume":
                            volume = json.loads(
                                subprocess.check_output(
                                    ["docker", "volume", "inspect", mount["Name"]]
                                )
                            )[0]
                            if (volume.get("Labels") or {}).get(
                                "com.docker.compose.project"
                            ) != project:
                                raise ValueError("runtime volume is not isolated")
                        mounts.append(
                            {k: mount[k] for k in ("Type", "Source", "Destination")}
                        )
                write_json(reports / "mounts.json", mounts)
                result["checks"]["mounts"] = "PASS"
                stage = "api"
                payload = pack.run_api(
                    values["APP_PUBLIC_URL"], password, project, source, reports
                )
                result["checks"]["api"] = "PASS"
                stage = "browser"
                result["checks"]["browser"] = browser.run(
                    pack.browser_script,
                    values["APP_PUBLIC_URL"],
                    password,
                    reports,
                    payload,
                )
                stage = "coverage"
                coverage = check_requirements(source, reports, result["checks"])
                if coverage is not None:
                    result["requirements"] = coverage
            except Exception as exc:
                primary = exc
            finally:
                if started:
                    for args, log in [
                        (compose + ["logs", "--no-color"], "runtime.log"),
                        (
                            compose + ["down", "--volumes", "--remove-orphans"],
                            "cleanup.log",
                        ),
                    ]:
                        try:
                            command(args, source, log, env, timeout=180)
                        except Exception as exc:
                            cleanup_errors.append(str(exc))
                if started and not cleanup_errors:
                    for args in (
                        [
                            "docker",
                            "ps",
                            "-aq",
                            "--filter",
                            "label=com.docker.compose.project=" + project,
                        ],
                        [
                            "docker",
                            "volume",
                            "ls",
                            "-q",
                            "--filter",
                            "label=com.docker.compose.project=" + project,
                        ],
                        [
                            "docker",
                            "network",
                            "ls",
                            "-q",
                            "--filter",
                            "label=com.docker.compose.project=" + project,
                        ],
                    ):
                        try:
                            if subprocess.check_output(args, text=True).strip():
                                cleanup_errors.append(
                                    "isolated resources remain after cleanup"
                                )
                        except Exception as exc:
                            cleanup_errors.append(str(exc))
                envfile.unlink(missing_ok=True)
            if cleanup_errors:
                result["cleanup_errors"] = cleanup_errors
            if primary is not None:
                raise primary
            if cleanup_errors:
                stage = "cleanup"
                raise RuntimeError("; ".join(cleanup_errors))
            result["checks"]["cleanup"] = "PASS"
        result["status"] = "PASS"
    except Exception as exc:
        result.update(failed_stage=stage, error=clean_text(str(exc)))
        (reports / "diagnostic.txt").write_text(clean_text(traceback.format_exc()))
    finally:
        write_json(reports / "release.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--reports", required=True)
    parser.add_argument("--acceptance-pack", required=True)
    args = parser.parse_args()
    result = verify_release(args.archive, args.reports, args.acceptance_pack)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k != "identity"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
