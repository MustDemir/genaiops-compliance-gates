# ================================================================
# G-OPS-03: Performance-Monitoring und Drift-Detection
# ================================================================
# Gate:       G-OPS-03 (Performance-Monitoring)
# Requirement: R010 — EU AI Act Art. 72, Art. 9 Abs. 2
# Automation:  AUTO (Gatekeeper Admission Controller / Conftest CI)
# Input:       K8s Deployment manifest (Pod template)
# Entrypoint:  violation[{"msg": msg}] (Gatekeeper convention)
#
# Dual-mode: Works with both Gatekeeper (input.review.object.*)
# and Conftest CI (input.spec.*) by resolving the object root.
#
# Checks:
#   1. drift-detection-enabled annotation present and "true"
#   2. service-monitor-configured annotation present and "true"
#   3. Prometheus scrape annotations present
# ================================================================

package genaiops.operations.monitoring_configured

import rego.v1

# Dual-mode: Gatekeeper wraps input in review.object, Conftest passes directly
_object := input.review.object if input.review
_object := input if not input.review

_pod_annotations := _object.spec.template.metadata.annotations

# Discriminator: is this input a workload manifest at all?
#
# Needed since SPEC-04, because this policy now sees two kinds of input:
# a Kubernetes object (annotations, checks 1-3) and a drift measurement
# document (scores, checks C-03..C-05). Without the guard, a measurement
# document trips all three "annotation is missing" rules — `not` over an
# undefined reference is true, so an absent Deployment spec reads exactly
# like a Deployment with its annotations stripped.
#
# The guard is deliberately `spec.template` and not merely "annotations
# are absent": a real Deployment that carries no annotations at all must
# still fail checks 1-3. Only a non-workload input is exempt.
_is_workload if _object.spec.template

# ================================================================
# Check 1: Drift detection must be enabled
# ================================================================

violation contains {"msg": msg} if {
	_is_workload
	not _pod_annotations["genaiops.io/drift-detection-enabled"]
	msg := "G-OPS-03 (R010): annotation genaiops.io/drift-detection-enabled is missing"
}

violation contains {"msg": msg} if {
	_is_workload
	_pod_annotations["genaiops.io/drift-detection-enabled"] != "true"
	msg := sprintf("G-OPS-03 (R010): drift-detection-enabled is '%s' — must be 'true'", [_pod_annotations["genaiops.io/drift-detection-enabled"]])
}

# ================================================================
# Check 2: ServiceMonitor must be configured
# ================================================================

violation contains {"msg": msg} if {
	_is_workload
	not _pod_annotations["genaiops.io/service-monitor-configured"]
	msg := "G-OPS-03 (R010): annotation genaiops.io/service-monitor-configured is missing"
}

violation contains {"msg": msg} if {
	_is_workload
	_pod_annotations["genaiops.io/service-monitor-configured"] != "true"
	msg := sprintf("G-OPS-03 (R010): service-monitor-configured is '%s' — must be 'true'", [_pod_annotations["genaiops.io/service-monitor-configured"]])
}

# ================================================================
# Check 3: Prometheus scrape config present
# ================================================================

violation contains {"msg": msg} if {
	_is_workload
	not _pod_annotations["prometheus.io/scrape"]
	msg := "G-OPS-03 (R010): annotation prometheus.io/scrape is missing — metrics endpoint not discoverable"
}

violation contains {"msg": msg} if {
	_is_workload
	_pod_annotations["prometheus.io/scrape"] != "true"
	msg := "G-OPS-03 (R010): prometheus.io/scrape is not 'true' — metrics scraping disabled"
}

