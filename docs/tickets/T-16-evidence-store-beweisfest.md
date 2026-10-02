# T-16 — Evidence Store beweisfest: Grundlage, Begründung und Freigabe jedes Urteils

Ticket T-16. Angelegt 02.10.2026 auf Auftrag des PO („Lücken als Befund ins Register, dann ein Paket für die Lücken, um sie zu schließen“). Befunde und Testlauf: [Review 12](../coverage/review/12-evidence-store-beweis.md). **Status:** ES-F1 a, ES-F2 a entschieden (02.10.2026). Bereit ist ein Teilschritt, wenn seine Ehrlichkeitsfelder gesetzt sind – DoR unten.

## WARUM

Der Evidence Store hält jedes Gate-Urteil hash-verkettet und unveränderbar, und das Manifest jedes CI-Laufs ist mit cosign signiert. Ein Auditor kann damit prüfen, **dass** geurteilt wurde. Nicht prüfen kann er, **worauf** das Urteil beruhte, **warum** es so ausfiel und **was der Mensch** bei der Freigabe geprüft hat. Und eine Ablehnung durch den Prüfer hat keine Wirkung:

| # | Befund (Review 12 Teil 4) | gemessen |
|---|---|---|
| ES-1 | MANUAL FAIL hält die Pipeline nicht an | Testlauf 02.10.2026: G-PRE-05 MANUAL FAIL aufgezeichnet (audit 5), Lauf ging weiter |
| ES-2 | HYBRID-Gate ohne Freigabe läuft durch | `run_pipeline`: Halt nur bei `decision == "FAIL"`; `manual_source` optional |
| ES-3 | Belege nicht gehasht | `payload_id` = `uuid4()` für automatische Zeilen (`record_evidence.build_record`) |
| ES-4 | Begründung nicht hash-gedeckt | `failures` nicht in der DB; `warnings` nur in `notes` (ungehasht); Digest nur `Gate:Urteil` |
| ES-5 | Freigabe-Eintrag unvollständig | `rationale` → `notes`; `evidence_refs`, `review_date`, `reviewer_role`, `approval_conditions` verworfen |
| ES-6 | Belegverzeichnis beim Rollenwechsel fehlt | Vorgabe P3-F3: geschuldete Belege Soll/Ist je Beleg |

## RECHTSBEZUG

Vom PO zu bestätigen (EF, AGENTS.md 3). Stand im Katalog: G-OPS-05 trägt R005 und nennt Art. 12, Art. 15. HYPOTHESE, nicht geprüft: Aufbewahrung der Protokolle durch den Betreiber (Art. 26 Abs. 6), menschliche Aufsicht und ihre Wirksamkeit (Art. 14 Abs. 4, Art. 26 Abs. 2), Übergabe beim Rollenwechsel (Art. 25 Abs. 2 n.F.). Das Ticket baut Infrastruktur; es begründet keine neue Pflicht.

## PO-ENTSCHEIDUNGEN

- **ES-F1 a** (02.10.2026): MANUAL FAIL → block; HYBRID-Gate ohne Freigabe → hält an („wartet auf Freigabe“), Wiederaufnahme mit Freigabe.
- **ES-F2 a** (02.10.2026): jetzt, parallel zu Paket 4; T-16.1 (ES-1, ES-2) zuerst.
- Je neuem Check und Wächter: **Severity MUST/SHOULD**, **evidence_level** (die Freigabe als Datei ist E-0; vom Prüfer signiert wäre sie E-1), **implemented/design_only**.

## SCOPE IN

- `pipeline/gate_orchestrator.py` (Halt-Logik, Input-Digest, Übergabe an den Store)
- `evidence-store/scripts/` (`record_evidence.py`, `verify_hash_chain.py`, `build_manifest.py`), neue Migration v06→v07 mit Cutoff, `POC_SQL_SCHEMA_SPEC.md`, `evidence-store/docs/SCHEMA_EVOLUTION.md`
- `tests/` (Hash-Parität, Manipulationsnachweis, Integritätssuite), Szenarien und Fixtures der Freigaben
- Review 12, Register, HANDBUCH Teil 7

## SCOPE OUT

- Inhalt von C-25d (je Beleg ein Feld) – Maßnahme aus P3-F3, Paket 5/6. T-16 liefert nur, **wie** ein Belegverzeichnis im Store steht (ES-6).
- Vier-Augen-Prinzip beim Schreiben von Requirement/Gate/Policy (T-11) – anderes Thema.
- Eine Oberfläche für Freigaben.

## Teilschritte (Vorschlag, je eigener Commit mit Wächter und rotem Lauf)

```
T-16.1  Wirkung       ES-1, ES-2   MANUAL FAIL → halt · HYBRID ohne Freigabe → halt („wartet auf Freigabe“)
T-16.2  Grundlage     ES-3         Digest der gelesenen Inputs je Gate → payload_id, hash-gedeckt
T-16.3  Begründung    ES-4         Digest der Befunde (Check-ID + Meldung) als Spalte, hash-gedeckt; Manifest mit
T-16.4  Freigabe      ES-5         Freigabe-Eintrag: Prüfer, Rolle, Zeit, Urteil, Begründung, Beleg-Hashes, Auflagen;
                                   Option: Signatur des Prüfers (E-1)
T-16.5  Belege        ES-6         Belegverzeichnis je Rollenwechsel: Soll/Ist/Hash je Beleg (mit Paket 6, P3-F3)
```

## DEFINITION OF READY

- ES-F1 und ES-F2 entschieden. ✓ 02.10.2026
- Je Teilschritt: Severity und evidence_level der neuen Checks vom PO gesetzt.

## DEFINITION OF DONE — maschinell

- **T-16.1:** Szenario mit MANUAL FAIL → Exit 1, `halt_gate` = das Gate; HYBRID-Gate ohne Freigabe → Exit 1 mit eigenem Grund. Beide Negativfälle in der CI (`negative-cases`).
- **T-16.2:** Ein geänderter Input bei gleichem Urteil ergibt einen anderen `payload_id`; `verify_hash_chain.py` meldet eine nachträglich getauschte Belegdatei, deren Hash nicht mehr passt.
- **T-16.3/16.4:** Eine nachträglich geänderte Begründung oder Belegliste macht `verify_hash_chain.py` rot.
- `make verify` grün; Hash-Parität (`test_hash_parity.py`) über Python und SQL-Trigger.

## ABNAHME DURCH DEN PO

Je Teilschritt der rote Lauf: die Manipulation bzw. Ablehnung, die vorher durchging, und jetzt hält.

## COMMIT

Je Teilschritt ein Commit. Kein Push ohne Freigabe des PO.
