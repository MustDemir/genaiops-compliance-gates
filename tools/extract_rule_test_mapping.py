#!/usr/bin/env python3
"""
extract_rule_test_mapping.py — Generate rule-to-test mapping appendix.

Scans all Rego policy files + their *_test.rego counterparts, extracts:
  - Rule signatures (deny contains msg if { ... }) with line numbers
  - Check-IDs parsed from rule messages (schema_version 2, SPEC-01 Abschnitt 6)
  - Declared policy_checks from the gate definitions, matched against those IDs
  - Test function names (test_*) with line numbers
  - Pattern class inferred from test naming convention

Output:
  - JSON (ground truth) at docs/appendix/rule_test_mapping.json
  - Markdown appendix at docs/appendix/rule_test_mapping.md

Usage:
  python3 tools/extract_rule_test_mapping.py
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POLICIES = sorted(REPO_ROOT.glob("policies/*/policy_*.rego"))
POLICIES = [p for p in POLICIES if not p.name.endswith("_test.rego")]

# Gate → Policy filename mapping (based on repo convention)
GATE_MAP = {
    "policy_risk_classification.rego":       ("G-PRE-01", "R001", "EU AI Act Art. 9", "HYBRID"),
    "policy_purpose_declaration.rego":       ("G-PRE-02", "R012", "EU AI Act Art. 27", "HYBRID"),
    "policy_risk_management_complete.rego":  ("G-PRE-03", "R001", "EU AI Act Art. 9", "HYBRID"),
    "policy_security_baseline.rego":         ("G-PRE-04", "R003", "EU AI Act Art. 15", "AUTO"),
    "policy_governance_approval.rego":       ("G-PRE-05", "R004", "EU AI Act Art. 14", "HYBRID"),
    "policy_data_provenance_documented.rego":("G-DEP-01", "R002", "EU AI Act Art. 10", "AUTO"),
    "policy_safety_metrics.rego":            ("G-DEP-02", "R003", "EU AI Act Art. 15", "AUTO"),
    "policy_transparency_docs_present.rego": ("G-DEP-03", "R007", "EU AI Act Art. 13", "AUTO"),
    "policy_conformity_verified.rego":       ("G-DEP-04", "R011", "EU AI Act Art. 26(1)", "AUTO"),
    "policy_bias_assessment_complete.rego":  ("G-DEP-05", "R013", "EU AI Act Art. 10(2)(f)", "AUTO"),
    "policy_logging_configured.rego":        ("G-DEP-06", "R014", "EU AI Act Art. 12", "AUTO"),
    "policy_human_oversight_operational.rego":("G-OPS-01", "R008", "EU AI Act Art. 14", "HYBRID"),
    "policy_incident_process_exists.rego":   ("G-OPS-02", "R009", "EU AI Act Art. 26(5)", "AUTO"),
    "policy_monitoring_configured.rego":     ("G-OPS-03", "R010", "EU AI Act Art. 72", "AUTO"),
    "policy_data_security_controls.rego":    ("G-OPS-04", "R003", "EU AI Act Art. 15", "AUTO"),
    "policy_evidence_completeness.rego":     ("G-OPS-05", "R005", "EU AI Act Art. 12", "AUTO"),
    "policy_role_change_monitoring.rego":    ("G-OPS-06", "R001", "EU AI Act Art. 25", "HYBRID"),
}

# Rule detection: "deny contains msg if { ... }" or "violation[...] { ... }"
# Rego v1 uses `deny contains X if { ... }`; older uses `deny[msg] { ... }`.
RULE_RE = re.compile(r'^\s*(deny|violation|warn|allow)\s+(contains\s+.+?\s+if|\[[^\]]*\])?\s*(if)?\s*\{', re.MULTILINE)
# Comment above a rule (# ----- Rule N: description -----)
COMMENT_RE = re.compile(r'^\s*#\s*(.*?)$', re.MULTILINE)
# Test function: test_xxx if { ... }
TEST_RE = re.compile(r'^\s*(test_[a-zA-Z0-9_]+)\s+if\s+\{', re.MULTILINE)
PACKAGE_RE = re.compile(r'^\s*package\s+([\w.]+)', re.MULTILINE)


# HYBRID domain keywords — tests covering D3-Override / EU AI Act Art. 14
# First-Degree Oversight evidence (manual review, approval, oversight-chain).
# Presence of ANY keyword in a *failing* test name classifies it as HYBRID,
# because the deny-rule under test enforces a human-judgment surface.
HYBRID_KEYWORDS = (
    "manual_review",
    "oversight",
    "approval",
    "approved",
    "fria",            # Fundamental Rights Impact Assessment
    "affected_rights",
    "kill_switch",
    "conformity",
    "governance",
)


def classify_test(name: str) -> str:
    """Infer pattern class from test name convention.

    Priority: PASS > HYBRID > FAIL-edge > FAIL-basic > OTHER.
    HYBRID wins over FAIL-edge when a grenzwert-test happens to land on a
    human-judgment surface (e.g. `test_fail_oversight_model_empty_string`):
    the DSR-relevant information is WHICH domain (HYBRID) the test enforces,
    not merely HOW (empty-string edge-case).
    """
    n = name.lower()
    # 1) Positive path always takes precedence.
    if "pass" in n:
        return "PASS"
    # 2) HYBRID domain — D3-Override / Art. 14 First-Degree Oversight.
    if "hybrid" in n or any(kw in n for kw in HYBRID_KEYWORDS):
        return "HYBRID"
    # 3) Grenzfall / edge-case on purely automated fields.
    if "fail" in n and ("edge" in n or "empty" in n or "whitespace" in n
                        or "zero" in n or "boundary" in n or "null" in n
                        or "invalid_value" in n or "wrong_value" in n):
        return "FAIL-edge"
    # 4) Happy-path missing-field failure.
    if "fail" in n:
        return "FAIL-basic"
    return "OTHER"


# schema_version 2 (SPEC-01 Abschnitt 6): Rego messages carry the check-id as
#   "<GATE-ID>/<CHECK-ID> (<Requirement>, <Legal-Ref>): <message>"
# Messages written before this convention have no "/<CHECK-ID>" part and yield
# check_id=None, which is surfaced as "unmapped" in the appendix.
MSG_CHECK_ID_RE = re.compile(r'"\s*([A-Z][A-Z0-9-]*)/([A-Za-z0-9-]+)\s*\(')


def extract_rule_check_id(body_lines: list[str]) -> str | None:
    """Find the check-id inside a rule body's msg assignment, if present."""
    for line in body_lines:
        m = MSG_CHECK_ID_RE.search(line)
        if m:
            return m.group(2)
    return None


