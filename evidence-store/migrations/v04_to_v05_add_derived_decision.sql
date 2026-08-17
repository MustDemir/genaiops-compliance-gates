-- ================================================================
-- Evidence Store Migration: v04 → v05
-- ================================================================
-- Purpose:  Bring the derived gate decision into the hashed payload.
--
-- `decision` only knows PASS/FAIL. The actual gate outcome per SPEC-01
-- section 5 is finer: block | manual_review | warn | approve. Until now
-- it was written as free text into the UNHASHED `notes` column, with the
-- consequence that a record could carry a sealed "decision = PASS" while
-- the qualifier "manual_review" — meaning a human still has to approve —
-- sat in a field anybody could edit without breaking a single hash. An
-- archived head hash would still match. The decision itself was therefore
-- not tamper-protected, only its coarse form.
--
-- Prerequisite: v03_to_v04_add_ai_act_role.sql applied
--
-- ----------------------------------------------------------------
-- Same migration variant as v04: per-field cutoff, no back-fill
-- ----------------------------------------------------------------
--   audit_id <  cutoff  ->  field absent from the payload, column NULL
--   audit_id >= cutoff  ->  field present in the payload, column required
--
-- The two cutoffs are independent, so one chain can legitimately hold
-- 13-, 14- and 15-field records. verify_hash_chain.py applies both.
--
-- NULL is deliberate and load-bearing, exactly as in v04: a back-filled
-- value below the cutoff would be unauthenticated — changing it breaks no
-- hash at all — so the verifier treats any non-NULL there as tampering.
-- ================================================================

-- 1) Spalte — NULL-faehig, kein Backfill (siehe Kopf)
ALTER TABLE compliance.quality_gate_results
    ADD COLUMN IF NOT EXISTS derived_decision TEXT
    CHECK (derived_decision IS NULL
           OR derived_decision IN ('block', 'manual_review', 'warn', 'approve'));

COMMENT ON COLUMN compliance.quality_gate_results.derived_decision IS
    'Derived gate outcome per SPEC-01 section 5: block (MUST violated) | manual_review (HYBRID gate) | warn (SHOULD violated) | approve. Part of the hashed payload from the audit_id recorded in compliance.schema_metadata. NULL means the record predates schema v05: the outcome was not captured as a column and is NOT covered by the hash chain — it must never be back-filled.';

-- 2) Cutoff festschreiben. ON CONFLICT DO NOTHING: ein bereits gesetzter
--    Cutoff darf nie verschoben werden, sonst werden geschriebene
--    v05-Records unverifizierbar.
INSERT INTO compliance.schema_metadata (key, value)
SELECT 'derived_decision_payload_from_audit_id',
       (COALESCE(MAX(audit_id), 0) + 1)::text
  FROM compliance.quality_gate_results
ON CONFLICT (key) DO NOTHING;

-- 3) Triggerfunktion: Payload inkrementell aufbauen.
--    Mit zwei unabhaengigen Cutoffs gaebe es vier Zweige, wenn man sie
--    ausschreibt. Der Array-Aufbau haelt die Feldreihenfolge an genau
--    einer Stelle fest und bleibt bei einem dritten Feld unveraendert.
CREATE OR REPLACE FUNCTION compliance.set_hash_chain()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    prev_hash_local TEXT;
    payload         TEXT;
    parts           TEXT[];
    role_cutoff     BIGINT;
    derived_cutoff  BIGINT;
BEGIN
    SELECT q.hash_value
      INTO prev_hash_local
      FROM compliance.quality_gate_results q
     ORDER BY q.audit_id DESC
     LIMIT 1;

    NEW.previous_hash := prev_hash_local;

    SELECT m.value::bigint INTO role_cutoff
      FROM compliance.schema_metadata m
     WHERE m.key = 'ai_act_role_payload_from_audit_id';

    SELECT m.value::bigint INTO derived_cutoff
      FROM compliance.schema_metadata m
     WHERE m.key = 'derived_decision_payload_from_audit_id';

    parts := ARRAY[
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
        coalesce(NEW.inserted_by, '')
    ];

    IF role_cutoff IS NOT NULL AND NEW.audit_id >= role_cutoff THEN
        parts := parts || coalesce(NEW.ai_act_role, '');
    END IF;

    IF derived_cutoff IS NOT NULL AND NEW.audit_id >= derived_cutoff THEN
        parts := parts || coalesce(NEW.derived_decision, '');
    END IF;

    parts := parts || coalesce(NEW.previous_hash, '');

    payload := array_to_string(parts, '|');
    NEW.hash_value := encode(digest(payload, 'sha256'), 'hex');
    RETURN NEW;
END;
$$;

-- 4) Reporting-View: beide Felder mit ihrer Deckungs-Kennzeichnung.
--    Ohne die *_hash_covered-Spalten staenden die Werte direkt neben
--    hash_value, ohne dass erkennbar waere, ob sie mitgesiegelt sind.
CREATE OR REPLACE VIEW compliance.vw_quality_gate_reporting AS
SELECT
    q.audit_id,
    q.model_name,
    q.model_version,
    q.pipeline_id,
    q.run_id,
    q.gate_type,
    q.decision,
    q.decision_method,
    q.ai_act_role,
    (q.audit_id >= COALESCE(
        (SELECT m.value::bigint FROM compliance.schema_metadata m
          WHERE m.key = 'ai_act_role_payload_from_audit_id'),
        9223372036854775807))          AS ai_act_role_hash_covered,
    q.derived_decision,
    (q.audit_id >= COALESCE(
        (SELECT m.value::bigint FROM compliance.schema_metadata m
          WHERE m.key = 'derived_decision_payload_from_audit_id'),
        9223372036854775807))          AS derived_decision_hash_covered,
    q.gate_name,
    q.policy_version,
    q.checked_at,
    q.hash_value,
    q.previous_hash
  FROM compliance.quality_gate_results q;

COMMENT ON VIEW compliance.vw_quality_gate_reporting IS
    'Auditor-facing view. The *_hash_covered flags are false for records written before the respective schema cutoff: those fields are NULL and are not protected by the hash chain.';
