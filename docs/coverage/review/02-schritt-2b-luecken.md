---
titel: Schritt 2b – Lücken (Version 2, konsolidiert)
stand: 2026-09-23
basis: Branch spec06-aiact-stufe0 · Raster T-13 + Ergänzungen 2a · Gegenprüfung (03) · Omnibus selbst gelesen
status: ENTSCHIEDEN 23.09.2026 – alle Empfehlungen E1–E8 vom PO angenommen
version: 2 (v1 → v2: Gegenprüfung eingearbeitet, Omnibus-Feld geprüft, Verifikationsstufen, steuernde Normen)
---

# PO-Entscheide bisher
| Datum | Schritt | Entscheid |
|---|---|---|
| 23.09.2026 | 1 | Systembild bestätigt |
| 23.09.2026 | 2a | 17 Zeilen → out (Gruppen A–C) · Art. 5 lit. e/f/g → luecke · Art. 60 Abs. 4 h/j → out mit Bedingung · Raster ergänzt um „Systemtyp" und „bedingte Pflicht" |
| 23.09.2026 | 2b | **E1–E8 angenommen** (Teil 7): 7 Zeilen umklassifiziert · 24 Lücken in P0–P8 · R015/R016 grundsätzlich ja · Durchschlagsregel · steuernde Normen `in` · Omnibus-Korrekturen · Bauverbot Meldekaskade für Planung aufgehoben (Bau erst Schritt 5) · T-14 vor 2c |
| 23.09.2026 | T-14 | **P-1 = a** (Omnibus als zweite gehashte Quelle) · **P-2 = b** (Satzebene nur für Mehrpflichten-Absätze) |

> **Umsetzung im Pflichtenraum:** Die Entscheide werden mit T-14 in `aiact_pflichtenraum.yaml` übernommen (`po_bestaetigt: true` für die entschiedenen Zeilen). Bis dahin gilt dieses Dokument als Entscheidungsnachweis.

# Teil 0 – Müssen alle Ergebnisse der Nachtläufe neu hinterfragt werden?

**Nein – gezielt dort, wo ein Fehlermuster gefunden wurde. Das ist mit dieser Version erledigt.**

| Ergebnisart | Geprüft | Fehlerquote | Folge |
|---|---|---|---|
| `scope` in/out | ~280 von 801 out (35 %), davon ~200 vollständig nach Risiko | 1 Fehler (Art. 79 Abs. 2) | **hält** – keine Neubewertung nötig; Rest per Sammelbestätigung (Schritt 5c) |
| `adressat` / Art. 26 | Art. 26 im Volltext | 0 inhaltlich, 1 zu grob (Abs. 5) | **hält** – Abs. 5 teilen |
| `omnibus`-Feld | alle Einheiten gegen Änderungsliste Nr. 1–43 | in-Zeilen: 1 von 4 geänderten **falsch** (Art. 4) · out-Zeilen: 5 kleine Fehler, alle ohne Betreiberbezug | **korrigiert** (Teil 5) |
| `verifikation` | alle 58 in-Zeilen | 80/81 VERIFIZIERT war zu hoch | **neu vorgeschlagen** (Teil 3) |
| steuernde Normen | Art. 2, 3, 6, 111, 113, Anhang III | systematisch auf out | **neu vorgeschlagen** (Teil 4) |
| Werkzeug | Pflichtenraum-Struktur | Art. 3 ungeschnitten, 24 doppelte IDs, Omnibus-Neuerungen fehlen | **Ticket T-14** |

**Noch nicht geprüft und bewusst offen:** 180 Einheiten (Anhänge + Art. 113) – laufen erst nach T-14 · Teilabdeckungen (33) – Schritt 2c

# Teil 1 – Umklassifizieren (7)

