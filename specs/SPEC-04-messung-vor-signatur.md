# SPEC-04 — Messung vor Signatur: gemessene und geprüfte Werte verbinden

**Status:** Auftrag an Claude Code
**Erstellt:** 2026-08-24
**Voraussetzung:** SPEC-01 bis SPEC-03 umgesetzt (Check-Ebene-Severity, `role_scope`, Evidence-Schema v05)
**Betroffen:** `pipeline/gate_orchestrator.py`, `monitoring/drift_detector.py`, `scenarios/healthcare-ambient-ai-scribe/`, `policies/deployment/policy_safety_metrics.rego`, `policies/operations/policy_monitoring_configured.rego`, Evidence-Schema, Gate-Definitionen G-DEP-02 / G-OPS-03, Tests
**Handbuch:** setzt Teil 11 „Sofort" Punkte 1–3 um (v0.4, 20.08.2026); Analyse in 7.5 und 7.6

---

## 1. Anlass

Die Messgrößen-Analyse in Handbuch 7.5 hat einen Befund erzeugt, der das Kernversprechen des Artefakts trifft:

> **Gemessene und geprüfte Werte berühren sich nicht.**

Die Anwendung misst, der Drift-Detektor rechnet — und die Gates prüfen eine Handdatei, die mit beidem nichts zu tun hat. Es existieren zwei getrennte Welten:

```
App misst  → scribe_latency_seconds → Prometheus → Drift-Detektor → PSI → (endet hier)
Gate prüft ← eval_results.json (Handdatei, erfundene Werte)
```

### 1.1 Drei belegte Einzelbefunde

**(1) `eval_results.json` ist eine Handdatei.** `scenarios/healthcare-ambient-ai-scribe/fixtures/eval_results.json`, Feld `"model_version": "mock-v1.0.0"`. Kein Code im Repo erzeugt diese Datei; CI und lokale Pipeline lesen sie ausschließlich.

**(1a) Neuer Befund, im Handbuch v0.4 noch nicht vermerkt — die Handdatei ist in sich widersprüchlich.** `quality_metrics.accuracy` steht auf `0.89`. `gate_result.details` behauptet für dieselbe Metrik `{"metric": "accuracy", "value": 0.91, "result": "PASS"}`. Zwei erfundene Werte für dieselbe Größe, die nicht einmal untereinander konsistent sind. Kein Gate merkt es, weil `policy_safety_metrics.rego` `input.quality_metrics.accuracy` gegen den Schwellenwert prüft und `input.gate_result.all_passed` separat — die beiden Pfade werden nie gegeneinander gehalten. **Das ist die kompakteste Illustration des Gesamtbefunds und gehört als Beleg ins Handbuch.**

**(2) Der Drift-Detektor misst Latenz als Stellvertreter und fällt still auf Fiktion zurück.** `monitoring/drift_detector.py:172 ff.` liest `scribe_latency_seconds_bucket` und nutzt die Buckets laut eigenem Kommentar als *Proxy* für die Eingabeverteilung. Findet er keine Buckets (Zeile 204 ff.), gibt er eine **fest kodierte Verteilung** zurück — mit `source: url` und frischem `captured_at`. Das Ergebnis ist von einer echten Messung nicht unterscheidbar.

**(3) `scribe_mock_mode` wird von keinem Gate gelesen.** Die Gauge existiert (`scenarios/healthcare-ambient-ai-scribe/app/main.py:61`), `grep -r "mock_mode" policies/` findet nichts. Ein Kontrollsystem, das im Mock-Betrieb PASS meldet, ist die peinlichste denkbare Lücke.

**(3a) Zusatzbefund zu G-OPS-03 — zwei Erzeuger, eine Gate-ID, verschiedene Logik.** `record_drift_evidence()` (`drift_detector.py:302`) schreibt bereits heute einen Evidence-Record unter `gate_id: "G-OPS-03"` mit einer in Python berechneten `decision`. Parallel dazu bewertet `policy_monitoring_configured.rego` dasselbe Gate über drei Pod-Annotationen. Die Aussage „der Drift-Detektor speist kein Gate" ist also zu grob: **er umgeht die Policy-Ebene und setzt die Entscheidung selbst.** Dieselbe Gate-ID trägt damit Evidenz aus zwei Quellen mit unvereinbarer Entscheidungslogik. Das ist gravierender als eine bloße Lücke.

