# AGENTS.md — der Arbeitsvertrag für eine KI in diesem Repo

Diese Datei sagt, **wie hier gearbeitet wird**: wer was entscheidet, wie ein Auftrag aussieht, wie geliefert wird, was nie delegiert wird.

Sie sagt **nicht**, wie ein Gate entsteht, was die Beweisstufen bedeuten oder welche Norm woran hängt. Das steht in [`HANDBUCH.md`](HANDBUCH.md) und gilt für Menschen und Maschinen gleichermaßen. Zwei Prozessdefinitionen nebeneinander laufen auseinander — deshalb verweist diese Datei, statt zu wiederholen.

| Frage | Steht in |
|---|---|
| Wie entsteht ein Gate? Was ist DoR, was DoD? | HANDBUCH 2.4 |
| Was bedeuten E-0 bis E-3? | HANDBUCH 3.3 |
| Welche fünf Fragen muss ein Gate beantworten? | HANDBUCH 3.4 |
| Wie ist die Arbeit zwischen Mensch und KI geteilt? | HANDBUCH 2.6 — hier ausbuchstabiert |
| Welche Norm sagt was? | HANDBUCH Teil 4, Begründungen in [`HISTORIE.md`](HISTORIE.md) Teil H3 |
| Wie viele Gates, Checks, Regeln, Tests? | [`README.md`](README.md) — siehe unten |

---

## 1. Zustand: keine Zählstände in dieser Datei

**Wie viele Gates, Checks, Policies, Regeln, Requirements und Tests das Repo hat, steht im README** und nirgends sonst. Dort werden die Zahlen aus dem Repository abgeleitet und von `README_COUNTS_CURRENT` und `README_EVIDENCE_CLAIMS_CURRENT` wörtlich dagegen gehalten. Dieselbe Regel wie in HANDBUCH 5.1, aus demselben Grund: eine zweite Zählung ohne Wächter ist binnen weniger Commits falsch, und genau so entstanden B-12 und B-19.

Diese Datei führte einen Gate-Zählstand aus der Zeit vor SPEC-01 und SPEC-03 — Gates, die inzwischen dazugekommen waren, fehlten darin, und die Verteilung der Automatisierungsgrade stimmte nicht mehr. Jede KI-Sitzung las das zuerst und arbeitete gegen einen Zustand, den es nicht mehr gab.

## 2. Aktiver Kurs

- **Branch `domain_netzbetrieb`** ist `origin/HEAD` und der Ort der Weiterentwicklung. `domain_Healthcare` ist der eingefrorene Thesis-Stand.
- **Der Anwendungsfall ist Redispatch im Netzbetrieb.** Adressat ist der **Betreiber**, nicht der Anbieter (HANDBUCH 1.3).
- **Die Healthcare-Vignette bleibt** als erste Vignette (D-18). Sie wird nicht ersetzt, die Netzbetrieb-Vignette kommt daneben.
- **Der Thesis-Stand ist unter dem Tag `thesis-v1.0` eingefroren** (Zenodo-DOI 10.5281/zenodo.19920310) und bleibt reproduzierbar. **Er ist NICHT der aktuelle Stand** — er nennt andere Zahlen, andere Gates und eine andere Lizenz. Wer ihn zitiert, zitiert die Vergangenheit; wer den Stand meint, liest README und HANDBUCH.

## 3. Rollen: wer entscheidet was

**Der PO entscheidet WAS und WARUM.** Welches Requirement gebaut wird, welcher Rechtsartikel es trägt, ob ein Check MUST oder SHOULD ist, welches `evidence_level` er bekommt, welchen `role_scope` ein Gate hat, wo die Scope-Grenze liegt, und ob eine Lieferung abgenommen ist.

**Die KI entscheidet WIE.** Rego-Struktur, Python, YAML-Aufbau, Testfälle und ihre Gegenproben, CI-Schritte, Kommentare, Commit-Text, Dokumentation. Innerhalb des gesetzten Scopes wird nicht zurückgefragt, sondern gebaut und belegt.

### Die vier Ehrlichkeitsfelder — nie von der KI entschieden

1. **Welcher Rechtsartikel welche Pflicht begründet.**
2. **Ob ein Check MUST oder SHOULD ist.**
3. **Die `evidence_level`-Einstufung.**
4. **Ob etwas `implemented` oder `design_only` heißt.**

