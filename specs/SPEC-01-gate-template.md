# SPEC-01 — Gate-Template: `evidence_level` und Severity auf Check-Ebene

**Status:** Auftrag an Claude Code
**Erstellt:** 2026-08-14
**Reihenfolge:** SPEC-01 ist Voraussetzung für SPEC-02 und SPEC-03. Zuerst umsetzen.
**Betroffen:** `gate-definitions/`, `pipeline/gate_orchestrator.py`, `tests/`, `tools/extract_rule_test_mapping.py`

---

## 0. Vorab — Reproduzierbarkeit der publizierten Fassung

Der Zenodo-DOI 10.5281/zenodo.19920310 verweist auf einen Stand, der in einer eingereichten und bewerteten Masterarbeit zitiert wird. Die dort genannten Kennzahlen (14 Requirements, 16 Gates, 10 AUTO / 6 HYBRID / 0 MANUAL, 108 Regeln, 141 Unit-Tests) müssen **reproduzierbar bleiben**.

**Vor der ersten Änderung:**

1. Git-Tag auf den aktuellen Stand setzen, z. B. `thesis-v1.0` mit Verweis auf den DOI.
2. In `README.md` und `CHANGELOG.md` festhalten, dass ab hier eine **Weiterentwicklung jenseits des Thesis-Stands** beginnt.
3. `schema_version: 2` in das Gate-Template aufnehmen; der Thesis-Stand ist implizit `schema_version: 1`.

Ohne diesen Schritt keine weiteren Änderungen.

---

## 1. Ziel

Zwei strukturelle Änderungen am Gate-Template:

**(A) `evidence_level`** — macht die Beweiskraft pro Gate explizit. Zweite Klassifikationsachse **neben** der Automatisierbarkeit, nicht statt ihrer.

**(B) Severity auf Check-Ebene** statt auf Gate-Ebene — löst das Problem, dass heterogene Prüfgegenstände in einem Gate auf die schwächste Severity gezogen werden.

---

## 2. Hintergrund (A) — die vier Evidenz-Ebenen

| Ebene | Was geprüft wird | Fälschungskosten |
|---|---|---|
| **E-0** | Ein Dokument, das jemand geschrieben hat (JSON/YAML, Pod-Annotationen) | Textänderung |
| **E-1** | Ein von einem Werkzeug **erzeugtes und signiertes** Artefakt; geprüft werden Signatur und Erzeuger-Identität (in-toto, SLSA, Sigstore/cosign) | Kompromittierung der CI-Identität |
| **E-2** | Der tatsächliche Clusterzustand über die Kubernetes-API (Gatekeeper `data.inventory`) | Manipulation des laufenden Systems |
| **E-3** | Eine Eigenschaft **über Zeit**, gemessen statt konfiguriert (Prometheus, Drift-Detektor) | Manipulation der Telemetriekette |

**Referenzimplementierung für E-3 existiert bereits:** `monitoring/drift_detector.py` misst PSI/Jensen-Shannon, statt zu prüfen „ist Monitoring konfiguriert?".

**Wichtige Klarstellung für die IST-Einstufung:** Die Gatekeeper-Constraints unter `scenarios/healthcare-ambient-ai-scribe/k8s/gatekeeper/` prüfen überwiegend **Pod-Annotationen**. Eine Annotation behauptet einen Zustand, sie beweist ihn nicht — das ist **E-0**, nicht E-2. Bitte bei der IST-Einstufung streng sein; eine geschönte Ausgangslage macht die ganze Achse wertlos.

**Automatisierbarkeit und Beweiskraft sind orthogonal.** Ein HYBRID-Gate kann E-3-Evidenz tragen; ein AUTO-Gate kann auf E-0 stehen. Die D3×D2-Override-Regel (Automation Ceiling) bleibt davon **vollständig unberührt**.

---

## 3. Hintergrund (B) — warum Severity auf Check-Ebene muss

Zwei belegte Fälle im Bestand:

