# Evidence Store — SQL Schema Specification

**Version:** 2026-03-13
**Purpose:** Design rationale and DDL component mapping for the Evidence Store (Chapter 5.4)
**Inputs:** v01.sql (minimal), v02_enterprise.sql (enterprise), architecture specification

---

## 1. Schema Evolution: v01 → v02 (DSR Design Rationale)

| Aspect | v01 (Minimal) | v02 (Enterprise) | Design Rationale |
|--------|---------------|-------------------|-----------------|
| Schema Separation | None | `medical.*` / `compliance.*` | DP4 Governance separation: Payload ≠ Telemetry |
| Roles | None | 3 roles (ingest/auditor/admin) | DP5 Least Privilege |
| RLS | No | Row-Level Security + Policies | DP1 + DP5 Privacy by Design |
| Hash Chain | `hash_value`/`previous_hash` (columns only) | Trigger function `set_hash_chain()` with SHA-256 | DP5.3 Tamper Evidence |
| Immutability | Trigger `trg_prevent_delete_update()` | Trigger `prevent_update_delete()` (identical) | DP2 Append-Only |
| Indexes | 3 (reporting, checked_at, failures) | 4 + Materialized View | DP5.2 Performance SLO |
| Privacy View | `vw_quality_gate_reporting` (basic) | View + Materialized View `mv_auditor_daily` | DP1 + DP4 |
| Payload Reference | `evidence_blob_url TEXT` | `payload_id UUID REFERENCES medical.payload_objects` | R3 FK constraint instead of URL string |

**Design Iteration:** v01 → v02 represents a DSR Build-Evaluate micro-cycle (Hevner et al., 2004).

---

## 2. DDL Components → Design Principles

### K1: Schema Separation (`medical.*` / `compliance.*`)

```sql
CREATE SCHEMA IF NOT EXISTS medical;
CREATE SCHEMA IF NOT EXISTS compliance;
```

| Dimension | Value |
|-----------|-------|
| **Design Principle** | DP4 (Governance Separation), R3 (Healthcare Requirement) |
| **Rationale** | GDPR Art. 9 requires strict separation of medical payload from regulatory telemetry |
| **References** | Nweke & Yeng (2026, p. 3-4): privacy-preserving compliance; Kholkar & Ahuja (2025, p. 1): data minimization |
| **DSR Contribution** | **E2**: Architecture pattern (encrypted Blob vs. SQL) — not described as dedicated pattern in existing literature |
| **SQL Artifact** | `medical.payload_objects` (blob metadata) + `compliance.quality_gate_results` (telemetry) |

### K2: Least-Privilege RBAC (3 Roles + RLS)

```sql
CREATE ROLE app_ingest_role NOINHERIT;    -- CI/CD Pipeline: INSERT only
CREATE ROLE auditor_role NOINHERIT;        -- Auditors: SELECT only
CREATE ROLE admin_compliance_role NOINHERIT; -- Compliance Officer: ALL
```

```sql
-- RLS Policies
CREATE POLICY pol_insert_ingest  ... FOR INSERT TO app_ingest_role;
CREATE POLICY pol_select_auditor ... FOR SELECT TO auditor_role;
CREATE POLICY pol_all_admin      ... FOR ALL    TO admin_compliance_role;
```

| Dimension | Value |
|-----------|-------|
| **Design Principle** | DP5 (Cloud-native Integrability) |
| **Rationale** | DB-native role enforcement instead of application-layer access control |
| **References** | Kholkar & Ahuja (2025, p. 1-2): least privilege + data minimization; Burns et al. (2025, p. 1+3): AIGA governance roles; Eisenberg et al. (2025, Sec. 2/Fig. 2): CONTROL-001 AI System Access Controls + RBAC |
| **SQL Artifact** | 3 roles + 3 RLS policies + REVOKE/GRANT chain |

### K3: quality_gate_results Table (Core Schema)

