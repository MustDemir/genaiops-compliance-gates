#!/usr/bin/env python3
"""
build_manifest.py — Summarise one pipeline run into a signable evidence manifest.

SPEC-05 Teil 2. The manifest is the document that Teil 3 signs, and the reason
the signature exists at all: in CI the Evidence Store lives at
/tmp/evidence_pipeline.db and dies with the runner (B-18). A chain that is
verified and then destroyed proves nothing to anyone who was not watching.

What the manifest states, and what it deliberately does not:

  * `chain_head` and `genesis_hash` pin the chain WITHOUT carrying it. The
    chain already binds its records to each other; what must be carried out of
    the runner is its head.
  * `gate_verdicts_digest` makes the manifest checkable WITHOUT the database.
    The verdicts are already inside the hashed payload via `decision`, so the
    head covers them — but a reader who only has the pipeline report needs to
    be able to hold that report against the signature. Evidence whose
    verification requires the database that was just deleted helps nobody.
  * `signing_context` names the context the manifest was produced in — the
    same building block as `runtime_mode` in SPEC-04. It is a DECLARATION, not
    proof: `ci` claims the run happened in CI, and only the signature from
    Teil 3 turns that claim into something an outsider can check. CI therefore
    asserts the value after generating the manifest and aborts otherwise
    (SPEC-05 Abschnitt 8.1).

The manifest is written on EVERY run — locally, in CI, and when the pipeline
blocks or the evidence path fails. A record that only appears on success
cannot document the failure (same reasoning as the drift measurement document
in SPEC-04).

This script never signs and never verifies. It reads the store and states what
is in it.

Exit codes: 0 = manifest written, 2 = error (no store, unreadable store).

Usage:
    python build_manifest.py --sqlite /tmp/evidence_pipeline.db \
        --out evidence-store/evidence_manifest.json
    python build_manifest.py --db-url "postgresql://..." --signing-context ci
"""

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

VALID_SIGNING_CONTEXTS = ("ci", "local")

# Schema version markers, newest first. The store states its own version
# through the cutoff keys the migrations write; deriving it here beats
# hard-coding a number that goes stale the way the "16/16" in G-OPS-05 did.
SCHEMA_MARKERS = [
    ("v06", "runtime_mode_payload_from_audit_id"),
    ("v05", "derived_decision_payload_from_audit_id"),
    ("v04", "ai_act_role_payload_from_audit_id"),
]


def fetch_records_sqlite(db_path: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM quality_gate_results ORDER BY audit_id ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_metadata_sqlite(db_path: str) -> dict:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT key, value FROM schema_metadata").fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return {k: v for k, v in rows}


def fetch_records_pg(db_url: str) -> list[dict]:
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("ERROR: psycopg2 not installed. Use --sqlite for local runs.")
        sys.exit(2)
    conn = psycopg2.connect(db_url)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM compliance.quality_gate_results ORDER BY audit_id ASC"
        )
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_metadata_pg(db_url: str) -> dict:
    import psycopg2
    conn = psycopg2.connect(db_url)
    with conn.cursor() as cur:
        cur.execute("SELECT key, value FROM compliance.schema_metadata")
        rows = cur.fetchall()
    conn.close()
    return {k: v for k, v in rows}


def detect_schema_version(metadata: dict) -> str:
    """Derive the payload schema version from the cutoff keys the store carries."""
    for version, key in SCHEMA_MARKERS:
        if key in metadata:
            return version
    return "v03"


def gate_verdict_lines(records: list[dict]) -> list[str]:
    """
    The verdict list the digest is taken over: one line per RECORD, sorted.

    Per record, not per gate: a HYBRID gate writes two records (the automated
    evaluation and the human decision), and those two can disagree. Collapsing
    them to one line would let a MANUAL FAIL hide behind an AUTO PASS, which is
    exactly the kind of quiet loss of a verdict this manifest exists to prevent.
    Duplicates are therefore kept — the multiset is the statement.
    """
    return sorted(f"{r['gate_name']}:{r['decision']}" for r in records)


def gate_verdicts_digest(records: list[dict]) -> str:
    payload = "\n".join(gate_verdict_lines(records))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def resolve_commit_sha(explicit: str | None) -> str:
    if explicit:
        return explicit
    env_sha = os.environ.get("GITHUB_SHA")
    if env_sha:
        return env_sha
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    # "unknown" and not a fabricated value: the manifest may not invent the
    # commit it belongs to. A signature over an invented commit is worse than
    # none, because it looks like an answer (B-18).
    return "unknown"


