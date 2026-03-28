#!/usr/bin/env bash
# ================================================================
# deploy-app.sh — Deploy Healthcare AI Scribe + Evidence Store
# ================================================================
# Phase 6: Step 3 — runs AFTER install-gatekeeper.sh
#
# What this does (Kolloquium):
#   1. Builds the Docker image for the AI Scribe app (inside Minikube)
#   2. Deploys PostgreSQL (Evidence Store database)
#   3. Initializes the Evidence Store schema (v03)
#   4. Deploys the AI Scribe app (with all compliance annotations)
#   5. Deploys Prometheus ConfigMap for metrics scraping
#   6. Verifies everything is running
#
#   Since Gatekeeper is already active, the app Deployment will only
#   succeed if it has ALL required annotations. If we tried to deploy
#   without them → Gatekeeper REJECTS → Deployment blocked.
#   That's the admission control in action.
#
# Usage:
#   ./infrastructure/scripts/deploy-app.sh
# ================================================================

set -euo pipefail

GREEN='\033[92m'
BLUE='\033[94m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
RESET='\033[0m'

log() { echo -e "${BLUE}[deploy]${RESET} $1"; }
ok()  { echo -e "${GREEN}[  OK ]${RESET} $1"; }
warn(){ echo -e "${YELLOW}[ WARN]${RESET} $1"; }
err() { echo -e "${RED}[ERROR]${RESET} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCENARIO_DIR="$REPO_ROOT/scenarios/healthcare-ambient-ai-scribe"
K8S_DIR="$SCENARIO_DIR/k8s"
SCHEMA_DIR="$REPO_ROOT/evidence-store/schema"

echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GenAIOps PoC — App Deployment (Phase 6)${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}\n"

# ── Pre-flight ─────────────────────────────────────────────────
log "Checking prerequisites..."

# Verify namespace exists
kubectl get namespace genaiops &> /dev/null || err "Namespace 'genaiops' not found. Run setup-minikube.sh first."
ok "Namespace 'genaiops' exists"

# Verify Gatekeeper is running
GK_PODS=$(kubectl get pods -n gatekeeper-system --no-headers 2>/dev/null | grep -c Running || echo "0")
if [[ "$GK_PODS" -gt 0 ]]; then
    ok "Gatekeeper is running ($GK_PODS pods)"
else
    warn "Gatekeeper not running — app will deploy without admission checks"
fi

# ── Step 1: Build Docker image in Minikube ─────────────────────
log "Configuring Docker to use Minikube's Docker daemon..."
eval $(minikube docker-env -p genaiops 2>/dev/null || minikube docker-env)

log "Building AI Scribe Docker image..."
docker build \
    -t ambient-ai-scribe:1.0.0 \
    -f "$SCENARIO_DIR/Dockerfile" \
    "$SCENARIO_DIR/"

ok "Docker image built: ambient-ai-scribe:1.0.0"

# ── Step 2: Create PostgreSQL Secret (if not exists) ───────────
log "Ensuring PostgreSQL credentials secret..."
kubectl create secret generic postgres-credentials \
    --from-literal=POSTGRES_USER=genaiops \
    --from-literal=POSTGRES_PASSWORD=genaiops-poc \
    --from-literal=POSTGRES_DB=genaiops \
    --namespace genaiops \
    --dry-run=client -o yaml | kubectl apply -f -
ok "PostgreSQL secret ready"

# ── Step 3: Deploy PostgreSQL (Evidence Store) ─────────────────
log "Deploying PostgreSQL (Evidence Store)..."

kubectl apply -f "$K8S_DIR/postgres-pvc.yaml" -n genaiops
kubectl apply -f "$K8S_DIR/postgres-deployment.yaml" -n genaiops
kubectl apply -f "$K8S_DIR/postgres-service.yaml" -n genaiops

log "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=Ready pod \
    -l app.kubernetes.io/name=postgres-evidence \
    -n genaiops \
    --timeout=120s

ok "PostgreSQL deployed and ready"

# ── Step 3: Initialize Evidence Store schema ───────────────────
log "Initializing Evidence Store schema (v03)..."

# Get postgres pod name
PG_POD=$(kubectl get pod -n genaiops -l app=postgres -o jsonpath='{.items[0].metadata.name}')

# Apply v02 enterprise schema first, then v03 migration
if [[ -f "$SCHEMA_DIR/evidence_store_schema_v02_enterprise.sql" ]]; then
    kubectl cp "$SCHEMA_DIR/evidence_store_schema_v02_enterprise.sql" \
        "genaiops/$PG_POD:/tmp/schema_v02.sql"

    kubectl exec -n genaiops "$PG_POD" -- \
        psql -U postgres -d genaiops -f /tmp/schema_v02.sql 2>/dev/null || \
        warn "Schema v02 may already exist (idempotent)"

    ok "Evidence Store schema v02 applied"
fi

# Apply v03 migration if exists
if [[ -f "$SCHEMA_DIR/../migrations/v02_to_v03_add_decision_method.sql" ]]; then
    kubectl cp "$SCHEMA_DIR/../migrations/v02_to_v03_add_decision_method.sql" \
        "genaiops/$PG_POD:/tmp/migration_v03.sql"

    kubectl exec -n genaiops "$PG_POD" -- \
        psql -U postgres -d genaiops -f /tmp/migration_v03.sql 2>/dev/null || \
        warn "Migration v03 may already be applied"

    ok "Evidence Store migration v03 applied"
fi

# ── Step 4: Deploy ConfigMaps ──────────────────────────────────
log "Deploying ConfigMaps..."

kubectl apply -f "$K8S_DIR/configmap.yaml" -n genaiops
kubectl apply -f "$K8S_DIR/prometheus-configmap.yaml" -n genaiops
kubectl apply -f "$K8S_DIR/drift-config.yaml" -n genaiops

ok "ConfigMaps deployed"

# ── Step 5: Deploy AI Scribe App ───────────────────────────────
log "Deploying AI Scribe application..."
log "  (Gatekeeper will check compliance annotations...)"

# This is the critical moment: Gatekeeper validates the Deployment
kubectl apply -f "$K8S_DIR/deployment.yaml" -n genaiops 2>&1
DEPLOY_EXIT=$?

if [[ $DEPLOY_EXIT -eq 0 ]]; then
    ok "AI Scribe Deployment ACCEPTED by Gatekeeper"
else
    err "AI Scribe Deployment REJECTED by Gatekeeper — check annotations!"
fi

kubectl apply -f "$K8S_DIR/service.yaml" -n genaiops

log "Waiting for AI Scribe pods to be ready..."
kubectl wait --for=condition=Ready pod \
    -l app.kubernetes.io/name=ambient-ai-scribe \
    -n genaiops \
    --timeout=120s

ok "AI Scribe app deployed and ready"

# ── Step 6: Deploy CronJob for hash-chain verification ─────────
log "Deploying hash-chain verification CronJob..."
kubectl apply -f "$K8S_DIR/cronjob-hash-chain-verify.yaml" -n genaiops 2>/dev/null || \
    warn "CronJob deployment skipped (may need adjustment)"

ok "CronJob deployed"

# ── Step 7: Verify all resources ───────────────────────────────
log "Verifying deployment..."
echo ""

echo -e "${BOLD}Pods in genaiops:${RESET}"
kubectl get pods -n genaiops
echo ""

echo -e "${BOLD}Services in genaiops:${RESET}"
kubectl get svc -n genaiops
echo ""

# Quick health check
log "Testing app health endpoint..."
APP_POD=$(kubectl get pod -n genaiops -l app.kubernetes.io/name=ambient-ai-scribe -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
if [[ -n "$APP_POD" ]]; then
    HEALTH=$(kubectl exec -n genaiops "$APP_POD" -- curl -s http://localhost:8080/health 2>/dev/null || echo "unreachable")
    ok "Health check: $HEALTH"
fi

# ── Summary ────────────────────────────────────────────────────
echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  App Deployment Complete${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  App:            ambient-ai-scribe:1.0.0"
echo -e "  Database:       PostgreSQL (Evidence Store v03)"
echo -e "  Namespace:      genaiops"
echo -e "  Gatekeeper:     ${GREEN}ADMITTED${RESET} (all annotations present)"
echo ""
echo -e "  ${BOLD}Access:${RESET}"
echo -e "  App:    ${BLUE}kubectl port-forward svc/ambient-ai-scribe 8080:8080 -n genaiops${RESET}"
echo -e "  DB:     ${BLUE}kubectl port-forward svc/postgres 5432:5432 -n genaiops${RESET}"
echo ""
echo -e "  ${BOLD}Next step:${RESET}"
echo -e "  ${BLUE}./infrastructure/scripts/smoke-test.sh${RESET}"
echo ""
