.PHONY: help install-conftest local-up local-down minikube gatekeeper monitoring app smoke \
        aks-up aks-down test test-integrity test-rego test-evidence check-python \
        verify verify-cluster clean-runtime check-verify test-eval test-verify-contract

# ── Interpreter ──────────────────────────────────────────────────────
#
# The suites need PyYAML. Which interpreter has it is a property of the
# MACHINE, not of this repository, so it is not hard-coded here.
#
# Instead: override PYTHON — and PYTHONPATH if needed — in Makefile.local,
# which is untracked (.gitignore covers *.local). check-python fails loudly
# and says what to do when no usable interpreter is found, rather than
# letting thirteen checks die with a stack trace apiece.
PYTHON ?= python3
-include Makefile.local

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
	@echo "  make test-rego              Run all Rego unit tests (needs opa on PATH)"
	@echo "  make test-evidence          Run hash parity, chain migration and manifest tests"
	@echo "  make test-eval              Run evaluation-reader tests against a local stand-in"
	@echo "  make test-verify-contract   Test verification prerequisites and verdict parsing"
	@echo "  make verify                 Selected local suites — the push gate (no cluster)"
	@echo "  make verify-cluster         verify + smoke (needs a running cluster)"
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

check-python:
	@$(PYTHON) -c 'import yaml' >/dev/null 2>&1 || { \
	  echo ""; \
	  echo "  $(PYTHON) cannot import yaml — the gate, requirement and README"; \
	  echo "  checks would all fail with a stack trace instead of a verdict."; \
	  echo ""; \
	  echo "  Install requirements.txt into your Python environment, then select it:"; \
	  echo ""; \
	  echo "      make PYTHON=.venv/bin/python verify"; \
	  echo "  You can also set PYTHON in Makefile.local (untracked)."; \
	  echo ""; \
	  exit 1; \
	}

check-verify: check-python
	$(PYTHON) tests/verify_contract.py preflight

test: check-verify
	$(PYTHON) tests/test_all.py

test-integrity: check-python
	$(PYTHON) tests/test_integrity_regression.py

test-rego:
	@command -v opa >/dev/null 2>&1 || { echo "opa is not on PATH — Rego tests cannot run"; exit 1; }
	bash tests/run_all_rego_tests.sh --quiet

test-evidence: check-python
	$(PYTHON) tests/test_hash_parity.py
	$(PYTHON) tests/test_hash_chain_migration.py
	$(PYTHON) tests/test_evidence_manifest.py

test-eval: check-verify
	$(PYTHON) scenarios/healthcare-ambient-ai-scribe/eval/test_eval_runner.py

test-verify-contract: check-python
	$(PYTHON) tests/test_verify_contract.py

# Selected local suites, without a cluster. This is the push gate: .githooks/pre-push
# runs it, which is why the integrity suite runs at --fail-on low here. At medium the
# roadmap check would print and the push would go through — noise, not a reminder.
# The suite's own default stays medium for standalone runs.
verify: check-verify
	$(MAKE) test-verify-contract test test-evidence test-eval
	$(PYTHON) tests/test_integrity_regression.py --fail-on low

verify-cluster: verify smoke

# ── Maintenance ──────────────────────────────────────────────────────

clean-runtime:
	@find evidence-store/data/reports -type f -name "*.json" -delete 2>/dev/null || true
	@find evidence-store/data/sqlite -type f \( -name "*.db" -o -name "*.db-journal" \) -delete 2>/dev/null || true
	@echo "Runtime artifacts cleared (evidence-store/data/{reports,sqlite}/)"
