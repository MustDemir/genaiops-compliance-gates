# T-13 — Deckungsanalyse Sektorstapel (NIS2, BSIG, EnWG, KRITIS, DSGVO)

**Status:** BEREIT · gestellt 04.09.2026 · Quellen beschafft 07.09.2026
**Bezug:** [`SPEC-06`](../../specs/SPEC-06-deckungsanalyse-norm-requirement.md) Abschnitt 3
Festlegung 4 · HANDBUCH 4.4, 6.1 · [`T-12`](T-12-cowork-aiact-stufe0.md)

---

## WARUM

HANDBUCH 4.4 nennt vier Regelwerke, die **gleichzeitig auf denselben Adressaten** wirken:
EnWG § 11 samt IT-Sicherheitskatalog, NIS2UmsuCG, KRITIS-Dachgesetz und den AI Act. Der
Pflichtenraum deckte bislang nur den letzten.

Solange die übrigen fehlen, bleibt zweierlei unsichtbar. Erstens die **Pflichtenlast**:
Der Adressat hat bereits ein zertifiziertes ISMS — die Frage ist nicht „wie fange ich an",
sondern wie die KI-Pflichten daran hängen. Zweitens die **Überschneidungen**, und die sind
entscheidungserheblich: **Art. 73 Abs. 9 AI Act kann eine Meldepflicht halbieren**, wenn
eine parallele Pflicht sie bereits erfüllt.

Dazu kommt ein Befund aus dem AI-Act-Lauf: Unter den 23 Lücken steht **Art. 26 Abs. 9** —
der Betreiber nutzt die Informationen nach Art. 13 für seine **DSFA nach Art. 35 DSGVO**.
Der AI Act reicht dort ausdrücklich an die DSGVO weiter. Sie ist deshalb keine Kür.

## Was seit dem 07.09. vorliegt

**Alle fünf Wortlaute sind beschafft, gehasht und im Repo.** Die Beschaffung war der
eigentliche Aufwand dieses Tickets — sie ist erledigt, heute Nacht läuft reine Analyse.

| Quelle | SHA-256 (gekürzt) | Einheiten |
|---|---|---|
| `nis2_2022-2555_DE.txt` | `5c81ec4b88531363…` | 418 |
| `dsgvo_2016-679_DE.txt` | `2d3a4bb6f8a5391d…` | 748 |
| `bsig_2025_DE.txt` | `6bc0f2230431ac5a…` | 245 |
| `kritisdachg_DE.txt` | `95ce2497799423ba…` | 110 |
| `enwg_p11_DE.txt` | `d72f7fbfda1402cc…` | 4 |

**Zum Geltungsstand, der in der ersten Fassung dieses Tickets offen war:** Das
KRITIS-Dachgesetz wurde am 16.03.2026 verkündet und ist seit dem **17.03.2026 in Kraft**.
Geprüft am Gesetz, nicht an einer Einschätzung.

**Ehrlichkeitsvermerk:** `bsig` und `kritisdachg` sind **abgeleitete Zusammenstellungen**
aus 66 bzw. 26 Einzelparagraphen-Seiten von gesetze-im-internet.de, kein amtliches
Einzeldokument. Das steht in `quelle.fassung` jedes betroffenen Pflichtenraums. Für eine
Veröffentlichung sind Rechtsaussagen daraus gegen das Bundesgesetzblatt zu prüfen.

## Was noch fehlt

**Der IT-Sicherheitskatalog der BNetzA hat noch keinen Pflichtenraum.** Beide Kataloge
liegen als PDF im Repo — `docs/legal/itsikat_1a_2015.pdf` (Netzbetreiber, 16 Seiten) und
`itsikat_1b_2018.pdf` (Anlagenbetreiber, 23 Seiten) —, aber der Extraktor arbeitet auf
Text. Es fehlt ein PDF-Textauszug und ein Parser für die Katalogstruktur, die weder
Artikel noch Paragraphen kennt.

**Und ein Hinweis zur Geltung:** Nach dem Inkrafttreten des NIS2UmsuCG am 06.12.2025 gelten
die bestehenden Kataloge nach § 11 Abs. 1a/1b EnWG **fort**, bis ein neuer veröffentlicht
wird. Ob inzwischen einer erschienen ist, gehört vor der Analyse geprüft — Sekundärquelle,
nicht verifiziert.

## RECHTSBEZUG

Je Norm der eigene Wortlaut. **Keine Aussage ohne Beleg aus der archivierten Quelle**;
Auslegung ist HYPOTHESE mit Begründung (HANDBUCH 2.3).

## PO-ENTSCHEIDUNGEN

Wie T-12: `scope`, `befund` und jede HYPOTHESE liegen beim PO. Der Lauf **legt vor** und
setzt auf jeder angefassten Zeile `po_bestaetigt: false`.

