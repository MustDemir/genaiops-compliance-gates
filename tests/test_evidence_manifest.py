#!/usr/bin/env python3
"""
test_evidence_manifest.py — Guard the evidence manifest (SPEC-05 Teil 2).

The manifest is what carries a run's evidence out of the runner. Everything
that matters about it is a claim that can silently stop being true:

  * that it names the head of the chain that actually exists
  * that its verdict digest changes when a verdict changes
  * that a HYBRID gate's two records both reach the digest
  * that `signing_context` follows the environment and is never invented
  * that it is written even when there is nothing to write about
  * that the digest has exactly ONE implementation, so the pipeline report and
    the manifest cannot drift apart (the lesson test_hash_parity.py encodes)
  * that prepare_inputs.py never manufactures one (B-03: the quiet fallback)

Every check has its counterproof beside it — a case that must go the other way.
A test that cannot fail is not a test (B-16).

Exit codes: 0 = all guards hold, 1 = at least one broke.
"""

import hashlib
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_MANIFEST = REPO_ROOT / "evidence-store" / "scripts" / "build_manifest.py"
RECORD_EVIDENCE = REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py"
ORCHESTRATOR = REPO_ROOT / "pipeline" / "gate_orchestrator.py"
PREPARE_INPUTS = REPO_ROOT / "pipeline" / "prepare_inputs.py"

REQUIRED_FIELDS = [
    "pipeline_run_id", "commit_sha", "schema_version", "record_count",
    "genesis_hash", "chain_head", "gate_verdicts_digest", "runtime_mode",
    "signing_context", "created_at",
]

failures = []


