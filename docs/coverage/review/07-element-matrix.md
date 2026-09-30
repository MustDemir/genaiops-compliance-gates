---
titel: Element-Matrix – jede Pflicht mit Gate-Bezug gegen den Rego-Code
stand: 2026-09-29
basis: Branch review-2c · alle 19 Policies, 196 Regeln aus dem OPA-AST (`tools/rego_inputs.py`, Zahl = README) · 50 in-Zeilen mit Gate-Bezug
status: M2a ENTSCHIEDEN 29.09.2026 (umgesetzt für Art. 26 Abs. 5 Satz 1; alle Zeilen mit Matrix-Lauf 2) · M1a ENTSCHIEDEN 30.09.2026 (umgesetzt, Review 09 Teil 7)
---

# Kurzfazit
- **Geprüft wurde jetzt am Code, nicht an der Beschreibung.** Alle 196 Regeln der 19 Policies sind ausgewertet: Welche Input-Felder liest jede Regel, wann schlägt sie an? Dagegen stehen alle 50 Pflichten mit Gate-Bezug, Element für Element.
- **Gegenrichtung bestätigt:** Keine der 196 Regeln prüft ein Element der 28 Lücken oder einer Pflicht ohne Gate. Die Lücken stimmen.
- **Drei Korrekturen:**
  1. **Art. 14 Abs. 3 und Abs. 4 lit. d** prüft der Code *nicht* vollständig. Sie bleiben Teilabdeckung; H2 („gedeckt mit E-0“) gilt für **4 statt 6** Zeilen.
  2. **Art. 26 Abs. 5 UAbs. 1 Satz 1:** Das Feld `gate` nennt G-OPS-02. Die Elemente prüfen aber **G-OPS-01** (`real_time_monitoring`) und **G-OPS-03** (Drift-Messung).
  3. **Art. 13 Abs. 3 lit. b** (Einleitung): Fähigkeiten und Leistungsgrenzen *werden* geprüft (Felder nicht leer). Das ist mehr, als der Nachtlauf schrieb.
- **Eine Methodenfrage (M1):** 9 Teilabdeckungen haben **kein einziges geprüftes Element**, nur eine **Nachbarprüfung** – ein Gate prüft etwas Verwandtes, nicht das Element selbst.
  - Beispiel: Die Anleitung soll die Genauigkeit nennen; G-DEP-02 misst die Genauigkeit, prüft aber die Anleitung nicht.
  - Streng nach dem Raster sind das **Lücken**.
- Schon umgesetzt (dein „Ja“): E1 (G-DEP-06 → Art. 26 Abs. 6), E3 (R007-Kriterium → `gap`), H2 für die 4 geprüften Zeilen, H3 (Art. 25 lit. a/c, Art. 13 Abs. 3 lit. a → Teilabdeckung).

# Teil 1 – Die Regel

```
Element gilt als geprüft  ⇔  eine Regel schlägt an, wenn es fehlt oder falsch ist
Nachbarprüfung (≈)        =  eine Regel prüft etwas Verwandtes, nicht das Element
```

| Zeichen | Bedeutung |
|---|---|
| ✓ | geprüft – Policy und Feld genannt |
| ≈ | nur Nachbarprüfung |
| ✗ | ungeprüft |

# Teil 2 – Matrix (50 Zeilen)

Kurzformen der Felder: `trans.*` = policy_transparency_docs_present · `conf.*` = policy_conformity_verified · `ho.*` = policy_human_oversight_operational (G-OPS-01) · `gov.*` = policy_governance_approval (G-PRE-05) · `log.*` = policy_logging_configured · `inc.*` = policy_incident_process_exists / policy_incident_thresholds · `drift.*` = policy_monitoring_configured · `role.*` = policy_role_change_monitoring

