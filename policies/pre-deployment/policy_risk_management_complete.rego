# ================================================================
# G-PRE-03: Risk Management Completeness
# ================================================================
# Gate:        G-PRE-03 (Risikomanagement-Vollstaendigkeit)
# Requirement: R001 — EU AI Act Art. 9
# Automation:  HYBRID (Conftest checks risk register, manual review assesses quality)
# Input:       app_documentation.json (risk_management block)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Redundancy note (Anhang M/H): R001 is multi-mapped. G-PRE-01 covers
# risk_classification.* (class, reasoning, annex, mitigation). This gate covers
# the DISTINCT risk-management register and data-risk assessment.
#
# Checks (R001):
#   1. risk register is versioned          (policy_risk_management_complete)
#   2. at least one risk is identified
#   3. every identified risk has a mitigation
#   4. data risk assessment performed       (policy_data_risk_assessed)
#   5. data classification documented
# ================================================================

package genaiops.pre_deployment.risk_management_complete

import rego.v1

# --- Rule 0: risk_management section must exist ---
deny contains msg if {
	not input.risk_management
	msg := "G-PRE-03 (R001): risk_management section missing — Art. 9 risk register not documented"
}

# --- Rule 1: risk register must be versioned (policy_risk_management_complete) ---
deny contains msg if {
	not input.risk_management.risk_register_versioned
	msg := "G-PRE-03 (R001): risk_management.risk_register_versioned is missing or false — risk register must be versioned"
}

# --- Rule 2: at least one risk must be identified ---
deny contains msg if {
	not input.risk_management.identified_risks
	msg := "G-PRE-03 (R001): risk_management.identified_risks is missing — risks must be identified"
}

deny contains msg if {
	count(input.risk_management.identified_risks) == 0
	msg := "G-PRE-03 (R001): risk_management.identified_risks is empty — at least one risk required"
}

# --- Rule 3: every identified risk must carry a mitigation ---
deny contains msg if {
	some risk in input.risk_management.identified_risks
	not risk.mitigation
	msg := sprintf("G-PRE-03 (R001): identified risk '%v' has no mitigation — each risk requires a mitigation", [risk.risk])
}

# --- Rule 4: data risk assessment must be performed (policy_data_risk_assessed) ---
deny contains msg if {
	not input.risk_management.data_risk_assessment.assessed
	msg := "G-PRE-03 (R001): risk_management.data_risk_assessment.assessed is missing or false — data risk must be assessed"
}

# --- Rule 5: data classification must be documented ---
deny contains msg if {
	not input.risk_management.data_risk_assessment.data_classification
	msg := "G-PRE-03 (R001): data_risk_assessment.data_classification is missing — data classification required"
}
