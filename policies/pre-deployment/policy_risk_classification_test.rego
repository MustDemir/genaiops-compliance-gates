# ================================================================
# G-PRE-01: Risk Classification Validation — UNIT TESTS
# ================================================================
# Tests:       policy_risk_classification.rego (14 deny-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + FAIL-basic + FAIL-edge + HYBRID-manual-review
# Coverage:    8 tests for 14 rules (~57% rule-level, 100% rule-group coverage)
#
# Fixtures:    data.fixtures.healthcare.app_documentation (real Use-Case)
#              Scenario: Healthcare Ambient AI Scribe (high-risk, Annex III 5a)
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.pre_deployment.risk_classification_test

import rego.v1

import data.fixtures.healthcare as fixtures
import data.fixtures.healthcare.app_documentation as scenario
import data.genaiops.pre_deployment.risk_classification

# ================================================================
# PASS Tests (real Use-Case scenario must produce zero deny)
# ================================================================

test_pass_valid_high_risk_scenario if {
	# Healthcare Ambient AI Scribe — full high-risk classification per Annex III 5a
	count(risk_classification.deny) == 0 with input as scenario
}

test_pass_minimal_risk_without_annex_or_mitigation if {
	# Boundary: minimal-risk does NOT require annex_reference or mitigation_measures
	input_override := object.union(scenario, {"risk_classification": {
		"risk_class": "minimal",
		"classification_reasoning": "Chatbot without safety-critical function per AI Act Art. 52",
	}})
	count(risk_classification.deny) == 0 with input as input_override
}

# ================================================================
# FAIL Tests — Basic (core contract violations on real scenario)
# ================================================================

