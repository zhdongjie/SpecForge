"""Compatibility checks for the retained legacy command; no Maven or services."""

from pathlib import Path
import subprocess
import sys
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "specforge-runtime"


class LegacyEntrypointTests(unittest.TestCase):
    def probe(self, source):
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(source)],
            cwd=RUNTIME,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_help_and_import_need_no_runtime_modules(self):
        self.probe("""
            import importlib.abc, sys
            class Block(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if fullname == 'runtime' or fullname.startswith('runtime.'):
                        raise AssertionError('unexpected import: ' + fullname)
            sys.meta_path.insert(0, Block())
            import main
            sys.argv = ['main.py', '--help']
            try:
                main.main()
            except SystemExit as exc:
                assert exc.code == 0
            else:
                raise AssertionError('help must exit')
        """)

    def test_real_autobuild_dependencies_exclude_simulation_and_mutation(self):
        self.probe("""
            import importlib.abc, sys
            blocked = ('runtime.dag_engine', 'runtime.executor', 'runtime.verifier',
                       'runtime.golden_validator', 'runtime.mutation', 'runtime.replay',
                       'runtime.parallel_scheduler', 'runtime.logical_clock')
            class Block(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if any(fullname == p or fullname.startswith(p + '.') for p in blocked):
                        raise AssertionError('unexpected import: ' + fullname)
            sys.meta_path.insert(0, Block())
            from runtime.hardening import HardeningPipeline
            assert HardeningPipeline
            import main
        """)

    def test_all_explicit_branches_keep_dispatch_and_arguments(self):
        branches = {
            "emit-code": ("codegen", "CodegenPipeline"),
            "mutate-module": ("mutation", "MutationEngine"),
            "synthesize-module": ("synthesis", "SynthesisPipeline"),
            "lower-ir": ("ir_lowering", "IRLoweringPipeline"),
            "compile-backend": ("platform_compiler", "ProjectCompiler"),
            "harden-backend": ("hardening", "HardeningPipeline"),
            "run-regression-suite": ("golden_validator", "GoldenValidator"),
        }
        for flag, (module, name) in branches.items():
            with self.subTest(flag=flag):
                self.probe(f"""
                    import sys, types
                    import main
                    calls = []
                    class Pipeline:
                        def __init__(self, *args, **kwargs): calls.append((args, kwargs))
                        def run(self, **kwargs):
                            calls.append(kwargs)
                            return {{'status': 'PASS'}}
                        def run_regression_suite(self):
                            calls.append('regression')
                            return {{'failed_count': 0}}
                    module = types.ModuleType('runtime.{module}')
                    module.{name} = Pipeline
                    sys.modules['runtime.{module}'] = module
                    sys.argv = ['main.py', '--{flag}', '--run-id', 'compat-isolated']
                    main.main()
                    assert len(calls) == 2, calls
                    if '{flag}' != 'run-regression-suite':
                        assert 'compat-isolated' in str(calls[0]), calls
                """)

    def test_autobuild_keeps_priority_and_default_simulation_dispatch(self):
        self.probe("""
            import sys
            import main
            calls = []
            main.run_auto_build = lambda args, root: calls.append('auto')
            main.run_simulation = lambda args, root: calls.append('simulation')
            sys.argv = ['main.py', '--auto-build', '--mutate-module', '--emit-code']
            main.main()
            sys.argv = ['main.py']
            main.main()
            assert calls == ['auto', 'simulation'], calls
        """)

    def test_autobuild_preserves_reports_export_and_failure_signal(self):
        self.probe("""
            import sys, tempfile
            from pathlib import Path
            from unittest.mock import patch
            import main
            from runtime.hardening import HardeningPipeline
            from runtime.codegen.common import safe_load_yaml
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                (root / 'specs').mkdir()
                (root / 'specs/build-plan.yaml').write_text(
                    chr(10).join(['plan_id: compat', 'final_output_dir: outputs/compat', '']))
                generated = root / 'generated'
                generated.mkdir()
                (generated / 'marker.txt').write_text('generated')
                sys.argv = ['main.py', '--auto-build', '--run-id', 'compat-run']
                args = main.parse_args()
                for status in ['PASS', 'FAIL']:
                    summary = dict(status=status, generated_project_root=str(generated),
                                   compile_status=status, boot_status=status)
                    with patch.object(HardeningPipeline, 'run', return_value=summary) as call:
                        try:
                            main.run_auto_build(args, root)
                        except RuntimeError as exc:
                            assert status == 'FAIL' and 'failed verification' in str(exc)
                        else:
                            assert status == 'PASS'
                        assert call.call_args.kwargs['module_spec_name'] == 'module-spec.yaml'
                        assert call.call_args.kwargs['verify_boot'] is True
                    report = safe_load_yaml(root / 'runs/compat-run/logs/auto-build-report.yaml')
                    exported = safe_load_yaml(root / 'outputs/compat/logs/final-output-report.yaml')
                    assert report == exported and report['status'] == status
                    assert (root / 'outputs/compat/marker.txt').read_text() == 'generated'
        """)


if __name__ == "__main__":
    unittest.main()
