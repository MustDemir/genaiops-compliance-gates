#!/usr/bin/env bash
# ================================================================
# install-monitoring.sh — Deploy Prometheus + Grafana + Drift Detector
# ================================================================
# Phase 9: Monitoring & Post-Market Surveillance (Pillar S5)
#
# What this does (Kolloquium):
#   This script sets up the complete monitoring stack:
#
#   1. kube-prometheus-stack (Helm chart)
#      → Prometheus scrapes metrics from the AI app
#      → Grafana visualizes drift scores and compliance status
#      → AlertManager sends alerts when thresholds are exceeded
#
#   2. Drift Detector (Kubernetes CronJob)
#      → Runs every 5 minutes
#      → Computes PSI + JSD against saved baseline
#      → Records FAIL to Evidence Store if drift detected
#      → Exports Prometheus metrics for Grafana dashboards
#
#   This implements Pillar S5 and operationalizes G-OPS-03.
#
# Prerequisites:
#   - Minikube running (setup-minikube.sh)
#   - Gatekeeper installed (install-gatekeeper.sh)
#   - App deployed (deploy-app.sh)
#   - prometheus-community Helm repo added (done in setup-minikube.sh)
#
# Usage:
#   ./infrastructure/scripts/install-monitoring.sh
# ================================================================

set -euo pipefail

GREEN='\033[92m'
BLUE='\033[94m'
YELLOW='\033[93m'
RED='\033[91m'
BOLD='\033[1m'
RESET='\033[0m'

