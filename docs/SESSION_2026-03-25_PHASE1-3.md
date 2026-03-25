# Session 2026-03-25 — Phase 1–3 Implementierung

## Ueberblick

Erste Implementierungssession des PoC. Phasen 1–3 des 12-Phasen-Plans abgeschlossen.
Alle Tools fuer macOS M5 (ARM64) installiert und verifiziert.

---

## 1. Toolchain Setup

### Homebrew ARM64 Migration

Altes Homebrew lief unter Rosetta (x86, `/usr/local`). Natives ARM64 Homebrew unter `/opt/homebrew` installiert.

### Installierte Tools (alle ARM64 nativ)

| Tool | Version | Zweck |
|------|---------|-------|
| Docker Desktop | v29.3.0 | Container Runtime (war schon vorhanden) |
| Minikube | v1.38.1 | Lokaler Kubernetes-Cluster (Phase 6) |
| kubectl | v1.35.3 | Kubernetes CLI |
| Helm | v4.1.3 | K8s Package Manager (Phase 6-7) |
| Conftest | v0.67.1 | Rego-Policy-Tests gegen YAML (Phase 5) |
| Terraform | v1.5.7 | Infrastructure-as-Code (Phase 12) |
| ArgoCD CLI | v3.3.4 | GitOps Deployment (Phase 10) |
| OPA | v1.14.1 | Policy Engine (Phase 5) |
| Azure CLI | v2.83.0 | Azure-Verwaltung (war schon vorhanden) |
| Python | v3.14.2 | App + Scripts (war schon vorhanden) |
| GitHub CLI | v2.85.0 | Repo-Verwaltung (war schon vorhanden) |

---

## 2. Phase 1 — Healthcare Scribe App (FastAPI)

### Entscheidung: Option B (Mock-Endpoint)

Azure OpenAI ist nicht kostenlos im Studentenabo. App gibt feste Demo-Antworten zurueck.
Forschungsbeitrag = Gates, nicht das LLM. Mock reicht fuer Phase 1–11, fuer den finalen
Walkthrough (Phase 12) optional 5 USD Azure OpenAI Credits nachladen.

### Erstellte Dateien

| Datei | Zweck |
|-------|-------|
| `scenarios/healthcare-ambient-ai-scribe/app/main.py` | FastAPI mit 3 Endpoints |
| `scenarios/healthcare-ambient-ai-scribe/app/requirements.txt` | 3 Dependencies |
| `scenarios/healthcare-ambient-ai-scribe/fixtures/app_documentation.json` | Gate-Input fuer G-PRE-01, G-PRE-05, G-OPS-03, G-OPS-05 |
| `scenarios/healthcare-ambient-ai-scribe/fixtures/eval_results.json` | Gate-Input fuer G-DEP-02 |

### Endpoints

| Endpoint | Methode | Zweck | Gate-Bezug |
|----------|---------|-------|------------|
| `/transcribe` | POST | Mock-Transkription (Healthcare) | Hauptfunktion der App |
| `/health` | GET | Kubernetes Liveness/Readiness Probe | K8s Deployment |
| `/metrics` | GET | Prometheus-Metriken | G-OPS-03, Saeule S5 |

### Prometheus-Metriken (in /metrics)

| Metrik | Typ | Zweck |
|--------|-----|-------|
| `scribe_requests_total` | Counter | Anfragevolumen |
| `scribe_latency_seconds` | Histogram | Antwortzeiten (p50, p95, p99) |
| `scribe_mock_mode` | Gauge | 1 = Mock, 0 = Live |

### Traceability (DP2)

Jede Antwort enthaelt `model_version`, `run_id`, `pipeline_id` — damit die
Evidence-Kette vom Gate-Ergebnis zurueck zum exakten Inference-Lauf nachvollziehbar ist.

### Test

App lokal gestartet (`uvicorn`), alle 3 Endpoints erfolgreich getestet.

---

## 3. Phase 2 — Dockerfile (G-PRE-04 Compliant)

### Erstellte Dateien

| Datei | Zweck |
|-------|-------|
| `scenarios/healthcare-ambient-ai-scribe/Dockerfile` | Multi-Stage Build, Non-Root |
| `scenarios/healthcare-ambient-ai-scribe/.dockerignore` | Security: kein .env, .git im Image |

### G-PRE-04 Compliance (6 Pruefpunkte)

| Check | Anforderung | Wie erfuellt | Status |
|-------|------------|-------------|--------|
| P1 | runAsNonRoot | `USER appuser` im Dockerfile | PASS |
| P2 | Resource Limits | Wird in K8s-Manifest gesetzt (Phase 4) | — |
| P3 | Read-Only FS | Wird in K8s-Manifest gesetzt (Phase 4) | — |
| P4 | Keine Secrets im Image | `.dockerignore` schliesst `.env` aus, kein ENV mit Keys | PASS |
| P5 | Slim Base-Image | `python:3.11-slim` (~243MB gesamt) | PASS |
| P6 | No Privilege Escalation | Wird in K8s-Manifest gesetzt (Phase 4) | — |

### Dockerfile-Architektur

