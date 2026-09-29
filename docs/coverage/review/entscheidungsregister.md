---
titel: Entscheidungsregister – was der PO noch entscheiden muss und welche Schritte ausstehen
stand: 2026-09-29 (nach Paket 2)
basis: Reviews 00–09, Entscheidungsdateien in docs/coverage/entscheide/, Plan Teil C
status: lebendes Register · der Wächter PO_DECISIONS_REGISTERED hält es vollständig
---

# Wozu

- **Eine Stelle für alles, was offen ist:** jede Entscheidung des PO und jeder beschlossene Schritt, der noch nicht umgesetzt ist, mit Ziel-Paket aus dem Plan (00 Teil C).
- **Vollständig durch einen Wächter, nicht durch Sorgfalt.** `PO_DECISIONS_REGISTERED` liest jede Entscheidungs- und Befundtabelle der Reviews (`| # | Entscheidung | …`, `| # | Frage | Optionen |`, `| # | Befund | Wohin |`). Jede Zeile dort muss hier stehen. Jeder offene Punkt hier braucht ein Paket.
- **Stand** ist eins von: `offen` · `vertagt` · `entschieden` (Umsetzung steht aus, wenn ein Paket genannt ist) · `umgesetzt` · `außerhalb` (nicht in diesem Repo).
- **Paket:** 1–9 aus Plan Teil C · `T-13` Sektorstapel · `jederzeit` · `–`.

```
Pakete:  1 Anhänge ✅ · 2 Omnibus · 3 Befunde + Matrix · 4 PO-Runde · 5 Bedarfsanalyse
         6 Bauen · 7 known_limits + Wächter · 8 PR · 9 Prüf-Agent
```

# Teil 1 – Offen: deine Entscheide

| ID | Gegenstand | Quelle | Stand | Paket |
|---|---|---|---|---|
| S3-1 | Art. 111 Abs. 2 Satz 2: Betreiber als Behörde, ggf. dritte Bedingung im P0-Check | `00-systembild-und-plan.md` | vertagt | 4 |
| S3-2 | Unterglieder entschiedener Normen: Art. 3 Nr. 49 lit. a–d, Art. 4a Abs. 2 lit. a/b n.F., Art. 113 Abs. 3 lit. c Ziff. ii n.F. | `00-systembild-und-plan.md` | vertagt | 4 |
| S3-3 | Verifikationsstufe der Zeilen ohne Stufe (12 AI Act, 10 Omnibus) | `00-systembild-und-plan.md` | vertagt | 4 |
| S3-4 | Hypothesen gegen Sekundärquellen prüfen (43 in-Zeilen, dazu 4 aus Paket 1) | `00-systembild-und-plan.md` | vertagt | 4 |
| Q1 | FRIA: R012, G-PRE-02 und G-PRE-05/C-01 verlangen eine Folgenabschätzung als MUST, Art. 27 nimmt Anhang III Nr. 2 aber aus | `05-schritt-2d-2e-gedeckt-querbefunde.md` | vertagt | 4 |
| Q11 | Art. 26 Abs. 11 (Information der betroffenen Personen) | `05-schritt-2d-2e-gedeckt-querbefunde.md` | vertagt | 4 |
| M1 | Zählt eine Nachbarprüfung als geprüftes Element? 9 Zeilen, Empfehlung a (streng: werden Lücke) | `07-element-matrix.md` | offen | 4 |
| A-F1 | Anhang IV nennt den Betreiber: Durchschlag? Empfehlung a (nein, out) | `08-paket-1-anhaenge.md` | offen | 4 |
| IN-1 | Alle `in`-Zeilen bestätigen (nach Paket 2 und P2-F2: 64 von 104 bestätigt – AI Act 61 von 83, Omnibus 3 von 21) | `entscheidungsregister.md` | offen | 4 |
| OUT-1 | `out`-Zeilen: Stichprobe nach Adressat-Gruppen, dann Sammelbestätigung (nach Paket 2 und P2-F1/F4/F5: 138 von 1368 bestätigt – AI Act 31 von 1120, Omnibus 107 von 248) | `entscheidungsregister.md` | offen | 4 |
| R-1 | Severity des Wächters `PO_DECISIONS_REGISTERED` (Vorschlag LOW: bricht `make verify`, wie `HANDBOOK_ROADMAP_CURRENT`) | `entscheidungsregister.md` | offen | 4 |
| M-B1 | Welches Requirement trägt Art. 26 Abs. 5 Satz 1: R009 wie heute oder R008/R010 der prüfenden Gates? | `07-element-matrix.md` | offen | 5 |
| EF | Die vier Ehrlichkeitsfelder je neuem oder geändertem Requirement und Check: Norm↔Pflicht, MUST/SHOULD, `evidence_level`, `implemented`/`design_only` (AGENTS.md 3) | `entscheidungsregister.md` | offen | 5 |
| P9-1 | Use Cases des Prüf-Agenten | `00-systembild-und-plan.md` | offen | 9 |
| P9-2 | Einordnung des Agenten selbst nach AI Act (HYPOTHESE: kein Hochrisiko; Art. 4, ggf. Art. 50) | `00-systembild-und-plan.md` | offen | 9 |
| P9-3 | Architektur des Agenten | `00-systembild-und-plan.md` | offen | 9 |
| PUSH-1 | Branch `review-2c` pushen (liegt lokal und auf dem Mac, nicht auf origin) | `entscheidungsregister.md` | offen | jederzeit |
| PUSH-2 | Commit 47c9833 auf `claude/scrum-solo-developer-6xyy9k` pushen (Whitepaper-PDFs in `.gitignore`) | `entscheidungsregister.md` | offen | jederzeit |
| WP-1 | Benennung des Whitepapers; Änderungen liegen in `stash@{0}` | `entscheidungsregister.md` | offen | jederzeit |

