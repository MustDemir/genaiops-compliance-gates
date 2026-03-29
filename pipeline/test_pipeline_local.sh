#!/usr/bin/env bash
# ================================================================
# test_pipeline_local.sh — Local simulation of GitHub Actions pipeline
# ================================================================
# Simulates the gate-pipeline.yml workflow locally without GitHub.
# Requires: conftest (installed), python3
#
# Usage:
#   ./pipeline/test_pipeline_local.sh              # Green Path (PASS)
#   ./pipeline/test_pipeline_local.sh --red-path    # Red Path (FAIL)
#   ./pipeline/test_pipeline_local.sh --dry-run     # No Evidence recording
#
# Exit codes:
#   0 = All gates PASS (Green Path)
#   1 = At least one gate FAIL (Red Path)
# ================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCENARIO_DIR="$REPO_ROOT/scenarios/healthcare-ambient-ai-scribe"
EVIDENCE_DB="/tmp/evidence_pipeline_local_test.db"
PIPELINE_RUN_ID="local-$(date +%Y%m%d-%H%M%S)-$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
COMMIT_SHA=$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo "local-no-git")

# ── Parse args ──
RED_PATH=false
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --red-path) RED_PATH=true ;;
    --dry-run)  DRY_RUN=true ;;
    *)          echo "Unknown arg: $arg"; exit 2 ;;
  esac
done

# ── Colors ──
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GenAIOps Quality Gate Pipeline — Local Test         ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║  Run ID: ${PIPELINE_RUN_ID}${NC}"
echo -e "${BLUE}║  Commit: ${COMMIT_SHA::8}${NC}"
echo -e "${BLUE}║  Mode:   $([ "$RED_PATH" = true ] && echo 'RED PATH (expect FAIL)' || echo 'GREEN PATH')${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Check conftest ──
if ! command -v conftest &> /dev/null; then
  echo -e "${RED}ERROR: conftest not found. Install: brew install conftest${NC}"
  exit 2
fi

# ── Select fixtures ──
if [ "$RED_PATH" = true ]; then
  RISK_FIXTURE="$SCENARIO_DIR/fixtures/app_documentation_incomplete.json"
  SECURITY_FIXTURE="$SCENARIO_DIR/fixtures/deployment_noncompliant.yaml"
  GOVERNANCE_FIXTURE="$SCENARIO_DIR/fixtures/app_documentation_incomplete.json"
  SAFETY_FIXTURE="$SCENARIO_DIR/fixtures/eval_results_fail.json"
  BIAS_FIXTURE="$SCENARIO_DIR/fixtures/model_documentation_bias_fail.json"
  PROVENANCE_FIXTURE="$SCENARIO_DIR/fixtures/data_documentation_provenance_fail.json"
  TRANSPARENCY_FIXTURE="$SCENARIO_DIR/fixtures/app_documentation_transparency_fail.json"
  INCIDENT_FIXTURE="$SCENARIO_DIR/fixtures/deployment_incident_fail.json"
  MONITORING_FIXTURE="$SCENARIO_DIR/fixtures/admission_review_noncompliant.json"
  EVIDENCE_FIXTURE="$SCENARIO_DIR/fixtures/admission_review_noncompliant.json"
else
  RISK_FIXTURE="$SCENARIO_DIR/fixtures/app_documentation.json"
  SECURITY_FIXTURE="$SCENARIO_DIR/fixtures/deployment_compliant.yaml"
  GOVERNANCE_FIXTURE="$SCENARIO_DIR/fixtures/app_documentation.json"
  SAFETY_FIXTURE="$SCENARIO_DIR/fixtures/eval_results.json"
  BIAS_FIXTURE="$SCENARIO_DIR/fixtures/model_documentation_bias_pass.json"
  PROVENANCE_FIXTURE="$SCENARIO_DIR/fixtures/data_documentation_provenance_pass.json"
  TRANSPARENCY_FIXTURE="$SCENARIO_DIR/fixtures/app_documentation_transparency_pass.json"
  INCIDENT_FIXTURE="$SCENARIO_DIR/fixtures/deployment_incident_pass.json"
  MONITORING_FIXTURE="$SCENARIO_DIR/fixtures/admission_review_compliant.json"
  EVIDENCE_FIXTURE="$SCENARIO_DIR/fixtures/admission_review_compliant.json"
fi

# ── Gate execution function ──
TOTAL_PASS=0
TOTAL_FAIL=0

