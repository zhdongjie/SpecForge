from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
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

    if java_home is not None:
        env["JAVA_HOME"] = str(java_home)
        path_value = os.pathsep.join(
            part
            for part in [str(java_home / "bin"), env.get("PATH", ""), env.get("Path", "")]
            if part
        )
        env["PATH"] = path_value
        env["Path"] = path_value

    maven_command, maven_source, rejected_maven = _resolve_maven_command(env, minimum_maven_version)
    local_repo = _normalize_local_repo(local_repo, java_home)

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


def _normalize_local_repo(local_repo: str, java_home: Path | None) -> str:
    if java_home is None or not str(java_home).startswith(str(Path(tempfile.gettempdir()) / "specforge-wsl-java-home-")):
        return local_repo
    repo_path = Path(local_repo)
    if str(repo_path).startswith("/mnt/"):
        return str(repo_path)
    root = Path(os.environ.get("SPECFORGE_WINDOWS_LOCAL_REPO_ROOT", "/mnt/d/SpecForge/maven-repositories"))
    return str(root / _safe_repo_name(repo_path))


def _safe_repo_name(path: Path) -> str:
    resolved = str(path.resolve() if path.exists() else path)
    safe = "".join(ch if ch.isalnum() else "-" for ch in resolved).strip("-")
    return safe[-120:] or "repository"


def _resolve_java_home(
    env: dict[str, str], minimum_java_major: int
) -> tuple[Path | None, str | None, list[dict[str, Any]]]:
    rejected: list[dict[str, Any]] = []
    for candidate, source in _iter_java_home_candidates(env):
        if not _is_java_home(candidate):
            continue
        runtime_home = _ensure_unix_java_home(candidate)
        major = _detect_java_major(_java_command_for_home(runtime_home))
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
        return runtime_home, source, rejected
    return None, None, rejected


def _resolve_java_command(env: dict[str, str]) -> str | None:
    return shutil.which("java", path=env.get("PATH") or env.get("Path"))


def _resolve_maven_command(
    env: dict[str, str], minimum_maven_version: tuple[int, int, int]
) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    rejected: list[dict[str, Any]] = []
    for candidate, source in _iter_maven_command_candidates(env):
        if not candidate.exists():
            continue
        version = _detect_maven_version(candidate, env.get("JAVA_HOME", ""), env.get("PATH") or env.get("Path", ""))
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

    java_on_path = shutil.which("java", path=env.get("PATH") or env.get("Path"))
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
        resolved = shutil.which(executable, path=env.get("PATH") or env.get("Path"))
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
                Path("/mnt/d/Java/JDK"),
                Path("/mnt/c/Program Files/Java"),
                Path("/mnt/c/Program Files/Eclipse Adoptium"),
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
        Path("/mnt/d/Java/Maven"),
        Path("/mnt/e/Dev/Maven"),
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
    return candidate.exists() and (
        (candidate / "bin" / "java").exists()
        or (candidate / "bin" / "java.exe").exists()
    )


def _java_command_for_home(candidate: Path) -> Path:
    java = candidate / "bin" / "java"
    return java if java.exists() else candidate / "bin" / "java.exe"


def _ensure_unix_java_home(candidate: Path) -> Path:
    if (candidate / "bin" / "java").exists():
        return candidate
    if not (candidate / "bin" / "java.exe").exists():
        return candidate

    wrapper_home = Path(tempfile.gettempdir()) / f"specforge-wsl-java-home-{candidate.name}"
    wrapper_bin = wrapper_home / "bin"
    wrapper_bin.mkdir(parents=True, exist_ok=True)
    for tool in ("java", "javac", "jar"):
        exe_path = candidate / "bin" / f"{tool}.exe"
        if not exe_path.exists():
            continue
        wrapper_path = wrapper_bin / tool
        wrapper_path.write_text(
            f"""#!/usr/bin/env bash
set -euo pipefail
convert_path() {{
  local value="$1"
  if [[ "$value" == *:* ]]; then
    local result=""
    local part
    IFS=':' read -ra parts <<< "$value"
    for part in "${{parts[@]}}"; do
      if [[ "$part" == /* ]]; then
        part="$(wslpath -w "$part")"
      fi
      if [[ -n "$result" ]]; then
        result="$result;$part"
      else
        result="$part"
      fi
    done
    printf '%s' "$result"
  elif [[ "$value" == /* ]]; then
    wslpath -w "$value"
  else
    printf '%s' "$value"
  fi
}}
args=()
convert_next=0
for arg in "$@"; do
  if [[ "$convert_next" == "1" ]]; then
    args+=("$(convert_path "$arg")")
    convert_next=0
    continue
  fi
  if [[ "$arg" == -D*=/* ]]; then
    key="${{arg%%=*}}"
    value="${{arg#*=}}"
    args+=("$key=$(convert_path "$value")")
    continue
  fi
  args+=("$arg")
  if [[ "$arg" == "-classpath" || "$arg" == "-cp" || "$arg" == "--class-path" || "$arg" == "-jar" ]]; then
    convert_next=1
  fi
done
exec '{exe_path}' "${{args[@]}}"
""",
            encoding="utf-8",
        )
        wrapper_path.chmod(0o755)
    return wrapper_home


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
def _detect_maven_version(maven_command: Path, java_home: str = "", path_value: str = "") -> tuple[int, int, int] | None:
    try:
        completed = subprocess.run(
            [str(maven_command), "-version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env={**os.environ, "JAVA_HOME": java_home, "PATH": path_value or os.environ.get("PATH", "")},
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
