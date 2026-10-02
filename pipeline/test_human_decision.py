#!/usr/bin/env python3
"""
test_human_decision.py — T-16.1 (ES-1, ES-2), verified by running it.

PO decision ES-F1 a of 02.10.2026: a rejection by the reviewer (MANUAL
FAIL) blocks, and a HYBRID gate without an approval halts the run until
one exists. Review 12 showed the opposite in a run: G-PRE-05 rejected,
recorded as audit 5, and the pipeline carried on.

The integrity suite (HUMAN_DECISION_TAKES_EFFECT) checks that both runners
are wired to pipeline/human_decision.py. Whether the wiring ACTS is shown
here, by running the orchestrator on scenarios derived from
poc_healthcare_pass.json, reduced to its two HYBRID gates so the cases
need neither conftest nor prepared measurements:

    A  both approved                       -> exit 0            (counter-check)
    B  G-PRE-05 rejected (MANUAL FAIL)     -> exit 1, halts at G-PRE-05,
                                              reason rejected_by_reviewer,
                                              the rejection is in the store
    C  G-PRE-05 without an approval        -> exit 1, halts at G-PRE-05,
                                              reason awaiting_approval
    D  G-PRE-05 relabelled AUTO            -> exit 2 (scenario contradicts
                                              the catalogue), nothing recorded
    E  G-PRE-05 with G-PRE-01's approval   -> exit 1, reason invalid_approval

and the CI ledger (human_decision.py gate / verdict):

    F  all HYBRID gates approved           -> verdict exit 0    (counter-check)
    G  one rejected                        -> verdict exit 1
    H  one HYBRID gate never evaluated     -> verdict exit 1
    I  a HYBRID gate declared AUTO         -> gate exit 2

Run:  python3 pipeline/test_human_decision.py
"""

import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ORCHESTRATOR = REPO_ROOT / "pipeline" / "gate_orchestrator.py"
HUMAN = REPO_ROOT / "pipeline" / "human_decision.py"
SCENARIO = REPO_ROOT / "pipeline" / "scenarios" / "poc_healthcare_pass.json"
FIXTURES = "scenarios/healthcare-ambient-ai-scribe/fixtures"

sys.path.insert(0, str(REPO_ROOT / "pipeline"))
import human_decision  # noqa: E402

GREEN, RED, BOLD, RESET = "\033[92m", "\033[91m", "\033[1m", "\033[0m"
_results = []
_reports = []
TMP = Path(tempfile.mkdtemp(prefix="t16_1_"))


def check(ok: bool, label: str) -> None:
    _results.append(ok)
    print(f"  {GREEN}PASS{RESET} {label}" if ok else f"  {RED}FAIL{RESET} {label}")


def scenario(case: str, gpre05: dict) -> Path:
    """poc_healthcare_pass reduced to G-PRE-01 and G-PRE-05, G-PRE-05 modified."""
    base = json.loads(SCENARIO.read_text(encoding="utf-8"))
    gates = [g for g in base["gates"] if g["gate_id"] in ("G-PRE-01", "G-PRE-05")]
    for g in gates:
        if g["gate_id"] == "G-PRE-05":
            for k, v in gpre05.items():
                if v is None:
                    g.pop(k, None)
                else:
                    g[k] = v
    base["gates"] = gates
    base["pipeline"]["evidence_db"] = f"evidence_t16_1_{case}.db"
    path = TMP / f"scenario_{case}.json"
    path.write_text(json.dumps(base, indent=2), encoding="utf-8")
    return path


def run(path: Path) -> tuple[subprocess.CompletedProcess, dict | None]:
    proc = subprocess.run([sys.executable, str(ORCHESTRATOR), "--scenario", str(path)],
                          capture_output=True, text=True, timeout=300)
    report = None
    for line in proc.stdout.splitlines():
        if "Pipeline report saved:" in line:
            name = line.split("Pipeline report saved:")[1].strip().split()[0]
            name = name.replace("\x1b[0m", "")
            _reports.append(REPO_ROOT / "evidence-store" / name)
            report = json.loads(_reports[-1].read_text(encoding="utf-8"))
    return proc, report


def store_rows(case: str) -> list:
    db = REPO_ROOT / "evidence-store" / f"evidence_t16_1_{case}.db"
    if not db.exists():
        return []
    with sqlite3.connect(db) as conn:
        return conn.execute("SELECT gate_name, decision, decision_method, inserted_by "
                            "FROM quality_gate_results ORDER BY audit_id").fetchall()


