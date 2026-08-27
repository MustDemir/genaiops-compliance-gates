# ================================================================
# G-OPS-02 incident thresholds — UNIT TESTS
# ================================================================
package genaiops.operations.incident_thresholds_test

import rego.v1

import data.genaiops.operations.incident_thresholds as thr

_valid := {
	"deployer_context": {
		"sector": "Elektrizitaet",
		"ai_act_scope_reduced_to": "Art. 3 Abs. 49 lit. c — Grundrechte",
	},
	"deadlines": [
		{"id": "F-CRIT", "hours": 48, "basis": "Art. 73 Abs. 3 AI Act"},
		{"id": "F-DEATH", "hours": 240, "basis": "Art. 73 Abs. 4 AI Act"},
		{"id": "F-STD", "hours": 360, "basis": "Art. 73 Abs. 2 AI Act"},
	],
	"thresholds": [{
		"id": "T-1",
		"applies_to_arm": "Art. 3(49)(c)",
		"status": "set",
	}],
	"evidence_preservation": {"required_before_rollback": true},
}

test_pass_complete_document if {
	count(thr.violation) == 0 with input as _valid
	count(thr.warn) == 0 with input as _valid
}

# ── C-04: the statute is the one thing that can be objectively wrong ──

test_fail_deadline_longer_than_statute if {
	doc := json.patch(_valid, [{"op": "replace", "path": "/deadlines/0/hours", "value": 72}])
	some msg in thr.violation with input as doc
	contains(msg.msg, "C-04")
}

test_fail_deadline_shorter_is_also_wrong if {
	# Not "at least as strict" — the document must state the law, not a
	# house rule. A stricter number here would misrepresent the statute.
	doc := json.patch(_valid, [{"op": "replace", "path": "/deadlines/0/hours", "value": 24}])
	count(thr.violation) > 0 with input as doc
}

test_fail_statutory_deadline_missing if {
	doc := json.patch(_valid, [{"op": "remove", "path": "/deadlines/0"}])
	some msg in thr.violation with input as doc
	contains(msg.msg, "not declared")
}

test_fail_deadline_without_legal_basis if {
	doc := json.patch(_valid, [{"op": "remove", "path": "/deadlines/0/basis"}])
	count(thr.violation) > 0 with input as doc
}

# ── C-03: an open threshold is honest, an undocumented one is not ──

test_warn_unset_threshold_does_not_block if {
	doc := json.patch(_valid, [
		{"op": "replace", "path": "/thresholds/0/status", "value": "unset"},
		{"op": "add", "path": "/thresholds/0/unset_reason", "value": "requires a legal reading, not a measurement"},
	])
	count(thr.warn) > 0 with input as doc
	count(thr.violation) == 0 with input as doc
}

test_fail_unset_without_reason if {
	doc := json.patch(_valid, [{"op": "replace", "path": "/thresholds/0/status", "value": "unset"}])
	some msg in thr.violation with input as doc
	contains(msg.msg, "indistinguishable from an overlooked one")
}

test_fail_threshold_without_arm if {
	doc := json.patch(_valid, [{"op": "remove", "path": "/thresholds/0/applies_to_arm"}])
	count(thr.violation) > 0 with input as doc
}

# ── C-02: scope decides which arms apply at all ──

test_fail_no_scope_reduction_stated if {
	doc := json.patch(_valid, [{"op": "remove", "path": "/deployer_context/ai_act_scope_reduced_to"}])
	some msg in thr.violation with input as doc
	contains(msg.msg, "C-02")
}

test_fail_no_thresholds_at_all if {
	doc := json.patch(_valid, [{"op": "replace", "path": "/thresholds", "value": []}])
	count(thr.violation) > 0 with input as doc
}

# ── C-05: rollback can destroy the record of what happened ──

test_warn_silent_on_evidence_preservation if {
	doc := json.patch(_valid, [{"op": "remove", "path": "/evidence_preservation"}])
	some msg in thr.warn with input as doc
	contains(msg, "C-05")
}

test_warn_preservation_not_required if {
	doc := json.patch(_valid, [{"op": "replace", "path": "/evidence_preservation/required_before_rollback", "value": false}])
	count(thr.warn) > 0 with input as doc
}
