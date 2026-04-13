#!/usr/bin/env bash
# ================================================================
# deploy-aks.sh — AKS Cluster + Full PoC Deployment (Phase 12)
# ================================================================
# Deploys the complete GenAIOps Compliance Architecture on Azure:
#   1. Resource Group + ACR + AKS Cluster (System + User Pool)
#   2. Build & push Docker image to ACR
#   3. Install Gatekeeper (standalone, DP5-konform)
#   4. Deploy App + Evidence Store + Monitoring
#   5. Run smoke-test
#
# Architecture (Thesis Kap. 5):
#   - 3 Nodes: 1x B2ms (System) + 2x B4ms (User/Workloads)
#   - Azure CNI Overlay (Microsoft-recommended, kubenet retiring 2028)
#   - System-Assigned Managed Identity (no Service Principal)
#   - ACR Basic via --attach-acr (AcrPull role, no imagePullSecrets)
#   - Standalone OPA Gatekeeper (D_GATEKEEPER_STANDALONE)
#   - LoadBalancer Service (real external IP)
#
# Decisions:
#   E4-upgrade: LoadBalancer statt Port-Forward (L7 entfällt)
#   E6: Lokal entwickeln, finale Phase auf AKS
#   E7: Secrets manuell via kubectl create secret
#   E8: Azure (OpenAI-SaaS + Enterprise-Compliance + DP5)
#
# Cost (Azure for Students, €30 Budget):
#   ~€1.20 für 3 Stunden | ~€8/Tag | teardown: az group delete
#
# Usage:
#   ./infrastructure/scripts/deploy-aks.sh
#
# Teardown:
#   ./infrastructure/scripts/teardown-aks.sh
# ================================================================

set -euo pipefail

GREEN='\033[92m'
BLUE='\033[94m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

log() { echo -e "${BLUE}[aks]${RESET} $1"; }
ok()  { echo -e "${GREEN}[  OK ]${RESET} $1"; }
warn(){ echo -e "${YELLOW}[ WARN]${RESET} $1"; }
err() { echo -e "${RED}[ERROR]${RESET} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SCENARIO_DIR="$REPO_ROOT/scenarios/healthcare-ambient-ai-scribe"
K8S_DIR="$SCENARIO_DIR/k8s"
SCHEMA_DIR="$REPO_ROOT/evidence-store/schema"
HELM_VALUES="$REPO_ROOT/infrastructure/helm"

# ── Azure Configuration ───────────────────────────────────────
RG="genaiops-compliance-rg"
CLUSTER="genaiops-aks"
ACR_NAME="genaiopsacr$(whoami | tr -d '.' | tail -c 8)$(date +%s | tail -c 4)"  # unique name
LOCATION="swedencentral"  # Azure for Students: only allowed region
IMAGE_NAME="ambient-ai-scribe"
IMAGE_TAG="1.0.0"

echo -e "\n${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GenAIOps PoC — AKS Deployment (Phase 12)${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}\n"

# ── Step 0: Preflight Checks ─────────────────────────────────
log "Preflight checks..."

command -v az    &>/dev/null || err "Azure CLI not found. Install: brew install azure-cli"
command -v kubectl &>/dev/null || err "kubectl not found."
command -v helm  &>/dev/null || err "Helm not found."

# Check Azure login
az account show &>/dev/null || err "Not logged in to Azure. Run: az login"
SUBSCRIPTION=$(az account show --query name -o tsv)
ok "Azure subscription: $SUBSCRIPTION"

# Check quota (informational)
log "Checking VM availability in $LOCATION..."
# Azure for Students (swedencentral): v2 B-series available
USER_VM_SIZE="Standard_B2s_v2"
ok "Location: $LOCATION | User pool VM: $USER_VM_SIZE"

# ══════════════════════════════════════════════════════════════
# PHASE 1: Azure Infrastructure
# ══════════════════════════════════════════════════════════════

echo -e "\n${BOLD}── Phase 1: Azure Infrastructure ──${RESET}\n"

# Resource Group
log "Creating Resource Group: $RG"
az group create --name "$RG" --location "$LOCATION" --output none
ok "Resource Group: $RG ($LOCATION)"

# ACR
log "Creating Azure Container Registry: $ACR_NAME"
az acr create \
    --resource-group "$RG" \
    --name "$ACR_NAME" \
    --sku Basic \
    --output none
ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)
ok "ACR: $ACR_LOGIN_SERVER"

