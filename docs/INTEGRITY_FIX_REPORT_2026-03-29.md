# GenAIOps Compliance Gates — Integrity Fix Report

**Datum:** 29. März 2026
**Autor:** Mustafa Demir
**Repository:** `genaiops-compliance-gates`
**Commits:** `23f5859`, `ea87fa8`
**CI Run:** [#23707082868](https://github.com/MustDemir/genaiops-compliance-gates/actions/runs/23707082868) — 10/10 Gates PASS

---

## 1. Ausgangslage

Das PoC-Repository implementiert eine Referenzarchitektur für die Operationalisierung des EU AI Act durch automatisierte Quality Gates in CI/CD-Pipelines. Vor diesem Fix-Zyklus befand sich das System in folgendem Zustand:

- **16 Quality Gates** als YAML-Definitionen vorhanden
- **10 Rego-Policies** implementiert (OPA/Conftest)
- **4 Gates** in der GitHub Actions CI-Pipeline erzwungen
- **22/22** lokale Integrationstests bestanden (`test_all.py`)
- **Hash-Chain-basierter Evidence Store** funktionsfähig

Das System wirkte funktional — die echten Risiken lagen jedoch in den Ausführungspfaden zwischen den Komponenten.

---

## 2. Methodik

Zwei unabhängige Analysen wurden durchgeführt:

1. **Statische Code-Analyse** — Systematische Durchsicht aller Python-Dateien, Rego-Policies, YAML-Configs, Shell-Scripts und der CI/CD-Pipeline auf Inkonsistenzen, Fallbacks und Schwachstellen.
2. **Integrity Regression Suite** — Automatisiertes Prüfskript (`test_integrity_regression.py`) mit 14 gezielten Checks auf Glaubwürdigkeitsrisiken.

Die Findings beider Analysen wurden abgeglichen, priorisiert und in einem Fix-Zyklus behoben.

---

## 3. Identifizierte Probleme

### 3.1 Kritisch — Fallback-Logik schwächt den Nachweis

| ID | Problem | Betroffene Datei | Auswirkung |
|----|---------|------------------|------------|
| F-01 | **5 von 10 Gates ohne Fallback-Code.** Wenn Conftest nicht installiert ist, geben G-PRE-04, G-DEP-01, G-DEP-03, G-DEP-05, G-OPS-02 automatisch PASS zurück — ohne jegliche Prüfung. | `gate_orchestrator.py:346` | Lokaler Walkthrough zeigt "bestanden" ohne echte Validierung. |
| F-02 | **YAML-Fixtures werden nach Dateinamen bewertet.** Enthält der Dateiname "compliant", wird PASS zurückgegeben — der Inhalt wird nicht gelesen. | `gate_orchestrator.py:237` | Keine inhaltliche Prüfung bei YAML-basierten Gates (G-PRE-04, G-OPS-03, G-OPS-05). |
| F-03 | **Unbekannte Gate-IDs erhalten PASS.** Ein Tippfehler in der Gate-ID führt zu stillem Durchwinken. | `gate_orchestrator.py:346` | Fehlerhafte Konfiguration bleibt unentdeckt. |

### 3.2 Hoch — CI-Pipeline behandelt Audit-Trail als optional

| ID | Problem | Betroffene Datei | Auswirkung |
|----|---------|------------------|------------|
| F-04 | **Evidence-Recording als "non-critical".** Bei Fehlern wird nur "skipped (non-critical)" geloggt, die Pipeline läuft weiter. | `gate-pipeline.yml:349` | Audit-Trail ist laut Architektur zentral, wird aber im Fehlerfall ignoriert. |
| F-05 | **Hash-Chain-Verification als "non-critical".** Gleiches Muster wie F-04 für die Integritätsprüfung. | `gate-pipeline.yml:363` | Tamper Detection kann ausfallen, ohne dass die Pipeline stoppt. |
| F-06 | **`2>/dev/null` unterdrückt Conftest-Fehler.** Stderr wird in allen 4 Gate-Steps verworfen. | `gate-pipeline.yml:102,151,199,248` | Rego-Syntaxfehler, fehlende Policies oder Conftest-Abstürze sind in CI-Logs unsichtbar. |
| F-07 | **CI-Pipeline prüft nur 4 von 10 Gates.** G-DEP-01, G-DEP-03, G-DEP-05, G-OPS-02, G-OPS-03, G-OPS-05 fehlen. | `gate-pipeline.yml` | README spricht von "10 Gates", CI erzwingt nur 4. |

### 3.3 Hoch — HYBRID-Semantik inkonsistent

| ID | Problem | Betroffene Datei | Auswirkung |
|----|---------|------------------|------------|
| F-08 | **G-PRE-01 fehlt `manual_source` im Szenario.** Gate ist als HYBRID markiert, aber die manuelle Bestätigung wird nicht referenziert. | `poc_healthcare_pass.json:18` | Evidence Store zeichnet nur AUTO-Teil auf, nicht die menschliche Bestätigung. |
| F-09 | **Lokale Pipeline schreibt HYBRID als AUTO.** `test_pipeline_local.sh` nutzt `--method "AUTO"` für alle Gates, auch HYBRID. | `test_pipeline_local.sh:146` | Audit-Trail zeigt falsche Decision-Methode. |

### 3.4 Hoch — Drift-Detection-zu-Evidence-Wiring defekt

| ID | Problem | Betroffene Datei | Auswirkung |
|----|---------|------------------|------------|
| F-10 | **ENV-Variable-Mismatch.** CronJob setzt `EVIDENCE_STORE_DB_URL`, record_evidence.py erwartet `EVIDENCE_STORE_URL`. | `cronjob-drift-detector.yaml:69` | Drift wird erkannt, aber Evidence kann nicht in PostgreSQL geschrieben werden. |
| F-11 | **drift_detector.py reicht DB-URL nicht weiter.** Die Funktion `record_drift_evidence()` akzeptiert kein `db_url`-Argument. | `drift_detector.py:302` | Cluster-Modus kann keine Evidence aufzeichnen. |

### 3.5 Hoch — Rego-Fallback Feld-Disparität

| ID | Problem | Betroffene Datei | Auswirkung |
|----|---------|------------------|------------|
| F-12 | **Rego-Policies prüfen mehr Felder als Fallback-Code.** Beispiel G-PRE-01: Rego prüft 6 Felder, Fallback nur 3. | `gate_orchestrator.py` | Gleiches Gate kann mit Conftest FAILen, aber im Fallback PASSen. |

### 3.6 Hoch — OPS-Rego-Policies nur Gatekeeper-kompatibel

| ID | Problem | Betroffene Datei | Auswirkung |
|----|---------|------------------|------------|
| F-13 | **OPS-Policies erwarten `input.review.object.*` (Gatekeeper-Format).** Conftest übergibt Input direkt als `input.*`. | `policy_monitoring_configured.rego`, `policy_evidence_completeness.rego`, `policy_incident_process_exists.rego` | Alle 3 OPS-Gates FAILen in CI, obwohl die Annotations korrekt sind. |

### 3.7 Mittel — Tests behaupten mehr als sie prüfen

| ID | Problem | Betroffene Datei | Auswirkung |
|----|---------|------------------|------------|
| F-14 | **Requirements-Mapping Test sucht nicht-existierende Datei.** `R001-R014.yaml` fehlt, Test soft-skippt mit "SKIP". | `test_all.py:292` | "22/22 PASS" enthält einen Test, der nichts validiert. |
| F-15 | **Smoke-Test kann "ALL TESTS PASSED" zeigen trotz übersprungener Checks.** Wenn kein App-Pod gefunden wird, werden Health- und Metrics-Checks übersprungen — zählen aber nicht als Fehler. | `smoke-test.sh:216,233` | Falsch-positives Testergebnis möglich. |

### 3.8 Mittel — Infrastruktur-Altlasten

| ID | Problem | Betroffene Datei | Auswirkung |
|----|---------|------------------|------------|
| F-16 | **Monitoring-Stub im Deployment.** busybox-Sidecar mit "sleep infinity" — Platzhalter aus Phase 3, obwohl Phase 9 (Drift Detector) abgeschlossen ist. | `deployment.yaml:136` | Unnötiger Container im K8s-Manifest. |
| F-17 | **Walkthrough referenziert veraltete Policy-Pfade.** 8 Pfade stimmen nicht mehr mit der aktuellen Dateistruktur überein. | `WALKTHROUGH_KAP63.md` | Walkthrough ist nicht reproduzierbar. |
| F-18 | **README: "all 16 gates exercised"** — tatsächlich nur 10 implementiert, davon 4 in CI. | `README.md:142` | Übertriebene Scope-Aussage. |

---

## 4. Durchgeführte Fixes

### 4.1 Fallback-Logik komplett überarbeitet

**Commit:** `23f5859`

| Gate | Vorher | Nachher |
|------|--------|---------|
| G-PRE-04 (Security Baseline) | Auto-PASS ohne Prüfung | Prüft 6 Container-Sicherheitsregeln: runAsNonRoot, Limits, readOnlyRootFilesystem, keine Klartext-Secrets, allowPrivilegeEscalation=false, capabilities.drop=ALL |
| G-DEP-01 (Data Provenance) | Auto-PASS | Prüft collection_methods, sources, preprocessing_steps, data_version |
| G-DEP-03 (Transparency Docs) | Auto-PASS | Prüft instructions_for_deployers, model_capabilities, known_limitations, ai_content_labeling |
| G-DEP-05 (Bias Assessment) | Auto-PASS | Prüft methods, fairness_results, protected_attributes, mitigation_measures |
| G-OPS-02 (Incident Process) | Auto-PASS | Prüft incident-response-configured, incident-contact, rollback-mechanism Annotations |
| Unbekannte Gates | Auto-PASS | FAIL mit Fehlermeldung |

**YAML-Parsing:** Dateinamen-Konvention durch `pyyaml`-basiertes Parsing ersetzt. Wenn pyyaml nicht installiert ist, wird FAIL zurückgegeben.

### 4.2 Rego-Fallback Feld-Parität hergestellt

**Commit:** `23f5859`

| Gate | Felder vorher (Fallback) | Felder nachher (Fallback) | Rego-Parität |
|------|-------------------------|--------------------------|-------------|
| G-PRE-01 | 3 (risk_class, reasoning, annex) | 6 (+mitigation_measures, manual_review.reviewed_by, manual_review.review_date) | 6/6 |
| G-PRE-05 | 5 (fria, oversight, lead, escalation, kill_switch) | 8 (+affected_rights, conformity_assessment, approval.approved_by) | 7/7 |
| G-DEP-02 | 3 (accuracy, latency, safety_score) | 6 (+evaluation.run_id, subgroup_analysis, adversarial_tests) | 6/6 |
| G-OPS-03 | 2 (JSON-Felder) | 3 (K8s-Annotations: drift-detection, service-monitor, prometheus.io/scrape) | 3/3 |
| G-OPS-05 | 2 (JSON-Felder) | 3 (K8s-Annotations: evidence-store-connected, hash-chain-enabled, evidence-store-type) | 3/3 |

### 4.3 CI-Pipeline auf 10 Gates erweitert

**Commit:** `23f5859`

| Phase | Gates vorher | Gates nachher |
|-------|-------------|---------------|
| Pre-Deployment | G-PRE-01, G-PRE-04, G-PRE-05 | + G-DEP-05 (Bias), G-DEP-01 (Data Provenance) |
| Deployment | G-DEP-02 | + G-DEP-03 (Transparency Docs) |
| Operations | — | + G-OPS-02 (Incident), G-OPS-03 (Monitoring), G-OPS-05 (Evidence) |
| **Gesamt** | **4** | **10** |

### 4.4 Evidence Store + Hash-Chain als Pflicht

**Commit:** `23f5859`

| Komponente | Vorher | Nachher |
|-----------|--------|---------|
| Evidence-Recording in CI | `echo "skipped (non-critical)"` | `exit 1` bei Fehler |
| Hash-Chain-Verification in CI | `echo "skipped (non-critical)"` | `exit 1` bei Fehler |
| Conftest stderr | `2>/dev/null` (unsichtbar) | `2>&1` (in Logs sichtbar) |

### 4.5 HYBRID-Semantik vereinheitlicht

**Commit:** `23f5859`

| Komponente | Vorher | Nachher |
|-----------|--------|---------|
| G-PRE-01 Szenario (pass + fail) | Kein `manual_source` | `decision_log_gpre01_manual.json` referenziert |
| `test_pipeline_local.sh` | Alle Gates als `--method "AUTO"` | G-PRE-01, G-PRE-05 als `--method "HYBRID"` |
| Evidence-Recording lokal | Fehler nur als Warning | `exit 1` bei Fehler |

### 4.6 Drift-Evidence-Wiring repariert

**Commits:** `23f5859`

| Komponente | Vorher | Nachher |
|-----------|--------|---------|
| `drift_detector.py` | Akzeptiert nur `--sqlite` | Akzeptiert `--sqlite`, `--db-url`, `EVIDENCE_STORE_URL`, `EVIDENCE_STORE_DB_URL` |
| `record_drift_evidence()` | Kein `db_url`-Parameter | Löst DB-URL aus allen ENV-Varianten auf |
| Fehlerbehandlung | Warning bei Fehler | `sys.exit(1)` — harter Abbruch |

### 4.7 OPS-Rego-Policies dual-mode

**Commit:** `ea87fa8`

Alle 3 OPS-Policies (G-OPS-02, G-OPS-03, G-OPS-05) wurden um eine dynamische Root-Auflösung erweitert:

```rego
# Dual-mode: Gatekeeper wraps input in review.object, Conftest passes directly
_object := input.review.object if { input.review }
_object := input if { not input.review }
```

Damit funktionieren dieselben Rego-Dateien sowohl mit dem Gatekeeper Admission Controller (Kubernetes) als auch mit Conftest (CI/CD).

### 4.8 Infrastruktur bereinigt

**Commit:** `23f5859`

| Fix | Detail |
|-----|--------|
| Requirements-Mapping Test | Liest jetzt die einzelnen R001.yaml–R014.yaml statt einer nicht-existierenden Sammeldatei |
| Smoke-Test | Zählt übersprungene Checks separat (`TESTS_SKIPPED`), unterscheidet PASS von SKIP |
| Monitoring-Stub | busybox-Sidecar aus `deployment.yaml` entfernt, Verweis auf CronJob eingefügt |
| Walkthrough | 8 Policy-Pfade auf aktuelle Dateinamen aktualisiert |
| README | "all 16 gates exercised" → "16 designed, 10 with Rego, 10 in CI" |
| install-monitoring.sh | Inline-Fallback-CronJob enthält jetzt `EVIDENCE_STORE_DB_URL` |
| deployment_compliant.yaml | Annotation `genaiops.io/evidence-store-type: "postgresql"` ergänzt |

---

## 5. Verifizierung

### 5.1 Integrity Regression Suite

```
Vorher:  0/11  PASS  (11 FAIL, 10 actionable)
Nachher: 14/14 PASS  (0 FAIL,  0 actionable)
```

Die Suite wurde um 3 Checks erweitert:
- `FALLBACK_COVERAGE_COMPLETE` — Jedes Szenario-Gate hat dedizierten Fallback-Code
- `REGO_FALLBACK_PARITY` — Fallback prüft die gleichen Felder wie die Rego-Policy
- `CI_CONFTEST_ERRORS_VISIBLE` — Conftest-Fehler sind in CI-Logs sichtbar

### 5.2 GitHub Actions CI-Pipeline

```
Run #23707082868 — 10/10 Gates PASS
├─ G-PRE-01 Risk Classification   PASS  [HYBRID]
├─ G-PRE-04 Security Baseline     PASS  [AUTO]
├─ G-PRE-05 Governance Approval   PASS  [HYBRID]
├─ G-DEP-05 Bias Assessment       PASS  [AUTO]
├─ G-DEP-01 Data Provenance       PASS  [AUTO]
├─ G-DEP-02 Safety Metrics        PASS  [AUTO]
├─ G-DEP-03 Transparency Docs     PASS  [AUTO]
├─ G-OPS-02 Incident Process      PASS  [AUTO]
├─ G-OPS-03 Monitoring Config     PASS  [AUTO]
├─ G-OPS-05 Evidence Completeness PASS  [AUTO]
├─ Evidence: 10 Records aufgezeichnet
├─ Hash-Chain: VALID (10 Records verifiziert)
└─ Docker Image: gebaut + gepusht (ghcr.io)
```

---

## 6. Geänderte Dateien

| Datei | Art der Änderung | LOC +/- |
|-------|-----------------|---------|
| `.github/workflows/gate-pipeline.yml` | Komplett neu: 10 Gates, Evidence mandatory | +436/-285 |
| `pipeline/gate_orchestrator.py` | Fallback-Logik für 5 Gates, YAML-Parsing, Feld-Parität | +204 |
| `monitoring/drift_detector.py` | DB-URL-Auflösung, --db-url Argument, harte Fehlerbehandlung | +34 |
| `pipeline/test_pipeline_local.sh` | HYBRID-Methode, harte Evidence-Fehler | +11 |
| `pipeline/scenarios/poc_healthcare_pass.json` | G-PRE-01 manual_source | +1 |
| `pipeline/scenarios/poc_healthcare_fail.json` | G-PRE-01 manual_source | +3 |
| `test_all.py` | Requirements-Mapping liest Einzeldateien | +32 |
| `test_integrity_regression.py` | 14 Checks (neu erstellt + 3 erweitert) | +469 |
| `policies/operations/policy_monitoring_configured.rego` | Dual-mode (Gatekeeper + Conftest) | +31/-22 |
| `policies/operations/policy_evidence_completeness.rego` | Dual-mode | +31/-22 |
| `policies/operations/policy_incident_process_exists.rego` | Dual-mode | +31/-22 |
| `scenarios/.../fixtures/deployment_compliant.yaml` | evidence-store-type Annotation | +1 |
| `scenarios/.../k8s/deployment.yaml` | Monitoring-Stub entfernt | -23 |
| `infrastructure/scripts/smoke-test.sh` | TESTS_SKIPPED Tracking | +11 |
| `infrastructure/scripts/install-monitoring.sh` | Evidence-URL in Inline-Fallback | +7 |
| `docs/WALKTHROUGH_KAP63.md` | 8 Policy-Pfade aktualisiert | ~20 |
| `README.md` | Scope-Claim korrigiert | ~20 |

---

## 7. Architektonische Auswirkungen

### 7.1 Konsistenz zwischen lokaler und CI-Ausführung

Vor den Fixes konnte dasselbe Gate unterschiedliche Ergebnisse liefern, je nachdem ob es lokal (Fallback) oder in CI (Conftest) ausgeführt wurde. Jetzt:

- **Conftest-Modus:** 10 Rego-Policies prüfen die definierten Felder
- **Fallback-Modus:** 10 Python-Funktionen prüfen die **gleichen Felder**
- **Gatekeeper-Modus:** 3 OPS-Policies funktionieren sowohl mit Gatekeeper als auch Conftest

### 7.2 Auswirkung auf K8s-Deployment (Phase 11/12)

Die Fixes sind **K8s-kompatibel und vorbereitet**:

- OPS-Rego-Policies funktionieren im Gatekeeper UND in CI (Dual-Mode)
- Drift-Detector kann Evidence in PostgreSQL schreiben (ENV-Var-Mismatch behoben)
- Monitoring-Stub entfernt — Deployment-Manifest ist produktionsbereit
- Smoke-Test unterscheidet "nicht geprüft" von "bestanden"

### 7.3 Auswirkung auf die Thesis

Die Fixes stärken folgende Aussagen:

| Thesis-Claim | Vorher | Nachher |
|-------------|--------|---------|
| "10 Quality Gates automatisiert" | 4 in CI, 6 nur lokal | 10 in CI |
| "Tamper-proof Audit-Trail" | Evidence-Fehler = "non-critical" | Evidence-Fehler = Pipeline-Stopp |
| "HYBRID = AUTO + Human Review" | Inkonsistent über 3 Scripts | Einheitlich |
| "Dual Enforcement: CI + K8s" | OPS-Policies nur Gatekeeper-kompatibel | Dual-mode Rego |
| "Closed-Loop: Gate → Evidence → Verification" | Loop konnte bei Evidence-Fehler offen bleiben | Loop ist jetzt geschlossen |

---

## 8. Verbleibende bekannte Limitationen

| # | Limitation | Bewertung | Empfehlung |
|---|-----------|-----------|------------|
| 1 | 6 von 16 Gate-Definitionen haben keine Rego-Policy (G-PRE-02, G-PRE-03, G-DEP-04, G-DEP-06, G-OPS-01, G-OPS-04) | Design-only — bewusste PoC-Scope-Entscheidung | In Thesis als "Future Work" benennen |
| 2 | SQLite statt PostgreSQL im PoC | DB-Trigger (L2) und RBAC (L3) nur als Design vorhanden | In Thesis: "1 von 3 Schutzebenen validiert" |
| 3 | Healthcare-App ist ein Mock (kein echtes LLM) | Bewusste Entscheidung (keine Azure-Kosten) | Prometheus-Metrik `scribe_mock_mode=1` dokumentiert |
| 4 | `|| true` bleibt bei Conftest-Aufrufen | Nötig, weil Conftest bei Violations Exitcode != 0 zurückgibt | Stderr ist jetzt sichtbar, Parsing fängt echte Fehler ab |

---

## 9. Neue Artefakte

| Datei | Zweck |
|-------|-------|
| `test_integrity_regression.py` | 14-Check Integrity Suite — prüft Glaubwürdigkeitsrisiken statt funktionaler Korrektheit |
| `docs/INTEGRITY_FIX_REPORT_2026-03-29.md` | Dieser Bericht |

---

## 10. Fazit

Die identifizierten Probleme lagen nicht im Kern der Architektur (Policy-Engine, Hash-Chain, Drift Detection), sondern in den Verbindungen zwischen den Komponenten: Fallbacks die den Nachweis schwächten, inkonsistente Semantik zwischen verschiedenen Ausführungspfaden, und optionale Behandlung von Pflicht-Komponenten.

Nach den Fixes ist das System in sich konsistent: **Lokaler Orchestrator, CI-Pipeline, und die zukünftige K8s-Gatekeeper-Enforcing prüfen die gleichen Gates mit den gleichen Feldern.** Der Audit-Trail ist nicht mehr optional, die HYBRID-Semantik ist einheitlich, und die Rego-Policies funktionieren in allen drei Enforcement-Modi.
