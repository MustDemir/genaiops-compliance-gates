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
#
# ----------------------------------------------------------------
# Art.-6-Pruefbaum "Sicherheitskomponente" (SPEC-02, ab 2026-08-14)
# ----------------------------------------------------------------
# Zusaetzlich zu den Regeln 1-7 oben bildet diese Datei den Pruefbaum
# nach Art. 3 Nr. 14 und Art. 6 Abs. 1a/1b i.d.F. der VO (EU) 2026/1744
# (Digital Omnibus on AI, in Kraft seit 27.07.2026) ab. Checks C-A1..C-A7.
#
# Rechtsstand (primaerquellenverifiziert gegen EUR-Lex, engl. Fassung):
#
#   Art. 3 Nr. 14 n.F. — zwei ODER-verknuepfte Arme:
#     Arm A (Zweckbestimmung): bestimmungsgemaesser Zweck ist es, Risiken
#            fuer Gesundheit und Sicherheit von Personen ODER SACHEN zu
#            verhindern oder zu mindern.
#     Arm B (Ausfallfolge): Ausfall oder Fehlfunktion gefaehrdet Gesundheit
#            und Sicherheit von Personen ODER SACHEN.
#     Nicht verkuerzen: geschuetzt sind Personen ODER Sachen. Betriebsmittel
#     eines Netzes sind Sachen.
#
#   Art. 6 Abs. 1a n.F.: Systeme, die AUSSCHLIESSLICH nicht-sicherheits-
#     bezogene Aspekte von Nutzerunterstuetzung, Leistungsoptimierung,
#     Serviceeffizienz, Automatisierung, Komfort oder Qualitaetskontrolle
#     erfuellen, gelten NICHT als Sicherheitskomponente.
#   Art. 6 Abs. 1b n.F.: Ungeachtet Abs. 1a gelten Systeme, deren Ausfall
#     oder Fehlfunktion Gesundheit und Sicherheit gefaehrden wuerde, DOCH
#     als Sicherheitskomponente.
#
# ***** AUSLEGUNGSHYPOTHESE — KEINE LEITLINIEN, KEINE RECHTSPRECHUNG *****
# Zu Art. 6 Abs. 1a/1b liegen weder Leitlinien der Kommission noch
# Rechtsprechung vor. Die hier implementierte Auslegung ist eine begruendete
# Hypothese und ausdruecklich als solche zu kennzeichnen:
#   Abs. 1a verengt Arm A. Abs. 1b schuetzt Arm B vor dieser Verengung.
#   Folge: ARM B IST DER DOMINANTE TEST. Wer sich auf "das ist doch nur
#   Optimierung" beruft, muss zusaetzlich zeigen, dass die Ausfallfolge
#   unkritisch ist.
# Daraus folgt die zentrale Umsetzungsanforderung: Schritt 4 des Pruefbaums
# ist NICHT ueberspringbar, wenn Abs. 1a geltend gemacht wurde (Check C-A3).
# ************************************************************************
#
# Weitere Einschraenkungen:
#   - Nur die ENGLISCHE Sprachfassung wurde geprueft. Die deutsche Fassung
#     gilt gleichermassen verbindlich; bei "safety function", "intended
#     purpose" und "endangers" koennen Nuancen abweichen. Vor einer
#     Veroeffentlichung abzugleichen.
#   - Art. 6 Abs. 1c ist BEWUSST NICHT umgesetzt: er verweist ausdruecklich
#     auf "the condition in paragraph 1, point (b)" und ist damit auf den
#     Annex-I-Pfad beschraenkt. Abs. 1a und 1b sind dagegen allgemein
#     formuliert und gelten auch fuer Annex III Nr. 2.
#
# UMSETZUNGSENTSCHEIDUNG (nicht aus SPEC-02, hier dokumentiert):
#   Der gesamte C-A-Block ist auf Systeme beschraenkt, die sich als
#   Annex-III-Nr.-2-Kandidat deklarieren (system.annex_iii_candidate ==
#   "no2_critical_infrastructure"). Ohne diese Beschraenkung wuerde C-A1
#   jedes Dokumentationsmanifest ausserhalb der kritischen Infrastruktur
#   blockieren (z. B. das Healthcare-Szenario nach Annex III Nr. 5a), was
#   weder von Art. 6 noch von SPEC-02 gedeckt ist — der Pruefbaum haengt
#   ausweislich Abschnitt 1 der SPEC vollstaendig an Annex III Nr. 2.
#
# Eingabestruktur: siehe SPEC-02 Abschnitt 4 (Block art6_assessment).
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

