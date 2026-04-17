# ================================================================
# G-PRE-04: Security Baseline — UNIT TESTS
# ================================================================
# Tests:       policy_security_baseline.rego (12 deny-rules)
# Convention:  OPA Rego Unit Tests (opa test policies/ tests/fixtures/ -v)
# Pattern:     PASS + multi-rule-FAIL (fixture) + 12× rule-isolation-FAIL
# Coverage:    14 tests for 12 rules — 6/6 check-groups covered,
#              rule-level 12/12 strict-isolation + multi-rule co-occurrence
#              via shared non-compliant fixture.
#              Pattern-class coverage: spec-container-array iteration
#              (different from flat-JSON policies) — each isolation test
#              builds a minimal single-container deployment that violates
#              exactly one rule.
#
# Fixtures:    data.fixtures.healthcare.deployment_compliant
#              (shared PASS fixture — full K8s deployment with all
#              securityContext, resources.limits, capabilities set).
#              data.fixtures.healthcare.deployment_noncompliant
#              (shared FAIL fixture — multi-rule: R2+R3+R4+R8+R9+R10+R11).
#
# Methodology: Strict rule-isolation per DSR-Rigor — for K8s container
#              policies, isolation requires constructing minimal
#              Deployment objects where the single container has all
#              valid security settings except the one rule under test.
#              Baseline container (_valid_container) encodes the
#              "compliant-by-default" state; each test overrides one
#              field via object.union.
#
# Strengthened assertion for multi-rule test:
#   count(result) >= 5 — the shared non-compliant fixture intentionally
#   violates 5+ rules, validating rule-aggregation behavior.
#
# Run:
#   opa test policies/ tests/fixtures/ -v
# ================================================================

package genaiops.pre_deployment.security_baseline_test

import rego.v1

import data.fixtures.healthcare.deployment_compliant as scenario_pass
import data.fixtures.healthcare.deployment_noncompliant as scenario_fail
import data.genaiops.pre_deployment.security_baseline

# ================================================================
# Helper: Valid baseline container (passes all 12 rules)
# ================================================================
# Used by rule-isolation tests as the starting point — each test
# overrides exactly one field to trigger exactly one rule.

_valid_container := {
	"name": "test-container",
	"image": "test:1.0.0",
	"securityContext": {
		"runAsNonRoot": true,
		"runAsUser": 1000,
		"allowPrivilegeEscalation": false,
		"readOnlyRootFilesystem": true,
		"capabilities": {"drop": ["ALL"]},
	},
	"resources": {"limits": {
		"cpu": "500m",
		"memory": "256Mi",
	}},
}

_wrap_deployment(container) := {"spec": {"template": {"spec": {"containers": [container]}}}}

# ================================================================
# PASS Tests (real Use-Case full compliant deployment)
# ================================================================

test_pass_compliant_deployment if {
	# Shared deployment_compliant fixture — scribe container has
	# all required securityContext, resources.limits, capabilities.
	# Exercises all 12 rules (none fire).
	count(security_baseline.deny) == 0 with input as scenario_pass
}

# ================================================================
# FAIL Tests — Multi-rule via shared non-compliant fixture
# ================================================================

test_fail_realistic_multi_rule_noncompliant if {
	# deployment_noncompliant triggers 5+ rules:
	#   R2 (runAsNonRoot: false), R3 (runAsUser: 0),
	#   R4 (no resources.limits), R8 (readOnlyRootFilesystem: false),
	#   R9 (DB_PASSWORD plain env), R10 (allowPrivEsc: true),
	#   R11 (no capabilities).
	result := security_baseline.deny with input as scenario_fail
	count(result) >= 5
}

# ================================================================
# FAIL Tests — Rule-isolation (P1: runAsNonRoot / runAsUser)
# ================================================================

