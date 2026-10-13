---
titel: Leitfall Bank – Kreditscoring nach Anhang III Nr. 5 lit. b
stand: 2026-10-13
basis: Branch domain_bank, abgezweigt von review-2c = 06a0cbd (Netz-Linie, eingefroren) · Review 15 (S3-4 G1)
status: S34-F1 und BK-F1 a entschieden 13.10.2026 · BK-F2 offen · Neueinordnung des Pflichtenraums steht aus
---

# Entscheid (PO, 13.10.2026)

- **S34-F1:** keine der drei Optionen aus Review 15. Stattdessen:
  - **Leitfall Bank** – Kreditscoring natürlicher Personen für Verbraucherkredit und Baufinanzierung (Anhang III Nr. 5 lit. b)
  - **Netzbetrieb wird Fall 3** (Anhang III Nr. 2), Diagnose-Assistent bleibt Fall 2 (FR-8)
  - **eigene Linie:** Branch `domain_bank`, abgezweigt von `review-2c` (PUSH-8, 06a0cbd). `review-2c` bleibt als Netz-Stand eingefroren
- **README:** zeigt den Leitfall aus Betreibersicht – Einstufung, AI-Act-Pflichten, weitere Regelwerke, Fristen (Auftrag PO, 13.10.2026)
- Die Architektur bleibt: Gates, Pipeline, Evidence Store, Wächter. Es ändert sich die Rechtsebene.

```
domain_netzbetrieb (origin/HEAD)
   └─ spec06 ─ t14 ─ review-2c @ 06a0cbd ── Netz-Linie, eingefroren
                          └─ domain_bank ── Arbeitslinie
                               Leitfall Bank (Nr. 5 lit. b) · Fall 2 Diagnose (Anhang I) · Fall 3 Netz (Nr. 2)
```

# Warum die Einstufung trägt

| Prüfpunkt | Ergebnis | Fundstelle |
|---|---|---|
| Anwendungsfall | Kreditwürdigkeitsprüfung und Bonitätsbewertung natürlicher Personen | Anhang III Nr. 5 lit. b |
| Ausnahme Betrugserkennung | greift nicht – Zweck ist Bonität, nicht Betrug | Anhang III Nr. 5 lit. b; Entwurf Leitlinien Rn. 306–308 |
| wesentliche private Dienstleistung | Verbraucherkredit, Baufinanzierung | Entwurf Leitlinien Rn. 302 |
| Filter Art. 6 Abs. 3 | greift nie: Scoring ist Profiling | Art. 6 Abs. 3 UAbs. 3 |
| Beispiel im Entwurf | Kreditscoring für Verbraucherkredit und Baufinanzierung = Hochrisiko | Entwurf Leitlinien, Abschn. 3.5.3, Beispiele nach Rn. 309 |
| Stichtag | 02.12.2027 | Art. 113 n.F. (VO (EU) 2026/1744) |

- **Gegenüber Nr. 2 neu einschlägig:** Art. 27 (FRIA, Nr. 5 lit. b ausdrücklich genannt), Art. 86 Abs. 1 (Ausnahme nur für Nr. 2), Art. 26 Abs. 11 (Entscheidungen über natürliche Personen), Art. 26 Abs. 5 UAbs. 2 und Abs. 6 UAbs. 2 (Finanzinstitute).
- **Weiter nicht einschlägig:** Art. 49 Abs. 3 und Anhang VIII Abschn. C – Registrierung nur für Betreiber, die Behörden sind.
- **Aufsicht:** Finanzaufsicht als Marktüberwachungsbehörde (Art. 74 Abs. 6), in Deutschland BaFin nach KI-MIG (SEKUNDÄRQUELLE).

# Was sich im Repo ändert (gemessen auf 06a0cbd)

| Bereich | Heute (Netz) | Für den Leitfall Bank |
|---|---|---|
| Steuernde Normen | Anhang III Nr. 2 `in` | Anhang III Nr. 5, Nr. 5 lit. b `in`; Nr. 2 für Fall 3 per Schalter |
| Bereichsausnahme Nr. 2 (20 Zeilen `out`) | Art. 27 (10 + Abs. 4 n.F.), Art. 86 Abs. 1, Art. 49 Abs. 3, Anhang VIII Abschn. C (6), Art. 2 Abs. 10 | `in`: Art. 27 (11), Art. 86 Abs. 1 · bleiben `out`: Art. 49 Abs. 3, Anhang VIII Abschn. C, Art. 2 Abs. 10 |
| Finanzinstitute | Art. 26 Abs. 5 UAbs. 2 Satz 1 `out` (Adressat Finanzinstitut) | `in` |
| Q1 b (FRIA intern, ohne Art.-27-Anker) | gilt | Wiedervorlage: R012 bekommt den Art.-27-Anker |
| Q11 a (Art. 26 Abs. 11 n.e.) | gilt | Wiedervorlage: einschlägig |
| G-PRE-01 | C-A1–C-A7 nur für `no2_critical_infrastructure` | inhaltliche Prüfung für Nr. 5 lit. b fehlt (wie FR-B4 für Anhang I) |
| Sektorstapel | NIS2, BSIG, KRITIS-DachG, EnWG | DSGVO (vorhanden), dazu DORA, BGB/KWG Verbraucherkredit, BDSG § 37a, KWG § 25a/MaRisk – nicht im Repo |

