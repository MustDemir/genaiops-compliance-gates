---
titel: Fachreview – trägt die Kette das Ziel „EU-AI-Act-Prüf-Agent business-ready“?
stand: 2026-10-05
basis: Branch review-2c, Stand f56e69b (gemessen) · Leitsatz und Teil C aus 00-systembild-und-plan.md · Auftrag des PO 05.10.2026 („aus Sicht eines geeigneten Fachspezialisten prüfen, ob unsere Kette das Ziel erreicht“)
status: Einschätzung und Vorschläge · nichts entschieden · Fragen FR-1 bis FR-5
---

# Kurzurteil

- **Richtung stimmt.** Das Fundament – Norm bis Rego nachvollziehbar, jede Behauptung von einem Wächter gehalten – ist für ein Audit-Produkt ungewöhnlich solide.
- **Business-ready ist die Kette heute nicht.** Von 74 einschlägigen `in`-Pflichten sind **2 gedeckt**, 30 teilweise, 42 Lücke. Jedes Gate steht auf **E-0** (Selbstauskunft). Der ausführbare Durchlauf ist ein **Healthcare-Szenario**, nicht Redispatch. Der Agent ist **nicht entworfen**.
- **Die Prüfungen nach jedem Commit sichern Ehrlichkeit, nicht Fortschritt.** Sie sind Voraussetzung für einen Agenten, der nur urteilt, was belegt ist – sie schließen aber keine Lücke.
- **Kritischer Pfad ab jetzt:** Bauen (Pakete 5–6), Belege härten (T-16, E-1), ein echter Redispatch-Durchlauf, früh die Use Cases des Agenten mit Kunden.

Perspektive: AI-Act-Compliance (Betreiberpflichten) · IT-Audit/Assurance (Beweisführung) · Produkt (Kunde Verteilnetzbetreiber). Kein Rechtsrat.

# Teil 1 – Die Kette, Glied für Glied

```
Norm ──► Pflichteneinheit ──► Requirement ──► Gate/Check ──► Rego ──► Evidence Store ──► Agent
 ✅        ✅ 113 in            🟡 14            🟡 2 gedeckt     ✅       🟡 Urteil ja,       ⬜ nicht
 gehasht   PO bestätigt 83      R015–R017 fehlen   30 Teil         AST-     Grundlage nein      begonnen
                                                   42 Lücke        geprüft  (T-16.2–16.5)
                              alle 17 Gates E-0 ──────────────┘
```

| Glied | Stand (gemessen) | Für „business-ready“ |
|---|---|---|
| Norm | AI Act + Omnibus als gehashte Wortlaute, Zitate zeichengenau geprüft | ✅ trägt |
| Pflichteneinheit | 113 `in` (AI Act 89, Omnibus 24), 83 bestätigt; 1403 `out`, 144 bestätigt | ✅ fast fertig (Paket 4) |
| Requirement | 14; R015–R017 beschlossen, nicht gebaut; 5 mit `anker: offen`, 1 `intern` | 🟡 Paket 5 |
| Gate/Check | 17 Gates, 55 Checks (48 implementiert); Abdeckung der 74 einschlägigen Pflichten: 2 gedeckt · 30 Teil · 42 Lücke; davon Betreiber direkt: 1 · 8 · 19 | 🟡 Kern der Arbeit, Pakete 5–6 |
| Beweisstärke | Gates alle E-0; Checks: E-1 ×4, E-3 ×3, Rest E-0/leer | 🔴 Auditor liest E-0 als Behauptung |
| Laufzeit | 9 Laufzeit-Requirements, 8 davon `declared_gap` | 🔴 der „Agent im Betrieb“ lebt genau davon |
| Rego | Element-Matrix hält 96 Regelangaben am OPA-AST | ✅ trägt |
| Evidence Store | Urteil hash-verkettet, Manifest signiert; Ablehnung wirkt (T-16.1 ✅); Belege, Begründung, Freigabe nicht gebunden | 🟡 T-16.2–16.5 |
| Grenzen | `known_limits` an 0 von 17 Gates | 🟡 Paket 7 |
| Agent | P9-1 bis P9-3 offen | ⬜ |

# Teil 2 – Was gut ist

- **Nachweis statt Behauptung, bis in die eigene Doku:** 49 Wächter halten Katalog, README, Register und Pflichtenräume gegeneinander. Das ist der Unterschied zu GRC-Tabellen, die niemand gegen Code prüft.
- **Ehrliche Grenzen:** `declared_gap`, Beweisstufen, HYPOTHESE-Vermerke, „nicht geprüft“ als eigene Antwort. Genau das braucht ein Prüf-Agent, damit aus einer unbekannten Lücke kein falsches „konform“ wird.
- **Fail-closed und menschliche Entscheidung mit Wirkung** (T-16.1): Ablehnung blockiert, fehlende Freigabe hält an – in Orchestrator und CI aus einem Modul.
- **Auslegung sichtbar entschieden:** jede Auslegungsfrage hat eine PO-Entscheidung mit Begründung und Gegenargument (heute z. B. Q11).
- **Muster für mehrere Kunden schon angelegt:** Bedingungsparameter im Manifest (P2-F4, S3-1 a) statt fest verdrahteter Annahmen.

