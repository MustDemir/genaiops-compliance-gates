#!/usr/bin/env python3
"""
test_hash_chain_migration.py — v03 → v04 hash-chain migration guard (SPEC-03).

Schema v04 adds `ai_act_role` to the hashed payload. The chosen migration
variant does NOT rehash existing records: the field enters the payload only
from a per-database cutoff audit_id onwards. Records below the cutoff keep the
13-field v03 payload, records at or above it use the 14-field v04 payload.

The decisive property is that a chain SPANNING the cutoff still verifies
end-to-end. Everything else in this file exists to make that assertion
meaningful:

  1. a pure v03 chain verifies                       (no regression)
  2. a chain spanning the cutoff verifies            (the migration works)
  3. tampering below the cutoff is still detected    (v03 records stay protected)
  4. tampering with ai_act_role above the cutoff is detected
     (the role is genuinely tamper-protected — the reason for hashing it
      instead of parking it in the unhashed `notes` column)

Exit codes: 0 = all properties hold, 1 = at least one failed.
"""

import importlib.util
import sqlite3
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RECORD = REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py"
VERIFY = REPO_ROOT / "evidence-store" / "scripts" / "verify_hash_chain.py"

CUTOFF_KEY = "ai_act_role_payload_from_audit_id"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


record = _load(RECORD, "record_evidence")
verify = _load(VERIFY, "verify_hash_chain")


V03_SCHEMA = """
CREATE TABLE quality_gate_results (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    gate_type TEXT NOT NULL,
    decision TEXT NOT NULL,
    decision_method TEXT NOT NULL DEFAULT 'AUTO',
    gate_name TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    payload_id TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    inserted_by TEXT NOT NULL DEFAULT 'poc_local',
    hash_value TEXT NOT NULL,
    previous_hash TEXT,
    notes TEXT
)
"""


def _base_fields(n: int) -> dict:
    return {
        "model_name": "ambient-ai-scribe",
        "model_version": "1.0.0-mock",
        "pipeline_id": "poc-local",
        "run_id": f"run-{n:04d}",
        "gate_type": "Technisch",
        "decision": "PASS",
        "decision_method": "AUTO",
        "gate_name": f"G-PRE-{n:02d}",
        "policy_version": "1.0.0",
        "payload_id": f"payload-{n:04d}",
        "checked_at": f"2026-08-14T00:00:{n:02d}.000000+00:00",
        "inserted_by": "pipeline_automation",
    }


def _insert(conn, n: int, previous_hash: str, role: str, include_role: bool) -> str:
    f = _base_fields(n)
    h = record.compute_hash(
        previous_hash=previous_hash,
        ai_act_role=role,
        include_ai_act_role=include_role,
        **f,
    )
    cols = list(f) + ["hash_value", "previous_hash", "notes"]
    vals = list(f.values()) + [h, previous_hash or None, ""]
    if include_role:
        cols.insert(-3, "ai_act_role")
        vals.insert(-3, role)
    conn.execute(
        f"INSERT INTO quality_gate_results ({','.join(cols)}) "
        f"VALUES ({','.join('?' * len(cols))})",
        vals,
    )
    conn.commit()
    return h


def _fetch(db_path: str) -> list[dict]:
    return verify.fetch_records_sqlite(db_path)


def _cutoff(db_path: str):
    return verify.fetch_role_cutoff_sqlite(db_path)


def _check(name: str, condition: bool, detail: str = "") -> bool:
    print(f"  [{'OK' if condition else 'FAIL'}] {name}")
    if not condition and detail:
        print(f"        {detail}")
    return condition


def main() -> int:
    ok = True
    print("Hash-chain v03 -> v04 migration (SPEC-03):")

    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "chain.db")
        conn = sqlite3.connect(db_path)
        conn.executescript(V03_SCHEMA)

        # ── Phase 1: pure v03 chain, three records ──
        prev = ""
        for n in (1, 2, 3):
            prev = _insert(conn, n, prev, role="DEPLOYER", include_role=False)

        valid, count, err = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path))
        ok &= _check(f"pure v03 chain verifies ({count} records)", valid and count == 3, err)

        # ── Phase 2: run the migration ──
        conn.execute(
            "ALTER TABLE quality_gate_results "
            "ADD COLUMN ai_act_role TEXT NOT NULL DEFAULT 'DEPLOYER'"
        )
        conn.execute("CREATE TABLE schema_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        next_id = conn.execute(
            "SELECT COALESCE(MAX(audit_id), 0) + 1 FROM quality_gate_results"
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO schema_metadata (key, value) VALUES (?, ?)",
            (CUTOFF_KEY, str(next_id)),
        )
        conn.commit()
        ok &= _check(f"migration sets cutoff to audit_id {next_id}", next_id == 4,
                     f"expected 4, got {next_id}")

        # ── Phase 3: two v04 records above the cutoff ──
        for n in (4, 5):
            prev = _insert(conn, n, prev, role="BOTH", include_role=True)

        # ── THE decisive assertion: chain spanning the cutoff ──
        valid, count, err = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path))
        ok &= _check(
            f"chain spanning the cutoff verifies ({count} records, 3x v03 + 2x v04)",
            valid and count == 5,
            err,
        )

        # ── Phase 4: tampering below the cutoff is still detected ──
        conn.execute("UPDATE quality_gate_results SET decision='FAIL' WHERE audit_id=2")
        conn.commit()
        valid, _, _ = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path))
        ok &= _check("tampering with a v03 record is detected", not valid,
                     "a modified pre-cutoff record still verified as intact")
        conn.execute("UPDATE quality_gate_results SET decision='PASS' WHERE audit_id=2")
        conn.commit()

        # ── Phase 5: the role itself is tamper-protected above the cutoff ──
        conn.execute("UPDATE quality_gate_results SET ai_act_role='DEPLOYER' WHERE audit_id=5")
        conn.commit()
        valid, _, _ = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path))
        ok &= _check("tampering with ai_act_role above the cutoff is detected", not valid,
                     "the role was silently changed without breaking the chain — "
                     "it is NOT actually protected")

        conn.close()

    if ok:
        print("\nMIGRATION OK — the cutoff variant keeps old records verifiable "
              "and protects ai_act_role from the cutoff onwards.")
        return 0
    print("\nMIGRATION BROKEN — see failures above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
