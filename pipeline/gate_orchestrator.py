#!/usr/bin/env python3
"""
gate_orchestrator.py — Closed-Loop Gate Pipeline for GenAIOps Compliance Gates.

Connects all five pillars into a single automated flow:
  S1 Design Principles  → embedded in gate definitions
  S2 Quality Gates       → scenario config drives gate sequence
  S3 Policy Engine       → Conftest (CI) or direct fixture evaluation
  S4 Evidence Store      → every gate result recorded with hash chain
  S5 Monitoring          → pipeline report + hash-chain verification

Usage:
    # Run PASS scenario (all gates succeed)
    python gate_orchestrator.py --scenario pipeline/scenarios/poc_healthcare_pass.json

    # Run FAIL scenario (G-DEP-02 blocks pipeline)
    python gate_orchestrator.py --scenario pipeline/scenarios/poc_healthcare_fail.json

    # Dry-run: show what would happen without writing to Evidence Store
    python gate_orchestrator.py --scenario pipeline/scenarios/poc_healthcare_pass.json --dry-run

    # With Conftest (requires conftest binary installed)
    python gate_orchestrator.py --scenario pipeline/scenarios/poc_healthcare_pass.json --use-conftest

Exit codes:
    0 = All gates passed, evidence recorded, hash chain verified
    1 = At least one gate FAILED (evidence still recorded for audit)
    2 = Error in pipeline execution
"""

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_SCRIPTS = REPO_ROOT / "evidence-store" / "scripts"
RECORD_EVIDENCE = EVIDENCE_SCRIPTS / "record_evidence.py"
VERIFY_HASH_CHAIN = EVIDENCE_SCRIPTS / "verify_hash_chain.py"

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ──────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────

def log(msg: str, color: str = "") -> None:
    """Print a timestamped log message."""
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    prefix = f"{color}[{ts}]{RESET}" if color else f"[{ts}]"
    print(f"{prefix} {msg}")


# ──────────────────────────────────────────────────────────────
# schema_version 2 (SPEC-01): decision derivation + check-ID parsing
# ──────────────────────────────────────────────────────────────

# Rego messages that already follow the SPEC-01 convention look like:
#   "G-PRE-04/P1 (R003): container 'x' must set runAsNonRoot: true"
# Older, pre-SPEC-01 messages have no "<GATE-ID>/<CHECK-ID>" prefix
# (e.g. "G-DEP-02 (R003): accuracy is missing") and yield check_id=None —
# this is expected until those Rego files are individually revisited.
_CHECK_ID_RE = re.compile(r"^([A-Z][A-Z0-9-]*)/([A-Za-z0-9-]+)\s*\(")


def parse_check_id(msg: str) -> str:
    """
    Extract the CHECK-ID from a Rego message of the form
    '<GATE-ID>/<CHECK-ID> (<Requirement>, <Legal-Ref>): <message>'.
    Returns None if the message does not follow this convention.
    """
    if not msg:
        return None
    m = _CHECK_ID_RE.match(msg.strip())
    return m.group(2) if m else None


def annotate_check_ids(items: list) -> list:
    """Attach a parsed 'check_id' field to each failure/warning dict."""
    annotated = []
    for item in items or []:
        if isinstance(item, dict):
            msg = item.get("msg", "")
            annotated.append({**item, "check_id": parse_check_id(msg)})
        else:
            annotated.append({"msg": str(item), "check_id": parse_check_id(str(item))})
    return annotated


# ──────────────────────────────────────────────────────────────
# Rollenparameter PROVIDER / DEPLOYER / BOTH (SPEC-03)
# ──────────────────────────────────────────────────────────────

VALID_AI_ACT_ROLES = ("PROVIDER", "DEPLOYER", "BOTH")

# Gate-Verzeichnisse, aus denen role_scope gelesen wird
GATE_DEF_DIRS = (
    REPO_ROOT / "gate-definitions" / "pre-deployment",
    REPO_ROOT / "gate-definitions" / "deployment",
    REPO_ROOT / "gate-definitions" / "operations",
)


def resolve_ai_act_role(config: dict) -> str:
    """
    Resolve the active EU AI Act role, in this precedence order
    (SPEC-03 Abschnitt 4):

      1. environment variable AI_ACT_ROLE
      2. field `role` in the scenario manifest
      3. default DEPLOYER (backwards compatible with the existing catalogue)

    The merkformel behind the split: the provider owes the properties of
    the SYSTEM (Art. 8-15 via Art. 16 lit. a), the deployer owes the
    properties of its USE (Art. 26).
    """
    raw = os.environ.get("AI_ACT_ROLE") or config.get("role") or "DEPLOYER"
    role = str(raw).strip().upper()
    if role not in VALID_AI_ACT_ROLES:
        log(f"ERROR: invalid AI_ACT_ROLE '{raw}' — must be one of: "
            f"{', '.join(VALID_AI_ACT_ROLES)}", RED)
        sys.exit(2)
    return role