**(3b) Und die Annotation ist genau der Angriffspunkt, den E6 benennt.** `policy_monitoring_configured.rego` prüft `genaiops.io/drift-detection-enabled == "true"` — eine Selbstauskunft im Manifest. Die Frage des Gates lautet „läuft Drift-Erkennung?", geprüft wird „behauptet jemand, dass Drift-Erkennung läuft?". Der PSI-Wert, der die Frage beantworten könnte, liegt daneben und wird nicht gelesen.

### 1.2 Der Leitsatz dieser SPEC

> **Herkunft vor Unterschrift.**

Handbuch 7.7 formuliert die Reihenfolge und begründet sie: Eine Signatur auf einem erfundenen Wert ist eine kryptografisch einwandfrei bewiesene Lüge. Die naheliegende Rückfrage im Fachgespräch lautet nicht „ist das signiert?", sondern **„woher kommt die Zahl?"** — und die muss beantwortet sein, bevor `cosign` überhaupt sinnvoll ist.

**E-1 ist ausdrücklich nicht Gegenstand dieser SPEC.** Sie schafft die Voraussetzung dafür: einen Wert, dessen Signatur etwas wert wäre.

---

## 2. Was diese SPEC nicht enthält

Bewusste Abgrenzung, damit der Auftrag abarbeitbar bleibt:

| Nicht enthalten | Warum, und wo es hingehört |
|---|---|
| **E-1-Signatur (`cosign attest-blob`, keyless/OIDC)** | Folgt als SPEC-05, **erst nach** dieser SPEC. Reihenfolge aus Handbuch Teil 11 Punkt 4 |
| **E-2 über Gatekeeper `data.inventory`** | Braucht einen laufenden Cluster; diese SPEC läuft vollständig lokal |
| **Feedback-Kanal für Ground Truth** (Handbuch 9.2, NEU/HOCH) | Größter inhaltlicher Block, eigene SPEC. Zusätzlich in der Redispatch-Domäne noch nicht übersetzt — die Leitstellen-Freigabe ist dort das Label, nicht die Arztkorrektur |
| **Output- und Konzeptdrift** (7.6 Lücke 1) | Diese SPEC verdrahtet die *vorhandene* Messung. Neue Messgrößen sind ein eigener Block |
| **Aufsichtsmetriken, Fristenuhr Art. 73, Fairness im Betrieb** | 7.6 Lücken 2, 3, 5 — eigene Blöcke |
| **Redispatch-Vignette** | Domänenarbeit, unabhängig von dieser Verdrahtung |

**Ebenfalls nicht enthalten: die Ersetzung des Latenz-Proxys durch eine echte Eingabeverteilung.** Teil 3 dieser SPEC macht den Stellvertreter *sichtbar und ehrlich*, es schafft ihn nicht ab. Die Begründung steht in Handbuch 7.6: Ohne Labels ist die labelfreie Größe die einzig verfügbare. Ein PoC-Stellvertreter, der als solcher deklariert ist, ist vertretbar; einer, der als Messung auftritt, ist es nicht.

---

## 3. Teil 1 — Laufzeit-Attestierung: `scribe_mock_mode` als Vorbedingung jedes Gates

### 3.1 Warum das nicht in Rego gehört

Die naheliegende Umsetzung — jede Policy prüft `input.mock_mode` — ist falsch, aus zwei Gründen:

1. Sie müsste in **jeder** der 17 Policies wiederholt werden. Eine Vorbedingung, die 17-mal dupliziert wird, wird irgendwann in einer vergessen.
2. Rego darf nicht messen. Gatekeeper unterbindet externe Aufrufe standardmäßig und zu Recht (Handbuch 7.7). Der Wert muss dem Gate als **Input** vorgelegt werden, er darf nicht von ihm geholt werden.

**Also: eine Stufe vor den Gates, im Orchestrator, einmal pro Lauf.**

### 3.2 Umsetzung