# --- Rule 7: Manual review evidence must be documented (HYBRID manual part) ---
# G-PRE-01 is HYBRID: Conftest validates structure, human reviews substance.
# These rules check that the MANUAL review step has been documented.

deny contains msg if {
	not input.manual_review
	msg := "G-PRE-01 (R001): manual_review section missing — human review evidence required (HYBRID gate)"
}

deny contains msg if {
	input.manual_review
	not input.manual_review.reviewed_by
	msg := "G-PRE-01 (R001): manual_review.reviewed_by is missing — reviewer identity required"
}

deny contains msg if {
	input.manual_review.reviewed_by == ""
	msg := "G-PRE-01 (R001): manual_review.reviewed_by is empty — reviewer identity required for audit trail"
}

deny contains msg if {
	input.manual_review
	not input.manual_review.review_date
	msg := "G-PRE-01 (R001): manual_review.review_date is missing — review timestamp required"
}

deny contains msg if {
	input.manual_review.review_date == ""
	msg := "G-PRE-01 (R001): manual_review.review_date is empty — review timestamp required for audit trail"
}

# ================================================================
# Art.-6-Pruefbaum: Sicherheitskomponente nach Art. 3 Nr. 14,
# Art. 6 Abs. 1a/1b, Anhang III Nr. 2 (SPEC-02)
# ================================================================

# Zulaessige Werte woertlich aus Anhang III Nr. 2
_valid_deployment_contexts := {
	"critical_digital_infrastructure",
	"road_traffic",
	"water_supply",
	"gas_supply",
	"heating_supply",
	"electricity_supply_operation",
}

# Zulaessige Werte woertlich aus Art. 6 Abs. 1a
_valid_sole_use_categories := {
	"user_assistance",
	"performance_optimisation",
	"service_efficiency",
	"automation",
	"convenience",
	"quality_control",
}

_a6 := input.art6_assessment

# Das System deklariert sich als Annex-III-Nr.-2-Kandidat.
# Gate-Bedingung fuer den gesamten C-A-Block (siehe Kopfkommentar).
_is_no2_candidate if input.system.annex_iii_candidate == "no2_critical_infrastructure"

# Schritt 1 des Pruefbaums: Einsatz in einem der Kontexte aus Anhang III Nr. 2
_in_scope if {
	_is_no2_candidate
	input.system.deployment_context in _valid_deployment_contexts
}

# Arm A — Zweckbestimmung (Personen ODER Sachen)
_arm_a_positive if {
	_a6.arm_a_intended_purpose.prevents_or_mitigates_risk_to_health_safety_or_property == true
}

# Arm B — Ausfallfolge (Personen ODER Sachen)
_arm_b_positive if {
	_a6.arm_b_failure_impact.endangers_health_safety_persons_or_property == true
}

# Art. 6 Abs. 1a wurde geltend gemacht
_exclusion_claimed if _a6.art6_1a_exclusion_claimed.claimed == true

# ----------------------------------------------------------------
# classification — berechnetes Ergebnis des Pruefbaums.
# Kein deny/warn; gehoert in den Evidence-Record.
#
# 1. nicht in Anhang III Nr. 2      -> NOT_IN_SCOPE
# 2. Arm A bejaht                    -> SAFETY_COMPONENT
# 3. Abs. 1a geltend gemacht         -> vorlaeufig kein Safety Component,
#                                       ABER Schritt 4 zwingend (C-A3)
# 4. Arm B bejaht                    -> SAFETY_COMPONENT (ueberschreibt 3)
#    sonst                           -> NO_SAFETY_COMPONENT
# ----------------------------------------------------------------
default classification := "NO_SAFETY_COMPONENT"

classification := "NOT_IN_SCOPE" if not _in_scope

classification := "SAFETY_COMPONENT" if {
	_in_scope
	_arm_a_positive
}

