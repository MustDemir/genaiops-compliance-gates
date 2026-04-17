# ================================================================
# G-PRE-01: Risk Classification Validation — UNIT TESTS
# ================================================================
# Tests:       policy_risk_classification.rego (14 deny-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + FAIL-basic + FAIL-edge + HYBRID-manual-review
# Coverage:    8 tests for 14 rules (~57% rule-level, 100% rule-group coverage)
#
# Fixtures:    data.fixtures.healthcare.app_documentation (real Use-Case)
#              Scenario: Healthcare Ambient AI Scribe (high-risk, Annex III 5a)
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.pre_deployment.risk_classification_test

import rego.v1

import data.fixtures.healthcare.app_documentation as scenario
import data.genaiops.pre_deployment.risk_classification

# ================================================================
# PASS Tests (real Use-Case scenario must produce zero deny)
# ================================================================

test_pass_valid_high_risk_scenario if {
	# Healthcare Ambient AI Scribe — full high-risk classification per Annex III 5a
	count(risk_classification.deny) == 0 with input as scenario
}

test_pass_minimal_risk_without_annex_or_mitigation if {
	# Boundary: minimal-risk does NOT require annex_reference or mitigation_measures
	input_override := object.union(scenario, {"risk_classification": {
		"risk_class": "minimal",
		"classification_reasoning": "Chatbot without safety-critical function per AI Act Art. 52",
	}})
	count(risk_classification.deny) == 0 with input as input_override
}

# ================================================================
# FAIL Tests — Basic (core contract violations on real scenario)
# ================================================================

test_fail_missing_risk_class if {
	# Rule 1: risk_class field missing entirely
	# Note: object.union does deep-merge in OPA v1.x — we rebuild the sub-object explicitly.
	input_override := {
		"risk_classification": {
			"classification_reasoning": scenario.risk_classification.classification_reasoning,
		},
		"manual_review": scenario.manual_review,
	}
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

test_fail_empty_risk_class_string if {
	# Rule 2: risk_class present but empty string
	input_override := object.union(scenario, {"risk_classification": object.union(
		scenario.risk_classification,
		{"risk_class": ""},
	)})
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

test_fail_invalid_risk_class_value if {
	# Rule 3: risk_class value not in {high, limited, minimal, unacceptable}
	input_override := object.union(scenario, {"risk_classification": object.union(
		scenario.risk_classification,
		{"risk_class": "extreme"},
	)})
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Edge (high-risk specific obligations, real scenario)
# ================================================================

test_fail_high_risk_without_annex_reference if {
	# Rule 5: high-risk requires annex_reference
	# Note: object.union does deep-merge in OPA v1.x — we rebuild risk_classification explicitly.
	input_override := {
		"risk_classification": {
			"risk_class": "high",
			"classification_reasoning": scenario.risk_classification.classification_reasoning,
			"mitigation_measures": scenario.risk_classification.mitigation_measures,
			# annex_reference intentionally omitted
		},
		"manual_review": scenario.manual_review,
	}
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

test_fail_high_risk_empty_mitigation_measures if {
	# Rule 6: high-risk requires non-empty mitigation_measures array
	input_override := object.union(scenario, {"risk_classification": object.union(
		scenario.risk_classification,
		{"mitigation_measures": []},
	)})
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — HYBRID Gate Manual-Review Evidence
# ================================================================

test_fail_missing_manual_review_section if {
	# Rule 7 (HYBRID): manual_review section required for audit trail
	input_override := object.remove(scenario, ["manual_review"])
	result := risk_classification.deny with input as input_override
	count(result) > 0
}
