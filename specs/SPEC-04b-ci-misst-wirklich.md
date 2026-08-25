# SPEC-04b — Die CI misst wirklich

**Status:** Auftrag an Claude Code
**Erstellt:** 2026-08-25
**Voraussetzung:** SPEC-04 umgesetzt (Commit `9afc47d`, Evidence-Schema v06)
**Betroffen:** `.github/workflows/gate-pipeline.yml`, `pipeline/gate_orchestrator.py`, `pipeline/scenarios/`, `gate-definitions/operations/G-OPS-03`, `tests/test_integrity_regression.py`
**Handbuch:** setzt Teil 11 Punkt 5 vorbereitend um; schließt die in SPEC-04 offen gebliebene Erzwingung

---

## 1. Anlass

SPEC-04 hat das Repo in die Lage versetzt zu messen. **Die CI nutzt davon nichts.** Am Workflow verifiziert (Stand `2af04a2`):

- **G-DEP-02** liest weiterhin `fixtures/eval_results.json` als eingecheckte Datei. Der `eval_runner` läuft im Workflow nicht. Das Dokument wird also erzeugt — aber auf einem Entwicklerrechner, nicht in der Pipeline, die es prüft.
- **G-OPS-03** bekommt nur `deployment_compliant.yaml`. Ohne `input.drift_measurement` bleiben C-03, C-04 und C-05 stumm. Nachgewiesen: `conftest test deployment_compliant.yaml` meldet *13 tests, 0 failures, 0 warnings* — die drei neuen Checks feuern nicht.
- Der Workflow hat **kein** `services:` und startet keine Anwendung.

**Folge: Das Gate, das gestern noch E-0 war, ist in der CI weiterhin E-0.** Die E-3-Checks existieren, werden aber nie ausgeführt. Ein Katalog, der eine Fähigkeit deklariert und sie in der einzigen Umgebung, die zählt, nicht aktiviert, ist der Nachbar von `implementation: design_only` — nur ohne die Kennzeichnung.

### 1.1 Der eigene Fehler, der zuerst zu benennen ist

SPEC-04 Abschnitt 5.3 schrieb wörtlich:

> „Requiring the document to be supplied at all is enforced one level up, by the orchestrator, not by absence of a rule here."

**Das wurde nicht implementiert.** Es gibt heute keinen Mechanismus, der verlangt, dass eine Messung überhaupt vorgelegt wird. Wer das Messdokument weglässt, bekommt ein grünes G-OPS-03 auf drei Annotationen.

> **Ein MUST-Check, den man durch Weglassen des Inputs umgeht, ist kein MUST.** Das ist dieselbe E-0-Schwäche, die das Gate loswerden sollte — nur eine Ebene verschoben. Diese SPEC schließt sie, und zwar zuerst.

### 1.2 Ein zweiter Befund derselben Klasse — im Workflow

Der Schritt „Rego Unit Tests" gibt aus:

```
Expected: 173/173 PASS (17 policies, updated 2026-08-15)
PASS: 187/187                       ← tatsächliches Ergebnis des Runners
✅ Rego Unit Tests PASS — 173/173 green
```

Die CI **meldet** 173/173, während 187 Tests liefen. Die Zahl steht hartkodiert im Meldungstext und wird gegen nichts gehalten; sie geht zusätzlich als `count=173` in `$GITHUB_OUTPUT`. Wäre die Testzahl gesunken, hätte die Pipeline weiterhin „173/173 green" gemeldet.

**Das ist strukturell `gate_result.all_passed`:** eine mitgelieferte Behauptung über ein Ergebnis, die niemand gegen das Ergebnis hält. Nur diesmal in der Pipeline, die das Kontrollsystem prüft.

---

## 2. Was diese SPEC nicht enthält