Eine zusätzliche Festlegung, die dieses Ticket braucht und die noch aussteht:

- [ ] **Adressatenzuschnitt je Norm.** Der AI Act kannte „Betreiber". NIS2 und BSIG
      unterscheiden *besonders wichtige* und *wichtige Einrichtungen* sowie *Betreiber
      kritischer Anlagen*; das KRITIS-Dachgesetz kennt *kritische Einrichtungen*. Welcher
      Status trifft auf einen Verteilnetzbetreiber mittlerer bis großer Größe zu?
      **Ohne diese Festlegung ist `scope: in` nicht entscheidbar** — und geraten wäre sie
      eine Rechtsauslegung, die anschließend als Deckungsaussage im Katalog steht.

## SCOPE OUT

- Rechtliche Bewertung der Konkurrenz zwischen den Regimen (lex specialis EnWG vs.
  NIS2UmsuCG). Rechtsfrage, kein Abgleich
- Gates oder Requirements bauen. Dieses Ticket stellt fest
- Der IT-Sicherheitskatalog, bis sein Text vorliegt

## Die Abbruchregel

> Ist ein Wortlaut nicht wortgleich beschaffbar, **hört die Bearbeitung für diese Norm
> auf**. In den Bericht: welche Quelle, welcher Fehler, welche Wege versucht. Es wird
> **niemals** aus dem Gedächtnis oder aus Sekundärquellen weitergearbeitet.
>
> Ein Pflichtenraum ohne Primärquelle ist **gefährlicher als keiner** — er sieht wie einer
> aus, und die Prüfung, die ihn tragen müsste, hat nie stattgefunden.

Für die fünf beschafften Normen greift sie nicht mehr. Sie gilt weiter für den
IT-Sicherheitskatalog und für jede Norm, die später dazukommt.

## DEFINITION OF DONE — maschinell

1. `verify_norm_quotes.py <datei>` meldet **BESTANDEN** für jeden bearbeiteten Raum
2. `make verify` grün — enthält `LEGAL_QUOTES_VERBATIM` (HIGH) über alle Räume
3. `fortschritt.py <datei>` meldet **0 offen** für jeden bearbeiteten Raum
4. Eine **Überschneidungstabelle**: welche Pflicht tritt in mehr als einem Regime auf.
   Mindestens die Meldepflichten sind daraufhin zu prüfen (Art. 73 Abs. 9 AI Act,
   Art. 23 NIS2, § 32 BSIG, § 13 KRITISDachG, Art. 33 DSGVO)

## COMMIT

Ein Branch und ein PR **je Norm**. Eine blockierte Norm darf die übrigen nicht aufhalten.

---

# Die Auftragstexte — zum Kopieren

**Block A aus [`T-12`](T-12-cowork-aiact-stufe0.md) gilt unverändert** — Regeln,
Feldbeschreibung, Prüfbefehle, Berichtsform. Nur diese vier Zeilen ersetzen:

```
Arbeite auf Branch spec06-<norm> (nis2 | bsig | kritis | dsgvo | enwg).
Die Zieldatei ist docs/coverage/<norm>_pflichtenraum.yaml.
Der Wortlaut liegt in docs/legal/wortlaut/ — welche Datei, sagt quelle.datei
im Kopf des jeweiligen Pflichtenraums.
```

## Lauf 1 — NIS2 und BSIG, die tragende Achse

```
LAUF 1 — NIS2 (RL 2022/2555) und BSIG (i.d.F. NIS2UmsuCG)

  docs/coverage/nis2_pflichtenraum.yaml   418 Einheiten
  docs/coverage/bsig_pflichtenraum.yaml   245 Einheiten

Reihenfolge: erst BSIG, dann NIS2. Das BSIG ist das unmittelbar anwendbare
Recht für den Adressaten; die Richtlinie erklärt, warum es so aussieht.

Im BSIG zuerst:
  § 2   Begriffsbestimmungen — entscheidet, welcher Einrichtungsstatus greift
  § 28  Einrichtungsarten und Betreiber kritischer Anlagen
  § 30  Risikomanagementmaßnahmen
  § 31  Besondere Anforderungen an Betreiber kritischer Anlagen
  § 32  Meldepflichten
  § 38  Pflichten der Geschäftsleitung

In NIS2 dann Art. 20-23 und Anhang I (Sektor Energie).

ACHTUNG ADRESSATENSTATUS: Ob der Adressat "besonders wichtige Einrichtung",
"wichtige Einrichtung" oder "Betreiber kritischer Anlagen" ist, entscheidet
über fast jede scope-Zuordnung. Diese Festlegung liegt beim PO und steht in
T-13 als offen. Solange sie fehlt: erfasse die Pflicht, setze scope nach der
WEITESTEN plausiblen Lesart auf 'in', und schreibe in befund_grund, von
welchem Status du ausgegangen bist. Nicht raten und stillschweigend
einschränken — die weitere Lesart ist korrigierbar, die engere verdeckt.

Die Einheit '§ 2 lit. e' des BSIG trägt mehrere Begriffsbestimmungen in einem
Ausschnitt (die Nummerierung '1. 2. 3.' deutscher Definitionslisten wird vom
Extraktor nicht getrennt). Das ist bekannt und kein Beleg-Fehler: der Beleg
ist wortgleich, nur grob geschnitten. Behandle die enthaltenen Definitionen
im Feld pflicht einzeln und vermerke es.
```

