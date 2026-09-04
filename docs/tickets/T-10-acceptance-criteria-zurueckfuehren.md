# T-10 — Die sechs nicht zurückgeführten `acceptance_criteria` schließen

**Status:** NICHT BEREIT — die PO-Entscheidungen fehlen · gestellt 04.09.2026
**Bezug:** HANDBUCH Teil 7 Punkt 11, 2.4 (DoD 7) · HISTORIE B-15 · `ACCEPTANCE_CRITERIA_TRACED`

---

## WARUM

Alle 14 Requirements tragen seit der Masterarbeit `acceptance_criteria` — 37 Stück.
**Zwei Jahre lang hat sie nichts gelesen** (B-15). Seit `ACCEPTANCE_CRITERIA_TRACED`
werden sie ausgewertet, und der Stand ist:

```
18 of 37 acceptance criteria are evidenced by a named check,
13 are declared gaps, 6 are not traced yet.
```

`unverified` ist ein **legitimer** Zustand: es sagt „das hat noch niemand geprüft",
was etwas anderes ist als eine behauptete Deckung. Der Check bestraft ihn deshalb
nicht. Genau darum bleibt er aber auch liegen — und ein Requirement, dessen eigene
Definition von Fertigkeit ungelesen ist, ist die dritte Ausprägung desselben Musters:
`policy_checks[].evidence_level` stand nach SPEC-01 auf jedem Gate `null`,
`scribe_mock_mode` wurde exportiert und von niemandem gelesen.

Die sechs offenen:

| # | Requirement | Kriterium |
|---|---|---|
| 1 | **R001** [2] | Mindestens ein Mitigationsplan pro identifiziertem High-Risk-Risiko ist dokumentiert |
| 2 | **R002** [1] | Dokumentation verweist eindeutig auf Modellversion und Release |
| 3 | **R004** [2] | Eskalationsprozess ist versioniert und für den Betriebsfall abrufbar |
| 4 | **R007** [3] | KI-generierte Inhalte werden gemäß Art. 50 gekennzeichnet |
| 5 | **R012** [2] | Betroffene Grundrechte sind identifiziert und bewertet |
| 6 | **R012** [3] | Mitigationsmaßnahmen für identifizierte Risiken sind dokumentiert |

## RECHTSBEZUG

**Offen, und je Kriterium einzeln zu füllen.** Ein Feld, das hier geraten wird, ist
eine ungeprüfte Auslegung, die anschließend als Deckungsaussage im Katalog steht
(HANDBUCH 2.4, DoR 1).

Ein Punkt fällt vorab auf und ist **kein** Vorschlag, sondern eine Rückfrage:
**R007 [3] nennt Art. 50.** Art. 50 adressiert Transparenzpflichten, deren Träger
überwiegend der **Anbieter** ist; der Adressat dieses Vorhabens ist der **Betreiber**
(HANDBUCH 1.3, 4.4). Ob das Kriterium in dieser Form überhaupt zum Rollenschnitt
passt, ist eine Entscheidung am Normtext, nicht am Katalog — und Art. 50 ist nicht
EUR-Lex-abgeglichen.

## PO-ENTSCHEIDUNGEN

**Je Kriterium genau eine Festlegung, sechsmal:**

- [ ] `status: met` **plus** `evidence: [G-xxx/C-xx]` — die genannten Checks müssen
      existieren, das prüft der Check maschinell
- [ ] oder `status: gap` **plus** `gap_reason` — was genau fehlt

**Warum das nicht die KI entscheidet:** `met` ist eine Behauptung über Wirklichkeit
und liegt damit in derselben Klasse wie `implementation: implemented` — ein Feld, das
in jedem Diff richtig aussieht, keinen Test brechen lässt und trotzdem falsch sein
kann (AGENTS.md 3). Die KI darf **Kandidaten vorschlagen** und muss belegen, warum
ein Check das Kriterium trägt; die Zuordnung selbst trifft der PO.

Zusätzlich, falls R007 [3] betroffen ist:
- [ ] Bleibt das Kriterium im Requirement, wird es umformuliert, oder entfällt es mit
      Begründung? Ein Kriterium zu streichen ist zulässig — es stillschweigend auf
      `gap` zu setzen, obwohl der Rollenschnitt es gar nicht vorsieht, wäre eine
      Lücke, die keine ist.

## SCOPE IN

- `requirements/R001.yaml`, `R002.yaml`, `R004.yaml`, `R007.yaml`, `R012.yaml`
- ausschließlich die sechs genannten `acceptance_criteria`-Einträge

## SCOPE OUT

- Die 18 `met` und 13 `gap` werden **nicht** angefasst. Wer beim Aufräumen die schon
  zugeordneten mitprüft, liefert einen Diff, den niemand mehr gegen den Auftrag halten kann
- Keine neuen Gates, Checks oder Policies. Wenn ein Kriterium einen Check bräuchte,
  den es nicht gibt, ist es ein `gap` — und der Check ist ein eigenes Ticket
- Kein Rechtsbezug wird neu gesetzt oder geändert

## DEFINITION OF READY

1. Für jedes der sechs Kriterien liegt die PO-Entscheidung vor (`met` + Checks, oder
   `gap` + Grund).
2. Die Frage zu R007 [3] und Art. 50 ist beantwortet.
3. **Nicht** Voraussetzung: EUR-Lex-Abgleich von Art. 50. Ein `gap` mit dem Grund
   „Rechtsbezug ungeprüft" ist eine zulässige und ehrliche Zuordnung.

## DEFINITION OF DONE — maschinell

1. `ACCEPTANCE_CRITERIA_TRACED` meldet **0 unverified**. Beleg: die Summenzeile,
   erwartet `37 = <met> + <gap> + 0`.
2. Jeder unter `evidence` genannte Check existiert im Katalog — das prüft derselbe
   Check gegen `policy_checks[].id`, und er wird rot, wenn ein Name erfunden ist.
3. Integrity-Suite grün: 36 Checks, 0 actionable.
4. `make test` grün: 36/36.

## ABNAHME DURCH DEN PO

- Der **rote Lauf**: ein `evidence`-Eintrag auf einen Check, den es nicht gibt →
  `ACCEPTANCE_CRITERIA_TRACED` rot mit Namen; zurücknehmen → grün. Gegen committeten
  Stand (AGENTS.md 5).
- Je Kriterium ein Satz, der die Zuordnung trägt — die Zuordnung selbst ist die
  Lieferung, nicht das YAML.

## COMMIT

Commit ja, ein Commit je Requirement oder einer für alle sechs — Entscheidung der KI.
Push: nach Abnahme.
