#!/usr/bin/env python3
"""
record_evidence.py — Persist Quality Gate decisions to the Evidence Store.

Part of the GenAIOps Compliance Gates PoC (Phase 8).
Supports both PostgreSQL (production) and SQLite (local testing).

Usage:
    # Record AUTO decision from Conftest output
    python record_evidence.py --gate G-PRE-01 --method AUTO \
        --source fixtures/conftest_output.json

    # Record MANUAL decision from Decision Log
    python record_evidence.py --gate G-PRE-01 --method MANUAL \
        --source fixtures/decision_log_gpre01_manual.json

    # Local test with SQLite (no PostgreSQL required)
    python record_evidence.py --gate G-PRE-01 --method AUTO \
        --source fixtures/conftest_output.json --sqlite evidence_test.db

Design decisions:
    - E13: Unified table with decision_method column (no separate tables)
    - Hash computed client-side AND verified against DB trigger (double-write)
    - Genesis-Eintrag: previous_hash ist leer (NULL in DB, "" im Hash-Payload);
      die DB-Trigger-Funktion compliance.set_hash_chain() setzt den Wert auf
      NULL beim Genesis-Eintrag und kodiert via coalesce(NEW.previous_hash, '').
    - Client sends timestamp; DB DEFAULT as fallback
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

# Default model info for PoC scenario
POC_DEFAULTS = {
    "model_name": "ambient-ai-scribe",
    "model_version": "1.0.0-mock",
    "pipeline_id": "poc-local",
    "gate_type_map": {
        "G-PRE-01": "Regulatorisch",
        "G-PRE-04": "Technisch",
        "G-PRE-05": "Strategisch",
        "G-DEP-02": "Technisch",
        "G-OPS-03": "Technisch",
        "G-OPS-05": "Regulatorisch",
    },
    "policy_version": "1.0.0",
}


# ────────────────────────────────────────────────────────────────
# Schema v04 (SPEC-03): ai_act_role in der Hash-Payload
# ────────────────────────────────────────────────────────────────
# Die Rolle (PROVIDER/DEPLOYER/BOTH) entscheidet, welche Gates ueberhaupt
# laufen, und ist damit auditrelevant: sie gehoert in die gehashte Payload,
# nicht in das ungehashte `notes`-Feld.
#
# Migrationsvariante (abgestimmt): das Feld wird NICHT rueckwirkend Teil der
# Payload, sondern erst ab einem pro Datenbank festgelegten audit_id. Records
# davor bleiben mit 13 Feldern verifizierbar, Records danach mit 14. Damit
# bricht die Aufnahme des Feldes keine bestehende Kette — auch nicht in einer
# langlebigen PostgreSQL-Instanz, die ueber die Migration hinweg fortgeschrieben
# wird.
#
# Der Schwellenwert steht in der Tabelle schema_metadata und wird gesetzt:
#   - bei einer frischen DB auf 1  (alle Records tragen die Rolle)
#   - bei der Migration einer bestehenden DB auf max(audit_id) + 1
# Fehlt der Eintrag, gilt der Default unten — das entspricht einer DB, die
# noch nie migriert wurde, also reines v03-Verhalten.
AI_ACT_ROLE_CUTOFF_KEY = "ai_act_role_payload_from_audit_id"
AI_ACT_ROLE_CUTOFF_DEFAULT = None  # None = Feld nie Teil der Payload (v03)


def compute_hash(
    previous_hash: str,
    model_name: str,
    model_version: str,
    pipeline_id: str,
    run_id: str,
    gate_type: str,
    decision: str,
    decision_method: str,
    gate_name: str,
    policy_version: str,
    payload_id: str,
    checked_at: str,
    inserted_by: str,
    ai_act_role: str = "",
    include_ai_act_role: bool = False,
) -> str:
    """
    Compute the SHA-256 chain hash.

    Field order must stay identical across record_evidence.py,
    verify_hash_chain.py and the SQL trigger (guarded by
    tests/test_hash_parity.py). `ai_act_role` sits directly before
    previous_hash and is only present from the migration cutoff onwards —
    see the comment block above.
    """
    fields = [
        model_name,
        model_version,
        pipeline_id,
        run_id,
        gate_type,
        decision,
        decision_method,
        gate_name,
        policy_version,
        payload_id,
        checked_at,
        inserted_by,
    ]
    if include_ai_act_role:
        fields.append(ai_act_role or "")
    fields.append(previous_hash or "")
    return hashlib.sha256("|".join(fields).encode("utf-8")).hexdigest()


def init_sqlite(db_path: str) -> sqlite3.Connection:
    """Create SQLite DB with schema matching v03 (without PG-specific features)."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quality_gate_results (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_version TEXT NOT NULL,
            pipeline_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            gate_type TEXT NOT NULL CHECK (gate_type IN ('Regulatorisch','Technisch','Strategisch')),
            decision TEXT NOT NULL CHECK (decision IN ('PASS','FAIL')),
            decision_method TEXT NOT NULL DEFAULT 'AUTO' CHECK (decision_method IN ('AUTO','MANUAL','HYBRID')),
            gate_name TEXT NOT NULL,
            policy_version TEXT NOT NULL,
            payload_id TEXT NOT NULL,
            checked_at TEXT NOT NULL,
            inserted_by TEXT NOT NULL DEFAULT 'poc_local',
            -- NULL-faehig und ohne Default, symmetrisch zur PostgreSQL-
            -- Migration v03->v04: NULL heisst "vor Schema v04 geschrieben,
            -- Rolle nicht erfasst und nicht hash-gedeckt". Niemals
            -- nachtraeglich befuellen — verify_hash_chain.py wertet ein
            -- Nicht-NULL unterhalb des Cutoffs als Manipulationssignal.
            -- Bei einer frischen DB ist der Cutoff 1, also traegt ohnehin
            -- jeder Record die Rolle.
            ai_act_role TEXT CHECK (ai_act_role IS NULL OR ai_act_role IN ('PROVIDER','DEPLOYER','BOTH')),
            hash_value TEXT NOT NULL,
            previous_hash TEXT,
            notes TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    # Fresh database: the cutoff is 1, so every record carries ai_act_role
    # in its payload. An existing v03 database gets its cutoff from the
    # migration script instead (max(audit_id) + 1), which is why this is an
    # INSERT OR IGNORE and never overwrites an existing value.
    conn.execute(
        "INSERT OR IGNORE INTO schema_metadata (key, value) VALUES (?, ?)",
        (AI_ACT_ROLE_CUTOFF_KEY, "1"),
    )
    conn.commit()
    return conn


