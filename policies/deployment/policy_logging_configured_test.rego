# ================================================================
# G-DEP-06: Logging Configuration Validation — UNIT TESTS
# ================================================================
# Tests:       policy_logging_configured.rego (8 deny-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS (real scenario) + FAIL per rule-group
#
# Fixtures:    data.fixtures.healthcare.app_documentation (real Use-Case)
#              Scenario: Healthcare Ambient AI Scribe (logging fully configured)
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.deployment.logging_configured_test

import rego.v1

import data.fixtures.healthcare.app_documentation as scenario
import data.genaiops.deployment.logging_configured

# ================================================================
# PASS Test — real scenario must produce zero deny
# ================================================================

test_pass_valid_logging_scenario if {
	# Healthcare Ambient AI Scribe: logging on, 5 event types, 2555 days, accessible
	count(logging_configured.deny) == 0 with input as scenario
}

# ================================================================
# FAIL Tests — one per rule-group (each breaks exactly one thing)
# ================================================================

test_fail_missing_logging_section if {
	# Rule 0: whole logging_configuration block absent
	input_override := object.remove(scenario, ["logging_configuration"])
	result := logging_configured.deny with input as input_override
	count(result) > 0
}

test_fail_logging_disabled if {
	# Rule 1: logging_enabled = false (deep-merge overrides just this field)
	input_override := object.union(scenario, {"logging_configuration": {"logging_enabled": false}})
	result := logging_configured.deny with input as input_override
	count(result) > 0
}

test_fail_missing_event_types if {
	# Rule 2: event_types_captured field removed.
	# Note: object.union deep-merges in OPA v1.x — we drop the whole block
	# first, then re-add it WITHOUT event_types_captured, so it stays gone.
	logging_without := object.remove(scenario.logging_configuration, ["event_types_captured"])
	input_override := object.union(
		object.remove(scenario, ["logging_configuration"]),
		{"logging_configuration": logging_without},
	)
	result := logging_configured.deny with input as input_override
	count(result) > 0
}

test_fail_empty_event_types if {
	# Rule 2: event_types_captured present but empty array
	input_override := object.union(scenario, {"logging_configuration": {"event_types_captured": []}})
	result := logging_configured.deny with input as input_override
	count(result) > 0
}

test_fail_retention_below_minimum if {
	# Rule 3: retention_period_days below 180 (6 months)
	input_override := object.union(scenario, {"logging_configuration": {"retention_period_days": 30}})
	result := logging_configured.deny with input as input_override
	count(result) > 0
}

test_fail_missing_log_accessibility if {
	# Rule 4: log_accessibility field removed (same deep-merge caveat as above)
	logging_without := object.remove(scenario.logging_configuration, ["log_accessibility"])
	input_override := object.union(
		object.remove(scenario, ["logging_configuration"]),
		{"logging_configuration": logging_without},
	)
	result := logging_configured.deny with input as input_override
	count(result) > 0
}
