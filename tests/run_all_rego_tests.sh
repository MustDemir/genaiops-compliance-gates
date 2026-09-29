#!/usr/bin/env bash
# ================================================================
# run_all_rego_tests.sh — Unified Rego Test Runner
# ================================================================
# Purpose:   Single entrypoint to run ALL OPA/Rego unit tests for
#            the Quality-Gate policies of the GenAIOps Compliance
#            Gates PoC (FIX-K6.3-012 rollout).
#
# Usage (from repo root):
#   ./tests/run_all_rego_tests.sh            # run all tests, verbose
#   ./tests/run_all_rego_tests.sh --quiet    # run all tests, compact
#   ./tests/run_all_rego_tests.sh --coverage # run with coverage report
#
# Requirements:
#   - opa binary available as `opa` in PATH
#   - Rego test files in policies/<stage>/*_test.rego
#   - Fixture wrapper in tests/fixtures/healthcare_scenarios.rego
#
# Exit codes:
#   0 = all tests pass
#   1 = one or more tests fail
#   2 = opa binary not found
# ================================================================

set -euo pipefail

# ---------- Locate opa binary ----------
if command -v opa >/dev/null 2>&1; then
    OPA_BIN="opa"
else
    echo "ERROR: opa binary not found in PATH" >&2
    echo "Install:  https://www.openpolicyagent.org/docs/latest/#running-opa" >&2
    exit 2
fi

# ---------- Locate repo root ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# ---------- Parse args ----------
VERBOSE_FLAG="-v"
COVERAGE_FLAG=""
for arg in "$@"; do
    case "$arg" in
        --quiet|-q)
            VERBOSE_FLAG=""
            ;;
        --coverage|-c)
            COVERAGE_FLAG="--coverage"
            ;;
        *)
            echo "Unknown option: $arg" >&2
            echo "Usage: $0 [--quiet|-q] [--coverage|-c]" >&2
            exit 2
            ;;
    esac
done

# ---------- Header ----------
echo "================================================================"
echo "  GenAIOps Compliance Gates — Rego Unit Test Suite"
echo "  Local policy unit tests; counts are reported by OPA"
echo "================================================================"
echo "  Repo:         ${REPO_ROOT}"
echo "  OPA binary:   ${OPA_BIN} ($(${OPA_BIN} version | head -1))"
TEST_FILE_COUNT=$(find policies -name '*_test.rego' -type f | wc -l | tr -d ' ')
echo "  Test files:   ${TEST_FILE_COUNT} (policies/**/*_test.rego)"
echo "  Fixtures:     $(find tests/fixtures -name '*.rego' -type f | wc -l | tr -d ' ') (tests/fixtures/*.rego)"
echo "================================================================"
echo ""

# ---------- Run tests ----------
# opa test recursively picks up all *_test.rego files in the given dirs.
# We pass both policies/ (where tests live) and tests/fixtures/ (wrapper
# module with fixture imports) so that fixture data is resolvable.

CMD="${OPA_BIN} test policies/ tests/fixtures/ --fail-on-empty ${VERBOSE_FLAG} ${COVERAGE_FLAG}"
echo "Running: ${CMD}"
echo "----------------------------------------------------------------"

# Capture exit code without tripping set -e
set +e
${CMD}
EXIT_CODE=$?
set -e

echo "----------------------------------------------------------------"
if [ ${EXIT_CODE} -eq 0 ]; then
    echo "SUCCESS — all tests passed."
else
    echo "FAILURE — one or more tests failed (exit ${EXIT_CODE})."
fi
echo "================================================================"

exit ${EXIT_CODE}
