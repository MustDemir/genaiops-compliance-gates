#!/usr/bin/env python3
"""
test_integrity_regression.py — PoC Integrity Regression Suite

Static regression checks for credibility risks in the GenAIOps Compliance Gates PoC.

This suite intentionally focuses on "does the PoC prove what it claims to prove?"
instead of only checking functional green paths.

What it checks (the registry in collect_results() is the list; the count lives in the README):
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
  15. schema_version 2: policy_checks[].id is gate-locally unique (check_gate_check_ids_unique)
  16. Audit F-3: policy_checks[].implementation matches reality (check_gate_implementation_honest)
  17. schema_version 2: evidence_level.current/.target valid and non-regressing (check_gate_evidence_level_valid)
  18. SPEC-03: every gate carries a valid role_scope (check_gate_role_scope_valid)
  19. record_evidence INSERT arity: columns == placeholders == bound values (check_evidence_insert_arity)
  20. Audit F-2: no gate declares a waiver the system cannot grant (check_waiver_not_declarative)

Usage:
  python3 test_integrity_regression.py
  python3 test_integrity_regression.py --format json
  python3 test_integrity_regression.py --fail-on low
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent  # tests/ -> repo root

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

# "info" (T-14.4): a check that reports FAIL in the output but never fails the
# build at any --fail-on threshold. For a new control whose severity the PO
# rates only after seeing its first list (T-14 DoD 6) — visible from day one,
# binding once rated. Not a place to park a check that should block.
SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3}


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


# ── schema_version 2 / SPEC-01 checks ──────────────────────────────

GATE_DIRS = ["gate-definitions/pre-deployment", "gate-definitions/deployment", "gate-definitions/operations"]

GATE_DIR_TO_POLICY_DIR = {
    "gate-definitions/pre-deployment": "policies/pre-deployment",
    "gate-definitions/deployment": "policies/deployment",
    "gate-definitions/operations": "policies/operations",
}

VALID_EVIDENCE_LEVELS = ["E-0", "E-1", "E-2", "E-3"]


def _load_gate_files() -> list[tuple[Path, dict]]:
    """Load every gate-definitions/**/G-*.yaml as (path, parsed_dict)."""
    import yaml

    gates = []
    for d in GATE_DIRS:
        for f in sorted((REPO_ROOT / d).glob("G-*.yaml")):
            gates.append((f, yaml.safe_load(read_text(f)) or {}))
    return gates


def check_gate_check_ids_unique() -> dict:
    """SPEC-01 Abschnitt 4/9: policy_checks[].id must be unique within each gate."""
    findings = []
    for f, gate in _load_gate_files():
        checks = gate.get("policy_checks") or []
        if checks and not isinstance(checks[0], dict):
            findings.append(
                f"{f.relative_to(REPO_ROOT)}: policy_checks is still a string list "
                "(not migrated to schema_version 2 check objects)"
            )
            continue
        ids = [c.get("id") for c in checks if isinstance(c, dict)]
        dupes = sorted({i for i in ids if i and ids.count(i) > 1})
        if dupes:
            findings.append(f"{f.relative_to(REPO_ROOT)}: duplicate check id(s) {dupes}")
        missing = [i for i, c in enumerate(checks) if isinstance(c, dict) and not c.get("id")]
        if missing:
            findings.append(f"{f.relative_to(REPO_ROOT)}: policy_checks entr(y/ies) at index {missing} missing an 'id'")

    return make_result(
        "GATE_CHECK_ID_UNIQUE",
        "policy_checks[].id is gate-locally unique (schema_version 2)",
        "high",
        not findings,
        "Duplicate or missing check IDs break check-level traceability and the "
        "'<GATE-ID>/<CHECK-ID>' message convention (SPEC-01 Abschnitt 6)." if findings
        else "All policy_checks[].id values are present and unique within their gate.",
        findings,
    )


def check_gate_implementation_honest() -> dict:
    """Audit F-3: policy_checks[].implementation must match reality.

    Before the `implementation` field existed, this check could only report
    "a referenced Rego file is missing" and had to run at LOW severity,
    because seven checks are legitimately design-only. That made it
    permanently red and permanently ignored — it never blocked anything, and
    the gate definition itself still asserted an enforcement that does not
    happen while CI reported the gate as PASS.

    Now each check states its own claim, so this verifies the claim rather
    than the absence:

        implementation: implemented  -> the Rego file MUST exist
        implementation: design_only  -> the Rego file MUST NOT exist

    Both directions are genuine inconsistencies between what a gate
    definition asserts and what the repository contains — the second one
    catches a declaration that went stale after the policy was written.
    Hence HIGH: there is no longer an expected-failure case to tolerate.
    """
    # Policies are looked up across ALL policy directories, not just the one
    # matching the gate's own lifecycle phase: a handful of pre-existing
    # implementations (e.g. G-DEP-01, G-DEP-05) are filed under
    # policies/pre-deployment/ even though their gate is a deployment-phase
    # gate. That placement predates this SPEC and is out of scope to move.
    all_policy_dirs = [REPO_ROOT / d for d in GATE_DIR_TO_POLICY_DIR.values()]

    findings = []
    for f, gate in _load_gate_files():
        checks = gate.get("policy_checks") or []
        if not checks or not isinstance(checks[0], dict):
            continue
        for c in checks:
            policy_name = c.get("policy")
            if not policy_name:
                continue
            declared = (c.get("implementation") or "").strip()
            exists = any((pdir / f"{policy_name}.rego").exists() for pdir in all_policy_dirs)

            if declared not in ("implemented", "design_only"):
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: check {c.get('id')} has "
                    f"implementation='{declared or '<missing>'}' — must be "
                    f"'implemented' or 'design_only'"
                )
            elif declared == "implemented" and not exists:
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: check {c.get('id')} claims "
                    f"implementation='implemented' but '{policy_name}.rego' does not "
                    f"exist — the gate asserts an enforcement that cannot run"
                )
            elif declared == "design_only" and exists:
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: check {c.get('id')} is marked "
                    f"'design_only' but '{policy_name}.rego' exists — the declaration "
                    f"understates what is actually enforced"
                )

    return make_result(
        "GATE_IMPLEMENTATION_HONEST",
        "policy_checks[].implementation matches whether the Rego file exists",
        "high",
        not findings,
        "A gate definition claims an enforcement state that does not match the repository." if findings
        else "Every check's implementation claim matches reality.",
        findings,
    )


def check_gate_evidence_level_valid() -> dict:
    """SPEC-01 Abschnitt 4/9: evidence_level.current/.target must be valid
    E-0..E-3 values, and target must be >= current (never regress the goal
    below the already-achieved level)."""
    findings = []
    for f, gate in _load_gate_files():
        el = gate.get("evidence_level")
        if not isinstance(el, dict):
            findings.append(f"{f.relative_to(REPO_ROOT)}: evidence_level block missing (schema_version 2)")
            continue
        current = el.get("current")
        target = el.get("target")
        if current not in VALID_EVIDENCE_LEVELS:
            findings.append(f"{f.relative_to(REPO_ROOT)}: evidence_level.current '{current}' is not one of {VALID_EVIDENCE_LEVELS}")
            continue
        if target not in VALID_EVIDENCE_LEVELS:
            findings.append(f"{f.relative_to(REPO_ROOT)}: evidence_level.target '{target}' is not one of {VALID_EVIDENCE_LEVELS}")
            continue
        if VALID_EVIDENCE_LEVELS.index(target) < VALID_EVIDENCE_LEVELS.index(current):
            findings.append(f"{f.relative_to(REPO_ROOT)}: evidence_level.target '{target}' is below .current '{current}'")
        if not (el.get("rationale") or "").strip():
            findings.append(f"{f.relative_to(REPO_ROOT)}: evidence_level.rationale is empty")

    return make_result(
        "GATE_EVIDENCE_LEVEL_VALID",
        "evidence_level.current/.target are valid and target >= current",
        "medium",
        not findings,
        "Invalid or regressing evidence_level values undermine the E-0..E-3 evidentiary-strength axis (SPEC-01 Abschnitt 2)." if findings
        else "All gates carry a valid, non-regressing evidence_level.",
        findings,
    )


def check_evidence_insert_arity() -> dict:
    """Column count, placeholder count and bound-value count must agree in
    every INSERT of record_evidence.py.

    Motivated by a real defect: schema v04 added `ai_act_role` to the column
    list and the placeholder list of insert_pg(), but not to the value tuple —
    16 placeholders against 15 values. psycopg2 raises IndexError, so the
    PostgreSQL write path was dead while the SQLite path (used by CI and the
    tests) stayed green. A static arity check catches this class without
    needing a live database.
    """
    path = REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py"
    text = read_text(path)
    findings = []

    for label, marker in (
        ("insert_sqlite", "INSERT INTO quality_gate_results"),
        ("insert_pg", "INSERT INTO compliance.quality_gate_results"),
    ):
        idx = text.find(marker)
        if idx == -1:
            findings.append(f"{path.name}: could not locate the {label} statement")
            continue
        block = text[idx:idx + 2500]

        col_match = re.search(r"\(([^)]*?)\)\s*\n\s*VALUES", block, re.S)
        val_match = re.search(r"VALUES\s*\(([^)]*)\)", block)
        if not (col_match and val_match):
            findings.append(f"{path.name}: could not parse the {label} statement")
            continue

        n_cols = len([c for c in col_match.group(1).replace("\n", " ").split(",") if c.strip()])
        n_ph = val_match.group(1).count("%s") + val_match.group(1).count("?")

        # Count the bound values: every line in the argument tuple that starts
        # with `record[...]` or `record.get(...)`. Bounded by the end of the
        # statement so the next function is not counted in. Indentation differs
        # between the two call sites, so anchoring on it is not reliable.
        tail = block[val_match.end():]
        for stop in ("cur.fetchone()", "conn.commit()", "lastrowid"):
            pos = tail.find(stop)
            if pos != -1:
                tail = tail[:pos]
        n_vals = len([ln for ln in tail.splitlines()
                      if re.match(r"\s*record[\[.]", ln)])

        if not (n_cols == n_ph == n_vals):
            findings.append(
                f"{path.name}: {label} arity mismatch — "
                f"{n_cols} columns / {n_ph} placeholders / {n_vals} bound values"
            )

    return make_result(
        "EVIDENCE_INSERT_ARITY",
        "record_evidence INSERTs bind as many values as they declare columns",
        "high",
        not findings,
        "A column/placeholder/value mismatch breaks one write path while the other stays green." if findings
        else "SQLite and PostgreSQL INSERT statements are arity-consistent.",
        findings,
    )


def check_waiver_not_declarative() -> dict:
    """Audit F-2: a gate must not declare a waiver the system cannot grant.

    11 of 17 gates used to set waiver.allowed: true, each naming an approver
    and a time limit. Nothing enforced any of it: "waiver" appeared in no
    line of logic in pipeline/, evidence-store/, policies/ or .github/, and
    the evidence schema only knows decision IN ('PASS','FAIL') — so a waived
    gate was indistinguishable from a passed one. An exception path that
    leaves no trace devalues the completeness of the hash chain, which is the
    one property the whole artefact rests on.

    The decision was to abolish waivers rather than implement them. This
    check keeps that decision from eroding silently: allowed: true is only
    acceptable once a real control exists. It detects that control by
    looking for waiver handling in the recording path — if you implement
    waivers, record_evidence.py has to learn about them, and then this check
    stops objecting on its own.
    """
    record = read_text(REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py")
    mechanism_exists = "waiver" in record.lower()

    findings = []
    for f, gate in _load_gate_files():
        if (gate.get("waiver") or {}).get("allowed") and not mechanism_exists:
            findings.append(
                f"{f.relative_to(REPO_ROOT)}: waiver.allowed is true, but "
                f"record_evidence.py has no waiver handling — the gate declares an "
                f"exception the system cannot grant, record or expire"
            )

    return make_result(
        "WAIVER_NOT_DECLARATIVE",
        "no gate declares a waiver the system cannot actually grant",
        "high",
        not findings,
        "A declarative-only exception path makes a waived gate look like a passed one." if findings
        else ("No gate declares a waiver; the exception path was abolished rather than "
              "left unimplemented (audit F-2)." if not mechanism_exists
              else "Waiver handling exists in the recording path."),
        findings,
    )


def check_runtime_mode_visible() -> dict:
    """SPEC-04 Teil 1: runtime_mode must stay visible, not just stored.

    The accepted weakness of option C (runtime_mode as a hashed field rather
    than a third decision value): a consumer reading only `decision` sees an
    undifferentiated PASS. The field is sealed, but nothing forces anyone to
    look at it. Option B would have bought that visibility by brute force, at
    the cost of discarding whether the thresholds held at all.

    The compensation is that every place reporting a decision also reports the
    mode. That compensation is a convention, and conventions erode — someone
    tidies up a banner, someone trims a view. This check makes the erosion
    fail loudly instead of quietly turning a mock PASS back into an ordinary
    PASS.

    Three carriers are required:
      1. the orchestrator banner (what a human reads during a walkthrough)
      2. the pipeline report (what a machine reads afterwards)
      3. the auditor-facing SQL view, with runtime_mode beside decision
    """
    findings = []

    orchestrator = read_text(REPO_ROOT / "pipeline" / "gate_orchestrator.py")
    if "RUNTIME MODE:" not in orchestrator:
        findings.append(
            "pipeline/gate_orchestrator.py: no runtime-mode banner — a mock run "
            "would print like an ordinary run"
        )
    if '"runtime_mode": runtime_mode' not in orchestrator:
        findings.append(
            "pipeline/gate_orchestrator.py: the pipeline report does not carry "
            "runtime_mode at top level"
        )

    migration = read_text(
        REPO_ROOT / "evidence-store" / "migrations" / "v05_to_v06_add_runtime_mode.sql"
    )
    view_start = migration.find("CREATE OR REPLACE VIEW")
    view_text = migration[view_start:] if view_start != -1 else ""
    if "q.runtime_mode" not in view_text:
        findings.append(
            "v05_to_v06_add_runtime_mode.sql: the reporting view omits runtime_mode — "
            "an auditor reading the view sees decision without its mode"
        )
    else:
        # Order matters: the column has to sit beside decision, not be filed
        # away among the trailing metadata where nobody scanning for a verdict
        # would pass it.
        if view_text.find("q.runtime_mode") > view_text.find("q.gate_name"):
            findings.append(
                "v05_to_v06_add_runtime_mode.sql: runtime_mode appears after "
                "gate_name in the reporting view — it must sit next to decision, "
                "where a reader scanning for the verdict cannot miss it"
            )

    verifier = read_text(REPO_ROOT / "evidence-store" / "scripts" / "verify_hash_chain.py")
    if "_mode_marker" not in verifier:
        findings.append(
            "verify_hash_chain.py: verbose output does not mark non-live runs"
        )

    # B-21: visible is not the same as RECORDED. The CI measured the mode,
    # asserted it, and then built its evidence source document without it, so
    # every record fell back to "unknown" — correctly, because a silent "live"
    # is the one assumption this field exists to prevent. The gap was not a
    # missing mechanism but a missing hand-over, and it stayed invisible until
    # somebody opened a signed artefact and read it field by field.
    #
    # So: every place that writes an evidence record has to pass the mode on.
    wf = read_text(REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml")
    record_calls = wf.count("record_evidence.py")
    handovers = wf.count("--runtime-mode")
    if record_calls and handovers < record_calls:
        findings.append(
            f".github/workflows/gate-pipeline.yml: {record_calls} evidence writes, "
            f"{handovers} of them hand the measured runtime_mode on. A record that "
            f"says 'unknown' about a run whose mode was measured is weaker than what "
            f"the run knew (B-21)"
        )
    # Both halves, producer and consumer. A first version of this rule checked
    # only that something READS steps.measure.outputs.runtime_mode — and stayed
    # green when the line that WRITES the output was deleted, because the
    # readers were still there, referring to a value that no longer existed.
    # A check a counter-proof cannot break is not a check (B-16), and this one
    # took three counter-proofs before the third broke it.
    if 'runtime_mode=$MODE" >> "$GITHUB_OUTPUT' not in wf:
        findings.append(
            ".github/workflows/gate-pipeline.yml: the measurement step never writes "
            "the mode to its step output — everything downstream would read an "
            "empty value and the run would fail closed, but for the wrong reason"
        )
    if "steps.measure.outputs.runtime_mode" not in wf:
        findings.append(
            ".github/workflows/gate-pipeline.yml: nothing consumes the published "
            "mode, so it is measured, asserted and then dropped again (B-21)"
        )
    # The signing job records a gate and never sees the evaluation document.
    # It must RECEIVE the mode; deriving a second one would not measure it.
    if "needs.quality-gates.outputs.runtime_mode" not in wf:
        findings.append(
            ".github/workflows/gate-pipeline.yml: the signing job does not receive "
            "the measured runtime_mode, so the record it writes would claim less "
            "than the run established"
        )

    return make_result(
        "RUNTIME_MODE_VISIBLE",
        "runtime_mode is surfaced wherever a decision is reported (SPEC-04 Teil 1)",
        "medium",
        not findings,
        "A sealed-but-invisible runtime_mode lets a mock PASS read as a live PASS — "
        "the exact gap option C accepted and these carriers compensate." if findings
        else "Banner, pipeline report, reporting view and verifier all surface the mode.",
        findings,
    )


def _own_check_count() -> int:
    """How many checks this suite registers, read from the registry itself.

    Counting the entries in collect_results() rather than hard-coding a
    number is the same rule this suite applies to everyone else: a count
    written next to its subject, with nothing holding the two together,
    drifts (B-12).
    """
    src = read_text(Path(__file__).resolve())
    block = re.search(r"def collect_results\(\).*?checks = \[(.*?)\n    \]", src, re.S)
    return len(re.findall(r"^\s+check_\w+,", block.group(1), re.M)) if block else 0


def check_readme_counts_current() -> dict:
    """The README must not claim more, or less, than the repository holds.

    This repository is a control system that checks whether declarations
    match reality. Its own front page had drifted: it advertised 166 rules
    and 173 unit tests when there were 175 and 187, named three
    technologies that appear nowhere in the code, and stated the master
    integration test as 31/31 in one place and 22/22 in another while the
    actual figure was 32. A README that overstates fails the standard the
    artefact demands of everyone else — and it is the first thing a reader
    sees, so it is the first place credibility is lost.

    Keeping it right by diligence does not work; the drift above happened
    despite diligence. So the numbers are verified mechanically, and the
    build fails when they part ways.

    The check is deliberately narrow. It verifies COUNTS that can be
    derived from the repository, not prose. Claims that cannot be counted
    stay a matter of authorship.
    """
    import yaml

    readme = read_text(REPO_ROOT / "README.md")
    findings = []

    gates = [(f, g) for f, g in _load_gate_files()]
    checks = [c for _, g in gates for c in (g.get("policy_checks") or [])]

    rules = 0
    for f in (REPO_ROOT / "policies").glob("*/*.rego"):
        if f.name.endswith("_test.rego"):
            continue
        rules += len(re.findall(r"^(?:deny|warn|violation) contains", read_text(f), re.M))

    rego_tests = 0
    for f in (REPO_ROOT / "policies").glob("*/*_test.rego"):
        rego_tests += len(re.findall(r"^test_[a-z0-9_]+", read_text(f), re.M))

    policies = len([
        f for f in (REPO_ROOT / "policies").glob("*/*.rego")
        if not f.name.endswith("_test.rego")
    ])
    requirements = len(list((REPO_ROOT / "requirements").glob("R0*.yaml")))
    design_only = sum(1 for c in checks if c.get("implementation") == "design_only")
    implemented = sum(1 for c in checks if c.get("implementation") == "implemented")
    effects = [t for _, g in gates for t in (g.get("triggers") or [])]
    effects_total = len(effects)
    effects_declared_only = sum(1 for t in effects if t.get("implementation") == "declared_only")

    # (claimed-substring, computed value, what it is) — the substring must
    # appear verbatim, so a stale number cannot survive by sitting next to
    # a correct one elsewhere in the file.
    expectations = [
        (f"{len(gates)} gates", len(gates), "gate count"),
        (f"{len(checks)} checks", len(checks), "check count"),
        (f"{policies} Rego policies", policies, "policy count"),
        (f"{rules} deny/warn/violation rules", rules, "rule count"),
        (f"{rego_tests} Rego unit tests", rego_tests, "Rego unit-test count"),
        (f"{requirements} requirements", requirements, "requirement count"),
        (f"{implemented} enforced, {design_only} design-only", implemented, "check implementation split"),
        (f"{design_only} of {len(checks)} checks are design-only", design_only, "design-only statement"),
        # Declared gate effects (Frage 5). ES-F3 added seven triggers; the
        # README said "4 of 22" and nothing would have noticed it go stale.
        (f"{effects_declared_only} of {effects_total} declared gate effects are not built",
         effects_declared_only, "gate-effect split"),
        # This suite's own size. It grew 28 -> 29 while the README kept
        # saying 28 in two places, and nothing noticed — the front page
        # understating the controls is the same error class as overstating
        # them, just less flattering.
        (f"{_own_check_count()} integrity checks", _own_check_count(), "integrity-check count"),
    ]
    for claim, _value, label in expectations:
        if claim not in readme:
            findings.append(
                f"README.md: does not state '{claim}' — the {label} derived from "
                f"the repository is not what the README claims"
            )

    # Presence is not enough — the README must not CONTRADICT itself.
    #
    # The rule above is satisfied by one correct occurrence anywhere in the
    # file. That let "187 Rego unit tests" sit in the stats table while
    # "199 Rego unit tests" stood twelve screens further down, both green.
    # A reader stops at the first number; the check has to as well.
    #
    # Deliberately limited to two unambiguous phrases. "N gates" and
    # "N checks" legitimately appear with other numbers (five PRE gates,
    # three checks in a gate), and a rule that fires on those would be
    # switched off rather than fixed.
    for phrase, value in (("Rego unit tests", rego_tests),
                          ("integrity checks", _own_check_count())):
        wrong = {int(n) for n in re.findall(rf"(\d+) {re.escape(phrase)}", readme)} - {value}
        for n in sorted(wrong):
            findings.append(
                f"README.md: says '{n} {phrase}' as well as '{value} {phrase}' — "
                f"two numbers for one thing, and a reader stops at the first"
            )

    # The Definition-of-Done score. A README that states how many gates meet
    # the bar has made a claim like any other, and this one moves every time
    # a design_only check is implemented or an acceptance criterion traced.
    reqs = {}
    for rf in (REPO_ROOT / "requirements").glob("R0*.yaml"):
        try:
            r = yaml.safe_load(read_text(rf)) or {}
        except yaml.YAMLError:
            continue
        if r.get("id"):
            reqs[r["id"]] = r

    dod_full = 0
    for _gf, gate in gates:
        gchecks = gate.get("policy_checks") or []
        rids = (gate.get("links") or {}).get("requirements") or []
        crit = [e for rid in rids for e in (reqs.get(rid, {}).get("acceptance_criteria") or [])]
        inputs = gate.get("required_inputs") or []
        met = (
            bool(gate.get("triggers"))
            and all(c.get("implementation") == "implemented" for c in gchecks)
            and all(d.get("evaluated_by") for d in inputs)
            and bool(crit)
            and all(isinstance(e, dict) and e.get("status") != "unverified" for e in crit)
        )
        dod_full += 1 if met else 0

    dod_claim = f"{dod_full} of {len(gates)} gates meet all five machine-checked points"
    if dod_claim not in readme:
        findings.append(
            f"README.md: does not state '{dod_claim}' — the Definition-of-Done "
            f"score derived from the catalogue is not what the README claims"
        )

    # Latest evidence-schema version must be the one the README names.
    migrations = sorted((REPO_ROOT / "evidence-store" / "migrations").glob("v*_to_v*.sql"))
    if migrations:
        latest = re.search(r"_to_(v\d+)_", migrations[-1].name)
        if latest and f"Evidence schema | {latest.group(1)}" not in readme.replace("  ", " "):
            if latest.group(1) not in readme:
                findings.append(
                    f"README.md: latest evidence-store migration is {latest.group(1)}, "
                    f"which the README does not mention"
                )

    # Technologies must not be advertised unless they appear in the code.
    # LangChain, ArgoCD and OpenTelemetry were listed in the tech stack with
    # zero, five (comment-only) and one occurrence respectively.
    for tech in ("LangChain", "ArgoCD", "OpenTelemetry"):
        if tech.lower() not in readme.lower():
            continue
        hits = 0
        for f in REPO_ROOT.rglob("*"):
            if not f.is_file() or any(
                part in (".git", ".claude", "docs", "tmp") for part in f.parts
            ):
                continue
            if f.name in ("README.md", "CHANGELOG.md"):
                continue
            try:
                if tech.lower() in f.read_text(encoding="utf-8", errors="ignore").lower():
                    hits += 1
            except OSError:
                continue
        if hits == 0:
            findings.append(
                f"README.md: names '{tech}' but it appears in no source file — "
                f"a tech stack is a claim like any other"
            )

    return make_result(
        "README_COUNTS_CURRENT",
        "the README's counts and tech stack match the repository",
        "medium",
        not findings,
        "The front page overstates or understates what the repository holds — the "
        "first place a reader checks is the first place credibility is lost." if findings
        else f"README matches: {len(gates)} gates, {len(checks)} checks, {rules} rules, "
             f"{rego_tests} Rego tests, {requirements} requirements.",
        findings,
    )


def check_readme_evidence_claims_current() -> dict:
    """The README's statements ABOUT evidence levels must match the catalogue.

    README_COUNTS_CURRENT verifies numbers. It does not read sentences, and
    that gap has a name: correcting B-18 — a check classified E-1 that met
    nothing E-1 requires — the README gained the sentence "no check in the
    catalogue is above E-0". It was false when it was written. Three checks
    in G-OPS-03 carry E-3, and have since the drift measurement landed. The
    correction of a claim-without-a-counterpart was itself a claim without a
    counterpart, and the suite that exists to catch exactly that was looking
    at numbers one line above.

    Two mechanisms, because a prose claim needs both:

      1. ONE anchored sentence, derived from the gate files, must appear
         verbatim. The distribution of evidence_level over all checks is a
         fact of the catalogue; the README has to state the current one, and
         the moment a check moves to another level the derived sentence
         changes and the anchor is gone. Everything else in the README stays
         free prose — exactly one sentence is word-bound, and that is the
         price of having a claim that can be checked at all.

      2. A contradiction detector for the sentence shape that failed here:
         "no/none ... above E-0". It is the strongest and most flattering
         claim the axis allows, so it is the one worth guarding, and it must
         not stand anywhere in the README while a check sits above E-0.

    Deliberately NOT attempted: reading the prose semantically. A check whose
    verdict depends on interpretation is a check that gets argued with
    instead of fixed.
    """
    readme = read_text(REPO_ROOT / "README.md")
    findings = []

    checks = [c for _, g in _load_gate_files() for c in (g.get("policy_checks") or [])]
    levels = {}
    for c in checks:
        level = c.get("evidence_level") if isinstance(c, dict) else None
        levels[level] = levels.get(level, 0) + 1
    at_e1 = levels.get("E-1", 0)
    at_e3 = levels.get("E-3", 0)
    at_e0 = levels.get("E-0", 0)
    unset = levels.get(None, 0)

    # The anchored sentence. Written the way the README says it, so the
    # expected string IS the claim rather than a paraphrase of it.
    claim = (f"{at_e1 if at_e1 else 'no'} check{'' if at_e1 == 1 else 's'} at E-1, "
             f"{at_e3} at E-3, {at_e0} at E-0, and {unset} without a level")
    if claim not in readme:
        findings.append(
            f"README.md: does not state '{claim}' — the evidence-level "
            f"distribution derived from the gate catalogue is not what the "
            f"README claims about it"
        )

    # The claim shape that broke: an absolute "nothing is above E-0".
    above = at_e1 + at_e3 + levels.get("E-2", 0)
    if above:
        for match in re.finditer(r"(?:no|none)[^.\n]{0,80}above E-0", readme, re.I):
            findings.append(
                f"README.md: says '{match.group(0).strip()}' while {above} check(s) "
                f"sit above E-0 — the sentence that had to be corrected once "
                f"already (B-18), stated again"
            )

    return make_result(
        "README_EVIDENCE_CLAIMS_CURRENT",
        "the README's statements about evidence levels match the catalogue",
        "medium",
        not findings,
        "The front page describes the evidence axis as something other than "
        "what the gate files hold — the failure type B-18 exposed, in the text "
        "that corrects it." if findings
        else f"README matches the catalogue: E-1 {at_e1}, E-3 {at_e3}, "
             f"E-0 {at_e0}, without a level {unset}.",
        findings,
    )


# Documents a reference may point at. A reference to source code is a
# different thing — the file either compiles or it does not, and the build
# says so. A reference to a DOCUMENT fails silently.
_DOC_REFERENCE_ROOTS = ("docs/", "specs/")

# "HANDBUCH 3.4", "HISTORIE H4.19", "SPEC-04b Teil 3.2" — a named section.
# The keyword is captured, because "Teil 3.2" in a SPEC is NOT heading 3.2:
# the SPECs number their headings (1., 2., 3.) and label their parts
# independently ("## 5. Teil 3 — ..."), so "Teil 3.2" means the second
# subsection of part 3, which is heading 5.2. Resolving that is the whole
# reason this stage can say anything about SPEC references at all.
_SECTION_REFERENCE = re.compile(
    r"\b(HANDBUCH|HISTORIE|SPEC-\d+[a-z]?)\b[^\S\n]*"
    r"(Abschnitt |Teil |Kapitel )?"
    r"(H?\d+(?:\.\d+)*)"
)

# "## 5. Teil 3 — Drift messen": part 3 lives under heading 5.
_PART_HEADING = re.compile(r"^#{1,6}\s*(\d+(?:\.\d+)*)\.?\s*Teil\s+(\d+)\b", re.M)

# Headings a section number can live in: "## 3.4 ...", "### H4.19 ...",
# "# TEIL 5 — ...", "## Teil 3 ..." — all four forms occur in these files.
_HEADING_NUMBER = re.compile(r"^#{1,6}\s*(?:TEIL|Teil)?\s*(H?\d+(?:\.\d+)*)", re.M)


def _tracked_files() -> set[str]:
    """Everything git knows. The point of the check is what a CLONE contains."""
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files"],
        capture_output=True, text=True, timeout=30,
    )
    if out.returncode != 0:
        return set()
    return set(out.stdout.split())


def _part_map_of(path: Path) -> dict:
    """part number -> heading number that carries it ("Teil 3" -> "5")."""
    return {part: head for head, part in _PART_HEADING.findall(read_text(path))}


def _headings_of(path: Path) -> set[str]:
    numbers = set()
    for n in _HEADING_NUMBER.findall(read_text(path)):
        numbers.add(n)
        # "7.3.1" also satisfies a reference to "7.3", which is how these
        # documents are cited in practice.
        parts = n.split(".")
        for i in range(1, len(parts)):
            numbers.add(".".join(parts[:i]))
    return numbers


# Inventory counts: a number that moves when the repository grows. The
# distinction is HANDBUCH 5.1's, quoted rather than reinvented — an inventory
# count changes through growth, an identifier changes through a decision.
#
# Every pattern is anchored with (?<![\w.-]) so that a digit belonging to an
# identifier cannot start a match: "E-3 checks" is a level and a noun,
# "3.4 Gate-Anatomie" is a section heading, and a guard that fires on those
# gets switched off instead of fixed.
_NO_ID_BEFORE = r"(?<![\w.\-/])"
_COUNT_PATTERNS = [
    (_NO_ID_BEFORE + r"\d+\s+(?:Quality[ -]?)?Gates?(?![\w-])", "gate count"),
    (_NO_ID_BEFORE + r"\d+\s+(?:policy[ _-]?)?[Cc]hecks?(?![\w-])", "check count"),
    (_NO_ID_BEFORE + r"\d+\s+(?:OPA[/ ])?(?:Rego[- ]?)?(?:Policies|Policy|policies)(?![\w-])",
     "policy count"),
    (_NO_ID_BEFORE + r"\d+\s+(?:Rego[- ]?)?(?:Regeln|rules)(?![\w-])", "rule count"),
    (_NO_ID_BEFORE + r"\d+\s+(?:Unit[- ]?)?(?:Tests?|tests?)(?![\w-])", "test count"),
    (_NO_ID_BEFORE + r"\d+\s+[Rr]equirements?(?![\w-])", "requirement count"),
    (_NO_ID_BEFORE + r"\d+\s+[Ii]ntegrity[- ]?[Cc]hecks?(?![\w-])", "integrity-check count"),
    (_NO_ID_BEFORE + r"\d+\s*(?:AUTO|HYBRID|MANUAL)(?![\w-])", "automation split"),
    (_NO_ID_BEFORE + r"\d+\s*[:/]\s*\d+\s*[:/]\s*\d+(?![\w-])", "ratio"),
    (_NO_ID_BEFORE + r"\d+\s+(?:von|of)\s+\d+\s+"
     r"(?:Gates?|[Cc]hecks?|Tests?|[Rr]equirements?|Policies|Regeln|rules|Wirkungen)(?![\w-])",
     "share of an inventory"),
]

# A date used as a deadline. AGENTS.md only: the handbook names statutory
# periods (NIS2 hours, the AI Act's application dates), and a check that fires
# on those is the false alarm this one exists to avoid.
_DATE = r"(?:\d{1,2}\.\s?(?:Januar|Februar|M(?:ä|ae)rz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{4}|\d{1,2}\.\d{1,2}\.\d{4}|\d{4}-\d{2}-\d{2})"
_DEADLINE_WORD = r"(?:Deadline|Frist|Abgabe|Termin|f(?:ä|ae)llig|sp(?:ä|ae)testens|bis zum|bis spätestens|due|by the)"
_DEADLINE_LINE = re.compile(
    rf"(?:{_DEADLINE_WORD}[^\n]{{0,60}}{_DATE}|{_DATE}[^\n]{{0,40}}{_DEADLINE_WORD})"
)

# Scope. HISTORIE.md is deliberately absent: it is a historical record and
# states counts about closed events on purpose — "the CI reported 173/173
# while 187 tests ran" is the finding, not a stale number.
_COUNT_FREE_DOCS = ("AGENTS.md", "HANDBUCH.md")


# The three ways to make an identity-bound verification worthless
# (SPEC-05 Abschnitt 6.1). They are named "insecure-*" for a reason; a
# repository whose subject is evidential weight does not use them, and does
# not rely on nobody having the idea — it checks.
_PERMISSIVE_IDENTITY = re.compile(
    r"--certificate-identity-regexp[= ]+['\"]?(\.\*|\.\+|\^?\.\*\$?)['\"]?"
)
_TLOG_OFF = "--insecure-ignore-tlog"
_SCT_OFF = "--insecure-ignore-sct"

# Only files that can EXECUTE something are held to the flags. Naming a flag
# in order to forbid it is not using it, and the ban has to be explainable:
# the SPEC says why the flags are refused, the policy comment says why C-07 is
# a MUST, the fixtures say what they are. Scanning prose for the words it
# needs in order to forbid them is the false alarm that gets a check switched
# off rather than repaired (T-03, twice).
#
# Rego cannot invoke cosign, so .rego counts as prose here too. The two places
# that CAN call it — the workflow and the verification script — are covered,
# and both were counter-proved by planting each flag in them (T-05).
_EXECUTABLE_SUFFIXES = (".py", ".sh", ".yml", ".yaml")
_SIGNING_FLAG_PROSE = (
    "tests/test_integrity_regression.py",
    "evidence-store/scripts/verify_signature.py",
)


def _python_code_only(text: str) -> str:
    """The source with comments and docstrings removed.

    A file may NAME a forbidden flag in order to forbid it — this suite does,
    the SPEC does, and so does the verification script's own docstring. What
    matters is whether the flag is PASSED. Stripping prose separates the two;
    a check that cannot tell "mentions" from "uses" produces exactly the kind
    of false alarm that gets a check switched off (T-03).
    """
    import io
    import tokenize

    triple = ('"' * 3, "'" * 3, 'r' + '"' * 3, 'r' + "'" * 3)
    kept = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING and tok.line.strip().startswith(triple):
                continue    # docstring
            kept.append(tok.string)
    except (tokenize.TokenError, IndentationError):
        return text
    return "\n".join(kept)


def check_e1_claims_are_signed() -> dict:
    """A check may only claim E-1 if a signature mechanism stands behind it.

    This is the generalisation of REQUIRED_INPUTS_ENFORCED onto the evidence
    axis, and it exists so that B-18 cannot happen twice. There, one check
    carried `evidence_level: "E-1"` for a SHA-256 hash chain: a checksum, not
    a signature, with `inserted_by` a string the writer picks. The claim was
    wrong at the moment it was written, and nothing in the repository could
    tell — a string in a YAML file breaks no test.

    E-1 means: a produced and SIGNED artefact, signature and producer identity
    verified, forgery costing the CI identity (HANDBUCH 3.3). So a gate that
    carries an E-1 check must

      * declare an input that IS a signature verification, produced by the
        verification script, and
      * have that obligation enforced by BOTH callers — the orchestrator and
        the workflow. The lesson of B-17 is not "check harder" but: ask WHERE
        a mechanism has to act. An E-1 claim enforced only locally would be an
        E-0 claim with a better label in the environment that ships images.

    Deliberately not checked here: whether the signature is any good. That is
    what SIGNATURE_VERIFY_PINS_IDENTITY and the gate's own C-04..C-07 do. This
    check answers one question only — is there a mechanism behind the claim.
    """
    findings = []
    workflow = REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml"
    wf_text = read_text(workflow) if workflow.is_file() else ""
    orch_text = read_text(REPO_ROOT / "pipeline" / "gate_orchestrator.py")
    runner = REPO_ROOT / "pipeline" / "ci" / "run_gate.sh"
    runner_text = read_text(runner) if runner.is_file() else ""

    for f, gate in _load_gate_files():
        gate_id = gate.get("id", f.stem)
        checks = gate.get("policy_checks") or []
        e1 = [c.get("id") for c in checks
              if isinstance(c, dict) and c.get("evidence_level") == "E-1"]
        if not e1:
            continue

        rel = f.relative_to(REPO_ROOT)
        inputs = gate.get("required_inputs") or []
        signature_inputs = [
            d for d in inputs
            if "signature" in str(d.get("kind", ""))
            or "verify_signature" in str(d.get("produced_by", ""))
        ]
        if not signature_inputs:
            findings.append(
                f"{rel}: {gate_id} carries E-1 on {', '.join(e1)} but declares no "
                f"signature input. E-1 means a signed artefact with a verified "
                f"producer identity — without one, the level is a label (B-18)"
            )
            continue

        for decl in signature_inputs:
            kind = decl.get("kind")
            producer = str(decl.get("produced_by", ""))
            if "verify_signature.py" not in producer:
                findings.append(
                    f"{rel}: {gate_id}'s '{kind}' is not produced by "
                    f"verify_signature.py, so what the E-1 checks read is not a "
                    f"signature verification"
                )
            # Both callers, or the obligation holds only where nobody ships.
            if f"{gate_id}:{kind}=" not in wf_text:
                findings.append(
                    f".github/workflows/gate-pipeline.yml: supplies no '{kind}' for "
                    f"{gate_id}, whose checks claim E-1 — the claim would hold "
                    f"locally and not in the pipeline that decides what ships (B-17)"
                )
            if "check_required_inputs" not in orch_text:
                findings.append(
                    "pipeline/gate_orchestrator.py: does not enforce required inputs, "
                    "so the E-1 claim rests on nothing locally"
                )
            if runner_text and "-inputs.args" not in runner_text and "-inputs.args" not in wf_text:
                findings.append(
                    "the CI gate runner never reads the resolved inputs — the "
                    "signature document would be supplied and not evaluated"
                )

    # The signing side has to exist at all.
    if any(c.get("evidence_level") == "E-1"
           for _f, g in _load_gate_files()
           for c in (g.get("policy_checks") or []) if isinstance(c, dict)):
        if "sign-blob" not in wf_text:
            findings.append(
                ".github/workflows/gate-pipeline.yml: a check claims E-1 and nothing "
                "in the workflow signs anything"
            )
        if "id-token" not in wf_text:
            findings.append(
                ".github/workflows/gate-pipeline.yml: a check claims E-1 and no job "
                "requests the OIDC token — keyless signing cannot happen"
            )

    return make_result(
        "E1_CLAIMS_ARE_SIGNED",
        "every E-1 claim has a signature mechanism behind it, enforced by both callers",
        "high",
        not findings,
        "A check claims signed evidence while nothing signs, or the obligation is "
        "enforced in only one of the two places that run gates — B-18 with a "
        "different label." if findings
        else "Every E-1 check rests on a declared signature verification, enforced by "
             "the orchestrator and by the workflow, with a signing job behind it.",
        findings,
    )


def check_signature_verify_pins_identity() -> dict:
    """Every signature verification names the signer, and nothing switches it off.

    Keyless signing is only worth the OIDC round-trip if the verification is
    bound to an identity. cosign covers the most obvious mistake itself — a
    verify-blob without any identity argument aborts rather than passing. The
    remaining three ways are quieter, and each one alone cancels the evidence
    level:

      * a permissive --certificate-identity-regexp (".*", ".+"): the call goes
        green and pins nothing. The same hole as B-17 — the mechanism is
        present and does not act.
      * --insecure-ignore-tlog: no transparency log, so no independent
        timestamp and no public verifiability. The proof falls back to "trust
        whoever hands it to you".
      * --insecure-ignore-sct: no proof of inclusion in the certificate
        transparency log.

    So: every `cosign verify-blob` in this repository must carry an exact
    --certificate-identity and a --certificate-oidc-issuer, and none of the
    three switches may appear anywhere outside the files that discuss them.

    HIGH severity: a verification that pins nothing is indistinguishable from
    one that pins everything, right up to the moment it matters.
    """
    findings = []
    tracked = _tracked_files()

    for f in sorted(tracked):
        path = REPO_ROOT / f
        if not path.is_file():
            continue
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue

        executable = f.endswith(_EXECUTABLE_SUFFIXES)
        if executable and f not in _SIGNING_FLAG_PROSE:
            for flag in (_TLOG_OFF, _SCT_OFF):
                for line in find_lines(text, flag):
                    findings.append(
                        f"{f}:{line}: uses {flag} — the transparency-log proof is "
                        f"the difference between an independently checkable "
                        f"signature and one you have to take on trust"
                    )
            hit = _PERMISSIVE_IDENTITY.search(text)
            if hit:
                findings.append(
                    f"{f}: uses a permissive identity regexp ({hit.group(0).strip()}) — "
                    f"the verification goes green while pinning nothing"
                )

        # Every actual verify-blob invocation must pin identity and issuer.
        if "verify-blob" in text and executable and f not in _SIGNING_FLAG_PROSE:
            if "--certificate-identity" not in text:
                findings.append(
                    f"{f}: calls cosign verify-blob without --certificate-identity"
                )
            if "--certificate-oidc-issuer" not in text:
                findings.append(
                    f"{f}: calls cosign verify-blob without --certificate-oidc-issuer"
                )

    # The verification script is the one place that builds the invocation, so
    # it is held to the flags positively rather than by absence.
    script = REPO_ROOT / "evidence-store" / "scripts" / "verify_signature.py"
    if script.is_file():
        text = read_text(script)
        for flag in ("--certificate-identity", "--certificate-oidc-issuer",
                     "--certificate-github-workflow-repository",
                     "--certificate-github-workflow-sha"):
            if flag not in text:
                findings.append(
                    f"evidence-store/scripts/verify_signature.py: does not pass {flag} — "
                    f"the signature would not be bound to {'the commit' if 'sha' in flag else 'an identity'}"
                )
        code = _python_code_only(text)
        for flag in (_TLOG_OFF, _SCT_OFF):
            if flag in code:
                findings.append(
                    f"evidence-store/scripts/verify_signature.py: passes {flag}"
                )
        if '"decision"' in code or "'decision'" in code:
            findings.append(
                "evidence-store/scripts/verify_signature.py: writes a 'decision' field — "
                "the detector verifies, Rego decides (B-04)"
            )
    else:
        findings.append("evidence-store/scripts/verify_signature.py is missing")

    return make_result(
        "SIGNATURE_VERIFY_PINS_IDENTITY",
        "every signature verification is bound to an identity, and nothing switches the checks off",
        "high",
        not findings,
        "A signature verification in this repository pins nothing, or a check that "
        "makes it worth something is switched off — the evidence level is gone and "
        "the call still reports success." if findings
        else "Verification pins identity, issuer, repository and commit; no insecure "
             "flag and no permissive identity regexp anywhere.",
        findings,
    )


def check_signing_context_asserted() -> dict:
    """CI reads `signing_context` back and refuses a run that calls itself local.

    The manifest DECLARES the context it was produced in (SPEC-05 Abschnitt
    8.1). A declaration is worth what the check behind it is worth, and this
    project has found the same gap five times (B-02, B-11, B-12, B-13, B-17):
    the field exists, nobody holds it against anything.

    The obvious objection to `signing_context` is that somebody sets it to
    "local" in CI and is off the hook. So CI asserts the value after building
    the manifest and again in the job that signs it, and aborts otherwise —
    and this check holds that both assertions are in the workflow.
    """
    workflow = REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml"
    findings = []
    if not workflow.is_file():
        findings.append("gate-pipeline.yml is missing")
    else:
        text = read_text(workflow)
        asserts = [
            line for line in text.splitlines()
            if 'CONTEXT' in line and '!=' in line and '"ci"' in line
        ]
        if not asserts:
            findings.append(
                ".github/workflows/gate-pipeline.yml: does not compare signing_context "
                "against 'ci' — the manifest could declare itself local in CI and "
                "nothing would notice"
            )
        elif len(asserts) < 2:
            findings.append(
                ".github/workflows/gate-pipeline.yml: asserts signing_context in only "
                "one place. It is asserted where the manifest is built AND in the job "
                "that signs it — the signing job runs on a downloaded artefact, so it "
                "has to check what it actually received (B-17: ask where a mechanism "
                "must act, not only whether it acts)"
            )
        if "signing_context" not in text:
            findings.append(
                ".github/workflows/gate-pipeline.yml: never mentions signing_context"
            )
        for marker in ("exit 1",):
            if asserts and marker not in text:
                findings.append(
                    ".github/workflows/gate-pipeline.yml: compares signing_context but "
                    "does not abort"
                )

    prepare = REPO_ROOT / "pipeline" / "prepare_inputs.py"
    if prepare.is_file():
        text = read_text(prepare)
        for forbidden in ("signing_context", "cosign", "sign-blob", "signature_verification"):
            if forbidden in text:
                findings.append(
                    f"pipeline/prepare_inputs.py: mentions '{forbidden}' — the walkthrough "
                    f"may not issue its own signature evidence (B-03)"
                )

    return make_result(
        "SIGNING_CONTEXT_ASSERTED",
        "CI checks the manifest's declared signing context and refuses a local claim",
        "medium",
        not findings,
        "The signing context is declared and not held against anything — the failure "
        "type this project has now found six times." if findings
        else "signing_context is asserted where the manifest is built and again where "
             "it is signed; prepare_inputs.py issues no signature evidence.",
        findings,
    )


def check_counts_live_in_readme_only() -> dict:
    """The working contract and the handbook carry no inventory counts.

    HANDBUCH 5.1 draws the line and this check only enforces it: an inventory
    count changes through GROWTH, an identifier changes through a DECISION.
    "Seventeen gates" is the first kind and is wrong as soon as an eighteenth
    lands. "E-1", "schema_version: 2", "v06", "Exit 3", "Art. 26", "R001",
    "DP1", "B-19", "SPEC-04b", "2.4" are the second kind: they move when
    somebody decides they move, and they are the vocabulary these documents
    are written in.

    The counts live in the README, where README_COUNTS_CURRENT and
    README_EVIDENCE_CLAIMS_CURRENT hold them against the repository. A second
    set anywhere else has no guardian, and this project has the receipts:
    AGENTS.md carried a gate count from before SPEC-01 and SPEC-03 for weeks
    while every session read it first (T-03), the CI reported a hard-coded
    test count while more tests ran (B-12), and the README denied a rung of
    its own evidence axis (B-19).

    HISTORIE.md is out of scope on purpose. It records closed events, and the
    stale numbers in it are the subject matter.

    Deadlines are checked in AGENTS.md only. The handbook names statutory
    periods and application dates; a check that fires on those is the false
    alarm that gets a check disabled rather than repaired.
    """
    findings = []
    for name in _COUNT_FREE_DOCS:
        path = REPO_ROOT / name
        if not path.is_file():
            findings.append(f"{name}: not found — this check cannot verify it")
            continue
        text = read_text(path)

        in_code_fence = False
        for number, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("```"):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue    # commit-message examples and templates quote reality

            for pattern, label in _COUNT_PATTERNS:
                for hit in re.finditer(pattern, line):
                    findings.append(
                        f"{name}:{number}: states '{hit.group(0).strip()}' — an inventory "
                        f"{label} belongs in the README, where a check holds it against "
                        f"the repository (HANDBUCH 5.1)"
                    )

            if name == "AGENTS.md":
                deadline = _DEADLINE_LINE.search(line)
                if deadline:
                    findings.append(
                        f"{name}:{number}: states a deadline ('{deadline.group(0).strip()}') "
                        f"— the working contract describes how work is done, not when it is due"
                    )

    return make_result(
        "COUNTS_LIVE_IN_README_ONLY",
        "the working contract and the handbook delegate every inventory count to the README",
        "medium",
        not findings,
        "A second set of counts has appeared outside the README, where nothing holds "
        "it against the repository — the way AGENTS.md came to describe a catalogue "
        "that no longer existed." if findings
        else f"{len(_COUNT_FREE_DOCS)} documents carry identifiers and no inventory counts.",
        findings,
    )


def check_doc_references_are_tracked() -> dict:
    """A tracked file may not point at a document the clone does not contain.

    HANDBUCH.md and HISTORIE.md carried the reasoning layer of this control
    system — the E6 axis, the gate anatomy, the finding register B-01…B-19 —
    and were excluded by .gitignore, in a block that listed generated
    artefacts. Meanwhile 40 tracked files cited them: every gate definition,
    the gate template, record_evidence.py, drift_detector.py, SPEC-04 and
    SPEC-05. Anyone who cloned the repository found references to documents
    that were not there.

    That is worse than a wrong number, and it is why this check is HIGH: a
    wrong number can be checked and disputed. A reference to a document the
    reader does not have is a claim they cannot even reach.

    Two stages, because the reference has two halves:

      1. The FILE must be tracked. Not "must exist" — a file that exists only
         on the author's machine is exactly the failure this check is named
         after, and it looks identical from inside that machine.
      2. The SECTION must exist. Forty references named the handbook and a
         section in the sevens; the handbook ends in the sixes, and those
         sections live in the history document. Nobody noticed for as long
         as neither document could be opened from a clone. (The numbers are
         spelled around here on purpose: this check reads its own file too,
         and a quoted example would be a finding.)

    Deliberately narrow: only documents (*.md at the root, docs/**, specs/**)
    and only numbered sections. Prose references ("see the handbook") are not
    machine-checkable and stay a matter of authorship.
    """
    tracked = _tracked_files()
    if not tracked:
        return make_result(
            "DOC_REFERENCES_ARE_TRACKED",
            "every document a tracked file names is itself tracked",
            "high", False,
            "git ls-files produced nothing — the check could not run, and a "
            "check that cannot run must not report success.",
            ["Could not enumerate tracked files."],
        )

    findings = []
    doc_names = {}          # bare filename -> repo-relative path, for tracked docs
    for f in tracked:
        if f.endswith(".md") and ("/" not in f or f.startswith(_DOC_REFERENCE_ROOTS)):
            doc_names[Path(f).name] = f

    tracked_basenames = {Path(f).name for f in tracked}

    # Every markdown file that is physically here, by basename. The first
    # version of this check looked only in the repository ROOT, which let
    # AGENTS.md keep pointing at a policy-candidates document: the file is
    # real, it sits under legacy/, and .gitignore excludes it —
    # so it was neither tracked nor found where the check was looking. A
    # guard that only searches one directory reports "fine" for exactly the
    # references that are hardest to notice by hand.
    on_disk = {}
    for path in REPO_ROOT.rglob("*.md"):
        if any(part in (".git", ".claude", "node_modules") for part in path.parts):
            continue
        on_disk.setdefault(path.name, []).append(
            str(path.relative_to(REPO_ROOT))
        )

    # Documents referenced by name anywhere in the tracked tree.
    referenced = re.compile(r"\b([A-Z][A-Za-z0-9_-]*\.md)\b")
    # ...and referenced by path, e.g. a file below docs/ or specs/.
    referenced_path = re.compile(r"((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.md)")

    section_targets = {}    # document name -> set of heading numbers
    for f in sorted(tracked):
        path = REPO_ROOT / f
        if not path.is_file():
            continue
        try:
            text = read_text(path)
        except (OSError, UnicodeDecodeError):
            continue

        # ── Stage 1: the document must be tracked ──
        #
        # .gitignore is exempt: naming files that are NOT in the repository
        # is what that file is for.
        for name in set(referenced.findall(text)) if f != ".gitignore" else ():
            if name in tracked_basenames or name == Path(f).name:
                continue
            where = on_disk.get(name)
            if where:
                findings.append(
                    f"{f}: names '{name}', which exists here ({', '.join(sorted(where))}) "
                    f"but is NOT tracked — a clone of this repository does not contain it"
                )

        # A path-form reference is unambiguously repo-internal when its first
        # segment is a directory of this repository. Then it must be tracked;
        # there is no reading under which it points somewhere else.
        for ref in set(referenced_path.findall(text)) if f != ".gitignore" else ():
            # A relative link is resolved against the file that carries it —
            # "../AGENTS.md" in docs/ is AGENTS.md, and reading it literally
            # would report a file that is right there.
            resolved = posixpath.normpath(
                posixpath.join(posixpath.dirname(f), ref) if ref.startswith("..") else ref
            )
            if resolved in tracked or resolved == f:
                continue
            if resolved.startswith("..") or not (REPO_ROOT / resolved.split("/")[0]).is_dir():
                continue    # points outside this repository — not this check's business
            findings.append(
                f"{f}: points at '{ref}', which is not tracked — the path is inside "
                f"this repository, so a clone must be able to open it"
            )

        # ── Stage 2: the named section must exist ──
        for doc, keyword, number in set(_SECTION_REFERENCE.findall(text)):
            if doc.startswith("SPEC-"):
                matches = [n for n in doc_names if n.startswith(doc + "-")]
                if not matches:
                    continue
                target = doc_names[matches[0]]
            else:
                target = doc_names.get(doc + ".md")
                if target is None:
                    # The citation names the document without its extension —
                    # "HANDBUCH 3.4" — which stage 1's filename scan cannot
                    # see. This is the exact shape the 17 gate definitions
                    # used while both documents sat in .gitignore.
                    findings.append(
                        f"{f}: cites '{doc}', which is not a tracked document — "
                        f"a clone cannot open the section it points at"
                    )
                    continue
            if target not in section_targets:
                section_targets[target] = (
                    _headings_of(REPO_ROOT / target),
                    _part_map_of(REPO_ROOT / target),
                )
            headings, parts = section_targets[target]

            wanted = number
            if keyword.strip() == "Teil" and parts:
                head, _, rest = number.partition(".")
                if head not in parts:
                    findings.append(
                        f"{f}: cites '{doc} Teil {number}', but {target} has no "
                        f"part {head}"
                    )
                    continue
                wanted = f"{parts[head]}.{rest}" if rest else parts[head]

            if wanted not in headings:
                cited = f"{doc} {keyword}{number}".strip()
                findings.append(
                    f"{f}: cites '{cited}', but {target} has no section "
                    f"with that number"
                )

    return make_result(
        "DOC_REFERENCES_ARE_TRACKED",
        "every document a tracked file names is tracked, and every cited section exists",
        "high",
        not findings,
        "A tracked file points at a document or a section that a clone of this "
        "repository does not contain — a claim the reader cannot even reach." if findings
        else f"{len(doc_names)} documents referenced, every reference resolves to a "
             f"tracked file and an existing section.",
        sorted(set(findings)),
    )


def check_required_inputs_enforced() -> dict:
    """SPEC-04b Teil 3.2: a high-assurance check must not be bypassable.

    Checks at evidence level E-2 or E-3 evaluate a document somebody has to
    produce — a cluster query, a measurement. Rego rules that read such a
    document only fire when it is present, so omitting it turns the check
    off silently and the gate passes on whatever E-0 material is left.

    SPEC-04 declared C-03..C-05 on G-OPS-03 at E-3 and stated the presence
    obligation would be "enforced one level up, by the orchestrator". It was
    not, for two weeks, and nothing noticed. That is the failure this check
    prevents from recurring: a MUST that can be bypassed by leaving out its
    input is not a MUST.

    Two directions, because a one-way check would leave the other half open:
      - a gate carrying E-2/E-3 checks must declare required_inputs
      - a declared required_input must be well-formed enough to act on
        (kind, and a producer a reader can actually run)
    """
    findings = []

    for f, gate in _load_gate_files():
        gate_id = gate.get("id", f.stem)
        checks = gate.get("policy_checks") or []
        high = [
            c for c in checks
            if c.get("evidence_level") in ("E-2", "E-3")
            and c.get("implementation") == "implemented"
        ]
        declared = gate.get("required_inputs") or []

        if high and not declared:
            ids = ", ".join(c.get("id", "?") for c in high)
            findings.append(
                f"{f.relative_to(REPO_ROOT)}: checks {ids} sit at evidence level "
                f"E-2/E-3 but the gate declares no required_inputs — omitting the "
                f"document those checks read would silently disable them"
            )

        for decl in declared:
            if not decl.get("kind"):
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: a required_inputs entry has no "
                    f"'kind', so nothing can be matched against it"
                )
            if not decl.get("produced_by"):
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: required input "
                    f"'{decl.get('kind')}' names no producer — a reader who hits "
                    f"the failure cannot act on it"
                )

    # The orchestrator has to actually act on the declaration.
    orch = read_text(REPO_ROOT / "pipeline" / "gate_orchestrator.py")
    if "check_required_inputs" not in orch or "load_gate_required_inputs" not in orch:
        findings.append(
            "pipeline/gate_orchestrator.py: no required-inputs enforcement — the "
            "declaration in the gate definitions would be decorative"
        )

    # And so does the CI, which is the environment that counts.
    #
    # This half was missing until SPEC-04b Teil 3.1/3.3, and its absence is
    # instructive: the check above passed the whole time, because the
    # orchestrator did enforce. The CI does not run the orchestrator — it
    # calls conftest per gate — so the obligation held everywhere except in
    # the pipeline that decides whether an image ships. Verifying one caller
    # and calling the obligation enforced is the same mistake one level out.
    wf = read_text(REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml")
    if "ci_required_inputs.py" not in wf:
        findings.append(
            ".github/workflows/gate-pipeline.yml: the workflow never resolves "
            "required_inputs, so a gate resting on a measurement passes in CI "
            "without one — the orchestrator's enforcement does not reach here"
        )
    else:
        # Resolving is not evaluating. If run_gate.sh ignores the resolved
        # files, the documents are supplied and nobody reads them.
        if "-inputs.args" not in wf or "-inputs.fail" not in wf:
            findings.append(
                ".github/workflows/gate-pipeline.yml: required inputs are resolved "
                "but the gate runner reads neither the resolved evaluations "
                "(-inputs.args) nor the findings (-inputs.fail) — supplying a "
                "document nobody reads is not evidence"
            )
        for f, gate in _load_gate_files():
            gate_id = gate.get("id", f.stem)
            for decl in gate.get("required_inputs") or []:
                kind = decl.get("kind")
                if kind and f"{gate_id}:{kind}=" not in wf:
                    findings.append(
                        f".github/workflows/gate-pipeline.yml: {gate_id} declares "
                        f"required input '{kind}', and the workflow supplies none. "
                        f"The gate would fail in CI for a reason nobody intended, "
                        f"or — worse — the declaration was added and forgotten"
                    )

    # PyYAML has to be installed in EVERY job that runs the enforcement, or
    # load_gate_required_inputs() returns {} after a warning and every
    # declaration is silently skipped.
    #
    # Per job, not per file: a first version of this rule searched the whole
    # workflow for "pip install ... PyYAML" and stayed green when the install
    # was removed from the job that needs it, because a different job still
    # had one. A check a counter-test cannot break is not a check (B-16).
    import yaml as _yaml
    try:
        jobs = (_yaml.safe_load(wf) or {}).get("jobs") or {}
    except _yaml.YAMLError as exc:
        findings.append(
            f".github/workflows/gate-pipeline.yml: not parsable ({exc}), so the "
            f"enforcement cannot be verified"
        )
        jobs = {}
    for job_name, job in jobs.items():
        runs = "\n".join(
            str(s.get("run", "")) for s in (job.get("steps") or []) if isinstance(s, dict)
        )
        if "ci_required_inputs.py" not in runs:
            continue
        if not re.search(r"pip install[^\n]*PyYAML", runs):
            findings.append(
                f".github/workflows/gate-pipeline.yml: job '{job_name}' runs the "
                f"required-inputs enforcement without installing PyYAML — "
                f"load_gate_required_inputs() returns an empty map after a warning, "
                f"so the enforcement is off while appearing to run"
            )

    return make_result(
        "REQUIRED_INPUTS_ENFORCED",
        "high-assurance checks declare the input they rest on, and it is enforced",
        "high",
        not findings,
        "An E-2/E-3 check whose input can simply be omitted is an E-0 check with a "
        "better label." if findings
        else "Every gate with E-2/E-3 checks declares its required inputs, and both "
             "the orchestrator and the CI workflow enforce them.",
        findings,
    )


def check_negative_cases_gate_the_build() -> dict:
    """SPEC-04b Teil 3.3: a green run must not be able to ship on its own.

    The quality-gates job proves that nothing blocked. It does not prove
    that anything COULD block, and those are different statements. A gate
    catalogue in which no gate can turn red any more — a broken policy, a
    wrong conftest namespace, a presence obligation that resolves to
    nothing — still reports 17/17 PASS, and that particular green is the
    opposite of evidence.

    So the build depends on both jobs: all gates green, AND the negative
    cases demonstrated that the gates block. This is checked rather than
    trusted for the same reason the counts are (B-12): `needs` is one line,
    it is convenient to drop while refactoring, and nothing about the
    workflow would look wrong afterwards.

    Three directions, because each alone leaves a hole:
      - the negative-cases job exists and asserts a BLOCK, not just a run
      - the build job lists it under `needs`
      - the job actually covers the gates whose negative case is claimed
    """
    findings = []
    import yaml as _yaml

    wf_path = REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml"
    try:
        wf = _yaml.safe_load(read_text(wf_path)) or {}
    except _yaml.YAMLError as exc:
        return make_result(
            "NEGATIVE_CASES_GATE_THE_BUILD",
            "the build waits for proof that the gates can block",
            "high", False,
            "The workflow is not parsable, so the dependency cannot be verified.",
            [f".github/workflows/gate-pipeline.yml: not parsable ({exc})"],
        )

    jobs = wf.get("jobs") or {}
    neg = jobs.get("negative-cases")
    build = jobs.get("build-and-push")

    if neg is None:
        findings.append(
            ".github/workflows/gate-pipeline.yml: no 'negative-cases' job — a green "
            "pipeline would only show that nothing blocked, never that anything could"
        )
    else:
        runs = "\n".join(
            str(s.get("run", "")) for s in (neg.get("steps") or []) if isinstance(s, dict)
        )
        # The INVOCATIONS, not the job text.
        #
        # A first version searched the job for the words "BLOCK", "PASS" and
        # the gate ids, and stayed green through three counter-tests: the
        # words also occur in expect_gate.sh's own definition ("$EXPECT" =
        # "BLOCK") and in the summary banner. It was reading the helper's
        # source and the decoration, not what the job asserts (B-16).
        calls = re.findall(r'expect_gate\.sh\s+(\w+)\s+"([^"]*)"', runs)
        blocked = [label for expect, label in calls if expect == "BLOCK"]
        passed = [label for expect, label in calls if expect == "PASS"]

        if not blocked:
            findings.append(
                ".github/workflows/gate-pipeline.yml: the negative-cases job makes no "
                "expect_gate.sh BLOCK assertion — a job that merely runs the fixtures "
                "proves nothing about blocking"
            )
        # The counter-check is half of the evidence: a case that is red for
        # the wrong reason looks exactly like one that is red for the right
        # one (B-16).
        if not passed:
            findings.append(
                ".github/workflows/gate-pipeline.yml: the negative-cases job makes no "
                "expect_gate.sh PASS assertion — without a passing normal case next "
                "to the blocked one, a block could be a block for any reason at all"
            )
        for gate_id in ("G-OPS-03", "G-DEP-02"):
            if not any(gate_id in label for label in blocked):
                findings.append(
                    f".github/workflows/gate-pipeline.yml: no negative case asserts "
                    f"that {gate_id} blocks, though the README claims its negative "
                    f"case is demonstrated in CI"
                )

    if build is None:
        findings.append(
            ".github/workflows/gate-pipeline.yml: no 'build-and-push' job to gate"
        )
    else:
        needs = build.get("needs")
        needs = [needs] if isinstance(needs, str) else list(needs or [])
        if "negative-cases" not in needs:
            findings.append(
                ".github/workflows/gate-pipeline.yml: build-and-push does not depend "
                "on 'negative-cases' — an image would ship even when the proof that "
                "the gates block is red, which is the one failure that invalidates "
                "every other green in the run"
            )
        if "quality-gates" not in needs:
            findings.append(
                ".github/workflows/gate-pipeline.yml: build-and-push does not depend "
                "on 'quality-gates'"
            )

    return make_result(
        "NEGATIVE_CASES_GATE_THE_BUILD",
        "the build waits for proof that the gates can block",
        "high",
        not findings,
        "A pipeline that ships on 'nothing blocked' alone cannot tell a working "
        "gate catalogue from a broken one." if findings
        else "The negative cases assert a block, carry their counter-check, and the "
             "build depends on them.",
        findings,
    )


def check_workflow_claims_no_counts() -> dict:
    """SPEC-04b Teil 1: the pipeline must report what ran, not what it expects.

    The Rego step printed "Rego Unit Tests PASS — 173/173 green" while the
    runner reported 187/187. The number was hard-coded in the message,
    compared against nothing, and travelled into $GITHUB_OUTPUT as
    count=173. Had the test count fallen, the pipeline would still have
    said 173/173 green.

    Structurally that is gate_result.all_passed — a claim about a result
    carried next to the result, which nobody holds against it. Removing it
    once is not enough; the convenient thing is always to type the number.
    So it is checked.

    Scope, deliberately narrow: only text that is DISPLAYED — `echo` output,
    step and job names, and OCI labels baked into the image. Comments may
    name a number as context, including the comments that record this very
    history. A comment is read by someone editing the file; an echo is read
    as a result.
    """
    findings = []
    wf_dir = REPO_ROOT / ".github" / "workflows"
    if not wf_dir.is_dir():
        return make_result(
            "WORKFLOW_CLAIMS_NO_COUNTS", "workflow output states no hard-coded counts",
            "medium", True, "No workflows present.", [],
        )

    # "17 gates", "173 tests", "173/173" — a bare number next to a countable
    # noun, or a ratio. Version-like tokens (v4, 3.11) are not counts.
    count_claim = re.compile(
        r"\b\d+\s*/\s*\d+\b"
        r"|\b\d+\s+(?:gates?|tests?|policies|policy|rules?|checks?|records?|requirements?)\b",
        re.I,
    )

    for wf in sorted(wf_dir.glob("*.y*ml")):
        for lineno, line in enumerate(read_text(wf).split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue  # comments may carry context
            displayed = (
                stripped.startswith("echo ")
                or stripped.startswith("- name:")
                or stripped.startswith("name:")
                or "--label" in stripped
            )
            if not displayed:
                continue
            # A count built from a variable is computed, not claimed.
            if "${{" in stripped or "$(" in stripped or "$PASSED" in stripped or "$COUNT" in stripped:
                continue
            hit = count_claim.search(stripped)
            if hit:
                findings.append(
                    f"{wf.relative_to(REPO_ROOT)}:{lineno}: displays the fixed count "
                    f"'{hit.group(0).strip()}' — a number written into output is a "
                    f"claim nobody holds against the result. Read it from the tool "
                    f"or compute it."
                )

    return make_result(
        "WORKFLOW_CLAIMS_NO_COUNTS",
        "workflow output states no hard-coded counts (SPEC-04b Teil 1)",
        "medium",
        not findings,
        "The pipeline that checks this control system asserts numbers instead of "
        "reporting them — the same fault class the gates were cleared of." if findings
        else "Every count in workflow output is read from the tool or computed.",
        findings,
    )


def check_trigger_matches_requirement() -> dict:
    """B-14: a runtime obligation must be covered by at least one gate that runs.

    Four operations gates declare trigger "kubectl apply — Gatekeeper
    Admission" while their requirements declare audit_trigger "Runtime
    (kontinuierlich)" or "Runtime (Event-getriggert)". Admission control
    fires ONCE, before the workload runs. A requirement asking for
    continuous or event-driven evaluation is not badly served by that —
    it is structurally unservable by it.

    Nobody noticed for months, and the reason is worth stating: both
    statements are checked in, both are valid, and nothing held them
    against each other. It is the kind of contradiction only visible when
    two files are laid side by side.

    The check groups BY REQUIREMENT, not by gate. A requirement with a
    compound audit_trigger ("Deployment CI/CD + Runtime") is legitimately
    served by a SET of gates covering different phases — R003 for instance
    runs through G-PRE-04, G-DEP-02 and G-OPS-04. Demanding that every one
    of them individually cover the runtime part produced six false
    positives on the first run. What matters is that AT LEAST ONE linked
    gate can actually observe operation.

    A gate counts as runtime-capable if it declares required_inputs — a
    document produced while the system runs — or if its trigger is not an
    admission event. G-OPS-03 is the reference: annotation check at
    admission (E-0) plus measurement check with a freshness budget (E-3).
    """
    import yaml

    findings = []

    requirements = {}
    for f in sorted((REPO_ROOT / "requirements").glob("R0*.yaml")):
        try:
            r = yaml.safe_load(read_text(f)) or {}
        except yaml.YAMLError:
            continue
        if r.get("id"):
            requirements[r["id"]] = {
                "audit_trigger": r.get("audit_trigger", "") or "",
                "coverage": r.get("runtime_coverage"),
                "reason": r.get("runtime_gap_reason"),
            }

    ADMISSION = ("kubectl apply", "pr merge", "image-build", "argocd manual-sync")

    # requirement id -> [(gate_id, runtime_capable)]
    coverage: dict[str, list] = {}
    for f, gate in _load_gate_files():
        gate_id = gate.get("id", f.stem)
        trigger = (gate.get("trigger") or "").lower()
        fires_once = any(a in trigger for a in ADMISSION)
        # The escape hatch is narrower than "has an input". An input only
        # covers a runtime obligation if it OBSERVES OPERATION. G-OPS-02
        # gained governance/incident_thresholds.yaml on 2026-08-27 — a
        # professional decision about when an incident is reportable. It
        # says WHEN one would be notifiable; it does not establish THAT
        # one occurred. Counting it as runtime coverage would have closed
        # R009's declared gap on paper while the gate still cannot detect
        # anything — precisely the drift this suite exists to catch.
        observing = any(
            d.get("observes_runtime") is True
            for d in (gate.get("required_inputs") or [])
        )
        runtime_capable = observing or not fires_once
        for rid in (gate.get("links") or {}).get("requirements") or []:
            coverage.setdefault(rid, []).append((gate_id, runtime_capable))

    VALID_COVERAGE = ("covered", "declared_gap")

    for rid, req in sorted(requirements.items()):
        audit = req["audit_trigger"]
        declared = req["coverage"]

        if declared is not None and declared not in VALID_COVERAGE:
            findings.append(
                f"requirements/{rid}.yaml: runtime_coverage '{declared}' is not one "
                f"of {VALID_COVERAGE}"
            )
            continue

        if "runtime" not in audit.lower():
            if declared == "declared_gap":
                findings.append(
                    f"requirements/{rid}.yaml: declares a runtime gap but its "
                    f"audit_trigger asks for no runtime checking — a stale "
                    f"declaration is as misleading as a missing one"
                )
            continue

        gates = coverage.get(rid, [])
        if not gates:
            continue  # unlinked requirements are a different check's problem
        actually_covered = any(capable for _, capable in gates)
        names = ", ".join(g for g, _ in gates)

        if actually_covered:
            # The gap closed. The declaration must not survive it, or the
            # catalogue would keep claiming a weakness it no longer has —
            # the same drift as a stale `design_only`.
            if declared == "declared_gap":
                findings.append(
                    f"requirements/{rid}.yaml: still declares runtime_coverage "
                    f"declared_gap, but {names} can now observe operation. Set it "
                    f"to 'covered'"
                )
            continue

        # Not covered. Acceptable only if the gap is stated, with a reason.
        if declared != "declared_gap":
            findings.append(
                f"requirements/{rid}.yaml: audit_trigger is '{audit.strip()}', but "
                f"none of its gates ({names}) can observe operation — all fire once "
                f"at admission and declare no runtime input. Either give one of them "
                f"a required_input produced while the system runs, as G-OPS-03 has, "
                f"or declare runtime_coverage: declared_gap with a reason"
            )
        elif not (req["reason"] or "").strip():
            findings.append(
                f"requirements/{rid}.yaml: declares a runtime gap without a reason — "
                f"an undocumented gap is indistinguishable from an overlooked one"
            )

    return make_result(
        "TRIGGER_MATCHES_REQUIREMENT",
        "runtime obligations are either covered by a running gate or declared (B-14)",
        "medium",
        not findings,
        "A requirement demanding continuous or event-driven checking is served only "
        "by gates evaluated once at admission, and does not say so — they report on "
        "a moment, not on operation." if findings
        else _runtime_coverage_summary(requirements, coverage),
        findings,
    )


def _runtime_coverage_summary(requirements: dict, coverage: dict) -> str:
    """State the split, so a declared gap stays countable rather than comfortable."""
    runtime = [r for r, v in requirements.items() if "runtime" in v["audit_trigger"].lower()]
    gaps = [r for r in runtime if requirements[r]["coverage"] == "declared_gap"]
    return (
        f"{len(runtime) - len(gaps)} of {len(runtime)} runtime obligations are covered "
        f"by a running gate; {len(gaps)} are declared gaps "
        f"({', '.join(sorted(gaps)) if gaps else 'none'})."
    )


def check_acceptance_criteria_traced() -> dict:
    """Every requirement's own acceptance criteria must point somewhere.

    All 14 requirements have carried `acceptance_criteria` since the
    thesis — 37 of them. Nothing read the field. The only mention outside
    requirements/ was a COMMENT in one policy saying its checks were
    "derived from R014 acceptance_criteria", which is prose, not a
    mechanism.

    That made them the third instance of the same pattern:
    policy_checks[].evidence_level sat null on every gate after SPEC-01,
    scribe_mock_mode was exported and read by nobody, and here a
    requirement stated its own definition of done while the catalogue
    never held the gates against it. R009 says "Meldung erfolgt innerhalb
    der gesetzlichen Frist" — there is no deadline clock, and for two
    years nothing said so.

    A criterion is prose and cannot be matched to a check automatically.
    So the tracing is DECLARED, and this check verifies the declaration
    is well-formed and honest:

      met        -> names concrete gate checks, and each one must exist
      gap        -> names what is missing
      unverified -> warns, and is counted, so it cannot sit unnoticed

    `unverified` is a legitimate state: it says nobody has traced this
    yet, which is different from claiming coverage. It is deliberately
    not a failure — a suite that punishes honesty gets worked around.
    """
    import yaml

    findings = []
    VALID = ("met", "gap", "unverified")

    known_checks = set()
    for _f, gate in _load_gate_files():
        gid = gate.get("id")
        for c in gate.get("policy_checks") or []:
            if gid and c.get("id"):
                known_checks.add(f"{gid}/{c['id']}")

    counts = {"met": 0, "gap": 0, "unverified": 0}
    for f in sorted((REPO_ROOT / "requirements").glob("R0*.yaml")):
        try:
            r = yaml.safe_load(read_text(f)) or {}
        except yaml.YAMLError:
            continue
        rid = r.get("id", f.stem)
        criteria = r.get("acceptance_criteria") or []

        if not criteria:
            findings.append(
                f"requirements/{rid}.yaml: no acceptance_criteria — the "
                f"requirement states no definition of done, so nothing can be "
                f"held against its gates"
            )
            continue

        for i, entry in enumerate(criteria):
            where = f"requirements/{rid}.yaml criterion {i + 1}"
            if not isinstance(entry, dict):
                findings.append(
                    f"{where}: is a bare string. Acceptance criteria must declare "
                    f"status and evidence, otherwise the definition of done is "
                    f"prose that nothing checks"
                )
                continue
            status = entry.get("status")
            if status not in VALID:
                findings.append(f"{where}: status '{status}' is not one of {VALID}")
                continue
            counts[status] += 1

            if status == "met":
                evidence = entry.get("evidence") or []
                if not evidence:
                    findings.append(
                        f"{where}: claims 'met' without naming a check — an "
                        f"unevidenced claim of coverage is the thing this "
                        f"repository exists to catch"
                    )
                for ref in evidence:
                    if ref not in known_checks:
                        findings.append(
                            f"{where}: cites '{ref}', which is not a check in any "
                            f"gate definition. Either the check was renamed or the "
                            f"coverage never existed"
                        )
            elif status == "gap" and not (entry.get("gap_reason") or "").strip():
                findings.append(
                    f"{where}: declares a gap without a reason — an undocumented "
                    f"gap is indistinguishable from an overlooked one"
                )

    total = sum(counts.values())
    summary = (
        f"{counts['met']} of {total} acceptance criteria are evidenced by a named "
        f"check, {counts['gap']} are declared gaps, {counts['unverified']} are not "
        f"traced yet."
    )
    return make_result(
        "ACCEPTANCE_CRITERIA_TRACED",
        "each requirement's acceptance criteria point at a check or a declared gap",
        "medium",
        not findings,
        "A requirement states its own definition of done; a catalogue that never "
        "holds its gates against it is grading its own homework." if findings
        else summary,
        findings,
    )


def check_evidence_fail_closed() -> dict:
    """B-16: a gate must not pass while its evidence went unwritten.

    record_to_evidence_store() returned a returncode that reached
    print_gate_result() for display and nothing else. If the write to the
    Evidence Store failed, the pipeline carried on and could report PASS.
    For a control system whose whole premise is the tamper-evident chain,
    evidence that may be missing is not evidence.

    The drift detector already had this right — "Hard fail — evidence
    recording is mandatory" — so the two paths into the same table gave
    two different answers to the same question. As with B-04, the
    contradiction was only visible with both open side by side.

    The cost is named rather than avoided: an Evidence Store whose outage
    blocks every pipeline is a single point of failure. That is the
    correct trade for a compliance control system, and it is a decision,
    not an accident — which is why it is tested.
    """
    findings = []
    orch = read_text(REPO_ROOT / "pipeline" / "gate_orchestrator.py")

    if "_evidence_problem" not in orch:
        findings.append(
            "pipeline/gate_orchestrator.py: no evidence-failure handling — a "
            "failed Evidence Store write would pass unnoticed"
        )
    # The BRANCH, not merely the token. A first version of this check
    # searched for "evidence_broken" and kept passing when the branch was
    # replaced by `if False:` — the name still appeared at its assignment.
    # A check that a probe cannot break is not a check.
    if "if evidence_broken:" not in orch:
        findings.append(
            "pipeline/gate_orchestrator.py: nothing branches on evidence_broken, "
            "so the exit code cannot distinguish a blocked gate from an "
            "unrecorded one"
        )
    if "return 3" not in orch:
        findings.append(
            "pipeline/gate_orchestrator.py: no distinct exit code for a failed "
            "evidence write. Collapsing it into 1 lets a broken Evidence Store "
            "look like an ordinary gate failure"
        )
    if "evidence_recording_failed" not in orch:
        findings.append(
            "pipeline/gate_orchestrator.py: the pipeline report does not state "
            "whether evidence recording failed — an auditor reading it cannot "
            "tell a verdict from an absent verdict"
        )

    # The drift detector must keep its hard fail.
    drift = read_text(REPO_ROOT / "monitoring" / "drift_detector.py")
    if "sys.exit(1)" not in drift or "evidence recording is mandatory" not in drift:
        findings.append(
            "monitoring/drift_detector.py: no longer hard-fails on a failed "
            "evidence write — the two writers into quality_gate_results must "
            "answer this question the same way"
        )

    return make_result(
        "EVIDENCE_FAIL_CLOSED",
        "the fail-closed evidence path is declared (B-16; behaviour in "
        "pipeline/test_evidence_fail_closed.py)",
        "high",
        not findings,
        "A gate can report PASS while its evidence went unwritten — the chain the "
        "artefact rests on would have a hole nobody sees." if findings
        else "Both writers into the evidence table fail closed, and the exit code "
             "tells an unrecorded run from a blocked gate.",
        findings,
    )


def check_human_decision_takes_effect() -> dict:
    """T-16.1 (ES-1, ES-2), PO ES-F1 a of 02.10.2026: the human half of a
    HYBRID gate has an effect. Severity HIGH (PO 02.10.2026).

    Review 12 showed in a run that a rejection by the reviewer was recorded
    and the pipeline carried on, and that a HYBRID gate without any decision
    passed. The rule now lives in pipeline/human_decision.py, called by both
    runners. pipeline/test_human_decision.py proves the end-to-end effect by
    running it; this check holds the parts a later edit could quietly undo:

      1. the rule itself: no approval -> halt, rejection -> halt, an approval
         for another gate -> halt, an approval -> proceed (counter-check);
      2. the local orchestrator halts on it;
      3. no pipeline scenario runs a HYBRID gate as anything else — the
         relabelling bypass (poc_healthcare_pass ran G-DEP-03 as AUTO);
      4. the CI lists every HYBRID gate as HYBRID with an approval that
         exists, belongs to that gate and approves, records it, evaluates it
         into the ledger, and lets the verdict decide the Pipeline Decision;
      5. the behavioural test runs in make test and in negative-cases;
      6. the catalogue says so (ES-F3 a, PO 05.10.2026): every HYBRID gate
         declares the halt on its human decision as an implemented trigger,
         `when` names exactly the halt reasons of human_decision.py, `by`
         names the module — and no gate without a human half declares one.
         Built but undeclared understates the gate; declared on an AUTO gate
         claims a stop that never comes.
    """
    import importlib.util

    findings = []
    spec = importlib.util.spec_from_file_location(
        "human_decision", REPO_ROOT / "pipeline" / "human_decision.py")
    hd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hd)
    automation = hd.load_gate_automation()
    hybrid = sorted(g for g, a in automation.items() if a == "HYBRID")

    # 1. The rule.
    approval = {"gate_id": "G-PRE-05", "decision": "PASS", "reviewed_by": "R"}
    cases = [
        ("no approval", None, True, hd.AWAITING),
        ("rejection", dict(approval, decision="FAIL"), True, hd.REJECTED),
        ("approval for another gate", dict(approval, gate_id="G-PRE-01"), True, hd.INVALID),
        ("approval without a reviewer", dict(approval, reviewed_by=""), True, hd.INVALID),
        ("approval (counter-check)", approval, False, None),
    ]
    for label, log, halt, reason in cases:
        got = hd.approval_effect("G-PRE-05", "HYBRID", "PASS", log)
        if got["halt"] != halt or got["reason"] != reason:
            findings.append(
                f"pipeline/human_decision.py: {label} gives halt={got['halt']}, "
                f"reason={got['reason']} — expected halt={halt}, reason={reason}")

    # 2. The orchestrator halts on it.
    orch = read_text(REPO_ROOT / "pipeline" / "gate_orchestrator.py")
    if "human_decision.approval_effect(" not in orch:
        findings.append("pipeline/gate_orchestrator.py: does not evaluate the human "
                        "decision (human_decision.approval_effect)")
    if not re.search(r'elif human\["halt"\]:\s*\n(?:\s*#.*\n)*\s*pipeline_halted = True', orch):
        findings.append("pipeline/gate_orchestrator.py: no branch halts the run on the "
                        "human decision (elif human[\"halt\"]: pipeline_halted = True)")
    if "human_decision.catalogue_method(" not in orch:
        findings.append("pipeline/gate_orchestrator.py: takes a gate's method from the "
                        "scenario instead of the catalogue (human_decision.catalogue_method)")

    # 3. Scenarios: a HYBRID gate stays HYBRID.
    for f in sorted((REPO_ROOT / "pipeline" / "scenarios").glob("*.json")):
        for g in json.loads(read_text(f)).get("gates", []):
            want = automation.get(g.get("gate_id"))
            if want and str(g.get("method", "")).upper() != want:
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: {g.get('gate_id')} runs as "
                    f"{g.get('method')}, the gate definition says {want}")

    # 4. CI.
    wf_path = REPO_ROOT / ".github" / "workflows" / "gate-pipeline.yml"
    wf = read_text(wf_path)
    listed = {m.group(1): (m.group(2), m.group(3)) for m in re.finditer(
        r'"(G-[A-Z]+-\d+):R\d+:\$\{\{ steps\.[a-z0-9-]+\.outputs\.result \}\}:'
        r'(AUTO|HYBRID|MANUAL):([^"]*)"', wf)}
    fixtures = REPO_ROOT / "scenarios" / "healthcare-ambient-ai-scribe" / "fixtures"
    for gate, (method, log) in sorted(listed.items()):
        if automation.get(gate) and method != automation[gate]:
            findings.append(f"{wf_path.relative_to(REPO_ROOT)}: {gate} listed as {method}, "
                            f"the gate definition says {automation[gate]}")
    for gate in hybrid:
        if gate not in listed:
            findings.append(f"{wf_path.relative_to(REPO_ROOT)}: HYBRID gate {gate} is not "
                            f"in the evidence list — its human half is never evaluated")
            continue
        log = listed[gate][1]
        if not log:
            findings.append(f"{wf_path.relative_to(REPO_ROOT)}: {gate} has no approval — "
                            f"the CI run halts there (ES-F1 a)")
            continue
        path = fixtures / log
        if not path.is_file():
            findings.append(f"{wf_path.relative_to(REPO_ROOT)}: {gate} names {log}, "
                            f"which does not exist")
            continue
        body = json.loads(read_text(path))
        if body.get("gate_id") != gate or body.get("decision") != "PASS" \
                or not str(body.get("reviewed_by") or "").strip():
            findings.append(f"{path.relative_to(REPO_ROOT)}: not an approval of {gate} "
                            f"(gate_id {body.get('gate_id')!r}, decision "
                            f"{body.get('decision')!r}, reviewer {body.get('reviewed_by')!r})")
    for needle, what in [
        ("--method MANUAL", "the CI does not record the human decision as a MANUAL record"),
        ("pipeline/human_decision.py gate", "the CI does not evaluate the human decisions"),
        ("pipeline/human_decision.py verdict", "the CI has no verdict over the human decisions"),
        ('HUMAN="${{ steps.human.outputs.result }}"',
         "the Pipeline Decision does not read the human verdict"),
        ("pipeline/test_human_decision.py", "negative-cases does not run the behavioural test"),
    ]:
        if needle not in wf:
            findings.append(f"{wf_path.relative_to(REPO_ROOT)}: {what}")
    decision_block = wf.split('HUMAN="${{ steps.human.outputs.result }}"', 1)[-1][:400]
    if "ALL_PASS=false" not in decision_block:
        findings.append(f"{wf_path.relative_to(REPO_ROOT)}: the human verdict does not "
                        f"block the Pipeline Decision (ALL_PASS=false)")

    # 5. make test.
    if "test_human_decision.py" not in read_text(REPO_ROOT / "tests" / "test_all.py"):
        findings.append("tests/test_all.py: does not run pipeline/test_human_decision.py")

    # 6. The catalogue declares the effect (ES-F3 a).
    reasons = set(hd.HALT_REASONS)
    for f, gate in _load_gate_files():
        gate_id = gate.get("id", f.stem)
        human = [t for t in (gate.get("triggers") or [])
                 if reasons & {w.strip() for w in str(t.get("when", "")).split("|")}]
        rel = f.relative_to(REPO_ROOT)
        if automation.get(gate_id) != "HYBRID":
            if human:
                findings.append(f"{rel}: {gate_id} is {automation.get(gate_id)} but declares "
                                f"a halt on a human decision — it has no human half")
            continue
        if len(human) != 1:
            findings.append(f"{rel}: HYBRID gate {gate_id} declares {len(human)} triggers on "
                            f"its human decision, expected one (ES-F3 a)")
            continue
        t = human[0]
        when = {w.strip() for w in str(t.get("when", "")).split("|")}
        if t.get("effect") != "halt_pipeline" or t.get("implementation") != "implemented" \
                or when != reasons or "pipeline/human_decision.py" not in str(t.get("by", "")):
            findings.append(
                f"{rel}: {gate_id} trigger on the human decision is effect="
                f"{t.get('effect')!r}, implementation={t.get('implementation')!r}, "
                f"when={sorted(when)}, by={t.get('by')!r} — expected halt_pipeline, "
                f"implemented, when={sorted(reasons)}, by pipeline/human_decision.py")

    return make_result(
        "HUMAN_DECISION_TAKES_EFFECT",
        "a rejection by the reviewer and a missing approval halt the run (T-16.1, ES-F1 a)",
        "high",
        not findings,
        "A human decision on a HYBRID gate can be bypassed or has no effect — a "
        "rejected or unapproved gate would read as passed." if findings
        else f"{len(hybrid)} HYBRID gates: both runners halt on a rejection or a "
             f"missing approval; CI lists all {len(hybrid)} with their approval; "
             f"all {len(hybrid)} declare the halt as implemented (ES-F3 a).",
        findings,
    )


