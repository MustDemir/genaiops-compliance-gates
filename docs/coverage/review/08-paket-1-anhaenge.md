---
titel: Paket 1 – Anhänge und Art. 113 eingeordnet
stand: 2026-09-29
basis: Branch review-2c · Pflichtenraum AI Act · Raster T-13 (Schritte 1, 2, 2b, 2c, 3, Ausnahme steuernde Norm) · Durchschlagsregel 2b E4 · Omnibus-Wortlaut Art. 1 Nr. 1–43
status: VORSCHLAG – alle 210 Zeilen po_bestaetigt false · Stichprobe und Fragen A-F1, A-F2 in Paket 4
---

# Kurzfazit
- **Alle 210 offenen Einheiten sind eingeordnet:** 206 Anhang-Einheiten und 4 aus Art. 113.
  - **4 in**, alle steuernd (`nicht_einschlaegig`): Anhang III (Einleitung), Art. 113, Art. 113 lit. a, Art. 113 lit. c.
  - **206 out**, jede mit Grund und Rasterschritt.
- **Keine neue prüfbare Pflicht, keine neue Lücke.** Das ist erwartbar:
  - Ein Anhang füllt den Artikel aus, der auf ihn verweist, und teilt dessen Scope.
  - Die Betreiber-Artikel (Art. 13, 14, 26) verweisen auf keinen Anhang. Anhang III Nr. 2, unser Bereich, war schon `in` (2b E5).
- **4 Hypothesen:** Anhang IV nennt an vier Stellen den Betreiber. Vorschlag: kein Durchschlag. Frage A-F1.
- **AI-Act-Pflichtenraum jetzt vollständig eingeordnet:**

| | vorher | jetzt |
|---|---|---|
| unbewertet | 210 | **0** |
| in | 85 | 89 (gedeckt 4 · teil 38 · Lücke 28 · n. e. 19) |
| out | 908 | 1114 |
| `verify_norm_quotes.py --modus vollstaendig` | 432 Befunde | 12 Befunde |

- Die 12 übrigen Befunde sind die steuernden Normen ohne Verifikationsstufe. Sie stehen schon auf der Liste für die PO-Runde (Paket 4).

# Teil 1 – Die Regel

```
Anhang füllt Artikel X aus  ──►  Scope wie Artikel X
   außer: der Anhang nennt selbst den Betreiber als Empfänger oder Zweck (Durchschlag a, 2b E4)
```

| Anhang | Inhalt | verweisender Artikel | Einheiten | Ergebnis | Rasterschritt |
|---|---|---|---|---|---|
| I | Harmonisierungsrecht (Produkte) | Art. 6 Abs. 1 (out) | 14 | out | 2b Systemtyp |
| II | Straftatenliste | Art. 5 Abs. 1 lit. h (out) | 1 | out | 1 Adressat Behörde |
| III Einleitung | Hochrisiko-Liste | Art. 6 Abs. 2 (in, steuernd) | 1 | **in**, n. e. | steuernd |
| III Nr. 1, 3–8 | andere Hochrisiko-Bereiche | Art. 6 Abs. 2 | 31 | out | 2b Systemtyp |
| IV | technische Dokumentation | Art. 11 Abs. 1 (out) | 26 | out, **4 HYPOTHESE** | 1 Adressat Anbieter |
| V | EU-Konformitätserklärung | Art. 47 (out) | 9 | out | 1 Adressat Anbieter |
| VI | interne Kontrolle | Art. 43 (out) | 4 | out | 1 Adressat Anbieter |
| VII | notifizierte Stelle | Art. 43 (out) | 28 | out | 1 Adressat Anbieter / Stelle |
| VIII A, B | Registrierung durch Anbieter | Art. 49 Abs. 1, 2 (out) | 24 | out | 1 Adressat Anbieter |
| VIII C | Registrierung durch Betreiber (Behörde) | Art. 49 Abs. 3 (out, PO 23.09.) | 6 | out | 2 Bereichsausnahme Nr. 2 |
| IX | Tests unter Realbedingungen | Art. 60 (out, bedingt) | 6 | out | 2c bedingte Pflicht |
| X | EU-IT-Großsysteme | Art. 111 Abs. 1 (out) | 16 | out | 2b Systemtyp |
| XI, XII | GPAI-Dokumentation und -Information | Art. 53 (out) | 32 | out | 1 Adressat GPAI-Anbieter |
| XIII | GPAI-Kriterien der Kommission | Art. 51 (out) | 8 | out | 1 Adressat Behörde |
| Art. 113 | Inkrafttreten, Geltungsbeginn | – | 4 | 3 in (steuernd), lit. b out | steuernd / 3 |
| **Summe** | | | **210** | **4 in · 206 out** | |