```
Stage 1 (builder):              Stage 2 (runtime):
  python:3.11-slim                python:3.11-slim
  + pip install                   + site-packages (kopiert)
  + requirements.txt              + uvicorn (kopiert)
  = WEGGEWORFEN                   + app code (als appuser)
                                  + USER appuser
                                  = FINALES IMAGE (243MB)
```

### Red Path Vorbereitung (Phase 11)

`USER appuser` entfernen → Conftest erkennt fehlendes `runAsNonRoot` → G-PRE-04 DENY.

### Test

`docker build` + `docker run` erfolgreich. `whoami` = `appuser`. Alle Endpoints funktionieren.

---

## 4. Phase 3 — Docker Compose (4 Services)

### Erstellte Dateien

| Datei | Zweck |
|-------|-------|
| `scenarios/healthcare-ambient-ai-scribe/docker-compose.yml` | 4 Services orchestriert |
| `scenarios/healthcare-ambient-ai-scribe/monitoring/prometheus.yml` | Scrape-Config |

### Services

| Service | Image | Port | Saeule | Status |
|---------|-------|------|--------|--------|
| **scribe** | Eigenes Dockerfile | 8080 | — | Laeuft, getestet |
| **postgres** | postgres:16-alpine | 5432 | S4 (Evidence Store) | Laeuft, leer (Schema Phase 8) |
| **prometheus** | prom/prometheus:v3.3.0 | 9090 | S5 (Monitoring) | Laeuft, scrapt App |
| **grafana** | grafana/grafana:11.6.0 | 3000 | S5 (Visualisierung) | Laeuft, Dashboard erstellt |

### Grafana Dashboard

Dashboard "GenAIOps — Ambient AI Scribe" per API erstellt mit 5 Panels:

| Panel | Query | Gate-Bezug |
|-------|-------|------------|
| Requests Total | `scribe_requests_total` | G-OPS-03 |
| Mock Mode | `scribe_mock_mode` | Walkthrough-Indikator |
| Request Rate | `rate(scribe_requests_total[1m])` | G-OPS-03 Performance |
| Latency p95 | `histogram_quantile(0.95, ...)` | G-DEP-02 (SLO ≤ 2000ms) |
| Latency Histogram | p50/p95/p99 | Kap. 6.3 Screenshots |

### Kommunikation zwischen Services

```
scribe ────────→ postgres     (Evidence Store, ab Phase 8)
       ←──────── prometheus   (scrapt /metrics alle 15s)
                 prometheus ←── grafana (liest Metriken, zeigt Dashboard)
```

### Test

Alle 4 Container gestartet (`docker-compose up -d`). Prometheus scrapt App erfolgreich
(`Health: up`). Grafana Dashboard zeigt Metriken nach 20 Test-Requests. PostgreSQL
laeuft (v16.13, leere DB).

---

## 5. Zusammenfassung: Wie haengt alles zusammen?

### Der Monitoring-Flow (Saeule S5)

```
App exponiert Metriken (/metrics)
       ↓
Prometheus sammelt sie (alle 15s)
       ↓
Gate G-OPS-03 prueft: "Ist Latency p95 ≤ 2000ms? Ist Drift PSI < 0.2?"
       ↓
Ergebnis → Evidence Store (PASS/FAIL mit Hash-Chain)
       ↓
Grafana zeigt alles visuell
```

### Automatisch vs. Manuell

| Was | Wer |
|-----|-----|
| Code schreiben + pushen | DU (manuell) |
| Conftest-Policies pruefen | Maschine (automatisch bei Push) |
| ArgoCD Sync klicken | DU (strategische Freigabe, G-PRE-05) |
| Gatekeeper-Check | Maschine (automatisch bei Deployment) |
| Prometheus scrapt Metriken | Maschine (alle 15 Sekunden) |
| Evidence Store speichert | Maschine (bei jedem Gate-Ergebnis) |
| Grafana Dashboard anschauen | DU (bei Bedarf) |
| Bei Alarm reagieren | DU (Human Oversight, Art. 14) |

---

## 6. Konzept-Erklaerungen (Verstaendnis)

### Was ist ein Container?

| Begriff | Was | Analogie |
|---------|-----|----------|
| **Dockerfile** | Rezept (Bauanleitung) | Kochrezept |
| **Image** | Fertiges Paket (eingefroren, unveraenderlich) | Tiefkuehlpizza |
| **Container** | Laufende Instanz eines Images | Pizza im Ofen |

Ein Image kann beliebig oft gestartet werden — jeder Start erzeugt einen neuen Container.
`docker build` erstellt das Image, `docker run` startet den Container.

### CLI-Tools vs. Desktop-Apps

Alle installierten Tools (minikube, helm, conftest, terraform, argocd, opa, kubectl) sind
**CLI-Tools** — sie laufen nur im Terminal per Befehl. Keine Desktop-Apps mit Fenster.
Einzige Ausnahme: **Docker Desktop** (hat eine GUI + CLI).

### Prometheus vs. Grafana

