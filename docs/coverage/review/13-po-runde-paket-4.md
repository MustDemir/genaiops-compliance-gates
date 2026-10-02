---
titel: PO-Runde (Paket 4) – Arbeitsliste
stand: 2026-10-02
basis: Entscheidungsregister Teil 1 und 3 (alle Punkte mit Paket 4) · Pflichtenräume AI Act und Omnibus, Stand Commit 6a074ed · Stichprobe mit festem Seed 20261002
status: Arbeitsliste – nichts entschieden · Befund P4-B1
---

# Kurzfazit

- **Was du tust:** 12 Punkte aus dem Register, drei Arten – **A** Einzelfragen (7), **B** Zeilen bestätigen (4), **C** `out`-Stichprobe (1).
- **Wie:** je Punkt eine Antwort im Chat („Q1 a“, „IN-1 Gruppe 1 ja“). Ich schreibe Entscheidungsdatei, Register und Wächter und committe. YAML fasst du nicht an.
- **Eine Stelle bleibt das Register.** Diese Liste ist das Arbeitsblatt dazu; ihre Tabellen haben eigene Köpfe, damit nichts doppelt registriert wird.
- **Neuer Befund P4-B1:** 11 `in`-Zeilen haben keinen Pflichttext, 12 teilen sich einen Sammeltext. Bestätigen kannst du nur, was dasteht – die Texte schreibe ich vor IN-1 neu (Teil 4).
- **a ist jeweils meine Empfehlung**, außer wo „keine Empfehlung“ steht.

```
Arbeitsblatt (13) ──► du: a/b je Punkt ──► ich: entscheide/2026-10-xx_paket-4.yaml
                                                 │
                                    Register Teil 4 · PO_DECISIONS_APPLIED · Commit
Reihenfolge:  P4-B1 (ich, Texte) ──► A Einzelfragen ──► B Bestätigen ──► C Stichprobe
```

# Teil 1 – A: Einzelfragen

| ID | Frage | Optionen | Antwort |
|---|---|---|---|
| Q1 | **FRIA:** R012, G-PRE-02 und G-PRE-05/C-01 verlangen eine Grundrechte-Folgenabschätzung als MUST. Art. 27 Abs. 1 nimmt Hochrisiko-Systeme aus Anhang III Nr. 2 aus (Review 05); Redispatch ist Anhang III Nr. 2. Omnibus Art. 27 Abs. 4 n.F. steht deshalb schon als `out` im Vorschlag (OUT-1) | a) **bedingt:** FRIA nur, wenn das System nicht unter Anhang III Nr. 2 fällt – Bedingungsparameter im Manifest wie P2-F4; für Redispatch kein MUST · b) MUST behalten, aber als interne Vorgabe ohne Art.-27-Anker kennzeichnen · c) unverändert (MUST mit Art. 27 – widerspricht dem Wortlaut). MUST/SHOULD ist dein Feld | |
| Q11 | **Art. 26 Abs. 11:** Trifft Redispatch „Entscheidungen über natürliche Personen“? Heute Teilabdeckung mit G-DEP-03 unter Vorbehalt (P3-F4 b); abgeleitet wäre es eine Lücke | a) nein: Redispatch steuert Anlagen, nicht Personen → nicht einschlägig · b) ja, soweit Anlagenbetreiber natürliche Personen sind → Lücke, Unterrichtung bauen (Paket 5). **Keine Empfehlung** – Auslegungsfrage. HYPOTHESE, nicht geprüft: Redispatch 2.0 bezieht kleinere Anlagen ein, deren Betreiber natürliche Personen sein können; das spräche für b | |
| S3-1 | **Art. 111 Abs. 2 Satz 2 n.F.** (`in`, Lücke): Frist für Hochrisiko-Systeme, die bestimmungsgemäß von Behörden verwendet werden. Trifft das einen Netzbetreiber, der Behörde ist (z. B. kommunaler Eigenbetrieb)? | a) **dritte Bedingung im P0-Check:** Manifest-Feld „Betreiber ist Behörde“, die Zeile bleibt Lücke, bis es gebaut ist (Paket 5) · b) nicht einschlägig für privatrechtliche Netzbetreiber – Vermerk, Zeile n.e. | |
| A-F1 | **Anhang IV** nennt an vier Stellen den Betreiber (Nr. 1 lit. g, lit. h, Nr. 2 lit. e, Nr. 3). Schlägt die Dokumentationspflicht des Anbieters auf ihn durch? | a) **nein, `out`:** der Betreiber ist Gegenstand der Dokumentation, nicht ihr Empfänger; was er braucht, verlangt Art. 13 (`in`) · b) ja, `in`: Befund je Zeile | |
| R-1 | **Severity** des Wächters `PO_DECISIONS_REGISTERED` | a) **LOW:** Pflegesignal, bricht `make verify` trotzdem (`--fail-on low`) · b) MEDIUM · c) HIGH | |
| P3-B1 | **Art. 73 ungleich zerlegt:** Abs. 2 UAbs. 1 Satz 1 ist Teilabdeckung („unmittelbar“, Fristbeginn bei Kenntnis ungeprüft). Abs. 3 und 4 haben denselben Aufbau und sind gedeckt | a) **Abs. 3, 4 wie Abs. 2 zerlegen** → Teilabdeckung (strenger) · b) Abs. 2 wie Abs. 3, 4 → gedeckt · c) so lassen | |
| A-W12 | **Omnibus-Unterabsätze:** nach der Aufzählung zählt Art. 75 Abs. 2a mit „UAbs. 2“ weiter, Art. 75a Abs. 4 und Art. 75c Abs. 4 springen auf „UAbs. 3“. Ob dort ein UAbs. 2 fehlt oder die Zählung falsch ist, ist offen. Alle Zeilen `out` – es geht um Kennungen, nicht um Befunde | a) **ich prüfe am amtlichen Text und berichtige**, du bestätigst die Kennungen · b) so lassen | |