- Zahlen der Spalte „Heute“ am Pflichtenraum gemessen (`scope_grund` „Bereichsausnahme“ bzw. „Systemtyp“). Welche Zeilen wirklich kippen, entscheidet der PO je Zeile (Prüfliste).

# Befunde

| # | Befund | Wohin |
|---|---|---|
| BK-B1 | Der Pflichtenraum ist auf Anhang III Nr. 2 zugeschnitten: für den Leitfall Bank sind mindestens Art. 27 (11 Zeilen), Art. 86 Abs. 1, Anhang III Nr. 5 und Nr. 5 lit. b und Art. 26 Abs. 5 UAbs. 2 Satz 1 neu einzuordnen, Art. 26 Abs. 11 wird einschlägig; Q1 b und Q11 a zur Wiedervorlage | Paket 4: Prüfliste Neueinordnung |
| BK-B2 | G-PRE-01 prüft inhaltlich nur den Nr.-2-Pfad; für Nr. 5 lit. b fehlen Checks (natürliche Person, keine Betrugserkennung, wesentliche Dienstleistung, Profiling) | Paket 5 (mit FR-B4) |
| BK-B3 | `domain_netzbetrieb` (origin/HEAD) hat 4 Commits, die `review-2c` und damit `domain_bank` fehlen (PR #6 „verify-reliable“, 2aec8a2, 29.09.2026) | Paket 8 (PR) |
| BK-B4 | HANDBUCH 1.1, 1.3, 1.4, 4.4, der Leitsatz (00) und AGENTS.md Abschn. 2 nennen den Netzbetrieb als Leitfall und schließen den Finanzsektor aus | nach BK-F1: nachziehen (Paket 4) |
| BK-B5 | PR-1 nennt `review-2c` als Quelle des PR; Arbeitslinie ist jetzt `domain_bank` | Paket 8 |

# Fragen

| # | Frage | Optionen |
|---|---|---|
| BK-F1 | Bank als Leitfall hebt D-06 (14.08., „Branche Energie/KRITIS“) und den Ausschluss „nicht der Finanzsektor mit DORA“ in HANDBUCH 1.3 auf, den FR-6 am 06.10. bestätigt hat. Gründe damals (HISTORIE H2, 6.2): Markt hoch besetzt, Publikum Frankfurt/Zürich, Thesis-Anschluss F4 = Anhang III Nr. 2 | a) **aufheben**: Bank Leitfall, Netz Fall 3 hält den Thesis-Anschluss; HANDBUCH, Leitsatz, AGENTS.md nachziehen · b) nicht aufheben: Bank nur als weiterer Fall, Netz bleibt Leitfall |
| BK-F2 | Welche Anwendung ist Fall 3 (Netzbetrieb, Anhang III Nr. 2)? | a) **Zustandsüberwachung der Betriebsmittel** (Rn. 184 lit. b) · b) Anomalieerkennung im Netzbetrieb (Beispiel S. 47) · c) Redispatch als Grenzfall – Entscheid mit FR-2 |

**Entschieden 13.10.2026:** BK-F1 **a** – Ausschluss des Finanzsektors aufgehoben. HANDBUCH (Titel, 1.1, 1.3, 1.4, 4.4, Fahrplan), Leitsatz (00), AGENTS.md Abschn. 2 und HISTORIE D-06, D-08 nachgezogen; damit auch S34-B4 umgesetzt.

# Ehrlich zur Methode

- AI-Act-Pflichten am Wortlaut im Repo (`docs/legal/wortlaut/`), Omnibus-Fassungen von Art. 4 und Art. 27 Abs. 4 dort geprüft.
- Leitlinien-Entwurf im Original (Hashes in Review 15), Abschnitt 3.5.3.
- Nationales Recht aus Sekundärquellen, Stand 13.10.2026: KI-MIG in Kraft, BaFin für KI im Zusammenhang mit regulierter Finanztätigkeit (IT-Finanzmagazin 30.07.2026, Regierungsentwurf 10.02.2026); Verbraucherkreditreform BGBl. I 2026 Nr. 139, verkündet 18.05.2026, gilt ab 20.11.2026 (Noerr, iww); § 37a BDSG nur erwähnt, Inhalt nicht geprüft. Kein Rechtsrat.