def main() -> int:
    approved = json.loads((REPO_ROOT / FIXTURES / "decision_log_gpre05_manual.json")
                          .read_text(encoding="utf-8"))
    rejected = dict(approved, decision="FAIL",
                    review_outcome="Strategic governance approval refused",
                    rationale="Evidence incomplete — test double for T-16.1.")
    rejected_path = TMP / "decision_log_gpre05_rejected.json"
    rejected_path.write_text(json.dumps(rejected, indent=2), encoding="utf-8")

    print(f"\n{BOLD}A: both HYBRID gates approved — the run passes (counter-check){RESET}")
    proc, rep = run(scenario("approved", {}))
    check(proc.returncode == 0, f"exit 0 (got {proc.returncode})")
    check(rep is not None and rep.get("halt_reason") is None, "the report names no halt")

    print(f"\n{BOLD}B: G-PRE-05 rejected by the reviewer — block (ES-1){RESET}")
    proc, rep = run(scenario("rejected", {"manual_source": str(rejected_path)}))
    check(proc.returncode == 1, f"exit 1 (got {proc.returncode})")
    check(rep is not None and rep.get("halt_gate") == "G-PRE-05",
          f"halts at G-PRE-05 (got {rep and rep.get('halt_gate')})")
    check(rep is not None and rep.get("halt_reason") == human_decision.REJECTED,
          f"reason {human_decision.REJECTED} (got {rep and rep.get('halt_reason')})")
    rows = store_rows("rejected")
    check(("G-PRE-05", "FAIL", "MANUAL", approved["reviewed_by"]) in rows,
          "the rejection is in the Evidence Store as a MANUAL FAIL by the reviewer")

    print(f"\n{BOLD}C: G-PRE-05 without an approval — the run waits (ES-2){RESET}")
    proc, rep = run(scenario("awaiting", {"manual_source": None}))
    check(proc.returncode == 1, f"exit 1 (got {proc.returncode})")
    check(rep is not None and rep.get("halt_gate") == "G-PRE-05",
          f"halts at G-PRE-05 (got {rep and rep.get('halt_gate')})")
    check(rep is not None and rep.get("halt_reason") == human_decision.AWAITING,
          f"reason {human_decision.AWAITING} (got {rep and rep.get('halt_reason')})")

    print(f"\n{BOLD}D: G-PRE-05 relabelled AUTO — the scenario is refused{RESET}")
    proc, _ = run(scenario("relabelled", {"method": "AUTO", "manual_source": None}))
    check(proc.returncode == 2, f"exit 2, a configuration error (got {proc.returncode})")
    check("definition says HYBRID" in proc.stdout, "the run names the contradiction")
    check(not store_rows("relabelled"), "nothing was recorded")

    print(f"\n{BOLD}E: G-PRE-05 carries G-PRE-01's approval — not an approval{RESET}")
    proc, rep = run(scenario("foreign", {
        "manual_source": f"{FIXTURES}/decision_log_gpre01_manual.json"}))
    check(proc.returncode == 1, f"exit 1 (got {proc.returncode})")
    check(rep is not None and rep.get("halt_reason") == human_decision.INVALID,
          f"reason {human_decision.INVALID} (got {rep and rep.get('halt_reason')})")

    # ── CI ledger ──
    hybrid = sorted(g for g, a in human_decision.load_gate_automation().items()
                    if a == "HYBRID")

    def ledger(case: str, entries: dict) -> tuple[Path, list]:
        path = TMP / f"ledger_{case}.tsv"
        codes = []
        for gate, (method, log) in entries.items():
            codes.append(subprocess.run(
                [sys.executable, str(HUMAN), "gate", "--gate", gate, "--method", method,
                 "--auto-decision", "PASS", "--decision-log", log, "--ledger", str(path)],
                capture_output=True, text=True).returncode)
        return path, codes

    def verdict(path: Path) -> int:
        return subprocess.run([sys.executable, str(HUMAN), "verdict", "--ledger", str(path)],
                              capture_output=True, text=True).returncode

    # One approval per gate, made for that gate from G-PRE-05's file.
    logs = {}
    for gate in hybrid:
        p = TMP / f"approval_{gate}.json"
        p.write_text(json.dumps(dict(approved, gate_id=gate)), encoding="utf-8")
        logs[gate] = str(p)

    print(f"\n{BOLD}F: CI — all {len(hybrid)} HYBRID gates approved (counter-check){RESET}")
    path, codes = ledger("all", {g: ("HYBRID", logs[g]) for g in hybrid})
    check(codes == [0] * len(hybrid), f"every gate call exits 0 (got {codes})")
    check(verdict(path) == 0, "verdict exit 0")

    print(f"\n{BOLD}G: CI — one HYBRID gate rejected{RESET}")
    entries = {g: ("HYBRID", logs[g]) for g in hybrid}
    entries["G-PRE-05"] = ("HYBRID", str(rejected_path))
    path, _ = ledger("rejected", entries)
    check(verdict(path) == 1, "verdict exit 1")

    print(f"\n{BOLD}H: CI — one HYBRID gate left out of the list{RESET}")
    path, _ = ledger("missing", {g: ("HYBRID", logs[g]) for g in hybrid if g != "G-OPS-06"})
    check(verdict(path) == 1, "verdict exit 1 — a gate cannot pass unseen")

    print(f"\n{BOLD}I: CI — a HYBRID gate declared AUTO{RESET}")
    _, codes = ledger("relabelled", {"G-OPS-01": ("AUTO", "")})
    check(codes == [2], f"gate call exits 2 (got {codes})")

    # The runs leave their stores and reports in evidence-store/ (gitignored).
    for f in (REPO_ROOT / "evidence-store").glob("evidence_t16_1_*.db"):
        f.unlink()
    for f in _reports:
        f.unlink(missing_ok=True)

    passed, total = sum(_results), len(_results)
    color = GREEN if passed == total else RED
    print(f"\n{color}{BOLD}{passed}/{total} checks passed{RESET}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
