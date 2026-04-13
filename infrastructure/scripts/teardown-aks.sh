#!/usr/bin/env bash
# ================================================================
# teardown-aks.sh — Destroy AKS Cluster + All Azure Resources
# ================================================================
# Deletes the entire Resource Group including:
#   - AKS Cluster (nodes, load balancers, managed disks)
#   - Azure Container Registry
#   - Public IPs, NSGs, VNets (auto-created by AKS)
#
# After running: $0.00/h Azure costs for this PoC.
#
# Usage:
#   ./infrastructure/scripts/teardown-aks.sh
# ================================================================

set -euo pipefail

RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BOLD='\033[1m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$REPO_ROOT/infrastructure/.aks-config"

echo -e "\n${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${RED}${BOLD}  GenAIOps PoC — AKS Teardown${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}\n"

# Load config
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
    echo -e "  Resource Group: ${BOLD}$RG${RESET}"
    echo -e "  Cluster:        ${BOLD}$CLUSTER${RESET}"
    echo -e "  ACR:            ${BOLD}$ACR_NAME${RESET}"
    echo -e "  Location:       ${BOLD}$LOCATION${RESET}"
else
    # Defaults if config not found
    RG="genaiops-compliance-rg"
    echo -e "  ${YELLOW}Config not found, using default: $RG${RESET}"
fi

echo ""
echo -e "  ${RED}${BOLD}This will PERMANENTLY DELETE all resources in $RG.${RESET}"
echo -e "  ${RED}All data (Evidence Store, images, logs) will be lost.${RESET}"
echo ""
read -p "  Type 'yes' to confirm teardown: " CONFIRM

if [[ "$CONFIRM" != "yes" ]]; then
    echo -e "\n  ${YELLOW}Teardown cancelled.${RESET}\n"
    exit 0
fi

echo ""

# Check if resource group exists
if ! az group show --name "$RG" &>/dev/null; then
    echo -e "  ${GREEN}Resource Group $RG does not exist — nothing to delete.${RESET}\n"
    rm -f "$CONFIG_FILE"
    exit 0
fi

# Delete Resource Group (includes everything)
echo -e "  ${RED}Deleting Resource Group $RG (this takes 2-5 minutes)...${RESET}"
az group delete --name "$RG" --yes --no-wait

echo ""
echo -e "  ${GREEN}Deletion initiated (running in background).${RESET}"
echo -e "  Resources will be fully removed within 5-10 minutes."
echo ""

# Clean up local config
rm -f "$CONFIG_FILE"

# Remove kubeconfig context
kubectl config delete-context "$CLUSTER" 2>/dev/null || true
kubectl config delete-cluster "$CLUSTER" 2>/dev/null || true

echo -e "  ${GREEN}Local kubeconfig cleaned.${RESET}"
echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  Teardown complete — no more Azure costs for this PoC.${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════${RESET}\n"

# Verify deletion progress (optional)
echo -e "  To check deletion status:"
echo -e "  ${BOLD}az group show --name $RG --query properties.provisioningState -o tsv${RESET}"
echo ""