Neue Funktion in `pipeline/gate_orchestrator.py`:

```
resolve_runtime_mode(config) -> ("live" | "mock" | "unknown", quelle: str)
```

Auflösung in dieser Reihenfolge — dasselbe Muster wie `resolve_ai_act_role()` (SPEC-03):

1. Umgebungsvariable `RUNTIME_MODE` (nur für Tests; setzt sie jemand im CI, ist das ein Befund)
2. Scrape des Metrics-Endpunkts aus dem Szenario-Manifest, Feld `pipeline.metrics_endpoint` → Gauge `scribe_mock_mode`
3. Metrics-Snapshot-Datei, falls im Manifest als `pipeline.metrics_snapshot` angegeben (für Läufe ohne laufende App)
4. Kein Wert auflösbar → **`unknown`**

**`unknown` ist nicht `live`.** Wer nicht weiß, ob das System echt lief, hat keinen Nachweis, dass es echt lief. Der Default fällt auf die unsichere Seite, nicht auf die bequeme.

### 3.3 Die Wirkung auf die Gate-Entscheidung — Entwurfsvorschlag, vor Implementierung abzustimmen

> **Dies ist die risikoreichste Entwurfsentscheidung dieser SPEC — Variante bitte vorschlagen und abstimmen, bevor implementiert wird.** Gleiches Vorgehen wie bei der Hash-Chain-Migration in SPEC-03 Abschnitt 4.

Drei Varianten stehen zur Wahl:

| Variante | Wirkung | Bewertung |
|---|---|---|
| **A — Mock erzwingt FAIL** | Jedes Gate schlägt bei `mock`/`unknown` fehl | **Verworfen.** Macht den Kolloquiums-Walkthrough unmöglich; das Mock-Szenario ist ein legitimer PoC-Betriebsmodus, kein Compliance-Verstoß. Ein Gate, das immer fehlschlägt, wird abgeschaltet — das Schicksal aller schwachen Gates (Handbuch 7.3.1) |
| **B — neuer Entscheidungswert `INCONCLUSIVE`** | `decision` bekommt einen dritten Wert | **Verworfen.** `decision TEXT NOT NULL CHECK (decision IN ('PASS','FAIL'))` steht in beiden Schema-Fassungen. Die Erweiterung zöge jede Auswertung, jeden Test und den Chain-Verifier mit. Zu teuer für den Gewinn |
| **C — `runtime_mode` als gehashtes Feld am Record** | Entscheidung bleibt PASS/FAIL, der Betriebsmodus wird mitversiegelt | **Empfohlen.** Ein PASS im Mock-Betrieb bleibt möglich — ist aber von einem PASS im Echtbetrieb **unterscheidbar und nicht nachträglich fälschbar**. Genau das ist heute nicht der Fall |

**Begründung für C:** Das Artefakt verspricht Tamper-**Evidence**, nicht Tamper-Prevention (Handbuch 7.7). Die Aufgabe ist nicht, den Mock-Betrieb zu verbieten, sondern ihn **unverbergbar** zu machen. Ein Auditor, der eine Kette liest, muss sehen können, welche PASS-Records aus einem Lauf ohne echtes Modell stammen. Variante C leistet genau das und nichts darüber hinaus.

Zusätzlich, ohne Schemaänderung: Der Konsolen-Report und `pipeline_report_*.json` weisen den Modus **prominent** aus, nicht in einer Fußnote. Bei `mock` oder `unknown` erscheint ein Banner über der Ergebnistabelle.

### 3.4 Migration v05 → v06

Neue Datei `evidence-store/migrations/v05_to_v06_add_runtime_mode.sql`, **exakt nach dem etablierten Muster** aus `v03_to_v04` und `v04_to_v05`:

