# ================================================================
# PROSPEKTIV — Art.-25-Rollenwechsel-Monitoring — UNIT TESTS
# ================================================================
# NICHT Teil von tests/run_all_rego_tests.sh / der 141 Tests.
# Manuell: opa test prospective/art25-role-change/ -v
# ================================================================
package genaiops.prospective.role_change_monitoring_test

import rego.v1

import data.genaiops.prospective.role_change_monitoring as gate

_benign := {"change_event": {
	"system_already_on_market": true,
	"rebranding": {"own_name_or_trademark_applied": false},
	"substantial_modification": {"modified": false, "remains_high_risk_art6": false},
	"purpose_change": {"changed": false, "becomes_high_risk_art6": false},
}}

test_no_warn_for_benign_change if {
	count(gate.warn) == 0 with input as _benign
}

test_warn_on_rebranding if {
	override := object.union(_benign, {"change_event": {"rebranding": {"own_name_or_trademark_applied": true}}})
	count(gate.warn) > 0 with input as override
}

test_warn_on_substantial_modification if {
	override := object.union(_benign, {"change_event": {"substantial_modification": {"modified": true, "remains_high_risk_art6": true}}})
	count(gate.warn) > 0 with input as override
}

test_warn_on_purpose_change if {
	override := object.union(_benign, {"change_event": {"purpose_change": {"changed": true, "becomes_high_risk_art6": true}}})
	count(gate.warn) > 0 with input as override
}
