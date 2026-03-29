# ================================================================
# G-OPS-03: Performance-Monitoring und Drift-Detection
# ================================================================
# Gate:       G-OPS-03 (Performance-Monitoring)
# Requirement: R010 — EU AI Act Art. 72, Art. 9 Abs. 2
# Automation:  AUTO (Gatekeeper Admission Controller / Conftest CI)
# Input:       K8s Deployment manifest (Pod template)
# Entrypoint:  violation[{"msg": msg}] (Gatekeeper convention)
#
# Dual-mode: Works with both Gatekeeper (input.review.object.*)
# and Conftest CI (input.spec.*) by resolving the object root.
#
# Checks:
#   1. drift-detection-enabled annotation present and "true"
#   2. service-monitor-configured annotation present and "true"
#   3. Prometheus scrape annotations present
# ================================================================

package genaiops.operations.monitoring_configured

import rego.v1

# Dual-mode: Gatekeeper wraps input in review.object, Conftest passes directly
_object := input.review.object if { input.review }
_object := input if { not input.review }

_pod_annotations := _object.spec.template.metadata.annotations

# ================================================================
# Check 1: Drift detection must be enabled
# ================================================================

violation contains {"msg": msg} if {
	not _pod_annotations["genaiops.io/drift-detection-enabled"]
	msg := "G-OPS-03 (R010): annotation genaiops.io/drift-detection-enabled is missing"
}

violation contains {"msg": msg} if {
	_pod_annotations["genaiops.io/drift-detection-enabled"] != "true"
	msg := sprintf("G-OPS-03 (R010): drift-detection-enabled is '%s' — must be 'true'", [_pod_annotations["genaiops.io/drift-detection-enabled"]])
}

# ================================================================
# Check 2: ServiceMonitor must be configured
# ================================================================

violation contains {"msg": msg} if {
	not _pod_annotations["genaiops.io/service-monitor-configured"]
	msg := "G-OPS-03 (R010): annotation genaiops.io/service-monitor-configured is missing"
}

violation contains {"msg": msg} if {
	_pod_annotations["genaiops.io/service-monitor-configured"] != "true"
	msg := sprintf("G-OPS-03 (R010): service-monitor-configured is '%s' — must be 'true'", [_pod_annotations["genaiops.io/service-monitor-configured"]])
}

# ================================================================
# Check 3: Prometheus scrape config present
# ================================================================

violation contains {"msg": msg} if {
	not _pod_annotations["prometheus.io/scrape"]
	msg := "G-OPS-03 (R010): annotation prometheus.io/scrape is missing — metrics endpoint not discoverable"
}

violation contains {"msg": msg} if {
	_pod_annotations["prometheus.io/scrape"] != "true"
	msg := "G-OPS-03 (R010): prometheus.io/scrape is not 'true' — metrics scraping disabled"
}
