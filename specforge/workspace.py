import hashlib, json, os, subprocess, uuid, tempfile
import re
from pathlib import Path
from datetime import datetime, timezone

EXCLUDED = {
    "node_modules",
    "target",
    "dist",
    ".git",
    ".jwk",
    "__pycache__",
    ".venv",
    ".idea",
    ".vscode",
    "files",
    "logs",
    "runs",
    "outputs",
    ".agents",
    ".codex",
    ".ssh",
    ".aws",
    "secrets",
    "credentials",
}


def _source_checkout(path):
    """Identify our source tree, not an arbitrary virtualenv or site-packages parent."""
    if not (path / "specforge/workspace.py").is_file():
        return False
    metadata = path / "pyproject.toml"
    if not metadata.is_file():
        return False
    section = re.search(
        r"(?ms)^\[project\][ \t]*(?:#[^\n]*)?\n(.*?)(?=^\[|\Z)",
        metadata.read_text(encoding="utf-8-sig"),
    )
    return bool(
        section and re.search(
            r"(?m)^[ \t]*name[ \t]*=[ \t]*(['\"])specforge-core\1[ \t]*(?:#[^\n]*)?$",
            section[1],
        )
    )


def _checkout_ancestor(path):
    return next((p for p in (path, *path.parents) if _source_checkout(p)), None)


def _overlap(left, right):
    return left == right or left in right.parents or right in left.parents


def validate_workspace(workspace, template=None):
    """Resolve and reject code/template overlap before any workspace writes."""
    root = Path(workspace).expanduser().resolve()
    package = Path(__file__).resolve().parent
    protected = {_checkout_ancestor(package) or package}
    # Also recognize a source checkout when invoking an installed wheel from it,
    # or when the requested workspace points into another checkout.
    for location in (Path.cwd().resolve(), root):
        checkout = _checkout_ancestor(location)
        if checkout is not None:
            protected.add(checkout)
    for code in sorted(protected):
        if _overlap(root, code):
            raise ValueError(
                "workspace must be outside SpecForge code and must not contain it: "
                f"{root} (protected: {code})"
            )
    if template is not None and _overlap(root, Path(template).expanduser().resolve()):
        raise ValueError("workspace and template must not contain one another")
    if root.exists() and not root.is_dir():
        raise ValueError("workspace must be a directory: " + str(root))
    for name in ("runs", "releases"):
        managed = root / name
        if managed.resolve() != managed:
            raise ValueError(
                "workspace managed directory must not be a symlink or junction: " + str(managed)
            )
    return root


def allowed(p):
    return (
        not any(x in EXCLUDED for x in p.parts)
        and not any(x.startswith(".env") and x != ".env.example" for x in p.parts)
        and p.name.lower() not in {"credentials.json", "secrets.json"}
        and p.suffix.lower()
        not in {
            ".log",
            ".eml",
            ".pem",
            ".key",
            ".pyc",
            ".p12",
            ".pfx",
            ".sqlite",
            ".db",
            ".p8",
            ".keystore",
        }
    )


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def inventory(root):
    """Prune caches before descent; never silently accept an externally linked source file."""
    root = Path(root)
    if root.is_symlink():
        raise ValueError("Source root must not be a symlink")
    result = {}

    def fail(error):
        raise error

    for directory, dirs, files in os.walk(
        root, topdown=True, followlinks=False, onerror=fail
    ):
        parent = Path(directory)
        dirs[:] = sorted(
            name for name in dirs if allowed((parent / name).relative_to(root))
        )
        for name in dirs:
            if (parent / name).is_symlink():
                raise ValueError("Source symlink rejected: " + str(parent / name))
        for name in sorted(files):
            p = parent / name
            relative = p.relative_to(root)
            if not allowed(relative):
                continue
            if p.is_symlink():
                raise ValueError("Source symlink rejected: " + str(p))
            if p.is_file():
                result[relative.as_posix()] = digest(p)
    return dict(sorted(result.items()))


def write_json(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=p.parent,
            prefix=p.name + ".",
            suffix=".tmp",
            delete=False,
        ) as file:
            temp = Path(file.name)
            json.dump(value, file, ensure_ascii=False, indent=2, sort_keys=True)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp, p)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def git_revision(root):
    p = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True
    )
    return p.stdout.strip() if p.returncode == 0 else None


def new_run(workspace):
    workspace = validate_workspace(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    run = (
        workspace
        / "runs"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            + "-"
            + uuid.uuid4().hex[:10]
        )
    )
    run.mkdir(parents=True)
    for name in ("input", "reports"):
        (run / name).mkdir()
    return run


def resolve_run(workspace, run_id=None):
    root = validate_workspace(workspace)
    run_id = run_id or read_json(root / "latest.json")["run_id"]
    if (
        not isinstance(run_id, str)
        or Path(run_id).name != run_id
        or run_id in (".", "..")
    ):
        raise ValueError("run-id must be a directory name")
    run = root / "runs" / run_id
    if not run.is_dir() or run.resolve().parent != root / "runs":
        raise ValueError("invalid run directory")
    return run