VALID_EFFECTS = ("halt_pipeline", "record_only", "open_incident",
                 "start_deadline", "notify")


def check_gate_declares_effect() -> dict:
    """Question 5: every gate must say what follows from its verdict.

    A gate produced a judgement and a record. What FOLLOWED from it —
    block the rollout, open an incident, start a deadline, notify someone
    — was written nowhere. The orchestrator halts on FAIL, but that is a
    property of the orchestrator, not a declared property of the gate.

    Where nothing is declared, imagination fills the gap. A draft article
    described an escalation cascade for G-OPS-02 because the gate is
    silent about its effect and a reporting duty without an effect would
    be pointless (B-13). The claim was the plausible inference from a
    blank.

    For Art. 26(5) this is not optional: the provision demands a
    CONSEQUENCE, not a verdict. A gate that can only say PASS/FAIL cannot
    represent that duty however well it checks.

    `declared_only` is the honest state for an effect that is intended
    and described but not built — the same move as
    policy_checks[].implementation. It is counted, not punished.
    """
    findings = []
    counts = {"implemented": 0, "declared_only": 0}

    for f, gate in _load_gate_files():
        gate_id = gate.get("id", f.stem)
        triggers = gate.get("triggers")
        if not triggers:
            findings.append(
                f"{f.relative_to(REPO_ROOT)}: declares no effect. A gate that "
                f"does not say what follows from its verdict leaves the reader "
                f"to guess, and readers guess generously"
            )
            continue

        for t in triggers:
            effect = t.get("effect")
            impl = t.get("implementation")
            if effect not in VALID_EFFECTS:
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: effect '{effect}' is not one of "
                    f"{VALID_EFFECTS}"
                )
                continue
            if impl not in ("implemented", "declared_only"):
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: effect '{effect}' has "
                    f"implementation '{impl}' — must be implemented or declared_only"
                )
                continue
            counts[impl] += 1
            if not (t.get("by") or "").strip():
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: effect '{effect}' names nothing "
                    f"that carries it out — an effect without a mechanism is a wish"
                )
            if impl == "declared_only" and not (t.get("rationale") or "").strip():
                findings.append(
                    f"{f.relative_to(REPO_ROOT)}: effect '{effect}' is declared_only "
                    f"without a rationale — an undocumented gap is "
                    f"indistinguishable from an overlooked one"
                )

    total = counts["implemented"] + counts["declared_only"]
    return make_result(
        "GATE_DECLARES_EFFECT",
        "every gate declares what follows from its verdict (Frage 5, B-13)",
        "medium",
        not findings,
        "A gate that does not state its effect invites the reader to invent one — "
        "which is exactly how an outward claim outran the catalogue." if findings
        else f"{counts['implemented']} of {total} declared effects are implemented, "
             f"{counts['declared_only']} are declared but not built.",
        findings,
    )