# Teil 2 – B: Zeilen bestätigen

## IN-1 – 42 `in`-Zeilen offen (bestätigt: 67 von 109)

**Gruppe 1 – nicht einschlägig (32):** Definitionen, Einstufung nach Art. 6, Geltungsbeginn, Verbote-Einleitung. Vorschlag: Sammelbestätigung nach P4-B1.

| Raum | Kennung | Befund | Gate | Pflicht (kurz) |
|---|---|---|---|---|
| AI Act | Art. 2 Abs. 1 lit. b | n.e. | – | Erfasst Betreiber von KI-Systemen mit Sitz oder Standort in der Union. |
| AI Act | Art. 3 Nr. 4 | n.e. | – | Definiert Kernbegriffe Nr. 1-44 der Verordnung (u.a. KI-System, Risiko, Anbieter, Betreiber, Bevollmaechtigte… |
| AI Act | Art. 3 Nr. 8 | n.e. | – | Definiert Kernbegriffe Nr. 1-44 der Verordnung (u.a. KI-System, Risiko, Anbieter, Betreiber, Bevollmaechtigte… |
| AI Act | Art. 3 Nr. 23 | n.e. | – | Definiert Kernbegriffe Nr. 1-44 der Verordnung (u.a. KI-System, Risiko, Anbieter, Betreiber, Bevollmaechtigte… |
| AI Act | Art. 3 Nr. 49 | n.e. | – | Teil der Definition 'Strafverfolgungsbehoerde', Variante b) (sonstige mit hoheitlichen Befugnissen betraute S… |
| AI Act | Art. 6 Abs. 2 | n.e. | – | Zusaetzlich zu Abs. 1 gelten auch die in Anhang III genannten KI-Systeme als hochriskant (Grundlage der Einst… |
| AI Act | Art. 6 Abs. 3 | n.e. | – | Ein in Anhang III genanntes System gilt abweichend NICHT als hochriskant, wenn es kein erhebliches Risiko bir… |
| AI Act | Art. 6 Abs. 3 lit. a | n.e. | – | Ausnahme a): das System fuehrt eine eng gefasste Verfahrensaufgabe durch. |
| AI Act | Art. 6 Abs. 3 lit. b | n.e. | – | Ausnahme b): das System verbessert das Ergebnis einer bereits abgeschlossenen menschlichen Taetigkeit. |
| AI Act | Art. 6 Abs. 3 lit. c | n.e. | – | Ausnahme c): das System erkennt Entscheidungsmuster/Abweichungen, ohne die menschliche Bewertung ohne Ueberpr… |
| AI Act | Art. 6 Abs. 3 lit. d | n.e. | – | Ausnahme d): das System fuehrt eine vorbereitende Aufgabe fuer eine Anhang-III-relevante Bewertung durch. |
| AI Act | Art. 6 Abs. 3 UAbs. 3 | n.e. | – | Ungeachtet des UAbs. 1 gilt ein Anhang-III-System immer als hochriskant, wenn es ein Profiling natuerlicher P… |
| AI Act | Art. 15 Abs. 4 UAbs. 2 Satz 1 | n.e. | – | Robustheit kann durch technische Redundanz erreicht werden, auch durch Sicherungs- oder Stoerungssicherheitsp… |
| AI Act | Art. 113 Abs. 2 | n.e. | – | Die Verordnung gilt ab dem 2. August 2026, soweit Abs. 3 nichts anderes bestimmt. |
| AI Act | Art. 113 Abs. 3 | n.e. | – | Einleitung der Ausnahmen vom Geltungsbeginn nach Abs. 2 (lit. a-d). |
| AI Act | Anhang III | n.e. | – | Einleitung der Liste: Als Hochrisiko-KI-Systeme nach Art. 6 Abs. 2 gelten die in den folgenden Bereichen aufg… |
| AI Act | Anhang III Nr. 2 | n.e. | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 3 Nr. 14 n.F. | n.e. | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 4a Abs. 2 n.F. | n.e. | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 4a Abs. 2 lit. a n.F. | n.e. | – | Bedingung der Erlaubnis nach Art. 4a Abs. 2 n.F.: eine solche Verarbeitung zur Erkennung und Korrektur von Ve… |
| Omnibus | Art. 4a Abs. 2 lit. b n.F. | n.e. | – | Bedingung der Erlaubnis nach Art. 4a Abs. 2 n.F.: alle in Absatz 1 genannten Bedingungen und Vorkehrungen Anw… |
| Omnibus | Art. 4a Abs. 2 UAbs. 2 n.F. | n.e. | – | Art. 4a Abs. 2 begruendet keine Verpflichtung, Verzerrungen zu erkennen und zu korrigieren. |
| Omnibus | Art. 5 Abs. 1a n.F. | n.e. | – | Einleitung: Konkretisierung der Verbote Art. 5 Abs. 1 UAbs. 1 lit. ba und bb n.F. |
| Omnibus | Art. 5 Abs. 1a lit. b n.F. | n.e. | – | Die Verwendung ist nur verboten, wenn der Betreiber das System zur Erzeugung oder Manipulation solchen Materi… |
| Omnibus | Art. 5 Abs. 1b n.F. | n.e. | – | Fuer lit. ba gilt ein System, das die Sichtbarkeit intimer Koerperteile nicht erhoeht und die Art der dargest… |
| Omnibus | Art. 6 Abs. 1a n.F. | n.e. | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 6 Abs. 1b n.F. | n.e. | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 6 Abs. 1c n.F. | n.e. | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 25 Abs. 2 UAbs. 4 n.F. | n.e. | G-OPS-06 | Ausnahme: Die Kooperations- und Uebergabepflicht entfaellt, wenn der Erstanbieter eindeutig festgelegt hat, d… |
| Omnibus | Art. 113 Abs. 3 lit. a n.F. | n.e. | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 113 Abs. 3 lit. c n.F. | n.e. | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 113 Abs. 3 lit. c Ziff. i n.F. | n.e. | – | ⚠ kein Pflichttext (P4-B1) |