| | Prometheus | Grafana |
|--|-----------|---------|
| **Was es tut** | Sammelt & speichert Metriken | Visualisiert sie als Dashboard |
| **Analogie** | Fitnesstracker-Sensor am Handgelenk | App auf dem Handy die Kurven zeigt |
| **Braucht Input von** | Der App (/metrics Endpoint) | Prometheus (als Datenquelle) |
| **Im Kolloquium zeigen** | Eher nicht (technisch/roh) | Ja (Dashboard-Screenshots fuer Kap. 6.3) |

```
Deine App ──(alle 15s)──→ Prometheus ──(auf Anfrage)──→ Grafana
  "Ich hatte 20 Requests,     speichert das              zeigt es als
   Latency war 0.5ms"         mit Zeitstempel             huebschen Graph
```

### Was ist die App eigentlich?

Die App ist ein **Backend-Service** (API), keine Desktop-App mit Benutzeroberflaeche.
Sie antwortet auf HTTP-Requests — im echten Einsatz wuerde ein Frontend (z.B. eine
Arzt-App) diesen Service aufrufen. Fuer den PoC reicht `curl` oder der Browser.

Fuer die Thesis ist das genau richtig: Die Gates pruefen den **Service und seine
Konfiguration**, nicht eine Benutzeroberflaeche.

### Warum diese 4 Services zusammen?

```
DU sendest Request
       ↓
   [scribe]         ← Deine Healthcare App (das regulierte KI-System)
       ↓
   [postgres]       ← Evidence Store: speichert Gate-Ergebnisse (ab Phase 8)
       ↑
   [prometheus]     ← Monitoring: sammelt App-Metriken alle 15 Sekunden
       ↑
   [grafana]        ← Dashboard: zeigt dir visuell ob alles OK ist
```

Ohne Prometheus haetten die Gates **nichts zu pruefen**. Prometheus liefert die **Daten**,
die Gates treffen die **Entscheidung**, der Evidence Store **beweist** es.

### Der komplette Enforcement-Flow (Endversion, Phase 10-11)

```
DU (Entwickler/Deployer)
 │
 │  1. Schreibst Code, pushst zu Git
 ▼
GitHub Actions (CI/CD Pipeline)
 │  2. Conftest prueft YAML/Dockerfile gegen Rego-Policies
 │     → PASS oder DENY (G-PRE-01, G-PRE-04, G-DEP-02)
 ▼
ArgoCD (GitOps)
 │  3. Erkennt neues Manifest
 │  4. DU klickst "Sync" (G-PRE-05 — strategische Freigabe)
 ▼
Kubernetes (Cluster)
 │  5. Gatekeeper prueft automatisch (G-OPS-03, G-OPS-05)
 │     → PASS → Pod startet
 │     → REJECT → Pod startet NICHT
 ▼
App laeuft als Pod
 │  6. Prometheus scrapt /metrics (automatisch, alle 15s)
 │  7. Evidence Store speichert Gate-Ergebnisse (automatisch)
 ▼
Grafana Dashboard
 │  8. DU schaust rein: Latency OK? Drift?
 │  9. Bei Alarm → DU entscheidest (Human Oversight, Art. 14)
```

### Warum Mock-Endpoint statt echtes LLM?

Azure OpenAI kostet Geld pro Token und ist nicht im Studentenabo enthalten.
Der Forschungsbeitrag der Thesis sind die **Quality Gates**, nicht das LLM.
Ein Mock-Endpoint reicht um zu demonstrieren, dass die Gate-Systematik funktioniert.
Fuer den finalen Walkthrough auf Azure (Phase 12) koennen optional 5 USD Credits
geladen werden.

---

## 7. Git Commits

| Hash | Message |
|------|---------|
| `ea929b8` | feat: Phase 1 — Healthcare Scribe App + Gate-Fixtures |
| `3bd50cf` | chore: Implementierungsfortschritt (12-Phasen-Tracker) in README |
| `58cc1a1` | feat: Phase 2 — G-PRE-04 compliant Dockerfile + .dockerignore |
| `9ca5c71` | chore: Phase 2 als done im Fortschritts-Tracker markiert |
| `8bfbd81` | feat: Phase 3 — Docker Compose (4 Services) |
| `8734eb7` | chore: Phase 3 als done im Fortschritts-Tracker markiert |

---

## 7. Naechste Schritte

| Phase | Was | Status |
|-------|-----|--------|
| **4** | K8s-Manifeste (Deployment, Service, ConfigMap, Sidecar-Stub) | Naechste Session |
| **5** | Rego-Policies + Conftest-Tests (6 Gates) | — |
| **6** | Lokaler Cluster (Minikube) + Helm | — |
| **7** | Gatekeeper + ConstraintTemplates | — |

---

## 8. Befehle zum Starten/Stoppen

```bash
# Zum Scenario-Ordner wechseln
cd /Users/mustafademir/Projects/genaiops-compliance-gates/scenarios/healthcare-ambient-ai-scribe

# Alle 4 Services starten
docker-compose up -d

# Status pruefen
docker ps

# Endpoints
# App:        http://localhost:8080/health
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/admin)

# Stoppen
docker-compose down
```
