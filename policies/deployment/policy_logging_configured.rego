# ================================================================
# G-DEP-06: Logging Configuration Validation
# ================================================================
# Gate:        G-DEP-06 (Protokollierungskonfiguration)
# Requirement: R014 — EU AI Act Art. 12, Art. 26 Abs. 6
# Automation:  AUTO (Conftest validates logging configuration fields)
# Input:       app_documentation.json (TechOps Application-Documentation Template)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Checks (derived from R014 acceptance_criteria):
#   1. logging is enabled                          (AC1, Art. 12)
#   2. all intended event types are captured        (AC1, Art. 12)
#   3. retention period >= 6 months (180 days)       (AC2, Art. 26 Abs. 6)
#   4. logs are accessible / auditable               (AC3, Art. 12)
#
# CDV-Pattern: Contract (logging block present) -> Validation (fields) -> Severity (BLOCK)
# ================================================================

package genaiops.deployment.logging_configured

import rego.v1

_min_retention_days := 180 # 6 months per EU AI Act Art. 26 Abs. 6

# --- Rule 0: logging_configuration section must exist ---
deny contains msg if {
	not input.logging_configuration
	msg := "G-DEP-06 (R014): logging_configuration section missing — Art. 12 logging obligations not documented"
}

# --- Rule 1: logging must be enabled (AC1) ---
deny contains msg if {
	not input.logging_configuration.logging_enabled
	msg := "G-DEP-06 (R014): logging_configuration.logging_enabled is missing or false — logging must be enabled (Art. 12)"
}

# --- Rule 2: intended event types must be captured (AC1) ---
deny contains msg if {
	not input.logging_configuration.event_types_captured
	msg := "G-DEP-06 (R014): logging_configuration.event_types_captured is missing — intended event types must be logged"
}

deny contains msg if {
	count(input.logging_configuration.event_types_captured) == 0
	msg := "G-DEP-06 (R014): logging_configuration.event_types_captured is empty — at least one event type must be captured"
}

# --- Rule 3: retention period must be >= 6 months (AC2, Art. 26 Abs. 6) ---
deny contains msg if {
	not input.logging_configuration.retention_period_days
	msg := "G-DEP-06 (R014): logging_configuration.retention_period_days is missing — minimum retention must be documented"
}

deny contains msg if {
	input.logging_configuration.retention_period_days < _min_retention_days
	msg := sprintf(
		"G-DEP-06 (R014): retention_period_days is %d — must be at least %d (6 months, Art. 26 Abs. 6)",
		[input.logging_configuration.retention_period_days, _min_retention_days],
	)
}

# --- Rule 4: logs must be accessible / auditable (AC3) ---
deny contains msg if {
	not input.logging_configuration.log_accessibility
	msg := "G-DEP-06 (R014): logging_configuration.log_accessibility is missing — logs must be accessible for supervisory authorities"
}

deny contains msg if {
	input.logging_configuration.log_accessibility == ""
	msg := "G-DEP-06 (R014): logging_configuration.log_accessibility is empty — accessibility/auditability must be documented"
}
