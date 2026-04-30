# Tamper-Detection Specification — Evidence Store Hash-Chain

> **Version:** 1.0
> **Date:** 2026-03-27
> **Decision:** E11 (Phase 8 vorgezogen), L_HASH_CHAIN_ROOT_COMPROMISE
> **Scope:** Quality Gate Evidence Records in `compliance.quality_gate_results`

## 1. Architecture Overview

The Evidence Store uses a **sequential SHA-256 hash chain** where each record's hash is computed from:
- 12 business fields (model_name, model_version, pipeline_id, run_id, gate_type, decision, decision_method, gate_name, policy_version, payload_id, checked_at, inserted_by)
- The previous record's hash_value (or an **empty string** for the Genesis-Eintrag)

Genesis convention: The first record (audit_id = 1) has no predecessor; its `previous_hash` column remains empty (NULL in PostgreSQL, "" in SQLite). The DB trigger `compliance.set_hash_chain()` encodes this as an empty string in the hash payload via `coalesce(NEW.previous_hash, '')`.

## 2. Three Protection Layers

| Layer | Mechanism | What it protects |
|-------|-----------|-----------------|
| L1: Hash-Chain | SHA-256 chain linking | Detects post-hoc modification of any field in any record |
| L2: Immutability Trigger | PostgreSQL BEFORE UPDATE trigger | Prevents UPDATE/DELETE at DB level (raises exception) |
| L3: Access Control | RBAC + Row-Level Security | Restricts who can INSERT (pipeline_automation role) |

## 3. What IS Detected (Tamper Evidence)

| Attack Vector | Detection Method | Exit Code |
|---------------|-----------------|-----------|
| Field modification (decision, gate_name, etc.) | Hash recomputation mismatch | 1 |
| Record deletion (mid-chain) | Gap in audit_id sequence | 1 |
| Record reordering | previous_hash linkage breaks | 1 |
| Hash replacement (without field change) | Recomputed hash ≠ stored hash | 1 |
| Inserted record (between existing) | audit_id gap pattern changes + hash mismatch | 1 |
| Appended fake record | previous_hash won't match real last record | 1 |
| MANUAL decision tampering | Same hash protection as AUTO records | 1 |
| decision_method change (AUTO→MANUAL) | Hash includes decision_method field | 1 |

## 4. What is NOT Detected (Known Limitations)

| Attack Vector | Reason | Mitigation |
|---------------|--------|-----------|
| Root DB compromise (rewrite entire chain) | Attacker recomputes all hashes with new data | L_HASH_CHAIN_ROOT_COMPROMISE: External backup comparison, L3 access controls |
| Trigger bypass via superuser ALTER | PostgreSQL superuser can disable triggers | L3: RBAC restricts superuser access |
| Pre-insertion manipulation | Data tampered before reaching Evidence Store | Out of scope — CI/CD pipeline integrity is separate concern |
| Network MITM (data in transit) | Hash computed on application side | TLS encryption for PostgreSQL connections |
| SQLite mode (local testing only) | No triggers, no RBAC — testing convenience | SQLite explicitly labeled as "local testing only" |
| Concurrent insert race condition | Two simultaneous inserts may get same previous_hash | L_CONCURRENCY_RACE: Acceptable for PoC; production needs advisory lock |

## 5. Detection Capabilities of verify_hash_chain.py

### Checks Performed:
1. **Genesis linkage**: First record's previous_hash must be empty (NULL or "") per Genesis-Eintrag convention
2. **Sequential linkage**: Each record[i].previous_hash == record[i-1].hash_value
3. **Hash recomputation**: Recompute hash from fields, compare to stored hash_value
4. **Gap detection**: Detect missing audit_ids (deleted records)

### Exit Codes:
- `0` — Chain valid, all records verified
- `1` — Chain corrupted, tampering detected
- `2` — Error (connection failure, empty store, etc.)

## 6. Verification Schedule

| Environment | Frequency | Trigger |
|-------------|-----------|---------|
| Production (K8s) | Every 6 hours | CronJob `cronjob-hash-chain-verify` |
| Pre-audit | On demand | Manual run before compliance audit |
| Post-incident | Immediate | Incident response procedure |
| PoC Walkthrough | Single run | End-to-end demonstration run |

## 7. Traceability

- **DP5 (Audit Trail Integrity)**: Hash-chain implements DP5.2
- **R005**: Evidence-Persistierung manipulationssicher und rueckverfolgbar
- **G-OPS-05**: Evidence-Completeness & Audit-Trail-Integritaet gate
- **Art. 12 EU AI Act**: Automatische Protokollierung auswertbar
