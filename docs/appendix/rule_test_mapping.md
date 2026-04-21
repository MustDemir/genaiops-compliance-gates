# Anhang F — Rego Unit Tests: Rule-zu-Test-Mapping

**Erzeugungsdatum:** 2026-04-18  
**Baseline:** 103/103 PASS  
**Quelle:** `tools/extract_rule_test_mapping.py` (auto-generiert aus `policies/**/*.rego` + `policies/**/*_test.rego`)  

Dieser Anhang belegt die Rule-Level-Isolation der PoC-Policy-Engine: Jede der **105 Rego-Regeln** wird durch mindestens eine Unit-Test-Assertion verifiziert. Insgesamt **103 Tests** decken die Muster PASS (positive path), FAIL-basic (missing field), FAIL-edge (invalid/empty values) und HYBRID (D3-Override First-Degree Oversight) ab. Alle Tests werden zeitgleich durch `tests/run_all_rego_tests.sh` (`opa test policies/ tests/fixtures/`) ausgeführt; die Pipeline-Integration (`pipeline/.github/workflows/gate-pipeline.yml`, Layer 1) bricht bei einem Fehlschlag vor jeder Conftest-Gate-Evaluation ab (Shift-Left).

## F.1 Übersicht

| Gate | Req. | EU-AI-Act | Methode | Regeln | Tests | PASS | FAIL-basic | FAIL-edge | HYBRID |
|------|------|-----------|---------|:-----:|:-----:|:----:|:----------:|:---------:|:------:|
| G-DEP-01 | R002 | EU AI Act Art. 10 | AUTO | 9 | 9 | 1 | 5 | 3 | 0 |
| G-DEP-02 | R003 | EU AI Act Art. 15 | AUTO | 16 | 18 | 2 | 14 | 2 | 0 |
| G-DEP-03 | R007 | EU AI Act Art. 13 | AUTO | 9 | 11 | 1 | 7 | 3 | 0 |
| G-DEP-05 | R013 | EU AI Act Art. 10(2)(f) | AUTO | 10 | 12 | 1 | 7 | 4 | 0 |
| G-OPS-02 | R009 | EU AI Act Art. 26(5) | AUTO | 6 | 4 | 2 | 1 | 1 | 0 |
| G-OPS-03 | R010 | EU AI Act Art. 11 | AUTO | 6 | 4 | 1 | 3 | 0 | 0 |
| G-OPS-05 | R005 | EU AI Act Art. 11 | AUTO | 6 | 4 | 1 | 2 | 1 | 0 |
| G-PRE-01 | R001 | EU AI Act Art. 9 | HYBRID | 14 | 8 | 2 | 3 | 2 | 1 |
| G-PRE-04 | R003 | EU AI Act Art. 15 | AUTO | 12 | 14 | 1 | 12 | 1 | 0 |
| G-PRE-05 | R012 | EU AI Act Art. 14 | HYBRID | 17 | 19 | 1 | 0 | 0 | 18 |
| **Gesamt** | — | — | — | **105** | **103** | 13 | 54 | 17 | 19 |

**Legende Muster-Klassen:**

- **PASS** — Positiver Pfad: compliant Input → keine Verletzung (alle deny/violation-Regeln bleiben stumm).
- **FAIL-basic** — Happy-Path-Verstoß: Pflichtfeld fehlt oder strukturelle Annotation nicht gesetzt.
- **FAIL-edge** — Grenzfall: leere/ungültige Werte, Whitespace, boolean-falsche Literale, Grenzwerte.
- **HYBRID** — D3-Override (Art. 14 First-Degree Oversight): automatischer Teil OK, aber manual-review/approval-Bereich blockiert Automatisierung.

## F.2 G-DEP-01 — R002 (EU AI Act Art. 10)

**Policy-Datei:** `policies/pre-deployment/policy_data_provenance_documented.rego`  
**Test-Datei:** `policies/pre-deployment/policy_data_provenance_documented_test.rego`  
**Package:** `genaiops.pre_deployment.data_provenance_documented`  
**Automatisierung:** AUTO  
**Coverage:** 9 Regeln, 9 Tests (FAIL-basic: 5 | FAIL-edge: 3 | PASS: 1)

