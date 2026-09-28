---
titel: Schritt 2c – die 44 Teilabdeckungen
stand: 2026-09-28
basis: Branch review-2c (ab t14-pflichtenraum-werkzeug 0d81d18) · Pflichtenraum nach T-14.5 · Leitfrage Q9 (02, Teil 3 und 6)
status: ENTSCHIEDEN 28.09.2026 – F1a–F6a angenommen
---

# PO-Entscheid 28.09.2026
- **F1a–F6a angenommen.**
- Im Pflichtenraum umgesetzt (F1, F2): `docs/coverage/entscheide/2026-09-28_schritt-2c.yaml` – 33 Zeilen neu bestätigt, 5 umklassifiziert. AI-Act-Raum danach: 85 `in` · 28 Lücken · 39 Teilabdeckungen · 15 nicht einschlägig · 3 gedeckt · 86 Zeilen bestätigt.
- In Schritt 4 umzusetzen: F3 (Anker R006, R007, R010, R013), F4 (Anker-Suche für R001, R002, R003, R005, R011 im Sektorstapel; bis dahin als offen kennzeichnen), F5 (G-OPS-02 umbauen), F6 (R017 Rollenwechsel).
- Offen: Art. 15 (7 Zeilen) bis zum Anker aus F4 · Art. 26 Abs. 11 in Schritt 3.

# Kurzfazit
- **44 Zeilen** stehen auf `teilabdeckung`. **39 zu Recht.** Keine ist in Wahrheit gedeckt.
- Sie fallen in **sechs Cluster** (Teil 1). Der fehlende Teil ist fast überall derselbe: **Das Gate prüft, dass etwas deklariert ist, nicht was drinsteht oder ob es wirkt** (E-0 statt Inhalt oder Wirkung).
- **Fünf Zeilen sind falsch eingeordnet (F2):**
  - Art. 26 Abs. 5 UAbs. 1 Satz 5 und UAbs. 2 betreffen einen anderen Betreibertyp → `out`
  - Art. 15 Abs. 4 UAbs. 2 ist ein Mittel („kann … erreicht werden“), keine Pflicht → `nicht_einschlaegig`
  - Art. 26 Abs. 7 (Arbeitnehmer unterrichten) und Art. 15 Abs. 4 UAbs. 3 (Rückkopplungsschleifen) trifft **kein** Check → `luecke`. Beide wurden erst durch die Satzteilung bzw. den genauen Blick in G-DEP-03/C-01 sichtbar.
- **Q9 (Teil 3):** 5 von 14 Requirements haben für den Betreiber **keinen Anker im AI Act** (R001, R002, R003, R005, R011). 4 haben einen besseren Anker als den heutigen (R006, R007, R010, R013).
- **Neuer Befund Art. 73 (Teil 4):** G-OPS-02 behandelt die Meldefristen als eigene Betreiberpflicht. Für den Betreiber gilt Art. 73 aber nur, wenn er den Anbieter nicht erreicht (Art. 26 Abs. 5 Satz 4). Und die Reduktion auf Grundrechtsvorfälle (Abs. 9) hängt am **Anbieter**, nicht am Betreiber.

```
44 Teilabdeckungen
 ├─ T-A Betriebsanleitung      12  → P3 erweitern: Inhaltscheck statt Existenzcheck
 ├─ T-B Menschliche Aufsicht    8  → P2 + P5 + Stopptasten-Übung
 ├─ T-C Robustheit/Cyber        6  → hängt an Q9 (F4); CRA-Vermutung nutzen
 ├─ T-D Rollenwechsel           3  → Requirement R017 (F6)
 ├─ T-E Art. 26 Kernpflichten   9  → 2× out (F2), Rest: Umsetzung, Aufbewahrung, Unterrichtung
 └─ T-F Meldung Art. 73         6  → G-OPS-02 umbauen (F5)
```

# Teil 1 – Cluster und Maßnahmen

