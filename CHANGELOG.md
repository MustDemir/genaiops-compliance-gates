# Changelog

All notable changes to the **GenAIOps Compliance Gates** reference architecture.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning is by lifecycle phase (Phase 0 = pre-implementation alignment, Phases 1–12 = PoC build phases as listed in the [README progress table](README.md#implementierungsfortschritt)).

---

> **Reproducibility note (2026-08-14):** Git tag `thesis-v1.0` (commit `32804b5`) freezes the exact state cited in the submitted and graded Master's thesis and archived under Zenodo DOI [10.5281/zenodo.19920310](https://doi.org/10.5281/zenodo.19920310) — 14 requirements, 16 gates, 10 AUTO / 6 HYBRID / 0 MANUAL, 108 rules, 141 unit tests. That state remains reproducible via `git checkout thesis-v1.0`. All changes from this point forward (starting with the `schema_version: 2` gate-template migration, SPEC-01/02/03) are **post-thesis further development** and may change gate counts, rule counts, and the severity/automation model described above.

## [Unreleased] — Post-Thesis Development (schema_version 2)

### Added — the evidence manifest, so a run's evidence outlives its runner (SPEC-05 Teil 2, 2026-09-01)

In CI the Evidence Store lives at `/tmp/evidence_pipeline.db` and is destroyed
with the runner. Verifying that chain and then throwing it away proves nothing
to anyone who was not watching (B-18). `evidence-store/scripts/build_manifest.py`
summarises a run into one small document that can be carried out — and, from
Teil 3 onwards, signed.

The manifest states `pipeline_run_id`, `commit_sha`, `schema_version`,
`record_count`, `genesis_hash`, `chain_head`, `gate_verdicts_digest`,
`runtime_mode`, `signing_context` and `created_at`. Nothing else: it pins the
chain without carrying it.

- **`gate_verdicts_digest` makes the manifest checkable without the database.**
  It is taken over one line per *record* — a HYBRID gate contributes both its
  automated and its human verdict, so a manual FAIL cannot hide behind an
  automated PASS. The pipeline report now carries the same verdict list under
  `gate_verdicts`, so a reader with the report and the signed manifest can
  recompute the digest. A report that merely repeated the digest would be the
  manifest quoting itself.
- **One implementation of that digest.** The orchestrator delegates to
  `build_manifest.py` instead of rebuilding the payload, and the new test
  asserts the orchestrator computes no hash of its own — the mistake
  `test_hash_parity.py` exists to catch, not repeated.
- **`signing_context`** declares the context the manifest was produced in
  (`ci` or `local`), the same building block as `runtime_mode` in SPEC-04. It
  is a declaration, not proof; the signature from Teil 3 is what makes it
  checkable. CI therefore reads the value back after generating the manifest
  and fails the job if the run does not declare itself as `ci`.
- **Written on every run** — locally, in CI, on a blocked pipeline and on an
  empty store, where it states a record count of zero rather than an invented
  chain. A document that appears only on success cannot describe a failure.
- `prepare_inputs.py` still issues nothing of its own; the new test guards it
  (B-03).

`tests/test_evidence_manifest.py`: 22 guards, each with its counterproof, and
two of them verified by deliberately breaking the implementation. Existing
suites unchanged and green — 36 `test_all`, 199 Rego, 29 integrity checks
(0 actionable), hash parity and chain migration. No payload change, so no
`v06 → v07` migration: `signing_context` belongs to the manifest, not to the
record.

**Still open in SPEC-05:** signing (`cosign`, keyless), `upload-artifact`,
identity-bound verification, the G-OPS-05 checks C-04…C-07, and the three new
integrity checks. Until then the manifest is produced but nothing carries it
off the runner yet.

### Changed — the catalogue's only E-1 check is downgraded to E-0 (SPEC-05 Teil 1, B-18, 2026-09-01)

G-OPS-05/C-02 ("Hash-Chain-Integritaet ueber alle Evidence-Records") carried
`evidence_level: "E-1"`. Measured against the project's own definition that is
wrong. E-1 requires a **signed** artefact with a **verified producer identity**
and forgery costs equal to compromising the CI identity. The chain offers none
of that: SHA-256 is a checksum, not a signature; `inserted_by` is a string the
writer picks (default `'poc_local'`), hash-covered but not evidenced; and
rewriting the chain from genesis costs write access to the database, not the CI
identity. The chain is tamper-evident against partial edits — a statement about
internal consistency, not about provenance — which places it at E-0 with an
extra property.

**The catalogue therefore carries no E-1 check at all right now.** That is the
honest interim state and it is meant to be visible: a wrong classification is
more harmful than a low one, because it reassures the reader.

- `evidence_level` of G-OPS-05/C-02: `E-1` → `E-0`; the gate's `rationale` and
  `notes` state why the earlier classification was withdrawn
- README: the sentence "G-OPS-05 pairs an E-0 annotation check with an E-1
  hash-chain check" is corrected, and the open-points entry now says that no
  per-check level is above E-0
- HISTORIE: B-18 / H4.21, status `teilbehoben` — Teile 2–6 of SPEC-05 (evidence
  manifest, keyless signing, identity-bound verification) remain open

The gate's `evidence_level.current` was already `E-0` and is unchanged; no rule,
no test and no count changed.

### Added — the CI measures drift, and the gates prove they would block (SPEC-04b Teil 3.1/3.3, 2026-08-28/31)

SPEC-04b is complete. Teil 1 (counts read, not claimed), Teil 3.2 (`required_inputs`
enforced) and Teil 2 (the app runs in the runner) landed earlier; this closes
Teil 3.1 and Teil 3.3. The gate rules are unchanged. What changed is that the
pipeline now produces the documents it judges, and that it demonstrates the
gates can fail.

**Counts unchanged.** 17 gates, 14 requirements, 199 Rego tests, 36 `test_all`,
28 integrity checks. No rule was added; two workflow jobs and one script were.

#### Added — drift is measured in the runner, not read from a fixture

- After the load run of Teil 2, a baseline is taken from the running app's
  `/metrics`, a second load profile with different text lengths is driven, and
  `drift_detector.py` measures against it. The resulting document is what
  G-OPS-03 evaluates.
- `provenance` is asserted to be `derived` and the source to be the app under
  test. Provenance follows the source, not the arithmetic: a live scrape is
  `derived`, a fixture file is `declared`. A `declared` document here would mean
  the pipeline passed a checked-in file through and observed nothing.
- **What this shows and what it does not.** The measurement is real; C-03
  (freshness) and C-05 (provenance) are for the first time evaluated against a
  document produced in the pipeline that judges it. It shows **no drift** —
  measured locally against the same app at PSI 0.000000 — and that is the
  construction, not a defect: the Prometheus histogram is cumulative over the
  process lifetime, so the "current" distribution contains the baseline and can
  only dilute; and the mock answers in sub-milliseconds largely independent of
  input length (B-09). That the gate would *block* on drift is not shown by a
  green run. It is shown by the job below.

#### Added — `required_inputs` is enforced in the CI, not only in the orchestrator

- SPEC-04b Teil 3.2 enforced the presence obligation in
  `pipeline/gate_orchestrator.py`. The CI does not run the orchestrator — it
  calls conftest per gate — so the obligation held everywhere **except in the
  pipeline that decides whether an image ships**. G-OPS-02 and G-OPS-03 have
  declared a required document since 25.08.; the workflow never supplied one and
  went green. Declaration present, mechanism absent, one level further out.
- New `pipeline/ci_required_inputs.py` resolves the declarations for a CI run
  and writes, per gate, either the evaluations to perform (`-inputs.args`:
  path, policy, namespace) or the findings naming the missing input
  (`-inputs.fail`). It exits 0 on a missing input: that is a **gate** failure,
  not a tool failure, and it belongs in the evidence record rather than in an
  aborted step. It exits 2 only when the check itself could not run — no
  PyYAML, no gate definitions — because an enforcement that can switch itself
  off silently is not one.
- The gate runner evaluates the primary document **and** every resolved
  required input into **one** result file, hence one evidence record — the same
  shape as `role_scope: BOTH` in SPEC-03. Recording them separately would give
  one gate two verdicts, which is exactly what SPEC-04 removed from G-OPS-03.
- Freshness is deliberately **not** checked here. An outdated document is
  present; it fails through G-OPS-03/C-03 in Rego, where the deadline is
  written. Presence and freshness are two questions.
- `PyYAML` added to the CI install. Without it,
  `load_gate_required_inputs()` returns an empty map after a warning — the
  enforcement would have been off while appearing to run.

#### Added — a negative-cases job: the gates would block

Three cases, each with its counter-check, in a job of its own so an expected
failure does not colour the main run red:

| Case | Blocks | Counter-check |
|---|---|---|
| measured drift (`current_drifted.json`) | G-OPS-03 via C-04 | `current_normal.json` passes |
| missed safety metric (`eval_results_fail.json`) | G-DEP-02 | `eval_results.json` passes |
| **absent** measurement | G-OPS-03 via the presence obligation | a supplied one resolves to a policy *and* a namespace |

The counter-check is not decoration. Case 1 would look identical if it were red
for another reason — a stale document, a wrong namespace — so the normal case
has to be green next to it. Case 3 is the one this SPEC is actually about: C-03
to C-05 only fire when `input.drift_measurement` exists, so omitting the
document walks past three MUST checks, and Rego cannot catch that because it
cannot tell an absent document from an absent rule.

`expect_gate.sh` asserts the *expectation*, not merely the outcome: a tool error
(broken policy, wrong namespace) also reports zero violations and would
otherwise be indistinguishable from a passing normal case.

#### Added — the build waits for proof that the gates can block

`build-and-push` now depends on **both** jobs: all gates green, and the negative
cases demonstrated. Without the second condition the first is worth little — a
catalogue in which no gate can turn red any more (a broken policy, a wrong
conftest namespace, a presence obligation resolving to nothing) still reports
17/17 PASS and ships an image. That particular green is the opposite of
evidence.

New integrity check `NEGATIVE_CASES_GATE_THE_BUILD` (HIGH) holds the dependency,
because `needs` is one line and convenient to drop while refactoring. It
verifies that the job asserts an expected BLOCK, that it carries its
counter-check, that G-OPS-03 and G-DEP-02 are among the blocked cases, and that
the build depends on it. Counter-checked in five directions. The first version
failed three of them: it searched the job text for "BLOCK", "PASS" and the gate
ids, and those words also occur in `expect_gate.sh`'s own definition and in the
summary banner — it was reading the helper's source and the decoration, not
what the job asserts. It now matches the invocations.

#### Changed — `REQUIRED_INPUTS_ENFORCED` now also holds the CI to it

The integrity check verified that the *orchestrator* enforces, and passed for
the entire time the CI did not. Verifying one caller and calling the obligation
enforced is the same mistake one level out. It now additionally requires that
the workflow resolves the declarations, that the gate runner reads what was
resolved, that every declared input is actually supplied, and that PyYAML is
installed **in each job that runs the enforcement** — per job, because a first
version searched the whole file and stayed green when the install was removed
from the job that needed it. All four halves were counter-checked by breaking
them (B-16).

### Changed (BREAKING) — measurement before signature (SPEC-04, 2026-08-25)

Gate inputs now come from the running system where they can. The rules are
unchanged; what changed is where their numbers come from. The evidence level
sits in the provenance of the input, not in the rule.

**Counts.** Rules 166 → 175, unit tests 173 → 187 (plus 19 eval-runner and 21 drift E2E checks), integrity checks 20 → 21. Gates and requirements are
unchanged at 17 and 14. The counts cited in the thesis (16 gates, 108 rules,
141 tests) remain reproducible under `git checkout thesis-v1.0`.

#### Removed — `gate_result` and its rule (G-DEP-02)

- `eval_results.json` carried `gate_result.all_passed`, and a `deny` rule read
  it. A candidate bringing its own report card. It also asserted nothing
  independent: if the thresholds hold, the verdict is PASS, and conftest
  decides that.
- It concealed a contradiction. The fixture stated `quality_metrics.accuracy:
  0.89` and, further down, `gate_result.details` `"value": 0.91` for the same
  metric. Two invented values for one number, not consistent with each other,
  and no rule compared them because the threshold rule and this rule read
  separate paths. Where a number is not produced, it cannot even be consistent
  with itself.
- The unit test asserting the removed rule is retired; a new test asserts the
  opposite, so a silent reintroduction would fail.

#### Removed — the drift detector's silent fallback

- On an unreachable app or an empty histogram, `load_distribution_from_app()`
  returned a hard-coded distribution stamped with `source: <url>` and a fresh
  `captured_at` — indistinguishable from a measurement. It now raises and exits
  non-zero, and writes no measurement document at all, so the previous document
  ages and C-03 catches it.

#### Changed — the drift detector measures, Rego decides

- `record_drift_evidence()` used to set its own `decision` under gate ID
  `G-OPS-03`, in parallel to `policy_monitoring_configured.rego` judging the
  same gate from three pod annotations. One gate ID, two producers, incompatible
  logic. The detector now writes a measurement document, conftest evaluates it,
  and the policy's verdict is what gets recorded.
- The measurement is written on every run, not only on drift: evidence that
  appears only when something is wrong cannot show that monitoring was running
  when nothing was wrong.

#### Added — `provenance` per metric group

- Every metric group in an evaluation document declares `measured`, `derived`
  or `declared`, with its source. This does not make `accuracy` true — without
  ground truth there is no accuracy in operation, only proxies. It makes the
  assertion legible as an assertion. E6 applied at field level.
- New `eval/eval_runner.py` produces `eval_results.json` instead of finding it:
  latency quantiles and throughput measured from `scribe_latency_seconds` and
  `scribe_requests_total`, `model_version` read from the app's own response,
  `runtime_mode` read from `scribe_mock_mode`.
- The values that cannot be measured moved to `eval/declared_metrics.json`, so
  the boundary between measured and asserted is a file boundary.
- New shared reader `monitoring/metrics_source.py`, so the bucket-parsing logic
  that feeds two gates exists once rather than twice.

#### Added — checks

- **G-OPS-03 C-03 (MUST)**: a drift measurement exists and is recent. The more
  important of the two: a gate reading only the value mistakes standstill for
  stability — a crashed detector leaves its last good PSI sitting there, green.
- **G-OPS-03 C-04 (MUST)**: PSI ≤ 0.2 and JSD ≤ 0.1, measured. The fixture
  `monitoring/fixtures/current_drifted.json` has been in the repository since
  the thesis without ever touching a gate; it now fails one.
- **G-OPS-03 C-05 (SHOULD)**: the measurement states a measured/derived
  provenance and a source. Advisory, so a fixture-driven walkthrough stays green.
- **G-DEP-02 C-03 (SHOULD)**: warns when a MUST threshold is applied to a
  `declared` value. Advisory on purpose — the whole estate is declared today,
  and a MUST would turn it red on day one over a gap left open deliberately.
- `policy_checks[].evidence_level` carries real values for the first time
  (it had been `null` on every gate since SPEC-01). G-OPS-03 now shows E-0 and
  E-3 side by side in one gate.

#### Added — `runtime_mode` sealed into the hash chain (schema v06)

- The app has always exported `scribe_mock_mode`. No gate read it, and a mock
  PASS was byte-identical to a live PASS in the evidence table.
- Three options were weighed. **A** (mock forces FAIL) was rejected: mock mode
  is a legitimate PoC mode, not a breach, and a gate that always fails gets
  switched off. **B** (a third decision value `INCONCLUSIVE`) was rejected
  because it carries *less*, not more — "PASS on a mock run" states two things,
  "INCONCLUSIVE" states one and discards whether the thresholds held.
  **C** was chosen: `runtime_mode` as a hashed column.
- A mock PASS stays possible but is distinguishable and cannot be relabelled
  afterwards. The task is not to forbid mock mode; it is to make it unhideable.
- Migration `v05_to_v06_add_runtime_mode.sql`, per-field cutoff, no back-fill.
  For this column the no-back-fill rule bites twice: nobody knows what mode the
  older runs were in, because the gauge was never read. Writing `live` into them
  would invent the very fact the column records.
- `resolve_runtime_mode()` in the orchestrator, four-stage: `RUNTIME_MODE` env,
  metrics endpoint, metrics snapshot, then **`unknown`** — never `live`. Whoever
  cannot establish that a real model ran has no evidence that one did.
- Resolved in the orchestrator rather than in Rego: the check would otherwise be
  duplicated across all 17 policies, and Rego must not measure — Gatekeeper
  blocks external calls by default. The value is handed to the gate as input.

#### Added — visibility carriers for the accepted weakness of option C

- Option C's known cost: a consumer reading only `decision` still sees an
  undifferentiated PASS. Compensated in four places — the orchestrator banner,
  the pipeline report's top level, the auditor-facing view (where `runtime_mode`
  sits directly beside `decision`), and the verifier's verbose output.
- New integrity check `RUNTIME_MODE_VISIBLE` (MEDIUM) keeps those from eroding,
  including the column's *position* in the view. Verified in both directions by
  removing the banner and confirming the check fails.

#### Fixed — PostgreSQL chain verification (pre-existing, since v05)

- `verify_hash_chain.py` fetched only the v04 role cutoff on the PostgreSQL
  path; nothing fetched the v05 `derived_decision` cutoff. A PostgreSQL store
  holding v05 records would have been verified against a 14-field payload while
  the trigger wrote 15 — **every record would have reported a hash mismatch**.
  The SQLite path was correct, which is why the test suite never caught it.
- Replaced by a generic `fetch_cutoff_pg(db_url, key)`; `runtime_mode` would
  otherwise have inherited the same gap.

#### Fixed — findings from the first run against the real app (2026-08-25)

Running the actual container rather than a stand-in surfaced three things the
unit tests could not.

- **Histogram buckets were mis-sized.** The floor was 0.1s while every mock
  response takes microseconds, so all observations landed in the first bucket
  and `histogram_quantile` could only interpolate inside it: p95 came out as
  0.95 x 0.1s = 95ms regardless of what the app did. G-DEP-02 was applying a
  2000ms threshold to a constant — measured, and almost information-free.
  Resolution is now 1ms at the bottom, upper bounds unchanged so the 2000ms
  threshold still sits on a real bucket edge. Measured against the real app,
  the reported p95 went from a fictitious 95ms to 0.95ms with the true mean at
  0.034ms.
- **Added `latency_mean_ms`, exact.** Derived from `_sum`/`_count`, so no
  bucket boundary is involved and no interpolation happens. It is the only
  latency figure in the document that is not an estimate. Verified against the
  stand-in: a 400ms app reports a mean of 400.0ms.
- **Added `latency_p95_resolution`.** States the enclosing bucket and whether
  the p95 sits inside the finest one. When it does, the quantile is pure
  interpolation between zero and that bound: it moves with the bucket layout,
  not with the system, and a threshold applied to it is a threshold applied to
  an artefact. Machine-readable rather than a footnote — the same move as
  `provenance`, one level deeper. The runner also says it out loud.
- **`sprintf` rendered an integer with `%.0f`** in the C-03 message, producing
  `budget is %!f(int=900)s`. The Rego unit tests assert `contains(msg, "C-03")`
  and never saw it.
- **Dockerfile carried `licenses="CC-BY-NC-4.0"`**, stale since the Apache 2.0
  relicence of 2026-08-15 and baked as an OCI label into every built image.

The checked-in `eval_results.json` is now generated against the real container
rather than the stand-in, and says so in `_spec`.

#### Known regression — the drift CronJob

- `--record-evidence` now requires `conftest` and `policies/operations/` inside
  the image, and `metrics_source.py` next to the script. There is no Dockerfile
  for that image in this repository. Until it is rebuilt, the CronJob exits 2
  with "conftest not found" rather than falling back to a Python verdict — which
  is the failure mode SPEC-04 chose. Documented in the manifest.


### Removed (BREAKING) — the waiver path (audit F-2)

- **Waivers are abolished.** 11 of 17 gates declared `waiver.allowed: true` with an approver and a time limit, but the mechanism existed only on paper: `waiver` appeared in no line of logic in `pipeline/`, `evidence-store/`, `policies/` or `.github/`, and the evidence schema only knows `decision IN ('PASS','FAIL')` — a waived gate could not even be represented, let alone distinguished from a passed one.
- Exceptions are the first thing an auditor tests. An exception path that leaves no trace devalues the completeness of the hash chain, which is the property the artefact rests on. Abolishing it is more honest than leaving an unimplemented promise in the template.
- The previous approver/expiry text of each gate is preserved in its `notes` as the documented governance intent, in case waivers are ever implemented for real.
- New integrity check `WAIVER_NOT_DECLARATIVE` (HIGH) keeps the decision from eroding: `waiver.allowed: true` is only accepted once `record_evidence.py` actually handles waivers. Verified by reactivating one and confirming it fails.

### Added — per-check implementation status (audit F-3)

- Every `policy_checks[]` entry carries `implementation: implemented | design_only`. Of 43 checks across 17 gates, **36 are enforced and 7 are design-only** (in G-PRE-04, G-DEP-01, G-DEP-03), so those gates report PASS while part of what they declare has not been evaluated.
- `GATE_POLICY_FILE_EXISTS` (LOW, permanently red, permanently ignored) became `GATE_IMPLEMENTATION_HONEST` (HIGH), verifying the claim in both directions instead of the mere absence of a file.

### Changed (BREAKING) — Licence: CC BY-NC 4.0 → Apache 2.0 (2026-08-15)

- The repository is now licensed under the **Apache License 2.0**. CC BY-NC is not an open-source licence under the OSI definition: the non-commercial restriction bars exactly the setting a compliance control system is built for.
- **Not retroactive.** The release archived under Zenodo DOI 10.5281/zenodo.19920310 and the tag `thesis-v1.0` stay available under CC BY-NC 4.0; that grant is not withdrawn. Anyone who received the work under the old terms keeps them.
- Relicensing is clean: the repository vendors no third-party source code and carries no foreign copyright headers, so the sole copyright holder can relicense. External tools (OPA, Gatekeeper, Kubernetes, PostgreSQL, …) are depended on, not redistributed — see `NOTICE`.
- Added `NOTICE` (Apache convention) with the licence history and the third-party dependency list. The previous licence text is retained as `LICENSE_CC-BY-NC-4.0_until_2026-08-15.txt`.
- `CITATION.cff`, `.zenodo.json`, `CONTRIBUTING.md` and the README badge updated to `Apache-2.0`.
- Official Journal documents under `docs/legal/` are EU publications reproduced unaltered for verification; their reuse follows Decision 2011/833/EU and is not covered by the repository licence.

### Changed (BREAKING) — Gate count 16 → 17 (SPEC-03)

- **`G-OPS-06` (Rollenwechsel) added to the enforced catalogue**, transferred from `prospective/art25-role-change/` where it deliberately sat outside the counted catalogue. **This changes the headline figures cited in the Master's thesis** (Kap. 7.4 / 8.1): the catalogue now holds **17 gates**, and the Rego unit-test count rises accordingly.
- The published figures — **14 requirements, 16 gates, 10 AUTO / 6 HYBRID / 0 MANUAL, 108 rules, 141 unit tests** — remain reproducible under the Git tag `thesis-v1.0` (`git checkout thesis-v1.0`) and in the Zenodo archive. They are **not** silently overwritten.
- Severity is no longer uniform across the Art. 25 triggers: C-25a (rebranding) and C-25c (purpose change) are binary offences and became MUST; only C-25b (substantial modification) stays SHOULD, because its threshold depends on Art. 3(23) and the pending Art. 97 delegated acts.
- C-25c now evaluates the `classification` rule from G-PRE-01 (SPEC-02) on the before/after purpose state instead of trusting a `becomes_high_risk_art6` boolean in the manifest.

### Added — Evidence Store schema v04: `ai_act_role` in the hashed payload (SPEC-03)

- New column `ai_act_role` on `compliance.quality_gate_results`, plus a `compliance.schema_metadata` table. Migration: `evidence-store/migrations/v03_to_v04_add_ai_act_role.sql`.
- The role decides which gates run at all and is therefore audit-relevant, so it goes into the **hashed** payload rather than the unhashed `notes` column.
- **Migration variant: cutoff instead of chain break.** Existing records were hashed without the field. Rather than rehashing them or starting a new chain, the field enters the payload only from a per-database cutoff `audit_id` (written by the migration as `max(audit_id) + 1`, and `1` for a fresh database). Records below the cutoff keep the 13-field v03 payload; records at or above it use the 14-field v04 payload. A chain spanning the cutoff verifies end-to-end, so no existing chain is broken — including in a long-lived PostgreSQL instance carried across the migration.
- All three hash implementations (`record_evidence.py`, `verify_hash_chain.py`, the `set_hash_chain()` trigger) apply the same cutoff. `tests/test_hash_parity.py` now compares the two Python implementations **behaviourally** in both variants instead of regex-parsing their source, and checks both SQL branches.
- New `tests/test_hash_chain_migration.py` proves the four properties that make the variant sound: a pure v03 chain verifies, a chain spanning the cutoff verifies, tampering below the cutoff is still detected, and tampering with `ai_act_role` above the cutoff is detected — the last one being the point of hashing the field at all.

### Added — AI Act role parameter PROVIDER / DEPLOYER / BOTH (SPEC-03)

- Every gate definition carries `role_scope`; all existing gates are marked `["deployer"]`, which is the correct label for the status quo rather than a downgrade (the architecture was deliberately deployer-scoped, thesis limitation L2).
- `AI_ACT_ROLE` resolves in three steps: environment variable → `role` field in the scenario manifest → default `DEPLOYER`. `PROVIDER` currently selects an empty gate set and exits 0 with an explanatory message instead of raising.
- Requirement template gains `role` and `provider_implication`; the 14 existing requirements are set to `role: deployer` with an empty `provider_implication`. Deriving the provider requirements from Art. 16(a)–(l) is explicitly **not** part of this change.

### Changed (BREAKING) — Gate-Template Schema v2 (SPEC-01)

- `policy_checks` on every gate definition moves from a flat string list to a list of check objects (`id`, `policy`, `description`, `severity`, `legal_refs`, `evidence_level`) — severity now lives on the individual check, not on the whole gate, so a gate with heterogeneous checks is no longer forced onto its weakest severity.
- New `evidence_level` axis (`current`/`target`/`rationale`, values `E-0`…`E-3`) makes the evidentiary strength of each gate explicit, orthogonal to the existing AUTO/HYBRID/MANUAL automation classification.
- Gate-level `decision` is no longer authored directly; it is derived from check results (MUST violated → `block`; HYBRID → `manual_review`; SHOULD violated → `warn`; else `approve`).

## [2.0.0] — 2026-05-29 — Severity Model, Integrity-Suite Repair & Consistency Hardening

### Highlights

Post-archival consistency release that aligns the artefact with the thesis text and hardens credibility mechanisms. **Major bump** because the enforcement severity model changed: SHOULD-criteria are now non-blocking advisories (`warn`) instead of hard blocks (`deny`). Headline invariants are preserved: **105 rules, 103 OPA unit tests, 14/14 integrity checks, 16 gates, 10 AUTO / 6 HYBRID / 0 MANUAL**.

### Changed (BREAKING) — CDV Severity: SHOULD → `warn`

- **G-DEP-05 (Bias, R013)** is `SHOULD` per `requirements/R013.yaml`; its 10 rules changed from `deny` to `warn` (advisory, non-blocking). Gate `decision: block` → `warn`. A missing bias documentation no longer blocks a deployment — it is recorded as an advisory in the Evidence Store (`notes`).
- **G-DEP-02 (Safety Metrics)** SHOULD-criteria `subgroup_analysis` / `adversarial_tests` (7 rules) changed `deny` → `warn`; MUST thresholds (accuracy/latency/safety) stay `deny`.
- Rule inventory now **70 deny + 18 violation + 17 warn = 105** (was 105 deny/violation). `decision_method` distribution unchanged (10 AUTO / 6 HYBRID / 0 MANUAL).
- `gate_orchestrator.py` + `record_evidence.py` collect and persist advisory `warnings` (Evidence `notes`, outside the hashed payload — hash chain untouched).

### Fixed — Integrity-Regression Suite (was crashing in v1.1.0)

- Restored `WALKTHROUGH_KAP63.md` to the tracked path `docs/walkthrough/` (v1.1.0 referenced the git-ignored `docs/reference/`, so the suite crashed). Test path corrected; per-check exception guard added in `collect_results()` so a single broken check no longer aborts the suite. → **14/14**.

### Added — Cross-Implementation Hash Parity Guard

- `tests/test_hash_parity.py`: build-time guard asserting identical 13-field SHA-256 payload order across `record_evidence.py` ↔ `verify_hash_chain.py` ↔ v03 SQL trigger (wired into `tests/test_all.py`).

### Fixed — Evidence Store RBAC (privacy by design)

- `auditor_role` no longer has base-table `SELECT` (could read `notes`/`inserted_by`/`payload_id`); access restricted to the privacy view `vw_quality_gate_reporting`. Dead RLS policy `pol_select_auditor` removed.

### Added / Fixed — Reproducibility & Docs

- Root `requirements.txt` (PyYAML required, psycopg2-binary optional); `test_all.py` PyYAML preflight warning.
- README: corrected non-existent Terraform workflow → `deploy-aks.sh` (Azure CLI) + Helm; `infrastructure/terraform/` marked as reserved placeholder; status counts updated.
- `pipeline/test_pipeline_local.sh`: portable lowercase (`tr`) — runs on macOS bash 3.2.

> **Citation note:** cite the Zenodo **Concept DOI** ("all versions"), which resolves to this release. v1.1.0 (DOI 10.5281/zenodo.19920310) remains archived and unchanged.

---

## [1.1.0] — 2026-04-30 — First Stable Public Release

### Highlights

First stable public release of the GenAIOps Compliance Gates reference architecture. All 12 implementation phases are complete, the AKS cluster is live in Sweden Central, and the full PoC is reproducible end-to-end in 39 seconds per pipeline run. Repository scope tightened to PoC source code, infrastructure, and technical specs only — non-code narrative material (knowledge-base notes, related-work analysis, walkthrough essays, internal reports) is kept locally and gitignored.

### Added — Layer-1 Rego Unit Tests (Shift-Left)

- **103/103 OPA Rego unit tests** across all 10 Quality-Gate policies (`tests/run_all_rego_tests.sh`).
- Test pattern coverage: 13 PASS / 54 FAIL-basic / 17 FAIL-edge / 19 HYBRID (D3-Override scenarios).
- Layer-1 runs *before* Conftest-Gate-Checks in the CI pipeline (`feat(pipeline): add Layer-1 Rego unit tests (103/103) before Conftest gates`, commit `1ea378c6`).

### Added — Appendix F (Rule-to-Test-Mapping)

- `tools/extract_rule_test_mapping.py`: auto-generator for the rule-to-test mapping appendix (JSON + Markdown).
- `docs/appendix/rule_test_mapping.{json,md}`: ground-truth artefact for academic reproducibility.
- 10 per-gate sections with full rule inventory + test inventory + pattern classification.

### Added — Genesis-Eintrag-Konvention (Hash-Chain v03)

- Schema v03 migration `v02_to_v03_add_decision_method.sql`: adds `decision_method` column (AUTO / MANUAL / HYBRID).
- Genesis-block convention for first hash-chain entry (`coalesce(NEW.previous_hash, '')` for `audit_id = 1`).
- 13-field SHA-256 payload sequence documented in `docs/appendix/` and Schema-File comments.

### Added — Red-Path Demonstration Test

- Pipeline `pipeline-20260430-091901-cde6cb8a`: explicitly injected invalid `risk_class: "invalid"` to demonstrate Deploy BLOCKED.
- All 10 gates evaluated, G-PRE-01 caught the violation, decision banner shows `❌ GATE FAILURE — Deploy BLOCKED`, exit code 1.
- Reproducibility anchor for Red-Path walkthrough scenarios.

### Fixed — GATE_MAP corrections (`tools/extract_rule_test_mapping.py`)

- **G-PRE-05**: requirement reference `R012` → `R004` (Human Oversight, Art. 14 — corrects historical drift between gate-YAML, policy-file, and Top-Level-Workflow vs. tooling map).
- **G-OPS-03**: article reference `Art. 11` → `Art. 72` (Post-Market Surveillance — aligns with gate-YAML).
- **G-OPS-05**: article reference `Art. 11` → `Art. 12` (Logging / Manipulation security — aligns with gate-YAML).
- Appendix F regenerated against corrected GATE_MAP.

### Cleanup — Repo Hygiene

- Drift workflow `pipeline/.github/workflows/gate-pipeline.yml` archived to `legacy/pipeline_workflow/` with explanatory README. GitHub Actions reads only top-level `.github/workflows/`; the nested path was dead code with stale `R012` mapping.
- Branch `claude/plan-phase-4-poc-BDn8W` deleted (was 52 commits behind main, no unmerged work).

### Repo Hygiene — 2026-04-16

- **Repo-root cleanup.** Moved 56 MB of Conftest binaries (`conftest`, `conftest_*.tar.gz`) out of the repo root into `legacy/binaries/` (gitignored). Added `infrastructure/scripts/install-conftest.sh` — cross-platform (Linux/macOS, x86_64/arm64) installer that pulls the release artifact directly from GitHub.
- **Runtime/source separation.** Defined a proper layout under `evidence-store/data/{reports,sqlite}/` for runtime outputs (gitignored). Old runtime artifacts (93 pipeline reports, 5 SQLite DBs, 2 journals) archived in `legacy/runtime-artifacts/`.
- **Test reorganization.** Moved `test_all.py` and `test_integrity_regression.py` from repo root into `tests/`. Updated `REPO_ROOT` resolution and cross-references. Added `tests/README.md`.
- **Documentation publication.** Removed `/docs/` from `.gitignore` and reorganized by audience: `docs/{reference,reports,related-work,walkthrough,knowledge-base,images,architecture}/`. Internal-only material (session summaries, marketing drafts, internal review notes, strategy `.docx`/`.pdf`, older diagram versions) moved to `legacy/docs/`.
- **Naming consistency.** Stale path references in `gate-definitions/G-PRE-04`, `monitoring/k8s/prometheusrule-drift.yaml`, `tests/test_integrity_regression.py`, and several Markdown cross-references fixed.

---

## [Phase 12] — 2026-04-13 — Azure AKS Migration

### Added
- AKS deployment scripts: `infrastructure/scripts/deploy-aks.sh`, `teardown-aks.sh`.
- 3-node AKS cluster in Sweden Central, exposed via LoadBalancer service.
- OPA Gatekeeper installed cluster-wide with 3 ConstraintTemplates enforced at runtime.
- PostgreSQL evidence store deployed in-cluster with hash-chain triggers.
- `kube-prometheus-stack` installed via Helm for monitoring.

### Documentation
- Phase 12 deployment walkthrough and result protocol in `docs/walkthrough/`.
- High-risk classification correction: Art. 6 (1) + Annex I No. 11 MDR (instead of earlier Annex III).

---

## [Phase 11] — 2026-03-29 — Walkthrough + Integrity Suite

### Added
- 13-step Green/Red-Path walkthrough demonstration.
- **Integrity Regression Suite** (`tests/test_integrity_regression.py`): 14 static credibility checks covering demo fallbacks, soft-skip patterns, evidence-store strictness, hash-chain failure handling, HYBRID gate consistency, walkthrough drift, and CI conftest error visibility.
- Integrity Fix Report documenting 14 credibility issues identified and fixed.

### Fixed
- 14 credibility risks (F-01 to F-14) closed: among them missing `R001-R014.yaml` files surfaced by Requirements-Mapping test, soft-skip patterns in master test, false-green smoke test behavior, monitoring stub remnants in deployments.
- G-OPS-02 dual-input + CI stderr separation hardened.

---

## [Phase 10] — 2026-03-28 / 03-29 — GitHub Actions Pipeline

### Added
- `pipeline/.github/workflows/gate-pipeline.yml`: CI/CD with 10 Conftest gates (expanded from initial 4) covering full EU AI Act Art. 9–15 + 26.5 + Annex IV mapping.
- HYBRID gate semantics: `method` + `decision_log` recorded with each evidence entry.
- Docker build + push integrated into pipeline.
- Hash-chain verification step in CI.
- `tests/test_all.py` (Master Integration Test): 22/22 PASS across all 5 architecture pillars.

### Fixed
- stderr → JSON corruption in Conftest call (parsing error visibility).
- Conftest pinned to 0.56.0 with robust JSON parsing.
- Docker tag lowercase compliance + Dockerfile existence check.
- Dual-mode OPS Rego policies: identical policy compatible with both Gatekeeper (admission) and Conftest (CI).

---

## [Phase 9] — 2026-03-28 — Drift Detection

### Added
- `monitoring/drift_detector.py`: PSI (Population Stability Index) + Jensen-Shannon-Divergence drift score calculation.
- 21 unit tests + 16 E2E tests for drift detection (`monitoring/test_drift_detector.py`, `test_drift_e2e.py`).
- Kubernetes `CronJob` for scheduled drift evaluation (`monitoring/k8s/cronjob-drift-detector.yaml`).
- Prometheus alerting rules (`prometheusrule-drift.yaml`): warning at PSI > 0.1, critical at PSI > 0.2, with runbook URL pointing to closed-loop documentation.

---

## [Phase 8] — 2026-03-28 — Evidence Store + Closed-Loop Pipeline

### Added
- `pipeline/gate_orchestrator.py`: 3 scenarios (PASS / FAIL / Gatekeeper admission) with closed-loop evidence recording.
- Tamper detection (`pipeline/test_tamper_detection.py`): SHA-256 hash-chain integrity verification across evidence-store rows.
- Schema v02 (enterprise): role-based access control, schema separation.
- Schema v03: `decision_method` field + extended evidence row (E13 contract).
- Closed-Loop architecture documentation for demonstration Q&A preparation.

---

## [Phase 7] — 2026-03-28 — Gatekeeper ConstraintTemplates

### Added
- 2 ConstraintTemplates + 2 Constraints deployed to Minikube.
- Live ADMIT/REJECT verification on cluster.
- G-DEP-02 Safety Metrics ConstraintTemplate added later (2026-04-10) for 3-CT enforcement.

---

## [Phase 6] — 2026-03-28 — Local Cluster (Minikube + Helm + Gatekeeper)

### Added
- 4 setup scripts: `setup-minikube.sh`, `install-gatekeeper.sh`, `deploy-app.sh`, `smoke-test.sh` (8/8 PASS).
- `gatekeeper-values.yaml` and `prometheus-stack-values.yaml` for Helm-based installation.

---

## [Phase 5] — 2026-03-27 — Rego Policies + Conftest Tests

### Added
- 10 OPA/Rego policies (5 pre-deployment Conftest, 2 deployment Conftest, 3 operations Gatekeeper).
- ~100 Rego rules across the policy set.
- 21 fixtures for policy testing.

### Changed
- Initial 6 policies expanded to 10 to cover all 14 requirements (R001–R014).

---

## [Phase 4] — 2026-03-27 — Kubernetes Manifests

### Added
- 8 K8s YAMLs for the Healthcare Ambient AI Scribe scenario: Namespace, Deployment, Service, ConfigMap, PostgreSQL, Prometheus.
- Non-technical explanation of Phases 1–4.

---

## [Phase 3] — 2026-03-25 — Docker Compose Stack

### Added
- `scenarios/healthcare-ambient-ai-scribe/docker-compose.yml` with 4 services: App + PostgreSQL + Prometheus + Grafana.
- `.env.example` + later `.env`-based configuration.

---

## [Phase 2] — 2026-03-25 — Containerization

### Added
- Multi-stage `Dockerfile` for the FastAPI app, compliant with G-PRE-04 security baseline (non-root user, slim base image, no secrets in ENV, `readOnlyRootFilesystem`-ready).
- `.dockerignore`.

---

## [Phase 1] — 2026-03-25 — Application + Gate Fixtures

### Added
- FastAPI Healthcare Ambient AI Scribe mock app: `/transcribe`, `/health`, `/metrics` endpoints.
- Gate fixtures: `app_documentation.json`, `eval_results.json`.

---

## [Phase 0] — 2026-03-16 / 03-17 — Initial Structure & Alignment

### Added
- Initial PoC structure: README, gate definitions skeleton, evidence-store schema (v01 basic), 14 requirement specifications (R001–R014), policy-candidate inventory.
- 7-attribute gate template + 3 example gates.
- Requirements–EU-AI-Act mapping (Art. 9–15).
- 12-phase implementation tracker in README.
- Internal documents convention (`*_INTERNAL.md` gitignored).

### Fixed
- Phase 0 consistency fixes between thesis and PoC repo.
- R006 → R003 correction in policy-candidate mapping.
- Schema specification translated to English; internal-only schema spec gitignored.
