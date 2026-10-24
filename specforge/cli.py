"""Small CLI dispatcher. Generation, verification and repair have separate contracts."""

import argparse
import json
import sys
from pathlib import Path
from .acceptance_packs import get_pack
from .errors import VerificationError, RepairNotApplicable
from .spec import load
from .generate import generate
from .workspace import resolve_run
from .verification import verify
from .release import package, repair


def verify_with_repair(run, acceptance_pack):
    try:
        return verify(run, acceptance_pack=acceptance_pack)
    except VerificationError as original:
        if original.stage != "backend":
            raise
        try:
            return repair(run)
        except RepairNotApplicable:
            # Keep the actual compiler error rather than replace it with an unhelpful repair error.
            raise original


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="SpecForge independent v1 business compiler"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "generate", "verify", "repair", "package", "run"):
        q = commands.add_parser(name)
        q.add_argument("--workspace", required=True)
        if name in ("validate", "generate", "run"):
            q.add_argument("--spec", required=True)
        if name in ("generate", "run"):
            q.add_argument("--template", required=True)
        if name in ("verify", "repair", "package"):
            q.add_argument("--run-id")
        if name in ("verify", "run"):
            q.add_argument(
                "--acceptance-pack",
                help="explicit business acceptance pack, e.g. device-borrow",
            )
        if name == "verify":
            q.add_argument("--build-only", action="store_true")
            q.add_argument("--reuse-build", action="store_true")
    a = parser.parse_args(argv)
    try:
        if a.command == "validate":
            load(a.spec)
            out = {"status": "PASS"}
        elif a.command in ("generate", "run"):
            if a.command == "run":
                get_pack(a.acceptance_pack).validate(load(a.spec))
            run = generate(a.spec, a.template, a.workspace)
            out = {"run_id": run.name, "source": str(run / "source")}
            if a.command == "run":
                print(json.dumps(out), flush=True)
                verify_with_repair(run, a.acceptance_pack)
                out = package(run, Path(a.workspace))
        else:
            run = resolve_run(a.workspace, a.run_id)
            if a.command == "verify":
                out = verify(run, a.build_only, a.reuse_build, a.acceptance_pack)
            elif a.command == "repair":
                out = repair(run)
            else:
                out = package(run, Path(a.workspace))
        print(
            json.dumps(
                {
                    k: v
                    for k, v in out.items()
                    if k not in ("source_sha256", "artifacts_sha256")
                },
                ensure_ascii=False,
            )
        )
        return 0
    except Exception as exc:
        error = {"status": "FAIL", "error": str(exc)}
        if isinstance(exc, VerificationError):
            error["failed_stage"] = exc.stage
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 1