# Teil 3 – Was bis „business-ready“ fehlt (nach Gewicht)

1. **Abdeckung.** Mit 2 von 74 gedeckt würde der Agent fast überall „Lücke“ oder „nicht geprüft“ sagen. Heute verkaufbar ist ein **Readiness-Bericht** (Gap-Analyse mit Belegpfad) – nicht ein Konformitätsurteil.
2. **Beweisstärke.** Alle Gates lesen JSON, das jemand ausfüllt (E-0). Für ein Audit braucht es mindestens: signierte Attestierung durch die verantwortliche Rolle (E-1) und für Laufzeitpflichten Messung aus dem System (E-3, wie G-OPS-03). Dafür fehlen Konnektoren zu Quellsystemen (MLOps-Registry, Ticketing, Logging, CMDB).
3. **Referenzfall.** Die Rechtsanalyse gilt dem Verteilnetzbetreiber (Redispatch, Anhang III Nr. 2). Der ausführbare End-to-End-Lauf ist `healthcare-ambient-ai-scribe`; für Redispatch gibt es eine Art.-6-Fixture, keinen Durchlauf. Ein Kunde aus dem Netzbetrieb sieht seinen Fall nicht laufen.
4. **Evidence Store.** Die Freigabe ist eine JSON-Datei ohne geprüfte Identität und Signatur (T-16.4); Belege und Begründung sind nicht hash-gedeckt (T-16.2, T-16.3). Ohne das ist ein Agent-Urteil nicht nachprüfbar.
5. **Laufzeitpflichten.** Art. 26 Abs. 5 (Überwachung, Meldung), Abs. 6 (Protokolle mind. 6 Monate), Art. 73-Fristen: überwiegend `declared_gap`, Fristenuhr fehlt (M-F3). Ein Agent „im Betrieb“ ohne Laufzeitprüfung ist ein Zulassungsprüfer.
6. **Rechtliche Absicherung.** 47 `in`-Zeilen stehen auf HYPOTHESE, dazu die Auslegungsentscheide des PO (Q1, Q11, A-F1, F4 …). Vor Kundeneinsatz: juristische Zweitprüfung und ein Haftungsrahmen („Prüf- und Nachweiswerkzeug, kein Rechtsrat“). Auslegungen, die je Kunde anders ausfallen können, gehören als **Parameter** ins Manifest, nicht fest in den Katalog.
7. **Souveräner Betrieb.** CI auf GitHub Actions, Signatur über das öffentliche Sigstore (Fulcio/Rekor, OIDC-Identität von GitHub), Referenz-Deployment AKS. Für einen KRITIS-Betreiber – und für die Positionierung „EU-souverän“ – fehlt ein Pfad mit selbst betriebener CI, eigener PKI oder privatem Sigstore und Kubernetes bei einem EU-Anbieter oder on-prem.
8. **Marktzuschnitt.** Für einen Verteilnetzbetreiber kosten NIS2/BSIG, KRITIS-DachG, EnWG und DSGVO mehr als der AI Act; der Sektorstapel kommt laut Plan nach dem Agenten. Als erstes Modul tragfähig, wenn der Agent seine Grenze nennt (so geplant) – aber mit Kunden früh prüfen. Beispiel: wo keine FRIA geschuldet ist (Q1), ist die DSFA nach Art. 35 DSGVO oft die eigentliche Pflicht (Art. 26 Abs. 9 verweist darauf).
9. **Der Agent selbst.** Einordnung nach AI Act offen (P9-2). Architekturgrundsatz, der aus dem Leitsatz folgt: **das Urteil kommt deterministisch aus Gates und Store; ein Sprachmodell erklärt, urteilt nie.**
10. **Zeit.** Stichtag Anhang III: 02.12.2027. Kunden brauchen das Werkzeug 6–9 Monate vorher, also Produktreife etwa Q1/Q2 2027 (Einschätzung). Pakete 5 und 6 sind beide „L“.

# Teil 4 – Sind die Prüfungen nach jedem Commit richtig investiert?

```
Wächter auf dem Urteilspfad (HIGH)          Pflege-Wächter (LOW/MEDIUM)
verhindern ein falsches „konform“           halten Doku, Register, Zahlen gleich
→ Kern des Leitsatzes, unverzichtbar        → nützlich, kosten aber Pflege je Änderung
```

- **Ja** für die HIGH-Wächter (Element-Matrix, Nachbar ≠ Prüfer, Omnibus-Neufassungen, menschliche Entscheidung, Extraktor-Schnitt): sie schützen genau das, worauf der Agent urteilen wird.
- **Vorsicht** bei weiteren Pflege-Wächtern: 49 Prüfungen, jede neue verlangsamt Änderungen. Vorschlag FR-3: ein neuer Wächter nur, wenn der Fehler, den er fängt, ein Agent-Urteil verfälschen kann.
- **Verhältnis:** Die letzten Sitzungen gingen überwiegend in Konsistenz und Entscheidungsdokumentation. Das war nötig (z. B. Art. 3 Nr. 49 trug den Text einer anderen Norm), aber der kritische Pfad zum Produkt ist Bauen, Belege härten, Pilot.

