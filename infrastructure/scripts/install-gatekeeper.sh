#!/usr/bin/env bash
# ================================================================
# install-gatekeeper.sh — Deploy Gatekeeper + ConstraintTemplates
# ================================================================
# Phase 6+7: Step 2 — runs AFTER setup-minikube.sh
#
# What this does (Kolloquium):
#   1. Installs Gatekeeper via Helm (the upstream chart from CNCF)
#   2. Waits until Gatekeeper pods are running
#   3. Deploys our 3 ConstraintTemplates (the compliance rules)
#   4. Deploys our 3 Constraints (which namespaces + parameters to enforce)
#   5. Verifies everything is active
#
#   After this script:
#   - Any Deployment in namespace "genaiops" WITHOUT the required
#     annotations will be REJECTED by Kubernetes.
#   - This is Pillar S3 (Policy Engine) in action.
#
#   ConstraintTemplates (3):
#     G-DEP-02: Safety Metrics   (eval-passed, eval-run-id)
#     G-OPS-03: Monitoring       (drift-detection, service-monitor)
#     G-OPS-05: Evidence Store   (evidence-store-connected, hash-chain)
#
# Usage:
#   ./infrastructure/scripts/install-gatekeeper.sh
# ================================================================

set -euo pipefail

# Colors
GREEN='\033[92m'
BLUE='\033[94m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
RESET='\033[0m'

log() { echo -e "${BLUE}[gatekeeper]${RESET} $1"; }
ok()  { echo -e "${GREEN}[  OK ]${RESET} $1"; }
warn(){ echo -e "${YELLOW}[ WARN]${RESET} $1"; }
err() { echo -e "${RED}[ERROR]${RESET} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HELM_VALUES="$REPO_ROOT/infrastructure/helm/gatekeeper-values.yaml"
GATEKEEPER_DIR="$REPO_ROOT/scenarios/healthcare-ambient-ai-scribe/k8s/gatekeeper"

echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GenAIOps PoC — Gatekeeper Installation (Phase 6+7)${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}\n"

# ── Pre-flight ─────────────────────────────────────────────────
log "Checking prerequisites..."

# Verify kubectl context
CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")
if [[ "$CONTEXT" != *"genaiops"* && "$CONTEXT" != *"minikube"* ]]; then
    warn "Current kubectl context is '$CONTEXT'. Expected 'genaiops' or 'minikube'."
    read -p "  Continue anyway? (y/N): " answer
    [[ "$answer" =~ ^[Yy]$ ]] || exit 0
fi
ok "kubectl context: $CONTEXT"

# Verify helm values exist
[[ -f "$HELM_VALUES" ]] || err "Helm values not found: $HELM_VALUES"
ok "Helm values found"

# Verify CT files exist
[[ -d "$GATEKEEPER_DIR" ]] || err "Gatekeeper directory not found: $GATEKEEPER_DIR"
ok "ConstraintTemplate files found"

# ── Step 1: Install Gatekeeper via Helm ────────────────────────
log "Installing Gatekeeper via Helm..."

# Check if already installed
if helm list -n gatekeeper-system 2>/dev/null | grep -q gatekeeper; then
    warn "Gatekeeper already installed. Upgrading..."
    helm upgrade gatekeeper gatekeeper/gatekeeper \
        --namespace gatekeeper-system \
        --values "$HELM_VALUES" \
        --wait \
        --timeout 120s
else
    helm install gatekeeper gatekeeper/gatekeeper \
        --create-namespace \
        --namespace gatekeeper-system \
        --values "$HELM_VALUES" \
        --wait \
        --timeout 120s
fi

ok "Gatekeeper Helm chart installed"

# ── Step 2: Wait for pods ──────────────────────────────────────
log "Waiting for Gatekeeper pods to be ready..."
kubectl wait --for=condition=Ready pod \
    -l control-plane=controller-manager \
    -n gatekeeper-system \
    --timeout=120s

kubectl wait --for=condition=Ready pod \
    -l control-plane=audit-controller \
    -n gatekeeper-system \
    --timeout=120s 2>/dev/null || true  # Audit might be same pod

ok "Gatekeeper pods running"

# Show pod status
echo ""
kubectl get pods -n gatekeeper-system
echo ""

# ── Step 3: Deploy ConstraintTemplates ─────────────────────────
log "Deploying ConstraintTemplates..."

for ct_file in "$GATEKEEPER_DIR"/constraint-*.yaml; do
    filename=$(basename "$ct_file")
    log "  Applying $filename..."
    kubectl apply -f "$ct_file"
done

ok "ConstraintTemplates and Constraints deployed"

# ── Step 4: Verify deployment ──────────────────────────────────
log "Verifying Gatekeeper deployment..."
echo ""

echo -e "${BOLD}ConstraintTemplates:${RESET}"
kubectl get constrainttemplates 2>/dev/null || warn "No ConstraintTemplates found"
echo ""

echo -e "${BOLD}Constraints:${RESET}"
kubectl get constraints 2>/dev/null || warn "No Constraints found"
echo ""

# ── Step 5: Quick validation ───────────────────────────────────
log "Validating webhook is active..."
WEBHOOK=$(kubectl get validatingwebhookconfigurations 2>/dev/null | grep gatekeeper || echo "")
if [[ -n "$WEBHOOK" ]]; then
    ok "Gatekeeper webhook is active"
else
    warn "Gatekeeper webhook not found — constraints may not enforce"
fi

# ── Summary ────────────────────────────────────────────────────
echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  Gatekeeper Installation Complete${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  Namespace:       gatekeeper-system"
echo -e "  Replicas:        1 (D_GATEKEEPER_STANDALONE)"
echo -e "  Audit interval:  60s"
echo -e "  Templates:       $(kubectl get constrainttemplates --no-headers 2>/dev/null | wc -l | tr -d ' ')"
echo -e "  Constraints:     $(kubectl get constraints --no-headers 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo -e "  ${BOLD}Enforced rules (3 ConstraintTemplates):${RESET}"
echo -e "  ${GREEN}G-DEP-02${RESET}: Safety Metrics (eval-passed, eval-run-id)"
echo -e "  ${GREEN}G-OPS-03${RESET}: Monitoring annotations (drift-detection, service-monitor)"
echo -e "  ${GREEN}G-OPS-05${RESET}: Evidence Store annotations (evidence-store-connected, hash-chain)"
echo ""
echo -e "  ${BOLD}Next step:${RESET}"
echo -e "  ${BLUE}./infrastructure/scripts/deploy-app.sh${RESET}"
echo ""