## Lauf 2 — KRITIS-Dachgesetz und EnWG § 11

```
LAUF 2 — KRITIS-Dachgesetz und EnWG § 11

  docs/coverage/kritisdachg_pflichtenraum.yaml   110 Einheiten
  docs/coverage/enwg_pflichtenraum.yaml            4 Einheiten

Das KRITIS-Dachgesetz setzt die CER-Richtlinie (EU) 2022/2557 um und regelt
die PHYSISCHE Resilienz — NIS2 und BSIG regeln die informationstechnische.
Diese Trennung ist bei jeder Einheit mitzudenken: eine Pflicht zur physischen
Sicherung einer Anlage ist für ein KI-Kontrollsystem in aller Regel
scope: out — aber MIT dieser Begründung, nicht stillschweigend.

Im KRITISDachG besonders:
  § 2   Begriffsbestimmungen (kritische Einrichtung, kritische Anlage)
  § 12  Resilienzmaßnahmen
  § 13  Meldepflichten — für die Überschneidungstabelle
  § 18  Registrierung

EnWG § 11 hat nur 4 Einheiten, ist aber der Anker: Abs. 1a und 1b sind die
Rechtsgrundlage des IT-Sicherheitskatalogs und damit des zertifizierten ISMS,
an dem laut HANDBUCH 4.4 die ganze KI-Pflichtenlage hängt. Erfasse besonders
genau, WORAUF Abs. 1a/1b verweisen und was sie dem Netzbetreiber auferlegen.
```

## Lauf 3 — DSGVO und die Überschneidungstabelle

```
LAUF 3 — DSGVO und die Überschneidungen

  docs/coverage/dsgvo_pflichtenraum.yaml   748 Einheiten

Die DSGVO ist der größte Raum und der mit dem geringsten Anteil einschlägiger
Pflichten. Arbeite gezielt:

  Art. 35   Datenschutz-Folgenabschätzung — der AI Act verweist in Art. 26
            Abs. 9 ausdrücklich darauf, und diese Einheit steht im AI-Act-Raum
            als LÜCKE. Hier liegt die Gegenseite.
  Art. 36   Vorherige Konsultation
  Art. 22   Automatisierte Entscheidungen im Einzelfall
  Art. 5    Grundsätze — Richtigkeit und Speicherbegrenzung treffen jedes
            Modell, das personenbezogene Daten verarbeitet
  Art. 32   Sicherheit der Verarbeitung
  Art. 33   Meldung von Verletzungen — für die Überschneidungstabelle
  Art. 30   Verzeichnis von Verarbeitungstätigkeiten

Alle übrigen Artikel: scope out MIT GRUND. Bei 748 Einheiten ist ein knapper,
wiederverwendbarer Grund je Artikelgruppe zulässig — aber er muss dastehen.

DANACH DIE ÜBERSCHNEIDUNGSTABELLE, das eigentliche Ergebnis dieses Laufs:
Lege im Verzeichnis docs/coverage/ eine neue Datei ueberschneidungen.md an. Je Zeile eine Pflicht, die in mehr
als einem Regime auftritt, mit den Fundstellen nebeneinander. Mindestens zu
prüfen:

  Meldepflichten:  AI Act Art. 73 · NIS2 Art. 23 · BSIG § 32 ·
                   KRITISDachG § 13 · DSGVO Art. 33
  Risikomanagement: AI Act Art. 9 · BSIG § 30 · EnWG § 11 Abs. 1a
  Folgenabschätzung: AI Act Art. 27 · DSGVO Art. 35
  Geschäftsleitung: BSIG § 38 · AI Act Art. 26 Abs. 2

Zu jeder Zeile die Frage beantworten, auf die es ankommt: ERFÜLLT die eine
Pflicht die andere mit, oder stehen sie nebeneinander? Art. 73 Abs. 9 AI Act
ist der ausdrückliche Fall, in dem eine Meldepflicht sich reduziert. Wo du es
nicht aus dem Wortlaut entscheiden kannst, ist es HYPOTHESE mit Begründung —
und genau diese Zeilen sind die wertvollsten des ganzen Laufs.
```
