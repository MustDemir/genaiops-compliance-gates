# ================================================================
# G-PRE-02: Purpose Declaration Completeness
# ================================================================
# Gate:        G-PRE-02 (Zweckbestimmung)
# Requirement: R012 — EU AI Act Art. 27 (FRIA)
# Automation:  HYBRID (Conftest checks completeness, manual review assesses FRIA substance)
# Input:       app_documentation.json (TechOps Application Template)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Redundancy note (Anhang M/H): fria_completed and affected_rights are checked
# by G-PRE-05. This gate checks the FRIA-completeness fields G-PRE-05 does NOT
# cover (stakeholder_groups, mitigation_documented) plus the purpose declaration.
#
# Checks (R012):
#   1. purpose/description declared      (policy_purpose_declaration_complete)
#   2. application domain/sector declared
#   3. FRIA stakeholder groups identified
#   4. FRIA mitigation documented
# ================================================================

package genaiops.pre_deployment.purpose_declaration

import rego.v1

# --- Rule 1: purpose description must be present (policy_purpose_declaration_complete) ---
deny contains msg if {
	not input.application.description
	msg := "G-PRE-02 (R012): application.description is missing — intended purpose must be declared"
}

deny contains msg if {
	input.application.description == ""
	msg := "G-PRE-02 (R012): application.description is empty — intended purpose must be declared"
}

# --- Rule 2: application domain/sector must be present ---
deny contains msg if {
	not input.application.domain
	msg := "G-PRE-02 (R012): application.domain is missing — sector/domain must be declared"
}

# --- Rule 3: FRIA stakeholder groups must be identified (policy_intended_use_boundaries) ---
deny contains msg if {
	not input.fundamental_rights_impact_assessment.stakeholder_groups
	msg := "G-PRE-02 (R012): fundamental_rights_impact_assessment.stakeholder_groups is missing — affected stakeholders must be identified"
}

deny contains msg if {
	count(input.fundamental_rights_impact_assessment.stakeholder_groups) == 0
	msg := "G-PRE-02 (R012): stakeholder_groups is empty — at least one affected stakeholder group required"
}

# --- Rule 4: FRIA mitigation must be documented (policy_model_description_complete) ---
deny contains msg if {
	not input.fundamental_rights_impact_assessment.mitigation_documented
	msg := "G-PRE-02 (R012): fundamental_rights_impact_assessment.mitigation_documented is missing or false — FRIA mitigations must be documented"
}
