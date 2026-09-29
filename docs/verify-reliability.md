# Local verification reliability — scoped remediation

## Authorization and baseline

The PO authorized prioritizing `make verify` remediation after QG-B06, on a
separate local branch intended for a later PR. Base:
`96f9ee0a3ae52b38cd1b08b63110053ee453662d` (`domain_netzbetrieb`).
Branch: `codex/verify-reliable`. Local commits are part of delivery; push and merge
remain pending explicit PO authorization. The original audit reports and unrelated
working changes are not part of this branch.

## Why and legal reference

F-A06-001: the master runner could skip OPA/Conftest, and its Conftest calls used
neither explicit namespaces nor a meaningful block assertion (`--no-fail`).
F-A06-007: the existing evaluation-reader suite was absent from `make verify`.
F-A06-006 (partial): recorder fault injection modified the checkout's recorder.
F-B06-001 (partial): output used stale scope counts and an unsupported readiness claim.
Legal reference: none added or changed. Protected PO fields (severity, evidence
level, implementation classification and role scope) remain unchanged.

## Scope and readiness

In scope: Make entry points, selected integration-runner checks, verification
contract tests, an isolated recorder-test wrapper, and accompanying documentation.
The failing invocation patterns were inspected in the baseline source. Existing
pass/fail fixtures and evaluation-reader tests are reused; policy semantics are not
changed. Out of scope: legal mapping, live clusters, CI/workflow or production
pipeline changes, full annotation/requirement traceability repair, and the broader
QG remediation backlog.

## Machine-checkable delivery criteria

- `make verify` exits zero in the documented dependency environment, including the
  existing evaluation-reader suite, OPA, evidence tests and strict integrity checks.
- Missing required tools or suite files fail preflight.
- Each selected Conftest namespace accepts its positive fixture and blocks its
  negative fixture for the expected reason; empty results/zero rules are rejected.
- Regression tests reject a disabled verification guard; representative mutations
  of fixtures and prerequisites make the actual entry point fail.
- Fault injection cannot alter the checkout's recorder.
- Implementation is committed before file-mutation counterprobes; probes operate
  only in temporary copies of that commit. The working tree is checked afterwards.

## Limits and change impact

This does not close all findings in A06 or B06. In particular, the legacy recorder
test's report assertions and other weak consistency assertions are not repaired.
Missing PyYAML is an unmet environment prerequisite, not evidence of a repository
defect. A failure of this host's package installer does not establish a general
bootstrap failure. No new minimum Python version is inferred from this machine.

Affected existing reports are `stale_after_change` when assessing this branch:
A01 and A03 require rebaselining inventory/static mapping claims; A06 and B06
require targeted retests; A07 must recheck what the local push hook
actually enforces (a local hook is not server-side branch protection); B04 requires
retesting evaluation-suite integration; A08 and B05 require confirming that the
isolated fault-injection run preserves the distinction between a blocked gate and
unrecorded evidence. These are impact flags, not retroactive changes to their
baseline findings. C01–C04 must review the resulting branch, not assume the old
test-runner behavior. Full local regression is required; independent review and
live-system claims remain pending.

## Evidence

Implementation was committed as `daf119e`; the empty-Rego-suite regression was
added in `832ad0a`. The following results were measured on 2026-09-29 against
`832ad0a`, before this evidence-only documentation update. Python 3.13.15,
PyYAML 6.0.3, OPA 1.14.1, Conftest `dev` (embedded OPA 1.14.1).

```sh
PYTHONPATH=/Users/mustafademir/.local/pylibs make PYTHON=/opt/homebrew/bin/python3.13 verify
```

These absolute paths describe the reviewed host, not a portable setup requirement.
The first sandboxed run stopped at the loopback HTTP bind with `PermissionError`;
the authorized local run outside that sandbox completed with exit 0. No tool was
installed and no external service was required.

Selected output, copied from the tools (ANSI colors removed):

