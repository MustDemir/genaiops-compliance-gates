---
titel: Paket 3a – Werkzeug T-15, Schnittfehler im Extraktor behoben
stand: 2026-09-30
basis: Branch review-2c · PO 30.09.2026 „erst Werkzeug, dann Matrix-Lauf 2“ (Review 09 Teil 7) · Befunde A-W1–A-W3 (Review 08), A-W7 (Review 09) · Extraktor tools/legal/extract_norm_units.py, extract_omnibus_units.py
status: Teil 1 geliefert (Commit folgt dieser Datei) · neu geschnittene Zeilen Vorschlag, po_bestaetigt false · Frage R-4 in Paket 4 · Teil 2 (Unterabsätze nach Listen, M-B2) folgt
---

# Kurzfazit

- **Fünf Schnittfehler behoben, alle sieben Pflichtenräume neu gebaut** (Migration nach Offset wie T-14.1, Berichte `docs/coverage/migration/t15_*.yaml`).
- **Kein Zitat war falsch, aber Belege trugen Text, der kein Normtext ist,** oder Kennungen wichen vom Gesetz ab.
- **Neuer Wächter `NORM_UNITS_MATCH_EXTRACTOR`:** Jeder Raum ist genau der heutige Schnitt seiner Quelle, und kein Beleg trägt Überschrift oder Fußzeile. Vorschlag MEDIUM, Frage **R-4**.
- **Nebenbefund auf dem Mac behoben (A-W8):** Der Resolver las den ignorierten Ordner `gate-definitions/legacy/` mit (162 statt 155 Verweise).

| Befund | Was falsch war | Jetzt | Einheiten |
|---|---|---|---|
| A-W1 | Art. 113 ohne Absatznummern: „Art. 113“, „Art. 113 lit. a“ | **Art. 113 Abs. 1, 2, 3 · Abs. 3 lit. a–c** – wie das Gesetz zitiert (Omnibus Art. 1 Nr. 40) | AI Act 4 → 6 · dazu Art. 85, DSGVO Art. 67, NIS2 Art. 44 je Abs. 1, 2 |
| A-W2 | Anhang I Abschn. B: Nr. 13–20 in einer Einheit | Nr. 13 … Nr. 20 einzeln (Zählung läuft aus Abschn. A weiter) | +8 |
| A-W3 | Anhang XIII lit. g endete mit „ELI: … ISSN …“ | Fußzeile abgeschnitten | 1 |
| A-W9 (neu) | Kapitel-/Abschnittsüberschriften hingen am letzten Glied davor (Art. 4 endete mit „KAPITEL II VERBOTENE PRAKTIKEN …“) | abgeschnitten | 53 (AI Act 24 · DSGVO 20 · NIS2 8 · Omnibus –), davon 1 in-Zeile: Art. 15 Abs. 5 |
| A-W7 (Teil) | Omnibus: Art. 5 Abs. 1b stand in Abs. 1a lit. b · Art. 75b Überschrift und Text in einer Einheit | Abs. 1b eigene Einheit · Art. 75b nach Buchstaben geschnitten | +5 |
| A-W8 (neu) | Resolver und Gate-Liste lasen ungetrackte Dateien | nur, was git verfolgt | – |

**Zählung danach** (gemessen 30.09.2026):

| Raum | Einheiten | in | out | Lücke | Teil | n. e. | gedeckt |
|---|---|---|---|---|---|---|---|
| AI Act | 1203 → **1214** | 84 | 1130 | 35 | 28 | 17 | 4 |
| Omnibus | 269 → **273** | 22 | 251 | 4 | 4 | 14 | – |
| DSGVO | 774 → 775 | – | – | – | – | – | – |
| NIS2 | 471 → 472 | – | – | – | – | – | – |

- Lücken unverändert **39**; neu `in` sind nur steuernde Zeilen ohne eigene Pflicht (Art. 113 Abs. 3, Art. 5 Abs. 1b n.F.).

# Teil 1 – Was sich an den Zeilen ändert

```
vorher                         jetzt
Art. 113  (3 Absätze, in)  ─►  Art. 113 Abs. 1  Inkrafttreten 2024       out  (wie P2-F5 a)
                               Art. 113 Abs. 2  gilt ab 02.08.2026        in, steuernd
                               Art. 113 Abs. 3  „Jedoch:“                 in, steuernd
Art. 113 lit. a / b / c    ─►  Art. 113 Abs. 3 lit. a / b / c            unverändert (gleicher Offset)
```

- **Art. 113 Abs. 1 wird `out`** (Vorschlag): ein abgeschlossenes Datum, dieselbe Begründung wie dein Entscheid zu Omnibus Art. 4 (P2-F5 a).
- **Art. 113 Abs. 3 lit. a und c** behalten Entscheid und Bestätigung (A-F2a); die Entscheidungsdatei nennt sie jetzt unter der neuen Kennung. `PO_DECISIONS_APPLIED` hatte die alten Kennungen sofort als fehlend gemeldet.
- **Art. 5 Abs. 1b n.F.** (Manipulation ohne erhöhte Sichtbarkeit gilt nicht als manipulativ): `in`, steuernd – wie Abs. 1a lit. b.
- **Anhang I Abschn. B Nr. 13–20, Art. 85 Abs. 1, 2, Art. 75b + lit. a–c n.F.:** `out` wie bisher, Pflichttext je Einheit.
- Alle neu geschnittenen Zeilen tragen `po_bestaetigt: false`.

# Teil 2 – Offen in Paket 3

| # | Befund | Wohin |
|---|---|---|
| A-W11 | **Unterabsätze nach einer Liste hängen am letzten Buchstaben** (dieselbe Ursache wie A-W6, A-W7 Rest). 26 Einheiten im AI Act, 5 DSGVO, 10 NIS2. Zwei davon sind `in` und inhaltlich wichtig: **Art. 6 Abs. 3 lit. d** trägt UAbs. 2 („gilt … immer als hochriskant, wenn es ein Profiling … vornimmt“ – steuert die Einstufung) · **Art. 9 Abs. 5 lit. c** trägt UAbs. 2 (Kenntnisse und Erfahrung des Betreibers bei der Risikominimierung). | Paket 3, Werkzeug Teil 2 – vor dem Matrix-Lauf |
| A-W10 | **Sektorstapel:** In § 2 BSIG und § 2 KRITIS-DachG erkennt der Extraktor die erste Nummer der Begriffsbestimmungen nicht; die Nummern fehlen als Einheiten. Gefunden, weil die A-W2-Regel dort umgeschnitten hätte (deshalb nur in Anhängen aktiv). | T-13 |

| # | Frage | Optionen |
|---|---|---|
| **R-4** | Severity von `NORM_UNITS_MATCH_EXTRACTOR` | a) **MEDIUM** – ein falscher Schnitt verschiebt, wo eine Pflicht steht, fälscht aber kein Zitat · b) HIGH |

**Ehrlich zur Methode:**
- A-W1 folgt der Zitierweise, die der Omnibus für Art. 113 selbst verwendet („Artikel 113 Absatz 3 Buchstabe a“). Dass Art. 85 AI Act, Art. 67 DSGVO und Art. 44 NIS2 ebenso als „Absatz 1, 2“ zitiert werden, ist dieselbe Regel, aber nicht einzeln an einer amtlichen Fundstelle belegt. Alle drei sind `out` oder unbewertet.
- Der Neubau lief vorher einmal ohne Änderung am Extraktor über alle Räume: 0 Abweichungen. Jede Abweichung danach kommt aus T-15.