| Einheit | Heute | Vorschlag | Grund |
|---|---|---|---|
| Art. 111 Abs. 2 | luecke | **nicht_einschlägig (steuernd)** → Maßnahme P0 | Anwendbarkeitsregel, keine Pflicht |
| Art. 73 Abs. 5 | luecke | **nicht_einschlägig (Erlaubnis)** | „kann … vorlegen" → Designvorgabe „Erstbericht" für G-OPS-02 |
| Art. 50 Abs. 3, 4, 5 | luecke | **out (Systemtyp)** | nur Emotionserkennung / biometrische Kategorisierung / Deepfake |
| Art. 49 Abs. 5 | luecke | **out (Adressat Anbieter)** · HYPOTHESE | Registrierung durch Anbieter (Art. 49 Abs. 1); relevant erst in K2/K3 |
| **Art. 79 Abs. 2** | out | **in → luecke (P6)** · HYPOTHESE | „Die betreffenden Akteure arbeiten … zusammen" – Akteur umfasst Betreiber (Art. 3 Nr. 8, Wortlaut geprüft) |

# Teil 2 – 24 echte Lücken in 8 Paketen + P0

| Paket | Einheiten | Maßnahme | Wohin | Beweisstufe | Prio |
|---|---|---|---|---|---|
| **P0 Anwendbarkeit** (steuernd) | Art. 111 Abs. 2 n.F. · Art. 113 Abs. 3 lit. c n.F. | Check „vor 02.12.2027 in Betrieb + keine wesentliche Veränderung → Kap. III gilt nicht" | G-PRE-01 (Typ-3-Regel) + G-OPS-06/C-25b | E-0 → E-1 | **1** |
| **P1 Verbote** (10) | Art. 5 Abs. 1 lit. a, b, c, c-i/ii, d, e, f, g · **neu** lit. ba, bb (ab 02.12.2026, Zeilen fehlen) | R015 + **ein** Check „Art.-5-Screening" | G-PRE-01 | E-0 | **1** |
| **P2 KI-Kompetenz** (4) | Art. 4 n.F. · Art. 9 Abs. 5 lit. c · Art. 14 Abs. 4 lit. b, c | R016 + Check „Maßnahmen zur **Unterstützung** der Kompetenzentwicklung je Aufsichtsrolle" (nicht: Niveau garantiert) | G-PRE-05 | E-0 → E-1 | 2 |
| **P3 Betriebsanleitung** (2) | Art. 13 Abs. 3 lit. c, e | Check „Pflichtinhalte Art. 13 Abs. 3" = Checkliste B1 | G-DEP-04 | E-0 → E-1 | 2 |
| **P4 Eingabedaten** (1) | Art. 26 Abs. 4 | R006 → Laufzeit-Check Eingaben gegen Anbieter-Spezifikation | neuer Check nach Muster G-OPS-03 | E-3 | 2 |
| **P8 Aussetzen bei Risiko** (1) | Art. 26 Abs. 5 Satz 2 (nach Teilung) | neue Gate-Wirkung `suspend_use` + Kopplung Risikosignal → kill_switch | G-OPS-02 / G-OPS-03 (Frage 5) | E-3 | 2 |
| **P5 Aufsicht wirksam** (2) | Art. 14 Abs. 2, Abs. 3 lit. a | R008 → G-OPS-01 auf Laufzeit (Override-Rate, Zeit bis Entscheidung) | G-OPS-01 (+ G-DEP-04 für 3a) | E-3 / E-2 | 3 |
| **P6 Vorfall & Behörden** (3) | Art. 20 Abs. 2 · Art. 26 Abs. 12 · Art. 79 Abs. 2 | Kooperationsprozess + Behördenkontakt | Ausbau G-OPS-02 | E-0 | 3 |
| **P7 Datenschutz** (1) | Art. 26 Abs. 9 | „DSFA-Referenz ODER begründet: keine personenbezogenen Daten" | G-PRE-03 | E-0 | 3 |

**Summe:** 10 + 4 + 2 + 1 + 1 + 2 + 3 + 1 = **24**

```
Prio 1:  P0 Anwendbarkeit ─► P1 Verbote            (billig, gilt schon / entscheidet alles)
Prio 2:  P2 Kompetenz · P3 Betriebsanleitung · P4 Eingabedaten · P8 Aussetzen
Prio 3:  P5 Aufsicht wirksam · P6 Vorfall · P7 Datenschutz   (Ground Truth / Bauverbot / Tatsachenfrage)
```

# Teil 3 – Verifikationsstufe der 58 in-Zeilen

**Regel:** VERIFIZIERT nur, wenn der Betreiber in der Einheit oder ihrem Einleitungssatz genannt ist. Jeder Durchschlag Anbieter → Betreiber ist Auslegung = HYPOTHESE.

