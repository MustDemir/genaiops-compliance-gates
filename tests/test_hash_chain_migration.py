#!/usr/bin/env python3
"""
test_hash_chain_migration.py — hash-chain migration guard (v03 -> v04 -> v05).

Two fields moved into the hashed payload: `ai_act_role` (v04, SPEC-03) and
`derived_decision` (v05 — the gate outcome block|manual_review|warn|approve,
which previously sat in the UNHASHED notes column). Neither migration rehashes
existing records: each field enters the payload only from its own per-database
cutoff audit_id. The cutoffs are independent, so one chain can legitimately
hold 13-, 14- and 15-field records at the same time.

The decisive property is that a chain SPANNING the cutoff still verifies
end-to-end. Everything else in this file exists to make that assertion
meaningful:

  1. a pure v03 chain verifies                       (no regression)
  2. a chain spanning the cutoff verifies            (the migration works)
  3. tampering below the cutoff is still detected    (v03 records stay protected)
  4. tampering with a newly hashed field above its cutoff is detected
     (the field is genuinely protected — the reason for hashing it at all)
  5. back-filling such a field BELOW its cutoff leaves every hash unchanged
     — that is the silent-tamper primitive the NULL rule exists for — and
     the verifier must reject it
  6. a chain carrying all three payload generations still verifies

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
DERIVED_KEY = "derived_decision_payload_from_audit_id"
RUNTIME_KEY = "runtime_mode_payload_from_audit_id"


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


def _derived_cutoff(db_path: str):
    return verify.fetch_derived_cutoff_sqlite(db_path)


def _runtime_cutoff(db_path: str):
    return verify.fetch_runtime_cutoff_sqlite(db_path)


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

        valid, count, err = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path),
                                                derived_cutoff=_derived_cutoff(db_path))
        ok &= _check(f"pure v03 chain verifies ({count} records)", valid and count == 3, err)

        # ── Phase 2: run the migration ──
        # Nullable, no default: pre-cutoff rows must stay NULL. A
        # `NOT NULL DEFAULT 'DEPLOYER'` here would stamp every historical
        # record with an unauthenticated role — see phase 6.
        conn.execute(
            "ALTER TABLE quality_gate_results ADD COLUMN ai_act_role TEXT"
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
        valid, count, err = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path),
                                                derived_cutoff=_derived_cutoff(db_path))
        ok &= _check(
            f"chain spanning the cutoff verifies ({count} records, 3x v03 + 2x v04)",
            valid and count == 5,
            err,
        )

        # ── Phase 4: tampering below the cutoff is still detected ──
        conn.execute("UPDATE quality_gate_results SET decision='FAIL' WHERE audit_id=2")
        conn.commit()
        valid, _, _ = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path),
                                                derived_cutoff=_derived_cutoff(db_path))
        ok &= _check("tampering with a v03 record is detected", not valid,
                     "a modified pre-cutoff record still verified as intact")
        conn.execute("UPDATE quality_gate_results SET decision='PASS' WHERE audit_id=2")
        conn.commit()

        # ── Phase 5: the role itself is tamper-protected above the cutoff ──
        conn.execute("UPDATE quality_gate_results SET ai_act_role='DEPLOYER' WHERE audit_id=5")
        conn.commit()
        valid, _, _ = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path),
                                                derived_cutoff=_derived_cutoff(db_path))
        ok &= _check("tampering with ai_act_role above the cutoff is detected", not valid,
                     "the role was silently changed without breaking the chain — "
                     "it is NOT actually protected")
        conn.execute("UPDATE quality_gate_results SET ai_act_role='BOTH' WHERE audit_id=5")
        conn.commit()

        # ── Phase 6: the silent-tamper primitive below the cutoff ──
        # Pre-cutoff rows are outside the hashed payload, so writing a role
        # there changes no hash at all: the chain stays byte-identical and an
        # archived head hash still matches. That is a stronger primitive than
        # rewriting the chain, and it is exactly why those rows must stay NULL
        # and why the verifier has to reject a value there explicitly.
        head_before = _fetch(db_path)[-1]["hash_value"]
        conn.execute("UPDATE quality_gate_results SET ai_act_role='PROVIDER' WHERE audit_id < 4")
        conn.commit()
        head_after = _fetch(db_path)[-1]["hash_value"]

        ok &= _check("back-filling a pre-cutoff role leaves every hash unchanged",
                     head_before == head_after,
                     "precondition of this test no longer holds")

        valid, _, err = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path),
                                                derived_cutoff=_derived_cutoff(db_path))
        ok &= _check("a role back-filled below the cutoff is rejected", not valid,
                     "the verifier accepted an unauthenticated role on historical "
                     "records — an auditor would read it as chain-verified")

        conn.execute("UPDATE quality_gate_results SET ai_act_role=NULL WHERE audit_id < 4")
        conn.commit()
        valid, _, _ = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path),
                                                derived_cutoff=_derived_cutoff(db_path))
        ok &= _check("NULL on pre-cutoff records verifies cleanly", valid,
                     "the honest state must not be reported as tampering")

        # ── Phase 7: a missing role AT/ABOVE the cutoff is equally loud ──
        conn.execute("UPDATE quality_gate_results SET ai_act_role=NULL WHERE audit_id=5")
        conn.commit()
        valid, _, _ = verify.verify_chain(_fetch(db_path), role_cutoff=_cutoff(db_path),
                                                derived_cutoff=_derived_cutoff(db_path))
        ok &= _check("a NULL role at/above the cutoff is rejected", not valid,
                     "a hash-covered record without a role went unnoticed")

        # ── Phase 8: second migration on top (v04 -> v05) ──
        # Two independent cutoffs must coexist: after this the chain holds
        # 13-, 14- and 15-field records at once.
        conn.execute("UPDATE quality_gate_results SET ai_act_role='BOTH' WHERE audit_id=5")
        conn.execute("ALTER TABLE quality_gate_results ADD COLUMN derived_decision TEXT")
        next_id2 = conn.execute(
            "SELECT COALESCE(MAX(audit_id), 0) + 1 FROM quality_gate_results"
        ).fetchone()[0]
        conn.execute("INSERT INTO schema_metadata (key, value) VALUES (?, ?)",
                     (DERIVED_KEY, str(next_id2)))
        conn.commit()

        prev = conn.execute(
            "SELECT hash_value FROM quality_gate_results ORDER BY audit_id DESC LIMIT 1"
        ).fetchone()[0]
        f = _base_fields(6)
        h = record.compute_hash(previous_hash=prev, ai_act_role="DEPLOYER",
                                include_ai_act_role=True,
                                derived_decision="manual_review",
                                include_derived_decision=True, **f)
        cols = list(f) + ["ai_act_role", "derived_decision", "hash_value", "previous_hash", "notes"]
        vals = list(f.values()) + ["DEPLOYER", "manual_review", h, prev, ""]
        conn.execute(
            f"INSERT INTO quality_gate_results ({','.join(cols)}) "
            f"VALUES ({','.join('?' * len(cols))})", vals)
        conn.commit()

        valid, count, err = verify.verify_chain(
            _fetch(db_path), role_cutoff=_cutoff(db_path),
            derived_cutoff=_derived_cutoff(db_path))
        ok &= _check(
            f"chain with three payload generations verifies ({count} records: v03 + v04 + v05)",
            valid and count == 6, err)

        # ── Phase 9: derived_decision is tamper-protected too ──
        conn.execute("UPDATE quality_gate_results SET derived_decision='approve' WHERE audit_id=6")
        conn.commit()
        valid, _, _ = verify.verify_chain(
            _fetch(db_path), role_cutoff=_cutoff(db_path),
            derived_cutoff=_derived_cutoff(db_path))
        ok &= _check("changing derived_decision above its cutoff is detected", not valid,
                     "manual_review could be rewritten to approve without breaking the chain")
        conn.execute("UPDATE quality_gate_results SET derived_decision='manual_review' WHERE audit_id=6")
        conn.commit()

        # ── Phase 10: back-filling it below its cutoff is rejected ──
        head_before = _fetch(db_path)[-1]["hash_value"]
        conn.execute("UPDATE quality_gate_results SET derived_decision='approve' WHERE audit_id < 6")
        conn.commit()
        ok &= _check("back-filling derived_decision leaves every hash unchanged",
                     _fetch(db_path)[-1]["hash_value"] == head_before,
                     "precondition of this test no longer holds")
        valid, _, _ = verify.verify_chain(
            _fetch(db_path), role_cutoff=_cutoff(db_path),
            derived_cutoff=_derived_cutoff(db_path))
        ok &= _check("a derived_decision back-filled below its cutoff is rejected", not valid,
                     "an unauthenticated gate outcome went unnoticed")

        # ── Phase 11: third migration on top (v05 -> v06, SPEC-04) ──
        # Three independent cutoffs must coexist: the chain now legitimately
        # holds 13-, 14-, 15- and 16-field records at once. If the array-based
        # payload build had been a branch tree, this is where it would have
        # needed eight copies of the field list.
        conn.execute("UPDATE quality_gate_results SET derived_decision=NULL WHERE audit_id < 6")
        conn.execute("ALTER TABLE quality_gate_results ADD COLUMN runtime_mode TEXT")
        next_id3 = conn.execute(
            "SELECT COALESCE(MAX(audit_id), 0) + 1 FROM quality_gate_results"
        ).fetchone()[0]
        conn.execute("INSERT INTO schema_metadata (key, value) VALUES (?, ?)",
                     (RUNTIME_KEY, str(next_id3)))
        conn.commit()

        prev = conn.execute(
            "SELECT hash_value FROM quality_gate_results ORDER BY audit_id DESC LIMIT 1"
        ).fetchone()[0]
        f = _base_fields(7)
        h = record.compute_hash(previous_hash=prev, ai_act_role="DEPLOYER",
                                include_ai_act_role=True,
                                derived_decision="approve",
                                include_derived_decision=True,
                                runtime_mode="mock", include_runtime_mode=True, **f)
        cols = list(f) + ["ai_act_role", "derived_decision", "runtime_mode",
                          "hash_value", "previous_hash", "notes"]
        vals = list(f.values()) + ["DEPLOYER", "approve", "mock", h, prev, ""]
        conn.execute(
            f"INSERT INTO quality_gate_results ({','.join(cols)}) "
            f"VALUES ({','.join('?' * len(cols))})", vals)
        conn.commit()

        def _verify():
            return verify.verify_chain(
                _fetch(db_path), role_cutoff=_cutoff(db_path),
                derived_cutoff=_derived_cutoff(db_path),
                runtime_cutoff=_runtime_cutoff(db_path))

        valid, count, err = _verify()
        ok &= _check(
            f"chain with four payload generations verifies ({count} records: v03..v06)",
            valid and count == 7, err)

        # ── Phase 12: the whole point — a mock run cannot be relabelled live ──
        # This is what option C buys and option A/B did not: the mock PASS
        # stays a PASS, but nobody can turn it into a live PASS afterwards.
        conn.execute("UPDATE quality_gate_results SET runtime_mode='live' WHERE audit_id=7")
        conn.commit()
        valid, _, _ = _verify()
        ok &= _check("relabelling a mock run as live is detected", not valid,
                     "a mock PASS could be rewritten into a live PASS without "
                     "breaking the chain — the field would be decorative")
        conn.execute("UPDATE quality_gate_results SET runtime_mode='mock' WHERE audit_id=7")
        conn.commit()

        # ── Phase 13: no back-fill below the cutoff ──
        # For runtime_mode this matters twice over: nobody KNOWS what mode the
        # older runs were in, because the gauge was never read. A back-filled
        # 'live' would be inventing the very fact the column exists to record.
        head_before = _fetch(db_path)[-1]["hash_value"]
        conn.execute("UPDATE quality_gate_results SET runtime_mode='live' WHERE audit_id < 7")
        conn.commit()
        ok &= _check("back-filling runtime_mode leaves every hash unchanged",
                     _fetch(db_path)[-1]["hash_value"] == head_before,
                     "precondition of this test no longer holds")
        valid, _, _ = _verify()
        ok &= _check("a runtime_mode back-filled below its cutoff is rejected", not valid,
                     "an invented runtime mode on historical records went unnoticed")
        conn.execute("UPDATE quality_gate_results SET runtime_mode=NULL WHERE audit_id < 7")
        conn.commit()

        # ── Phase 14: NULL at/above the cutoff is equally loud ──
        # Every run happened in SOME mode, even if that mode is 'unknown'.
        conn.execute("UPDATE quality_gate_results SET runtime_mode=NULL WHERE audit_id=7")
        conn.commit()
        valid, _, _ = _verify()
        ok &= _check("a NULL runtime_mode at/above the cutoff is rejected", not valid,
                     "a hash-covered record without a runtime mode went unnoticed")

        conn.close()

    if ok:
        print("\nMIGRATION OK — the cutoff variant keeps old records verifiable "
              "and protects ai_act_role, derived_decision and runtime_mode "
              "from their respective cutoffs onwards.")
        return 0
    print("\nMIGRATION BROKEN — see failures above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
