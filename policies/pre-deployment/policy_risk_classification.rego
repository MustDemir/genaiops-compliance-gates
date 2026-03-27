# ================================================================
# G-PRE-01: Risk Classification Validation
# ================================================================
# Gate:       G-PRE-01 (Risiko-Klassifikation)
# Requirement: R001 — EU AI Act Art. 9
# Automation:  HYBRID (Conftest validates format, manual review substance)
# Input:       app_documentation.json
# Entrypoint:  deny[msg] (Conftest convention)
#
# Checks:
#   1. risk_class exists and is a valid EU AI Act class
#   2. classification_reasoning is non-empty
#   3. annex_reference is provided for high-risk systems
#   4. mitigation_measures are defined for high-risk systems
#
# CDV-Pattern: Contract (valid class) → Validation (reasoning) → Severity (BLOCK)
# ================================================================

package genaiops.pre_deployment.risk_classification

import rego.v1

_valid_risk_classes := {"high", "limited", "minimal", "unacceptable"}

# --- Rule 1: risk_class must exist ---
deny contains msg if {
	not input.risk_classification.risk_class
	msg := "G-PRE-01 (R001): risk_classification.risk_class is missing"
}

# --- Rule 2: risk_class must not be empty string ---
deny contains msg if {
	input.risk_classification.risk_class == ""
	msg := "G-PRE-01 (R001): risk_classification.risk_class is empty string"
}

# --- Rule 3: risk_class must be a valid EU AI Act class ---
deny contains msg if {
	rc := input.risk_classification.risk_class
	rc != ""
	not rc in _valid_risk_classes
	msg := sprintf("G-PRE-01 (R001): invalid risk_class '%s' — must be one of: high, limited, minimal, unacceptable", [rc])
}

# --- Rule 4: classification_reasoning must be non-empty ---
deny contains msg if {
	not input.risk_classification.classification_reasoning
	msg := "G-PRE-01 (R001): classification_reasoning is missing"
}

deny contains msg if {
	input.risk_classification.classification_reasoning == ""
	msg := "G-PRE-01 (R001): classification_reasoning is empty — substantive justification required"
}

# --- Rule 5: high-risk systems must have annex_reference ---
deny contains msg if {
	input.risk_classification.risk_class == "high"
	not input.risk_classification.annex_reference
	msg := "G-PRE-01 (R001): annex_reference required for high-risk classification"
}

deny contains msg if {
	input.risk_classification.risk_class == "high"
	input.risk_classification.annex_reference == ""
	msg := "G-PRE-01 (R001): annex_reference is empty — Annex III reference required for high-risk systems"
}

# --- Rule 6: high-risk systems must have mitigation measures ---
deny contains msg if {
	input.risk_classification.risk_class == "high"
	not input.risk_classification.mitigation_measures
	msg := "G-PRE-01 (R001): mitigation_measures required for high-risk classification"
}

deny contains msg if {
	input.risk_classification.risk_class == "high"
	count(input.risk_classification.mitigation_measures) == 0
	msg := "G-PRE-01 (R001): mitigation_measures array is empty — at least one measure required"
}
