# Schema Evolution — Evidence Store

> **Zweck:** Dokumentiert die Schema-Versionen des Evidence Store für Nachvollziehbarkeit in Kap. 6.
> **Entscheidung:** E13 (Schema v03 mit decision_method)

## Versionsübersicht

| Version | Datum | Änderung | Entscheidung |
|---------|-------|----------|-------------|
| v01 | 2026-03 | Initial: quality_gate_results + hash-chain trigger + immutability trigger | Kap. 5.4 (D_DSR_EVIDENCE_STORE) |
| v02 | 2026-03 | Privacy Views, RBAC+RLS, Composite Indexes, Materialized View | Kap. 5.4/5.5 |
| v03 | 2026-03-27 | `decision_method` Spalte (AUTO/MANUAL/HYBRID) + Hash-Trigger-Update | E13 |

## v01 → v02: Privacy & Performance

**Neue Komponenten:**
- `compliance.gate_results_public` — Privacy View (ohne `inserted_by`, `notes`)
- RBAC: `pipeline_automation` (INSERT), `compliance_auditor` (SELECT), `privacy_viewer` (public view)
- Row-Level Security auf `quality_gate_results`
- Composite Indexes für häufige Query-Patterns
- `compliance.gate_results_summary_mv` — Materialized View für Reporting

**Migration:** `evidence-store/migrations/v01_to_v02_privacy_rbac.sql`

## v02 → v03: HYBRID Gate Support (E13)

**Problem:** HYBRID Gates (D_HYBRID_NONBLOCKING) erfordern die Unterscheidung ob ein Evidence Record aus einer automatischen Pipeline-Prüfung oder einer manuellen Human-Review stammt.

**Lösung:**
```sql
ALTER TABLE compliance.quality_gate_results
    ADD COLUMN IF NOT EXISTS decision_method TEXT NOT NULL DEFAULT 'AUTO'
    CHECK (decision_method IN ('AUTO', 'MANUAL', 'HYBRID'));
```

**Hash-Trigger-Update:** `decision_method` wird als Feld 7 von 13 in den SHA-256-Hash aufgenommen:
```
model_name | model_version | pipeline_id | run_id | gate_type | decision |
decision_method | gate_name | policy_version | payload_id | checked_at |
inserted_by | previous_hash
```

**Reporting-View-Update:** `decision_method` als Spalte in Public View und Materialized View hinzugefügt.

**Index:** `idx_qgr_decision_method` für Filterung nach AUTO/MANUAL/HYBRID.

**Migration:** `evidence-store/migrations/v02_to_v03_add_decision_method.sql`

**Rückwärtskompatibilität:** `DEFAULT 'AUTO'` stellt sicher, dass bestehende Records valide bleiben. Der Hash-Trigger berechnet neue Hashes nur für neue Inserts (bestehende Chain bleibt intakt).

## Thesis-Relevanz

- **Kap. 5.4:** Schema v01/v02 spezifiziert als DSR-Artefakt
- **Kap. 6.3:** Schema v03 demonstriert im PoC-Walkthrough
- **Kap. 7 (Diskussion):** Schema-Evolution als Beispiel für iteratives DSR-Design
- **DP5.2/DP5.3:** Hash-Chain und Immutability über alle Schema-Versionen konsistent