### F.2.01.1 Regel-Inventar (9 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 29 | `deny` | Check 1: data_provenance section must exist |
| 2 | 38 | `deny` | Check 2: Collection methods must be documented |
| 3 | 44 | `deny` | — |
| 4 | 54 | `deny` | Check 3: Data sources must be listed |
| 5 | 60 | `deny` | — |
| 6 | 70 | `deny` | Check 4: Preprocessing steps must be documented |
| 7 | 76 | `deny` | — |
| 8 | 86 | `deny` | Check 5: Data version must be specified |
| 9 | 92 | `deny` | — |

### F.2.01.2 Test-Inventar (9 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 39 | `test_pass_full_data_provenance` | PASS |
| 2 | 50 | `test_fail_realistic_incomplete_documentation_multi_rule` | FAIL-basic |
| 3 | 65 | `test_fail_missing_data_provenance_section` | FAIL-basic |
| 4 | 76 | `test_fail_missing_collection_methods_field` | FAIL-basic |
| 5 | 88 | `test_fail_missing_sources_field` | FAIL-basic |
| 6 | 99 | `test_fail_missing_preprocessing_steps_field` | FAIL-basic |
| 7 | 115 | `test_fail_empty_collection_methods_array` | FAIL-edge |
| 8 | 125 | `test_fail_empty_preprocessing_steps_array` | FAIL-edge |
| 9 | 139 | `test_fail_empty_data_version_string` | FAIL-edge |

## F.2 G-DEP-02 — R003 (EU AI Act Art. 15)

**Policy-Datei:** `policies/deployment/policy_safety_metrics.rego`  
**Test-Datei:** `policies/deployment/policy_safety_metrics_test.rego`  
**Package:** `genaiops.deployment.safety_metrics`  
**Automatisierung:** AUTO  
**Coverage:** 16 Regeln, 18 Tests (FAIL-basic: 14 | FAIL-edge: 2 | PASS: 2)

### F.2.02.1 Regel-Inventar (16 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 31 | `deny` | Check 1: Accuracy threshold |
| 2 | 36 | `deny` | Check 1: Accuracy threshold |
| 3 | 46 | `deny` | Check 2: Latency P95 threshold |
| 4 | 51 | `deny` | Check 2: Latency P95 threshold |
| 5 | 61 | `deny` | Check 3: Safety score threshold |
| 6 | 66 | `deny` | Check 3: Safety score threshold |
| 7 | 76 | `deny` | Check 4: gate_result.all_passed consistency |
| 8 | 85 | `deny` | Check 5: Eval run metadata must be present |
| 9 | 90 | `deny` | Check 5: Eval run metadata must be present |
| 10 | 100 | `deny` | Ref: Lucaj Template — subgroup sensitivity testing |
| 11 | 105 | `deny` | Ref: Lucaj Template — subgroup sensitivity testing |
| 12 | 111 | `deny` | — |
| 13 | 116 | `deny` | — |
| 14 | 127 | `deny` | Ref: Lucaj Template — adversarial robustness testing |
| 15 | 132 | `deny` | Ref: Lucaj Template — adversarial robustness testing |
| 16 | 138 | `deny` | — |

### F.2.02.2 Test-Inventar (18 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 49 | `test_pass_full_eval_results` | PASS |
| 2 | 60 | `test_fail_realistic_multi_rule_eval_failure` | FAIL-basic |
| 3 | 76 | `test_fail_accuracy_missing` | FAIL-basic |
| 4 | 87 | `test_fail_accuracy_below_threshold` | FAIL-basic |
| 5 | 102 | `test_fail_latency_p95_missing` | FAIL-basic |
| 6 | 112 | `test_fail_latency_p95_above_threshold` | FAIL-basic |
| 7 | 127 | `test_fail_safety_score_missing` | FAIL-basic |
| 8 | 137 | `test_fail_safety_score_below_threshold` | FAIL-basic |
| 9 | 151 | `test_fail_gate_result_all_passed_false` | PASS |
| 10 | 166 | `test_fail_run_id_missing` | FAIL-basic |
| 11 | 176 | `test_fail_run_id_empty_string` | FAIL-edge |
| 12 | 191 | `test_fail_subgroup_analysis_section_missing` | FAIL-basic |
| 13 | 198 | `test_fail_subgroup_analysis_performed_field_missing` | FAIL-basic |
| 14 | 209 | `test_fail_subgroup_analysis_performed_false` | FAIL-basic |
| 15 | 219 | `test_fail_subgroup_analysis_empty_subgroups` | FAIL-edge |
| 16 | 234 | `test_fail_adversarial_tests_section_missing` | FAIL-basic |
| 17 | 241 | `test_fail_adversarial_tests_performed_field_missing` | FAIL-basic |
| 18 | 252 | `test_fail_adversarial_tests_performed_false` | FAIL-basic |

