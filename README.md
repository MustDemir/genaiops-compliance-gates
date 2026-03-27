# GenAIOps Compliance Gates — EU AI Act Compliant Quality Gate System

A cloud-native reference architecture for operationalizing regulatory, technical, and strategic requirements in GenAI systems through automated Quality Gates — with full EU AI Act (Regulation 2024/1689) compliance built into CI/CD/CT pipelines.

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

## What This Is

Enterprise GenAI systems face a triple challenge: they must be **technically robust**, **strategically governed**, and **regulatorily compliant** — simultaneously and continuously. This reference architecture solves that by embedding 16 automated Quality Gates across the entire GenAI lifecycle, enforced through Policy-as-Code.

**Key idea:** Compliance is not a document you write after deployment. It's a property the system enforces at every pipeline stage.

### Core Capabilities

- **16 Quality Gates** across 3 lifecycle phases (Pre-Deployment, Deployment, Operations)
- **Policy-as-Code** via OPA/Rego with three enforcement pillars (Conftest, Gatekeeper, Decision Logs)
- **Immutable Evidence Store** with SHA-256 hash-chain for audit-proof traceability
- **Full EU AI Act mapping**: Art. 9–15 → Requirements → Gates → Policies → Evidence
- **Automated gate decisions** using the CDV Framework (Contract → Validation → Severity → Pipeline-Decision)
- **Post-Market Surveillance** with drift detection and incident reporting (Art. 72, Art. 26.5)

## Architecture Overview

### Five-Pillar Model

| Pillar | Component | Purpose |
|--------|-----------|---------|
| **S1** | Design Principles (DP1–DP5) | Architectural foundation and cloud-native integrability |
| **S2** | Quality Gate Control System | 16 lifecycle-integrated gates with 7-attribute template |
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

The architecture achieves a **9:5:0 distribution** — 9 fully automated gates (64.3%), 5 hybrid gates (35.7%), 0 manual-only gates. A dedicated **D3×D2 Override Rule** ensures that gates requiring human oversight (Art. 14) are capped at HYBRID automation, regardless of technical feasibility.

```
Gate Inclusion Rule: D1 (Gate-Eignung) → D3 (Regulatory) → D2 (Technical) → Classification
                     ↓
                     D3=FIRST-DEGREE → D2 max HYBRID (Automation Ceiling)
```

### Enforcement Flow

![GenAIOps Quality Gate Enforcement Flow](docs/images/enforcement-flow.svg)

## Repository Structure

```
genaiops-compliance-gates/
├── README.md
├── docs/
│   ├── architecture/           # Architecture diagrams (Five-Pillar, Gate Flow, Pipeline)
│   └── walkthrough/            # PoC walkthrough documentation with screenshots
├── gate-definitions/           # Quality Gate specifications (YAML)
│   ├── gate_template.yaml      # 7-attribute gate template
│   ├── pre-deployment/         # G-PRE-01 to G-PRE-05
│   ├── deployment/             # G-DEP-01 to G-DEP-06
│   └── operations/             # G-OPS-01 to G-OPS-05
├── policies/                   # OPA/Rego policy implementations
│   ├── pre-deployment/         # Conftest policies (CI stage)
│   ├── deployment/             # Conftest + Gatekeeper policies
│   └── operations/             # Gatekeeper admission policies
├── pipeline/
│   └── .github/workflows/      # GitHub Actions with gate-integrated stages
├── evidence-store/
│   ├── schema/                 # PostgreSQL DDL (v01 basic, v02 enterprise)
│   └── migrations/             # Schema migration scripts
├── monitoring/                 # Drift detection, PMS, sidecar configuration
├── infrastructure/
│   ├── terraform/              # Azure AKS, PostgreSQL, Blob Storage provisioning
│   └── helm/                   # Kubernetes deployments (OPA Gatekeeper, app, monitoring)
├── scenarios/
│   └── healthcare-ambient-ai-scribe/  # PoC scenario: High-risk AI (Annex III)
└── requirements/               # R001–R014 requirement specifications (from EU AI Act)
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
| **IaC** | Terraform, Helm | Infrastructure provisioning + app deployment |
| **GenAI Runtime** | Azure OpenAI Service, LangChain | LLM inference, RAG pipeline |

## Quality Gate Framework

Each of the 16 gates follows a standardized 7-attribute template:

```yaml
gate_id: G-PRE-01
name: Risk Classification & Impact Assessment
trigger: Model registration or risk-level change
governance_dimension: regulatory
check_criteria:
  - EU AI Act risk classification completed
  - Risk mitigation measures documented