**Gruppe 2 – Teilabdeckung und Lücke (10):** einzeln. Art. 26 Abs. 11 hängt an Q11, Art. 111 Abs. 2 Satz 2 n.F. an S3-1; Art. 15 Abs. 3 und Abs. 4 UAbs. 1 stehen in der Element-Matrix unter Vorbehalt F4.

| Raum | Kennung | Befund | Gate | Pflicht (kurz) |
|---|---|---|---|---|
| AI Act | Art. 15 Abs. 1 | Teil | G-PRE-04, G-DEP-02, G-OPS-04 | Hochrisiko-KI-Systeme werden so konzipiert und entwickelt, dass sie ein angemessenes Mass an Genauigkeit, Rob… |
| AI Act | Art. 15 Abs. 3 | Teil | G-DEP-03 | Die Genauigkeitsmasse und relevanten Genauigkeitsmetriken von Hochrisiko-KI-Systemen werden in den beigefuegt… |
| AI Act | Art. 15 Abs. 4 UAbs. 1 Satz 1 | Teil | G-DEP-02, G-OPS-04 | Hochrisiko-KI-Systeme muessen so widerstandsfaehig wie moeglich gegenueber Fehlern, Stoerungen oder Unstimmig… |
| AI Act | Art. 15 Abs. 4 UAbs. 1 Satz 2 | Teil | G-DEP-02, G-OPS-04 | Dazu sind technische und organisatorische Massnahmen zu ergreifen. |
| AI Act | Art. 15 Abs. 4 UAbs. 3 Satz 1 | Lücke | – | Weiterlernende Hochrisiko-KI-Systeme sind so zu entwickeln, dass das Risiko verzerrter Ausgaben durch Rueckko… |
| AI Act | Art. 15 Abs. 5 | Teil | G-OPS-04 | Hochrisiko-KI-Systeme muessen widerstandsfaehig gegen Manipulationsversuche unbefugter Dritter sein; die tech… |
| AI Act | Art. 26 Abs. 11 | Teil | G-DEP-03 | Unbeschadet Art. 50 informieren Betreiber der in Anhang III aufgefuehrten Hochrisiko-KI-Systeme, die Entschei… |
| Omnibus | Art. 5 Abs. 1 UAbs. 1 lit. ba n.F. | Lücke | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 5 Abs. 1 UAbs. 1 lit. bb n.F. | Lücke | – | ⚠ kein Pflichttext (P4-B1) |
| Omnibus | Art. 111 Abs. 2 Satz 2 n.F. | Lücke | – | Anbieter und Betreiber von Hochrisiko-KI-Systemen, die bestimmungsgemaess von Behoerden verwendet werden soll… |