```sql
CREATE TABLE compliance.quality_gate_results (
    audit_id      BIGSERIAL PRIMARY KEY,
    model_name    TEXT NOT NULL,
    model_version TEXT NOT NULL,
    pipeline_id   TEXT NOT NULL,
    run_id        UUID NOT NULL,
    gate_type     TEXT NOT NULL CHECK (gate_type IN ('Strategisch','Technisch','Compliance')),
    decision      TEXT NOT NULL CHECK (decision IN ('PASS','FAIL')),
    gate_name     TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    payload_id    UUID NOT NULL REFERENCES medical.payload_objects(payload_id),
    checked_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    inserted_by   TEXT NOT NULL DEFAULT current_user,
    hash_value    TEXT NOT NULL,
    previous_hash TEXT,
    notes         TEXT
);
```

| Dimension | Value |
|-----------|-------|
| **Design Principle** | DP1 (Compliance Lifecycle), DP2 (Traceability) |
| **Rationale** | Each gate evaluation = 1 evidence record. CDV Framework output as structured record. |
| **References** | Butt (2026, p. 1-2): tamper-evident Evidence Backbone; Muhammad et al. (2026, Sec. 3.4): bounded evidence schema; Eisenberg et al. (2025, Sec. 2): UCF unified governance |

**Field-to-Design-Principle Mapping:**

| Field | Origin | DP | Source |
|-------|--------|-----|--------|
| `gate_type` CHECK | 3-pillar taxonomy (Ch. 5.2) | DP1 | Nweke & Yeng (2026): Clause-to-Control |
| `decision` CHECK | PASS/FAIL gate semantics | DP2 | Muhammad et al. (2026, Sec. 3.4): gate engine |
| `policy_version` | Versioned policy reference | DP2 | Muhammad et al. (2026, Sec. 3.4) |
| `payload_id` FK | R3 separation → FK instead of blob URL | DP4, R3 | DSR contribution E2 |
| `hash_value` / `previous_hash` | Hash chain fields | DP5.3 | Butt (2026, p. 6+14+16): SHA-256 |
| `inserted_by` | Audit trail: who inserted | DP5 | Kholkar & Ahuja (2025, p. 1): audit logging |

**DSR Contribution E4:** Synthesis from 9 sources into complete schema with DP mapping. No single source provides a comparable schema.

### K4: Immutability Trigger (Append-Only Enforcement)

```sql
CREATE OR REPLACE FUNCTION compliance.prevent_update_delete()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'EU AI Act compliance: UPDATE/DELETE on audit evidence is prohibited';
END; $$;

CREATE TRIGGER trg_prevent_ud
BEFORE UPDATE OR DELETE ON compliance.quality_gate_results
FOR EACH ROW EXECUTE FUNCTION compliance.prevent_update_delete();
```

| Dimension | Value |
|-----------|-------|
| **Design Principle** | DP2 (Traceability), DP5.3 (Tamper Evidence) |
| **Rationale** | SQL-level enforcement: Append-only as technical guarantee, not convention |
| **References** | Kholkar & Ahuja (2025, p. 1): provenance + audit logging; Butt (2026, p. 1-2+4): tamper-evident Evidence Backbone; Muhammad et al. (2026, Sec. 3.4): immutable evidence trail |
| **DSR Contribution** | Part of E1 — SQL trigger enforcement is a design contribution |

### K5: Hash Chain Trigger Function (SHA-256 Chaining)

```sql
CREATE OR REPLACE FUNCTION compliance.set_hash_chain()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
    prev_hash_local TEXT;
    payload TEXT;
BEGIN
    SELECT q.hash_value INTO prev_hash_local
      FROM compliance.quality_gate_results q
     ORDER BY q.audit_id DESC LIMIT 1;
    NEW.previous_hash := prev_hash_local;
    payload := concat_ws('|',
        coalesce(NEW.model_name, ''),
        coalesce(NEW.model_version, ''),
        coalesce(NEW.pipeline_id, ''),
        coalesce(NEW.run_id::text, ''),
        coalesce(NEW.gate_type, ''),
        coalesce(NEW.decision, ''),
        coalesce(NEW.gate_name, ''),
        coalesce(NEW.policy_version, ''),
        coalesce(NEW.payload_id::text, ''),
        coalesce(NEW.checked_at::text, ''),
        coalesce(NEW.inserted_by, ''),
        coalesce(NEW.previous_hash, '')
    );
    NEW.hash_value := encode(digest(payload, 'sha256'), 'hex');
    RETURN NEW;
END; $$;

CREATE TRIGGER trg_set_hash_chain
BEFORE INSERT ON compliance.quality_gate_results
FOR EACH ROW EXECUTE FUNCTION compliance.set_hash_chain();
```