## F.2 G-DEP-03 — R007 (EU AI Act Art. 13)

**Policy-Datei:** `policies/deployment/policy_transparency_docs_present.rego`  
**Test-Datei:** `policies/deployment/policy_transparency_docs_present_test.rego`  
**Package:** `genaiops.deployment.transparency_docs_present`  
**Automatisierung:** AUTO  
**Coverage:** 9 Regeln, 11 Tests (FAIL-basic: 7 | FAIL-edge: 3 | PASS: 1)

### F.2.03.1 Regel-Inventar (9 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 29 | `deny` | Check 1: transparency section must exist |
| 2 | 38 | `deny` | Check 2: Instructions for deployers must be present |
| 3 | 44 | `deny` | — |
| 4 | 53 | `deny` | Check 3: Model capabilities must be documented |
| 5 | 59 | `deny` | — |
| 6 | 68 | `deny` | Check 4: Known limitations must be documented |
| 7 | 74 | `deny` | — |
| 8 | 84 | `deny` | Check 5: AI content labeling must be configured (Art. 50 GenAI) |
| 9 | 90 | `deny` | — |

### F.2.03.2 Test-Inventar (11 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 38 | `test_pass_full_transparency_documentation` | PASS |
| 2 | 48 | `test_fail_realistic_incomplete_transparency_multi_rule` | FAIL-basic |
| 3 | 61 | `test_fail_missing_transparency_section` | FAIL-basic |
| 4 | 72 | `test_fail_missing_instructions_for_deployers_field` | FAIL-basic |
| 5 | 84 | `test_fail_empty_instructions_for_deployers_string` | FAIL-edge |
| 6 | 98 | `test_fail_missing_model_capabilities_field` | FAIL-basic |
| 7 | 110 | `test_fail_empty_model_capabilities_string` | FAIL-edge |
| 8 | 124 | `test_fail_missing_known_limitations_field` | FAIL-basic |
| 9 | 136 | `test_fail_empty_known_limitations_array` | FAIL-edge |
| 10 | 150 | `test_fail_missing_ai_content_labeling_object` | FAIL-basic |
| 11 | 162 | `test_fail_missing_ai_content_labeling_enabled_subfield` | FAIL-basic |

## F.2 G-DEP-05 — R013 (EU AI Act Art. 10(2)(f))

**Policy-Datei:** `policies/pre-deployment/policy_bias_assessment_complete.rego`  
**Test-Datei:** `policies/pre-deployment/policy_bias_assessment_complete_test.rego`  
**Package:** `genaiops.pre_deployment.bias_assessment_complete`  
**Automatisierung:** AUTO  
**Coverage:** 10 Regeln, 12 Tests (FAIL-basic: 7 | FAIL-edge: 4 | PASS: 1)

### F.2.05.1 Regel-Inventar (10 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 29 | `deny` | Check 1: bias_detection section must exist |
| 2 | 38 | `deny` | Check 2: At least one bias detection method must be defined |
| 3 | 44 | `deny` | — |
| 4 | 54 | `deny` | Check 3: Fairness results must be present with at least one metric |
| 5 | 60 | `deny` | — |
| 6 | 66 | `deny` | — |
| 7 | 76 | `deny` | Check 4: Protected attributes must be explicitly listed |
| 8 | 82 | `deny` | — |
| 9 | 92 | `deny` | Check 5: Mitigation measures required if bias was detected |
| 10 | 99 | `deny` | — |

### F.2.05.2 Test-Inventar (12 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 52 | `test_pass_full_bias_assessment` | PASS |
| 2 | 64 | `test_fail_realistic_missing_mitigation_single_rule` | FAIL-basic |
| 3 | 79 | `test_fail_missing_bias_detection_section` | FAIL-basic |
| 4 | 91 | `test_fail_missing_methods_field` | FAIL-basic |
| 5 | 102 | `test_fail_empty_methods_array` | FAIL-edge |
| 6 | 116 | `test_fail_missing_fairness_results_field` | FAIL-basic |
| 7 | 134 | `test_fail_missing_metrics_field` | FAIL-basic |
| 8 | 149 | `test_fail_empty_metrics_array` | FAIL-edge |
| 9 | 168 | `test_fail_missing_protected_attributes_field` | FAIL-basic |
| 10 | 179 | `test_fail_empty_protected_attributes_array` | FAIL-edge |
| 11 | 198 | `test_fail_bias_detected_without_mitigation` | FAIL-basic |
| 12 | 213 | `test_fail_bias_detected_with_empty_mitigation` | FAIL-edge |

