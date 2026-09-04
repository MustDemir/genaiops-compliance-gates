# T-13 — Deckungsanalyse Sektorstapel (NIS2, EnWG § 11, IT-Sicherheitskatalog, KRITIS)

**Status:** NICHT BEREIT — die Wortlaute liegen nicht im Repo · gestellt 04.09.2026
**Bezug:** [`SPEC-06`](../../specs/SPEC-06-deckungsanalyse-norm-requirement.md) Abschnitt 3
Festlegung 4 · HANDBUCH 4.4, 6.1 · [`T-12`](T-12-cowork-aiact-stufe0.md)

---

## WARUM

HANDBUCH 4.4 nennt vier Regelwerke, die gleichzeitig auf denselben Adressaten wirken:
EnWG § 11 samt IT-Sicherheitskatalog der BNetzA, NIS2UmsuCG, KRITIS-Dachgesetz und den
EU AI Act. Der Pflichtenraum aus SPEC-06 deckt bislang nur den letzten. Solange die
übrigen fehlen, ist die Aussage über die Business Readiness eines Netzbetreibers
unvollständig — und die Überschneidungen bleiben unsichtbar, obwohl genau sie
entscheidungserheblich sind: **Art. 73 Abs. 9 AI Act kann eine Meldepflicht halbieren,
wenn eine parallele Pflicht sie bereits erfüllt.**

Der PO hat den vollen Sektorstapel am 04.09. ausdrücklich in den Scope genommen.

## Warum das Ticket NICHT BEREIT ist

**Keiner dieser Wortlaute liegt im Repo, und HANDBUCH 6.1 führt sie alle als offen und
nicht primärquellengeprüft.** Anders als beim AI Act ist die Beschaffung hier der
eigentliche Aufwand, und sie ist nicht gesichert:

| Norm | Quelle | Erwartete Schwierigkeit |
|---|---|---|
| NIS2 — RL (EU) 2022/2555 | EUR-Lex, deutsche Fassung | EUR-Lex liefert nicht an `curl` aus (AWS-WAF). Nur über einen Browser |
| NIS2UmsuCG | Bundesgesetzblatt / gesetze-im-internet.de | Geltungsstand und Fundstelle zuerst klären |
| EnWG § 11 | gesetze-im-internet.de | Unproblematisch erwartet |
| IT-Sicherheitskatalog Strom/Gas | BNetzA, PDF | Keine strukturierte Quelle; PDF-Textlage unbekannt |
| KRITIS-Dachgesetz | Bundesgesetzblatt | **Geltungsstand ist selbst offen** und vor allem anderen zu klären |

## DEFINITION OF READY

1. **T-12 ist abgenommen.** Erst wenn das Verfahren am AI Act durchgelaufen ist, lohnt
   es sich, es auf vier weitere Normen zu ziehen
2. Je Norm: Wortlaut beschafft, unter `docs/legal/wortlaut/` abgelegt, SHA-256 vermerkt
3. Je Normtyp ein Parser: `extract_norm_units.py` schneidet Artikel/Absatz/Buchstabe.
   Deutsche Gesetze sind Paragraph/Absatz/Nummer, die BNetzA-Kataloge sind wieder anders.
   **Der Verbatim-Check bleibt derselbe** — nur das Schneiden ist normabhängig
4. Der Geltungsstand des KRITIS-Dachgesetzes ist geklärt

## SCOPE OUT

- Rechtliche Bewertung der Konkurrenz zwischen den Regimen (lex specialis EnWG vs.
  NIS2UmsuCG). Das ist eine Rechtsfrage, kein Abgleich, und gehört nicht in diesen Auftrag
- Gates bauen. Dieses Ticket stellt fest

## Die Abbruchregel — der wichtigste Teil dieses Auftrags

> **Ist ein Wortlaut nicht wortgleich beschaffbar, hört die Bearbeitung für diese Norm
> auf.** In den Bericht kommt: welche Quelle, welcher Fehler, welche Wege wurden versucht.
> Es wird **niemals** aus dem Gedächtnis oder aus Sekundärquellen weitergearbeitet.
>
> Mit der nächsten Norm der Liste weiterzumachen ist richtig. Die blockierte zu
> überspringen und als erledigt auszuweisen ist ein Fehlschlag.
>
> Der Grund ist nicht Vorsicht, sondern Statik: Ein Pflichtenraum ohne Primärquelle ist
> nicht weniger wert als einer mit — er ist **gefährlicher als keiner**, weil er wie einer
> aussieht und die Prüfung, die ihn tragen müsste, nie stattgefunden hat.

## DEFINITION OF DONE — maschinell

Je Norm dieselben Punkte wie T-12, plus:

1. `docs/legal/wortlaut/<norm>.txt` existiert, SHA-256 im Kopf des jeweiligen
   Pflichtenraums
2. `verify_norm_quotes.py` meldet BESTANDEN für jede erzeugte Datei
3. Eine Überschneidungstabelle: welche Pflicht tritt in mehr als einem Regime auf.
   Mindestens die Meldepflichten sind daraufhin zu prüfen (Art. 73 Abs. 9)

## COMMIT

Ein Branch und ein PR **je Norm**, nicht einer für alle. Eine blockierte Norm darf die
übrigen nicht aufhalten.