| # | Einheit | heute | Elemente | nach Code |
|---|---|---|---|---|
| 1 | Art. 13 Abs. 1 | teil | ≈ `trans.instructions_for_deployers` nicht leer · ✗ Betrieb hinreichend transparent zur Interpretation | **streng: Lücke** |
| 2 | Art. 13 Abs. 2 | teil | ✓ Anleitung liegt vor (`trans.instructions_for_deployers`, `conf.provider_documentation_received`) · ✗ präzise/vollständig/korrekt/barrierefrei | teil |
| 3 | Art. 13 Abs. 3 | teil | ✓ lit. a und b teilweise · ✗ lit. c–f | teil |
| 4 | Art. 13 Abs. 3 lit. a | teil (H3) | ✓ `conf.model_info.provider`, `conf.provider_contact` · ✗ Bevollmächtigter | teil |
| 5 | Art. 13 Abs. 3 lit. b | teil | ✓ Fähigkeiten `trans.model_capabilities`, Grenzen `trans.known_limitations` · ✗ Ziff. i–vii im Einzelnen | teil |
| 6 | … Ziff. i | teil | ≈ `application.description` (G-PRE-02: Zweck vom Betreiber deklariert) · ✗ Zweckbestimmung in der Anleitung | **streng: Lücke** |
| 7 | … Ziff. ii | teil ✓PO | ≈ G-DEP-02 misst `accuracy`, `safety_score` · ✗ Maße in der Anleitung | **streng: Lücke** |
| 8 | … Ziff. iii | teil ✓PO | ≈ `trans.known_limitations` · ✗ Umstände, die zu Risiken führen | **streng: Lücke** |
| 9 | … Ziff. iv | Lücke | ✗ (G-DEP-03/C-02 design_only) | Lücke ✓ |
| 10 | … Ziff. v | teil | ≈ G-DEP-05 Bias-Kennzahlen, G-DEP-02 `subgroup_analysis` (warn) · ✗ Leistung je Gruppe in der Anleitung | **streng: Lücke** |
| 11 | … Ziff. vi | teil ✓PO | ✓ Angaben zu Trainingsdaten (`data_provenance.sources`, `collection_methods`, `preprocessing_steps`, `data_version`) · ✗ Eingabedaten-Spezifikation | teil |
| 12 | … Ziff. vii | Lücke ✓PO | ≈ `trans.instructions_for_deployers` (allgemeine Nutzungsanleitung) · ✗ Informationen zur Interpretation der Ausgabe | Lücke ✓ |
| 13 | Art. 13 Abs. 3 lit. d | teil | ≈ `gov.oversight_model`, `ho.oversight_roles` (Aufsicht beim Betreiber) · ✗ Aufsichtsmaßnahmen in der Anleitung | **streng: Lücke** |
| 14 | Art. 13 Abs. 3 lit. f | teil | ≈ `log.*` (Protokollierung beim Betreiber) · ✗ Beschreibung der Mechanismen in der Anleitung | **streng: Lücke** |
| 15 | Art. 14 Abs. 1 | teil | ✓ Eingriffsmöglichkeiten deklariert (`ho.output_override`, `ho.real_time_monitoring`) · ✗ „wirksam“ | teil |
| 16 | Art. 14 Abs. 3 | teil | ✓ Aufsichtsmodell (`gov.oversight_model`) · ≈ Freigabe (`gov.approval.approved_by`) · ✗ Angemessenheit | teil (**nicht** gedeckt) |
| 17 | Art. 14 Abs. 3 lit. b | teil | ≈ Aufsicht beim Betreiber · ✗ vom Anbieter bestimmte Vorkehrungen umgesetzt | **streng: Lücke** |
| 18 | Art. 14 Abs. 4 | teil | ✓ über lit. a, d, e | teil |
| 19 | Art. 14 Abs. 4 lit. a | teil | ✓ Überwachen (`ho.real_time_monitoring`) · ✗ Verstehen, Anomalien erkennen | teil |
| 20 | Art. 14 Abs. 4 lit. d | teil | ✓ außer Kraft setzen (`ho.output_override`) · ✗ nicht verwenden, rückgängig machen | teil (**nicht** gedeckt) |
| 21 | Art. 14 Abs. 4 lit. e | teil | ✓ Stopptaste (`gov.kill_switch`, bei Hochrisiko) · ✓ eingreifen (`ho.output_override`) · ✗ sicherer Zustand | teil |
| 22 | Art. 15 Abs. 1 | teil | ✓ Genauigkeit (G-DEP-02), Cyber-Infrastruktur (G-PRE-04, G-OPS-04) · ≈ Robustheit (`adversarial_tests`, warn) | teil (F4) |
| 23 | Art. 15 Abs. 3 | teil | ≈ G-DEP-02 misst · ✗ Metriken in der Anleitung | streng: Lücke (F4) |
| 24 | Art. 15 Abs. 4 UAbs. 1 Satz 1 | teil | ≈ `resources.limits` (G-PRE-04) · ✗ Fehlertoleranz | streng: Lücke (F4) |
| 25 | Art. 15 Abs. 4 UAbs. 1 Satz 2 | teil | ≈ Sicherheitsmaßnahmen (G-PRE-04, G-OPS-04) – für Sicherheit, nicht für Fehlertoleranz | streng: Lücke (F4) |
| 26 | Art. 15 Abs. 4 UAbs. 2 Satz 1 | n. e. | – Mittel | unverändert |
| 27 | Art. 15 Abs. 4 UAbs. 3 Satz 1 | Lücke | ✗ | Lücke ✓ |
| 28 | Art. 15 Abs. 5 | teil | ✓ vertrauliche Daten (`encryption_at_rest`, `encryption_in_transit`, `network_policies_specified`) · ≈ `adversarial_tests` (warn) · ✗ Poisoning | teil (F4) |
| 29 | Art. 25 Abs. 1 | teil | ✓ über lit. a–c · ✗ Folgepflichten Art. 16 | teil |
| 30 | Art. 25 Abs. 1 lit. a | teil (H3) | ✓ `role.*` C-25a (deny) · Kette: kein Requirement | teil (K) |
| 31 | Art. 25 Abs. 1 lit. b | teil | ✓ C-25b (warn) · Kette | teil (K) |
| 32 | Art. 25 Abs. 1 lit. c | teil (H3) | ✓ C-25c (deny, gegen die Einstufungsregel) · Kette | teil (K) |
| 33 | Art. 25 Abs. 2 | teil | ✓ C-25d Übergabe, schriftliche Vereinbarung, Kooperationszusage · Kette | teil (K) |
| 34 | Art. 26 Abs. 1 | teil | ≈ Anleitung erhalten (`conf.provider_documentation_received`), CE geprüft · ✗ Maßnahmen für die Verwendung nach der Anleitung | **streng: Lücke** |
| 35 | Art. 26 Abs. 2 | teil | ✓ Rollen (`ho.oversight_roles`), Verantwortliche (`gov.human_oversight_lead`), Eskalation (`ho.escalation_procedure`) · ✗ Kompetenz, Ausbildung | teil |
| 36 | Art. 26 Abs. 4 | Lücke | ≈ G-DEP-01 (Trainings-, nicht Eingabedaten) | Lücke ✓ |
| 37 | Art. 26 Abs. 5 UAbs. 1 Satz 1 | teil | ✓ Überwachung (`ho.real_time_monitoring`; `drift.*` misst) · ✗ Anbieter informieren | teil – **Gate-Feld falsch** |
| 38 | Art. 26 Abs. 5 UAbs. 1 Satz 2 | Lücke | ≈ `gov.kill_switch` (Stopptaste, nicht Aussetzen bei Risiko) | Lücke ✓ |
| 39 | Art. 26 Abs. 5 UAbs. 1 Satz 3 | teil | ✓ Kontakt (`inc` incident-contact), Prozess konfiguriert · ✗ Reihenfolge | teil |
| 40 | Art. 26 Abs. 5 UAbs. 1 Satz 4 | teil | ✓ Art.-73-Fristen deklariert (`inc` Fristen) · ✗ Auslöser „Anbieter nicht erreichbar“ | teil |
| 41 | Art. 26 Abs. 6 | gedeckt E-0 (H2) | ✓ aktiv, ≥ 180 Tage, zugänglich (`log.*`) | gedeckt ✓ |
| 42 | Art. 26 Abs. 7 | Lücke | ✗ (kein Feld in `trans.*`) | Lücke ✓ |
| 43 | Art. 26 Abs. 11 | teil | ✗ (`trans.ai_content_labeling` ist Art. 50) | vertagt (Q11) |
| 44 | Art. 73 Abs. 1 | teil | ✓ Vorfallprozess, Kontakt · ✗ Meldung selbst, Fallback-Bedingung | teil |
| 45 | Art. 73 Abs. 2 UAbs. 1 Satz 1 | teil | ✓ 360 h gegen das Gesetz gehalten · ✗ „unmittelbar“, Fristbeginn bei Kenntnis des Betreibers | teil |
| 46 | Art. 73 Abs. 2 UAbs. 2 Satz 1 | gedeckt E-0 (H2) | ✓ Fristen nach Schwere gestuft | gedeckt ✓ |
| 47 | Art. 73 Abs. 3 | gedeckt E-0 (H2) | ✓ 48 h | gedeckt ✓ |
| 48 | Art. 73 Abs. 4 | gedeckt E-0 (H2) | ✓ 240 h | gedeckt ✓ |
| 49 | Art. 73 Abs. 5 | n. e. | – Erlaubnis | unverändert |
| 50 | Art. 73 Abs. 9 | teil | ✓ Reduktion deklariert (`inc` deployer_context) · ✗ Bedingung: Status des **Anbieters** | teil |