def load_gate_role_scopes() -> dict:
    """
    Map gate_id -> role_scope list, read from the gate definitions.

    Gates without an explicit role_scope default to ["deployer"], matching
    the documented state of the catalogue before SPEC-03.
    """
    try:
        import yaml
    except ImportError:
        log("WARNING: pyyaml not installed — role filtering falls back to "
            "'deployer' for every gate", YELLOW)
        return {}

    scopes = {}
    for d in GATE_DEF_DIRS:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("G-*.yaml")):
            try:
                gate = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                log(f"WARNING: could not parse {f.name}: {exc}", YELLOW)
                continue
            gate_id = gate.get("id")
            if gate_id:
                scopes[gate_id] = gate.get("role_scope") or ["deployer"]
    return scopes


def gate_matches_role(gate_id: str, role: str, scopes: dict) -> bool:
    """
    Filter rule (SPEC-03 Abschnitt 4):

      AI_ACT_ROLE = DEPLOYER  -> only gates with "deployer" in role_scope
      AI_ACT_ROLE = PROVIDER  -> only gates with "provider" in role_scope
      AI_ACT_ROLE = BOTH      -> all gates (union, no double execution)

    Under BOTH a gate carrying both roles still runs exactly once and
    produces exactly one evidence record — the union is over the gate set,
    not over role-gate pairs.
    """
    if role == "BOTH":
        return True
    scope = scopes.get(gate_id, ["deployer"])
    return role.lower() in [str(s).lower() for s in scope]


def derive_decision(failures: list, warnings: list, method: str) -> str:
    """
    Derive the gate decision from check results (SPEC-01 Abschnitt 5).

    Evaluation order (do not reorder):
      1. At least one MUST check violated (failures non-empty) -> "block"
      2. Gate is HYBRID (D3xD2-Override)                        -> "manual_review"
      3. At least one SHOULD check violated (warnings non-empty) -> "warn"
      4. Otherwise                                               -> "approve"

    A HYBRID gate with a violated MUST still blocks — the automation
    classification never overrides a MUST violation, so step 1 precedes
    step 2.
    """
    if failures:
        return "block"
    if method == "HYBRID":
        return "manual_review"
    if warnings:
        return "warn"
    return "approve"


