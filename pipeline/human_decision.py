#!/usr/bin/env python3
"""
human_decision.py — what a human decision on a HYBRID gate does to the run.

T-16.1 (ES-1, ES-2), PO decision ES-F1 a of 02.10.2026:

    MANUAL FAIL                      -> block: the run halts at that gate
    HYBRID gate without an approval  -> the run halts ("awaiting approval")
                                        and resumes once an approval exists

Until then the human half of a HYBRID gate was a record without an effect.
Review 12 showed it in a run: G-PRE-05 was rejected by its reviewer, the
rejection went into the Evidence Store (audit 5), and the pipeline carried
on to G-DEP-02. A HYBRID gate without any decision log passed as well —
`manual_review` was a note, not a stop.

Two runners evaluate gates — pipeline/gate_orchestrator.py locally and the
quality-gates job in .github/workflows/gate-pipeline.yml in CI. Both call
this module, so the rule exists once. Two copies of a halt rule drift
apart, and the copy that drifts is the one nobody runs locally.

Which gate is HYBRID is read from the gate definition, never from the
caller. A scenario or a CI list that declares a HYBRID gate as AUTO would
otherwise skip the human half by relabelling it — the same bypass as
omitting a required input (B-11, B-17). A mismatch is a configuration
error (exit 2), not a silent correction.

Scope: the EFFECT of the human decision. What the approval record holds
and whether it is hash-covered is T-16.4 (ES-5); the approval stays a
JSON file at evidence level E-0 (PO 02.10.2026).

CLI (used by CI):

    human_decision.py gate --gate G-PRE-05 --method HYBRID \
        --auto-decision PASS --decision-log <path or ''> --ledger <tsv>
        -> appends one line to the ledger, exit 0 (2 on a config error)

    human_decision.py verdict --ledger <tsv>
        -> exit 0 if every HYBRID gate of the catalogue has an approval,
           exit 1 if any halts or is missing, exit 2 on a config error
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GATE_DEF_DIRS = (
    REPO_ROOT / "gate-definitions" / "pre-deployment",
    REPO_ROOT / "gate-definitions" / "deployment",
    REPO_ROOT / "gate-definitions" / "operations",
)

# Reasons a run halts at a HYBRID gate because of its human half.
REJECTED = "rejected_by_reviewer"
AWAITING = "awaiting_approval"
INVALID = "invalid_approval"
HALT_REASONS = (REJECTED, AWAITING, INVALID)


class ConfigError(Exception):
    """The caller's view of a gate contradicts the catalogue."""


def load_gate_automation() -> dict:
    """Map gate_id -> automation (AUTO / HYBRID / MANUAL) from the gate definitions."""
    import yaml

    automation = {}
    for d in GATE_DEF_DIRS:
        if not d.is_dir():
            continue
        for f in sorted(d.glob("G-*.yaml")):
            gate = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            if gate.get("id"):
                automation[gate["id"]] = str(gate.get("automation", "")).upper()
    return automation


def catalogue_method(gate_id: str, declared: str, automation: dict) -> str:
    """The method the catalogue gives a gate; a contradicting caller is a config error.

    A gate without a definition (none today) keeps the caller's method.
    """
    if gate_id not in automation:
        return declared
    actual = automation[gate_id]
    if declared and declared.upper() != actual:
        raise ConfigError(
            f"{gate_id}: declared as {declared.upper()}, but the gate definition says "
            f"{actual}. A HYBRID gate run as AUTO skips its human half; the catalogue "
            f"decides, not the caller."
        )
    return actual


def load_decision_log(path) -> dict | None:
    """Read a decision log; None if no path is given. A broken file is a config error."""
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        raise ConfigError(f"decision log not found: {path}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"decision log is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"decision log must be a JSON object: {path}")
    return data


