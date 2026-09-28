# T-14 — Pflichtenraum: eindeutige IDs, Art. 3 nach Nummern, Omnibus als eigene Einheiten

**Status:** ABGENOMMEN 28.09.2026 · gestellt 23.09.2026 · P-1/P-2 entschieden 23.09.2026, P-3/P-4 entschieden 28.09.2026 · geliefert: T-14.1, T-14.2, T-14.3 (Satzebene), T-14.4 (`NORM_REFS_RESOLVE`), T-14.5 (PO-Entscheide im Pflichtenraum)
**Bezug:** [`SPEC-06`](../../specs/SPEC-06-deckungsanalyse-norm-requirement.md) · [`T-12`](T-12-cowork-aiact-stufe0.md) · [`T-13`](T-13-cowork-sektorstapel.md) · Gegenprüfung `docs/coverage/review/03-gegenpruefung-omnibus-art26-out.md` · 2b v2 `docs/coverage/review/02-schritt-2b-luecken.md`

---

## WARUM

Die PO-Durchsicht des Pflichtenraums (23.09.) hat vier Werkzeugbefunde ergeben. Sie sind keine Auslegungsfragen, sondern Konstruktionsmängel – und jeder weitere Lauf (Anhänge, Sektorstapel) würde auf ihnen aufbauen.

| ID | Befund | Gemessen |
|---|---|---|
| T1 | **Omnibus-Neuerungen haben keine Einheit.** Der Pflichtenraum ist die Grundfassung; eingefügte Normen fehlen (u. a. Art. 4 Abs. 2/3, 4a, 5 Abs. 1 lit. ba/bb + Abs. 1a/1b, 6 Abs. 1a–1c, 25 Abs. 2 lit. a–c, 60a, 111 Abs. 4, 113 Abs. 3 lit. c/d n.F.). Bei geänderten Normen zeigt `beleg` den **alten** Text (Art. 4, 111) | Abgleich gegen Art. 1 Nr. 1–43 VO (EU) 2026/1744 |
| T2 | **Art. 3 nicht nach Nummern geschnitten; IDs nicht eindeutig.** Art. 3 = eine Einheit mit 10.818 Zeichen plus falsch geschnittene „lit."-Einheiten. **24 IDs doppelt, 59 Zeilen** (u. a. `Art. 3 lit. a` ×3, `Art. 5 Abs. 1 lit. i` ×2, `Anhang VIII Nr. 1–5` ×3, `Anhang X lit. a/b` ×4). Römische Ziffern (`Art. 13 Abs. 3 lit. i`, `lit. v`) werden als Buchstaben gelesen | Zählung über `id` im Pflichtenraum |
| T3 | **Satzebene nicht umgesetzt** (SPEC-06, PO-Festlegung 2). Einheiten sind Absätze; Mehrpflichten-Absätze bekommen einen Sammelbefund – Art. 26 Abs. 5 trägt vier Pflichten und einen Befund | Art. 26 Abs. 5: `saetze: 5`, eine Zeile |
| T4 | **Zitierte Normen ohne auflösbare Einheit.** Gates und Requirements verweisen auf Normen, die im Pflichtenraum fehlen, `out` oder unbewertet sind (Art. 3 Nr. 14, Art. 3 Abs. 49, Art. 3 Nr. 23, Art. 4a, Art. 6 Abs. 1a–1c, Anhang III Nr. 2, Art. 16, 47, 48, 97). Kein Wächter prüft die Richtung Gate → Pflichtenraum | `grep legal_refs` über `gate-definitions/`, `requirements/` |

T2 bricht die Rückverfolgung: Eine Requirement-Zuordnung auf `Art. 5 Abs. 1 lit. i` ist heute nicht eindeutig. Das ist derselbe Fehlertyp wie B-20: eine Deklaration, die sich nicht gegen ihren Gegenstand halten lässt.

## RECHTSBEZUG

Keiner neu. Quellen: VO (EU) 2024/1689 (`docs/legal/wortlaut/aiact_2024-1689_DE.txt`, SHA-256 im Pflichtenraum) und VO (EU) 2026/1744 (`docs/legal/OJ_L_202601744_DE.pdf`). Das Ticket **schneidet**, es legt nichts aus.

## PO-ENTSCHEIDUNGEN

Die vier Ehrlichkeitsfelder sind nicht betroffen. Entschieden am 23.09.2026 – jeweils Variante (a) bzw. (b) wie empfohlen:

- [x] **P-1 Omnibus-Quelle = (a).** (a) Omnibus-Text als zweite Quelle `docs/legal/wortlaut/omnibus_2026-1744_DE.txt` (aus dem PDF extrahiert, gehasht), neue Einheiten mit `quelle: 2026/1744` und eigenem Offset · **oder** (b) konsolidierte Fassung selbst erzeugen. **Empfehlung (a)**: bestehende Offsets bleiben gültig, Herkunft je Einheit nachweisbar, keine selbst erzeugte Rechtsfassung
- [x] **P-2 Satzebene = (b).** (a) alle Einheiten auf Sätze · **oder** (b) nur Absätze mit mehr als einer Pflicht (Liste vom PO, Start: Art. 26 Abs. 5, Art. 13 Abs. 3 lit. b, Art. 73 Abs. 2). **Empfehlung (b)**: Aufwand proportional zum Nutzen, Befunde bleiben lesbar