# Teil 2 – Entschieden, Umsetzung steht aus

| ID | Gegenstand | Quelle | Stand | Paket |
|---|---|---|---|---|
| M2 | `gate` nennt nur elementprüfende Gates, Nachbarn in `nachbar_gate`; umgesetzt für Art. 26 Abs. 5 Satz 1, alle übrigen Zeilen mit Matrix-Lauf 2 | `07-element-matrix.md` | entschieden 29.09.2026 a | 3 |
| E2 | 24 Lücken in den Paketen P0–P8 mit Prioritäten | `02-schritt-2b-luecken.md` | entschieden 23.09.2026 | 5 |
| E3 | R015 (Art. 5 Verbote) und R016 (Art. 4 KI-Kompetenz); Artikel und MUST/SHOULD je Requirement | `02-schritt-2b-luecken.md` | entschieden 23.09.2026 | 5 |
| F1 | Cluster und Maßnahmen aus 2c als Grundlage der Bedarfsanalyse | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 5 |
| F3 | Anker korrigieren: R006 ohne Art. 10, R007 ohne Art. 50, R010 + Art. 26 Abs. 5 Satz 1, R013 + Art. 26 Abs. 5 Satz 3 | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 5 |
| F5 | G-OPS-02 umbauen: Art.-73-Fristen nur als Auffangregel, Reduktion nach Abs. 9 am Status des Anbieters. Zwischenschritt „Vermerk HYPOTHESE im Gate“ am 29.09.2026 nachgeholt | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 5 |
| F6 | Neues Requirement R017 Rollenwechsel (Art. 25), MUST/SHOULD in Paket 5 | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 5 |
| E2 | Rego-Meldungen mit Check-ID (130 von 195 ohne), Wächter `REGO_MESSAGES_CARRY_CHECK_ID` im selben Commit | `05-schritt-2d-2e-gedeckt-querbefunde.md` | entschieden 29.09.2026 a | 5 |
| P2-F4 | Art. 4a Abs. 1 lit. a–f bleiben out (bedingte Pflicht); Wiedervorlage maschinell: Manifest-Feld `special_categories_for_bias` + Check, der die Zeilen meldet, sobald `true` (Bedingungsparameter je Anwendungsfall, wie SPEC-03) | `09-paket-2-omnibus.md` | entschieden 29.09.2026 c | 5 |
| E7 | Meldekaskade: planen ja, bauen erst in der Umsetzung | `02-schritt-2b-luecken.md` | entschieden 23.09.2026 | 6 |
| F4 | R001, R002, R003, R005, R011 ohne Betreiber-Anker: `anker: offen`, Anker-Suche im Sektorstapel. Zwischenschritt `anker: offen` am 29.09.2026 nachgeholt. **Folge aus Teil C:** Der Sektorstapel kommt nach dem Agenten, der Anker bleibt so lange offen, und der Agent muss „Anker offen“ melden | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 7 |
| H4 | `known_limits` je Gate, Hinweis in jedem Lauf, Urteil unverändert, Wächter `GATE_LIMITS_DECLARED` | `06-grenzen-statt-teilabdeckung.md` | entschieden 29.09.2026 Option 1 | 7 |

