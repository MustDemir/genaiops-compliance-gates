# T-12 — Deckungsanalyse EU AI Act, Stufe 0 ausfüllen (Cowork, drei geplante Läufe)

**Status:** BEREIT · gestellt 04.09.2026
**Bezug:** [`SPEC-06`](../../specs/SPEC-06-deckungsanalyse-norm-requirement.md) · HANDBUCH Teil 7 Punkt 9, 2.4 · AGENTS.md 3 und 5

---

## WARUM

`docs/coverage/aiact_pflichtenraum.yaml` enthält **1027 Pflichteneinheiten** des EU AI Act
mit fertigem, aus der Quelle geschnittenem Belegzitat — und leeren Analysefeldern. Eine
Einheit ist ausgefüllt (Musterzeile `Art. 26 Abs. 1`), 1026 sind offen.

Das Ausfüllen ist Fleißarbeit mit Urteilsanteil: je Einheit Adressat, Pflicht in einem
Satz, Scope-Entscheidung, Abgleich gegen die 14 Requirements und 17 Gates, Befund. Über
eine Sitzung ist das nicht zu schaffen, und es muss auch nicht — der Pflichtenraum trägt
seinen Zustand selbst, und `tools/legal/fortschritt.py` liest ihn aus.

Deshalb drei geplante Läufe über Nacht statt eines langen.

## RECHTSBEZUG

VO (EU) 2024/1689 in der Fassung der VO (EU) 2026/1744. Beide Wortlaute liegen im Repo,
je mit SHA-256. **Der Auftrag erzeugt keine Rechtsaussage, die nicht aus dem Wortlaut
belegt ist** — jede Auslegung ist als HYPOTHESE zu kennzeichnen (HANDBUCH 2.3).

## PO-ENTSCHEIDUNGEN

Vier Festlegungen zum Scope stehen in SPEC-06 Abschnitt 3 und gelten unverändert:
Betreiberpflichten samt durchschlagender · Satz- und Pflichtenebene · Art. 25 inbegriffen ·
Sektorstapel erst danach.

**Nicht entschieden und nicht zu entscheiden:** `scope`, `befund` und jede HYPOTHESE je
Einheit. Das sind Aussagen über Wirklichkeit und liegen beim PO (AGENTS.md 3, SPEC-06
Abschnitt 8). Ein unbeaufsichtigter Lauf kann nicht fragen — deshalb **legt er vor und
markiert**: jede angefasste Zeile bekommt zusätzlich `po_bestaetigt: false`.

## SCOPE IN

- `docs/coverage/aiact_pflichtenraum.yaml` — ausschließlich die Analysefelder
- `tools/legal/` — nur, falls ein Werkzeug nachweislich fehlerhaft ist

## SCOPE OUT

- **`docs/legal/**` wird nicht verändert.** Gehashte Primärquelle; jede Änderung macht
  alle 1027 Offsets ungültig
- Das Feld `beleg` wird nicht angefasst. Es ist geschnitten, nicht getippt
- Requirements, Gates, Policies ändern. Dieses Ticket **stellt fest**; Lücken zu schließen
  ist je ein eigenes Ticket mit den PO-Entscheidungen, die dazugehören
- Der Sektorstapel (NIS2, EnWG, KRITIS) — siehe T-13
- Push auf `domain_netzbetrieb`. Der Cloud-Lauf hat den lokalen `pre-push`-Hook nicht

## DEFINITION OF READY

1. Wortlaut im Repo: `docs/legal/wortlaut/aiact_2024-1689_DE.txt`, SHA-256
   `4720c11b40496f901c4a91a62190f9256c1f43dfd9df796b2e5e22855b0bf199` ✅
2. Gerüst erzeugt, 1027 Einheiten, alle Belege wortgleich geprüft ✅
3. SPEC-06 mit den vier Scope-Festlegungen ✅

## DEFINITION OF DONE — maschinell