evidence_artifacts:
  - risk_classification_report
  - impact_assessment_document
decision_logic: CDV (Contract → Validation → Severity → Pipeline-Decision)
responsibility: AI Governance Lead + Risk Officer
audit_trail: Immutable evidence record with SHA-256 hash
waiver_policy: Requires C-level approval with time-bound remediation plan
```

### Gate Distribution

| Phase | Gates | Automation |
|-------|-------|-----------|
| **Pre-Deployment** | G-PRE-01 to G-PRE-05 | 1 AUTO, 4 HYBRID |
| **Deployment** | G-DEP-01 to G-DEP-06 | 5 AUTO, 1 HYBRID |
| **Operations** | G-OPS-01 to G-OPS-05 | 3 AUTO, 0 HYBRID (excl. G-OPS-05 = Compliance) |

## PoC Scenario: Healthcare Ambient AI Scribe

The architecture is demonstrated using a **high-risk AI system** (EU AI Act Annex III): an Ambient AI Scribe that transcribes and summarizes medical consultations.

**Why this scenario:**
- High-risk classification → maximum regulatory requirements
- Sensitive health data → GDPR Art. 9 + AI Act convergence
- Stochastic outputs → quality assurance for generative content
- Full lifecycle coverage → all 16 gates exercised

## Traceability Chain

Every regulatory requirement is traceable from norm to evidence:

```
EU AI Act Article → Requirement (R-xx) → Design Principle (DP) → Quality Gate (G-xx) → Policy (Rego) → Evidence (Audit Trail)
```

This six-level traceability chain ensures that for any audit finding, the path back to the originating regulation is documented and verifiable.

## Getting Started

> ⚠️ **Work in Progress** — The architecture is being implemented incrementally. See the build status below.

### Prerequisites

- Azure subscription with AKS enabled
- Terraform >= 1.5
- Helm >= 3.12
- OPA/Conftest CLI
- kubectl configured for AKS cluster

### Quick Start

```bash
# 1. Provision infrastructure
cd infrastructure/terraform
terraform init && terraform apply

# 2. Deploy OPA Gatekeeper
cd ../helm
helm install gatekeeper gatekeeper/gatekeeper --namespace gatekeeper-system

# 3. Apply policies
cd ../../policies
conftest test --policy pre-deployment/ scenarios/healthcare-ambient-ai-scribe/

# 4. Initialize Evidence Store
cd ../evidence-store
psql -f schema/evidence_store_schema_v02_enterprise.sql