# Teil 3 – Befunde mit Ziel-Paket

| ID | Gegenstand | Quelle | Stand | Paket |
|---|---|---|---|---|
| A-W1 | Art. 113: Kennungen weichen von der amtlichen Zitierweise ab („Abs. 3 lit. a“). Aus Paket 2 verschoben: Extraktor-Umbau über alle Räume, eigenes Werkzeug-Ticket mit M-B2, A-W7 | `08-paket-1-anhaenge.md` | offen | 3 |
| A-W2 | Anhang I Abschn. B: Nr. 13–20 in einer Einheit (Werkzeug-Ticket wie A-W1) | `08-paket-1-anhaenge.md` | offen | 3 |
| A-W3 | Anhang XIII lit. g: Fußzeile der Quelldatei im Beleg (Werkzeug-Ticket wie A-W1) | `08-paket-1-anhaenge.md` | offen | 3 |
| M-B2 | 14 Satz-Einheiten tragen den Pflichttext des ganzen Absatzes | `07-element-matrix.md` | offen | 3 |
| A-W7 | Omnibus-Extraktor: Einheiten mit zwei Stellen (Art. 5 Abs. 1b in Abs. 1a lit. b, Art. 75b, Folgesätze am letzten Buchstaben) | `09-paket-2-omnibus.md` | offen | 3 |
| P2-B1 | Art. 25 Abs. 2 lit. a–c n.F.: Teilabdeckung vorläufig, C-25d prüft den Übergabebeleg nicht je Element | `09-paket-2-omnibus.md` | offen | 3 |
| AN-1 | Wächter Requirement-Anker ↔ Pflichtenraum: ein Requirement, dessen Normverweise nur auf `out`-Einheiten zeigen, muss `anker: offen` tragen. Gemessen am 29.09.2026: R002 (markiert), dazu R010 (F3) und R012 (Q1) ohne `in`-Anker. Kommt mit F3/F4 | `entscheidungsregister.md` | offen | 5 |
| MX-1 | Element-Matrix als Daten, `gate` daraus abgeleitet, Wächter in `make verify` | `entscheidungsregister.md` | offen | 7 |
| W-1 | Wiedervorlage Anhang XI/XII (GPAI) beim Prüf-Agenten selbst | `entscheidungsregister.md` | offen | 9 |
| W-2 | Wiedervorlage Anhang IX, sobald der Betreiber an einem Test unter Realbedingungen teilnimmt | `entscheidungsregister.md` | offen | jederzeit |

# Teil 4 – Erledigt