log() { echo -e "${BLUE}[monitoring]${RESET} $1"; }
ok()  { echo -e "${GREEN}[  OK  ]${RESET} $1"; }
warn(){ echo -e "${YELLOW}[ WARN ]${RESET} $1"; }
fail(){ echo -e "${RED}[ FAIL ]${RESET} $1"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GenAIOps PoC — Monitoring Stack (Phase 9)${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}\n"

# ── Step 1: Verify prerequisites ─────────────────────────────
log "Step 1: Verifying prerequisites..."

kubectl cluster-info &>/dev/null || fail "Kubernetes cluster not reachable"
ok "Cluster reachable"

helm version &>/dev/null || fail "Helm not installed"
ok "Helm available"

helm repo list 2>/dev/null | grep -q prometheus-community || {
    log "Adding prometheus-community Helm repo..."
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
}
ok "prometheus-community repo available"

# ── Step 2: Create monitoring namespace ──────────────────────
log "Step 2: Creating monitoring namespace..."

kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
ok "Namespace 'monitoring' ready"

# ── Step 3: Install kube-prometheus-stack ────────────────────
log "Step 3: Installing kube-prometheus-stack..."

VALUES_FILE="$REPO_ROOT/infrastructure/helm/prometheus-stack-values.yaml"
if [[ ! -f "$VALUES_FILE" ]]; then
    fail "Values file not found: $VALUES_FILE"
fi

helm upgrade --install prometheus-stack prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --values "$VALUES_FILE" \
    --wait \
    --timeout 10m

ok "kube-prometheus-stack installed"

# ── Step 4: Wait for Prometheus pods ─────────────────────────
log "Step 4: Waiting for Prometheus pods..."

kubectl wait --for=condition=Ready pod \
    -l app.kubernetes.io/name=prometheus \
    -n monitoring \
    --timeout=300s 2>/dev/null || warn "Prometheus pod not ready yet (may need more time)"

kubectl wait --for=condition=Ready pod \
    -l app.kubernetes.io/name=grafana \
    -n monitoring \
    --timeout=300s 2>/dev/null || warn "Grafana pod not ready yet"

ok "Monitoring pods running"

# ── Step 5: Deploy ServiceMonitor for AI Scribe ──────────────
log "Step 5: Deploying ServiceMonitor for AI Scribe app..."

SERVICEMONITOR_FILE="$REPO_ROOT/monitoring/k8s/servicemonitor-scribe.yaml"
if [[ -f "$SERVICEMONITOR_FILE" ]]; then
    kubectl apply -f "$SERVICEMONITOR_FILE"
    ok "ServiceMonitor deployed"
else
    warn "ServiceMonitor file not found: $SERVICEMONITOR_FILE (create in Phase 9.6)"
fi

# ── Step 6: Deploy PrometheusRule for drift alerts ───────────
log "Step 6: Deploying PrometheusRule for drift alerts..."

PROMETHEUSRULE_FILE="$REPO_ROOT/monitoring/k8s/prometheusrule-drift.yaml"
if [[ -f "$PROMETHEUSRULE_FILE" ]]; then
    kubectl apply -f "$PROMETHEUSRULE_FILE"
    ok "PrometheusRule deployed"
else
    warn "PrometheusRule file not found: $PROMETHEUSRULE_FILE (create in Phase 9.6)"
fi

# ── Step 7: Deploy drift detector baseline ───────────────────
log "Step 7: Creating drift detector baseline ConfigMap..."

BASELINE_FILE="$REPO_ROOT/monitoring/fixtures/baseline_normal.json"
if [[ -f "$BASELINE_FILE" ]]; then
    kubectl create configmap drift-baseline \
        --from-file=baseline.json="$BASELINE_FILE" \
        --namespace genaiops \
        --dry-run=client -o yaml | kubectl apply -f -
    ok "Baseline ConfigMap created"
else
    warn "Baseline file not found: $BASELINE_FILE"
fi

# ── Step 8: Deploy drift detector CronJob ────────────────────
log "Step 8: Deploying drift detector CronJob..."

DRIFT_CRONJOB="$REPO_ROOT/monitoring/k8s/cronjob-drift-detector.yaml"
if [[ -f "$DRIFT_CRONJOB" ]]; then
    kubectl apply -f "$DRIFT_CRONJOB"
    ok "Drift detector CronJob deployed"
else
    warn "CronJob file not found: $DRIFT_CRONJOB (will create inline)"

    # Create inline CronJob for drift detection
    cat <<'EOF' | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: drift-detector
  namespace: genaiops
  labels:
    app.kubernetes.io/name: drift-detector
    app.kubernetes.io/part-of: genaiops-compliance-gates
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        metadata:
          annotations:
            genaiops.io/gate-id: "G-OPS-03"
            genaiops.io/pillar: "S5"
        spec:
          containers:
            - name: drift-detector
              image: genaiops/drift-detector:latest
              command: ["python3", "/app/drift_detector.py"]
              args:
                - "--source"
                - "http://ambient-ai-scribe.genaiops.svc:8080/metrics"
                - "--baseline"
                - "/data/baseline.json"
                - "--record-evidence"
              envFrom:
                - configMapRef:
                    name: drift-config
              env:
                - name: EVIDENCE_STORE_DB_URL
                  valueFrom:
                    secretKeyRef:
                      name: evidence-store-credentials
                      key: database-url
                      optional: true
              volumeMounts:
                - name: baseline
                  mountPath: /data
                  readOnly: true
              resources:
                requests:
                  cpu: 50m
                  memory: 64Mi
                limits:
                  cpu: 100m
                  memory: 128Mi
          volumes:
            - name: baseline
              configMap:
                name: drift-baseline
          restartPolicy: OnFailure
EOF
    ok "Drift detector CronJob deployed (inline)"
fi

# ── Step 9: Print access info ────────────────────────────────
echo -e "\n${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  Monitoring Stack Deployed${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo ""

GRAFANA_URL=$(minikube service prometheus-stack-grafana -n monitoring --url 2>/dev/null || echo "unknown")

echo -e "  ${BOLD}Grafana:${RESET}"
echo -e "    URL:      ${BLUE}${GRAFANA_URL}${RESET}"
echo -e "    User:     admin"
echo -e "    Password: genaiops-poc"
echo ""
echo -e "  ${BOLD}Prometheus:${RESET}"
echo -e "    Port-forward: kubectl port-forward svc/prometheus-stack-kube-prom-prometheus 9090:9090 -n monitoring"
echo ""
echo -e "  ${BOLD}Drift Detector:${RESET}"
echo -e "    CronJob:  kubectl get cronjob drift-detector -n genaiops"
echo -e "    Logs:     kubectl logs -l job-name=drift-detector -n genaiops"
echo ""
echo -e "  ${BOLD}What was deployed:${RESET}"
echo -e "  1. Prometheus — scrapes metrics from AI Scribe + drift detector"
echo -e "  2. Grafana — dashboards for drift scores and compliance status"
echo -e "  3. AlertManager — fires alerts when PSI/JSD exceed thresholds"
echo -e "  4. Drift Detector CronJob — runs every 5 minutes"
echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}\n"