def check(label: str, condition: bool, detail: str = "") -> bool:
    print(f"  [{'OK' if condition else 'FAIL'}] {label}")
    if not condition:
        if detail:
            print(f"        {detail}")
        failures.append(label)
    return condition


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_store(path: str, verdicts: list[tuple[str, str, str]]) -> None:
    """
    Build a store with the real schema and the given (gate, decision, method).

    The hash values are placeholders: the manifest REPORTS the chain head, it
    does not recompute it — verify_hash_chain.py does that, and duplicating it
    here would test the wrong script.
    """
    record = load(RECORD_EVIDENCE, "record_evidence")
    conn = record.init_sqlite(path)
    for i, (gate, decision, method) in enumerate(verdicts, start=1):
        conn.execute(
            """INSERT INTO quality_gate_results
               (model_name, model_version, pipeline_id, run_id, gate_type,
                decision, decision_method, gate_name, policy_version, payload_id,
                checked_at, inserted_by, ai_act_role, derived_decision,
                runtime_mode, hash_value, previous_hash)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("ambient-ai-scribe", "1.0.0-mock", "poc-test", "run-fixed",
             "Regulatorisch", decision, method, gate, "1.0.0", f"payload-{i}",
             "2026-09-01T00:00:00+00:00", "poc_local", "DEPLOYER",
             "approve" if decision == "PASS" else "block", "mock",
             f"hash-{i:03d}", f"hash-{i - 1:03d}" if i > 1 else None),
        )
    conn.commit()
    conn.close()


def build(db: str, out: str, env: dict = None, extra: list = None):
    cmd = [sys.executable, str(BUILD_MANIFEST), "--sqlite", db, "--out", out, "--quiet"]
    result = subprocess.run(
        cmd + (extra or []), capture_output=True, text=True,
        env={**os.environ, **(env or {})},
    )
    body = None
    if os.path.exists(out):
        with open(out, encoding="utf-8") as f:
            body = json.load(f).get("evidence_manifest")
    return result, body


def main() -> int:
    print("\nEvidence manifest — SPEC-05 Teil 2\n")
    tmp = tempfile.mkdtemp(prefix="manifest-test-")
    manifest_mod = load(BUILD_MANIFEST, "build_manifest")

    base = [("G-PRE-01", "PASS", "AUTO"), ("G-DEP-02", "PASS", "AUTO"),
            ("G-OPS-05", "PASS", "AUTO")]

    # ── 1. Shape and chain anchors ──
    print("1. What the manifest states about the chain")
    db = os.path.join(tmp, "base.db")
    make_store(db, base)
    result, body = build(db, os.path.join(tmp, "base.json"))
    check("manifest is written (exit 0)", result.returncode == 0, result.stderr)
    check("all ten declared fields are present",
          body is not None and all(f in body for f in REQUIRED_FIELDS),
          f"missing: {[f for f in REQUIRED_FIELDS if body and f not in body]}")
    check("genesis_hash is the FIRST record's hash", body["genesis_hash"] == "hash-001",
          f"got {body['genesis_hash']}")
    check("chain_head is the LAST record's hash", body["chain_head"] == "hash-003",
          f"got {body['chain_head']}")
    check("record_count matches the store", body["record_count"] == 3)
    check("schema_version is read from the store, not hard-coded",
          body["schema_version"] == "v06", f"got {body['schema_version']}")

    # counterproof: a fourth record must move the head
    db4 = os.path.join(tmp, "four.db")
    make_store(db4, base + [("G-OPS-02", "PASS", "AUTO")])
    _, body4 = build(db4, os.path.join(tmp, "four.json"))
    check("counterproof — one more record moves chain_head and count",
          body4["chain_head"] == "hash-004" and body4["record_count"] == 4)

    # ── 2. The verdict digest ──
    print("\n2. gate_verdicts_digest")
    flipped = os.path.join(tmp, "flipped.db")
    make_store(flipped, [("G-PRE-01", "PASS", "AUTO"), ("G-DEP-02", "FAIL", "AUTO"),
                         ("G-OPS-05", "PASS", "AUTO")])
    _, body_flipped = build(flipped, os.path.join(tmp, "flipped.json"))
    check("a changed verdict changes the digest",
          body["gate_verdicts_digest"] != body_flipped["gate_verdicts_digest"])

    same = os.path.join(tmp, "same.db")
    make_store(same, base)
    _, body_same = build(same, os.path.join(tmp, "same.json"))
    check("counterproof — the same verdicts give the same digest",
          body["gate_verdicts_digest"] == body_same["gate_verdicts_digest"])

    reordered = os.path.join(tmp, "reordered.db")
    make_store(reordered, list(reversed(base)))
    _, body_reordered = build(reordered, os.path.join(tmp, "reordered.json"))
    check("gate order does not change the digest (the list is sorted)",
          body["gate_verdicts_digest"] == body_reordered["gate_verdicts_digest"])

    # A HYBRID gate writes two records. If the digest deduplicated them, a
    # MANUAL FAIL could hide behind an AUTO PASS on the same gate.
    hybrid_agree = os.path.join(tmp, "hyb_agree.db")
    make_store(hybrid_agree, [("G-PRE-01", "PASS", "HYBRID"), ("G-PRE-01", "PASS", "MANUAL")])
    hybrid_split = os.path.join(tmp, "hyb_split.db")
    make_store(hybrid_split, [("G-PRE-01", "PASS", "HYBRID"), ("G-PRE-01", "FAIL", "MANUAL")])
    _, ha = build(hybrid_agree, os.path.join(tmp, "ha.json"))
    _, hs = build(hybrid_split, os.path.join(tmp, "hs.json"))
    check("a HYBRID gate's manual FAIL cannot hide behind its automated PASS",
          ha["gate_verdicts_digest"] != hs["gate_verdicts_digest"])

    single = os.path.join(tmp, "single.db")
    make_store(single, [("G-PRE-01", "PASS", "HYBRID")])
    _, sg = build(single, os.path.join(tmp, "sg.json"))
    # This is the one that catches a deduplicating digest: two identical PASS
    # records and one PASS record must not hash to the same thing, or a lost
    # record would be invisible.
    check("two identical verdicts are not one verdict (the multiset is kept)",
          ha["gate_verdicts_digest"] != sg["gate_verdicts_digest"])

    # ── 3. One implementation of the digest, not two ──
    print("\n3. The report and the manifest cannot drift apart")
    orchestrator = load(ORCHESTRATOR, "gate_orchestrator")
    lines = orchestrator.read_verdict_lines(db)
    recomputed = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    check("the digest recomputes from the report's gate_verdicts list",
          recomputed == body["gate_verdicts_digest"],
          f"{recomputed} != {body['gate_verdicts_digest']}")
    orch_src = ORCHESTRATOR.read_text(encoding="utf-8")
    check("the orchestrator has no second digest implementation",
          "sha256" not in orch_src,
          "gate_orchestrator.py computes a hash of its own — it must delegate")

    # ── 4. signing_context ──
    print("\n4. signing_context follows the environment, and is never invented")
    _, local_body = build(db, os.path.join(tmp, "local.json"), env={"GITHUB_ACTIONS": ""})
    check("outside CI the manifest declares itself local",
          local_body["signing_context"] == "local", f"got {local_body['signing_context']}")
    _, ci_body = build(db, os.path.join(tmp, "ci.json"), env={"GITHUB_ACTIONS": "true"})
    check("counterproof — in CI it declares ci",
          ci_body["signing_context"] == "ci", f"got {ci_body['signing_context']}")
    _, forced = build(db, os.path.join(tmp, "forced.json"),
                      env={"GITHUB_ACTIONS": "true"}, extra=["--signing-context", "local"])
    check("an explicit flag overrides the environment (the negative cases need it)",
          forced["signing_context"] == "local")
    bad = subprocess.run(
        [sys.executable, str(BUILD_MANIFEST), "--sqlite", db, "--out",
         os.path.join(tmp, "bad.json"), "--signing-context", "trusted"],
        capture_output=True, text=True)
    check("an unknown context is refused, not passed through", bad.returncode != 0)

    # ── 5. Written on every run, including the ones with nothing in them ──
    print("\n5. The manifest exists even when the run has nothing to show")
    empty = os.path.join(tmp, "empty.db")
    make_store(empty, [])
    res_empty, body_empty = build(empty, os.path.join(tmp, "empty.json"))
    check("an empty store still produces a manifest (exit 0)", res_empty.returncode == 0)
    check("it says so rather than inventing a chain",
          body_empty["record_count"] == 0 and body_empty["chain_head"] is None
          and body_empty["genesis_hash"] is None)
    missing = subprocess.run(
        [sys.executable, str(BUILD_MANIFEST), "--sqlite", os.path.join(tmp, "nope.db"),
         "--out", os.path.join(tmp, "nope.json")], capture_output=True, text=True)
    check("counterproof — a store that does not exist is an error, not an empty manifest",
          missing.returncode == 2)

    # ── 6. No self-issued evidence ──
    print("\n6. The walkthrough may not issue its own evidence (B-03)")
    prepare_src = PREPARE_INPUTS.read_text(encoding="utf-8")
    check("prepare_inputs.py writes no manifest and no signature",
          "build_manifest" not in prepare_src and "signing_context" not in prepare_src
          and "cosign" not in prepare_src)
    check("build_manifest.py neither signs nor verifies",
          "cosign" not in BUILD_MANIFEST.read_text(encoding="utf-8"))

    print()
    if failures:
        print(f"FAILED — {len(failures)} guard(s) broke:")
        for f in failures:
            print(f"  · {f}")
        return 1
    print("MANIFEST GUARDS OK — the manifest states the chain it actually found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
