---
titel: Schritt 2d und 2e – die drei gedeckten Zeilen und die Querbefunde
stand: 2026-09-28
basis: Branch review-2c · Pflichtenraum nach 2c · Querbefunde aus 00 (A6) und 02 (Teil 6)
status: VORSCHLAG – Entscheidungsvorlage D1, D2, E1–E3 in Teil 3
---

# Kurzfazit
- **2d:** Keine der drei „gedeckt“-Zeilen hält dem Raster stand. „Gedeckt“ verlangt ein Requirement **und** ein Gate, die die Pflicht **vollständig** treffen.
  - Art. 25 Abs. 1 lit. a und c: G-OPS-06 prüft sauber, aber es gibt kein passendes Requirement (G-OPS-06 hängt an R001, das Art. 9 trägt)
  - Art. 13 Abs. 3 lit. a: Der Bevollmächtigte des Anbieters wird nicht geprüft, der Kontakt nur als nicht-leerer String
  - → Nach D1/D2 ist **keine einzige Pflicht vollständig gedeckt**. Das ist die ehrliche Zahl.
- **2e:** Von 17 Querbefunden sind 11 erledigt, entschieden oder geklärt, 2 vertagt, 2 liegen außerhalb des Repos. **Zwei sind offen** (E1, E2), dazu einer aus 2c (E3).

# Teil 1 – 2d: Gegenprobe der gedeckten Zeilen

| Einheit | Gate / Requirement | Was das Gate prüft (Rego gelesen) | Was fehlt | Vorschlag |
|---|---|---|---|---|
| Art. 25 Abs. 1 lit. a | G-OPS-06/C-25a · **kein passendes Requirement** | eigener Name/Marke auf einem bereits in Verkehr gebrachten Hochrisiko-System → deny, MUST | das Requirement: G-OPS-06 verweist auf R001 (Art. 9), R001 nicht zurück (SPEC-06 Befunde 1 und 2) | **teilabdeckung** bis R017 (F6) steht, dann gedeckt |
| Art. 25 Abs. 1 lit. c | G-OPS-06/C-25c · **kein passendes Requirement** | Zweckänderung, gewertet gegen die Einstufungsregel aus G-PRE-01 (nicht gegen ein Manifest-Boolean) → deny, MUST | wie lit. a | **teilabdeckung** bis R017 |
| Art. 13 Abs. 3 lit. a | G-DEP-04/C-01 · R011 | `model_info.provider` gesetzt, `provider_contact` nicht leer | (1) Bevollmächtigter nach Art. 22 – Pflichtangabe, wenn der Anbieter außerhalb der Union sitzt, also etwa bei US-Anbietern; (2) Kontakt nur als String, nicht als erreichbar belegt; (3) R011 hat keinen Betreiber-Anker (F4) | **teilabdeckung** · Maßnahme: Feld „Bevollmächtigter“ im Pflichtinhalte-Check (M-A1) |

**Folge:** Die Zahl „3 gedeckt“ aus dem Nachtlauf beruhte auf der Gate-Seite allein. Mit D1 und D2 steht der AI-Act-Raum bei **0 gedeckt · 42 Teilabdeckungen**. Nach R017 werden Art. 25 Abs. 1 lit. a und c die ersten gedeckten Pflichten.

# Teil 2 – 2e: Querbefunde, Stand 28.09.2026