- Spalte `runtime_mode TEXT` mit `CHECK (runtime_mode IN ('live','mock','unknown'))`
- **Per-Field-Cutoff, kein Back-fill.** `audit_id < cutoff` → Feld nicht in der Payload, Spalte `NULL`. `audit_id >= cutoff` → Feld in der Payload, Spalte verpflichtend
- NULL unterhalb des Cutoffs ist tragend, nicht kosmetisch: Ein back-gefüllter Wert wäre unauthentifiziert, sein Ändern bräche keinen Hash. Der Verifier behandelt jeden Nicht-NULL-Wert unterhalb des Cutoffs als Manipulation
- `compliance.set_hash_chain()` und `verify_hash_chain.py` entsprechend erweitern; die Kette trägt danach legitim 13-, 14-, 15- und 16-Feld-Records

**Die bestehende Kette darf nicht brechen.** `verify_hash_chain.py` muss nach der Migration über den gesamten Bestand mit Exit 0 laufen.

---

## 4. Teil 2 — `eval_results.json` wird Ausgabe statt Eingabe

### 4.1 Die Regel bleibt, der Input ändert sich

`policy_safety_metrics.rego` ist **korrekt und bleibt unverändert**. Die Schwellenwerte (accuracy ≥ 0.85, latency_p95 ≤ 2000 ms, safety_score ≥ 0.90) sind richtig, die Severity-Trennung C-01 MUST / C-02 SHOULD ist seit SPEC-01 sauber. Falsch war nie die Regel — falsch war, woher die Zahl kam.

Das ist die konkrete Einlösung von Handbuch 7.7: **Die E-Stufe steckt in der Herkunft des Inputs, nicht in der Prüflogik.**

### 4.2 Neuer Baustein: `scenarios/healthcare-ambient-ai-scribe/eval/eval_runner.py`

Erzeugt `eval_results.json`, statt sie vorzufinden.

| Feld im Ergebnis | Herkunft nach dieser SPEC |
|---|---|
| `performance_metrics.latency_p50_ms` / `_p95_ms` / `_p99_ms` | **Gemessen** — Quantile aus `scribe_latency_seconds_bucket` |
| `performance_metrics.throughput_rps` | **Gemessen** — `scribe_requests_total` über die Laufzeit |
| `evaluation.run_id`, `evaluated_at`, `pipeline_id` | **Erzeugt** — aus dem Lauf, nicht aus der Datei |
| `evaluation.model_version` | **Gelesen** — `MODEL_VERSION` aus der Anwendung, nicht aus dem Manifest abgeschrieben |
| `runtime_mode` (neu) | **Gemessen** — `scribe_mock_mode`, siehe Teil 1 |
| `quality_metrics.*`, `safety_metrics.*`, `subgroup_analysis`, `adversarial_tests` | **Weiterhin nicht messbar** — siehe 4.3 |
| `gate_thresholds` | Konfiguration, bleibt Eingabe |
| `gate_result` | **Entfällt ersatzlos** — siehe 4.4 |

Für die Messung wird ein deterministischer Lastlauf gegen `/transcribe` gefahren (feste Anzahl Anfragen, fester Eingabesatz), danach `/metrics` gescraped. Kein Cluster, kein Prometheus-Server nötig: Der Histogramm-Endpunkt der Anwendung genügt. Die Bucket-Parselogik existiert bereits in `drift_detector.py:188 ff.` und ist in ein gemeinsames Modul zu ziehen, statt sie ein zweites Mal zu schreiben.

### 4.3 Was ehrlich bleiben muss: `accuracy` ist nicht gemessen

**`accuracy` wird durch diese SPEC nicht echt.** Handbuch 7.6 benennt den Grund: Ohne Ground Truth gibt es im Betrieb keine Genauigkeit, nur Stellvertreter. Das ist kein Versäumnis dieses Repos, sondern das ungelöste Kernproblem des Feldes.

**Daraus folgt eine Kennzeichnungspflicht im Ergebnisdokument.** Jede Metrikgruppe trägt ein Feld `provenance`:

```json
"performance_metrics": {
  "provenance": "measured",
  "source": "scribe_latency_seconds_bucket @ http://localhost:8080/metrics",
  "measured_at": "2026-08-24T09:12:33Z",
  "latency_p95_ms": 890
},
"quality_metrics": {
  "provenance": "declared",
  "source": "offline evaluation set, manually maintained",
  "note": "Kein Ground-Truth-Kanal im Betrieb — siehe HANDBUCH 7.6. Nicht als Betriebsmessung verwendbar.",
  "accuracy": 0.89
}
```

