# ================================================================
# G-DEP-03: Transparency Documentation Present
# ================================================================
# Gate:       G-DEP-03 (Transparenzdokumentation)
# Requirement: R007 — EU AI Act Art. 13, Art. 26 Abs. 7, Art. 50
# Automation:  AUTO (Conftest evaluates app_documentation.json)
# Input:       app_documentation.json (Lucaj Application Documentation Template)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Checks:
#   1. transparency section exists
#   2. instructions_for_deployers is present and non-empty
#   3. model_capabilities are documented
#   4. known_limitations are documented
#   5. ai_content_labeling is configured (Art. 50 GenAI)
#
# CDV-Pattern: Contract (transparency docs exist) → Validation (completeness) → Severity (BLOCK)
# Lucaj-Ref:   Application Documentation Template → "Application Functionality" section
# ================================================================

package genaiops.deployment.transparency_docs_present

import rego.v1

# ================================================================
# Check 1: transparency section must exist
# ================================================================

deny contains msg if {
	not input.transparency
	msg := "G-DEP-03 (R007): transparency section is missing — Art. 13 requires deployer instructions"
}

# ================================================================
# Check 2: Instructions for deployers must be present
# ================================================================

deny contains msg if {
	input.transparency
	not input.transparency.instructions_for_deployers
	msg := "G-DEP-03 (R007): transparency.instructions_for_deployers is missing — Art. 13(1) mandates clear usage instructions"
}

deny contains msg if {
	input.transparency.instructions_for_deployers == ""
	msg := "G-DEP-03 (R007): instructions_for_deployers is empty — substantive deployer guidance required"
}

# ================================================================
# Check 3: Model capabilities must be documented
# ================================================================

deny contains msg if {
	input.transparency
	not input.transparency.model_capabilities
	msg := "G-DEP-03 (R007): transparency.model_capabilities is missing — system capabilities must be disclosed"
}

deny contains msg if {
	input.transparency.model_capabilities == ""
	msg := "G-DEP-03 (R007): model_capabilities is empty — substantive capability description required"
}

# ================================================================
# Check 4: Known limitations must be documented
# ================================================================

deny contains msg if {
	input.transparency
	not input.transparency.known_limitations
	msg := "G-DEP-03 (R007): transparency.known_limitations is missing — Art. 13(3)(b) requires disclosure of limitations"
}

deny contains msg if {
	input.transparency.known_limitations
	count(input.transparency.known_limitations) == 0
	msg := "G-DEP-03 (R007): known_limitations is empty — at least one known limitation must be disclosed"
}

# ================================================================
# Check 5: AI content labeling must be configured (Art. 50 GenAI)
# ================================================================

deny contains msg if {
	input.transparency
	not input.transparency.ai_content_labeling
	msg := "G-DEP-03 (R007): transparency.ai_content_labeling is missing — Art. 50 requires AI-generated content labeling for GenAI systems"
}

deny contains msg if {
	input.transparency.ai_content_labeling
	not input.transparency.ai_content_labeling.enabled
	msg := "G-DEP-03 (R007): ai_content_labeling.enabled is missing — must declare whether content labeling is active"
}
