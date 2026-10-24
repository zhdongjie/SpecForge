"""Build and disposable deployment orchestration; business checks are selected packs."""

import os
import secrets
import socket
import subprocess
from pathlib import Path
from .acceptance_packs import get_pack
from .browser import BrowserRunner
from .errors import VerificationError
from .coverage import check_requirements
from .spec import load
from .workspace import inventory, digest, write_json, read_json


def command(args, cwd, log, env=None, timeout=1200):
    with Path(log).open("w") as out:
        p = subprocess.run(
            args,
            cwd=cwd,
            env=env,
            stdout=out,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    if p.returncode:
        raise RuntimeError(f"command failed ({p.returncode}): {log}")


def artifact_hashes(source):
    jar = source / "backend/target/original-service-0.0.1-SNAPSHOT.jar"
    if not jar.is_file():
        raise ValueError("production JAR missing")
    files = [jar, *sorted((source / "frontend/dist").rglob("*"))]
    return {p.relative_to(source).as_posix(): digest(p) for p in files if p.is_file()}


def verify(run, build_only=False, reuse_build=False, acceptance_pack=None):
    run = Path(run)
    source = run / "source"
    reports = run / "reports"
    result = {
        "status": "FAIL",
        "checks": {},
        "source_sha256": inventory(source),
        "acceptance_pack": acceptance_pack,
        "build_only": build_only,
    }
    previous = read_json(reports / "verify.json") if reuse_build else None
    stage = "preflight"
    try:
        if reuse_build:
            if (
                previous.get("source_sha256") != inventory(source)
                or previous.get("artifacts_sha256") != artifact_hashes(source)
                or any(
                    previous.get("checks", {}).get(k) != "PASS"
                    for k in ("backend", "frontend")
                )
            ):
                raise ValueError(
                    "Previous build does not match current source/artifacts"
                )
            result["checks"].update(backend="PASS", frontend="PASS")
            result["artifacts_sha256"] = previous["artifacts_sha256"]
        # Resolve business compatibility and browser tooling before expensive builds/deployment.
        if not build_only:
            pack = get_pack(acceptance_pack)
            pack.validate(load(source / "specforge/project.yaml"))
            browser = BrowserRunner.from_environment()
        if not reuse_build:
            stage = "backend"
            command(
                ["mvn", "-B", "-f", "backend/pom.xml", "clean", "verify"],
                source,
                reports / "backend.log",
            )
            result["checks"]["backend"] = "PASS"
            stage = "install"
            command(
                ["pnpm", "install", "--frozen-lockfile"],
                source / "frontend",
                reports / "install.log",
            )
            stage = "frontend"
            command(
                ["pnpm", "build:prod"],
                source / "frontend",
                reports / "frontend.log",
                dict(os.environ, VITE_APP_BASE_API="/api"),
            )
            result["checks"]["frontend"] = "PASS"
        result["source_sha256"] = inventory(source)
        result["artifacts_sha256"] = artifact_hashes(source)
        if build_only:
            result["status"] = "BUILD_ONLY"
            return result
        project = ("sf-accept-" + run.name.lower())[:60]
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        password = "Sf" + secrets.token_hex(6) + "9"
        envfile = run / "acceptance.env"
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
        envfile.write_text(
            "".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8"
        )
        envfile.chmod(0o600)
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
        clean = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith(("APP_", "SPRING_MAIL_", "COMPOSE_"))
        }
        primary = None
        cleanup_errors = []
        try:
            stage = "compose"
            command(
                compose + ["up", "-d", "--build", "--wait", "--wait-timeout", "300"],
                source,
                reports / "compose.log",
                clean,
            )
            result["checks"]["compose"] = "PASS"
            stage = "api"
            payload = pack.run_api(
                f"http://127.0.0.1:{port}", password, project, source, reports
            )
            result["checks"]["api"] = "PASS"
            stage = "browser"
            result["checks"]["browser"] = browser.run(
                pack.browser_script,
                f"http://127.0.0.1:{port}",
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
            for args, name, timeout in [
                (compose + ["logs", "--no-color"], "runtime.log", 60),
                (
                    compose + ["down", "--volumes", "--remove-orphans"],
                    "cleanup.log",
                    180,
                ),
            ]:
                try:
                    command(args, source, reports / name, clean, timeout=timeout)
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
        result["status"] = "PASS"
    except Exception as exc:
        result.update(status="FAIL", failed_stage=stage, error=str(exc))
        raise VerificationError(stage, str(exc)) from exc
    finally:
        write_json(reports / "verify.json", result)
    return result
