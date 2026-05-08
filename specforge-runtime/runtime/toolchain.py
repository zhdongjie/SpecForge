from __future__ import annotations

import os
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any


def resolve_toolchain(
    local_repo: str = ".m2/repository",
    minimum_java_major: int = 17,
    minimum_maven_version: tuple[int, int, int] = (3, 6, 3),
) -> dict[str, Any]:
    env = os.environ.copy()
    java_home, java_home_source, rejected_java = _resolve_java_home(env, minimum_java_major)
    maven_command, maven_source, rejected_maven = _resolve_maven_command(env, minimum_maven_version)

    if java_home is not None:
        env["JAVA_HOME"] = str(java_home)
        env["Path"] = str(java_home / "bin") + os.pathsep + env.get("Path", "")

    binding = {
        "java_home": str(java_home) if java_home is not None else None,
        "java_home_source": java_home_source,
        "java_command": _resolve_java_command(env),
        "maven_command": maven_command,
        "maven_source": maven_source,
        "local_repo": local_repo,
        "minimum_java_major": minimum_java_major,
        "minimum_maven_version": ".".join(str(part) for part in minimum_maven_version),
        "rejected_java_homes": rejected_java,
        "rejected_maven_commands": rejected_maven,
    }
    return {
        "env": env,
        "binding": binding,
        "java_home": str(java_home) if java_home is not None else None,
        "maven_command": maven_command,
    }


def _resolve_java_home(
    env: dict[str, str], minimum_java_major: int
) -> tuple[Path | None, str | None, list[dict[str, Any]]]:
    rejected: list[dict[str, Any]] = []
    for candidate, source in _iter_java_home_candidates(env):
        if not _is_java_home(candidate):
            continue
        major = _detect_java_major(candidate / "bin" / "java.exe")
        if major is None or major < minimum_java_major:
            rejected.append(
                {
                    "candidate": str(candidate),
                    "source": source,
                    "detected_major": major,
                    "reason": "java-version-too-old",
                }
            )
            continue
        return candidate, source, rejected
    return None, None, rejected


def _resolve_java_command(env: dict[str, str]) -> str | None:
    return shutil.which("java", path=env.get("Path"))


def _resolve_maven_command(
    env: dict[str, str], minimum_maven_version: tuple[int, int, int]
) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    rejected: list[dict[str, Any]] = []
    for candidate, source in _iter_maven_command_candidates(env):
        if not candidate.exists():
            continue
        version = _detect_maven_version(candidate)
        if version is None or version < minimum_maven_version:
            rejected.append(
                {
                    "candidate": str(candidate),
                    "source": source,
                    "detected_version": _format_version(version),
                    "reason": "maven-version-too-old",
                }
            )
            continue
        return str(candidate), source, rejected
    return None, None, rejected


def _iter_java_home_candidates(env: dict[str, str]) -> list[tuple[Path, str]]:
    candidates: list[tuple[Path, str]] = []
    for key in ("SPECFORGE_JAVA_HOME", "JAVA_HOME"):
        raw_value = env.get(key)
        if raw_value:
            candidates.append((Path(raw_value), f"env:{key}"))

    java_on_path = shutil.which("java", path=env.get("Path"))
    if java_on_path:
        java_path = Path(java_on_path).resolve()
        candidates.append((java_path.parent.parent, "path:java"))

    candidates.extend((candidate, "scan:common-install") for candidate in _iter_common_java_homes())
    return _dedupe_path_candidates(candidates)


def _iter_maven_command_candidates(env: dict[str, str]) -> list[tuple[Path, str]]:
    candidates: list[tuple[Path, str]] = []
    override = env.get("SPECFORGE_MAVEN_CMD")
    if override:
        candidates.append((Path(override), "env:SPECFORGE_MAVEN_CMD"))

    for key in ("SPECFORGE_MAVEN_HOME", "MAVEN_HOME", "M2_HOME"):
        raw_value = env.get(key)
        if not raw_value:
            continue
        candidates.extend((candidate, f"env:{key}") for candidate in _maven_commands_from_home(Path(raw_value)))

    for executable in ("mvn.cmd", "mvn"):
        resolved = shutil.which(executable, path=env.get("Path"))
        if resolved:
            candidates.append((Path(resolved), f"path:{executable}"))

    candidates.extend((candidate, "scan:common-install") for candidate in _iter_common_maven_commands())
    return _dedupe_path_candidates(candidates)


def _maven_commands_from_home(home: Path) -> tuple[Path, Path]:
    return (home / "bin" / "mvn.cmd", home / "bin" / "mvn")


def _iter_common_java_homes() -> list[Path]:
    candidates: list[Path] = []
    for drive in ("C:\\", "D:\\", "E:\\"):
        candidates.extend(
            [
                Path(drive) / "Program Files" / "Java",
                Path(drive) / "Program Files" / "Eclipse Adoptium",
                Path(drive) / "Program Files" / "Microsoft",
                Path(drive) / "Dev" / "JDK",
                Path(drive) / "tools",
            ]
        )

    homes: list[Path] = []
    for parent in candidates:
        if not parent.exists() or not parent.is_dir():
            continue
        for child in sorted(parent.iterdir()):
            if child.is_dir():
                homes.append(child)
    return homes


def _iter_common_maven_commands() -> list[Path]:
    roots = [
        Path(r"C:\Program Files\Apache"),
        Path(r"C:\Program Files"),
        Path(r"C:\tools"),
        Path(r"C:\apache-maven"),
        Path(r"D:\tools"),
        Path(r"E:\Dev\Maven"),
    ]
    commands: list[Path] = []
    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            commands.extend(_maven_commands_from_home(child))
            if child.name.lower().startswith("apache-maven"):
                commands.extend(_maven_commands_from_home(child))
    return commands


def _is_java_home(candidate: Path) -> bool:
    return candidate.exists() and (candidate / "bin" / "java.exe").exists()


def _dedupe_path_candidates(candidates: list[tuple[Path, str]]) -> list[tuple[Path, str]]:
    deduped: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for candidate, source in candidates:
        key = str(candidate).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append((candidate, source))
    return deduped


@lru_cache(maxsize=None)
def _detect_java_major(java_command: Path) -> int | None:
    try:
        completed = subprocess.run(
            [str(java_command), "-version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    for token in output.replace('"', " ").split():
        if token.count(".") >= 1 and token[0].isdigit():
            if token.startswith("1.8"):
                return 8
            try:
                return int(token.split(".")[0])
            except ValueError:
                continue
    return None


@lru_cache(maxsize=None)
def _detect_maven_version(maven_command: Path) -> tuple[int, int, int] | None:
    try:
        completed = subprocess.run(
            [str(maven_command), "-version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    for line in output.splitlines():
        normalized = line.strip()
        if not normalized.startswith("Apache Maven "):
            continue
        raw_version = normalized[len("Apache Maven ") :].strip().split()[0]
        parts = raw_version.split(".")
        if len(parts) < 2:
            return None
        numeric = []
        for part in parts[:3]:
            try:
                numeric.append(int(part))
            except ValueError:
                numeric.append(0)
        while len(numeric) < 3:
            numeric.append(0)
        return tuple(numeric[:3])
    return None


def _format_version(version: tuple[int, int, int] | None) -> str | None:
    if version is None:
        return None
    return ".".join(str(part) for part in version)
