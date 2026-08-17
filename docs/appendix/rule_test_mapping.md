# Rego Unit Tests — Rule-to-Test Mapping

**Erzeugungsdatum:** 2026-08-14  
**Baseline:** 141/141 PASS  
**Quelle:** `tools/extract_rule_test_mapping.py` (auto-generiert aus `policies/**/*.rego` + `policies/**/*_test.rego`)  

Dieses Dokument belegt die Rule-Level-Isolation der PoC-Policy-Engine: Jede der **166 Rego-Regeln** wird durch mindestens eine Unit-Test-Assertion verifiziert. Insgesamt **173 Tests** decken die Muster PASS (positive path), FAIL-basic (missing field), FAIL-edge (invalid/empty values) und HYBRID (D3-Override First-Degree Oversight) ab. Alle Tests werden zeitgleich durch `tests/run_all_rego_tests.sh` (`opa test policies/ tests/fixtures/`) ausgeführt; die Pipeline-Integration (`pipeline/.github/workflows/gate-pipeline.yml`, Layer 1) bricht bei einem Fehlschlag vor jeder Conftest-Gate-Evaluation ab (Shift-Left).

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
| G-OPS-06 | R001 | EU AI Act Art. 25 | HYBRID | 4 | 9 | 13 | 4 | 6 | 0 | 0 |
| G-PRE-01 | R001 | EU AI Act Art. 9 | HYBRID | 8 | 28 | 27 | 8 | 11 | 4 | 4 |
| G-PRE-02 | R012 | EU AI Act Art. 27 | HYBRID | 1 | 6 | 6 | 1 | 4 | 1 | 0 |
| G-PRE-03 | R001 | EU AI Act Art. 9 | HYBRID | 2 | 7 | 7 | 1 | 5 | 1 | 0 |
| G-PRE-04 | R003 | EU AI Act Art. 15 | AUTO | 6 | 12 | 14 | 1 | 12 | 1 | 0 |
| G-PRE-05 | R004 | EU AI Act Art. 14 | HYBRID | 1 | 17 | 19 | 1 | 0 | 0 | 18 |
| **Gesamt** | — | — | — | **43** | **166** | **173** | 29 | 93 | 22 | 26 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 10, Art. 11 | `policy_data_provenance_documented` | 0 |
| C-02 | MUST | ⬜ design_only | Art. 10, Art. 11 | `policy_training_documented` | 0 |
| C-03 | MUST | ⬜ design_only | Art. 10, Art. 11 | `policy_data_lineage_complete` | 0 |
| C-04 | MUST | ⬜ design_only | Art. 10, Art. 11 | `policy_dataset_description_complete` | 0 |
| C-05 | MUST | ⬜ design_only | Art. 10, Art. 11 | `policy_annotation_quality_verified` | 0 |
| C-06 | MUST | ⬜ design_only | Art. 10, Art. 11 | `policy_data_license_valid` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 15 | `policy_safety_metrics` | 0 |
| C-02 | SHOULD | ✅ implemented | Art. 15 | `policy_safety_metrics` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 13, Art. 26 Abs. 7, Art. 50 | `policy_transparency_docs_present` | 0 |
| C-02 | MUST | ⬜ design_only | Art. 13, Art. 26 Abs. 7, Art. 50 | `policy_explainability_documented` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 26 Abs. 1 | `policy_conformity_verified` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | SHOULD | ✅ implemented | Art. 9 Abs. 2 lit. a, Art. 10 Abs. 2 lit. f, Art. 15 | `policy_bias_assessment_complete` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 12, Art. 26 Abs. 3 | `policy_logging_configured` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 14, Art. 26 Abs. 2 | `policy_human_oversight_operational` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 26 Abs. 5, Art. 73 | `policy_incident_process_exists` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 72, Art. 9 Abs. 2 | `policy_monitoring_configured` | 0 |
| C-02 | MUST | ✅ implemented | Art. 72, Art. 9 Abs. 2 | `policy_monitoring_configured` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 15 | `policy_data_security_controls` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 12, Art. 15 | `policy_evidence_completeness` | 0 |
| C-02 | MUST | ✅ implemented | Art. 12, Art. 15 | `policy_evidence_completeness` | 0 |
| C-03 | MUST | ✅ implemented | Art. 12, Art. 15 | `policy_evidence_completeness` | 0 |

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

