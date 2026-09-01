# Ticket-Vorlage

Das Format, in dem der PO Aufträge stellt und die KI liefert. Es ist die Anwendung von HANDBUCH 2.4 (Definition of Ready und Definition of Done) und HANDBUCH 2.6 (Arbeitsteilung) auf einen einzelnen Auftrag — **es definiert nichts davon neu.** Wer wissen will, wann ein Gate bereit und wann es fertig ist, liest HANDBUCH 2.4; hier steht nur, wo diese Angaben im Ticket stehen.

Die Rollenteilung, auf der das Format aufsitzt, steht in [`../AGENTS.md`](../AGENTS.md) Abschnitt 3: der PO entscheidet WAS und WARUM, die KI entscheidet WIE, und vier Felder werden nie von der KI entschieden.

---

## Vorlage

```markdown
Ticket T-NN.

WARUM
Der Befund, nicht der Wunsch. Was ist heute falsch oder fehlt, und
woran ist das gemessen? Wenn es eine Befund-ID gibt (B-xx), hier.

RECHTSBEZUG
Welcher Artikel, welche Fassung, welche Verifikationsstufe
(VERIFIZIERT / SEKUNDÄRQUELLE / HYPOTHESE, HANDBUCH 2.3).
"keiner" ist eine zulässige Angabe — sie zu erraten ist nicht.

PO-ENTSCHEIDUNGEN
Die vier Ehrlichkeitsfelder, soweit betroffen, und sonstige
Festlegungen, die nicht zur Disposition stehen:
  - Severity MUST / SHOULD
  - evidence_level
  - implementation: implemented / design_only
  - role_scope
Ohne diese Angaben ist das Ticket nicht bereit.

SCOPE IN
Welche Dateien und Bereiche angefasst werden dürfen.

SCOPE OUT
Was ausdrücklich nicht angefasst wird. Nennt der Auftrag nichts,
gilt: alles, was nicht unter SCOPE IN steht.

DEFINITION OF READY
Die Kriterien aus HANDBUCH 2.4 gelten unverändert. Hier nur, was
speziell für dieses Ticket vorliegen muss — ein erzeugtes Dokument,
eine Entscheidung, ein abgeschlossenes Vorgänger-Ticket.

DEFINITION OF DONE — maschinell
Jeder Punkt muss von einem Kommando belegbar sein, dessen Ausgabe
in der Antwort steht. Gate-DoD nach HANDBUCH 2.4; hier die
Ticket-spezifischen Punkte, zum Beispiel:
  - <Suite> grün, Anzahl nennen
  - neuer Check X ist rot, wenn <Bedingung> verletzt ist
  - grep über <Datei> findet <Passage> nicht mehr

ABNAHME DURCH DEN PO
Was der PO sehen will, um abzunehmen. Regelmäßig: der rote Lauf.
Grün allein ist kein Nachweis (AGENTS.md 5).

COMMIT
Commit ja/nein, Push ja/nein. Die Nachricht sagt, was jetzt wahr
ist (AGENTS.md 6).
```

---

## Warum die Felder so heißen

**WARUM vor WAS.** Ein Auftrag, der mit der Lösung beginnt, macht die Lösung unprüfbar — es fehlt der Zustand, gegen den sie zu halten wäre. Derselbe Grund, aus dem jedes Gate seinen Prüfgegenstand nennt.

**RECHTSBEZUG als eigenes Feld.** Die Zuordnung Norm → Pflicht ist die erste der vier Entscheidungen, die nie von der KI getroffen werden. Ein leeres Feld ist eine Angabe; ein geratenes Feld ist eine ungeprüfte Auslegung, die anschließend automatisiert wird (HANDBUCH 2.4, DoR 1).

**SCOPE OUT ausdrücklich.** Nicht als Misstrauen, sondern weil ein Auftrag ohne Grenze zum Nebenbei-Aufräumen einlädt und der Diff dann nicht mehr prüfbar ist.

**DEFINITION OF DONE maschinell.** „Fertig" ist eine Behauptung wie jede andere. Was sie stützt, ist die Ausgabe eines Kommandos — nicht die Zusicherung dessen, der geliefert hat.

**ABNAHME getrennt von DoD.** Die DoD ist, was die Maschine zeigt. Die Abnahme ist, was der Mensch sehen will, um es zu glauben. Meistens ist das der rote Lauf: der Nachweis, dass die neue Kontrolle den Fehler gefunden hätte.
