# ================================================================
# G-OPS-01: Human Oversight (Operational) — UNIT TESTS
# ================================================================
package genaiops.operations.human_oversight_operational_test

import rego.v1

import data.fixtures.healthcare.app_documentation as scenario
import data.genaiops.operations.human_oversight_operational

test_pass_valid_oversight_scenario if {
	count(human_oversight_operational.deny) == 0 with input as scenario
}

test_fail_missing_oversight_section if {
	input_override := object.remove(scenario, ["human_oversight"])
	count(human_oversight_operational.deny) > 0 with input as input_override
}

test_fail_missing_oversight_roles if {
	without := object.remove(scenario.human_oversight, ["oversight_roles"])
	input_override := object.union(object.remove(scenario, ["human_oversight"]), {"human_oversight": without})
	count(human_oversight_operational.deny) > 0 with input as input_override
}

test_fail_empty_oversight_roles if {
	input_override := object.union(scenario, {"human_oversight": {"oversight_roles": []}})
	count(human_oversight_operational.deny) > 0 with input as input_override
}

test_fail_missing_escalation_procedure if {
	without := object.remove(scenario.human_oversight, ["escalation_procedure"])
	input_override := object.union(object.remove(scenario, ["human_oversight"]), {"human_oversight": without})
	count(human_oversight_operational.deny) > 0 with input as input_override
}

test_fail_output_override_false if {
	input_override := object.union(scenario, {"human_oversight": {"intervention_capability": {"output_override": false}}})
	count(human_oversight_operational.deny) > 0 with input as input_override
}

test_fail_real_time_monitoring_false if {
	input_override := object.union(scenario, {"human_oversight": {"intervention_capability": {"real_time_monitoring": false}}})
	count(human_oversight_operational.deny) > 0 with input as input_override
}