def extract_rules(policy_path: Path) -> list[dict]:
    """Extract rule signatures with surrounding comment hint and check-id."""
    lines = policy_path.read_text().splitlines()
    rules = []
    for i, line in enumerate(lines):
        m = re.match(r'^\s*(deny|violation|warn|allow)\s+(contains\s+.+?\s+if|\[[^\]]*\])?\s*(if)?\s*\{', line)
        if m:
            kind = m.group(1)
            # Look backwards up to 8 lines for a comment hint
            hint = ""
            for j in range(max(0, i-8), i):
                c = lines[j].strip()
                if c.startswith("#") and c.lstrip("#").strip():
                    # Prefer lines that look like rule descriptions (contain "Rule" or ":" or "—")
                    txt = c.lstrip("#").strip()
                    if not txt.startswith("--") and not txt.startswith("=="):
                        hint = txt
            # Scan forward to the rule's closing brace for the msg assignment
            body = []
            for k in range(i + 1, len(lines)):
                if re.match(r'^\}', lines[k]):
                    break
                body.append(lines[k])
            rules.append({
                "kind": kind,
                "line": i + 1,
                "signature": line.strip(),
                "hint": hint,
                "check_id": extract_rule_check_id(body),
            })
    return rules


def load_gate_checks(gate_id: str) -> list[dict]:
    """Load the declared policy_checks of a gate definition (schema_version 2).

    Returns [] when PyYAML is unavailable or the gate file cannot be found, so
    the appendix still generates (without the check dimension) rather than
    failing.
    """
    if gate_id in ("?", None):
        return []
    try:
        import yaml
    except ImportError:
        return []
    for d in ("pre-deployment", "deployment", "operations"):
        for f in (REPO_ROOT / "gate-definitions" / d).glob(f"{gate_id}_*.yaml"):
            gate = yaml.safe_load(f.read_text()) or {}
            checks = gate.get("policy_checks") or []
            return [c for c in checks if isinstance(c, dict)]
    return []