| Cluster | Zeilen | Was fehlt (gemeinsam) | Maßnahme | Wohin | Prüfbar in Pipeline | E möglich |
|---|---|---|---|---|---|---|
| **T-A Betriebsanleitung** (Art. 13, 15 Abs. 3) | 12 | G-DEP-03/C-01 prüft, *dass* eine Anleitung existiert, nicht die Pflichtinhalte nach Art. 13 Abs. 3 und nicht die Qualität nach Abs. 1/2 | **M-A1** P3 erweitern zu *einem* Check „Pflichtinhalte Betriebsanleitung“: strukturierte Felder für Abs. 3 lit. a–f inkl. lit. b Ziff. i–vii und Art. 15 Abs. 3 · **M-A2** Qualität (präzise, vollständig, verständlich, barrierefrei) als manuelles Review | G-DEP-04 (P3) | M-A1 ja · M-A2 HYBRID | E-0 → E-1 (Anleitung vom Anbieter signiert) · Ziff. ii: E-2 (deklarierte Genauigkeit vs. gemessene aus G-DEP-02) |
| **T-B Menschliche Aufsicht** (Art. 14, 26 Abs. 2) | 8 | G-PRE-05 und G-OPS-01 prüfen Dokumentation der Aufsicht, nicht Kompetenz, Wirksamkeit und sicheren Stillstand; Kette Anbieter-Vorgabe → Betreiber-Umsetzung fehlt | **M-B1** = P5 (Override-Rate, Zeit bis Entscheidung) · **M-B2** = P2 (Kompetenzmaßnahmen je Rolle) · **M-B3** neu: Stopptasten-Übung mit Nachweis „sicherer Zustand erreicht“, nicht älter als N Tage · **M-B4** neu: Abgleich Aufsichtsmodell des Betreibers ↔ Aufsichtsmaßnahmen aus der Anleitung (Feld lit. d aus M-A1) | G-OPS-01 | ja | M-B3: E-2/E-3 · M-B4: E-0 → E-1 |
| **T-C Robustheit/Cybersicherheit** (Art. 15 Abs. 1, 4, 5) | 6 | Modellebene nur deklariert (E-0); Rückkopplungsschleifen und KI-spezifische Angriffe (Poisoning, Adversarial) prüft kein Gate | **zuerst F4** (kein Betreiber-Anker) · dann **M-C1** Tatsachenfeld „lernt im Betrieb weiter?“ – nur bei ja gilt UAbs. 3 → Rückkopplungsmetrik in G-OPS-03 · **M-C2** KI-Angriffe: Anbieter-Nachweis über die Anleitung (M-A1, Ziff. ii) statt eigener Tests · **M-C3** CRA-Vermutung Art. 42 Abs. 3 n.F. als Eingangsnachweis · **M-C4** Infrastruktur-Sicherheit (G-PRE-04, G-OPS-04) im Sektorstapel an NIS2/BSIG verankern | G-PRE-01, G-OPS-03, G-DEP-04 | M-C1, M-C3 ja · M-C2 nur Nachweis | M-C3: E-1 (Konformitätserklärung) |
| **T-D Rollenwechsel** (Art. 25) | 3 | kein Requirement (SPEC-06 Befund 1); C-25b nur SHOULD mangels Schwelle; Trigger `notify` nur deklariert | **M-D1** Requirement R017 (F6) · **M-D2** eine Schwellendefinition „wesentliche/erhebliche Veränderung“ für C-25b **und** P0 (Art. 3 Nr. 23 ↔ Art. 111 Abs. 2, Erwägungsgrund 177) · **M-D3** `notify` bauen (Schritt 5) · Folgepflichten nach Art. 16: bewusst offen (K2/K3) | G-OPS-06 | ja | E-0 → E-1 |
| **T-E Art. 26 Kernpflichten** | 9 | Umsetzung der Anleitung, Überwachung, Meldekaskade, tatsächliche Aufbewahrung, Unterrichtung der Arbeitnehmer – je nur deklariert oder gar nicht | **M-E1** Abs. 1: Einsatzgrenzen aus der Anleitung (M-A1) als Deployment-Policy · **M-E2** Abs. 5 S. 1: G-OPS-03 ist die Überwachung, dazu Trigger „Anbieter informieren“ · **M-E3/E4** Abs. 5 S. 3/4: Reihenfolge der Meldekette und Fallback-Pfad in G-OPS-02 (P6) · **M-E5** Abs. 6: tatsächliche Aufbewahrung messen (ältester Eintrag, Lückenlosigkeit) · **M-E6** Abs. 7: eigenes Feld „Arbeitnehmervertretung unterrichtet“ vor Inbetriebnahme · 2 Zeilen out, Abs. 7 Lücke (F2) · Abs. 11 vertagt (Q11) | G-DEP-04, G-OPS-03, G-OPS-02, G-DEP-06, G-PRE-05 | ja | M-E1: E-2 · M-E5: E-3 · M-E6: E-1 |
| **T-F Meldung Art. 73** | 6 | Fristen als Betreiberpflicht modelliert, gelten aber nur im Fallback; Reduktion Abs. 9 an falscher Bedingung; Fristenuhr fehlt | **M-F1** Frist-Arm nur im Fallback · **M-F2** Reduktion an Anbieter-Status koppeln · **M-F3** Fristenuhr (P6, Bau in Schritt 5) | G-OPS-02 | ja | E-0 → E-3 (Uhr) |

