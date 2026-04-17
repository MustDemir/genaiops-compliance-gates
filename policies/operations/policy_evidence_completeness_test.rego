# ================================================================
# G-OPS-05: Evidence-Completeness — UNIT TESTS
# ================================================================
# Tests:       policy_evidence_completeness.rego (6 violation-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + FAIL-missing + FAIL-wrong-value + FAIL-edge
# Coverage:    4 tests for 6 rules — 3/3 check-groups covered,
#              rule-level 4/6 (PASS covers positive path of all 6).
#
# Fixtures:    data.fixtures.healthcare.deployment_compliant (real Use-Case)
#              Scenario: Healthcare Ambient AI Scribe K8s Deployment
#
# FAIL-Variant technique (learned 2026-04-17):
#   - object.union in OPA v1.x does DEEP-merge (not shallow).
#   - For value overrides at leaf level: object.union works.
#   - For key removal: use json.patch with op "remove" (JSON Pointer
#     escaping: "/" = "~1" per RFC 6901).
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.operations.evidence_completeness_test

import rego.v1

import data.fixtures.healthcare.deployment_compliant as scenario
import data.genaiops.operations.evidence_completeness

# ================================================================
# PASS Tests (real Use-Case scenario must produce zero violations)
# ================================================================

test_pass_compliant_deployment if {
	# Healthcare Ambient AI Scribe — full evidence-store annotations per R005
	# Positive path exercises all 6 rules (no violation triggered).
	count(evidence_completeness.violation) == 0 with input as scenario
}

# ================================================================
# FAIL Tests — Missing annotation (Check 1: evidence-store-connected)
# ================================================================

test_fail_missing_evidence_store_connected_annotation if {
	# Rule 1: pod annotation genaiops.io/evidence-store-connected missing
	# JSON Pointer escaping: "/" = "~1" per RFC 6901.
	input_override := json.patch(scenario, [{
		"op": "remove",
		"path": "/spec/template/metadata/annotations/genaiops.io~1evidence-store-connected",
	}])
	result := evidence_completeness.violation with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Wrong value (Check 2: hash-chain-enabled != "true")
# ================================================================

test_fail_hash_chain_disabled_value if {
	# Rule 4: hash-chain-enabled present but not "true" (e.g. "false")
	# object.union deep-merges at leaf level — other annotations preserved.
	input_override := object.union(scenario, {"spec": {"template": {"metadata": {"annotations": {
		"genaiops.io/hash-chain-enabled": "false",
	}}}}})
	result := evidence_completeness.violation with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Edge: empty string (Check 3: evidence-store-type)
# ================================================================

test_fail_empty_evidence_store_type if {
	# Rule 6: evidence-store-type present but empty string
	# Deployment-level annotation (metadata.annotations, not pod template).
	input_override := object.union(scenario, {"metadata": {"annotations": {
		"genaiops.io/evidence-store-type": "",
	}}})
	result := evidence_completeness.violation with input as input_override
	count(result) > 0
}