Zulässige Werte: `measured` · `derived` · `declared`.

> **Das ist der eigentliche inhaltliche Gewinn dieser SPEC.** Nach der Umsetzung ist an jeder einzelnen Zahl ablesbar, ob sie gemessen, gerechnet oder behauptet ist. Die Behauptung verschwindet nicht — sie wird **als Behauptung kenntlich**. Das ist die Anwendung von E6 auf die Feldebene und beantwortbar macht es die Rückfrage „woher kommt die Zahl?" für jede Zahl einzeln.

**Zusatzcheck C-03 (neu, Severity SHOULD)** in `policy_safety_metrics.rego`: Trägt eine für die MUST-Prüfung herangezogene Metrikgruppe `provenance: "declared"`, wird gewarnt. Der Lauf bleibt grün, der Befund steht in der Evidenz. Nicht MUST — sonst wäre der Bestand am Tag der Einführung rot, und die Warnung träfe eine Lücke, die diese SPEC bewusst offen lässt.

### 4.4 `gate_result` entfällt

Das Feld ist der Widerspruch aus Befund 1a: eine im Dokument mitgelieferte Behauptung über das Prüfergebnis — in einem Dokument, das *Gegenstand* der Prüfung ist. Ein Prüfling, der sein eigenes Zeugnis mitbringt.

`deny`-Regel `input.gate_result.all_passed == false` (`policy_safety_metrics.rego:79 ff.`) entfällt mit. Sie prüft nichts Eigenständiges: Wenn die Schwellenwerte halten, ist das Ergebnis PASS, und das entscheidet Conftest, nicht die Datei. Die Zeilenzahl der Regeln sinkt dadurch — das ist im `CHANGELOG.md` zu vermerken, weil die Zählstände in der Thesis zitiert sind (Muster: SPEC-03 Abschnitt 5.4).

### 4.5 Gate-Definition G-DEP-02 nachziehen

- `evidence_level.current`: `E-0` → **`E-0/E-1-vorbereitet`** — die Zahl ist erzeugt und nachvollziehbar, aber noch unsigniert. **Nicht auf E-1 setzen.** E-1 verlangt Signatur und Erzeuger-Identität; beides kommt erst mit SPEC-05
- `trigger`: neu formulieren — Conftest evaluiert das **erzeugte** Ergebnis, nicht eine eingecheckte Fixture
- `evidence_level.rationale`: den Herkunftsstand benennen
- Neuer Check C-03 mit `severity: SHOULD`, `implementation: implemented`
- `notes`: Befund 1a und die Abschaffung von `gate_result` dokumentieren, mit Datum — Pflegeregel Teil 0, Begründungskette bleibt sichtbar

---

## 5. Teil 3 — Drift-Ergebnis an G-OPS-03 verdrahten

### 5.1 Den stillen Fallback abschaffen

`drift_detector.py:204 ff.` gibt bei fehlenden Buckets eine fest kodierte Verteilung zurück, versehen mit `source: url` und frischem Zeitstempel. **Das ist die schlimmste Einzelstelle im Repo**, weil sie eine Fiktion als Messung ausgibt — schlimmer als gar keine Messung, weil sie eine beruhigende Antwort liefert.

**Ersetzen durch:** Fehler mit Exit-Code ≠ 0 und einer Meldung, die den Grund nennt. Kein Fallback, keine Mock-Verteilung, kein „für Demo-Zwecke".

Wer eine Verteilung ohne laufende App braucht, gibt sie **ausdrücklich** an: `--source monitoring/fixtures/current_normal.json`. Der Pfad existiert bereits (`load_distribution_from_file`), ist explizit und lügt nicht über seine Herkunft. Die stille Variante wird ersatzlos gestrichen.

### 5.2 Die Doppelzuständigkeit auflösen

Aus Befund 3a: Zwei Erzeuger schreiben Evidenz unter `G-OPS-03` mit verschiedener Logik. Das ist zu bereinigen, nicht zu ergänzen.

**Regel: Der Drift-Detektor misst, er entscheidet nicht.**

