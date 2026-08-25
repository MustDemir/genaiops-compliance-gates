-- ================================================================
-- Evidence Store Migration: v05 → v06
-- ================================================================
-- Purpose:  Seal WHETHER A REAL MODEL RAN into the hashed payload.
--
-- The application has always exported `scribe_mock_mode` — a gauge that
-- says "I am only pretending". No gate ever read it. A control system
-- that reports PASS in mock mode is the most embarrassing gap available
-- (HANDBUCH 7.5 (3)), and until now a mock PASS and a live PASS were
-- byte-identical in this table.
--
-- Three options were weighed (SPEC-04 3.3 / HANDBUCH 7.8):
--
--   A) mock forces FAIL.
--      Rejected. Mock mode is a legitimate PoC mode, not a compliance
--      breach, and a gate that always fails gets switched off within
--      weeks — the fate of every weak gate.
--
--   B) a third decision value, INCONCLUSIVE.
--      Rejected, and not only for cost. It carries LESS than option C,
--      not more: "PASS on a mock run" states two things — the thresholds
--      held, and no real model was behind them. "INCONCLUSIVE" states
--      one and discards whether the thresholds held at all.
--
--   C) runtime_mode as a hashed field.  ← chosen
--      A mock PASS stays possible, but is distinguishable from a live
--      PASS and cannot be altered afterwards without breaking the chain.
--
-- The task is not to forbid mock mode. It is to make it unhideable.
-- Tamper evidence, not tamper prevention — the same line the rest of
-- this artefact holds (HANDBUCH 7.7).
--
-- Known limitation of option C, accepted with eyes open: a consumer
-- reading only `decision` still sees an undifferentiated PASS. The field
-- exists, but nothing forces anyone to look at it. That is what option B
-- would have bought by brute force. Mitigations live outside this
-- migration: the pipeline report and console banner state the mode
-- prominently, the reporting view below surfaces it next to `decision`,
-- and integrity check RUNTIME_MODE_VISIBLE keeps those from eroding.
--
-- Prerequisite: v04_to_v05_add_derived_decision.sql applied
--
-- ----------------------------------------------------------------
-- Same migration variant as v04 and v05: per-field cutoff, no back-fill
-- ----------------------------------------------------------------
--   audit_id <  cutoff  ->  field absent from the payload, column NULL
--   audit_id >= cutoff  ->  field present in the payload, column required
--
-- The three cutoffs are independent, so one chain can legitimately hold
-- 13-, 14-, 15- and 16-field records. verify_hash_chain.py applies all
-- three.
--
-- NULL below the cutoff is deliberate and load-bearing, exactly as in
-- v04 and v05: a back-filled value there would be unauthenticated —
-- changing it would break no hash at all — so the verifier treats any
-- non-NULL below the cutoff as tampering.
--
-- For runtime_mode there is a second reason not to back-fill, stronger
-- than the first: nobody knows what mode those runs were in. The metric
-- was never read. Writing 'live' into them would be inventing the very
-- fact this column exists to record.
-- ================================================================

-- 1) Spalte — NULL-faehig, kein Backfill (siehe Kopf)
ALTER TABLE compliance.quality_gate_results
    ADD COLUMN IF NOT EXISTS runtime_mode TEXT
    CHECK (runtime_mode IS NULL
           OR runtime_mode IN ('live', 'mock', 'unknown'));

COMMENT ON COLUMN compliance.quality_gate_results.runtime_mode IS
    'Whether a real model was behind this gate run: live | mock | unknown, read from the scribe_mock_mode gauge at pipeline start. "unknown" is NOT "live" — it means the mode could not be established, and whoever cannot tell whether a real model ran has no evidence that one did. Part of the hashed payload from the audit_id recorded in compliance.schema_metadata. NULL means the record predates schema v06: the mode was never captured and cannot be reconstructed — it must never be back-filled.';

-- 2) Cutoff festschreiben. ON CONFLICT DO NOTHING: ein bereits gesetzter
--    Cutoff darf nie verschoben werden, sonst werden geschriebene
--    v06-Records unverifizierbar.
INSERT INTO compliance.schema_metadata (key, value)
SELECT 'runtime_mode_payload_from_audit_id',
       (COALESCE(MAX(audit_id), 0) + 1)::text
  FROM compliance.quality_gate_results
ON CONFLICT (key) DO NOTHING;

-- 3) Triggerfunktion: dritter Cutoff, gleiche Struktur.
--    Der Array-Aufbau aus v05 traegt das dritte Feld ohne Umbau — genau
--    dafuer wurde er dort so gewaehlt.
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
    runtime_cutoff  BIGINT;
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

    SELECT m.value::bigint INTO runtime_cutoff
      FROM compliance.schema_metadata m
     WHERE m.key = 'runtime_mode_payload_from_audit_id';

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

    IF runtime_cutoff IS NOT NULL AND NEW.audit_id >= runtime_cutoff THEN
        parts := parts || coalesce(NEW.runtime_mode, '');
    END IF;

    parts := parts || coalesce(NEW.previous_hash, '');

    payload := array_to_string(parts, '|');
    NEW.hash_value := encode(digest(payload, 'sha256'), 'hex');
    RETURN NEW;
END;
$$;

-- 4) Reporting-View: runtime_mode steht DIREKT NEBEN decision.
--    Das ist die Gegenmassnahme zur bekannten Schwaeche von Variante C
--    (siehe Kopf): wer diese View liest, kann einen Mock-PASS nicht
--    uebersehen, auch wenn er nur nach decision gesucht hat.
CREATE OR REPLACE VIEW compliance.vw_quality_gate_reporting AS
SELECT
    q.audit_id,
    q.model_name,
    q.model_version,
    q.pipeline_id,
    q.run_id,
    q.gate_type,
    q.decision,
    q.runtime_mode,
    (q.audit_id >= COALESCE(
        (SELECT m.value::bigint FROM compliance.schema_metadata m
          WHERE m.key = 'runtime_mode_payload_from_audit_id'),
        9223372036854775807))          AS runtime_mode_hash_covered,
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
    'Auditor-facing view. runtime_mode sits next to decision on purpose: a PASS produced in mock mode must not be readable as an ordinary PASS. The *_hash_covered flags are false for records written before the respective schema cutoff: those fields are NULL and are not protected by the hash chain.';
