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

### Four-Pillar Model

| Pillar | Component | Purpose |
|--------|-----------|---------|
| **S1** | Quality Gate Control System | 16 lifecycle-integrated gates with 7-attribute template |
| **S2** | Policy Engine | OPA/Rego policies, Conftest (CI), Gatekeeper (K8s admission), Decision Logs |
| **S3** | Evidence Store | PostgreSQL + Blob Storage, hash-chain integrity, RBAC, schema separation |
| **S4** | Monitoring & PMS | Drift detection (PSI/Jensen-Shannon), incident reporting, sidecar pattern |

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

## Repository Structure

```
genaiops-reference-architecture/
├── README.md
├── docs/
│   ├── architecture/           # Architecture diagrams (Four-Pillar, Gate Flow, Pipeline)
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

## Build Status

| Component | Status | Notes |
|-----------|--------|-------|
| Requirements (R001–R014) | ✅ Complete | Derived from EU AI Act Art. 9–15 |
| Gate Definitions (YAML) | 🔨 In Progress | 3/16 gates specified, template ready |
| OPA/Rego Policies | 📋 Planned | 29 policy candidates identified |
| Evidence Store Schema | ✅ Complete | v01 (basic) + v02 (enterprise with RLS) |
| GitHub Actions Pipeline | 📋 Planned | Gate-integrated stages |
| Terraform (Azure) | 📋 Planned | AKS, PostgreSQL, Blob Storage |
| Helm Charts | 📋 Planned | Gatekeeper, app, monitoring |
| Monitoring / PMS | 📋 Planned | Prometheus, drift detection |
| PoC Walkthrough | 📋 Planned | Healthcare scenario end-to-end |

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
