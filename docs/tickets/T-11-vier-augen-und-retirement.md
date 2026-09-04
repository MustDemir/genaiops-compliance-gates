# T-11 — Vier-Augen-Prinzip und Retirement-Pfad

**Status:** NICHT BEREIT — die Grundsatzentscheidung fehlt · gestellt 04.09.2026
**Bezug:** HANDBUCH Teil 7 Punkt 7, 2.4 („Was dem Prozess noch fehlt", Punkte 3 und 4) ·
HISTORIE H4.18 · Limitation L2

---

## WARUM

HANDBUCH 2.4 führt vier Punkte, die „kein Dokument, sondern eine Entscheidung
brauchen". Zwei sind erledigt: Validierung ist als schwerwiegendster offener Punkt
eingeordnet, fail-closed wurde am 27.08. entschieden. Zwei stehen unverändert:

**Punkt 3 — Vier-Augen-Prinzip.** „Ein Autor schreibt Requirement, Gate, Policy, Test
und Prüfung." Das ist heute wörtlich so, und es ist die strukturelle Schwäche unter
allen anderen: jeder Wächter in diesem Repo prüft eine Behauptung, die derselbe
Mensch aufgestellt hat, der den Wächter gebaut hat. Die Integrity-Suite verkleinert
das, sie hebt es nicht auf — B-19 und B-20 sind genau die Fälle, in denen die
Korrektur selbst falsch war und der Wächter den Fehler trug, gegen den er gebaut war.

**Punkt 4 — Retirement-Pfad** für Gates und Systeme. Deckungsgleich mit der eigenen
Limitation L2 und mit dem Forschungsbefund, dass das Lebenszyklus-Ende die anerkannte
Lücke im Feld ist (HISTORIE H7). Es gibt heute keinen Weg, ein Gate oder ein System
geordnet außer Betrieb zu nehmen — kein Zustand, kein Übergang, keine Frage, was mit
den Evidence-Records eines stillgelegten Systems passiert.

## RECHTSBEZUG

**Für das Vier-Augen-Prinzip: keiner.** Es ist ein Engineering-Prozessgrundsatz. Wenn
ein Normbezug bestünde (etwa Art. 17 Qualitätsmanagement für Anbieter), wäre er
anbieterseitig und damit außerhalb des Rollenschnitts — zu prüfen, nicht zu vermuten.

**Für den Retirement-Pfad: offen und zu prüfen.** Art. 26 kennt Betreiberpflichten
über den Betriebszeitraum; ob daraus eine Pflicht bei Außerbetriebnahme folgt, und
was mit Aufbewahrungsfristen für Logs geschieht, ist eine Frage an den Wortlaut.
Nicht EUR-Lex-abgeglichen.

## PO-ENTSCHEIDUNGEN

**Die Grundsatzentscheidung, ohne die das Ticket nicht bereit ist:**

- [ ] **Vier-Augen-Prinzip — bauen oder als Limitation benennen?**

  Vorschlag der KI: **benennen, nicht bauen.** Ein Vier-Augen-Prinzip in einem
  Ein-Personen-Vorhaben ist eine Deklaration ohne Mechanismus. Ein
  `CODEOWNERS`-Eintrag oder eine Branch-Protection-Regel, die derselbe Mensch setzt,
  erfüllt und aufheben kann, sieht nach Kontrolle aus und ist keine — und damit
  exakt der Fehlertyp, den dieses Repo an anderen prüft (B-02, B-11, B-13).
  Ehrlicher: ein Limitations-Eintrag plus die Angabe, **was ein Zweiter prüfen müsste**,
  damit die Lücke benutzbar statt nur eingestanden ist.

  **Diese Entscheidung gehört dem PO, weil sie den Umfang des Vorhabens kürzt.** Die
  KI darf einen Punkt nicht selbst zur Limitation erklären — das wäre eine
  Scope-Kürzung als Sachaussage getarnt.

- [ ] **Retirement-Pfad — Zustandsmodell bauen oder Limitation vertiefen?**
      Falls bauen: welche Zustände hat ein Gate (`active` / `deprecated` / `retired`),
      wer setzt sie, und was geschieht mit Evidence-Records eines stillgelegten
      Systems? Der letzte Teil ist keine Feldfrage: eine Kette, aus der Records
      verschwinden, ist gebrochen — Retirement darf also nicht löschen.

- [ ] Falls Zustandsmodell: `severity` und `evidence_level` eines etwaigen neuen
      Checks — nie von der KI gesetzt (AGENTS.md 3).

## SCOPE IN

Abhängig von der Grundsatzentscheidung. Bei **benennen**:

- `HANDBUCH.md` 2.4 (die beiden Punkte auflösen) und der Limitations-Abschnitt
- `HISTORIE.md` — H4.18 nachziehen, mit der getroffenen Entscheidung und ihrem Preis

Bei **bauen** kommt hinzu: `gate-definitions/`, das Gate-Template, die Integrity-Suite.

## SCOPE OUT

- Aufbewahrungsfristen für Evidence-Records aus dem Normtext ableiten — Rechtsarbeit,
  eigener Auftrag, und ohne EUR-Lex-Abgleich unzulässig
- Das Löschen von Records. Bei jedem Ausgang: die Kette bleibt vollständig
- Zugriffsrechte, Rollen, Freigabe-Workflows auf GitHub-Ebene

## DEFINITION OF READY

1. Die Grundsatzentscheidung liegt für beide Punkte vor.
2. Bei „bauen": das Zustandsmodell ist festgelegt, inklusive der Frage nach den
   Records. Bei „benennen": entfällt.

## DEFINITION OF DONE — maschinell

Abhängig vom Ausgang. **Bei „benennen":**

1. HANDBUCH 2.4 führt die Punkte 3 und 4 nicht mehr als offen, sondern als
   entschieden — mit Datum und Verweis auf die Historie.
   Beleg: `grep -n "Vier-Augen\|Retirement" HANDBUCH.md`.
2. Die Limitation nennt, **was ein Zweiter prüfen müsste** — eine Limitation ohne
   diese Angabe ist ein Eingeständnis ohne Nutzen.
3. Jede in HANDBUCH 2.4 genannte ID existiert auch in `HISTORIE.md`.
   **Achtung:** HANDBUCH 0.2 und HISTORIE nennen dafür `check_handbuch_konsistenz.py` —
   **dieses Skript existiert im Repo nicht** (Befundvorschlag B-22). Bis es existiert,
   ist dieser DoD-Punkt manuell und damit kein maschineller Beleg.
4. `DOC_REFERENCES_ARE_TRACKED` grün — jeder neue Abschnittsverweis muss auflösbar sein.
5. Integrity-Suite grün: 36 Checks, 0 actionable.

**Bei „bauen"** zusätzlich: ein Check, der einen Zustandsübergang ohne Begründung rot
meldet, plus dessen Gegenprobe.

## ABNAHME DURCH DEN PO

Bei „benennen" gibt es keinen roten Lauf im üblichen Sinn — es entsteht kein
Mechanismus. **Das ist der Grund, warum diese Variante überhaupt zur Debatte steht,
und es ist zugleich ihre Schwäche.** Der PO nimmt hier einen Text ab, keine Kontrolle.
Zu zeigen ist deshalb die Konsistenzprüfung und der Nachweis, dass kein Verweis ins
Leere zeigt.

Bei „bauen": der rote Lauf wie üblich, gegen committeten Stand.

## COMMIT

Commit ja. Push: nach Abnahme.
