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
	input_override := object.union(scenario, {"spec": {"template": {"metadata": {"annotations": {
		"genaiops.io/service-monitor-configured": "false",
	}}}}})
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
