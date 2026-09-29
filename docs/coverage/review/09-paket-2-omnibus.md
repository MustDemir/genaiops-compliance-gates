---
titel: Paket 2 – Omnibus-Neufassungen eingeordnet, A-F2a umgesetzt
stand: 2026-09-29
basis: Branch review-2c · Omnibus-Pflichtenraum VO (EU) 2026/1744 (269 Einheiten) · AI-Act-Pflichtenraum (1203) · Raster T-13 (Schritte 1, 2, 2b, 2c, 3, Ausnahme steuernde Norm) · Durchschlagsregel 2b E4 · A-F2a (Review 08 Teil 7)
status: VORSCHLAG – alle 259 neu eingeordneten Omnibus-Zeilen po_bestaetigt false · A-F2a an sechs in-Zeilen als PO-Entscheid eingetragen · Fragen P2-F1 bis P2-F5 und R-2 in Paket 4
---

# Kurzfazit

- **Omnibus-Pflichtenraum vollständig eingeordnet:** 259 offene Einheiten → 0.
  - **100 Änderungsanweisungen** („Artikel 4 erhält folgende Fassung:“) → `out`. Sie tragen keine Pflicht; bewertet wird der neue Text. Frage **P2-F1**.
  - **159 n.F.-Zeilen:** **11 in**, 148 out.
- **A-F2a umgesetzt, in einem Schritt mit den n.F.-Zeilen** – keine Pflicht fällt aus der Zählung:
  - 6 AI-Act-Zeilen `in` → `out` („ersetzt durch n.F.“): Art. 4 · Art. 25 Abs. 2 · Art. 111 Abs. 2 Satz 1, 2 · Art. 113 lit. a, c.
  - Ihre Befunde stehen jetzt an den n.F.-Zeilen (Art. 4 Abs. 1 n.F. = Lücke usw.).
  - Jede AI-Act-Zeile mit Neufassung trägt jetzt `neufassung: ersetzt | teilweise | gestrichen` (54 Zeilen).
- **Neuer Wächter `OMNIBUS_SUPERSEDED_UNITS_OUT`** (MEDIUM, Frage **R-2**): ersetzte Zeile = out, Neufassung bewertet, Normverweise der Gates zeigen auf die Neufassung.
- **Keine neue Lücke.** Neu `in`: 7 Zeilen, alle Untergliederungen schon bewerteter Normen (Art. 25 Abs. 2 lit. a–c, Art. 4a Abs. 2 lit. a/b, Art. 5 Abs. 1a).
- **Werkzeug:** A-W4 (geerbte Omnibus-Vermerke) berichtigt, dazu zwei neue Fehler im Verknüpfer gefunden und behoben (A-W5, A-W6).

**Zählung vorher → nachher** (gemessen 29.09.2026, Branch `review-2c`):

| | AI Act vorher | AI Act jetzt | Omnibus vorher | Omnibus jetzt | **zusammen jetzt** |
|---|---|---|---|---|---|
| unbewertet | 0 | 0 | 259 | **0** | 0 |
| in | 89 | 83 | 10 | 21 | **104** |
| · gedeckt | 4 | 4 | – | – | 4 |
| · Teilabdeckung | 38 | 37 | – | 4 | 41 |
| · Lücke | 28 | 26 | 2 | 4 | **30** |
| · nicht einschlägig | 19 | 16 | 8 | 13 | 29 |
| out | 1114 | 1120 | 0 | 248 | 1368 |
| in, PO-bestätigt | 64 | 61 | 0 | 0 | 61 von 104 |
| out, PO-bestätigt | 25 | 31 | 0 | 0 | 31 von 1368 |

- **Lücken bleiben 30** (28 + 2): Art. 4 und Art. 111 Abs. 2 Satz 2 sind nur umgezogen.
- **Doppelzählung weg:** Art. 113 lit. a, c zählten bisher zweimal (AI Act und n.F.).
- `verify_norm_quotes.py --modus vollstaendig`: AI Act 12, Omnibus 10 Befunde – nur die Zeilen ohne Verifikationsstufe (S3-3, Paket 4).

# Teil 1 – Die Regel

