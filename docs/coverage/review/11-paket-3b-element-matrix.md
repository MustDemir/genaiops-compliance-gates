---
titel: Paket 3b – Element-Matrix Lauf 2 als Daten, gate daraus abgeleitet
stand: 2026-10-01
basis: Branch review-2c · PO-Entscheide M2a (29.09.2026) und M1a (30.09.2026) · Review 07 (Lauf 1) · Befund P2-B1 (Review 09) · alle 19 Policies, 196 Regeln aus dem OPA-AST
status: geliefert · PO 01.10.2026: P3-F4 b, R-6 HIGH (Teil 8) · P3-F3 offen · Befunde A-W13, P3-B1
---

# Kurzfazit

- **Die Matrix ist jetzt Daten:** `docs/coverage/matrix/element_matrix.yaml` – 54 Zeilen, 92 Elemente, 97 Regelangaben (Gate, Check, gelesenes Feld).
- **Jede Regelangabe ist am Code bestätigt.** Der Wächter hält sie gegen den OPA-AST: Liest die Regel das Feld nicht mehr, wird `make verify` rot.
- **`gate` und `nachbar_gate` sind abgeleitet, nicht mehr gesetzt** (M2a für alle Zeilen). 21 Zeilen berichtigt – 19 in, 2 out.
- **P2-B1 (zuerst):** Art. 25 Abs. 2 lit. a–c n.F. werden **Lücke** (Vorschlag, Frage P3-F3). C-25d verlangt den Übergabebeleg, sieht aber nicht hinein.
- **Art. 26 Abs. 11:** vorgeschlagen war Lücke (Frage P3-F4). **PO: Vorbehalt bis Q11** – die Zeile bleibt Teilabdeckung, der Wächter meldet, dass sie abgeleitet Lücke wäre (Teil 8).
- **Neuer Wächter `ELEMENT_MATRIX_DERIVES_GATE`** – **HIGH** (PO R-6).
- **Werkzeug:** `tools/rego_inputs.py` liest jetzt durch Aliase, `object.get`, Schleifen und Annotationen. Regeln ohne erkanntes Feld: **24 → 0**.
- Zwei Befunde nebenbei: **A-W13** (19 Pflichttexte tragen noch den abgeschnittenen Unterabsatz) und **P3-B1** (Art. 73 Abs. 2 und Abs. 3/4 ungleich zerlegt).

**Zählung danach** (gemessen 30.09.2026):

| Raum | in | Lücke | Teil | n. e. | gedeckt |
|---|---|---|---|---|---|
| AI Act | 85 | 35 → **36** | 28 → **27** | 18 | 4 |
| Omnibus | 24 | 4 → **7** | 4 → **1** | 16 | – |
| **zusammen** | 109 | 39 → **43** | 32 → **28** | 34 | 4 |

- in bestätigt: 64 von 109 (unverändert) · out bestätigt: 139 von 1407 (unverändert).
- **Nach den Entscheiden vom 01.10.2026:** Art. 26 Abs. 11 bleibt Teilabdeckung → AI Act Lücke **35**, Teil **28**; zusammen Lücke **42**, Teil **29**.

# Teil 1 – Das Modell

```
docs/coverage/matrix/element_matrix.yaml         OPA-AST (tools/rego_inputs.py)
  Zeile → Elemente → Regel (Gate, Check, Feld)  ─── liest die Regel das Feld? ───┐
          status: geprueft | nachbar | ungeprueft                                  │
                │                                                                  │
                ▼  abgeleitet (M2a, M1a)                                           │
  gate          = Gates der geprüften Elemente                                     │
  nachbar_gate  = Gates der Nachbar-Elemente (ohne die in gate)                    │
  Befundklasse  = kein Element geprüft  → Lücke                                    │
                  alle geprüft + Requirement trägt die Pflicht → gedeckt           │
                  sonst → Teilabdeckung                                            │
                ▼                                                                  │
  Pflichtenraum (aiact, omnibus)  ◄── ELEMENT_MATRIX_DERIVES_GATE (HIGH) ──────────┘
```

- **Drei Richtungen hält der Wächter:**
  1. Matrix → Code: Gate und Check gibt es, der Check ist `implemented`, eine Regel liest das Feld.
  2. Matrix → Pflichtenraum: `gate`, `nachbar_gate` und Befundklasse stimmen.
  3. Pflichtenraum → Matrix: Eine Zeile ohne Eintrag trägt kein Gate und ist weder gedeckt noch Teilabdeckung. Eine `out`-Zeile trägt gar kein Gate.
