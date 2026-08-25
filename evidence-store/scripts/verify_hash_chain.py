#!/usr/bin/env python3
"""
verify_hash_chain.py — Verify tamper-evidence of the Quality Gate audit trail.

Part of the GenAIOps Compliance Gates PoC (Phase 8).
Used by the CronJob (cronjob-hash-chain-verify.yaml) every 6 hours,
and manually during PoC walkthrough demonstrations.

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


# Schema v04 (SPEC-03): ai_act_role ist erst ab einem pro Datenbank
# festgelegten audit_id Teil der Payload — siehe den Kommentarblock in
# record_evidence.py. Diese Datei MUSS dieselbe Fallunterscheidung treffen,
# sonst schlaegt die Verifikation genau an der Migrationsgrenze fehl.
AI_ACT_ROLE_CUTOFF_KEY = "ai_act_role_payload_from_audit_id"
AI_ACT_ROLE_CUTOFF_DEFAULT = None  # None = Feld nie Teil der Payload (v03)

# Schema v05: derived_decision (block|manual_review|warn|approve) — eigener
# Cutoff, gleiche NULL-Regel. Siehe Kommentarblock in record_evidence.py.
DERIVED_DECISION_CUTOFF_KEY = "derived_decision_payload_from_audit_id"

# Schema v06: runtime_mode (live|mock|unknown) — eigener Cutoff, gleiche
# NULL-Regel. SPEC-04 Teil 1: ein Mock-PASS bleibt moeglich, aber er ist
# vom Echt-PASS unterscheidbar und nicht nachtraeglich faelschbar.
RUNTIME_MODE_CUTOFF_KEY = "runtime_mode_payload_from_audit_id"


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
    derived_decision: str = "",
    include_derived_decision: bool = False,
    runtime_mode: str = "",
    include_runtime_mode: bool = False,
) -> str:
    """Compute SHA-256 hash — identical logic to record_evidence.py and DB trigger."""
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
    if include_derived_decision:
        fields.append(derived_decision or "")
    if include_runtime_mode:
        fields.append(runtime_mode or "")
    fields.append(previous_hash or "")
    return hashlib.sha256("|".join(fields).encode("utf-8")).hexdigest()


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


def fetch_cutoff_sqlite(db_path: str, key: str):
    """Read a payload cutoff from SQLite (None if never migrated)."""
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT value FROM schema_metadata WHERE key = ?", (key,)
        ).fetchone()
    except sqlite3.OperationalError:
        return None
    finally:
        conn.close()
    return int(row[0]) if row else None


def fetch_role_cutoff_sqlite(db_path: str):
    """Read the schema-v04 cutoff from SQLite (None if never migrated)."""
    return fetch_cutoff_sqlite(db_path, AI_ACT_ROLE_CUTOFF_KEY)


def fetch_derived_cutoff_sqlite(db_path: str):
    """Read the schema-v05 cutoff from SQLite (None if never migrated)."""
    return fetch_cutoff_sqlite(db_path, DERIVED_DECISION_CUTOFF_KEY)


def fetch_runtime_cutoff_sqlite(db_path: str):
    """Read the schema-v06 cutoff from SQLite (None if never migrated)."""
    return fetch_cutoff_sqlite(db_path, RUNTIME_MODE_CUTOFF_KEY)


def fetch_cutoff_pg(db_url: str, key: str):
    """Read any payload cutoff from PostgreSQL (None if never migrated).

    Added 2026-08-25 (SPEC-04). Until now only the v04 role cutoff was read
    on the PostgreSQL path: fetch_role_cutoff_pg() existed, but nothing
    fetched the v05 derived_decision cutoff, so a PostgreSQL store holding
    v05 records would have been verified against a 14-field payload while
    the trigger wrote 15 — every record would have reported a hash mismatch.
    The SQLite path had it right. Fixing it here rather than adding a third
    one-off function; runtime_mode would have inherited the same gap.
    """
    try:
        import psycopg2
    except ImportError:
        return None
    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT value FROM compliance.schema_metadata WHERE key = %s", (key,)
            )
            row = cur.fetchone()
        return int(row[0]) if row else None
    except Exception:
        return None
    finally:
        conn.close()


def fetch_role_cutoff_pg(db_url: str):
    """Read the schema-v04 cutoff from PostgreSQL (None if never migrated)."""
    try:
        import psycopg2
    except ImportError:
        return AI_ACT_ROLE_CUTOFF_DEFAULT
    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT value FROM compliance.schema_metadata WHERE key = %s",
                (AI_ACT_ROLE_CUTOFF_KEY,),
            )
            row = cur.fetchone()
    except Exception:
        return AI_ACT_ROLE_CUTOFF_DEFAULT
    finally:
        conn.close()
    return int(row[0]) if row else AI_ACT_ROLE_CUTOFF_DEFAULT


def _mode_marker(rec: dict) -> str:
    """Render runtime_mode next to the decision, loudly when it is not live.

    The known weakness of SPEC-04 option C: a reader who only looks at
    `decision` sees an undifferentiated PASS. The field exists but nothing
    forces anyone to read it. So every place that prints a decision prints
    the mode with it — here, in the pipeline report, and in the reporting
    view, where runtime_mode sits directly beside decision.
    """
    mode = rec.get("runtime_mode")
    if mode in (None, "", "live"):
        return ""
    return f" [{mode.upper()}]"


def verify_chain(records: list[dict], verbose: bool = False, role_cutoff=None,
                 derived_cutoff=None, runtime_cutoff=None) -> tuple[bool, int, str]:
    """
    Verify the hash chain integrity.

    `role_cutoff`, `derived_cutoff` and `runtime_cutoff` are the audit_ids
    from which ai_act_role (schema v04), derived_decision (schema v05) and
    runtime_mode (schema v06) join the hashed payload. Each field is
    independent, so one chain can legitimately contain 13-, 14-, 15- and
    16-field records. Passing None for a cutoff means that field was never
    part of the payload in this store.

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
            ai_act_role=rec.get("ai_act_role", "") or "",
            include_ai_act_role=(role_cutoff is not None and audit_id >= role_cutoff),
            derived_decision=rec.get("derived_decision", "") or "",
            include_derived_decision=(derived_cutoff is not None and audit_id >= derived_cutoff),
            runtime_mode=rec.get("runtime_mode", "") or "",
            include_runtime_mode=(runtime_cutoff is not None and audit_id >= runtime_cutoff),
        )

        stored_hash = rec.get("hash_value", "")
        if recomputed != stored_hash:
            errors.append(
                f"  audit_id={audit_id}: hash mismatch "
                f"(stored={stored_hash[:16]}... recomputed={recomputed[:16]}...)"
            )

        # Check 3: ai_act_role must be present exactly where the hash covers it.
        #
        # Below the cutoff the field is NOT part of the payload, so any value
        # there is unauthenticated — it could be changed without breaking a
        # single hash, leaving even an archived head hash intact. Since the
        # migration deliberately leaves those rows NULL, a non-NULL value can
        # only come from a back-fill or a manipulation. Both must be loud.
        #
        # Above the cutoff the reverse holds: a NULL would mean the record was
        # written without the role while claiming to cover it.
        # Check 3: a field must not carry a value where the hash does not cover it.
        #
        # BELOW the cutoff this is the whole point: the field is absent from the
        # payload there, so any value is unauthenticated — it could be changed
        # without breaking a single hash, leaving even an archived head hash
        # intact. Since the migrations deliberately leave those rows NULL, a
        # value can only come from a back-fill or a manipulation.
        #
        # ABOVE the cutoff no rule is needed: the hash covers whatever is there,
        # including the empty string, so both adding and removing a value breaks
        # verification on its own. `required_above` therefore expresses a
        # SEMANTIC expectation, not a security one — and it only holds for
        # fields every record type actually has. ai_act_role does (every gate
        # runs under some role); derived_decision does not, because MANUAL
        # decision-log records and drift-detector records are not gate
        # evaluations and have no block/manual_review/warn/approve outcome.
        # runtime_mode is `required_above`: every run happened in SOME mode,
        # even if that mode is "unknown". A NULL above the cutoff would mean
        # the record was written without recording whether a real model ran,
        # while claiming hash coverage for that very fact.
        for field_name, cutoff, required_above in (
            ("ai_act_role", role_cutoff, True),
            ("derived_decision", derived_cutoff, False),
            ("runtime_mode", runtime_cutoff, True),
        ):
            if cutoff is None:
                continue
            value = rec.get(field_name)
            covered = audit_id >= cutoff
            if not covered and value not in (None, ""):
                errors.append(
                    f"  audit_id={audit_id}: {field_name}='{value}' on a pre-cutoff "
                    f"record (cutoff={cutoff}) — this field is not covered by the "
                    f"hash chain here and must stay NULL; a value indicates a "
                    f"back-fill or tampering"
                )
            elif covered and required_above and value in (None, ""):
                errors.append(
                    f"  audit_id={audit_id}: {field_name} is NULL although the record "
                    f"is at or above the cutoff ({cutoff}) — it is a required, "
                    f"hash-covered field from here on"
                )

        if verbose:
            status = "OK" if not any(str(audit_id) in e for e in errors) else "FAIL"
            print(
                f"  [{status}] audit_id={audit_id} gate={rec.get('gate_name', '?')} "
                f"method={rec.get('decision_method', '?')} "
                f"decision={rec.get('decision', '?')}"
                f"{_mode_marker(rec)} "
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
    role_cutoff = None
    derived_cutoff = None
    runtime_cutoff = None
    if args.sqlite:
        print(f"Source: SQLite ({args.sqlite})")
        try:
            records = fetch_records_sqlite(args.sqlite)
            role_cutoff = fetch_role_cutoff_sqlite(args.sqlite)
            derived_cutoff = fetch_derived_cutoff_sqlite(args.sqlite)
            runtime_cutoff = fetch_runtime_cutoff_sqlite(args.sqlite)
        except Exception as e:
            print(f"ERROR: Could not read SQLite DB: {e}")
            sys.exit(2)
    elif args.db_url:
        print("Source: PostgreSQL")
        try:
            records = fetch_records_pg(args.db_url)
            role_cutoff = fetch_cutoff_pg(args.db_url, AI_ACT_ROLE_CUTOFF_KEY)
            derived_cutoff = fetch_cutoff_pg(args.db_url, DERIVED_DECISION_CUTOFF_KEY)
            runtime_cutoff = fetch_cutoff_pg(args.db_url, RUNTIME_MODE_CUTOFF_KEY)
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
            role_cutoff = fetch_cutoff_pg(db_url, AI_ACT_ROLE_CUTOFF_KEY)
            derived_cutoff = fetch_cutoff_pg(db_url, DERIVED_DECISION_CUTOFF_KEY)
            runtime_cutoff = fetch_cutoff_pg(db_url, RUNTIME_MODE_CUTOFF_KEY)
        except Exception as e:
            print(f"ERROR: Could not connect to PostgreSQL: {e}")
            sys.exit(2)

    print(f"Records found: {len(records)}")
    print(f"Payload schema: ai_act_role hashed from audit_id "
          f"{role_cutoff if role_cutoff is not None else '(never)'}, "
          f"derived_decision hashed from audit_id "
          f"{derived_cutoff if derived_cutoff is not None else '(never)'}, "
          f"runtime_mode hashed from audit_id "
          f"{runtime_cutoff if runtime_cutoff is not None else '(never)'}")
    print("-" * 60)

    # Verify
    is_valid, count, error_msg = verify_chain(
        records, args.verbose, role_cutoff, derived_cutoff, runtime_cutoff
    )

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