## F.2 G-OPS-02 — R009 (EU AI Act Art. 26(5))

**Policy-Datei:** `policies/operations/policy_incident_process_exists.rego`  
**Test-Datei:** `policies/operations/policy_incident_process_exists_test.rego`  
**Package:** `genaiops.operations.incident_process_exists`  
**Automatisierung:** AUTO  
**Coverage:** 6 Regeln, 4 Tests (FAIL-basic: 1 | FAIL-edge: 1 | PASS: 2)

### F.2.02.1 Regel-Inventar (6 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 35 | `violation` | Check 1: Incident response must be configured |
| 2 | 40 | `violation` | Check 1: Incident response must be configured |
| 3 | 49 | `violation` | Check 2: Incident contact must be specified |
| 4 | 54 | `violation` | Check 2: Incident contact must be specified |
| 5 | 63 | `violation` | Check 3: Rollback mechanism must be available |
| 6 | 68 | `violation` | Check 3: Rollback mechanism must be available |

### F.2.02.2 Test-Inventar (4 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 37 | `test_pass_conftest_mode_compliant_deployment` | PASS |
| 2 | 44 | `test_pass_gatekeeper_mode_incident_annotations_present` | PASS |
| 3 | 54 | `test_fail_missing_incident_contact_annotation` | FAIL-basic |
| 4 | 70 | `test_fail_rollback_mechanism_wrong_value` | FAIL-edge |

## F.2 G-OPS-03 — R010 (EU AI Act Art. 11)

**Policy-Datei:** `policies/operations/policy_monitoring_configured.rego`  
**Test-Datei:** `policies/operations/policy_monitoring_configured_test.rego`  
**Package:** `genaiops.operations.monitoring_configured`  
**Automatisierung:** AUTO  
**Coverage:** 6 Regeln, 4 Tests (FAIL-basic: 3 | PASS: 1)

### F.2.03.1 Regel-Inventar (6 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 33 | `violation` | Check 1: Drift detection must be enabled |
| 2 | 38 | `violation` | Check 1: Drift detection must be enabled |
| 3 | 47 | `violation` | Check 2: ServiceMonitor must be configured |
| 4 | 52 | `violation` | Check 2: ServiceMonitor must be configured |
| 5 | 61 | `violation` | Check 3: Prometheus scrape config present |
| 6 | 66 | `violation` | Check 3: Prometheus scrape config present |

### F.2.03.2 Test-Inventar (4 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 34 | `test_pass_compliant_deployment` | PASS |
| 2 | 45 | `test_fail_missing_drift_detection_annotation` | FAIL-basic |
| 3 | 61 | `test_fail_service_monitor_disabled_value` | FAIL-basic |
| 4 | 75 | `test_fail_prometheus_scrape_missing_annotation` | FAIL-basic |

## F.2 G-OPS-05 — R005 (EU AI Act Art. 11)

**Policy-Datei:** `policies/operations/policy_evidence_completeness.rego`  
**Test-Datei:** `policies/operations/policy_evidence_completeness_test.rego`  
**Package:** `genaiops.operations.evidence_completeness`  
**Automatisierung:** AUTO  
**Coverage:** 6 Regeln, 4 Tests (FAIL-basic: 2 | FAIL-edge: 1 | PASS: 1)

### F.2.05.1 Regel-Inventar (6 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 41 | `violation` | Check 1: Evidence Store connection declared |
| 2 | 46 | `violation` | Check 1: Evidence Store connection declared |
| 3 | 55 | `violation` | Check 2: Hash-chain integrity enabled |
| 4 | 60 | `violation` | Check 2: Hash-chain integrity enabled |
| 5 | 69 | `violation` | Check 3: Evidence store type specified (for audit documentation) |
| 6 | 74 | `violation` | Check 3: Evidence store type specified (for audit documentation) |