- **Behälter = Nachbar.** Verlangt eine Regel nur den Beleg, in dem das Element stehen soll, prüft sie das Element nicht. Vorbild: Art. 13 Abs. 3 lit. b Ziff. vii (Lücke, vom PO bestätigt, M1a).
- **Kette:** „alle Elemente geprüft“ reicht für „gedeckt“ nur, wenn ein Requirement die Pflicht trägt. Sonst Teilabdeckung (H3a) – das trifft die Art.-25-Zeilen bis R017.
- **Ziele fallen weg.** `gate` nannte bei Lücken oft das Gate, in das ein Check gehören würde (Review 07 Teil 5). Das Ziel steht in der Maßnahme (Review 04), nicht in `gate`.
- **Vorbehalt:** Art. 15 Abs. 3, Abs. 4 UAbs. 1 Satz 1 und 2 bleiben, wie sie sind, bis F4 den Anker klärt (M1-Entscheid). Abgeleitet wären sie Lücke; der Wächter meldet das bei jedem Lauf. Steht F4 im Register nicht mehr offen, wird er rot.

# Teil 2 – Zuerst: P2-B1 und die neuen in-Zeilen aus T-15

**Art. 25 Abs. 2 n.F. – was C-25d wirklich liest** (OPA-AST):

```
change_event.evidence.cooperation_commitment_ref  ← C-25d: fehlt → deny     ✓ Zusammenarbeit zugesagt
change_event.evidence.provider_handover_record    ← C-25d: fehlt → deny     ✓ Übergabe liegt vor
   ├─ lit. a technische Unterlagen (Art. 16)        keine Regel sieht hinein  ≈
   ├─ lit. b Einschränkungen, Fehlerarten           keine Regel sieht hinein  ≈
   └─ lit. c gezielter technischer Zugang           keine Regel sieht hinein  ≈
change_event.evidence.initial_provider_exclusion_ref ← C-25d: Ausnahme belegt  ✓ UAbs. 4
```

| Zeile | vorher | jetzt | warum |
|---|---|---|---|
| Art. 25 Abs. 2 n.F. | Teil, G-OPS-06 | Teil, G-OPS-06 (unverändert) | Zusage und Übergabe geprüft; Zugang und Unterstützung nicht; Kette offen (R017) |
| … lit. a n.F. | Teil, G-OPS-06 | **Lücke**, Nachbar G-OPS-06 | Behälter – ob der Beleg die Unterlagen enthält, prüft keine Regel |
| … lit. b n.F. | Teil, G-OPS-06 | **Lücke**, Nachbar G-OPS-06 | dito, Einschränkungen und Fehlerarten |
| … lit. c n.F. | Teil, G-OPS-06 | **Lücke**, Nachbar G-OPS-06 | dito, technischer Zugang |
| … UAbs. 4 n.F. | n. e., G-OPS-06 | n. e., G-OPS-06 (am Code bestätigt) | C-25d liest `initial_provider_exclusion_ref`; eine bloße Behauptung genügt nicht |

- **Kürzester Weg zur Maßnahme:** C-25d liest je Element ein Feld des Übergabebelegs. Dann sind lit. a–c geprüft (E-0). MUST/SHOULD und Beweisstufe entscheidest du in Paket 5 (EF).
- **Art. 6 Abs. 3 UAbs. 3** (T-15, in, steuernd, n. e.): kein Gate-Bezug, keine Matrix-Zeile nötig. Der Wächter hält, dass sie kein Gate trägt.

# Teil 3 – Was die Ableitung an `gate` ändert

Alle übrigen Änderungen setzen M2a um (entschieden 29.09.2026). Der Befund ändert sich dabei nicht.

