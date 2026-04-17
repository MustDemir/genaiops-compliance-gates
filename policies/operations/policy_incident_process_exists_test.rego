# ================================================================
# G-OPS-02: Incident Process Exists — UNIT TESTS
# ================================================================
# Tests:       policy_incident_process_exists.rego (6 violation-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS-conftest + PASS-gatekeeper + FAIL-missing + FAIL-wrong-value
# Coverage:    4 tests for 6 rules — 3/3 check-groups covered,
#              rule-level 2/6 explicit + PASS covers positive path of all 6.
#              Dual-mode resolver (Conftest vs. Gatekeeper) explicitly tested.
#
# Fixtures:    data.fixtures.healthcare.deployment_compliant
#              (Conftest mode — direct deployment input)
#              data.fixtures.healthcare.deployment_incident_pass
#              (Gatekeeper mode — review.object wrapper)
#
# FAIL-Variant techniques (per Session-Handoff 2026-04-17):
#   - Key-removal in nested K8s manifests: json.patch with op "remove"
#     (JSON Pointer escaping: "/" = "~1" per RFC 6901).
#   - Leaf-value override: object.union deep-merge preserves siblings.
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.operations.incident_process_exists_test

import rego.v1

import data.fixtures.healthcare.deployment_compliant as scenario_conftest
import data.fixtures.healthcare.deployment_incident_pass as scenario_gatekeeper
import data.genaiops.operations.incident_process_exists

# ================================================================
# PASS Tests (both dual-modes: Conftest direct + Gatekeeper wrapper)
# ================================================================

test_pass_conftest_mode_compliant_deployment if {
	# Conftest mode: input is the deployment directly (no review wrapper).
	# Real Use-Case deployment has all 3 incident annotations present.
	# Positive path exercises all 6 rules (no violation triggered).
	count(incident_process_exists.violation) == 0 with input as scenario_conftest
}

test_pass_gatekeeper_mode_incident_annotations_present if {
	# Gatekeeper mode: input is an AdmissionReview with review.object wrapper.
	# This scenario tests the dual-mode resolver explicitly.
	count(incident_process_exists.violation) == 0 with input as scenario_gatekeeper
}

# ================================================================
# FAIL Tests — Missing annotation (Check 2: incident-contact)
# ================================================================

test_fail_missing_incident_contact_annotation if {
	# Rule 3: pod annotation genaiops.io/incident-contact missing.
	# Art. 26(5) AI Act requires identifiable reporting contact.
	# JSON Pointer escaping: "/" = "~1" per RFC 6901.
	input_override := json.patch(scenario_conftest, [{
		"op": "remove",
		"path": "/spec/template/metadata/annotations/genaiops.io~1incident-contact",
	}])
	result := incident_process_exists.violation with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Wrong value (Check 3: rollback-mechanism != "true")
# ================================================================

test_fail_rollback_mechanism_wrong_value if {
	# Rule 6: rollback-mechanism present but not "true" (e.g. "false").
	# object.union deep-merges at leaf level — other annotations preserved.
	input_override := object.union(scenario_conftest, {"spec": {"template": {"metadata": {"annotations": {
		"genaiops.io/rollback-mechanism": "false",
	}}}}})
	result := incident_process_exists.violation with input as input_override
	count(result) > 0
}
