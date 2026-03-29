# ================================================================
# G-OPS-02: Incident Reporting Process Exists
# ================================================================
# Gate:       G-OPS-02 (Incident-Reporting)
# Requirement: R009 — EU AI Act Art. 26 Abs. 5, Art. 73
# Automation:  AUTO (Gatekeeper Admission Controller)
# Input:       K8s Deployment manifest (Pod template)
# Entrypoint:  violation[{"msg": msg}] (Gatekeeper convention)
#
# Checks:
#   1. incident-response-configured annotation present and "true"
#   2. incident-contact annotation present (non-empty)
#   3. rollback-mechanism annotation present and "true"
#
# Art. 26(5): Deployers must report serious incidents to provider
#             and relevant market surveillance authority.
# Art. 73:   Defines the notification procedure and timelines.
#
# CDV-Pattern: Contract (annotations exist) → Validation (values) → Severity (BLOCK)
# ================================================================

package genaiops.operations.incident_process_exists

import rego.v1

# Gatekeeper passes input as input.review.object
_pod_annotations := input.review.object.spec.template.metadata.annotations

# ================================================================
# Check 1: Incident response must be configured
# ================================================================

violation contains {"msg": msg} if {
	not _pod_annotations["genaiops.io/incident-response-configured"]
	msg := "G-OPS-02 (R009): annotation genaiops.io/incident-response-configured is missing"
}

violation contains {"msg": msg} if {
	_pod_annotations["genaiops.io/incident-response-configured"] != "true"
	msg := sprintf("G-OPS-02 (R009): incident-response-configured is '%s' — must be 'true'", [_pod_annotations["genaiops.io/incident-response-configured"]])
}

# ================================================================
# Check 2: Incident contact must be specified
# ================================================================

violation contains {"msg": msg} if {
	not _pod_annotations["genaiops.io/incident-contact"]
	msg := "G-OPS-02 (R009): annotation genaiops.io/incident-contact is missing — Art. 26(5) requires identifiable reporting contact"
}

violation contains {"msg": msg} if {
	_pod_annotations["genaiops.io/incident-contact"] == ""
	msg := "G-OPS-02 (R009): incident-contact is empty — responsible person or team must be identified"
}

# ================================================================
# Check 3: Rollback mechanism must be available
# ================================================================

violation contains {"msg": msg} if {
	not _pod_annotations["genaiops.io/rollback-mechanism"]
	msg := "G-OPS-02 (R009): annotation genaiops.io/rollback-mechanism is missing — incident remediation requires rollback capability"
}

violation contains {"msg": msg} if {
	_pod_annotations["genaiops.io/rollback-mechanism"] != "true"
	msg := sprintf("G-OPS-02 (R009): rollback-mechanism is '%s' — must be 'true'", [_pod_annotations["genaiops.io/rollback-mechanism"]])
}