**Anmerkungen:**
- **Anhang V:** G-DEP-04 prüft beim Betreiber die CE-Kennzeichnung als Eingangskontrolle (Art. 26 Abs. 1), nicht den Inhalt der Erklärung. Kein Widerspruch zu `out`.
- **Anhang VIII Abschn. C:** Die Registrierungspflicht für Betreiber, die Behörden sind, nimmt Anhang-III-Nr.-2-Systeme aus. Die offene Frage Art. 111 Abs. 2 Satz 2 (Betreiber als Behörde) ändert daran nichts.
- **Art. 113 lit. b:** Er setzt nur Daten für Kapitel und Artikel ohne `in`-Pflicht (Kap. III Abschn. 4, V, VII, XII, Art. 78). Gezählt am 29.09.2026: keine `in`-Zeile in Art. 28–39, 51–56, 64–70, 78, 99–101. Damit steuert er nichts, das wir prüfen.

# Teil 2 – Omnibus

- Anhänge ändert der Omnibus nur an drei Stellen. Geprüft am verfügenden Teil, Art. 1 Nr. 1–43:
  - **Nr. 41:** Anhang I Abschn. A Nr. 1 (Maschinenrichtlinie) gestrichen, Abschn. B Nr. 21 (Maschinenverordnung (EU) 2023/1230) angefügt
  - **Nr. 42:** Anhang VIII Abschn. B Nr. 7 und 9 gestrichen
  - **Nr. 43:** Anhang XIV neu (Codes für die Benennung notifizierter Stellen)
- Eingetragen im Feld `omnibus` jeder Einheit. Die gestrichenen Einheiten sind ohnehin `out`.
- Anhang I Abschn. B Nr. 21 n.F. und Anhang XIV n.F. stehen im Omnibus-Pflichtenraum und kommen in **Paket 2**.
- **Art. 113:** Nr. 40 fasst Abs. 3 lit. a und c neu und fügt lit. d an. Die AI-Act-Zeilen lit. a und c tragen den Inhalt der Neufassung, wie bisher Art. 4 und Art. 111 Abs. 2 (siehe A-F2).

# Teil 3 – Fragen an den PO (für Paket 4)

**a ist jeweils die Empfehlung.**

| # | Frage | Optionen |
|---|---|---|
| **A-F1** | Anhang IV Nr. 1 lit. g, lit. h, Nr. 2 lit. e und Nr. 3 nennen den Betreiber. Schlägt die Dokumentationspflicht des Anbieters auf ihn durch? | a) **nein, out:** Der Betreiber ist Gegenstand der Dokumentation, nicht ihr Empfänger. Die technische Dokumentation erhält die Behörde. Was der Betreiber braucht, verlangt Art. 13, der `in` ist · b) ja, in: Befund je Zeile |
| **A-F2** | Methode für Paket 2: Wie werden AI-Act-Zeilen geführt, die der Omnibus neu gefasst hat? Heute tragen sie den Inhalt der Neufassung (Art. 4, Art. 111 Abs. 2, jetzt Art. 113 lit. a, c). Ihr `beleg` ist aber der alte Wortlaut – Beleg und Aussage passen nicht zusammen, und die n.F.-Zeile im Omnibus-Raum zählt dieselbe Pflicht ein zweites Mal. | a) **AI-Act-Zeile `out`** mit Grund „ersetzt durch n.F.“, bewertet wird nur die n.F.-Zeile mit ihrem eigenen Wortlaut · b) wie heute; die n.F.-Zeile wird `out` mit Verweis auf die AI-Act-Zeile |