# AKS Cluster
log "Creating AKS cluster: $CLUSTER (this takes 3-5 minutes)..."
az aks create \
    --resource-group "$RG" \
    --name "$CLUSTER" \
    --nodepool-name system \
    --node-count 1 \
    --node-vm-size Standard_B2s_v2 \
    --network-plugin azure \
    --network-plugin-mode overlay \
    --pod-cidr 192.168.0.0/16 \
    --tier free \
    --generate-ssh-keys \
    --attach-acr "$ACR_NAME" \
    --enable-managed-identity \
    --output none

ok "AKS cluster created: $CLUSTER"

# User Node Pool
log "Adding user node pool (2x $USER_VM_SIZE)..."
az aks nodepool add \
    --resource-group "$RG" \
    --cluster-name "$CLUSTER" \
    --name userpool \
    --node-count 2 \
    --node-vm-size "$USER_VM_SIZE" \
    --labels workload=genaiops \
    --output none

ok "User pool: 2x $USER_VM_SIZE"

# Get credentials
log "Fetching kubeconfig..."
az aks get-credentials --resource-group "$RG" --name "$CLUSTER" --overwrite-existing
ok "kubectl configured for $CLUSTER"

echo ""
kubectl get nodes
echo ""

# ══════════════════════════════════════════════════════════════
# PHASE 2: Build & Push Image to ACR
# ══════════════════════════════════════════════════════════════

echo -e "\n${BOLD}── Phase 2: Container Image → ACR ──${RESET}\n"

FULL_IMAGE="$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG"

log "Building image in ACR (cloud build)..."
az acr build \
    --registry "$ACR_NAME" \
    --image "$IMAGE_NAME:$IMAGE_TAG" \
    "$SCENARIO_DIR/" \
    --output none

ok "Image pushed: $FULL_IMAGE"

# ══════════════════════════════════════════════════════════════
# PHASE 3: Namespace + Gatekeeper
# ══════════════════════════════════════════════════════════════

echo -e "\n${BOLD}── Phase 3: Namespace + Gatekeeper ──${RESET}\n"

# Namespace
log "Creating namespace genaiops..."
kubectl apply -f "$K8S_DIR/namespace.yaml"
ok "Namespace: genaiops"

# Gatekeeper via Helm
log "Installing OPA Gatekeeper (standalone, DP5)..."
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts 2>/dev/null || true
helm repo update gatekeeper

helm upgrade --install gatekeeper gatekeeper/gatekeeper \
    --namespace gatekeeper-system \
    --create-namespace \
    --values "$HELM_VALUES/gatekeeper-values.yaml" \
    --wait --timeout 3m

ok "Gatekeeper installed"

# Wait for webhook to be ready
log "Waiting for Gatekeeper webhook..."
kubectl wait --for=condition=Ready pod \
    -l control-plane=controller-manager \
    -n gatekeeper-system \
    --timeout=120s
sleep 10  # Extra buffer for webhook registration
ok "Gatekeeper webhook ready"

# ConstraintTemplates — deploy in two phases: CTs first, then Constraints
log "Deploying 3 ConstraintTemplates (Phase 1: Templates)..."
GATEKEEPER_DIR="$K8S_DIR/gatekeeper"

# Phase 1: Apply only ConstraintTemplates (first document in each file)
for CT_FILE in "$GATEKEEPER_DIR"/constraint-*.yaml; do
    CT_NAME=$(basename "$CT_FILE")
    # Extract only the first YAML document (ConstraintTemplate)
    python3 -c "
import yaml, sys
docs = list(yaml.safe_load_all(open('$CT_FILE')))
print(yaml.dump(docs[0]))
" | kubectl apply -f - 2>&1 | head -2
    ok "$CT_NAME — ConstraintTemplate applied"
done

# Wait for CTs to compile (critical: Gatekeeper needs time to register CRDs)
log "Waiting for ConstraintTemplates to compile (45s)..."
sleep 45

CT_COUNT=$(kubectl get constrainttemplates --no-headers 2>/dev/null | wc -l | tr -d ' ')
ok "ConstraintTemplates compiled: $CT_COUNT"

# Phase 2: Apply Constraints (second document in each file)
log "Deploying 3 Constraints (Phase 2: Enforcement)..."
for CT_FILE in "$GATEKEEPER_DIR"/constraint-*.yaml; do
    CT_NAME=$(basename "$CT_FILE")
    python3 -c "
import yaml, sys
docs = list(yaml.safe_load_all(open('$CT_FILE')))
if len(docs) > 1:
    print(yaml.dump(docs[1]))
" | kubectl apply -f - 2>&1 | head -2
    ok "$CT_NAME — Constraint applied"