| ID | Frage | Optionen | Antwort |
|---|---|---|---|
| IN-1 | Bestätigen? | a) **Gruppe 1 gesammelt** (nach den neuen Texten aus P4-B1), Gruppe 2 einzeln mit Q11 und S3-1 · b) alle 42 einzeln | |

## S3-2 – Unterglieder entschiedener Normen

| Raum | Kennung | Scope | Verifikation | bestätigt | Wortlaut (Anfang) |
|---|---|---|---|---|---|
| AI Act | Art. 3 Nr. 49 | in | – | nein | 49. „schwerwiegender Vorfall“ einen Vorfall oder eine Fehlfunktion bezüglich eines KI-Sys… |
| AI Act | Art. 3 Nr. 49 lit. a | out | VERIFIZIERT | nein | a) den Tod oder die schwere gesundheitliche Schädigung einer Person; |
| AI Act | Art. 3 Nr. 49 lit. b | out | VERIFIZIERT | nein | b) eine schwere und unumkehrbare Störung der Verwaltung oder des Betriebs kritischer Infr… |
| AI Act | Art. 3 Nr. 49 lit. c | out | VERIFIZIERT | nein | c) die Verletzung von Pflichten aus den Unionsrechtsvorschriften zum Schutz der Grundrech… |
| AI Act | Art. 3 Nr. 49 lit. d | out | VERIFIZIERT | nein | d) schwere Sach- oder Umweltschäden; |
| Omnibus | Art. 4a Abs. 2 n.F. | in | – | nein | (2) Anbieter und Betreiber anderer KI-Systeme und KI-Modelle und Betreiber von Hochrisiko… |
| Omnibus | Art. 4a Abs. 2 lit. a n.F. | in | VERIFIZIERT | nein | a) eine solche Verarbeitung zur Erkennung und Korrektur von Verzerrungen im Hinblick auf … |
| Omnibus | Art. 4a Abs. 2 lit. b n.F. | in | VERIFIZIERT | nein | b) alle in Absatz 1 genannten Bedingungen und Vorkehrungen Anwendung finden. |
| Omnibus | Art. 4a Abs. 2 UAbs. 2 n.F. | in | VERIFIZIERT | nein | Dieser Absatz begründet keine Verpflichtung, eine solche Erkennung und Korrektur von Verz… |
| Omnibus | Art. 113 Abs. 3 lit. c Ziff. ii n.F. | out | VERIFIZIERT | nein | ii) 2. August 2028 in Bezug auf KI-Systeme, die gemäß Artikel 6 Absatz 1 und Anhang I als… |