**Neu gegenüber 2b:** M-B3, M-B4, M-C1–C4, M-D2, M-E1, M-E2, M-E5, M-E6, M-F1, M-F2. Alles andere hängt an bestehenden Paketen (P2, P3, P5, P6).

# Teil 2 – Zeile für Zeile

`bestätigbar` = mit F1a und F2a sind scope, befund und verifikation entschieden → `po_bestaetigt: true`. **✓\*** = schon bestätigt (T-14.1).

| # | Einheit | C | Was fehlt | Schließt | bestätigbar |
|---|---|---|---|---|---|
| 1 | Art. 13 Abs. 1 | A | materielle Transparenz („hinreichend, damit Betreiber interpretieren können“) | M-A2 | ✓ |
| 2 | Art. 13 Abs. 2 | A | Qualitätsmerkmale der Anleitung | M-A2 | ✓ |
| 3 | Art. 13 Abs. 3 | A | Einleitung zu lit. a–f – Befund folgt den Buchstaben | M-A1 | ✓ |
| 4 | Art. 13 Abs. 3 lit. b | A | Einleitung zu Ziff. i–vii | M-A1 | ✓ |
| 5 | Art. 13 Abs. 3 lit. b Ziff. i | A | Zweckbestimmung als Pflichtfeld der Anleitung | M-A1 | ✓ |
| 6 | Art. 13 Abs. 3 lit. b Ziff. ii | A | Genauigkeit/Robustheit/Cyber-Maße in der Anleitung; Abgleich mit Messung | M-A1 (+E-2 gegen G-DEP-02) | ✓\* |
| 7 | Art. 13 Abs. 3 lit. b Ziff. iii | A | bekannte Risikoumstände in der Anleitung | M-A1 | ✓\* |
| 8 | Art. 13 Abs. 3 lit. b Ziff. v | A | Leistung für Personengruppen in der Anleitung | M-A1 (Bezug G-DEP-05) | ✓ |
| 9 | Art. 13 Abs. 3 lit. b Ziff. vi | A | Eingabedaten-Spezifikation in der Anleitung | M-A1 – liefert die Spezifikation, gegen die P4 zur Laufzeit prüft | ✓\* |
| 10 | Art. 13 Abs. 3 lit. d | A | Aufsichtsmaßnahmen in der Anleitung | M-A1 → M-B4 | ✓ |
| 11 | Art. 13 Abs. 3 lit. f | A | Beschreibung der Protokollierungsmechanismen | M-A1 (Bezug G-DEP-06) | ✓ |
| 12 | Art. 15 Abs. 3 | A | Genauigkeitsmetriken in der Anleitung | M-A1 | – (F4) |
| 13 | Art. 14 Abs. 1 | B | Beaufsichtigbarkeit als Systemeigenschaft (Anbieter) | M-B4 (Nachweis über Anleitung) | ✓ |
| 14 | Art. 14 Abs. 3 | B | Angemessenheit der Maßnahmen | manuelles Review bleibt – bewusst | ✓ |
| 15 | Art. 14 Abs. 3 lit. b | B | Kette Anbieter-Vorgabe → Betreiber-Umsetzung | M-B4 | ✓ |
| 16 | Art. 14 Abs. 4 | B | Befähigung der Aufsichtspersonen | M-B2 (P2) | ✓ |
| 17 | Art. 14 Abs. 4 lit. a | B | Fähigkeit, Anomalien zu erkennen | M-B2 (P2) + M-B1 (P5) | ✓ |
| 18 | Art. 14 Abs. 4 lit. d | B | Override wird genutzt (Rate) | M-B1 (P5) | ✓ |
| 19 | Art. 14 Abs. 4 lit. e | B | sicherer Stillstand nachgewiesen | M-B3 | ✓ |
| 20 | Art. 26 Abs. 2 | B | Kompetenz, Ausbildung, Befugnis, Unterstützung | M-B2 (P2) + M-B1 (P5) | ✓ |
| 21 | Art. 15 Abs. 1 | C | Modellebene nur deklariert | F4, dann M-C3/M-C4 | – (F4) |
| 22 | Art. 15 Abs. 4 UAbs. 1 Satz 1 | C | Widerstandsfähigkeit gegen Fehler | F4, dann M-C2 | – (F4) |
| 23 | Art. 15 Abs. 4 UAbs. 1 Satz 2 | C | technische und organisatorische Maßnahmen | F4, dann M-C4 | – (F4) |
| 24 | Art. 15 Abs. 4 UAbs. 2 Satz 1 | C | – Mittel („kann … erreicht werden“), keine Pflicht | **F2: nicht_einschlaegig** | – (F4) |
| 25 | Art. 15 Abs. 4 UAbs. 3 Satz 1 | C | Rückkopplungsschleifen – kein Gate prüft sie | **F2: luecke** · F4, dann M-C1 | – (F4) |
| 26 | Art. 15 Abs. 5 | C | Poisoning, Adversarial, Evasion | F4, dann M-C2 | – (F4) |
| 27 | Art. 25 Abs. 1 | D | Requirement fehlt; Folgepflichten (Art. 16) | M-D1; Art. 16 bewusst offen | ✓ |
| 28 | Art. 25 Abs. 1 lit. b | D | Schwelle „wesentliche Veränderung“ | M-D2 | ✓ |
| 29 | Art. 25 Abs. 2 | D | Kooperation wird nicht angestoßen (`notify`) | M-D3 | ✓ |
| 30 | Art. 26 Abs. 1 | E | Umsetzung der Anleitung im Betrieb | M-E1 | ✓ |
| 31 | Art. 26 Abs. 5 UAbs. 1 Satz 1 | E | Überwachung als Tatsache; Information an Anbieter | M-E2 | ✓ |
| 32 | Art. 26 Abs. 5 UAbs. 1 Satz 3 | E | Reihenfolge Anbieter → Einführer/Händler → Behörde | M-E3 (P6) | ✓ |
| 33 | Art. 26 Abs. 5 UAbs. 1 Satz 4 | E | Fallback bei unerreichbarem Anbieter | M-E4 (P6) + M-F1 | ✓ |
| 34 | Art. 26 Abs. 5 UAbs. 1 Satz 5 | E | – betrifft Betreiber, die Strafverfolgungsbehörden sind | **F2: out** | ✓ |
| 35 | Art. 26 Abs. 5 UAbs. 2 Satz 1 | E | – betrifft Betreiber, die Finanzinstitute sind | **F2: out** | ✓ |
| 36 | Art. 26 Abs. 6 | E | tatsächliche Aufbewahrung ≥ 6 Monate | M-E5 | ✓ |
| 37 | Art. 26 Abs. 7 | E | Unterrichtung Arbeitnehmervertretung – G-DEP-03/C-01 nennt sie nicht, kein Check trifft sie | **F2: luecke** · M-E6 | ✓ |
| 38 | Art. 26 Abs. 11 | E | Betrifft Redispatch Entscheidungen über natürliche Personen? | **vertagt** (Q11, Schritt 3) | – |
| 39 | Art. 73 Abs. 1 | F | Meldepflicht des Betreibers nur im Fallback | M-F1 | ✓ |
| 40 | Art. 73 Abs. 2 UAbs. 1 Satz 1 | F | Fristbeginn bei Kenntnis des Betreibers; Uhr | M-F1 + M-F3 | ✓ |
| 41 | Art. 73 Abs. 2 UAbs. 2 Satz 1 | F | Abstufung nach Schwere | in C-04 abgebildet, Uhr fehlt (M-F3) | ✓ |
| 42 | Art. 73 Abs. 3 | F | 48-h-Frist läuft nicht wirklich | M-F3 | ✓ |
| 43 | Art. 73 Abs. 4 | F | 10-Tage-Frist läuft nicht wirklich | M-F3 | ✓ |
| 44 | Art. 73 Abs. 9 | F | Reduktion hängt am Anbieter | M-F2 | ✓ |