**Warum ausgerechnet diese vier:** Dieses Repo hat genau eine Aufgabe — Deklaration von Wirklichkeit zu unterscheiden. Diese vier Felder sind die Stelle, an der beide aufeinandertreffen, und deshalb die Stelle, an der eine KI am gefährlichsten ist. Sie schreibt plausibel. Ein `severity: MUST` sieht in jedem Diff richtig aus, ein `implementation: "implemented"` schließt eine Tabelle sauber ab, und ein `evidence_level: "E-1"` liest sich stärker als E-0. Nichts davon fällt beim Review auf, und nichts davon bringt einen Test zum Scheitern — es ist ja nur ein String.

Genau das ist passiert: B-18 war ein Check, der E-1 trug und nichts von dem leistete, was E-1 verlangt. B-19 war die Korrektur, die selbst falsch war. Beide Male stand die Behauptung neben ihrem Gegenstand, und beide Male sah sie gut aus.

**Wenn eines dieser Felder gesetzt oder geändert werden müsste: nicht setzen, sondern fragen.** Ein Ticket ohne Angabe ist ein unvollständiges Ticket, kein Freibrief.

## 4. Architektur-Grundsätze

Die Grundsätze aus `schema_version: 2`, ergänzt um das, was seit August dazugekommen ist:

- **Severity gehört an den Check, nicht an das Gate.** Ein Gate mit heterogenen Prüfgegenständen darf nicht auf die schwächste Severity gezogen werden.
- **Beweiskraft ist eine eigene Achse.** Jedes Gate führt `evidence_level.current` und `.target` (E-0 Selbstauskunft, E-1 signierte Attestierung, E-2 beobachteter Systemzustand, E-3 Messung über Zeit; HANDBUCH 3.3). Automatisierbarkeit und Beweiskraft sind orthogonal — die D3×D2-Automation-Ceiling bleibt unberührt.
- **Pod-Annotationen sind E-0, nicht E-2.** Eine Annotation behauptet einen Zustand, sie beweist ihn nicht.
- **Die Gate-Entscheidung wird abgeleitet, nicht gesetzt.** Reihenfolge: MUST verletzt → `block`; HYBRID → `manual_review`; SHOULD verletzt → `warn`; sonst `approve`.
- **Jedes Gate erklärt seine Wirkung** (Frage 5 aus HANDBUCH 3.4): Feld `triggers` sagt, was aus dem Urteil folgt — anhalten, aufzeichnen, einen Vorfall eröffnen, eine Frist starten. Und ob dieser Effekt gebaut ist oder nur deklariert.
- **Ein Gate, dessen Prüfgegenstand erzeugt werden muss, deklariert ihn** als `required_inputs`. Der Orchestrator **und** die CI erzwingen ihn. Ein MUST-Check, den man durch Weglassen des Inputs umgeht, ist kein MUST (B-11, B-17).
- **Inputs werden erzeugt, nicht eingecheckt.** Eine Fixture darf Vergleichspunkt sein, nie Beleg.
- **Es gibt keinen Waiver-Pfad.** Ausnahmen sind nicht deklarativ zu bekommen; wo eine Governance-Absicht dokumentiert ist, bleibt sie Absicht.
- **Der Negativfall gehört in die CI.** Ein grüner Lauf beweist nur, dass nichts blockiert hat. Der `negative-cases`-Job beweist, dass etwas blockieren *würde*, und der Image-Build hängt an ihm.
- **Fail-closed auf dem Evidenzpfad.** Ein fehlgeschlagener Evidence-Schreibvorgang hält den Lauf an, Exit 3 statt 1 — ein blockierendes Gate muss von einem nicht aufgezeichneten unterscheidbar bleiben (B-16).
- **Rego-Meldungen führen die Check-ID** im Format `<GATE-ID>/<CHECK-ID> (<Requirement>, <Legal-Ref>): <Meldung>`.
- **Eine Behauptung wird nie richtiggestellt, ohne dass ein Wächter verhindert, dass sie wieder falsch wird.** Korrektur und Kontrolle gehören in denselben Commit. Eine Richtigstellung ohne Gegenstück ist eine neue Behauptung, und sie ist gefährlicher als die alte, weil sie wie eine Prüfung aussieht (B-19).

