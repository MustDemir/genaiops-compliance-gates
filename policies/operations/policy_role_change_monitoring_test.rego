# ================================================================
# G-OPS-06: Rollenwechsel-Monitoring — UNIT TESTS
# ================================================================
# Tests:      policy_role_change_monitoring.rego (C-25a..C-25d)
# Convention: OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
#
# Diese Datei ersetzt die prospektive Skizze unter
# prospective/art25-role-change/policy_role_change_monitoring_test.rego,
# die bewusst ausserhalb der gezaehlten Testsuite lag. Mit der
# Ueberfuehrung nach G-OPS-06 (SPEC-03 Abschnitt 5) sind die Tests
# regulaer Teil von tests/run_all_rego_tests.sh.
# ================================================================

package genaiops.operations.role_change_monitoring_test

import rego.v1

import data.fixtures.healthcare as fixtures
import data.genaiops.operations.role_change_monitoring as gate

_msgs(set_, prefix) := {m | some m in set_; startswith(m, prefix)}

# ================================================================
# PASS — benigne Aenderung loest keinen Tatbestand aus
# ================================================================

test_pass_benign_change_no_trigger if {
	count(gate.deny) == 0 with input as fixtures.art25_benign_change
	count(gate.warn) == 0 with input as fixtures.art25_benign_change
}

# ================================================================
# C-25a (MUST) — Rebranding, binaerer Tatbestand
# ================================================================

test_fail_c25a_rebranding_triggers_deny if {
	result := gate.deny with input as fixtures.art25_rebranding_with_handover
	count(_msgs(result, "G-OPS-06/C-25a")) > 0
}

test_pass_c25a_with_handover_no_c25d if {
	# Uebergabeartefakte vollstaendig -> C-25d darf NICHT feuern
	result := gate.deny with input as fixtures.art25_rebranding_with_handover
	count(_msgs(result, "G-OPS-06/C-25d")) == 0
}

# ================================================================
# C-25b (SHOULD) — wesentliche Veraenderung bleibt advisory
# ================================================================

test_warn_c25b_substantial_modification_is_advisory if {
	result := gate.warn with input as fixtures.art25_substantial_modification
	count(_msgs(result, "G-OPS-06/C-25b")) > 0
}

test_pass_c25b_does_not_block if {
	# Die Art.-97-Schwellenwerte fehlen -> SHOULD, kein deny
	count(gate.deny) == 0 with input as fixtures.art25_substantial_modification
}

# ================================================================
# C-25c (MUST) — Zweckaenderung, ausgewertet gegen die
# classification-Regel aus SPEC-02, nicht gegen ein Manifest-Boolean
# ================================================================

test_fail_c25c_purpose_change_to_high_risk if {
	result := gate.deny with input as fixtures.art25_purpose_change_to_high_risk
	count(_msgs(result, "G-OPS-06/C-25c")) > 0
}

test_c25c_uses_spec02_classification_not_a_boolean if {
	# Beweis der Kopplung: die classification-Regel aus G-PRE-01 liefert
	# fuer den Zustand VOR der Aenderung NOT_IN_SCOPE und danach
	# SAFETY_COMPONENT. Kein Feld im Manifest behauptet das Ergebnis.
	ce := fixtures.art25_purpose_change_to_high_risk.change_event
	before := data.genaiops.pre_deployment.risk_classification.classification with input as ce.purpose_change.before
	after := data.genaiops.pre_deployment.risk_classification.classification with input as ce.purpose_change.after
	before == "NOT_IN_SCOPE"
	after == "SAFETY_COMPONENT"
}

test_fail_c25c_missing_before_state if {
	ce := fixtures.art25_purpose_change_to_high_risk.change_event
	input_override := {"change_event": json.remove(ce, ["/purpose_change/before"])}
	result := gate.deny with input as input_override
	count(_msgs(result, "G-OPS-06/C-25c")) > 0
}

test_fail_c25c_missing_after_state if {
	ce := fixtures.art25_purpose_change_to_high_risk.change_event
	input_override := {"change_event": json.remove(ce, ["/purpose_change/after"])}
	result := gate.deny with input as input_override
	count(_msgs(result, "G-OPS-06/C-25c")) > 0
}

# ================================================================
# C-25d (MUST) — Uebergabeartefakte nach Art. 25 Abs. 2 / Abs. 4 n.F.
# ================================================================

test_fail_c25d_trigger_without_handover_artifacts if {
	# Ausloeser gefeuert, aber keines der drei Artefakte vorhanden
	result := gate.deny with input as fixtures.art25_trigger_without_handover
	count(_msgs(result, "G-OPS-06/C-25d")) == 3
}

test_fail_c25d_names_all_three_artifacts if {
	result := gate.deny with input as fixtures.art25_trigger_without_handover
	msgs := _msgs(result, "G-OPS-06/C-25d")
	count({m | some m in msgs; contains(m, "provider_handover_record")}) == 1
	count({m | some m in msgs; contains(m, "written_agreement_ref")}) == 1
	count({m | some m in msgs; contains(m, "cooperation_commitment_ref")}) == 1
}

# ================================================================
# C-25d Carve-out — Art. 25 Abs. 2 letzter Satz n.F.
# (Befund ueber SPEC-03 hinaus, siehe Kopfkommentar der Policy)
# ================================================================

test_pass_c25d_carve_out_lifts_handover_duty if {
	# Urspruenglicher Anbieter hat die Hochrisiko-Umwandlung klar
	# ausgeschlossen UND es belegt -> keine Uebergabepflicht
	ce := fixtures.art25_trigger_without_handover.change_event
	input_override := {"change_event": object.union(ce, {"evidence": object.union(
		ce.evidence,
		{
			"initial_provider_excluded_high_risk_conversion": true,
			"initial_provider_exclusion_ref": "evidence://contracts/exclusion-2026-0043",
		},
	)})}
	result := gate.deny with input as input_override
	count(_msgs(result, "G-OPS-06/C-25d")) == 0
}

test_warn_c25d_carve_out_claimed_without_evidence if {
	# Carve-out behauptet, aber nicht belegt -> Pflicht bleibt, plus warn
	ce := fixtures.art25_trigger_without_handover.change_event
	input_override := {"change_event": object.union(ce, {"evidence": object.union(
		ce.evidence,
		{"initial_provider_excluded_high_risk_conversion": true},
	)})}
	deny_result := gate.deny with input as input_override
	warn_result := gate.warn with input as input_override
	count(_msgs(deny_result, "G-OPS-06/C-25d")) == 3
	count(_msgs(warn_result, "G-OPS-06/C-25d")) > 0
}