## F.2 G-OPS-06 — R001 (EU AI Act Art. 25)

**Policy-Datei:** `policies/operations/policy_role_change_monitoring.rego`  
**Test-Datei:** `policies/operations/policy_role_change_monitoring_test.rego`  
**Package:** `genaiops.operations.role_change_monitoring`  
**Automatisierung:** HYBRID  
**Coverage:** 9 Regeln, 13 Tests (FAIL-basic: 6 | OTHER: 3 | PASS: 4)

### F.2.06.0 Check-Inventar (4 Checks, schema_version 2)

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-25a | MUST | ✅ implemented | Art. 25 Abs. 1 lit. a | `policy_role_change_monitoring` | 1 |
| C-25b | SHOULD | ✅ implemented | Art. 25 Abs. 1 lit. b, Art. 3 Nr. 23, Art. 97 | `policy_role_change_monitoring` | 1 |
| C-25c | MUST | ✅ implemented | Art. 25 Abs. 1 lit. c, Art. 6 | `policy_role_change_monitoring` | 3 |
| C-25d | MUST | ✅ implemented | Art. 25 Abs. 2, Art. 25 Abs. 4 UAbs. 1 | `policy_role_change_monitoring` | 4 |

*Regeln mit Check-ID im Meldungstext: 9 / 9 — ohne: 0 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.06.1 Regel-Inventar (9 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 111 | `deny` | C-25a | in Verkehr gebrachten Hochrisiko-System. Kein Schwellenwertproblem. |
| 2 | 127 | `warn` | C-25b | Rechtsakten nach Art. 97, die noch ausstehen. Daher advisory. |
| 3 | 156 | `deny` | C-25c | — |
| 4 | 163 | `deny` | C-25c | vor UND nach der Aenderung mitliefern, sonst ist C-25c nicht auswertbar. |
| 5 | 169 | `deny` | C-25c | vor UND nach der Aenderung mitliefern, sonst ist C-25c nicht auswertbar. |
| 6 | 197 | `deny` | C-25d | — |
| 7 | 204 | `deny` | C-25d | — |
| 8 | 211 | `deny` | C-25d | — |
| 9 | 219 | `warn` | C-25d | Der Carve-out wird behauptet, aber nicht belegt. |

### F.2.06.2 Test-Inventar (13 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 27 | `test_pass_benign_change_no_trigger` | PASS |
| 2 | 36 | `test_fail_c25a_rebranding_triggers_deny` | FAIL-basic |
| 3 | 41 | `test_pass_c25a_with_handover_no_c25d` | PASS |
| 4 | 51 | `test_warn_c25b_substantial_modification_is_advisory` | OTHER |
| 5 | 56 | `test_pass_c25b_does_not_block` | PASS |
| 6 | 66 | `test_fail_c25c_purpose_change_to_high_risk` | FAIL-basic |
| 7 | 71 | `test_c25c_uses_spec02_classification_not_a_boolean` | OTHER |
| 8 | 82 | `test_fail_c25c_missing_before_state` | FAIL-basic |
| 9 | 89 | `test_fail_c25c_missing_after_state` | FAIL-basic |
| 10 | 100 | `test_fail_c25d_trigger_without_handover_artifacts` | FAIL-basic |
| 11 | 106 | `test_fail_c25d_names_all_three_artifacts` | FAIL-basic |
| 12 | 119 | `test_pass_c25d_carve_out_lifts_handover_duty` | PASS |
| 13 | 134 | `test_warn_c25d_carve_out_claimed_without_evidence` | OTHER |

## F.2 G-PRE-01 — R001 (EU AI Act Art. 9)

**Policy-Datei:** `policies/pre-deployment/policy_risk_classification.rego`  
**Test-Datei:** `policies/pre-deployment/policy_risk_classification_test.rego`  
**Package:** `genaiops.pre_deployment.risk_classification`  
**Automatisierung:** HYBRID  
**Coverage:** 28 Regeln, 27 Tests (FAIL-basic: 11 | FAIL-edge: 4 | HYBRID: 4 | PASS: 8)

### F.2.01.0 Check-Inventar (8 Checks, schema_version 2)

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 9 | `policy_risk_classification` | 0 |
| C-A1 | MUST | ✅ implemented | Art. 3 Nr. 14, Anhang III Nr. 2 | `policy_risk_classification` | 1 |
| C-A2 | MUST | ✅ implemented | Anhang III Nr. 2 | `policy_risk_classification` | 2 |
| C-A3 | MUST | ✅ implemented | Art. 6 Abs. 1a, Art. 6 Abs. 1b | `policy_risk_classification` | 1 |
| C-A4 | MUST | ✅ implemented | Art. 6 Abs. 1a | `policy_risk_classification` | 3 |
| C-A5 | MUST | ✅ implemented | Art. 3 Nr. 14 | `policy_risk_classification` | 4 |
| C-A6 | MUST | ✅ implemented | Art. 6 Abs. 1b | `policy_risk_classification` | 1 |
| C-A7 | SHOULD | ✅ implemented | Art. 26 Abs. 2 | `policy_risk_classification` | 2 |

*Regeln mit Check-ID im Meldungstext: 14 / 28 — ohne: 14 (Meldungen aus der Zeit vor der `<GATE-ID>/<CHECK-ID>`-Konvention nach SPEC-01 Abschnitt 6).*

### F.2.01.1 Regel-Inventar (28 Regeln)

| Nr. | Zeile | Art | Check-ID | Hinweis-Kommentar (nächstliegend) |
|----:|------:|-----|----------|-----------------------------------|
| 1 | 108 | `deny` | — | — |
| 2 | 114 | `deny` | — | — |
| 3 | 120 | `deny` | — | — |
| 4 | 128 | `deny` | — | — |
| 5 | 133 | `deny` | — | — |
| 6 | 139 | `deny` | — | — |
| 7 | 145 | `deny` | — | — |
| 8 | 152 | `deny` | — | — |
| 9 | 158 | `deny` | — | — |
| 10 | 168 | `deny` | — | These rules check that the MANUAL review step has been documented. |
| 11 | 173 | `deny` | — | These rules check that the MANUAL review step has been documented. |
| 12 | 179 | `deny` | — | — |
| 13 | 184 | `deny` | — | — |
| 14 | 190 | `deny` | — | — |
| 15 | 274 | `deny` | C-A1 | C-A1 (MUST) — art6_assessment fehlt vollstaendig |
| 16 | 283 | `deny` | C-A2 | C-A2 (MUST) — deployment_context fehlt oder unzulaessig |
| 17 | 289 | `deny` | C-A2 | C-A2 (MUST) — deployment_context fehlt oder unzulaessig |
| 18 | 303 | `deny` | C-A3 | Ausfallfolge geprueft zu haben. Wichtigster Check dieser SPEC. |
| 19 | 314 | `deny` | C-A4 | leer oder mit unzulaessigen Werten |
| 20 | 321 | `deny` | C-A4 | — |
| 21 | 328 | `deny` | C-A4 | — |
| 22 | 339 | `deny` | C-A5 | C-A5 (MUST) — Arm A oder Arm B bejaht, aber justification fehlt |
| 23 | 346 | `deny` | C-A5 | — |
| 24 | 353 | `deny` | C-A5 | — |
| 25 | 360 | `deny` | C-A5 | — |
| 26 | 378 | `deny` | C-A6 | art6_assessment.self_declared_classification eingefuehrt. |
| 27 | 403 | `warn` | C-A7 | eine Folge-Iteration, sobald die Reihenfolge geklaert ist. |
| 28 | 410 | `warn` | C-A7 | — |

### F.2.01.2 Test-Inventar (27 Tests)

| Nr. | Zeile | Test-Name | Muster |
|----:|------:|-----------|:------:|
| 1 | 28 | `test_pass_valid_high_risk_scenario` | PASS |
| 2 | 33 | `test_pass_minimal_risk_without_annex_or_mitigation` | PASS |
| 3 | 46 | `test_fail_missing_risk_class` | FAIL-basic |
| 4 | 57 | `test_fail_empty_risk_class_string` | FAIL-edge |
| 5 | 67 | `test_fail_invalid_risk_class_value` | FAIL-basic |
| 6 | 81 | `test_fail_high_risk_without_annex_reference` | FAIL-basic |
| 7 | 97 | `test_fail_high_risk_empty_mitigation_measures` | FAIL-edge |
| 8 | 111 | `test_fail_missing_manual_review_section` | HYBRID |
| 9 | 133 | `test_pass_art6_redispatch_no_violations` | PASS |
| 10 | 138 | `test_pass_art6_redispatch_classified_safety_component` | PASS |
| 11 | 147 | `test_hybrid_art6_lastprognose_classified_via_arm_b` | HYBRID |
| 12 | 152 | `test_hybrid_art6_lastprognose_warns_missing_oversight_evidence` | HYBRID |
| 13 | 158 | `test_hybrid_art6_lastprognose_does_not_block` | HYBRID |
| 14 | 168 | `test_pass_art6_predictive_maintenance_no_violations` | PASS |
| 15 | 172 | `test_pass_art6_predictive_maintenance_classified_no_safety_component` | PASS |
| 16 | 180 | `test_pass_art6_chatbot_not_in_scope` | PASS |
| 17 | 184 | `test_pass_art6_chatbot_no_art6_violations` | PASS |
| 18 | 195 | `test_fail_art6_optimization_claim_without_failure_assessment` | FAIL-basic |
| 19 | 204 | `test_fail_art6_contradiction_self_declaration` | FAIL-basic |
| 20 | 209 | `test_fail_art6_contradiction_classified_safety_component` | FAIL-basic |
| 21 | 218 | `test_fail_art6_missing_assessment_section` | FAIL-basic |
| 22 | 228 | `test_fail_art6_missing_deployment_context` | FAIL-basic |
| 23 | 236 | `test_fail_art6_invalid_deployment_context` | FAIL-basic |
| 24 | 249 | `test_fail_art6_exclusion_claimed_with_empty_categories` | FAIL-edge |
| 25 | 258 | `test_fail_art6_exclusion_claimed_with_invalid_category` | FAIL-basic |
| 26 | 274 | `test_fail_art6_arm_a_positive_without_justification` | FAIL-basic |
| 27 | 284 | `test_fail_art6_arm_b_positive_with_empty_justification` | FAIL-edge |

## F.2 G-PRE-02 — R012 (EU AI Act Art. 27)

**Policy-Datei:** `policies/pre-deployment/policy_purpose_declaration.rego`  
**Test-Datei:** `policies/pre-deployment/policy_purpose_declaration_test.rego`  
**Package:** `genaiops.pre_deployment.purpose_declaration`  
**Automatisierung:** HYBRID  
**Coverage:** 6 Regeln, 6 Tests (FAIL-basic: 4 | FAIL-edge: 1 | PASS: 1)

### F.2.02.0 Check-Inventar (1 Checks, schema_version 2)

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 27 | `policy_purpose_declaration` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 9 | `policy_risk_management_complete` | 0 |
| C-02 | MUST | ✅ implemented | Art. 9 | `policy_risk_management_complete` | 0 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| P1 | MUST | ✅ implemented | Art. 15 | `policy_security_baseline` | 3 |
| P2 | MUST | ✅ implemented | Art. 15 | `policy_security_baseline` | 3 |
| P3 | MUST | ✅ implemented | Art. 15 | `policy_security_baseline` | 2 |
| P4 | MUST | ✅ implemented | Art. 15 | `policy_security_baseline` | 1 |
| P5 | SHOULD | ⬜ design_only | Art. 15 | `policy_cybersecurity_controls` | 0 |
| P6 | MUST | ✅ implemented | Art. 15 | `policy_security_baseline` | 3 |

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

| Check-ID | Severity | Status | Legal-Refs | Policy | Regeln mit dieser Check-ID |
|----------|:--------:|:------:|------------|--------|---------------------------:|
| C-01 | MUST | ✅ implemented | Art. 14 | `policy_governance_approval` | 0 |

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

Zur Verifikation der obigen Zahlen (17 Policies / 166 Regeln / 173 Tests):

```bash
# OPA ≥ 1.15.2 vorausgesetzt
./tests/run_all_rego_tests.sh --quiet   # Erwartet: 'PASS: 173/173'
python3 tools/extract_rule_test_mapping.py
```

Die JSON-Ground-Truth-Variante liegt unter `docs/appendix/rule_test_mapping.json` und wird über `tools/extract_rule_test_mapping.py` aus den Quell-Regos regeneriert.
