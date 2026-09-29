#!/usr/bin/env python3
"""Prerequisites and explicit Conftest fixture contracts for local verification."""

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = "scenarios/healthcare-ambient-ai-scribe/fixtures"
CASES = {
    "pre-deployment": (
        "policies/pre-deployment/policy_security_baseline.rego",
        "genaiops.pre_deployment.security_baseline",
        "deployment_compliant.yaml", "deployment_noncompliant.yaml",
        "G-PRE-04/P1 (R003):", "runAsNonRoot",
    ),
    "deployment": (
        "policies/deployment/policy_safety_metrics.rego",
        "genaiops.deployment.safety_metrics",
        "eval_results.json", "eval_results_fail.json",
        "G-DEP-02 (R003): accuracy", "below threshold",
    ),
    "operations": (
        "policies/operations/policy_evidence_completeness.rego",
        "genaiops.operations.evidence_completeness",
        "deployment_compliant.yaml", "deployment_noncompliant.yaml",
        "G-OPS-05 (R005): annotation genaiops.io/evidence-store-connected", "is missing",
    ),
}
REQUIRED = (
    "tests/test_all.py", "tests/run_all_rego_tests.sh",
    "tests/test_verify_contract.py", "tests/run_isolated_evidence_test.py",
    "tests/test_integrity_regression.py", "tests/test_hash_parity.py",
    "tests/test_hash_chain_migration.py", "tests/test_evidence_manifest.py",
    "tests/fixtures/healthcare_scenarios.rego",
    "evidence-store/scripts/record_evidence.py",
    "evidence-store/scripts/tests/test_hybrid_gate_integration.py",
    "pipeline/gate_orchestrator.py", "pipeline/prepare_inputs.py",
    "pipeline/test_evidence_fail_closed.py", "pipeline/test_tamper_detection.py",
    "pipeline/scenarios/poc_healthcare_pass.json",
    "pipeline/scenarios/poc_healthcare_fail.json",
    "pipeline/scenarios/poc_gatekeeper_admission.json",
    "monitoring/test_drift_detector.py", "monitoring/test_drift_e2e.py",
    "scenarios/healthcare-ambient-ai-scribe/eval/test_eval_runner.py",
    "scenarios/healthcare-ambient-ai-scribe/eval/eval_runner.py",
)


def preflight(root=ROOT, which=shutil.which, find_spec=importlib.util.find_spec):
    """Fail before running tests if a mandatory dependency or suite is absent."""
    errors = []
    if find_spec("yaml") is None:
        errors.append(f"{sys.executable} needs PyYAML; install requirements.txt")
    for tool in ("bash", "opa", "conftest"):
        if which(tool) is None:
            errors.append(f"required tool is missing from PATH: {tool}")
    required = set(REQUIRED)
    for policy, _, positive, negative, *_ in CASES.values():
        required.update((policy, f"{FIXTURES}/{positive}", f"{FIXTURES}/{negative}"))
    for path in sorted(required):
        if not (root / path).is_file():
            errors.append(f"required verification file is missing: {path}")
    for phase in CASES:
        if not list((root / "gate-definitions" / phase).glob("G-*.yaml")):
            errors.append(f"no gate definitions found for {phase}")
        policies = list((root / "policies" / phase).glob("*.rego"))
        if not policies:
            errors.append(f"no policies found for {phase}")
        for policy in policies:
            if not policy.name.endswith("_test.rego"):
                test = policy.with_name(f"{policy.stem}_test.rego")
                if not test.is_file():
                    errors.append(f"policy test file is missing: {test.relative_to(root)}")
    if errors:
        raise ValueError("Verification preflight failed:\n  " + "\n  ".join(errors))


def validate_result(result, namespace, negative, expected):
    """A zero exit alone is not evidence that a namespace evaluated any rules."""
    rows = json.loads(result.stdout)
    if not isinstance(rows, list) or not rows:
        raise ValueError("Conftest returned no file results")
    failures, evaluated = [], 0
    for row in rows:
        if not isinstance(row, dict) or row.get("namespace") != namespace:
            raise ValueError("Conftest returned an unexpected namespace")
        if row.get("exceptions") or row.get("errors"):
            raise ValueError("Conftest reported exceptions or errors")
        successes = row.get("successes", 0)
        if type(successes) is not int or successes < 0:
            raise ValueError("invalid Conftest success count")
        evaluated += successes
        for field in ("failures", "warnings"):
            messages = row.get(field) or []
            if not isinstance(messages, list) or any(
                not isinstance(m, dict) or not isinstance(m.get("msg"), str)
                for m in messages
            ):
                raise ValueError(f"invalid Conftest {field}")
            evaluated += len(messages)
            if field == "failures":
                failures.extend(m["msg"] for m in messages)
    if evaluated == 0:
        raise ValueError("Conftest evaluated zero rules")
    if negative:
        if result.returncode != 1 or not any(
            all(fragment in message for fragment in expected) for message in failures
        ):
            raise ValueError("negative fixture did not block for the expected reason")
    elif result.returncode != 0 or failures:
        raise ValueError("positive fixture did not pass")
    return evaluated, len(failures)


def run_case(phase, root=ROOT):
    policy, namespace, positive, negative, *expected = CASES[phase]
    for blocked, fixture in ((False, positive), (True, negative)):
        result = subprocess.run(
            ["conftest", "test", str(root / FIXTURES / fixture),
             "--policy", str(root / policy), "--namespace", namespace,
             "--output", "json", "--no-color"],
            capture_output=True, text=True, timeout=60, cwd=root,
        )
        evaluated, failures = validate_result(result, namespace, blocked, expected)
        print(f"PASS {phase}/{fixture}: exit={result.returncode}, "
              f"evaluated={evaluated}, failures={failures}, "
              f"expected={'block' if blocked else 'pass'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("preflight", *CASES))
    args = parser.parse_args()
    try:
        if args.phase == "preflight":
            preflight()
            print("PASS verification preflight: required tools, suites and fixtures present")
        else:
            run_case(args.phase)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
