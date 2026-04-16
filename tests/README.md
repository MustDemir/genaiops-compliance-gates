# Tests

Top-level test suites for the GenAIOps Compliance Gates PoC. Always run from repo root.

## Suites

| File | Purpose |
|------|---------|
| `test_all.py` | Master integration test — runs all functional tests across the 5 architecture pillars (Phases 5, 8, 9, infra, evidence). Validates the entire PoC is consistent and Minikube-deployment-ready. |
| `test_integrity_regression.py` | Static credibility regression suite — catches "does the PoC prove what it claims" risks: demo fallbacks, soft-skips, fallback coverage gaps, walkthrough drift, scope-claim mismatches, etc. |

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
