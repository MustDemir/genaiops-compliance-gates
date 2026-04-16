.PHONY: help install-conftest local-up local-down minikube gatekeeper monitoring app smoke \
        aks-up aks-down test test-integrity verify clean-runtime

# Default target prints help
help:
	@echo "GenAIOps Compliance Gates — Make targets"
	@echo ""
	@echo "Setup:"
	@echo "  make install-conftest       Install Conftest CLI (sudo; or NO_SUDO=1)"
	@echo ""
	@echo "Local (Minikube) — full PoC stack on a laptop:"
	@echo "  make minikube               Spin up Minikube cluster"
	@echo "  make gatekeeper             Install OPA Gatekeeper via Helm"
	@echo "  make monitoring             Install kube-prometheus-stack"
	@echo "  make app                    Deploy the Healthcare Scribe app"
	@echo "  make smoke                  Run smoke tests against the deployed app"
	@echo "  make local-up               Run minikube + gatekeeper + monitoring + app + smoke"
	@echo "  make local-down             Stop & delete the Minikube cluster"
	@echo ""
	@echo "Cloud (Azure AKS):"
	@echo "  make aks-up                 Provision AKS + deploy stack (Sweden Central)"
	@echo "  make aks-down               Tear down the AKS cluster"
	@echo ""
	@echo "Tests:"
	@echo "  make test                   Run master integration test (tests/test_all.py)"
	@echo "  make test-integrity         Run integrity regression suite (tests/test_integrity_regression.py)"
	@echo "  make verify                 Run both test suites + smoke"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean-runtime          Remove evidence-store/data/{reports,sqlite}/ contents"

# ── Setup ────────────────────────────────────────────────────────────

install-conftest:
	./infrastructure/scripts/install-conftest.sh

# ── Local (Minikube) ─────────────────────────────────────────────────

minikube:
	./infrastructure/scripts/setup-minikube.sh

gatekeeper:
	./infrastructure/scripts/install-gatekeeper.sh

monitoring:
	./infrastructure/scripts/install-monitoring.sh

app:
	./infrastructure/scripts/deploy-app.sh

smoke:
	./infrastructure/scripts/smoke-test.sh

local-up: minikube gatekeeper monitoring app smoke

local-down:
	@minikube stop && minikube delete

# ── Cloud (Azure AKS) ────────────────────────────────────────────────

aks-up:
	./infrastructure/scripts/deploy-aks.sh

aks-down:
	./infrastructure/scripts/teardown-aks.sh

# ── Tests ────────────────────────────────────────────────────────────

test:
	python3 tests/test_all.py

test-integrity:
	python3 tests/test_integrity_regression.py

verify: test test-integrity smoke

# ── Maintenance ──────────────────────────────────────────────────────

clean-runtime:
	@find evidence-store/data/reports -type f -name "*.json" -delete 2>/dev/null || true
	@find evidence-store/data/sqlite -type f \( -name "*.db" -o -name "*.db-journal" \) -delete 2>/dev/null || true
	@echo "Runtime artifacts cleared (evidence-store/data/{reports,sqlite}/)"
