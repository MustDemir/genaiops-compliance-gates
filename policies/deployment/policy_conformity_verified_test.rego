# ================================================================
# G-DEP-04: Conformity Input Verification — UNIT TESTS
# ================================================================
package genaiops.deployment.conformity_verified_test

import rego.v1

import data.fixtures.healthcare.app_documentation as scenario
import data.genaiops.deployment.conformity_verified

test_pass_valid_conformity_scenario if {
	count(conformity_verified.deny) == 0 with input as scenario
}

test_fail_missing_conformity_section if {
	input_override := object.remove(scenario, ["conformity_assessment"])
	count(conformity_verified.deny) > 0 with input as input_override
}

test_fail_ce_marking_not_verified if {
	input_override := object.union(scenario, {"conformity_assessment": {"ce_marking_verified": false}})
	count(conformity_verified.deny) > 0 with input as input_override
}

test_fail_provider_docs_not_received if {
	input_override := object.union(scenario, {"conformity_assessment": {"provider_documentation_received": false}})
	count(conformity_verified.deny) > 0 with input as input_override
}

test_fail_missing_provider_contact if {
	without := object.remove(scenario.conformity_assessment, ["provider_contact"])
	input_override := object.union(object.remove(scenario, ["conformity_assessment"]), {"conformity_assessment": without})
	count(conformity_verified.deny) > 0 with input as input_override
}

test_fail_missing_model_version if {
	without := object.remove(scenario.model_info, ["model_version"])
	input_override := object.union(object.remove(scenario, ["model_info"]), {"model_info": without})
	count(conformity_verified.deny) > 0 with input as input_override
}
