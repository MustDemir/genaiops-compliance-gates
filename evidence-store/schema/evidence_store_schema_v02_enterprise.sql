-- Ambient AI Scribe - Evidence Store Schema v02 (Enterprise / Option B)
-- Target: PostgreSQL / Azure Database for PostgreSQL
-- Focus: schema separation, RLS, least privilege, insert-only, hash chain

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1) Schema separation (medical payload vs compliance telemetry)
CREATE SCHEMA IF NOT EXISTS medical;
CREATE SCHEMA IF NOT EXISTS compliance;

-- 2) Roles (least privilege model)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_ingest_role') THEN
        CREATE ROLE app_ingest_role NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'auditor_role') THEN
        CREATE ROLE auditor_role NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'admin_compliance_role') THEN
        CREATE ROLE admin_compliance_role NOINHERIT;
    END IF;
END $$;

-- 3) Medical payload metadata (no raw transcript in compliance schema)
CREATE TABLE IF NOT EXISTS medical.payload_objects (
    payload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blob_url TEXT NOT NULL,
    blob_etag TEXT,
    encrypted BOOLEAN NOT NULL DEFAULT TRUE,
    pii_level TEXT NOT NULL DEFAULT 'health_sensitive',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

REVOKE ALL ON SCHEMA medical FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA medical FROM PUBLIC;
GRANT USAGE ON SCHEMA medical TO admin_compliance_role;

-- 4) Compliance evidence table (append-only telemetry)
CREATE TABLE IF NOT EXISTS compliance.quality_gate_results (
    audit_id BIGSERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    pipeline_id TEXT NOT NULL,
    run_id UUID NOT NULL,
    gate_type TEXT NOT NULL CHECK (gate_type IN ('Strategisch','Technisch','Compliance')),
    decision TEXT NOT NULL CHECK (decision IN ('PASS','FAIL')),
    gate_name TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    payload_id UUID NOT NULL REFERENCES medical.payload_objects(payload_id),
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    inserted_by TEXT NOT NULL DEFAULT current_user,
    hash_value TEXT NOT NULL,
    previous_hash TEXT,
    notes TEXT
);

-- 5) Hash-chain function (tamper-evident chain)
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

DROP TRIGGER IF EXISTS trg_set_hash_chain ON compliance.quality_gate_results;
CREATE TRIGGER trg_set_hash_chain
BEFORE INSERT ON compliance.quality_gate_results
FOR EACH ROW
EXECUTE FUNCTION compliance.set_hash_chain();

-- 6) Insert-only enforcement (immutability)
CREATE OR REPLACE FUNCTION compliance.prevent_update_delete()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'EU AI Act compliance: UPDATE/DELETE on audit evidence is prohibited';
END;
$$;

DROP TRIGGER IF EXISTS trg_prevent_ud ON compliance.quality_gate_results;
CREATE TRIGGER trg_prevent_ud
BEFORE UPDATE OR DELETE ON compliance.quality_gate_results
FOR EACH ROW
EXECUTE FUNCTION compliance.prevent_update_delete();

-- 7) RLS and policies (privacy by design)
ALTER TABLE compliance.quality_gate_results ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS pol_insert_ingest ON compliance.quality_gate_results;
CREATE POLICY pol_insert_ingest
ON compliance.quality_gate_results
FOR INSERT
TO app_ingest_role
WITH CHECK (true);

DROP POLICY IF EXISTS pol_select_auditor ON compliance.quality_gate_results;
CREATE POLICY pol_select_auditor
ON compliance.quality_gate_results
FOR SELECT
TO auditor_role
USING (true);

DROP POLICY IF EXISTS pol_all_admin ON compliance.quality_gate_results;
CREATE POLICY pol_all_admin
ON compliance.quality_gate_results
FOR ALL
TO admin_compliance_role
USING (true)
WITH CHECK (true);

-- 8) Privileges (no direct table updates for pipeline role)
REVOKE ALL ON SCHEMA compliance FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA compliance FROM PUBLIC;

GRANT USAGE ON SCHEMA compliance TO app_ingest_role, auditor_role, admin_compliance_role;
GRANT INSERT ON compliance.quality_gate_results TO app_ingest_role;
GRANT SELECT ON compliance.quality_gate_results TO auditor_role, admin_compliance_role;
GRANT USAGE, SELECT ON SEQUENCE compliance.quality_gate_results_audit_id_seq TO app_ingest_role, admin_compliance_role;

-- 9) Reporting optimization (performance)
CREATE INDEX IF NOT EXISTS idx_qgr_reporting
    ON compliance.quality_gate_results (model_name, gate_type);

CREATE INDEX IF NOT EXISTS idx_qgr_checked_at
    ON compliance.quality_gate_results (checked_at);

CREATE INDEX IF NOT EXISTS idx_qgr_failures_partial
    ON compliance.quality_gate_results (checked_at)
    WHERE decision = 'FAIL';

CREATE INDEX IF NOT EXISTS idx_qgr_run_id
    ON compliance.quality_gate_results (run_id);

-- 10) Privacy-safe reporting view
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
    checked_at,
    hash_value,
    previous_hash
FROM compliance.quality_gate_results;

GRANT SELECT ON compliance.vw_quality_gate_reporting TO auditor_role, admin_compliance_role;

-- 11) Optional materialized view for auditor dashboards
CREATE MATERIALIZED VIEW IF NOT EXISTS compliance.mv_auditor_daily AS
SELECT
    date_trunc('day', checked_at) AS day_bucket,
    model_name,
    gate_type,
    decision,
    count(*) AS run_count
FROM compliance.quality_gate_results
GROUP BY 1,2,3,4;

CREATE INDEX IF NOT EXISTS idx_mv_auditor_daily
    ON compliance.mv_auditor_daily (day_bucket, model_name, gate_type, decision);

