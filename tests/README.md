# Tests

Top-level test suites for the GenAIOps Compliance Gates PoC. Always run from repo root.

## Suites

| File | Purpose |
|------|---------|
| `test_all.py` | Master integration test — runs all functional tests across the 5 architecture pillars (Phases 5, 8, 9, infra, evidence). Validates the entire PoC is consistent and Minikube-deployment-ready. |
| `test_integrity_regression.py` | Static credibility regression suite — catches "does the PoC prove what it claims" risks: demo fallbacks, soft-skips, fallback coverage gaps, walkthrough drift, scope-claim mismatches, etc. |
| `run_all_rego_tests.sh` | Rego unit-test runner — executes `opa test` across all 10 Rego policies and their `*_test.rego` files. Baseline 2026-04-17: **103/103 PASS**. Used by both `test_all.py` (Phase 3, Layer 1) and the CI pipeline (`gate-pipeline.yml`, fail-fast before Conftest). |

## Rego Test Layers (Shift-Left)

The PoC applies a two-layer Rego validation strategy — unit tests first, integration second:

| Layer | What | Runner | Purpose |
|-------|------|--------|---------|
| 1 — Unit | 103 `opa test` assertions across 10 policies (`policies/**/*_test.rego` + fixtures under `tests/fixtures/`) | `tests/run_all_rego_tests.sh` | Catches rule-semantic drift at the source. Fail-fast: any broken rule aborts CI before Conftest evaluates scenario fixtures. |
| 2 — Integration | Conftest execution of policies against scenario fixtures (`scenarios/healthcare-ambient-ai-scribe/fixtures/*.json`) | `conftest test --policy …` (in `test_all.py` Phase 3 and in `gate-pipeline.yml` G-PRE-01…G-OPS-02) | Validates end-to-end gate behaviour on realistic inputs. |

Ground-truth baseline (2026-04-17): 10 policies, 105 total rules, 103 unit tests; rule-per-policy distribution 14/12/17/9/16/9/10/6/6/6.

### Local invocation

```bash
# Prerequisite: OPA v1.15.2+ in PATH (or /tmp/opa)
./tests/run_all_rego_tests.sh            # full output
./tests/run_all_rego_tests.sh --quiet    # CI mode, only summary
./tests/run_all_rego_tests.sh --coverage # with coverage report
```

Exit codes: `0` = all pass, `1` = ≥1 test failed, `2` = OPA binary not found.

## Usage

```bash
# Run from repo root (both files use REPO_ROOT = parent of tests/)
python3 tests/test_all.py
python3 tests/test_integrity_regression.py
python3 tests/test_integrity_regression.py --format json
python3 tests/test_integrity_regression.py --fail-on low
```

## Other test locations

These two suites orchestrate component-level tests that live next to the code they test:

- `pipeline/test_pipeline_local.sh`, `pipeline/test_tamper_detection.py`
- `monitoring/test_drift_detector.py`, `monitoring/test_drift_e2e.py`
- `evidence-store/scripts/tests/test_hybrid_gate_integration.py`
- `infrastructure/scripts/smoke-test.sh`
- `policies/**/*_test.rego` — Rego unit tests (executed by `run_all_rego_tests.sh`)