def load_scenario(path: str) -> dict:
    """Load and validate a scenario configuration file."""
    scenario_path = Path(path)
    if not scenario_path.is_absolute():
        scenario_path = REPO_ROOT / scenario_path

    if not scenario_path.exists():
        log(f"ERROR: Scenario file not found: {scenario_path}", RED)
        sys.exit(2)

    with open(scenario_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Validate required fields
    required = ["scenario", "pipeline", "gates"]
    for field in required:
        if field not in config:
            log(f"ERROR: Missing required field '{field}' in scenario config", RED)
            sys.exit(2)

    return config


def resolve_fixture_path(fixture_rel: str) -> Path:
    """Resolve a fixture path relative to repo root."""
    p = REPO_ROOT / fixture_rel
    if not p.exists():
        log(f"ERROR: Fixture not found: {p}", RED)
        sys.exit(2)
    return p


def evaluate_gate_with_conftest(policy_path: str, fixture_path: str) -> dict:
    """
    Run Conftest against a fixture using a Rego policy.
    Returns parsed JSON output with pass/fail status.
    """
    policy_abs = REPO_ROOT / policy_path
    fixture_abs = REPO_ROOT / fixture_path

    cmd = [
        "conftest", "test",
        str(fixture_abs),
        "--policy", str(policy_abs.parent),
        "--output", "json",
        "--no-color",
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        output = json.loads(result.stdout) if result.stdout.strip() else []

        # Conftest JSON output: list of file results.
        # `failures` = deny (MUST, blocking); `warnings` = warn (SHOULD, advisory).
        failures = []
        warnings = []
        successes = []
        for file_result in output:
            failures.extend(file_result.get("failures", []))
            warnings.extend(file_result.get("warnings", []))
            successes.extend(file_result.get("successes", []))

        return {
            "tool": "conftest",
            "failures": failures,
            "warnings": warnings,
            "successes": successes,
            "failure_count": len(failures),
            "warning_count": len(warnings),
            "success_count": len(successes),
            "decision": "FAIL" if failures else "PASS",
            "raw_output": output,
        }
    except FileNotFoundError:
        log("WARNING: conftest not installed, falling back to fixture-based evaluation", YELLOW)
        return None
    except subprocess.TimeoutExpired:
        log("ERROR: conftest timed out after 30s", RED)
        return {"tool": "conftest", "decision": "FAIL", "failures": [{"msg": "timeout"}]}
    except json.JSONDecodeError:
        log(f"WARNING: Could not parse conftest output: {result.stdout[:200]}", YELLOW)
        return None


def evaluate_gatekeeper_admission(k8s_object: dict, gate_id: str) -> dict:
    """
    Simulate Gatekeeper Admission Controller logic locally.

    This mirrors the exact Rego logic from the ConstraintTemplates in
    k8s/gatekeeper/ — checking pod template annotations against required values.

    In production, Gatekeeper runs this inside the K8s API server.
    Here we simulate it for local testing and walkthrough demos.
    """
    # Extract pod template annotations (where Gatekeeper checks)
    pod_annotations = (
        k8s_object.get("spec", {})
        .get("template", {})
        .get("metadata", {})
        .get("annotations", {})
    )
    # Also check metadata-level annotations
    meta_annotations = k8s_object.get("metadata", {}).get("annotations", {})

    violations = []

    if gate_id == "G-OPS-03":
        # GenaiopsMonitoringConfigured: require drift + service-monitor annotations
        required = {
            "genaiops.io/drift-detection-enabled": "true",
            "genaiops.io/service-monitor-configured": "true",
        }
        for key, expected in required.items():
            actual = pod_annotations.get(key)
            if actual is None:
                violations.append({
                    "msg": f"G-OPS-03 FAIL: Pod annotation '{key}' is missing",
                    "type": "gatekeeper_violation",
                })
            elif actual != expected:
                violations.append({
                    "msg": f"G-OPS-03 FAIL: Pod annotation '{key}' must be '{expected}', got '{actual}'",
                    "type": "gatekeeper_violation",
                })

    elif gate_id == "G-OPS-05":
        # GenaiopsEvidenceCompleteness: require evidence-store + hash-chain annotations
        required = {
            "genaiops.io/evidence-store-connected": "true",
            "genaiops.io/hash-chain-enabled": "true",
        }
        for key, expected in required.items():
            actual = pod_annotations.get(key) or meta_annotations.get(key)
            if actual is None:
                violations.append({
                    "msg": f"G-OPS-05 FAIL: Annotation '{key}' is missing",
                    "type": "gatekeeper_violation",
                })
            elif actual != expected:
                violations.append({
                    "msg": f"G-OPS-05 FAIL: Annotation '{key}' must be '{expected}', got '{actual}'",
                    "type": "gatekeeper_violation",
                })

    elif gate_id == "G-OPS-04":
        # GenaiopsCybersecurityOperations: require runtime security-control annotations
        required = {
            "genaiops.io/image-scanning-enabled": "true",
            "genaiops.io/network-policies-specified": "true",
            "genaiops.io/encryption-at-rest": "true",
            "genaiops.io/encryption-in-transit": "true",
        }
        for key, expected in required.items():
            actual = pod_annotations.get(key)
            if actual is None:
                violations.append({
                    "msg": f"G-OPS-04 FAIL: Pod annotation '{key}' is missing",
                    "type": "gatekeeper_violation",
                })
            elif actual != expected:
                violations.append({
                    "msg": f"G-OPS-04 FAIL: Pod annotation '{key}' must be '{expected}', got '{actual}'",
                    "type": "gatekeeper_violation",
                })

    decision = "FAIL" if violations else "PASS"
    admission_action = "REJECT" if violations else "ADMIT"

    return {
        "tool": "gatekeeper-sim",
        "decision": decision,
        "admission_action": admission_action,
        "failures": violations,
        "annotations_checked": len(pod_annotations),
    }


def evaluate_gate_from_fixture(fixture_path: str, gate_id: str) -> dict:
    """
    Evaluate a gate directly from fixture data (without Conftest).
    Used in local/demo mode and as fallback when Conftest is not available.

    This reads the fixture JSON and applies the same logic that the
    Rego policies would apply — making the result reproducible without
    requiring the OPA/Conftest binary.
    """
    fixture_abs = REPO_ROOT / fixture_path

    with open(fixture_abs, "r", encoding="utf-8") as f:
        if fixture_path.endswith(".yaml") or fixture_path.endswith(".yml"):
            try:
                import yaml
            except ImportError:
                log("WARNING: pyyaml not installed — YAML fixtures cannot be evaluated. "
                    "Install with: pip install pyyaml", YELLOW)
                return {
                    "tool": "fixture-eval",
                    "decision": "FAIL",
                    "failures": [{"msg": "pyyaml not installed, cannot evaluate YAML fixture"}],
                }
            data = yaml.safe_load(f)
        else:
            data = json.load(f)

    # Gate-specific evaluation logic (mirrors Rego policies)
    if gate_id == "G-PRE-01":
        # policy_risk_classification: mirrors Rego policy fields
        rc = data.get("risk_classification", {})
        mr = data.get("manual_review", {})
        failures = []
        if rc.get("risk_class") not in ("high", "limited", "minimal"):
            failures.append({"msg": "risk_class must be high, limited, or minimal"})
        if not rc.get("classification_reasoning"):
            failures.append({"msg": "classification_reasoning is required"})
        if rc.get("risk_class") == "high" and not rc.get("annex_reference"):
            failures.append({"msg": "annex_reference required for high-risk systems"})
        if rc.get("risk_class") == "high" and not rc.get("mitigation_measures"):
            failures.append({"msg": "mitigation_measures required for high-risk systems"})
        if not mr.get("reviewed_by"):
            failures.append({"msg": "manual_review.reviewed_by is required"})
        if not mr.get("review_date"):
            failures.append({"msg": "manual_review.review_date is required"})
        return {
            "tool": "fixture-eval",
            "decision": "FAIL" if failures else "PASS",
            "failures": failures,
        }

    elif gate_id == "G-PRE-05":
        # policy_governance_approval: mirrors Rego policy fields
        fria = data.get("fundamental_rights_impact_assessment", {})
        ho = data.get("human_oversight", {})
        ca = data.get("conformity_assessment", {})
        approval = data.get("approval", {})
        failures = []
        if not fria.get("fria_completed"):
            failures.append({"msg": "FRIA not completed"})
        if not fria.get("affected_rights"):
            failures.append({"msg": "affected_rights not documented in FRIA"})
        if not ho.get("oversight_model"):
            failures.append({"msg": "oversight_model not specified"})
        if not ho.get("human_oversight_lead"):
            failures.append({"msg": "human_oversight_lead not assigned"})
        if not ho.get("escalation_procedure"):
            failures.append({"msg": "escalation_procedure not defined"})
        intervention = ho.get("intervention_capability", {})
        if not intervention.get("kill_switch"):
            failures.append({"msg": "kill_switch capability not configured"})
        if not ca.get("declaration_available"):
            failures.append({"msg": "conformity_assessment.declaration_available not set"})
        if not approval.get("approved_by"):
            failures.append({"msg": "approval.approved_by not set"})
        return {
            "tool": "fixture-eval",
            "decision": "FAIL" if failures else "PASS",
            "failures": failures,
        }

    elif gate_id == "G-DEP-02":
        # policy_safety_metrics: mirrors Rego policy fields
        qm = data.get("quality_metrics", {})
        pm = data.get("performance_metrics", {})
        sm = data.get("safety_metrics", {})
        ev = data.get("evaluation", {})
        sg = data.get("subgroup_analysis", {})
        at = data.get("adversarial_tests", {})
        thresholds = data.get("gate_thresholds", {})
        failures = []

        acc = qm.get("accuracy", 0)
        acc_min = thresholds.get("accuracy_min", 0.85)
        if acc < acc_min:
            failures.append({"msg": f"accuracy {acc} < {acc_min}"})

        lat = pm.get("latency_p95_ms", 99999)
        lat_max = thresholds.get("latency_p95_max_ms", 2000)
        if lat > lat_max:
            failures.append({"msg": f"latency_p95 {lat}ms > {lat_max}ms"})

        ss = sm.get("safety_score", 0)
        ss_min = thresholds.get("safety_score_min", 0.90)
        if ss < ss_min:
            failures.append({"msg": f"safety_score {ss} < {ss_min}"})

        if not ev.get("run_id"):
            failures.append({"msg": "evaluation.run_id is required"})

        # SHOULD criteria (RFC 2119): advisory, non-blocking — mirror Rego `warn`.
        warnings = []
        if not sg.get("performed"):
            warnings.append({"msg": "subgroup_analysis.performed is missing [SHOULD]"})
        if not at.get("performed"):
            warnings.append({"msg": "adversarial_tests.performed is missing [SHOULD]"})

        return {
            "tool": "fixture-eval",
            "decision": "FAIL" if failures else "PASS",
            "failures": failures,
            "warnings": warnings,
        }

    elif gate_id == "G-PRE-04":
        # policy_security_baseline: check 6 container security rules (P1-P6)
        containers = (
            data.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        )
        failures = []
        if not containers:
            failures.append({"msg": "no containers found in deployment spec"})
        for c in containers:
            sc = c.get("securityContext", {})
            # P1: runAsNonRoot
            if not sc.get("runAsNonRoot"):
                failures.append({"msg": f"container '{c.get('name', '?')}': runAsNonRoot is not true"})
            # P2: resource limits
            limits = c.get("resources", {}).get("limits", {})
            if not limits.get("cpu") or not limits.get("memory"):
                failures.append({"msg": f"container '{c.get('name', '?')}': cpu/memory limits not set"})
            # P3: readOnlyRootFilesystem
            if not sc.get("readOnlyRootFilesystem"):
                failures.append({"msg": f"container '{c.get('name', '?')}': readOnlyRootFilesystem is not true"})
            # P4: no plaintext secrets in env
            for env in c.get("env", []):
                env_name = (env.get("name") or "").lower()
                if any(kw in env_name for kw in ("password", "secret", "key", "token")):
                    if env.get("value") and not env.get("valueFrom"):
                        failures.append({"msg": f"container '{c.get('name', '?')}': env '{env.get('name')}' contains plaintext secret"})
            # P5: allowPrivilegeEscalation
            if sc.get("allowPrivilegeEscalation") is not False:
                failures.append({"msg": f"container '{c.get('name', '?')}': allowPrivilegeEscalation is not false"})
            # P6: capabilities drop ALL
            caps = sc.get("capabilities", {}).get("drop", [])
            if "ALL" not in caps:
                failures.append({"msg": f"container '{c.get('name', '?')}': capabilities.drop does not include ALL"})
        return {
            "tool": "fixture-eval",
            "decision": "FAIL" if failures else "PASS",
            "failures": failures,
        }

    elif gate_id == "G-DEP-05":
        # policy_bias_assessment_complete: R013 is SHOULD (see requirements/R013.yaml)
        # → all checks are advisory (warn), non-blocking. Decision stays PASS.
        bd = data.get("bias_detection", {})
        warnings = []
        if not bd.get("methods"):
            warnings.append({"msg": "bias_detection.methods not documented [SHOULD]"})
        fr = bd.get("fairness_results", {})
        if not fr.get("metrics"):
            warnings.append({"msg": "bias_detection.fairness_results.metrics not documented [SHOULD]"})
        if not bd.get("protected_attributes"):
            warnings.append({"msg": "bias_detection.protected_attributes not listed [SHOULD]"})
        if fr.get("bias_detected") and not bd.get("mitigation_measures"):
            warnings.append({"msg": "bias detected but no mitigation_measures documented [SHOULD]"})
        return {
            "tool": "fixture-eval",
            "decision": "PASS",
            "failures": [],
            "warnings": warnings,
        }

    elif gate_id == "G-DEP-01":
        # policy_data_provenance_documented: check data governance fields
        dp = data.get("data_provenance", {})
        failures = []
        if not dp.get("collection_methods"):
            failures.append({"msg": "data_provenance.collection_methods not documented"})
        if not dp.get("sources"):
            failures.append({"msg": "data_provenance.sources not listed"})
        if not dp.get("preprocessing_steps"):
            failures.append({"msg": "data_provenance.preprocessing_steps not documented"})
        if not dp.get("data_version"):
            failures.append({"msg": "data_provenance.data_version not set"})
        return {
            "tool": "fixture-eval",
            "decision": "FAIL" if failures else "PASS",
            "failures": failures,
        }

    elif gate_id == "G-DEP-03":
        # policy_transparency_docs_present: check transparency documentation
        tr = data.get("transparency", {})
        failures = []
        if not tr.get("instructions_for_deployers"):
            failures.append({"msg": "transparency.instructions_for_deployers missing"})
        if not tr.get("model_capabilities"):
            failures.append({"msg": "transparency.model_capabilities missing"})
        if not tr.get("known_limitations"):
            failures.append({"msg": "transparency.known_limitations missing"})
        labeling = tr.get("ai_content_labeling", {})
        if not labeling.get("enabled"):
            failures.append({"msg": "transparency.ai_content_labeling.enabled is not true"})
        return {
            "tool": "fixture-eval",
            "decision": "FAIL" if failures else "PASS",
            "failures": failures,
        }

    elif gate_id in ("G-OPS-03", "G-OPS-04", "G-OPS-05"):
        # Annotation-based gates — check via AdmissionReview or K8s annotations
        review_data = data.get("review", {}).get("object", {})
        if review_data:
            return evaluate_gatekeeper_admission(review_data, gate_id)

        # For K8s manifests: check annotations directly
        pod_annotations = (
            data.get("spec", {}).get("template", {}).get("metadata", {}).get("annotations", {})
        )
        meta_annotations = data.get("metadata", {}).get("annotations", {})
        all_annotations = {**meta_annotations, **pod_annotations}
        failures = []

        if gate_id == "G-OPS-03":
            for key in ["genaiops.io/drift-detection-enabled", "genaiops.io/service-monitor-configured", "prometheus.io/scrape"]:
                if all_annotations.get(key) != "true":
                    failures.append({"msg": f"annotation '{key}' is not 'true'"})
        elif gate_id == "G-OPS-04":
            for key in [
                "genaiops.io/image-scanning-enabled",
                "genaiops.io/network-policies-specified",
                "genaiops.io/encryption-at-rest",
                "genaiops.io/encryption-in-transit",
            ]:
                if all_annotations.get(key) != "true":
                    failures.append({"msg": f"annotation '{key}' is not 'true'"})
        elif gate_id == "G-OPS-05":
            for key in ["genaiops.io/evidence-store-connected", "genaiops.io/hash-chain-enabled"]:
                if all_annotations.get(key) != "true":
                    failures.append({"msg": f"annotation '{key}' is not 'true'"})
            if not all_annotations.get("genaiops.io/evidence-store-type"):
                failures.append({"msg": "annotation 'genaiops.io/evidence-store-type' is missing"})

        return {
            "tool": "fixture-eval",
            "decision": "FAIL" if failures else "PASS",
            "failures": failures,
        }

    elif gate_id == "G-OPS-02":
        # policy_incident_process_exists: check incident-response annotations
        # Dual-mode: resolve review.object (Gatekeeper) or direct input (Conftest/YAML)
        obj = data.get("review", {}).get("object", data)
        pod_annotations = (
            obj.get("spec", {}).get("template", {}).get("metadata", {}).get("annotations", {})
        )
        meta_annotations = obj.get("metadata", {}).get("annotations", {})
        all_annotations = {**meta_annotations, **pod_annotations}
        failures = []
        # incident-response-configured and rollback-mechanism must be "true" (not just present)
        for key in ["genaiops.io/incident-response-configured", "genaiops.io/rollback-mechanism"]:
            if all_annotations.get(key) != "true":
                failures.append({"msg": f"annotation '{key}' must be 'true'"})
        # incident-contact must be present and non-empty
        contact = all_annotations.get("genaiops.io/incident-contact", "")
        if not contact:
            failures.append({"msg": "annotation 'genaiops.io/incident-contact' is missing or empty"})
        return {
            "tool": "fixture-eval",
            "decision": "FAIL" if failures else "PASS",
            "failures": failures,
        }

    # Strict: unknown gates FAIL (not PASS)
    log(f"WARNING: No evaluation logic for {gate_id} — treating as FAIL", YELLOW)
    return {
        "tool": "fixture-eval",
        "decision": "FAIL",
        "failures": [{"msg": f"No evaluation logic implemented for gate {gate_id}"}],
    }


def record_to_evidence_store(
    gate_id: str,
    method: str,
    fixture_path: str,
    db_path: str,
    run_id: str,
    eval_result: dict = None,
    dry_run: bool = False,
) -> dict:
    """
    Call record_evidence.py to persist a gate decision to the Evidence Store.

    If the fixture is YAML (not valid JSON for record_evidence.py), we create
    a temporary JSON file from the evaluation result so record_evidence.py
    can process it.

    Returns the captured output.
    """
    import tempfile

    source_path = str(REPO_ROOT / fixture_path)
    temp_json = None

    # Always create a temporary JSON file from the evaluation result
    # so record_evidence.py gets the correct decision (PASS/FAIL).
    # This ensures the Evidence Store reflects the actual gate evaluation.
    if eval_result:
        temp_json = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, prefix=f"gate_{gate_id}_"
        )
        failures = annotate_check_ids(eval_result.get("failures", []))
        warnings = annotate_check_ids(eval_result.get("warnings", []))
        gate_evidence = {
            "gate_id": gate_id,
            "decision": eval_result.get("decision", "PASS"),
            # schema_version 2 (SPEC-01 Abschnitt 5): derived gate decision
            # (block/manual_review/warn/approve), independent from the
            # PASS/FAIL persisted in the 'decision' DB column above.
            "derived_decision": derive_decision(failures, warnings, method),
            "tool": eval_result.get("tool", "fixture-eval"),
            "failures": failures,
            "warnings": warnings,
            "source_fixture": fixture_path,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }
        json.dump(gate_evidence, temp_json, indent=2)
        temp_json.close()
        source_path = temp_json.name

    cmd = [
        sys.executable,
        str(RECORD_EVIDENCE),
        "--gate", gate_id,
        "--method", method,
        "--source", source_path,
        "--sqlite", db_path,
        "--run-id", run_id,
    ]

    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Clean up temp file
    if temp_json and os.path.exists(temp_json.name):
        os.unlink(temp_json.name)

    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def verify_chain(db_path: str, verbose: bool = False) -> dict:
    """
    Call verify_hash_chain.py to verify the Evidence Store integrity.
    Returns verification result.
    """
    cmd = [
        sys.executable,
        str(VERIFY_HASH_CHAIN),
        "--sqlite", db_path,
    ]
    if verbose:
        cmd.append("--verbose")

    result = subprocess.run(cmd, capture_output=True, text=True)

    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "is_valid": result.returncode == 0,
    }