| Zeile | gate vorher | gate jetzt | nachbar_gate jetzt | Grund |
|---|---|---|---|---|
| Art. 13 Abs. 2 | G-DEP-03 | G-DEP-03, **G-DEP-04** | – | `provider_documentation_received`: Anleitung liegt vor (Review 07 Z. 2) |
| Art. 13 Abs. 3 | G-DEP-03 | G-DEP-03, **G-DEP-04** | – | lit. a über G-DEP-04 (Z. 3) |
| Art. 13 Abs. 3 lit. b Ziff. iv | G-DEP-03, G-DEP-02 | – | – | einziger passender Check C-02 ist `design_only` (Z. 9) |
| Art. 13 Abs. 3 lit. b Ziff. vii | G-DEP-05 | – | **G-DEP-03** | G-DEP-05 prüft Bias, nichts an Ziff. vii; Anleitung ist Behälter (Z. 12) |
| Art. 14 Abs. 4 | G-OPS-01 | G-OPS-01, **G-PRE-05** | – | lit. e über `kill_switch` (Z. 18) |
| Art. 14 Abs. 4 lit. e | G-PRE-05 | G-PRE-05, **G-OPS-01** | – | „eingreifen“ über `output_override` (Z. 21) |
| Art. 15 Abs. 1 | unverändert | unverändert | **G-OPS-03** | Drift ≈ „beständig während des Lebenszyklus“ (neu) |
| Art. 15 Abs. 4 UAbs. 2 Satz 1 | G-DEP-02, G-OPS-04 | – | – | Mittel, keine Pflicht; keine Regel prüft Redundanz |
| Art. 15 Abs. 4 UAbs. 3 Satz 1 | G-DEP-02, G-OPS-04 | – | **G-OPS-03** | Drift allgemein, nicht Rückkopplung (M-C1) |
| Art. 15 Abs. 5 | unverändert | unverändert | **G-DEP-02** | `adversarial_tests` ist nur ein SHOULD-Flag (Z. 28) |
| Art. 26 Abs. 2 | G-OPS-01, G-PRE-01 | G-OPS-01, **G-PRE-05** | **G-PRE-01** | `human_oversight_lead` überträgt die Aufsicht; C-A7 prüft nur einen Wirksamkeitsnachweis in der Art.-6-Einstufung (Z. 35) |
| Art. 26 Abs. 4 | G-DEP-01 | – | **G-DEP-01** | Trainings-, nicht Eingabedaten (Z. 36) |
| Art. 26 Abs. 5 UAbs. 1 Satz 2 | G-OPS-02 | – | **G-PRE-05** | Stopptaste dokumentiert, Aussetzen bei Risiko ist keine Regel (Z. 38) |
| Art. 26 Abs. 5 UAbs. 1 Satz 5 (out) | G-OPS-02 | – | – | `out`-Zeile trägt kein Gate |
| Art. 26 Abs. 5 UAbs. 2 Satz 1 (out) | G-OPS-02 | – | – | dito |
| Art. 26 Abs. 7 | G-DEP-03 | – | – | Ziel, kein Prüfer (Z. 42, M-E6) |
| Art. 26 Abs. 11 | G-DEP-03 | G-DEP-03 (Vorbehalt Q11) | – | vorgeschlagen Lücke; PO P3-F4 b: bleibt bis Q11 (Teil 8) |
| Art. 73 Abs. 5 | G-OPS-02 | – | – | Erlaubnis, keine Regel (Z. 49) |
| Art. 25 Abs. 2 lit. a–c n.F. | G-OPS-06 | – | **G-OPS-06** | Teil 2 |

- **Unverändert bestätigt am Code:** Art. 26 Abs. 5 UAbs. 1 Satz 1 (G-OPS-01, G-OPS-03 – dein M2a-Entscheid), die neun M1a-Zeilen, die vier gedeckten Zeilen, alle Art.-25-Abs.-1-Zeilen.
- **Gleiche Reihenfolge wie vorher:** Was bleibt, behält seinen Platz in der Liste; Neues kommt dahinter. So bleiben deine Entscheidungsdateien gleich (`PO_DECISIONS_APPLIED`: 0 Abweichungen).

# Teil 4 – Art. 26 Abs. 11

- Die Zeile war Teilabdeckung mit G-DEP-03. Die einzige verwandte Regel verlangt `ai_content_labeling` – das ist Art. 50.
- Abs. 11 nimmt Art. 50 ausdrücklich aus („Unbeschadet des Artikels 50“). Die Unterrichtung der betroffenen Personen prüft keine Regel.
- Nach M1a ist das eine Lücke – unabhängig davon, ob Abs. 11 für Redispatch gilt (Q11). Q11 entscheidet in/out, nicht die Deckung.

```
Q11 offen:  gilt Abs. 11?  ── ja ──► in,  Lücke (Unterrichtung fehlt)
                           └─ nein ─► out
            heute: in, Teilabdeckung  ← stützt sich auf Art. 50, den Abs. 11 ausnimmt
```

# Teil 5 – Werkzeug: `rego_inputs.py` Lauf 2

| | Lauf 1 (Review 07) | Lauf 2 |
|---|---|---|
| Regeln | 196 | 196 |
| Regeln ohne erkanntes Feld | 24 | **0** |
| G-OPS-06 (`_ce := input.change_event`) | alle Regeln: `change_event` | je Regel das Feld, z. B. `change_event.evidence.provider_handover_record` |
| G-OPS-02/C-02–C-04 (`object.get(_doc, …)`) | leer | `thresholds[].status`, `deadlines[].hours` … |
| Gatekeeper-Annotationen | `review.object` | `…annotations[genaiops.io/incident-contact]` |
| G-PRE-04 (`some c in _containers`) | leer | `…containers[].securityContext.runAsNonRoot` … |

