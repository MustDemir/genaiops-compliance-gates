# ================================================================
# G-PRE-03: Risk Management Completeness — UNIT TESTS
# ================================================================
package genaiops.pre_deployment.risk_management_complete_test

import rego.v1

import data.fixtures.healthcare.app_documentation as scenario
import data.genaiops.pre_deployment.risk_management_complete

test_pass_valid_risk_management_scenario if {
	count(risk_management_complete.deny) == 0 with input as scenario
}

test_fail_missing_risk_management_section if {
	input_override := object.remove(scenario, ["risk_management"])
	count(risk_management_complete.deny) > 0 with input as input_override
}

test_fail_register_not_versioned if {
	input_override := object.union(scenario, {"risk_management": {"risk_register_versioned": false}})
	count(risk_management_complete.deny) > 0 with input as input_override
}

test_fail_empty_identified_risks if {
	input_override := object.union(scenario, {"risk_management": {"identified_risks": []}})
	count(risk_management_complete.deny) > 0 with input as input_override
}

test_fail_risk_without_mitigation if {
	input_override := object.union(scenario, {"risk_management": {"identified_risks": [{"risk": "unmitigated risk"}]}})
	count(risk_management_complete.deny) > 0 with input as input_override
}

test_fail_data_risk_not_assessed if {
	input_override := object.union(scenario, {"risk_management": {"data_risk_assessment": {"assessed": false}}})
	count(risk_management_complete.deny) > 0 with input as input_override
}

test_fail_missing_data_classification if {
	dra := object.remove(scenario.risk_management.data_risk_assessment, ["data_classification"])
	rm := object.union(object.remove(scenario.risk_management, ["data_risk_assessment"]), {"data_risk_assessment": dra})
	input_override := object.union(object.remove(scenario, ["risk_management"]), {"risk_management": rm})
	count(risk_management_complete.deny) > 0 with input as input_override
}