def print_banner(scenario_name: str) -> None:
    """Print the pipeline startup banner."""
    print()
    print(f"{BOLD}{'═' * 70}{RESET}")
    print(f"{BOLD}  GenAIOps Compliance Gate Pipeline — Closed Loop{RESET}")
    print(f"{BOLD}{'═' * 70}{RESET}")
    print(f"  Scenario:  {scenario_name}")
    print(f"  Started:   {datetime.now(timezone.utc).isoformat()}")
    print("  Run ID:    (generated per execution)")
    print(f"{BOLD}{'═' * 70}{RESET}")
    print()


def print_gate_result(gate: dict, result: dict, evidence: dict, index: int, total: int) -> None:
    """Print a formatted gate result to terminal."""
    decision = result["decision"]
    color = GREEN if decision == "PASS" else RED
    method = gate["method"]
    method_badge = f"{BLUE}[{method}]{RESET}"
    derived_decision = derive_decision(
        result.get("failures", []), result.get("warnings", []), method
    )

    print(f"  {BOLD}Gate {index}/{total}: {gate['gate_id']} — {gate['gate_name']}{RESET}")
    print(f"  Method: {method_badge}  |  Decision: {color}{BOLD}{decision}{RESET}"
          f"  |  Derived: {BLUE}{derived_decision}{RESET}")

    if result.get("failures"):
        for f in result["failures"]:
            check_id = f.get("check_id") or parse_check_id(f.get("msg", ""))
            tag = f"{check_id}: " if check_id else ""
            print(f"    {RED}✗ {tag}{f.get('msg', str(f))}{RESET}")

    if result.get("warnings"):
        for w in result["warnings"]:
            check_id = w.get("check_id") or parse_check_id(w.get("msg", ""))
            tag = f"{check_id}: " if check_id else ""
            print(f"    {YELLOW}⚠ {tag}{w.get('msg', str(w))}{RESET}")

    if evidence.get("stdout"):
        # Extract hash info from record_evidence output
        for line in evidence["stdout"].split("\n"):
            if "Hash:" in line or "audit_id" in line:
                print(f"    {BLUE}{line.strip()}{RESET}")

    print()