VALID_ROLE_SCOPES = {"provider", "deployer"}


def check_gate_role_scope_valid() -> dict:
    """SPEC-03 Abschnitt 7: every gate must carry a valid, non-empty role_scope.

    Without it the AI_ACT_ROLE filter in gate_orchestrator silently falls back
    to "deployer", which would hide a mis-scoped gate rather than surface it.
    """
    findings = []
    for f, gate in _load_gate_files():
        scope = gate.get("role_scope")
        if scope is None:
            findings.append(f"{f.relative_to(REPO_ROOT)}: role_scope is missing")
            continue
        if not isinstance(scope, list) or not scope:
            findings.append(f"{f.relative_to(REPO_ROOT)}: role_scope must be a non-empty list, got {scope!r}")
            continue
        invalid = [s for s in scope if str(s).lower() not in VALID_ROLE_SCOPES]
        if invalid:
            findings.append(
                f"{f.relative_to(REPO_ROOT)}: invalid role_scope entr(y/ies) {invalid} — "
                f"allowed: {sorted(VALID_ROLE_SCOPES)}"
            )

    return make_result(
        "GATE_ROLE_SCOPE_VALID",
        "every gate carries a valid role_scope (SPEC-03)",
        "medium",
        not findings,
        "A missing or invalid role_scope makes the AI_ACT_ROLE gate filter fall back silently." if findings
        else "All gates carry a valid role_scope.",
        findings,
    )


