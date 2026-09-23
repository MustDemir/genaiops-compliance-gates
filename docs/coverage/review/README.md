# Deckungsanalyse – PO-Durchsicht des Pflichtenraums

Arbeitsdokumente zur Abnahme von SPEC-06 / T-12: Die Vorschläge der Nachtläufe im Pflichtenraum (`po_bestaetigt: false`) werden Schritt für Schritt geprüft und vom PO entschieden.

**Basis:** Branch `spec06-aiact-stufe0` (Pflichtenraum mit 1062 Einheiten, Raster aus T-13)
**Sprache:** Deutsch, wie HANDBUCH und HISTORIE
**Status:** Vorschläge und PO-Entscheide – im Pflichtenraum selbst ist noch nichts geändert

| Nr. | Datei | Inhalt | Status |
|---|---|---|---|
| 00 | [`00-systembild-und-plan.md`](00-systembild-und-plan.md) | Systembild (Zweck, Gate-Logik, Ist-Stand) + Plan Schritt 1–5 | vom PO bestätigt 23.09.2026 |
| 01 | [`01-schritt-2a-nicht-einschlaegig.md`](01-schritt-2a-nicht-einschlaegig.md) | 22 × `nicht_einschlaegig` neu eingeordnet, Raster-Ergänzungen | vom PO bestätigt 23.09.2026 |
| 02 | [`02-schritt-2b-luecken.md`](02-schritt-2b-luecken.md) | **v2 konsolidiert:** 24 Lücken in P0–P8, Verifikationsstufen, steuernde Normen, Omnibus-Vollprüfung, Entscheidungsvorlage E1–E8 | **entschieden 23.09.2026** (E1–E8 angenommen) |
| 03 | [`03-gegenpruefung-omnibus-art26-out.md`](03-gegenpruefung-omnibus-art26-out.md) | Omnibus selbst gelesen, Art. 26 Volltext, ~280 `out`-Zeilen geprüft; Werkzeugbefunde T1–T4 | in 02 v2 eingearbeitet |

Ticket-Entwurf zu den Werkzeugbefunden: [`../../tickets/T-14-pflichtenraum-werkzeug.md`](../../tickets/T-14-pflichtenraum-werkzeug.md)

## Plan

```
1 Verstehen ✅ → 2a ✅ → 2b (offen) → Gegenprüfung (offen) → 2c Teilabdeckungen → 3 PO-Entscheid → 4 Bedarf Requirements/Rego/Gates → 5 Tickets
```

## Nächste Schritte

- T-14 umsetzen (BEREIT seit 23.09.2026) – vor 2c und vor dem Anhänge-Lauf
- 2c: 33 Teilabdeckungen, Leitfrage Q9 (Betreiber-Requirements auf Anbieterartikeln)
