#!/usr/bin/env python3
"""
test_integrity_regression.py — PoC Integrity Regression Suite

Static regression checks for credibility risks in the GenAIOps Compliance Gates PoC.

This suite intentionally focuses on "does the PoC prove what it claims to prove?"
instead of only checking functional green paths.

What it checks (20 checks, fail-fast ordering):
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
        check_gate_declares_effect,
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
