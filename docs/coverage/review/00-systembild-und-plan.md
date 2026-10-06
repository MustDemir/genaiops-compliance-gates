---
titel: Systembild + Plan – Regulariendurchlauf abschließen
stand: 2026-09-29 (Teil C Ziellinie und Reihenfolge; Teil A/B unverändert seit 2026-09-23)
basis: Branch spec06-aiact-stufe0 (30 Commits vor domain_netzbetrieb, nicht gemergt)
status: Systembild vom PO bestätigt 23.09.2026 · Leitsatz ergänzt 28.09.2026 · Teil C vom PO bestätigt 29.09.2026
---

> **Seit 29.09.2026 gilt Teil C** (unten): messbare Ziellinie, acht Pakete, neue Reihenfolge.
> AI Act + Omnibus → Prüf-Agent → Sektorstapel. Teil B bleibt als Herkunft stehen.

# Leitsatz – unser Ziel

> **EU-AI-Act-Konformität für einen Verteilnetzbetreiber nachweisbar statt behauptbar machen – lückenlos von der Norm bis zum Beleg.**

- **Wer:** Betreiber (Verteilnetzbetreiber), nicht Anbieter
- **Was:** KI im Redispatch, Einstufung Anhang III Nr. 2 (kritische Infrastruktur)
- **Bis wann:** Stichtag 02.12.2027 (Omnibus)
- **Form:** Referenzarchitektur, kein Produkt (D-05)