| ID | Frage | Optionen | Antwort |
|---|---|---|---|
| S3-2 | Folgen die Unterglieder ihrer Norm? | a) **Art. 3 Nr. 49 lit. a–d wie Nr. 49** (`in`, n.e.). Gemessen: G-OPS-02 (C-02, C-03) stützt seine Meldeschwelle auf **lit. c** (Grundrechte), weil Art. 73 Abs. 9 die Meldepflicht für Anhang-III-Nr.-2-Systeme darauf reduziert – das Gate zitiert also eine Zeile, die heute `out` ist. Lit. b (Störung kritischer Infrastruktur) läuft nach dieser Lesart über CER und NIS2 (HYPOTHESE, gestützt auf den Leitlinien-Entwurf zu Art. 73) · Art. 4a Abs. 2 lit. a/b n.F. bestätigen wie sie stehen · Art. 113 Abs. 3 lit. c Ziff. ii n.F. bleibt `out` (Anhang-I-Systeme, nicht Redispatch) · b) alles bleibt, wie es steht | |

## S3-3 – Verifikationsstufe fehlt (23 `in`-Zeilen, gemessen; Register sagte 12 + 10)

- AI Act (13): Art. 2 Abs. 1 lit. b · Art. 3 Nr. 4 · Art. 3 Nr. 8 · Art. 3 Nr. 23 · Art. 3 Nr. 49 · Art. 6 Abs. 2 · Art. 6 Abs. 3 · Art. 6 Abs. 3 lit. a · Art. 6 Abs. 3 lit. b · Art. 6 Abs. 3 lit. c · Art. 6 Abs. 3 lit. d · Art. 6 Abs. 3 UAbs. 3 · Anhang III Nr. 2
- Omnibus (10): Art. 3 Nr. 14 n.F. · Art. 4a Abs. 2 n.F. · Art. 5 Abs. 1 UAbs. 1 lit. ba n.F. · Art. 5 Abs. 1 UAbs. 1 lit. bb n.F. · Art. 6 Abs. 1a n.F. · Art. 6 Abs. 1b n.F. · Art. 6 Abs. 1c n.F. · Art. 113 Abs. 3 lit. a n.F. · Art. 113 Abs. 3 lit. c n.F. · Art. 113 Abs. 3 lit. c Ziff. i n.F.

| ID | Frage | Optionen | Antwort |
|---|---|---|---|
| S3-3 | Wer setzt die Stufe? | a) **ich schlage je Zeile VERIFIZIERT oder HYPOTHESE vor, mit Begründung am Wortlaut**; du bestätigst gesammelt · b) du setzt je Zeile | |

## S3-4 – Hypothesen gegen Sekundärquellen (47 `in`-Zeilen)

- AI Act (42): Art. 9 Abs. 5 lit. c · Art. 13 Abs. 1 · Art. 13 Abs. 2 · Art. 13 Abs. 3 · Art. 13 Abs. 3 lit. a · Art. 13 Abs. 3 lit. b · Art. 13 Abs. 3 lit. b Ziff. i · Art. 13 Abs. 3 lit. b Ziff. ii · Art. 13 Abs. 3 lit. b Ziff. iii · Art. 13 Abs. 3 lit. b Ziff. iv · Art. 13 Abs. 3 lit. b Ziff. v · Art. 13 Abs. 3 lit. b Ziff. vi · Art. 13 Abs. 3 lit. b Ziff. vii · Art. 13 Abs. 3 lit. c · Art. 13 Abs. 3 lit. d · Art. 13 Abs. 3 lit. e · Art. 13 Abs. 3 lit. f · Art. 14 Abs. 1 · Art. 14 Abs. 2 · Art. 14 Abs. 3 · Art. 14 Abs. 3 lit. a · Art. 14 Abs. 3 lit. b · Art. 14 Abs. 4 · Art. 14 Abs. 4 lit. a · Art. 14 Abs. 4 lit. b · Art. 14 Abs. 4 lit. c · Art. 14 Abs. 4 lit. d · Art. 14 Abs. 4 lit. e · Art. 15 Abs. 1 · Art. 15 Abs. 3 · Art. 15 Abs. 4 UAbs. 1 Satz 1 · Art. 15 Abs. 4 UAbs. 1 Satz 2 · Art. 15 Abs. 4 UAbs. 2 Satz 1 · Art. 15 Abs. 4 UAbs. 3 Satz 1 · Art. 15 Abs. 5 · Art. 73 Abs. 1 · Art. 73 Abs. 2 UAbs. 1 Satz 1 · Art. 73 Abs. 2 UAbs. 2 Satz 1 · Art. 73 Abs. 3 · Art. 73 Abs. 4 · Art. 73 Abs. 9 · Art. 79 Abs. 2
- Omnibus (5): Art. 25 Abs. 2 n.F. · Art. 25 Abs. 2 lit. a n.F. · Art. 25 Abs. 2 lit. b n.F. · Art. 25 Abs. 2 lit. c n.F. · Art. 25 Abs. 2 UAbs. 4 n.F.