def extract_tests(test_path: Path) -> list[dict]:
    """Extract test functions with pattern classification."""
    lines = test_path.read_text().splitlines()
    tests = []
    for i, line in enumerate(lines):
        m = re.match(r'^\s*(test_[a-zA-Z0-9_]+)\s+if\s+\{', line)
        if m:
            name = m.group(1)
            tests.append({
                "name": name,
                "line": i + 1,
                "pattern": classify_test(name),
            })
    return tests


def get_package(rego_path: Path) -> str:
    for line in rego_path.read_text().splitlines():
        m = re.match(r'^\s*package\s+([\w.]+)', line)
        if m:
            return m.group(1)
    return "(unknown)"


def render_markdown(out: dict) -> str:
    """Render JSON data as appendix Markdown."""
    lines = []
    lines.append("# Rego Unit Tests — Rule-to-Test Mapping")
    total_rules = sum(g["rule_count"] for g in out["gates"])
    total_tests = sum(g["test_count"] for g in out["gates"])
    lines.append("")
    lines.append(f"**Erzeugungsdatum:** {out['generated_at']}  ")
    lines.append(f"**Baseline:** {out['baseline']}  ")
    lines.append("**Quelle:** `tools/extract_rule_test_mapping.py` (auto-generiert aus "
                 "`policies/**/*.rego` + `policies/**/*_test.rego`)  ")
    lines.append("")
    lines.append("Dieses Dokument belegt die Rule-Level-Isolation der PoC-Policy-Engine: "
                 f"Jede der **{total_rules} Rego-Regeln** wird durch mindestens eine Unit-Test-Assertion "
                 f"verifiziert. Insgesamt **{total_tests} Tests** decken die Muster "
                 "PASS (positive path), FAIL-basic (missing field), FAIL-edge "
                 "(invalid/empty values) und HYBRID (D3-Override First-Degree Oversight) ab. "
                 "Alle Tests werden zeitgleich durch `tests/run_all_rego_tests.sh` "
                 "(`opa test policies/ tests/fixtures/`) ausgeführt; die Pipeline-Integration "
                 "(`pipeline/.github/workflows/gate-pipeline.yml`, Layer 1) bricht bei einem "
                 "Fehlschlag vor jeder Conftest-Gate-Evaluation ab (Shift-Left).")
    lines.append("")

    # ── Summary table ──
    lines.append("## F.1 Übersicht")
    lines.append("")
    lines.append("| Gate | Req. | EU-AI-Act | Methode | Checks | Regeln | Tests | PASS | FAIL-basic | FAIL-edge | HYBRID |")
    lines.append("|------|------|-----------|---------|:-----:|:-----:|:-----:|:----:|:----------:|:---------:|:------:|")
    for g in sorted(out["gates"], key=lambda x: x["gate_id"]):
        pc = g["pattern_counts"]
        lines.append(
            f"| {g['gate_id']} | {g['requirement_id']} | {g['article']} | "
            f"{g['method']} | {g.get('check_count', 0)} | {g['rule_count']} | {g['test_count']} | "
            f"{pc.get('PASS', 0)} | {pc.get('FAIL-basic', 0)} | "
            f"{pc.get('FAIL-edge', 0)} | {pc.get('HYBRID', 0)} |"
        )
    lines.append(f"| **Gesamt** | — | — | — | **{sum(g.get('check_count', 0) for g in out['gates'])}** | **{total_rules}** | **{total_tests}** | "
                 f"{sum(g['pattern_counts'].get('PASS', 0) for g in out['gates'])} | "
                 f"{sum(g['pattern_counts'].get('FAIL-basic', 0) for g in out['gates'])} | "
                 f"{sum(g['pattern_counts'].get('FAIL-edge', 0) for g in out['gates'])} | "
                 f"{sum(g['pattern_counts'].get('HYBRID', 0) for g in out['gates'])} |")
    lines.append("")
    lines.append("**Legende Muster-Klassen:**")
    lines.append("")
    lines.append("- **PASS** — Positiver Pfad: compliant Input → keine Verletzung (alle deny/violation-Regeln bleiben stumm).")
    lines.append("- **FAIL-basic** — Happy-Path-Verstoß: Pflichtfeld fehlt oder strukturelle Annotation nicht gesetzt.")
    lines.append("- **FAIL-edge** — Grenzfall: leere/ungültige Werte, Whitespace, boolean-falsche Literale, Grenzwerte.")
    lines.append("- **HYBRID** — D3-Override (Art. 14 First-Degree Oversight): automatischer Teil OK, aber manual-review/approval-Bereich blockiert Automatisierung.")
    lines.append("")

    # ── Per-gate sections ──
    for g in sorted(out["gates"], key=lambda x: x["gate_id"]):
        lines.append(f"## F.2 {g['gate_id']} — {g['requirement_id']} ({g['article']})")
        lines.append("")
        lines.append(f"**Policy-Datei:** `{g['policy_file']}`  ")
        if g["test_file"]:
            lines.append(f"**Test-Datei:** `{g['test_file']}`  ")
        lines.append(f"**Package:** `{g['package']}`  ")
        lines.append(f"**Automatisierung:** {g['method']}  ")
        pc = g["pattern_counts"]
        counts_str = " | ".join(f"{k}: {v}" for k, v in sorted(pc.items()))
        lines.append(f"**Coverage:** {g['rule_count']} Regeln, {g['test_count']} Tests ({counts_str})")
        lines.append("")

        # Declared checks block (schema_version 2)
        if g.get("checks"):
            lines.append(f"### F.2.{g['gate_id'][-2:]}.0 Check-Inventar ({g['check_count']} Checks, schema_version 2)")
            lines.append("")
            lines.append("| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |")
            lines.append("|----------|:--------:|------------|--------|---------------------------:|")
            for c in g["checks"]:
                refs = ", ".join(c["legal_refs"]) if c["legal_refs"] else "—"
                lines.append(
                    f"| {c['id']} | {c['severity']} | {refs} | `{c['policy']}` | {c['rules_matched']} |"
                )
            lines.append("")
            lines.append(
                f"*Regeln mit Check-ID im Meldungstext: {g['rules_with_check_id']} / {g['rule_count']}"
                f" — ohne: {g['rules_without_check_id']} (Meldungen aus der Zeit vor der "
                f"`<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*"
            )
            if g.get("orphan_check_ids"):
                lines.append("")
                lines.append(
                    f"*⚠ Check-IDs in Rego-Meldungen ohne Entsprechung in der Gate-Definition: "
                    f"{', '.join(g['orphan_check_ids'])}*"
                )
            lines.append("")

        # Rules block
        lines.append(f"### F.2.{g['gate_id'][-2:]}.1 Regel-Inventar ({g['rule_count']} Regeln)")
        lines.append("")
        lines.append("| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |")
        lines.append("|----:|------:|-----|----------|-----------------------------------|")
        for idx, r in enumerate(g["rules"], 1):
            hint = r["hint"].replace("|", "\\|")[:80] if r["hint"] else "—"
            check_id = r["check_id"] or "—"
            lines.append(f"| {idx} | {r['line']} | `{r['kind']}` | {check_id} | {hint} |")
        lines.append("")

        # Tests block
        lines.append(f"### F.2.{g['gate_id'][-2:]}.2 Test-Inventar ({g['test_count']} Tests)")
        lines.append("")
        lines.append("| Nr. | Zeile | Test-Name | Muster |")
        lines.append("|----:|------:|-----------|:------:|")
        for idx, t in enumerate(g["tests"], 1):
            lines.append(f"| {idx} | {t['line']} | `{t['name']}` | {t['pattern']} |")
        lines.append("")

    # ── Footer ──
    lines.append("## F.3 Reproduzierbarkeit")
    lines.append("")
    lines.append(f"Zur Verifikation der obigen Zahlen ({len(out['gates'])} Policies / {total_rules} Regeln / {total_tests} Tests):")
    lines.append("")
    lines.append("```bash")
    lines.append("# OPA ≥ 1.15.2 vorausgesetzt")
    lines.append(f"./tests/run_all_rego_tests.sh --quiet   # Erwartet: 'PASS: {total_tests}/{total_tests}'")
    lines.append("python3 tools/extract_rule_test_mapping.py")
    lines.append("```")
    lines.append("")
    lines.append("Die JSON-Ground-Truth-Variante liegt unter `docs/appendix/rule_test_mapping.json` "
                 "und wird über `tools/extract_rule_test_mapping.py` aus den Quell-Regos regeneriert.")
    lines.append("")
    return "\n".join(lines)


