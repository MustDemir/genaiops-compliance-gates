# ================================================================
# G-OPS-06: Rollenwechsel-Monitoring (Betreiber-zu-Anbieter-Aufstieg)
# ================================================================
# Gate:        G-OPS-06 (Rollenwechsel)
# Requirement: R001 (Risikomanagement-Anschluss) — EU AI Act Art. 25
# Automation:  HYBRID (Conftest prueft Tatbestand + Uebergabeartefakte,
#              Compliance-Officer bewertet die Wesentlichkeit)
# Input:       change_event manifest (siehe Fixtures art25_*.json)
# Entrypoint:  deny[msg] (MUST) / warn[msg] (SHOULD), Conftest-Konvention
#
# Richtung: Art. 25 regelt den Aufstieg Betreiber/Haendler/Einfuehrer/
# Dritter -> ANBIETER (nicht umgekehrt). Beobachtet wird er hier vom
# Betreiber aus, daher role_scope ["deployer"].
#
# ----------------------------------------------------------------
# Severity je Tatbestand (SPEC-03 Abschnitt 5.1)
# ----------------------------------------------------------------
# Die fruehere Skizze in prospective/art25-role-change/ fuehrte ALLE
# drei Ausloesetatbestaende einheitlich als `warn` mit der Begruendung,
# die Art.-97-Schwellenwerte fehlten. Das trifft aber nur auf lit. b zu:
#
#   C-25a  Art. 25 Abs. 1 lit. a  MUST    binaerer Tatbestand (Rebranding)
#   C-25b  Art. 25 Abs. 1 lit. b  SHOULD  Schwellenwert haengt an Art. 3
#                                         Nr. 23 und den delegierten
#                                         Rechtsakten nach Art. 97
#   C-25c  Art. 25 Abs. 1 lit. c  MUST    binaer; stuetzt sich auf die
#                                         Art.-6-Klassifikation (SPEC-02)
#   C-25d  Art. 25 Abs. 2/4 n.F.  MUST    Uebergabeartefakte fehlen
#
# ----------------------------------------------------------------
# Rechtsstand (primaerquellenverifiziert gegen EUR-Lex, engl. Fassung,
# VO (EU) 2026/1744 Aenderungspunkt (12))
# ----------------------------------------------------------------
# Art. 25 Abs. 2 n.F.: Der urspruengliche Anbieter "shall no longer be
#   considered to be a provider of that specific AI system", muss aber
#   eng mit den neuen Anbietern zusammenarbeiten und die erforderlichen
#   Informationen sowie den vernuenftigerweise zu erwartenden technischen
#   Zugang bereitstellen. Konkretisiert auf drei Positionen:
#     (a) technische Dokumentation, ausreichend zur Beurteilung der
#         Konformitaet mit Art. 16,
#     (b) Information ueber bekannte Grenzen und Fehlermodi,
#     (c) gezielter technischer Zugang, auch fuer Test und Validierung.
# Art. 25 Abs. 4 UAbs. 1 n.F.: Anbieter und Drittzulieferer legen die
#   erforderlichen Informationen, Faehigkeiten und technischen Zugaenge
#   DURCH SCHRIFTLICHE VEREINBARUNG fest.
#
# Der Rollenuebergang ist damit ein zweiseitiger, dokumentierter Vorgang,
# kein einseitiger Statuswechsel.
#
# ----------------------------------------------------------------
# ABGRENZUNG — wen Art. 25 Abs. 2/4 traegt, und wen nicht
# ----------------------------------------------------------------
# Art. 25 Abs. 2 n.F. verpflichtet den ERSTANBIETER gegenueber den NEUEN
# ANBIETERN; der Anspruch entsteht erst NACH einem Rollenuebergang.
# Art. 25 Abs. 4 n.F. regelt Anbieter <-> Drittzulieferer; der Betreiber
# ist dort nicht Partei.
#
# Fuer den REINEN Betreiber — also die Lieferantenpruefung ohne jeden
# Rollenwechsel — tragen diese Absaetze daher NICHT. Wer Lieferanten-
# nachweise im Regelfall pruefen will, muss das ueber Art. 13 und
# Art. 26 Abs. 1/5/6/9 begruenden (Vollstaendigkeit der Betriebsanleitung),
# nicht ueber Art. 25.
#
# DIESES GATE IST DAVON NICHT BETROFFEN: C-25d feuert ausschliesslich,
# nachdem ein bindender Ausloeser (C-25a oder C-25c) gegriffen hat — also
# nachdem der Rollenuebergang stattgefunden hat und der Betreiber selbst
# zum neuen Anbieter geworden ist. Genau dann ist er Anspruchsberechtigter
# nach Abs. 2. Die Verankerung ist korrekt; bitte nicht "wegkorrigieren".
#
# NICHT hier zu pruefen: die technische Dokumentation nach Art. 11 /
# Anhang IV. Sie ist Anbieterpflicht GEGENUEBER BEHOERDEN, kein Anspruch
# des Betreibers. Ein Check, der sie vom Betreiber verlangt, pruefte eine
# Pflicht, die es nicht gibt.
#
# ***** BEFUND UEBER SPEC-03 HINAUS — CARVE-OUT IN ART. 25 ABS. 2 *****
# Der letzte Satz des neuen Abs. 2 lautet sinngemaess: der Absatz gilt
# NICHT, wenn der urspruengliche Anbieter klar festgelegt hat, dass sein
# System nicht in ein Hochrisiko-System umgewandelt werden soll — dann
# trifft ihn weder die Kooperations- noch die Uebergabepflicht.
# SPEC-03 Abschnitt 5.3 erwaehnt diesen Carve-out nicht. C-25d wuerde
# ohne ihn Uebergabeartefakte einfordern, die rechtlich gar nicht
# geschuldet sind. Er ist daher als Ausnahme implementiert und muss
# im Manifest ausdruecklich belegt werden.
#
# GRENZE DIESES GATES (bewusst, nicht behebbar durch mehr Rego):
# Der Anbieter kann sich die Kooperationspflicht EINSEITIG UND VORAB
# wegbedingen. Die wirksame Pruefung liegt damit VOR VERTRAGSSCHLUSS,
# nicht in der Deployment-Pipeline. Dieses Gate meldet den fehlenden
# Uebergabeanspruch erst beim Rollout — also zu spaet, um ihn noch zu
# verhandeln. Es bleibt als Nachweis- und Eskalationspunkt sinnvoll,
# ersetzt aber keine Beschaffungspruefung.
# ********************************************************************
# ================================================================

