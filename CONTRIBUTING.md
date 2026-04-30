# Contributing

Thank you for your interest in this project. **Important context:** this repository is a Design Science Research (DSR) reference artifact. The architecture (5-pillar design, 16 quality gates) is currently scope-fixed; only additive, compatibility, and bug-fix contributions are accepted while the v1.x branch is active.

## What contributions are welcome

| Type | Welcome? | Notes |
|------|----------|-------|
| **Bug reports** | ✅ Yes | Use GitHub Issues. Include exact reproduction steps and the relevant test command. |
| **Documentation fixes** | ✅ Yes | Typos, broken links, clarifications — small PRs preferred. |
| **Compatibility patches** | ✅ Yes | E.g. newer Conftest / OPA versions, alternative cluster runtimes. Keep changes minimal and additive. |
| **New Quality Gates** | 🟡 Discuss first | Open an issue describing the regulatory anchor and the gate template fields before submitting code. |
| **Architectural changes** | 🔴 No | The 5-pillar design and 16-gate set are scope-fixed in the v1.x branch. |
| **Scope expansion (e.g. NIST AI RMF coverage)** | 🔴 No | Out of scope for the v1.x branch. |

## Before opening a pull request

1. **Search existing issues** for related discussion.
2. **Run the local test suites** and ensure they still pass:
   ```bash
   make verify
   # which runs:
   #   python3 tests/test_all.py                 (master integration, 22/22 expected)
   #   python3 tests/test_integrity_regression.py (credibility checks, 14/14 expected)
   #   ./infrastructure/scripts/smoke-test.sh    (Minikube smoke, 8/8 expected)
   ```
3. **Editor config** — `.editorconfig` is provided. Use an editor that respects it (most modern editors do natively).
4. **Commit format** — short, imperative present-tense subject. Example:
   ```
   fix(rego): G-OPS-02 dual-input parser handles null annotations

   Previously crashed on missing data.review.annotations. Now treats
   absent annotations as empty list, matching Conftest semantics.
   ```
5. **Sign your commits** if you are comfortable doing so (`git commit -s`).

## Code style

- **Python:** PEP 8, 4-space indent. Type hints encouraged.
- **Rego:** Conventional `package` naming aligned with the gate ID (e.g. `package g_pre_04`).
- **YAML:** 2-space indent. Stable key order: `gate_id`, `name`, `trigger`, `governance_dimension`, `check_criteria`, `evidence_artifacts`, `decision_logic`, `responsibility`, `audit_trail`, `waiver_policy`.
- **Bash scripts:** `#!/usr/bin/env bash`, `set -euo pipefail` at the top, prefer `[ ... ]` over `[[ ... ]]` only where POSIX matters.
- **Markdown:** Atx-style headers (`#`), tables for structured comparison, fenced code blocks with language hints.

## Reporting security issues

If you discover a security vulnerability (e.g. in the gate orchestrator's evidence handling, hash-chain verification, or any policy that could be bypassed), please **do not open a public issue**. Email the author directly (contact via [LinkedIn](https://www.linkedin.com/in/mustafa-demir-331900202/) or [website](https://mustafa-demir.com)) so the issue can be coordinated before public disclosure.

## License of contributions

By submitting a pull request, you agree that your contribution is licensed under the same [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) license that covers the rest of the repository.
