#!/usr/bin/env python3
"""
test_hybrid_gate_integration.py — End-to-End Integration Test for HYBRID Gates.

Addresses Reviewer Finding K1:
  "No end-to-end test exists that puts AUTO + MANUAL records into
   the same hash chain and then verifies the entire chain."

Test scenario (Healthcare Ambient AI Scribe):
  1. Record 4 AUTO gate decisions (G-PRE-01, G-PRE-04, G-DEP-02, G-OPS-03)
  2. Record 2 MANUAL gate decisions (G-PRE-01 manual review, G-PRE-05 governance)
  3. Verify the complete 6-record chain is valid
  4. Tamper with one record → verify chain detects corruption
  5. Verify HYBRID semantics: same gate can have both AUTO and MANUAL entries

Run:
    python -m pytest tests/test_hybrid_gate_integration.py -v
    # or directly:
    python tests/test_hybrid_gate_integration.py
"""

import hashlib
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent dir so we can import the scripts
SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from record_evidence import (
    GENESIS_HASH,
    POC_DEFAULTS,
    build_record,
    compute_hash,
    get_previous_hash_sqlite,
    init_sqlite,
    insert_sqlite,
    load_source,
)
from verify_hash_chain import fetch_records_sqlite, verify_chain

# Fixture paths relative to repo root
REPO_ROOT = SCRIPT_DIR.parent.parent
FIXTURES = REPO_ROOT / "scenarios" / "healthcare-ambient-ai-scribe" / "fixtures"


