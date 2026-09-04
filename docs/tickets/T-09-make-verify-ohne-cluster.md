# T-09 — `make verify` läuft ohne Cluster, und der Push prüft es

**Status:** ERLEDIGT · gestellt und geliefert 04.09.2026 · abgenommen vom PO
**Beleg:** `make verify` Exit 0 in 6,46 s — 36 Integration · 36 Integrity (`--fail-on low`) ·
215 Rego · Parität · Chain-Migration · Manifest. Zwei Gegenproben gegen committeten Stand:
eine gebrochene Rego-Assertion macht `verify` rot (Exit 2, `FAIL: 1/215`), und ein
Substanz-Commit ohne Handbuch-Nachzug lässt den `pre-push`-Hook den Push abbrechen.
**Bezug:** HANDBUCH Teil 7 Punkt 10 · AGENTS.md 5

---

## WARUM

**Erster Befund — `verify` prüft weniger und läuft trotzdem nicht.**
`verify: test test-integrity smoke`. `smoke` ruft `infrastructure/scripts/smoke-test.sh`
und setzt ein Cluster voraus; auf der Entwicklungsmaschine bricht das Target immer ab,
und zwar erst *nach* den beiden Suiten. Gleichzeitig fährt es vier Prüfungen **nicht**,
die kein Cluster brauchen: Rego (215 Tests), Hash-Parität, Chain-Migration,
Evidenz-Manifest.

Der eine Befehl, der „prüf alles" heißt, prüft also weniger als die Summe der
Einzelbefehle **und** ist unbenutzbar. Ein Prüfbefehl, den niemand ausführen kann,
ist funktional dasselbe wie kein Prüfbefehl.

**Zweiter Befund — das Cluster war nicht der einzige Grund.**
Die Targets rufen `python3`. Das ist hier `/opt/homebrew/bin/python3` **ohne PyYAML**:

```
make test-integrity
  Actionable failures (>= MEDIUM): 13     ← alle 13: ModuleNotFoundError: No module named 'yaml'
  make: *** [test-integrity] Error 1
```

`make verify` liefe also **auch nach dem Entkoppeln von `smoke` nicht durch**. Wer nur
Befund 1 behebt, liefert ein Target, das weiterhin niemand benutzen kann — und das
Ticket wäre umsonst gewesen. Der Grund ist bekannt und nicht behebbar: pip ist auf
dieser Maschine unbrauchbar (leeres `platform.mac_ver()` unter macOS 26.2), PyYAML
liegt manuell entpackt unter `~/.local/pylibs`. Das ist eine **Maschineneigenschaft**
und gehört nicht in ein getracktes Makefile.

**Dritter Befund — die Kontrolle erinnert an nichts.**
`HANDBOOK_ROADMAP_CURRENT` meldet, wenn HANDBUCH Teil 7 hinter Gates, Pipeline und
Specs zurückfällt. Gemeldet wird es nur, wenn jemand die Suite fährt. Es gibt keinen
Moment im Arbeitsablauf, an dem das zwingend geschieht — dieselbe Abhängigkeit von
Disziplin, gegen die der Check gebaut ist, eine Ebene tiefer.

Es gibt aber einen Moment, der **verlässlich** eintritt: der Push. Der PO pusht einmal
pro Sitzung; der Push *ist* das Sitzungsende. Ein `pre-push`-Hook hängt sich an eine
vorhandene Gewohnheit und verlangt keine neue.

## RECHTSBEZUG

keiner. Werkzeugfrage.

## PO-ENTSCHEIDUNGEN

Keines der vier Ehrlichkeitsfelder ist betroffen — kein Gate, kein Check, kein
Requirement wird angefasst. Zwei Festlegungen sind getroffen:

- [x] **`--fail-on low` in `verify`.** Begründung: `verify` ist kein Alltagsbefehl,
      sondern der Push-Torwächter — es fährt genau einmal pro Sitzung, im Hook. In
      dieser Rolle ist `medium` wirkungslos: der Roadmap-Befund würde gedruckt und der
      Push ginge durch, also Rauschen statt Erinnerung. Für Läufe zwischendurch bleibt
      der Suite-Default `medium` unverändert; wer `tests/test_integrity_regression.py`
      einzeln fährt, merkt nichts von dieser Entscheidung.
