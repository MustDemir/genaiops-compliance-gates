# SPEC-06 — Deckungsanalyse Norm → Requirement: die fehlende Richtung

**Status:** Entwurf · 04.09.2026 · Stufe 0 einsatzbereit, Analyse beginnt 04.09. 22:00
**Voraussetzung:** T-09 abgeschlossen (`f209f72`)
**Bezug:** HANDBUCH 2.4 („Was dem Prozess noch fehlt", Punkt 1), Teil 7 Punkt 9 ·
Masterarbeit Anhang B und Anhang M.3 · HISTORIE H4.18

---

## 1. Anlass

**Alles, was dieses Repo bisher gebaut hat, ist Verifikation.** Die Gates tun, was sie
sagen; die Integrity-Suite hält jede Deklaration gegen ihren Gegenstand; die Kette ist
signiert und identitätsgebunden. Was nichts prüft: **ob der Katalog die richtigen Gates
enthält.** HANDBUCH 2.4 führt das seit der ersten Fassung als den schwerwiegendsten
offenen Punkt — *„Woher weiß ich, dass diese 17 die richtigen 17 sind?"*

### 1.1 Warum die vorhandene Coverage-Analyse das nicht beantwortet

Die Masterarbeit hat eine Coverage-Matrix (Anhang B) und ein Compliance-Mapping über
eine sechsstufige Kette (Anhang M.3):

```
EU-AI-Act-Artikel → Requirement → Gate-Instanz → Enforcement-Säule → Rego-Policy → Evidence-Record
```

Ihr Befund lautet: *„Alle 14 Requirements werden durch mindestens ein Quality Gate
operationalisiert."* Das ist **Abdeckung der Requirements durch Gates** — die Kette wird
von links nach rechts geprüft und ist lückenlos.

**Nie geprüft wurde, ob links genug steht.** Die Norm-Extraktion (Kap. 4.3, Stufe 1)
setzt den Rahmen „Art. 9–15 plus Art. 26" — literaturgestützt und plausibel, aber
**gesetzt, nicht abgeleitet**. Deshalb kann die Arbeit sagen „jedes Requirement hat eine
Norm", nicht aber „jede Norm hat ein Requirement".

Es fehlt keine Sorgfalt. Es fehlt eine **Stufe 0**: den Pflichtenraum erst aufzählen,
dann abbilden.

### 1.2 Drei Befunde, die ohne Stufe 0 nicht auffallen konnten

Maschinelle Auswertung der 14 Requirements gegen die 17 Gates am 04.09.:

| # | Befund |
|---|---|
| 1 | **`G-OPS-06` hat kein Requirement.** Das Gate deckt Art. 25 und Art. 97 — kein Requirement nennt diese Artikel. Die sechsstufige Kette hat dort ein fehlendes Glied |
| 2 | **Asymmetrische Verknüpfung.** `G-OPS-06.links.requirements` nennt `R001`; `R001.linked_gates` nennt nur `G-PRE-01, G-PRE-03`. Die Methode verlangt ausdrücklich *bidirektionale* Traceability |
| 3 | **Eine Scope-Entscheidung ist nicht zurückgeflossen.** Anhang M.3 hält fest, dass Art. 47/48 Anbieterpflichten sind und außerhalb des Scopes liegen. `R011` führt beide weiterhin als eigene `eu_ai_act_refs` |

## 2. Der Rechtsstand, gegen den geprüft wird

Bis heute lag im Repo **nur der ändernde Rechtsakt**: `docs/legal/OJ_L_202601744_DE.pdf`
ist VO (EU) 2026/1744 (Digital-Omnibus zur KI), nicht der AI Act. Die Artikel, an denen
die Requirements hängen, stehen in 2024/1689 — und dieser Text fehlte.

Seit 04.09. liegt er als `docs/legal/wortlaut/aiact_2024-1689_DE.txt`, aus EUR-Lex
(CELEX 32024R1689, deutsche Fassung), mit SHA-256 im Kopf des Pflichtenraums.

**Was der Omnibus an den tragenden Artikeln ändert** — geprüft am verfügenden Teil,
dessen Änderungsliste nach Artikelnummer geordnet ist, sodass auch die Lücken belastbar
sind:

| Artikel | Status | Bedeutung |
|---|---|---|
| **Art. 26** | **nicht geändert** (Liste springt 25 → 27) | Der Kernartikel steht unverändert |
| **Art. 13** | nicht geändert | — |
| **Art. 73** | nicht direkt geändert | Neuer Art. 75 Abs. 1a schafft einen Parallelweg zum KI-Büro. Berührt B-13 |
| **Art. 27** | **geändert**, Abs. 4 und 5 | Trifft R012 direkt |
| Art. 50 | nur Abs. 7 | Kennzeichnungspflicht selbst unverändert |
| **Art. 113** | geändert | Annex III ab 02.12.2027, Annex I ab 02.08.2028 |

> **Ein Widerspruch im eigenen Bestand:** `HISTORIE.md:943` nennt als geänderte Artikel
> „Art. 10, 11, 25, 27, 43, 49, 72". Nach Lesung des verfügenden Teils ist die Liste
> unvollständig, und **Art. 49 kommt darin nicht vor** — Artikel 3 des Omnibus ändert
> einen Art. 47, aber das ist die Maschinenverordnung 2023/1230. Befundvorschlag, vom
> PO zu prüfen.

## 3. Scope — vier Festlegungen des PO (04.09.2026)

| # | Festlegung | Konsequenz |
|---|---|---|
| 1 | **Betreiberpflichten vollständig + alle mittelbar durchschlagenden** | Art. 26 ganz, plus jede Pflicht der Art. 8–15, 27, 50, 72, 73, die den Betreiber als Prüf-, Verifikations- oder Mitwirkungspflicht trifft. Anbieterpflichten nur, wo sie eine Betreiberpflicht auslösen |
| 2 | **Satz- und Pflichtenebene** | Jede einzelne normative Aussage ist eine Zeile. Feinstes Raster, höchste Nachweiskraft — und die einzige Granularität, auf der „ist das Abgebildete vollständig" beantwortbar ist |
| 3 | **Art. 25 gehört in den Pflichtenraum** | Der Aufstieg zum Anbieter ist der Fall, in dem Anbieterpflichten voll durchschlagen. Schließt zugleich Befund 1 |
| 4 | **Der volle Sektorstapel** | NIS2/NIS2UmsuCG, EnWG § 11 + IT-Sicherheitskatalog BNetzA, KRITIS-Dachgesetz — nach dem AI Act, Norm für Norm |

## 4. Was diese SPEC nicht enthält

| Nicht enthalten | Warum, und wohin es gehört |
|---|---|
| **Alle Hochrisiko-Pflichten (Kapitel III vollständig, Anbieter wie Betreiber)** | Vom PO ausdrücklich als **spätere Ausbaustufe** vorgemerkt (04.09.). Schließt an den größten offenen Block aus HANDBUCH 6.1 an — Provider-Pflichten Art. 16–20, 43, 47–49, für die heute kein Gate existiert. Eigene SPEC |
| **Neue Gates oder Requirements bauen** | Diese SPEC stellt Lücken fest. Sie zu schließen ist je ein eigenes Ticket, mit den PO-Entscheidungen, die dazugehören |
| **Die Meldekaskade** | Bleibt gesperrt, bis Art. 26 Abs. 5 und Art. 73 EUR-Lex-abgeglichen sind (HANDBUCH 6.1). Diese SPEC **liest** beide im Wortlaut und hebt die Sperre damit möglicherweise auf — bauen darf sie nichts |
| **Rechtsberatung** | Kein Rechtsgutachten. Jede Zeile trägt ihre Verifikationsstufe; Auslegung ist als HYPOTHESE gekennzeichnet und bleibt eine Entscheidung des PO |

## 5. Stufe 0 — wie der Pflichtenraum entsteht

**Vollständigkeit entsteht durch Aufzählung, nicht durch Behauptung.**
`tools/legal/extract_norm_units.py` schneidet die Quelle in Einheiten:

```
Artikel → Absatz → (Buchstabe) → Satz
```

`build_pflichtenraum.py` legt für **jede** Einheit eine Zeile an — auch für die
offensichtlich nicht einschlägigen. Die müssen auf `scope: out` **mit Grund** gesetzt
werden. Stilles Weglassen ist damit von Übersehen unterscheidbar, und beides ist ein
Fehlschlag statt einer unsichtbaren Auslassung.

**Stand der Quelle:** 113 Artikel, lückenlos 1–113, alle Anhänge I–XIII.
**1027 Einheiten, 1577 Sätze.** In den 18 kernnahen Artikeln: 188 Einheiten, 271 Sätze.

### 5.1 Die Zeile

```yaml
- id: "Art. 26 Abs. 1"
  offset: 358947          # Zeichenposition in der Quelldatei
  laenge: 257
  beleg: "(1)   Die Betreiber von Hochrisiko-KI-Systemen treffen geeignete …"
  adressat: betreiber
  pflicht: "…"            # CLAIM — meine Formulierung, getrennt vom BELEG
  scope: in               # in | out (+ scope_grund)
  verifikation: VERIFIZIERT   # | SEKUNDAERQUELLE | HYPOTHESE (+ hypothese_grund)
  omnibus: "unveraendert — …"
  requirement: [R011]
  gate: [G-DEP-04]
  befund: teilabdeckung   # gedeckt | teilabdeckung | luecke | nicht_einschlaegig
  befund_grund: "…"
```

`beleg` wird **geschnitten, nie getippt**. Das ist der Unterschied zwischen Auszug und
Erinnerung, und er ist der Kern der Fälschungssicherheit dieser Analyse.

## 6. Wie Halluzination ausgeschlossen wird

Nicht durch Sorgfalt, sondern durch Konstruktion. `verify_norm_quotes.py` prüft:

1. **Der SHA-256 der Quelle** stimmt mit dem im Pflichtenraum vermerkten überein.
   Ändert sich die Quelle, sind alle Offsets ungültig und die Ableitung nachweislich
   veraltet statt still falsch.
2. **Jedes Zitat steht wörtlich an seinem Offset.** Umformuliert, gekürzt, ergänzt
   oder erfunden — alles fällt auf, unabhängig davon, wie plausibel es klingt.
3. **Wortlaut und Auslegung sind getrennte Felder.** `beleg` ist Quelle, `pflicht` und
   `befund_grund` sind Aussage. Sie können nicht ineinanderlaufen.
4. **Jede Zeile trägt eine Verifikationsstufe**, und HYPOTHESE ohne Begründung ist ein
   Fehlschlag.
5. **Jede Zeile trägt eine Scope-Entscheidung**, und `out` ohne Grund ist ein Fehlschlag.

**Gegenprobe geführt (04.09.):** In `Art. 26 Abs. 4` wurde *„ausreichend repräsentativ"*
durch *„hinreichend repräsentativ"* ersetzt — ein Wort, in den ersten 120 Zeichen
unsichtbar, juristisch bedeutsam. Der Check meldete den Eintrag namentlich; nach dem
Zurücknehmen war er still. **1027 von 1027 Einheiten sind wortgleich belegt.**

## 7. Definition of Done

1. Jede der 1027 Einheiten trägt `scope` und `verifikation`; `out` und `HYPOTHESE`
   tragen ihren Grund. Beleg: `verify_norm_quotes.py` BESTANDEN.
2. Jede Einheit mit `scope: in` trägt einen `befund`; `teilabdeckung` und `luecke`
   tragen einen `befund_grund`.
3. Die drei Befunde aus 1.2 sind adressiert — behoben oder als Ticket gestellt.
4. Der Widerspruch in `HISTORIE.md:943` ist geprüft.
5. `LEGAL_QUOTES_VERBATIM` läuft in der Integrity-Suite und in `make verify`.
6. Ergebnisbericht: Wie viele Betreiberpflichten hat der AI Act, wie viele sind
   gedeckt, wie viele teilweise, wie viele gar nicht — als Zahlen, die man nachzählen
   kann.

## 8. Abnahme durch den PO

Der rote Lauf ist geführt (6). Abzunehmen ist die **Zuordnung**: `scope`, `befund` und
jede HYPOTHESE sind Entscheidungen des PO, nicht der KI — dieselbe Linie wie bei den
vier Ehrlichkeitsfeldern (AGENTS.md 3). Die KI legt vor und belegt; sie entscheidet nicht.
