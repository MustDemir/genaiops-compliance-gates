# GenAIOps Compliance Gates — EU AI Act Compliant Quality Gate System

A cloud-native reference architecture for operationalizing regulatory, technical, and strategic requirements in GenAI systems through automated Quality Gates — with full EU AI Act (Regulation 2024/1689) compliance built into CI/CD/CT pipelines.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Changelog](https://img.shields.io/badge/Changelog-Phase%201--12-blue)](CHANGELOG.md)
[![Documentation](https://img.shields.io/badge/Docs-published-brightgreen)](docs/README.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19920310.svg)](https://doi.org/10.5281/zenodo.19920310)

> **Reproducibility:** the exact state cited in the submitted and graded Master's thesis (14 requirements, 16 gates, 10 AUTO / 6 HYBRID / 0 MANUAL, 108 rules, 141 unit tests) is frozen under the Git tag `thesis-v1.0` and archived under the Zenodo DOI above. Everything from that tag forward is post-thesis further development (see [CHANGELOG.md](CHANGELOG.md)) and may report different counts.

---

## What This Is

Enterprise GenAI systems face a triple challenge: they must be **technically robust**, **strategically governed**, and **regulatorily compliant** — simultaneously and continuously. This reference architecture solves that by embedding 17 automated Quality Gates across the entire GenAI lifecycle, enforced through Policy-as-Code.

**Key idea:** Compliance is not a document you write after deployment. It's a property the system enforces at every pipeline stage.

### Core Capabilities

- **17 Quality Gates** across 3 lifecycle phases (Pre-Deployment, Deployment, Operations)
- **Policy-as-Code** via OPA/Rego with three enforcement pillars (Conftest, Gatekeeper, Decision Logs)
- **17 implemented Rego Policies** with **166 deny/violation/warn rules + 173 unit tests** covering Art. 3(14), 6(1a)/(1b), 9, 10, 11, 12, 13, 14, 15, 25, 26 (1+5+7), 27, 47, 48, 50, 72, 73 + Annex III No. 2 + Annex IV
- **Two orthogonal classification axes** — *automatability* (AUTO/HYBRID/MANUAL) and, new in schema v2, *evidentiary strength* (E-0 … E-3)
- **Severity on the check, not the gate** — a gate with heterogeneous checks is no longer dragged down to its weakest severity
- **Role as an architecture parameter** — PROVIDER / DEPLOYER / BOTH selects which gates apply at all
- **Immutable Evidence Store** with SHA-256 hash-chain for audit-proof traceability
- **Full EU AI Act mapping**: Art. 9–15 → Requirements → Gates → Policies → Evidence
- **Automated gate decisions** using the CDV Framework (Contract → Validation → Severity → Pipeline-Decision)
- **Post-Market Surveillance** with drift detection and incident reporting (Art. 72, Art. 26.5)
- **3-layer test architecture** — Layer 1: 173 Rego unit tests (OPA, fail-fast); Layer 2: Conftest gate evaluations; Layer 3: SHA-256 hash-chain verification per pipeline run

## Legal Status

The architecture is maintained against the **consolidated** EU AI Act, i.e. Regulation (EU) 2024/1689 **as amended by Regulation (EU) 2026/1744** (*Digital Omnibus on AI*, in force since 27 July 2026, OJ L of 24 July 2026).

| What changed | Effect here |
|---|---|
| High-risk application date deferred from 2 Aug 2026 to **2 Dec 2027** (Annex III) / **2 Aug 2028** (Annex I) | `audit_trigger` in the affected requirements |
| **Art. 3(14)** redefined — "safety component" now has two OR-linked arms (intended purpose / failure impact), each protecting persons **or property** | new Art. 6 decision tree in G-PRE-01 |
| **Art. 6(1a)/(1b)** inserted — 1a narrows the purpose arm, 1b shields the failure-impact arm from that narrowing | checks C-A1 … C-A7 |
| **Art. 10(5)** deleted, legal basis moved to the new **Art. 4a** (extended to deployers) | R006 / G-DEP-01 references |
| **Art. 25(2)/(4)** replaced — the role transfer became a two-sided, documented act | G-OPS-06 handover artefacts |
| **Art. 27(4)/(5)** eased — deployers may cross-reference an existing DPIA | R012 |
| **Art. 72(3)** — the post-market monitoring plan is now part of the Annex IV technical documentation | R010 |

Both binding language versions were reconciled against the Official Journal; the German text is archived under [`docs/legal/`](docs/legal/). Where the versions diverge (e.g. official German *Sicherheitsbauteil*, not *Sicherheitskomponente*), the finding is recorded in the policy header.

> **Not legal advice.** Interpretations that go beyond the wording are marked as hypotheses in the code — most prominently the reading of Art. 6(1a)/(1b), for which no Commission guidelines and no case law exist yet.

## Architecture Overview

### Five-Pillar Model

| Pillar | Component | Purpose |
|--------|-----------|---------|
| **S1** | Design Principles (DP1–DP5) | Architectural foundation and cloud-native integrability |
| **S2** | Quality Gate Control System | 17 lifecycle-integrated gates, `schema_version: 2` template |
| **S3** | Policy Engine | OPA/Rego policies, Conftest (CI), Gatekeeper (K8s admission), Decision Logs |
| **S4** | Evidence Store | PostgreSQL + Blob Storage, hash-chain integrity, RBAC, schema separation |
| **S5** | Monitoring & PMS | Drift detection (PSI/Jensen-Shannon), incident reporting, sidecar pattern |

### Design Principles

| ID | Principle | EU AI Act Anchor |
|----|-----------|-----------------|
| DP1 | Compliance as controllable lifecycle process | Art. 9 (Risk Management) |
| DP2 | End-to-end traceability chain | Art. 11 (Technical Documentation) |
| DP3 | Gate template as standardization unit | Art. 11 + Annex IV |
| DP4 | Separation of governance dimensions, integrated decision | Art. 14 (Human Oversight) |
| DP5 | Cloud-native integrability | Art. 15 (Robustness) |

### Automation Classification

The architecture achieves a **10:7:0 distribution** — 10 fully automated gates, 7 hybrid gates, 0 manual-only gates. A dedicated **D3×D2 Override Rule** ensures that gates requiring First-Degree Human Oversight (EU AI Act Art. 14, operationalized following Laux 2024, S. 2857) are capped at HYBRID automation, regardless of technical feasibility.

```
Gate Inclusion Rule: D1 (Gate-Eignung) → D3 (Regulatory) → D2 (Technical) → Classification
                     ↓
                     D3=FIRST-DEGREE → D2 max HYBRID (Automation Ceiling)
```

### Evidentiary Strength (E-0 … E-3)

Automatability answers *how much of a check runs without a human*. It says nothing about *how hard the evidence is to fake*. Schema v2 therefore adds a second, **orthogonal** axis: every gate declares `evidence_level.current` and `.target`.

| Level | What is actually checked | Cost of faking it |
|---|---|---|
| **E-0** | A document somebody wrote (JSON/YAML manifest, pod annotation) | Editing text |
| **E-1** | An artefact **produced and signed** by a tool; signature and producer identity are verified | Compromising the CI identity |
| **E-2** | The actual cluster state via the Kubernetes API | Manipulating the running system |
| **E-3** | A property **over time**, measured rather than configured | Manipulating the telemetry chain |

Two consequences the architecture takes seriously:

- **A pod annotation is E-0, not E-2.** An annotation *asserts* a state, it does not *prove* one. Every Gatekeeper-based gate here is therefore classified E-0 today, even though it runs at admission time.
- **The axes really are independent.** A HYBRID gate can carry E-3 evidence; an AUTO gate can sit on E-0. G-OPS-05 demonstrates this within a single gate: its hash-chain check is E-1 while its annotation check is E-0.

The D3×D2 automation ceiling is untouched by this axis.

### Severity on the Check, Not the Gate

A gate bundles heterogeneous checks. Putting one severity on the whole gate forces the strictest check down to the weakest one. Since schema v2, `policy_checks` is a list of objects, each with its own `severity`, `legal_refs` and optional `evidence_level`:

```yaml
policy_checks:
  - id: "C-01"
    policy: "policy_safety_metrics"
    description: "accuracy >= 0.85, latency_p95 <= 2000ms, safety_score >= 0.90"
    severity: "MUST"          # -> deny (blocking)
    legal_refs: ["Art. 15"]
  - id: "C-02"
    policy: "policy_safety_metrics"
    description: "subgroup_analysis and adversarial_tests performed"
    severity: "SHOULD"        # -> warn (advisory)
    legal_refs: ["Art. 15"]
```

The gate decision is **derived**, never authored, in this order (do not reorder — a HYBRID gate with a violated MUST still blocks):

```
1. any MUST violated   -> block
2. gate is HYBRID      -> manual_review
3. any SHOULD violated -> warn
4. otherwise           -> approve
```

Rego messages carry the check id — `<GATE-ID>/<CHECK-ID> (<Requirement>, <Legal-Ref>): <message>` — so each advisory in the Evidence Store traces back to the specific check that raised it.

### Role as an Architecture Parameter

> **The provider owes the properties of the system. The deployer owes the properties of its use.**

Art. 16(a) is the hinge: providers must ensure their high-risk systems meet Chapter III Section 2 — i.e. **Art. 9–15 are provider duties**. The deployer duties live in Art. 26 (and Art. 27 for the FRIA).

| Topic | Provider | Deployer |
|---|---|---|
| Risk management | Art. 9 | Art. 26(5) — monitor, suspend, report |
| Data | Art. 10 — training/validation/test data | Art. 26(4) — **input** data, as far as controlled |
| Technical documentation | Art. 11, Art. 18 | — |
| Logging | Art. 12, Art. 19 | Art. 26(6) — retain ≥ 6 months |
| Transparency | Art. 13 — write the instructions | Art. 26(1) — use accordingly, Art. 26(11) — inform affected persons |
| Human oversight | Art. 14 — **design** it | Art. 26(2) — **staff** it (competence, training, authority) |
| Fundamental-rights impact assessment | — | Art. 27 |

`AI_ACT_ROLE` resolves in three steps: environment variable → `role` in the scenario manifest → default `DEPLOYER`. Each gate declares a `role_scope`; the orchestrator filters accordingly. All 17 gates are currently `["deployer"]` — the correct label for a deliberately deployer-scoped architecture, not a downgrade. `PROVIDER` therefore selects an empty gate set today and exits cleanly with an explanatory message.


### Process Model: From Regulation to Automated Quality Gate

<a href="docs/images/process_regulation_to_pipeline_v2_export.png">
  <img src="docs/images/process_regulation_to_pipeline_v2_export.png" width="100%" alt="Process Model: Regulation → Policy-as-Code → CI/CD Pipeline → K8s Runtime Enforcement" />
</a>
*7-phase operationalization process: EU AI Act (Art. 9–15) → Requirements → Gate Definition → Rego Policy → Orchestrator → CI/CD Pipeline → Evidence Store → K8s Runtime Enforcement. BPMN 2.0 notation. Legend (Start / End / Activity / Gateway / Artefact) and DSR cycle annotations (Relevance / Design / Rigor) shown at the bottom. **Click image to view full resolution (3176×3200).****

## Repository Structure

```
genaiops-compliance-gates/
├── README.md
├── AGENTS.md                   # Standing architecture principles for Claude Code sessions
├── specs/                      # Implementation specs (SPEC-01 … SPEC-03)
├── docs/
│   ├── appendix/               # Auto-generated rule-to-test mapping (tools/extract_rule_test_mapping.py)
│   ├── architecture/           # Architecture diagrams (Five-Pillar, Gate Flow, Pipeline)
│   ├── images/                 # Process model + diagram exports
│   ├── legal/                  # Official Journal primary sources (Reg. (EU) 2026/1744, DE)
│   └── walkthrough/            # Conftest test results (Phase 5)
├── gate-definitions/           # Quality Gate specifications (YAML, schema_version 2)
│   ├── gate_template.yaml      # Gate template incl. evidence_level + role_scope
│   ├── pre-deployment/         # G-PRE-01 to G-PRE-05
│   ├── deployment/             # G-DEP-01 to G-DEP-06
│   └── operations/             # G-OPS-01 to G-OPS-06
├── policies/                   # OPA/Rego policy implementations
│   ├── pre-deployment/         # Conftest policies (CI stage)
│   ├── deployment/             # Conftest + Gatekeeper policies
│   └── operations/             # Gatekeeper admission policies
├── pipeline/
│   └── .github/workflows/      # GitHub Actions with gate-integrated stages
├── evidence-store/
│   ├── schema/                 # PostgreSQL DDL (v01 basic, v02 enterprise, v03 decision_method)
│   ├── migrations/             # Schema migrations (v03 decision_method, v04 ai_act_role)
│   └── scripts/                # record_evidence.py, verify_hash_chain.py
├── monitoring/                 # Drift detection, PMS, sidecar configuration
├── infrastructure/
│   ├── scripts/                # AKS/Minikube provisioning via Azure CLI (deploy-aks.sh etc.)
│   ├── terraform/              # Reserved for declarative IaC (not part of PoC; see terraform/README.md)
│   └── helm/                   # Kubernetes deployments (OPA Gatekeeper, app, monitoring)
├── scenarios/
│   └── healthcare-ambient-ai-scribe/  # PoC scenario: High-risk AI (Art. 6 (1) + Annex I No. 11 MDR)
├── requirements/               # R001–R014 requirement specifications (from EU AI Act)
├── prospective/                # Research outlooks (F5) — Art.-25 sketch, now superseded by G-OPS-06
└── tests/                      # test_all.py, integrity regression, hash parity + migration guards
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Orchestration** | Kubernetes (AKS) | Container orchestration, admission control |
| **GitOps** | ArgoCD | Declarative deployments, drift reconciliation |
| **Policy Engine** | OPA/Rego, Conftest, Gatekeeper | Policy-as-Code evaluation at CI + admission |
| **CI/CD** | GitHub Actions | Pipeline orchestration with gate stages |
| **Evidence Store** | Azure PostgreSQL + Blob Storage | Structured metadata + unstructured artifacts |
| **Monitoring** | Prometheus, Grafana, OpenTelemetry | Metrics, drift detection, alerting |
| **IaC** | Azure CLI scripts, Helm | Infrastructure provisioning + app deployment (Terraform reserved, not in PoC) |
| **GenAI Runtime** | Azure OpenAI Service, LangChain | LLM inference, RAG pipeline |

## Quality Gate Framework

Each of the 17 gates follows a standardized template (`schema_version: 2`):

```yaml
schema_version: 2
id: G-PRE-01
name: "Risiko-Klassifikation"
dimension: "regulatorisch"
lifecycle_phase: "pre-deployment"
trigger: "PR merge to main — Conftest evaluates app_documentation.json in CI"

evidence_level:                 # how strong is the evidence, independent of automation
  current: "E-0"
  target: "E-2"
  rationale: "Whether a system triggers switching operations is checkable
              against the system state and need not rest on self-declaration."

policy_checks:                  # severity per check, not per gate
  - id: "C-A3"
    policy: "policy_risk_classification"
    description: "Art. 6(1a) invoked but Arm B not assessed — step 4 is not skippable"
    severity: "MUST"
    legal_refs: ["Art. 6 Abs. 1a", "Art. 6 Abs. 1b"]
    evidence_level: null        # null = inherit the gate default

evidence_required: [...]
decision: "derived"             # derived from check results, never authored
automation: "HYBRID"            # D3xD2 ceiling — untouched by evidence_level
role_scope: ["deployer"]        # provider | deployer | both
owner: "AI Governance Lead"
audit_trail: { enabled: true, evidence_store_ref: "evidence://gates/pre-deployment/G-PRE-01" }
waiver: { allowed: true, requires: "Governance Lead + CTO Approval, 30 days" }
links: { requirements: [...], eu_ai_act_refs: [...] }
```

### Gate Distribution

| Phase | Gates | Automation |
|-------|-------|-----------|
| **Pre-Deployment** | G-PRE-01 to G-PRE-05 | 1 AUTO (G-PRE-04), 4 HYBRID (G-PRE-01/02/03/05 — D3-Override fuer First-Degree-Oversight) |
| **Deployment** | G-DEP-01 to G-DEP-06 | 5 AUTO, 1 HYBRID (G-DEP-03 Transparency-Docs) |
| **Operations** | G-OPS-01 to G-OPS-06 | 4 AUTO, 2 HYBRID (G-OPS-01 Human-Oversight-Wirksamkeit, G-OPS-06 Rollenwechsel) |
| **Summe** | **17 Gates** | **10 AUTO, 7 HYBRID, 0 MANUAL** |

### Two Gates Worth a Closer Look

**G-PRE-01 — the Art. 6 "safety component" decision tree.** Whether an AI system falls under Annex III No. 2 (critical infrastructure) hangs entirely on one legal definition. The gate walks the tree from Art. 3(14) and Art. 6(1a)/(1b):

```
1. Deployed in water/gas/heat/electricity supply, critical digital
   infrastructure or road traffic?      no -> NOT_IN_SCOPE
2. ARM A — is the intended purpose to prevent or mitigate risks to the
   health and safety of persons OR PROPERTY?   yes -> SAFETY_COMPONENT
3. Art. 6(1a) exclusion invoked (solely assistance / optimisation /
   efficiency / automation / usability / quality control)?
                                        yes -> step 4 is MANDATORY
4. ARM B — would failure or malfunction endanger health and safety?
                                        yes -> SAFETY_COMPONENT (overrides 3)
                                        no  -> NO_SAFETY_COMPONENT
```

The load-bearing check is **C-A3**: invoking the Art. 6(1a) exclusion without assessing the failure impact is denied. Step 4 is not skippable — "it's only optimisation" is not a defence unless you also show the failure impact is uncritical.

The most interesting one is **C-A7**: where a system's output only takes effect through a human decision, Arm B turns on whether that oversight is *effective*. **That couples the Art. 6 classification to oversight quality under Art. 26(2)** — whoever classifies themselves as "not high-risk *because* a human sits in between" owes proof that this oversight works. C-A7 demands the reference to G-OPS-01, which already checks those effectiveness conditions.

**G-OPS-06 — the role change (Art. 25).** A deployer becomes a provider on rebranding (a), substantial modification (b), or a purpose change to high-risk (c). Severity differs per trigger: (a) and (c) are binary offences and are MUST; only (b) stays SHOULD, because its threshold depends on Art. 3(23) and the still-pending Art. 97 delegated acts. C-25c does not trust a manifest boolean — it runs the G-PRE-01 `classification` rule against the purpose state before and after the change. Since the Omnibus, the transfer also requires handover artefacts (Art. 25(2)/(4)).

Two boundaries of this gate, stated because they are easy to get wrong:

- **Art. 25(2)/(4) does not carry the plain deployer.** Paragraph 2 obliges the *initial provider towards the new providers* — the claim only arises *after* a role transfer. Paragraph 4 governs provider ↔ third-party supplier, where the deployer is not a party. Supplier verification in the normal case (no role change) has to be argued from Art. 13 and Art. 26(1)/(5)/(6)/(9) — completeness of the *instructions for use* — not from Art. 25. G-OPS-06 is unaffected because C-25d only fires *after* a binding trigger, i.e. once the deployer has itself become the new provider.
- **The carve-out shifts the decisive moment out of the pipeline.** Art. 25(2) does not apply where the initial provider clearly specified that its system must not be turned into a high-risk system — a unilateral, up-front opt-out. The real check therefore belongs *before contract signature*; a gate that reports it at rollout reports it too late to negotiate. G-OPS-06 remains useful as an evidence and escalation point, but it does not replace a procurement check.

## PoC Scenario: Healthcare Ambient AI Scribe

The architecture is demonstrated using a **high-risk AI system** (EU AI Act Art. 6 (1) in conjunction with Annex I No. 11 — safety component of a Clinical Decision Support System classified as a medical device under MDR 2017/745): an Ambient AI Scribe that transcribes and summarizes medical consultations.

**Why this scenario:**
- High-risk classification → maximum regulatory requirements
- Sensitive health data → GDPR Art. 9 + AI Act convergence
- Stochastic outputs → quality assurance for generative content
- Full lifecycle coverage → 17 gates designed, **17 with Rego policies** (local + CI), enforced in GitHub Actions (3-layer architecture: 173 OPA unit tests + Conftest gates + hash-chain verify)

## Traceability Chain

Every regulatory requirement is traceable from norm to evidence:

```
EU AI Act Article → Requirement (R-xx) → Design Principle (DP) → Quality Gate (G-xx) → Policy (Rego) → Evidence (Audit Trail)
```

This six-level traceability chain ensures that for any audit finding, the path back to the originating regulation is documented and verifiable.

## Getting Started

> ✅ **Status: v1.0.0 — first stable release (2026-04-30).** All 12 implementation phases complete. Live AKS deployment in Sweden Central. Reproducible end-to-end in 39 seconds per pipeline run.

### Prerequisites

- Azure subscription with AKS enabled
- Azure CLI (`az`) >= 2.50 — used by `infrastructure/scripts/deploy-aks.sh`
- Helm >= 3.12
- OPA/Conftest CLI — install via `./infrastructure/scripts/install-conftest.sh`
- kubectl configured for AKS cluster

### Quick Start

**Fast path via Makefile** — see all targets with `make help`. The most common workflows:

```bash
# Install Conftest CLI (cross-platform, Linux/macOS, x86_64/arm64)
make install-conftest                 # → /usr/local/bin (sudo)
NO_SUDO=1 make install-conftest       # → ~/.local/bin

# Run the full PoC stack on a local Minikube (~5 min on a laptop)
make local-up                         # minikube + gatekeeper + monitoring + app + smoke
make verify                           # master integration + integrity regression + smoke

# Tear down
make local-down

# Cloud variant: provision AKS in Sweden Central
make aks-up
make aks-down
```

**Detailed manual flow** (if you want to run the steps individually):

```bash
# 1. Provision infrastructure (AKS + ACR + stack) via Azure CLI
bash infrastructure/scripts/deploy-aks.sh

# 2. Deploy OPA Gatekeeper
cd infrastructure/helm && helm install gatekeeper gatekeeper/gatekeeper --namespace gatekeeper-system

# 3. Apply policies
cd ../../policies && conftest test --policy pre-deployment/ scenarios/healthcare-ambient-ai-scribe/

# 4. Initialize Evidence Store (v02 base schema + v03 + v04 migrations)
cd ../evidence-store && psql -f schema/evidence_store_schema_v02_enterprise.sql \
  && psql -f migrations/v02_to_v03_add_decision_method.sql \
  && psql -f migrations/v03_to_v04_add_ai_act_role.sql

# 5. Run pipeline with gates — see pipeline/.github/workflows/ for CI/CD integration
```

### Running the Gates Locally

```bash
# Full local suite: Rego unit tests, consistency, pipeline scenarios, hash chain
python3 tests/test_all.py                       # requires PyYAML
bash    tests/run_all_rego_tests.sh --quiet     # requires `opa` on PATH
python3 tests/test_integrity_regression.py      # static credibility checks

# Closed-loop pipeline
python3 pipeline/gate_orchestrator.py --scenario pipeline/scenarios/poc_healthcare_pass.json
python3 pipeline/gate_orchestrator.py --scenario pipeline/scenarios/poc_healthcare_fail.json
```

**Selecting the AI Act role.** The gate set is filtered by role; the default is `DEPLOYER`:

```bash
AI_ACT_ROLE=DEPLOYER python3 pipeline/gate_orchestrator.py --scenario ...   # 10/10 gates
AI_ACT_ROLE=BOTH     python3 pipeline/gate_orchestrator.py --scenario ...   # union, no double execution
AI_ACT_ROLE=PROVIDER python3 pipeline/gate_orchestrator.py --scenario ...   # empty set today, exits 0
```

The role is written into the Evidence Store **and into the hashed payload**, so an auditor can prove which role a run was evaluated under.

### Evidence Store Schema v04 — Migration Without a Chain Break

`ai_act_role` had to enter the hashed payload, but existing records were hashed without it. Rather than rehashing history or starting a new chain, the field enters the payload only **from a per-database cutoff `audit_id`** — written by the migration as `max(audit_id) + 1`, and `1` for a fresh database.

```
audit_id <  cutoff  ->  13-field payload (v03), unchanged and still verifiable
audit_id >= cutoff  ->  14-field payload (v04, incl. ai_act_role)
```

All three implementations apply the same cutoff: `record_evidence.py`, `verify_hash_chain.py` and the `set_hash_chain()` trigger. `tests/test_hash_chain_migration.py` proves the four properties that make this sound — a pure v03 chain verifies, a chain **spanning** the cutoff verifies, tampering below the cutoff is still caught, and tampering with `ai_act_role` above the cutoff is caught.

## Post-Thesis Development

The state cited in the graded thesis is frozen under the tag `thesis-v1.0` and stays reproducible (`git checkout thesis-v1.0`). Everything below happened after it. Specifications live in [`specs/`](specs/); standing principles for future sessions in [`AGENTS.md`](AGENTS.md).

| Spec | What it changed | Status |
|---|---|---|
| **SPEC-01** | `schema_version: 2` — `evidence_level` axis, severity per check, derived gate decision, check-ids in Rego messages | done |
| **SPEC-02** | Art. 6 "safety component" decision tree in G-PRE-01 (C-A1 … C-A7 + computed `classification`) | done |
| **SPEC-03** | Role parameter PROVIDER/DEPLOYER/BOTH, Art.-25 gate promoted to G-OPS-06, Evidence Store schema v04 | done |

**Counts moved.** 16 → 17 gates, 10 AUTO / 6 HYBRID → 10 AUTO / 7 HYBRID, 108 → 166 rules, 141 → 173 unit tests. The published figures remain reproducible under the tag — see [CHANGELOG.md](CHANGELOG.md).

**Known open points**, carried deliberately rather than silently:

- **Provider requirements are not derived yet.** Art. 16(a)–(l) with Art. 17–20, 43, 47, 48, 49(1) is the largest open block; `AI_ACT_ROLE=PROVIDER` therefore matches no gate today.
- **Seven checks reference Rego policies that do not exist yet** (DESIGN-ONLY). Tracked by the low-severity `GATE_POLICY_FILE_EXISTS` check in the integrity regression rather than hidden.
- **The Art. 6(1a)/(1b) reading is a hypothesis** — no guidelines, no case law. Marked as such in the policy header.
- **`evidence_level.current` is E-0 almost everywhere.** Raising gates to E-1 requires signed CI attestations; the drift detector (`monitoring/drift_detector.py`) is already the E-3 reference implementation but is not yet wired in as an evidence source.
- **The role is a property of the pipeline run, not of the system.** `AI_ACT_ROLE` is resolved per run (env var → scenario manifest → default). Whether the role state should instead be tracked *per system* or *per system version* is undecided; the current design makes the simplest choice and defers the question.
- **G-DEP-01 references Art. 10 and Art. 11 while being deployer-scoped.** Both are provider duties, and the Art. 11 / Annex IV technical documentation is owed to *authorities*, not to the deployer. The deployer-side anchor is Art. 26(4) (input-data relevance). Left unchanged for now because the correction also touches the R002 requirement mapping and belongs with the provider derivation.
- **Versioning and release tagging are unresolved.** `thesis-v1.0` points at a *later* commit (2026-07-06) than the `v2.0.0` (2026-05-29) and `v1.1.0` (2026-04-30) release tags, while `CITATION.cff` declares `version: 2.0.0` with three DOIs. Which commit corresponds to the figures cited in the thesis is therefore not unambiguously established. **New release tags and Zenodo pushes are on hold until this is settled** — ordinary development on branches is not affected.

## Implementierungsfortschritt

> Strategie: Lokal-first (Phase 1–11 kostenlos auf Minikube), Azure erst Phase 12. Geschaetzter Aufwand: ~30–42h ueber 4–6 Wochen.
>
> **Reproduzierbarkeits-Anker:** [GitHub Actions Run #21](https://github.com/MustDemir/genaiops-compliance-gates/actions/runs/24589487911) (2026-04-17, success in 39 s, all 10 gates PASS, hash-chain verified).
>
> **AKS-Verifikation – 1. Lauf:** 2026-04-13, Erst-Instanziierung (Green/Red Path, 24 Screenshots → Thesis Anhang C).
>
> **AKS-Verifikation – 2. Lauf:** 2026-05-27, unabhängiges Re-Deployment zur Bestätigung der Reproduzierbarkeit (Green-Path ADMIT, Red-Path REJECT, Evidence Store v02+v03, Monitoring); zwei `deploy-aks.sh`-Defekte behoben → Instanziierung in einem Durchlauf. Details: [docs/session-logs/2026-05-27-aks-redeploy-verification.md](docs/session-logs/2026-05-27-aks-redeploy-verification.md).

<!-- PROGRESS-START -->
> Gesamtfortschritt: `████████████████████` **100%** (12/12 Phasen)

| Phase | Beschreibung | Fortschritt | Status |
|-------|-------------|------------|--------|
| **1** | App entwickeln (FastAPI + Mock-Endpoint) | `████████████████████` 100% | done |
| **2** | Containerisieren (Dockerfile, Multi-Stage, Non-Root) | `████████████████████` 100% | done |
| **3** | Docker Compose (App + DB + Prometheus + Grafana) | `████████████████████` 100% | done |
| **4** | K8s-Manifeste (Deployment, Service, ConfigMap, Compliance-Annotations) | `████████████████████` 100% | done |
| **5** | Rego-Policies + Conftest-Tests (17 Gates) | `████████████████████` 100% | done |
| **6** | Lokaler Cluster (Minikube) + Helm + Gatekeeper | `████████████████████` 100% | done |
| **7** | Gatekeeper ConstraintTemplates (ADMIT/REJECT live) | `████████████████████` 100% | done |
| **8** | Evidence Store + Closed-Loop Pipeline | `████████████████████` 100% | done |
| **9** | Drift Detection (PSI/JSD + Prometheus + Grafana) | `████████████████████` 100% | done |
| **10** | GitHub Actions Pipeline (Conftest CI + Evidence) | `████████████████████` 100% | done |
| **11** | Green/Red Path Walkthrough + Screenshots | `████████████████████` 100% | done |
| **12** | Azure AKS Migration (Sweden Central, LoadBalancer) | `████████████████████` 100% | done |
<!-- PROGRESS-END -->

### Artefakt-Status

| Komponente | Status | Details |
|-----------|--------|--------|
| Requirements (R001–R014) | done | 14 YAML-Specs, EU AI Act Art. 9–15 Mapping |
| Evidence Store Schema | done | v01 (basic) + v02 (enterprise) + v03 (decision_method, E13) |
| Evidence Store Scripts | done | record_evidence.py + verify_hash_chain.py, SQLite + PostgreSQL, Hash-Chain verified |
| Decision-Log-Fixtures | done | G-PRE-01 (manual_review) + G-PRE-05 (governance_approval), HYBRID-Demo ready |
| Gate Template | done | 7-Attribut-Template, 3 Beispiel-Gates |
| Policy-Kandidaten | done | 29 Kandidaten dokumentiert (22 Conftest, **4 Gatekeeper-ConstraintTemplates**, 3 Decision Logs); 166 deny/violation/warn-Regeln total |
| Healthcare Scribe App | done | FastAPI Mock-Endpoint, /transcribe, /health, /metrics |
| Gate-Fixtures | done | app_documentation.json, eval_results.json |
| K8s-Manifeste | done | 8 YAMLs: Namespace, Deployment, Service, ConfigMap, PostgreSQL, Prometheus |
| OPA/Rego-Code | done | 17 Policies, **166 deny/violation/warn-Regeln** (auditierbar via tools/extract_rule_test_mapping.py), 30 Fixtures |
| Integration Tests | done | tests/test_integration_*.py — covered via Master Integration Test (22/22 PASS) |
| **Layer-1 Rego Unit Tests** | done | **173/173 PASS** via `tests/run_all_rego_tests.sh` (OPA v1.14.1+); Shift-Left vor Conftest-Gate-Checks; Verteilung siehe `docs/appendix/rule_test_mapping.md` |
| **Rule-to-Test-Mapping (Appendix)** | done | Auto-generiert via `tools/extract_rule_test_mapping.py` → `docs/appendix/rule_test_mapping.{json,md}` (10 Policies × Per-Gate-Sektionen) |
| Tamper-Detection Spec | done | Dokumentiert: 8 erkannte Angriffsvektoren, 6 bekannte Limitationen, 3 Protection Layers |
| Walkthrough-Dokumentation | done | 13-Schritte Walkthrough (Pre-Dep → Dep → Ops → HYBRID → Tamper) |
| Schema-Evolution-Dok | done | v01→v02→v03 Changelog mit Rationale und Hash-Trigger-Details |
| Minikube Deployment Scripts | done | 4 scripts: setup-minikube, install-gatekeeper, deploy-app, smoke-test (8/8 PASS) |
| Helm Values | done | gatekeeper-values.yaml + prometheus-stack-values.yaml |
| Gatekeeper Live | done | **4 ConstraintTemplates + 4 Constraints** configured (require-safety-eval, require-monitoring, require-cybersecurity-operations, require-evidence), enforcementAction: deny; first 3 ADMIT/REJECT verified on AKS Sweden Central, G-OPS-04 verified locally via Gatekeeper fixture path |
| Closed-Loop Pipeline | done | gate_orchestrator.py: 3 scenarios (PASS/FAIL/Gatekeeper), tamper detection |
| Drift Detection | done | drift_detector.py (PSI+JSD), CronJob + Prometheus/Grafana/AlertManager |
| GitHub Actions Pipeline | done | gate-pipeline.yml (16 CI gates + Evidence + Hash-Chain + Docker Push), test_pipeline_local.sh |
| Master Integration Test | done | tests/test_all.py: 31/31 PASS across all 5 pillars |
| Integrity Regression Suite | done | tests/test_integrity_regression.py: credibility checks for fallbacks, evidence strictness, HYBRID consistency, walkthrough drift |
| Azure CLI/Helm (Azure) | done | AKS Sweden Central live 2026-04-13 (kube-prometheus-stack via Helm, OPA Gatekeeper mit 3 live verifizierten + 1 lokal ergaenzten ConstraintTemplate, PostgreSQL + Hash-Chain-Triggern im Cluster-Pod) |

## Integrity Regression Suite

The repository includes a dedicated integrity-focused regression suite in addition to the functional master test.

```bash
python3 tests/test_integrity_regression.py
python3 tests/test_integrity_regression.py --format json
python3 tests/test_integrity_regression.py --fail-on low
```

This suite is intended to catch PoC-credibility risks such as:

- demo fallbacks that can mask missing enforcement
- non-critical treatment of Evidence Store or hash-chain failures
- HYBRID gate inconsistencies across scripts and scenarios
- walkthrough/documentation drift against current repo files

## Academic Foundation

This implementation is the technical instantiation of a Design Science Research (DSR) artifact developed as part of a master's thesis:

> **Demir, M. (2026).** *Cloud-native Referenzarchitektur für GenAIOps mit Quality-Gate-Kontrollsystem zur lifecycle-integrierten Operationalisierung regulatorischer, technischer und strategischer Anforderungen.* M.Sc. Thesis, SRH Fernhochschule. [Thesis Repository →](https://github.com/MustDemir/Masterarbeit-GenAIOps-Referenzarchitektur)

The thesis provides the full academic rationale including: DSR methodology (Hevner/Peffers/vom Brocke), requirements derivation from EU AI Act, convergence analysis with NIST AI RMF, and expert evaluation.

**Citation (archived Zenodo release — the state cited in the thesis):**

```bibtex
@software{demir2026genaiopscompliancegates,
  author       = {Demir, Mustafa},
  title        = {GenAIOps Compliance Gates: A Cloud-native Reference Architecture for EU AI Act Operationalization},
  version      = {v1.1.0},
  date         = {2026-04-30},
  doi          = {10.5281/zenodo.19920310},
  url          = {https://doi.org/10.5281/zenodo.19920310},
  license      = {CC-BY-NC-4.0}
}
```

> The `license` field above is deliberately **not** `Apache-2.0`: it describes the archived artefact, which was published under CC BY-NC 4.0 and stays available under those terms. The current repository is Apache 2.0 — see [License](#license).

## License

Licensed under the [Apache License 2.0](LICENSE) — use, modification and distribution are permitted, including commercially, subject to attribution and the patent-grant terms of the licence. See [NOTICE](NOTICE).

**Licence change, 15 August 2026.** This repository was previously published under CC BY-NC 4.0. The non-commercial clause makes that licence non-open-source under the OSI definition — and a compliance control system that may not be used commercially misses the setting it exists for. The change is **not retroactive**: the release archived under Zenodo DOI [10.5281/zenodo.19920310](https://doi.org/10.5281/zenodo.19920310) and the tag `thesis-v1.0` remain available under their original CC BY-NC 4.0 terms, and that earlier grant is not withdrawn. The previous licence text is kept as `LICENSE_CC-BY-NC-4.0_until_2026-08-15.txt`.

## Author

**Mustafa Demir** — AI & Cloud Solution Architect

[![Website](https://img.shields.io/badge/Website-mustafa--demir.com-4285F4?style=flat&logo=googlechrome&logoColor=white)](https://mustafa-demir.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mustafa%20Demir-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/mustafa-demir-331900202/)
[![GitHub](https://img.shields.io/badge/GitHub-MustDemir-181717?style=flat&logo=github)](https://github.com/MustDemir)
