---
titel: Entscheidungsregister – was der PO noch entscheiden muss und welche Schritte ausstehen
stand: 2026-10-05 (nach Paket 3b, P3-F5 und Review 12 Evidence Store; T-16.1 gebaut und abgenommen: ES-1, ES-2, ES-F3 a)
basis: Reviews 00–09, Entscheidungsdateien in docs/coverage/entscheide/, Plan Teil C
status: lebendes Register · der Wächter PO_DECISIONS_REGISTERED hält es vollständig
---

# Wozu

- **Arbeitsblatt der PO-Runde (Paket 4):** [`13-po-runde-paket-4.md`](13-po-runde-paket-4.md) – je Punkt Frage, Optionen, Empfehlung und die Zeilenlisten. Das Register bleibt die eine Stelle für den Stand.

- **Eine Stelle für alles, was offen ist:** jede Entscheidung des PO und jeder beschlossene Schritt, der noch nicht umgesetzt ist, mit Ziel-Paket aus dem Plan (00 Teil C).
- **Vollständig durch einen Wächter, nicht durch Sorgfalt.** `PO_DECISIONS_REGISTERED` liest jede Entscheidungs- und Befundtabelle der Reviews (`| # | Entscheidung | …`, `| # | Frage | Optionen |`, `| # | Befund | Wohin |`). Jede Zeile dort muss hier stehen. Jeder offene Punkt hier braucht ein Paket.
- **Stand** ist eins von: `offen` · `vertagt` · `entschieden` (Umsetzung steht aus, wenn ein Paket genannt ist) · `umgesetzt` · `außerhalb` (nicht in diesem Repo).
- **Paket:** 1–9 aus Plan Teil C · `T-13` Sektorstapel · `T-16` Evidence Store beweisfest · `jederzeit` · `–`.

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
| Q11 | Art. 26 Abs. 11 (Information der betroffenen Personen); die Zeile steht bis dahin unter Vorbehalt Q11 in der Element-Matrix (P3-F4 b) | `05-schritt-2d-2e-gedeckt-querbefunde.md` | vertagt | 4 |
| A-F1 | Anhang IV nennt den Betreiber: Durchschlag? Empfehlung a (nein, out) | `08-paket-1-anhaenge.md` | offen | 4 |
| IN-1 | Alle `in`-Zeilen bestätigen (nach P3-F3: 67 von 109 bestätigt – AI Act 61 von 85, Omnibus 6 von 24) | `entscheidungsregister.md` | offen | 4 |
| OUT-1 | `out`-Zeilen: Stichprobe nach Adressat-Gruppen, dann Sammelbestätigung (30.09.2026: 139 von 1407 bestätigt – AI Act 32 von 1147, Omnibus 107 von 260) | `entscheidungsregister.md` | offen | 4 |
| R-1 | Severity des Wächters `PO_DECISIONS_REGISTERED` (Vorschlag LOW: bricht `make verify`, wie `HANDBOOK_ROADMAP_CURRENT`) | `entscheidungsregister.md` | offen | 4 |
| M-B1 | Welches Requirement trägt Art. 26 Abs. 5 Satz 1: R009 wie heute oder R008/R010 der prüfenden Gates? | `07-element-matrix.md` | offen | 5 |
| EF | Die vier Ehrlichkeitsfelder je neuem oder geändertem Requirement und Check: Norm↔Pflicht, MUST/SHOULD, `evidence_level`, `implemented`/`design_only` (AGENTS.md 3) | `entscheidungsregister.md` | offen | 5 |
| P9-1 | Use Cases des Prüf-Agenten | `00-systembild-und-plan.md` | offen | 9 |
| P9-2 | Einordnung des Agenten selbst nach AI Act (HYPOTHESE: kein Hochrisiko; Art. 4, ggf. Art. 50) | `00-systembild-und-plan.md` | offen | 9 |
| P9-3 | Architektur des Agenten | `00-systembild-und-plan.md` | offen | 9 |
| PUSH-2 | Commit 47c9833 auf `claude/scrum-solo-developer-6xyy9k` pushen (Whitepaper-PDFs in `.gitignore`) | `entscheidungsregister.md` | offen | jederzeit |
| WP-1 | Benennung des Whitepapers; Änderungen liegen in `stash@{0}` | `entscheidungsregister.md` | offen | jederzeit |

# Teil 2 – Entschieden, Umsetzung steht aus

