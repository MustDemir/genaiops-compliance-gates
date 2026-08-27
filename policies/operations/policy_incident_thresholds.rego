# ================================================================
# G-OPS-02: Incident thresholds are declared, anchored and current
# ================================================================
# Gate:        G-OPS-02 (Incident Reporting)
# Requirement: R009 — EU AI Act Art. 26 Abs. 5, Art. 73
# Input:       governance/incident_thresholds.yaml (as JSON)
# Entrypoint:  violation / warn
#
# WHY THIS EXISTS
#
# Until 2026-08-27 this gate checked three pod annotations at
# admission: an incident process is "configured", a contact is named,
# a rollback mechanism "exists". All three are E-0 — someone wrote
# them. Nothing said WHEN an incident is reportable, and nothing knew
# the deadlines.
#
# The Commission's draft guidance on Article 73 (26 September 2025)
# changed what this gate should ask. For Annex III No. 2 systems —
# electricity among them — already covered by CER and NIS2, Article
# 73(9) reduces the AI Act reporting duty to Article 3(49)(c):
# fundamental rights. Operational disruption keeps flowing through
# CER and NIS2.
#
# So for this deployer the question is not "above which error rate"
# but "when does a load-shedding decision become discrimination" —
# and the Commission uses exactly that as its example (recital 58).
#
# WHAT THIS CHECKS, AND WHAT IT DELIBERATELY DOES NOT
#
# It checks that the decision has been WRITTEN DOWN, anchored to law,
# and kept consistent with the statutory deadlines. It does not check
# that a threshold is correct — that is a professional judgement, and
# a policy asserting it would be the same overreach the artefact was
# built to expose.
#
# An `unset` threshold is a legitimate, honest state and produces a
# WARNING, not a denial. An invented number would be worse than an
# open one.
# ================================================================
package genaiops.operations.incident_thresholds

import rego.v1

_doc := input

# Statutory deadlines in hours. These are LAW, not judgement: Art. 73
# (2)-(4) as read in the draft guidance, recital 38. A file that
# contradicts them is wrong about the law, which is a denial.
_statutory := {
	"F-CRIT": 48,
	"F-DEATH": 240,
	"F-STD": 360,
}

# ================================================================
# C-02 [MUST] — the decision exists and states its scope
# ================================================================

violation contains {"msg": msg} if {
	not _doc.deployer_context
	msg := "G-OPS-02/C-02 (R009, Art. 73): no deployer_context — the reporting duty depends on which parallel regimes already apply, so a threshold document that does not state them cannot be evaluated"
}

violation contains {"msg": msg} if {
	_doc.deployer_context
	not _doc.deployer_context.ai_act_scope_reduced_to
	msg := "G-OPS-02/C-02 (R009, Art. 73): deployer_context does not state which incident arms the AI Act duty reduces to under Art. 73(9) — for an Annex III No. 2 deployer under CER and NIS2 this is the difference between reporting every outage and reporting fundamental-rights breaches"
}

violation contains {"msg": msg} if {
	count(object.get(_doc, "thresholds", [])) == 0
	msg := "G-OPS-02/C-02 (R009, Art. 73): no thresholds declared at all. The question of when a misclassification becomes a reportable incident is the one this gate exists for; leaving it unwritten is not the same as leaving it open"
}

# ================================================================
# C-03 [SHOULD] — every threshold is either set or honestly open
# ================================================================
# Advisory on purpose. Every threshold is `unset` today, and a MUST
# would block the pipeline over a professional judgement that has not
# been made. The run stays green; the finding stands in the evidence.

warn contains msg if {
	some t in object.get(_doc, "thresholds", [])
	t.status == "unset"
	msg := sprintf("G-OPS-02/C-03 (R009, Art. 73): threshold '%s' is unset — incident detection for this arm cannot trigger. Honest, but it means the gate reports on a duty nobody can yet act on", [t.id])
}

violation contains {"msg": msg} if {
	some t in object.get(_doc, "thresholds", [])
	t.status == "unset"
	not t.unset_reason
	msg := sprintf("G-OPS-02/C-03 (R009, Art. 73): threshold '%s' is unset without a reason — an undocumented gap is indistinguishable from an overlooked one", [t.id])
}

violation contains {"msg": msg} if {
	some t in object.get(_doc, "thresholds", [])
	not t.applies_to_arm
	msg := sprintf("G-OPS-02/C-03 (R009, Art. 73): threshold '%s' names no incident arm of Art. 3(49) — an unanchored threshold cannot be traced to a duty", [t.id])
}

# ================================================================
# C-04 [MUST] — the deadlines match the statute
# ================================================================
# The one place where the document can be objectively wrong. A
# deadline clock built on a mis-stated deadline is worse than none:
# it would report compliance while the statutory window has passed.

violation contains {"msg": msg} if {
	some d in object.get(_doc, "deadlines", [])
	expected := _statutory[d.id]
	d.hours != expected
	msg := sprintf("G-OPS-02/C-04 (R009, Art. 73): deadline '%s' is %v hours, the statute gives %v — a clock built on this would report compliance after the window closed", [d.id, d.hours, expected])
}

violation contains {"msg": msg} if {
	some id, _ in _statutory
	not _declared_deadlines[id]
	msg := sprintf("G-OPS-02/C-04 (R009, Art. 73): statutory deadline '%s' is not declared — the shortest window applying to this deployer is 48h (Art. 73(3), critical infrastructure), and a missing one cannot be measured against", [id])
}

_declared_deadlines[d.id] if some d in object.get(_doc, "deadlines", [])

violation contains {"msg": msg} if {
	some d in object.get(_doc, "deadlines", [])
	not d.basis
	msg := sprintf("G-OPS-02/C-04 (R009, Art. 73): deadline '%s' names no legal basis — a deadline without a citation is a number somebody chose", [d.id])
}

# ================================================================
# C-05 [SHOULD] — evidence preservation before corrective action
# ================================================================
# Recitals 42-43: the provider must not alter the system in a way
# that impairs later root-cause assessment before informing the
# authority. Software updates, configuration changes, overwritten
# training data, disabled monitoring and edited logs all count.
#
# This sits in tension with C-01, which treats
# "rollback-mechanism: true" as a satisfied requirement. A rollback
# after an incident may itself be notifiable.

warn contains msg if {
	not _doc.evidence_preservation
	msg := "G-OPS-02/C-05 (R009, Art. 73): the document is silent on evidence preservation before corrective action (Art. 73(6)) — yet this gate elsewhere accepts a rollback mechanism as evidence of readiness, and a rollback can destroy the record of what happened"
}

warn contains msg if {
	_doc.evidence_preservation
	_doc.evidence_preservation.required_before_rollback != true
	msg := "G-OPS-02/C-05 (R009, Art. 73): evidence preservation is not required before rollback — Art. 73(6) forbids alterations that impair root-cause assessment until the authority has been informed"
}