classification := "SAFETY_COMPONENT" if {
	_in_scope
	not _arm_a_positive
	_arm_b_positive
}

# ----------------------------------------------------------------
# C-A1 (MUST) — art6_assessment fehlt vollstaendig
# ----------------------------------------------------------------
deny contains msg if {
	_is_no2_candidate
	not input.art6_assessment
	msg := "G-PRE-01/C-A1 (R001, Art. 3 Nr. 14): art6_assessment section is missing — Annex III No. 2 candidates must document the safety-component assessment"
}

# ----------------------------------------------------------------
# C-A2 (MUST) — deployment_context fehlt oder unzulaessig
# ----------------------------------------------------------------
deny contains msg if {
	_is_no2_candidate
	not input.system.deployment_context
	msg := "G-PRE-01/C-A2 (R001, Anhang III Nr. 2): system.deployment_context is missing despite annex_iii_candidate == 'no2_critical_infrastructure'"
}

deny contains msg if {
	_is_no2_candidate
	ctx := input.system.deployment_context
	not ctx in _valid_deployment_contexts
	msg := sprintf("G-PRE-01/C-A2 (R001, Anhang III Nr. 2): invalid deployment_context '%s' — must be one of: critical_digital_infrastructure, road_traffic, water_supply, gas_supply, heating_supply, electricity_supply_operation", [ctx])
}

# ----------------------------------------------------------------
# C-A3 (MUST) — DER KERN: Schritt 4 ist nicht ueberspringbar.
# Abs. 1a geltend gemacht, aber Arm B nicht bewertet.
# Auslegung: Abs. 1b schuetzt Arm B vor der Verengung durch Abs. 1a,
# also darf sich niemand auf "nur Optimierung" berufen, ohne die
# Ausfallfolge geprueft zu haben. Wichtigster Check dieser SPEC.
# ----------------------------------------------------------------
deny contains msg if {
	_is_no2_candidate
	_exclusion_claimed
	not _a6.arm_b_failure_impact.assessed == true
	msg := "G-PRE-01/C-A3 (R001, Art. 6 Abs. 1b): art6_1a exclusion claimed but arm_b_failure_impact.assessed is not true — the failure-impact test (Art. 6 Abs. 1b) cannot be skipped when the Abs. 1a exclusion is invoked"
}

# ----------------------------------------------------------------
# C-A4 (MUST) — Abs. 1a geltend gemacht, aber sole_use_categories
# leer oder mit unzulaessigen Werten
# ----------------------------------------------------------------
deny contains msg if {
	_is_no2_candidate
	_exclusion_claimed
	not _a6.art6_1a_exclusion_claimed.sole_use_categories
	msg := "G-PRE-01/C-A4 (R001, Art. 6 Abs. 1a): art6_1a exclusion claimed but sole_use_categories is missing — the exclusion must name the categories relied upon"
}

deny contains msg if {
	_is_no2_candidate
	_exclusion_claimed
	count(_a6.art6_1a_exclusion_claimed.sole_use_categories) == 0
	msg := "G-PRE-01/C-A4 (R001, Art. 6 Abs. 1a): sole_use_categories is empty — at least one Art. 6 Abs. 1a category required"
}

deny contains msg if {
	_is_no2_candidate
	_exclusion_claimed
	some cat in _a6.art6_1a_exclusion_claimed.sole_use_categories
	not cat in _valid_sole_use_categories
	msg := sprintf("G-PRE-01/C-A4 (R001, Art. 6 Abs. 1a): invalid sole_use_category '%s' — must be one of: user_assistance, performance_optimisation, service_efficiency, automation, convenience, quality_control", [cat])
}

# ----------------------------------------------------------------
# C-A5 (MUST) — Arm A oder Arm B bejaht, aber justification fehlt
# ----------------------------------------------------------------
deny contains msg if {
	_is_no2_candidate
	_arm_a_positive
	not _a6.arm_a_intended_purpose.justification
	msg := "G-PRE-01/C-A5 (R001, Art. 3 Nr. 14): arm_a_intended_purpose answered true but justification is missing"
}

deny contains msg if {
	_is_no2_candidate
	_arm_a_positive
	_a6.arm_a_intended_purpose.justification == ""
	msg := "G-PRE-01/C-A5 (R001, Art. 3 Nr. 14): arm_a_intended_purpose.justification is empty — substantive reasoning required"
}