1. `python3 tools/legal/verify_norm_quotes.py docs/coverage/aiact_pflichtenraum.yaml`
   meldet **BESTANDEN**
2. `make verify` grün — 36 Integration, 36 Integrity, 215 Rego, Parität, Migration, Manifest
3. `python3 tools/legal/fortschritt.py docs/coverage/aiact_pflichtenraum.yaml` meldet
   **0 offen**
4. Jede Einheit trägt `scope` und `verifikation`; `out` und `HYPOTHESE` tragen ihren Grund
5. Jede Einheit mit `scope: in` trägt einen `befund`; `teilabdeckung` und `luecke` tragen
   einen `befund_grund`

## ABNAHME DURCH DEN PO

Abzunehmen ist die **Zuordnung**, nicht der Durchlauf. Der PO geht die Zeilen mit
`po_bestaetigt: false` durch und bestätigt oder korrigiert. `fortschritt.py` nennt die Zahl.

Zusätzlich vorzulegen: die Zahlen des Abschlussberichts — wie viele Betreiberpflichten hat
der AI Act auf Satzebene, wie viele sind gedeckt, teilweise gedeckt, nicht gedeckt.

## COMMIT

Ein Commit je Artikelgruppe, nicht einer am Ende. PR gegen `domain_netzbetrieb`, kein
direkter Push. Keine `Co-Authored-By`-Zeile.

---

# Die Auftragstexte — zum Kopieren

Drei Läufe. **Block A steht in jedem Lauf**, dahinter der Block des jeweiligen Laufs.

## Block A — gilt für alle drei Läufe

