# ================================================================
# G-DEP-03: Transparency Docs Present — UNIT TESTS
# ================================================================
# Tests:       policy_transparency_docs_present.rego (9 deny-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + multi-rule-FAIL (fixture) + 9× rule-isolation-FAIL
# Coverage:    11 tests for 9 rules — 5/5 check-groups covered,
#              rule-level 9/9 strict-isolation + 3/9 via multi-rule fixture
#              (redundant-by-design for co-occurrence evidence).
#              Pattern-class coverage: 5/5 (top-level-missing, field-missing,
#              string-empty, array-empty, nested-field-missing).
#
# Fixtures:    data.fixtures.healthcare.app_documentation_transparency_pass
#              (dedicated PASS — full 5-field transparency block)
#              data.fixtures.healthcare.app_documentation_transparency_fail
#              (dedicated FAIL — multi-rule: R3+R6+R8)
#
# Methodology: Strict rule-isolation per DSR-Rigor — each rule fires in
#              exactly one dedicated test where only that rule's condition
#              is violated. Multi-rule fixture tests realistic co-occurrence.
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.deployment.transparency_docs_present_test

import rego.v1

import data.fixtures.healthcare.app_documentation_transparency_pass as scenario_pass
import data.fixtures.healthcare.app_documentation_transparency_fail as scenario_fail
import data.genaiops.deployment.transparency_docs_present

# ================================================================
# PASS Tests (real Use-Case full transparency documentation)
# ================================================================

test_pass_full_transparency_documentation if {
	# Healthcare Ambient AI Scribe has complete transparency block:
	# instructions + capabilities + limitations + ai_content_labeling.
	count(transparency_docs_present.deny) == 0 with input as scenario_pass
}

# ================================================================
# FAIL Tests — Multi-rule co-occurrence via dedicated fail-fixture
# ================================================================

test_fail_realistic_incomplete_transparency_multi_rule if {
	# FAIL fixture triggers exactly 3 rules:
	#   R3 (instructions_for_deployers empty string)
	#   R6 (known_limitations missing)
	#   R8 (ai_content_labeling missing)
	result := transparency_docs_present.deny with input as scenario_fail
	count(result) >= 3
}

# ================================================================
# FAIL Tests — Rule-isolation (R1: top-level-missing)
# ================================================================

test_fail_missing_transparency_section if {
	# R1 (isolation): entire transparency section absent.
	input_override := {}
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R2, R3: instructions_for_deployers)
# ================================================================

test_fail_missing_instructions_for_deployers_field if {
	# R2 (isolation): instructions_for_deployers field absent,
	# all other transparency fields valid.
	input_override := {"transparency": {
		"model_capabilities": scenario_pass.transparency.model_capabilities,
		"known_limitations": scenario_pass.transparency.known_limitations,
		"ai_content_labeling": scenario_pass.transparency.ai_content_labeling,
	}}
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}

test_fail_empty_instructions_for_deployers_string if {
	# R3 (isolation): instructions_for_deployers present but empty string.
	input_override := object.union(scenario_pass, {"transparency": object.union(
		scenario_pass.transparency,
		{"instructions_for_deployers": ""},
	)})
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R4, R5: model_capabilities)
# ================================================================

test_fail_missing_model_capabilities_field if {
	# R4 (isolation): model_capabilities field absent,
	# all other transparency fields valid.
	input_override := {"transparency": {
		"instructions_for_deployers": scenario_pass.transparency.instructions_for_deployers,
		"known_limitations": scenario_pass.transparency.known_limitations,
		"ai_content_labeling": scenario_pass.transparency.ai_content_labeling,
	}}
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}

test_fail_empty_model_capabilities_string if {
	# R5 (isolation): model_capabilities present but empty string.
	input_override := object.union(scenario_pass, {"transparency": object.union(
		scenario_pass.transparency,
		{"model_capabilities": ""},
	)})
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R6, R7: known_limitations)
# ================================================================

test_fail_missing_known_limitations_field if {
	# R6 (isolation): known_limitations field absent,
	# all other transparency fields valid.
	input_override := {"transparency": {
		"instructions_for_deployers": scenario_pass.transparency.instructions_for_deployers,
		"model_capabilities": scenario_pass.transparency.model_capabilities,
		"ai_content_labeling": scenario_pass.transparency.ai_content_labeling,
	}}
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}

test_fail_empty_known_limitations_array if {
	# R7 (isolation): known_limitations present but empty array.
	input_override := object.union(scenario_pass, {"transparency": object.union(
		scenario_pass.transparency,
		{"known_limitations": []},
	)})
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (R8, R9: ai_content_labeling)
# ================================================================

test_fail_missing_ai_content_labeling_object if {
	# R8 (isolation): ai_content_labeling object entirely absent,
	# all other transparency fields valid. Art. 50 GenAI violation.
	input_override := {"transparency": {
		"instructions_for_deployers": scenario_pass.transparency.instructions_for_deployers,
		"model_capabilities": scenario_pass.transparency.model_capabilities,
		"known_limitations": scenario_pass.transparency.known_limitations,
	}}
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}

test_fail_missing_ai_content_labeling_enabled_subfield if {
	# R9 (isolation): ai_content_labeling exists but .enabled subfield
	# missing — must declare whether labeling is active. New pattern-class.
	# Note: object.union deep-merges — we rebuild transparency explicitly
	# to ensure the new ai_content_labeling object has NO "enabled" key.
	input_override := {"transparency": {
		"instructions_for_deployers": scenario_pass.transparency.instructions_for_deployers,
		"model_capabilities": scenario_pass.transparency.model_capabilities,
		"known_limitations": scenario_pass.transparency.known_limitations,
		"ai_content_labeling": {
			"method": "Metadata tag in FHIR DocumentReference.category",
			"label_text": "AI-generated summary — review required",
		},
	}}
	result := transparency_docs_present.deny with input as input_override
	count(result) > 0
}
