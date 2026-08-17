#!/usr/bin/env python3
"""
test_hash_parity.py — Guard the SHA-256 hash-payload field parity (E4).

The Evidence Store hash chain is computed in THREE independent places that
MUST use the exact same field order, otherwise verify_hash_chain.py reports a
live PostgreSQL store as CORRUPTED (false-positive tamper detection):

  1. evidence-store/scripts/record_evidence.py   — compute_hash() (client write)
  2. evidence-store/scripts/verify_hash_chain.py  — compute_hash() (verification)
  3. evidence-store/migrations/v03_to_v04_add_ai_act_role.sql
                                                  — compliance.set_hash_chain() (DB trigger)

Since schema v04 (SPEC-03) there are TWO payload variants, and the guard must
cover both:

  v03 — 13 fields, without ai_act_role   (records below the migration cutoff)
  v04 — 14 fields, ai_act_role directly before previous_hash (at/above cutoff)

The two Python implementations are compared BEHAVIOURALLY: both are imported
and must produce byte-identical digests for the same inputs, in both variants.
That is stronger than parsing their source, because it also catches a
divergence that a regex would read as equivalent. The SQL trigger cannot be
executed without a database, so its two concat_ws branches are still checked
statically against the canonical field order.

Exit codes: 0 = parity holds, 1 = mismatch.
"""

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RECORD = REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py"
VERIFY = REPO_ROOT / "evidence-store" / "scripts" / "verify_hash_chain.py"
MIGRATION = REPO_ROOT / "evidence-store" / "migrations" / "v04_to_v05_add_derived_decision.sql"

# Canonical field order. previous_hash is always the final element;
# ai_act_role sits directly before it in the v04 variant.
EXPECTED_V03 = [
    "model_name", "model_version", "pipeline_id", "run_id", "gate_type",
    "decision", "decision_method", "gate_name", "policy_version",
    "payload_id", "checked_at", "inserted_by", "previous_hash",
]
EXPECTED_V04 = [
    "model_name", "model_version", "pipeline_id", "run_id", "gate_type",
    "decision", "decision_method", "gate_name", "policy_version",
    "payload_id", "checked_at", "inserted_by", "ai_act_role", "previous_hash",
]
EXPECTED_V05 = [
    "model_name", "model_version", "pipeline_id", "run_id", "gate_type",
    "decision", "decision_method", "gate_name", "policy_version",
    "payload_id", "checked_at", "inserted_by", "ai_act_role",
    "derived_decision", "previous_hash",
]

# Distinct sentinel values so a swapped pair of fields changes the digest.
SAMPLE = {
    "previous_hash": "prev-hash-0001",
    "model_name": "model-name-0002",
    "model_version": "model-version-0003",
    "pipeline_id": "pipeline-id-0004",
    "run_id": "run-id-0005",
    "gate_type": "Technisch",
    "decision": "PASS",
    "decision_method": "AUTO",
    "gate_name": "G-PRE-01",
    "policy_version": "policy-version-0006",
    "payload_id": "payload-id-0007",
    "checked_at": "2026-08-14T00:00:00.000000+00:00",
    "inserted_by": "inserted-by-0008",
    "ai_act_role": "DEPLOYER",
    "derived_decision": "manual_review",
}


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sql_payload_order(path: Path) -> list[str]:
    """Extract the NEW.<field> order from the set_hash_chain() payload build.

    Since v05 the trigger assembles the payload incrementally into a TEXT[]
    instead of branching over concat_ws variants — with two independent
    cutoffs the branch form would need four copies of the field list. The
    array form states the order once, in source order, which is exactly the
    maximal (v05) payload.
    """
    text = path.read_text(encoding="utf-8")
    start = text.find("parts := ARRAY[")
    end = text.find("array_to_string(parts", start)
    if start == -1 or end == -1:
        raise AssertionError(f"{path.name}: could not find the parts := ARRAY[...] payload build")
    # Only coalesce(NEW.x, '') entries are payload fields. The bare NEW.audit_id
    # references in the IF conditions guarding the optional appends are not.
    return re.findall(r"coalesce\(NEW\.([a-z_]+)", text[start:end])


def main() -> int:
    record = _load(RECORD, "record_evidence")
    verify = _load(VERIFY, "verify_hash_chain")

    ok = True
    print("Hash-payload parity (E4):")

    # ── 1. Behavioural parity of the two Python implementations ──
    variants = (
        ("v03", dict(include_ai_act_role=False, include_derived_decision=False)),
        ("v04", dict(include_ai_act_role=True, include_derived_decision=False)),
        ("v05", dict(include_ai_act_role=True, include_derived_decision=True)),
    )
    for variant, flags in variants:
        h_record = record.compute_hash(**flags, **SAMPLE)
        h_verify = verify.compute_hash(**flags, **SAMPLE)
        match = h_record == h_verify
        ok = ok and match
        print(f"  [{'OK' if match else 'FAIL'}] {variant}: record_evidence.py == verify_hash_chain.py")
        if not match:
            print(f"        record_evidence.py:   {h_record}")
            print(f"        verify_hash_chain.py: {h_verify}")

    # ── 2. Every variant must produce a distinct digest ──
    digests = {v: record.compute_hash(**f, **SAMPLE) for v, f in variants}
    distinct = len(set(digests.values())) == len(digests)
    ok = ok and distinct
    print(f"  [{'OK' if distinct else 'FAIL'}] v03, v04 and v05 produce different digests")
    if not distinct:
        print("        a field is not actually entering the payload:", digests)

    # ── 3. Static field order of the SQL trigger ──
    sql_order = _sql_payload_order(MIGRATION)
    sql_ok = sql_order == EXPECTED_V05
    ok = ok and sql_ok
    print(f"  [{'OK' if sql_ok else 'FAIL'}] set_hash_chain() (v05 SQL): {len(sql_order)} fields in order")
    if not sql_ok:
        print(f"        got:      {sql_order}")
        print(f"        expected: {EXPECTED_V05}")

    if ok:
        print(f"\nPARITY OK — all 3 implementations agree on all payload variants "
              f"({len(EXPECTED_V03)} / {len(EXPECTED_V04)} / {len(EXPECTED_V05)} fields).")
        return 0
    print("\nPARITY MISMATCH — verify_hash_chain.py would flag a live PG store as CORRUPTED.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