```text
Ran 22 tests in 0.061s
OK
PASS: 215/215
PASSED: 19  /  FAILED: 0  /  Total: 19
Passed checks: 37
Failed checks: 0
Actionable failures (>= LOW): 0
PARITY OK — all 3 implementations agree on all payload variants (13 / 14 / 15 / 16 fields).
MANIFEST GUARDS OK — the manifest states the chain it actually found.
```

The master integration runner reported 36 passed, 0 failed. Chain migration also
returned exit 0 with `MIGRATION OK`. The OPA result above was separately printed
by `bash tests/run_all_rego_tests.sh --quiet`; it is also run within the master suite.

```text
PASS pre-deployment/deployment_compliant.yaml: exit=0, evaluated=12, failures=0, expected=pass
PASS pre-deployment/deployment_noncompliant.yaml: exit=1, evaluated=12, failures=10, expected=block
PASS deployment/eval_results.json: exit=0, evaluated=18, failures=0, expected=pass
PASS deployment/eval_results_fail.json: exit=1, evaluated=18, failures=3, expected=block
PASS operations/deployment_compliant.yaml: exit=0, evaluated=6, failures=0, expected=pass
PASS operations/deployment_noncompliant.yaml: exit=1, evaluated=6, failures=3, expected=block
```

Counterprobes used archived committed source, never the caller's checkout:

| Mutation / command | Red result | Restored result |
|---|---|---|
| PATH without OPA/Conftest; `make verify` | exit 2; `required tool is missing from PATH: opa`, same for `conftest` | preflight exit 0 |
| Rename evaluation test file; `make verify` | exit 2; `required verification file is missing: scenarios/healthcare-ambient-ai-scribe/eval/test_eval_runner.py` | preflight exit 0 |
| Disable the zero-evaluation guard; its regression test | exit 1; `AssertionError: ValueError not raised`, `FAILED (failures=1)` | `Ran 1 test`, `OK`, exit 0 |
| Give the negative evaluation fixture passing MUST metrics; Conftest deployment pair | exit 1; `FAIL negative fixture did not block for the expected reason` | pair exits 0, negative tool result exit 1 with 3 failures |
| Remove `test-eval` from verify; wiring regression test | exit 1; evaluation script `not found` in the scheduled commands | `Ran 1 test`, `OK`, exit 0 |
| Remove `--fail-on-empty`; empty-suite regression test | exit 1; `AssertionError: 0 == 0`; broken runner printed `SUCCESS — all tests passed.` with 0 test files | `Ran 1 test`, `OK`, exit 0 |
| Reintroduce `PoC is consistent and complete`; output-claim regression | exit 1; obsolete assertion `unexpectedly found`, `FAILED (failures=1)` | `Ran 1 test`, `OK`, exit 0 |
| Remove the G-OPS-06 mapping; master integration test | exit 1; `35 passed`, `1 failed`, static-reference check red | restored copy rerun: `36 passed`, `0 failed`, exit 0 |

The isolated recorder test reported `PASSED: 6 / FAILED: 0`, with exit 0 before
fault injection, exit 3 during failure and exit 0 after restoration. Recorder
SHA-256 before and after:
`4bd5bc013c0b973e887c842e8663a65f61bdf141d5bcb4eaa48278f7865709e9`.
The regression suite also simulates an interruption after a temporary-copy write
and verifies that the original recorder remains unchanged.

After restoring all mutations, the aggregate SHA-256 of sorted-in-Git-order tracked
file hashes was identical in the worktree and the temporary copy:
`02cceb6de9d249c5d2d7097bec5f8f9a1e7e2d323d9ae93cbe37adc8a7b6972a`.
`git diff --exit-code` returned 0 before this documentation update.

No changes occurred under gate-definitions, policies, pipeline, evidence-store,
requirements, specs or .github/workflows. The broader QGs, server-side enforcement
and clean-host package installation have not been re-reviewed. F-A06-007 is only
addressed for local `make verify`; the hosted workflow integration remains open.
PO acceptance and independent review remain pending. No push or merge occurred.
