# Deckungsanalyse – PO-Durchsicht des Pflichtenraums

Arbeitsdokumente zur Abnahme von SPEC-06 / T-12: Die Vorschläge der Nachtläufe im Pflichtenraum (`po_bestaetigt: false`) werden Schritt für Schritt geprüft und vom PO entschieden.

**Basis:** Branch `spec06-aiact-stufe0` (Pflichtenraum mit 1062 Einheiten, Raster aus T-13)
**Sprache:** Deutsch, wie HANDBUCH und HISTORIE
**Status:** PO-Entscheide vom 23.09.2026 stehen seit T-14.5 auch im Pflichtenraum – maschinenlesbar in `docs/coverage/entscheide/`, gehalten von `PO_DECISIONS_APPLIED`

| Nr. | Datei | Inhalt | Status |
|---|---|---|---|
| 00 | [`00-systembild-und-plan.md`](00-systembild-und-plan.md) | Leitsatz (Ziel) + Systembild (Zweck, Gate-Logik, Ist-Stand) + Plan Schritt 1–5 | vom PO bestätigt 23.09.2026 |
| 01 | [`01-schritt-2a-nicht-einschlaegig.md`](01-schritt-2a-nicht-einschlaegig.md) | 22 × `nicht_einschlaegig` neu eingeordnet, Raster-Ergänzungen | vom PO bestätigt 23.09.2026 |
| 02 | [`02-schritt-2b-luecken.md`](02-schritt-2b-luecken.md) | **v2 konsolidiert:** 26 Lücken in P0–P8 (24 + 2 aus T-14.1; im Pflichtenraum 27 Zeilen, weil Art. 5 Abs. 1 lit. c Ziff. i und ii getrennt stehen), Verifikationsstufen, steuernde Normen, Omnibus-Vollprüfung, Entscheidungsvorlage E1–E8 | **entschieden 23.09.2026** (E1–E8 angenommen) |
| 03 | [`03-gegenpruefung-omnibus-art26-out.md`](03-gegenpruefung-omnibus-art26-out.md) | Omnibus selbst gelesen, Art. 26 Volltext, ~280 `out`-Zeilen geprüft; Werkzeugbefunde T1–T4 | in 02 v2 eingearbeitet |
| 04 | [`04-schritt-2c-teilabdeckungen.md`](04-schritt-2c-teilabdeckungen.md) | 44 Teilabdeckungen in 6 Clustern, Maßnahmen je Zeile, Q9 (Requirements ohne Betreiber-Anker), Befunde zu Art. 73 | **entschieden 28.09.2026** (F1a–F6a) |
| 05 | [`05-schritt-2d-2e-gedeckt-querbefunde.md`](05-schritt-2d-2e-gedeckt-querbefunde.md) | Gegenprobe der 3 gedeckten Zeilen, 17 Querbefunde mit Stand | Vorschlag – Entscheidungsvorlage D1, D2, E1–E3 |

Ticket-Entwurf zu den Werkzeugbefunden: [`../../tickets/T-14-pflichtenraum-werkzeug.md`](../../tickets/T-14-pflichtenraum-werkzeug.md)

## Plan

```
1 Verstehen ✅ → 2a ✅ → 2b ✅ → Gegenprüfung ✅ → T-14 ✅ → 2c ✅ → 2d/2e (Vorlage) → 3 PO-Entscheid → 4 Bedarf Requirements/Rego/Gates → 5 Tickets
```

## Nächste Schritte

- T-14 abgenommen 28.09.2026. Geliefert: T-14.1 (eindeutige IDs, Art. 3 nach Nummern), T-14.2 (Omnibus als eigene Quelle), T-14.3 (Satzebene für vier Absätze), T-14.4 (`NORM_REFS_RESOLVE`), T-14.5 (PO-Entscheide im Pflichtenraum). Offen beim PO: Entscheide, die eine Teilung offengelassen hat (Art. 111 Abs. 2 Satz 2, Unterglieder), Verifikationsstufe der 22 steuernden bzw. neuen Zeilen
- 2c: 33 Teilabdeckungen, Leitfrage Q9 (Betreiber-Requirements auf Anbieterartikeln)
