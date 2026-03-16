# Mapping: Lucaj TechOps Templates → R-xx Requirements → Rego-Policy-Kandidaten

> Stand: 2026-03-11 | Erstellt für Kap. 5.2 Gate-Spezifikation + Kap. 5.3 Policy-as-Code
> Basis: Lucaj et al. TechOps Templates (Application, Model, Data Documentation)

## Legende

- **Template-Sektion**: Abschnitt im Lucaj-Template
- **EU AI Act Ref**: Artikel-Referenz aus Template-Annotations
- **R-xx**: Zugeordnetes Requirement aus Kap. 4.6
- **Prüfbare Felder**: Konkrete Template-Felder die als Policy-Input dienen
- **Rego-Policy-Kandidat**: Vorgeschlagene Policy-Rule für Conftest/Gatekeeper
- **Säule**: Conftest (C) / Gatekeeper (GK) / Decision Logs (DL)

---

## 1. Application Documentation Template

| Template-Sektion | EU AI Act | R-xx | Prüfbare Felder | Rego-Policy-Kandidat | Säule |
|---|---|---|---|---|---|
| General Information / Purpose | Art. 11, Annex IV §1-3 | R012 (Zweckbestimmung) | `intended_purpose`, `sector`, `prohibited_uses` | `policy_purpose_declaration_complete` — prüft ob alle Pflichtfelder ausgefüllt | C |
| Risk Classification | Art. 5-7 | R001 (Risikobewertung) | `risk_class`, `classification_reasoning` | `policy_risk_classification_valid` — prüft ob Klasse ∈ {high, limited, minimal} + Begründung vorhanden | C |
| Application Functionality | Art. 11, 13 | R007 (Transparenz) | `instructions_for_deployers`, `model_capabilities`, `limitations` | `policy_transparency_docs_present` — prüft ob Deployer-Instruktionen + Limitationen dokumentiert | C |
| Models and Datasets | Art. 11, Annex IV §2d | R011 (Konformitätsbewertung) | `model_links[]`, `dataset_links[]` | `policy_model_dataset_traceability` — prüft ob alle referenzierten Models/Datasets dokumentiert sind | C |
| Deployment / Infrastructure | Art. 11, Annex IV §1b-h | R006 (Cybersecurity) | `cloud_provider`, `security_groups`, `api_auth_method` | `policy_deployment_security_baseline` — prüft ob Verschlüsselung + Auth konfiguriert | C |
| Lifecycle Management | Art. 11, Annex IV §6 | R010 (Performance-Monitoring) | `monitoring_metrics[]`, `review_schedule`, `audit_trails` | `policy_monitoring_configured` — prüft ob Monitoring-Endpoints + Metriken definiert | GK |
| Risk Management System | Art. 9 | R001 (Risikobewertung) | `risk_methodology`, `identified_risks[]`, `mitigation_measures[]` | `policy_risk_management_complete` — prüft ob Risiken identifiziert + Mitigationen vorhanden | C |
| Testing / Accuracy | Art. 15 | R003 (Safety-Metriken) | `performance_metrics`, `validation_results`, `accuracy_measures` | `policy_accuracy_threshold_met` — prüft ob Metriken über definierten Schwellenwerten | C |
| Robustness | Art. 15 | R003 (Safety-Metriken) | `stress_test_results`, `adversarial_tests` | `policy_robustness_tested` — prüft ob Stress-/Adversarial-Tests durchgeführt | C |
| Cybersecurity | Art. 11, Annex IV §2h | R006 (Cybersecurity) | `data_security`, `access_control`, `incident_response` | `policy_cybersecurity_controls` — prüft ob Security-Maßnahmen dokumentiert | C |
| Human Oversight | Art. 14 | R008 (Human Oversight) | `hitl_mechanisms`, `override_procedures`, `user_training` | `policy_human_oversight_defined` — prüft ob HITL + Override-Prozeduren existieren | GK |
| Incident Management | — | R009 (Incident-Reporting) | `common_issues[]`, `support_contact`, `rollback_mechanisms` | `policy_incident_process_exists` — prüft ob Incident-Prozess + Rollback definiert | GK |
| EU Declaration of Conformity | Art. 47 | R011 (Konformitätsbewertung) | `conformity_statement`, `standards_applied` | `policy_conformity_declaration` — prüft ob Konformitätserklärung vorhanden | C |

## 2. Model Documentation Template

| Template-Sektion | EU AI Act | R-xx | Prüfbare Felder | Rego-Policy-Kandidat | Säule |
|---|---|---|---|---|---|
| Overview / Description | Art. 11 §1 | R012 (Zweckbestimmung) | `model_type`, `model_description`, `status` | `policy_model_description_complete` — prüft ob Typ + Beschreibung + Status vorhanden | C |
| Version Details | Art. 11, Annex IV §1c | R014 (Protokollierung) | `model_version`, `release_date`, `artifacts` | `policy_model_versioning` — prüft ob Version + Artefakt-Pfade dokumentiert | C |
| Intended Use / Out of Scope | Art. 11, Annex IV §1f | R012 (Zweckbestimmung) | `intended_use`, `out_of_scope_uses`, `known_applications` | `policy_intended_use_boundaries` — prüft ob Intended + Out-of-Scope definiert | C |
| Architecture / Training | Art. 11, Annex IV §2b-c | R002 (Data Governance) | `architecture`, `training_methodology`, `compute_resources` | `policy_training_documented` — prüft ob Architektur + Training-Details vorhanden | C |
| Data Collection | Art. 11, Annex IV §2d | R002 (Data Governance) | `data_sources`, `preprocessing_steps`, `data_splitting` | `policy_data_lineage_complete` — prüft ob Datenherkunft + Splits dokumentiert | C |
| Model Bias/Fairness | Art. 11, Annex IV §2f-g | R013 (Bias-Prüfung) | `bias_detection_methods`, `fairness_results`, `mitigation_measures` | `policy_bias_assessment_complete` — prüft ob Bias-Test durchgeführt + dokumentiert | C |
| Explainability | Art. 11, Annex IV §2e | R007 (Transparenz) | `explainability_techniques`, `post_hoc_models` | `policy_explainability_documented` — prüft ob Erklärbarkeits-Methode dokumentiert | C |

