---
titel: Schritt 2a – die 22 „nicht_einschlaegig" neu eingeordnet
stand: 2026-09-23
basis: Branch spec06-aiact-stufe0, Raster aus T-13 (07.09.2026)
status: ENTSCHIEDEN 23.09.2026 (Nachweis: 02 „PO-Entscheide bisher“, entscheide/2026-09-23_schritt-2.yaml)
---

# Warum dieser Schritt
- Nachtläufe 04.–06.09., Raster erst 07.09.
- Raster sagt: `nicht_einschlaegig` = Einheit adressiert uns, begründet aber **keine prüfbare Pflicht** (Recht, Erlaubnis, steuernde Definition)
- Die Läufe nutzten es anders: „passt nicht zu unserem Fall" → das ist laut Raster meist `out`

# Das Raster (T-13), kurz
```
Schritt 1  Adressat ist jemand anderes?          → out (Grund: Adressat)
Schritt 2  Bereichsausnahme greift?              → out (Grund: Ausnahme + Fundstelle)
Schritt 3  Kein Lebenszyklusbezug?               → out
Schritt 4  sonst                                 → in → befund
```

# Ergebnis auf einen Blick
| Gruppe | Zeilen | Vorschlag | Raster-Schritt |
|---|---|---|---|
| A – Anhang-III-Nr.-2-Ausnahme | Art. 27 (10×), Art. 49 Abs. 3, Art. 71 Abs. 3, Art. 86 Abs. 1 | **out** | 2 – Bereichsausnahme |
| B – anderer Betreibertyp | Art. 26 Abs. 8, Art. 26 Abs. 10 | **out** | 1 – Adressat |
| C – anderer Systemtyp | Art. 14 Abs. 5, Art. 73 Abs. 10 | **out** | fehlt im Raster → Ergänzung nötig |
| D – Verbote Art. 5 | Art. 5 Abs. 1 lit. e, f, g | **luecke** (wie lit. a–d) | 4 – in |
| E – bedingte Pflicht | Art. 60 Abs. 4 lit. h, j | **out mit Bedingung** | PO-Frage |

**Neue Zählung (falls PO zustimmt):**
| | vorher | nachher |
|---|---|---|
| in | 81 | **62** |
| gedeckt | 3 | 3 |
| teilabdeckung | 33 | 33 |
| luecke | 23 | **26** |
| nicht_einschlaegig | 22 | **0** |
| out | 801 | **820** |

# Tabelle je Zeile
| # | Einheit | Wortlaut-Kern (aus `beleg`) | Vorschlag | Grund |
|---|---|---|---|---|
| 1 | Art. 27 Abs. 1 | „— mit Ausnahme von Hochrisiko-KI-Systemen, die in dem in Anhang III Nummer 2 aufgeführten Bereich verwendet werden sollen —" | out | Bereichsausnahme Art. 27 Abs. 1 |
| 2–7 | Art. 27 Abs. 1 lit. a–f | Inhalt der FRIA | out | teilen Ausnahme aus Abs. 1 |
| 8 | Art. 27 Abs. 2 | Erstverwendung, Aktualisierung | out | setzt Pflicht aus Abs. 1 voraus |
| 9 | Art. 27 Abs. 3 | Mitteilung an Marktüberwachung | out | dito |
| 10 | Art. 27 Abs. 4 | FRIA ergänzt DSFA | out | dito – **DSFA selbst bleibt über Art. 26 Abs. 9** |
| 11 | Art. 49 Abs. 3 | „— mit Ausnahme der in Anhang III Nummer 2 aufgeführten Hochrisiko-KI-Systeme —" + nur Behörden | out | Ausnahme + Adressat |
| 12 | Art. 71 Abs. 3 | Dateneingabe durch Betreiber-Behörden | out | Adressat Behörde |
| 13 | Art. 86 Abs. 1 | „mit Ausnahme der in Nummer 2 des genannten Anhangs aufgeführten Systeme" | out | Bereichsausnahme Art. 86 Abs. 1 |
| 14 | Art. 26 Abs. 8 | Betreiber = Organe/Stellen der Union | out | Adressat |
| 15 | Art. 26 Abs. 10 | nachträgliche biometrische Fernidentifizierung, Strafverfolgung | out | Adressat |
| 16 | Art. 14 Abs. 5 | nur Anhang III Nr. 1 lit. a (biometrisch) | out | Systemtyp |
| 17 | Art. 73 Abs. 10 | nur Medizinprodukte (VO 2017/745, 746) | out | Systemtyp |
| 18 | Art. 5 Abs. 1 lit. e | Verbot: Gesichtserkennungs-DB durch Scraping | **luecke** | Verbot gilt für jede Verwendung; prüfbar |
| 19 | Art. 5 Abs. 1 lit. f | Verbot: Emotionserkennung am Arbeitsplatz | **luecke** | dito – Netzbetreiber ist Arbeitgeber |
| 20 | Art. 5 Abs. 1 lit. g | Verbot: biometrische Kategorisierung | **luecke** | dito |
| 21 | Art. 60 Abs. 4 lit. h | Vereinbarung bei Realbedingungstest | out* | *wird `in`, sobald Teilnahme an Test |
| 22 | Art. 60 Abs. 4 lit. j | Überwachung des Realbedingungstests | out* | dito |