def get_ai_act_role_cutoff_sqlite(conn: sqlite3.Connection):
    """Read the audit_id from which ai_act_role is part of the hash payload."""
    try:
        row = conn.execute(
            "SELECT value FROM schema_metadata WHERE key = ?",
            (AI_ACT_ROLE_CUTOFF_KEY,),
        ).fetchone()
    except sqlite3.OperationalError:
        # schema_metadata does not exist -> never migrated -> v03 behaviour
        return AI_ACT_ROLE_CUTOFF_DEFAULT
    return int(row[0]) if row else AI_ACT_ROLE_CUTOFF_DEFAULT


def get_next_audit_id_sqlite(conn: sqlite3.Connection) -> int:
    """
    Predict the audit_id the next INSERT will receive.

    Needed because the hash is computed before the row exists. Safe here
    because the Evidence Store has a single writer per run; the same
    assumption already underpins get_previous_hash_sqlite().
    """
    row = conn.execute(
        "SELECT COALESCE(MAX(audit_id), 0) + 1 FROM quality_gate_results"
    ).fetchone()
    return int(row[0])


def get_previous_hash_sqlite(conn: sqlite3.Connection) -> str:
    """Get the last hash in the chain, or empty string for the Genesis-Eintrag."""
    row = conn.execute(
        "SELECT hash_value FROM quality_gate_results ORDER BY audit_id DESC LIMIT 1"
    ).fetchone()
    return row[0] if row else ""