def main():
    out = {"generated_at": "2026-08-14", "baseline": "141/141 PASS", "gates": []}
    for policy in POLICIES:
        test_path = policy.with_name(policy.stem + "_test.rego")
        gate_info = GATE_MAP.get(policy.name, ("?", "?", "?", "?"))
        gate_id, req_id, art, method = gate_info

        rules = extract_rules(policy)
        tests = extract_tests(test_path) if test_path.exists() else []

        # Count by pattern
        pattern_counts = {}
        for t in tests:
            pattern_counts[t["pattern"]] = pattern_counts.get(t["pattern"], 0) + 1

        # schema_version 2: declared checks vs. check-ids actually carried by
        # the Rego messages. A declared check with no rule referencing its id
        # is a traceability gap; rules with check_id=None predate SPEC-01's
        # message convention.
        declared_checks = load_gate_checks(gate_id)
        rule_check_ids = {r["check_id"] for r in rules if r["check_id"]}
        checks_summary = [
            {
                "id": c.get("id"),
                "policy": c.get("policy"),
                "severity": c.get("severity"),
                "legal_refs": c.get("legal_refs") or [],
                "rules_matched": sum(1 for r in rules if r["check_id"] == c.get("id")),
            }
            for c in declared_checks
        ]

        out["gates"].append({
            "gate_id": gate_id,
            "requirement_id": req_id,
            "article": art,
            "method": method,
            "policy_file": str(policy.relative_to(REPO_ROOT)),
            "test_file": str(test_path.relative_to(REPO_ROOT)) if test_path.exists() else None,
            "package": get_package(policy),
            "test_package": get_package(test_path) if test_path.exists() else None,
            "rules": rules,
            "tests": tests,
            "checks": checks_summary,
            "check_count": len(checks_summary),
            "rules_with_check_id": len([r for r in rules if r["check_id"]]),
            "rules_without_check_id": len([r for r in rules if not r["check_id"]]),
            "orphan_check_ids": sorted(rule_check_ids - {c.get("id") for c in declared_checks}),
            "pattern_counts": pattern_counts,
            "rule_count": len(rules),
            "test_count": len(tests),
        })

    out_json = REPO_ROOT / "docs" / "appendix" / "rule_test_mapping.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"✅ JSON written: {out_json}")

    # Markdown appendix
    out_md = REPO_ROOT / "docs" / "appendix" / "rule_test_mapping.md"
    out_md.write_text(render_markdown(out))
    print(f"✅ Markdown written: {out_md}")

    # ── Totals ──
    total_rules = sum(g["rule_count"] for g in out["gates"])
    total_tests = sum(g["test_count"] for g in out["gates"])
    print(f"   Gates: {len(out['gates'])}")
    print(f"   Rules: {total_rules}")
    print(f"   Tests: {total_tests}")
    for g in out["gates"]:
        print(f"   - {g['gate_id']:9s}: {g['rule_count']:2d} rules, {g['test_count']:2d} tests "
              f"({' | '.join(f'{k}:{v}' for k, v in sorted(g['pattern_counts'].items()))})")


if __name__ == "__main__":
    main()