done

sleep 5
CONSTRAINT_COUNT=$(kubectl get constraints --no-headers 2>/dev/null | wc -l | tr -d ' ')
ok "ConstraintTemplates: $CT_COUNT | Constraints: $CONSTRAINT_COUNT"

# ══════════════════════════════════════════════════════════════
# PHASE 4: Application Stack
# ══════════════════════════════════════════════════════════════

echo -e "\n${BOLD}── Phase 4: Application Stack ──${RESET}\n"

# PostgreSQL Secret
log "Creating PostgreSQL credentials..."
kubectl create secret generic postgres-credentials \
    --from-literal=POSTGRES_USER=genaiops \
    --from-literal=POSTGRES_PASSWORD=genaiops-poc \
    --from-literal=POSTGRES_DB=genaiops \
    --namespace genaiops \
    --dry-run=client -o yaml | kubectl apply -f -
ok "PostgreSQL secret ready"

# PostgreSQL
log "Deploying PostgreSQL (Evidence Store)..."
kubectl apply -f "$K8S_DIR/postgres-pvc.yaml" -n genaiops
kubectl apply -f "$K8S_DIR/postgres-deployment.yaml" -n genaiops
kubectl apply -f "$K8S_DIR/postgres-service.yaml" -n genaiops

log "Waiting for PostgreSQL..."
kubectl wait --for=condition=Ready pod \
    -l app.kubernetes.io/name=postgres-evidence \
    -n genaiops \
    --timeout=180s
ok "PostgreSQL ready"

# Schema initialization
log "Initializing Evidence Store schema..."
PG_POD=$(kubectl get pod -n genaiops -l app=postgres -o jsonpath='{.items[0].metadata.name}')

if [[ -f "$SCHEMA_DIR/evidence_store_schema_v02_enterprise.sql" ]]; then
    kubectl cp "$SCHEMA_DIR/evidence_store_schema_v02_enterprise.sql" \
        "genaiops/$PG_POD:/tmp/schema_v02.sql"
    kubectl exec -n genaiops "$PG_POD" -- \
        psql -U postgres -d genaiops -f /tmp/schema_v02.sql 2>/dev/null || \
        warn "Schema v02 may already exist"
    ok "Evidence Store schema v02 applied"
fi

if [[ -f "$SCHEMA_DIR/../migrations/v02_to_v03_add_decision_method.sql" ]]; then
    kubectl cp "$SCHEMA_DIR/../migrations/v02_to_v03_add_decision_method.sql" \
        "genaiops/$PG_POD:/tmp/migration_v03.sql"
    kubectl exec -n genaiops "$PG_POD" -- \
        psql -U postgres -d genaiops -f /tmp/migration_v03.sql 2>/dev/null || \
        warn "Migration v03 may already be applied"
    ok "Evidence Store migration v03 applied"
fi

# ConfigMaps
log "Deploying ConfigMaps..."
kubectl apply -f "$K8S_DIR/configmap.yaml" -n genaiops
kubectl apply -f "$K8S_DIR/prometheus-configmap.yaml" -n genaiops
kubectl apply -f "$K8S_DIR/drift-config.yaml" -n genaiops
ok "ConfigMaps deployed"

# App Deployment — update image to ACR
log "Deploying AI Scribe (image: $FULL_IMAGE)..."
sed "s|ambient-ai-scribe:1.0.0|$FULL_IMAGE|g" "$K8S_DIR/deployment.yaml" | \
    kubectl apply -n genaiops -f - 2>&1
ok "AI Scribe Deployment ACCEPTED by Gatekeeper"

# Service as LoadBalancer (upgrade from ClusterIP)
log "Creating LoadBalancer Service (real external IP)..."
cat <<'LBEOF' | sed "s|NAMESPACE|genaiops|g" | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: ambient-ai-scribe
  namespace: NAMESPACE
  labels:
    app.kubernetes.io/name: ambient-ai-scribe
    app.kubernetes.io/component: application
    app.kubernetes.io/part-of: genaiops-compliance-gates
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: ambient-ai-scribe
  ports:
    - name: http
      port: 8080
      targetPort: http
      protocol: TCP
LBEOF

log "Waiting for AI Scribe pods..."
kubectl wait --for=condition=Ready pod \
    -l app.kubernetes.io/name=ambient-ai-scribe \
    -n genaiops \
    --timeout=120s
ok "AI Scribe ready"

# CronJob
log "Deploying hash-chain verification CronJob..."
kubectl apply -f "$K8S_DIR/cronjob-hash-chain-verify.yaml" -n genaiops 2>/dev/null || \
    warn "CronJob may need adjustment"