# Teil 7 des Handbuchs ist der Übergabepunkt: "wie es weitergeht". Diese Pfade
# tragen das, was die Reihenfolge dort verändern kann — Gates, Pipeline und die
# Aufträge, aus denen beides entsteht. Absichtlich schmal: Doku, Evidence Store
# und Tooling ändern sich, ohne dass die Roadmap dadurch falsch wird.
_ROADMAP_SUBSTANCE_PATHS = ("gate-definitions", "pipeline", "specs")
_ROADMAP_DOC = "HANDBUCH.md"


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True, text=True, timeout=30,
    )


def _roadmap_drift(doc: str, substance_paths: tuple[str, ...]) -> list[str] | None:
    """Commits that changed substance after `doc` was last touched.

    Returns None when git cannot answer — the caller must not read that as
    "nothing drifted".
    """
    head = _git("log", "-1", "--format=%H %ct", "--", doc)
    if head.returncode != 0 or not head.stdout.strip():
        return None

    doc_sha, doc_time = head.stdout.split()

    later = _git(
        "log", f"--since=@{doc_time}", "--format=%H\t%h\t%ad\t%s",
        "--date=short", "--", *substance_paths,
    )
    if later.returncode != 0:
        return None

    drift = []
    for line in later.stdout.splitlines():
        if not line.strip():
            continue
        sha, short, date, subject = line.split("\t", 3)
        # The commit that carried the document itself is not drift, and
        # --since is inclusive of its own second.
        if sha == doc_sha:
            continue
        drift.append(f"{short} {date} {subject}")
    return drift


