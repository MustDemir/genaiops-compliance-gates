# Walkthrough-Dokumentation — Kap. 6.3 PoC-Demonstration

> **Zweck:** Schritt-für-Schritt-Anleitung für den PoC-Walkthrough in Kap. 6.3 der Masterarbeit.
> **Szenario:** Healthcare Ambient AI Scribe auf Azure AKS (Minikube für PoC).
> **Zielgruppe:** Thesis-Leser + Kolloquium-Auditorium

## Voraussetzungen

- Minikube gestartet (`minikube start`)
- Helm installiert
- PostgreSQL-Pod running mit Evidence Store Schema (v03)
- OPA Gatekeeper installiert (`helm install gatekeeper ...`)
- PoC-Repo geklont + `cd genaiops-compliance-gates`

## Abschnitt 6.3.1 — Pre-Deployment Gate Demonstration

### Schritt 1: Conftest — Policy-Checks (AUTO)

```bash
# G-PRE-01: Risk Classification Check
conftest test scenarios/healthcare-ambient-ai-scribe/fixtures/app_documentation.json \
  -p policies/pre-deployment/policy_risk_classification.rego \
  --namespace genaiops.pre_deployment.risk_classification

# Erwartetes Ergebnis: 5 tests, 5 passed, 0 warnings, 0 failures
# Was passiert: Prüft ob Risiko-Klassifikation (Annex III, 5b) dokumentiert ist
```

```bash
# G-PRE-04: Security Baseline Check
conftest test scenarios/healthcare-ambient-ai-scribe/fixtures/deployment_compliant.yaml \
  -p policies/pre-deployment/policy_security_baseline.rego \
  --namespace genaiops.pre_deployment.security_baseline

# Erwartetes Ergebnis: 6 tests, 6 passed
# Was passiert: Prüft Container-Sicherheit (Non-Root, Limits, PrivEsc, etc.)
```

```bash
# G-PRE-05: Strategic Governance Approval (AUTO-Part)
conftest test scenarios/healthcare-ambient-ai-scribe/fixtures/app_documentation.json \
  -p policies/pre-deployment/policy_governance_approval.rego \
  --namespace genaiops.pre_deployment.governance_approval

# Erwartetes Ergebnis: Tests mit SHOULD_MEET Warnungen (HYBRID Gate — Manual folgt)
```

### Schritt 2: FAIL-Case demonstrieren

```bash
# Unvollständige Dokumentation → Gate blockiert
conftest test scenarios/healthcare-ambient-ai-scribe/fixtures/app_documentation_incomplete.json \
  -p policies/pre-deployment/policy_risk_classification.rego \
  --namespace genaiops.pre_deployment.risk_classification

# Erwartetes Ergebnis: FAILURES → Pipeline stoppt
# Was passiert: Zeigt dass fehlende Pflichtfelder erkannt werden
```

### Schritt 3: Evidence aufzeichnen (AUTO)

```bash
# Record AUTO decisions to Evidence Store
python evidence-store/scripts/record_evidence.py \
  --gate G-PRE-01 --method AUTO \
  --source scenarios/healthcare-ambient-ai-scribe/fixtures/app_documentation.json \
  --sqlite evidence_walkthrough.db

python evidence-store/scripts/record_evidence.py \
  --gate G-PRE-04 --method AUTO \
  --source scenarios/healthcare-ambient-ai-scribe/fixtures/eval_results.json \
  --sqlite evidence_walkthrough.db
```

## Abschnitt 6.3.2 — Deployment Gate Demonstration

### Schritt 4: Conftest — Deployment-Checks

```bash
# G-DEP-02: Safety Metrics Validation
conftest test scenarios/healthcare-ambient-ai-scribe/fixtures/eval_results.json \
  -p policies/deployment/policy_safety_metrics.rego \
  --namespace genaiops.deployment.safety_metrics

# G-DEP-03: Transparency Documentation
conftest test scenarios/healthcare-ambient-ai-scribe/fixtures/app_documentation_transparency_pass.json \
  -p policies/deployment/policy_transparency_docs_present.rego \
  --namespace genaiops.deployment.transparency_docs_present
```

### Schritt 5: Gatekeeper — Kubernetes Admission Control

```bash
# Deploy compliant workload → admitted
kubectl apply -f scenarios/healthcare-ambient-ai-scribe/fixtures/deployment_compliant.yaml

# Deploy non-compliant workload → rejected by Gatekeeper
kubectl apply -f scenarios/healthcare-ambient-ai-scribe/fixtures/deployment_noncompliant.yaml
# Erwartetes Ergebnis: Error from server (Forbidden): admission webhook denied the request
```

### Schritt 6: Evidence aufzeichnen (Deployment)

```bash
python evidence-store/scripts/record_evidence.py \
  --gate G-DEP-02 --method AUTO \
  --source scenarios/healthcare-ambient-ai-scribe/fixtures/eval_results.json \
  --sqlite evidence_walkthrough.db
```

## Abschnitt 6.3.3 — Operations Gate Demonstration

### Schritt 7: OPS-Policy-Checks