| Vorschlag | Anzahl | Einheiten |
|---|---|---|
| **VERIFIZIERT** | 25 | Art. 4 · Art. 5 Abs. 1 lit. a–g (8, Verbot der „Verwendung" im Wortlaut) · Art. 20 Abs. 2 · Art. 25 Abs. 1 + lit. a–c (4) · Art. 26 Abs. 1, 2, 4, 5, 6, 7, 9, 11, 12 (9) · Art. 73 Abs. 5 · Art. 111 Abs. 2 (n.F. „Akteure") |
| **HYPOTHESE** | 33 | Art. 9 Abs. 5 lit. c · Art. 13 (11) · Art. 14 (11) · Art. 15 (4) · Art. 25 Abs. 2 · Art. 73 Abs. 1–4, 9 (5) |

**Statt 33 Einzelentscheide – eine Sammelentscheidung „Durchschlagsregel":**
> Eine Anbieterpflicht ist für den Betreiber `in`, wenn **(a)** ihr Wortlaut den Betreiber als Empfänger oder Zweck nennt (z. B. Art. 13 „damit die Betreiber …", Art. 14 Abs. 4 „Personen, denen die Aufsicht übertragen wurde") **oder (b)** Art. 26 auf sie verweist (Abs. 1 → Art. 13, Abs. 2 → Art. 14, Abs. 5 → Art. 72/73, Abs. 9 → Art. 13).

- Bestätigt der PO die Regel, bleiben die 33 Zeilen HYPOTHESE, aber mit **einem** begründeten Anker statt 33 Einzelurteilen
- Diese Regel ist zugleich die Leitfrage für 2c (Q9): Welche Betreiber-Requirements hängen an Anbieterartikeln **ohne** (a) oder (b)?

# Teil 4 – Steuernde Normen (Raster: steuernde Definition/Verweisung = `in`, Befund `nicht_einschlägig`)

| Norm | Heute | Steuert | Hinweis |
|---|---|---|---|
| Art. 2 Abs. 1 lit. b | out | dass Betreiber überhaupt erfasst sind | – |
| Art. 3 Nr. 4, 8, 14 n.F., 23, 49 | nicht adressierbar | Betreiber, Akteur, Sicherheitsbauteil, wesentliche Veränderung, schwerwiegender Vorfall – genutzt von G-PRE-01, G-OPS-02, G-OPS-06 | **erst nach T-14** |
| Art. 6 Abs. 2, Abs. 3 + lit. a–d | out | Hochrisiko-Einstufung – G-PRE-01 prüft genau das | – |
| Art. 6 Abs. 1a, 1b, 1c n.F. | fehlen | Sicherheitsbauteil-Klarstellung – G-PRE-01/C-A3…A6 | **erst nach T-14** |
| Art. 4a Abs. 2 n.F. | fehlt | Erlaubnis für Betreiber (Bias-Daten) – R013 stützt sich darauf | Befund: nicht_einschlägig (Erlaubnis) |
| Art. 113 Abs. 3 lit. a, c n.F. | unbewertet | Stichtage – P0 | **erst nach T-14** |
| Anhang III Nr. 2 | unbewertet | Einstufung, auf der das ganze Vorhaben ruht | im Anhänge-Lauf zuerst |

**Befund dazu (für T-14):** Gates und Requirements zitieren Normen, die im Pflichtenraum `out`, unbewertet oder nicht vorhanden sind (u. a. Art. 3 Nr. 14, Art. 3 Abs. 49, Art. 4a, Art. 6 Abs. 1a–1c, Anhang III Nr. 2, Art. 16, 47, 48, 97). → Vorschlag Integrity-Check `NORM_REFS_RESOLVE`: jede `legal_ref` muss auf eine Einheit zeigen, die `in` ist oder deren `out` begründet, warum ein Gate trotzdem darauf verweist.

# Teil 5 – Omnibus-Feld: Ergebnis der Vollprüfung

