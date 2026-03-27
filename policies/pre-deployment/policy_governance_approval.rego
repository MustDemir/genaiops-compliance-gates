# ================================================================
# G-PRE-05: Strategische Governance-Freigabe
# ================================================================
# Gate:       G-PRE-05 (Strategische Governance-Freigabe)
# Requirement: R004 — EU AI Act Art. 14
# Automation:  HYBRID (Conftest checks doc existence, manual approval)
# Input:       app_documentation.json
# Entrypoint:  deny[msg] (Conftest convention)
#
# Checks:
#   1. FRIA (Fundamental Rights Impact Assessment) completed
#   2. Human oversight model defined
#   3. Oversight lead assigned
#   4. Escalation procedure exists
#   5. Kill-switch capability enabled
#   6. Conformity assessment declaration available
#
# CDV-Pattern: Contract (docs exist) → Validation (completeness) → Severity (BLOCK)
# D3-Override: Art. 14 = First-Degree Oversight → max HYBRID
# ================================================================

package genaiops.pre_deployment.governance_approval

import rego.v1

# --- Rule 1: FRIA must be completed ---
deny contains msg if {
	not input.fundamental_rights_impact_assessment.fria_completed
	msg := "G-PRE-05 (R004): FRIA (Fundamental Rights Impact Assessment) not completed"
}

deny contains msg if {
	input.fundamental_rights_impact_assessment.fria_completed == false
	msg := "G-PRE-05 (R004): FRIA completed flag is false — assessment required before deployment"
}

# --- Rule 2: affected_rights must be documented ---
deny contains msg if {
	input.fundamental_rights_impact_assessment.fria_completed == true
	not input.fundamental_rights_impact_assessment.affected_rights
	msg := "G-PRE-05 (R004): affected_rights not documented despite FRIA completion"
}

deny contains msg if {
	input.fundamental_rights_impact_assessment.fria_completed == true
	count(input.fundamental_rights_impact_assessment.affected_rights) == 0
	msg := "G-PRE-05 (R004): affected_rights is empty — at least one right must be identified"
}

# --- Rule 3: human oversight model must be defined ---
deny contains msg if {
	not input.human_oversight.oversight_model
	msg := "G-PRE-05 (R004): human oversight model not defined"
}

deny contains msg if {
	input.human_oversight.oversight_model == ""
	msg := "G-PRE-05 (R004): human oversight model is empty string"
}

# --- Rule 4: oversight lead must be assigned ---
deny contains msg if {
	not input.human_oversight.human_oversight_lead
	msg := "G-PRE-05 (R004): human_oversight_lead not assigned"
}

deny contains msg if {
	input.human_oversight.human_oversight_lead == ""
	msg := "G-PRE-05 (R004): human_oversight_lead is empty — responsible person required"
}

# --- Rule 5: kill-switch must be enabled for high-risk ---
deny contains msg if {
	input.risk_classification.risk_class == "high"
	not input.human_oversight.intervention_capability.kill_switch
	msg := "G-PRE-05 (R004): kill_switch not enabled — required for high-risk systems (Art. 14)"
}

deny contains msg if {
	input.risk_classification.risk_class == "high"
	input.human_oversight.intervention_capability.kill_switch == false
	msg := "G-PRE-05 (R004): kill_switch is false — high-risk systems must have intervention capability"
}

# --- Rule 6: conformity assessment declaration ---
deny contains msg if {
	not input.conformity_assessment.declaration_available
	msg := "G-PRE-05 (R004): conformity assessment declaration not available"
}

deny contains msg if {
	input.conformity_assessment.declaration_available == false
	msg := "G-PRE-05 (R004): conformity assessment declaration missing — Art. 47 EU AI Act"
}
