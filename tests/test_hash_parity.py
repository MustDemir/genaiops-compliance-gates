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
MIGRATION = REPO_ROOT / "evidence-store" / "migrations" / "v03_to_v04_add_ai_act_role.sql"

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
}


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sql_payload_branches(path: Path) -> list[list[str]]:
    """Extract the NEW.<field> order of every concat_ws('|', ...) branch."""
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"concat_ws\('\|',(.*?)\)\s*;", text, re.DOTALL)
    if not blocks:
        raise AssertionError(f"{path.name}: could not find any concat_ws('|', ...) block")
    return [re.findall(r"NEW\.([a-z_]+)", b) for b in blocks]


def main() -> int:
    record = _load(RECORD, "record_evidence")
    verify = _load(VERIFY, "verify_hash_chain")

    ok = True
    print("Hash-payload parity (E4):")

    # ── 1. Behavioural parity of the two Python implementations ──
    for variant, include in (("v03", False), ("v04", True)):
        h_record = record.compute_hash(include_ai_act_role=include, **SAMPLE)
        h_verify = verify.compute_hash(include_ai_act_role=include, **SAMPLE)
        match = h_record == h_verify
        ok = ok and match
        print(f"  [{'OK' if match else 'FAIL'}] {variant}: record_evidence.py == verify_hash_chain.py")
        if not match:
            print(f"        record_evidence.py:   {h_record}")
            print(f"        verify_hash_chain.py: {h_verify}")

    # ── 2. The two variants must NOT collide ──
    h_v03 = record.compute_hash(include_ai_act_role=False, **SAMPLE)
    h_v04 = record.compute_hash(include_ai_act_role=True, **SAMPLE)
    distinct = h_v03 != h_v04
    ok = ok and distinct
    print(f"  [{'OK' if distinct else 'FAIL'}] v03 and v04 produce different digests")
    if not distinct:
        print("        ai_act_role is not actually entering the payload")

    # ── 3. Static field order of both SQL branches ──
    branches = _sql_payload_branches(MIGRATION)
    expected_branches = {tuple(EXPECTED_V03), tuple(EXPECTED_V04)}
    got_branches = {tuple(b) for b in branches}
    sql_ok = got_branches == expected_branches
    ok = ok and sql_ok
    print(f"  [{'OK' if sql_ok else 'FAIL'}] set_hash_chain() (v04 SQL): "
          f"{len(branches)} branch(es), {[len(b) for b in branches]} fields")
    if not sql_ok:
        for b in branches:
            print(f"        got:      {b}")
        print(f"        expected: {EXPECTED_V03}")
        print(f"        and:      {EXPECTED_V04}")

    if ok:
        print(f"\nPARITY OK — all 3 implementations agree on both payload variants "
              f"({len(EXPECTED_V03)} / {len(EXPECTED_V04)} fields).")
        return 0
    print("\nPARITY MISMATCH — verify_hash_chain.py would flag a live PG store as CORRUPTED.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
