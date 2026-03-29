# ================================================================
# G-DEP-05: Bias-Prüfung (Bias Assessment Complete)
# ================================================================
# Gate:       G-DEP-05 (Bias-Prüfung)
# Requirement: R013 — EU AI Act Art. 10(2)(f), Art. 9 Abs. 2 lit. a
# Automation:  AUTO (Conftest evaluates model_documentation.json)
# Input:       model_documentation.json (Lucaj Model Documentation Template)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Checks:
#   1. bias_detection section exists
#   2. bias_detection_methods are defined (at least one)
#   3. fairness_results are present with metric values
#   4. mitigation_measures are documented if bias detected
#   5. protected_attributes are explicitly listed
#
# CDV-Pattern: Contract (bias docs exist) → Validation (methods+results) → Severity (BLOCK)
# Lucaj-Ref:   Model Documentation Template → "Model Bias/Fairness" section
# ================================================================

package genaiops.pre_deployment.bias_assessment_complete

import rego.v1

# ================================================================
# Check 1: bias_detection section must exist
# ================================================================

deny contains msg if {
	not input.bias_detection
	msg := "G-DEP-05 (R013): bias_detection section is missing from model documentation"
}

# ================================================================
# Check 2: At least one bias detection method must be defined
# ================================================================

deny contains msg if {
	input.bias_detection
	not input.bias_detection.methods
	msg := "G-DEP-05 (R013): bias_detection.methods is missing — at least one detection method required"
}

deny contains msg if {
	input.bias_detection.methods
	count(input.bias_detection.methods) == 0
	msg := "G-DEP-05 (R013): bias_detection.methods is empty — at least one method required (e.g., counterfactual, disparate_impact)"
}

# ================================================================
# Check 3: Fairness results must be present with at least one metric
# ================================================================

deny contains msg if {
	input.bias_detection
	not input.bias_detection.fairness_results
	msg := "G-DEP-05 (R013): bias_detection.fairness_results is missing — evaluation results required"
}

deny contains msg if {
	input.bias_detection.fairness_results
	not input.bias_detection.fairness_results.metrics
	msg := "G-DEP-05 (R013): fairness_results.metrics is missing — quantitative fairness metrics required"
}

deny contains msg if {
	input.bias_detection.fairness_results.metrics
	count(input.bias_detection.fairness_results.metrics) == 0
	msg := "G-DEP-05 (R013): fairness_results.metrics is empty — at least one metric required (e.g., demographic_parity, equalized_odds)"
}

# ================================================================
# Check 4: Protected attributes must be explicitly listed
# ================================================================

deny contains msg if {
	input.bias_detection
	not input.bias_detection.protected_attributes
	msg := "G-DEP-05 (R013): bias_detection.protected_attributes is missing — Art. 10(2)(f) requires explicit identification"
}

deny contains msg if {
	input.bias_detection.protected_attributes
	count(input.bias_detection.protected_attributes) == 0
	msg := "G-DEP-05 (R013): protected_attributes is empty — at least one protected attribute required (e.g., gender, ethnicity, age)"
}

# ================================================================
# Check 5: Mitigation measures required if bias was detected
# ================================================================

deny contains msg if {
	input.bias_detection.fairness_results
	input.bias_detection.fairness_results.bias_detected == true
	not input.bias_detection.mitigation_measures
	msg := "G-DEP-05 (R013): bias detected but mitigation_measures is missing — Art. 9 requires documented risk mitigation"
}

deny contains msg if {
	input.bias_detection.fairness_results
	input.bias_detection.fairness_results.bias_detected == true
	input.bias_detection.mitigation_measures
	count(input.bias_detection.mitigation_measures) == 0
	msg := "G-DEP-05 (R013): bias detected but mitigation_measures is empty — at least one mitigation action required"
}
