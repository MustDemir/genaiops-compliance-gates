# ================================================================
# G-PRE-02: Purpose Declaration Completeness — UNIT TESTS
# ================================================================
package genaiops.pre_deployment.purpose_declaration_test

import rego.v1

import data.fixtures.healthcare.app_documentation as scenario
import data.genaiops.pre_deployment.purpose_declaration

test_pass_valid_purpose_scenario if {
	count(purpose_declaration.deny) == 0 with input as scenario
}

test_fail_missing_description if {
	without := object.remove(scenario.application, ["description"])
	input_override := object.union(object.remove(scenario, ["application"]), {"application": without})
	count(purpose_declaration.deny) > 0 with input as input_override
}

test_fail_missing_domain if {
	without := object.remove(scenario.application, ["domain"])
	input_override := object.union(object.remove(scenario, ["application"]), {"application": without})
	count(purpose_declaration.deny) > 0 with input as input_override
}

test_fail_missing_stakeholder_groups if {
	without := object.remove(scenario.fundamental_rights_impact_assessment, ["stakeholder_groups"])
	input_override := object.union(object.remove(scenario, ["fundamental_rights_impact_assessment"]), {"fundamental_rights_impact_assessment": without})
	count(purpose_declaration.deny) > 0 with input as input_override
}

test_fail_empty_stakeholder_groups if {
	input_override := object.union(scenario, {"fundamental_rights_impact_assessment": {"stakeholder_groups": []}})
	count(purpose_declaration.deny) > 0 with input as input_override
}

test_fail_mitigation_not_documented if {
	input_override := object.union(scenario, {"fundamental_rights_impact_assessment": {"mitigation_documented": false}})
	count(purpose_declaration.deny) > 0 with input as input_override
}