- [x] **P-3 Satzebene-Liste (28.09.2026).** Art. 26 Abs. 5 · Art. 73 Abs. 2 · Art. 15 Abs. 4 · Art. 111 Abs. 2 (Grundfassung und n.F.). Art. 13 Abs. 3 lit. b ist durch T-14.1 schon nach Ziffern geschnitten. Die Liste steht in `docs/coverage/entscheide/satzebene.yaml`, `NORM_SENTENCE_UNITS_CURRENT` hält den Pflichtenraum dagegen
- [x] **P-4 PO-Entscheide in den Pflichtenraum (28.09.2026).** Die bereits getroffenen Entscheide (2a, 2b E1–E8, T-14.1) werden als T-14.5 in `aiact_pflichtenraum.yaml` geschrieben – nur Entschiedenes, mit Verweis auf das Review-Dokument je Zeile

Festgelegt (aus 2a/2b):
- Steuernde Normen (Art. 2 Abs. 1 lit. b, Art. 3 Nr. 4/8/14/23/49, Art. 6 Abs. 1a–1c/2/3, Art. 111 Abs. 2, Art. 113 Abs. 3, Anhang III Nr. 2) bekommen adressierbare Einheiten
- Raster-Ergänzungen aus 2a (Systemtyp, bedingte Pflicht) werden in T-13 „Wie `scope` und `befund` entschieden werden" nachgetragen

## SCOPE IN

- `tools/legal/extract_norm_units.py` – Art. 3 nach Nummern, römische Ziffern, eindeutige IDs
- `tools/legal/build_pflichtenraum.py` – Omnibus-Einheiten, Migration der Analysefelder
- `tools/legal/verify_norm_quotes.py` – zweite Quelle
- `tools/legal/fortschritt.py` – Zählung je Quelle
- Integrity-Suite: neue Checks `NORM_UNIT_IDS_UNIQUE`, `NORM_REFS_RESOLVE`
- `docs/coverage/aiact_pflichtenraum.yaml` – **nur** Struktur und Migration; Analysefelder werden übernommen, nicht neu entschieden
- **neu** `docs/legal/wortlaut/omnibus_2026-1744_DE.txt` (nur bei P-1 = a)

## SCOPE OUT

- Bestehende Dateien unter `docs/legal/**` – gehashte Primärquellen, unverändert
- `scope`, `befund`, `verifikation` neu entscheiden – bleibt beim PO (Schritt 3)
- Gates, Requirements, Policies
- Sektorstapel-Pflichtenräume (T-13) – profitieren vom Werkzeug, werden aber hier nicht bearbeitet
- Push auf `domain_netzbetrieb`

## DEFINITION OF READY

1. P-1 und P-2 entschieden ✅ 23.09.2026
2. 2b v2 Entscheid E5, E6, E8 (steuernde Normen, Omnibus-Korrekturen, Reihenfolge) liegt vor ✅ 23.09.2026
3. Omnibus-PDF lässt sich mit stabilem Text extrahieren ✅ Probe 23.09.2026: `pdftotext -layout` liefert Art. 1 Nr. 1–43 vollständig (2800 Zeilen)

## DEFINITION OF DONE — maschinell

1. `NORM_UNIT_IDS_UNIQUE` grün: **0** doppelte IDs (heute 24 / 59 Zeilen)
2. Art. 3: je Begriffsbestimmung eine Einheit `Art. 3 Nr. N`; Anzahl gleich der Zählung im Quelltext; Nr. 14 n.F., 14a, 14b vorhanden
3. Omnibus: jede Änderungsanweisung Art. 1 Nr. 1–43 ist mindestens einer Einheit zugeordnet (Bericht: Nr. → Einheiten, 0 ohne Zuordnung)
4. `verify_norm_quotes.py` BESTANDEN für **beide** Quellen, Modus `belege`
5. Migration verlustfrei: Anzahl befüllter Analysefelder vorher = nachher, Zuordnungsbericht alte ID → neue ID(s)
6. `NORM_REFS_RESOLVE` läuft, meldet jede `legal_ref` aus `gate-definitions/` und `requirements/` ohne auflösbare Einheit – **zunächst als Warnung**, Severity entscheidet der PO nach Sichtung der Liste
7. `make verify` grün

## ABNAHME DURCH DEN PO

- Severity `NORM_UNIT_IDS_UNIQUE` = HIGH, vom PO bestätigt 23.09.2026 (T-14.1)
- Severity `NORM_SENTENCE_UNITS_CURRENT` = MEDIUM, `PO_DECISIONS_APPLIED` = HIGH, `NORM_REFS_RESOLVE` = INFO (Warnung), vom PO bestätigt 28.09.2026
- Die zwei Verweise, die `NORM_REFS_RESOLVE` fand (G-OPS-02: `Art. 3 Abs. 49` statt `Nr. 49`), auf Entscheid des PO sofort berichtigt, 28.09.2026
- **Abgenommen 28.09.2026**, Push freigegeben
- **Roter Lauf 1:** eine ID doppelt einfügen → `NORM_UNIT_IDS_UNIQUE` rot, zurücknehmen → grün
- **Roter Lauf 2:** eine `legal_ref` auf eine nicht existierende Einheit setzen → `NORM_REFS_RESOLVE` meldet sie namentlich
- **Roter Lauf 3:** ein Zeichen im Omnibus-Beleg ändern → `verify_norm_quotes.py` rot
- Zuordnungsbericht alte → neue IDs zur Sichtprüfung
- Gegenprobe gegen committeten Stand (AGENTS.md 5)

## COMMIT

Commit ja, ein Commit je logischer Gruppe (Extraktor · Omnibus-Quelle · Migration · Integrity-Checks). Branch `spec06-aiact-stufe0` oder Feature-Branch davon, PR gegen `domain_netzbetrieb`. Kein Push ohne Freigabe des PO. Keine `Co-Authored-By`-Zeile. Die Nachricht sagt, was jetzt wahr ist, z. B. `fix(legal): every norm unit has a unique id, and Art. 3 is cut by definition number`.