**Fertig heißt:**
- Jede `in`-Pflicht ist durch Gate/Check gedeckt (mit ehrlicher Beweisstufe) **oder** bewusst offen (`declared_gap`) mit Begründung
- Jede Zeile `po_bestaetigt: true` – die 4 Ehrlichkeitsfelder entscheidet nur der PO
- Beide Richtungen geprüft: Verifikation (Gate prüft, was es behauptet) + Validierung (Katalog deckt alle Pflichten – „richtige 17 Gates?")
- PR `spec06-aiact-stufe0` → `domain_netzbetrieb` gemergt

**Danach** (Reihenfolge seit 29.09.2026, Teil C):
```
AI Act + Omnibus fertig ──► EU-AI-Act-Prüf-Agent ──► Sektorstapel (T-13: NIS2, BSIG, DSGVO, KRITIS-DachG, EnWG)
```
(bis 28.09.2026: AI-Act-Durchlauf → Sektorstapel → Agenten)

**Warum:** Belege statt Aussagen gegenüber Aufsicht und Kunden (Hash-Chain, cosign) · Art. 99 Abs. 7: dokumentierte TOMs mindern Bußgeld (Q10) · Grundlage für die Agenten

---

# Teil A – Systembild (zur Prüfung durch den PO)

## A1 Zweck in einem Satz
- Konformität **nachweisbar statt behauptbar**: Pflicht → Requirement → Gate/Check → Rego → Evidence-Record, jeder Nachweis mit Beweisstärke (E-0…E-3)
- Adressat: **Betreiber** (Verteilnetzbetreiber), Anwendungsfall **Redispatch**, Anhang III Nr. 2, Stichtag 02.12.2027
- Referenzarchitektur, kein Produkt (D-05)

## A2 Die Kette
```
Norm (Wortlaut, gehasht)
  └─► Pflichteneinheit (Pflichtenraum, SPEC-06)       ← NEU: Stufe 0
        └─► Requirement R001–R014 (acceptance_criteria = DoD)
              └─► Gate G-PRE/DEP/OPS (17) → Checks (55, Severity je Check)
                    └─► Rego-Policy (19) → Conftest / Gatekeeper
                          └─► Evidence Store (Hash-Chain, cosign E-1)
```
- Bisher nur **links→rechts** geprüft (Verifikation). SPEC-06 prüft **rechts←links**: Deckt der Katalog alle Pflichten? (Validierung, „richtige 17 Gates?")

## A3 Gate-Logik (was ein Gate „fertig" macht)
- 5 Fragen: Ziel · Daten (`required_inputs`) · Ergebnis (Severity→Entscheidung) · Auslöser ein (`trigger`) · Auslöser aus (`triggers`)
- Entscheidung abgeleitet: MUST verletzt→block · HYBRID→manual_review · SHOULD→warn
- Zwei Gate-Arten: **präventiv** (einmal bei Zulassung, max. E-2) vs. **operativ** (Laufzeit, E-3) – B-14: 8 von 9 Laufzeitpflichten nur als `declared_gap`
- DoR (6 Punkte, u. a. Primärquelle, Rolle, Datenquelle, Negativfall, Parallelregime) · DoD (7 Punkte)
- **4 Ehrlichkeitsfelder = nur PO**: Norm↔Pflicht · MUST/SHOULD · evidence_level · implemented/design_only

## A4 Ist-Stand Katalog (README)
- 17 Gates · 14 Requirements · 55 Checks (48 implemented, 7 design_only) · alle Gates `role_scope: deployer`
- Beweisstärke: jedes Gate E-0; Checks: 4× E-1 (G-OPS-05), 3× E-3 (G-OPS-03), Rest E-0/leer
- 9 von 17 Gates erfüllen die maschinelle DoD
- Requirements decken: Art. 9, 10(via 26 Abs. 4), 11, 12, 13, 14, 15, 26 Abs. 1/2/4/5/6/7, 27, 47/48, 50, 72, 73

## A5 Was der Regulariendurchlauf (T-12) ergeben hat
- 1062 Einheiten → **81 in** · 801 out · **180 unbewertet** (Anhänge + Art. 113, kamen nach den Läufen)
- Die 81 `in`: 47 Adressat Betreiber, 33 Anbieter mit Durchschlag
- Befunde: 3 gedeckt · 33 teilabdeckung · **23 luecke** · 22 nicht_einschlaegig
- Sektorstapel (NIS2, BSIG, DSGVO, KRITIS-DachG, EnWG): Wortlaute + Pflichtenräume angelegt, **noch nicht analysiert** (T-13 nicht gelaufen)

## A6 Auffälligkeiten beim Lesen (für Schritt 2 relevant)
1. **FRIA-Befund:** Art. 27 Abs. 1 nimmt Anhang III Nr. 2 aus → R012/G-PRE-02 (FRIA als MUST) trägt für Redispatch evtl. keine Pflicht → PO-Frage
2. **Raster-Drift:** Läufe 04.–06.09., Raster erst 07.09. → „nicht_einschlaegig" wurde anders genutzt als definiert (Raster: Recht/Erlaubnis/Definition; Lauf: „passt nicht zum Use Case", z. B. Art. 5, Art. 26 Abs. 8/10) → Zeilen neu einordnen
3. **Verifikation:** 80 von 81 `in` = VERIFIZIERT, nur 1 HYPOTHESE → unplausibel hoch, Adressaten-/Durchschlagsurteile sind Auslegung
4. **Inkonsistenz:** G-DEP-06 `legal_refs` = Art. 26 **Abs. 3**, R014 + Policy = Abs. 6 (Fix 27.05. nicht ins Gate zurückgeflossen)
5. SPEC-06 Befunde 1–3 offen: G-OPS-06 ohne Requirement (Art. 25/97) · Asymmetrie G-OPS-06↔R001 · R011 führt Art. 47/48 (Anbieterpflichten)
6. Offene PO-Fragen im Pflichtenraum: 4× „PO-FRAGE" (u. a. Art. 4 KI-Kompetenz, Art. 60, Art. 86)
7. Rego-Stichprobe (G-DEP-06, G-OPS-01): Policies prüfen, was die Checks beschreiben ✓ – Meldungsformat ohne Check-ID (AGENTS 4 verlangt `G-XX/C-NN`)

## A7 Nicht vollständig gelesen (bewusst)
- HISTORIE H4 7.5–7.10 und H4.20–H4.25 (Messdetails), H5–H7 (Thesis-Diff, Forschung) – für die Tabelle nicht tragend
- Policies: 2 von 19 im Detail, Rest nur Regelzahl

---

# Teil B – Plan Schritt 1–5

```
1 VERSTEHEN ✅ ─► PO prüft Systembild ─► 2 TABELLE ─► 3 PO-ENTSCHEID ─► 4 BEDARFSANALYSE ─► 5 UMSETZUNG
```

## Schritt 1 – Verstehen ✅
- 1a–1e gelesen, 1f dieses Dokument
- **Stopp:** PO bestätigt/korrigiert Teil A

## Schritt 2 – Tabelle (je Teilschritt eine Sitzung)
- **2a Vorarbeit:** Raster-Drift bereinigen (A6.2) – welche der 22 nicht_einschlaegig sind eigentlich `out` oder `luecke`?
- **2b Lücken (23):** je Zeile Pflicht · Adressat · heutiges Gate · Vorschlag (neues Gate / Check erweitern / Requirement erweitern / bewusst offen) · Begründung · prüfbar in Pipeline? · Beweisstufe möglich
- **2c Teilabdeckungen (33):** welcher Teil fehlt · welcher Check würde ihn schließen
- **2d nicht_einschlaegig (22) + 3 gedeckt:** Kurzcheck, Gegenprobe
- **2e Querbefunde:** A6.1, A6.4, A6.5 als eigene Zeilen

## Schritt 3 – PO-Entscheid
- PO geht Tabelle Zeile für Zeile durch → Entscheid = `po_bestaetigt: true` für diese 81 Zeilen
- Ergebnis: Entscheidungsliste mit Begründung (neue D-xx-Einträge in HISTORIE)
- **Vertagt auf Schritt 3 (PO 28.09.2026, P2b/P3c):**
  - **S3-1** Art. 111 Abs. 2 Satz 2 – Betreiber als Behörde (z. B. kommunaler Eigenbetrieb) → ggf. dritte Bedingung im P0-Check
  - **S3-2** Unterglieder entschiedener Normen: Art. 3 Nr. 49 lit. a–d · Art. 4a Abs. 2 lit. a/b n.F. · Art. 113 Abs. 3 lit. c Ziff. ii n.F.
  - **S3-3** Verifikationsstufe der 22 Zeilen ohne Stufe (12 steuernde Normen AI Act, 10 Omnibus inkl. Art. 5 lit. ba/bb)
  - **S3-4** Hypothesen-Prüfung (43 + neue) gegen Sekundärquellen

## Schritt 4 – Bedarfsanalyse (Requirements · Rego · Gates)
- **4a** Neue/zu ändernde Requirements (R015 ff., eu_ai_act_refs, acceptance_criteria)
- **4b** Gate-Änderungen: neue Checks in bestehenden Gates vs. neue Gates (Kriterium: gleicher Trigger + gleiche Datenquelle → Check ergänzen, sonst neues Gate)
- **4c** Rego-Bedarf je Check (Input-Datei, Pass/Fail-Fall, Negativfall)
- **4d** Reihenfolge nach Priorität (MUST + Stichtag + Aufwand), DoR je Paket

## Schritt 5 – Umsetzung + Ausbau
- **5a** Tickets nach TICKET_TEMPLATE, je Paket
- **5b** Anhänge-Lauf (180 Einheiten) → **vorgezogen als Paket 1 (Teil C)**
- **5c** Stichprobe der 801 `out` nach Adressat-Gruppen → Sammelbestätigung → **Paket 4**
- **5d** PR spec06-aiact-stufe0 → domain_netzbetrieb → **Paket 8**
- **5e** Danach: Sektorstapel (T-13), gleiches Verfahren → **nach dem Agenten**
- **5f** Danach: Agent-Use-Cases (siehe Agent-Aufbau-Handbuch) → **Paket 9, vor dem Sektorstapel**

---

# Teil C – Ziellinie und Reihenfolge (PO 29.09.2026)

## C1 Ziel

- **Ziel bleibt der Leitsatz:** EU-AI-Act-Konformität des Betreibers nachweisbar statt behauptbar.
- **Neu: der Zweck dahinter.** Das Gate-System wird die Prüfbasis für einen **EU-AI-Act-Agenten im Betrieb**.
- **Der Agent fällt Urteile** („konform / nicht konform / nicht geprüft“). Er ist ein Prüf-Agent, kein Auskunfts-Agent. Deshalb braucht er **alle Pakete 1–8**.
- **Die Architektur des Agenten ist offen.** Sie wird in Paket 9 erarbeitet: erst Use Cases, dann Technik.
- **Warum Vollständigkeit Voraussetzung ist:** Der Agent darf nur urteilen, was das System belegt. Eine unbekannte Lücke wird sonst zu einem falschen „konform“.

## C2 Reihenfolge

```
AI Act + Omnibus (Pakete 1–8) ──► Prüf-Agent (Paket 9) ──► Sektorstapel (T-13)
```

- **Parallel zu Paket 5 (PO FR-2 a, 06.10.2026):** ein Redispatch-Referenzszenario (Fixtures + End-to-End-Lauf) und die Use Cases des Agenten (P9-1) mit Netzbetreibern – der Kunde soll seinen Fall laufen sehen, und die Use Cases steuern, was in Paket 6 zuerst gebaut wird (Review 14).
- **Sektorstapel nach dem Agenten:** zulässig, weil der Agent seine Grenze offen nennt. Er prüft den AI Act, nicht NIS2, BSIG, DSGVO, KRITIS-DachG oder EnWG.
- Das ist dieselbe Logik wie H4 (PASS mit Hinweis): Der Agent urteilt nur über das, was er prüft, und sagt, was er nicht prüft.
- **Anhänge und Omnibus vor der Bedarfsanalyse:** Sonst planen wir Requirements und Gates, bevor alle Pflichten bekannt sind.

## C3 Ziellinie – messbar

„Qualitätsprüfung Policies und Gates abgeschlossen“ heißt: alle Zeilen auf Soll.

| Kriterium | Ist 29.09.2026 | Soll |
|---|---|---|
| AI-Act-Einheiten ohne in/out (206 Anhänge, 4 Art. 113) | 210 → **0** (Paket 1, Vorschlag, Review 08) | 0 |
| Omnibus-Einheiten ohne in/out | 259 von 269 → **0** (Paket 2, Vorschlag, Review 09) | 0 |
| `in`-Pflichten vom PO bestätigt | 64 von 85 (nach Paket 1: 64 von 89; nach Paket 2 mit Omnibus: 61 von 104) → **125 von 125** (06.10.2026, Paket 4; 12 Begriffsbestimmungen kamen mit OUT-1 dazu) | alle |
| `out` vom PO bestätigt | 25 von 908 (nach Paket 1: 25 von 1114; nach Paket 2 mit Omnibus: 31 von 1368) → **1391 von 1391** (06.10.2026, Stichprobe 20 je Gruppe, Sonstige ganz) | Stichprobe nach Adressat-Gruppen, dann Sammelbestätigung |
| Lücken (28) und Teilabdeckungen (38) | benannt | je gebaut **oder** `declared_gap` mit Begründung |
| Gate nennt, was es nicht prüft | nein | `known_limits` je Gate, Hinweis in jedem Lauf (H4) |
| Element-Matrix Pflicht ↔ Rego-Regel | einmal von Hand (Review 07) | als Daten, Wächter in `make verify` |
| Evidence Store: Urteil, Grundlage, Begründung und Freigabe beweisfest (Review 12) | nur das Urteil (02.10.2026); Ablehnung und fehlende Freigabe halten an (T-16.1, 02.10.2026) | alle vier hash-gedeckt, Ablehnung wirkt (T-16) |
| PR `spec06-aiact-stufe0` → `domain_netzbetrieb` | offen | gemergt |

- Ist-Zahlen gemessen am Pflichtenraum auf Branch `review-2c`, Stand 29.09.2026.

## C4 Die acht Pakete

```
A VOLLSTÄNDIGKEIT          B ABGLEICH                C BAUEN
1 Anhänge + Art. 113       5 Bedarfsanalyse          6 Checks + Rego
2 Omnibus n.F.      ─► 4 ─►  je Lücke/Teil:    ──►   7 known_limits + Wächter ─► 8 PR ─► 9 AGENT
3 Befunde + Matrix   PO-     bauen oder offen
  (2. Lauf)          Runde
```

| # | Paket | aus Plan | Größe | PO |
|---|---|---|---|---|
| 1 | Anhänge + Art. 113 einordnen (210) | 5b, vorgezogen | M | Stichprobe |
| 2 | Omnibus-Neufassungen einordnen (259) | neu | M | Stichprobe |
| 3 | Befunde für neue `in`-Zeilen + Element-Matrix, 2. Lauf | 2 | S–M | ja |
| 4 | PO-Runde: Schritt-3-Liste (FRIA, Art. 111 Abs. 2 Satz 2, Unterglieder, Verifikationsstufen, Hypothesen, Art. 26 Abs. 11, M1), alle `in` bestätigen, `out`-Stichprobe | 3, 5c | M | **viel** |
| 5 | Bedarfsanalyse: R015–R017, Anker (F3/F4/F6), je Lücke/Teilabdeckung bauen oder `declared_gap`, E2 | 4 | L | ja |
| 6 | Checks + Rego bauen, nach MUST + Stichtag | 5a | **L** | Abnahme |
| 7 | `known_limits` + Hinweis-Stufe (H4), Element-Matrix als Wächter | 5 | M | – |
| 8 | PR mergen | 5d | S | Freigabe |
| T-16 | **Evidence Store beweisfest** (PO 02.10.2026, Review 12): Ablehnung und fehlende Freigabe wirken (ES-1, ES-2), Belege, Begründung und Freigabe hash-gedeckt (ES-3–ES-5), Belegverzeichnis beim Rollenwechsel (ES-6). Neben 4–6, spätestens vor 8 – der Agent urteilt auf diesem Store | neu | M | ja (ES-F1, ES-F2, EF) |
| 9 | Prüf-Agent: Use Cases (P9-1) → Einordnung des Agenten selbst nach AI Act (P9-2) → Architektur (P9-3) → Betrieb | 5f | offen | ja |

- Paket 6 wird kleiner als 66 Zeilen: Laufzeitpflichten sind oft nur als `declared_gap` führbar (B-14: 8 von 9).
- Paket 9: Der Agent ist selbst ein KI-System und braucht eine eigene Einordnung nach AI Act (HYPOTHESE: kein Hochrisiko; Art. 4, ggf. Art. 50 prüfen).
- **Alle offenen Entscheide und Befunde mit Ziel-Paket** stehen im [Entscheidungsregister](entscheidungsregister.md); der Wächter `PO_DECISIONS_REGISTERED` hält es vollständig.
- **Element-Matrix:** läuft nach Paket 3 (2. Lauf) und nach Paket 6 (3. Lauf, als Wächter) erneut. Review 07 ist der 1. Lauf, gültig für den AI-Act-Artikelteil.