| Einheit | scope | Agent | Wortlaut Omnibus | Korrektur |
|---|---|---|---|---|
| **Art. 4** | in | „Abs. 1 inhaltsgleich" | Pflicht von „sicherstellen … ausreichendes Maß" zu „Entwicklung … unterstützen" | `pflicht` und `omnibus` neu fassen (P2) |
| Art. 25 Abs. 2 | in | geändert, lit. a–c neu | ✅ korrekt | lit. a–c als eigene Einheiten (T-14) |
| Art. 27 Abs. 4 | in→out | geändert | ✅ korrekt | – |
| Art. 111 Abs. 2 | in | geändert | ✅ korrekt | – |
| Art. 56 Abs. 6 | out | „unverändert" | Nr. 21 ändert Abs. 6 | Feld korrigieren (kein Betreiberbezug) |
| Art. 95 Abs. 4 | out | „unverändert" | Nr. 35 ändert Abs. 4 | dto. |
| Art. 60 Abs. 2 | out | „unverändert – … neu gefasst" | Nr. 24 lit. b ändert Abs. 2 | Widerspruch im Feld auflösen |
| Art. 58 Abs. 2 lit. b | out | „geändert" | nicht geändert (Nr. 23 betrifft Abs. 1) | dto. |
| Art. 75 Abs. 2 | out | „geändert" | Abs. 2 selbst unverändert (neu: 1a–1e, 2a) | dto. |
| 180 Einheiten | – | leer | Anhang I (Nr. 41), Anhang VIII Abschn. B Nr. 7, 9 gestrichen (Nr. 42), Anhang XIV neu (Nr. 43), Art. 113 (Nr. 40) | im Anhänge-Lauf |

**Zusatzfund:** Art. 42 Abs. 3 n.F. – ein Hochrisiko-System, das die Cyber-Resilience-Act-Bedingungen erfüllt, **gilt als konform mit Art. 15 Cybersicherheit** → betrifft R003 / G-OPS-04 und den späteren Sektorstapel (Crosswalk)

# Teil 6 – Querbefunde (Stand)
| ID | Befund | Wo weiter |
|---|---|---|
| Q1 | FRIA ohne Pflicht (R012, G-PRE-02, G-PRE-05) | Schritt 3 |
| Q2 | Nr.-2-Ausnahmen: Art. 27, 43 Abs. 2, 49 Abs. 1/3, 75 Abs. 1 n.F., 86 | Fachbeitrag |
| Q6 | Art. 50 in R007 stammt aus Healthcare | 2c |
| Q7 | Bauverbot Meldekaskade – Wortlaut liegt jetzt geprüft vor | Entscheid Teil 7 |
| Q8 | Stichtag 02.12.2027 → HANDBUCH 4.3 ergänzen | Schritt 5 |
| Q9 | Betreiber-Requirements auf Anbieterartikeln (R001, R002, R003, R005, R006, R013) | 2c, Leitfrage |
| Q10 | Art. 99 Abs. 7: TOMs mindern Bußgeld → Nutzenargument Evidence Store | BIZDEV |
| Q11 | Art. 26 Abs. 11: keine Nr.-2-Ausnahme, Redispatch 2.0 betrifft auch Anlagen natürlicher Personen | 2c |

# Teil 7 – Entscheidungsvorlage

Je Punkt eine Empfehlung. „Alles ok" übernimmt alle Empfehlungen.

| # | Entscheidung | Empfehlung |
|---|---|---|
| E1 | Teil 1: 7 Zeilen umklassifizieren | **ja** |
| E2 | Teil 2: 24 Lücken in P0–P8 mit Prioritäten | **ja** |
| E3 | Neue Requirements R015 (Art. 5) und R016 (Art. 4) grundsätzlich | **ja** – Artikel und MUST/SHOULD je Requirement in Schritt 4 |
| E4 | Teil 3: Durchschlagsregel als Sammelentscheid | **ja** |
| E5 | Teil 4: steuernde Normen auf `in` / nicht_einschlägig | **ja**, Umsetzung nach T-14 |
| E6 | Teil 5: Omnibus-Korrekturen in den Pflichtenraum | **ja**, mit T-14 |
| E7 | Q7 Bauverbot Meldekaskade | **aufheben für P6/P8-Planung**, Bau erst in Schritt 5 |
| E8 | T-14 vor 2c und vor dem Anhänge-Lauf | **ja** |