**Summe:** bestätigbar 36 (davon 3 schon bestätigt) · wartet auf F4: 7 (Art. 15) · vertagt: 1 (Art. 26 Abs. 11)

# Teil 3 – Q9: Welche Requirements hängen an Anbieterartikeln?

Regel aus 2b (E4): Eine Anbieterpflicht ist für den Betreiber `in`, wenn (a) ihr Wortlaut den Betreiber nennt oder (b) Art. 26 auf sie verweist.

| Req | heute (`eu_ai_act_refs`) | Status im Pflichtenraum | Anker für den Betreiber | Vorschlag |
|---|---|---|---|---|
| R001 Risikomanagement (MUST) | Art. 9 | out – Anbieter (bis auf Abs. 5 lit. c) | **keiner** im AI Act | F4 – Anker im Sektorstapel: Risikomanagement ist Pflicht des KRITIS-Betreibers nach NIS2/BSIG |
| R002 Techn. Dokumentation (MUST) | Art. 11 | out – Anbieter | **keiner** | F4 |
| R003 Robustheit/Cyber (MUST) | Art. 15 | in – HYPOTHESE ohne Anker | **keiner** benannt | F4 – Infrastruktur über NIS2/BSIG; Art. 42 Abs. 3 n.F. (CRA-Vermutung) als Eingangsnachweis |
| R005 Evidence-Persistierung (MUST) | Art. 12, 15 | out / in ohne Anker | **keiner** – Betreiberpflicht zu Logs steht in Art. 26 Abs. 6 (= R014) | F4 – ist ein Architekturprinzip der Referenz, keine AI-Act-Pflicht |
| R011 CE/Konformitätserklärung (MUST) | Art. 26 Abs. 1, 47, 48 | 47/48 out – Anbieter | Art. 26 Abs. 1 trägt „Verwendung nach Anleitung“, nicht die CE-Prüfung | F4 – Eingangsprüfung ist gute Praxis; Prüfpflichten stehen bei Einführer/Händler (Art. 23/24) |
| R006 Eingabedaten (MUST) | Art. 10 Abs. 1/6, Art. 26 Abs. 4 | Art. 10 out | **Art. 26 Abs. 4** reicht | F3 – Art. 10 streichen |
| R007 Transparenz (MUST) | Art. 13, 26 Abs. 7, Art. 50 | Art. 50 out (Healthcare-Erbe, Q6) | Art. 13 (a+b), Art. 26 Abs. 7 | F3 – Art. 50 streichen |
| R010 Post-Market/Drift (MUST) | Art. 72, 9 Abs. 2 | beide out – Anbieter | **Art. 26 Abs. 5 Satz 1** („überwachen … informieren gegebenenfalls die Anbieter gemäß Artikel 72“) | F3 – Anker Art. 26 Abs. 5 Satz 1 ergänzen, Art. 9 Abs. 2 streichen |
| R013 Bias/Fairness (SHOULD) | Art. 9 Abs. 2 lit. a, 10 Abs. 2 lit. f, 15 | alle out/ohne Anker | **Art. 26 Abs. 5 Satz 3** i. V. m. Art. 3 Nr. 49 lit. c – Auslegung: Ein Grundrechtsvorfall muss erkannt werden, um gemeldet zu werden; genau der Arm, auf den G-OPS-02 reduziert | F3 – Anker ergänzen; Art. 4a Abs. 2 n.F. erlaubt die Verarbeitung der nötigen Daten |
| R004, R008, R009, R014 | Art. 14 + 26 Abs. 2 · 26 Abs. 5 + 73 · 12 + 26 Abs. 6 | – | vorhanden (b) | bleibt; R009 siehe Teil 4 |
| R012 FRIA | Art. 27 | out – Bereichsausnahme | keiner | Q1, Schritt 3 |