| ID | Frage | Optionen | Antwort |
|---|---|---|---|
| S3-4 | Gegen welche Quellen? | a) **Leitlinien der Kommission und deine Zotero-Bibliothek;** ich schlage je Zeile „verifiziert“ oder „bleibt HYPOTHESE“ mit Fundstelle vor, du bestätigst · b) nur Leitlinien der Kommission | |

# Teil 3 – C: `out`-Stichprobe (OUT-1)

- **1268 `out`-Zeilen offen** (bestätigt: 139 von 1407): Behörde 599 · Anbieter 356 · Sonstige 304 · **Betreiber 9**.
- **Betreiber (9): jede einzeln** – dein Adressat.
- **Übrige Gruppen:** 10 Zeilen je Gruppe, zufällig gezogen (Seed 20261002, wiederholbar). Ohne Fehler → Sammelbestätigung der Gruppe. Ein Fehler → ich sehe die Gruppe ganz durch, dann neue Stichprobe.

## Betreiber (9)

| Raum | Kennung | Grund für out (kurz) |
|---|---|---|
| AI Act | Art. 2 Abs. 10 | Bereichsausnahme fuer den privaten/nicht-beruflichen Betreiber, schliesst diese Gruppe von der Verordnung aus; der Anwendungsfall… |
| AI Act | Art. 26 Abs. 3 | Unberuehrtheits-/Verhaeltnisbestimmungsklausel ohne eigenstaendigen, pruefbaren Regelungsgehalt - sie begruendet keine zusaetzlic… |
| AI Act | Anhang VIII Abschn. C | Bereichsausnahme und Adressat wie Art. 49 Abs. 3 (PO 23.09.2026, 2a Gruppe A): Registrierung durch Betreiber, die Behoerden sind,… |
| AI Act | Anhang VIII Abschn. C Nr. 1 | Bereichsausnahme und Adressat wie Art. 49 Abs. 3 (PO 23.09.2026, 2a Gruppe A): Registrierung durch Betreiber, die Behoerden sind,… |
| AI Act | Anhang VIII Abschn. C Nr. 2 | Bereichsausnahme und Adressat wie Art. 49 Abs. 3 (PO 23.09.2026, 2a Gruppe A): Registrierung durch Betreiber, die Behoerden sind,… |
| AI Act | Anhang VIII Abschn. C Nr. 3 | Bereichsausnahme und Adressat wie Art. 49 Abs. 3 (PO 23.09.2026, 2a Gruppe A): Registrierung durch Betreiber, die Behoerden sind,… |
| AI Act | Anhang VIII Abschn. C Nr. 4 | Bereichsausnahme und Adressat wie Art. 49 Abs. 3 (PO 23.09.2026, 2a Gruppe A): Registrierung durch Betreiber, die Behoerden sind,… |
| AI Act | Anhang VIII Abschn. C Nr. 5 | Bereichsausnahme und Adressat wie Art. 49 Abs. 3 (PO 23.09.2026, 2a Gruppe A): Registrierung durch Betreiber, die Behoerden sind,… |
| Omnibus | Art. 27 Abs. 4 n.F. | Bereichsausnahme (T-13 Schritt 2): Art. 27 Abs. 1 nimmt Anhang-III-Nr.-2-Systeme aus; Abs. 4 setzt die Pflicht aus Abs. 1 voraus … |

