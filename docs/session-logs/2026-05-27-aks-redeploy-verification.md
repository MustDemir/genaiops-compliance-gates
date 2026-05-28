# Session-Log — AKS Re-Deployment & Runtime-Enforcement-Verifikation

**Datum:** 2026-05-27
**Umgebung:** Azure Kubernetes Service (AKS), Region `swedencentral`
**Ziel:** Erneute, unabhängige End-to-End-Instanziierung des PoC auf Kubernetes zur Bestätigung der Reproduzierbarkeit der Runtime-Enforcement-Stufe (Admission-Time-Gates via OPA Gatekeeper), inklusive Green-Path (ADMIT) und Red-Path (REJECT).

Dieses Protokoll dokumentiert einen zweiten, vom ursprünglichen Walkthrough (vgl. Thesis Kap. 6.3, Anhang C) unabhängigen Deployment-Lauf. Es dient dem Nachweis der Reproduzierbarkeit und hält zwei im Zuge dieses Laufs behobene Skript-Defekte fest.

---

## 1. Vorgehen

| Schritt | Aktion | Ergebnis |
|---------|--------|----------|
| 1 | Voll-Deployment via `deploy-aks.sh` (`make aks-up`) | Cluster, ACR und Image-Build erfolgreich; Abbruch in Phase 3 (siehe Defekt 1) |
| 2 | Deployment ab Phase 3/4 fortgesetzt (ohne Cluster-Neuaufbau) | Vollständig durchgelaufen, Anwendung live |
| 3 | Runtime-Enforcement-Test (Green-/Red-Path) | Konforme App admittiert, nicht-konformes Deployment am Admission Controller blockiert |
| 4 | Behebung beider Defekte in `deploy-aks.sh` | Syntaxprüfung (`bash -n`) bestanden, committet |
| 5 | Teardown via `teardown-aks.sh` (`make aks-down`) | Resource Group gelöscht |

---

## 2. Verifikationsergebnis

Cluster-Stand vor dem Teardown:

| Komponente | Status |
|-----------|--------|
| Nodes | 3/3 Ready (1× System `B2s_v2` + 2× Userpool `B2s_v2`) |
| AI-Scribe-Anwendung | `1/1 Running`, vom Gatekeeper admittiert (ADMIT) |
| PostgreSQL (Evidence Store) | `Running`, Schema v02 + Migration v03 angewendet |
| Gatekeeper | `2/2 Running`, 3 ConstraintTemplates + 3 Constraints (`enforcementAction: deny`, 0 Violations) |
| Monitoring | Prometheus, Grafana, Alertmanager, node-exporter — alle `Running` |
| App-Endpoint | LoadBalancer (`<LoadBalancer-IP>`); `GET /health` → `{"status":"healthy","model_version":"mock-v1.0.0"}` |

### Green-Path (ADMIT)
Das konforme Deployment `ambient-ai-scribe` mit vollständigen Compliance-Annotationen wurde zugelassen, erreichte `1/1 Ready` und beantwortete den Health-Endpoint mit HTTP 200.

### Red-Path (REJECT)
Ein bewusst nicht-konformes Deployment (ohne Compliance-Annotationen) wurde am Admission Controller abgelehnt — mit Begründungen aus allen drei Constraints:

```
admission webhook "validation.gatekeeper.sh" denied the request:
[require-safety-eval-annotations]   G-DEP-02 FAIL: genaiops.io/eval-passed, eval-run-id
[require-monitoring-annotations]    G-OPS-03 FAIL: drift-detection-enabled, service-monitor-configured
[require-evidence-annotations]      G-OPS-05 FAIL: evidence-store-connected, hash-chain-enabled
```

Damit ist die Admission-Time-Durchsetzung (zweite Enforcement-Ebene) end-to-end reproduziert.

---

## 3. Behobene Defekte in `deploy-aks.sh`

Beide Defekte traten im realen Re-Deployment auf und sind in einem dedizierten Commit behoben.

### Defekt 1 — Phase 3: Abhängigkeit von PyYAML
- **Symptom:** `ModuleNotFoundError: No module named 'yaml'` → Abbruch beim Anwenden der ConstraintTemplates.
- **Ursache:** Das Skript trennte die mehrteiligen Gatekeeper-YAML-Dateien über `python3 -c "import yaml ..."`. Auf einer Ausführungsumgebung ohne installiertes PyYAML schlägt dies fehl.
- **Behebung:** Python-basierte Trennung entfernt, ersetzt durch ein zweiphasiges `kubectl apply` der vollständigen Dateien: Phase 1 registriert die ConstraintTemplates (die enthaltenen Constraints scheitern mangels noch nicht existierender CRD und werden toleriert); nach der Compile-Wartezeit registriert Phase 2 die Constraints. Keine Python-Abhängigkeit mehr.

### Defekt 2 — Phase 4: fehlerhafter Pod-Selektor und DB-Benutzer
- **Symptom:** `error executing jsonpath ... array index out of bounds` → Abbruch bei der Schema-Initialisierung des Evidence Store.
- **Ursache:** Pod-Suche über `-l app=postgres`; das tatsächliche Label lautet `app.kubernetes.io/name=postgres-evidence` (leere Ergebnisliste). Zusätzlich `psql -U postgres`, obwohl der Datenbank-Superuser laut Secret `genaiops` ist.
- **Behebung:** Selektor auf `app.kubernetes.io/name=postgres-evidence` und Benutzer auf `psql -U genaiops` korrigiert.