def check_handbook_roadmap_is_current() -> dict:
    """The roadmap in HANDBUCH Teil 7 is younger than the work it orders.

    Teil 7 is the handover point of this project: whoever comes back after a
    pause reads it and knows what to do next. Nothing holds it to reality.
    It is maintained when the author thinks of it, and it was — on 03.09.2026
    it was the last commit of the session. A session that ends unplanned
    leaves a roadmap that describes a state the repository has left, and the
    next reader starts from it in good faith.

    That is the same failure as a stale count, one level up: AGENTS.md carried
    a gate inventory from before SPEC-01 while every session read it first
    (T-03). The fix there was a guardian, not a rule, and it is the fix here.

    The check does not read a date out of the prose. A date in the text is a
    second statement of the same fact and would need its own guardian. Git
    already knows when the handbook was last written and when the gates, the
    pipeline and the specifications last moved; the comparison is between
    those two, and there is nothing new to keep in sync.

    Severity is LOW on purpose, and that is a PO decision open to revision.
    Drift here is not a credibility defect — no claim is wrong, no evidence is
    overstated. It is a maintenance signal, and it appears mid-session by
    design: the moment a gate changes, the roadmap is behind until the session
    closes. A guard that turns the suite red while the work is still being
    done is a guard that gets skipped, and then it guards nothing.
    """
    drift = _roadmap_drift(_ROADMAP_DOC, _ROADMAP_SUBSTANCE_PATHS)

    if drift is None:
        return make_result(
            "HANDBOOK_ROADMAP_CURRENT",
            "the roadmap is younger than the work it orders (HANDBUCH Teil 7)",
            "low", False,
            "git could not be asked when the handbook and the substance last "
            "moved — a check that cannot run must not report success. A shallow "
            "clone is the usual reason.",
            ["git log returned nothing for HANDBUCH.md or for the substance paths."],
        )

    covered = ", ".join(_ROADMAP_SUBSTANCE_PATHS)
    return make_result(
        "HANDBOOK_ROADMAP_CURRENT",
        "the roadmap is younger than the work it orders (HANDBUCH Teil 7)",
        "low",
        not drift,
        f"{len(drift)} commit(s) changed {covered} after HANDBUCH.md was last "
        f"written. Teil 7 describes a state the repository has left, and it is "
        f"the first thing the next session reads." if drift
        else f"HANDBUCH.md is at least as young as the newest commit to {covered}.",
        drift,
    )


