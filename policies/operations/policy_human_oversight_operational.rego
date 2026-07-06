# ================================================================
# G-OPS-01: Human Oversight (Operational Effectiveness)
# ================================================================
# Gate:        G-OPS-01 (Human Oversight)
# Requirement: R008 — EU AI Act Art. 14, Art. 26 Abs. 2
# Automation:  HYBRID (Conftest checks structure, manual review assesses effectiveness)
# Input:       app_documentation.json (human_oversight block)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Redundancy note (Anhang M/H): G-PRE-05 (R004, pre-deployment) checks
# oversight_model, human_oversight_lead, intervention_capability.kill_switch.
# This gate (R008, operational) checks the DISTINCT operational-effectiveness
# fields: role assignment, escalation procedure, override + monitoring capability.
#
# Checks (R008):
#   1. operational oversight roles assigned  (policy_human_oversight_defined)
#   2. escalation procedure defined
#   3. output override capability present
#   4. real-time monitoring active
# ================================================================

package genaiops.operations.human_oversight_operational

import rego.v1

# --- Rule 0: human_oversight section must exist ---
deny contains msg if {
	not input.human_oversight
	msg := "G-OPS-01 (R008): human_oversight section missing — Art. 14 operational oversight not documented"
}

# --- Rule 1: operational oversight roles must be assigned ---
deny contains msg if {
	not input.human_oversight.oversight_roles
	msg := "G-OPS-01 (R008): human_oversight.oversight_roles is missing — HITL roles must be assigned"
}

deny contains msg if {
	count(input.human_oversight.oversight_roles) == 0
	msg := "G-OPS-01 (R008): human_oversight.oversight_roles is empty — at least one oversight role required"
}

# --- Rule 2: escalation procedure must be defined ---
deny contains msg if {
	not input.human_oversight.escalation_procedure
	msg := "G-OPS-01 (R008): human_oversight.escalation_procedure is missing — override/escalation path required"
}

# --- Rule 3: output override capability must be present ---
deny contains msg if {
	not input.human_oversight.intervention_capability.output_override
	msg := "G-OPS-01 (R008): intervention_capability.output_override is missing or false — operators must be able to override output"
}

# --- Rule 4: real-time monitoring must be active ---
deny contains msg if {
	not input.human_oversight.intervention_capability.real_time_monitoring
	msg := "G-OPS-01 (R008): intervention_capability.real_time_monitoring is missing or false — real-time oversight required"
}
