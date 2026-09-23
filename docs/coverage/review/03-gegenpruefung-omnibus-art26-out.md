---
titel: Gegenprüfung – Omnibus, Art. 26, Stichprobe out
stand: 2026-09-23
basis: Branch spec06-aiact-stufe0 · docs/legal/OJ_L_202601744_DE.pdf (selbst extrahiert) · docs/legal/wortlaut/aiact_2024-1689_DE.txt
status: Ergebnis – Korrekturen an 2b zur PO-Entscheidung
---

# Kurzfazit
- **Nachtlauf-Agent ist bei der Einordnung verlässlich:** 0 von 85 Zufallszeilen falsch, 28 von 28 „Betreiber"-Treffern plausibel, 130 Anbieterzeilen aus Kap. III plausibel
- **Schwächen liegen woanders:** (1) Omnibus-Inhalte teils falsch wiedergegeben · (2) Omnibus-Neuerungen fehlen als Zeilen · (3) steuernde Normen auf `out` · (4) Werkzeugfehler bei Art. 3 und doppelte IDs
- **P0 ist jetzt VERIFIZIERT**, P2 muss auf neuen Wortlaut umgestellt werden, **zwei neue Lücken**

# G1 – Omnibus-PDF selbst gelesen (Art. 1 der VO 2026/1744, Nr. 1–41)

| Punkt | Agent sagte | Wortlaut Omnibus | Urteil |
|---|---|---|---|
| Art. 26 | unverändert | nicht in der Änderungsliste (Nr. 12 = Art. 25, Nr. 13 = Art. 27) | ✅ bestätigt |
| Art. 27 Abs. 1 (Nr.-2-Ausnahme) | unverändert, nur Abs. 4/5 neu | Nr. 13 ändert nur Abs. 4 und 5 | ✅ bestätigt → 2a-Entscheid FRIA steht |
| Art. 111 Abs. 2 | Stichtag = Beginn Kap. III, Adressat „Akteure" | „…vor dem Beginn der Anwendung des Kapitels III gemäß Artikel 113 in Verkehr gebracht oder in Betrieb genommen … nur dann, wenn … in ihrer Konzeption erheblich verändert" | ✅ bestätigt |
| Art. 113 Abs. 3 lit. c | Anhang III ab 02.12.2027 | „Kapitel III Abschnitte 1, 2 und 3 … gelten ab dem: i) 2. Dezember 2027 … Anhang III" | ✅ bestätigt – Art. 26 steht in Abschnitt 3 |
| **Art. 4** | „Abs. 1 inhaltsgleich, ergänzt um Klarstellung" | alt: „sicherzustellen, dass … über ein **ausreichendes Maß** an KI-Kompetenz verfügen" → neu: „ergreifen Maßnahmen, um die **Entwicklung** der KI-Kompetenz … **zu unterstützen**" + keine Pflicht, ein Niveau zu garantieren | ❌ **falsch** – Pflicht deutlich abgeschwächt |
| Art. 5 | lit. a–h unverändert | ✅ – aber **neu: lit. ba, bb** (Deepfake intim/CSAM) + Abs. 1a, 1b, gelten ab **02.12.2026** | ⚠️ neue Verbote fehlen im Pflichtenraum |

**Belege zur Kopplung P0 ↔ G-OPS-06:**
- Erwägungsgrund 177 (Wortlaut im Repo): „der Begriff der erheblichen Veränderung … als **gleichwertig mit dem Begriff der wesentlichen Änderung** verstanden werden sollte"
- → „erheblich verändert" (Art. 111) = „wesentliche Veränderung" (Art. 3 Nr. 23) = was G-OPS-06/C-25b schon prüft
- Einschränkung: Erwägungsgrund = Auslegungshilfe, nicht verbindlich → Kopplung als HYPOTHESE mit starkem Beleg

**Weitere Nr.-2-Ausnahmen gefunden** (ergänzt Q2 aus 2a):
- Art. 49 Abs. 1 – keine EU-Datenbank für Nr. 2 (national, Abs. 5)
- Art. 43 Abs. 2 – Nr. 2–8: Konformitätsbewertung durch interne Kontrolle (keine notifizierte Stelle) → für G-DEP-04: keine NB-Nummer erwartbar
- Art. 75 Abs. 1 n.F. – KI-Büro für Nr.-2-Systeme nicht zuständig

**Offen, nicht jetzt:** Kap. IX (Art. 72/73) gilt nach Art. 113 ab 02.08.2026 – Verhältnis zum Stichtag 02.12.2027 für Hochrisiko-Pflichten ungeklärt → HYPOTHESE, eigener Prüfpunkt

# G2 – Art. 26 komplett im Volltext