- **`prospective/art25-role-change/`**: Drei Auslösetatbestände nach Art. 25 Abs. 1 lit. a–c, alle auf `warn` gezogen mit der Begründung, die Art.-97-Schwellenwerte fehlten. Das trifft aber nur auf lit. b („wesentliche Veränderung") zu. Lit. a (Rebranding) und lit. c (Zweckänderung) sind binäre Tatbestände ohne Schwellenwertproblem.
- **`G-DEP-02`**: Laut Thesis-Limitation L12 sind `subgroup_analysis` und `adversarial_tests` SHOULD, während das Gate einheitlich entscheidet.

In beiden Fällen zwingt die Gate-Ebene eine Severity auf, die für einen Teil der Checks falsch ist.

---

## 4. Neues Template

Datei: `gate-definitions/gate_template.yaml`

```yaml
schema_version: 2
id: G-XXX-00
name: ""
dimension: "regulatorisch|technisch|strategisch"
lifecycle_phase: "pre-deployment|deployment|operations"
trigger: ""

# NEU (A): Beweiskraft — IST und ZIEL
evidence_level:
  current: "E-0"          # E-0 | E-1 | E-2 | E-3
  target: "E-1"           # E-0 | E-1 | E-2 | E-3
  rationale: ""           # warum dieses Ziel, was fehlt bis dahin

# GEÄNDERT (B): Liste von Objekten statt Liste von Strings
policy_checks:
  - id: "C-01"                        # gate-lokal eindeutig
    policy: "policy_xxx"              # Rego-Package bzw. Dateiname
    description: ""
    severity: "MUST"                  # MUST -> deny (blockierend)
                                      # SHOULD -> warn (advisory)
    legal_refs: []                    # z. B. ["Art. 26 Abs. 4"]
    evidence_level: null              # optional; null = Gate-Default aus evidence_level.current

evidence_required: []

# GEÄNDERT: nicht mehr gesetzt, sondern abgeleitet (siehe Abschnitt 5)
decision: "derived"

# Automatisierungsklassifikation bleibt unverändert auf Gate-Ebene
automation: "AUTO|HYBRID|MANUAL"

owner: ""
audit_trail:
  enabled: true
  evidence_store_ref: ""
waiver:
  allowed: false
  requires: ""
links:
  requirements: []
  eu_ai_act_refs: []
sources: []
notes: ""
```

---

## 5. Ableitungsregel für `decision`

Die Gate-Entscheidung wird aus den Check-Ergebnissen abgeleitet, in dieser Prüfreihenfolge:

```
1. Mindestens ein MUST-Check verletzt          -> block
2. Gate ist HYBRID (D3xD2-Override greift)     -> manual_review
3. Mindestens ein SHOULD-Check verletzt        -> warn
4. Sonst                                       -> approve
```

**Wichtig zu Schritt 2:** Der HYBRID-Status kommt aus der Automatisierungsklassifikation (D3×D2-Override, Automation Ceiling nach Art. 14), **nicht** aus der Severity. Ein HYBRID-Gate mit verletztem MUST-Check blockiert trotzdem — deshalb steht Schritt 1 vor Schritt 2. Diese Reihenfolge nicht vertauschen.

**Persistierung:** Verletzte SHOULD-Checks werden weiterhin als Advisory im `notes`-Feld des Evidence-Records abgelegt, jetzt aber **einzeln mit Check-ID**, nicht als Sammeltext.

---

## 6. Abbildung auf Rego

Die Zuordnung ist bereits durch die Conftest-Konvention vorgegeben und ändert sich konzeptionell nicht:

| Severity | Rego-Regel | Conftest |
|---|---|---|
| `MUST` | `deny contains msg if { ... }` | Exit 1, blockierend |
| `SHOULD` | `warn contains msg if { ... }` | Exit 0, advisory |

**Migrationsbedarf:** `policies/pre-deployment/policy_bias_assessment_complete.rego` nutzt derzeit ausschließlich `warn` für alle zehn Regeln, weil R013 gate-weit als SHOULD geführt wird. Die Aufteilung dieser Regeln auf MUST/SHOULD erfolgt **nicht in dieser SPEC** — sie hängt an der Neubewertung von R013 im Lichte des neuen Art. 4a EU AI Act und wird separat beauftragt. Hier nur die Struktur schaffen.

**Konvention für die Rückverfolgbarkeit:** Jede Rego-Meldung soll die Check-ID führen, damit der Orchestrator sie eindeutig zuordnen kann:

```
msg := "G-DEP-05/C-03 (R013, Art. 10 Abs. 2 lit. f): fairness_results.metrics fehlt"
```

Format: `<GATE-ID>/<CHECK-ID> (<Requirement>, <Legal-Ref>): <Meldung>`

---

## 7. Umzusetzen

1. **`gate-definitions/gate_template.yaml`** auf das neue Schema heben.
2. **Alle 16 Gate-Definitionen migrieren** (`pre-deployment/`, `deployment/`, `operations/`):
   - `policy_checks` von Stringliste auf Objektliste
   - Severity je Check aus dem bisherigen Gate-`decision` und dem `must_should` des verknüpften Requirements ableiten; wo unklar, konservativ **MUST** setzen und im `notes`-Feld markieren
   - `evidence_level.current` **ehrlich** einstufen (siehe Abschnitt 2), `target` zunächst durchgängig `E-1`
3. **`pipeline/gate_orchestrator.py`**: Ableitungsregel aus Abschnitt 5 implementieren; Check-IDs aus den Rego-Meldungen parsen und einzeln im Evidence-Record ablegen.
4. **`tests/test_integrity_regression.py`**: Konsistenz-Checks auf das neue Schema anpassen; zusätzlich prüfen, dass
   - jeder `policy_checks[].id` gate-lokal eindeutig ist,
   - jede referenzierte Policy existiert,
   - `evidence_level.current` und `.target` gültige Werte tragen und `target >= current` gilt.
5. **`tools/extract_rule_test_mapping.py`**: um die Check-ID-Dimension erweitern.
6. **`tests/test_all.py`** und die Rego-Testsuiten grün halten.
7. **`AGENTS.md`** ergänzen (siehe Abschnitt 8).

---

## 8. Ergänzung für `AGENTS.md`

Damit die Grundsätze in jeder künftigen Claude-Code-Session gelten, folgenden Abschnitt aufnehmen:

```markdown
## Architektur-Grundsätze (ab schema_version 2)

- **Severity gehört an den Check, nicht an das Gate.** Ein Gate mit heterogenen
  Prüfgegenständen darf nicht auf die schwächste Severity gezogen werden.
- **Beweiskraft ist eine eigene Achse.** Jedes Gate führt `evidence_level.current`
  und `.target` (E-0 Selbstauskunft, E-1 signierte Attestierung, E-2 beobachteter
  Systemzustand, E-3 Messung über Zeit). Automatisierbarkeit und Beweiskraft sind
  orthogonal — die D3xD2-Automation-Ceiling bleibt unberührt.
- **Pod-Annotationen sind E-0, nicht E-2.** Eine Annotation behauptet einen
  Zustand, sie beweist ihn nicht.
- **Die Gate-Entscheidung wird abgeleitet, nicht gesetzt.** Reihenfolge:
  MUST verletzt -> block; HYBRID -> manual_review; SHOULD verletzt -> warn;
  sonst approve.
- **Rego-Meldungen führen die Check-ID** im Format
  `<GATE-ID>/<CHECK-ID> (<Requirement>, <Legal-Ref>): <Meldung>`.
- **Der Thesis-Stand ist unter dem Tag `thesis-v1.0` eingefroren** und muss
  reproduzierbar bleiben (Zenodo-DOI 10.5281/zenodo.19920310).
```

---

## 9. Definition of Done

- [ ] Tag `thesis-v1.0` gesetzt, CHANGELOG-Eintrag vorhanden
- [ ] Template auf `schema_version: 2`
- [ ] Alle 16 Gate-Definitionen migriert, keine Stringliste in `policy_checks` mehr
- [ ] `evidence_level.current` für alle 16 Gates gesetzt und begründet
- [ ] Orchestrator leitet `decision` nach Abschnitt 5 ab
- [ ] Integrity-Regression um die drei neuen Prüfungen erweitert, alle Checks grün
- [ ] 141 Rego-Unit-Tests weiterhin grün
- [ ] `AGENTS.md` ergänzt