def print_summary(results: list, pipeline_halted: bool, halt_gate: str, verification: dict) -> None:
    """Print the pipeline execution summary."""
    passed = sum(1 for r in results if r["decision"] == "PASS")
    failed = sum(1 for r in results if r["decision"] == "FAIL")
    skipped = sum(1 for r in results if r["decision"] == "SKIPPED")
    total = len(results)

    print(f"{BOLD}{'─' * 70}{RESET}")
    print(f"{BOLD}  PIPELINE SUMMARY{RESET}")
    print(f"{'─' * 70}")
    print(f"  Gates executed:  {passed + failed}/{total}")
    print(f"  {GREEN}PASS: {passed}{RESET}  |  {RED}FAIL: {failed}{RESET}  |  {YELLOW}SKIPPED: {skipped}{RESET}")

    if pipeline_halted:
        print(f"\n  {RED}{BOLD}⚠ Pipeline HALTED at {halt_gate}{RESET}")
        print(f"  {RED}  Reason: Gate returned FAIL — downstream gates skipped{RESET}")
        print(f"  {BLUE}  Note: FAIL evidence was recorded for audit traceability{RESET}")

    if verification:
        v_color = GREEN if verification["is_valid"] else RED
        v_status = "VALID" if verification["is_valid"] else "CORRUPTED"
        print(f"\n  Hash-Chain: {v_color}{BOLD}{v_status}{RESET}")
        # Extract record count from verification output
        for line in verification["stdout"].split("\n"):
            if "records" in line.lower():
                print(f"    {line.strip()}")

    print(f"\n{BOLD}{'═' * 70}{RESET}")

    # Final verdict
    if not pipeline_halted and verification and verification["is_valid"]:
        print(f"\n  {GREEN}{BOLD}✓ PIPELINE RESULT: ALL GATES PASSED — DEPLOYMENT APPROVED{RESET}")
    elif pipeline_halted:
        print(f"\n  {RED}{BOLD}✗ PIPELINE RESULT: GATE FAILURE — DEPLOYMENT BLOCKED{RESET}")

    print()


