# Changelog

All notable changes to the **GenAIOps Compliance Gates** reference architecture.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning is by lifecycle phase (Phase 0 = pre-implementation alignment, Phases 1–12 = PoC build phases as listed in the [README progress table](README.md#implementierungsfortschritt)).

---

## [Unreleased]

### Repo Hygiene — 2026-04-16

- **Repo-root cleanup.** Moved 56 MB of Conftest binaries (`conftest`, `conftest_*.tar.gz`) out of the repo root into `legacy/binaries/` (gitignored). Added `infrastructure/scripts/install-conftest.sh` — cross-platform (Linux/macOS, x86_64/arm64) installer that pulls the release artifact directly from GitHub.
- **Runtime/source separation.** Defined a proper layout under `evidence-store/data/{reports,sqlite}/` for runtime outputs (gitignored). Old runtime artifacts (93 pipeline reports, 5 SQLite DBs, 2 journals) archived in `legacy/runtime-artifacts/`.
- **Test reorganization.** Moved `test_all.py` and `test_integrity_regression.py` from repo root into `tests/`. Updated `REPO_ROOT` resolution and cross-references. Added `tests/README.md`.
- **Documentation publication.** Removed `/docs/` from `.gitignore` and reorganized by audience: `docs/{reference,reports,related-work,walkthrough,knowledge-base,images,architecture}/`. Internal-only material (session summaries, marketing drafts, internal review notes, strategy `.docx`/`.pdf`, older diagram versions) moved to `legacy/docs/`.
- **Naming consistency.** `docs/knowledge-base/` subfolders renamed to kebab-case (`Docker/`→`docker/`, `Kubernetes/`→`kubernetes/`, `cloud computing/`→`cloud-computing/`). Stale path references in `gate-definitions/G-PRE-04`, `monitoring/k8s/prometheusrule-drift.yaml`, `tests/test_integrity_regression.py`, and several Markdown cross-references fixed accordingly.

---

## [Phase 12] — 2026-04-13 — Azure AKS Migration

### Added
- AKS deployment scripts: `infrastructure/scripts/deploy-aks.sh`, `teardown-aks.sh`.
- 3-node AKS cluster in Sweden Central, LoadBalancer at `74.241.179.251`.
- OPA Gatekeeper installed cluster-wide with 3 ConstraintTemplates enforced at runtime.
- PostgreSQL evidence store deployed in-cluster with hash-chain triggers.
- `kube-prometheus-stack` installed via Helm for monitoring.

### Documentation
- Phase 12 deployment walkthrough and result protocol in `docs/walkthrough/`.
- High-risk classification correction: Art. 6 (1) + Annex I No. 11 MDR (instead of earlier Annex III).

---

## [Phase 11] — 2026-03-29 — Walkthrough + Integrity Suite

### Added
- 13-step Green/Red-Path walkthrough for Kapitel 6.3 (`docs/reference/WALKTHROUGH_KAP63.md`).
- **Integrity Regression Suite** (`tests/test_integrity_regression.py`): 14 static credibility checks covering demo fallbacks, soft-skip patterns, evidence-store strictness, hash-chain failure handling, HYBRID gate consistency, walkthrough drift, and CI conftest error visibility.
- Integrity Fix Report (`docs/reports/INTEGRITY_FIX_REPORT_2026-03-29.md`) documenting 14 credibility issues identified and fixed.

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
- Closed-Loop architecture documentation (`docs/reference/CLOSED_LOOP_ERKLAERUNG.md`) for Kolloquium Q&A preparation.

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
- Walkthrough doc for Kap. 5.3 Policy-as-Code (`docs/walkthrough/kap5_3_policy_as_code_ergaenzung.md`).

### Changed
- Initial 6 policies expanded to 10 to cover all 14 requirements (R001–R014).

---

## [Phase 4] — 2026-03-27 — Kubernetes Manifests

### Added
- 8 K8s YAMLs for the Healthcare Ambient AI Scribe scenario: Namespace, Deployment, Service, ConfigMap, PostgreSQL, Prometheus.
- Kolloquium-friendly explanation of Phases 1–4 (`docs/walkthrough/poc_phasen_1_bis_4_erklaerung.md`).

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