def resolve_signing_context(explicit: str | None) -> str:
    """
    Default from the environment, override only explicitly.

    An explicit `--signing-context ci` on a laptop is allowed on purpose: the
    field is a declaration, and the mechanism that makes a false declaration
    worthless is the signature, not this script. Blocking the flag here would
    only make the negative test cases of Abschnitt 11 unwritable.
    """
    if explicit:
        if explicit not in VALID_SIGNING_CONTEXTS:
            print(f"ERROR: invalid signing_context '{explicit}' — "
                  f"expected one of {', '.join(VALID_SIGNING_CONTEXTS)}")
            sys.exit(2)
        return explicit
    return "ci" if os.environ.get("GITHUB_ACTIONS") == "true" else "local"


def resolve_run_id(explicit: str | None, records: list[dict], commit_sha: str) -> str:
    if explicit:
        return explicit
    run_ids = {r["run_id"] for r in records}
    # One run wrote this store: use ITS identifier rather than minting a second
    # one. A manifest whose id matches nothing in the records it summarises
    # would need a lookup table to be useful.
    if len(run_ids) == 1:
        return run_ids.pop()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"pipeline-{stamp}-{commit_sha[:8]}"


def build_manifest(records: list[dict], metadata: dict, commit_sha: str,
                   signing_context: str, runtime_mode: str | None,
                   run_id: str | None) -> dict:
    resolved_sha = resolve_commit_sha(commit_sha)
    modes = {r.get("runtime_mode") for r in records if r.get("runtime_mode")}
    if runtime_mode:
        resolved_mode = runtime_mode
    elif len(modes) == 1:
        resolved_mode = modes.pop()
    elif modes:
        # Two modes in one run is not a value to average — it is a finding.
        resolved_mode = "mixed"
    else:
        resolved_mode = "unknown"

    return {
        "evidence_manifest": {
            "pipeline_run_id": resolve_run_id(run_id, records, resolved_sha),
            "commit_sha": resolved_sha,
            "schema_version": detect_schema_version(metadata),
            "record_count": len(records),
            "genesis_hash": records[0]["hash_value"] if records else None,
            "chain_head": records[-1]["hash_value"] if records else None,
            "gate_verdicts_digest": gate_verdicts_digest(records),
            "runtime_mode": resolved_mode,
            "signing_context": signing_context,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the signable evidence manifest for one pipeline run "
                    "(SPEC-05 Teil 2). Does not sign and does not verify."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--sqlite", metavar="PATH", help="SQLite Evidence Store")
    source.add_argument("--db-url", metavar="URL", help="PostgreSQL connection URL")
    parser.add_argument("--out", required=True, metavar="PATH",
                        help="Where to write the manifest JSON")
    parser.add_argument("--signing-context", choices=VALID_SIGNING_CONTEXTS,
                        help="Context declaration. Default: 'ci' when "
                             "GITHUB_ACTIONS=true, otherwise 'local'")
    parser.add_argument("--commit-sha", help="Commit the run belongs to. "
                                             "Default: $GITHUB_SHA, then git rev-parse HEAD")
    parser.add_argument("--runtime-mode", help="Override the mode read from the records")
    parser.add_argument("--pipeline-run-id", help="Override the run id read from the records")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if args.sqlite:
        if not os.path.exists(args.sqlite):
            print(f"ERROR: Evidence Store not found: {args.sqlite}")
            return 2
        try:
            records = fetch_records_sqlite(args.sqlite)
            metadata = fetch_metadata_sqlite(args.sqlite)
        except sqlite3.Error as exc:
            print(f"ERROR: could not read {args.sqlite}: {exc}")
            return 2
    else:
        try:
            records = fetch_records_pg(args.db_url)
            metadata = fetch_metadata_pg(args.db_url)
        except Exception as exc:  # noqa: BLE001 — the driver raises its own types
            print(f"ERROR: could not read the Evidence Store: {exc}")
            return 2

    manifest = build_manifest(
        records=records,
        metadata=metadata,
        commit_sha=args.commit_sha,
        signing_context=resolve_signing_context(args.signing_context),
        runtime_mode=args.runtime_mode,
        run_id=args.pipeline_run_id,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if not args.quiet:
        body = manifest["evidence_manifest"]
        print(f"Evidence manifest written: {out_path}")
        print(f"  records:      {body['record_count']}")
        print(f"  chain head:   {body['chain_head']}")
        print(f"  verdicts:     {body['gate_verdicts_digest']}")
        print(f"  context:      {body['signing_context']} "
              f"({'unsigned — E-1 needs CI' if body['signing_context'] == 'local' else 'to be signed in CI'})")
        if body["record_count"] == 0:
            # An empty store is a legitimate manifest — it documents that the
            # run recorded nothing, which is precisely what an auditor of a
            # fail-closed abort (exit 3) needs to see stated rather than absent.
            print("  NOTE: the store is empty. This manifest documents a run that "
                  "recorded no evidence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
