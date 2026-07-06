# ================================================================
# G-OPS-04: Cybersecurity Operations (Data Security Controls)
# ================================================================
# Gate:        G-OPS-04 (Cybersecurity-Operations)
# Requirement: R003 — EU AI Act Art. 15
# Automation:  AUTO
# Input:       app_documentation.json (security + data_governance blocks)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Redundancy note (Anhang M/H): R003 is multi-mapped. G-PRE-04 (Security-Baseline)
# checks the Kubernetes securityContext (non-root, limits, privilege escalation,
# capabilities, secrets). This gate checks the DISTINCT operational controls:
# image scanning, network policies, and data encryption.
#
# Checks (R003):
#   1. container image scanning enabled     (policy_data_security_controls)
#   2. network policies specified
#   3. encryption at rest enabled
#   4. encryption in transit enabled
# ================================================================

package genaiops.operations.data_security_controls

import rego.v1

# --- Rule 1: image scanning must be enabled ---
deny contains msg if {
	not input.security.image_scanning_enabled
	msg := "G-OPS-04 (R003): security.image_scanning_enabled is missing or false — container images must be scanned"
}

# --- Rule 2: network policies must be specified ---
deny contains msg if {
	not input.security.network_policies_specified
	msg := "G-OPS-04 (R003): security.network_policies_specified is missing or false — network policies must be defined"
}

# --- Rule 3: encryption at rest must be enabled ---
deny contains msg if {
	not input.data_governance.encryption_at_rest
	msg := "G-OPS-04 (R003): data_governance.encryption_at_rest is missing or false — data must be encrypted at rest"
}

# --- Rule 4: encryption in transit must be enabled ---
deny contains msg if {
	not input.data_governance.encryption_in_transit
	msg := "G-OPS-04 (R003): data_governance.encryption_in_transit is missing or false — data must be encrypted in transit"
}