| Dimension | Value |
|-----------|-------|
| **Design Principle** | **DP5.3** (Tamper Evidence — sub-extension of DP5) |
| **Rationale** | Chained SHA-256 hashes across all evidence records. Retroactive manipulation breaks chain → O(1) tamper detection. EU AI Act Art. 12 logging obligation. |
| **References** | Butt (2026, p. 6+14+16): SHA-256 content-addressing; Joseph (2023, p. 4+7): hash chain formula h_i = H(h_{i-1} ∥ canon(E_i)); Joseph (2023, p. 16): median latency 3.2ms for tamper detection |
| **DSR Contribution** | **E1: Hash-Chain Immutability** — No paper describes SQL-level hash chain for AI governance evidence stores. |
| **Distinction** | ≠ Blockchain (no consensus mechanism), ≠ Merkle Tree (linear chain vs. tree structure). Lightweight variant for DB trigger context. |

### K6: Composite Indexes + Performance SLO

```sql
CREATE INDEX idx_qgr_reporting       ON compliance.quality_gate_results (model_name, gate_type);
CREATE INDEX idx_qgr_checked_at      ON compliance.quality_gate_results (checked_at);
CREATE INDEX idx_qgr_failures_partial ON compliance.quality_gate_results (checked_at) WHERE decision = 'FAIL';
CREATE INDEX idx_qgr_run_id          ON compliance.quality_gate_results (run_id);
```

| Dimension | Value |
|-----------|-------|
| **Design Principle** | **DP5.2** (Performance — sub-extension of DP5) |
| **Rationale** | Query < 100ms SLO for audit reporting across millions of gate executions. Partial index on `decision = 'FAIL'` for incident response. |
| **References** | Eisenberg et al. (2025, Sec. 2): UCF enables efficient governance queries; Muhammad et al. (2026, Sec. 3.4): bounded evidence schema |
| **DSR Contribution** | **E3**: No source defines quantitative performance targets for audit query response. |

| Index | Purpose | Query Pattern |
|-------|---------|---------------|
| `idx_qgr_reporting` | Compliance dashboard | `WHERE model_name = ? AND gate_type = ?` |
| `idx_qgr_checked_at` | Time-series analysis | `WHERE checked_at BETWEEN ? AND ?` |
| `idx_qgr_failures_partial` | Incident response (partial) | `WHERE decision = 'FAIL' AND checked_at > ?` |
| `idx_qgr_run_id` | Pipeline run lookup | `WHERE run_id = ?` |

### K7: Privacy-Safe Reporting Views

```sql
CREATE OR REPLACE VIEW compliance.vw_quality_gate_reporting AS
SELECT audit_id, model_name, model_version, pipeline_id, run_id,
       gate_type, gate_name, decision, checked_at, hash_value, previous_hash
FROM compliance.quality_gate_results;
-- Excluded: notes, inserted_by, payload_id → PII minimization

CREATE MATERIALIZED VIEW compliance.mv_auditor_daily AS
SELECT date_trunc('day', checked_at) AS day_bucket,
       model_name, gate_type, decision, count(*) AS run_count
FROM compliance.quality_gate_results
GROUP BY 1,2,3,4;
```

