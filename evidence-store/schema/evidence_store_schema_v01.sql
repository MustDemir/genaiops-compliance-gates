-- Ambient AI Scribe - Evidence Store Schema v01
-- Target: PostgreSQL / Azure Database for PostgreSQL

CREATE TABLE IF NOT EXISTS quality_gate_results (
    audit_id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    run_id UUID NOT NULL,
    gate_type TEXT NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('PASS','FAIL')),
    evidence_blob_url TEXT NOT NULL,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hash_value TEXT,
    previous_hash TEXT
);

CREATE INDEX IF NOT EXISTS idx_gate_reporting
    ON quality_gate_results (model_name, gate_type);

CREATE INDEX IF NOT EXISTS idx_gate_checked_at
    ON quality_gate_results (checked_at);

CREATE INDEX IF NOT EXISTS idx_gate_failures
    ON quality_gate_results (checked_at)
    WHERE decision = 'FAIL';

CREATE OR REPLACE FUNCTION trg_prevent_delete_update()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'EU AI Act compliance: modification or deletion of audit logs is prohibited';
END;
$$;

DROP TRIGGER IF EXISTS make_evidence_immutable ON quality_gate_results;

CREATE TRIGGER make_evidence_immutable
BEFORE UPDATE OR DELETE ON quality_gate_results
FOR EACH ROW EXECUTE FUNCTION trg_prevent_delete_update();

-- Minimal privacy view for reporting consumers
CREATE OR REPLACE VIEW vw_quality_gate_reporting AS
SELECT
    audit_id,
    model_name,
    model_version,
    pipeline_id,
    run_id,
    gate_type,
    decision,
    checked_at
FROM quality_gate_results;