**Ehrlich zur Methode:**
- Welche Felder eine Regel liest, ist **maschinell** aus dem Code gezogen.
- Wie eine Pflicht in Elemente zerfällt und ob ein Feld ein Element trifft, ist **meine Auslegung** des Wortlauts.
- Bei den Gatekeeper-Regeln (Annotationen) habe ich den Annotationsnamen aus der Meldung gelesen.
- Stichproben durch dich lohnen sich am meisten bei den ≈-Fällen.

# Teil 3 – Was die Strenge ändert

| | heute (nach H2/H3) | streng (M1a) |
|---|---|---|
| gedeckt | 4 | 4 |
| Teilabdeckung | 38 | **29** |
| Lücke | 28 | **37** |

- Neu Lücke wären: Art. 13 Abs. 1 · Ziff. i · Ziff. ii · Ziff. iii · Ziff. v · lit. d · lit. f · Art. 14 Abs. 3 lit. b · Art. 26 Abs. 1.
- Davon hast du Ziff. ii und iii in T-14.1 als Teilabdeckung bestätigt, die übrigen in 2c (F1). **Deshalb brauchen sie deinen neuen Entscheid.**
- Art. 15 (drei weitere Zeilen) folgt, sobald F4 den Anker klärt.

# Teil 4 – Entscheidungsvorlage

