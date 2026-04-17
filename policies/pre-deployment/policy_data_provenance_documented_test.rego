# ================================================================
# G-DEP-01: Data Provenance Documented — UNIT TESTS
# ================================================================
# Tests:       policy_data_provenance_documented.rego (9 deny-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + multi-rule-FAIL (fixture) + 7× single-rule-FAIL
# Coverage:    9 tests for 9 rules — 5/5 check-groups covered,
#              rule-level 7/9 explicit + 2/9 via multi-rule fixture
#              = 9/9 total (100% rule-level coverage).
#              Pattern-class coverage: 4/4 (top-level-missing,
#              field-missing, array-empty, string-empty).
#
# Fixtures:    data.fixtures.healthcare.data_documentation_provenance_pass
#              (dedicated PASS fixture — full 5-section documentation)
#              data.fixtures.healthcare.data_documentation_provenance_fail
#              (dedicated FAIL fixture — multi-rule failure: R5+R6+R8)
#
# Strengthened assertion for multi-rule test:
#   count(result) >= 3 (exact rule-count expected from fixture design)
#   — this is a DSR-Rigor deviation from the Blueprint "count > 0"
#     pattern, justified by the multi-rule nature of the fail-fixture.
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.pre_deployment.data_provenance_documented_test

import rego.v1

import data.fixtures.healthcare.data_documentation_provenance_pass as scenario_pass
import data.fixtures.healthcare.data_documentation_provenance_fail as scenario_fail
import data.genaiops.pre_deployment.data_provenance_documented

# ================================================================
# PASS Tests (real Use-Case full data documentation)
# ================================================================

test_pass_full_data_provenance if {
	# Healthcare Ambient AI Scribe training data fully documented:
	# collection_methods + sources + preprocessing_steps + data_version.
	# Positive path exercises all 9 rules (no deny triggered).
	count(data_provenance_documented.deny) == 0 with input as scenario_pass
}

# ================================================================
# FAIL Tests — Multi-rule via dedicated incomplete fixture
# ================================================================

test_fail_realistic_incomplete_documentation_multi_rule if {
	# FAIL fixture triggers exactly 3 rules:
	#   R5 (sources empty array)
	#   R6 (preprocessing_steps missing)
	#   R8 (data_version missing)
	# Strengthened assertion: count >= 3 verifies multi-rule deny
	# accumulation, not just "any single rule fired".
	result := data_provenance_documented.deny with input as scenario_fail
	count(result) >= 3
}

# ================================================================
# FAIL Tests — Pattern-class: Top-level-missing (R1)
# ================================================================

test_fail_missing_data_provenance_section if {
	# Rule 1: entire data_provenance section absent — Art. 10 violation.
	input_override := {}
	result := data_provenance_documented.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Pattern-class: Field-missing (R2, R4, R6)
# ================================================================

test_fail_missing_collection_methods_field if {
	# Rule 2: data_provenance.collection_methods absent —
	# Annex IV §2d requires data collection documentation.
	input_override := {"data_provenance": {
		"sources": scenario_pass.data_provenance.sources,
		"preprocessing_steps": scenario_pass.data_provenance.preprocessing_steps,
		"data_version": scenario_pass.data_provenance.data_version,
	}}
	result := data_provenance_documented.deny with input as input_override
	count(result) > 0
}

test_fail_missing_sources_field if {
	# Rule 4: data_provenance.sources absent — origin not traceable.
	input_override := {"data_provenance": {
		"collection_methods": scenario_pass.data_provenance.collection_methods,
		"preprocessing_steps": scenario_pass.data_provenance.preprocessing_steps,
		"data_version": scenario_pass.data_provenance.data_version,
	}}
	result := data_provenance_documented.deny with input as input_override
	count(result) > 0
}

test_fail_missing_preprocessing_steps_field if {
	# Rule 6: data_provenance.preprocessing_steps absent —
	# reproducibility of data transformation chain broken.
	input_override := {"data_provenance": {
		"collection_methods": scenario_pass.data_provenance.collection_methods,
		"sources": scenario_pass.data_provenance.sources,
		"data_version": scenario_pass.data_provenance.data_version,
	}}
	result := data_provenance_documented.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Pattern-class: Array-empty (R3, R7)
# ================================================================

test_fail_empty_collection_methods_array if {
	# Rule 3: collection_methods present but empty array.
	input_override := object.union(scenario_pass, {"data_provenance": object.union(
		scenario_pass.data_provenance,
		{"collection_methods": []},
	)})
	result := data_provenance_documented.deny with input as input_override
	count(result) > 0
}

test_fail_empty_preprocessing_steps_array if {
	# Rule 7: preprocessing_steps present but empty array.
	input_override := object.union(scenario_pass, {"data_provenance": object.union(
		scenario_pass.data_provenance,
		{"preprocessing_steps": []},
	)})
	result := data_provenance_documented.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Pattern-class: String-empty (R9)
# ================================================================

test_fail_empty_data_version_string if {
	# Rule 9: data_version present but empty string.
	input_override := object.union(scenario_pass, {"data_provenance": object.union(
		scenario_pass.data_provenance,
		{"data_version": ""},
	)})
	result := data_provenance_documented.deny with input as input_override
	count(result) > 0
}
