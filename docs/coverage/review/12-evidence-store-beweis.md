---
titel: Evidence Store – hält er, was ein Auditor sehen will?
stand: 2026-10-02
basis: Branch review-2c · Frage des PO 01.10.2026 („werden alle Gate-Entscheidungen, Belege und Freigaben mit Hash im Audit festgehalten?“) · Code pipeline/gate_orchestrator.py, evidence-store/scripts/*, POC_SQL_SCHEMA_SPEC.md · Testlauf poc_healthcare_pass mit abgelehnter Freigabe
status: Befunde ES-1–ES-6 · ES-F1 a, ES-F2 a entschieden (PO 02.10.2026) · Paket T-16 läuft, zuerst T-16.1
---

# Kurzfazit

- **Urteile sind beweisfest, ihre Grundlage nicht.** Jedes Gate-Urteil steht hash-verkettet und unveränderbar im Evidence Store; das Manifest jedes CI-Laufs ist mit cosign signiert.
- **Was fehlt:** welche Belege das Gate gesehen hat, warum es so urteilte, und was der Mensch bei der Freigabe geprüft hat. Was nie im Store steht, kann auch cosign nicht versiegeln.
- **Schwerster Befund (ES-1), im Testlauf gezeigt:** Lehnt der Prüfer ab (MANUAL FAIL), läuft die Pipeline weiter.
- PO 02.10.2026: Befunde ins Register, ein eigenes Paket zum Schließen → **T-16 „Evidence Store beweisfest“**.

# Teil 1 – Soll (Gedanken des PO, technisch)

```
Belege (Input) ──Hash──► Gate (Rego) ──► Urteil + Begründung ──► Evidence Store (Kette, append-only)
                                              │                              │
                            HYBRID: Mensch prüft Belege                       ▼
                            richtig + vollständig?               Manifest je Lauf ──cosign──► signiert
                                              │                              │
                            Freigabe / Ablehnung ──► Evidence Store           ▼
                                              │                       Auditor prüft:
                            Ablehnung → Pipeline stoppt              Kette · Signatur · Beleg-Hash = Datei
```

| # | Soll |
|---|---|
| S1 | Jedes Urteil (PASS/FAIL, block/manual_review/warn/approve) mit Begründung im Store, hash-gedeckt |
| S2 | Woran das Gate urteilte (die Belege), per Hash festgehalten |
| S3 | Beim Rollenwechsel: geschuldete Belege, Soll und Ist (P3-F3) |
| S4 | Freigabe durch einen Menschen: wer, wann, Rolle, Urteil, Begründung, geprüfte Belege, Auflagen – hash-gedeckt |
| S5 | Die Freigabe wirkt: Ablehnung stoppt, ohne Freigabe kein Weiter |
| S6 | Ein Auditor kann alles unabhängig nachprüfen |

# Teil 2 – Ist (am Code geprüft)

**Was schon trägt:**
- Je Gate eine Zeile in `quality_gate_results`, SHA-256-verkettet über Modell, Lauf, Gate, Urteil, Methode, `payload_id`, Zeit, `inserted_by`, Rolle, `derived_decision`, Laufmodus, Vorgänger-Hash.
- PostgreSQL: Trigger verbietet UPDATE/DELETE, RLS mit drei Rollen; `verify_hash_chain.py` findet jede Änderung.
- Fail-closed: Schlägt das Schreiben fehl, hält der Lauf an (B-16).
- Manifest je Lauf (`chain_head`, Digest aller Urteile, Commit): in der CI mit **cosign keyless** signiert (OIDC-Identität des Workflows, Rekor-Eintrag), identitätsgebunden geprüft; G-OPS-05/C-04–C-07 werten die Prüfung aus.

| # | Ist | Stand |
|---|---|---|
| S1 | Urteil hash-gedeckt ✓. **Begründung nicht:** die Meldungen der verletzten MUST-Checks stehen nicht in der Datenbank; Warnungen nur im ungehashten `notes`. Im Bericht stehen sie, der Bericht ist nicht signiert; der Manifest-Digest deckt nur `Gate:Urteil` | ◐ |
| S2 | **Belege nicht gehasht.** `payload_id` einer automatischen Zeile ist eine Zufalls-UUID; kein Digest der gelesenen Inputs, weder in der Zeile noch im Manifest | ❌ |
| S3 | gibt es nicht; C-25d prüft nur „Übergabebeleg vorhanden“ (P3-F3) | ❌ |
| S4 | MANUAL-Zeile: Urteil und Prüfer (`inserted_by`) hash-gedeckt ✓. Begründung nur in `notes` (ungehasht). `evidence_refs`, `review_date`, `reviewer_role`, `approval_conditions` werden **verworfen**. Die Freigabe ist eine vorbereitete JSON-Datei, ohne Signatur des Prüfers | ◐ |
| S5 | **Nein** (Teil 3). Angehalten wird nur bei automatischem FAIL. Ein HYBRID-Gate ohne Freigabedatei läuft durch; `manual_review` wird nur notiert. Pflicht ist die Freigabedatei nur im Szenario `poc_healthcare_pass.json` (Wächter `HYBRID_MANUAL_SOURCE`) | ❌ |
| S6 | Kette, Signatur, Urteile prüfbar ✓ · Grundlage, Belege, Begründung der Freigabe nicht | ◐ |

- **cosign versiegelt, was im Store steht.** Fehlt etwas im Store (S2, S4), ist es auch im signierten Manifest nicht enthalten. Signatur ≠ Vollständigkeit.

# Teil 3 – Testlauf (02.10.2026, Cloud, SQLite)

Szenario `poc_healthcare_pass.json`, Freigabe zu G-PRE-05 auf `FAIL` gesetzt („Belege unvollständig“):

```
audit 4  G-PRE-05  PASS  HYBRID  manual_review  pipeline_automation
audit 5  G-PRE-05  FAIL  MANUAL  –              Prof. Dr. Weber (AI Governance Lead)
→ Konsole: „G-PRE-05 … Decision: PASS | Derived: manual_review“
→ Pipeline läuft weiter: G-DEP-02, G-OPS-03 …
→ Manifest-Digest enthält G-PRE-05:FAIL und G-PRE-05:PASS
```

- Der Lauf hielt später an G-OPS-03 – die Drift-Messung im Sandkasten war älter als erlaubt; kein Bezug zu dieser Frage.

# Teil 4 – Befunde

| # | Befund | Wohin |
|---|---|---|
| ES-1 | **Ablehnung wirkt nicht:** Ein MANUAL FAIL wird aufgezeichnet, hält die Pipeline aber nicht an; der Halt hängt nur am automatischen PASS/FAIL (Testlauf Teil 3) | T-16 |
| ES-2 | **Fehlende Freigabe wirkt nicht:** Ein HYBRID-Gate ohne menschliche Entscheidung läuft durch; `manual_review` ist nur ein Vermerk. Die Freigabedatei ist nur für ein Szenario Pflicht | T-16 |
| ES-3 | **Belege nicht gebunden:** Die gelesenen Inputs eines Gates werden nicht gehasht; `payload_id` ist eine Zufalls-UUID. Beweisbar ist das Urteil, nicht seine Grundlage | T-16 |
| ES-4 | **Begründung nicht hash-gedeckt:** Meldungen verletzter MUST-Checks fehlen in der Datenbank, Warnungen stehen nur im ungehashten `notes`; der Manifest-Digest deckt nur `Gate:Urteil` | T-16 |
| ES-5 | **Freigabe-Eintrag unvollständig:** Begründung ungehasht; geprüfte Belege, Datum, Rolle und Auflagen werden verworfen; keine Signatur des Prüfers | T-16 |
| ES-6 | **Belegverzeichnis beim Rollenwechsel fehlt im Store:** Soll und Ist je geschuldetem Beleg (Art. 25 Abs. 2 n.F., Vorgabe P3-F3) | T-16 |

# Teil 5 – Fragen

**a ist jeweils die Empfehlung.**

| # | Frage | Optionen |
|---|---|---|
| **ES-F1** | Wirkung der menschlichen Entscheidung | a) **beides hält an:** MANUAL FAIL → block; HYBRID-Gate ohne Freigabe → hält an („wartet auf Freigabe“), Wiederaufnahme mit Freigabe · b) nur MANUAL FAIL hält an, fehlende Freigabe ist `warn` |
| **ES-F2** | Wann kommt T-16? | a) **jetzt, parallel zu Paket 4**; zuerst ES-1/ES-2 (klein, größtes Risiko), dann ES-3–ES-5; ES-6 mit der P3-F3-Maßnahme in Paket 6 · b) nach Paket 5, mit den übrigen Bauten |

**Entschieden 02.10.2026:** ES-F1 **a** (Ablehnung und fehlende Freigabe halten an) · ES-F2 **a** (T-16 jetzt, parallel zu Paket 4, T-16.1 zuerst).

# Teil 6 – Paket T-16

- Ticket: [`T-16-evidence-store-beweisfest.md`](../../tickets/T-16-evidence-store-beweisfest.md). Ziel: S1–S6 auf Soll; jede Lücke mit Wächter und rotem Lauf.
- Im Plan (00 Teil C) als eigenes Paket neben 4–6, spätestens vor Paket 8 (PR): der Prüf-Agent (Paket 9) urteilt auf Grundlage dieses Stores.

**Ehrlich zur Methode:**
- Geprüft am Code und mit einem SQLite-Lauf. Der PostgreSQL-Pfad (Trigger, RLS) ist gelesen, nicht gelaufen.
- `notes` ist absichtlich ungehasht (Docstring in `record_evidence.py`): dort sollte nur Erläuterung stehen. Für die Begründung einer Freigabe trägt diese Absicht nicht.