```
Repository: https://github.com/MustDemir/genaiops-compliance-gates
Basis-Branch: domain_netzbetrieb
Arbeite auf Branch spec06-aiact-stufe0 und öffne am Ende einen Pull Request.
Pushe NICHT auf domain_netzbetrieb.

Vorbereitung:
  git pull
  git checkout -B spec06-aiact-stufe0 origin/domain_netzbetrieb
  python3 -c "import yaml" || pip install pyyaml
  python3 tools/legal/fortschritt.py docs/coverage/aiact_pflichtenraum.yaml

Der letzte Befehl sagt dir, wo der vorige Lauf aufgehört hat. Bearbeite NUR
Einheiten, die noch kein Feld "scope" haben. Fasse keine Einheit an, die
bereits eines hat.

ZUERST LESEN, IN DIESER REIHENFOLGE
1. specs/SPEC-06-deckungsanalyse-norm-requirement.md — der Auftrag, die vier
   PO-Festlegungen zum Scope, die Definition of Done
2. docs/tickets/T-12-cowork-aiact-stufe0.md — dieses Ticket
3. AGENTS.md Abschnitt 3 (wer entscheidet was) und 5 (Lieferformat)
4. HANDBUCH.md Teil 0, 2.3 (Evidenzstufen), 2.4, 4.4
5. requirements/R001.yaml bis R014.yaml und gate-definitions/**/*.yaml

DIE AUFGABE JE EINHEIT
Fülle in docs/coverage/aiact_pflichtenraum.yaml:
  adressat        betreiber | anbieter | behoerde | sonstige
  pflicht         die Pflicht in EINEM Satz, deine Formulierung
  scope           in | out   (bei out: scope_grund, immer)
  verifikation    VERIFIZIERT | SEKUNDAERQUELLE | HYPOTHESE
  hypothese_grund bei HYPOTHESE Pflicht
  omnibus         unveraendert, oder: geaendert durch 2026/1744 Art. 1 Nr. N
  requirement     Liste der R-xx, die diese Pflicht abbilden, oder []
  gate            Liste der G-xxx, die sie prüfen, oder []
  befund          gedeckt | teilabdeckung | luecke | nicht_einschlaegig
  befund_grund    bei teilabdeckung und luecke Pflicht
  po_bestaetigt   IMMER false — du entscheidest nichts, du legst vor

UNVERHANDELBARE REGELN
- Zitate werden NIE getippt. Das Feld "beleg" ist bereits aus der Quelle
  geschnitten und wird nicht verändert. Brauchst du weiteren Wortlaut, schneide
  ihn per Skript aus docs/legal/wortlaut/aiact_2024-1689_DE.txt.
- docs/legal/** wird NICHT verändert. Gehashte Primärquelle. Jede Änderung
  macht alle 1027 Offsets ungültig.
- Du entscheidest keine PO-Felder. po_bestaetigt: false auf jeder Zeile, die
  du anfasst.
- VERIFIZIERT nur, wo die Aussage unmittelbar im Wortlaut steht. Alles
  Ausgelegte ist HYPOTHESE mit Begründung. Eine ungekennzeichnete Auslegung
  ist der Fehler, gegen den diese ganze Analyse gebaut ist.
- Für das Feld omnibus: prüfe die Änderungsliste in Artikel 1 der VO (EU)
  2026/1744, docs/legal/OJ_L_202601744_DE.pdf. Sie ist nach Artikelnummer
  geordnet — was nicht darin steht, ist unverändert.
- Erfinde nichts. Was ohne PO-Entscheidung nicht beantwortbar ist, kommt in
  den Bericht, nicht ins Feld.
- Auch "offensichtlich nicht einschlägig" braucht scope: out MIT Grund.
  Stilles Weglassen ist ein Fehlschlag, kein Zeitgewinn.

VOR JEDEM COMMIT
  python3 tools/legal/verify_norm_quotes.py docs/coverage/aiact_pflichtenraum.yaml

Meldet es FEHLGESCHLAGEN wegen eines Belegs, hast du eine Quellzeile
verändert — nimm das zurück. Meldungen zu fehlenden Analysefeldern der noch
offenen Einheiten sind erwartet und kein Fehler.

COMMITS
Ein Commit je Artikelgruppe, nicht einer am Ende. Die Nachricht sagt, was jetzt
wahr ist, nicht was getan wurde. Keine Co-Authored-By-Zeile.

AM ENDE DES LAUFS
Schreibe einen Zwischenbericht in die PR-Beschreibung:
- welche Artikel bearbeitet, wie viele Einheiten
- Ausgabe von fortschritt.py
- die gefundenen Lücken und Teilabdeckungen, je mit einem Satz
- jede Frage, die eine PO-Entscheidung braucht, gesammelt an einer Stelle
- was du nicht geschafft hast und warum
```

## Block B — Lauf 1: der Kern

```
LAUF 1 VON 3 — Art. 26 und die durchschlagenden Pflichten

Bearbeite in dieser Reihenfolge:
  1. Artikel 26, alle 12 Absätze — die Betreiberpflichten, der Kern
  2. Artikel 8, 9, 10, 11, 12, 13, 14, 15 — die Anforderungen an
     Hochrisiko-Systeme, soweit sie auf den Betreiber durchschlagen

Rund 90 Einheiten. Hier entstehen die inhaltlichen Befunde; nimm dir Zeit je
Einheit statt viele oberflächlich zu füllen. Wenn du 90 nicht schaffst, ist
das in Ordnung — der nächste Lauf setzt an, wo du aufhörst.

Achte besonders auf:
- Art. 26 Abs. 1 ist als Musterzeile schon gefüllt und trägt einen Verdacht:
  R011 nennt diesen Absatz als Fundstelle, zielt aber ausweislich seines Titels
  auf Art. 47/48. Prüfe, ob die Pflicht aus Abs. 1 — organisatorische Maßnahmen
  für den betriebsanleitungskonformen Einsatz — anderswo im Katalog getroffen
  wird. Ergebnis in befund_grund, po_bestaetigt bleibt false.
- Art. 26 Abs. 5 und Art. 73: die Meldekaskade darf NICHT gebaut werden
  (HANDBUCH 6.1, Bauverbot). Lesen und im Pflichtenraum erfassen ist erlaubt
  und ausdrücklich erwünscht — es ist der Abgleich, auf den das Bauverbot wartet.
- Art. 10: Anhang M.3 der Masterarbeit hält fest, dass für Betreiber, die
  Foundation Models über API nutzen, nur Abs. 6 einschlägig ist. Prüfe das am
  Wortlaut und übernimm es nicht ungeprüft.
```