| Abs. | Mein Befund | Agent | Abweichung |
|---|---|---|---|
| 1 | TOMs für Einsatz nach Betriebsanleitung – kein Gate prüft Umsetzung | teil | – |
| 2 | Übertragung an Personen mit Kompetenz/Ausbildung/Befugnis + Unterstützung | teil | – |
| 3 | Unberührtheitsklausel | out | – (G-DEP-06 zitiert Abs. 3 falsch, schon bekannt) |
| 4 | Eingabedaten | Lücke | – |
| **5** | **vier Pflichten in einer Zeile:** ① Betrieb überwachen + Anbieter nach Art. 72 informieren · ② bei Risiko (Art. 79 Abs. 1): informieren **und Verwendung aussetzen** · ③ schwerwiegender Vorfall: erst Anbieter, dann Einführer/Händler + Behörde · ④ Anbieter nicht erreichbar → Art. 73 entsprechend | teil (eine Zeile) | ⚠️ **Zeile aufteilen.** ② „aussetzen" ist nirgends abgebildet – kein Gate hat eine Wirkung „System aussetzen" (`halt_pipeline` stoppt das Deployment, nicht den laufenden Betrieb). G-PRE-05 prüft nur, dass ein kill_switch dokumentiert ist → **neue Lücke** |
| 6 | Logs ≥ 6 Monate, soweit unter Kontrolle | teil | – |
| 7 | Arbeitnehmervertreter vor Einsatz informieren | teil | – (Leitstelle = Arbeitnehmer, die dem System „unterliegen": HYPOTHESE) |
| 8, 10 | anderer Betreibertyp | out (2a) | – |
| 9 | DSFA | Lücke | – |
| **11** | Information natürlicher Personen bei Entscheidungen über sie | teil, offen | ⚠️ Hinweis: **keine Nr.-2-Ausnahme** (anders als Art. 86!) · Redispatch 2.0 steuert auch Anlagen natürlicher Personen (ab 100 kW) → spricht eher für `in` (SEKUNDÄRQUELLE, gegen EnWG §§ 13, 13a prüfen) |
| 12 | Kooperation mit Behörden | Lücke | – |

**Urteil:** Die Art.-26-Analyse des Agenten ist gut. Einziger echter Mangel: Abs. 5 ist zu grob erfasst. Die „Satzebene" aus PO-Festlegung 2 (SPEC-06) ist im Pflichtenraum nicht umgesetzt: Einheiten sind Absätze, der Befund gilt je Absatz.

# G3 – Erweiterte Stichprobe der 801 `out`

| Prüfung | Umfang | Ergebnis |
|---|---|---|
| A – **alle** out-Zeilen mit „Betreiber" im Wortlaut | 28 (voll) | 28 plausibel (Betreiber nur Empfänger, Datenquelle, Nutznießer oder anderer Betreibertyp) |
| B – **alle** Anbieterzeilen Kap. III + IX (Art. 6, 8–12, 16–22, 25, 43, 47–50, 72–74, 79–82 …) | ~130 (voll) | plausibel. Hinweis: Art. 9 komplett Anbieterpflicht → siehe Q9 |
| C – „Akteur"/„jede Person"-Treffer | 38 (voll) | **1 Fehler:** Art. 79 Abs. 2 „Die betreffenden **Akteure** arbeiten … mit der Marktüberwachungsbehörde … zusammen" – Akteur umfasst laut Art. 3 Nr. 8 den **Betreiber** (Wortlaut geprüft) → `in`, gehört zu P6 |
| D – Zufallsstichprobe, geschichtet (Seed 20260923) | 85 (45 Behörde · 25 sonstige · 15 Anbieter GPAI/Reallabor) | **0 übersehene Betreiberpflichten** · 1 steuernde Definition (Art. 3 Nr. 49 lit. b „Störung kritischer Infrastruktur") |

**Summe geprüft:** ~280 von 801 out-Zeilen (35 %), davon ~200 vollständig nach Risiko-Kriterium, 85 zufällig

# Strukturbefunde (Werkzeug / Pflichtenraum)

| ID | Befund | Wirkung |
|---|---|---|
| **T1** | **Pflichtenraum = Grundfassung.** Vom Omnibus **eingefügte** Normen haben keine Zeile: Art. 4 Abs. 2/3, 4a, 5 Abs. 1 lit. ba/bb + Abs. 1a/1b, 6 Abs. 1a–1c, 2 Abs. 13, 60a, 75 Abs. 1a–2a, 75a–d, 111 Abs. 4, 113 Abs. 3 lit. c/d n.F. Bei **geänderten** Normen zeigt `beleg` den alten Text (z. B. Art. 4, 111) | Für Betreiber relevant: Art. 5 ba/bb + 1a (neue Verbote), 4a Abs. 2 (Erlaubnis), 6 Abs. 1a/1b und 113 Abs. 3 lit. c (steuernd, von G-PRE-01 und P0 genutzt) |
| **T2** | **Art. 3 nicht nach Nummern geschnitten:** 1 Zeile mit 10.818 Zeichen + falsch geschnittene „lit."-Zeilen. **24 IDs doppelt (59 Zeilen)** – u. a. Art. 3, Art. 5 Abs. 1 lit. i, Anhang VIII | IDs nicht eindeutig → Rückverfolgung Requirement → Einheit bricht. Von Gates genutzte Definitionen (Nr. 8 Akteur, 14 Sicherheitsbauteil, 23 wesentliche Veränderung, 49 schwerwiegender Vorfall) nicht adressierbar |
| **T3** | **Satzebene nicht umgesetzt** (PO-Festlegung 2) | Mehrpflichten-Absätze wie Art. 26 Abs. 5 bekommen einen Sammelbefund |
| **T4** | **Steuernde Normen auf `out`:** Art. 2, 3, 111, 113 – das Raster verlangt `in` für Definitionen und Verweise, die eine `in`-Pflicht steuern | P0 und G-PRE-01 hängen genau daran |

# Querbefund aus G3
| ID | Befund |
|---|---|
| **Q9** | **Art. 9 (Risikomanagement) ist komplett Anbieterpflicht** – bis auf Abs. 5 lit. c. R001 (MUST, role: deployer) und G-PRE-03 hängen aber an Art. 9. Gleiches Muster wie FRIA (Q1) und Art. 50 (Q6): **deployer-Requirements auf Anbieterartikeln** (R001 Art. 9, R002 Art. 11, R003 Art. 15, R005 Art. 12/15, R006 Art. 10, R013 Art. 9/10/15). HANDBUCH kennt das für G-DEP-01 – der Pflichtenraum zeigt: es ist **katalogweit** → Thema für 2c (die meisten der 33 Teilabdeckungen liegen in Art. 13–15) |
| Q10 | Art. 99 Abs. 7 lit. g/h: Bußgeldhöhe berücksichtigt „ergriffene technische und organisatorische Maßnahmen" und ob der Akteur den Verstoß gemeldet hat → **Nutzenargument für den Evidence Store** (BIZDEV), keine Pflicht |

# Korrekturen an Schritt 2b (Vorschlag)

| Paket | Änderung |
|---|---|
| **P0 Anwendbarkeit** | HYPOTHESE → **VERIFIZIERT** (Art. 111 Abs. 2 + Art. 113 Abs. 3 lit. c i n.F.). Kopplung an G-OPS-06/C-25b über Erwägungsgrund 177 |
| **P1 Verbote** | + Art. 5 Abs. 1 lit. **ba, bb** + Abs. 1a lit. b (ab 02.12.2026) → Zeilen fehlen (T1) |
| **P2 KI-Kompetenz** | Auf **neuen Wortlaut** umstellen: geprüft wird „Maßnahmen zur Unterstützung der Kompetenzentwicklung vorhanden", **nicht** „ausreichende Kompetenz sichergestellt". Prio bleibt 2 (Aufwand kleiner) |
| **P6 Vorfall & Behörden** | + Art. 79 Abs. 2 (Kooperation der Akteure) |
| **P8 NEU – Aussetzen bei Risiko** | Art. 26 Abs. 5 Satz 2: Betreiber setzt die Verwendung aus. Maßnahme: neue Gate-Wirkung `suspend_use` (Frage 5) + Kopplung Risiko-Signal (G-OPS-03 Drift, G-OPS-02 Schwellen) → kill_switch aus G-PRE-05. Prio **2** |

**Zählung neu (falls PO zustimmt):** echte Lücken 20 → **24** (+ Art. 5 ba, bb · Art. 79 Abs. 2 · Art. 26 Abs. 5 Aussetzen) in **8 Paketen**

# Vorschlag Tooling-Ticket (T-14, vor Anhänge-Lauf)
1. Art. 3 nach Nummern schneiden, IDs eindeutig machen (Integrity-Check: `NORM_UNIT_IDS_UNIQUE`)
2. Omnibus-Neufassungen als eigene Einheiten (`quelle: 2026/1744`) mit Offset im Omnibus-Text
3. Art. 26 Abs. 5 (und andere Mehrpflichten-Absätze) auf Satzebene
4. Raster-Ergänzungen aus 2a einarbeiten (Systemtyp, bedingte Pflicht) + steuernde Normen = `in`

# PO-Entscheidungen
1. Korrekturen an 2b übernehmen (P0 verifiziert, P1/P2/P6 angepasst, P8 neu)?
2. Tooling-Ticket T-14 **vor** dem Anhänge-Lauf und vor 2c?
3. Q9 (deployer-Requirements auf Anbieterartikeln) als Leitfrage für 2c?
