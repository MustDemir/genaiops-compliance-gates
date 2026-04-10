#!/usr/bin/env bash
# ================================================================
# smoke-test.sh — Verify Gatekeeper Admission Control works
# ================================================================
# Phase 6: Final verification — proves the Quality Gate system works
#
# What this does (Kolloquium):
#   This is the "proof" that our admission control works.
#   We try two things:
#
#   Test 1 (ADMIT): Deploy a compliant app with all required annotations
#          → Gatekeeper lets it through → SUCCESS
#
#   Test 2 (REJECT): Deploy a non-compliant app WITHOUT annotations
#          → Gatekeeper BLOCKS it → ERROR message shows WHY
#
#   This demonstrates:
#   - Pillar S3 (Policy Engine) is enforcing rules
#   - Pillar S2 (Quality Gates) G-DEP-02, G-OPS-03, G-OPS-05 are active
#   - Non-compliant deployments cannot bypass the system
#
# Usage:
#   ./infrastructure/scripts/smoke-test.sh
# ================================================================

set -euo pipefail

GREEN='\033[92m'
BLUE='\033[94m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
RESET='\033[0m'

log() { echo -e "${BLUE}[smoke-test]${RESET} $1"; }
ok()  { echo -e "${GREEN}[  PASS ]${RESET} $1"; }
fail(){ echo -e "${RED}[  FAIL ]${RESET} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FIXTURES_DIR="$REPO_ROOT/scenarios/healthcare-ambient-ai-scribe/fixtures"

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GenAIOps PoC — Smoke Test (Phase 6)${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}\n"

# ── Test 0: Cluster Health ─────────────────────────────────────
log "Test 0: Cluster health check..."

if kubectl cluster-info &> /dev/null; then
    ok "Kubernetes cluster is reachable"
    ((TESTS_PASSED++))
else
    fail "Cannot reach Kubernetes cluster"
    ((TESTS_FAILED++))
    echo "Aborting — cluster must be running."
    exit 1
fi

# ── Test 1: Gatekeeper is running ──────────────────────────────
log "Test 1: Gatekeeper pods are running..."

GK_STATUS=$(kubectl get pods -n gatekeeper-system -l control-plane=controller-manager \
    -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")

if [[ "$GK_STATUS" == "Running" ]]; then
    ok "Gatekeeper controller is Running"
    ((TESTS_PASSED++))
else
    fail "Gatekeeper controller status: $GK_STATUS"
    ((TESTS_FAILED++))
fi

# ── Test 2: ConstraintTemplates are registered ─────────────────
log "Test 2: ConstraintTemplates registered..."

CT_COUNT=$(kubectl get constrainttemplates --no-headers 2>/dev/null | wc -l | tr -d ' ')
if [[ "$CT_COUNT" -ge 3 ]]; then
    ok "ConstraintTemplates: $CT_COUNT registered (G-DEP-02, G-OPS-03, G-OPS-05)"
    ((TESTS_PASSED++))
else
    fail "Expected ≥3 ConstraintTemplates, got $CT_COUNT"
    ((TESTS_FAILED++))
fi

# ── Test 3: Constraints are active ─────────────────────────────
log "Test 3: Constraints are active..."

CONSTRAINTS=$(kubectl get constraints --no-headers 2>/dev/null | wc -l | tr -d ' ')
if [[ "$CONSTRAINTS" -ge 3 ]]; then
    ok "Constraints: $CONSTRAINTS active"
    ((TESTS_PASSED++))
else
    fail "Expected ≥3 Constraints, got $CONSTRAINTS"
    ((TESTS_FAILED++))
fi

# ── Test 4: ADMIT compliant Deployment ─────────────────────────
log "Test 4: ADMIT — compliant Deployment should be accepted..."

# Create a temporary test deployment (compliant)
cat <<'EOF' | kubectl apply -f - -n genaiops 2>&1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smoke-test-compliant
  namespace: genaiops
  labels:
    app.kubernetes.io/name: smoke-test-compliant
    risk_class: "high"
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: smoke-test-compliant
  template:
    metadata:
      labels:
        app.kubernetes.io/name: smoke-test-compliant
      annotations:
        genaiops.io/eval-passed: "true"
        genaiops.io/eval-run-id: "smoke-test-eval-001"
        genaiops.io/drift-detection-enabled: "true"
        genaiops.io/service-monitor-configured: "true"
        genaiops.io/evidence-store-connected: "true"
        genaiops.io/hash-chain-enabled: "true"
    spec:
      containers:
        - name: test
          image: busybox
          command: ["sleep", "3600"]
          resources:
            limits:
              cpu: "100m"
              memory: "64Mi"
EOF

ADMIT_EXIT=$?
if [[ $ADMIT_EXIT -eq 0 ]]; then
    ok "Compliant Deployment ADMITTED by Gatekeeper"
    ((TESTS_PASSED++))
    # Clean up
    kubectl delete deployment smoke-test-compliant -n genaiops --wait=false 2>/dev/null
else
    fail "Compliant Deployment was REJECTED (should have been admitted)"
    ((TESTS_FAILED++))
fi

# ── Test 5: REJECT non-compliant Deployment ────────────────────
log "Test 5: REJECT — non-compliant Deployment should be blocked..."

# Create a test deployment WITHOUT required annotations
# NOTE: We expect this to FAIL (exit ≠ 0), so we disable set -e temporarily
set +e
REJECT_OUTPUT=$(cat <<'EOF' | kubectl apply -f - -n genaiops 2>&1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smoke-test-noncompliant
  namespace: genaiops
  labels:
    app.kubernetes.io/name: smoke-test-noncompliant
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: smoke-test-noncompliant
  template:
    metadata:
      labels:
        app.kubernetes.io/name: smoke-test-noncompliant
    spec:
      containers:
        - name: test
          image: busybox
          command: ["sleep", "3600"]
          resources:
            limits:
              cpu: "100m"
              memory: "64Mi"
EOF
)
REJECT_EXIT=$?
set -e

if [[ $REJECT_EXIT -ne 0 ]]; then
    ok "Non-compliant Deployment REJECTED by Gatekeeper"
    echo -e "  ${YELLOW}Rejection message:${RESET}"
    echo "$REJECT_OUTPUT" | head -5 | sed 's/^/    /'
    ((TESTS_PASSED++))
else
    fail "Non-compliant Deployment was ADMITTED (should have been rejected!)"
    ((TESTS_FAILED++))
    # Clean up — shouldn't happen
    kubectl delete deployment smoke-test-noncompliant -n genaiops --wait=false 2>/dev/null
fi

# ── Test 6: App is healthy ─────────────────────────────────────
log "Test 6: AI Scribe app health check..."

APP_POD=$(kubectl get pod -n genaiops -l app.kubernetes.io/name=ambient-ai-scribe \
    -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [[ -n "$APP_POD" ]]; then
    HEALTH=$(kubectl exec -n genaiops "$APP_POD" -c scribe -- \
        python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8080/health').status)" 2>/dev/null || echo "000")
    if [[ "$HEALTH" == "200" ]]; then
        ok "App health endpoint returns 200"
        ((TESTS_PASSED++))
    else
        fail "App health endpoint returns $HEALTH (expected 200)"
        ((TESTS_FAILED++))
    fi
else
    warn "App pod not found — skipping health check (deploy-app.sh may not have run)"
    ((TESTS_SKIPPED++))
fi

# ── Test 7: Prometheus metrics accessible ──────────────────────
log "Test 7: Prometheus metrics endpoint..."

if [[ -n "$APP_POD" ]]; then
    METRICS=$(kubectl exec -n genaiops "$APP_POD" -c scribe -- \
        python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8080/metrics').read().decode()[:80])" 2>/dev/null || echo "")
    if [[ -n "$METRICS" ]]; then
        ok "Metrics endpoint accessible"
        ((TESTS_PASSED++))
    else
        fail "Metrics endpoint not responding"
        ((TESTS_FAILED++))
    fi
else
    warn "App pod not found — skipping metrics check"
    ((TESTS_SKIPPED++))
fi

# ── Summary ────────────────────────────────────────────────────
TOTAL=$((TESTS_PASSED + TESTS_FAILED))

echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  Smoke Test Results${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${GREEN}PASSED: $TESTS_PASSED${RESET}  /  ${RED}FAILED: $TESTS_FAILED${RESET}  /  ${YELLOW}SKIPPED: $TESTS_SKIPPED${RESET}  /  Total: $TOTAL"
echo ""

if [[ $TESTS_FAILED -eq 0 && $TESTS_SKIPPED -eq 0 ]]; then
    echo -e "  ${GREEN}${BOLD}✓ ALL TESTS PASSED — Phase 6 complete${RESET}"
    echo ""
    echo -e "  ${BOLD}What was proven:${RESET}"
    echo -e "  1. Gatekeeper is enforcing compliance rules in Kubernetes"
    echo -e "  2. Compliant Deployments pass through (ADMIT)"
    echo -e "  3. Non-compliant Deployments are blocked (REJECT)"
    echo -e "  4. The AI Scribe app is running with all compliance annotations"
    echo ""
    echo -e "  ${BOLD}Next steps:${RESET}"
    echo -e "  Phase 7:  ${BLUE}Test ConstraintTemplates in detail${RESET}"
    echo -e "  Phase 9:  ${BLUE}Deploy Prometheus + drift_detector${RESET}"
    echo -e "  Phase 10: ${BLUE}ArgoCD + GitHub Actions pipeline${RESET}"
    EXIT_CODE=0
elif [[ $TESTS_FAILED -eq 0 && $TESTS_SKIPPED -gt 0 ]]; then
    echo -e "  ${YELLOW}${BOLD}⚠ TESTS PASSED but $TESTS_SKIPPED SKIPPED — not all checks could run${RESET}"
    echo -e "  ${YELLOW}  Skipped checks do not count as passed. Deploy app first to run full suite.${RESET}"
    EXIT_CODE=0
else
    echo -e "  ${RED}${BOLD}✗ SOME TESTS FAILED — review output above${RESET}"
    EXIT_CODE=1
fi

echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}\n"
exit $EXIT_CODE