package genaiops.operations.role_change_monitoring

import rego.v1

_ce := input.change_event

# ----------------------------------------------------------------
# C-25a (MUST) — Art. 25 Abs. 1 lit. a: Rebranding
# Binaerer Tatbestand: eigener Name oder eigene Marke auf einem bereits
# in Verkehr gebrachten Hochrisiko-System. Kein Schwellenwertproblem.
# ----------------------------------------------------------------
_trigger_a if {
	_ce.system_already_on_market == true
	_ce.rebranding.own_name_or_trademark_applied == true
}

deny contains msg if {
	_trigger_a
	msg := "G-OPS-06/C-25a (R001, Art. 25 Abs. 1 lit. a): own name or trademark applied to a high-risk AI system already placed on the market — the deployer becomes a provider of that system"
}

# ----------------------------------------------------------------
# C-25b (SHOULD, warn) — Art. 25 Abs. 1 lit. b: wesentliche Veraenderung
# Hier — und nur hier — greift die urspruengliche Begruendung: die
# Wesentlichkeitsschwelle haengt an Art. 3 Nr. 23 und den delegierten
# Rechtsakten nach Art. 97, die noch ausstehen. Daher advisory.
# ----------------------------------------------------------------
_trigger_b if {
	_ce.substantial_modification.modified == true
	_ce.substantial_modification.remains_high_risk_art6 == true
}

warn contains msg if {
	_trigger_b
	msg := "G-OPS-06/C-25b (R001, Art. 25 Abs. 1 lit. b): substantial modification of a high-risk AI system that remains high-risk — provider status likely; substantiality threshold still depends on the Art. 97 delegated acts, therefore advisory [SHOULD]"
}

# ----------------------------------------------------------------
# C-25c (MUST) — Art. 25 Abs. 1 lit. c: Zweckaenderung zu Hochrisiko
#
# Ausgewertet wird NICHT ein Manifest-Boolean, sondern die
# classification-Regel aus SPEC-02 (G-PRE-01), einmal auf den Zustand
# VOR und einmal auf den Zustand NACH der Zweckaenderung angewandt.
# Das Manifest liefert damit die Zweckangaben, nicht das Ergebnis —
# eine Selbstauskunft "wird nicht hochriskant" kann den Check nicht
# mehr aushebeln.
# ----------------------------------------------------------------
_classification_before := c if {
	c := data.genaiops.pre_deployment.risk_classification.classification with input as _ce.purpose_change.before
}

