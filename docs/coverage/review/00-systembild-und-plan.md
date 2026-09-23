---
titel: Systembild + Plan – Regulariendurchlauf abschließen
stand: 2026-09-23
basis: Branch spec06-aiact-stufe0 (30 Commits vor domain_netzbetrieb, nicht gemergt)
status: Schritt 1 fertig – wartet auf PO-Prüfung
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

## Schritt 4 – Bedarfsanalyse (Requirements · Rego · Gates)
- **4a** Neue/zu ändernde Requirements (R015 ff., eu_ai_act_refs, acceptance_criteria)
- **4b** Gate-Änderungen: neue Checks in bestehenden Gates vs. neue Gates (Kriterium: gleicher Trigger + gleiche Datenquelle → Check ergänzen, sonst neues Gate)
- **4c** Rego-Bedarf je Check (Input-Datei, Pass/Fail-Fall, Negativfall)
- **4d** Reihenfolge nach Priorität (MUST + Stichtag + Aufwand), DoR je Paket

## Schritt 5 – Umsetzung + Ausbau
- **5a** Tickets nach TICKET_TEMPLATE, je Paket
- **5b** Anhänge-Lauf (180 Einheiten)
- **5c** Stichprobe der 801 `out` nach Adressat-Gruppen → Sammelbestätigung
- **5d** PR spec06-aiact-stufe0 → domain_netzbetrieb
- **5e** Danach: Sektorstapel (T-13), gleiches Verfahren
- **5f** Danach: Agent-Use-Cases (siehe Agent-Aufbau-Handbuch)