## Stichprobe je Gruppe

### behoerde (599 offen, 10 gezogen)
| Raum | Kennung | Grund für out (kurz) |
|---|---|---|
| AI Act | Art. 41 Abs. 1 UAbs. 3 | Voraussetzung und Verfahrenspflicht der Kommission, keine Betreiberpflicht. |
| AI Act | Art. 56 Abs. 9 | Die Regelung betrifft eine Handlungs- oder Aufsichtspflicht der Kommission, des Buero fuer Kuenstliche Intelligenz, des KI-Gremiu… |
| AI Act | Art. 57 Abs. 16 | Die Regelung betrifft eine Handlungs- oder Aufsichtspflicht der Kommission, des Buero fuer Kuenstliche Intelligenz, des KI-Gremiu… |
| AI Act | Art. 73 Abs. 7 | Behoerden-/Kommissionspflicht (Weiterleitung, Leitlinienerstellung), keine Betreiberpflicht. |
| AI Act | Art. 79 Abs. 5 | Regelt das behoerdliche Verfahren zum Umgang mit risikobehafteten oder nicht konformen KI-Systemen; keine Betreiberpflicht. |
| AI Act | Art. 91 Abs. 3 | Regelt Aufsichts- und Durchsetzungsbefugnisse des Buero fuer Kuenstliche Intelligenz bzw. der Kommission gegenueber Anbietern von… |
| AI Act | Art. 96 Abs. 1 lit. c | Adressiert behoerde, keine Betreiber-Handlungspflicht. |
| AI Act | Art. 99 Abs. 7 lit. h | Adressiert behoerde, keine Betreiber-Handlungspflicht. |
| Omnibus | Art. 60a Abs. 5 n.F. | Systemtyp (T-13 Schritt 2b) und Adressat (1): Rahmen der Mitgliedstaaten fuer Tests von Produkten nach Anhang I Abschn. B. Das Re… |
| Omnibus | Art. 75a Abs. 8 n.F. | Adressat (T-13 Schritt 1): KI-Buero und Marktueberwachungsbehoerden (Zustaendigkeit, Befugnisse, Verfahren, Sanktionen). Gilt nur… |

### anbieter (356 offen, 10 gezogen)
| Raum | Kennung | Grund für out (kurz) |
|---|---|---|
| AI Act | Anhang IV Nr. 2 lit. c | Adressat (T-13 Schritt 1): Inhalt der technischen Dokumentation nach Art. 11 Abs. 1, die der Anbieter erstellt und der Behoerde v… |
| AI Act | Anhang V Nr. 1 | Adressat (T-13 Schritt 1): Inhalt der EU-Konformitaetserklaerung nach Art. 47, die der Anbieter ausstellt; Art. 47 ist out. G-DEP… |
| AI Act | Anhang XI Abschn. 1 Nr. 1 lit. b | Adressat (T-13 Schritt 1): Anbieter von KI-Modellen mit allgemeinem Verwendungszweck (Art. 53, Abschn. 2 zusaetzlich Art. 55); Ar… |
| AI Act | Anhang XI Abschn. 1 Nr. 1 lit. d | Adressat (T-13 Schritt 1): Anbieter von KI-Modellen mit allgemeinem Verwendungszweck (Art. 53, Abschn. 2 zusaetzlich Art. 55); Ar… |
| AI Act | Art. 43 Abs. 1 UAbs. 1 lit. b | Verfahrenspflicht des Anbieters, keine Betreiberpflicht. |
| AI Act | Art. 53 Abs. 1 lit. b Ziff. ii | Die Pflicht richtet sich an den Anbieter bzw. kuenftigen Anbieter des KI-Modells oder KI-Systems und nicht an den Betreiber im Si… |
| AI Act | Art. 55 Abs. 1 lit. a | Die Pflicht richtet sich an den Anbieter bzw. kuenftigen Anbieter des KI-Modells oder KI-Systems und nicht an den Betreiber im Si… |
| AI Act | Art. 8 Abs. 2 | Anbieterpflicht (Kapitel III Abschnitt 2 i.V.m. Art. 16 lit. a); allgemeine Chapeau-Norm zu Abschnitt 2 ohne im Wortlaut erkennba… |
| AI Act | Art. 83 Abs. 1 lit. c | Betrifft eine Mitwirkungs- bzw. Korrekturpflicht des Anbieters gegenueber der Marktueberwachungsbehoerde, nicht des Betreibers. |
| Omnibus | Art. 25 Abs. 4 UAbs. 1 n.F. | Adressat (T-13 Schritt 1): Verhaeltnis Anbieter - Dritter (Zulieferer); wie Art. 25 Abs. 4 der Grundfassung. Den Betreiber trifft… |

