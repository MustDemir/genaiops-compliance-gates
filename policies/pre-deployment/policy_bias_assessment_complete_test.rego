# ================================================================
# G-DEP-05: Bias Assessment Complete — UNIT TESTS
# ================================================================
# Tests:       policy_bias_assessment_complete.rego (10 warn-rules; R013 = SHOULD)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + realistic-single-rule-FAIL (fixture, count == 1)
#              + 10× rule-isolation-FAIL
# Coverage:    12 tests for 10 rules — 5/5 check-groups covered,
#              rule-level 10/10 strict-isolation + 1/10 via realistic
#              single-rule fixture (redundant-by-design for R9 realistic
#              co-occurrence evidence, bias_detected=true scenario).
#              Pattern-class coverage: 5/5 (top-level-missing,
#              field-missing, array-empty, nested-field-missing,
#              conditional-rule [NEW — R9/R10 depend on bias_detected]).
#
# Fixtures:    data.fixtures.healthcare.model_documentation_bias_pass
#              (dedicated PASS — full 5-section bias block,
#              bias_detected=false, mitigation_measures=[] allowed because
#              R10 requires bias_detected=true to fire).
#              data.fixtures.healthcare.model_documentation_bias_fail
#              (dedicated FAIL — realistic single-rule scenario:
#              bias detected in age_group, no mitigation documented,
#              all other documentation complete → only R9 fires).
#
# Strengthened assertion for realistic FAIL test:
#   count(result) == 1 (exact, not >=1) — DSR-Rigor upgrade over
#   G-DEP-01/G-DEP-03 pattern. If policy adds a new rule that would
#   fire on this realistic fixture, the test will fail intentionally,
#   forcing deliberate test-maintenance instead of silent drift.
#
# Methodology: Strict rule-isolation per DSR-Rigor — each of the 10
#              rules fires in exactly one dedicated test where only
#              that rule's condition is violated. Conditional rules
#              (R9, R10) isolation requires bias_detected=true input.
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.pre_deployment.bias_assessment_complete_test

import rego.v1

import data.fixtures.healthcare.model_documentation_bias_pass as scenario_pass
import data.fixtures.healthcare.model_documentation_bias_fail as scenario_fail
import data.genaiops.pre_deployment.bias_assessment_complete

# ================================================================
# PASS Tests (real Use-Case full bias documentation)
# ================================================================

test_pass_full_bias_assessment if {
	# Healthcare Ambient AI Scribe has complete bias assessment:
	# methods + protected_attributes + fairness_results (metrics,
	# bias_detected=false) + mitigation_measures=[] (permitted
	# because R10 only triggers when bias_detected=true).
	count(bias_assessment_complete.warn) == 0 with input as scenario_pass
}

# ================================================================
# FAIL Tests — Realistic single-rule via dedicated fail-fixture
# ================================================================

test_fail_realistic_missing_mitigation_single_rule if {
	# FAIL fixture: bias_detected=true in age_group but
	# mitigation_measures section entirely absent.
	# Expected: ONLY R9 fires (all other documentation complete).
	# Strengthened assertion count==1 verifies exclusivity —
	# any future rule addition that trips this fixture breaks
	# the test intentionally.
	result := bias_assessment_complete.warn with input as scenario_fail
	count(result) == 1
}

# ================================================================
# FAIL Tests — Rule-isolation (R1: top-level-missing)
# ================================================================

test_fail_missing_bias_detection_section if {
	# R1 (isolation): entire bias_detection section absent.
	# Art. 10(2)(f) + Art. 9 Abs. 2 lit. a violation.
	input_override := {}
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R2, R3: methods)
# ================================================================

