# Deckungsanalyse – PO-Durchsicht des Pflichtenraums

Arbeitsdokumente zur Abnahme von SPEC-06 / T-12: Die Vorschläge der Nachtläufe im Pflichtenraum (`po_bestaetigt: false`) werden Schritt für Schritt geprüft und vom PO entschieden.

**Basis:** Branch `spec06-aiact-stufe0` (Pflichtenraum mit 1062 Einheiten, Raster aus T-13)
**Sprache:** Deutsch, wie HANDBUCH und HISTORIE
**Status:** PO-Entscheide vom 23.09.2026 stehen seit T-14.5 auch im Pflichtenraum – maschinenlesbar in `docs/coverage/entscheide/`, gehalten von `PO_DECISIONS_APPLIED`

| Nr. | Datei | Inhalt | Status |
|---|---|---|---|
| 00 | [`00-systembild-und-plan.md`](00-systembild-und-plan.md) | Leitsatz (Ziel) + Systembild (Zweck, Gate-Logik, Ist-Stand) + Plan Schritt 1–5 + Teil C: Ziellinie, acht Pakete, Reihenfolge bis zum Prüf-Agenten | vom PO bestätigt 23.09.2026 · Teil C 29.09.2026 |
| 01 | [`01-schritt-2a-nicht-einschlaegig.md`](01-schritt-2a-nicht-einschlaegig.md) | 22 × `nicht_einschlaegig` neu eingeordnet, Raster-Ergänzungen | vom PO bestätigt 23.09.2026 |
| 02 | [`02-schritt-2b-luecken.md`](02-schritt-2b-luecken.md) | **v2 konsolidiert:** 26 Lücken in P0–P8 (24 + 2 aus T-14.1; im Pflichtenraum 27 Zeilen, weil Art. 5 Abs. 1 lit. c Ziff. i und ii getrennt stehen), Verifikationsstufen, steuernde Normen, Omnibus-Vollprüfung, Entscheidungsvorlage E1–E8 | **entschieden 23.09.2026** (E1–E8 angenommen) |
| 03 | [`03-gegenpruefung-omnibus-art26-out.md`](03-gegenpruefung-omnibus-art26-out.md) | Omnibus selbst gelesen, Art. 26 Volltext, ~280 `out`-Zeilen geprüft; Werkzeugbefunde T1–T4 | in 02 v2 eingearbeitet |
| 04 | [`04-schritt-2c-teilabdeckungen.md`](04-schritt-2c-teilabdeckungen.md) | 44 Teilabdeckungen in 6 Clustern, Maßnahmen je Zeile, Q9 (Requirements ohne Betreiber-Anker), Befunde zu Art. 73 | **entschieden 28.09.2026** (F1a–F6a) |
| 05 | [`05-schritt-2d-2e-gedeckt-querbefunde.md`](05-schritt-2d-2e-gedeckt-querbefunde.md) | Gegenprobe der 3 gedeckten Zeilen, 17 Querbefunde mit Stand | Vorschlag – Entscheidungsvorlage D1, D2, E1–E3 |
| 06 | [`06-grenzen-statt-teilabdeckung.md`](06-grenzen-statt-teilabdeckung.md) | Teilabdeckung getrennt in Grenze (Element ungeprüft) und gedeckt mit E-0; Hinweisfunktion am Gate | **entschieden 28./29.09.2026** (H1b, H2a, H3a, H4 Option 1) |
| 07 | [`07-element-matrix.md`](07-element-matrix.md) | Alle 50 Pflichten mit Gate-Bezug gegen die 196 Regeln aus dem Code; Korrekturen, Methodenfrage Nachbarprüfung | M2a entschieden 29.09.2026 · M1 offen (Paket 4) |
| 08 | [`08-paket-1-anhaenge.md`](08-paket-1-anhaenge.md) | Paket 1: 206 Anhang-Einheiten und Art. 113 eingeordnet (4 in, alle steuernd; 206 out), Omnibus-Änderungen an Anhängen, Fragen A-F1, A-F2 | Vorschlag – Stichprobe in Paket 4 |
| 09 | [`09-paket-2-omnibus.md`](09-paket-2-omnibus.md) | Paket 2: 259 Omnibus-Einheiten eingeordnet (100 Änderungsanweisungen out; 159 n.F.: 11 in, 148 out), A-F2a umgesetzt (6 AI-Act-Zeilen ersetzt → out), Wächter `OMNIBUS_SUPERSEDED_UNITS_OUT`, Fragen P2-F1–F5, R-2 | **entschieden 29.09.2026** (P2-F1 a, F2 a, F3 a, F4 c, F5 a, R-2 HIGH) |
| 10 | [`10-paket-3-werkzeug.md`](10-paket-3-werkzeug.md) | Paket 3a, Werkzeug T-15: Art.-113-Kennungen, Anhang I Abschn. B, Fußzeile, Überschriften im Beleg, Omnibus Abs. 1b/Art. 75b; alle Räume neu gebaut; Wächter `NORM_UNITS_MATCH_EXTRACTOR` | Teil 1 geliefert · Teil 2 (Unterabsätze nach Listen) offen |
| – | [`entscheidungsregister.md`](entscheidungsregister.md) | **Alle offenen Entscheide des PO und ausstehenden Schritte mit Ziel-Paket** (Wächter `PO_DECISIONS_REGISTERED`) | lebend |

Ticket-Entwurf zu den Werkzeugbefunden: [`../../tickets/T-14-pflichtenraum-werkzeug.md`](../../tickets/T-14-pflichtenraum-werkzeug.md)

## Plan

```
1 Verstehen ✅ → 2a ✅ → 2b ✅ → Gegenprüfung ✅ → T-14 ✅ → 2c ✅ → 2d/2e ✅ → 06 ✅ → 07 (M2 ✅, M1 offen)

ab 29.09.2026 (00 Teil C): 1 Anhänge ✅ (Vorschlag, 08) → 2 Omnibus n.F. ✅ (Vorschlag, 09) → 3 Befunde + Matrix-Lauf 2 → 4 PO-Runde
                           → 5 Bedarfsanalyse → 6 Bauen → 7 known_limits + Wächter → 8 PR → 9 Prüf-Agent
```

## Nächste Schritte

- T-14 abgenommen 28.09.2026. Geliefert: T-14.1 (eindeutige IDs, Art. 3 nach Nummern), T-14.2 (Omnibus als eigene Quelle), T-14.3 (Satzebene für vier Absätze), T-14.4 (`NORM_REFS_RESOLVE`), T-14.5 (PO-Entscheide im Pflichtenraum). Offen beim PO: Entscheide, die eine Teilung offengelassen hat (Art. 111 Abs. 2 Satz 2, Unterglieder), Verifikationsstufe der 22 steuernden bzw. neuen Zeilen
- 2c: 33 Teilabdeckungen, Leitfrage Q9 (Betreiber-Requirements auf Anbieterartikeln)