`record_drift_evidence()` verliert die selbst gesetzte `decision`. Er schreibt sein Ergebnis als **Messdokument** — `psi_score`, `jsd_score`, `drift_status`, `bucket_labels`, `provenance: "measured"`, `source`, `measured_at`. Die Entscheidung trifft ausschließlich Rego, wie bei jedem anderen Gate auch.

Das ist zugleich die saubere Anwendung von Handbuch 7.7: *Die Messung liefert den Inhalt, die Regel trifft die Entscheidung.* Ein Messwerkzeug, das sein eigenes Ergebnis bewertet, verwischt genau die Trennung, die das Artefakt behauptet.

### 5.3 `policy_monitoring_configured.rego` erweitern

Die drei bestehenden Annotationsprüfungen **bleiben** — sie prüfen die Konfiguration, und die muss stimmen. Ergänzt wird die Prüfung des Ergebnisses:

| Check | Regel | Severity | Ebene |
|---|---|---|---|
| C-01 (Bestand) | ServiceMonitor-Annotation gesetzt | MUST | E-0 |
| C-02 (Bestand) | Drift-Detection-Annotation gesetzt | MUST | E-0 |
| **C-03 (neu)** | Drift-Messdokument vorhanden, `measured_at` nicht älter als das konfigurierte Intervall | **MUST** | E-3 |
| **C-04 (neu)** | `psi_score ≤ 0.2` **und** `jsd_score ≤ 0.1` | **MUST** | E-3 |
| **C-05 (neu)** | `provenance == "measured"` — kein Fixture-Lauf zählt als Betriebsnachweis | **SHOULD** | E-3 |

**C-03 ist der wichtigere der beiden MUST-Checks.** Er unterscheidet „PSI ist niedrig" von „es wurde seit drei Wochen nicht gemessen". Ein Gate, das nur den Wert prüft, hält Stillstand für Stabilität — die Drift-Erkennung könnte seit Wochen abgestürzt sein, und der letzte gute Wert stünde weiter da. Die Frist ist damit selbst ein Prüfgegenstand.

**Die E-Stufen-Wirkung, ausdrücklich benannt:** C-01/C-02 prüfen, ob jemand *behauptet*, dass Drift-Erkennung läuft (E-0). C-03/C-04 prüfen, ob sie *gelaufen ist und was sie ergeben hat* (E-3). Beide bleiben im Gate. Der Unterschied zwischen ihnen ist die Demonstration des gesamten E6-Modells an einem einzigen Gate — und damit **das vorzeigbarste Ergebnis dieser SPEC**.

### 5.4 Gate-Definition G-OPS-03 nachziehen

- `evidence_level.current`: `E-0` → **`E-0/E-3 gemischt`**, mit Zuordnung je Check über das seit SPEC-01 vorhandene Feld `policy_checks[].evidence_level`. **Das ist der erste Gebrauch dieses Feldes mit echtem Inhalt** — bislang steht dort überall `null`
- C-03 bis C-05 mit Severity und `implementation: implemented` eintragen
- `notes`: die aufgelöste Doppelzuständigkeit aus 5.2 dokumentieren, mit Datum

---

## 6. Reihenfolge der Umsetzung

Die drei Teile sind nach steigendem Risiko geordnet und **in dieser Reihenfolge** abzuarbeiten:

1. **Teil 3 zuerst** — der stille Fallback (5.1) ist eine Löschung, sofort machbar, kein Schemabezug. Größte Ehrlichkeitswirkung pro Zeile
2. **Teil 2** — `eval_runner.py`, `provenance`-Felder, `gate_result` entfernen. Keine Schemaänderung
3. **Teil 1 zuletzt** — die Migration v05 → v06 ist der einzige Eingriff in die Hash-Kette. Sie kommt ans Ende, damit sie auf einem sonst grünen Stand aufsetzt

> **Abstimmungspunkt vor Beginn von Teil 1:** Variante A/B/C aus 3.3 vorschlagen und bestätigen lassen.

---

## 7. Tests