### F.2.05.2 Test-Inventar (4 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 34 | `test_pass_compliant_deployment` | PASS |
| 2 | 44 | `test_fail_missing_evidence_store_connected_annotation` | FAIL-basic |
| 3 | 59 | `test_fail_hash_chain_disabled_value` | FAIL-basic |
| 4 | 73 | `test_fail_empty_evidence_store_type` | FAIL-edge |

## F.2 G-PRE-01 — R001 (EU AI Act Art. 9)

**Policy-Datei:** `policies/pre-deployment/policy_risk_classification.rego`  
**Test-Datei:** `policies/pre-deployment/policy_risk_classification_test.rego`  
**Package:** `genaiops.pre_deployment.risk_classification`  
**Automatisierung:** HYBRID  
**Coverage:** 14 Regeln, 8 Tests (FAIL-basic: 3 | FAIL-edge: 2 | HYBRID: 1 | PASS: 2)

### F.2.01.1 Regel-Inventar (14 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 26 | `deny` | — |
| 2 | 32 | `deny` | — |
| 3 | 38 | `deny` | — |
| 4 | 46 | `deny` | — |
| 5 | 51 | `deny` | — |
| 6 | 57 | `deny` | — |
| 7 | 63 | `deny` | — |
| 8 | 70 | `deny` | — |
| 9 | 76 | `deny` | — |
| 10 | 86 | `deny` | These rules check that the MANUAL review step has been documented. |
| 11 | 91 | `deny` | These rules check that the MANUAL review step has been documented. |
| 12 | 97 | `deny` | — |
| 13 | 102 | `deny` | — |
| 14 | 108 | `deny` | — |

### F.2.01.2 Test-Inventar (8 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 27 | `test_pass_valid_high_risk_scenario` | PASS |
| 2 | 32 | `test_pass_minimal_risk_without_annex_or_mitigation` | PASS |
| 3 | 45 | `test_fail_missing_risk_class` | FAIL-basic |
| 4 | 58 | `test_fail_empty_risk_class_string` | FAIL-edge |
| 5 | 68 | `test_fail_invalid_risk_class_value` | FAIL-basic |
| 6 | 82 | `test_fail_high_risk_without_annex_reference` | FAIL-basic |
| 7 | 98 | `test_fail_high_risk_empty_mitigation_measures` | FAIL-edge |
| 8 | 112 | `test_fail_missing_manual_review_section` | HYBRID |

## F.2 G-PRE-04 — R003 (EU AI Act Art. 15)

**Policy-Datei:** `policies/pre-deployment/policy_security_baseline.rego`  
**Test-Datei:** `policies/pre-deployment/policy_security_baseline_test.rego`  
**Package:** `genaiops.pre_deployment.security_baseline`  
**Automatisierung:** AUTO  
**Coverage:** 12 Regeln, 14 Tests (FAIL-basic: 12 | FAIL-edge: 1 | PASS: 1)

### F.2.04.1 Regel-Inventar (12 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 35 | `deny` | P1: Non-Root Enforcement (CIS 5.2.6) [MUST] |
| 2 | 41 | `deny` | — |
| 3 | 47 | `deny` | — |
| 4 | 57 | `deny` | P2: Resource Limits (CIS 5.4.x) [MUST] |
| 5 | 63 | `deny` | — |
| 6 | 70 | `deny` | — |
| 7 | 83 | `deny` | Waiverable with Security Lead approval (14 days). |
| 8 | 89 | `deny` | Waiverable with Security Lead approval (14 days). |
| 9 | 101 | `deny` | P4: No Secrets in Plain ENV [MUST] |
| 10 | 116 | `deny` | P6: No Privilege Escalation (CIS 5.2.5) [MUST] |
| 11 | 127 | `deny` | P6b: Drop ALL Capabilities (CIS 5.2.7) [MUST] |
| 12 | 133 | `deny` | — |

### F.2.04.2 Test-Inventar (14 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 73 | `test_pass_compliant_deployment` | PASS |
| 2 | 84 | `test_fail_realistic_multi_rule_noncompliant` | FAIL-basic |
| 3 | 98 | `test_fail_runAsNonRoot_not_set` | FAIL-basic |
| 4 | 111 | `test_fail_runAsNonRoot_explicit_false` | FAIL-basic |
| 5 | 121 | `test_fail_runAsUser_zero` | FAIL-edge |
| 6 | 136 | `test_fail_no_resources_limits` | FAIL-basic |
| 7 | 144 | `test_fail_missing_limits_cpu` | FAIL-basic |
| 8 | 151 | `test_fail_missing_limits_memory` | FAIL-basic |
| 9 | 162 | `test_fail_readOnlyRootFilesystem_not_set` | FAIL-basic |
| 10 | 175 | `test_fail_readOnlyRootFilesystem_explicit_false` | FAIL-basic |
| 11 | 189 | `test_fail_plain_secret_in_env` | FAIL-basic |
| 12 | 205 | `test_fail_allowPrivilegeEscalation_not_false` | FAIL-basic |
| 13 | 219 | `test_fail_capabilities_missing` | FAIL-basic |
| 14 | 232 | `test_fail_capabilities_drop_not_all` | FAIL-basic |