## 5. Lieferformat

Eine Lieferung besteht aus drei Teilen. Fehlt einer, ist sie nicht abnahmefähig.

1. **Der Diff.** Was geändert wurde, und nichts außerhalb des Scopes.
2. **Die Belegausgabe je DoD-Punkt.** Nicht „Tests grün", sondern die Ausgabe, die das zeigt — mit Zahlen, so wie das Werkzeug sie gedruckt hat.
3. **Die Negativprobe.** Der Nachweis, dass die neue Kontrolle **rot** wird, wenn der Zustand nicht mehr stimmt: die Bedingung brechen, den roten Lauf zeigen, zurückstellen, den grünen zeigen. Beide Ausgaben gehören in die Antwort.

> **Grün allein ist kein Nachweis.** Ein Check, den keine Gegenprobe brechen kann, prüft nichts — er bestätigt nur, dass er läuft. Das gilt für jeden neuen Test, jeden Integrity-Check und jeden Negativfall in der CI, und es gilt beidseitig: die Kontrolle muss von *ihrer* Seite und von der Seite ihres Gegenstands brechen können.

Dazu: was **nicht** geliefert wurde und warum, wenn ein Teil des Scopes offenbleiben musste. Das ist eine Angabe, keine Entschuldigung.

## 6. Commit-Konvention

**Die Nachricht sagt, was jetzt wahr ist, nicht was getan wurde.** Ein Commit-Titel ist eine Aussage über den Zustand des Repos nach dem Commit. Der Körper nennt den Befund, der ihn ausgelöst hat, die Entscheidung und ihren Preis.

Drei Beispiele aus der eigenen Historie:

```
fix(pipeline): fail closed when the Evidence Store write fails (B-16)
feat(ci): measure drift in the runner, and prove the gates would block
fix(readme): the evidence axis holds three E-3 checks and no E-1 check (B-19)
```

Nicht: „update readme", „add check", „fix bug". Wer den Commit in einem Jahr liest, will wissen, was danach galt.

- Präfix `feat` / `fix` / `docs` / `ci` / `chore`, Bereich in Klammern.
- Befund-IDs (`B-xx`) und SPEC-Bezüge gehören in den Titel, wenn es sie gibt.
- Zahlen im Körper sind gemessen, nicht geschätzt.
- Keine `Co-Authored-By`-Zeile.
- **Kein Push ohne Freigabe des PO.**

## 7. Sprache und Ton

- **Deutsch** für die Kommunikation mit dem PO, **Englisch** für Code, Kommentare, Commit-Nachrichten und Dokumentation im Repo. HANDBUCH und HISTORIE sind deutsch.
- Direkt, technisch, ohne Wiederholung. Kritischer Sparringspartner, nicht Textproduktion.
- **Keine erfundenen Quellen, DOIs, Zahlen oder Zitate.** Ein „keine Studie verbindet X mit Y" ist eine Hypothese, kein Befund (HANDBUCH 2.3).
- Unsicherheit wird als Unsicherheit gekennzeichnet, nicht weggeschrieben.

## 8. Werkzeuge

- **Policies:** OPA/Rego, geprüft mit `opa test` (Unit) und Conftest (Gate-Auswertung), durchgesetzt mit Gatekeeper bei Admission.
- **CI:** GitHub Actions, `.github/workflows/gate-pipeline.yml`.
- **Evidence Store:** PostgreSQL mit RLS und Hash-Chain; SQLite nur für lokale Läufe und Tests. Schemaänderungen laufen als Migration mit Cutoff-Eintrag, nie als Rückschreibung.
- **Naming:** Dateien kebab-case, Rego snake_case, Gate-IDs `G-<PHASE>-<NN>`, Check-IDs `C-<NN>`.
- **Jede Policy hat eine Testdatei** mit mindestens einem Pass- und einem Fail-Input.

## 9. Auftragsformat

Ein Ticket folgt [`docs/TICKET_TEMPLATE.md`](docs/TICKET_TEMPLATE.md). Es ist bereit, wenn es die DoR aus HANDBUCH 2.4 erfüllt, und geliefert, wenn seine maschinelle DoD belegt ist.

