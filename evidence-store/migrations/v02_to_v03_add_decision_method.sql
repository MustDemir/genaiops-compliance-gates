-- ================================================================
-- Evidence Store Migration: v02 → v03
-- ================================================================
-- Decision: E13 (Schema v02 → v03: decision_method Spalte)
-- Purpose:  Track whether a gate decision was AUTO, MANUAL, or HYBRID.
--           Unified table for both automated and manual decisions —
--           no separate tables needed.
--
-- Prerequisite: evidence_store_schema_v02_enterprise.sql applied
-- ================================================================

-- 1) Add decision_method column with CHECK constraint
ALTER TABLE compliance.quality_gate_results
    ADD COLUMN IF NOT EXISTS decision_method TEXT NOT NULL DEFAULT 'AUTO'
    CHECK (decision_method IN ('AUTO', 'MANUAL', 'HYBRID'));

COMMENT ON COLUMN compliance.quality_gate_results.decision_method IS
    'How the gate decision was made: AUTO (Conftest/Gatekeeper), MANUAL (human approval), HYBRID (both). See E13.';

-- 2) Update hash-chain function to include decision_method in payload
CREATE OR REPLACE FUNCTION compliance.set_hash_chain()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    prev_hash_local TEXT;
    payload TEXT;
BEGIN
    SELECT q.hash_value
      INTO prev_hash_local
      FROM compliance.quality_gate_results q
     ORDER BY q.audit_id DESC
     LIMIT 1;

    NEW.previous_hash := prev_hash_local;

    payload := concat_ws('|',
        coalesce(NEW.model_name, ''),
        coalesce(NEW.model_version, ''),
        coalesce(NEW.pipeline_id, ''),
        coalesce(NEW.run_id::text, ''),
        coalesce(NEW.gate_type, ''),
        coalesce(NEW.decision, ''),
        coalesce(NEW.decision_method, ''),
        coalesce(NEW.gate_name, ''),
        coalesce(NEW.policy_version, ''),
        coalesce(NEW.payload_id::text, ''),
        coalesce(NEW.checked_at::text, ''),
        coalesce(NEW.inserted_by, ''),
        coalesce(NEW.previous_hash, '')
    );

    NEW.hash_value := encode(digest(payload, 'sha256'), 'hex');
    RETURN NEW;
END;
$$;

-- 3) Update reporting view to include decision_method
CREATE OR REPLACE VIEW compliance.vw_quality_gate_reporting AS
SELECT
    audit_id,
    model_name,
    model_version,
    pipeline_id,
    run_id,
    gate_type,
    gate_name,
    decision,
    decision_method,
    checked_at,
    hash_value,
    previous_hash
FROM compliance.quality_gate_results;

-- 4) Add index for filtering by decision_method (HYBRID walkthrough queries)
CREATE INDEX IF NOT EXISTS idx_qgr_decision_method
    ON compliance.quality_gate_results (decision_method);

-- 5) Update materialized view to include decision_method dimension
DROP MATERIALIZED VIEW IF EXISTS compliance.mv_auditor_daily;
CREATE MATERIALIZED VIEW compliance.mv_auditor_daily AS
SELECT
    date_trunc('day', checked_at) AS day_bucket,
    model_name,
    gate_type,
    decision,
    decision_method,
    count(*) AS run_count
FROM compliance.quality_gate_results
GROUP BY 1, 2, 3, 4, 5;

CREATE INDEX IF NOT EXISTS idx_mv_auditor_daily
    ON compliance.mv_auditor_daily (day_bucket, model_name, gate_type, decision, decision_method);