- **Herkunft:** `eval_results.json` wird erzeugt; zwei Läufe mit unterschiedlicher Last liefern **unterschiedliche** `latency_p95_ms`. Ein identischer Wert über zwei Läufe ist ein Fehlschlag, kein Erfolg — er hieße, dass wieder eine Konstante geprüft wird
- **Konsistenz:** Ein Regressionstest, der die Widerspruchsklasse aus Befund 1a abfängt — dieselbe Metrik darf im Ergebnisdokument nicht zweimal mit verschiedenen Werten vorkommen
- **Mock-Erkennung:** Lauf mit `MOCK_MODE=1` → Record trägt `runtime_mode: "mock"`; Lauf ohne erreichbare App → `"unknown"`, **nicht** `"live"`
- **Kein stiller Fallback:** Drift-Detektor gegen einen Endpunkt ohne Histogramm-Buckets → Exit ≠ 0, keine Zahlen in der Ausgabe. Der Test prüft ausdrücklich, dass **keine** Verteilung zurückkommt
- **C-03 Frist:** Fixture mit `measured_at` älter als das Intervall → deny, obwohl `psi_score` gut ist. Der Negativfall ist der eigentliche Test
- **C-04:** `monitoring/fixtures/current_drifted.json` (existiert) muss G-OPS-03 zum Fehlschlag bringen. Bislang berührt diese Fixture kein Gate
- **Hash-Kette:** `verify_hash_chain.py` nach der Migration über den Gesamtbestand, Exit 0. Records vor und nach dem Cutoff in derselben Kette
- **Chain-Migration:** `tests/test_hash_chain_migration.py` um den v05 → v06-Fall erweitern
- **Integrity-Regression:** Prüfung ergänzen, dass jeder Check mit `evidence_level != null` einen zulässigen Wert (`E-0` bis `E-3`) trägt
- **Gesamtsuite:** 173/173 Rego-Tests plus die neuen, 32/32 `test_all.py`, Integrity-Regression 0 actionable

---

## 8. Definition of Done

- [ ] Stiller Fallback in `load_distribution_from_app()` ersatzlos entfernt, Exit ≠ 0 mit Begründung
- [ ] Bucket-Parselogik in ein gemeinsames Modul gezogen, nicht dupliziert
- [ ] `record_drift_evidence()` schreibt ein Messdokument ohne eigene `decision`
- [ ] `policy_monitoring_configured.rego` um C-03 (Frist), C-04 (Schwellenwerte), C-05 (Provenance) erweitert
- [ ] `eval_runner.py` erzeugt `eval_results.json`; Latenz und Durchsatz gemessen
- [ ] `provenance` (`measured`/`derived`/`declared`) auf jeder Metrikgruppe, `quality_metrics` ehrlich als `declared`
- [ ] `gate_result` aus Fixture und Policy entfernt, Zählstandsänderung im `CHANGELOG.md`
- [ ] Befund 1a (0.89 ≠ 0.91) in den `notes` von G-DEP-02 dokumentiert
- [ ] C-03 in `policy_safety_metrics.rego` (SHOULD) — Warnung bei `declared` in einer MUST-Prüfung
- [ ] **Variante A/B/C aus 3.3 vorgeschlagen und abgestimmt, bevor implementiert**
- [ ] `resolve_runtime_mode()` mit vierstufiger Auflösung, Default `unknown`
- [ ] Migration `v05_to_v06_add_runtime_mode.sql` nach dem Per-Field-Cutoff-Muster, kein Back-fill
- [ ] `set_hash_chain()` und `verify_hash_chain.py` erweitert, Gesamtkette Exit 0
- [ ] Report und Konsolenausgabe weisen `mock`/`unknown` als Banner aus
- [ ] `evidence_level` je Check auf G-OPS-03 gesetzt (erster echter Gebrauch des Feldes)
- [ ] G-DEP-02 und G-OPS-03 in `evidence_level.current`, `trigger`, `rationale`, `notes` nachgezogen
- [ ] Gesamttestsuite grün
- [ ] Handbuch-Fortschreibung vorbereitet: Befund 1a nach 7.5, Befund 3a nach 7.5 (2), erledigte Punkte in 9.2 und Teil 11 mit Nachweis markiert — **nicht gelöscht** (Pflegeregel Teil 0)