test_fail_runAsNonRoot_not_set if {
	# R1 (isolation): securityContext present but runAsNonRoot
	# field absent. Remove-then-union to defeat object.union deep-merge.
	container := object.union(object.remove(_valid_container, ["securityContext"]), {"securityContext": {
		"runAsUser": 1000,
		"allowPrivilegeEscalation": false,
		"readOnlyRootFilesystem": true,
		"capabilities": {"drop": ["ALL"]},
	}})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

test_fail_runAsNonRoot_explicit_false if {
	# R2 (isolation): runAsNonRoot explicitly false.
	container := object.union(_valid_container, {"securityContext": object.union(
		_valid_container.securityContext,
		{"runAsNonRoot": false},
	)})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

test_fail_runAsUser_zero if {
	# R3 (isolation): runAsUser == 0 (root UID), despite
	# runAsNonRoot: true — rule fires independently.
	container := object.union(_valid_container, {"securityContext": object.union(
		_valid_container.securityContext,
		{"runAsUser": 0},
	)})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (P2: resources.limits)
# ================================================================

test_fail_no_resources_limits if {
	# R4 (isolation): resources object present but limits absent.
	# Remove-then-union to defeat object.union deep-merge.
	container := object.union(object.remove(_valid_container, ["resources"]), {"resources": {"requests": {"cpu": "100m"}}})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

test_fail_missing_limits_cpu if {
	# R5 (isolation): resources.limits present but cpu missing.
	container := object.union(object.remove(_valid_container, ["resources"]), {"resources": {"limits": {"memory": "256Mi"}}})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

test_fail_missing_limits_memory if {
	# R6 (isolation): resources.limits present but memory missing.
	container := object.union(object.remove(_valid_container, ["resources"]), {"resources": {"limits": {"cpu": "500m"}}})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (P3: readOnlyRootFilesystem)
# ================================================================

test_fail_readOnlyRootFilesystem_not_set if {
	# R7 (isolation): readOnlyRootFilesystem field absent.
	# Remove-then-union to defeat object.union deep-merge.
	container := object.union(object.remove(_valid_container, ["securityContext"]), {"securityContext": {
		"runAsNonRoot": true,
		"runAsUser": 1000,
		"allowPrivilegeEscalation": false,
		"capabilities": {"drop": ["ALL"]},
	}})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

test_fail_readOnlyRootFilesystem_explicit_false if {
	# R8 (isolation): readOnlyRootFilesystem: false.
	container := object.union(_valid_container, {"securityContext": object.union(
		_valid_container.securityContext,
		{"readOnlyRootFilesystem": false},
	)})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (P4: secrets in plain env)
# ================================================================

test_fail_plain_secret_in_env if {
	# R9 (isolation): container env has plain-value secret —
	# env var name matches pattern (e.g., DB_PASSWORD) with
	# inline value and no valueFrom.
	container := object.union(_valid_container, {"env": [{
		"name": "DB_PASSWORD",
		"value": "super-secret-password-123",
	}]})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (P6: allowPrivilegeEscalation)
# ================================================================

test_fail_allowPrivilegeEscalation_not_false if {
	# R10 (isolation): allowPrivilegeEscalation: true.
	container := object.union(_valid_container, {"securityContext": object.union(
		_valid_container.securityContext,
		{"allowPrivilegeEscalation": true},
	)})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

# ================================================================
# FAIL Tests — Rule-isolation (P6b: capabilities.drop ALL)
# ================================================================

test_fail_capabilities_missing if {
	# R11 (isolation): capabilities object absent.
	# Remove-then-union to defeat object.union deep-merge.
	container := object.union(object.remove(_valid_container, ["securityContext"]), {"securityContext": {
		"runAsNonRoot": true,
		"runAsUser": 1000,
		"allowPrivilegeEscalation": false,
		"readOnlyRootFilesystem": true,
	}})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}

test_fail_capabilities_drop_not_all if {
	# R12 (isolation): capabilities.drop present but missing "ALL".
	container := object.union(_valid_container, {"securityContext": object.union(
		_valid_container.securityContext,
		{"capabilities": {"drop": ["NET_RAW"]}},
	)})
	result := security_baseline.deny with input as _wrap_deployment(container)
	count(result) > 0
}