def check_legal_quotes_verbatim() -> dict:
    """Jedes Belegzitat der Deckungsanalyse steht wortgleich in seiner Quelle.

    SPEC-06 stellt den Pflichtenraum des AI Act auf: eine Zeile je Norm-Einheit,
    mit dem Wortlaut daneben. Der Wert dieser Analyse haengt an genau einer
    Eigenschaft — dass die Zitate echt sind. Ein Zitat, das jemand umformuliert,
    kuerzt oder aus dem Gedaechtnis ergaenzt, sieht in jedem Review richtig aus
    und traegt trotzdem eine Rechtsaussage, die der Text nicht hergibt.

    Deshalb traegt jede Zeile ihren Zeichen-Offset, und dieser Check laesst
    tools/legal/verify_norm_quotes.py die Quelle erneut lesen. Der Unterschied
    zu jedem anderen Waechter hier ist keiner: eine Behauptung wird gegen ihren
    Gegenstand gehalten. Neu ist nur, dass der Gegenstand ein Gesetzestext ist.

    Geprueft wird der Modus `belege` — Quell-Hash und Wortgleichheit. NICHT
    geprueft wird, ob die Analysefelder schon gefuellt sind: waehrend der
    Bearbeitung sind sie es nicht, und ein Waechter, der ueber Wochen rot steht,
    weil die Arbeit laeuft, wird abgeschaltet und schuetzt dann nichts. Die
    Vollstaendigkeit ist Definition of Done des Tickets, nicht Integritaet.

    HIGH, weil der Fehler unsichtbar ist und eine Rechtsaussage traegt. Ein
    falscher Zaehlstand laesst sich nachrechnen; ein erfundenes Zitat aus einer
    Verordnung glaubt der Leser, weil er den Text nicht danebenliegen hat.
    """
    raum = sorted((REPO_ROOT / "docs" / "coverage").glob("*.yaml"))
    if not raum:
        return make_result(
            "LEGAL_QUOTES_VERBATIM",
            "jedes Belegzitat der Deckungsanalyse steht wortgleich in seiner Quelle (SPEC-06)",
            "high", True,
            "Kein Pflichtenraum unter docs/coverage/ — nichts zu pruefen.",
        )

    script = REPO_ROOT / "tools" / "legal" / "verify_norm_quotes.py"
    findings = []
    geprueft = 0
    for datei in raum:
        out = subprocess.run(
            [sys.executable, str(script), str(datei), "--modus", "belege"],
            capture_output=True, text=True, timeout=120,
        )
        if out.returncode != 0:
            lines = [l.strip() for l in out.stdout.splitlines() if l.strip().startswith("-")]
            findings.append(
                f"{datei.relative_to(REPO_ROOT)}: {len(lines) or 'mehrere'} Belege stimmen "
                f"nicht mit der Quelle ueberein"
            )
            findings.extend(f"  {l}" for l in lines[:5])
        else:
            m = re.search(r"— (\d+) von (\d+)", out.stdout)
            geprueft += int(m.group(1)) if m else 0

    return make_result(
        "LEGAL_QUOTES_VERBATIM",
        "jedes Belegzitat der Deckungsanalyse steht wortgleich in seiner Quelle (SPEC-06)",
        "high",
        not findings,
        "Ein Belegzitat weicht von seiner Quelle ab — damit traegt eine Zeile des "
        "Pflichtenraums eine Rechtsaussage, die der Wortlaut nicht hergibt." if findings
        else f"{geprueft} Einheiten aus {len(raum)} Pflichtenraum-Datei(en) wortgleich "
             f"gegen ihre Quelle geprueft, Quell-Hash stimmt.",
        findings,
    )



def check_norm_unit_ids_unique() -> dict:
    """Jede Einheit eines Pflichtenraums hat eine Kennung, die es nur einmal gibt.

    T-14 (23.09.2026). Die Kennung ist der Anker, an dem alles andere haengt:
    ein Requirement zeigt auf 'Art. 26 Abs. 5', ein PO-Entscheid auf 'Art. 5
    Abs. 1 lit. c Ziff. i', ein Gate auf 'Art. 3 Nr. 49'. Bis T-14 trug der
    Pflichtenraum des AI Act 24 Kennungen doppelt (59 Zeilen) — 'Art. 3 lit. a'
    dreimal, 'Anhang VIII Nr. 1' dreimal —, weil der Extraktor Nummern,
    roemische Ziffern, zweite Buchstabenlisten und Anhangabschnitte nicht
    kannte. Eine Zuordnung auf eine solche Kennung zeigt auf mehrere Stellen
    zugleich und ist damit keine Zuordnung. Der Fehler faellt in keinem Review
    auf, weil jede einzelne Zeile richtig aussieht.

    Geprueft werden id UND uid. Die uid (Kennung@Offset) ist der technische
    Schluessel des Zusammenfuehrens; die id ist der Schluessel, den Menschen
    und andere Dateien benutzen. Beide muessen eindeutig sein.

    HIGH wie LEGAL_QUOTES_VERBATIM: der Fehler traegt eine Rechtszuordnung und
    ist ohne Maschine nicht zu sehen. Einstufung vom PO bestaetigt (23.09.2026).
    """
    from collections import Counter

    import yaml

    raum = sorted((REPO_ROOT / "docs" / "coverage").glob("*_pflichtenraum.yaml"))
    if not raum:
        return make_result(
            "NORM_UNIT_IDS_UNIQUE",
            "jede Einheit eines Pflichtenraums traegt eine eindeutige Kennung (T-14)",
            "high", True,
            "Kein Pflichtenraum unter docs/coverage/ — nichts zu pruefen.",
        )

    findings = []
    gesamt = 0
    for datei in raum:
        doc = yaml.safe_load(datei.read_text(encoding="utf-8")) or {}
        einheiten = doc.get("einheiten") or []
        gesamt += len(einheiten)
        for feld in ("id", "uid"):
            zaehlung = Counter(e.get(feld) for e in einheiten)
            doppelt = sorted(k for k, n in zaehlung.items() if n > 1)
            fehlend = zaehlung.get(None, 0)
            if fehlend:
                findings.append(f"{datei.relative_to(REPO_ROOT)}: {fehlend} Einheit(en) ohne {feld}")
            if doppelt:
                findings.append(
                    f"{datei.relative_to(REPO_ROOT)}: {len(doppelt)} {feld}(s) mehrfach — "
                    + ", ".join(str(k) for k in doppelt[:8])
                    + (" …" if len(doppelt) > 8 else "")
                )

    return make_result(
        "NORM_UNIT_IDS_UNIQUE",
        "jede Einheit eines Pflichtenraums traegt eine eindeutige Kennung (T-14)",
        "high",
        not findings,
        "Eine Kennung steht fuer mehrere Stellen — jede Zuordnung darauf ist "
        "mehrdeutig." if findings
        else f"{gesamt} Einheiten aus {len(raum)} Pflichtenraum-Datei(en), jede id "
             f"und jede uid genau einmal.",
        findings,
    )

def check_norm_sentence_units_current() -> dict:
    """Die Satzebene im Pflichtenraum ist genau die, die der PO gelistet hat.

    T-14.3 (28.09.2026). PO-Festlegung P-2 = b: nur Absaetze mit mehr als einer
    Pflicht werden in Saetze geschnitten, gelistet in docs/coverage/entscheide/satzebene.yaml.
    Anlass war Art. 26 Abs. 5 — vier Pflichten, ein Befund 'teilabdeckung', und
    die Pflicht, die Verwendung auszusetzen, war nirgends abgebildet.

    Die Liste ist eine Deklaration; dieser Check haelt sie gegen die Daten, in
    beiden Richtungen:
      * eine gelistete Einheit existiert nicht mehr als Ganzes, sondern als
        mindestens zwei Saetze — sonst ist der Sammelbefund zurueck, etwa nach
        einem Lauf des Builders ohne Liste;
      * jede Satz-Einheit gehoert zu einer gelisteten — sonst schneidet jemand
        feiner, als der PO entschieden hat, und die Befunde zerfallen ungefragt.

    HIGH (PO R-5, 30.09.2026; bis dahin MEDIUM, bestaetigt am 28.09.2026): fehlt
    die Satzebene, steht wieder ein Sammelbefund ueber dem Absatz, und eine Pflicht
    wie das Aussetzen nach Art. 26 Abs. 5 Satz 2 (Luecke) ist nicht zu sehen; traegt
    ein Satz den Text eines anderen, nennt die Zeile eine Pflicht, die ihr Beleg nicht
    traegt. Derselbe Schaden wie bei R-4.
    """
    import yaml

    titel = "die Satzebene der Pflichtenraeume ist genau die vom PO gelistete (T-14.3)"
    liste_pfad = REPO_ROOT / "docs" / "coverage" / "entscheide" / "satzebene.yaml"
    if not liste_pfad.exists():
        return make_result("NORM_SENTENCE_UNITS_CURRENT", titel, "high", True,
                           "Keine docs/coverage/entscheide/satzebene.yaml — keine Satzebene deklariert.")
    liste = (yaml.safe_load(liste_pfad.read_text(encoding="utf-8")) or {}).get("quellen") or {}

    raeume = {}
    for datei in sorted((REPO_ROOT / "docs" / "coverage").glob("*_pflichtenraum.yaml")):
        doc = yaml.safe_load(datei.read_text(encoding="utf-8")) or {}
        name = Path((doc.get("quelle") or {}).get("datei", "")).name
        raeume[name] = (datei, [e.get("id") or "" for e in doc.get("einheiten") or []])

    satz_muster = re.compile(r"^(?P<basis>.+?)(?: UAbs\. \d+)? Satz \d+(?P<nf> n\.F\.)?$")
    findings = []
    geschnitten = 0
    for quelle, eintraege in liste.items():
        if quelle not in raeume:
            findings.append(f"satzebene.yaml nennt {quelle}, dazu gibt es keinen Pflichtenraum")
            continue
        datei, ids = raeume[quelle]
        rel = datei.relative_to(REPO_ROOT)
        for eintrag in eintraege or []:
            ziel = eintrag.get("id", "")
            if ziel in ids:
                findings.append(f"{rel}: {ziel} steht noch als ganze Einheit — die Satzebene fehlt")
            saetze = [i for i in ids if (m := satz_muster.match(i))
                      and m.group("basis") + (m.group("nf") or "") == ziel]
            if len(saetze) < 2:
                findings.append(f"{rel}: {ziel} hat {len(saetze)} Satz-Einheit(en), erwartet mindestens 2")
            else:
                geschnitten += 1
    for quelle, (datei, ids) in raeume.items():
        gelistet = {e.get("id") for e in (liste.get(quelle) or [])}
        for i in ids:
            m = satz_muster.match(i)
            if m and m.group("basis") + (m.group("nf") or "") not in gelistet:
                findings.append(f"{datei.relative_to(REPO_ROOT)}: {i} ist auf Satzebene geschnitten, "
                                f"steht aber nicht in satzebene.yaml")

    # M-B2 (Review 07, umgesetzt in Paket 3 / Review 10): beim Schnitt auf Satzebene erbte
    # jeder Satz den pflicht-Text des ganzen Absatzes - 14 Saetze trugen eine Aussage, die
    # ihr Beleg nicht traegt. Zwei Saetze derselben Einheit duerfen nicht denselben Text haben.
    for datei in sorted((REPO_ROOT / "docs" / "coverage").glob("*_pflichtenraum.yaml")):
        doc = yaml.safe_load(datei.read_text(encoding="utf-8")) or {}
        texte: dict = {}
        for e in doc.get("einheiten") or []:
            m = satz_muster.match(e.get("id") or "")
            if m and (e.get("pflicht") or "").strip():
                texte.setdefault((m.group("basis") + (m.group("nf") or ""), e["pflicht"].strip()), []).append(e["id"])
        for (basis, _), satz_ids in texte.items():
            if len(satz_ids) > 1:
                findings.append(f"{datei.relative_to(REPO_ROOT)}: {', '.join(satz_ids)} tragen denselben "
                                f"pflicht-Text - ein Satz beschreibt nur, was sein Beleg sagt (M-B2)")

    return make_result(
        "NORM_SENTENCE_UNITS_CURRENT", titel, "high", not findings,
        "Pflichtenraum und PO-Liste der Satzebene weichen voneinander ab." if findings
        else f"{geschnitten} gelistete Einheit(en) auf Satzebene, keine Satz-Einheit ohne Listeneintrag.",
        findings,
    )


