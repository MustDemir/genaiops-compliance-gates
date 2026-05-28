#!/usr/bin/env python3
"""
test_hash_parity.py — Guard the SHA-256 hash-payload field parity (E4).

The Evidence Store hash chain is computed in THREE independent places that
MUST use the exact same field order, otherwise verify_hash_chain.py reports a
live PostgreSQL store as CORRUPTED (false-positive tamper detection):

  1. evidence-store/scripts/record_evidence.py   — compute_hash() (client write)
  2. evidence-store/scripts/verify_hash_chain.py  — compute_hash() (verification)
  3. evidence-store/migrations/v02_to_v03_add_decision_method.sql
                                                  — compliance.set_hash_chain() (DB trigger)

This test parses the field order out of all three sources and asserts they are
identical. It needs no database — it is a pure static-parity guard.

Exit codes: 0 = parity holds, 1 = mismatch.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RECORD = REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py"
VERIFY = REPO_ROOT / "evidence-store" / "scripts" / "verify_hash_chain.py"
MIGRATION = REPO_ROOT / "evidence-store" / "migrations" / "v02_to_v03_add_decision_method.sql"

# Canonical field order (v03). previous_hash is always the final element.
EXPECTED = [
    "model_name", "model_version", "pipeline_id", "run_id", "gate_type",
    "decision", "decision_method", "gate_name", "policy_version",
    "payload_id", "checked_at", "inserted_by", "previous_hash",
]


def _python_payload_fields(path: Path) -> list[str]:
    """Extract the identifier order from `payload = "|".join([ ... ])`."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r'"\|"\.join\(\[(.*?)\]\)', text, re.DOTALL)
    if not m:
        raise AssertionError(f'{path.name}: could not find "|".join([...]) payload block')
    fields = []
    for raw in m.group(1).split(","):
        token = raw.strip()
        if not token:
            continue
        # Strip trailing ` or ""` (e.g. `previous_hash or ""`).
        ident = re.split(r"\s+or\s+", token)[0].strip()
        fields.append(ident)
    return fields


def _sql_payload_fields(path: Path) -> list[str]:
    """Extract NEW.<field> order from the concat_ws('|', ...) of set_hash_chain()."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"concat_ws\('\|',(.*?)\)\s*;", text, re.DOTALL)
    if not m:
        raise AssertionError(f"{path.name}: could not find concat_ws('|', ...) block")
    # coalesce(NEW.run_id::text, '') -> run_id ; coalesce(NEW.model_name, '') -> model_name
    fields = re.findall(r"NEW\.([a-z_]+)", m.group(1))
    return fields


def main() -> int:
    sources = {
        "record_evidence.py": _python_payload_fields(RECORD),
        "verify_hash_chain.py": _python_payload_fields(VERIFY),
        "set_hash_chain() (v03 SQL)": _sql_payload_fields(MIGRATION),
    }

    print("Hash-payload field parity (E4):")
    ok = True
    for name, fields in sources.items():
        match = fields == EXPECTED
        ok = ok and match
        print(f"  [{'OK' if match else 'FAIL'}] {name}: {len(fields)} fields")
        if not match:
            print(f"        expected: {EXPECTED}")
            print(f"        got:      {fields}")

    if ok:
        print(f"\nPARITY OK — all 3 implementations hash the same {len(EXPECTED)} fields in order.")
        return 0
    print("\nPARITY MISMATCH — verify_hash_chain.py would flag a live PG store as CORRUPTED.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