| ID | Befund | Stand | Wo |
|---|---|---|---|
| A6.1 / Q1 | FRIA ohne Pflicht (R012, G-PRE-02, G-PRE-05/C-01 als MUST) | vertagt | Schritt 3 |
| A6.2 | Raster-Drift „nicht_einschlaegig“ | erledigt | 2a |
| A6.3 | 80 von 81 VERIFIZIERT | erledigt | 2b E4, T-14.5 |
| **A6.4** | **G-DEP-06 zitiert Art. 26 Abs. 3 (Unberührtheitsklausel), R014 und die Policy Abs. 6 (Aufbewahrung)** | **offen** | **E1** |
| A6.5 / 1 | G-OPS-06 ohne Requirement | entschieden | 2c F6 (R017) |
| A6.5 / 2 | G-OPS-06 → R001 einseitig; die Rego-Meldungen von G-OPS-06 nennen „R001“ | entschieden mit F6 | Schritt 4: Verknüpfung und Meldungen auf R017 |
| A6.5 / 3 | R011 führt Art. 47/48 (Anbieterpflichten) | entschieden | 2c F4 |
| A6.6 | vier PO-FRAGEN im Pflichtenraum (Art. 4, 20, 60, 86) | erledigt | T-14.5 |
| **A6.7** | **Rego-Meldungen ohne Check-ID: 130 von 195 Meldungen in 16 Policy-Dateien folgen nicht dem Format aus AGENTS.md 4 (`G-XX/C-NN (Rxxx, Art.): …`). Die Regel steht im Arbeitsvertrag, kein Wächter prüft sie** | **offen** | **E2** |
| Q2 | Nr.-2-Ausnahmen (Art. 27, 43 Abs. 2, 49, 75, 86) | vermerkt | Fachbeitrag, außerhalb des Repos |
| Q6 | Art. 50 in R007 aus der Healthcare-Vignette | entschieden | 2c F3 |
| Q7 | Bauverbot Meldekaskade | erledigt | 2b E7, HANDBUCH Teil 7 |
| Q8 | Stichtag 02.12.2027 im HANDBUCH | erledigt | steht bereits in HANDBUCH 4.3 |
| Q9 | Requirements auf Anbieterartikeln | entschieden | 2c F3/F4 |
| Q10 | Art. 99 Abs. 7: TOMs mindern Bußgeld | vermerkt | BIZDEV, außerhalb des Repos |
| Q11 | Art. 26 Abs. 11 | vertagt | Schritt 3 |
| G1-offen | Ab wann gilt Kap. IX (Art. 72/73) für Anhang-III-Systeme? | **geklärt für den Betreiber** | siehe unten |

**Kap. IX, geklärt für den Betreiber:**
- Formal gilt Kap. IX ab 02.08.2026: Art. 113 nennt es nicht unter den Ausnahmen.
- Für den Betreiber greift Art. 73 aber nur über Art. 26 Abs. 5 Satz 4 (Befund B2c-1). Art. 26 steht in Kap. III Abschnitt 3 und gilt für Anhang III ab **02.12.2027** (Art. 113 Abs. 3 lit. c Ziff. i n.F.).
- Folge für die Meldepflicht des Betreibers: praktisch ab 02.12.2027.
- Für den Anbieter bleibt offen, ob ein Anhang-III-System vor diesem Datum „Hochrisiko“ im Sinne des Art. 73 ist. Die Einstufung nach Art. 6 steht selbst in Kap. III Abschnitt 1. Das ist eine HYPOTHESE und für den Betreiber nicht tragend.

**Aus 2c dazugekommen:**
- B2c-6: R007 führt das Kriterium zu Art. 26 Abs. 7 als `met`, obwohl G-DEP-03/C-01 es nicht prüft.
- `ACCEPTANCE_CRITERIA_TRACED` sieht nur, dass ein Beleg genannt ist, nicht ob er trägt → **E3**

# Teil 3 – Entscheidungsvorlage

**a ist jeweils die Empfehlung.**

| # | Entscheidung | Optionen |
|---|---|---|
| **D1** | Art. 25 Abs. 1 lit. a und c: `gedeckt` → `teilabdeckung`, bis R017 steht | a) ja · b) nein |
| **D2** | Art. 13 Abs. 3 lit. a: `gedeckt` → `teilabdeckung` (Bevollmächtigter fehlt; Maßnahme im Pflichtinhalte-Check M-A1) | a) ja · b) nein |
| **E1** | G-DEP-06: `legal_refs` Art. 26 Abs. 3 → Abs. 6, wie R014 und die Policy seit 27.05. | a) jetzt, wie P4b · b) in Schritt 4 |
| **E2** | Rego-Meldungen ohne Check-ID (130 von 195) | a) Schritt 4: eigenes Paket, mit Wächter `REGO_MESSAGES_CARRY_CHECK_ID` im selben Commit · b) jetzt nur den Wächter, als INFO · c) Regel aus AGENTS.md streichen |
| **E3** | R007: Kriterium „Art. 13 und Art. 26 Abs. 7 dokumentiert“ von `met` auf `gap` | a) jetzt – `met` ist deine Aussage, und sie stimmt nicht · b) in Schritt 4 |

Mit D1 und D2 werden die drei Zeilen bestätigbar (scope, befund und verifikation sind dann entschieden).
