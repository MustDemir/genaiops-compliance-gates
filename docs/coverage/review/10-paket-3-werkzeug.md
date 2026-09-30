---
titel: Paket 3a – Werkzeug T-15, Schnittfehler im Extraktor behoben
stand: 2026-09-30
basis: Branch review-2c · PO 30.09.2026 „erst Werkzeug, dann Matrix-Lauf 2“ (Review 09 Teil 7) · Befunde A-W1–A-W3 (Review 08), A-W7 (Review 09) · Extraktor tools/legal/extract_norm_units.py, extract_omnibus_units.py
status: T-15 geliefert (Teil 1 und 2) · neu geschnittene Zeilen Vorschlag, po_bestaetigt false · Fragen R-4, P3-F1, P3-F2 in Paket 4 · als Nächstes Element-Matrix Lauf 2
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

# Teil 2 – Unterabsätze hinter einer Liste (A-W11) und Pflichttexte der Sätze (M-B2)

**A-W11 – der größte Fund:** Text, der hinter einer Aufzählung steht, ist der nächste Unterabsatz des Absatzes. Der Extraktor hängte ihn an den letzten Buchstaben.

```
vorher  Art. 6 Abs. 3 lit. d   „d) … vorbereitende Aufgabe …“  +  „Ungeachtet des Unterabsatzes 1 gilt ein
                                in Anhang III aufgeführtes KI-System immer dann als hochriskant, wenn … Profiling“
jetzt   Art. 6 Abs. 3 lit. d   nur lit. d
        Art. 6 Abs. 3 UAbs. 3  die Profiling-Regel – in, steuernd (G-PRE-01)
```

- **Neue Einheiten:** AI Act 18 · Omnibus 11 · DSGVO 5 · NIS2 16. Deutsche Gesetze nicht – dort ist der Text hinter einer Aufzählung ein Satz, kein Unterabsatz.
- **Nummerierung wie im Gesetz:** Der Kopf des Absatzes zählt mit. Art. 6 Abs. 3 und Art. 9 Abs. 5 haben zwei Unterabsätze vor der Liste, der Folgeabsatz ist deshalb UAbs. 3 – so zitiert ihn die Verordnung. Art. 43 Abs. 1: Kopf, Liste, UAbs. 2 mit zweiter Liste, UAbs. 3.
- **Zwei in-Zeilen betroffen:**

| Einheit | vorher | jetzt (Vorschlag) |
|---|---|---|
| Art. 6 Abs. 3 UAbs. 3 | in lit. d versteckt | **in**, steuernd (Profiling immer hochriskant) |
| Art. 9 Abs. 5 UAbs. 3 | in lit. c (Lücke) versteckt | **out, HYPOTHESE** – Frage **P3-F1** |
| Art. 9 Abs. 5 lit. c | Lücke, Pflichttext mit UAbs. 3 vermischt | Lücke bleibt (Schulung der Betreiber), Pflichttext nur lit. c |
| Art. 25 Abs. 2 UAbs. 4 n.F. | in lit. c n.F. versteckt | **in**, n. e. – Ausnahme (Carve-out), G-OPS-06/C-25d verlangt ihren Beleg |
| Art. 4a Abs. 2 UAbs. 2 n.F. | in lit. b n.F. | **in**, n. e. – „begründet keine Verpflichtung“ |

- **Art. 96 Abs. 1:** Mit dem neuen Schnitt gibt es die Einheit „Art. 96 Abs. 1 UAbs. 2“; der Omnibus ersetzt genau sie. `OMNIBUS_SUPERSEDED_UNITS_OUT` meldete sofort, dass lit. f und UAbs. 3 noch als „teilweise ersetzt“ geführt waren – berichtigt: UAbs. 2 `ersetzt`, lit. f und UAbs. 3 unverändert. Die Hilfsregel A-W6 im Verknüpfer greift dort nicht mehr.

**M-B2 – Pflichttexte der Satz-Einheiten:** 13 Sätze (Art. 15 Abs. 4, Art. 26 Abs. 5, Art. 73 Abs. 2, Art. 111 Abs. 2, Art. 111 Abs. 2 Satz 1 n.F.) trugen den Pflichttext des ganzen Absatzes. Jeder Satz hat jetzt einen eigenen, der nur sagt, was sein Beleg sagt. `NORM_SENTENCE_UNITS_CURRENT` prüft das jetzt mit: zwei Sätze derselben Einheit dürfen nicht denselben Text tragen. Frage **P3-F2**, weil darunter bestätigte Zeilen sind (Art. 26 Abs. 5).

**Zählung nach Teil 2** (gemessen 30.09.2026):

| | AI Act | Omnibus | zusammen |
|---|---|---|---|
| Einheiten | **1232** | **284** | 1516 |
| in | 85 | 24 | **109** |
| · Lücke | 35 | 4 | **39** |
| · Teilabdeckung | 28 | 4 | 32 |
| · nicht einschlägig | 18 | 16 | 34 |
| · gedeckt | 4 | – | 4 |
| in bestätigt | | | 64 von 109 |
| out bestätigt | | | 138 von 1407 |

# Teil 3 – Fragen und Befunde

| # | Frage | Optionen |
|---|---|---|
| **R-4** | Severity von `NORM_UNITS_MATCH_EXTRACTOR` | a) **MEDIUM** – ein falscher Schnitt verschiebt, wo eine Pflicht steht, fälscht aber kein Zitat · b) HIGH |
| **P3-F1** | Art. 9 Abs. 5 UAbs. 3: Der Anbieter berücksichtigt bei der Risikominimierung Kenntnisse und Erfahrung des Betreibers. Durchschlag? | a) **nein, out** – der Betreiber ist Maßstab, nicht Empfänger oder Zweck (wie A-F1) · b) ja, in – Befund je Element |
| **P3-F2** | Neue Pflichttexte nach dem Neuschnitt (13 Sätze, Art. 9 Abs. 5 lit. c, Art. 6 Abs. 3 lit. d) bestätigen? | a) **ja, Sammelbestätigung** – die Texte beschreiben nur ihren Beleg · b) Einzeldurchsicht in der PO-Runde |

| # | Befund | Wohin |
|---|---|---|
| A-W10 | **Sektorstapel:** In § 2 BSIG und § 2 KRITIS-DachG erkennt der Extraktor die erste Nummer der Begriffsbestimmungen nicht; die Nummern fehlen als Einheiten. | T-13 |
| A-W12 | **Omnibus-Unterabsätze aus dem Zeilenfall gezählt:** Der Omnibus-Text (pdftotext) trennt Unterabsätze nicht immer durch Leerzeilen. Geprüft an Selbstverweisen: Art. 25 Abs. 2 (Gesetz nennt „Unterabsatz 2“) und Art. 75 Abs. 1 („Unterabsatz 1“) stimmen. Art. 75 Abs. 2a, 75a Abs. 4, 75c Abs. 4 sind ungeprüft – alle `out`. | Paket 4, Stichprobe |

**Ehrlich zur Methode:**
- A-W1 folgt der Zitierweise, die der Omnibus für Art. 113 selbst verwendet („Artikel 113 Absatz 3 Buchstabe a“). Dass Art. 85 AI Act, Art. 67 DSGVO und Art. 44 NIS2 ebenso als „Absatz 1, 2“ zitiert werden, ist dieselbe Regel, aber nicht einzeln an einer amtlichen Fundstelle belegt. Alle drei sind `out` oder unbewertet.
- Der Neubau lief vorher einmal ohne Änderung am Extraktor über alle Räume: 0 Abweichungen. Jede Abweichung danach kommt aus T-15.
