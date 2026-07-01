#!/usr/bin/env python3
"""
test_tamper_detection.py — Demonstrates that the Evidence Store hash chain
detects tampering (manipulation of stored gate decisions).

This is the "smoking gun" test for the demonstration: it proves that if someone
changes a FAIL to PASS in the database, the hash-chain verification catches it.

Part of the GenAIOps Compliance Gates PoC — Closed Loop Pipeline.

Usage:
    python pipeline/test_tamper_detection.py

Steps:
    1. Run the PASS scenario → all gates pass, chain is VALID
    2. Tamper with the database: change G-DEP-02 from PASS to FAIL
    3. Verify hash chain → chain is CORRUPTED
    4. Print report showing tamper detection works
"""

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ORCHESTRATOR = REPO_ROOT / "pipeline" / "gate_orchestrator.py"
VERIFY_SCRIPT = REPO_ROOT / "evidence-store" / "scripts" / "verify_hash_chain.py"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_command(cmd: list, label: str) -> subprocess.CompletedProcess:
    """Run a command and print its status."""
    print(f"\n{BLUE}[Step] {label}{RESET}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def main():
    print(f"\n{BOLD}{'═' * 70}{RESET}")
    print(f"{BOLD}  TAMPER DETECTION TEST — GenAIOps Evidence Store{RESET}")
    print(f"{BOLD}  Proves: Hash-Chain catches manipulated gate decisions{RESET}")
    print(f"{BOLD}{'═' * 70}{RESET}")

    # Use a dedicated DB in /tmp
    db_path = os.path.join(tempfile.gettempdir(), "evidence_tamper_test.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    # ──────────────────────────────────────────────────
    # Step 1: Run PASS scenario to populate Evidence Store
    # ──────────────────────────────────────────────────
    print(f"\n{BOLD}Phase 1: Populate Evidence Store with valid data{RESET}")

    # Temporarily modify the scenario to use our test DB
    scenario_path = REPO_ROOT / "pipeline" / "scenarios" / "poc_healthcare_pass.json"
    with open(scenario_path, "r") as f:
        scenario = json.load(f)

    # Create a temporary scenario with our test DB name
    tmp_scenario = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, prefix="tamper_scenario_"
    )
    scenario["pipeline"]["evidence_db"] = "evidence_tamper_test.db"
    json.dump(scenario, tmp_scenario, indent=2)
    tmp_scenario.close()

    result = run_command(
        [sys.executable, str(ORCHESTRATOR), "--scenario", tmp_scenario.name],
        "Running PASS scenario to populate Evidence Store..."
    )

    if result.returncode != 0:
        print(f"{RED}ERROR: PASS scenario failed. Cannot continue.{RESET}")
        print(result.stdout[-500:] if result.stdout else "")
        print(result.stderr[-500:] if result.stderr else "")
        os.unlink(tmp_scenario.name)
        sys.exit(2)

    print(f"{GREEN}✓ Evidence Store populated — all gates PASS{RESET}")

    # ──────────────────────────────────────────────────
    # Step 2: Verify chain is VALID before tampering
    # ──────────────────────────────────────────────────
    print(f"\n{BOLD}Phase 2: Verify chain integrity BEFORE tampering{RESET}")

    result = run_command(
        [sys.executable, str(VERIFY_SCRIPT), "--sqlite", db_path, "--verbose"],
        "Verifying hash chain (should be VALID)..."
    )
    print(result.stdout)

    if result.returncode != 0:
        print(f"{RED}ERROR: Chain already invalid before tampering!{RESET}")
        os.unlink(tmp_scenario.name)
        sys.exit(2)

    print(f"{GREEN}✓ Hash chain is VALID — baseline established{RESET}")

    # ──────────────────────────────────────────────────
    # Step 3: TAMPER with the database
    # ──────────────────────────────────────────────────
    print(f"\n{BOLD}Phase 3: SIMULATING ATTACK — Tampering with Evidence Store{RESET}")
    print(f"{RED}  Scenario: An insider changes a FAIL to PASS to bypass compliance{RESET}")

    conn = sqlite3.connect(db_path)

    # Show the record before tampering
    row = conn.execute(
        "SELECT audit_id, gate_name, decision, decision_method, hash_value "
        "FROM quality_gate_results WHERE gate_name = 'G-DEP-02' LIMIT 1"
    ).fetchone()

    if row:
        audit_id, gate_name, decision, method, hash_val = row
        print(f"\n  Target record: audit_id={audit_id}")
        print(f"  Gate: {gate_name} | Decision: {decision} | Method: {method}")
        print(f"  Hash: {hash_val[:32]}...")

        # TAMPER: Change decision from PASS to FAIL (or vice versa)
        new_decision = "FAIL" if decision == "PASS" else "PASS"
        conn.execute(
            "UPDATE quality_gate_results SET decision = ? WHERE audit_id = ?",
            (new_decision, audit_id)
        )
        conn.commit()
        print(f"\n  {RED}{BOLD}✗ TAMPERED: Changed decision from '{decision}' to '{new_decision}'{RESET}")
        print(f"  {RED}  (hash_value was NOT updated — this is the detectable inconsistency){RESET}")
    else:
        print(f"{YELLOW}  No G-DEP-02 record found, tampering audit_id=1 instead{RESET}")
        conn.execute(
            "UPDATE quality_gate_results SET decision = 'FAIL' WHERE audit_id = 1"
        )
        conn.commit()

    conn.close()

    # ──────────────────────────────────────────────────
    # Step 4: Verify chain AFTER tampering — should detect corruption
    # ──────────────────────────────────────────────────
    print(f"\n{BOLD}Phase 4: Verify chain integrity AFTER tampering{RESET}")

    result = run_command(
        [sys.executable, str(VERIFY_SCRIPT), "--sqlite", db_path, "--verbose"],
        "Verifying hash chain (should be CORRUPTED)..."
    )
    print(result.stdout)

    # ──────────────────────────────────────────────────
    # Step 5: Report
    # ──────────────────────────────────────────────────
    print(f"\n{BOLD}{'═' * 70}{RESET}")
    print(f"{BOLD}  TEST RESULT{RESET}")
    print(f"{'═' * 70}")

    if result.returncode == 1:
        print(f"\n  {GREEN}{BOLD}✓ TAMPER DETECTION WORKS{RESET}")
        print(f"  {GREEN}  The hash chain correctly identified the manipulated record.{RESET}")
        print(f"  {GREEN}  An attacker cannot silently change gate decisions without{RESET}")
        print(f"  {GREEN}  breaking the cryptographic chain — this is the core guarantee{RESET}")
        print(f"  {GREEN}  of the Evidence Store (DP5: Tamper Evidence).{RESET}")
        test_passed = True
    else:
        print(f"\n  {RED}{BOLD}✗ TAMPER DETECTION FAILED{RESET}")
        print(f"  {RED}  The hash chain did NOT detect the manipulation!{RESET}")
        test_passed = False

    print(f"\n{BOLD}  Demonstration:{RESET}")
    print("  Jeder Eintrag im Evidence Store enthält einen SHA-256 Hash,")
    print("  der aus allen Feldern des Eintrags PLUS dem Hash des vorherigen")
    print("  Eintrags berechnet wird (Hash-Kette). Wenn jemand einen Eintrag")
    print("  nachträglich ändert (z.B. FAIL→PASS), stimmt der gespeicherte Hash")
    print("  nicht mehr mit dem neu berechneten Hash überein.")
    print("  Das System erkennt: 'Dieser Eintrag wurde manipuliert.'")
    print("  Das entspricht Art. 12 EU AI Act (automatische Protokollierung)")
    print("  und DP5.3 unserer Architektur (Tamper Evidence).")

    print(f"\n{BOLD}{'═' * 70}{RESET}\n")

    # Cleanup
    os.unlink(tmp_scenario.name)

    sys.exit(0 if test_passed else 1)


if __name__ == "__main__":
    main()