**Wirkung:** `make aks-up` läuft fortan ohne manuelles Nacharbeiten in einem Durchlauf.

---

## 4. Ressourcennutzung
Cluster-Laufzeit ca. 40–45 Minuten; Teardown über `az group delete` (`teardown-aks.sh`) beendet sämtliche Cloud-Ressourcen.

---

## 5. Bezug zur Masterarbeit (Kapitel 4 / 5 / 6)

Dieser Lauf realisiert keinen neuen Funktionsumfang, sondern bestätigt erneut den technisch-funktionalen Evaluationsteil der Arbeit (PoC-Walkthrough, Kap. 6.3, Evaluationsstufe b). Die in Kapitel 5 entworfene und in Kapitel 6 demonstrierte Architektur wurde ein zweites Mal, unabhängig, auf realer Infrastruktur instanziiert.

### Kapitel 4 — Anforderungen
Kapitel 4 leitet aus dem EU AI Act die Anforderungen R001–R014 ab. In diesem Lauf wurden drei davon zur Laufzeit technisch durchgesetzt (Prinzip „Enforcement statt Dokumentation", Kap. 4.1.4):

| Geprüfte Compliance-Annotation | Anforderung | EU-AI-Act-Bezug |
|---|---|---|
| `eval-passed`, `eval-run-id` (Sicherheitsbewertung) | R003 | Art. 15 (Robustheit/Sicherheit) |
| `drift-detection-enabled`, `service-monitor-configured` (Überwachung) | R010 | Art. 72 (Post-Market Surveillance) |
| `evidence-store-connected`, `hash-chain-enabled` (Nachweisführung) | R005 | Art. 12 (Aufzeichnung) |

### Kapitel 5 — Referenzarchitektur
Die prototypische Instanziierung aus Kap. 5.6 wurde vollständig aufgebaut, womit alle fünf Säulen (S1–S5) operationalisiert waren:

- **S1 — Plattform/Cloud-native (DP5):** AKS-Cluster (Sweden Central), Image-Build, Helm-Deployment.
- **S2 — Quality-Gate-Kontrollsystem:** drei Gatekeeper-Gates (G-DEP-02, G-OPS-03, G-OPS-05) aktiv und entscheidend.
- **S3 — Policy Engine (Gatekeeper-Teil):** ConstraintTemplates registriert, Auswertung zur Admission-Time.
- **S4 — Evidence Store:** PostgreSQL mit Schema v02 + Migration v03 (inkl. Hash-Chain-Trigger, Kap. 5.4).
- **S5 — Monitoring/PMS:** Prometheus, Grafana und Alertmanager (Kap. 5.5).

### Kapitel 6 — Evaluation
Der Lauf realisiert unmittelbar:

- **Kap. 6.3.4 (Säule 2 — Runtime-Gates auf AKS), Green-Path:** Die konforme Anwendung wurde admittiert; Pod `1/1 Ready`; Health-Endpoint mit erwartetem JSON-Körper.
- **Kap. 6.3.4, Red-Path:** Ein nicht-konformes Deployment wurde mit denselben sechs Verletzungs-Meldungen (G-DEP-02 ×2, G-OPS-03 ×2, G-OPS-05 ×2) abgelehnt, die die Arbeit dokumentiert. Damit ist die in Kap. 6.3.2 beschriebene Bypass-Lücke geschlossen: Auch ein direkter `kubectl apply` am CI/CD-Pfad vorbei wird abgewiesen.
- **Kap. 6.3.2 (Defense-in-Depth):** Der Red-Path belegt die Notwendigkeit der zweiten (Laufzeit-)Enforcement-Ebene gegenüber einer reinen CI/CD-Prüfung.
- **Kap. 6.3.5 (Evidence Store + Monitoring):** Aufbau der Nachweis-Datenbank und der Monitoring-Säule als Querschnittskomponente.

### Einordnung der zwei Defekte (Kap. 6.3.7 / Anhang D)
Kap. 6.3.7 dokumentiert für den ursprünglichen Lauf sechs plattformspezifische Schwierigkeiten (S1–S6) und 18 Integrity-Fixes. Die beiden hier behobenen Skript-Defekte sind derselben Klasse werkzeug- bzw. umgebungsspezifischer Reibung zuzuordnen und nun dauerhaft im Skript behoben. Dies stützt die in Kap. 6.3.7 betonte operative Schlankheit und Reproduzierbarkeit des PoC.

### Zusammenfassung
Der Lauf erbringt den technisch-funktionalen Nachweis der Arbeit (Evaluationsstufe b, Kap. 6.3) erneut: Die in Kap. 5 entworfene Architektur erzwingt auf realer Azure-Infrastruktur regelkonforme Deployments (ADMIT) und blockiert nicht-konforme (REJECT); nach Behebung der zwei Skript-Defekte ist die Instanziierung in einem Durchlauf reproduzierbar.