_classification_after := c if {
	c := data.genaiops.pre_deployment.risk_classification.classification with input as _ce.purpose_change.after
}

_trigger_c if {
	_ce.purpose_change.changed == true
	_classification_before in {"NO_SAFETY_COMPONENT", "NOT_IN_SCOPE"}
	_classification_after == "SAFETY_COMPONENT"
}

deny contains msg if {
	_trigger_c
	msg := sprintf("G-OPS-06/C-25c (R001, Art. 25 Abs. 1 lit. c): purpose change moves the Art. 6 classification from '%s' to 'SAFETY_COMPONENT' — the system becomes high-risk and the deployer becomes its provider", [_classification_before])
}

# Ein als Zweckaenderung deklariertes Ereignis muss die Zweckangaben
# vor UND nach der Aenderung mitliefern, sonst ist C-25c nicht auswertbar.
deny contains msg if {
	_ce.purpose_change.changed == true
	not _ce.purpose_change.before
	msg := "G-OPS-06/C-25c (R001, Art. 25 Abs. 1 lit. c): purpose_change.before is missing — the Art. 6 classification cannot be evaluated before/after without it"
}

deny contains msg if {
	_ce.purpose_change.changed == true
	not _ce.purpose_change.after
	msg := "G-OPS-06/C-25c (R001, Art. 25 Abs. 1 lit. c): purpose_change.after is missing — the Art. 6 classification cannot be evaluated before/after without it"
}

# ----------------------------------------------------------------
# C-25d (MUST) — Art. 25 Abs. 2 und Abs. 4 UAbs. 1 n.F.:
# Uebergabeartefakte. Der Uebergang ist ohne sie nicht wirksam
# dokumentiert.
#
# Ausnahme (Carve-out aus Art. 25 Abs. 2 letzter Satz, siehe Kopf):
# Hat der urspruengliche Anbieter klar festgelegt, dass sein System
# nicht in ein Hochrisiko-System umgewandelt werden soll, entfaellt
# die Kooperations- und Uebergabepflicht. Der Carve-out muss im
# Manifest belegt sein (Verweis auf die Festlegung), sonst greift er
# nicht — eine blosse Behauptung genuegt nicht.
# ----------------------------------------------------------------
_binding_trigger_fired if _trigger_a

_binding_trigger_fired if _trigger_c

_carve_out_applies if {
	_ce.evidence.initial_provider_excluded_high_risk_conversion == true
	ref := _ce.evidence.initial_provider_exclusion_ref
	ref != ""
}

deny contains msg if {
	_binding_trigger_fired
	not _carve_out_applies
	not _ce.evidence.provider_handover_record
	msg := "G-OPS-06/C-25d (R001, Art. 25 Abs. 2): a role-change trigger fired but provider_handover_record is missing — the initial provider owes technical documentation (Art. 16), known limitations and failure modes, and targeted technical access"
}

deny contains msg if {
	_binding_trigger_fired
	not _carve_out_applies
	not _ce.evidence.written_agreement_ref
	msg := "G-OPS-06/C-25d (R001, Art. 25 Abs. 4 UAbs. 1): a role-change trigger fired but written_agreement_ref is missing — the necessary information, capabilities and technical access must be specified BY WRITTEN AGREEMENT"
}

deny contains msg if {
	_binding_trigger_fired
	not _carve_out_applies
	not _ce.evidence.cooperation_commitment_ref
	msg := "G-OPS-06/C-25d (R001, Art. 25 Abs. 2): a role-change trigger fired but cooperation_commitment_ref is missing — the initial provider must commit to close cooperation with the new provider"
}

# Der Carve-out wird behauptet, aber nicht belegt.
warn contains msg if {
	_binding_trigger_fired
	_ce.evidence.initial_provider_excluded_high_risk_conversion == true
	not _carve_out_applies
	msg := "G-OPS-06/C-25d (R001, Art. 25 Abs. 2): the Art. 25(2) carve-out is claimed but initial_provider_exclusion_ref is missing or empty — an unevidenced claim does not lift the handover duty [SHOULD]"
}
