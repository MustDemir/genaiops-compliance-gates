#!/usr/bin/env python3
"""
verify_hash_chain.py — Verify tamper-evidence of the Quality Gate audit trail.

Part of the GenAIOps Compliance Gates PoC (Phase 8).
Used by the CronJob (cronjob-hash-chain-verify.yaml) every 6 hours,
and manually during the Kap. 6.3 walkthrough.

Exit codes:
    0 = Chain is valid (all hashes match)
    1 = Chain is corrupted (at least one hash mismatch)
    2 = Error (DB connection, empty store, etc.)

Usage:
    # Verify against SQLite (local testing)
    python verify_hash_chain.py --sqlite evidence_test.db

    # Verify against PostgreSQL (production / Minikube)
    python verify_hash_chain.py --db-url "postgresql://user:pass@host:5432/db"

    # Verbose mode (show each record's verification)
    python verify_hash_chain.py --sqlite evidence_test.db --verbose
"""

import argparse
import hashlib
import os
import sqlite3
import sys
from datetime import datetime, timezone

# Genesis-Eintrag: previous_hash ist leer (NULL in DB, "" im Hash-Payload).
# Die DB-Trigger-Funktion compliance.set_hash_chain() setzt NEW.previous_hash auf
# den hash_value des Vorgaenger-Datensatzes oder auf NULL beim Genesis-Eintrag.
# concat_ws('|', ..., coalesce(NEW.previous_hash, '')) kodiert NULL als "".


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
) -> str:
    """Compute SHA-256 hash — identical logic to record_evidence.py and DB trigger."""
    payload = "|".join([
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
        previous_hash or "",
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fetch_records_sqlite(db_path: str) -> list[dict]:
    """Fetch all records from SQLite ordered by audit_id."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM quality_gate_results ORDER BY audit_id ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_records_pg(db_url: str) -> list[dict]:
    """Fetch all records from PostgreSQL ordered by audit_id."""
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("ERROR: psycopg2 not installed. Use --sqlite for local testing.")
        sys.exit(2)

    conn = psycopg2.connect(db_url)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM compliance.quality_gate_results ORDER BY audit_id ASC"
        )
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def verify_chain(records: list[dict], verbose: bool = False) -> tuple[bool, int, str]:
    """
    Verify the hash chain integrity.

    Returns:
        (is_valid, records_checked, error_message)
    """
    if not records:
        return True, 0, "Empty store — nothing to verify"

    # Genesis-Eintrag: previous_hash ist leer ("" in Payload, NULL in DB).
    expected_previous = ""
    errors = []

    # Gap detection: check for deleted records (missing audit_ids)
    audit_ids = [rec["audit_id"] for rec in records]
    if len(audit_ids) >= 2:
        expected_ids = set(range(audit_ids[0], audit_ids[-1] + 1))
        actual_ids = set(audit_ids)
        missing = sorted(expected_ids - actual_ids)
        if missing:
            errors.append(
                f"  GAP DETECTED: {len(missing)} missing audit_id(s): "
                f"{missing[:10]}{'...' if len(missing) > 10 else ''}"
            )
            if verbose:
                print(f"  [FAIL] Gap detection: {len(missing)} missing record(s)")

    for i, rec in enumerate(records):
        audit_id = rec["audit_id"]

        # Check 1: previous_hash links correctly
        stored_previous = rec.get("previous_hash") or ""
        if i == 0:
            # Genesis-Eintrag: previous_hash muss leer sein (NULL oder "").
            if stored_previous:
                errors.append(
                    f"  audit_id={audit_id}: first record previous_hash must be empty "
                    f"(got {stored_previous[:16]}...)"
                )
        else:
            if stored_previous != expected_previous:
                errors.append(
                    f"  audit_id={audit_id}: previous_hash mismatch "
                    f"(stored={stored_previous[:16]}... expected={expected_previous[:16]}...)"
                )

        # Check 2: Recompute hash and compare
        recomputed = compute_hash(
            previous_hash=rec.get("previous_hash") or "",
            model_name=rec.get("model_name", ""),
            model_version=rec.get("model_version", ""),
            pipeline_id=rec.get("pipeline_id", ""),
            run_id=str(rec.get("run_id", "")),
            gate_type=rec.get("gate_type", ""),
            decision=rec.get("decision", ""),
            decision_method=rec.get("decision_method", "AUTO"),
            gate_name=rec.get("gate_name", ""),
            policy_version=rec.get("policy_version", ""),
            payload_id=str(rec.get("payload_id", "")),
            checked_at=str(rec.get("checked_at", "")),
            inserted_by=rec.get("inserted_by", ""),
        )

        stored_hash = rec.get("hash_value", "")
        if recomputed != stored_hash:
            errors.append(
                f"  audit_id={audit_id}: hash mismatch "
                f"(stored={stored_hash[:16]}... recomputed={recomputed[:16]}...)"
            )

        if verbose:
            status = "OK" if not any(str(audit_id) in e for e in errors) else "FAIL"
            print(
                f"  [{status}] audit_id={audit_id} gate={rec.get('gate_name', '?')} "
                f"method={rec.get('decision_method', '?')} "
                f"decision={rec.get('decision', '?')} "
                f"hash={stored_hash[:16]}..."
            )

        # Next iteration expects this record's hash as previous
        expected_previous = stored_hash

    if errors:
        return False, len(records), "\n".join(errors)
    return True, len(records), ""


def main():
    parser = argparse.ArgumentParser(
        description="Verify Evidence Store hash-chain integrity (Phase 8)"
    )
    parser.add_argument(
        "--sqlite", metavar="DB_PATH",
        help="Verify SQLite database (local testing)"
    )
    parser.add_argument(
        "--db-url",
        default=os.environ.get("EVIDENCE_STORE_URL"),
        help="PostgreSQL connection URL"
    )
    parser.add_argument("--verbose", action="store_true", help="Show each record")

    args = parser.parse_args()

    print("=" * 60)
    print("Hash-Chain Verification — GenAIOps Evidence Store")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    # Fetch records
    if args.sqlite:
        print(f"Source: SQLite ({args.sqlite})")
        try:
            records = fetch_records_sqlite(args.sqlite)
        except Exception as e:
            print(f"ERROR: Could not read SQLite DB: {e}")
            sys.exit(2)
    elif args.db_url:
        print("Source: PostgreSQL")
        try:
            records = fetch_records_pg(args.db_url)
        except Exception as e:
            print(f"ERROR: Could not connect to PostgreSQL: {e}")
            sys.exit(2)
    else:
        # CronJob mode: construct URL from env vars
        host = os.environ.get("EVIDENCE_STORE_HOST", "localhost")
        port = os.environ.get("EVIDENCE_STORE_PORT", "5432")
        db = os.environ.get("EVIDENCE_STORE_DB", "genaiops")
        password = os.environ.get("POSTGRES_PASSWORD", "")
        db_url = f"postgresql://postgres:{password}@{host}:{port}/{db}"
        print(f"Source: PostgreSQL ({host}:{port}/{db})")
        try:
            records = fetch_records_pg(db_url)
        except Exception as e:
            print(f"ERROR: Could not connect to PostgreSQL: {e}")
            sys.exit(2)

    print(f"Records found: {len(records)}")
    print("-" * 60)

    # Verify
    is_valid, count, error_msg = verify_chain(records, args.verbose)

    print("-" * 60)
    if count == 0:
        print("Result: EMPTY — No records in Evidence Store")
        print("Status: OK (nothing to verify)")
        sys.exit(0)
    elif is_valid:
        print(f"Result: VALID — {count} records verified, chain intact")
        print("Genesis: previous_hash=<empty> (audit_id=1)")
        if records:
            print(f"Latest:  {records[-1]['hash_value'][:16]}... (audit_id={records[-1]['audit_id']})")
        sys.exit(0)
    else:
        print(f"Result: CORRUPTED — {count} records checked, chain broken!")
        print("Errors:")
        print(error_msg)
        print("\nACTION REQUIRED: Evidence tampering detected. Initiate incident response.")
        sys.exit(1)


if __name__ == "__main__":
    main()