**Lesart:** Der Katalog ist in Teilen ein **Anbieter-Katalog mit Betreiber-Etikett**. Das ist kein Fehler der Gates – sie prüfen Sinnvolles –, aber die Rechtsgrundlage stimmt nicht. Für R001 und R003 liegt der wahrscheinlich tragende Anker im Sektorstapel (NIS2/BSIG), nicht im AI Act. Das ist eine HYPOTHESE, zu prüfen in T-13.

# Teil 4 – Neue Befunde

| ID | Befund | Beleg | Wirkung |
|---|---|---|---|
| **B2c-1** | Art. 73 gilt für den Betreiber nur als Auffangregel: „Kann der Betreiber den Anbieter nicht erreichen, so gilt Artikel 73 entsprechend.“ G-OPS-02/C-04 und R009 modellieren die Fristen als eigene Betreiberpflicht. | Art. 26 Abs. 5 UAbs. 1 Satz 4 | M-F1, F5 |
| **B2c-2** | Die Reduktion auf Grundrechtsvorfälle (Art. 73 Abs. 9) setzt voraus, dass die **Anbieter** gleichwertigen Meldepflichten unterliegen. G-OPS-02/C-02 stützt sie auf CER/NIS2 – die treffen den **Betreiber**. Gestützt ist das heute auf den Leitlinien-Entwurf vom 26.09.2025 (Rn. 57, 60), nicht auf den Wortlaut. | Art. 73 Abs. 9 | M-F2, F5 – bis zur Klärung HYPOTHESE |
| **B2c-3** | Art. 26 Abs. 5 Satz 1 ist der Betreiber-Anker für die Drift-Überwachung (G-OPS-03, R010) – heute zitiert das Gate Art. 72, eine Anbieterpflicht. | Art. 26 Abs. 5 UAbs. 1 Satz 1 | F3 |
| **B2c-4** | Art. 42 Abs. 3 n.F.: Ein System, das die Bedingungen nach Art. 12 Abs. 1 der Verordnung (EU) 2024/2847 (Cyber Resilience Act) erfüllt, gilt als konform mit Art. 15 Cybersicherheit. Nachweis des Anbieters statt eigener Prüfung. | Art. 42 Abs. 3 n.F. | M-C3 |
| **B2c-5** | Art. 15 Abs. 4 UAbs. 3 (Rückkopplungsschleifen) gilt nur für Systeme, die im Betrieb weiterlernen – eine Tatsache über das System, die heute nirgends erfasst ist. | Wortlaut UAbs. 3 | M-C1 |
| **B2c-6** | R007 führt das Kriterium „Informationspflichten gemäß Art. 13 und Art. 26 Abs. 7 dokumentiert“ als `met` mit Beleg G-DEP-03/C-01 – der Check prüft die Unterrichtung nach Abs. 7 nicht. `ACCEPTANCE_CRITERIA_TRACED` sieht nur, dass ein Beleg genannt ist, nicht, ob er trägt. | R007, G-DEP-03/C-01 | Schritt 4: Kriterium auf `gap` |

