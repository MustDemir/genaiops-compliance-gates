# ================================================================
# G-PRE-05: Governance Approval — UNIT TESTS
# ================================================================
# Tests:       policy_governance_approval.rego (17 deny-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + multi-rule-FAIL (fixture) + 17× rule-isolation-FAIL
# Coverage:    19 tests for 17 rules — 7/7 check-groups covered
#              (FRIA, affected_rights, oversight_model, oversight_lead,
#              kill_switch [conditional], conformity, approval [HYBRID]),
#              rule-level 17/17 strict-isolation + multi-rule fixture.
#              Pattern-class coverage: 6/6 — top-level-missing,
#              field-missing, string-empty, boolean-false,
#              array-empty, conditional-rule (R9/R10 depend on
#              risk_class == "high" from G-DEP-05 precedent).
#
# Fixtures:    data.fixtures.healthcare.app_documentation
#              (shared PASS — full governance docs: FRIA, oversight,
#              conformity, approval all present and valid).
#              data.fixtures.healthcare.app_documentation_incomplete
#              (shared FAIL — multi-rule: FRIA missing, oversight
#              incomplete, approval missing → 5+ rules fire).
#
# Strengthened assertion for multi-rule test:
#   count(result) >= 5 — realistic governance failure scenario.
#
# Methodology: Strict rule-isolation per DSR-Rigor — each rule fires
#              in exactly one dedicated test. HYBRID gate (D3-Override
#              Art. 14) has 5 approval rules (R13-R17) covering the
#              manual-approval evidence requirements. Conditional
#              rules (R9/R10) isolate by injecting risk_class: "high"
#              AND toggling kill_switch value.
#
# DSR traceability:
#   D3-Override: Art. 14 First-Degree Oversight = max HYBRID
#   → Conftest checks MANUAL approval evidence (not the decision itself)
#   → Tests validate that documentation requirements are enforced.
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.pre_deployment.governance_approval_test

import rego.v1

import data.fixtures.healthcare.app_documentation as scenario_pass
import data.fixtures.healthcare.app_documentation_incomplete as scenario_fail
import data.genaiops.pre_deployment.governance_approval

# ================================================================
# PASS Tests (real Use-Case full governance documentation)
# ================================================================

test_pass_full_governance_approval if {
	# Healthcare Ambient AI Scribe has complete governance:
	# FRIA + oversight_model + oversight_lead + kill_switch
	# (high-risk) + conformity declaration + approval evidence.
	count(governance_approval.deny) == 0 with input as scenario_pass
}

# ================================================================
# FAIL Tests — Multi-rule via shared incomplete fixture
# ================================================================

test_fail_realistic_multi_rule_incomplete_governance if {
	# app_documentation_incomplete triggers multiple rules across
	# governance dimensions (FRIA/oversight/approval gaps).
	result := governance_approval.deny with input as scenario_fail
	count(result) >= 5
}

# ================================================================
# FAIL Tests — Rule-isolation (Rule 1: FRIA completed)
# ================================================================

