"""Behavioral boundaries for extracted historical commands."""

import unittest
import test_legacy_entrypoint as entrypoint


class LegacyCommandTests(unittest.TestCase):
    probe = entrypoint.LegacyEntrypointTests.probe

    def test_autobuild_does_not_import_legacy_commands(self):
        self.probe("""
            import importlib.abc, sys
            import main
            class Block(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if fullname == 'legacy_commands' or fullname.startswith('legacy_commands.'):
                        raise AssertionError('auto-build loaded legacy commands')
            sys.meta_path.insert(0, Block())
            calls = []
            main.run_auto_build = lambda args, root: calls.append(args.run_id)
            sys.argv = ['main.py', '--auto-build', '--run-id', 'isolated']
            main.main()
            assert calls == ['isolated']
        """)

    def test_forwarded_config_keeps_replay_failure_and_defaults(self):
        self.probe("""
            import sys
            import main
            from legacy_commands.simulation import build_run_config
            sys.argv = ['main.py', '--run-id', 'replay-test',
                '--replay-source-run', 'original', '--partial-replay', ' T1, ,T2 ',
                '--inject-failure', 'T1::2:message:detail', '--inject-failure', 'T2',
                '--max-workers', '0']
            args = main.parse_args()
            config = main.build_run_config(args)
            assert config == build_run_config(args)
            assert config.mode == 'partial-replay'
            assert config.partial_replay_tasks == ('T1', 'T2')
            assert config.max_workers == 1 and config.compare_trace
            first, second = config.failure_injections
            assert (first.task_id, first.failure_type, first.attempt, first.message) == (
                'T1', 'validation', 2, 'message:detail')
            assert second.message == 'Injected runtime failure' and second.attempt == 1
            args.no_compare_trace = True
            assert not main.build_run_config(args).compare_trace
        """)

    def test_extracted_branches_preserve_failure_signals_and_precedence(self):
        self.probe("""
            import sys, types
            import main
            branches = [
                ('emit-code', 'codegen', 'CodegenPipeline', 'Code generation'),
                ('mutate-module', 'mutation', 'MutationEngine', 'Module mutation'),
                ('synthesize-module', 'synthesis', 'SynthesisPipeline', 'Field-level synthesis'),
                ('lower-ir', 'ir_lowering', 'IRLoweringPipeline', 'IR lowering'),
                ('compile-backend', 'platform_compiler', 'ProjectCompiler', 'Backend compilation'),
                ('harden-backend', 'hardening', 'HardeningPipeline', 'Backend hardening'),
                ('run-regression-suite', 'golden_validator', 'GoldenValidator', 'Regression suite'),
            ]
            calls = []
            def pipeline(name):
                class Pipeline:
                    def __init__(self, *args, **kwargs): calls.append(name)
                    def run(self, **kwargs): return {'status': 'FAIL'}
                    def run_regression_suite(self): return {'failed_count': 1}
                return Pipeline
            for flag, module, name, message in branches:
                fake = types.ModuleType('runtime.' + module)
                setattr(fake, name, pipeline(flag))
                sys.modules['runtime.' + module] = fake
            for index, (flag, module, name, message) in enumerate(branches):
                # Multiple flags retain first-branch precedence, including failures.
                sys.argv = ['main.py'] + ['--' + b[0] for b in branches[index:]]
                try:
                    main.main()
                except RuntimeError as exc:
                    expected = 'Regression suite failed' if flag == 'run-regression-suite' else message + ' failed verification'
                    assert str(exc) == expected, str(exc)
                else:
                    raise AssertionError('failure swallowed: ' + flag)
                assert calls[-1] == flag, calls
            assert len(calls) == len(branches)
        """)

    def test_default_simulation_still_verifies_after_execution_error(self):
        self.probe("""
            import sys, types
            from pathlib import Path
            import main
            calls = []
            execution_error = ValueError('execution failed')
            class Loader:
                def __init__(self, *args): pass
                def load_all(self): return {'task_graph': {}, 'resolved_schema': {}}
            class Dag:
                def __init__(self, *args): pass
                def validate_acyclic(self): calls.append('acyclic')
                def validate_serial_order(self): calls.append('serial')
            class Executor:
                affected_tasks = ['T1']
                def __init__(self, **kwargs):
                    assert kwargs['run_dir'] == Path('/tmp/compat-only/runs/simulation')
                def execute(self):
                    calls.append('execute')
                    raise execution_error
            class Verifier:
                def __init__(self, **kwargs): pass
                def verify_static(self, loaded):
                    calls.append('static')
                    return {'passed': True}
                def verify_runtime(self, loaded, **kwargs):
                    calls.append('runtime')
                    assert kwargs == {'replay_source_run_id': 'source', 'affected_tasks': {'T1'}}
                    return {'passed': False}
            for module, name, cls in [
                ('loader', 'SpecLoader', Loader), ('dag_engine', 'DagEngine', Dag),
                ('executor', 'RuntimeExecutor', Executor), ('verifier', 'RuntimeVerifier', Verifier)]:
                fake = types.ModuleType('runtime.' + module)
                setattr(fake, name, cls)
                sys.modules['runtime.' + module] = fake
            sys.argv = ['main.py', '--run-id', 'simulation', '--partial-replay', 'T1',
                        '--replay-source-run', 'source']
            try:
                main.run_simulation(main.parse_args(), Path('/tmp/compat-only'))
            except ValueError as exc:
                assert exc is execution_error
            else:
                raise AssertionError('execution failure swallowed')
            assert calls == ['acyclic', 'serial', 'static', 'execute', 'runtime'], calls
        """)


if __name__ == "__main__":
    unittest.main()