| ID | Gegenstand | Quelle | Stand | Paket |
|---|---|---|---|---|
| E1 | 7 Zeilen umklassifiziert | `02-schritt-2b-luecken.md` | umgesetzt | – |
| E4 | Durchschlagsregel als Sammelentscheid | `02-schritt-2b-luecken.md` | umgesetzt | – |
| E5 | Steuernde Normen `in` / `nicht_einschlaegig` | `02-schritt-2b-luecken.md` | umgesetzt | – |
| E6 | Omnibus-Korrekturen in den Pflichtenraum (T-14.2) | `02-schritt-2b-luecken.md` | umgesetzt | – |
| E8 | T-14 vor 2c und vor dem Anhänge-Lauf | `02-schritt-2b-luecken.md` | umgesetzt | – |
| F2 | Fünf Zeilen umklassifiziert | `04-schritt-2c-teilabdeckungen.md` | umgesetzt | – |
| D1 | Art. 25 Abs. 1 lit. a, c → Teilabdeckung (aufgegangen in H3) | `05-schritt-2d-2e-gedeckt-querbefunde.md` | umgesetzt | – |
| D2 | Art. 13 Abs. 3 lit. a → Teilabdeckung (aufgegangen in H3) | `05-schritt-2d-2e-gedeckt-querbefunde.md` | umgesetzt | – |
| E1 | G-DEP-06 zitiert Art. 26 Abs. 6 | `05-schritt-2d-2e-gedeckt-querbefunde.md` | umgesetzt | – |
| E3 | R007-Kriterium Art. 26 Abs. 7 auf `gap` | `05-schritt-2d-2e-gedeckt-querbefunde.md` | umgesetzt | – |
| H1 | Name `teilabdeckung` bleibt (Option b) | `06-grenzen-statt-teilabdeckung.md` | umgesetzt | – |
| H2 | 4 Zeilen gedeckt mit E-0 | `06-grenzen-statt-teilabdeckung.md` | umgesetzt | – |
| H3 | Art. 25 Abs. 1 lit. a, c und Art. 13 Abs. 3 lit. a Teilabdeckung | `06-grenzen-statt-teilabdeckung.md` | umgesetzt | – |
| A-F2 | Vom Omnibus neu gefasste AI-Act-Zeilen `out` („ersetzt durch n.F.“): 6 in-Zeilen als Entscheid, 54 Zeilen mit `neufassung`, Wächter `OMNIBUS_SUPERSEDED_UNITS_OUT` | `08-paket-1-anhaenge.md` | umgesetzt 29.09.2026 (Paket 2, Review 09) | – |
| A-W4 | Art. 3 Nr. 4, 8, 23 (und 52 weitere Zeilen): falscher Omnibus-Vermerk berichtigt | `08-paket-1-anhaenge.md` | umgesetzt 29.09.2026 (Paket 2) | – |
| P2-F1 | 100 Änderungsanweisungen des Omnibus `out`, bewertet wird die n.F.-Zeile | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 a | – |
| P2-F2 | Bestätigte Einordnungen von Art. 4, 25 Abs. 2, 111 Abs. 2 Satz 1 gelten für die n.F.-Zeilen | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 a | – |
| P2-F3 | Art. 25 Abs. 2 ganz ersetzt (nicht teilweise) | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 a | – |
| P2-F5 | Omnibus Art. 4 (Inkrafttreten) `out` | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 a | – |
| R-2 | Severity `OMNIBUS_SUPERSEDED_UNITS_OUT` = HIGH (unbewertete Neufassung = unbekannte Lücke = falsches „konform“) | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 HIGH | – |
| A-W5 | Verknüpfer verlor nach der Satzebene den Verweis Art. 111 Abs. 2 → n.F. | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 | – |
| A-W6 | Verknüpfer verband Art. 96 Abs. 1 UAbs. 2 n.F. mit allen Buchstaben | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 | – |
| Q2 | Nr.-2-Ausnahmen (Art. 27, 43 Abs. 2, 49, 75, 86) für einen Fachbeitrag | `05-schritt-2d-2e-gedeckt-querbefunde.md` | außerhalb | – |
| Q10 | Art. 99 Abs. 7: dokumentierte Maßnahmen mindern das Bußgeld (BIZDEV) | `05-schritt-2d-2e-gedeckt-querbefunde.md` | außerhalb | – |

# Pflege

- **Neue Frage an den PO:** in einer Tabelle `| # | Entscheidung | Optionen |` oder `| # | Frage | Optionen |` im Review, und hier eine Zeile. Fehlt sie hier, wird `make verify` rot.
- **Entscheid gefallen:** Stand auf `entschieden <Datum> <Option>`; Paket stehen lassen, bis umgesetzt; dann `umgesetzt`, Paket `–`.
