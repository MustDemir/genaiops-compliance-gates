# Rego Unit Tests — Rule-to-Test Mapping

**Erzeugungsdatum:** 2026-08-14  
**Baseline:** 141/141 PASS  
**Quelle:** `tools/extract_rule_test_mapping.py` (auto-generiert aus `policies/**/*.rego` + `policies/**/*_test.rego`)  

Dieses Dokument belegt die Rule-Level-Isolation der PoC-Policy-Engine: Jede der **143 Rego-Regeln** wird durch mindestens eine Unit-Test-Assertion verifiziert. Insgesamt **141 Tests** decken die Muster PASS (positive path), FAIL-basic (missing field), FAIL-edge (invalid/empty values) und HYBRID (D3-Override First-Degree Oversight) ab. Alle Tests werden zeitgleich durch `tests/run_all_rego_tests.sh` (`opa test policies/ tests/fixtures/`) ausgeführt; die Pipeline-Integration (`pipeline/.github/workflows/gate-pipeline.yml`, Layer 1) bricht bei einem Fehlschlag vor jeder Conftest-Gate-Evaluation ab (Shift-Left).

## F.1 Übersicht

| Gate | Req. | EU-AI-Act | Methode | Checks | Regeln | Tests | PASS | FAIL-basic | FAIL-edge | HYBRID |
|------|------|-----------|---------|:-----:|:-----:|:-----:|:----:|:----------:|:---------:|:------:|
| G-DEP-01 | R002 | EU AI Act Art. 10 | AUTO | 6 | 9 | 9 | 1 | 5 | 3 | 0 |
| G-DEP-02 | R003 | EU AI Act Art. 15 | AUTO | 2 | 16 | 18 | 2 | 14 | 2 | 0 |
| G-DEP-03 | R007 | EU AI Act Art. 13 | AUTO | 2 | 9 | 11 | 1 | 7 | 3 | 0 |
| G-DEP-04 | R011 | EU AI Act Art. 26(1) | AUTO | 1 | 7 | 6 | 1 | 4 | 0 | 1 |
| G-DEP-05 | R013 | EU AI Act Art. 10(2)(f) | AUTO | 1 | 10 | 12 | 1 | 7 | 4 | 0 |
| G-DEP-06 | R014 | EU AI Act Art. 12 | AUTO | 1 | 8 | 7 | 1 | 5 | 1 | 0 |
| G-OPS-01 | R008 | EU AI Act Art. 14 | HYBRID | 1 | 6 | 7 | 1 | 3 | 0 | 3 |
| G-OPS-02 | R009 | EU AI Act Art. 26(5) | AUTO | 1 | 6 | 4 | 2 | 1 | 1 | 0 |
| G-OPS-03 | R010 | EU AI Act Art. 72 | AUTO | 2 | 6 | 4 | 1 | 3 | 0 | 0 |
| G-OPS-04 | R003 | EU AI Act Art. 15 | AUTO | 1 | 4 | 5 | 1 | 4 | 0 | 0 |
| G-OPS-05 | R005 | EU AI Act Art. 12 | AUTO | 3 | 6 | 4 | 1 | 2 | 1 | 0 |
| G-PRE-01 | R001 | EU AI Act Art. 9 | HYBRID | 1 | 14 | 8 | 2 | 3 | 2 | 1 |
| G-PRE-02 | R012 | EU AI Act Art. 27 | HYBRID | 1 | 6 | 6 | 1 | 4 | 1 | 0 |
| G-PRE-03 | R001 | EU AI Act Art. 9 | HYBRID | 2 | 7 | 7 | 1 | 5 | 1 | 0 |
| G-PRE-04 | R003 | EU AI Act Art. 15 | AUTO | 6 | 12 | 14 | 1 | 12 | 1 | 0 |
| G-PRE-05 | R004 | EU AI Act Art. 14 | HYBRID | 1 | 17 | 19 | 1 | 0 | 0 | 18 |
| **Gesamt** | — | — | — | **32** | **143** | **141** | 19 | 79 | 20 | 23 |

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