- Lauf 1 hätte P2-B1 gar nicht beantworten können: Er sah bei G-OPS-06 nur `change_event`, nicht welches Feld welche Regel liest.
- Die Zuordnung Regel → Check nimmt die Check-ID aus der Meldung. Fehlt sie (131 von 196 Meldungen, gemessen; E2, Paket 5), gilt jeder Check des Gates mit derselben Policy.

# Teil 6 – Gegenprobe des Wächters

Gegen den committeten Stand, je eine Richtung gebrochen, danach zurückgenommen – grün.

| # | gebrochen | Meldung (`ELEMENT_MATRIX_DERIVES_GATE`, HIGH) |
|---|---|---|
| G1 | Matrix nennt ein Feld, das C-25d nicht liest | keine Regel von G-OPS-06/C-25d liest `…provider_handover_record.technical_documentation` (OPA-AST) |
| G2 | Rego: C-25d liest `cooperation_commitment_ref` nicht mehr | keine Regel von G-OPS-06/C-25d liest `change_event.evidence.cooperation_commitment_ref` |
| G3 | Ziff. iv als geprüft über G-DEP-03/C-02 | G-DEP-03/C-02 ist design_only, ohne Regel ist er weder Prüfer noch Nachbar |
| G4 | Art. 26 Abs. 7 trägt wieder G-DEP-03 | gate ist [G-DEP-03], abgeleitet [] |
| G5 | lit. a n.F. zurück auf Teilabdeckung | befund ist 'teilabdeckung', nach den Elementen 'luecke' (M1a) |
| G6 | Art. 5 Abs. 1 lit. a (ohne Matrix-Zeile) bekommt G-PRE-02 | trägt gate ohne Eintrag in der Element-Matrix |
| G7 | Vorbehalt auf eine erledigte Frage (M2 statt F4) | Vorbehalt 'M2' steht im Register nicht offen |
| G8 | `opa` nicht auf PATH | die Element-Matrix kann nicht gegen den Rego-Code gehalten werden |

# Teil 7 – Fragen und Befunde

**a ist jeweils die Empfehlung.**

| # | Frage | Optionen |
|---|---|---|
| **P3-F3** | P2-B1: Art. 25 Abs. 2 lit. a–c n.F. – zählt der Übergabebeleg als Prüfung der Elemente? | a) **nein – Lücke:** Behälter = Nachbar, wie Ziff. vii (M1a) · b) ja – Teilabdeckung: der Beleg liegt vor, sein Inhalt ist Beweisfrage |
| **P3-F4** | Art. 26 Abs. 11: Lücke jetzt oder Vorbehalt bis Q11? | a) **Lücke jetzt** – keine Regel prüft die Unterrichtung; Q11 entscheidet nur in/out · b) Vorbehalt Q11, Zeile bleibt Teilabdeckung |
| **R-6** | Severity des Wächters `ELEMENT_MATRIX_DERIVES_GATE` | a) **HIGH** wie R-3 – ein Gate in `gate`, das kein Element prüft, macht aus einer Lücke eine scheinbare Prüfung · b) MEDIUM |

| # | Befund | Wohin |
|---|---|---|
| A-W13 | **Pflichttexte hinter Aufzählungen:** T-15 Teil 2 (A-W11) hat 19 Unterabsätze aus dem letzten Buchstaben geschnitten, aber dessen `pflicht` nicht nachgezogen – M-B2 galt nur für Sätze. Der Text nennt noch den abgeschnittenen Unterabsatz. AI Act 12 (Art. 5 Abs. 1 lit. h Ziff. iii, 5 Abs. 2 lit. b, 22 Abs. 3 lit. e, 36 Abs. 9 lit. b, 41 Abs. 1 lit. b, 43 Abs. 1 UAbs. 1 lit. b, 43 Abs. 1 UAbs. 2 lit. d, 49 Abs. 4 lit. d, 68 Abs. 2 lit. c, 96 Abs. 1 lit. f, 101 Abs. 1 lit. d, Anhang XI Abschn. 1 Nr. 2 lit. e), Omnibus 7 (Art. 2 Abs. 13 lit. b, 4a Abs. 2 lit. b, 25 Abs. 2 lit. c, 75 Abs. 2a lit. c, 75b lit. c, 75c Abs. 4 lit. c, 75c Abs. 5 lit. g). Zwei sind `in`: Art. 25 Abs. 2 lit. c n.F. und Art. 4a Abs. 2 lit. b n.F. | Paket 3, Nacharbeit T-15: Texte neu, Wächter (wörtlicher Rest maschinell prüfbar: 7 der 19), Bestätigung wie P3-F2 |
| P3-B1 | **Art. 73 ungleich zerlegt:** Abs. 2 UAbs. 1 Satz 1 ist Teilabdeckung, weil „unmittelbar“ und der Fristbeginn bei Kenntnis des Betreibers ungeprüft sind. Abs. 3 und 4 haben denselben Aufbau („unverzüglich, spätestens … nachdem der Anbieter oder gegebenenfalls der Betreiber Kenntnis erlangt hat“) und sind gedeckt (H2a). Die Matrix bildet beides ab, wie entschieden. Empfehlung: Abs. 3 und 4 wie Abs. 2 zerlegen (strenger, Teilabdeckung); der Fristbeginn ist Inhalt, nicht Beweis. | Paket 4, zusammen mit M-F1/M-F3 |