| Nicht enthalten | Warum |
|---|---|
| **E-1-Signatur** (`cosign attest-blob`, keyless/OIDC) | Folgt als SPEC-05. Reihenfolge bleibt: erst Herkunft, dann Unterschrift |
| **E-2 über Gatekeeper `data.inventory`** | Braucht einen Cluster. Diese SPEC läuft vollständig in einem GitHub-Actions-Runner |
| **Kubernetes im CI** (kind/minikube) | Ausdrücklich später. Der Adressat dieser SPEC ist der Runner, nicht der Cluster |
| **Dockerfile für das Drift-Detector-Image** | Bleibt offen (SPEC-04 „Known regression"). Im Runner läuft der Detektor direkt, nicht als CronJob |
| **Echtes Modell / LLM-Aufruf** | Kostenpflichtig. Die CI wird `runtime_mode: mock` melden, und das ist die richtige Antwort — siehe 4.4 |

---

## 3. Teil 1 — Die CI meldet, was gelaufen ist

**Zuerst, weil es die kleinste Änderung mit der größten Signalwirkung ist.** Ein Kontrollsystem, dessen eigene Pipeline eine Zahl behauptet, kann die Behauptungsprüfung anderer nicht glaubwürdig anbieten.

Der Runner gibt bereits `PASS: <n>/<m>` aus. Der Schritt liest diese Zahl statt sie zu setzen:

- Ausgabe des Runners parsen, `count` und `total` daraus ziehen
- Bei `count != total` → Fehlschlag (verhält sich wie bisher, nur ohne Wunschzahl)
- `$GITHUB_OUTPUT` bekommt die **gemessene** Zahl
- Die Schrittbezeichnung darf keine Zahl mehr tragen: aus `"Rego Unit Tests (Layer 1 — 17 policies, 173 tests)"` wird `"Rego Unit Tests (Layer 1 — OPA, fail-fast)"`

**Zusätzlich, gegen die Rückkehr des Fehlers:** Integrity-Check `WORKFLOW_CLAIMS_NO_COUNTS` (MEDIUM). Er prüft, dass `.github/workflows/*.yml` keine hartkodierten Test-, Gate- oder Regelzahlen in Meldungstexten trägt. Die zulässige Ausnahme sind Kommentare, die eine Zahl als Kontext nennen — nicht Ausgaben, die sie als Ergebnis melden.

> Dieselbe Logik wie `README_COUNTS_CURRENT`: Zahlen richtig zu halten gelingt nicht durch Sorgfalt. Es gelingt durch einen Test.

---

## 4. Teil 2 — Die CI startet die Anwendung und misst

### 4.1 Warum das ohne Kubernetes geht

Für **E-3** braucht es eine laufende Anwendung mit `/metrics` — keinen Cluster. Das wurde am 25.08. lokal mit Docker nachgewiesen: Image bauen, `-p 8080:8080` starten, `eval_runner` und Drift-Detektor dagegen laufen lassen, vollständige Kette. Ein GitHub-Actions-Runner kann exakt dasselbe.

Nur **E-2** (`data.inventory`, `readyReplicas`) verlangt zwingend einen Cluster. Diese Stufe bleibt bewusst offen.

### 4.2 Umsetzung

Vor den Deployment-Gates ein neuer Schritt:

1. Image aus `scenarios/healthcare-ambient-ai-scribe/Dockerfile` bauen (bereits vorhanden, non-root, Multi-Stage)
2. Container starten, auf `/health` warten (Poll mit Timeout, kein blindes `sleep`)
3. `eval/eval_runner.py --app-url http://localhost:8080 --requests 50` ausführen
4. Ergebnis nach `/tmp/eval_results.json`

G-DEP-02 liest danach **`/tmp/eval_results.json`**, nicht mehr die eingecheckte Fixture.

> **`pip install` ist im Runner unproblematisch.** Die lokale Beschränkung (kaputtes pip auf dem Autorenrechner, deshalb der stdlib-Stellvertreter in `eval/test_eval_runner.py`) gilt dort nicht. Die CI kann die **echte** Anwendung fahren — sie ist damit die verlässlichere Messumgebung von beiden.

### 4.3 Die eingecheckte Fixture bleibt — als Vergleichspunkt

`fixtures/eval_results.json` wird **nicht** gelöscht. Sie dient weiter dem lokalen Durchlauf ohne Docker und der Walkthrough-Demonstration. Sie trägt bereits `_spec` mit dem Erzeugungskommando.

**Neu:** Ein Schritt vergleicht das in der CI erzeugte Dokument mit der eingecheckten Fixture in der **Struktur** (Feldnamen, `provenance`-Blöcke, Abwesenheit von `gate_result`) — nicht in den Werten, die sich zwangsläufig unterscheiden. Weicht die Struktur ab, ist die Fixture veraltet und wird als Warnung gemeldet.

### 4.4 `runtime_mode` bleibt `mock` — und das ist das Ergebnis, nicht der Mangel

`MOCK_MODE.set(1)` steht fest im Anwendungscode. Die CI wird deshalb **immer** `runtime_mode: mock` in die Evidenz schreiben, das Banner ausgeben und den Record entsprechend versiegeln.

> Das ist kein Defekt der Pipeline. Es ist das System, das funktioniert: ohne echtes Modell kein Echt-Lauf, und die Kette sagt das, statt es zu verschweigen. Ein `live` gäbe es erst mit einem echten LLM-Aufruf, also mit Kosten. **Wer die CI grün und `live` sehen will, muss zahlen — genau diese Ehrlichkeit ist der Punkt.**

Ein Testfall hält das fest: die CI-Evidenz **muss** `runtime_mode = mock` tragen. Ein `live` aus dem Runner wäre ein Befund, kein Fortschritt.

---

## 5. Teil 3 — Drift messen und das Gate erzwingen

### 5.1 Messung im Runner

Nach dem Lastlauf aus Teil 2 hat die Anwendung Histogramm-Beobachtungen. Damit:

1. `drift_detector.py --init-baseline --source http://localhost:8080/metrics --baseline /tmp/baseline.json`
2. Zweiter Lastlauf mit **anderem** Eingabeprofil (andere Textlängen), damit die Verteilung sich bewegen kann
3. `drift_detector.py --source http://localhost:8080/metrics --baseline /tmp/baseline.json --measurement-out /tmp/drift_measurement.json`

G-OPS-03 wird danach **zweimal** ausgewertet: gegen das Deployment-Manifest (C-01/C-02, E-0) und gegen das Messdokument (C-03/C-04/C-05, E-3). Beide Ergebnisse fließen in **einen** Evidence-Record, wie bei `role_scope: BOTH` in SPEC-03.

### 5.2 Die Erzwingung — der Kern dieser SPEC

Gate-Definitionen bekommen ein optionales Feld:

```yaml
required_inputs:
  - kind: "drift_measurement"
    produced_by: "monitoring/drift_detector.py"
    max_age_seconds: 900
```

**Regel im Orchestrator:** Deklariert ein Gate ein `required_inputs`-Element und liegt es beim Lauf nicht vor, ist das Gate **FAIL** — mit einer Meldung, die den fehlenden Input benennt, nicht mit stillem Durchwinken.

> **Warum im Orchestrator und nicht in Rego:** Rego kann die Abwesenheit eines Dokuments nicht von der Abwesenheit einer Regel unterscheiden. Eine Regel, die nur feuert, wenn ihr Input existiert, ist per Konstruktion umgehbar, indem man den Input weglässt. Die Anwesenheitspflicht gehört auf die Ebene, die die Inputs zusammenstellt.

**Neuer Integrity-Check `REQUIRED_INPUTS_ENFORCED`** (HIGH): Jeder Check mit `evidence_level` E-2 oder E-3 muss zu einem Gate gehören, das den zugehörigen Input in `required_inputs` deklariert. Sonst wäre eine hohe Beweisstufe deklariert, aber weglassbar — die genaue Lücke aus 1.1, in Testform gegossen.

### 5.3 Ein Negativfall gehört in die CI

Ein zweiter Lauf mit `monitoring/fixtures/current_drifted.json` als Quelle muss G-OPS-03 zum **Fehlschlag** bringen (C-04). Ein grüner Durchlauf allein beweist nur, dass nichts blockiert — nicht, dass etwas blockieren *würde*.

Dasselbe für Teil 2: ein Lauf mit `eval_results_fail.json` muss G-DEP-02 blockieren. Beide Negativfälle laufen als eigener Job, damit sie den Hauptlauf nicht rot färben.

---

## 6. Reihenfolge

1. **Teil 1** — Zahlen aus dem Runner lesen. Keine Abhängigkeiten, sofort machbar
2. **Teil 3.2** — `required_inputs` und die Erzwingung im Orchestrator. **Vor** Teil 2, weil sonst die CI misst, ohne dass das Fehlen der Messung auffiele — und genau dieser Zustand herrscht heute
3. **Teil 2** — App als Service, `eval_runner` im Workflow
4. **Teil 3.1/3.3** — Drift im Runner, Negativfälle
5. Erst danach **SPEC-05** (E-1)

---

## 7. Tests

- **Kein hartkodierter Zählstand:** Testzahl künstlich verändern → CI meldet die neue Zahl, nicht die alte
- **Erzwingung:** Szenario mit `required_inputs`, Dokument entfernt → Gate FAIL mit benanntem Input; Dokument vorhanden → PASS
- **Erzwingung greift auch bei veraltetem Dokument:** `measured_at` außerhalb des Budgets → FAIL über C-03, nicht über die Anwesenheitsprüfung
- **Gemessen, nicht kopiert:** Das in der CI erzeugte `eval_results.json` trägt `provenance: measured`, ein `run_id` aus dem Lauf und **andere** Latenzwerte als die eingecheckte Fixture
- **Mock-Erkennung in der CI:** Evidenz trägt `runtime_mode = mock`; ein `live` lässt den Job fehlschlagen
- **Negativfälle:** `current_drifted.json` blockiert G-OPS-03, `eval_results_fail.json` blockiert G-DEP-02 — beide in einem eigenen Job
- **Kette:** `verify_hash_chain.py` über die CI-Evidenz, Exit 0
- **Strukturvergleich:** erzeugtes Dokument gegen eingecheckte Fixture, Feldnamen und `provenance`-Blöcke identisch
- Gesamtsuite unverändert grün: 187 Rego, 32 `test_all.py`, Integrity 0 actionable

---

## 8. Definition of Done

- [ ] Rego-Test-Schritt liest die Zahl aus dem Runner; Schrittbezeichnung ohne Zahl
- [ ] `$GITHUB_OUTPUT` trägt die gemessene Zahl
- [ ] Integrity-Check `WORKFLOW_CLAIMS_NO_COUNTS` (MEDIUM), beidseitig gegengeprüft
- [ ] `required_inputs` im Gate-Template dokumentiert und auf G-OPS-03 gesetzt
- [ ] Orchestrator lässt ein Gate mit fehlendem `required_inputs`-Element fehlschlagen, mit benanntem Input
- [ ] Integrity-Check `REQUIRED_INPUTS_ENFORCED` (HIGH), beidseitig gegengeprüft
- [ ] Workflow baut das App-Image und startet es; Bereitschaft per `/health`-Poll, nicht per `sleep`
- [ ] `eval_runner.py` läuft im Workflow; G-DEP-02 prüft das erzeugte Dokument
- [ ] Drift-Detektor läuft im Workflow; G-OPS-03 wird gegen Manifest **und** Messdokument ausgewertet, ein Evidence-Record
- [ ] CI-Evidenz trägt `runtime_mode = mock`; ein `live` lässt den Job fehlschlagen
- [ ] Negativfall-Job: `current_drifted.json` blockiert G-OPS-03, `eval_results_fail.json` blockiert G-DEP-02
- [ ] Strukturvergleich erzeugtes Dokument ↔ eingecheckte Fixture, Abweichung als Warnung
- [ ] Hash-Kette über die CI-Evidenz verifiziert, Exit 0
- [ ] `evidence_level.current` von G-OPS-03 neu bewertet — bleibt E-0, solange C-01/C-02 im Gate sind; die Begründung im Gate nachziehen
- [ ] README-Zahlen und CHANGELOG nachgezogen, `README_COUNTS_CURRENT` grün
- [ ] Handbuch: 7.5 und Teil 11 fortschreiben, Befund 1.1 und 1.2 aufnehmen