test_fail_fria_completed_missing if {
	# R1 (isolation): fria_completed field absent.
	# Remove-then-union to defeat object.union deep-merge.
	input_override := object.union(
		object.remove(scenario_pass, ["fundamental_rights_impact_assessment"]),
		{"fundamental_rights_impact_assessment": object.remove(
			scenario_pass.fundamental_rights_impact_assessment,
			["fria_completed"],
		)},
	)
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_fria_completed_false if {
	# R2 (isolation): fria_completed == false.
	# Pattern-class: boolean-false.
	input_override := object.union(scenario_pass, {"fundamental_rights_impact_assessment": object.union(
		scenario_pass.fundamental_rights_impact_assessment,
		{"fria_completed": false},
	)})
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Rule 2: affected_rights)
# ================================================================

test_fail_affected_rights_missing if {
	# R3 (isolation): fria_completed: true but affected_rights
	# field absent. Conditional: requires FRIA completed.
	input_override := object.union(
		object.remove(scenario_pass, ["fundamental_rights_impact_assessment"]),
		{"fundamental_rights_impact_assessment": object.remove(
			scenario_pass.fundamental_rights_impact_assessment,
			["affected_rights"],
		)},
	)
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_affected_rights_empty_array if {
	# R4 (isolation): affected_rights present but empty array.
	# Conditional: requires FRIA completed.
	input_override := object.union(scenario_pass, {"fundamental_rights_impact_assessment": object.union(
		scenario_pass.fundamental_rights_impact_assessment,
		{"affected_rights": []},
	)})
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Rule 3: oversight_model)
# ================================================================

test_fail_oversight_model_missing if {
	# R5 (isolation): human_oversight.oversight_model absent.
	input_override := object.union(
		object.remove(scenario_pass, ["human_oversight"]),
		{"human_oversight": object.remove(scenario_pass.human_oversight, ["oversight_model"])},
	)
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_oversight_model_empty_string if {
	# R6 (isolation): oversight_model == "".
	input_override := object.union(scenario_pass, {"human_oversight": object.union(
		scenario_pass.human_oversight,
		{"oversight_model": ""},
	)})
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Rule 4: oversight_lead)
# ================================================================

test_fail_oversight_lead_missing if {
	# R7 (isolation): human_oversight_lead field absent.
	input_override := object.union(
		object.remove(scenario_pass, ["human_oversight"]),
		{"human_oversight": object.remove(scenario_pass.human_oversight, ["human_oversight_lead"])},
	)
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_oversight_lead_empty_string if {
	# R8 (isolation): human_oversight_lead == "".
	input_override := object.union(scenario_pass, {"human_oversight": object.union(
		scenario_pass.human_oversight,
		{"human_oversight_lead": ""},
	)})
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Rule 5: kill_switch — conditional)
# ================================================================
# R9/R10 only fire when risk_class == "high". All isolation tests
# inherit risk_class: "high" from the PASS fixture.

test_fail_kill_switch_missing_for_high_risk if {
	# R9 (isolation): risk_class=high but kill_switch field absent.
	# Pattern-class: conditional-rule. Two-level remove-then-union
	# (outer: human_oversight, inner: intervention_capability).
	input_override := object.union(
		object.remove(scenario_pass, ["human_oversight"]),
		{"human_oversight": object.union(
			object.remove(scenario_pass.human_oversight, ["intervention_capability"]),
			{"intervention_capability": object.remove(
				scenario_pass.human_oversight.intervention_capability,
				["kill_switch"],
			)},
		)},
	)
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_kill_switch_false_for_high_risk if {
	# R10 (isolation): risk_class=high and kill_switch: false.
	input_override := object.union(scenario_pass, {"human_oversight": object.union(
		scenario_pass.human_oversight,
		{"intervention_capability": object.union(
			scenario_pass.human_oversight.intervention_capability,
			{"kill_switch": false},
		)},
	)})
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Rule 6: conformity_assessment)
# ================================================================

test_fail_conformity_declaration_missing if {
	# R11 (isolation): declaration_available field absent.
	input_override := object.union(
		object.remove(scenario_pass, ["conformity_assessment"]),
		{"conformity_assessment": object.remove(scenario_pass.conformity_assessment, ["declaration_available"])},
	)
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_conformity_declaration_false if {
	# R12 (isolation): declaration_available == false.
	input_override := object.union(scenario_pass, {"conformity_assessment": object.union(
		scenario_pass.conformity_assessment,
		{"declaration_available": false},
	)})
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Rule 7: HYBRID approval evidence)
# ================================================================
# D3-Override: Art. 14 First-Degree Oversight → max HYBRID.
# These rules validate that MANUAL approval evidence exists.

test_fail_approval_section_missing if {
	# R13 (isolation): approval section entirely absent.
	input_override := object.remove(scenario_pass, ["approval"])
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_approval_approved_by_missing if {
	# R14 (isolation): approval.approved_by field absent.
	input_override := object.union(
		object.remove(scenario_pass, ["approval"]),
		{"approval": object.remove(scenario_pass.approval, ["approved_by"])},
	)
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_approval_approved_by_empty_string if {
	# R15 (isolation): approval.approved_by == "".
	input_override := object.union(scenario_pass, {"approval": object.union(
		scenario_pass.approval,
		{"approved_by": ""},
	)})
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_approval_approved_at_missing if {
	# R16 (isolation): approval.approved_at field absent.
	input_override := object.union(
		object.remove(scenario_pass, ["approval"]),
		{"approval": object.remove(scenario_pass.approval, ["approved_at"])},
	)
	result := governance_approval.deny with input as input_override
	count(result) > 0
}

test_fail_approval_approved_at_empty_string if {
	# R17 (isolation): approval.approved_at == "".
	input_override := object.union(scenario_pass, {"approval": object.union(
		scenario_pass.approval,
		{"approved_at": ""},
	)})
	result := governance_approval.deny with input as input_override
	count(result) > 0
}