```bash
# G-OPS-03: Monitoring Configuration Check
conftest test scenarios/healthcare-ambient-ai-scribe/fixtures/deployment_compliant.yaml \
  -p policies/operations/policy_monitoring_configured.rego \
  --namespace genaiops.operations.monitoring_configured

# G-OPS-05: Evidence Completeness Check
conftest test scenarios/healthcare-ambient-ai-scribe/fixtures/deployment_compliant.yaml \
  -p policies/operations/policy_evidence_completeness.rego \
  --namespace genaiops.operations.evidence_completeness
```

### Schritt 8: Evidence aufzeichnen (Operations)

```bash
python evidence-store/scripts/record_evidence.py \
  --gate G-OPS-03 --method AUTO \
  --source scenarios/healthcare-ambient-ai-scribe/fixtures/deployment_compliant.yaml \
  --sqlite evidence_walkthrough.db
```

## Abschnitt 6.3.4 — HYBRID Gate Demonstration (D_HYBRID_NONBLOCKING)

### Schritt 9: MANUAL Decision — Risk Classification Review

```bash
# Dr. Sarah Chen reviews Risk Classification (G-PRE-01 MANUAL part)
python evidence-store/scripts/record_evidence.py \
  --gate G-PRE-01 --method MANUAL \
  --source scenarios/healthcare-ambient-ai-scribe/fixtures/decision_log_gpre01_manual.json \
  --sqlite evidence_walkthrough.db

# Was demonstriert wird:
# - AUTO (Schritt 3) und MANUAL laufen zeitlich entkoppelt
# - Beide landen in derselben Hash-Chain
# - MANUAL-Record hat menschlichen Reviewer als inserted_by
```

### Schritt 10: MANUAL Decision — Strategic Governance Approval

```bash
# Prof. Dr. Weber approves Strategic Governance (G-PRE-05 MANUAL part)
python evidence-store/scripts/record_evidence.py \
  --gate G-PRE-05 --method MANUAL \
  --source scenarios/healthcare-ambient-ai-scribe/fixtures/decision_log_gpre05_manual.json \
  --sqlite evidence_walkthrough.db

# Was demonstriert wird:
# - Governance-Lead gibt strategische Freigabe
# - approval_conditions werden als Audit-Trail persistiert
```

## Abschnitt 6.3.5 — Hash-Chain Verifikation & Tamper-Detection

### Schritt 11: Chain-Verifikation (Green Path)

```bash
python evidence-store/scripts/verify_hash_chain.py \
  --sqlite evidence_walkthrough.db --verbose

# Erwartetes Ergebnis:
# Result: VALID — 6 records verified, chain intact
# Zeigt: AUTO + MANUAL Records in einer durchgängigen Kette
```

### Schritt 12: Tamper-Detection (Manipulation simulieren)

```bash
# Manipulate: Change a PASS to FAIL in record 3
sqlite3 evidence_walkthrough.db \
  "UPDATE quality_gate_results SET decision = 'FAIL' WHERE audit_id = 3;"

# Re-verify → corruption detected
python evidence-store/scripts/verify_hash_chain.py \
  --sqlite evidence_walkthrough.db --verbose

# Erwartetes Ergebnis:
# Result: CORRUPTED — chain broken!
# audit_id=3: hash mismatch (stored=xxxx... recomputed=yyyy...)
# Zeigt: Jede Manipulation wird durch Hash-Recomputation erkannt
```

## Abschnitt 6.3.6 — Integration Tests

### Schritt 13: Automatisierte Tests

```bash
cd evidence-store/scripts
python tests/test_hybrid_gate_integration.py

# Erwartetes Ergebnis: 8 tests, 8 passed
# Zeigt: Automatisierte Verifikation aller Szenarien
```

## Zusammenfassung der Demonstration

| Schritt | Gate(s) | Methode | Was gezeigt wird |
|---------|---------|---------|-----------------|
| 1-2 | G-PRE-01/04/05 | AUTO | Policy-as-Code prüft Pflichtfelder |
| 3 | G-PRE-01/04 | AUTO | Evidence wird in Hash-Chain persistiert |
| 4 | G-DEP-01/02 | AUTO | Deployment-Gates prüfen Datenqualität |
| 5 | Gatekeeper | AUTO | K8s Admission Control blockiert Non-Compliant |
| 6 | G-DEP-02 | AUTO | Deployment-Evidence in Chain |
| 7-8 | G-OPS-03/05 | AUTO | Operations-Monitoring validiert |
| 9-10 | G-PRE-01/05 | MANUAL | HYBRID: Mensch ergänzt asynchron |
| 11 | — | Verify | Gesamte Kette (AUTO+MANUAL) valide |
| 12 | — | Tamper | Manipulation wird erkannt |
| 13 | — | Test | Automatisierte Regressionstest-Suite |

## Traceability zu Thesis

- **RQ3**: Ist die Architektur technisch wirksam und auditierbar nachweisbar?
- **Kap. 5 → 6**: Jeder Walkthrough-Schritt demonstriert ein Design-Artefakt aus Kap. 5
- **DP1-DP5**: Alle Design Principles werden mindestens einmal demonstriert
- **R001-R014**: Coverage Matrix (Kap. 6.2) zeigt welche Requirements durch welche Schritte abgedeckt werden
