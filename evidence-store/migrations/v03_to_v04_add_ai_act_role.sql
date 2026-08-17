-- ================================================================
-- Evidence Store Migration: v03 → v04
-- ================================================================
-- Decision: SPEC-03 (Rollenparameter PROVIDER / DEPLOYER / BOTH)
-- Purpose:  Record which EU AI Act role a gate ran under. The role
--           decides which gates execute at all and is therefore
--           audit-relevant: it belongs in the hashed payload, not in
--           the unhashed `notes` column.
--
-- Prerequisite: v02_to_v03_add_decision_method.sql applied
--
-- ----------------------------------------------------------------
-- MIGRATIONSVARIANTE: Cutoff statt Kettenbruch
-- ----------------------------------------------------------------
-- Bestehende Records wurden ohne ai_act_role gehasht. Damit die
-- Aufnahme des Feldes keine bestehende Kette bricht, wird es NICHT
-- rueckwirkend Teil der Payload, sondern erst ab einem festgelegten
-- audit_id. Dieser Schwellenwert wird hier auf max(audit_id) + 1
-- gesetzt und in compliance.schema_metadata persistiert.
--
--   audit_id <  cutoff  ->  13-Feld-Payload (v03), unveraendert
--   audit_id >= cutoff  ->  14-Feld-Payload (v04, inkl. ai_act_role)
--
-- record_evidence.py, verify_hash_chain.py und die Triggerfunktion
-- unten treffen exakt dieselbe Fallunterscheidung; die Feldreihenfolge
-- ist durch tests/test_hash_parity.py abgesichert.
-- ================================================================

-- 1) Rollen-Spalte — BEWUSST NULL-faehig, KEIN Default-Backfill.
--
-- Ein NOT NULL DEFAULT 'DEPLOYER' wuerde jeden historischen Record
-- rueckwirkend mit einer Rolle stempeln, die dort NIE gehasht wurde und
-- damit frei aenderbar ist: die Kette bliebe byteweise gueltig, ein
-- archivierter Head-Hash wuerde weiter passen, und die Reporting-View
-- zeigte die ungedeckte Angabe in derselben Zeile wie hash_value. Fuer
-- Pre-Cutoff-Records ist die Rolle schlicht nicht bekannt — NULL sagt
-- das, 'DEPLOYER' behauptet etwas.
--
-- NULL heisst hier ausdruecklich: "damals nicht erfasst, nicht durch die
-- Hash-Kette gedeckt". verify_hash_chain.py erzwingt das in beide
-- Richtungen (siehe dort): ein Nicht-NULL unterhalb des Cutoffs ist ein
-- Manipulationssignal, ein NULL ab dem Cutoff ein fehlendes Pflichtfeld.
ALTER TABLE compliance.quality_gate_results
    ADD COLUMN IF NOT EXISTS ai_act_role TEXT
    CHECK (ai_act_role IS NULL OR ai_act_role IN ('PROVIDER', 'DEPLOYER', 'BOTH'));

COMMENT ON COLUMN compliance.quality_gate_results.ai_act_role IS
    'EU AI Act role the gate ran under: PROVIDER (Art. 16 lit. a — properties of the system), DEPLOYER (Art. 26 — properties of its use), or BOTH. Part of the hashed payload from the audit_id recorded in compliance.schema_metadata. NULL means the record predates schema v04: the role was not captured and is NOT covered by the hash chain — it must never be back-filled. See SPEC-03.';

-- 2) Metadaten-Tabelle fuer den Cutoff
CREATE TABLE IF NOT EXISTS compliance.schema_metadata (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

COMMENT ON TABLE compliance.schema_metadata IS
    'Schema-level markers that hash verification depends on. Written by migrations, read by record_evidence.py and verify_hash_chain.py.';

-- 3) Cutoff festschreiben: alles ab dem NAECHSTEN Record traegt die Rolle.
--    ON CONFLICT DO NOTHING — ein bereits gesetzter Cutoff darf nie
--    verschoben werden, sonst wuerden bereits geschriebene v04-Records
--    unverifizierbar.
INSERT INTO compliance.schema_metadata (key, value)
SELECT 'ai_act_role_payload_from_audit_id',
       (COALESCE(MAX(audit_id), 0) + 1)::text
  FROM compliance.quality_gate_results
ON CONFLICT (key) DO NOTHING;

-- 4) Triggerfunktion: dieselbe Fallunterscheidung serverseitig
CREATE OR REPLACE FUNCTION compliance.set_hash_chain()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    prev_hash_local TEXT;
    payload         TEXT;
    role_cutoff     BIGINT;
BEGIN
    SELECT q.hash_value
      INTO prev_hash_local
      FROM compliance.quality_gate_results q
     ORDER BY q.audit_id DESC
     LIMIT 1;

    NEW.previous_hash := prev_hash_local;

    SELECT m.value::bigint
      INTO role_cutoff
      FROM compliance.schema_metadata m
     WHERE m.key = 'ai_act_role_payload_from_audit_id';

    IF role_cutoff IS NOT NULL AND NEW.audit_id >= role_cutoff THEN
        -- v04: 14 Felder, ai_act_role direkt vor previous_hash
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
            coalesce(NEW.ai_act_role, ''),
            coalesce(NEW.previous_hash, '')
        );
    ELSE
        -- v03: 13 Felder, unveraendert
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
    END IF;

    NEW.hash_value := encode(digest(payload, 'sha256'), 'hex');
    RETURN NEW;
END;
$$;

-- 5) Reporting-View um die Rolle erweitern (Privacy-View: kein notes,
--    kein inserted_by, kein payload_id — siehe RBAC-Fix in v2.0.0)
--
-- ai_act_role_hash_covered macht fuer den Auditor sichtbar, ob die Rolle
-- in dieser Zeile durch die Hash-Kette gedeckt ist. Ohne diese Spalte
-- staende die Rolle direkt neben hash_value, ohne dass erkennbar waere,
-- dass sie bei alten Zeilen gar nicht mitgesiegelt wurde.
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
        (SELECT m.value::bigint
           FROM compliance.schema_metadata m
          WHERE m.key = 'ai_act_role_payload_from_audit_id'),
        9223372036854775807))          AS ai_act_role_hash_covered,
    q.gate_name,
    q.policy_version,
    q.checked_at,
    q.hash_value,
    q.previous_hash
  FROM compliance.quality_gate_results q;

COMMENT ON VIEW compliance.vw_quality_gate_reporting IS
    'Auditor-facing view. ai_act_role_hash_covered is false for records written before the schema-v04 cutoff: their ai_act_role is NULL and is not protected by the hash chain.';
