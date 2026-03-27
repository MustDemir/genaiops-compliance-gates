# ================================================================
# G-OPS-05: Evidence-Completeness und Audit-Trail-Integritaet
# ================================================================
# Gate:       G-OPS-05 (Evidence-Completeness)
# Requirement: R005 — EU AI Act Art. 12, Art. 15
# Automation:  AUTO (Gatekeeper Admission Controller)
# Input:       K8s Deployment manifest (Pod template)
# Entrypoint:  violation[{"msg": msg}] (Gatekeeper convention)
#
# Checks:
#   1. evidence-store-connected annotation present and "true"
#   2. hash-chain-enabled annotation present and "true"
#   3. Evidence store type is specified
#
# Note: Hash-chain integrity verification is done by CronJob
#       (cronjob-hash-chain-verify.yaml), not by admission.
#       This gate validates that the deployment DECLARES its
#       evidence store integration.
#
# Waiver: NOT ALLOWED — evidence integrity is non-negotiable
# ================================================================

package genaiops.operations.evidence_completeness

import rego.v1

# Gatekeeper passes input as input.review.object
_pod_annotations := input.review.object.spec.template.metadata.annotations

# ================================================================
# Check 1: Evidence Store connection declared
# ================================================================

violation contains {"msg": msg} if {
	not _pod_annotations["genaiops.io/evidence-store-connected"]
	msg := "G-OPS-05 (R005): annotation genaiops.io/evidence-store-connected is missing — evidence persistence required (Art. 12)"
}

violation contains {"msg": msg} if {
	_pod_annotations["genaiops.io/evidence-store-connected"] != "true"
	msg := sprintf("G-OPS-05 (R005): evidence-store-connected is '%s' — must be 'true'", [_pod_annotations["genaiops.io/evidence-store-connected"]])
}

# ================================================================
# Check 2: Hash-chain integrity enabled
# ================================================================

violation contains {"msg": msg} if {
	not _pod_annotations["genaiops.io/hash-chain-enabled"]
	msg := "G-OPS-05 (R005): annotation genaiops.io/hash-chain-enabled is missing — tamper-proof audit trail required"
}

violation contains {"msg": msg} if {
	_pod_annotations["genaiops.io/hash-chain-enabled"] != "true"
	msg := sprintf("G-OPS-05 (R005): hash-chain-enabled is '%s' — must be 'true' for audit trail integrity", [_pod_annotations["genaiops.io/hash-chain-enabled"]])
}

# ================================================================
# Check 3: Evidence store type specified (for audit documentation)
# ================================================================

_deployment_annotations := input.review.object.metadata.annotations

violation contains {"msg": msg} if {
	not _deployment_annotations["genaiops.io/evidence-store-type"]
	msg := "G-OPS-05 (R005): annotation genaiops.io/evidence-store-type is missing — storage backend must be declared"
}

violation contains {"msg": msg} if {
	est := _deployment_annotations["genaiops.io/evidence-store-type"]
	est == ""
	msg := "G-OPS-05 (R005): evidence-store-type is empty string — must specify storage backend"
}
