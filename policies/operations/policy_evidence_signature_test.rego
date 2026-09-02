# ================================================================
# G-OPS-05 / C-04..C-07: signature verification — UNIT TESTS
# ================================================================
# Tests:      policy_evidence_signature.rego
# Convention: OPA Rego unit tests (opa test policies/ tests/fixtures/ -v)
# Pattern:    for every deny, one input that triggers it and one that
#             does not. A rule that only ever passes proves nothing —
#             the counter-check is the difference between a check and a
#             decoration (B-16).
#
# The signed values themselves are never asserted here. The signature
# states origin and time, not correctness (SPEC-05 Abschnitt 13); whether
# a verdict is right is decided by the gate that produced it.
# ================================================================

package genaiops.operations.evidence_signature_test

import rego.v1

import data.genaiops.operations.evidence_signature

_ci_verified := {"signature_verification": {
	"gate_id": "G-OPS-05",
	"verified": true,
	"identity_pinned": true,
	"certificate_oidc_issuer": "https://token.actions.githubusercontent.com",
	"workflow_sha_pinned": true,
	"signed_chain_head": "abc123",
	"observed_chain_head": "abc123",
	"tlog_verified": true,
	"rekor_log_index": 2675797321,
	"signing_context": "ci",
	"input_provenance": "ci-run",
}}

_with(field, value) := {"signature_verification": object.union(
	_ci_verified.signature_verification,
	{field: value},
)}

_without(field) := {"signature_verification": object.remove(
	_ci_verified.signature_verification,
	{field},
)}

# ── The positive path: a verified, identity-bound, logged signature ──

test_verified_signature_passes if {
	count(evidence_signature.deny) == 0 with input as _ci_verified
}

test_verified_signature_warns_about_nothing if {
	count(evidence_signature.warn) == 0 with input as _ci_verified
}

# ── C-04: the verification failed ──

test_c04_denies_failed_verification if {
	count(evidence_signature.deny) > 0 with input as _with("verified", false)
}

# ── C-04 local: unsigned run warns, and does not block ──

test_c04_local_run_warns if {
	count(evidence_signature.warn) == 1 with input as _with("signing_context", "local")
}

test_c04_local_run_does_not_block if {
	count(evidence_signature.deny) == 0 with input as _with("signing_context", "local")
}

# Counter-check to the two above: the same document in CI is not a warning
# but a finding — otherwise "local" would be a way out rather than a label.
test_c04_unverified_in_ci_is_not_a_warning if {
	count(evidence_signature.warn) == 0 with input as _with("verified", false)
}

# ── C-05: identity, issuer, commit ──

test_c05_denies_unpinned_identity if {
	count(evidence_signature.deny) > 0 with input as _with("identity_pinned", false)
}

test_c05_denies_missing_issuer if {
	count(evidence_signature.deny) > 0 with input as _without("certificate_oidc_issuer")
}

test_c05_denies_signature_not_bound_to_commit if {
	count(evidence_signature.deny) > 0 with input as _with("workflow_sha_pinned", false)
}

# ── C-06: the signed head is the head that was verified ──

test_c06_denies_head_mismatch if {
	count(evidence_signature.deny) > 0 with input as _with("observed_chain_head", "deadbeef")
}

test_c06_denies_missing_signed_head if {
	count(evidence_signature.deny) > 0 with input as _without("signed_chain_head")
}

# Counter-check: matching heads are not a finding — the rule fires on the
# difference, not on the presence of the fields.
test_c06_matching_heads_pass if {
	count(evidence_signature.deny) == 0 with input as _with("observed_chain_head", "abc123")
}

# ── C-07: the transparency log ──

test_c07_denies_unchecked_tlog if {
	count(evidence_signature.deny) > 0 with input as _with("tlog_verified", false)
}

test_c07_denies_missing_log_index if {
	count(evidence_signature.deny) > 0 with input as _without("rekor_log_index")
}

# ── The input's own provenance ──

test_fixture_input_is_denied if {
	count(evidence_signature.deny) > 0 with input as _with("input_provenance", "fixture")
}

test_ci_run_input_is_accepted if {
	count(evidence_signature.deny) == 0 with input as _with("input_provenance", "ci-run")
}