def approval_effect(gate_id: str, method: str, auto_decision: str,
                    decision_log: dict | None) -> dict:
    """What the human half of a gate does to the run.

    Returns {"halt": bool, "reason": str|None, "message": str,
             "manual_decision": "PASS"|"FAIL"|None}.

    Only HYBRID gates have a human half. An automatic FAIL halts on its own
    (the existing rule); an approval cannot lift it — there is no waiver path.
    """
    if method != "HYBRID":
        return {"halt": False, "reason": None, "manual_decision": None,
                "message": f"{gate_id}: {method} gate, no human decision required"}

    if decision_log is None:
        return {"halt": True, "reason": AWAITING, "manual_decision": None,
                "message": f"{gate_id}: HYBRID gate without a human decision — the run "
                           f"waits for approval (ES-F1 a)"}

    manual = decision_log.get("decision")
    problems = []
    if decision_log.get("gate_id") != gate_id:
        problems.append(f"the decision log is for {decision_log.get('gate_id')!r}, "
                        f"not for {gate_id}")
    if manual not in ("PASS", "FAIL"):
        problems.append(f"decision is {manual!r}, not PASS or FAIL")
    if not str(decision_log.get("reviewed_by") or "").strip():
        problems.append("reviewed_by is empty — an approval without a reviewer "
                        "is nobody's approval")
    if problems:
        return {"halt": True, "reason": INVALID, "manual_decision": None,
                "message": f"{gate_id}: the approval is not valid — " + "; ".join(problems)}

    if manual == "FAIL":
        return {"halt": True, "reason": REJECTED, "manual_decision": "FAIL",
                "message": f"{gate_id}: rejected by {decision_log['reviewed_by']} — "
                           f"block (ES-F1 a)"}

    if auto_decision == "FAIL":
        # Recorded as approved by the human, but the automatic half blocked.
        # The automatic FAIL halts the run; the approval does not lift it.
        return {"halt": False, "reason": None, "manual_decision": "PASS",
                "message": f"{gate_id}: approved by {decision_log['reviewed_by']}, but the "
                           f"automatic half failed — the gate blocks regardless"}

    return {"halt": False, "reason": None, "manual_decision": "PASS",
            "message": f"{gate_id}: approved by {decision_log['reviewed_by']}"}


# ── CLI (CI) ──────────────────────────────────────────────────────────

def _cmd_gate(args) -> int:
    try:
        automation = load_gate_automation()
        method = catalogue_method(args.gate, args.method, automation)
        log = load_decision_log(args.decision_log)
    except ConfigError as exc:
        print(f"::error::{exc}")
        return 2
    effect = approval_effect(args.gate, method, args.auto_decision, log)
    with open(args.ledger, "a", encoding="utf-8") as f:
        f.write("\t".join([args.gate, method, "HALT" if effect["halt"] else "OK",
                           effect["reason"] or "-", effect["message"]]) + "\n")
    print(("  ⛔ " if effect["halt"] else "  ✅ ") + effect["message"])
    return 0


def _cmd_verdict(args) -> int:
    try:
        automation = load_gate_automation()
    except Exception as exc:  # pragma: no cover - a broken catalogue
        print(f"::error::gate definitions could not be read: {exc}")
        return 2
    seen, halts = {}, []
    ledger = Path(args.ledger)
    lines = ledger.read_text(encoding="utf-8").splitlines() if ledger.is_file() else []
    for line in lines:
        gate, method, state, reason, message = line.split("\t", 4)
        seen[gate] = method
        if state == "HALT":
            halts.append(message)
    hybrid = sorted(g for g, a in automation.items() if a == "HYBRID")
    missing = [g for g in hybrid if g not in seen]
    for g in missing:
        halts.append(f"{g}: HYBRID gate of the catalogue was not evaluated for its "
                     f"human decision — it cannot pass unseen")
    print(f"Human decisions: {len(hybrid)} HYBRID gates in the catalogue, "
          f"{len(hybrid) - len(missing)} evaluated, {len(halts)} halting")
    for h in halts:
        print(f"::error::{h}")
    return 1 if halts else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gate", help="evaluate one gate's human decision into the ledger")
    g.add_argument("--gate", required=True)
    g.add_argument("--method", required=True)
    g.add_argument("--auto-decision", required=True, choices=["PASS", "FAIL"])
    g.add_argument("--decision-log", default="")
    g.add_argument("--ledger", required=True)
    v = sub.add_parser("verdict", help="exit 1 if any HYBRID gate halts or is missing")
    v.add_argument("--ledger", required=True)
    args = parser.parse_args()
    return _cmd_gate(args) if args.cmd == "gate" else _cmd_verdict(args)


if __name__ == "__main__":
    sys.exit(main())