```
Omnibus-Einheit
 ├─ "Omnibus Art. 1 Nr. X"  Änderungsanweisung ──► out (P2-F1)  · bewertet wird ─┐
 └─ "… n.F."                neuer Normtext     ──► Raster T-13 wie Paket 1   ◄───┘
                                                    │
AI-Act-Zeile, deren Text ersetzt ist ──► out „ersetzt durch n.F.“ (A-F2a)
   Befund, Gate, Requirement wandern an die n.F.-Zeile
```

## 1a – Die 159 n.F.-Zeilen nach Rasterschritt

| Gruppe | Beispiele | Zeilen | Ergebnis | Schritt |
|---|---|---|---|---|
| Übernahme nach A-F2a | Art. 4 Abs. 1 · Art. 25 Abs. 2 · Art. 111 Abs. 2 Satz 1, 2 | 4 | **in** (Lücke 2 · teil 1 · n. e. 1) | wie Grundfassung |
| neue Untergliederung | Art. 25 Abs. 2 lit. a–c | 3 | **in**, teil (vorläufig) | Durchschlag 2b E4 |
| neue Untergliederung | Art. 4a Abs. 2 lit. a, b | 2 | **in**, n. e. | wie Art. 4a Abs. 2 (Erlaubnis) |
| steuernd | Art. 5 Abs. 1a, lit. b (Verbot ba/bb nur bei Zweck des Betreibers) | 2 | **in**, n. e. | steuernde Norm |
| schon bewertet (2b E5) | Art. 3 Nr. 14 · Art. 5 lit. ba, bb · Art. 6 Abs. 1a–1c · Art. 113 Abs. 3 lit. a, c, c Ziff. i | (10) | in, unverändert | – |
| Adressat Behörde, Kommission, Stellen | Art. 4 Abs. 2, 3 · 27 Abs. 5 · 28–30 · 40 · 50 Abs. 7 · 56–58 · 64–70 · 75–77 · 96, 97 · Anhang XIV | 92 | out | 1 |
| Adressat Anbieter | Art. 4a Abs. 1 + lit. a–f · 5 Abs. 1a lit. a + Ziff. i, ii · 10 · 11 · 17 · 25 Abs. 4 · 42 · 43 · 63 · 72 · 111 Abs. 4 | 20 | out, **7 HYPOTHESE** | 1 |
| Systemtyp | Art. 2 Abs. 2, 13 · 60a · Art. 113 Abs. 3 lit. c Ziff. ii · Anhang I Abschn. B Nr. 21 | 16 | out | 2b |
| Bereichsausnahme | Art. 27 Abs. 4 (FRIA) | 1 | out | 2 |
| bedingte Pflicht | Art. 60 Abs. 1, 2 (Test unter Realbedingungen) | 2 | out | 2c |
| kein Lebenszyklusbezug | Art. 1 Abs. 2 lit. g · 2 Abs. 7 · 3 Nr. 14a, 14b · 99 · 113 Abs. 3 lit. d | 8 | out | 3 |
| Überschrift | Art. 4 · 4a · 60a · 75 · 75a · 75c · 75d · 77 · Anhang XIV | 9 | out | 3 |
| **Summe neu** | | **159** | **11 in · 148 out** | |

**Anmerkungen:**
- **Art. 4a Abs. 1 lit. a–f (7 HYPOTHESE):** Anbieternorm. Den Betreiber binden die Bedingungen nur über Abs. 2 lit. b – *wenn* er die Erlaubnis nutzt, besondere Kategorien personenbezogener Daten zur Bias-Erkennung zu verarbeiten. Das ist eine bedingte Pflicht (2c). Frage **P2-F4**.
- **Art. 75 ff. (KI-Büro):** Abs. 1 lit. a Ziff. ii n.F. nimmt Anhang-III-Nr.-2-Systeme ausdrücklich von der Zuständigkeit des KI-Büros aus. Für Redispatch bleibt die nationale Marktüberwachung zuständig; Art. 75a–75d treffen uns deshalb nicht.
- **Art. 75a Abs. 4 lit. a, Art. 77 Abs. 1a** nennen den Betreiber – als Gegenstand einer Behördenbefugnis. Eine Pflicht entsteht erst auf Anordnung (Adressat Behörde).
- **Art. 113 Abs. 3 lit. c Ziff. ii n.F.** (Anhang-I-Systeme, 02.08.2028) und **Art. 4a Abs. 2 lit. a/b** sind Unterglieder aus S3-2. Hier als Vorschlag eingeordnet, Entscheid bleibt in Paket 4.

