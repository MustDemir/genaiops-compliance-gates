# ================================================================
# PROSPEKTIV — Art.-25-Rollenwechsel-Monitoring (F5)
# ================================================================
# NICHT Teil des enforcten 16-Gate-Katalogs. Advisory-only:
# uses `warn` (Conftest: warning, exit 0 — NO blocking), not `deny`,
# because the Art. 25 thresholds await the Art. 97 delegated acts.
#
# Gate:        G-OPS-XX-prospektiv (Rollenwechsel-Monitoring)
# Requirement: R0XX-prospektiv (nicht im 14er-Katalog)
# Direction:   Deployer/distributor/importer/third party -> Provider
# Input:       change_event manifest (see change_event_sample.json)
# ================================================================

package genaiops.prospective.role_change_monitoring

import rego.v1

# --- Trigger (a): Rebranding — own name/trademark on a system already placed ---
warn contains msg if {
	input.change_event.system_already_on_market == true
	input.change_event.rebranding.own_name_or_trademark_applied == true
	msg := "G-OPS-XX (Art. 25 Abs. 1 lit. a, PROSPEKTIV): eigener Name/Marke auf bereits in Verkehr gebrachtem Hochrisiko-System — moeglicher Aufstieg zum Anbieter; Compliance-Officer-Review erforderlich"
}

# --- Trigger (b): Substantial modification, remains high-risk under Art. 6 ---
warn contains msg if {
	input.change_event.substantial_modification.modified == true
	input.change_event.substantial_modification.remains_high_risk_art6 == true
	msg := "G-OPS-XX (Art. 25 Abs. 1 lit. b, PROSPEKTIV): wesentliche Veraenderung eines Hochrisiko-Systems (bleibt Art.-6-Hochrisiko) — moeglicher Aufstieg zum Anbieter; Compliance-Officer-Review erforderlich"
}

# --- Trigger (c): Purpose change turning a non-high-risk system into high-risk ---
warn contains msg if {
	input.change_event.purpose_change.changed == true
	input.change_event.purpose_change.becomes_high_risk_art6 == true
	msg := "G-OPS-XX (Art. 25 Abs. 1 lit. c, PROSPEKTIV): Zweckaenderung macht System zu Art.-6-Hochrisiko — moeglicher Aufstieg zum Anbieter; Compliance-Officer-Review erforderlich"
}