| Dimension | Value |
|-----------|-------|
| **Design Principle** | DP1 (Compliance Lifecycle), DP4 (Governance Separation) |
| **Rationale** | No direct table access for auditors. View masks PII-adjacent fields. Materialized view for dashboard performance. |
| **References** | Kholkar & Ahuja (2025, p. 1): data minimization; Nweke & Yeng (2026): privacy-preserving compliance |
| **Masking Logic** | View excludes: `notes` (free text), `inserted_by` (username), `payload_id` (FK to medical data) |

---

## 3. Traceability Chain: R → DP → Gate → Evidence

```
Requirement (Ch. 4)
    → Design Principle (Ch. 5.1)
        → Gate Instance (Ch. 5.2, CDV Framework)
            → Evidence Record (quality_gate_results, Ch. 5.4)
                → Hash Chain (DP5.3)
                    → Conformity Bundle (Audit Report)
```

| Reference | Contribution |
|-----------|-------------|
| Nweke & Yeng (2026, p. 5-6) | Clause-to-Control mapping for traceability |
| Muhammad et al. (2026, p. 1) | Traceability and explainability as core principle |
| Kholkar & Ahuja (2025, p. 1) | Complete provenance, traceability, and audit logging |
| Butt (2026, p. 1-2) | Clause-to-Artifact Traceability (C2AT) |

---

## 4. CAC/AAC Classification

| Schema Component | CAC (Compliance-as-Code) | AAC (Audit-as-Code) |
|------------------|--------------------------|---------------------|
| `gate_type` CHECK | Strategic/Technical/Compliance → CAC taxonomy | — |
| `policy_version` | Versioned policy reference → CAC | — |
| Immutability Trigger | — | Evidence preservation → AAC |
| Hash Chain Trigger | — | Chain of custody → AAC |
| `decision` PASS/FAIL | Gate decision → CAC | Persisted as evidence → AAC |
| Privacy Views | — | Audit access → AAC |

**Sources:** Muhammad et al. (2026): Audit-as-Code framework; Nweke & Yeng (2026): Compliance-as-Code operationalization

---

## 5. DSR Contributions → SQL Components

| # | Contribution | SQL Component | DP | Gap Justification |
|---|-------------|---------------|-----|-------------------|
| **E1** | Hash-Chain Immutability | `set_hash_chain()` + `prevent_update_delete()` triggers | DP5.3 + DP2 | 1/9 sources explicit. No SQL-level hash chain for AI governance. |
| **E2** | Payload/Telemetry Separation | `medical.*` / `compliance.*` schema + FK constraint | DP4 + R3 | 3 explicit, 4 implicit. No dedicated architecture pattern. |
| **E3** | Performance SLO 100ms | 4 composite/partial indexes + materialized view | DP5.2 | No quantitative performance targets in literature. |
| **E4** | PostgreSQL Evidence Store Schema | Complete v02 schema (7 DDL blocks, 5 components) | All DP | Synthesis: No single source provides complete schema. |

---

## 6. Known Limitations (PoC Scope)

| # | Limitation | Affected Component | Impact | Treatment |
|---|-----------|-------------------|--------|-----------|
| **L1** | Race condition on concurrent INSERTs | K5 Hash Chain Trigger | Two parallel pipeline runs read same `previous_hash` → chain break | PoC scope trade-off. Fix: SERIALIZABLE isolation or advisory lock. Single-pipeline PoC = acceptable. |
| **L2** | No table partitioning | K3 quality_gate_results | 100ms SLO breaks at >>10M records without `PARTITION BY RANGE (checked_at)` | SLO valid for PoC scale. Partitioning as future work. |
| **L3** | No retention/archival | K3 + K7 | EU AI Act Art. 12(2) retention obligation, but no automated archival | Retention policy as future work. |
| **L4** | `inserted_by = current_user` | K3 field | With connection pooling (PgBouncer) all INSERTs appear as same user | Alternative: application-layer `x-pipeline-id` header. |

### Note on Joseph (2023)
Joseph (2023) is used as supplementary source for hash chain performance (3.2ms median latency). Published in WJAETS (not a top-tier venue). If stronger peer-reviewed sources for quantitative hash chain performance in AI governance become available, they should be considered as replacement or complement.
