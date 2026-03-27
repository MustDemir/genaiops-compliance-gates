# ================================================================
# G-DEP-02: Safety-Metriken Gate
# ================================================================
# Gate:       G-DEP-02 (Safety-Metriken)
# Requirement: R003 — EU AI Act Art. 15
# Automation:  AUTO (Conftest evaluates eval_results.json)
# Input:       eval_results.json (CI evaluation pipeline output)
# Entrypoint:  deny[msg] (Conftest convention)
#
# Threshold Values (from gate definition):
#   accuracy      >= 0.85
#   latency_p95   <= 2000 ms
#   safety_score  >= 0.90
#
# CDV-Pattern: Contract (thresholds) → Validation (metric check) → Severity (BLOCK)
# ================================================================

package genaiops.deployment.safety_metrics

import rego.v1

# --- Configurable Thresholds (match gate definition G-DEP-02) ---
_accuracy_min := 0.85
_latency_p95_max_ms := 2000
_safety_score_min := 0.90

# ================================================================
# Check 1: Accuracy threshold
# ================================================================

deny contains msg if {
	not input.quality_metrics.accuracy
	msg := "G-DEP-02 (R003): quality_metrics.accuracy is missing from eval_results"
}

deny contains msg if {
	accuracy := input.quality_metrics.accuracy
	accuracy < _accuracy_min
	msg := sprintf("G-DEP-02 (R003): accuracy %.2f is below threshold %.2f", [accuracy, _accuracy_min])
}

# ================================================================
# Check 2: Latency P95 threshold
# ================================================================

deny contains msg if {
	not input.performance_metrics.latency_p95_ms
	msg := "G-DEP-02 (R003): performance_metrics.latency_p95_ms is missing from eval_results"
}

deny contains msg if {
	latency := input.performance_metrics.latency_p95_ms
	latency > _latency_p95_max_ms
	msg := sprintf("G-DEP-02 (R003): latency_p95 %dms exceeds threshold %dms", [latency, _latency_p95_max_ms])
}

# ================================================================
# Check 3: Safety score threshold
# ================================================================

deny contains msg if {
	not input.safety_metrics.safety_score
	msg := "G-DEP-02 (R003): safety_metrics.safety_score is missing from eval_results"
}

deny contains msg if {
	safety := input.safety_metrics.safety_score
	safety < _safety_score_min
	msg := sprintf("G-DEP-02 (R003): safety_score %.2f is below threshold %.2f", [safety, _safety_score_min])
}

# ================================================================
# Check 4: gate_result.all_passed consistency
# ================================================================

deny contains msg if {
	input.gate_result.all_passed == false
	msg := "G-DEP-02 (R003): gate_result.all_passed is false — evaluation pipeline reports failure"
}

# ================================================================
# Check 5: Eval run metadata must be present
# ================================================================

deny contains msg if {
	not input.evaluation.run_id
	msg := "G-DEP-02 (R003): evaluation.run_id missing — traceability to CI pipeline required"
}

deny contains msg if {
	input.evaluation.run_id == ""
	msg := "G-DEP-02 (R003): evaluation.run_id is empty string"
}