test_fail_missing_risk_class if {
	# Rule 1: risk_class field missing entirely
	# Note: object.union does deep-merge in OPA v1.x — we rebuild the sub-object explicitly.
	input_override := {
		"risk_classification": {"classification_reasoning": scenario.risk_classification.classification_reasoning},
		"manual_review": scenario.manual_review,
	}
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

test_fail_empty_risk_class_string if {
	# Rule 2: risk_class present but empty string
	input_override := object.union(scenario, {"risk_classification": object.union(
		scenario.risk_classification,
		{"risk_class": ""},
	)})
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

test_fail_invalid_risk_class_value if {
	# Rule 3: risk_class value not in {high, limited, minimal, unacceptable}
	input_override := object.union(scenario, {"risk_classification": object.union(
		scenario.risk_classification,
		{"risk_class": "extreme"},
	)})
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Edge (high-risk specific obligations, real scenario)
# ================================================================

test_fail_high_risk_without_annex_reference if {
	# Rule 5: high-risk requires annex_reference
	# Note: object.union does deep-merge in OPA v1.x — we rebuild risk_classification explicitly.
	input_override := {
		"risk_classification": {
			"risk_class": "high",
			"classification_reasoning": scenario.risk_classification.classification_reasoning,
			"mitigation_measures": scenario.risk_classification.mitigation_measures,
			# annex_reference intentionally omitted
		},
		"manual_review": scenario.manual_review,
	}
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

test_fail_high_risk_empty_mitigation_measures if {
	# Rule 6: high-risk requires non-empty mitigation_measures array
	input_override := object.union(scenario, {"risk_classification": object.union(
		scenario.risk_classification,
		{"mitigation_measures": []},
	)})
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — HYBRID Gate Manual-Review Evidence
# ================================================================

test_fail_missing_manual_review_section if {
	# Rule 7 (HYBRID): manual_review section required for audit trail
	input_override := object.remove(scenario, ["manual_review"])
	result := risk_classification.deny with input as input_override
	count(result) > 0
}

# ================================================================
# Art.-6-Pruefbaum (SPEC-02) — Checks C-A1..C-A7 + classification
# ================================================================
# Fixtures: scenarios/healthcare-ambient-ai-scribe/fixtures/art6_*.json
# (Fallback-Ablage nach SPEC-02 Abschnitt 7, solange der Szenario-
# Rahmen grid-redispatch aus SPEC-03 noch nicht existiert.)
# ================================================================

# --- Helfer: nur die C-A-Meldungen aus einem deny/warn-Set filtern ---
_ca_messages(msgs, prefix) := {m | some m in msgs; startswith(m, prefix)}

# ================================================================
# PASS — Fixture 1: SAFETY_COMPONENT ueber Arm A und Arm B
# ================================================================

test_pass_art6_redispatch_no_violations if {
	count(risk_classification.deny) == 0 with input as fixtures.art6_redispatch_pass
	count(risk_classification.warn) == 0 with input as fixtures.art6_redispatch_pass
}

test_pass_art6_redispatch_classified_safety_component if {
	risk_classification.classification == "SAFETY_COMPONENT" with input as fixtures.art6_redispatch_pass
}

# ================================================================
# HYBRID/Grenzfall — Fixture 2: Arm B traegt die Einstufung,
# C-A7 warnt mangels Aufsichtsnachweis
# ================================================================

test_hybrid_art6_lastprognose_classified_via_arm_b if {
	# Arm A verneint, Arm B bejaht -> dennoch SAFETY_COMPONENT
	risk_classification.classification == "SAFETY_COMPONENT" with input as fixtures.art6_lastprognose_boundary
}

test_hybrid_art6_lastprognose_warns_missing_oversight_evidence if {
	# C-A7: menschliche Kontrolle behauptet, aber kein Wirksamkeitsnachweis
	result := risk_classification.warn with input as fixtures.art6_lastprognose_boundary
	count(_ca_messages(result, "G-PRE-01/C-A7")) > 0
}

test_hybrid_art6_lastprognose_does_not_block if {
	# C-A7 ist SHOULD -> advisory, kein deny
	count(risk_classification.deny) == 0 with input as fixtures.art6_lastprognose_boundary
}

# ================================================================
# PASS — Fixture 3: Abs. 1a geltend gemacht UND Arm B bewertet
# und verneint -> muss sauber durchlaufen
# ================================================================

test_pass_art6_predictive_maintenance_no_violations if {
	count(risk_classification.deny) == 0 with input as fixtures.art6_predictive_maintenance
}

test_pass_art6_predictive_maintenance_classified_no_safety_component if {
	risk_classification.classification == "NO_SAFETY_COMPONENT" with input as fixtures.art6_predictive_maintenance
}

# ================================================================
# PASS — Fixture 4: ausserhalb Anhang III Nr. 2
# ================================================================

test_pass_art6_chatbot_not_in_scope if {
	risk_classification.classification == "NOT_IN_SCOPE" with input as fixtures.art6_chatbot_out_of_scope
}

test_pass_art6_chatbot_no_art6_violations if {
	# Kein C-A-Check darf ausserhalb Anhang III Nr. 2 feuern
	result := risk_classification.deny with input as fixtures.art6_chatbot_out_of_scope
	count(_ca_messages(result, "G-PRE-01/C-A")) == 0
}

# ================================================================
# FAIL — Fixture 5: DER WICHTIGSTE NEGATIVTEST DER SPEC.
# Abs. 1a behauptet, Arm B nicht bewertet -> C-A3 muss blockieren.
# ================================================================

test_fail_art6_optimization_claim_without_failure_assessment if {
	result := risk_classification.deny with input as fixtures.art6_optimization_claim_without_failure_assessment
	count(_ca_messages(result, "G-PRE-01/C-A3")) > 0
}

# ================================================================
# FAIL — Fixture 6: Selbsteinstufung widerspricht Arm B -> C-A6
# ================================================================

test_fail_art6_contradiction_self_declaration if {
	result := risk_classification.deny with input as fixtures.art6_contradiction
	count(_ca_messages(result, "G-PRE-01/C-A6")) > 0
}

test_fail_art6_contradiction_classified_safety_component if {
	# Art. 6 Abs. 1b ueberschreibt die Abs.-1a-Berufung
	risk_classification.classification == "SAFETY_COMPONENT" with input as fixtures.art6_contradiction
}

# ================================================================
# FAIL-basic — C-A1: art6_assessment fehlt vollstaendig
# ================================================================

test_fail_art6_missing_assessment_section if {
	input_override := object.remove(fixtures.art6_redispatch_pass, ["art6_assessment"])
	result := risk_classification.deny with input as input_override
	count(_ca_messages(result, "G-PRE-01/C-A1")) > 0
}

# ================================================================
# FAIL-basic / FAIL-edge — C-A2: deployment_context
# ================================================================

test_fail_art6_missing_deployment_context if {
	# Note: object.union deep-merges in OPA v1.x, so a nested key cannot be
	# dropped that way — json.remove operates on a JSON pointer path instead.
	input_override := json.remove(fixtures.art6_redispatch_pass, ["/system/deployment_context"])
	result := risk_classification.deny with input as input_override
	count(_ca_messages(result, "G-PRE-01/C-A2")) > 0
}

test_fail_art6_invalid_deployment_context if {
	input_override := object.union(fixtures.art6_redispatch_pass, {"system": object.union(
		fixtures.art6_redispatch_pass.system,
		{"deployment_context": "telecommunications"},
	)})
	result := risk_classification.deny with input as input_override
	count(_ca_messages(result, "G-PRE-01/C-A2")) > 0
}

# ================================================================
# FAIL-edge — C-A4: sole_use_categories leer bzw. unzulaessig
# ================================================================

test_fail_art6_exclusion_claimed_with_empty_categories if {
	input_override := object.union(fixtures.art6_predictive_maintenance, {"art6_assessment": object.union(
		fixtures.art6_predictive_maintenance.art6_assessment,
		{"art6_1a_exclusion_claimed": {"claimed": true, "sole_use_categories": []}},
	)})
	result := risk_classification.deny with input as input_override
	count(_ca_messages(result, "G-PRE-01/C-A4")) > 0
}

test_fail_art6_exclusion_claimed_with_invalid_category if {
	input_override := object.union(fixtures.art6_predictive_maintenance, {"art6_assessment": object.union(
		fixtures.art6_predictive_maintenance.art6_assessment,
		{"art6_1a_exclusion_claimed": {
			"claimed": true,
			"sole_use_categories": ["cost_reduction"],
		}},
	)})
	result := risk_classification.deny with input as input_override
	count(_ca_messages(result, "G-PRE-01/C-A4")) > 0
}

# ================================================================
# FAIL-edge — C-A5: bejahter Arm ohne justification
# ================================================================

test_fail_art6_arm_a_positive_without_justification if {
	# json.remove instead of object.union — see note on the C-A2 test above.
	input_override := json.remove(
		fixtures.art6_redispatch_pass,
		["/art6_assessment/arm_a_intended_purpose/justification"],
	)
	result := risk_classification.deny with input as input_override
	count(_ca_messages(result, "G-PRE-01/C-A5")) > 0
}

test_fail_art6_arm_b_positive_with_empty_justification if {
	input_override := object.union(fixtures.art6_redispatch_pass, {"art6_assessment": object.union(
		fixtures.art6_redispatch_pass.art6_assessment,
		{"arm_b_failure_impact": object.union(
			fixtures.art6_redispatch_pass.art6_assessment.arm_b_failure_impact,
			{"justification": ""},
		)},
	)})
	result := risk_classification.deny with input as input_override
	count(_ca_messages(result, "G-PRE-01/C-A5")) > 0
}
