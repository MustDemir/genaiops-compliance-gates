# ================================================================
# G-OPS-04: Cybersecurity Operations — UNIT TESTS
# ================================================================
package genaiops.operations.data_security_controls_test

import rego.v1

import data.fixtures.healthcare.app_documentation as scenario
import data.genaiops.operations.data_security_controls

test_pass_valid_security_scenario if {
	count(data_security_controls.deny) == 0 with input as scenario
}

test_fail_image_scanning_disabled if {
	input_override := object.union(scenario, {"security": {"image_scanning_enabled": false}})
	count(data_security_controls.deny) > 0 with input as input_override
}

test_fail_network_policies_missing if {
	input_override := object.union(scenario, {"security": {"network_policies_specified": false}})
	count(data_security_controls.deny) > 0 with input as input_override
}

test_fail_encryption_at_rest_disabled if {
	input_override := object.union(scenario, {"data_governance": {"encryption_at_rest": false}})
	count(data_security_controls.deny) > 0 with input as input_override
}

test_fail_encryption_in_transit_disabled if {
	input_override := object.union(scenario, {"data_governance": {"encryption_in_transit": false}})
	count(data_security_controls.deny) > 0 with input as input_override
}