def insert_sqlite(conn: sqlite3.Connection, record: dict) -> int:
    """Insert a record into SQLite and return the audit_id."""
    cursor = conn.execute(
        """
        INSERT INTO quality_gate_results
            (model_name, model_version, pipeline_id, run_id, gate_type,
             decision, decision_method, gate_name, policy_version, payload_id,
             checked_at, inserted_by, ai_act_role, hash_value, previous_hash, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["model_name"],
            record["model_version"],
            record["pipeline_id"],
            record["run_id"],
            record["gate_type"],
            record["decision"],
            record["decision_method"],
            record["gate_name"],
            record["policy_version"],
            record["payload_id"],
            record["checked_at"],
            record["inserted_by"],
            record.get("ai_act_role", "DEPLOYER"),
            record["hash_value"],
            record["previous_hash"],
            record.get("notes", ""),
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_pg_connection(db_url: str):
    """Connect to PostgreSQL. Requires psycopg2."""
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 not installed. Use --sqlite for local testing,")
        print("       or install with: pip install psycopg2-binary")
        sys.exit(1)
    return psycopg2.connect(db_url)


def get_previous_hash_pg(conn) -> str:
    """Get the last hash from PostgreSQL, or empty string for the Genesis-Eintrag."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT hash_value FROM compliance.quality_gate_results "
            "ORDER BY audit_id DESC LIMIT 1"
        )
        row = cur.fetchone()
    return row[0] if row else ""


def get_ai_act_role_cutoff_pg(conn):
    """Read the schema-v04 cutoff from PostgreSQL (None if never migrated)."""
    with conn.cursor() as cur:
        try:
            cur.execute(
                "SELECT value FROM compliance.schema_metadata WHERE key = %s",
                (AI_ACT_ROLE_CUTOFF_KEY,),
            )
            row = cur.fetchone()
        except Exception:
            # Table absent -> v03 database -> keep the 13-field payload
            conn.rollback()
            return AI_ACT_ROLE_CUTOFF_DEFAULT
    return int(row[0]) if row else AI_ACT_ROLE_CUTOFF_DEFAULT