## Block C — Lauf 2: die übrigen einschlägigen

```
LAUF 2 VON 3 — die übrigen einschlägigen Artikel und die Anhänge

Bearbeite in dieser Reihenfolge:
  1. Artikel 25 — Rollenwechsel Betreiber zu Anbieter
  2. Artikel 27 — Grundrechte-Folgenabschätzung
  3. Artikel 50 — Transparenzpflichten
  4. Artikel 72 — Beobachtung nach dem Inverkehrbringen
  5. Artikel 73 — Meldung schwerwiegender Vorfälle
  6. Anhang III, Anhang IV, Anhang VIII

Rund 100 Einheiten.

Achte besonders auf:
- Art. 25 deckt heute G-OPS-06 ab, OHNE dass ein Requirement dazwischensteht.
  Dasselbe gilt für Art. 97. Das ist Befund 1 aus SPEC-06 Abschnitt 1.2 —
  bestätige oder widerlege ihn am Wortlaut.
- Art. 27 wurde durch die VO 2026/1744 in Abs. 4 und 5 GEÄNDERT. Erfasse die
  geänderte Fassung und vermerke es im Feld omnibus. R012 hängt daran.
- Anhang III Nummer 2 ist die Einstufung, auf der das ganze Vorhaben ruht
  (kritische Infrastruktur). Erfasse sie besonders sorgfältig.
```

## Block D — Lauf 3: Rest, Bericht, Selbstreview

```
LAUF 3 VON 3 — alle übrigen Einheiten, Abschlussbericht, Selbstreview

1. Alle noch offenen Einheiten bearbeiten. Das sind überwiegend Artikel, die
   den Betreiber nicht adressieren — Marktüberwachung, Notifizierung,
   Governance, Schlussbestimmungen. Sie bekommen scope: out MIT GRUND. Ein
   Satz genügt, aber er muss dastehen.

2. Selbstreview von Lauf 1 und 2: Geh die Einheiten mit scope: in erneut durch
   und prüfe, ob jede requirement- und gate-Zuordnung in BEIDE Richtungen
   stimmt — nennt das Requirement das Gate, und nennt das Gate das Requirement?
   Asymmetrien sind ein Befund (SPEC-06 Abschnitt 1.2, Befund 2).

3. Abschlussbericht in der PR-Beschreibung, mit diesen Zahlen:
   - Betreiberpflichten des AI Act, gezählt auf Satzebene
   - davon gedeckt / teilabdeckung / luecke, je als Zahl und als Liste
   - Artikel, die nur ein Gate nennt, aber kein Requirement
   - Requirements, deren eu_ai_act_refs auf Fundstellen zeigen, die der
     Wortlaut nicht trägt
   - alle offenen PO-Entscheidungen, gesammelt
   - alle HYPOTHESE-Zeilen, gesammelt, weil sie zusammen den Auslegungsanteil
     der Analyse zeigen

4. Definition of Done prüfen und Ausgaben in den PR:
     python3 tools/legal/verify_norm_quotes.py docs/coverage/aiact_pflichtenraum.yaml
     python3 tools/legal/fortschritt.py docs/coverage/aiact_pflichtenraum.yaml
     make verify

   fortschritt.py muss 0 offen melden. Meldet es mehr, sag im Bericht wie
   viele und warum — schließe den PR trotzdem, mit dieser Angabe.
```