# Teil 5 – Die Entscheide vom 05.10.2026, fachlich

| Punkt | Einschätzung |
|---|---|
| Q1 b (FRIA intern) | Tragfähig: Art. 27 Abs. 1 nimmt Anhang III Nr. 2 ausdrücklich aus, unabhängig vom Betreibertyp. Folge für den Agenten: er muss „verstößt gegen interne Vorgabe“ von „verstößt gegen Gesetz“ trennen (R-8-Wächter sichert die Daten dafür). |
| Q11 a (Art. 26 Abs. 11 n.e.) | Vertretbar, aber angreifbar: der Wortlaut sagt „natürliche Personen **betreffende** Entscheidungen“ – weit gefasst. Redispatch 2.0 bezieht Anlagen ab 100 kW ein; ist deren Betreiber eine natürliche Person, betrifft eine Abregelung ihn (HYPOTHESE). Vorschlag FR-1: Bedingungsparameter wie P2-F4 statt festem „n.e.“. |
| S3-1 a | Richtig und das richtige Muster (Parameter „Betreiber ist Behörde“). |
| P3-B1 a | Richtig, strenger: ungeprüfter Fristbeginn ist eine echte Teillücke. |
| A-F1 a | Richtig: Anhang IV richtet sich an den Anbieter; der Betreiber bekommt seine Informationen über Art. 13. |
| S3-2 a | Richtig; deckte nebenbei einen falschen Pflichttext auf (lit. d trug Nr. 50–61). |

# Teil 6 – Vorschlag: Reihenfolge

```
jetzt ─► PO-Runde schlank abschließen (P4-F1, IN-1 Gr. 1, S3-3, S3-4 auf Leitlinien begrenzen, OUT-1)
      ─► T-16.2–16.4 (Belege, Begründung, Freigabe beweisfest)
      ─► Paket 5 Bedarfsanalyse ─► Paket 6 nach MUST + Stichtag
parallel:
      ├─ Redispatch-Referenzszenario: Fixtures + ein End-to-End-Lauf (FR-2)
      ├─ P9-1 Use Cases des Agenten mit 1–2 Netzbetreibern (FR-2)
      └─ Pfad souveräner Betrieb als eigenes Paket planen (FR-4)
vor Paket 8/9: juristische Zweitprüfung der Auslegungsentscheide (FR-5)
```

- **MVP-Vorschlag** (für Kundengespräche): Readiness-Bericht über alle Betreiberpflichten mit Belegpfad + Nachweis-Pipeline für Art. 26/13/14/73 mit signierter Freigabe (E-1).

# Teil 7 – Fragen

| # | Frage | Optionen |
|---|---|---|
| FR-1 | Art. 26 Abs. 11 (Q11 a) als Bedingungsparameter führen? | a) **ja:** Manifest-Feld „natürliche Personen unter den betroffenen Anlagenbetreibern“; bei `true` meldet ein Check die Zeile als Lücke (wie P2-F4, Bau Paket 5) · b) nein, Q11 a bleibt fest |
| FR-2 | Redispatch-Referenzszenario und Use Cases des Agenten (P9-1) vorziehen, parallel zu Paket 5? | a) **ja, beides** · b) nur Referenzszenario · c) Reihenfolge bleibt (Teil C) |
| FR-3 | Kriterium für neue Wächter: nur, wenn der Fehler ein Agent-Urteil verfälschen kann; Pflege-Wächter nur noch auf Antrag des PO | a) **ja** · b) nein, wie bisher |
| FR-4 | Souveräner Betriebspfad (selbst betriebene CI, eigene PKI oder privates Sigstore, Kubernetes bei EU-Anbieter oder on-prem) als eigenes Paket | a) **ja, als Paket nach 8, vor dem ersten Kunden** · b) später · c) nicht im Repo |
| FR-5 | Juristische Zweitprüfung der Auslegungsentscheide (Q1, Q11, A-F1, F4 und der HYPOTHESE-Zeilen mit Befund) vor Paket 8 | a) **ja** · b) erst vor dem ersten Kunden · c) nein |

# Ehrlich zur Methode

- Zahlen am Repo gemessen (Stand `f56e69b`); Einschätzungen zu Markt, Zeit und Rechtsrisiko sind Einschätzungen, kein Rechtsrat.
- Nicht geprüft: Rego-Qualität jenseits der Element-Matrix, Kubernetes-Pfad im Cluster, PostgreSQL-Pfad des Stores.
- Q11-Gegenargument (Anlagen ab 100 kW, private Betreiber) stützt sich auf Branchenquellen, nicht auf eine amtliche Auslegung.