## F.2 G-PRE-05 — R012 (EU AI Act Art. 14)

**Policy-Datei:** `policies/pre-deployment/policy_governance_approval.rego`  
**Test-Datei:** `policies/pre-deployment/policy_governance_approval_test.rego`  
**Package:** `genaiops.pre_deployment.governance_approval`  
**Automatisierung:** HYBRID  
**Coverage:** 17 Regeln, 19 Tests (HYBRID: 18 | PASS: 1)

### F.2.05.1 Regel-Inventar (17 Regeln)

| Nr. | Zeile | Art | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|-----------------------------------|
| 1 | 27 | `deny` | D3-Override: Art. 14 = First-Degree Oversight → max HYBRID |
| 2 | 32 | `deny` | — |
| 3 | 38 | `deny` | — |
| 4 | 44 | `deny` | — |
| 5 | 51 | `deny` | — |
| 6 | 56 | `deny` | — |
| 7 | 62 | `deny` | — |
| 8 | 67 | `deny` | — |
| 9 | 73 | `deny` | — |
| 10 | 79 | `deny` | — |
| 11 | 86 | `deny` | — |
| 12 | 91 | `deny` | — |
| 13 | 101 | `deny` | The actual approval decision is made by a human — Conftest only checks evidence. |
| 14 | 106 | `deny` | The actual approval decision is made by a human — Conftest only checks evidence. |
| 15 | 112 | `deny` | — |
| 16 | 117 | `deny` | — |
| 17 | 123 | `deny` | — |

### F.2.05.2 Test-Inventar (19 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 54 | `test_pass_full_governance_approval` | PASS |
| 2 | 65 | `test_fail_realistic_multi_rule_incomplete_governance` | HYBRID |
| 3 | 76 | `test_fail_fria_completed_missing` | HYBRID |
| 4 | 90 | `test_fail_fria_completed_false` | HYBRID |
| 5 | 105 | `test_fail_affected_rights_missing` | HYBRID |
| 6 | 119 | `test_fail_affected_rights_empty_array` | HYBRID |
| 7 | 134 | `test_fail_oversight_model_missing` | HYBRID |
| 8 | 144 | `test_fail_oversight_model_empty_string` | HYBRID |
| 9 | 158 | `test_fail_oversight_lead_missing` | HYBRID |
| 10 | 168 | `test_fail_oversight_lead_empty_string` | HYBRID |
| 11 | 184 | `test_fail_kill_switch_missing_for_high_risk` | HYBRID |
| 12 | 202 | `test_fail_kill_switch_false_for_high_risk` | HYBRID |
| 13 | 219 | `test_fail_conformity_declaration_missing` | HYBRID |
| 14 | 229 | `test_fail_conformity_declaration_false` | HYBRID |
| 15 | 245 | `test_fail_approval_section_missing` | HYBRID |
| 16 | 252 | `test_fail_approval_approved_by_missing` | HYBRID |
| 17 | 262 | `test_fail_approval_approved_by_empty_string` | HYBRID |
| 18 | 272 | `test_fail_approval_approved_at_missing` | HYBRID |
| 19 | 282 | `test_fail_approval_approved_at_empty_string` | HYBRID |

## F.3 Reproduzierbarkeit

Zur Verifikation der obigen Zahlen (10 Policies / 105 Regeln / 103 Tests):

```bash
# OPA ≥ 1.15.2 vorausgesetzt
./tests/run_all_rego_tests.sh --quiet   # Erwartet: 'PASS: 103/103'
python3 tools/extract_rule_test_mapping.py
```

Die JSON-Ground-Truth-Variante liegt unter `docs/appendix/rule_test_mapping.json` und wird über `tools/extract_rule_test_mapping.py` aus den Quell-Regos regeneriert.
