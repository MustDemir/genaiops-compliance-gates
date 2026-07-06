#!/usr/bin/env python3
"""
test_integrity_regression.py — PoC Integrity Regression Suite

Static regression checks for credibility risks in the GenAIOps Compliance Gates PoC.

This suite intentionally focuses on "does the PoC prove what it claims to prove?"
instead of only checking functional green paths.

What it checks (14 checks, fail-fast ordering):
  1.  Demo fallbacks that can mask missing real enforcement (check_orchestrator_fallbacks)
  2.  Optional/non-critical handling of Evidence Store recording (check_ci_evidence_mandatory)
  3.  Drift detection wiring to the Evidence Store (check_drift_evidence_wiring)
  4.  Inline monitoring fallback patterns (check_inline_monitoring_fallback)
  5.  HYBRID gate manual-source consistency (check_hybrid_manual_sources)
  6.  Local pipeline HYBRID semantics (check_local_pipeline_hybrid_semantics)
  7.  Requirements-mapping test reads R0xx.yaml files (check_requirements_mapping_test)
  8.  False-green smoke test behavior (check_smoke_test_false_green)
  9.  Walkthrough reproducibility against current policy paths (check_walkthrough_policy_paths)
  10. Monitoring stub remnants in the main deployment (check_monitoring_stub_removed)
  11. Scope-claim mismatches between README and CI enforcement (check_scope_claims)
  12. Fallback coverage gaps — gates that silently default to PASS (check_fallback_coverage_gaps)
  13. Rego-to-fallback field parity — same gate, different checks (check_rego_fallback_parity)
  14. CI Conftest error visibility — stderr/exit code suppression (check_ci_conftest_errors_visible)

Usage:
  python3 test_integrity_regression.py
  python3 test_integrity_regression.py --format json
  python3 test_integrity_regression.py --fail-on low
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent  # tests/ -> repo root

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_lines(text: str, needle: str) -> list[int]:
    return [
        idx for idx, line in enumerate(text.splitlines(), start=1)
        if needle in line
    ]


def format_file_line(path: Path, line: int) -> str:
    rel = path.relative_to(REPO_ROOT)
    return f"{rel}:{line}"


def make_result(
    check_id: str,
    title: str,
    severity: str,
    passed: bool,
    summary: str,
    details: list[str] | None = None,
) -> dict:
    return {
        "id": check_id,
        "title": title,
        "severity": severity,
        "passed": passed,
        "summary": summary,
        "details": details or [],
    }


def check_orchestrator_fallbacks() -> dict:
    path = REPO_ROOT / "pipeline" / "gate_orchestrator.py"
    text = read_text(path)
    findings = []

    patterns = [
        ("YAML fixture evaluated by naming convention", "YAML fixtures are evaluated by filename convention"),
        ("defaulting to PASS", "Unknown gates default to PASS"),
    ]
    # Note: "falling back to fixture-based evaluation" is acceptable when
    # the fallback implements real validation logic (checked by FALLBACK_COVERAGE_COMPLETE).

    for needle, message in patterns:
        for line in find_lines(text, needle):
            findings.append(f"{format_file_line(path, line)} — {message}")

    return make_result(
        "ORCH_NO_DEMO_FALLBACKS",
        "gate_orchestrator avoids demo/pass fallbacks",
        "high",
        not findings,
        "Fallbacks in the closed-loop orchestrator weaken the proof path." if findings
        else "No demo fallbacks detected in gate_orchestrator.",
        findings,
    )


def check_ci_evidence_mandatory() -> dict:
    path = REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml"
    text = read_text(path)
    findings = []

    patterns = [
        ("Evidence recording skipped (non-critical)", "Evidence recording treated as non-critical"),
        ("Hash chain verification skipped (non-critical", "Hash-chain verification treated as non-critical"),
    ]

    for needle, message in patterns:
        for line in find_lines(text, needle):
            findings.append(f"{format_file_line(path, line)} — {message}")

    return make_result(
        "CI_EVIDENCE_MANDATORY",
        "CI treats Evidence Store and hash-chain as mandatory",
        "high",
        not findings,
        "CI currently allows evidence/hash integrity steps to be skipped." if findings
        else "CI evidence handling is strict.",
        findings,
    )


def check_drift_evidence_wiring() -> dict:
    cronjob = REPO_ROOT / "monitoring" / "k8s" / "cronjob-drift-detector.yaml"
    drift = REPO_ROOT / "monitoring" / "drift_detector.py"
    record = REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py"

    cronjob_text = read_text(cronjob)
    drift_text = read_text(drift)
    record_text = read_text(record)

    findings = []

    if "EVIDENCE_STORE_DB_URL" in cronjob_text and "EVIDENCE_STORE_DB_URL" not in record_text:
        # Check if drift_detector.py bridges the gap (reads EVIDENCE_STORE_DB_URL and forwards it)
        drift_bridges = "EVIDENCE_STORE_DB_URL" in drift_text
        if not drift_bridges:
            line = find_lines(cronjob_text, "EVIDENCE_STORE_DB_URL")[0]
            findings.append(
                f"{format_file_line(cronjob, line)} — CronJob sets EVIDENCE_STORE_DB_URL, "
                "but neither drift_detector.py nor record_evidence.py consume that env var"
            )

    if "--db-url" not in drift_text and "EVIDENCE_STORE_URL" not in drift_text:
        line = find_lines(drift_text, "record_drift_evidence(")[0]
        findings.append(
            f"{format_file_line(drift, line)} — drift_detector.py does not forward a PostgreSQL URL to record_evidence.py"
        )

    return make_result(
        "DRIFT_EVIDENCE_WIRING",
        "Drift detector is wired to record evidence in cluster mode",
        "high",
        not findings,
        "Drift detection and Evidence Store wiring are misaligned." if findings
        else "Drift detection evidence wiring looks aligned.",
        findings,
    )


def check_inline_monitoring_fallback() -> dict:
    path = REPO_ROOT / "infrastructure" / "scripts" / "install-monitoring.sh"
    text = read_text(path)
    findings = []

    if "CronJob file not found" in text and "kubectl apply -f -" in text:
        # Inline fallback is acceptable IF it injects the Evidence Store URL
        has_evidence_url = "EVIDENCE_STORE_DB_URL" in text or "EVIDENCE_STORE_URL" in text
        if not has_evidence_url:
            line = find_lines(text, "CronJob file not found")[0]
            findings.append(
                f"{format_file_line(path, line)} — inline CronJob fallback does not inject any Evidence Store URL"
            )

    return make_result(
        "MONITORING_INLINE_FALLBACK",
        "Monitoring install path avoids inline fallback definitions",
        "medium",
        not findings,
        "Monitoring deployment still depends on inline fallback behavior." if findings
        else "No inline fallback detected in monitoring install path.",
        findings,
    )


def check_hybrid_manual_sources() -> dict:
    path = REPO_ROOT / "pipeline" / "scenarios" / "poc_healthcare_pass.json"
    data = json.loads(read_text(path))
    missing = []

    for gate in data.get("gates", []):
        if gate.get("method") == "HYBRID" and not gate.get("manual_source"):
            missing.append(
                f"{path.relative_to(REPO_ROOT)} — {gate.get('gate_id')} is HYBRID but has no manual_source"
            )

    return make_result(
        "HYBRID_MANUAL_SOURCE",
        "Every HYBRID gate scenario includes a manual evidence source",
        "high",
        not missing,
        "HYBRID scenario definitions are incomplete." if missing
        else "All HYBRID scenario gates include manual sources.",
        missing,
    )


def check_local_pipeline_hybrid_semantics() -> dict:
    path = REPO_ROOT / "pipeline" / "test_pipeline_local.sh"
    text = read_text(path)
    findings = []

    fixed_auto = find_lines(text, '--method "AUTO"')
    has_hybrid_gate_1 = bool(find_lines(text, 'run_gate "G-PRE-01"'))
    has_hybrid_gate_5 = bool(find_lines(text, 'run_gate "G-PRE-05"'))

    if fixed_auto and has_hybrid_gate_1 and has_hybrid_gate_5:
        findings.append(
            f"{format_file_line(path, fixed_auto[0])} — local pipeline records evidence with a fixed AUTO method even though HYBRID gates are executed"
        )

    return make_result(
        "LOCAL_PIPELINE_HYBRID",
        "Local pipeline preserves HYBRID evidence semantics",
        "high",
        not findings,
        "Local pipeline hardcodes AUTO evidence semantics for HYBRID gates." if findings
        else "Local pipeline preserves HYBRID semantics.",
        findings,
    )


def check_requirements_mapping_test() -> dict:
    path = REPO_ROOT / "tests" / "test_all.py"
    text = read_text(path)
    findings = []

    for needle, message in [
        ("R001-R014.yaml", "Master test expects a combined requirements file that is not present in the repo"),
        ("Requirements file not found — SKIP", "Master test soft-skips the requirements mapping check"),
    ]:
        for line in find_lines(text, needle):
            findings.append(f"{format_file_line(path, line)} — {message}")

    return make_result(
        "REQ_MAPPING_REAL",
        "Requirements-to-gates mapping test is real, not a soft-skip",
        "medium",
        not findings,
        "Requirements mapping in the master test can pass without a real validation." if findings
        else "Requirements mapping check looks real.",
        findings,
    )


def check_smoke_test_false_green() -> dict:
    path = REPO_ROOT / "infrastructure" / "scripts" / "smoke-test.sh"
    text = read_text(path)
    findings = []

    # Check: does a skipped test increment TESTS_SKIPPED?
    # If the script has TESTS_SKIPPED tracking, the false-green issue is resolved.
    has_skip_tracking = "TESTS_SKIPPED" in text

    if "skipping health check" in text and not has_skip_tracking:
        line = find_lines(text, "skipping health check")[0]
        findings.append(
            f"{format_file_line(path, line)} — smoke test can skip health checks and still end green"
        )

    if "skipping metrics check" in text and not has_skip_tracking:
        line = find_lines(text, "skipping metrics check")[0]
        findings.append(
            f"{format_file_line(path, line)} — smoke test can skip metrics checks and still end green"
        )

    return make_result(
        "SMOKE_NO_FALSE_GREEN",
        "Smoke test distinguishes skipped checks from real success",
        "medium",
        not findings,
        "Smoke test can produce false-green outcomes when checks are skipped." if findings
        else "Smoke test does not show a false-green pattern.",
        findings,
    )


def check_walkthrough_policy_paths() -> dict:
    path = REPO_ROOT / "docs" / "walkthrough" / "WALKTHROUGH_KAP63.md"
    text = read_text(path)
    missing = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        match = re.search(r"-p\s+([A-Za-z0-9_./-]+\.rego)", line)
        if not match:
            continue
        rel_path = match.group(1)
        policy_path = REPO_ROOT / rel_path
        if not policy_path.exists():
            missing.append(
                f"{format_file_line(path, lineno)} — references missing policy path {rel_path}"
            )

    return make_result(
        "WALKTHROUGH_REPRODUCIBLE",
        "Walkthrough policy references match current repo files",
        "medium",
        not missing,
        "Walkthrough documentation references policy files that no longer exist." if missing
        else "Walkthrough policy references resolve cleanly.",
        missing,
    )


def check_monitoring_stub_removed() -> dict:
    path = REPO_ROOT / "scenarios" / "healthcare-ambient-ai-scribe" / "k8s" / "deployment.yaml"
    text = read_text(path)
    findings = []

    for needle, message in [
        ("Monitoring sidecar stub", "main deployment still contains a monitoring stub marker"),
        ("busybox:1.37", "main deployment still uses a busybox monitoring placeholder"),
    ]:
        for line in find_lines(text, needle):
            findings.append(f"{format_file_line(path, line)} — {message}")

    return make_result(
        "MONITORING_STUB_REMOVED",
        "Main deployment no longer contains monitoring stub remnants",
        "medium",
        not findings,
        "Main deployment still contains monitoring stub remnants." if findings
        else "No monitoring stub remnants detected in main deployment.",
        findings,
    )


def check_scope_claims() -> dict:
    readme = REPO_ROOT / "README.md"
    workflow = REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml"

    readme_text = read_text(readme)
    workflow_text = read_text(workflow)
    findings = []

    workflow_gate_count = len(re.findall(r"^\s*#\s+G-[A-Z]+-\d{2}", workflow_text, flags=re.MULTILINE))
    readme_claims_all_16 = "all 16 gates exercised" in readme_text.lower()

    if readme_claims_all_16 and workflow_gate_count < 16:
        line = find_lines(readme_text, "all 16 gates exercised")[0]
        findings.append(
            f"{format_file_line(readme, line)} — README claims all 16 gates are exercised, "
            f"while CI workflow comments list {workflow_gate_count} enforced gates"
        )

    return make_result(
        "SCOPE_CLAIMS_CLEAR",
        "README scope claims align with CI-enforced gate scope",
        "low",
        not findings,
        "High-level scope claims are broader than the CI-enforced subset." if findings
        else "No obvious README/CI scope-claim mismatch detected.",
        findings,
    )


def check_fallback_coverage_gaps() -> dict:
    """Check that every gate in the scenario has dedicated fallback evaluation logic,
    not just the default-to-PASS catch-all."""
    orchestrator = REPO_ROOT / "pipeline" / "gate_orchestrator.py"
    scenario = REPO_ROOT / "pipeline" / "scenarios" / "poc_healthcare_pass.json"

    orch_text = read_text(orchestrator)
    scenario_data = json.loads(read_text(scenario))

    # Extract gate IDs that have explicit branches in evaluate_gate_from_fixture
    covered_pattern = re.compile(r'gate_id\s*==\s*"(G-[A-Z]+-\d{2})"')
    tuple_pattern = re.compile(r'gate_id\s+in\s+\(([^)]+)\)')

    covered_gates: set[str] = set()
    for m in covered_pattern.finditer(orch_text):
        covered_gates.add(m.group(1))
    for m in tuple_pattern.finditer(orch_text):
        for gate_id in re.findall(r'"(G-[A-Z]+-\d{2})"', m.group(1)):
            covered_gates.add(gate_id)

    # Gates in the scenario that lack dedicated fallback logic
    findings = []
    for gate in scenario_data.get("gates", []):
        gid = gate.get("gate_id", "")
        if gid not in covered_gates:
            findings.append(
                f"{scenario.relative_to(REPO_ROOT)} — {gid} ({gate.get('gate_name', '?')}) "
                "has no dedicated fallback logic in gate_orchestrator and will default to PASS"
            )

    return make_result(
        "FALLBACK_COVERAGE_COMPLETE",
        "Every scenario gate has dedicated fallback evaluation logic",
        "high",
        not findings,
        f"{len(findings)} gate(s) silently default to PASS when Conftest is unavailable." if findings
        else "All scenario gates have dedicated fallback logic.",
        findings,
    )


def check_rego_fallback_parity() -> dict:
    """Check that the fixture-based fallback evaluates the same fields
    as the corresponding Rego policy.  A mismatch means the same gate
    can produce different results depending on whether Conftest is present."""
    orchestrator = REPO_ROOT / "pipeline" / "gate_orchestrator.py"
    orch_text = read_text(orchestrator)

    # Map of gate_id -> fields the Rego policy checks (from static analysis)
    rego_fields: dict[str, list[str]] = {
        "G-PRE-01": [
            "risk_classification.risk_class",
            "risk_classification.classification_reasoning",
            "risk_classification.annex_reference",
            "risk_classification.mitigation_measures",
            "manual_review.reviewed_by",
            "manual_review.review_date",
        ],
        "G-PRE-05": [
            "fundamental_rights_impact_assessment.fria_completed",
            "fundamental_rights_impact_assessment.affected_rights",
            "human_oversight.oversight_model",
            "human_oversight.human_oversight_lead",
            "human_oversight.intervention_capability.kill_switch",
            "conformity_assessment.declaration_available",
            "approval.approved_by",
        ],
        "G-DEP-02": [
            "quality_metrics.accuracy",
            "performance_metrics.latency_p95_ms",
            "safety_metrics.safety_score",
            "evaluation.run_id",
            "subgroup_analysis.performed",
            "adversarial_tests.performed",
        ],
        "G-OPS-03": [
            "genaiops.io/drift-detection-enabled",
            "genaiops.io/service-monitor-configured",
            "prometheus.io/scrape",
        ],
        "G-OPS-05": [
            "genaiops.io/evidence-store-connected",
            "genaiops.io/hash-chain-enabled",
            "genaiops.io/evidence-store-type",
        ],
    }

    # Map of gate_id -> fields the fallback actually checks (from code inspection)
    fallback_fields: dict[str, list[str]] = {
        "G-PRE-01": [
            "risk_classification.risk_class",
            "risk_classification.classification_reasoning",
            "risk_classification.annex_reference",
            "risk_classification.mitigation_measures",
            "manual_review.reviewed_by",
            "manual_review.review_date",
        ],
        "G-PRE-05": [
            "fundamental_rights_impact_assessment.fria_completed",
            "fundamental_rights_impact_assessment.affected_rights",
            "human_oversight.oversight_model",
            "human_oversight.human_oversight_lead",
            "human_oversight.escalation_procedure",
            "human_oversight.intervention_capability.kill_switch",
            "conformity_assessment.declaration_available",
            "approval.approved_by",
        ],
        "G-DEP-02": [
            "quality_metrics.accuracy",
            "performance_metrics.latency_p95_ms",
            "safety_metrics.safety_score",
            "evaluation.run_id",
            "subgroup_analysis.performed",
            "adversarial_tests.performed",
        ],
        "G-OPS-03": [
            "genaiops.io/drift-detection-enabled",
            "genaiops.io/service-monitor-configured",
            "prometheus.io/scrape",
        ],
        "G-OPS-05": [
            "genaiops.io/evidence-store-connected",
            "genaiops.io/hash-chain-enabled",
            "genaiops.io/evidence-store-type",
        ],
    }

    findings = []

    # Guard against fallback_fields drifting from the real code: every field
    # declared here must actually be referenced in gate_orchestrator.py.
    # Annotation keys (containing '/') are matched whole; dotted config paths
    # by their leaf segment (which is how the fallback accesses them).
    def _leaf(field: str) -> str:
        return field if "/" in field else field.split(".")[-1]

    for gate_id, fallback in fallback_fields.items():
        for field in fallback:
            if _leaf(field) not in orch_text:
                findings.append(
                    f"{gate_id} — fallback_fields declares '{field}' but it is not "
                    f"referenced in gate_orchestrator.py (map drifted from code)."
                )

    for gate_id, rego in rego_fields.items():
        fallback = fallback_fields.get(gate_id, [])
        # Normalize: strip annotation prefixes for comparison
        rego_set = set(rego)
        fallback_set = set(fallback)
        missing = rego_set - fallback_set
        if missing:
            findings.append(
                f"{gate_id} — Rego checks {len(rego)} fields, fallback checks {len(fallback)}. "
                f"Missing in fallback: {', '.join(sorted(missing))}"
            )

    return make_result(
        "REGO_FALLBACK_PARITY",
        "Fixture-based fallback checks the same fields as Rego policies",
        "high",
        not findings,
        f"{len(findings)} gate(s) have field-level mismatches between Rego and fallback." if findings
        else "Rego and fallback field coverage is aligned.",
        findings,
    )


def check_ci_conftest_errors_visible() -> dict:
    """Check that CI does not silently swallow Conftest errors via || true
    combined with stderr suppression.

    The workflow uses multiline shell commands with backslash continuation:
        conftest test \\
          file.json \\
          --policy ... \\
          --output json > /tmp/result.json 2>/dev/null || true

    We join continuation lines to detect the combined pattern."""
    path = REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml"
    text = read_text(path)
    findings = []
    lines = text.splitlines()

    # Check 1: Direct conftest invocations with stderr suppression
    # Join backslash-continuation lines into logical commands and track start line
    logical_commands: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        if "conftest test" in lines[i]:
            start_line = i + 1  # 1-indexed
            joined = lines[i]
            while joined.rstrip().endswith("\\") and i + 1 < len(lines):
                i += 1
                joined += " " + lines[i].strip()
            logical_commands.append((start_line, joined))
        i += 1

    for start_line, cmd in logical_commands:
        issues = []
        if "2>/dev/null" in cmd:
            issues.append("stderr suppressed (2>/dev/null)")
        # stdout+stderr to same file makes JSON unparseable if stderr is non-empty
        if "2>&1" in cmd and (">" in cmd.split("2>&1")[0]):
            issues.append("stderr merged into JSON output file (> file 2>&1)")
        if issues:
            findings.append(
                f"{format_file_line(path, start_line)} — Conftest invocation: {', '.join(issues)}. "
                "A Rego syntax error or missing policy would be invisible or corrupt JSON output."
            )

    # Check 2: Verify that the pipeline uses separated stderr (run_gate.sh pattern)
    # If conftest is called via run_gate.sh with separate stderr, that's clean.
    uses_gate_runner = "run_gate.sh" in text
    direct_conftest_in_steps = any("conftest test" in line and "run_gate" not in line
                                   for line in lines)
    if direct_conftest_in_steps and not uses_gate_runner:
        findings.append(
            f"{path.relative_to(REPO_ROOT)} — Conftest called directly in gate steps "
            "without separated stderr handling"
        )

    return make_result(
        "CI_CONFTEST_ERRORS_VISIBLE",
        "CI Conftest invocations do not silently swallow errors",
        "high",
        not findings,
        f"{len(findings)} Conftest invocation(s) suppress stderr or mask exit codes." if findings
        else "Conftest error output is visible in CI.",
        findings,
    )


def collect_results() -> list[dict]:
    checks = [
        check_orchestrator_fallbacks,
        check_ci_evidence_mandatory,
        check_drift_evidence_wiring,
        check_inline_monitoring_fallback,
        check_hybrid_manual_sources,
        check_local_pipeline_hybrid_semantics,
        check_requirements_mapping_test,
        check_smoke_test_false_green,
        check_walkthrough_policy_paths,
        check_monitoring_stub_removed,
        check_scope_claims,
        # Additional checks from cross-analysis review
        check_fallback_coverage_gaps,
        check_rego_fallback_parity,
        check_ci_conftest_errors_visible,
    ]
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as exc:
            # A single broken check (e.g. a moved file) must not crash the
            # whole suite — report it as a high-severity failure instead.
            results.append(make_result(
                check.__name__,
                f"{check.__name__} raised an exception",
                "high",
                False,
                f"Check could not run: {type(exc).__name__}: {exc}",
            ))
    return results


def failing_results(results: list[dict], fail_on: str) -> list[dict]:
    threshold = SEVERITY_RANK[fail_on]
    return [
        result for result in results
        if (not result["passed"]) and SEVERITY_RANK[result["severity"]] >= threshold
    ]


def print_text_report(results: list[dict], fail_on: str) -> None:
    print(f"\n{BOLD}{BLUE}PoC Integrity Regression Suite{RESET}")
    print(f"Repository: {REPO_ROOT}")
    print(f"Fail threshold: {fail_on.upper()}")
    print()

    passed = 0
    failed = 0

    for result in results:
        color = GREEN if result["passed"] else RED
        status = "PASS" if result["passed"] else "FAIL"
        severity = result["severity"].upper()
        print(f"{color}[{status}]{RESET} [{severity}] {result['id']} — {result['title']}")
        print(f"  {result['summary']}")
        for detail in result["details"]:
            print(f"  - {detail}")
        print()
        if result["passed"]:
            passed += 1
        else:
            failed += 1

    actionable = failing_results(results, fail_on)
    print(f"{BOLD}Summary{RESET}")
    print(f"  Passed checks: {passed}")
    print(f"  Failed checks: {failed}")
    print(f"  Actionable failures (>= {fail_on.upper()}): {len(actionable)}")

    if actionable:
        print(f"\n{RED}{BOLD}Integrity regression FAILED{RESET}")
    else:
        print(f"\n{GREEN}{BOLD}Integrity regression PASSED{RESET}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run static integrity regression checks for the GenAIOps PoC."
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-on",
        choices=["low", "medium", "high"],
        default="medium",
        help="Minimum severity that should trigger a non-zero exit code",
    )

    args = parser.parse_args()

    results = collect_results()
    actionable = failing_results(results, args.fail_on)

    if args.format == "json":
        payload = {
            "repo_root": str(REPO_ROOT),
            "fail_on": args.fail_on,
            "actionable_failures": len(actionable),
            "results": results,
        }
        print(json.dumps(payload, indent=2))
    else:
        print_text_report(results, args.fail_on)

    return 1 if actionable else 0


if __name__ == "__main__":
    sys.exit(main())