deny contains msg if {
	_is_no2_candidate
	_arm_b_positive
	not _a6.arm_b_failure_impact.justification
	msg := "G-PRE-01/C-A5 (R001, Art. 3 Nr. 14): arm_b_failure_impact answered true but justification is missing"
}

deny contains msg if {
	_is_no2_candidate
	_arm_b_positive
	_a6.arm_b_failure_impact.justification == ""
	msg := "G-PRE-01/C-A5 (R001, Art. 3 Nr. 14): arm_b_failure_impact.justification is empty — substantive reasoning required"
}

# ----------------------------------------------------------------
# C-A6 (MUST) — Selbsteinstufung NO_SAFETY_COMPONENT trotz bejahter
# Ausfallgefaehrdung. Art. 6 Abs. 1b ueberschreibt.
#
# Hinweis zur Eingabestruktur: SPEC-02 Abschnitt 4 fuehrt kein Feld
# fuer die Selbsteinstufung. Da C-A6 laut Abschnitt 5 aber genau gegen
# eine "Selbsteinstufung als NO_SAFETY_COMPONENT" prueft — und die
# berechnete classification bei bejahtem Arm B nie NO_SAFETY_COMPONENT
# ergeben kann, die Regel dort also tot waere — wird das Feld
# art6_assessment.self_declared_classification eingefuehrt.
# ----------------------------------------------------------------
deny contains msg if {
	_is_no2_candidate
	_a6.self_declared_classification == "NO_SAFETY_COMPONENT"
	_arm_b_positive
	msg := "G-PRE-01/C-A6 (R001, Art. 6 Abs. 1b): self_declared_classification is NO_SAFETY_COMPONENT although arm_b_failure_impact endangers health/safety of persons or property — Art. 6 Abs. 1b overrides the Abs. 1a exclusion"
}

# ----------------------------------------------------------------
# C-A7 (SHOULD, warn) — menschliche Kontrolle zwischen Ausgabe und
# Wirkung behauptet, aber kein Wirksamkeitsnachweis referenziert.
#
# Der inhaltlich interessante Check: Bei Systemen, deren Ausgabe erst
# ueber eine menschliche Entscheidung wirksam wird, entscheidet ueber
# Arm B, ob eine WIRKSAME Kontrolle dazwischensteht. Damit haengt die
# Einstufung nach Art. 6 an der Aufsichtsqualitaet nach Art. 26 Abs. 2:
# Wer sich als "kein Hochrisiko" einstuft, WEIL ein Mensch dazwischen-
# steht, schuldet den Nachweis, dass diese Aufsicht wirksam ist.
# Ziel der Verknuepfung ist G-OPS-01 (Causal Power, Epistemic Access,
# Self-Control, Fitting Intentions).
#
# Severity bewusst SHOULD, nicht MUST: der Verweis kann zum Zeitpunkt
# der Pre-Deployment-Klassifikation noch nicht aufloesbar sein, weil
# G-OPS-01 in der Operations-Phase laeuft. Verschaerfung auf MUST ist
# eine Folge-Iteration, sobald die Reihenfolge geklaert ist.
# ----------------------------------------------------------------
warn contains msg if {
	_is_no2_candidate
	_a6.arm_b_failure_impact.human_control_between_output_and_action == true
	not _a6.arm_b_failure_impact.human_control_effectiveness_evidence_ref
	msg := "G-PRE-01/C-A7 (R001, Art. 26 Abs. 2): human_control_between_output_and_action claimed but human_control_effectiveness_evidence_ref is missing — effectiveness of the oversight must be evidenced (target: G-OPS-01) [SHOULD]"
}

warn contains msg if {
	_is_no2_candidate
	_a6.arm_b_failure_impact.human_control_between_output_and_action == true
	_a6.arm_b_failure_impact.human_control_effectiveness_evidence_ref == ""
	msg := "G-PRE-01/C-A7 (R001, Art. 26 Abs. 2): human_control_effectiveness_evidence_ref is empty — a resolvable reference to the oversight-effectiveness evidence is required (target: G-OPS-01) [SHOULD]"
}
