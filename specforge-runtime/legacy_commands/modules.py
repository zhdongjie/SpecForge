"""Retained legacy module-generation commands, outside the auto-build path."""

from __future__ import annotations

import argparse
from pathlib import Path


def run_emit_code(args: argparse.Namespace, root: Path) -> None:
    from runtime.codegen import CodegenPipeline

    output_root = root / "runs" / args.run_id / "generated-module"
    specs_dir = root / "specs"
    backend_root = (root / args.backend_root).resolve()
    summary = CodegenPipeline(
        project_root=root.parent,
        backend_root=backend_root,
        output_root=output_root,
        specs_dir=specs_dir,
    ).run(verify_compile=args.verify_compile)
    if summary["status"] != "PASS":
        raise RuntimeError("Code generation failed verification")
    return


def run_mutate_module(args: argparse.Namespace, root: Path) -> None:
    from runtime.mutation import MutationEngine

    output_root = root / "runs" / args.run_id / "mutated-module"
    specs_dir = root / "specs"
    backend_root = (root / args.backend_root).resolve()
    mutation_spec_path = specs_dir / args.mutation_spec
    summary = MutationEngine(
        project_root=root.parent,
        backend_root=backend_root,
        output_root=output_root,
        specs_dir=specs_dir,
        mutation_spec_path=mutation_spec_path,
    ).run(verify_compile=args.verify_compile)
    if summary["status"] != "PASS":
        raise RuntimeError("Module mutation failed verification")
    return


def run_synthesize_module(args: argparse.Namespace, root: Path) -> None:
    from runtime.synthesis import SynthesisPipeline

    output_root = root / "runs" / args.run_id / "generated-module"
    specs_dir = root / "specs"
    backend_root = (root / args.backend_root).resolve()
    summary = SynthesisPipeline(
        project_root=root.parent,
        backend_root=backend_root,
        output_root=output_root,
        specs_dir=specs_dir,
    ).run(verify_compile=args.verify_compile, field_schema_name=args.field_schema)
    if summary["status"] != "PASS":
        raise RuntimeError("Field-level synthesis failed verification")
    return


def run_lower_ir(args: argparse.Namespace, root: Path) -> None:
    from runtime.ir_lowering import IRLoweringPipeline

    output_root = root / "runs" / args.run_id
    specs_dir = root / "specs"
    summary = IRLoweringPipeline(
        output_root=output_root,
        specs_dir=specs_dir,
    ).run(module_schema_name=args.module_schema)
    if summary["status"] != "PASS":
        raise RuntimeError("IR lowering failed verification")
    return


def run_compile_backend(args: argparse.Namespace, root: Path) -> None:
    from runtime.platform_compiler import ProjectCompiler

    output_root = root / "runs" / args.run_id
    specs_dir = root / "specs"
    backend_root = (root / args.backend_root).resolve()
    summary = ProjectCompiler(
        project_root=root.parent,
        backend_root=backend_root,
        run_root=output_root,
        specs_dir=specs_dir,
    ).run(
        module_schema_name=args.module_schema,
        module_spec_name="module-spec.yaml",
        project_assembly_plan_name=args.project_assembly_plan or None,
        run_compile=True,
        run_boot=not args.skip_boot_verify,
    )
    if summary["status"] == "FAIL":
        raise RuntimeError("Backend compilation failed verification")
    return


def run_harden_backend(args: argparse.Namespace, root: Path) -> None:
    from runtime.hardening import HardeningPipeline

    output_root = root / "runs" / args.run_id
    specs_dir = root / "specs"
    backend_root = (root / args.backend_root).resolve()
    summary = HardeningPipeline(
        project_root=root.parent,
        backend_root=backend_root,
        run_root=output_root,
        specs_dir=specs_dir,
    ).run(
        module_schema_name=args.module_schema,
        module_spec_name="module-spec.yaml",
        project_assembly_plan_name=args.project_assembly_plan or None,
        auto_repair=args.auto_repair,
        verify_boot=args.verify_boot,
        repair_max_passes=max(1, args.repair_max_passes),
    )
    if summary["status"] == "FAIL":
        raise RuntimeError("Backend hardening failed verification")
    return