**Warum A-F2a:** Der Kern der Fälschungssicherheit ist, dass die Aussage auf ihrem Beleg steht (SPEC-06 Abschnitt 6). Bei b) steht die Aussage auf einem Wortlaut, der nicht mehr gilt.

# Teil 4 – Befunde am Werkzeug

| # | Befund | Wohin |
|---|---|---|
| A-W1 | **Art. 113:** Der Extraktor führt die drei Absätze ohne Nummer als eine Einheit „Art. 113“ und die Buchstaben als „Art. 113 lit. a“. Das Gesetz selbst zitiert „Artikel 113 Absatz 3 Buchstabe a“ (Omnibus Art. 1 Nr. 40 und Art. 111 Abs. 2 n.F. aus Nr. 39). Die Kennung weicht von der amtlichen Zitierweise ab. | Werkzeug-Ticket wie T-14.1; dabei prüfen, welche Artikel sonst Absätze ohne Nummer haben |
| A-W2 | **Anhang I Abschn. B:** Nr. 13–20 stehen in einer Einheit. Ohne Folge für die Analyse (alle `out`). | Werkzeug-Ticket, niedrig |
| A-W3 | **Anhang XIII lit. g:** Der Beleg endet mit der Fußzeile „ELI: … ISSN 1977-0642 (electronic edition)“ aus der Quelldatei. Wortgleich, aber kein Normtext. | Werkzeug-Ticket, niedrig |

# Teil 5 – Wiedervorlage

- **Anhang IX:** sobald der Betreiber an einem Test unter Realbedingungen teilnimmt (wie Art. 60 Abs. 4 lit. h, j).
- **Anhang XI, XII:** beim Prüf-Agenten selbst (Paket 9). Baut er auf einem KI-Modell mit allgemeinem Verwendungszweck auf, stellt sich dort die Frage nach der Anbieterrolle und den Informationen nach Anhang XII.
- **Anhang I Abschn. B Nr. 21 n.F., Anhang XIV n.F.:** Paket 2.

# Teil 6 – Stichprobe für den PO

Acht Zeilen, je eine pro Begründungsart:

| Zeile | Ergebnis | prüft |
|---|---|---|
| Anhang III (Einleitung) | in, n. e. | steuernde Norm |
| Anhang III Nr. 5 lit. d | out | Systemtyp |
| Anhang IV Nr. 1 lit. h | out, HYPOTHESE | Durchschlag (A-F1) |
| Anhang IV Nr. 2 lit. g | out | Adressat Anbieter |
| Anhang VIII Abschn. C Nr. 4 | out | Bereichsausnahme |
| Anhang IX Nr. 2 | out | bedingte Pflicht |
| Anhang XII Nr. 2 lit. a | out | Adressat GPAI-Anbieter |
| Art. 113 lit. b | out | steuert keine in-Pflicht |

**Ehrlich zur Methode:**
- Die Einordnung ist gruppenweise nach dem verweisenden Artikel gemacht. Jede Zeile trägt Grund und Rasterschritt, und jede Zeile ist gelesen.
- Der `pflicht`-Text der Listeneinträge ist eine Kurzform des Belegs mit Vorsatz (z. B. „Pflichtinhalt der technischen Dokumentation des Anbieters (Art. 11 Abs. 1): …“). Er beschreibt, er legt nicht aus.
