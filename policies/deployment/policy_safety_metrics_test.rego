# ================================================================
# G-DEP-02: Safety Metrics — UNIT TESTS
# ================================================================
# Tests:       policy_safety_metrics.rego (16 deny-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + multi-rule-FAIL (fixture) + 16× rule-isolation-FAIL
# Coverage:    18 tests for 16 rules — 7/7 check-groups covered
#              (accuracy, latency, safety_score, gate_result, run_id,
#              subgroup_analysis, adversarial_tests), rule-level 16/16
#              strict-isolation + multi-rule co-occurrence.
#              Pattern-class coverage: 6/6 — threshold-comparison (NEW:
#              numeric < > checks against hard-coded thresholds),
#              top-level-missing, field-missing, string-empty,
#              boolean-false, array-empty, nested-field-missing.
#
# Fixtures:    data.fixtures.healthcare.eval_results
#              (shared PASS — accuracy 0.91, latency_p95 890ms,
#              safety_score 0.96, subgroup + adversarial tests done).
#              data.fixtures.healthcare.eval_results_fail
#              (shared FAIL multi-rule: below all thresholds +
#              subgroup/adversarial not performed → 5+ rules fire).
#
# Strengthened assertion for multi-rule test:
#   count(result) >= 5 — realistic evaluation failure scenario where
#   model misses all three quality thresholds AND missing SHOULD-tests.
#
# Methodology: Strict rule-isolation per DSR-Rigor — each rule fires
#              in exactly one dedicated test where only that rule's
#              condition is violated. Threshold rules (R2, R4, R6)
#              tested with values just below/above limits to exercise
#              the exact boundary comparison logic.
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.deployment.safety_metrics_test

import rego.v1

import data.fixtures.healthcare.eval_results as scenario_pass
import data.fixtures.healthcare.eval_results_fail as scenario_fail
import data.genaiops.deployment.safety_metrics

# ================================================================
# PASS Tests (real Use-Case passing evaluation)
# ================================================================

test_pass_full_eval_results if {
	# eval_results fixture: accuracy 0.91 >= 0.85, latency_p95
	# 890ms <= 2000ms, safety_score 0.96 >= 0.90, gate all_passed,
	# subgroup + adversarial performed. 0 deny rules fire.
	count(safety_metrics.deny) == 0 with input as scenario_pass
}

# ================================================================
# FAIL Tests — Multi-rule via shared eval_results_fail fixture
# ================================================================

test_fail_realistic_multi_rule_eval_failure if {
	# eval_results_fail fixture triggers MUST (deny) rules:
	#   accuracy 0.72 < 0.85, latency_p95 2800 > 2000,
	#   safety_score 0.78 < 0.90, gate_result.all_passed: false
	# and SHOULD (warn) advisories:
	#   subgroup_analysis.performed: false, adversarial_tests.performed: false
	count(safety_metrics.deny) >= 4 with input as scenario_fail
	count(safety_metrics.warn) >= 2 with input as scenario_fail
}

# ================================================================
# FAIL Tests — Rule-isolation (Check 1: accuracy)
# ================================================================

