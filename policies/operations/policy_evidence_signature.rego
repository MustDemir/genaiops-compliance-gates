# ================================================================
# G-OPS-05 / C-04..C-07: the evidence manifest carries a verified
# signature, bound to the identity that produced it
# ================================================================
# Gate:        G-OPS-05 (Evidence-Completeness und Audit-Trail-Integritaet)
# Requirement: R005 — EU AI Act Art. 12, Art. 15
# Input:       signature_verification document, produced by
#              evidence-store/scripts/verify_signature.py
# Entrypoint:  deny contains msg (Conftest convention)
#
# WHAT A SIGNATURE PROVES HERE, AND WHAT IT DOES NOT:
#
#   It states ORIGIN and TIME — which workflow, in which repository, on
#   which commit, asserted this chain head and these verdicts, and when.
#   It says NOTHING about whether the values are correct. That is what the
#   other gates decide, and where the numbers came from was SPEC-04's
#   question. A compromised CI signs a wrong record flawlessly; what rises
#   is the cost of forgery, from "edit a row" to "take over the CI
#   identity" (SPEC-05 Abschnitt 13).
#
# The detector verifies, this policy decides (B-04). verify_signature.py
# writes no decision field; the verdict is made here and recorded once.
#
# Waiver: NOT ALLOWED.
# ================================================================

package genaiops.operations.evidence_signature

import rego.v1

_v := input.signature_verification

_local := _v.signing_context == "local"

# ================================================================
# C-04 [MUST, E-1] — a signature verification exists and is valid
# ================================================================
# Absent document: Rego cannot tell a missing input from a missing rule,
# so the presence obligation lives in required_inputs and is enforced by
# the orchestrator and by CI (B-17). What this check can see is a document
# that says the verification failed.

deny contains msg if {
	_v
	not _local
	not _v.verified
	msg := sprintf("G-OPS-05/C-04 (R005, Art. 12, Art. 15): the evidence manifest is not covered by a valid signature (verified=%v). Without it the run's evidence cannot be told from a rewritten copy of it", [_v.verified])
}

# A local run has no OIDC identity and therefore no signature; E-1 needs
# the CI (HANDBUCH 5.3). The run stays drivable and the evidence says which
# rung it stands on — that is the point of signing_context, not a back door:
# CI asserts the value where the manifest is built AND in the job that signs
# it, and refuses anything but "ci" (SPEC-05 Abschnitt 8.1).
warn contains msg if {
	_v
	_local
	msg := "G-OPS-05/C-04 (R005, Art. 12, Art. 15): this run is unsigned — signing_context is 'local', so the evidence stands at E-0. E-1 requires the CI"
}

# ================================================================
# C-05 [MUST, E-1] — the signature comes from the expected identity
# ================================================================
# `verified: true` alone does not answer the question. A verification
# against a permissive identity pattern is green and pins nothing — the
# same hole as B-17: the mechanism is present and does not act.

deny contains msg if {
	_v
	not _local
	_v.verified
	not _v.identity_pinned
	msg := "G-OPS-05/C-05 (R005, Art. 12, Art. 15): the signature was verified without pinning the producer identity. A verification that accepts any signer proves that something signed, not who"
}

deny contains msg if {
	_v
	not _local
	_v.verified
	not _v.certificate_oidc_issuer
	msg := "G-OPS-05/C-05 (R005, Art. 12, Art. 15): no OIDC issuer recorded — the identity is unanchored"
}

deny contains msg if {
	_v
	not _local
	_v.verified
	not _v.workflow_sha_pinned
	msg := "G-OPS-05/C-05 (R005, Art. 12, Art. 15): the signature is not bound to a commit. 'This workflow signed' is a weaker claim than 'this workflow signed on this state', and traceability is the point"
}

# ================================================================
# C-06 [MUST, E-1] — the signed chain head is the head that was verified
# ================================================================
# The check that is easy to miss at design time. Without it a validly
# signed manifest could be presented that has nothing to do with the
# database that was verified — a flawless signature on an unrelated
# statement. That is the gap SPEC-04 closed with "measure, then sign",
# here on the signing side.

deny contains msg if {
	_v
	_v.signed_chain_head
	_v.observed_chain_head
	_v.signed_chain_head != _v.observed_chain_head
	msg := sprintf("G-OPS-05/C-06 (R005, Art. 12, Art. 15): the signed chain head (%v) is not the head of the chain that was verified (%v). The signature is valid and covers a different statement", [_v.signed_chain_head, _v.observed_chain_head])
}

deny contains msg if {
	_v
	not _local
	not _v.signed_chain_head
	msg := "G-OPS-05/C-06 (R005, Art. 12, Art. 15): the verification names no signed chain head, so nothing ties the signature to the evidence chain"
}

# ================================================================
# C-07 [MUST, E-1] — the transparency log was checked
# ================================================================
# cosign checks the log BY DEFAULT; it has to be switched off deliberately
# with --insecure-ignore-tlog. A SHOULD here would have turned the default
# into an option and invited switching it off when the service is slow.
# Without the log there is no independent timestamp and no public
# verifiability: the proof falls back to "trust whoever hands it to you".
#
# The price is named rather than hidden: Sigstore is a third-party service,
# and its unavailability blocks the run. Same trade-off as the fail-closed
# evidence path (B-16) — a proof system that waves things through when it
# breaks is not one.

deny contains msg if {
	_v
	not _local
	_v.verified
	not _v.tlog_verified
	msg := "G-OPS-05/C-07 (R005, Art. 12, Art. 15): the transparency-log check did not take place. Without it the signature has no independent timestamp and cannot be verified by anyone but the holder"
}

deny contains msg if {
	_v
	not _local
	_v.tlog_verified
	not _v.rekor_log_index
	msg := "G-OPS-05/C-07 (R005, Art. 12, Art. 15): the log check is reported as done but no log index was recorded. A third party cannot find an entry that is not addressed"
}

# ================================================================
# Provenance of the input itself
# ================================================================
# A verification run against a checked-in fixture proves the mechanism,
# never the current run. It is labelled in the document, and a gate that
# read one without noticing would be the quiet fallback of B-03.

deny contains msg if {
	_v
	_v.input_provenance == "fixture"
	msg := "G-OPS-05 (R005, Art. 12, Art. 15): this verification was run against a checked-in fixture, not against this run's manifest. It demonstrates the mechanism and proves nothing about this run"
}