## 1b – Die 100 Änderungsanweisungen

| Anweisung | Zeilen | Ergebnis | Grund |
|---|---|---|---|
| Omnibus Art. 1 Nr. 1–43 | 89 | out | verfügt die Änderung; bewertet wird die n.F.-Zeile (P2-F1) |
| · davon Streichungen (Nr. 9 lit. b, 41 lit. a, 42) | 3 | out | die gestrichene AI-Act-Zeile trägt `neufassung: gestrichen` |
| Omnibus Art. 2 Nr. 1–7 (VO 2018/1139, Luftfahrt) | 7 | out | Adressat Kommission, Systemtyp |
| Omnibus Art. 3 Nr. 1–3 (Maschinen-VO 2023/1230) | 3 | out | Adressat Kommission, Systemtyp |
| Omnibus Art. 4 (Inkrafttreten 27.07.2026) | 1 | out | kein offenes Datum mehr (P2-F5) |

# Teil 2 – A-F2a im AI-Act-Pflichtenraum

```
Omnibus: „Absatz 2 erhält folgende Fassung“ ──► AI-Act-Zeile neufassung: ersetzt ─► out
         „Unterabsatz 2 erhält …“ (Rest gilt) ──► neufassung: teilweise ─► Scope bleibt
         „Absatz 5 wird gestrichen“            ──► neufassung: gestrichen ─► out
```

| neufassung | Zeilen | davon bisher in | Beispiele |
|---|---|---|---|
| ersetzt | 39 | **6** | Art. 4 · 25 Abs. 2 · 111 Abs. 2 Satz 1, 2 · 113 lit. a, c · 10 Abs. 1 · 75 Abs. 1 |
| teilweise | 5 | 0 | Art. 11 Abs. 1 · 25 Abs. 4 · 57 Abs. 1 · 60 Abs. 1 · 96 Abs. 1 lit. f |
| gestrichen | 10 | 0 | Art. 10 Abs. 5 + lit. a–f · Anhang I Abschn. A Nr. 1 · Anhang VIII Abschn. B Nr. 7, 9 |

- **Die sechs in-Zeilen** stehen als PO-Entscheid in `docs/coverage/entscheide/2026-09-29_ueberholt-durch-omnibus.yaml` (A-F2a, bestätigt). Review 08 Teil 7 nennt sie als Umfang des Entscheids.
- **Übernahme an die n.F.-Zeile** (Vorschlag, nicht bestätigt – Frage **P2-F2**):

| AI-Act-Zeile (jetzt out) | n.F.-Zeile (jetzt in) | Befund | übernommen |
|---|---|---|---|
| Art. 4 | Art. 4 Abs. 1 n.F. | Lücke (P2) | Pflicht, Befundgrund |
| Art. 25 Abs. 2 | Art. 25 Abs. 2 n.F. | Teilabdeckung, G-OPS-06 | Befundgrund, HYPOTHESE, Gate |
| Art. 111 Abs. 2 Satz 1 | Art. 111 Abs. 2 Satz 1 n.F. | n. e. (steuernd, P0) | Befundgrund |
| Art. 111 Abs. 2 Satz 2 | Art. 111 Abs. 2 Satz 2 n.F. | Lücke (S3-1) | Befundgrund |
| Art. 113 lit. a, c | Art. 113 Abs. 3 lit. a, c n.F. | n. e. | waren schon in (2b E5) |