| # | Entscheidung | Optionen |
|---|---|---|
| **M1** | Zählt eine Nachbarprüfung als „Element geprüft“? | a) **nein – streng:** Teilabdeckung nur, wenn mindestens ein Element selbst geprüft wird; die 9 Zeilen werden Lücke, der Nachbar wird als Hinweis vermerkt · b) ja – zweckbezogen: Wer die Genauigkeit selbst misst, braucht sie nicht aus der Anleitung; die 9 bleiben Teilabdeckung |
| **M2** | Das Feld `gate` nennt nur Gates, die ein Element prüfen; Nachbarn stehen in einem eigenen Feld `nachbar_gate`. Art. 26 Abs. 5 Satz 1: G-OPS-02 → G-OPS-01, G-OPS-03 | a) ja · b) nein |

**Empfehlung M1a:**
- Die Strenge ist das Raster, das wir bisher angelegt haben: „Trifft der Katalog die Pflicht?“
- Die zweckbezogene Lesart klingt vernünftig, öffnet aber genau die Tür, gegen die das Repo gebaut ist: Ein verwandter Check „deckt“ eine Pflicht, die er nicht prüft.
- Der Nachbar geht dabei nicht verloren: Er ist oft der kürzeste Weg zur Maßnahme. Beispiel Ziff. ii: M-A1 kann die Genauigkeit aus der Anleitung gegen die Messung aus G-DEP-02 halten (E-2).

# Teil 5 – Entscheid und Folgen (29.09.2026)

**M2a entschieden:**
- `gate` nennt nur Gates, deren Regel ein Element prüft; Nachbarn stehen in `nachbar_gate`. Festgehalten in SPEC-06 5.1 und T-13.
- Umgesetzt für Art. 26 Abs. 5 UAbs. 1 Satz 1: `gate` G-OPS-02 → G-OPS-01, G-OPS-03 (`docs/coverage/entscheide/2026-09-29_element-matrix.yaml`).
  - G-OPS-02 ist kein Nachbar: Die Regel prüft den eigenen Meldekontakt des Betreibers (`genaiops.io/incident-contact`), nicht den Weg zum Anbieter.
- **Alle übrigen Zeilen folgen mit Matrix-Lauf 2 (Plan Teil C, Paket 3).** Dort wird `gate` aus den Matrix-Daten abgeleitet statt von Hand gesetzt. Bis dahin kann `gate` noch Nachbarn enthalten (die ≈-Fälle in Teil 2).
- Dabei zu klären: Bei Lücken nennt `gate` heute oft das Gate, in das ein Check **gehören würde** (z. B. Art. 26 Abs. 7 → G-DEP-03). Das ist weder Prüfer noch Nachbar, sondern ein Ziel. Es gehört in die Maßnahme der Bedarfsanalyse (Paket 5), nicht in `gate`.

**M1 offen:** Paket 4 (PO-Runde), zusammen mit den Anhängen, damit die Regel für alle Zeilen auf einmal gilt.

**Zwei neue Befunde beim Umsetzen:**

| # | Befund | Wohin |
|---|---|---|
| M-B1 | Art. 26 Abs. 5 UAbs. 1 Satz 1 trägt `requirement` R009 (Vorfallprozess, gehört zu G-OPS-02). Die prüfenden Gates hängen an R008 (G-OPS-01) und R010 (G-OPS-03). Welches Requirement die Pflicht trägt, entscheidet der PO. | Paket 5, zusammen mit F3 (Anker R010) |
| M-B2 | 14 Satz-Einheiten tragen noch den `pflicht`-Text des ganzen Absatzes, geerbt beim Schnitt auf Satzebene (T-14.3): Art. 15 Abs. 4 (4), Art. 26 Abs. 5 (6), Art. 73 Abs. 2 (2), Art. 111 Abs. 2 (2). Der Beleg ist richtig geschnitten, die Aussage nicht. | Paket 3: je Satz eine eigene Pflicht formulieren, PO bestätigt |

