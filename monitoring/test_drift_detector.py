#!/usr/bin/env python3
"""
test_drift_detector.py — Unit Tests for drift_detector.py

Tests PSI and JSD computations with known distributions,
then runs drift_detector against fixture files.

Phase 9.3: Verifies mathematical correctness before live deployment.
"""

import sys
from pathlib import Path

# Add parent to path so we can import drift_detector functions
sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift_detector import compute_psi, compute_jsd, check_drift, load_distribution_from_file

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

passed = 0
failed = 0


def assert_close(actual, expected, tolerance, label):
    """Assert that actual is within tolerance of expected."""
    global passed, failed
    if abs(actual - expected) <= tolerance:
        print(f"  {GREEN}PASS{RESET} {label}: {actual:.6f} (expected ~{expected}, tol={tolerance})")
        passed += 1
    else:
        print(f"  {RED}FAIL{RESET} {label}: {actual:.6f} (expected ~{expected}, diff={abs(actual-expected):.6f})")
        failed += 1


def assert_true(condition, label):
    """Assert a boolean condition."""
    global passed, failed
    if condition:
        print(f"  {GREEN}PASS{RESET} {label}")
        passed += 1
    else:
        print(f"  {RED}FAIL{RESET} {label}")
        failed += 1


# ══════════════════════════════════════════════════════════════
# Test 1: Identical distributions → PSI = 0, JSD = 0
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 1: Identical distributions → PSI=0, JSD=0{RESET}")
p = [0.2, 0.3, 0.3, 0.1, 0.1]
psi_identical = compute_psi(p, p)
jsd_identical = compute_jsd(p, p)
assert_close(psi_identical, 0.0, 1e-10, "PSI(P, P)")
assert_close(jsd_identical, 0.0, 1e-10, "JSD(P, P)")


# ══════════════════════════════════════════════════════════════
# Test 2: Uniform distributions → PSI = 0, JSD = 0
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 2: Two uniform distributions → PSI=0, JSD=0{RESET}")
u = [0.25, 0.25, 0.25, 0.25]
psi_uniform = compute_psi(u, u)
jsd_uniform = compute_jsd(u, u)
assert_close(psi_uniform, 0.0, 1e-10, "PSI(U, U)")
assert_close(jsd_uniform, 0.0, 1e-10, "JSD(U, U)")


# ══════════════════════════════════════════════════════════════
# Test 3: Known shift → PSI should be positive, JSD bounded
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 3: Known shift → PSI > 0, JSD > 0{RESET}")
baseline = [0.5, 0.3, 0.2]
shifted = [0.2, 0.3, 0.5]  # Reversed — should show significant drift

psi_shifted = compute_psi(baseline, shifted)
jsd_shifted = compute_jsd(baseline, shifted)

# PSI for this specific case: manual calculation
# (0.2-0.5)*ln(0.2/0.5) + (0.3-0.3)*ln(1) + (0.5-0.2)*ln(0.5/0.2)
# = (-0.3)*(-0.9163) + 0 + (0.3)*(0.9163) = 0.2749 + 0.2749 = 0.5498
assert_close(psi_shifted, 0.5498, 0.001, "PSI([.5,.3,.2], [.2,.3,.5])")
assert_true(jsd_shifted > 0.05, f"JSD > 0.05 (actual: {jsd_shifted:.6f})")
assert_true(psi_shifted > 0.2, f"PSI > 0.2 = CRITICAL (actual: {psi_shifted:.6f})")


# ══════════════════════════════════════════════════════════════
# Test 4: Small shift → PSI < 0.1 (no drift)
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 4: Small shift → PSI < 0.1 (within normal range){RESET}")
baseline_small = [0.20, 0.30, 0.30, 0.10, 0.10]
shifted_small = [0.21, 0.29, 0.31, 0.10, 0.09]

psi_small = compute_psi(baseline_small, shifted_small)
jsd_small = compute_jsd(baseline_small, shifted_small)

assert_true(psi_small < 0.1, f"PSI < 0.1 (no drift) (actual: {psi_small:.6f})")
assert_true(jsd_small < 0.05, f"JSD < 0.05 (no drift) (actual: {jsd_small:.6f})")


# ══════════════════════════════════════════════════════════════
# Test 5: PSI is always non-negative
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 5: PSI is always non-negative{RESET}")
assert_true(psi_identical >= 0, "PSI(identical) >= 0")
assert_true(psi_shifted >= 0, "PSI(shifted) >= 0")
assert_true(psi_small >= 0, "PSI(small) >= 0")