def check_po_decisions_applied() -> dict:
    """Der Pflichtenraum traegt genau die PO-Entscheide, die in docs/coverage/entscheide/ stehen.

    T-14.5 (28.09.2026). po_bestaetigt ist die Stelle, an der der Pflichtenraum
    sagt: das hat der PO entschieden. Ein `po_bestaetigt: true` sieht in jedem
    Diff richtig aus und bringt keinen Test zum Scheitern — dieselbe Lage wie
    bei den vier Ehrlichkeitsfeldern (AGENTS.md 3), und dieselbe Gefahr: eine
    KI, die eine Tabelle sauber abschliesst.

    Deshalb in beiden Richtungen:
      * jeder Entscheid einer Entscheidungsdatei steht so im Pflichtenraum —
        Felder, Beleg in po_entscheid, po_bestaetigt;
      * jede Zeile mit po_bestaetigt: true hat einen Entscheid mit
        bestaetigt: true. Eine Bestaetigung ohne Entscheid ist keine.

    Nebenbei faengt er, was ein Neuschnitt anrichtet: build_pflichtenraum.py
    setzt geerbte Zeilen auf po_bestaetigt: false — der Check meldet dann den
    Entscheid, der seine Zeile verloren hat.

    HIGH wie NORM_UNIT_IDS_UNIQUE: der Fehler traegt eine Rechtszuordnung und
    ist ohne Maschine nicht zu sehen. Einstufung vom PO bestaetigt (28.09.2026).
    """
    import importlib.util

    titel = "jede PO-Bestaetigung im Pflichtenraum hat ihren Entscheid, und jeder Entscheid steht dort (T-14.5)"
    pfad = REPO_ROOT / "tools" / "legal" / "po_entscheide.py"
    spec = importlib.util.spec_from_file_location("po_entscheide", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    befunde = modul.abweichungen(REPO_ROOT)
    soll = modul.erwartet(REPO_ROOT)
    bestaetigt = sum(1 for s in soll.values() if s["bestaetigt"])
    return make_result(
        "PO_DECISIONS_APPLIED", titel, "high", not befunde,
        f"{len(befunde)} Abweichung(en) zwischen Entscheidungsdateien und Pflichtenraum." if befunde
        else f"{len(soll)} entschiedene Zeilen stehen so im Pflichtenraum, {bestaetigt} davon bestaetigt; "
             f"keine Bestaetigung ohne Entscheid.",
        befunde[:12] + ([f"… und {len(befunde) - 12} weitere"] if len(befunde) > 12 else []),
    )


def check_omnibus_superseded_units_out() -> dict:
    """Eine vom Omnibus ersetzte Einheit der Grundfassung ist out, und ihre Neufassung ist bewertet.

    A-F2a (PO 29.09.2026, Review 08 Teil 7, umgesetzt in Paket 2 / Review 09).
    Bis dahin trugen AI-Act-Zeilen wie Art. 4 den Inhalt der Neufassung, ihr
    Beleg aber war der alte Wortlaut: die Aussage stand auf einem Text, der
    nicht mehr gilt, und die n.F.-Zeile im Omnibus-Raum zaehlte dieselbe Pflicht
    ein zweites Mal. Die Umsetzung ist eine Richtigstellung; dieser Check haelt
    sie (AGENTS.md 4, B-19):

      * jede Einheit, deren Text der Omnibus ersetzt oder streicht
        (fassung_2026_1744, gesetzt von tools/legal/link_omnibus.py), sagt in
        'neufassung', ob ganz ('ersetzt'), 'teilweise' oder 'gestrichen' —
        ein neuer Verweis ohne Einordnung faellt auf;
      * 'ersetzt' und 'gestrichen' sind out und tragen weder Befund noch Gate
        noch Requirement — die gehoeren an die n.F.-Zeile;
      * jede Neufassung, auf die eine ersetzte oder teilweise ersetzte
        Einheit verweist, ist bewertet (in/out) — sonst fiele die Pflicht aus
        der Zaehlung, genau der Grund, warum A-F2a nur zusammen mit Paket 2
        umgesetzt werden durfte;
      * keine Normverweisung eines Gates oder Requirements loest auf eine
        ersetzte oder gestrichene Einheit auf, sondern auf ihre Neufassung
        (tools/legal/resolve_norm_refs.py).

    HIGH, PO-Entscheid R-2 (29.09.2026, Review 09 Teil 6): eine unbewertete
    Neufassung ist eine unbekannte Luecke, und aus ihr wuerde der Pruef-Agent
    (Paket 9) ein falsches 'konform' machen. Vorgeschlagen war MEDIUM, weil kein
    Zitat falsch wird; das wiegt weniger als die falsche Konformitaetsaussage.
    """
    import importlib.util
    from collections import Counter

    import yaml

    titel = "eine vom Omnibus ersetzte Einheit ist out, und ihre Neufassung ist bewertet (A-F2a)"
    ai_pfad = REPO_ROOT / "docs" / "coverage" / "aiact_pflichtenraum.yaml"
    om_pfad = REPO_ROOT / "docs" / "coverage" / "omnibus_pflichtenraum.yaml"
    if not (ai_pfad.exists() and om_pfad.exists()):
        return make_result("OMNIBUS_SUPERSEDED_UNITS_OUT", titel, "high", False,
                           "Pflichtenraum AI Act oder Omnibus fehlt — der Check kann nicht laufen.", [])
    ai = (yaml.safe_load(ai_pfad.read_text(encoding="utf-8")) or {}).get("einheiten") or []
    om = (yaml.safe_load(om_pfad.read_text(encoding="utf-8")) or {}).get("einheiten") or []
    om_uid = {e.get("uid"): e for e in om}

    findings: list[str] = []
    zahl: Counter = Counter()
    abgeloest: set[str] = set()
    for e in ai:
        sid, verweis, art = e.get("id"), e.get("fassung_2026_1744") or [], e.get("neufassung")
        if verweis and art not in ("ersetzt", "teilweise", "gestrichen"):
            findings.append(f"{sid}: der Omnibus ersetzt oder streicht Text dieser Einheit "
                            f"({', '.join(v.split('@')[0] for v in verweis)}), neufassung ist {art!r} "
                            f"— ganz, teilweise oder gestrichen?")
            continue
        if art and not verweis:
            findings.append(f"{sid}: neufassung '{art}' ohne Verweis fassung_2026_1744")
            continue
        if not art:
            continue
        zahl[art] += 1
        if art in ("ersetzt", "gestrichen"):
            abgeloest.add(sid)
            if e.get("scope") != "out":
                findings.append(f"{sid}: {art} durch den Omnibus, aber scope '{e.get('scope')}' — die Aussage "
                                f"stuende auf einem Wortlaut, der nicht mehr gilt (A-F2a)")
            if e.get("befund") or e.get("gate") or e.get("requirement"):
                findings.append(f"{sid}: {art}, traegt aber noch Befund, Gate oder Requirement — "
                                f"das gehoert an die Neufassung")
        for v in verweis:
            ziel = om_uid.get(v)
            if ziel is None:
                findings.append(f"{sid}: fassung_2026_1744 nennt {v}, im Omnibus-Pflichtenraum nicht vorhanden")
            elif art != "gestrichen" and ziel.get("scope") not in ("in", "out"):
                findings.append(f"{sid}: die Neufassung {ziel.get('id')} ist nicht bewertet — "
                                f"die Pflicht fiele aus der Zaehlung")

    pfad = REPO_ROOT / "tools" / "legal" / "resolve_norm_refs.py"
    spec = importlib.util.spec_from_file_location("resolve_norm_refs", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    for r in modul.aufloesen(REPO_ROOT):
        if r["ref"] in abgeloest and r["aufloesung"] != "n.F.":
            findings.append(f"{r['datei']}: {r['traeger']}{'/' + r['check'] if r['check'] else ''} "
                            f"'{r['ref']}' loest als '{r['aufloesung']}' auf eine abgeloeste Einheit auf, "
                            f"nicht auf ihre Neufassung")

    return make_result(
        "OMNIBUS_SUPERSEDED_UNITS_OUT", titel, "high", not findings,
        f"{len(findings)} Befund(e) zu vom Omnibus abgeloesten Einheiten." if findings
        else (f"{sum(zahl.values())} Einheiten mit Neufassung eingeordnet: "
              + " · ".join(f"{k} {n}" for k, n in sorted(zahl.items()))
              + "; ersetzte und gestrichene sind out, jede Neufassung ist bewertet."),
        findings[:12] + ([f"… und {len(findings) - 12} weitere"] if len(findings) > 12 else []),
    )


def check_coverage_finding_names_checking_gate() -> dict:
    """Eine Teilabdeckung oder Deckung nennt ein pruefendes Gate; ein Nachbar ist keins.

    M1a (PO 30.09.2026, Review 07 Frage M1, Review 09 Teil 7) mit M2a (29.09.2026):
    Teilabdeckung nur, wenn eine Regel mindestens ein Element der Pflicht selbst
    prueft. Ein Gate, das nur etwas Verwandtes prueft, steht in 'nachbar_gate',
    und die Pflicht ist eine Luecke. Neun Zeilen trugen bis dahin 'teilabdeckung'
    auf der Grundlage eines Nachbarn - ein verwandter Check 'deckte' eine Pflicht,
    die er nicht prueft, und der Pruef-Agent (Paket 9) haette daraus 'teilweise
    geprueft' gemacht.

    Der Check haelt, was die Daten allein sagen koennen:
      * eine in-Zeile mit Befund 'gedeckt' oder 'teilabdeckung' nennt mindestens
        ein Gate in 'gate';
      * kein Gate steht zugleich in 'gate' und 'nachbar_gate';
      * jedes genannte Gate gibt es in gate-definitions/.
    Ob ein Gate in 'gate' wirklich ein Element prueft, haelt seit Paket 3b
    ELEMENT_MATRIX_DERIVES_GATE am Rego-Code (Review 11).

    HIGH aus demselben Grund wie OMNIBUS_SUPERSEDED_UNITS_OUT (R-2): der Fehler
    macht aus einer Luecke eine scheinbare Pruefung. Einstufung vom PO bestaetigt
    (R-3, 30.09.2026).
    """
    import yaml

    titel = "eine Teilabdeckung oder Deckung nennt ein pruefendes Gate, ein Nachbar ist keins (M1a)"
    gate_ids = set()
    getrackt = _tracked_files()
    for datei in (REPO_ROOT / "gate-definitions").rglob("*.yaml"):
        if "template" in datei.name or (getrackt and str(datei.relative_to(REPO_ROOT)) not in getrackt):
            continue  # was ein Klon nicht enthaelt, zaehlt nicht (A-W8)
        doc = yaml.safe_load(datei.read_text(encoding="utf-8")) or {}
        if isinstance(doc.get("id"), str):
            gate_ids.add(doc["id"])

    findings: list[str] = []
    geprueft = 0
    for name in ("aiact", "omnibus"):
        pfad = REPO_ROOT / "docs" / "coverage" / f"{name}_pflichtenraum.yaml"
        if not pfad.exists():
            continue
        for e in (yaml.safe_load(pfad.read_text(encoding="utf-8")) or {}).get("einheiten") or []:
            gates, nachbarn = e.get("gate") or [], e.get("nachbar_gate") or []
            if e.get("scope") == "in" and e.get("befund") in ("gedeckt", "teilabdeckung"):
                geprueft += 1
                if not gates:
                    findings.append(f"{name}: {e.get('id')} — Befund '{e.get('befund')}' ohne pruefendes Gate "
                                    f"(Nachbarn: {', '.join(nachbarn) or 'keine'}); nach M1a ist das eine Luecke")
            for g in sorted(set(gates) & set(nachbarn)):
                findings.append(f"{name}: {e.get('id')} — {g} steht in gate und nachbar_gate")
            for g in gates + nachbarn:
                if g not in gate_ids:
                    findings.append(f"{name}: {e.get('id')} — Gate {g} gibt es in gate-definitions/ nicht")

    return make_result(
        "COVERAGE_FINDING_NAMES_CHECKING_GATE", titel, "high", not findings,
        f"{len(findings)} Befund(e) zu Gate-Angaben im Pflichtenraum." if findings
        else f"{geprueft} gedeckte oder teilweise gedeckte Zeilen nennen je ein pruefendes Gate; "
             f"kein Nachbar zugleich als Pruefer, kein unbekanntes Gate.",
        findings[:12] + ([f"… und {len(findings) - 12} weitere"] if len(findings) > 12 else []),
    )


def check_element_matrix_derives_gate() -> dict:
    """'gate' und 'nachbar_gate' sind aus der Element-Matrix abgeleitet, und die Matrix aus dem Code.

    Paket 3b (30.09.2026, Review 11): Element-Matrix Lauf 2 als Daten
    (docs/coverage/matrix/element_matrix.yaml), PO-Entscheide M2a (29.09.) und M1a (30.09.).
    Bis dahin war 'gate' von Hand gesetzt und nannte Pruefer, Nachbarn und Ziele
    durcheinander: Art. 26 Abs. 7 trug G-DEP-03, obwohl keine Regel die Unterrichtung
    der Arbeitnehmer prueft; Art. 25 Abs. 2 lit. a-c n.F. trugen 'teilabdeckung', weil
    C-25d einen Uebergabebeleg verlangt - hineingesehen hat keine Regel.
    COVERAGE_FINDING_NAMES_CHECKING_GATE sah beides nicht: ein Gate stand da, und es
    gab es.

    Drei Richtungen:
      * Matrix -> Code: jede genannte Regel (Gate, Check, Feld) gibt es - der Check ist
        implementiert, und eine Regel dieses Gates und Checks liest das Feld (OPA-AST,
        tools/rego_inputs.py). Liest die Regel das Feld nicht mehr, ist die Matrix falsch.
      * Matrix -> Pflichtenraum: gate, nachbar_gate und die Befundklasse (M1a: kein
        Element geprueft = Luecke; alle geprueft und Kette geschlossen = gedeckt; sonst
        Teilabdeckung) stimmen mit der Zeile ueberein.
      * Pflichtenraum -> Matrix: eine Zeile ohne Matrix-Eintrag traegt kein gate, kein
        nachbar_gate und ist weder gedeckt noch Teilabdeckung.
    Ausgenommen sind Zeilen unter Vorbehalt einer Frage, die im Entscheidungsregister
    offen steht (F4); sie werden mit dem abgeleiteten Befund gemeldet.

    Braucht opa auf PATH (wie make test-rego). Ohne opa kann die Matrix nicht gegen den
    Code gehalten werden - das ist ein Befund, kein Uebersprung.

    HIGH (PO R-6, 01.10.2026), aus demselben Grund wie R-3: ein Gate in 'gate', das kein
    Element prueft, macht aus einer Luecke eine scheinbare Pruefung.
    """
    import shutil
    import sys as _sys

    titel = "gate und nachbar_gate sind aus der Element-Matrix abgeleitet, und die Matrix haelt am Rego-Code (M2a, M1a)"
    if shutil.which("opa") is None:
        return make_result(
            "ELEMENT_MATRIX_DERIVES_GATE", titel, "high", False,
            "opa ist nicht auf PATH - die Element-Matrix kann nicht gegen den Rego-Code gehalten werden.",
        )
    _sys.path.insert(0, str(REPO_ROOT / "tools" / "legal"))
    import element_matrix as mx  # noqa: E402

    befunde, zahl = mx.pruefen(REPO_ROOT, getrackt=_tracked_files())
    vorbehalt = zahl["vorbehalt"]
    return make_result(
        "ELEMENT_MATRIX_DERIVES_GATE", titel, "high", not befunde,
        f"{len(befunde)} Befund(e) zwischen Element-Matrix, Rego-Code und Pflichtenraum." if befunde
        else (f"{zahl['zeilen']} Zeilen, {zahl['elemente']} Elemente, {zahl['regeln']} Regelangaben am "
              f"OPA-AST bestaetigt; {zahl['abgeleitet']} Zeilen tragen genau ihr abgeleitetes gate, "
              f"nachbar_gate und ihre Befundklasse, {len(vorbehalt)} unter Vorbehalt."),
        (befunde[:12] + ([f"… und {len(befunde) - 12} weitere"] if len(befunde) > 12 else []))
        + [f"Vorbehalt: {v}" for v in vorbehalt],
    )


def check_norm_units_match_extractor() -> dict:
    """Jeder Pflichtenraum ist genau das, was der Extraktor heute aus seiner Quelle schneidet.

    T-15 (30.09.2026, Review 10). Vier Schnittfehler waren seit Paket 1 bekannt
    (A-W1 Art. 113 ohne Absatznummern, A-W2 Anhang I Abschn. B ungeteilt, A-W3
    Fusszeile im Beleg, A-W7 Omnibus Abs. 1b und Art. 75b), ein fuenfter fiel beim
    Beheben auf (A-W9: Kapitel- und Abschnittsueberschriften im Beleg des letzten
    Glieds davor, 53 Einheiten in AI Act, DSGVO und NIS2). Keine Pruefung sah sie:
    LEGAL_QUOTES_VERBATIM haelt nur, dass der Beleg an seinem Offset steht - auch
    eine Ueberschrift steht dort.

    Zwei Richtungen:
      * die Einheiten jedes Raums (uid = Kennung@Offset) sind genau die, die
        extract_norm_units.py bzw. extract_omnibus_units.py samt Satzebene heute
        liefern - ein Extraktor, der sich aendert, ohne dass der Raum neu gebaut
        wird, faellt auf, und ein Raum, der von Hand geschnitten wird, auch;
      * kein Beleg eines Artikels traegt eine Kapitel- oder Abschnittsueberschrift
        auf eigener Zeile, keiner die Fusszeile des Amtsblatts - faellt die Grenze
        im Extraktor weg, bleibt die erste Richtung nach einem Neubau gruen, diese
        nicht.

    Dritte Richtung (A-W13, Review 11, 01.10.2026): der Schnitt kommt auch in der Aussage
    an. T-15 Teil 2 (A-W11) schnitt Unterabsaetze aus dem letzten Glied einer Aufzaehlung,
    zog dessen Pflichttext aber nicht nach - M-B2 galt nur fuer Saetze. 19 Glieder nannten
    weiter den Unterabsatz, der jetzt eine eigene Zeile ist, darunter Art. 25 Abs. 2 lit. c
    n.F. ("Dieser Absatz gilt nicht in Faellen ..." - die Ausnahme von UAbs. 4). Maschinell
    pruefbar ist der woertliche Rest: der Pflichttext der Einheit direkt vor einem
    Unterabsatz nennt nicht dessen erste drei Woerter, wenn ihr eigener Beleg sie nicht
    enthaelt. Umschriebene Reste haelt das nicht; die Texte haelt PO_DECISIONS_APPLIED,
    sobald der PO sie bestaetigt hat.

    HIGH (PO R-4, 30.09.2026; vorgeschlagen war MEDIUM, weil kein Zitat gefaelscht
    wird): ein veralteter Schnitt kann eine Pflicht verstecken. Bis T-15 stand die
    Profiling-Regel (Art. 6 Abs. 3 UAbs. 3) im Beleg von lit. d und Art. 9 Abs. 5
    UAbs. 3 in dem von lit. c - die Zeile traegt dann Befund und scope eines anderen
    Glieds, und die Lage sieht vollstaendiger aus, als sie ist. Derselbe Schaden wie
    bei R-2 und R-3.
    """
    import sys as _sys

    import yaml

    titel = "jeder Pflichtenraum ist genau das, was der Extraktor heute schneidet (T-15, A-W13)"
    _sys.path.insert(0, str(REPO_ROOT / "tools" / "legal"))
    import extract_norm_units as ex  # noqa: E402
    from extract_omnibus_units import omnibus_units  # noqa: E402

    satz = REPO_ROOT / "docs" / "coverage" / "entscheide" / "satzebene.yaml"
    liste = ((yaml.safe_load(satz.read_text(encoding="utf-8")) or {}).get("quellen") or {}) if satz.exists() else {}
    ueberschrift = re.compile(r"\n(?:KAPITEL [IVXLC]+|ABSCHNITT \d+|Abschnitt \d+|TITEL [IVXLC]+)\n")
    fuss = re.compile(r"\nELI: http")
    aufzaehlung = re.compile(r"^(?:\(\d+[a-z]?\)|\d+[a-z]?\.|[a-z]{1,2}\)|\([a-z]{1,2}\)|[ivx]+\))\s*")

    def _woerter(text: str) -> list[str]:
        return re.findall(r"[\wÄÖÜäöüß%-]+", text or "")

    findings: list[str] = []
    geprueft = 0
    for pfad in sorted((REPO_ROOT / "docs" / "coverage").glob("*_pflichtenraum.yaml")):
        doc = yaml.safe_load(pfad.read_text(encoding="utf-8")) or {}
        quelle = REPO_ROOT / (doc.get("quelle") or {}).get("datei", "")
        if not quelle.is_file():
            findings.append(f"{pfad.name}: Quelle {quelle} fehlt")
            continue
        _, norm, _ = ex.load(quelle)
        if pfad.name.startswith("omnibus_"):
            einheiten, _ = omnibus_units(norm)
        else:
            arts = ex.index_articles(norm) + ex.index_paragraphen(norm) + ex.index_anhaenge(norm)
            einheiten = [u for a in arts for u in ex.units_for(norm, a)]
        ids = [x["id"] for x in (liste.get(quelle.name) or [])]
        if ids:
            einheiten, _ = ex.auf_satzebene(norm, einheiten, ids)
        soll = {u["uid"] for u in einheiten}
        ist = {e.get("uid") for e in doc.get("einheiten") or []}
        for u in sorted(ist - soll)[:5]:
            findings.append(f"{pfad.name}: {u} steht im Raum, der Extraktor schneidet sie nicht (mehr)")
        for u in sorted(soll - ist)[:5]:
            findings.append(f"{pfad.name}: {u} schneidet der Extraktor, im Raum fehlt sie")
        for e in doc.get("einheiten") or []:
            geprueft += 1
            span = norm[e["offset"]:e["offset"] + e["laenge"]]
            if not str(e.get("id", "")).startswith("Anhang") and ueberschrift.search(span):
                findings.append(f"{pfad.name}: {e['id']} — Beleg traegt eine Kapitel- oder Abschnittsueberschrift")
            if fuss.search(span):
                findings.append(f"{pfad.name}: {e['id']} — Beleg traegt die Fusszeile des Amtsblatts")
        folge = sorted(doc.get("einheiten") or [], key=lambda x: x["offset"])
        for vor, nach in zip(folge, folge[1:]):
            if "UAbs." not in str(nach.get("id", "")):
                continue
            kopf = " ".join(_woerter(aufzaehlung.sub("", nach.get("beleg") or ""))[:3])
            if kopf and kopf in " ".join(_woerter(vor.get("pflicht") or "")) \
                    and kopf not in " ".join(_woerter(vor.get("beleg") or "")):
                findings.append(f"{pfad.name}: {vor['id']} — Pflichttext nennt den Unterabsatz "
                                f"{nach['id']} ('{kopf} …'), der eine eigene Einheit ist (A-W13)")

    return make_result(
        "NORM_UNITS_MATCH_EXTRACTOR", titel, "high", not findings,
        f"{len(findings)} Befund(e) zwischen Extraktor und Pflichtenraeumen." if findings
        else f"{geprueft} Einheiten in allen Raeumen sind genau der heutige Schnitt ihrer Quelle; "
             f"kein Beleg traegt Ueberschrift oder Fusszeile, kein Pflichttext den Unterabsatz danach.",
        findings[:12] + ([f"… und {len(findings) - 12} weitere"] if len(findings) > 12 else []),
    )


def check_in_units_own_duty_text() -> dict:
    """Jede `in`-Zeile traegt einen eigenen, vollstaendigen Pflichttext (P4-B1, Review 13).

    Der PO bestaetigt in Paket 4 die `in`-Zeilen (IN-1) und ihre Texte (wie P3-F2,
    P3-F5). Bestaetigen kann er nur, was dasteht. Gemessen am 05.10.2026 standen
    24 `in`-Zeilen ohne eigenen Text da: 11 ohne jeden Text (Anhang III Nr. 2,
    zehn Omnibus-Neufassungen), 12 mit einem Sammeltext, den sich mehrere Zeilen
    teilten (Art. 3 Nr. 4/8/23 'Definiert Kernbegriffe Nr. 1-44 ...', Art. 13 Abs. 3
    lit. b Ziff. i-iv und v-vii je ein Text), und Art. 3 Nr. 49 mit dem Text der
    Nummern 45 lit. b bis 48 ('Strafverfolgungsbehoerde ...') - ausgerechnet die
    Definition, auf die G-OPS-02 seine Meldeschwelle stuetzt. Dazu ein Text, der
    mit '…' abbrach (Art. 4a Abs. 2 lit. a n.F.).

    Geprueft wird je Raum, maschinell:
      * der Pflichttext einer `in`-Zeile ist nicht leer,
      * keine andere Zeile desselben Raums (`in` oder `out`) traegt denselben Text,
      * er endet nicht mit einem Auslassungszeichen.
    Ob der Text sagt, was sein Beleg sagt, prueft das nicht - das ist die
    Sammelbestaetigung des PO, danach haelt PO_DECISIONS_APPLIED den Text.

    MEDIUM (PO R-7, 05.10.2026): eine Zeile ohne eigenen Text versteckt keine
    Pflicht - scope und Befund stehen -, aber ihre Bestaetigung bestaetigt nichts.
    """
    import yaml
    from collections import Counter

    titel = "jede in-Zeile traegt einen eigenen, vollstaendigen Pflichttext (P4-B1)"
    findings: list[str] = []
    gezaehlt = 0
    for pfad in sorted((REPO_ROOT / "docs" / "coverage").glob("*_pflichtenraum.yaml")):
        einheiten = (yaml.safe_load(pfad.read_text(encoding="utf-8")) or {}).get("einheiten") or []
        texte = Counter(str(e.get("pflicht") or "").strip() for e in einheiten)
        for e in einheiten:
            if e.get("scope") != "in":
                continue
            gezaehlt += 1
            text = str(e.get("pflicht") or "").strip()
            if not text:
                findings.append(f"{pfad.name}: {e['id']} — kein Pflichttext")
            elif texte[text] > 1:
                findings.append(f"{pfad.name}: {e['id']} — Pflichttext teilt sich die Zeile mit "
                                f"{texte[text] - 1} anderen ('{text[:50]} …')")
            elif text.endswith(("…", "...")):
                findings.append(f"{pfad.name}: {e['id']} — Pflichttext bricht ab ('… {text[-40:]}')")

    return make_result(
        "IN_UNITS_OWN_DUTY_TEXT", titel, "medium", not findings,
        f"{len(findings)} in-Zeile(n) ohne eigenen, vollstaendigen Pflichttext - bestaetigen "
        f"kann der PO nur, was dasteht." if findings
        else f"{gezaehlt} in-Zeilen in allen Raeumen, jede mit eigenem, vollstaendigem Pflichttext.",
        findings[:12] + ([f"… und {len(findings) - 12} weitere"] if len(findings) > 12 else []),
    )


def check_requirement_anchor_declared() -> dict:
    """Ein Requirement nennt seinen gesetzlichen Anker - oder sagt, warum es keinen hat (Q1 b, F4).

    Review 05 (Q1) fand R012 mit dem Anker Art. 27, obwohl Art. 27 Abs. 1 Systeme aus
    Anhang III Nr. 2 ausnimmt - der Referenzfall Redispatch schuldet keine FRIA. Der PO hat
    am 05.10.2026 entschieden (Q1 b): MUST bleibt, als interne Vorgabe ohne Art.-27-Anker.
    Eine interne Vorgabe, die einen Artikel zitiert, sieht aus wie Gesetz; ein Pruef-Agent,
    der eu_ai_act_refs liest, wuerde daraus eine gesetzliche Pflicht machen.

    Geprueft:
      * `anker` ist leer, `offen` (F4: Betreiber-Anker gesucht) oder `intern` (Q1 b), und
        ein gesetzter `anker` hat einen `anker_grund`;
      * ein Requirement ohne eu_ai_act_refs traegt `anker` - wer keine Norm nennt, sagt warum;
      * `anker: intern` hat keine eu_ai_act_refs, und ein Gate, das nur interne Requirements
        traegt, zitiert weder in links.eu_ai_act_refs noch in legal_refs eines Checks eine Norm.
    Ob ein genannter Anker traegt, prueft das nicht - das ist AN-1 (Paket 5).

    MEDIUM (Vorschlag, R-8 offen): eine interne Vorgabe mit Gesetzeszitat erzeugt kein
    falsches 'konform', aber eine falsche Rechtsbehauptung nach aussen.
    """
    import yaml

    titel = "ein Requirement nennt seinen Anker oder sagt, warum es keinen hat (Q1 b)"
    findings: list[str] = []
    reqs: dict[str, dict] = {}
    for f in sorted((REPO_ROOT / "requirements").glob("R0*.yaml")):
        r = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        rid = r.get("id", f.stem)
        reqs[rid] = r
        anker = r.get("anker")
        refs = r.get("eu_ai_act_refs") or []
        rel = f.relative_to(REPO_ROOT)
        if anker not in (None, "offen", "intern"):
            findings.append(f"{rel}: anker '{anker}' ist weder offen noch intern")
        if anker and not str(r.get("anker_grund") or "").strip():
            findings.append(f"{rel}: anker '{anker}' ohne anker_grund")
        if not refs and not anker:
            findings.append(f"{rel}: keine eu_ai_act_refs und kein anker - ohne Norm und ohne Grund")
        if anker == "intern" and refs:
            findings.append(f"{rel}: anker intern, nennt aber eu_ai_act_refs {refs} - eine interne "
                            f"Vorgabe mit Gesetzeszitat sieht aus wie Gesetz")
    intern = {rid for rid, r in reqs.items() if r.get("anker") == "intern"}
    gates_intern = 0
    for f, gate in _load_gate_files():
        traeger = (gate.get("links") or {}).get("requirements") or []
        if not traeger or not set(traeger) <= intern:
            continue
        gates_intern += 1
        rel = f.relative_to(REPO_ROOT)
        if (gate.get("links") or {}).get("eu_ai_act_refs"):
            findings.append(f"{rel}: traegt nur interne Requirements {traeger}, zitiert aber "
                            f"links.eu_ai_act_refs {gate['links']['eu_ai_act_refs']}")
        for c in gate.get("policy_checks") or []:
            if c.get("legal_refs"):
                findings.append(f"{rel}: {c.get('id')} zitiert legal_refs {c['legal_refs']}, das Gate "
                                f"traegt nur interne Requirements {traeger}")

    return make_result(
        "REQUIREMENT_ANCHOR_DECLARED", titel, "medium", not findings,
        f"{len(findings)} Befund(e): ein Requirement oder Gate behauptet einen Anker, den es nicht hat, "
        f"oder verschweigt, dass es keinen hat." if findings
        else f"{len(reqs)} Requirements: {sum(1 for r in reqs.values() if not r.get('anker'))} mit Anker, "
             f"{sum(1 for r in reqs.values() if r.get('anker') == 'offen')} Anker offen, "
             f"{len(intern)} intern ohne Gesetzeszitat; {gates_intern} Gate(s) nur intern, ohne Normverweis.",
        findings,
    )


def check_norm_refs_resolve() -> dict:
    """Jede Normverweisung eines Gates oder Requirements zeigt auf eine Einheit des Pflichtenraums.

    T-14.4 (28.09.2026), Befund T4. LEGAL_QUOTES_VERBATIM prueft die Richtung
    Pflichtenraum -> Quelle. Die Richtung Gate -> Pflichtenraum pruefte niemand:
    G-OPS-02 berief sich bis zum 28.09.2026 auf 'Art. 3 Abs. 49', eine Stelle,
    die es nicht gibt — Art. 3 zaehlt in Nummern, gemeint war Nr. 49. Der String
    sah plausibel aus, und genau deshalb fiel er in keinem Review auf.

    Aufgeloest wird genau, als Neufassung (Omnibus, 'n.F.') oder als
    Oberbegriff vorhandener Einheiten ('Art. 15', 'Art. 26 Abs. 5' seit
    T-14.3); die Logik steht in tools/legal/resolve_norm_refs.py, das auch die
    volle Liste fuer den PO druckt. Ob eine aufgeloeste Stelle eine
    Betreiberpflicht ist, prueft dieser Check NICHT — das ist Auslegung und
    Sache des PO (2b, Teil 4); gemeldet wird nur die Verteilung nach scope.

    INFO: laut T-14 DoD 6 zunaechst Warnung; nach Sichtung der Liste vom PO so
    bestaetigt (28.09.2026). Der Befund steht in jeder Ausgabe, ohne den Build
    anzuhalten.
    """
    import importlib.util
    from collections import Counter

    titel = "jede Normverweisung der Gates und Requirements loest auf eine Einheit auf (T-14.4)"
    pfad = REPO_ROOT / "tools" / "legal" / "resolve_norm_refs.py"
    spec = importlib.util.spec_from_file_location("resolve_norm_refs", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    erg = modul.aufloesen(REPO_ROOT)

    offen = [e for e in erg if e["aufloesung"] in ("offen", "gestrichen")]
    findings = [
        f"{e['datei']}: {e['traeger']}{'/' + e['check'] if e['check'] else ''} "
        f"{e['schluessel']} '{e['ref']}' — "
        + ("vom Omnibus gestrichen" if e["aufloesung"] == "gestrichen" else "keine Einheit im Pflichtenraum")
        for e in offen
    ]
    verschieden = {e["ref"]: e for e in erg}
    scope = Counter(str(e["scope"]) for e in verschieden.values() if e["scope"])
    return make_result(
        "NORM_REFS_RESOLVE", titel, "info", not findings,
        (f"{len(offen)} von {len(erg)} Verweisungen zeigen ins Leere." if findings
         else f"{len(erg)} Verweisungen ({len(verschieden)} verschiedene) loesen auf.")
        + " Aufgeloeste nach scope: "
        + " · ".join(f"{k} {n}" for k, n in sorted(scope.items())) + ".",
        findings,
    )


_REVIEW_DIR = REPO_ROOT / "docs" / "coverage" / "review"
_REGISTER = "entscheidungsregister.md"
_DECISION_HEADERS = {
    ("#", "Entscheidung", "Optionen"),
    ("#", "Entscheidung", "Empfehlung"),
    ("#", "Frage", "Optionen"),
    ("#", "Befund", "Wohin"),
}
_REGISTER_HEADER = ("ID", "Gegenstand", "Quelle", "Stand", "Paket")
_REGISTER_STAENDE = ("offen", "vertagt", "entschieden", "umgesetzt", "außerhalb")
_REGISTER_PAKETE = {str(n) for n in range(1, 10)} | {"T-13", "T-16", "jederzeit"}  # T-16: Review 12, PO 02.10.2026


def _md_tables(text: str) -> list[tuple[tuple[str, ...], list[list[str]]]]:
    """Every pipe table in a Markdown text as (header cells, body rows)."""
    def cells(line: str) -> list[str]:
        return [c.strip() for c in line.strip().strip("|").split("|")]

    tables, lines, i = [], text.splitlines(), 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header, rows, j = tuple(cells(lines[i])), [], i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append(cells(lines[j]))
                j += 1
            tables.append((header, rows))
            i = j
        else:
            i += 1
    return tables


def check_po_decisions_registered() -> dict:
    """Jede Frage an den PO und jeder Befund mit Ziel steht im Entscheidungsregister.

    PO 29.09.2026: "ich hoffe, wir vergessen keinen Schritt und keine
    Entscheidung". Die Entscheidungen standen in neun Reviews, jede in ihrer
    eigenen Tabelle, und zwei beschlossene Zwischenschritte (F4a: Requirements
    als `anker: offen` kennzeichnen, F5a: Vermerk HYPOTHESE in G-OPS-02) waren
    einen Tag nach dem Entscheid nirgends umgesetzt. Beide Male stand der
    Entscheid im Review, und niemand fragte ihn wieder ab.

    Das Register sammelt alles an einer Stelle; dieser Check haelt es
    vollstaendig, in beiden Richtungen:
      * jede Zeile einer Entscheidungs- oder Befundtabelle eines Reviews
        (`| # | Entscheidung | Optionen |`, `| # | Entscheidung | Empfehlung |`,
        `| # | Frage | Optionen |`, `| # | Befund | Wohin |`) steht im Register,
        mit diesem Review als Quelle;
      * jede Registerzeile zeigt auf eine Quelle, die es gibt und in der ihre
        Kennung steht, traegt einen gueltigen Stand, und was offen oder
        vertagt ist, hat ein Paket aus dem Plan (00 Teil C).

    Ob ein Entscheid richtig umgesetzt ist, prueft dieser Check NICHT — das
    tun PO_DECISIONS_APPLIED und die Wächter der jeweiligen Umsetzung. Er
    prueft, dass nichts aus dem Blick geraet.

    LOW wie HANDBOOK_ROADMAP_CURRENT: ein Pflegesignal, keine falsche
    Aussage — aber `make verify` laeuft mit --fail-on low, der Build haelt
    also an. LOW ist entschieden (PO R-1, 05.10.2026).
    """
    titel = "jede Frage an den PO und jeder Befund mit Ziel steht im Entscheidungsregister"
    findings: list[str] = []
    register_pfad = _REVIEW_DIR / _REGISTER
    if not register_pfad.exists():
        return make_result("PO_DECISIONS_REGISTERED", titel, "low", False,
                           f"{register_pfad.relative_to(REPO_ROOT)} fehlt.", [])

    registriert: dict[tuple[str, str], list[str]] = {}
    for header, rows in _md_tables(register_pfad.read_text(encoding="utf-8")):
        if header != _REGISTER_HEADER:
            continue
        for row in rows:
            if len(row) != len(_REGISTER_HEADER):
                findings.append(f"Registerzeile mit {len(row)} statt 5 Spalten: {' | '.join(row)[:80]}")
                continue
            kennung, _, quelle, stand, paket = row
            m = re.search(r"`([^`]+\.md)`", quelle)
            if not m:
                findings.append(f"{kennung}: Quelle '{quelle}' nennt keine Datei in `…md`")
                continue
            schluessel = (m.group(1), kennung)
            if schluessel in registriert:
                findings.append(f"{kennung} ({m.group(1)}): doppelt im Register")
            registriert[schluessel] = row
            q = _REVIEW_DIR / m.group(1)
            if not q.exists():
                findings.append(f"{kennung}: Quelle {m.group(1)} gibt es nicht")
            elif m.group(1) != _REGISTER and kennung not in q.read_text(encoding="utf-8"):
                findings.append(f"{kennung}: steht nicht in seiner Quelle {m.group(1)}")
            wort = stand.split()[0] if stand.split() else ""
            if wort not in _REGISTER_STAENDE:
                findings.append(f"{kennung}: Stand '{stand}' beginnt nicht mit {'/'.join(_REGISTER_STAENDE)}")
            if wort in ("offen", "vertagt") and paket not in _REGISTER_PAKETE:
                findings.append(f"{kennung}: {wort}, aber kein Paket (steht: '{paket}')")

    quellen = 0
    for pfad in sorted(_REVIEW_DIR.glob("*.md")):
        if pfad.name in (_REGISTER, "README.md"):
            continue
        for header, rows in _md_tables(pfad.read_text(encoding="utf-8")):
            if header[:3] not in _DECISION_HEADERS:
                continue
            for row in rows:
                kennung = row[0].replace("*", "").strip()
                if not kennung:
                    continue
                quellen += 1
                if (pfad.name, kennung) not in registriert:
                    findings.append(f"{pfad.name}: {kennung} fehlt im Register")

    offen = sum(1 for r in registriert.values() if r[3].split()[:1] in (["offen"], ["vertagt"]))
    return make_result(
        "PO_DECISIONS_REGISTERED", titel, "low", not findings,
        f"{len(findings)} Befund(e) zwischen Reviews und Entscheidungsregister." if findings
        else f"{quellen} Zeilen aus Entscheidungs- und Befundtabellen der Reviews stehen im Register; "
             f"{len(registriert)} Registerzeilen, davon {offen} offen oder vertagt, jede mit Paket.",
        findings[:12] + ([f"… und {len(findings) - 12} weitere"] if len(findings) > 12 else []),
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
        # schema_version 2 / SPEC-01
        check_gate_check_ids_unique,
        check_gate_implementation_honest,
        check_gate_evidence_level_valid,
        check_gate_role_scope_valid,
        check_evidence_insert_arity,
        check_waiver_not_declarative,
        check_runtime_mode_visible,
        check_readme_counts_current,
        check_readme_evidence_claims_current,
        check_doc_references_are_tracked,
        check_counts_live_in_readme_only,
        check_signature_verify_pins_identity,
        check_signing_context_asserted,
        check_e1_claims_are_signed,
        check_required_inputs_enforced,
        check_negative_cases_gate_the_build,
        check_workflow_claims_no_counts,
        check_trigger_matches_requirement,
        check_acceptance_criteria_traced,
        check_evidence_fail_closed,
        check_human_decision_takes_effect,
        check_gate_declares_effect,
        check_handbook_roadmap_is_current,
        check_legal_quotes_verbatim,
        check_norm_unit_ids_unique,
        check_norm_sentence_units_current,
        check_po_decisions_applied,
        check_omnibus_superseded_units_out,
        check_coverage_finding_names_checking_gate,
        check_element_matrix_derives_gate,
        check_norm_units_match_extractor,
        check_in_units_own_duty_text,
        check_requirement_anchor_declared,
        check_norm_refs_resolve,
        check_po_decisions_registered,
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
