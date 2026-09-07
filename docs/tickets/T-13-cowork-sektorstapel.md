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
| `nis2_2022-2555_DE.txt` | siehe `quelle.sha256` | 418 |
| `dsgvo_2016-679_DE.txt` | siehe `quelle.sha256` | 748 |
| `bsig_2025_DE.txt` | siehe `quelle.sha256` | 295 |
| `kritisdachg_DE.txt` | siehe `quelle.sha256` | 135 |
| `enwg_DE.txt` (§§ 5c, 5d, 5e, 11) | siehe `quelle.sha256` | 15 |

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

### Adressatenstatus — entschieden am 07.09.2026

- [x] **Arbeitsannahme: besonders wichtige Einrichtung nach § 28 Abs. 1 Nr. 1 BSIG**,
      mit der Bereichsausnahme des § 28 Abs. 5 Nr. 2 ausdrücklich mitgeführt.

**Was der Wortlaut sagt.** § 28 Abs. 1: *„Als besonders wichtige Einrichtung gelten
1. Betreiber kritischer Anlagen, …"*. Die Definitionskette läuft über § 2 Nr. 22 BSIG
(*„‚kritische Anlage' eine Anlage im Sinne des § 2 Nummer 3 des KRITIS-Dachgesetzes"*)
weiter zu einer Rechtsverordnung mit Schwellenwerten. Der zweite Weg führt über § 28
Abs. 1 Nr. 4: Einrichtungsart nach Anlage 1 **plus** ≥ 250 Mitarbeiter **oder** über
50 Mio. € Umsatz **und** über 43 Mio. € Bilanzsumme.

**Die Bereichsausnahme ist der eigentliche Befund.** § 28 Abs. 5 Nr. 2 nimmt die
§§ 30, 31, 32, 35, 36, 38, 39, 61 und 62 heraus für Einrichtungen, die Energie­
versorgungsnetze betreiben und den §§ 5c bis 5e EnWG unterliegen. Der Status greift
also, die **Kernpflichten sind verdrängt** — sie stehen im EnWG, nicht im BSIG.

**Warum die weiteste Lesart.** Eine zu weit gefasste Pflicht fällt bei der Durchsicht
auf und wird gestrichen. Eine zu eng gefasste fällt nie auf, weil die Zeile gar nicht
erst entsteht. Dieselbe Logik wie bei `scope: out` mit Begründungspflicht.

**Der Status bleibt vorläufig.** Ob der Adressat tatsächlich eine kritische Anlage
oberhalb des Schwellenwerts betreibt und wo er bei Mitarbeitern, Umsatz und
Bilanzsumme liegt, ist eine Tatsachenfrage über den Zieladressaten, keine
Normfrage. Solange sie offen ist, trägt jede darauf gestützte Zuordnung
`verifikation: HYPOTHESE` mit Begründung.

---

## Wie `scope` und `befund` entschieden werden

Zwei verschiedene Achsen, die nicht vermischt werden dürfen. `scope` fragt: **gehört
diese Einheit in den Prüfraum?** `befund` fragt: **trifft der Katalog sie?** Die zweite
Frage stellt sich nur, wenn die erste mit `in` beantwortet ist.

### `scope` — die Aufnahmeregel, in vier Schritten

Grundlage ist **HANDBUCH 4.1**: *„Eine Anforderung gehört in den Normenraum, wenn sie am
Lebenszyklus eines KI-Systems prüfbar anfällt."* Daraus vier Prüfungen, in dieser
Reihenfolge. **Die erste, die zutrifft, entscheidet:**

| # | Frage | Wenn ja |
|---|---|---|
| 1 | Adressiert die Einheit **jemand anderen** als unsere Einrichtung? Kommission, Mitgliedstaaten, notifizierte Stellen, Behörden, Anbieter ohne Durchschlag auf den Betreiber | `out` — Grund: Adressat |
| 2 | Greift eine **Bereichsausnahme**? Für BSIG §§ 30 ff.: § 28 Abs. 5 Nr. 2 | `out` — Grund: Ausnahme mit Fundstelle **und** Angabe, welche Norm stattdessen gilt |
| 3 | Fällt die Pflicht **am Lebenszyklus eines KI-Systems** prüfbar an? Physische Objektsicherung, Verwaltungsverfahren, Sanktionsrahmen, Berichtspflichten der Behörden: nein | `out` — Grund: kein Lebenszyklusbezug (HANDBUCH 4.1) |
| 4 | Sonst | `in` |

**Im Zweifel `in`.** Eine Einheit, die zu Unrecht `in` steht, kostet eine Zeile
Durchsicht. Eine, die zu Unrecht `out` steht, verschwindet aus der Analyse und taucht
nie wieder auf.

**Eine Ausnahme von Schritt 3:** Definitionen und Verweisungen, die eine `in`-Pflicht
*steuern*, bleiben `in` — § 2 Nr. 22 BSIG entscheidet über den ganzen Status und ist
deshalb selbst prüfrelevant, obwohl er für sich genommen keine Pflicht begründet.

### `befund` — nur bei `scope: in`

| Wert | Bedeutung | Verlangt |
|---|---|---|
| `gedeckt` | Ein Requirement **und** ein Gate treffen die Pflicht **vollständig** | die IDs in `requirement` und `gate` |
| `teilabdeckung` | Getroffen, aber ein Teil der Pflicht bleibt ungeprüft | `befund_grund`: **welcher Teil** fehlt |
| `luecke` | Kein Requirement und kein Gate trifft sie | `befund_grund`: ein Satz, warum das eine Lücke und keine Scope-Grenze ist |
| `nicht_einschlaegig` | Adressiert uns und ist lebenszyklusrelevant, begründet aber **keine prüfbare Pflicht** — ein Recht, eine Erlaubnis, eine steuernde Definition | `befund_grund` |

Der Unterschied zwischen `luecke` und `nicht_einschlaegig` ist der teuerste in dieser
Tabelle: **eine Lücke verlangt ein Gate, ein `nicht_einschlaegig` verlangt keines.** Wer
die beiden vermischt, erzeugt entweder Arbeit, die niemand braucht, oder eine Deckung,
die es nicht gibt.

### Was der Agent nie entscheidet

`scope`, `befund` und jede HYPOTHESE sind Aussagen über Wirklichkeit und liegen beim PO
(AGENTS.md 3). Der Lauf **legt vor** und setzt auf jeder angefassten Zeile
`po_bestaetigt: false`. Die Regeln oben sind kein Ersatz für die Entscheidung — sie
sorgen dafür, dass alle Zeilen nach demselben Maß vorgelegt werden und die Durchsicht
gegen ein Raster läuft statt gegen Einzelfälle.

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
  docs/coverage/bsig_pflichtenraum.yaml   295 Einheiten

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

DIE BEREICHSAUSNAHME IST DAS ERGEBNIS DIESES LAUFS. § 28 Absatz 5 Nummer 2
nimmt die §§ 30, 31, 32, 35, 36, 38, 39, 61 und 62 heraus für Einrichtungen,
die Energieversorgungsnetze betreiben und den §§ 5c bis 5e EnWG unterliegen.
Diese Paragraphen gehen also überwiegend auf scope: out — aber MIT der
Begründung und mit der Angabe, welche Norm stattdessen gilt. Der begründete
Ausschluss ist hier die Erkenntnis, nicht das Weglassen. § 2 und § 28 selbst
bleiben scope: in, denn sie tragen den Status und die Ausnahme.

Deutsche Definitionslisten ('1. 2. 3.' innerhalb eines Absatzes) trennt der
Extraktor nicht. Wo eine Einheit mehrere Begriffsbestimmungen in einem
Ausschnitt trägt, ist das kein Beleg-Fehler — der Beleg ist wortgleich, nur
grob geschnitten. Behandle die enthaltenen Definitionen im Feld pflicht
einzeln und vermerke es.
```

## Lauf 2 — KRITIS-Dachgesetz und EnWG § 11

```
LAUF 2 — KRITIS-Dachgesetz und EnWG § 11

  docs/coverage/kritisdachg_pflichtenraum.yaml   135 Einheiten
  docs/coverage/enwg_pflichtenraum.yaml           15 Einheiten

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

DAS EnWG IST DER OPERATIVE KERN, NICHT DAS ANHÄNGSEL. Weil § 28 Absatz 5
Nummer 2 BSIG die dortigen Kernpflichten verdrängt, stehen die materiellen
IT-Sicherheitspflichten des Adressaten hier — in 15 Einheiten:

  § 5c  IT-Sicherheit im Anlagen- und im Netzbetrieb, Festlegungskompetenz
        (die Rechtsgrundlage, aus der der BNetzA-Katalog stammt)
  § 5d  Dokumentations-, Melde-, Registrierungspflicht
  § 5e  Umsetzungs-, Überwachungs- und Schulungspflicht für Geschäftsleitungen
  § 11  Betrieb von Energieversorgungsnetzen, Abs. 1a/1b

Diese 15 Einheiten sind pro Stück wertvoller als hundert im DSGVO-Raum.
Arbeite sie mit derselben Sorgfalt durch wie Art. 26 des AI Act.

Erfasse besonders genau, WORAUF § 5c verweist und was er dem Netzbetreiber
auferlegt: die Festlegungskompetenz ist der Übergabepunkt zum IT-Sicherheits-
katalog, für den noch kein Pflichtenraum existiert. Was dort steht, entscheidet,
wie groß diese Lücke ist.
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
