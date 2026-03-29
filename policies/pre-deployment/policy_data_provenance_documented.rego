# ================================================================
# G-DEP-01: Data Provenance Documented
# ================================================================
# Gate:       G-DEP-01 (Data Governance)
# Requirement: R002 — EU AI Act Art. 10, Art. 11 Annex IV §2d
# Automation:  AUTO (Conftest evaluates data_documentation.json)
# Input:       data_documentation.json (Lucaj Data Documentation Template)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Checks:
#   1. data_provenance section exists
#   2. collection_methods are documented (at least one)
#   3. sources are listed with identifiers
#   4. preprocessing_steps are documented
#   5. data_version is specified for reproducibility
#
# CDV-Pattern: Contract (provenance exists) → Validation (completeness) → Severity (BLOCK)
# Lucaj-Ref:   Data Documentation Template → "Provenance / Collection" section
# ================================================================

package genaiops.pre_deployment.data_provenance_documented

import rego.v1

# ================================================================
# Check 1: data_provenance section must exist
# ================================================================

deny contains msg if {
	not input.data_provenance
	msg := "G-DEP-01 (R002): data_provenance section is missing — Art. 10 requires documented data governance"
}

# ================================================================
# Check 2: Collection methods must be documented
# ================================================================

deny contains msg if {
	input.data_provenance
	not input.data_provenance.collection_methods
	msg := "G-DEP-01 (R002): data_provenance.collection_methods is missing — Annex IV §2d requires data collection documentation"
}

deny contains msg if {
	input.data_provenance.collection_methods
	count(input.data_provenance.collection_methods) == 0
	msg := "G-DEP-01 (R002): collection_methods is empty — at least one method required (e.g., manual_annotation, web_scraping, sensor_data)"
}

# ================================================================
# Check 3: Data sources must be listed
# ================================================================

deny contains msg if {
	input.data_provenance
	not input.data_provenance.sources
	msg := "G-DEP-01 (R002): data_provenance.sources is missing — data origin must be traceable"
}

deny contains msg if {
	input.data_provenance.sources
	count(input.data_provenance.sources) == 0
	msg := "G-DEP-01 (R002): data_provenance.sources is empty — at least one data source required"
}

# ================================================================
# Check 4: Preprocessing steps must be documented
# ================================================================

deny contains msg if {
	input.data_provenance
	not input.data_provenance.preprocessing_steps
	msg := "G-DEP-01 (R002): data_provenance.preprocessing_steps is missing — data transformation chain required for reproducibility"
}

deny contains msg if {
	input.data_provenance.preprocessing_steps
	count(input.data_provenance.preprocessing_steps) == 0
	msg := "G-DEP-01 (R002): preprocessing_steps is empty — at least one step required (e.g., cleaning, normalization, tokenization)"
}

# ================================================================
# Check 5: Data version must be specified
# ================================================================

deny contains msg if {
	input.data_provenance
	not input.data_provenance.data_version
	msg := "G-DEP-01 (R002): data_provenance.data_version is missing — versioned datasets required for traceability"
}

deny contains msg if {
	input.data_provenance.data_version == ""
	msg := "G-DEP-01 (R002): data_provenance.data_version is empty string — version identifier required"
}
