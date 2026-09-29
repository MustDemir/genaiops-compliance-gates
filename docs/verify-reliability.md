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
A06 and B06 require targeted retests; A07 must recheck what the local push hook
actually enforces (a local hook is not server-side branch protection); B04 requires
retesting evaluation-suite integration; A08 and B05 require confirming that the
isolated fault-injection run preserves the distinction between a blocked gate and
unrecorded evidence. These are impact flags, not retroactive changes to their
baseline findings. C01–C04 must review the resulting branch, not assume the old
test-runner behavior. Full local regression is required; independent review and
live-system claims remain pending.

## Evidence

Execution results and counterprobe outputs are recorded after implementation.
PO acceptance remains separate from a green local run.
