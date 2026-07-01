# ================================================================
# G-DEP-04: Conformity Input Verification
# ================================================================
# Gate:        G-DEP-04 (Konformitaets-Eingangspruefung)
# Requirement: R011 — EU AI Act Art. 26 Abs. 1
# Automation:  AUTO
# Input:       app_documentation.json (TechOps Application/Model Template)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Scope (Anhang M, Tab. M.3): Deployer-side verification of provider-supplied
# conformity artefacts only. Art. 47/48 (provider CE/declaration duties) are
# OUT OF SCOPE. declaration_available is checked by G-PRE-05 (not duplicated).
#
# Checks (R011):
#   1. CE marking verified by deployer
#   2. provider documentation received
#   3. provider is contactable (traceability)
#   4. model version documented (model-dataset traceability)
#   5. provider documented (model-dataset traceability)
# ================================================================

package genaiops.deployment.conformity_verified

import rego.v1

# --- Rule 0: conformity_assessment section must exist ---
deny contains msg if {
	not input.conformity_assessment
	msg := "G-DEP-04 (R011): conformity_assessment section missing — Art. 26 Abs. 1 deployer verification not documented"
}

# --- Rule 1: CE marking must be verified (policy_conformity_declaration) ---
deny contains msg if {
	not input.conformity_assessment.ce_marking_verified
	msg := "G-DEP-04 (R011): conformity_assessment.ce_marking_verified is missing or false — deployer must verify CE marking"
}

# --- Rule 2: provider documentation must be received ---
deny contains msg if {
	not input.conformity_assessment.provider_documentation_received
	msg := "G-DEP-04 (R011): conformity_assessment.provider_documentation_received is missing or false"
}

# --- Rule 3: provider contact must be documented (traceability) ---
deny contains msg if {
	not input.conformity_assessment.provider_contact
	msg := "G-DEP-04 (R011): conformity_assessment.provider_contact is missing — provider must be traceable"
}

deny contains msg if {
	input.conformity_assessment.provider_contact == ""
	msg := "G-DEP-04 (R011): conformity_assessment.provider_contact is empty — provider must be traceable"
}

# --- Rule 4: model version documented (policy_model_dataset_traceability) ---
deny contains msg if {
	not input.model_info.model_version
	msg := "G-DEP-04 (R011): model_info.model_version is missing — model-dataset traceability required"
}

# --- Rule 5: provider documented (policy_model_dataset_traceability) ---
deny contains msg if {
	not input.model_info.provider
	msg := "G-DEP-04 (R011): model_info.provider is missing — model-dataset traceability required"
}
