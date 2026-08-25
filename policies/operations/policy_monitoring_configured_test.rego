# ================================================================
# G-OPS-03: Monitoring Configured — UNIT TESTS
# ================================================================
# Tests:       policy_monitoring_configured.rego (6 violation-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + FAIL-missing + FAIL-wrong-value + FAIL-missing
# Coverage:    4 tests for 6 rules — 3/3 check-groups covered,
#              rule-level 3/6 explicit + PASS covers positive path of all 6.
#
# Fixtures:    data.fixtures.healthcare.deployment_compliant (real Use-Case)
#              Dual-mode resolver already verified in G-OPS-02 test —
#              shared resolver pattern, single verification suffices.
#
# Checks mapped:
#   Check 1 (drift-detection)     — rule 1 explicit-FAIL, rule 2 implicit-PASS
#   Check 2 (service-monitor)     — rule 4 explicit-FAIL, rule 3 implicit-PASS
#   Check 3 (prometheus.io/scrape) — rule 5 explicit-FAIL, rule 6 implicit-PASS
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.operations.monitoring_configured_test

import rego.v1

import data.fixtures.healthcare.deployment_compliant as scenario
import data.genaiops.operations.monitoring_configured

# ================================================================
# PASS Tests (real Use-Case scenario must produce zero violations)
# ================================================================

test_pass_compliant_deployment if {
	# Healthcare Ambient AI Scribe has all monitoring annotations:
	# drift-detection, service-monitor, prometheus scrape config.
	# Positive path exercises all 6 rules (no violation triggered).
	count(monitoring_configured.violation) == 0 with input as scenario
}

# ================================================================
# FAIL Tests — Missing annotation (Check 1: drift-detection-enabled)
# ================================================================

test_fail_missing_drift_detection_annotation if {
	# Rule 1: pod annotation genaiops.io/drift-detection-enabled missing.
	# Post-market monitoring per Art. 72 requires drift detection.
	# JSON Pointer escaping: "/" = "~1" per RFC 6901.
	input_override := json.patch(scenario, [{
		"op": "remove",
		"path": "/spec/template/metadata/annotations/genaiops.io~1drift-detection-enabled",
	}])
	result := monitoring_configured.violation with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Wrong value (Check 2: service-monitor-configured != "true")
# ================================================================

test_fail_service_monitor_disabled_value if {
	# Rule 4: service-monitor-configured present but not "true".
	# Prometheus ServiceMonitor CR required for metrics collection.
	input_override := object.union(scenario, {"spec": {"template": {"metadata": {"annotations": {"genaiops.io/service-monitor-configured": "false"}}}}})
	result := monitoring_configured.violation with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Missing annotation (Check 3: prometheus.io/scrape)
# ================================================================

test_fail_prometheus_scrape_missing_annotation if {
	# Rule 5: prometheus.io/scrape annotation missing — metrics endpoint
	# not discoverable by Prometheus scrape targets.
	input_override := json.patch(scenario, [{
		"op": "remove",
		"path": "/spec/template/metadata/annotations/prometheus.io~1scrape",
	}])
	result := monitoring_configured.violation with input as input_override
	count(result) > 0
}

# ================================================================
# SPEC-04 Teil 3.3 — C-03 / C-04 / C-05 (Messnachweis statt Annotation)
# ================================================================
# The tests above exercise the E-0 half of this gate: three annotations
# that someone wrote. The tests below exercise the E-3 half: a drift
# measurement that a process produced.
#
# `measured_at` is built relative to time.now_ns() rather than hard-coded,
# so these tests do not rot. A fixed timestamp would pass today and start
# failing the moment the freshness budget elapsed in wall-clock time —
# a test that expires is worse than no test.
# ================================================================

_now_rfc3339 := time.format([time.now_ns(), "UTC", "2006-01-02T15:04:05Z07:00"])

_ago_rfc3339(seconds) := time.format([
	time.now_ns() - (seconds * 1000000000),
	"UTC",
	"2006-01-02T15:04:05Z07:00",
])

_fresh_measurement := {"drift_measurement": {
	"psi_score": 0.03,
	"jsd_score": 0.01,
	"drift_status": "ok",
	"provenance": "derived",
	"source": "http://scribe:8080/metrics",
	"measured_at": _now_rfc3339,
	"max_age_seconds": 900,
}}

# ── PASS: a fresh measurement under both thresholds ──

test_pass_fresh_measurement_within_thresholds if {
	count(monitoring_configured.violation) == 0 with input as _fresh_measurement
}

test_pass_fresh_measurement_no_warnings if {
	count(monitoring_configured.warn) == 0 with input as _fresh_measurement
}

# ── C-03: the freshness check is the point of the whole gate ──
# A stale measurement must fail EVEN THOUGH its scores are good. This is
# the negative case that separates "no drift" from "no longer measuring".

test_fail_c03_stale_measurement_despite_good_scores if {
	stale := json.patch(_fresh_measurement, [{
		"op": "replace",
		"path": "/drift_measurement/measured_at",
		"value": _ago_rfc3339(3600),
	}])
	result := monitoring_configured.violation with input as stale
	count(result) > 0

	# and it must be C-03 that fired, not one of the threshold rules
	some msg in result
	contains(msg.msg, "C-03")
}

test_fail_c03_measurement_without_timestamp if {
	undated := json.patch(_fresh_measurement, [{
		"op": "remove",
		"path": "/drift_measurement/measured_at",
	}])
	result := monitoring_configured.violation with input as undated
	count(result) > 0
}

# ── C-04: thresholds ──

test_fail_c04_psi_above_critical if {
	drifted := json.patch(_fresh_measurement, [{
		"op": "replace",
		"path": "/drift_measurement/psi_score",
		"value": 0.35,
	}])
	result := monitoring_configured.violation with input as drifted
	some msg in result
	contains(msg.msg, "C-04")
}

test_fail_c04_jsd_above_critical if {
	drifted := json.patch(_fresh_measurement, [{
		"op": "replace",
		"path": "/drift_measurement/jsd_score",
		"value": 0.25,
	}])
	result := monitoring_configured.violation with input as drifted
	some msg in result
	contains(msg.msg, "C-04")
}

test_fail_c04_missing_psi_score if {
	result := monitoring_configured.violation with input as {"drift_measurement": {
		"jsd_score": 0.01,
		"measured_at": _now_rfc3339,
		"provenance": "derived",
		"source": "http://scribe:8080/metrics",
	}}
	count(result) > 0
}

# ── C-05: advisory, must warn without blocking ──

test_warn_c05_declared_provenance_does_not_block if {
	fixture_run := json.patch(_fresh_measurement, [{
		"op": "replace",
		"path": "/drift_measurement/provenance",
		"value": "declared",
	}])
	count(monitoring_configured.warn) > 0 with input as fixture_run
	count(monitoring_configured.violation) == 0 with input as fixture_run
}

test_warn_c05_missing_source if {
	no_source := json.patch(_fresh_measurement, [{
		"op": "remove",
		"path": "/drift_measurement/source",
	}])
	count(monitoring_configured.warn) > 0 with input as no_source
}

# ── The measurement rules must stay silent on an admission review ──
# Gatekeeper admits a workload before it runs; there is no operating
# measurement to be had at that moment. Demanding one there would make
# the gate impossible to satisfy rather than harder to fake.

test_pass_admission_review_unaffected_by_measurement_rules if {
	count(monitoring_configured.violation) == 0 with input as scenario
	count(monitoring_configured.warn) == 0 with input as scenario
}
