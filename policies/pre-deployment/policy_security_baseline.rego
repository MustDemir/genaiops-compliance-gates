# ================================================================
# G-PRE-04: Security Baseline (Container Compliance)
# ================================================================
# Gate:       G-PRE-04 (Security-Baseline)
# Requirement: R003 — EU AI Act Art. 15
# Automation:  AUTO (Conftest validates K8s deployment manifest)
# Input:       K8s Deployment YAML
# Entrypoint:  deny[msg] (Conftest convention)
#
# CDV-Contract (6 checks):
#   P1: runAsNonRoot + runAsUser > 0          [MUST]  — CIS 5.2.6
#   P2: resources.limits (CPU + Memory)        [MUST]  — CIS 5.4.x
#   P3: readOnlyRootFilesystem: true           [SHOULD] — CIS 5.2.9
#   P4: no secrets in env (plain values)       [MUST]
#   P5: (slim base image — checked via Dockerfile, not here)
#   P6: allowPrivilegeEscalation: false        [MUST]  — CIS 5.2.5
#       capabilities.drop: ["ALL"]             [MUST]  — CIS 5.2.7
#
# References:
#   - CIS Kubernetes Benchmark v1.8, Section 5.2
#   - NSA/CISA Kubernetes Hardening Guide v1.2
# ================================================================

package genaiops.pre_deployment.security_baseline

import rego.v1

# Helper: iterate over all containers in spec.template.spec.containers
_containers := input.spec.template.spec.containers

# ================================================================
# P1: Non-Root Enforcement (CIS 5.2.6) [MUST]
# ================================================================

deny contains msg if {
	some container in _containers
	not container.securityContext.runAsNonRoot
	msg := sprintf("G-PRE-04/P1 (R003): container '%s' must set securityContext.runAsNonRoot: true", [container.name])
}

deny contains msg if {
	some container in _containers
	container.securityContext.runAsNonRoot == false
	msg := sprintf("G-PRE-04/P1 (R003): container '%s' has runAsNonRoot: false — root execution prohibited", [container.name])
}

deny contains msg if {
	some container in _containers
	container.securityContext.runAsUser == 0
	msg := sprintf("G-PRE-04/P1 (R003): container '%s' runs as UID 0 (root) — must use non-root user", [container.name])
}

# ================================================================
# P2: Resource Limits (CIS 5.4.x) [MUST]
# ================================================================

deny contains msg if {
	some container in _containers
	not container.resources.limits
	msg := sprintf("G-PRE-04/P2 (R003): container '%s' has no resources.limits defined", [container.name])
}

deny contains msg if {
	some container in _containers
	container.resources.limits
	not container.resources.limits.cpu
	msg := sprintf("G-PRE-04/P2 (R003): container '%s' is missing resources.limits.cpu", [container.name])
}

deny contains msg if {
	some container in _containers
	container.resources.limits
	not container.resources.limits.memory
	msg := sprintf("G-PRE-04/P2 (R003): container '%s' is missing resources.limits.memory", [container.name])
}

# ================================================================
# P3: Read-Only Root Filesystem (CIS 5.2.9) [SHOULD]
# ================================================================
# Note: SHOULD-level — generates warning-style denial.
# Waiverable with Security Lead approval (14 days).

deny contains msg if {
	some container in _containers
	not container.securityContext.readOnlyRootFilesystem
	msg := sprintf("G-PRE-04/P3 (R003): container '%s' should set readOnlyRootFilesystem: true [SHOULD]", [container.name])
}

deny contains msg if {
	some container in _containers
	container.securityContext.readOnlyRootFilesystem == false
	msg := sprintf("G-PRE-04/P3 (R003): container '%s' has readOnlyRootFilesystem: false — writable root filesystem [SHOULD]", [container.name])
}

# ================================================================
# P4: No Secrets in Plain ENV [MUST]
# ================================================================

_secret_patterns := {"password", "secret", "token", "api_key", "apikey", "private_key"}

deny contains msg if {
	some container in _containers
	some env_var in container.env
	env_var.value
	not env_var.valueFrom
	lower_name := lower(env_var.name)
	some pattern in _secret_patterns
	contains(lower_name, pattern)
	msg := sprintf("G-PRE-04/P4 (R003): container '%s' has suspected secret '%s' as plain env value — use secretKeyRef", [container.name, env_var.name])
}

# ================================================================
# P6: No Privilege Escalation (CIS 5.2.5) [MUST]
# ================================================================

deny contains msg if {
	some container in _containers
	not container.securityContext.allowPrivilegeEscalation == false
	container.securityContext.allowPrivilegeEscalation != false
	msg := sprintf("G-PRE-04/P6 (R003): container '%s' must set allowPrivilegeEscalation: false", [container.name])
}

# ================================================================
# P6b: Drop ALL Capabilities (CIS 5.2.7) [MUST]
# ================================================================

deny contains msg if {
	some container in _containers
	not container.securityContext.capabilities
	msg := sprintf("G-PRE-04/P6 (R003): container '%s' must define capabilities.drop: [\"ALL\"]", [container.name])
}

deny contains msg if {
	some container in _containers
	container.securityContext.capabilities
	not "ALL" in container.securityContext.capabilities.drop
	msg := sprintf("G-PRE-04/P6 (R003): container '%s' must drop ALL capabilities — found: %v", [container.name, container.securityContext.capabilities.drop])
}