| ID | Gegenstand | Quelle | Stand | Paket |
|---|---|---|---|---|
| E2 | 24 Lücken in den Paketen P0–P8 mit Prioritäten | `02-schritt-2b-luecken.md` | entschieden 23.09.2026 | 5 |
| E3 | R015 (Art. 5 Verbote) und R016 (Art. 4 KI-Kompetenz); Artikel und MUST/SHOULD je Requirement | `02-schritt-2b-luecken.md` | entschieden 23.09.2026 | 5 |
| F1 | Cluster und Maßnahmen aus 2c als Grundlage der Bedarfsanalyse | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 5 |
| F3 | Anker korrigieren: R006 ohne Art. 10, R007 ohne Art. 50, R010 + Art. 26 Abs. 5 Satz 1, R013 + Art. 26 Abs. 5 Satz 3 | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 5 |
| F5 | G-OPS-02 umbauen: Art.-73-Fristen nur als Auffangregel, Reduktion nach Abs. 9 am Status des Anbieters. Zwischenschritt „Vermerk HYPOTHESE im Gate“ am 29.09.2026 nachgeholt | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 5 |
| F6 | Neues Requirement R017 Rollenwechsel (Art. 25), MUST/SHOULD in Paket 5 | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 5 |
| E2 | Rego-Meldungen mit Check-ID (130 von 195 ohne), Wächter `REGO_MESSAGES_CARRY_CHECK_ID` im selben Commit | `05-schritt-2d-2e-gedeckt-querbefunde.md` | entschieden 29.09.2026 a | 5 |
| P2-F4 | Art. 4a Abs. 1 lit. a–f bleiben out (bedingte Pflicht); Wiedervorlage maschinell: Manifest-Feld `special_categories_for_bias` + Check, der die Zeilen meldet, sobald `true` (Bedingungsparameter je Anwendungsfall, wie SPEC-03) | `09-paket-2-omnibus.md` | entschieden 29.09.2026 c | 5 |
| P3-F3 | Art. 25 Abs. 2 lit. a–c n.F. sind Lücken (Übergabebeleg = Behälter, wie Ziff. vii) – eingetragen und bestätigt. Aus steht die Maßnahme, mit der Vorgabe des PO: Wird der Betreiber zum Anbieter (C-25a eigene Marke, C-25c Zweckänderung), **nennt G-OPS-06 die Belege, die bereitgestellt werden müssen** – lit. a technische Unterlagen für Art. 16, lit. b Einschränkungen und Fehlerarten, lit. c gezielter technischer Zugang auch für Test und Validierung, dazu Kooperationszusage und schriftliche Vereinbarung (Abs. 4) –, und C-25d prüft je Beleg ein Feld und sagt, welcher fehlt. MUST/SHOULD und Beweisstufe: EF | `11-paket-3b-element-matrix.md` | entschieden 01.10.2026 a | 5 |
| ES-F2 | T-16 jetzt, parallel zu Paket 4; ES-1/ES-2 zuerst (T-16.1), dann ES-3–ES-5, ES-6 mit der P3-F3-Maßnahme | `12-evidence-store-beweis.md` | entschieden 02.10.2026 a | T-16 |
| E7 | Meldekaskade: planen ja, bauen erst in der Umsetzung | `02-schritt-2b-luecken.md` | entschieden 23.09.2026 | 6 |
| F4 | R001, R002, R003, R005, R011 ohne Betreiber-Anker: `anker: offen`, Anker-Suche im Sektorstapel. Zwischenschritt `anker: offen` am 29.09.2026 nachgeholt. **Folge aus Teil C:** Der Sektorstapel kommt nach dem Agenten, der Anker bleibt so lange offen, und der Agent muss „Anker offen“ melden | `04-schritt-2c-teilabdeckungen.md` | entschieden 28.09.2026 a | 7 |
| H4 | `known_limits` je Gate, Hinweis in jedem Lauf, Urteil unverändert, Wächter `GATE_LIMITS_DECLARED` | `06-grenzen-statt-teilabdeckung.md` | entschieden 29.09.2026 Option 1 | 7 |

# Teil 3 – Befunde mit Ziel-Paket