# Teil 5 – Entscheidungsvorlage

**a ist jeweils die Empfehlung.** Antwortformat wie bisher, z. B. „F1a F2a …“.

| # | Entscheidung | Optionen |
|---|---|---|
| **F1** | Cluster und Maßnahmen aus Teil 1 als Grundlage für Schritt 4; die 36 bestätigbaren Zeilen aus Teil 2 bestätigen | a) ja · b) nur Maßnahmen, Bestätigung in Schritt 3 |
| **F2** | Fünf Zeilen umklassifizieren: Art. 26 Abs. 5 UAbs. 1 Satz 5 und UAbs. 2 Satz 1 → `out` (anderer Betreibertyp, wie 2a Gruppe B) · Art. 15 Abs. 4 UAbs. 2 → `nicht_einschlaegig` (Mittel) · Art. 26 Abs. 7 und Art. 15 Abs. 4 UAbs. 3 Satz 1 → `luecke` | a) ja · b) nein |
| **F3** | Anker korrigieren, wo der Betreiber-Anker im Wortlaut steht: R006 ohne Art. 10 · R007 ohne Art. 50 · R010 + Art. 26 Abs. 5 Satz 1, ohne Art. 9 Abs. 2 · R013 + Art. 26 Abs. 5 Satz 3 | a) ja, Umsetzung in Schritt 4 · b) nein |
| **F4** | Requirements ohne Betreiber-Anker (R001, R002, R003, R005, R011) | a) Anker im Sektorstapel suchen (T-13), bis dahin je Requirement `anker: offen` · b) jetzt auf SHOULD · c) unverändert |
| **F5** | G-OPS-02: Fristen nur im Fallback (B2c-1), Reduktion Abs. 9 an den Anbieter-Status (B2c-2) | a) Umbau in Schritt 4, bis dahin Vermerk HYPOTHESE im Gate · b) belassen, als bekannte Abweichung dokumentieren |
| **F6** | Neues Requirement R017 Rollenwechsel (Art. 25), schließt SPEC-06 Befund 1 | a) ja, MUST/SHOULD in Schritt 4 · b) nein |

**Nicht entschieden, bewusst:** Art. 26 Abs. 11 (Q11) liegt mit den anderen vertagten Punkten in Schritt 3. Wie jede neue Maßnahme gebaut wird (MUST/SHOULD, Beweisstufe) entscheidet Schritt 4.
