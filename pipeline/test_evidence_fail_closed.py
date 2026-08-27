#!/usr/bin/env python3
"""
test_evidence_fail_closed.py — B-16, verified by running it.

The integrity suite can only check that the fail-closed handling is
DECLARED: it reads source text. That is worth having, but a first
version of that check searched for the token `evidence_broken` and kept
passing when the branch was replaced by `if False:` — the name still
appeared at its assignment. A check a probe cannot break is not a check.

So the behaviour is verified here, by breaking the Evidence Store write
and observing what the pipeline does:

    the run must halt, the exit code must be 3 (not 1), and the report
    must say the recording failed.

Exit 3 is deliberately distinct: 1 means a gate blocked and the system
worked; 3 means no result from that run is recorded, so none may be read
as a verdict.

Run:  python3 pipeline/test_evidence_fail_closed.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ORCHESTRATOR = REPO_ROOT / "pipeline" / "gate_orchestrator.py"
RECORDER = REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py"
PREPARE = REPO_ROOT / "pipeline" / "prepare_inputs.py"
SCENARIO = REPO_ROOT / "pipeline" / "scenarios" / "poc_healthcare_pass.json"

GREEN, RED, BOLD, RESET = "\033[92m", "\033[91m", "\033[1m", "\033[0m"
_results = []


def check(ok: bool, label: str) -> None:
    _results.append(ok)
    print(f"  {GREEN}PASS{RESET} {label}" if ok else f"  {RED}FAIL{RESET} {label}")


def run_pipeline() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ORCHESTRATOR), "--scenario", str(SCENARIO)],
        capture_output=True, text=True, timeout=300,
    )


def main() -> int:
    subprocess.run([sys.executable, str(PREPARE), "--scenario", str(SCENARIO)],
                   capture_output=True, text=True)

    print(f"\n{BOLD}A: a healthy run records and exits 0{RESET}")
    healthy = run_pipeline()
    check(healthy.returncode == 0, f"exit 0 with a working recorder (got {healthy.returncode})")

    print(f"\n{BOLD}B: a broken recorder halts the run with its own exit code{RESET}")
    backup = Path(tempfile.mkdtemp()) / "record_evidence.py.bak"
    shutil.copy2(RECORDER, backup)
    try:
        # Exit 9: an Evidence Store that refuses to write, for any reason.
        RECORDER.write_text(
            "import sys\n"
            "# Test double for pipeline/test_evidence_fail_closed.py — refuses to write.\n"
            "sys.exit(9)\n",
            encoding="utf-8",
        )
        broken = run_pipeline()
    finally:
        shutil.copy2(backup, RECORDER)

    check(broken.returncode == 3,
          f"exit 3, distinct from a blocked gate (got {broken.returncode})")
    check("UNRECORDED" in broken.stdout,
          "the run says the gate result is unrecorded rather than reporting a verdict")
    check("EVIDENCE RECORDING FAILED" in broken.stdout,
          "the failure is named, not folded into an ordinary gate failure")

    print(f"\n{BOLD}C: the recorder is intact again{RESET}")
    restored = run_pipeline()
    check(restored.returncode == 0, f"exit 0 after restore (got {restored.returncode})")

    reports = sorted((REPO_ROOT / "evidence-store").glob("pipeline_report_*.json"),
                     key=lambda p: p.stat().st_mtime)
    if reports:
        report = json.loads(reports[-1].read_text(encoding="utf-8"))
        check(report.get("evidence_recording_failed") is False,
              "the report states evidence recording succeeded, so an auditor can tell")

    passed = sum(1 for r in _results if r)
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"  {GREEN}PASSED: {passed}{RESET}  /  {RED}FAILED: {len(_results) - passed}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    return 0 if passed == len(_results) else 1


if __name__ == "__main__":
    sys.exit(main())