| ID | Gegenstand | Quelle | Stand | Paket |
|---|---|---|---|---|
| A-W12 | Omnibus-Unterabsätze aus dem Zeilenfall gezählt; Art. 75 Abs. 2a, 75a Abs. 4, 75c Abs. 4 ungeprüft (alle out) | `10-paket-3-werkzeug.md` | offen | 4 |
| P4-B1 | `in`-Zeilen ohne eigenen Pflichttext: 11 ohne Text, 12 mit Sammeltext in vier Gruppen – vor IN-1 neu schreiben, Wächter, Sammelbestätigung der Texte wie P3-F5 | `13-po-runde-paket-4.md` | offen | 4 |
| A-W10 | Sektorstapel: § 2 BSIG / § 2 KRITIS-DachG – erste Nummer der Begriffsbestimmungen nicht erkannt | `10-paket-3-werkzeug.md` | offen | T-13 |
| P3-B1 | Art. 73 Abs. 2 UAbs. 1 Satz 1 (Teilabdeckung) und Abs. 3, 4 (gedeckt) bei gleichem Aufbau ungleich zerlegt; Empfehlung: Abs. 3, 4 wie Abs. 2 | `11-paket-3b-element-matrix.md` | offen | 4 |
| AN-1 | Wächter Requirement-Anker ↔ Pflichtenraum: ein Requirement, dessen Normverweise nur auf `out`-Einheiten zeigen, muss `anker: offen` tragen. Gemessen am 29.09.2026: R002 (markiert), dazu R010 (F3) und R012 (Q1) ohne `in`-Anker. Kommt mit F3/F4 | `entscheidungsregister.md` | offen | 5 |
| ES-3 | Belege nicht gebunden: gelesene Inputs werden nicht gehasht, `payload_id` ist eine Zufalls-UUID | `12-evidence-store-beweis.md` | offen | T-16 |
| ES-4 | Begründung nicht hash-gedeckt: MUST-Meldungen fehlen in der DB, Warnungen nur im ungehashten `notes`, Manifest-Digest nur `Gate:Urteil` | `12-evidence-store-beweis.md` | offen | T-16 |
| ES-5 | Freigabe-Eintrag unvollständig: Begründung ungehasht; geprüfte Belege, Datum, Rolle, Auflagen verworfen; keine Signatur des Prüfers | `12-evidence-store-beweis.md` | offen | T-16 |
| ES-6 | Belegverzeichnis beim Rollenwechsel (Soll/Ist je geschuldetem Beleg, P3-F3) fehlt im Store | `12-evidence-store-beweis.md` | offen | T-16 |
| ES-7 | Dritter Läufer `pipeline/test_pipeline_local.sh` (nicht in `make verify`, nicht in der CI) kennt die menschliche Entscheidung nicht: G-PRE-01/G-PRE-05 ohne Freigabe, G-DEP-03 als AUTO, meldet „Deploy authorized“ – angleichen oder entfernen | `12-evidence-store-beweis.md` | offen | T-16 |
| PR-1 | Paket 8: Der PR muss von `review-2c` kommen, nicht von `spec06-aiact-stufe0` (Plan Teil C). `review-2c` enthält `spec06-aiact-stufe0` und `t14-pflichtenraum-werkzeug` vollständig und liegt 38 Commits darüber (gemessen 30.09.2026); ein PR von `spec06-aiact-stufe0` ließe T-14 und alle Pakete aus | `entscheidungsregister.md` | offen | 8 |
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
| M1 | Nachbarprüfung zählt nicht als Element (streng): 9 Zeilen Teilabdeckung → Lücke, Nachbarn in `nachbar_gate`; Wächter `COVERAGE_FINDING_NAMES_CHECKING_GATE`. Art. 15 Abs. 3, Abs. 4 UAbs. 1 Satz 1, 2 folgen mit F4 | `07-element-matrix.md` | umgesetzt 30.09.2026 a | – |
| P2-F1 | 100 Änderungsanweisungen des Omnibus `out`, bewertet wird die n.F.-Zeile | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 a | – |
| P2-F2 | Bestätigte Einordnungen von Art. 4, 25 Abs. 2, 111 Abs. 2 Satz 1 gelten für die n.F.-Zeilen | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 a | – |
| P2-F3 | Art. 25 Abs. 2 ganz ersetzt (nicht teilweise) | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 a | – |
| P2-F5 | Omnibus Art. 4 (Inkrafttreten) `out` | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 a | – |
| R-2 | Severity `OMNIBUS_SUPERSEDED_UNITS_OUT` = HIGH (unbewertete Neufassung = unbekannte Lücke = falsches „konform“) | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 HIGH | – |
| R-3 | Severity `COVERAGE_FINDING_NAMES_CHECKING_GATE` = HIGH (wie R-2: eine Nachbarprüfung darf nicht als Prüfung erscheinen) | `09-paket-2-omnibus.md` | umgesetzt 30.09.2026 HIGH | – |
| R-4 | Severity `NORM_UNITS_MATCH_EXTRACTOR` = HIGH (vorgeschlagen MEDIUM; ein veralteter Schnitt kann eine Pflicht verstecken) | `10-paket-3-werkzeug.md` | umgesetzt 30.09.2026 HIGH | – |
| P3-F1 | Art. 9 Abs. 5 UAbs. 3 `out`: Betreiber ist Maßstab, nicht Empfänger; Beleg im Audit legt der Anbieter vor (Anhang IV Nr. 5). HYPOTHESE bleibt | `10-paket-3-werkzeug.md` | umgesetzt 30.09.2026 a | – |
| P3-F2 | Sammelbestätigung der 17 Pflichttexte nach dem Neuschnitt (15 Sätze, Art. 9 Abs. 5 lit. c, Art. 6 Abs. 3 lit. d); bestätigt ist der Text, nicht der Befund | `10-paket-3-werkzeug.md` | umgesetzt 30.09.2026 a | – |
| M2 | `gate` nennt nur elementprüfende Gates, Nachbarn in `nachbar_gate` – für alle Zeilen aus der Element-Matrix abgeleitet (Paket 3b) | `07-element-matrix.md` | umgesetzt 30.09.2026 a | – |
| MX-1 | Element-Matrix als Daten (`docs/coverage/matrix/element_matrix.yaml`), `gate` daraus abgeleitet, Wächter `ELEMENT_MATRIX_DERIVES_GATE` in `make verify` – aus Paket 7 vorgezogen | `entscheidungsregister.md` | umgesetzt 30.09.2026 (Paket 3b) | – |
| P2-B1 | Art. 25 Abs. 2 lit. a–c n.F.: C-25d prüft den Übergabebeleg nicht je Element → Lücke als Vorschlag, Bestätigung P3-F3 | `09-paket-2-omnibus.md` | umgesetzt 30.09.2026 (Review 11) | – |
| A-W13 | Pflichttexte hinter Aufzählungen: 19 Zeilen (AI Act 12, Omnibus 7; davon 2 `in`) nannten noch den Unterabsatz, den T-15 Teil 2 aus ihnen geschnitten hat – Texte neu, `NORM_UNITS_MATCH_EXTRACTOR` prüft den wörtlichen Rest (Bestätigung P3-F5) | `11-paket-3b-element-matrix.md` | umgesetzt 01.10.2026 | – |
| P3-F5 | Sammelbestätigung der 19 Pflichttexte aus A-W13 – bestätigt ist der Text, nicht der Befund; festgehalten in `2026-10-02_p3-f5-pflichttexte.yaml` | `11-paket-3b-element-matrix.md` | umgesetzt 02.10.2026 a | – |
| P3-F4 | Art. 26 Abs. 11: Vorbehalt bis Q11 – bleibt Teilabdeckung mit G-DEP-03; die Element-Matrix meldet, dass sie abgeleitet Lücke wäre | `11-paket-3b-element-matrix.md` | umgesetzt 01.10.2026 b | – |
| R-6 | Severity `ELEMENT_MATRIX_DERIVES_GATE` = HIGH (wie R-3) | `11-paket-3b-element-matrix.md` | umgesetzt 01.10.2026 HIGH | – |
| R-5 | Severity `NORM_SENTENCE_UNITS_CURRENT` = HIGH (vorher MEDIUM; fehlende Satzebene versteckt eine Pflicht wie Art. 26 Abs. 5 Satz 2) | `10-paket-3-werkzeug.md` | umgesetzt 30.09.2026 HIGH | – |
| PUSH-1 | Branch `review-2c` nach origin gepusht (Stand `45e2eb1`, pre-push `make verify` grün) | `entscheidungsregister.md` | umgesetzt 30.09.2026 | – |
| ES-1 | Ablehnung wirkt: MANUAL FAIL → block, in Orchestrator und CI aus einem Modul (`pipeline/human_decision.py`); Wächter `HUMAN_DECISION_TAKES_EFFECT` (HIGH), Verhalten `pipeline/test_human_decision.py`, CI negative-cases Fall 10 | `12-evidence-store-beweis.md` | umgesetzt 02.10.2026 (T-16.1), abgenommen 05.10.2026 | – |
| ES-2 | Fehlende Freigabe wirkt: ein HYBRID-Gate ohne Freigabe hält an (`awaiting_approval`); HYBRID kommt aus der Gate-Definition, ein Szenario mit AUTO wird abgewiesen (G-DEP-03 lief so); CI: vier Fixture-Freigaben (PO Option a), ein fehlendes HYBRID-Gate blockiert | `12-evidence-store-beweis.md` | umgesetzt 02.10.2026 (T-16.1), abgenommen 05.10.2026 | – |
| ES-F1 | Wirkung der menschlichen Entscheidung: MANUAL FAIL → block, HYBRID-Gate ohne Freigabe → hält an („wartet auf Freigabe“), Wiederaufnahme mit Freigabe | `12-evidence-store-beweis.md` | umgesetzt 02.10.2026 a (T-16.1), abgenommen 05.10.2026 | – |
| ES-F3 | Trigger `halt_pipeline` bei fehlender, abgelehnter oder ungültiger Freigabe an den sieben HYBRID-Gates `implemented` (Feld 4 gilt der Wirkung; die Freigabe bleibt E-0 bis T-16.4); `HUMAN_DECISION_TAKES_EFFECT` Teil 6 hält die Deklaration gegen das Modul | `12-evidence-store-beweis.md` | umgesetzt 05.10.2026 a | – |
| PUSH-3 | `review-2c` 876c1b1..7ca98ce nach origin: Commits auf dem Mac mit dem SSH-Schlüssel des PO neu signiert, Schlüssel als Signing Key im GitHub-Konto, pre-push `make verify` grün, alle fünf Commits auf GitHub „Verified“ | `entscheidungsregister.md` | umgesetzt 02.10.2026 | – |
| A-W1 | Art. 113 (und Art. 85, DSGVO Art. 67, NIS2 Art. 44): unnummerierte Absätze als Abs. 1–n, Kennung „Art. 113 Abs. 3 lit. a“ wie im Gesetz (T-15) | `08-paket-1-anhaenge.md` | umgesetzt 30.09.2026 | – |
| A-W2 | Anhang I Abschn. B Nr. 13–20 einzeln (T-15) | `08-paket-1-anhaenge.md` | umgesetzt 30.09.2026 | – |
| A-W3 | Fußzeile „ELI … ISSN“ nicht mehr im Beleg von Anhang XIII lit. g (T-15) | `08-paket-1-anhaenge.md` | umgesetzt 30.09.2026 | – |
| M-B2 | Satz-Einheiten tragen je einen eigenen Pflichttext; Wächter in `NORM_SENTENCE_UNITS_CURRENT` | `07-element-matrix.md` | umgesetzt 30.09.2026 (T-15) | – |
| A-W7 | Omnibus: Abs. 1b, Art. 75b und Folgesätze hinter Aufzählungen eigene Einheiten (T-15) | `09-paket-2-omnibus.md` | umgesetzt 30.09.2026 | – |
| A-W11 | Unterabsätze hinter einer Aufzählung sind eigene Einheiten (AI Act 18, Omnibus 11, DSGVO 5, NIS2 16) | `10-paket-3-werkzeug.md` | umgesetzt 30.09.2026 (T-15) | – |
| A-W5 | Verknüpfer verlor nach der Satzebene den Verweis Art. 111 Abs. 2 → n.F. | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 | – |
| A-W6 | Verknüpfer verband Art. 96 Abs. 1 UAbs. 2 n.F. mit allen Buchstaben | `09-paket-2-omnibus.md` | umgesetzt 29.09.2026 | – |
| Q2 | Nr.-2-Ausnahmen (Art. 27, 43 Abs. 2, 49, 75, 86) für einen Fachbeitrag | `05-schritt-2d-2e-gedeckt-querbefunde.md` | außerhalb | – |
| Q10 | Art. 99 Abs. 7: dokumentierte Maßnahmen mindern das Bußgeld (BIZDEV) | `05-schritt-2d-2e-gedeckt-querbefunde.md` | außerhalb | – |

# Pflege

- **Neue Frage an den PO:** in einer Tabelle `| # | Entscheidung | Optionen |` oder `| # | Frage | Optionen |` im Review, und hier eine Zeile. Fehlt sie hier, wird `make verify` rot.
- **Entscheid gefallen:** Stand auf `entschieden <Datum> <Option>`; Paket stehen lassen, bis umgesetzt; dann `umgesetzt`, Paket `–`.