**Ehrlich zur Methode:**
- **Maschinell:** welches Feld welche Regel liest, und dass jede Matrix-Angabe darauf passt.
- **Auslegung:** wie eine Pflicht in Elemente zerfällt, ob ein Feld ein Element trifft oder nur daneben liegt. Grundlage ist Lauf 1, den du gesehen hast; neu beurteilt sind nur die Art.-25-Abs.-2-n.F.-Zeilen, Art. 26 Abs. 11 und zwei Drift-Nachbarn bei Art. 15.
- **Nicht maschinell:** die Rückrichtung „keine Regel prüft ein Element einer Lücke ohne Gate“. Review 07 hat sie einmal von Hand geprüft; der Wächter hält nur Zeilen mit Gate-Bezug.

**Nicht geliefert, und warum:**
- **Art. 15 Abs. 3, Abs. 4 UAbs. 1 Satz 1 und 2:** unter Vorbehalt F4, wie im M1-Entscheid festgelegt.
- **A-W13:** eigener Fehlerklasse, 17 von 19 Zeilen `out`. Gehört mit Wächter und deiner Bestätigung in einen eigenen Commit, nicht in die Matrix.
- **Ziel-Gates** als eigenes Feld: nicht angelegt. Die Maßnahmen aus Review 04 nennen das Ziel bereits.

# Teil 8 – Entscheide des PO (01.10.2026)

| Frage | Entscheid | Umsetzung |
|---|---|---|
| P3-F3 | **offen** – b gewählt und am selben Tag zurückgenommen: der PO sieht sich den Fall genauer an | bis dahin gilt der Vorschlag: lit. a–c n.F. Lücke, Nachbar G-OPS-06, nicht bestätigt |
| P3-F4 | **b – Vorbehalt Q11** (vorgeschlagen war a) | Art. 26 Abs. 11 bleibt Teilabdeckung mit G-DEP-03; Matrix-Zeile mit `vorbehalt: Q11`; Entscheidungsdatei `2026-10-01_paket-3b.yaml` (nicht bestätigt – vertagt, nicht eingeordnet) |
| R-6 | **a – HIGH** | `ELEMENT_MATRIX_DERIVES_GATE` war schon HIGH, Docstring nennt den Entscheid |

```
Art. 26 Abs. 11   heute:     in, Teilabdeckung, gate G-DEP-03
                  Matrix:    Vorbehalt Q11 → bei jedem Lauf: "abgeleitet Lücke"
                  Q11 nein → out          Q11 ja → Vorbehalt fällt, Lücke (Wächter erzwingt es)
```

- **Der Vorbehalt läuft nicht still ab:** Steht Q11 im Register nicht mehr offen, wird der Wächter rot, bis die Zeile abgeleitet ist.
- **Zu P3-F3, zum Nachsehen:** Der Unterschied zwischen a und b ist genau eine Frage – zählt „der Beleg liegt vor“ als Prüfung dessen, was drinstehen muss?
  - Für b spricht: Der Übergabebeleg hat keinen anderen Zweck als lit. a–c; die Meldung von C-25d nennt alle drei.
  - Für a spricht: Ein Beleg mit nur lit. b lässt C-25d grün; Ziff. vii (Anleitung ist da, Inhalt ungeprüft) hast du als Lücke bestätigt.
  - Wählst du b, gehört die Abgrenzung zu Ziff. vii mit in den Entscheid („Beleg mit einzigem Zweck“ vs. „Dokument mit vielen Inhalten“), sonst ist die Regel nicht mehr eine.