test_fail_missing_methods_field if {
	# R2 (isolation): bias_detection.methods field absent,
	# all other bias_detection fields valid.
	input_override := {"bias_detection": {
		"protected_attributes": scenario_pass.bias_detection.protected_attributes,
		"fairness_results": scenario_pass.bias_detection.fairness_results,
	}}
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

test_fail_empty_methods_array if {
	# R3 (isolation): methods present but empty array.
	input_override := object.union(scenario_pass, {"bias_detection": object.union(
		scenario_pass.bias_detection,
		{"methods": []},
	)})
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R4: fairness_results missing)
# ================================================================

test_fail_missing_fairness_results_field if {
	# R4 (isolation): fairness_results field absent,
	# all other bias_detection fields valid.
	input_override := {"bias_detection": {
		"methods": scenario_pass.bias_detection.methods,
		"protected_attributes": scenario_pass.bias_detection.protected_attributes,
	}}
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R5, R6: metrics [nested])
# ================================================================
# Note: object.union deep-merges — we rebuild bias_detection
# explicitly to ensure nested metrics manipulations don't leak
# the pass-fixture's metrics through the merge.

test_fail_missing_metrics_field if {
	# R5 (isolation): fairness_results exists but .metrics
	# subfield missing. Pattern-class: nested-field-missing.
	input_override := {"bias_detection": {
		"methods": scenario_pass.bias_detection.methods,
		"protected_attributes": scenario_pass.bias_detection.protected_attributes,
		"fairness_results": {
			"bias_detected": false,
			"evaluation_date": "2026-03-15",
		},
	}}
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

test_fail_empty_metrics_array if {
	# R6 (isolation): fairness_results.metrics present but
	# empty array. Quantitative evidence absent.
	input_override := {"bias_detection": {
		"methods": scenario_pass.bias_detection.methods,
		"protected_attributes": scenario_pass.bias_detection.protected_attributes,
		"fairness_results": {
			"bias_detected": false,
			"metrics": [],
		},
	}}
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R7, R8: protected_attributes)
# ================================================================

test_fail_missing_protected_attributes_field if {
	# R7 (isolation): protected_attributes field absent —
	# Art. 10(2)(f) requires explicit identification.
	input_override := {"bias_detection": {
		"methods": scenario_pass.bias_detection.methods,
		"fairness_results": scenario_pass.bias_detection.fairness_results,
	}}
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

test_fail_empty_protected_attributes_array if {
	# R8 (isolation): protected_attributes present but empty array.
	input_override := object.union(scenario_pass, {"bias_detection": object.union(
		scenario_pass.bias_detection,
		{"protected_attributes": []},
	)})
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R9, R10: conditional-rule class)
# ================================================================
# R9/R10 only fire when bias_detected=true. Isolation requires
# explicit rebuild of fairness_results with bias_detected=true
# (overriding the PASS fixture's bias_detected=false baseline).
# Pattern-class: conditional-rule (NEW in catalog, not seen in
# G-DEP-01, G-DEP-03, G-OPS-02/03/05 or G-PRE-01).

test_fail_bias_detected_without_mitigation if {
	# R9 (isolation): bias_detected=true and mitigation_measures
	# field entirely absent. Art. 9 risk-mitigation violation.
	input_override := {"bias_detection": {
		"methods": scenario_pass.bias_detection.methods,
		"protected_attributes": scenario_pass.bias_detection.protected_attributes,
		"fairness_results": {
			"bias_detected": true,
			"metrics": scenario_pass.bias_detection.fairness_results.metrics,
		},
	}}
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}

test_fail_bias_detected_with_empty_mitigation if {
	# R10 (isolation): bias_detected=true and mitigation_measures
	# present but empty array — mitigation declared but unspecified.
	input_override := {"bias_detection": {
		"methods": scenario_pass.bias_detection.methods,
		"protected_attributes": scenario_pass.bias_detection.protected_attributes,
		"fairness_results": {
			"bias_detected": true,
			"metrics": scenario_pass.bias_detection.fairness_results.metrics,
		},
		"mitigation_measures": [],
	}}
	result := bias_assessment_complete.warn with input as input_override
	count(result) > 0
}
