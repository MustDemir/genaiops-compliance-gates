#!/usr/bin/env bash
# ================================================================
# setup-minikube.sh — Initialize Minikube for GenAIOps PoC
# ================================================================
# Phase 6: Minikube + Helm-Basics
# Decision: E6 (Lokal-first), 8 GB RAM, 4 CPUs
#
# What this does (Overview):
#   Creates a local Kubernetes cluster on your computer using Minikube.
#   Think of it as a "mini data center" running on your laptop.
#   We allocate 8 GB RAM so that all components fit:
#   - Gatekeeper (the admission controller / "doorman")
#   - The AI Scribe app + PostgreSQL (evidence store)
#   - Prometheus + Grafana (monitoring)
#   - ArgoCD (deployment management, Phase 10)
#
# Prerequisites:
#   - minikube installed (brew install minikube / choco install minikube)
#   - kubectl installed (brew install kubectl)
#   - helm installed (brew install helm)
#   - Docker Desktop running (Minikube driver)
#
# Usage:
#   chmod +x infrastructure/scripts/setup-minikube.sh
#   ./infrastructure/scripts/setup-minikube.sh
# ================================================================

set -euo pipefail

# ── Configuration ──────────────────────────────────────────────
PROFILE="genaiops"
MEMORY="8192"        # 8 GB — fits Gatekeeper + ArgoCD + App + Prometheus
CPUS="4"
K8S_VERSION="v1.29.0"  # Stable version with Gatekeeper compatibility
DRIVER="docker"      # Requires Docker Desktop running

# Colors
GREEN='\033[92m'
BLUE='\033[94m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
RESET='\033[0m'

log() { echo -e "${BLUE}[setup]${RESET} $1"; }
ok()  { echo -e "${GREEN}[  OK ]${RESET} $1"; }
warn(){ echo -e "${YELLOW}[ WARN]${RESET} $1"; }
err() { echo -e "${RED}[ERROR]${RESET} $1"; }

# ── Pre-flight checks ─────────────────────────────────────────
echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GenAIOps PoC — Minikube Setup (Phase 6)${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}\n"

log "Checking prerequisites..."

for cmd in minikube kubectl helm docker; do
    if command -v "$cmd" &> /dev/null; then
        version=$($cmd version --short 2>/dev/null || $cmd version --client --short 2>/dev/null || $cmd --version 2>/dev/null | head -1)
        ok "$cmd found: $version"
    else
        err "$cmd not found. Please install it first."
        exit 1
    fi
done

# ── Check if profile already exists ───────────────────────────
if minikube status -p "$PROFILE" &> /dev/null; then
    warn "Minikube profile '$PROFILE' already exists."
    echo -e "  To reset: minikube delete -p $PROFILE"
    echo -e "  To continue with existing: just run the next scripts."
    read -p "  Delete and recreate? (y/N): " answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        log "Deleting existing profile..."
        minikube delete -p "$PROFILE"
    else
        log "Keeping existing profile. Exiting."
        exit 0
    fi
fi

# ── Start Minikube ─────────────────────────────────────────────
log "Starting Minikube cluster..."
log "  Profile:    $PROFILE"
log "  Memory:     ${MEMORY}Mi (8 GB)"
log "  CPUs:       $CPUS"
log "  K8s:        $K8S_VERSION"
log "  Driver:     $DRIVER"
echo ""

minikube start \
    --profile="$PROFILE" \
    --memory="$MEMORY" \
    --cpus="$CPUS" \
    --kubernetes-version="$K8S_VERSION" \
    --driver="$DRIVER" \
    --addons=metrics-server \
    --addons=ingress \
    --extra-config=apiserver.enable-admission-plugins=MutatingAdmissionWebhook,ValidatingAdmissionWebhook

ok "Minikube cluster '$PROFILE' started"

# ── Set kubectl context ────────────────────────────────────────
log "Setting kubectl context to '$PROFILE'..."
kubectl config use-context "$PROFILE"
ok "kubectl context set"

# ── Create genaiops namespace ──────────────────────────────────
log "Creating 'genaiops' namespace..."

# Use the existing namespace manifest from the repo
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NAMESPACE_YAML="$REPO_ROOT/scenarios/healthcare-ambient-ai-scribe/k8s/namespace.yaml"

if [[ -f "$NAMESPACE_YAML" ]]; then
    kubectl apply -f "$NAMESPACE_YAML"
    ok "Namespace 'genaiops' created from repo manifest"
else
    kubectl create namespace genaiops --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace genaiops risk_class=high --overwrite
    ok "Namespace 'genaiops' created with risk_class=high label"
fi

# ── Add Helm repos ─────────────────────────────────────────────
log "Adding Helm repositories..."

helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts 2>/dev/null || true
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo add argo https://argoproj.github.io/argo-helm 2>/dev/null || true
helm repo update

ok "Helm repositories added and updated"

# ── Verify cluster health ──────────────────────────────────────
log "Verifying cluster health..."

kubectl cluster-info
echo ""
kubectl get nodes
echo ""

# Wait for system pods
log "Waiting for system pods to be ready (max 120s)..."
kubectl wait --for=condition=Ready pod --all -n kube-system --timeout=120s 2>/dev/null || warn "Some system pods not ready yet"

ok "Cluster is healthy"

# ── Summary ────────────────────────────────────────────────────
echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  Setup Complete${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  Cluster:     $PROFILE"
echo -e "  Namespace:   genaiops (risk_class=high)"
echo -e "  Helm repos:  gatekeeper, prometheus-community, argo"
echo ""
echo -e "  ${BOLD}Next steps:${RESET}"
echo -e "  1. ${BLUE}./infrastructure/scripts/install-gatekeeper.sh${RESET}"
echo -e "  2. ${BLUE}./infrastructure/scripts/deploy-app.sh${RESET}"
echo -e "  3. ${BLUE}./infrastructure/scripts/smoke-test.sh${RESET}"
echo ""