- [x] **Ein Target, kein zweites Vokabular.** Kein `make session-close` neben `verify`.
      Ein zweiter Befehl für denselben Moment ist eine zweite Definition desselben
      Vorgangs — derselbe Grund, aus dem AGENTS.md das Handbuch nicht wiederholt.

## SCOPE IN

- `Makefile` — Test- und Verify-Targets, Interpreter-Auflösung, Hilfetext
- `.githooks/pre-push` (neu)
- `README.md` — die Aktivierungszeile für `core.hooksPath`
- `Makefile.local` — **nicht getrackt** (`.gitignore` deckt `*.local`), hält die
  maschinenspezifische Interpreter-Angabe

## SCOPE OUT

- `infrastructure/scripts/smoke-test.sh` bleibt unverändert
- Die Integrity-Suite in die CI hängen — eigener Auftrag, eigener Befund
- Neue Tests schreiben. Dieses Ticket verdrahtet vorhandene, es erzeugt keine
- Die `severity` eines bestehenden Checks ändern
- Die Schlusszeile der Suite reparieren, die bei `--fail-on high` „PASSED" druckt,
  während ein FAIL darübersteht — eigener Befund, eigener Auftrag

## DEFINITION OF READY

1. Die vier einzuhängenden Kommandos laufen einzeln durch. **Belegt:**
   Rego 215/215 · Parität OK · Chain-Migration Exit 0 · Manifest Exit 0 · Gesamt ≈ 6,5 s.
2. `opa` ist auf PATH (1.14.1).
3. Die beiden PO-Festlegungen liegen vor (siehe oben).

## DEFINITION OF DONE — maschinell

1. `make verify` läuft **ohne Cluster** durch, Exit 0. Beleg: vollständige Ausgabe.
2. `make verify` fährt sechs Prüfungen mit ihren Zählständen: `test_all.py` (36),
   Integrity (36, `--fail-on low`), Rego (215), Parität, Chain-Migration, Manifest.
3. `grep -n "^verify:" Makefile` zeigt kein `smoke`.
4. `make verify-cluster` existiert und hängt an `verify` **und** `smoke`.
5. **Der Interpreter ist gelöst:** `make verify` läuft auf dieser Maschine, ohne dass
   der Aufrufer `PYTHONPATH` von Hand setzt. Fehlt ein tauglicher Interpreter, bricht
   `make` mit einer Meldung ab, die sagt was zu tun ist — nicht mit 13 Stacktraces.
6. `.githooks/pre-push` ruft `make verify` und bricht den Push bei Exit ≠ 0 ab.
7. Der Hook ist aktiviert (`git config core.hooksPath .githooks`), und das README
   nennt diesen Befehl — ein Hook, dessen Aktivierung nirgends steht, ist in einem
   frischen Klon nicht vorhanden und behauptet trotzdem, zu schützen.

## ABNAHME DURCH DEN PO

Zwei rote Läufe, beide **gegen committeten Stand** (AGENTS.md 5 — erst committen,
dann brechen, dann `git restore --source=HEAD --worktree`):

1. **`verify` bricht, wenn eine eingehängte Prüfung bricht.** Eine Rego-Regel brechen →
   `make verify` Exit ≠ 0 → zurücknehmen → Exit 0.
2. **Der Hook hält den Push an.** Einen Commit an `pipeline/` ohne Handbuch-Nachzug →
   `git push` wird vom Hook abgebrochen, mit der Zeile aus `HANDBOOK_ROADMAP_CURRENT` →
   zurücknehmen → Push läuft.

Der zweite ist der eigentliche Nachweis: er zeigt, dass die Erinnerung an dem Moment
ankommt, an dem sie ankommen soll.

## COMMIT

Commit ja. Push: nach Abnahme — und der Push ist ab dann selbst Teil der Prüfung.