# Begründung der zwei strittigen Gruppen

## D – Art. 5 e/f/g: warum Lücke statt „passt nicht"
- Verbot trifft **jede Verwendung**, auch durch Betreiber → kein Adressat-/Ausnahme-Out
- Ob **unser** System das tut, ist eine **Tatsachenfrage**, keine Normfrage → genau dafür sind Gates da
- Heute uneinheitlich: lit. a–d = `luecke`, lit. e–g = `nicht_einschlaegig` → gleiches Maß anlegen
- Verifikation: Norm VERIFIZIERT, „unser System tut es nicht" = **HYPOTHESE** (Tatsache über das System)
- Folge für Schritt 4: **eine** Lücke für alle 8 Art.-5-Zeilen → ein Check „Art.-5-Screening" (z. B. in G-PRE-01), keine 8 Gates

## E – Art. 60: warum out mit Bedingung
- Echte Betreiberpflicht, aber nur bei **freiwilliger** Teilnahme an einem Realbedingungstest
- K1 (Zukauf, Regelfall) sieht das nicht vor
- Vorschlag: `out` + Grund „bedingt: Teilnahme an Test nach Art. 60" → Wiedervorlage, falls Teilnahme geplant
- Alternative: `in` + `luecke` mit Trigger „Testteilnahme" – mehr Aufwand, wenig Nutzen

# Querbefunde (gehen in Schritt 2e / Schritt 4)
| ID | Befund | Wirkung |
|---|---|---|
| Q1 | **FRIA ohne Pflicht.** R012 (MUST, Art. 27) + G-PRE-02/C-01 + **G-PRE-05/C-01** (prüft „FRIA abgeschlossen mit affected_rights") verlangen eine FRIA, die für Anhang III Nr. 2 nicht geschuldet ist. R012 schreibt selbst „für private Deployer … Best Practice" und steht trotzdem auf MUST | Ehrlichkeitsfeld MUST/SHOULD → PO: streichen / SHOULD / freiwillig kennzeichnen. Wichtig: Einstufung als Nr.-2-System hängt an G-PRE-01 – kippt die, kippt die Ausnahme |
| Q2 | **Drei Nr.-2-Ausnahmen** (Art. 27, 49 Abs. 3, 86 Abs. 1) – der Gesetzgeber entlastet kritische Infrastruktur gezielt | Inhalt für Fachbeitrag; ggf. Pflichtenmenge an Einstufung aus G-PRE-01 koppeln |
| Q3 | **Raster-Lücke „Systemtyp".** Kein Schritt für „Norm gilt nur für anderen Systemtyp" (Art. 14 Abs. 5, 73 Abs. 10) | Raster in T-13 um Schritt 2b ergänzen, bevor die Anhänge und der Sektorstapel laufen |
| Q4 | **Raster-Lücke „bedingte Pflicht".** Art. 60 passt in keinen Schritt | Raster-Regel ergänzen: out + Bedingung + Wiedervorlage |
| Q5 | **DSFA bleibt.** Art. 27 fällt weg, aber Art. 26 Abs. 9 (DSFA nach Art. 35 DSGVO) ist eine der 23 Lücken | nicht mit Q1 verwechseln |

# PO-Entscheidungen für diesen Schritt
1. Gruppe A–C (17 Zeilen) → `out` wie vorgeschlagen?
2. Gruppe D (3 Zeilen) → `luecke`?
3. Gruppe E (2 Zeilen) → `out` mit Bedingung?
4. Raster um „Systemtyp" und „bedingte Pflicht" ergänzen (Q3, Q4)?
5. Q1 FRIA: vormerken für Schritt 3 (keine Entscheidung jetzt nötig)
