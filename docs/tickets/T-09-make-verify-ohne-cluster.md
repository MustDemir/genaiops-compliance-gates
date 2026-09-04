# T-09 — `make verify` läuft ohne Cluster

**Status:** BEREIT · gestellt 04.09.2026
**Bezug:** HANDBUCH Teil 7 Punkt 10 · AGENTS.md 5

---

## WARUM

`verify: test test-integrity smoke` — `smoke` ruft `infrastructure/scripts/smoke-test.sh`
und setzt ein laufendes Cluster voraus. Auf der Entwicklungsmaschine bricht das Target
deshalb immer ab, und zwar erst **nach** den beiden Suiten, die durchgelaufen wären.

Gleichzeitig fährt `verify` vier Prüfungen **nicht**, die keinerlei Cluster brauchen:

| Prüfung | Kommando | Umfang |
|---|---|---|
| Rego-Unit-Tests | `bash tests/run_all_rego_tests.sh --quiet` | 215 Tests, braucht `opa` auf PATH |
| Hash-Parität | `python3 tests/test_hash_parity.py` | Exit 0 |
| Chain-Migration | `python3 tests/test_hash_chain_migration.py` | Exit 0 |
| Evidenz-Manifest | `python3 tests/test_evidence_manifest.py` | Exit 0 |

Der Befund ist nicht, dass `smoke` falsch wäre. Er ist, dass **der eine Befehl, der
„prüf alles" heißt, weniger prüft als die Summe der Einzelbefehle und trotzdem nicht
durchläuft.** Ein Prüfbefehl, den niemand benutzen kann, ist funktional dasselbe wie
kein Prüfbefehl — dieselbe Struktur wie eine Kontrolle, die deklariert ist und nicht
greift (B-02, B-11, B-13).

Verschärfend: die Integrity-Suite läuft in **keinem** CI-Job. `.github/workflows/gate-pipeline.yml`
ruft weder `tests/test_integrity_regression.py` noch `tests/test_all.py` auf. Damit sind
36 Checks vollständig davon abhängig, dass jemand lokal `make test-integrity` tippt.
**Das ist ein eigener Befund und nicht Teil dieses Tickets** (siehe SCOPE OUT) — es
erhöht aber das Gewicht: der lokale Befehl ist derzeit der einzige Ort, an dem diese
Checks überhaupt wirken.

## RECHTSBEZUG

keiner. Werkzeugfrage.

## PO-ENTSCHEIDUNGEN

Keines der vier Ehrlichkeitsfelder ist betroffen — es wird kein Gate, kein Check und
kein Requirement angefasst. Eine Festlegung braucht das Ticket dennoch:

- [ ] **`--fail-on`-Stufe für die Integrity-Suite in `verify`:** `medium` (Default,
      der neue `HANDBOOK_ROADMAP_CURRENT` meldet sichtbar, blockiert aber nicht) oder
      `low` (jeder Befund blockiert, auch der Roadmap-Drift mitten in der Sitzung).
      **Vorschlag: `medium`** — begründet in derselben Überlegung, aus der der Check
      LOW bekam. `verify` soll am Ende einer Arbeit grün sein können.

## SCOPE IN

- `Makefile` — die Test- und Verify-Targets
- `README.md` — nur, falls dort ein Kommando genannt wird, das sich ändert

## SCOPE OUT

- `infrastructure/scripts/smoke-test.sh` bleibt unverändert
- Die Integrity-Suite in die CI hängen — eigener Auftrag
- Neue Tests schreiben. Dieses Ticket verdrahtet vorhandene, es erzeugt keine

## DEFINITION OF READY

1. Die vier oben genannten Kommandos laufen auf dieser Maschine einzeln durch.
   **Vorbedingung:** `opa` auf PATH; PyYAML über `PYTHONPATH=$HOME/.local/pylibs`
   und `/opt/homebrew/bin/python3.13`, weil pip auf dieser Maschine unbrauchbar ist.
2. Die `--fail-on`-Stufe ist entschieden (siehe PO-ENTSCHEIDUNGEN).

## DEFINITION OF DONE — maschinell

1. `make verify` läuft **ohne Cluster** vollständig durch und endet mit Exit 0.
   Beleg: die vollständige Ausgabe mit den Zahlen jeder Suite.
2. `make verify` fährt alle sechs Prüfungen: `test_all.py` (36), Integrity (36),
   Rego (215), Hash-Parität, Chain-Migration, Evidenz-Manifest.
   Beleg: die Zählstände aus der Ausgabe, nicht die Zusicherung.
3. `make verify-cluster` existiert, hängt an `verify` **und** `smoke`, und bricht auf
   dieser Maschine erwartungsgemäß im `smoke`-Schritt ab — **nachdem** alles andere
   grün gelaufen ist. Beleg: die Ausgabe bis zum Abbruchpunkt.
4. `grep -n "^verify" Makefile` zeigt kein `smoke` mehr in der `verify`-Zeile.
5. Die Integrity-Suite bleibt grün: 36 Checks, 0 actionable auf der entschiedenen Stufe.

## ABNAHME DURCH DEN PO

Der **rote Lauf** ist hier kein gebrochener Check, sondern der Nachweis, dass `verify`
scheitert, wenn eine der neu eingehängten Prüfungen scheitert. Zu zeigen:

- Eine Rego-Regel oder eine Hash-Prüfung **gegen committeten Stand** brechen, `make verify`
  rot mit Exit ≠ 0, zurücknehmen, `make verify` grün.
- Reihenfolge zwingend (AGENTS.md 5): erst committen, dann brechen, dann
  `git restore --source=HEAD --worktree <datei>`.

## COMMIT

Commit ja. Push: nach Abnahme.
