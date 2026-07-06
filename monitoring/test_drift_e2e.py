#!/usr/bin/env python3
"""
test_drift_e2e.py — End-to-End Test for Drift Detection Pipeline

Simulates the complete drift detection lifecycle:
  Phase A: Init baseline from fixture
  Phase B: Check normal data → expect OK (no drift)
  Phase C: Check drifted data → expect CRITICAL + Evidence Store recording
  Phase D: Verify Evidence Store hash chain

This proves the full G-OPS-03 pipeline:
  drift_detector.py → Evidence Store → Hash-Chain Verification

What this proves (Overview):
  1. Baseline initialization works
  2. Normal operation does NOT trigger false alarms
  3. Drifted data IS detected as CRITICAL
  4. CRITICAL drift is automatically recorded in the Evidence Store
  5. The Evidence Store hash chain remains VALID (tamper-proof)
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

REPO_ROOT = Path(__file__).resolve().parent.parent
DRIFT_DETECTOR = REPO_ROOT / "monitoring" / "drift_detector.py"
VERIFY_CHAIN = REPO_ROOT / "evidence-store" / "scripts" / "verify_hash_chain.py"
FIXTURES = REPO_ROOT / "monitoring" / "fixtures"

passed = 0
failed = 0


def run_cmd(args, expect_exit=0):
    """Run command and return (stdout, stderr, exit_code)."""
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def check(condition, label):
    global passed, failed
    if condition:
        print(f"  {GREEN}PASS{RESET} {label}")
        passed += 1
    else:
        print(f"  {RED}FAIL{RESET} {label}")
        failed += 1


# Use temp files for this test
baseline_tmp = tempfile.mktemp(suffix=".json", prefix="e2e_baseline_")
sqlite_tmp = tempfile.mktemp(suffix=".db", prefix="e2e_evidence_")

print(f"\n{BOLD}{'═' * 60}{RESET}")
print(f"{BOLD}  GenAIOps — Drift Detection End-to-End Test{RESET}")
print(f"{BOLD}{'═' * 60}{RESET}\n")

# ══════════════════════════════════════════════════════════════
# Phase A: Initialize baseline
# ══════════════════════════════════════════════════════════════
print(f"{BOLD}Phase A: Initialize baseline from fixture{RESET}")

stdout, stderr, rc = run_cmd([
    sys.executable, str(DRIFT_DETECTOR),
    "--init-baseline",
    "--source", str(FIXTURES / "baseline_normal.json"),
    "--baseline", baseline_tmp,
])

check(rc == 0, f"--init-baseline exit code = 0 (actual: {rc})")
check(os.path.exists(baseline_tmp), f"Baseline file created: {baseline_tmp}")

if os.path.exists(baseline_tmp):
    with open(baseline_tmp) as f:
        bl = json.load(f)
    check("features" in bl, "Baseline has 'features' key")
    check(len(bl["features"]) == 3, f"Baseline has 3 features (actual: {len(bl['features'])})")

# ══════════════════════════════════════════════════════════════
# Phase B: Check normal data → expect OK
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Phase B: Normal data → expect OK (no drift, no evidence){RESET}")

stdout, stderr, rc = run_cmd([
    sys.executable, str(DRIFT_DETECTOR),
    "--source", str(FIXTURES / "current_normal.json"),
    "--baseline", baseline_tmp,
    "--record-evidence",
    "--sqlite", sqlite_tmp,
])

check(rc == 0, f"Normal check exit code = 0 (actual: {rc})")
check("OK" in stdout, "Output contains 'OK'")
check("evidence" not in stdout.lower() or "recorded" not in stdout.lower(),
      "No evidence recorded (PSI/JSD below threshold)")

# Evidence Store should NOT exist yet (no drift = no recording)
check(not os.path.exists(sqlite_tmp), "No SQLite DB created (no drift to record)")

# ══════════════════════════════════════════════════════════════
# Phase C: Check drifted data → expect CRITICAL + Evidence
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Phase C: Drifted data → expect CRITICAL + Evidence Store recording{RESET}")

stdout, stderr, rc = run_cmd([
    sys.executable, str(DRIFT_DETECTOR),
    "--source", str(FIXTURES / "current_drifted.json"),
    "--baseline", baseline_tmp,
    "--record-evidence",
    "--sqlite", sqlite_tmp,
])

check(rc == 1, f"Drifted check exit code = 1 (CRITICAL) (actual: {rc})")
check("CRITICAL" in stdout, "Output contains 'CRITICAL'")
check("evidence" in stdout.lower(), "Evidence Store recording confirmed in output")

# Check Evidence Store was created with a record
check(os.path.exists(sqlite_tmp), "SQLite DB created by Evidence Store")

# ══════════════════════════════════════════════════════════════
# Phase D: Verify hash chain
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Phase D: Verify Evidence Store hash chain{RESET}")

stdout, stderr, rc = run_cmd([
    sys.executable, str(VERIFY_CHAIN),
    "--sqlite", sqlite_tmp,
    "--verbose",
])

check(rc == 0, f"Hash chain verification exit code = 0 (VALID) (actual: {rc})")
check("VALID" in stdout, "Chain verified as VALID")

# Check the record details
check("G-OPS-03" in stdout, "Evidence record contains G-OPS-03 gate")
check("FAIL" in stdout, "Evidence record decision = FAIL")

# ══════════════════════════════════════════════════════════════
# Cleanup
# ══════════════════════════════════════════════════════════════
for f in [baseline_tmp, sqlite_tmp]:
    try:
        os.unlink(f)
    except OSError:
        pass

# ══════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════
total = passed + failed
print(f"\n{BOLD}{'═' * 60}{RESET}")
print(f"{BOLD}  End-to-End Test Results{RESET}")
print(f"{BOLD}{'═' * 60}{RESET}")
print(f"  {GREEN}PASSED: {passed}{RESET}  /  {RED}FAILED: {failed}{RESET}  /  Total: {total}")

if failed == 0:
    print(f"\n  {GREEN}{BOLD}✓ ALL TESTS PASSED — Full drift pipeline verified{RESET}")
    print(f"\n  {BOLD}What was proven (Overview):{RESET}")
    print("  1. Baseline can be initialized from fixture data")
    print("  2. Normal data → OK status, NO false alarms, NO evidence recorded")
    print("  3. Drifted data → CRITICAL status, pipeline returns exit code 1")
    print("  4. CRITICAL drift → automatic FAIL recording in Evidence Store")
    print("  5. Evidence Store hash chain remains VALID (tamper-proof)")
    print("  6. Complete pipeline: drift_detector → Evidence Store → Hash-Chain")
    print(f"\n  {BOLD}Architecture verification:{RESET}")
    print("  Pillar S5 (Monitoring) → Pillar S4 (Evidence Store) → DP5 (Tamper Evidence)")
    print("  G-OPS-03 operationalized through automated drift detection")
else:
    print(f"\n  {RED}{BOLD}✗ SOME TESTS FAILED — review above{RESET}")

print(f"{BOLD}{'═' * 60}{RESET}\n")
sys.exit(1 if failed > 0 else 0)