## 3. Data Documentation Template

| Template-Sektion | EU AI Act | R-xx | Prüfbare Felder | Rego-Policy-Kandidat | Säule |
|---|---|---|---|---|---|
| Overview / Description | Art. 10-11 | R002 (Data Governance) | `dataset_description`, `data_types`, `size` | `policy_dataset_description_complete` | C |
| Provenance / Collection | Art. 11, Annex IV §2d | R002 (Data Governance) | `collection_methods[]`, `sources[]`, `ethical_sourcing` | `policy_data_provenance_documented` | C |
| Annotation / Labeling | Art. 11, Annex IV §2d | R002 (Data Governance) | `annotation_process`, `quality_control`, `annotator_demographics` | `policy_annotation_quality_verified` | C |
| Data Pre-Processing | Art. 11, Annex IV §2d-e | R002 (Data Governance) | `cleaning_methods`, `transformation_methods`, `feature_engineering` | `policy_preprocessing_documented` | C |
| Distribution / Licensing | Art. 11, Annex IV §2d | R002 (Data Governance) | `availability`, `license`, `user_rights` | `policy_data_license_valid` | C |
| Data Risk Assessment | — | R001 (Risikobewertung) | `risk_description`, `potential_biases` | `policy_data_risk_assessed` | C |
| Cybersecurity Measures | Art. 11, Annex IV §5 | R006 (Cybersecurity) | `encryption`, `access_control`, `audit_logs` | `policy_data_security_controls` | C |
| Post-Market Monitoring | — | R010 (Performance-Monitoring) | `drift_detection`, `audit_logs`, `action_plans` | `policy_data_drift_monitoring` — prüft ob Drift-Detection konfiguriert | GK |

---

## Querschnitt: Decision Logs (Säule 3)

| Scope | R-xx | Policy-Output → Evidence Store |
|---|---|---|
| Alle Conftest-Policies | R005 (Evidence-Persistierung) | Jede allow/deny-Entscheidung → `compliance.quality_gate_results` mit `gate_type=conftest_*` |
| Alle Gatekeeper-Policies | R005 (Evidence-Persistierung) | Jede admit/reject-Entscheidung → `compliance.quality_gate_results` mit `gate_type=gatekeeper_*` |
| Audit Trail Integrität | R014 (Protokollierung) | Hash-Chain (DP-7) sichert Unveränderlichkeit aller Entscheidungen |

---

## Coverage-Matrix: R-xx → Policy-Abdeckung

| R-xx | Kurztitel | Lucaj-Template(s) | Anzahl Policies | Säule(n) |
|---|---|---|---|---|
| R001 | Risikobewertung | App (Risk Classification + Risk Mgmt), Data (Risk Assessment) | 3 | C |
| R002 | Data Governance | Model (Architecture, Data Collection), Data (alle Sektionen) | 5 | C |
| R003 | Safety-Metriken | App (Testing/Accuracy, Robustness) | 2 | C |
| R004 | Strategische Verankerung | — (kein Template-Feld) | 0 | manuell |
| R005 | Evidence-Persistierung | Querschnitt Decision Logs | 2 | DL |
| R006 | Cybersecurity | App (Cybersecurity, Deployment), Data (Cybersecurity) | 3 | C |
| R007 | Transparenz | App (Functionality), Model (Explainability) | 2 | C |
| R008 | Human Oversight | App (Human Oversight) | 1 | GK |
| R009 | Incident-Reporting | App (Incident Management) | 1 | GK |
| R010 | Performance-Monitoring | App (Lifecycle Mgmt), Data (Post-Market) | 2 | GK |
| R011 | Konformitätsbewertung | App (Models/Datasets, EU Declaration) | 2 | C |
| R012 | Zweckbestimmung | App (General Info), Model (Overview, Intended Use) | 3 | C |
| R013 | Bias-Prüfung | Model (Bias/Fairness) | 1 | C |
| R014 | Protokollierung | Model (Version Details), Querschnitt DL | 2 | C + DL |

### Abdeckungs-Statistik
- **14/14 R-xx abgedeckt** (R004 = manuell/strategisch, kein technischer Check)
- **29 Policy-Kandidaten** gesamt
- **22 Conftest** (Pre-Deployment/Deployment)
- **4 Gatekeeper** (Operations)
- **3 Decision Logs** (Querschnitt)

---

## PoC-Empfehlung: Priorisierte Policies für Kap. 6

### Must-Have (Kolloquium-Demo)
1. `policy_risk_classification_valid` (R001) — zeigt Conftest in CI
2. `policy_accuracy_threshold_met` (R003) — zeigt metrische Prüfung
3. `policy_transparency_docs_present` (R007) — zeigt Dokumentations-Gate
4. `policy_monitoring_configured` (R010) — zeigt Gatekeeper in AKS
5. `policy_human_oversight_defined` (R008) — zeigt Gatekeeper Admission
6. Evidence Store Integration (R005/R014) — zeigt Decision Logs

### Nice-to-Have
7. `policy_bias_assessment_complete` (R013)
8. `policy_data_provenance_documented` (R002)
9. `policy_incident_process_exists` (R009)