# ================================================================
# SPEC-04 Teil 3.3 — vom Konfigurationsnachweis zum Messnachweis
# ================================================================
# Checks 1-3 above ask "does someone CLAIM that drift detection runs?"
# — three annotations, written by whoever wrote the manifest. That is
# evidence level E-0, and it is exactly the self-declaration attack
# surface the project names in HANDBUCH Teil 10.
#
# The checks below ask "did it run, and what did it say?" — evidence
# level E-3, a property measured over time. Both stay in the gate. The
# contrast between them is the E6 model demonstrated inside a single
# gate (HANDBUCH 7.5 (2b), 7.8).
#
# Input: a drift measurement document produced by
# monitoring/drift_detector.py. The detector MEASURES; it no longer
# decides. Until 2026-08 it wrote its own PASS/FAIL into the Evidence
# Store under this very gate ID, in parallel to the annotation rules
# above — one gate ID, two producers, incompatible logic
# (HANDBUCH 7.5 (2a)). The decision now lives here, and only here.
#
# These rules stay silent unless input.drift_measurement is present, so
# a Gatekeeper admission review (which cannot carry an operating
# measurement — nothing is running yet at admission time) is unaffected.
# Requiring the document to be supplied at all is enforced one level up,
# by the orchestrator, not by absence of a rule here.
# ================================================================

_drift := input.drift_measurement

# Freshness budget in seconds; the document states its own, falling back
# to 15 minutes — three times the CronJob's 5-minute schedule, so a
# single missed run does not trip the gate.
_max_age_seconds := object.get(_drift, "max_age_seconds", 900)

_measured_ns := time.parse_rfc3339_ns(_drift.measured_at)

_age_seconds := (time.now_ns() - _measured_ns) / 1000000000

# ================================================================
# C-03 [MUST] — a measurement exists, and it is recent
# ================================================================
# The more important of the two MUST checks. A gate that only reads the
# value mistakes standstill for stability: drift detection could have
# been crashed for three weeks and the last good PSI would still be
# sitting there, green. The deadline is itself the subject of the check.

violation contains {"msg": msg} if {
	_drift
	not _drift.measured_at
	msg := "G-OPS-03/C-03 (R010, Art. 72): drift measurement carries no measured_at — an undated measurement cannot be shown to be current"
}

violation contains {"msg": msg} if {
	_drift.measured_at
	_age_seconds > _max_age_seconds
	msg := sprintf("G-OPS-03/C-03 (R010, Art. 72): last drift measurement is %.0fs old, budget is %vs — drift detection has stopped reporting, which is not the same as 'no drift'", [_age_seconds, _max_age_seconds])
}

# ================================================================
# C-04 [MUST] — the measured values stay under the thresholds
# ================================================================
# Thresholds from drift-config.yaml (HANDBUCH 7.1): PSI > 0.2 and
# JSD > 0.1 are critical. Warning bands are handled by the detector's
# own exit code; the gate blocks on critical only.

violation contains {"msg": msg} if {
	_drift
	not _drift.psi_score
	msg := "G-OPS-03/C-04 (R010, Art. 72): drift measurement carries no psi_score"
}

violation contains {"msg": msg} if {
	psi := _drift.psi_score
	psi > 0.2
	msg := sprintf("G-OPS-03/C-04 (R010, Art. 72): PSI %.4f exceeds critical threshold 0.2 — input distribution has shifted, gate re-evaluation required", [psi])
}

violation contains {"msg": msg} if {
	jsd := _drift.jsd_score
	jsd > 0.1
	msg := sprintf("G-OPS-03/C-04 (R010, Art. 72): JSD %.4f exceeds critical threshold 0.1 — input distribution has shifted, gate re-evaluation required", [jsd])
}

# ================================================================
# C-05 [SHOULD] — the numbers came from a measurement, not a fixture
# ================================================================
# Advisory on purpose. A fixture-driven walkthrough is a legitimate way
# to run this repository, and blocking it would only teach people to
# switch the gate off. But a walkthrough must not be mistaken for an
# operating record: the run stays green, the finding stands in the
# evidence.

warn contains msg if {
	_drift
	provenance := object.get(_drift, "provenance", "declared")
	provenance != "measured"
	provenance != "derived"
	msg := sprintf("G-OPS-03/C-05 (R010, Art. 72): drift measurement has provenance '%s' — this is not an operating measurement and does not evidence post-market monitoring", [provenance])
}

warn contains msg if {
	_drift
	not _drift.source
	msg := "G-OPS-03/C-05 (R010, Art. 72): drift measurement names no source — its origin cannot be traced"
}