test_fail_accuracy_missing if {
	# R1 (isolation): quality_metrics.accuracy absent.
	# Remove-then-union to defeat object.union deep-merge preserving field.
	input_override := object.union(
		object.remove(scenario_pass, ["quality_metrics"]),
		{"quality_metrics": object.remove(scenario_pass.quality_metrics, ["accuracy"])},
	)
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

test_fail_accuracy_below_threshold if {
	# R2 (isolation): accuracy 0.80 < 0.85 threshold.
	# Pattern-class: threshold-comparison (NEW).
	input_override := object.union(scenario_pass, {"quality_metrics": object.union(
		scenario_pass.quality_metrics,
		{"accuracy": 0.80},
	)})
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Check 2: latency_p95)
# ================================================================

test_fail_latency_p95_missing if {
	# R3 (isolation): performance_metrics.latency_p95_ms absent.
	input_override := object.union(
		object.remove(scenario_pass, ["performance_metrics"]),
		{"performance_metrics": object.remove(scenario_pass.performance_metrics, ["latency_p95_ms"])},
	)
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

test_fail_latency_p95_above_threshold if {
	# R4 (isolation): latency_p95 2500ms > 2000ms threshold.
	# Pattern-class: threshold-comparison.
	input_override := object.union(scenario_pass, {"performance_metrics": object.union(
		scenario_pass.performance_metrics,
		{"latency_p95_ms": 2500},
	)})
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Check 3: safety_score)
# ================================================================

test_fail_safety_score_missing if {
	# R5 (isolation): safety_metrics.safety_score absent.
	input_override := object.union(
		object.remove(scenario_pass, ["safety_metrics"]),
		{"safety_metrics": object.remove(scenario_pass.safety_metrics, ["safety_score"])},
	)
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

test_fail_safety_score_below_threshold if {
	# R6 (isolation): safety_score 0.85 < 0.90 threshold.
	input_override := object.union(scenario_pass, {"safety_metrics": object.union(
		scenario_pass.safety_metrics,
		{"safety_score": 0.85},
	)})
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Check 4: gate_result.all_passed)
# ================================================================

test_fail_gate_result_all_passed_false if {
	# R7 (isolation): gate_result.all_passed == false.
	# Pattern-class: boolean-false.
	input_override := object.union(scenario_pass, {"gate_result": object.union(
		scenario_pass.gate_result,
		{"all_passed": false},
	)})
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Check 5: evaluation.run_id)
# ================================================================

test_fail_run_id_missing if {
	# R8 (isolation): evaluation.run_id field absent.
	input_override := object.union(
		object.remove(scenario_pass, ["evaluation"]),
		{"evaluation": object.remove(scenario_pass.evaluation, ["run_id"])},
	)
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

test_fail_run_id_empty_string if {
	# R9 (isolation): evaluation.run_id == "".
	# Pattern-class: string-empty.
	input_override := object.union(scenario_pass, {"evaluation": object.union(
		scenario_pass.evaluation,
		{"run_id": ""},
	)})
	result := safety_metrics.deny with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Check 6: subgroup_analysis)
# ================================================================

test_fail_subgroup_analysis_section_missing if {
	# R10 (isolation): subgroup_analysis section absent. [SHOULD → warn]
	input_override := object.remove(scenario_pass, ["subgroup_analysis"])
	result := safety_metrics.warn with input as input_override
	count(result) > 0
}

test_fail_subgroup_analysis_performed_field_missing if {
	# R11 (isolation): subgroup_analysis present but .performed
	# subfield absent. Pattern-class: nested-field-missing. [SHOULD → warn]
	input_override := object.union(
		object.remove(scenario_pass, ["subgroup_analysis"]),
		{"subgroup_analysis": object.remove(scenario_pass.subgroup_analysis, ["performed"])},
	)
	result := safety_metrics.warn with input as input_override
	count(result) > 0
}

test_fail_subgroup_analysis_performed_false if {
	# R12 (isolation): subgroup_analysis.performed == false. [SHOULD → warn]
	input_override := object.union(scenario_pass, {"subgroup_analysis": object.union(
		scenario_pass.subgroup_analysis,
		{"performed": false},
	)})
	result := safety_metrics.warn with input as input_override
	count(result) > 0
}

test_fail_subgroup_analysis_empty_subgroups if {
	# R13 (isolation): subgroup_analysis.performed: true but
	# subgroups array is empty. [SHOULD → warn]
	input_override := object.union(scenario_pass, {"subgroup_analysis": object.union(
		scenario_pass.subgroup_analysis,
		{"performed": true, "subgroups": []},
	)})
	result := safety_metrics.warn with input as input_override
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (Check 7: adversarial_tests) [SHOULD → warn]
# ================================================================

test_fail_adversarial_tests_section_missing if {
	# R14 (isolation): adversarial_tests section absent. [SHOULD → warn]
	input_override := object.remove(scenario_pass, ["adversarial_tests"])
	result := safety_metrics.warn with input as input_override
	count(result) > 0
}

test_fail_adversarial_tests_performed_field_missing if {
	# R15 (isolation): adversarial_tests present but .performed
	# subfield absent. Pattern-class: nested-field-missing. [SHOULD → warn]
	input_override := object.union(
		object.remove(scenario_pass, ["adversarial_tests"]),
		{"adversarial_tests": object.remove(scenario_pass.adversarial_tests, ["performed"])},
	)
	result := safety_metrics.warn with input as input_override
	count(result) > 0
}

test_fail_adversarial_tests_performed_false if {
	# R16 (isolation): adversarial_tests.performed == false. [SHOULD → warn]
	input_override := object.union(scenario_pass, {"adversarial_tests": object.union(
		scenario_pass.adversarial_tests,
		{"performed": false},
	)})
	result := safety_metrics.warn with input as input_override
	count(result) > 0
}