class TestHybridGateIntegration(unittest.TestCase):
    """End-to-end test: AUTO + MANUAL decisions in a single hash chain."""

    def setUp(self):
        """Create a temporary SQLite DB for each test."""
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        self.conn = init_sqlite(self.db_path)

    def tearDown(self):
        """Clean up temporary DB."""
        self.conn.close()
        os.unlink(self.db_path)

    def _record(self, gate: str, method: str, source_data: dict, run_id: str = None) -> dict:
        """Helper: build and insert a record, return the record dict."""
        prev = get_previous_hash_sqlite(self.conn)
        record = build_record(gate, method, source_data, prev, run_id=run_id)
        audit_id = insert_sqlite(self.conn, record)
        record["audit_id"] = audit_id
        return record

    def _auto_source(self, gate: str, passed: bool = True) -> dict:
        """Generate a minimal AUTO source (like Conftest output)."""
        return {
            "gate_id": gate,
            "failures": [] if passed else [{"rule": "test_rule", "msg": "failed"}],
            "payload_id": f"auto-{gate}-{id(self)}",
        }

    def test_e2e_mixed_chain_valid(self):
        """
        K1 Core Test: 4 AUTO + 2 MANUAL records form a valid chain.
        Simulates a real pipeline run for the Healthcare Ambient AI Scribe.
        """
        run_id = "e2e-hybrid-test-run-001"

        # --- Phase 1: AUTO decisions (pipeline runs through) ---
        r1 = self._record("G-PRE-01", "AUTO", self._auto_source("G-PRE-01"), run_id)
        r2 = self._record("G-PRE-04", "AUTO", self._auto_source("G-PRE-04"), run_id)
        r3 = self._record("G-DEP-02", "AUTO", self._auto_source("G-DEP-02"), run_id)
        r4 = self._record("G-OPS-03", "AUTO", self._auto_source("G-OPS-03"), run_id)

        # --- Phase 2: MANUAL decisions (async, from decision logs) ---
        manual_gpre01 = {
            "gate_id": "G-PRE-01",
            "decision": "PASS",
            "decision_method": "MANUAL",
            "reviewed_by": "Dr. Sarah Chen (Compliance Officer)",
            "rationale": "Risk classification confirmed: High-Risk per Annex III, 5(b)",
            "payload_id": "manual-gpre01-test",
        }
        r5 = self._record("G-PRE-01", "MANUAL", manual_gpre01, run_id)

        manual_gpre05 = {
            "gate_id": "G-PRE-05",
            "decision": "PASS",
            "decision_method": "MANUAL",
            "reviewed_by": "Prof. Dr. Weber (AI Governance Lead)",
            "rationale": "Strategic governance approval granted with conditions",
            "payload_id": "manual-gpre05-test",
        }
        r6 = self._record("G-PRE-05", "MANUAL", manual_gpre05, run_id)

        # --- Verify chain ---
        records = fetch_records_sqlite(self.db_path)
        self.assertEqual(len(records), 6, "Should have 6 records in chain")

        is_valid, count, error_msg = verify_chain(records)
        self.assertTrue(is_valid, f"Chain should be valid. Errors: {error_msg}")
        self.assertEqual(count, 6)

        # Verify decision_method distribution
        methods = [r["decision_method"] for r in records]
        self.assertEqual(methods.count("AUTO"), 4, "Should have 4 AUTO records")
        self.assertEqual(methods.count("MANUAL"), 2, "Should have 2 MANUAL records")

        # Verify G-PRE-01 appears twice (AUTO + MANUAL = HYBRID pattern)
        gpre01_records = [r for r in records if r["gate_name"] == "G-PRE-01"]
        self.assertEqual(len(gpre01_records), 2, "G-PRE-01 should have 2 entries (AUTO+MANUAL)")
        gpre01_methods = {r["decision_method"] for r in gpre01_records}
        self.assertEqual(gpre01_methods, {"AUTO", "MANUAL"}, "G-PRE-01 should have both AUTO and MANUAL")

    def test_tamper_detection_mid_chain(self):
        """Tamper with record 3 of 6 → records 3+ should show cascading failure."""
        run_id = "tamper-test-run-001"

        # Insert 4 AUTO + 2 MANUAL
        self._record("G-PRE-01", "AUTO", self._auto_source("G-PRE-01"), run_id)
        self._record("G-PRE-04", "AUTO", self._auto_source("G-PRE-04"), run_id)
        self._record("G-DEP-02", "AUTO", self._auto_source("G-DEP-02"), run_id)
        self._record("G-OPS-03", "AUTO", self._auto_source("G-OPS-03"), run_id)
        self._record("G-PRE-01", "MANUAL", {
            "gate_id": "G-PRE-01", "decision": "PASS",
            "decision_method": "MANUAL", "reviewed_by": "Test Reviewer",
            "rationale": "Test", "payload_id": "tamper-manual-1",
        }, run_id)
        self._record("G-PRE-05", "MANUAL", {
            "gate_id": "G-PRE-05", "decision": "PASS",
            "decision_method": "MANUAL", "reviewed_by": "Test Reviewer",
            "rationale": "Test", "payload_id": "tamper-manual-2",
        }, run_id)

        # Tamper: change decision of record 3 (G-DEP-02) from PASS to FAIL
        self.conn.execute(
            "UPDATE quality_gate_results SET decision = 'FAIL' WHERE audit_id = 3"
        )
        self.conn.commit()

        records = fetch_records_sqlite(self.db_path)
        is_valid, count, error_msg = verify_chain(records)

        self.assertFalse(is_valid, "Tampered chain should be detected as CORRUPTED")
        self.assertIn("audit_id=3", error_msg, "Error should reference tampered record")

    def test_tamper_detection_manual_record(self):
        """Tamper with a MANUAL record specifically — ensures MANUAL entries are hash-protected too."""
        run_id = "tamper-manual-test"

        self._record("G-PRE-01", "AUTO", self._auto_source("G-PRE-01"), run_id)
        self._record("G-PRE-01", "MANUAL", {
            "gate_id": "G-PRE-01", "decision": "PASS",
            "decision_method": "MANUAL", "reviewed_by": "Dr. Chen",
            "rationale": "Approved", "payload_id": "tamper-target",
        }, run_id)
        self._record("G-DEP-02", "AUTO", self._auto_source("G-DEP-02"), run_id)

        # Tamper: change MANUAL decision from PASS to FAIL
        self.conn.execute(
            "UPDATE quality_gate_results SET decision = 'FAIL' WHERE audit_id = 2"
        )
        self.conn.commit()

        records = fetch_records_sqlite(self.db_path)
        is_valid, count, error_msg = verify_chain(records)

        self.assertFalse(is_valid, "Tampered MANUAL record should be detected")
        self.assertIn("audit_id=2", error_msg)

    def test_chain_linkage_genesis(self):
        """First record's previous_hash should be GENESIS_HASH."""
        self._record("G-PRE-01", "AUTO", self._auto_source("G-PRE-01"))

        records = fetch_records_sqlite(self.db_path)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["previous_hash"], GENESIS_HASH,
                         "First record must reference GENESIS_HASH")

    def test_chain_linkage_sequential(self):
        """Each record's previous_hash must equal the prior record's hash_value."""
        for gate in ["G-PRE-01", "G-PRE-04", "G-DEP-02"]:
            self._record(gate, "AUTO", self._auto_source(gate))

        records = fetch_records_sqlite(self.db_path)
        for i in range(1, len(records)):
            self.assertEqual(
                records[i]["previous_hash"],
                records[i - 1]["hash_value"],
                f"Record {i+1} previous_hash must equal record {i} hash_value",
            )

    def test_decision_method_constraint(self):
        """SQLite should reject invalid decision_method values."""
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """INSERT INTO quality_gate_results
                   (model_name, model_version, pipeline_id, run_id, gate_type,
                    decision, decision_method, gate_name, policy_version, payload_id,
                    checked_at, inserted_by, hash_value, previous_hash)
                   VALUES ('m','1','p','r','Technisch','PASS','INVALID','G-TEST','1',
                           'pid','2026-01-01','test','hash','prev')""",
            )

    def test_hybrid_non_blocking_semantics(self):
        """
        D_HYBRID_NONBLOCKING: AUTO runs through pipeline first, MANUAL comes async.
        All records share the same run_id but different decision_methods.
        """
        run_id = "nonblocking-test-run"

        # Simulate: full AUTO pipeline runs through
        auto_gates = ["G-PRE-01", "G-PRE-04", "G-DEP-02", "G-OPS-03"]
        for gate in auto_gates:
            self._record(gate, "AUTO", self._auto_source(gate), run_id)

        # Verify: chain is already valid after AUTO-only
        records_auto = fetch_records_sqlite(self.db_path)
        is_valid, _, _ = verify_chain(records_auto)
        self.assertTrue(is_valid, "Chain must be valid after AUTO-only phase")

        # Simulate: MANUAL decisions arrive later (async)
        self._record("G-PRE-01", "MANUAL", {
            "gate_id": "G-PRE-01", "decision": "PASS",
            "decision_method": "MANUAL", "reviewed_by": "Dr. Chen",
            "rationale": "Review complete", "payload_id": "async-manual-1",
        }, run_id)

        # Chain remains valid after MANUAL extension
        records_full = fetch_records_sqlite(self.db_path)
        is_valid, count, error_msg = verify_chain(records_full)
        self.assertTrue(is_valid, f"Chain must remain valid after MANUAL append. Errors: {error_msg}")
        self.assertEqual(count, 5, "Should have 5 records (4 AUTO + 1 MANUAL)")

        # All share same run_id
        run_ids = {r["run_id"] for r in records_full}
        self.assertEqual(len(run_ids), 1, "All records should share the same run_id")
        self.assertEqual(run_ids.pop(), run_id)

    def test_with_real_fixtures(self):
        """Use actual fixture files from the PoC scenario if available."""
        manual_gpre01_path = FIXTURES / "decision_log_gpre01_manual.json"
        manual_gpre05_path = FIXTURES / "decision_log_gpre05_manual.json"

        if not manual_gpre01_path.exists():
            self.skipTest("Fixture files not found — run from repo root")

        run_id = "fixture-test-run"

        # AUTO records
        self._record("G-PRE-01", "AUTO", self._auto_source("G-PRE-01"), run_id)
        self._record("G-DEP-02", "AUTO", self._auto_source("G-DEP-02"), run_id)

        # MANUAL from real fixtures
        with open(manual_gpre01_path) as f:
            gpre01_data = json.load(f)
        self._record("G-PRE-01", "MANUAL", gpre01_data, run_id)

        with open(manual_gpre05_path) as f:
            gpre05_data = json.load(f)
        self._record("G-PRE-05", "MANUAL", gpre05_data, run_id)

        # Verify
        records = fetch_records_sqlite(self.db_path)
        is_valid, count, error_msg = verify_chain(records)
        self.assertTrue(is_valid, f"Chain with real fixtures should be valid. Errors: {error_msg}")
        self.assertEqual(count, 4)

        # Verify MANUAL records have correct inserter
        manual_records = [r for r in records if r["decision_method"] == "MANUAL"]
        for r in manual_records:
            self.assertNotEqual(r["inserted_by"], "pipeline_automation",
                                "MANUAL records should have human reviewer as inserted_by")


if __name__ == "__main__":
    unittest.main(verbosity=2)