# ──────────────────────────────────────────────────────────────
# Main pipeline logic
# ──────────────────────────────────────────────────────────────

def run_pipeline(scenario_path: str, use_conftest: bool = False, dry_run: bool = False, verbose: bool = False) -> int:
    """
    Execute the closed-loop gate pipeline.

    Flow per gate:
      1. Evaluate gate (Conftest or fixture-based)
      2. Record result to Evidence Store (record_evidence.py)
      3. If FAIL on blocking gate → halt pipeline, record FAIL, skip remaining
      4. After all gates → verify hash chain (verify_hash_chain.py)
      5. Print summary report

    Returns exit code: 0=all pass, 1=gate failure, 2=error
    """
    config = load_scenario(scenario_path)
    scenario = config["scenario"]
    pipeline = config["pipeline"]
    gates = config["gates"]

    print_banner(scenario["name"])

    run_id = str(uuid.uuid4())
    # Use /tmp for SQLite (mounted filesystems may not support WAL locking)
    import tempfile
    db_path = os.path.join(tempfile.gettempdir(), pipeline["evidence_db"])
    db_final_path = str(REPO_ROOT / "evidence-store" / pipeline["evidence_db"])

    # Clean previous DB for fresh run
    for p in [db_path, db_final_path]:
        if os.path.exists(p) and not dry_run:
            try:
                os.remove(p)
            except PermissionError:
                log(f"Could not remove {p} (permission denied, using fresh /tmp path)", YELLOW)

    # ── Resolve role and filter the gate set (SPEC-03) ──
    ai_act_role = resolve_ai_act_role(config)
    role_scopes = load_gate_role_scopes()
    total_gates_before_filter = len(gates)
    filtered_out = [g["gate_id"] for g in gates
                    if not gate_matches_role(g["gate_id"], ai_act_role, role_scopes)]
    gates = [g for g in gates if gate_matches_role(g["gate_id"], ai_act_role, role_scopes)]

    log(f"Run ID: {run_id}", BLUE)
    log(f"Evidence DB: {pipeline['evidence_db']}", BLUE)
    log(f"AI Act role: {ai_act_role} — {len(gates)}/{total_gates_before_filter} gates in scope", BLUE)
    if filtered_out:
        log(f"  Out of role scope: {', '.join(filtered_out)}", YELLOW)
    log(f"Mode: {'Conftest' if use_conftest else 'Fixture-based'} | {'DRY-RUN' if dry_run else 'LIVE'}", BLUE)

    # An empty gate set is a legitimate outcome, not an error: the catalogue
    # is currently deployer-only, so AI_ACT_ROLE=PROVIDER selects nothing.
    # This must exit cleanly with a comprehensible message (SPEC-03 Abschnitt 7).
    if not gates:
        print()
        log(f"No gate in the catalogue declares role_scope '{ai_act_role.lower()}' — "
            f"nothing to evaluate.", YELLOW)
        log("The 16 gates of this catalogue are deployer-scoped (Art. 26). "
            "Provider requirements (Art. 16 lit. a-l) are not yet derived — "
            "see SPEC-03 Abschnitt 6.", YELLOW)
        return 0

    print()

    # ── Execute gates sequentially ──
    results = []
    pipeline_halted = False
    halt_gate = ""

    for i, gate in enumerate(gates, 1):
        gate_id = gate["gate_id"]
        method = gate["method"]
        fixture = gate["fixture"]

        # Check if this gate should be skipped (pipeline halted earlier)
        if pipeline_halted or gate.get("skip_reason"):
            reason = gate.get("skip_reason", f"Pipeline halted at {halt_gate}")
            log(f"SKIP {gate_id} — {reason}", YELLOW)
            results.append({"gate_id": gate_id, "decision": "SKIPPED", "reason": reason})
            continue

        log(f"Evaluating {gate_id} ({gate['gate_name']})...", BLUE)

        # Step 1: Evaluate the gate
        eval_result = None
        if use_conftest and gate.get("policy"):
            eval_result = evaluate_gate_with_conftest(gate["policy"], fixture)

        if eval_result is None:
            # Fallback to fixture-based evaluation
            eval_result = evaluate_gate_from_fixture(fixture, gate_id)

        decision = eval_result["decision"]
        # schema_version 2 (SPEC-01 Abschnitt 5): derived gate decision,
        # informational alongside the persisted PASS/FAIL — does not change
        # the pipeline-halt control flow below, which stays on PASS/FAIL.
        derived_decision = derive_decision(
            eval_result.get("failures", []), eval_result.get("warnings", []), method
        )

        # Step 2: Record to Evidence Store
        # For HYBRID gates: record the AUTO part first
        evidence_method = method
        if method == "HYBRID":
            evidence_method = "HYBRID"  # record_evidence.py handles this

        evidence_result = record_to_evidence_store(
            gate_id=gate_id,
            method=evidence_method,
            fixture_path=fixture,
            db_path=db_path,
            run_id=run_id,
            eval_result=eval_result,
            dry_run=dry_run,
        )

        # For HYBRID gates with manual source, also record the manual decision
        if method == "HYBRID" and gate.get("manual_source") and not dry_run:
            log(f"  Recording manual decision for {gate_id}...", BLUE)
            # Side effect only: the MANUAL record is persisted to the Evidence
            # Store; its return value is intentionally not consumed here.
            record_to_evidence_store(
                gate_id=gate_id,
                method="MANUAL",
                fixture_path=gate["manual_source"],
                db_path=db_path,
                run_id=run_id,
                dry_run=dry_run,
            )

        # Print gate result
        print_gate_result(gate, eval_result, evidence_result, i, len(gates))

        # Track result
        results.append({
            "gate_id": gate_id,
            "decision": decision,
            "derived_decision": derived_decision,
            "method": method,
            "failures": eval_result.get("failures", []),
        })

        # Step 3: Check if pipeline should halt
        if decision == "FAIL":
            pipeline_halted = True
            halt_gate = gate_id
            log(f"{gate_id} FAILED — pipeline will halt after recording evidence", RED)

    # ── Step 4: Verify hash chain ──
    print(f"\n{BOLD}{'─' * 70}{RESET}")
    log("Verifying Evidence Store hash-chain integrity...", BLUE)

    verification = None
    if not dry_run:
        verification = verify_chain(db_path, verbose=verbose)
        print(verification["stdout"])
    else:
        log("DRY-RUN: Skipping hash-chain verification", YELLOW)

    # ── Step 5: Print summary ──
    print_summary(results, pipeline_halted, halt_gate, verification)

    # ── Generate machine-readable report ──
    report = {
        "pipeline_id": pipeline["id"],
        "run_id": run_id,
        "scenario": scenario["name"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evidence_db": pipeline["evidence_db"],
        "mode": "conftest" if use_conftest else "fixture-eval",
        "ai_act_role": ai_act_role,
        "gates_filtered_out": filtered_out,
        "gates": results,
        "pipeline_halted": pipeline_halted,
        "halt_gate": halt_gate if pipeline_halted else None,
        "hash_chain_valid": verification["is_valid"] if verification else None,
        "overall_result": "PASS" if not pipeline_halted else "FAIL",
    }

    report_path = REPO_ROOT / "evidence-store" / f"pipeline_report_{run_id[:8]}.json"
    if not dry_run:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        log(f"Pipeline report saved: {report_path.name}", GREEN)

        # Copy evidence DB from /tmp to repo for persistence
        import shutil
        if os.path.exists(db_path):
            shutil.copy2(db_path, db_final_path)
            log(f"Evidence DB copied to: evidence-store/{pipeline['evidence_db']}", GREEN)

    # Return exit code
    if pipeline_halted:
        return 1
    return 0


# ──────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="GenAIOps Closed-Loop Gate Pipeline — connects Policy Engine → Evidence Store → Hash-Chain Verification"
    )
    parser.add_argument(
        "--scenario", required=True,
        help="Path to scenario config JSON (e.g., pipeline/scenarios/poc_healthcare_pass.json)"
    )
    parser.add_argument(
        "--use-conftest", action="store_true",
        help="Use Conftest binary for policy evaluation (requires conftest installed)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show evaluation results without writing to Evidence Store"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show detailed hash-chain verification output"
    )

    args = parser.parse_args()
    exit_code = run_pipeline(
        scenario_path=args.scenario,
        use_conftest=args.use_conftest,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