# 5. Run pipeline with gates
# (see pipeline/.github/workflows/ for CI/CD integration)
```

## Implementierungsfortschritt

> Strategie: Lokal-first (Phase 1–11 kostenlos auf Minikube), Azure erst Phase 12. Geschaetzter Aufwand: ~30–42h ueber 4–6 Wochen.

<!-- PROGRESS-START -->
> Gesamtfortschritt: `██████████░░░░░░░░░░` **50%** (6/12 Phasen)

| Phase | Beschreibung | Fortschritt | Status |
|-------|-------------|------------|--------|
| **1** | App entwickeln (FastAPI + Mock-Endpoint) | `████████████████████` 100% | done |
| **2** | Containerisieren (Dockerfile, Multi-Stage, Non-Root) | `████████████████████` 100% | done |
| **3** | Docker Compose (App + DB + Prometheus + Grafana) | `████████████████████` 100% | done |
| **4** | K8s-Manifeste (Deployment, Service, ConfigMap, Sidecar) | `████████████████████` 100% | done |
| **5** | Rego-Policies + Conftest-Tests (6 Gates) | `████████████████████` 100% | done |
| **6** | Lokaler Cluster (Minikube) + Helm-Basics | `░░░░░░░░░░░░░░░░░░░░` 0% | planned |
| **7** | Gatekeeper + ConstraintTemplates + OPS-Policies | `░░░░░░░░░░░░░░░░░░░░` 0% | planned |
| **8** | Evidence Store (PostgreSQL Schema + Scripts) | `████████████████████` 100% | done |
| **9** | Monitoring-Sidecar (PSI + Jensen-Shannon + Prometheus) | `░░░░░░░░░░░░░░░░░░░░` 0% | planned |
| **10** | ArgoCD + GitHub Actions Pipeline | `░░░░░░░░░░░░░░░░░░░░` 0% | planned |
| **11** | Green/Red Path Walkthrough + Screenshots (Kap. 6.3) | `░░░░░░░░░░░░░░░░░░░░` 0% | planned |
| **12** | Azure AKS Migration (Terraform + ACR + PostgreSQL) | `░░░░░░░░░░░░░░░░░░░░` 0% | planned |
<!-- PROGRESS-END -->

### Artefakt-Status

| Komponente | Status | Details |
|-----------|--------|--------|
| Requirements (R001–R014) | done | 14 YAML-Specs, EU AI Act Art. 9–15 Mapping |
| Evidence Store Schema | done | v01 (basic) + v02 (enterprise) + v03 (decision_method, E13) |
| Evidence Store Scripts | done | record_evidence.py + verify_hash_chain.py, SQLite + PostgreSQL, Hash-Chain verified |
| Decision-Log-Fixtures | done | G-PRE-01 (manual_review) + G-PRE-05 (governance_approval), HYBRID-Demo ready |
| Gate Template | done | 7-Attribut-Template, 3 Beispiel-Gates |
| Policy-Kandidaten | done | 29 Kandidaten dokumentiert (22 Conftest, 4 Gatekeeper, 3 Decision Logs) |
| Healthcare Scribe App | done | FastAPI Mock-Endpoint, /transcribe, /health, /metrics |
| Gate-Fixtures | done | app_documentation.json, eval_results.json |
| K8s-Manifeste | done | 8 YAMLs: Namespace, Deployment, Service, ConfigMap, PostgreSQL, Prometheus |
| OPA/Rego-Code | done | 6 Policies (3 Conftest PRE + 1 Conftest DEP + 2 Gatekeeper OPS), 71 Regeln, 13 Fixtures |
| Integration Tests | done | 8 Tests (HYBRID E2E, Tamper Detection, Chain Linkage, Non-Blocking Semantics) |
| Tamper-Detection Spec | done | Dokumentiert: 8 erkannte Angriffsvektoren, 6 bekannte Limitationen, 3 Protection Layers |
| Walkthrough-Dokumentation | done | 13-Schritte Walkthrough für Kap. 6.3 (Pre-Dep → Dep → Ops → HYBRID → Tamper) |
| Schema-Evolution-Dok | done | v01→v02→v03 Changelog mit Rationale und Hash-Trigger-Details |
| Terraform/Helm | planned | 0% — Phase 6/12 |
| GitHub Actions Pipeline | planned | 0% — Phase 10 |

## Academic Foundation

This implementation is the technical instantiation of a Design Science Research (DSR) artifact developed as part of a master's thesis:

> **Demir, M. (2026).** *Cloud-native Referenzarchitektur für GenAIOps mit Quality-Gate-Kontrollsystem zur lifecycle-integrierten Operationalisierung normativer Anforderungen — auf Basis des EU AI Act.* M.Sc. Thesis, SRH Fernhochschule. [Thesis Repository →](https://github.com/MustDemir/Masterarbeit-GenAIOps-Referenzarchitektur)

The thesis provides the full academic rationale including: DSR methodology (Hevner/Peffers), requirements derivation from EU AI Act, convergence analysis with NIST AI RMF, and expert evaluation.

## License

This work is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). You may share and adapt for non-commercial purposes with attribution.

## Author

**Mustafa Demir** — AI & Cloud Solution Architect

[![Website](https://img.shields.io/badge/Website-mustafa--demir.com-4285F4?style=flat&logo=googlechrome&logoColor=white)](https://mustafa-demir.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Mustafa%20Demir-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/mustafa-demir-331900202/)
[![GitHub](https://img.shields.io/badge/GitHub-MustDemir-181717?style=flat&logo=github)](https://github.com/MustDemir)