### F.2.01.0 Check-Inventar (6 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 10, Art. 11 | `policy_data_provenance_documented` | 0 |
| C-02 | MUST | Art. 10, Art. 11 | `policy_training_documented` | 0 |
| C-03 | MUST | Art. 10, Art. 11 | `policy_data_lineage_complete` | 0 |
| C-04 | MUST | Art. 10, Art. 11 | `policy_dataset_description_complete` | 0 |
| C-05 | MUST | Art. 10, Art. 11 | `policy_annotation_quality_verified` | 0 |
| C-06 | MUST | Art. 10, Art. 11 | `policy_data_license_valid` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 9 — ohne: 9 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.01.1 Regel-Inventar (9 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 29 | `deny` | — | Check 1: data_provenance section must exist |
| 2 | 38 | `deny` | — | Check 2: Collection methods must be documented |
| 3 | 44 | `deny` | — | — |
| 4 | 54 | `deny` | — | Check 3: Data sources must be listed |
| 5 | 60 | `deny` | — | — |
| 6 | 70 | `deny` | — | Check 4: Preprocessing steps must be documented |
| 7 | 76 | `deny` | — | — |
| 8 | 86 | `deny` | — | Check 5: Data version must be specified |
| 9 | 92 | `deny` | — | — |

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

### F.2.02.0 Check-Inventar (2 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 15 | `policy_safety_metrics` | 0 |
| C-02 | SHOULD | Art. 15 | `policy_safety_metrics` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 16 — ohne: 16 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.02.1 Regel-Inventar (16 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 34 | `deny` | — | Check 1: Accuracy threshold |
| 2 | 39 | `deny` | — | Check 1: Accuracy threshold |
| 3 | 49 | `deny` | — | Check 2: Latency P95 threshold |
| 4 | 54 | `deny` | — | Check 2: Latency P95 threshold |
| 5 | 64 | `deny` | — | Check 3: Safety score threshold |
| 6 | 69 | `deny` | — | Check 3: Safety score threshold |
| 7 | 79 | `deny` | — | Check 4: gate_result.all_passed consistency |
| 8 | 88 | `deny` | — | Check 5: Eval run metadata must be present |
| 9 | 93 | `deny` | — | Check 5: Eval run metadata must be present |
| 10 | 105 | `warn` | — | recorded as advisory finding in the Evidence Store payload. |
| 11 | 110 | `warn` | — | recorded as advisory finding in the Evidence Store payload. |
| 12 | 116 | `warn` | — | — |
| 13 | 121 | `warn` | — | — |
| 14 | 134 | `warn` | — | recorded as advisory finding in the Evidence Store payload. |
| 15 | 139 | `warn` | — | recorded as advisory finding in the Evidence Store payload. |
| 16 | 145 | `warn` | — | — |

### F.2.02.2 Test-Inventar (18 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 49 | `test_pass_full_eval_results` | PASS |
| 2 | 60 | `test_fail_realistic_multi_rule_eval_failure` | FAIL-basic |
| 3 | 74 | `test_fail_accuracy_missing` | FAIL-basic |
| 4 | 85 | `test_fail_accuracy_below_threshold` | FAIL-basic |
| 5 | 100 | `test_fail_latency_p95_missing` | FAIL-basic |
| 6 | 110 | `test_fail_latency_p95_above_threshold` | FAIL-basic |
| 7 | 125 | `test_fail_safety_score_missing` | FAIL-basic |
| 8 | 135 | `test_fail_safety_score_below_threshold` | FAIL-basic |
| 9 | 149 | `test_fail_gate_result_all_passed_false` | PASS |
| 10 | 164 | `test_fail_run_id_missing` | FAIL-basic |
| 11 | 174 | `test_fail_run_id_empty_string` | FAIL-edge |
| 12 | 189 | `test_fail_subgroup_analysis_section_missing` | FAIL-basic |
| 13 | 196 | `test_fail_subgroup_analysis_performed_field_missing` | FAIL-basic |
| 14 | 207 | `test_fail_subgroup_analysis_performed_false` | FAIL-basic |
| 15 | 217 | `test_fail_subgroup_analysis_empty_subgroups` | FAIL-edge |
| 16 | 232 | `test_fail_adversarial_tests_section_missing` | FAIL-basic |
| 17 | 239 | `test_fail_adversarial_tests_performed_field_missing` | FAIL-basic |
| 18 | 250 | `test_fail_adversarial_tests_performed_false` | FAIL-basic |

## F.2 G-DEP-03 — R007 (EU AI Act Art. 13)

**Policy-Datei:** `policies/deployment/policy_transparency_docs_present.rego`  
**Test-Datei:** `policies/deployment/policy_transparency_docs_present_test.rego`  
**Package:** `genaiops.deployment.transparency_docs_present`  
**Automatisierung:** AUTO  
**Coverage:** 9 Regeln, 11 Tests (FAIL-basic: 7 | FAIL-edge: 3 | PASS: 1)

### F.2.03.0 Check-Inventar (2 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 13, Art. 26 Abs. 7, Art. 50 | `policy_transparency_docs_present` | 0 |
| C-02 | MUST | Art. 13, Art. 26 Abs. 7, Art. 50 | `policy_explainability_documented` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 9 — ohne: 9 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.03.1 Regel-Inventar (9 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 29 | `deny` | — | Check 1: transparency section must exist |
| 2 | 38 | `deny` | — | Check 2: Instructions for deployers must be present |
| 3 | 44 | `deny` | — | — |
| 4 | 53 | `deny` | — | Check 3: Model capabilities must be documented |
| 5 | 59 | `deny` | — | — |
| 6 | 68 | `deny` | — | Check 4: Known limitations must be documented |
| 7 | 74 | `deny` | — | — |
| 8 | 84 | `deny` | — | Check 5: AI content labeling must be configured (Art. 50 GenAI) |
| 9 | 90 | `deny` | — | — |

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

## F.2 G-DEP-04 — R011 (EU AI Act Art. 26(1))

**Policy-Datei:** `policies/deployment/policy_conformity_verified.rego`  
**Test-Datei:** `policies/deployment/policy_conformity_verified_test.rego`  
**Package:** `genaiops.deployment.conformity_verified`  
**Automatisierung:** AUTO  
**Coverage:** 7 Regeln, 6 Tests (FAIL-basic: 4 | HYBRID: 1 | PASS: 1)

### F.2.04.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 26 Abs. 1 | `policy_conformity_verified` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 7 — ohne: 7 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.04.1 Regel-Inventar (7 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 27 | `deny` | — | 5. provider documented (model-dataset traceability) |
| 2 | 33 | `deny` | — | — |
| 3 | 39 | `deny` | — | — |
| 4 | 45 | `deny` | — | — |
| 5 | 50 | `deny` | — | — |
| 6 | 56 | `deny` | — | — |
| 7 | 62 | `deny` | — | — |

### F.2.04.2 Test-Inventar (6 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 11 | `test_pass_valid_conformity_scenario` | PASS |
| 2 | 15 | `test_fail_missing_conformity_section` | HYBRID |
| 3 | 20 | `test_fail_ce_marking_not_verified` | FAIL-basic |
| 4 | 25 | `test_fail_provider_docs_not_received` | FAIL-basic |
| 5 | 30 | `test_fail_missing_provider_contact` | FAIL-basic |
| 6 | 36 | `test_fail_missing_model_version` | FAIL-basic |

## F.2 G-DEP-05 — R013 (EU AI Act Art. 10(2)(f))

**Policy-Datei:** `policies/pre-deployment/policy_bias_assessment_complete.rego`  
**Test-Datei:** `policies/pre-deployment/policy_bias_assessment_complete_test.rego`  
**Package:** `genaiops.pre_deployment.bias_assessment_complete`  
**Automatisierung:** AUTO  
**Coverage:** 10 Regeln, 12 Tests (FAIL-basic: 7 | FAIL-edge: 4 | PASS: 1)

### F.2.05.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | SHOULD | Art. 9 Abs. 2 lit. a, Art. 10 Abs. 2 lit. f, Art. 15 | `policy_bias_assessment_complete` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 10 — ohne: 10 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.05.1 Regel-Inventar (10 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 35 | `warn` | — | Check 1: bias_detection section must exist |
| 2 | 44 | `warn` | — | Check 2: At least one bias detection method must be defined |
| 3 | 50 | `warn` | — | — |
| 4 | 60 | `warn` | — | Check 3: Fairness results must be present with at least one metric |
| 5 | 66 | `warn` | — | — |
| 6 | 72 | `warn` | — | — |
| 7 | 82 | `warn` | — | Check 4: Protected attributes must be explicitly listed |
| 8 | 88 | `warn` | — | — |
| 9 | 98 | `warn` | — | Check 5: Mitigation measures required if bias was detected |
| 10 | 105 | `warn` | — | — |

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

## F.2 G-DEP-06 — R014 (EU AI Act Art. 12)

**Policy-Datei:** `policies/deployment/policy_logging_configured.rego`  
**Test-Datei:** `policies/deployment/policy_logging_configured_test.rego`  
**Package:** `genaiops.deployment.logging_configured`  
**Automatisierung:** AUTO  
**Coverage:** 8 Regeln, 7 Tests (FAIL-basic: 5 | FAIL-edge: 1 | PASS: 1)

### F.2.06.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 12, Art. 26 Abs. 3 | `policy_logging_configured` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 8 — ohne: 8 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.06.1 Regel-Inventar (8 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 26 | `deny` | — | — |
| 2 | 32 | `deny` | — | — |
| 3 | 38 | `deny` | — | — |
| 4 | 43 | `deny` | — | — |
| 5 | 49 | `deny` | — | — |
| 6 | 54 | `deny` | — | — |
| 7 | 63 | `deny` | — | — |
| 8 | 68 | `deny` | — | — |

### F.2.06.2 Test-Inventar (7 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 26 | `test_pass_valid_logging_scenario` | PASS |
| 2 | 35 | `test_fail_missing_logging_section` | FAIL-basic |
| 3 | 42 | `test_fail_logging_disabled` | FAIL-basic |
| 4 | 49 | `test_fail_missing_event_types` | FAIL-basic |
| 5 | 62 | `test_fail_empty_event_types` | FAIL-edge |
| 6 | 69 | `test_fail_retention_below_minimum` | FAIL-basic |
| 7 | 76 | `test_fail_missing_log_accessibility` | FAIL-basic |

## F.2 G-OPS-01 — R008 (EU AI Act Art. 14)

**Policy-Datei:** `policies/operations/policy_human_oversight_operational.rego`  
**Test-Datei:** `policies/operations/policy_human_oversight_operational_test.rego`  
**Package:** `genaiops.operations.human_oversight_operational`  
**Automatisierung:** HYBRID  
**Coverage:** 6 Regeln, 7 Tests (FAIL-basic: 3 | HYBRID: 3 | PASS: 1)

### F.2.01.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 14, Art. 26 Abs. 2 | `policy_human_oversight_operational` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 6 — ohne: 6 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.01.1 Regel-Inventar (6 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 27 | `deny` | — | 4. real-time monitoring active |
| 2 | 33 | `deny` | — | — |
| 3 | 38 | `deny` | — | — |
| 4 | 44 | `deny` | — | — |
| 5 | 50 | `deny` | — | — |
| 6 | 56 | `deny` | — | — |

### F.2.01.2 Test-Inventar (7 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 11 | `test_pass_valid_oversight_scenario` | PASS |
| 2 | 15 | `test_fail_missing_oversight_section` | HYBRID |
| 3 | 20 | `test_fail_missing_oversight_roles` | HYBRID |
| 4 | 26 | `test_fail_empty_oversight_roles` | HYBRID |
| 5 | 31 | `test_fail_missing_escalation_procedure` | FAIL-basic |
| 6 | 37 | `test_fail_output_override_false` | FAIL-basic |
| 7 | 42 | `test_fail_real_time_monitoring_false` | FAIL-basic |

## F.2 G-OPS-02 — R009 (EU AI Act Art. 26(5))

**Policy-Datei:** `policies/operations/policy_incident_process_exists.rego`  
**Test-Datei:** `policies/operations/policy_incident_process_exists_test.rego`  
**Package:** `genaiops.operations.incident_process_exists`  
**Automatisierung:** AUTO  
**Coverage:** 6 Regeln, 4 Tests (FAIL-basic: 1 | FAIL-edge: 1 | PASS: 2)

### F.2.02.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 26 Abs. 5, Art. 73 | `policy_incident_process_exists` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 6 — ohne: 6 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.02.1 Regel-Inventar (6 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 35 | `violation` | — | Check 1: Incident response must be configured |
| 2 | 40 | `violation` | — | Check 1: Incident response must be configured |
| 3 | 49 | `violation` | — | Check 2: Incident contact must be specified |
| 4 | 54 | `violation` | — | Check 2: Incident contact must be specified |
| 5 | 63 | `violation` | — | Check 3: Rollback mechanism must be available |
| 6 | 68 | `violation` | — | Check 3: Rollback mechanism must be available |

### F.2.02.2 Test-Inventar (4 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 37 | `test_pass_conftest_mode_compliant_deployment` | PASS |
| 2 | 44 | `test_pass_gatekeeper_mode_incident_annotations_present` | PASS |
| 3 | 54 | `test_fail_missing_incident_contact_annotation` | FAIL-basic |
| 4 | 70 | `test_fail_rollback_mechanism_wrong_value` | FAIL-edge |

## F.2 G-OPS-03 — R010 (EU AI Act Art. 72)

**Policy-Datei:** `policies/operations/policy_monitoring_configured.rego`  
**Test-Datei:** `policies/operations/policy_monitoring_configured_test.rego`  
**Package:** `genaiops.operations.monitoring_configured`  
**Automatisierung:** AUTO  
**Coverage:** 6 Regeln, 4 Tests (FAIL-basic: 3 | PASS: 1)

### F.2.03.0 Check-Inventar (2 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 72, Art. 9 Abs. 2 | `policy_monitoring_configured` | 0 |
| C-02 | MUST | Art. 72, Art. 9 Abs. 2 | `policy_monitoring_configured` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 6 — ohne: 6 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.03.1 Regel-Inventar (6 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 33 | `violation` | — | Check 1: Drift detection must be enabled |
| 2 | 38 | `violation` | — | Check 1: Drift detection must be enabled |
| 3 | 47 | `violation` | — | Check 2: ServiceMonitor must be configured |
| 4 | 52 | `violation` | — | Check 2: ServiceMonitor must be configured |
| 5 | 61 | `violation` | — | Check 3: Prometheus scrape config present |
| 6 | 66 | `violation` | — | Check 3: Prometheus scrape config present |

### F.2.03.2 Test-Inventar (4 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 34 | `test_pass_compliant_deployment` | PASS |
| 2 | 45 | `test_fail_missing_drift_detection_annotation` | FAIL-basic |
| 3 | 61 | `test_fail_service_monitor_disabled_value` | FAIL-basic |
| 4 | 73 | `test_fail_prometheus_scrape_missing_annotation` | FAIL-basic |

## F.2 G-OPS-04 — R003 (EU AI Act Art. 15)

**Policy-Datei:** `policies/operations/policy_data_security_controls.rego`  
**Test-Datei:** `policies/operations/policy_data_security_controls_test.rego`  
**Package:** `genaiops.operations.data_security_controls`  
**Automatisierung:** AUTO  
**Coverage:** 4 Regeln, 5 Tests (FAIL-basic: 4 | PASS: 1)

### F.2.04.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 15 | `policy_data_security_controls` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 4 — ohne: 4 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.04.1 Regel-Inventar (4 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 27 | `deny` | — | 4. encryption in transit enabled |
| 2 | 33 | `deny` | — | — |
| 3 | 39 | `deny` | — | — |
| 4 | 45 | `deny` | — | — |

### F.2.04.2 Test-Inventar (5 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 11 | `test_pass_valid_security_scenario` | PASS |
| 2 | 15 | `test_fail_image_scanning_disabled` | FAIL-basic |
| 3 | 20 | `test_fail_network_policies_missing` | FAIL-basic |
| 4 | 25 | `test_fail_encryption_at_rest_disabled` | FAIL-basic |
| 5 | 30 | `test_fail_encryption_in_transit_disabled` | FAIL-basic |

## F.2 G-OPS-05 — R005 (EU AI Act Art. 12)

**Policy-Datei:** `policies/operations/policy_evidence_completeness.rego`  
**Test-Datei:** `policies/operations/policy_evidence_completeness_test.rego`  
**Package:** `genaiops.operations.evidence_completeness`  
**Automatisierung:** AUTO  
**Coverage:** 6 Regeln, 4 Tests (FAIL-basic: 2 | FAIL-edge: 1 | PASS: 1)

### F.2.05.0 Check-Inventar (3 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 12, Art. 15 | `policy_evidence_completeness` | 0 |
| C-02 | MUST | Art. 12, Art. 15 | `policy_evidence_completeness` | 0 |
| C-03 | MUST | Art. 12, Art. 15 | `policy_evidence_completeness` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 6 — ohne: 6 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.05.1 Regel-Inventar (6 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 41 | `violation` | — | Check 1: Evidence Store connection declared |
| 2 | 46 | `violation` | — | Check 1: Evidence Store connection declared |
| 3 | 55 | `violation` | — | Check 2: Hash-chain integrity enabled |
| 4 | 60 | `violation` | — | Check 2: Hash-chain integrity enabled |
| 5 | 69 | `violation` | — | Check 3: Evidence store type specified (for audit documentation) |
| 6 | 74 | `violation` | — | Check 3: Evidence store type specified (for audit documentation) |

### F.2.05.2 Test-Inventar (4 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 34 | `test_pass_compliant_deployment` | PASS |
| 2 | 44 | `test_fail_missing_evidence_store_connected_annotation` | FAIL-basic |
| 3 | 59 | `test_fail_hash_chain_disabled_value` | FAIL-basic |
| 4 | 71 | `test_fail_empty_evidence_store_type` | FAIL-edge |

## F.2 G-PRE-01 — R001 (EU AI Act Art. 9)

**Policy-Datei:** `policies/pre-deployment/policy_risk_classification.rego`  
**Test-Datei:** `policies/pre-deployment/policy_risk_classification_test.rego`  
**Package:** `genaiops.pre_deployment.risk_classification`  
**Automatisierung:** HYBRID  
**Coverage:** 14 Regeln, 8 Tests (FAIL-basic: 3 | FAIL-edge: 2 | HYBRID: 1 | PASS: 2)

### F.2.01.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 9 | `policy_risk_classification` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 14 — ohne: 14 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.01.1 Regel-Inventar (14 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 26 | `deny` | — | — |
| 2 | 32 | `deny` | — | — |
| 3 | 38 | `deny` | — | — |
| 4 | 46 | `deny` | — | — |
| 5 | 51 | `deny` | — | — |
| 6 | 57 | `deny` | — | — |
| 7 | 63 | `deny` | — | — |
| 8 | 70 | `deny` | — | — |
| 9 | 76 | `deny` | — | — |
| 10 | 86 | `deny` | — | These rules check that the MANUAL review step has been documented. |
| 11 | 91 | `deny` | — | These rules check that the MANUAL review step has been documented. |
| 12 | 97 | `deny` | — | — |
| 13 | 102 | `deny` | — | — |
| 14 | 108 | `deny` | — | — |

### F.2.01.2 Test-Inventar (8 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 27 | `test_pass_valid_high_risk_scenario` | PASS |
| 2 | 32 | `test_pass_minimal_risk_without_annex_or_mitigation` | PASS |
| 3 | 45 | `test_fail_missing_risk_class` | FAIL-basic |
| 4 | 56 | `test_fail_empty_risk_class_string` | FAIL-edge |
| 5 | 66 | `test_fail_invalid_risk_class_value` | FAIL-basic |
| 6 | 80 | `test_fail_high_risk_without_annex_reference` | FAIL-basic |
| 7 | 96 | `test_fail_high_risk_empty_mitigation_measures` | FAIL-edge |
| 8 | 110 | `test_fail_missing_manual_review_section` | HYBRID |

## F.2 G-PRE-02 — R012 (EU AI Act Art. 27)

**Policy-Datei:** `policies/pre-deployment/policy_purpose_declaration.rego`  
**Test-Datei:** `policies/pre-deployment/policy_purpose_declaration_test.rego`  
**Package:** `genaiops.pre_deployment.purpose_declaration`  
**Automatisierung:** HYBRID  
**Coverage:** 6 Regeln, 6 Tests (FAIL-basic: 4 | FAIL-edge: 1 | PASS: 1)

### F.2.02.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 27 | `policy_purpose_declaration` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 6 — ohne: 6 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.02.1 Regel-Inventar (6 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 26 | `deny` | — | 4. FRIA mitigation documented |
| 2 | 31 | `deny` | — | — |
| 3 | 37 | `deny` | — | — |
| 4 | 43 | `deny` | — | — |
| 5 | 48 | `deny` | — | — |
| 6 | 54 | `deny` | — | — |

### F.2.02.2 Test-Inventar (6 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 11 | `test_pass_valid_purpose_scenario` | PASS |
| 2 | 15 | `test_fail_missing_description` | FAIL-basic |
| 3 | 21 | `test_fail_missing_domain` | FAIL-basic |
| 4 | 27 | `test_fail_missing_stakeholder_groups` | FAIL-basic |
| 5 | 33 | `test_fail_empty_stakeholder_groups` | FAIL-edge |
| 6 | 38 | `test_fail_mitigation_not_documented` | FAIL-basic |

## F.2 G-PRE-03 — R001 (EU AI Act Art. 9)

**Policy-Datei:** `policies/pre-deployment/policy_risk_management_complete.rego`  
**Test-Datei:** `policies/pre-deployment/policy_risk_management_complete_test.rego`  
**Package:** `genaiops.pre_deployment.risk_management_complete`  
**Automatisierung:** HYBRID  
**Coverage:** 7 Regeln, 7 Tests (FAIL-basic: 5 | FAIL-edge: 1 | PASS: 1)

### F.2.03.0 Check-Inventar (2 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 9 | `policy_risk_management_complete` | 0 |
| C-02 | MUST | Art. 9 | `policy_risk_management_complete` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 7 — ohne: 7 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.03.1 Regel-Inventar (7 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 27 | `deny` | — | 5. data classification documented |
| 2 | 33 | `deny` | — | — |
| 3 | 39 | `deny` | — | — |
| 4 | 44 | `deny` | — | — |
| 5 | 50 | `deny` | — | — |
| 6 | 57 | `deny` | — | — |
| 7 | 63 | `deny` | — | — |

### F.2.03.2 Test-Inventar (7 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 11 | `test_pass_valid_risk_management_scenario` | PASS |
| 2 | 15 | `test_fail_missing_risk_management_section` | FAIL-basic |
| 3 | 20 | `test_fail_register_not_versioned` | FAIL-basic |
| 4 | 25 | `test_fail_empty_identified_risks` | FAIL-edge |
| 5 | 30 | `test_fail_risk_without_mitigation` | FAIL-basic |
| 6 | 35 | `test_fail_data_risk_not_assessed` | FAIL-basic |
| 7 | 40 | `test_fail_missing_data_classification` | FAIL-basic |

## F.2 G-PRE-04 — R003 (EU AI Act Art. 15)

**Policy-Datei:** `policies/pre-deployment/policy_security_baseline.rego`  
**Test-Datei:** `policies/pre-deployment/policy_security_baseline_test.rego`  
**Package:** `genaiops.pre_deployment.security_baseline`  
**Automatisierung:** AUTO  
**Coverage:** 12 Regeln, 14 Tests (FAIL-basic: 12 | FAIL-edge: 1 | PASS: 1)

### F.2.04.0 Check-Inventar (6 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| P1 | MUST | Art. 15 | `policy_security_baseline` | 3 |
| P2 | MUST | Art. 15 | `policy_security_baseline` | 3 |
| P3 | MUST | Art. 15 | `policy_security_baseline` | 2 |
| P4 | MUST | Art. 15 | `policy_security_baseline` | 1 |
| P5 | SHOULD | Art. 15 | `policy_cybersecurity_controls` | 0 |
| P6 | MUST | Art. 15 | `policy_security_baseline` | 3 |

*Regeln mit Check-ID im Meldungstext: 12 / 12 — ohne: 0 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.04.1 Regel-Inventar (12 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 35 | `deny` | P1 | P1: Non-Root Enforcement (CIS 5.2.6) [MUST] |
| 2 | 41 | `deny` | P1 | — |
| 3 | 47 | `deny` | P1 | — |
| 4 | 57 | `deny` | P2 | P2: Resource Limits (CIS 5.4.x) [MUST] |
| 5 | 63 | `deny` | P2 | — |
| 6 | 70 | `deny` | P2 | — |
| 7 | 83 | `deny` | P3 | contract (blocking). Waiverable with Security Lead approval (14 days). |
| 8 | 89 | `deny` | P3 | contract (blocking). Waiverable with Security Lead approval (14 days). |
| 9 | 101 | `deny` | P4 | P4: No Secrets in Plain ENV [MUST] |
| 10 | 116 | `deny` | P6 | P6: No Privilege Escalation (CIS 5.2.5) [MUST] |
| 11 | 127 | `deny` | P6 | P6b: Drop ALL Capabilities (CIS 5.2.7) [MUST] |
| 12 | 133 | `deny` | P6 | — |

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

## F.2 G-PRE-05 — R004 (EU AI Act Art. 14)

**Policy-Datei:** `policies/pre-deployment/policy_governance_approval.rego`  
**Test-Datei:** `policies/pre-deployment/policy_governance_approval_test.rego`  
**Package:** `genaiops.pre_deployment.governance_approval`  
**Automatisierung:** HYBRID  
**Coverage:** 17 Regeln, 19 Tests (HYBRID: 18 | PASS: 1)

### F.2.05.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|------------|--------|---------------------------:|
| C-01 | MUST | Art. 14 | `policy_governance_approval` | 0 |

*Regeln mit Check-ID im Meldungstext: 0 / 17 — ohne: 17 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.05.1 Regel-Inventar (17 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 27 | `deny` | — | D3-Override: Art. 14 = First-Degree Oversight → max HYBRID |
| 2 | 32 | `deny` | — | — |
| 3 | 38 | `deny` | — | — |
| 4 | 44 | `deny` | — | — |
| 5 | 51 | `deny` | — | — |
| 6 | 56 | `deny` | — | — |
| 7 | 62 | `deny` | — | — |
| 8 | 67 | `deny` | — | — |
| 9 | 73 | `deny` | — | — |
| 10 | 79 | `deny` | — | — |
| 11 | 86 | `deny` | — | — |
| 12 | 91 | `deny` | — | — |
| 13 | 101 | `deny` | — | The actual approval decision is made by a human — Conftest only checks evidence. |
| 14 | 106 | `deny` | — | The actual approval decision is made by a human — Conftest only checks evidence. |
| 15 | 112 | `deny` | — | — |
| 16 | 117 | `deny` | — | — |
| 17 | 123 | `deny` | — | — |

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

Zur Verifikation der obigen Zahlen (16 Policies / 143 Regeln / 141 Tests):

```bash
# OPA ≥ 1.15.2 vorausgesetzt
./tests/run_all_rego_tests.sh --quiet   # Erwartet: 'PASS: 141/141'
python3 tools/extract_rule_test_mapping.py
```

Die JSON-Ground-Truth-Variante liegt unter `docs/appendix/rule_test_mapping.json` und wird über `tools/extract_rule_test_mapping.py` aus den Quell-Regos regeneriert.