### sonstige (304 offen, 10 gezogen)
| Raum | Kennung | Grund für out (kurz) |
|---|---|---|
| AI Act | Anhang VII Nr. 5.3 | Adressat (T-13 Schritt 1): Verfahren zwischen Anbieter und notifizierter Stelle nach Art. 43 Abs. 1; Art. 43 ist out. Fuer Anhang… |
| AI Act | Anhang X Nr. 1 lit. a | Systemtyp (T-13 Schritt 2b): KI-Komponenten der EU-IT-Grosssysteme (Schengen, VIS, Eurodac, EES, ETIAS, ECRIS-TCN), fuer die Art.… |
| AI Act | Art. 1 Abs. 2 lit. g | Zweckbestimmungs-/Inhaltsuebersichtsnorm (Art. 1) - keine Handlungspflicht fuer einen Akteur, insbesondere keine Betreiberpflicht… |
| AI Act | Art. 23 Abs. 1 lit. a | Einfuehrerpflicht (Art. 23) - eigenstaendiger Akteur in der Lieferkette, keine Betreiber-Handlungspflicht. |
| AI Act | Art. 3 Nr. 15 | Begriffsbestimmung (Art. 3) - definiert Rechtsbegriffe der Verordnung, begruendet selbst keine Handlungspflicht fuer einen Akteur. |
| AI Act | Art. 3 Nr. 19 | Begriffsbestimmung (Art. 3) - definiert Rechtsbegriffe der Verordnung, begruendet selbst keine Handlungspflicht fuer einen Akteur. |
| AI Act | Art. 3 Nr. 34 | Begriffsbestimmung (Art. 3) - definiert Rechtsbegriffe der Verordnung, begruendet selbst keine Handlungspflicht fuer einen Akteur. |
| AI Act | Art. 3 Nr. 36 | Begriffsbestimmung (Art. 3) - definiert Rechtsbegriffe der Verordnung, begruendet selbst keine Handlungspflicht fuer einen Akteur. |
| AI Act | Art. 3 Nr. 43 | Begriffsbestimmung (Art. 3) - definiert Rechtsbegriffe der Verordnung, begruendet selbst keine Handlungspflicht fuer einen Akteur. |
| AI Act | Art. 54 Abs. 3 lit. d | Die Pflicht richtet sich an den vom Anbieter benannten Bevollmaechtigten und nicht an den Betreiber im Sinne der Verordnung. |

| ID | Frage | Optionen | Antwort |
|---|---|---|---|
| OUT-1 | Stichprobe so? | a) **10 je Gruppe**, Betreiber vollständig · b) 20 je Gruppe | |

# Teil 4 – Befund

| # | Befund | Wohin |
|---|---|---|
| P4-B1 | **`in`-Zeilen ohne eigenen Pflichttext:** 11 ohne Text (Anhang III Nr. 2; Omnibus Art. 3 Nr. 14, Art. 4a Abs. 2, Art. 5 Abs. 1 UAbs. 1 lit. ba/bb, Art. 6 Abs. 1a–1c, Art. 113 Abs. 3 lit. a, lit. c, lit. c Ziff. i n.F.), 12 mit Sammeltext in vier Gruppen (Art. 3 Nr. 4/8/23 · Art. 5 Abs. 1 lit. c Ziff. i/ii · Art. 13 Abs. 3 lit. b Ziff. i–iv · Ziff. v–vii). Bestätigt werden kann nur, was dasteht. Vorschlag: Texte neu, Wächter „jede `in`-Zeile hat einen eigenen Pflichttext“, Sammelbestätigung der Texte wie P3-F5 | 4 |