- **Art. 25 Abs. 2 weicht von Review 08 ab.** Dort stand „nur UAbs. 2 geändert“. Die Anweisung lautet aber „Absatz 2 erhält folgende Fassung“ – der ganze Absatz ist ersetzt, auch der inhaltsgleiche Satz 1. Deshalb `ersetzt`. Frage **P2-F3**.
- **Normverweise folgen der Neufassung.** `resolve_norm_refs.py` löst einen Verweis auf eine ersetzte Zeile jetzt über `fassung_2026_1744` auf. Folge: „Art. 3 Nr. 14“ (G-PRE-01) zeigt jetzt auf Nr. 14 n.F. (in, steuernd) statt auf die alte Zeile (out); „Art. 25 Abs. 2“ (G-OPS-06) auf Abs. 2 n.F. mit lit. a–c.
- **Omnibus-Vermerke berichtigt:** 112 → 57 Zeilen mit Änderungsvermerk. 55 Zeilen behaupteten eine Änderung, die es an ihrer Stelle nicht gibt:
  - Art. 3 Einleitung und 44 Nummern (A-W4) – geändert ist nur Nr. 14
  - Art. 43 Abs. 4 · Art. 75 Abs. 3 · Art. 77 Abs. 2–4 · Art. 96 Abs. 1 Einleitung und lit. b–e
  - Präzisiert, wo der PO eine Angabe offen hatte: Art. 75 Abs. 1, Art. 77 Abs. 1, Art. 99 Abs. 4
  - Nicht angefasst: Vermerke aus PO-Entscheiden (Art. 4, 56 Abs. 6, 60 Abs. 2, 95 Abs. 4).

# Teil 3 – Fragen an den PO (für Paket 4)

**a ist jeweils die Empfehlung.**

| # | Frage | Optionen |
|---|---|---|
| **P2-F1** | Wie werden die 100 Änderungsanweisungen geführt? | a) **`out`** mit Grund „Änderungsanweisung; bewertet wird die n.F.-Zeile“ – sie bleiben gezählt und sichtbar · b) eigene Kategorie außerhalb von in/out (Feld `art: anweisung`), nicht gezählt |
| **P2-F2** | Die Einordnungen von Art. 4, Art. 25 Abs. 2 und Art. 111 Abs. 2 Satz 1 waren bestätigt. Gelten sie für die n.F.-Zeilen weiter? | a) **ja, Sammelbestätigung** – der Wortlaut ist neu, die Einordnung hattest du schon am neuen Wortlaut getroffen (2b E6) · b) Einzelprüfung in der PO-Runde |
| **P2-F3** | Art. 25 Abs. 2: ganz ersetzt (Abweichung von Review 08)? | a) **ja, `ersetzt`** – die Anweisung fasst den ganzen Absatz neu · b) `teilweise`, alte Zeile bleibt in (Doppelzählung mit Abs. 2 n.F.) |
| **P2-F4** | Art. 4a Abs. 1 lit. a–f: Nutzt der Betreiber die Erlaubnis, besondere Kategorien personenbezogener Daten zur Bias-Erkennung zu verarbeiten (Art. 4a Abs. 2)? | a) **nein, out bleibt** – bedingte Pflicht (2c), Wiedervorlage wie W-2 · b) ja, geplant → 7 Zeilen `in`, Befund je Zeile, Bezug R013 |
| **P2-F5** | Omnibus Art. 4 (Inkrafttreten am 27.07.2026): steuernd? | a) **out** – das Datum ist abgeschlossen, die Stichtage trägt Art. 113 Abs. 3 n.F. · b) `in`, steuernd, wie Art. 113 |
| **R-2** | Severity des Wächters `OMNIBUS_SUPERSEDED_UNITS_OUT` | a) **MEDIUM** wie `NORM_SENTENCE_UNITS_CURRENT` – verschiebt, wo gezählt wird, fälscht kein Zitat · b) HIGH wie `PO_DECISIONS_APPLIED` |

# Teil 4 – Befunde

| # | Befund | Wohin |
|---|---|---|
| A-W5 | **Verknüpfer:** Seit der Satzebene (T-14.3) gibt es „Art. 111 Abs. 2“ nur noch als Satz 1 und Satz 2. `link_omnibus.py` fand das Ziel nicht mehr, der Verweis auf die Neufassung ging still verloren (57 statt 58 Verweise im Bericht). | umgesetzt: Satz-Einheiten werden verknüpft; `OMNIBUS_SUPERSEDED_UNITS_OUT` meldet jeden Verweis ohne Einordnung |
| A-W6 | **Verknüpfer:** Die Neufassung von Art. 96 Abs. 1 **UAbs. 2** war mit allen sechs Buchstaben verknüpft. Der Extraktor hängt UAbs. 2 und 3 an lit. f; nur diese Einheit ist betroffen. | umgesetzt: ein späterer Unterabsatz verknüpft die letzte Untergliederung |
| A-W7 | **Extraktor Omnibus:** Einheiten, die zwei Stellen tragen – Art. 5 Abs. 1b steht in Abs. 1a lit. b · Art. 75b Überschrift und Text in einer Einheit · Folgesätze nach einer Aufzählung hängen am letzten Buchstaben (Art. 2 Abs. 13 lit. b, 4a Abs. 2 lit. b, 25 Abs. 2 lit. c, 75 Abs. 2a lit. c, 75c Abs. 4 lit. c, Abs. 5 lit. g). Wortgleich, aber falsch geschnitten. | Paket 3, Werkzeug-Ticket zusammen mit M-B2 und A-W1–A-W3 |
| P2-B1 | **Art. 25 Abs. 2 lit. a–c n.F.:** Befund Teilabdeckung vorläufig. G-OPS-06/C-25d verlangt `provider_handover_record`, prüft aber nicht, ob er das einzelne Element enthält. | Paket 3, Element-Matrix Lauf 2 (Bezug M1) |