run_gate() {
  local GATE_ID="$1"
  local GATE_NAME="$2"
  local POLICY="$3"
  local FIXTURE="$4"
  local REQ_ID="$5"
  local NAMESPACE="$6"

  echo -e "${BLUE}── $GATE_ID: $GATE_NAME ──${NC}"
  echo "   Policy:  $POLICY"
  echo "   Fixture: $(basename "$FIXTURE")"

  set +e
  OUTPUT=$(conftest test "$FIXTURE" --policy "$REPO_ROOT/$POLICY" --namespace "$NAMESPACE" --no-color --output json 2>&1)
  EXIT_CODE=$?
  set -e

  FAILURES=$(echo "$OUTPUT" | python3 -c "
import json, sys
try:
  data = json.load(sys.stdin)
  failures = sum(len(r.get('failures', [])) for r in data)
  print(failures)
except:
  print(-1)
" 2>/dev/null)

  if [ "$FAILURES" = "0" ]; then
    echo -e "   ${GREEN}✅ $GATE_ID PASS${NC}"
    TOTAL_PASS=$((TOTAL_PASS + 1))
    DECISION="PASS"
  else
    echo -e "   ${RED}❌ $GATE_ID FAIL${NC}"
    # Show failure messages
    echo "$OUTPUT" | python3 -c "
import json, sys
try:
  data = json.load(sys.stdin)
  for r in data:
    for f in r.get('failures', []):
      print(f'      → {f[\"msg\"]}')
except:
  pass
" 2>/dev/null
    TOTAL_FAIL=$((TOTAL_FAIL + 1))
    DECISION="FAIL"
  fi

  # Record evidence (unless --dry-run)
  if [ "$DRY_RUN" = false ]; then
    # Create temp JSON source for record_evidence.py
    local EVIDENCE_SOURCE="/tmp/evidence_${GATE_ID,,}.json"
    echo "{\"pipeline_run_id\": \"$PIPELINE_RUN_ID\", \"commit_sha\": \"$COMMIT_SHA\", \"gate_id\": \"$GATE_ID\", \"requirement_id\": \"$REQ_ID\", \"decision\": \"$DECISION\", \"conftest_failures\": $FAILURES}" > "$EVIDENCE_SOURCE"

    python3 "$REPO_ROOT/evidence-store/scripts/record_evidence.py" \
      --sqlite "$EVIDENCE_DB" \
      --gate "$GATE_ID" \
      --method "AUTO" \
      --source "$EVIDENCE_SOURCE" \
      2>/dev/null && echo -e "   ${YELLOW}📦 Evidence recorded${NC}" \
                 || echo -e "   ${YELLOW}⚠️  Evidence recording skipped${NC}"
  fi
  echo ""
}

# ── Run all 10 gates (7 Conftest + 3 Gatekeeper simulation) ──
echo -e "${BLUE}━━━ Pre-Deployment Gates ━━━${NC}"
echo ""

run_gate "G-PRE-01" "Risk Classification"    "policies/pre-deployment/policy_risk_classification.rego"       "$RISK_FIXTURE"       "R001" "genaiops.pre_deployment.risk_classification"
run_gate "G-PRE-04" "Security Baseline"       "policies/pre-deployment/policy_security_baseline.rego"         "$SECURITY_FIXTURE"   "R003" "genaiops.pre_deployment.security_baseline"
run_gate "G-PRE-05" "Governance Approval"     "policies/pre-deployment/policy_governance_approval.rego"       "$GOVERNANCE_FIXTURE" "R012" "genaiops.pre_deployment.governance_approval"
run_gate "G-DEP-05" "Bias Assessment"         "policies/pre-deployment/policy_bias_assessment_complete.rego"  "$BIAS_FIXTURE"       "R013" "genaiops.pre_deployment.bias_assessment_complete"
run_gate "G-DEP-01" "Data Provenance"         "policies/pre-deployment/policy_data_provenance_documented.rego" "$PROVENANCE_FIXTURE" "R002" "genaiops.pre_deployment.data_provenance_documented"

echo -e "${BLUE}━━━ Deployment Gates ━━━${NC}"
echo ""

run_gate "G-DEP-02" "Safety Metrics"          "policies/deployment/policy_safety_metrics.rego"                "$SAFETY_FIXTURE"       "R003" "genaiops.deployment.safety_metrics"
run_gate "G-DEP-03" "Transparency Docs"       "policies/deployment/policy_transparency_docs_present.rego"     "$TRANSPARENCY_FIXTURE" "R007" "genaiops.deployment.transparency_docs_present"

echo -e "${BLUE}━━━ Operations Gates (Gatekeeper simulation) ━━━${NC}"
echo ""

run_gate "G-OPS-03" "Monitoring Config"       "policies/operations/policy_monitoring_configured.rego"         "$MONITORING_FIXTURE"   "R010" "genaiops.operations.monitoring_configured"
run_gate "G-OPS-05" "Evidence Completeness"   "policies/operations/policy_evidence_completeness.rego"         "$EVIDENCE_FIXTURE"     "R005" "genaiops.operations.evidence_completeness"
run_gate "G-OPS-02" "Incident Process"        "policies/operations/policy_incident_process_exists.rego"       "$INCIDENT_FIXTURE"     "R009" "genaiops.operations.incident_process_exists"

# ── Hash chain verification ──
if [ "$DRY_RUN" = false ]; then
  echo -e "${BLUE}━━━ Hash Chain Verification (S4 + DP5) ━━━${NC}"
  echo ""
  python3 "$REPO_ROOT/evidence-store/scripts/verify_hash_chain.py" \
    --sqlite "$EVIDENCE_DB" 2>/dev/null \
    && echo -e "   ${GREEN}🔗 Hash chain VALID${NC}" \
    || echo -e "   ${YELLOW}⚠️  Hash chain verification skipped${NC}"
  echo ""
fi

# ── Summary ──
TOTAL=$((TOTAL_PASS + TOTAL_FAIL))

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Pipeline Summary                                     ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║  Gates: $TOTAL_PASS/$TOTAL PASS, $TOTAL_FAIL/$TOTAL FAIL${NC}"

if [ "$TOTAL_FAIL" -eq 0 ]; then
  echo -e "${GREEN}║  DECISION: ✅ ALL GATES PASSED — Deploy authorized       ║${NC}"
  echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
  echo ""
  exit 0
else
  echo -e "${RED}║  DECISION: ❌ GATE FAILURE — Deploy BLOCKED              ║${NC}"
  echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
  echo ""
  exit 1
fi
