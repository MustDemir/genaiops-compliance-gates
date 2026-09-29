#!/usr/bin/env python3
"""Regression tests for verification's dependency and verdict boundaries."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import verify_contract as contract
import run_isolated_evidence_test as isolation


class PreflightTests(unittest.TestCase):
    def test_checkout_has_all_required_files(self):
        contract.preflight(which=lambda _: "/tool", find_spec=lambda _: object())

    def test_every_required_tool_is_mandatory(self):
        for missing in ("bash", "opa", "conftest"):
            with self.subTest(tool=missing), self.assertRaisesRegex(ValueError, missing):
                contract.preflight(which=lambda tool: None if tool == missing else "/tool",
                                   find_spec=lambda _: object())

    def test_yaml_is_mandatory(self):
        with self.assertRaisesRegex(ValueError, "PyYAML"):
            contract.preflight(which=lambda _: "/tool", find_spec=lambda _: None)

    def test_each_required_file_is_mandatory(self):
        required = set(contract.REQUIRED)
        for policy, _, positive, negative, *_ in contract.CASES.values():
            required.update((policy, f"{contract.FIXTURES}/{positive}",
                             f"{contract.FIXTURES}/{negative}"))
        original = Path.is_file
        for missing in required:
            with self.subTest(path=missing):
                def exists(path):
                    return path != contract.ROOT / missing and original(path)
                with patch.object(Path, "is_file", exists), self.assertRaises(ValueError):
                    contract.preflight(which=lambda _: "/tool", find_spec=lambda _: object())

    def test_empty_repository_is_not_verified(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            contract.preflight(Path(directory), which=lambda _: "/tool",
                               find_spec=lambda _: object())


class WiringTests(unittest.TestCase):
    def test_verify_schedules_eval_and_contract_suites(self):
        result = subprocess.run(
            ["make", "--dry-run", "verify"], cwd=contract.ROOT,
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for suite in ("tests/test_verify_contract.py", "tests/test_all.py",
                      "scenarios/healthcare-ambient-ai-scribe/eval/test_eval_runner.py",
                      "tests/test_integrity_regression.py --fail-on low"):
            self.assertIn(suite, result.stdout)

    def test_runner_does_not_claim_full_readiness(self):
        text = (contract.ROOT / "tests/test_all.py").read_text()
        for obsolete in ("PoC is consistent and complete", "10 policies, 103 tests",
                         "(16 Gates)", "all 16 gates", '"--no-fail"', "[SKIP]"):
            self.assertNotIn(obsolete, text)
        self.assertIn("Not proved: live admission, production readiness or legal completeness.", text)

    def test_fault_injection_only_touches_a_disposable_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            recorder = root / "evidence-store/scripts/record_evidence.py"
            recorder.parent.mkdir(parents=True)
            recorder.write_text("original recorder")

            def interrupt(_args, *, cwd, timeout):
                self.assertNotEqual(cwd, root)
                (cwd / recorder.relative_to(root)).write_text("injected fault")
                raise subprocess.TimeoutExpired(_args, timeout)

            with patch.object(isolation, "ROOT", root), patch.object(
                isolation.subprocess, "run", side_effect=interrupt
            ), self.assertRaises(subprocess.TimeoutExpired):
                isolation.run()
            self.assertEqual(recorder.read_text(), "original recorder")


class VerdictTests(unittest.TestCase):
    namespace = "example.policy"
    expected = ("G-EXAMPLE", "missing")

    def result(self, code=0, **fields):
        return subprocess.CompletedProcess([], code, json.dumps([
            {"namespace": self.namespace, "successes": 1, **fields}
        ]), "")

    def validate(self, result, negative=False):
        return contract.validate_result(result, self.namespace, negative, self.expected)

    def test_positive(self):
        self.assertEqual(self.validate(self.result()), (1, 0))

    def test_negative_requires_its_specific_reason(self):
        result = self.result(1, failures=[{"msg": "G-EXAMPLE: field missing"}])
        self.assertEqual(self.validate(result, True), (2, 1))

    def test_wrong_reason_fails(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(1, failures=[{"msg": "unrelated failure"}]), True)

    def test_wrong_namespace_fails(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(namespace="main"))

    def test_empty_results_fail(self):
        for payload in ("[]", "null", "{}", "not JSON"):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.validate(subprocess.CompletedProcess([], 0, payload, ""))

    def test_zero_evaluations_fail(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(successes=0))

    def test_bad_counts_fail(self):
        for value in (-1, True, "1"):
            with self.subTest(count=value), self.assertRaises(ValueError):
                self.validate(self.result(successes=value))

    def test_exceptions_fail(self):
        for field in ("errors", "exceptions"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(self.result(**{field: [{"msg": "error"}]}))

    def test_positive_cannot_hide_failure_with_zero_exit(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(failures=[{"msg": "G-EXAMPLE: field missing"}]))

    def test_negative_cannot_use_no_fail(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(failures=[{"msg": "G-EXAMPLE: field missing"}]), True)

    def test_tool_error_is_not_policy_block(self):
        for code in (2, 127):
            with self.subTest(code=code), self.assertRaises(ValueError):
                self.validate(self.result(code, failures=[{"msg": "G-EXAMPLE: field missing"}]), True)

    def test_warnings_are_not_a_block(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(1, warnings=[{"msg": "G-EXAMPLE: field missing"}]), True)

    def test_malformed_messages_fail(self):
        with self.assertRaises(ValueError):
            self.validate(self.result(failures=[{}]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