**Nicht geliefert, und warum:**
- **A-W1 bis A-W3** (Art.-113-Kennungen, Anhang I Abschn. B ungeteilt, Fußzeile in Anhang XIII lit. g) sind Umbauten am Extraktor. Sie ändern Kennungen und Schnitte in allen sieben Pflichtenräumen und brauchen einen Neubau mit Migration wie T-14.1. Das ist ein eigenes Werkzeug-Ticket, kein Teil der Einordnung. Verschoben nach **Paket 3**, gebündelt mit M-B2 und A-W7.
- **Befunde der neuen in-Zeilen** sind Vorschläge. Die Prüfung am Rego-Code (Element-Matrix) ist Paket 3.

# Teil 5 – Stichprobe für den PO

Elf Zeilen, je eine pro Begründungsart:

| Zeile | Ergebnis | prüft |
|---|---|---|
| Art. 4 Abs. 1 n.F. | in, Lücke | Übernahme nach A-F2a (P2-F2) |
| Art. 25 Abs. 2 lit. b n.F. | in, teil (vorläufig), HYPOTHESE | neue Untergliederung, Durchschlag |
| Art. 5 Abs. 1a lit. b n.F. | in, n. e. | steuernd (Verbot nur bei Zweck des Betreibers) |
| Art. 4a Abs. 1 lit. c n.F. | out, HYPOTHESE | Adressat Anbieter, bedingt (P2-F4) |
| Art. 27 Abs. 4 n.F. | out | Bereichsausnahme (Q1 offen) |
| Art. 60 Abs. 2 n.F. | out | bedingte Pflicht |
| Art. 2 Abs. 13 lit. a n.F. | out | Systemtyp |
| Art. 75a Abs. 4 lit. a n.F. | out | Adressat Behörde, nennt den Betreiber |
| Art. 113 Abs. 3 lit. d n.F. | out | steuert keine in-Pflicht |
| Omnibus Art. 1 Nr. 12 lit. a | out | Änderungsanweisung (P2-F1) |
| Art. 4 n.F. | out | Überschrift |

**Ehrlich zur Methode:**
- Eingeordnet gruppenweise nach Adressat und Rasterschritt; jede Zeile ist gelesen und trägt Grund und Schritt.
- Wo die Grundfassung schon out war und der Omnibus den Adressaten nicht ändert, folgt die n.F.-Zeile ihr (z. B. Art. 10 Abs. 1).
- **Gegenprobe am Wortlaut:** 14 n.F.-Zeilen nennen den Betreiber.
  - 5 als Adressat einer Pflicht, Erlaubnis oder Verbotsgrenze: Art. 4 Abs. 1 · 4a Abs. 2 · 5 Abs. 1a lit. b · 111 Abs. 2 Satz 2 (alle in) · 27 Abs. 4 (out, Bereichsausnahme).
  - 9 als Empfänger einer Unterstützung oder Gegenstand einer Behördenbefugnis: Art. 4 Abs. 2 · 27 Abs. 5 · 60 Abs. 2 · 75 Abs. 1 lit. b · 75 Abs. 2a, lit. a · 75a Abs. 2 · 75a Abs. 4 lit. a · 77 Abs. 1a (alle out).
- Der `pflicht`-Text ist eine Kurzform des Belegs mit Vorsatz. Er beschreibt, er legt nicht aus.