def get_next_audit_id_pg(conn) -> int:
    """Predict the audit_id the next INSERT will receive (single writer)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(MAX(audit_id), 0) + 1 FROM compliance.quality_gate_results"
        )
        row = cur.fetchone()
    return int(row[0])


def insert_pg(conn, record: dict) -> int:
    """Insert into PostgreSQL. DB trigger computes hash — we verify match."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO compliance.quality_gate_results
                (model_name, model_version, pipeline_id, run_id, gate_type,
                 decision, decision_method, gate_name, policy_version, payload_id,
                 checked_at, inserted_by, ai_act_role, hash_value, previous_hash, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid, %s, %s, %s, %s, %s, %s)
            RETURNING audit_id, hash_value
            """,
            (
                record["model_name"],
                record["model_version"],
                record["pipeline_id"],
                record["run_id"],
                record["gate_type"],
                record["decision"],
                record["decision_method"],
                record["gate_name"],
                record["policy_version"],
                record["payload_id"],
                record["checked_at"],
                record["inserted_by"],
                record.get("ai_act_role", "DEPLOYER"),
                record["hash_value"],
                record["previous_hash"],
                record.get("notes", ""),
            ),
        )
        audit_id, db_hash = cur.fetchone()
    conn.commit()

    # Double-write verification
    if db_hash != record["hash_value"]:
        print(f"WARNING: Hash mismatch! Client={record['hash_value'][:16]}... "
              f"DB={db_hash[:16]}...")
        print("This indicates the DB trigger and client use different payloads.")

    return audit_id


def validate_gate_id(gate: str) -> None:
    """Validate gate ID format: G-{PRE|DEP|OPS}-{NN}."""
    import re
    if not re.match(r"^G-(PRE|DEP|OPS)-\d{2}$", gate):
        print(f"ERROR: Invalid gate ID '{gate}'. Expected format: G-PRE-01, G-DEP-02, G-OPS-03")
        sys.exit(1)


def validate_source_file(source_path: str) -> None:
    """Validate source file exists and is valid JSON."""
    if not os.path.isfile(source_path):
        print(f"ERROR: Source file not found: {source_path}")
        sys.exit(1)
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"ERROR: Source file must contain a JSON object, got {type(data).__name__}")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {source_path}: {e}")
        sys.exit(1)


def load_source(source_path: str) -> dict:
    """Load and parse a JSON source file."""
    with open(source_path, "r", encoding="utf-8") as f:
        return json.load(f)


def determine_decision(source_data: dict, method: str) -> str:
    """Extract PASS/FAIL decision from source data."""
    # MANUAL sources have explicit decision field
    if "decision" in source_data:
        return source_data["decision"]
    # Conftest output: no failures = PASS
    if "failures" in source_data:
        return "FAIL" if len(source_data["failures"]) > 0 else "PASS"
    # Default: PASS (source was loaded successfully)
    return "PASS"


def build_record(
    gate: str,
    method: str,
    source_data: dict,
    previous_hash: str,
    run_id: str = None,
    ai_act_role: str = "DEPLOYER",
    next_audit_id: int = None,
    role_cutoff: int = None,
) -> dict:
    """
    Build a complete evidence record from gate + method + source.

    `next_audit_id` and `role_cutoff` drive the schema-v04 payload switch:
    ai_act_role only enters the hashed payload once the record's audit_id
    has reached the cutoff recorded for this database. Passing None for
    either keeps the v03 payload, so a database that was never migrated
    behaves exactly as before.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    run_id = run_id or str(uuid.uuid4())
    gate_type = POC_DEFAULTS["gate_type_map"].get(gate, "Technisch")
    decision = determine_decision(source_data, method)
    inserted_by = source_data.get("reviewed_by", "pipeline_automation") if method == "MANUAL" else "pipeline_automation"
    payload_id = source_data.get("payload_id", str(uuid.uuid4()))

    # Notes: rationale for MANUAL decisions, derived decision (schema_version 2,
    # SPEC-01 Abschnitt 5) and SHOULD advisories (warn). `notes` is NOT part of
    # the hashed payload, so this can carry richer detail without affecting
    # hash-chain integrity.
    notes = ""
    if method == "MANUAL" and "rationale" in source_data:
        notes = source_data["rationale"]
    if "derived_decision" in source_data:
        notes = (notes + " | " if notes else "") + f"DERIVED_DECISION: {source_data['derived_decision']}"

    # SPEC-01 Abschnitt 5: violated SHOULD-checks are persisted individually
    # with their check-id, not bundled into one sentence, so an auditor can
    # trace each advisory back to the specific check that raised it.
    advisories = source_data.get("warnings", [])
    for w in advisories:
        if isinstance(w, dict):
            check_id = w.get("check_id")
            msg = w.get("msg", str(w))
        else:
            check_id = None
            msg = str(w)
        tag = f"C={check_id}" if check_id else "C=unmapped"
        notes = (notes + " | " if notes else "") + f"ADVISORY [SHOULD, {tag}]: {msg}"

    include_role = (
        role_cutoff is not None
        and next_audit_id is not None
        and next_audit_id >= role_cutoff
    )

    hash_value = compute_hash(
        previous_hash=previous_hash,
        model_name=POC_DEFAULTS["model_name"],
        model_version=POC_DEFAULTS["model_version"],
        pipeline_id=POC_DEFAULTS["pipeline_id"],
        run_id=run_id,
        gate_type=gate_type,
        decision=decision,
        decision_method=method,
        gate_name=gate,
        policy_version=POC_DEFAULTS["policy_version"],
        payload_id=payload_id,
        checked_at=now,
        inserted_by=inserted_by,
        ai_act_role=ai_act_role,
        include_ai_act_role=include_role,
    )

    return {
        "model_name": POC_DEFAULTS["model_name"],
        "model_version": POC_DEFAULTS["model_version"],
        "pipeline_id": POC_DEFAULTS["pipeline_id"],
        "run_id": run_id,
        "gate_type": gate_type,
        "decision": decision,
        "decision_method": method,
        "gate_name": gate,
        "policy_version": POC_DEFAULTS["policy_version"],
        "payload_id": payload_id,
        "checked_at": now,
        "inserted_by": inserted_by,
        "ai_act_role": ai_act_role,
        "hash_value": hash_value,
        "previous_hash": previous_hash,
        "notes": notes,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Record Quality Gate evidence to the Evidence Store (Phase 8)"
    )
    parser.add_argument("--gate", required=True, help="Gate ID (e.g., G-PRE-01)")
    parser.add_argument(
        "--method", required=True, choices=["AUTO", "MANUAL", "HYBRID"],
        help="Decision method"
    )
    parser.add_argument("--source", required=True, help="Path to JSON source file")
    parser.add_argument(
        "--sqlite", metavar="DB_PATH",
        help="Use SQLite instead of PostgreSQL (local testing)"
    )
    parser.add_argument(
        "--db-url",
        default=os.environ.get("EVIDENCE_STORE_URL"),
        help="PostgreSQL connection URL (or set EVIDENCE_STORE_URL env var)"
    )
    parser.add_argument("--run-id", help="Override run UUID (default: auto-generated)")
    parser.add_argument(
        "--ai-act-role",
        default=os.environ.get("AI_ACT_ROLE", "DEPLOYER"),
        choices=["PROVIDER", "DEPLOYER", "BOTH"],
        help="EU AI Act role this gate ran under (or set AI_ACT_ROLE env var; default: DEPLOYER)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show record without persisting")

    args = parser.parse_args()

    # Input validation
    validate_gate_id(args.gate)
    validate_source_file(args.source)

    # Load source
    source_data = load_source(args.source)
    print(f"[record_evidence] Gate: {args.gate} | Method: {args.method}")
    print(f"[record_evidence] Source: {args.source}")

    if args.sqlite:
        # SQLite mode
        conn = init_sqlite(args.sqlite)
        previous_hash = get_previous_hash_sqlite(conn)
        record = build_record(
            args.gate, args.method, source_data, previous_hash, args.run_id,
            ai_act_role=args.ai_act_role,
            next_audit_id=get_next_audit_id_sqlite(conn),
            role_cutoff=get_ai_act_role_cutoff_sqlite(conn),
        )

        if args.dry_run:
            print(json.dumps(record, indent=2))
            return

        audit_id = insert_sqlite(conn, record)
        conn.close()
        print(f"[record_evidence] Inserted audit_id={audit_id} into SQLite ({args.sqlite})")

    elif args.db_url:
        # PostgreSQL mode
        conn = get_pg_connection(args.db_url)
        previous_hash = get_previous_hash_pg(conn)
        record = build_record(
            args.gate, args.method, source_data, previous_hash, args.run_id,
            ai_act_role=args.ai_act_role,
            next_audit_id=get_next_audit_id_pg(conn),
            role_cutoff=get_ai_act_role_cutoff_pg(conn),
        )

        if args.dry_run:
            print(json.dumps(record, indent=2))
            conn.close()
            return

        audit_id = insert_pg(conn, record)
        conn.close()
        print(f"[record_evidence] Inserted audit_id={audit_id} into PostgreSQL")

    else:
        print("ERROR: Specify --sqlite <path> or --db-url <url> (or EVIDENCE_STORE_URL env var)")
        sys.exit(1)

    print(f"[record_evidence] Decision: {record['decision']} | Hash: {record['hash_value'][:16]}...")
    prev = record['previous_hash']
    print(f"[record_evidence] Previous: {prev[:16] + '...' if prev else '<empty> (Genesis-Eintrag)'}")


if __name__ == "__main__":
    main()