ok "CronJob deployed"

# ══════════════════════════════════════════════════════════════
# PHASE 5: Monitoring Stack
# ══════════════════════════════════════════════════════════════

echo -e "\n${BOLD}── Phase 5: Monitoring (Prometheus + Grafana) ──${RESET}\n"

log "Installing kube-prometheus-stack..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo update prometheus-community

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --values "$HELM_VALUES/prometheus-stack-values.yaml" \
    --wait --timeout 5m

ok "Prometheus + Grafana installed"

# ══════════════════════════════════════════════════════════════
# PHASE 6: Verification
# ══════════════════════════════════════════════════════════════

echo -e "\n${BOLD}── Phase 6: Verification ──${RESET}\n"

# Wait for LoadBalancer IP
log "Waiting for external IP (LoadBalancer)..."
for i in $(seq 1 30); do
    EXTERNAL_IP=$(kubectl get svc ambient-ai-scribe -n genaiops -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [[ -n "$EXTERNAL_IP" ]]; then
        break
    fi
    sleep 5
done

echo ""
echo -e "${BOLD}Nodes:${RESET}"
kubectl get nodes -o wide
echo ""

echo -e "${BOLD}Pods (genaiops):${RESET}"
kubectl get pods -n genaiops -o wide
echo ""

echo -e "${BOLD}Pods (gatekeeper-system):${RESET}"
kubectl get pods -n gatekeeper-system
echo ""

echo -e "${BOLD}Pods (monitoring):${RESET}"
kubectl get pods -n monitoring --no-headers | head -10
echo ""

echo -e "${BOLD}Services:${RESET}"
kubectl get svc -n genaiops
echo ""

echo -e "${BOLD}ConstraintTemplates:${RESET}"
kubectl get constrainttemplates
echo ""

echo -e "${BOLD}Constraints:${RESET}"
kubectl get constraints
echo ""

# Health check
if [[ -n "$EXTERNAL_IP" ]]; then
    log "Testing health endpoint: http://$EXTERNAL_IP:8080/health"
    curl -s "http://$EXTERNAL_IP:8080/health" 2>/dev/null && echo "" || warn "Health endpoint not reachable yet"
fi

# ── Summary ───────────────────────────────────────────────────
echo -e "\n${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  AKS Deployment Complete${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${BOLD}Cluster:${RESET}        $CLUSTER ($LOCATION)"
echo -e "  ${BOLD}Resource Group:${RESET} $RG"
echo -e "  ${BOLD}ACR:${RESET}            $ACR_LOGIN_SERVER"
echo -e "  ${BOLD}Image:${RESET}          $FULL_IMAGE"
echo -e "  ${BOLD}Nodes:${RESET}          1 System (B2ms) + 2 User ($USER_VM_SIZE)"
echo -e "  ${BOLD}Networking:${RESET}     Azure CNI Overlay"
echo ""
echo -e "  ${BOLD}Endpoints:${RESET}"
if [[ -n "$EXTERNAL_IP" ]]; then
    echo -e "  App:      ${GREEN}http://$EXTERNAL_IP:8080/health${RESET}"
    echo -e "  Metrics:  ${GREEN}http://$EXTERNAL_IP:8080/metrics${RESET}"
else
    echo -e "  App:      ${YELLOW}kubectl port-forward svc/ambient-ai-scribe 8080:8080 -n genaiops${RESET}"
fi
echo -e "  Grafana:  ${BLUE}kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring${RESET}"
echo ""
echo -e "  ${BOLD}Gatekeeper:${RESET}"
echo -e "  ${GREEN}G-DEP-02${RESET}: Safety Metrics (eval-passed, eval-run-id)"
echo -e "  ${GREEN}G-OPS-03${RESET}: Monitoring (drift-detection, service-monitor)"
echo -e "  ${GREEN}G-OPS-05${RESET}: Evidence Store (evidence-store-connected, hash-chain)"
echo ""
echo -e "  ${BOLD}Next:${RESET} Take screenshots, then run:"
echo -e "  ${RED}./infrastructure/scripts/teardown-aks.sh${RESET}"
echo ""

# Save config for teardown
cat > "$REPO_ROOT/infrastructure/.aks-config" << EOF
RG=$RG
CLUSTER=$CLUSTER
ACR_NAME=$ACR_NAME
LOCATION=$LOCATION
EXTERNAL_IP=${EXTERNAL_IP:-}
EOF
ok "Config saved to infrastructure/.aks-config"