# ══════════════════════════════════════════════════════════════
# Test 6: JSD is symmetric
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 6: JSD is symmetric → JSD(P,Q) == JSD(Q,P){RESET}")
jsd_ab = compute_jsd(baseline, shifted)
jsd_ba = compute_jsd(shifted, baseline)
assert_close(jsd_ab, jsd_ba, 1e-10, "JSD(P,Q) == JSD(Q,P)")


# ══════════════════════════════════════════════════════════════
# Test 7: Length mismatch → ValueError
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 7: Distribution length mismatch → ValueError{RESET}")
try:
    compute_psi([0.5, 0.5], [0.33, 0.33, 0.34])
    print(f"  {RED}FAIL{RESET} PSI did not raise ValueError")
    failed += 1
except ValueError:
    print(f"  {GREEN}PASS{RESET} PSI raises ValueError on length mismatch")
    passed += 1

try:
    compute_jsd([0.5, 0.5], [0.33, 0.33, 0.34])
    print(f"  {RED}FAIL{RESET} JSD did not raise ValueError")
    failed += 1
except ValueError:
    print(f"  {GREEN}PASS{RESET} JSD raises ValueError on length mismatch")
    passed += 1


# ══════════════════════════════════════════════════════════════
# Test 8: Fixture test — baseline vs normal (should be OK)
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 8: Fixture — baseline vs current_normal → status OK{RESET}")
baseline_data = load_distribution_from_file(str(FIXTURES_DIR / "baseline_normal.json"))
normal_data = load_distribution_from_file(str(FIXTURES_DIR / "current_normal.json"))

result_normal = check_drift(baseline_data, normal_data)
assert_true(result_normal["overall_status"] == "ok",
            f"Overall status == 'ok' (actual: {result_normal['overall_status']})")
assert_true(result_normal["max_psi"] < 0.1,
            f"PSI < 0.1 warning threshold (actual: {result_normal['max_psi']:.6f})")
assert_true(result_normal["max_jsd"] < 0.05,
            f"JSD < 0.05 warning threshold (actual: {result_normal['max_jsd']:.6f})")

print("  Details per feature:")
for fname, fdata in result_normal["features"].items():
    print(f"    {fname}: PSI={fdata['psi']:.6f} JSD={fdata['jsd']:.6f} [{fdata['status']}]")


# ══════════════════════════════════════════════════════════════
# Test 9: Fixture test — baseline vs drifted (should be CRITICAL)
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}Test 9: Fixture — baseline vs current_drifted → status CRITICAL{RESET}")
drifted_data = load_distribution_from_file(str(FIXTURES_DIR / "current_drifted.json"))

result_drifted = check_drift(baseline_data, drifted_data)
assert_true(result_drifted["overall_status"] == "critical",
            f"Overall status == 'critical' (actual: {result_drifted['overall_status']})")
assert_true(result_drifted["max_psi"] > 0.2,
            f"PSI > 0.2 critical threshold (actual: {result_drifted['max_psi']:.6f})")
assert_true(result_drifted["max_jsd"] > 0.1,
            f"JSD > 0.1 critical threshold (actual: {result_drifted['max_jsd']:.6f})")

print("  Details per feature:")
for fname, fdata in result_drifted["features"].items():
    color = {"ok": GREEN, "warning": YELLOW, "critical": RED}.get(fdata["status"], "")
    print(f"    {fname}: PSI={fdata['psi']:.6f} JSD={fdata['jsd']:.6f} [{color}{fdata['status']}{RESET}]")


# ══════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════
total = passed + failed
print(f"\n{BOLD}{'═' * 55}{RESET}")
print(f"{BOLD}  Drift Detector Unit Test Results{RESET}")
print(f"{BOLD}{'═' * 55}{RESET}")
print(f"  {GREEN}PASSED: {passed}{RESET}  /  {RED}FAILED: {failed}{RESET}  /  Total: {total}")

if failed == 0:
    print(f"\n  {GREEN}{BOLD}✓ ALL TESTS PASSED — PSI/JSD computations verified{RESET}")
    print(f"\n  {BOLD}What was proven:{RESET}")
    print("  1. PSI = 0 for identical distributions (mathematically correct)")
    print("  2. JSD is symmetric (JSD(P,Q) == JSD(Q,P))")
    print("  3. Small variations → status OK (no false alarms)")
    print("  4. Large drift → status CRITICAL (drift detected)")
    print("  5. Input validation works (length mismatch caught)")
else:
    print(f"\n  {RED}{BOLD}✗ SOME TESTS FAILED — review above{RESET}")

print(f"{BOLD}{'═' * 55}{RESET}\n")
sys.exit(1 if failed > 0 else 0)
