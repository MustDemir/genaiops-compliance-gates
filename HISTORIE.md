# Historie — Begründungen, Befunde und Revidiertes

**Zum Handbuch gehörend · Stand 25. August 2026**
Projekt „Cloud Architect AI Governance" · Mustafa Demir

---

## Wozu diese Datei

`HANDBUCH.md` sagt, **was gilt**. Diese Datei sagt, **warum es gilt** — und was einmal galt und nicht mehr gilt.

Der Schnitt entstand am 25.08.2026, weil das Handbuch monoton wuchs (v0.4: 929 Zeilen, v0.5: 1016, v0.6: 1205) und damit als Einstiegskontext für eine Arbeitssitzung untauglich wurde. Die alte Pflegeregel „Fortschreibung statt Neufassung **in einer Datei**" ist damit aufgehoben. Was bleibt, ist ihr Kern:

> **Nichts wird gelöscht. Revidiertes bleibt sichtbar. Die Begründungskette ist wichtiger als der Endzustand.**

Sie gilt jetzt **für diese Datei**. Das Handbuch darf gekürzt und umgeschrieben werden; die Historie nur ergänzt.

## Wie beide Dateien zusammenhängen

Jede Entscheidung trägt eine stabile ID `D-xx`, jeder Befund eine ID `B-xx`. Das Handbuch nennt die ID und den Einzeiler, diese Datei die Begründung. Wer eine ID sucht, greppt danach — in beiden Dateien.

**Bei Widerspruch zwischen Handbuch und Historie gilt das Handbuch für den *aktuellen Stand*, die Historie für die *Begründung*.** Widersprechen sich die Sachaussagen, ist das ein Fehler und gehört behoben, nicht ausgelegt. `check_handbuch_konsistenz.py` prüft, dass jede ID auf beiden Seiten existiert.

---

# TEIL H1 — Entscheidungsregister mit Begründung

Chronologisch. Status: **gültig** · **revidiert** (mit sichtbarer alter Fassung) · **vertagt**.

| ID | Datum | Entscheidung | Status | Begründung steht in |
|---|---|---|---|---|
| **D-01** | 13.08. | Zeithorizont langfristig/strategisch, kein kurzfristiger Umsatzdruck | gültig | H2 |
| **D-02** | 13.08. | Zielsegment volle Hochrisiko-Anforderungen (Annex III), nicht Art.-50-Transparenz | gültig | H2, H3 |
| **D-03** | 13.08. | Differenzierung über Lifecycle-Vollständigkeit inkl. Retirement | **revidiert** — in D-14 nachrangig gestellt | H2 |
| **D-04** | 14.08. | Masterarbeit ist Ansatzpunkt, nicht SSOT; Anspruch business ready | gültig | Handbuch 2.1 |
| **D-05** | 14.08. | Zielrolle A + C, ausdrücklich nicht B (Produktunternehmen) | gültig | H2 |
| **D-06** | 14.08. | Branche Energie/Kritis, Adressat Netzbetreiber | gültig | H2 |
| **D-07** | 14.08. | Normenpackungen NIS2 Anhang I, AI Act Annex III Nr. 2, ergänzend EnWG § 11 | gültig | H2, H3 |
| **D-08** | 14.08. | Anwendungsfall Redispatch in drei Rollenkonstellationen | gültig | H2 |
| **D-09** | 14.08. | Normenraum-Aufnahmeregel: Prüfbarkeit am KI-Lebenszyklus | gültig | Handbuch 4.1 |
| **D-10** | 14.08. | Evidenz-Ebenen-Modell E6; Gates zunächst flächendeckend auf E-1 als Ziel | gültig | H4 |
| **D-11** | 14.08. | Severity auf Check-Ebene statt Gate-Ebene | gültig, umgesetzt SPEC-01 | H5 |
| **D-12** | 14.08. | Rollen-Scope PROVIDER / DEPLOYER / BOTH als Architekturparameter | gültig, umgesetzt SPEC-03 | H2 |
| **D-13** | 14.08. | Rollenübergangs-Gate erzeugt beidseitige Evidenz | gültig, umgesetzt als G-OPS-06 | H2 |
| **D-14** | 14.08. | Achsen-Reihenfolge Beweiskraft → Befähigung → Lifecycle | gültig | H2 |
| **D-15** | 14.08. | Lizenzwechsel auf Apache 2.0 | gültig, umgesetzt 15.08. (`6319943`) | H5 |
| **D-16** | 14.08. | Zielstack souverän, Open Source, ohne Vendor-Lock-in; Azure-PoC bleibt Funktionsreferenz | gültig | H5 |
| **D-17** | 14.08. | Arbeitsteilung Cowork ↔ Claude Code | gültig | Handbuch 2.5 |
| **D-18** | 14.08. | Healthcare-PoC behalten, um eine Netzbetrieb-Vignette ergänzen | gültig | H5 |
| **D-19** | 14.08. | Richtung A und B beide im Scope, A zuerst; Außenpositionierung offen | gültig | H2 |
| **D-20** | 14.08. | Drei Artefakttypen getrennt; NIS2 und EnWG erzeugen keine eigenen Requirements | gültig | Handbuch 4.2 |
| **D-21** | 14.08. | Crosswalk auf frei zugänglichen Primärquellen verankert, ISO nur als Klauselverweis | gültig | H2 |
| **D-22** | 14.08. | Redispatch zuerst als Ableitungs- und Prüffall; Negativfall zwingend | gültig | H2 |
| **D-23** | 14.08. | Art. 25 lit. c statt lit. b als voraussichtlicher Haupttrigger | Hypothese, gültig | H2 |
| **D-24** | 14.08. | Tag- und Versionierungsfrage vertagt, mit Folgenabgrenzung | **vertagt**, weiterhin offen | H5 |
| **D-25** | 14.08. | Modellanbieter nicht als eigene Zielgruppe | gültig | H2 |
| **D-26** | 15.08. | R013-Bias-Gate bleibt SHOULD | **revidiert eine Neubewertung** — Art. 4a ist Erlaubnis-, keine Pflichtnorm | H5 |
| **D-27** | 20.08. | Reihenfolge: Verdrahtung vor Signatur — erst Herkunft, dann E-1 | gültig, umgesetzt SPEC-04 | H4 |
| **D-28** | 25.08. | `runtime_mode` als gehashtes Feld (Variante C), nicht FAIL und nicht `INCONCLUSIVE` | gültig, umgesetzt Schema v06 | H4 |
| **D-29** | 25.08. | Kubernetes wird verschoben; es kostet nur E-2 | gültig | H4 |
| **D-30** | 25.08. | README ist Doku **und** Positionierung, geschichtet statt ersetzt; Englisch mit zweisprachiger Begriffstabelle | gültig, umgesetzt (`2af04a2`) | H6 |
| **D-31** | 25.08. | Pflegeregel „eine Datei" aufgehoben; Schnitt in Handbuch + Historie | gültig | diese Datei, oben |
| **D-32** | 02.09. | G-OPS-05 wird im signierenden Job ausgewertet, nicht bei den übrigen Gates — der Ort wandert, nicht die Zuständigkeit | gültig | H4.24 |

> **Revidierte Entscheidungen bleiben im Register stehen.** D-03 und D-26 sind die beiden Fälle, in denen eine einmal getroffene Position dem Wortlaut- bzw. Evidenztest nicht standgehalten hat. Sie zu löschen würde den Eindruck erwecken, es habe den Irrtum nie gegeben — und genau der ist der Beleg dafür, dass geprüft wird.

---

# TEIL H2 — Fokus: die Begründungen

## 6.2 Warum diese Wahl

| Kriterium | Maschinenbau | **Energie / Kritis** | Finanz / DORA |
|---|---|---|---|
| Passt auf bestehende Architektur | ✗ Provider-Rollenwechsel, 5 neue Artikelkomplexe | **✓✓ Deployer-Scope bleibt** | ✓ |
| Normenüberlappung | AI Act Annex I + Maschinen-VO + NIS2 Anh. II | **AI Act Annex III Nr. 2 + NIS2 Anh. I + EnWG § 11 + KRITIS** | AI Act Annex III Nr. 5 + DORA |
| Stichtag AI Act | 2028 | **02.12.2027** | 02.12.2027 |
| Besetzungsgrad | mittel | **niedrig** | ✗ hoch besetzt |
| Publikum erreichbar | ✓✓ Südwest | ✓ Südwest | ✗ Frankfurt/Zürich |
| Löst Forschungsanschluss ein | ✗ | **✓ F4 nennt Anhang III Nr. 2 ausdrücklich** | ✗ |

**Die drei ausschlaggebenden Gründe:** Der Deployer-Scope bleibt intakt (ein Netzbetreiber betreibt KI, er baut sie nicht). Die eigene Arbeit nennt Anhang III Nr. 2 in F4 ausdrücklich als nächsten Schritt — geschlossener Bogen statt Themenwechsel. Und die Normenüberlappung ist die dichteste aller Kandidaten.

## 6.6 Der inhaltliche Kern des ersten Beitrags

**Zwei Befunde, die zusammengehören:**

**Erstens — die Rollenverwechslung.** Fachbeiträge zählen regelmäßig Art. 9–15 als „Betreiberpflichten" auf, teils mit „Konformitätsbewertung und CE-Kennzeichnung". Das ist unzutreffend: **Art. 16 lit. a** adressiert Art. 8–15 an den **Anbieter**. Merkformel:

> **Der Anbieter schuldet die Beschaffenheit des Systems. Der Betreiber schuldet die Beschaffenheit der Verwendung.**

Die schärfste Einzelabgrenzung ist **Art. 14 ↔ Art. 26 Abs. 2**: Der Anbieter schuldet die **Gestaltung** (das System muss Aufsicht ermöglichen), der Betreiber die **Besetzung** (Personen mit Kompetenz, Schulung und Befugnis). Ein System mit perfektem Override und einer überforderten Leitstelle erfüllt Art. 26 Abs. 2 nicht.

**Zweitens — die Kopplung von Einstufung und Aufsicht.** Bei Systemen, deren Ausgabe erst über eine menschliche Entscheidung wirksam wird, entscheidet über den Ausfallfolgen-Arm, ob eine **wirksame** Kontrolle dazwischensteht.

> **Damit hängt die Einstufung nach Art. 6 an der Aufsichtsqualität nach Art. 26 Abs. 2.** Je schwächer der Override, desto eher ist das System Sicherheitskomponente und damit Hochrisiko. Wer sich als „kein Hochrisiko" einstuft, **weil** ein Mensch dazwischensteht, schuldet den Nachweis, dass diese Aufsicht wirksam ist.

Das koppelt zwei Fragen, die üblicherweise getrennt behandelt werden — und greift auf ein Gate zurück, das im Bestand bereits existiert (G-OPS-01 mit den Sterz-Bedingungen).

## 6.7 Zwei Richtungen im Artefakt: A und B (neu in v0.2)

| | **Richtung A — Pflichten-Prüfer** | **Richtung B — Lieferanten-Prüfer** |
|---|---|---|
| Frage | Erfülle ich meine eigenen Pflichten? | Kann ich beweisen, dass mein Lieferant geliefert hat, was ich brauche? |
| Blickrichtung | nach innen, eigene Organisation | nach außen, Lieferkette |
| Ansprechpartner | Compliance, IT-Sicherheit | **Einkauf**, Vertragsstelle |
| Umfang | viele Regeln über den Betrieb | wenige Regeln, aber Verwaltung fremder Nachweise |
| Stand | weitgehend gebaut | neu, klein |

**Beschluss: beide, A zuerst.**

**Begründung:** B funktioniert ohne A nicht — ein Lieferantennachweis ist nur gegen die eigenen Pflichten bewertbar. A hat ohne B eine offene Flanke, weil ungeprüft bleibt, ob das, worauf sich der Betreiber stützt, überhaupt existiert. Streng genommen ist B ein Teil von A: ein zusätzliches Prüftor an der Stelle, wo etwas Fremdes ins Haus kommt.

> **AUSDRÜCKLICH OFFEN — Außenpositionierung.** Welcher der beiden Aspekte die Überschrift nach außen trägt (Fachbeitrag, Erstgespräch), ist **nicht** mitentschieden. Das ist eine Positionierungs-, keine Architekturentscheidung, und sie hängt an der Marktrecherche (6.9).

## 6.8 Richtung B: der korrigierte Rechtsanker (neu in v0.2)

**Die Arbeitsannahme war falsch.** Richtung B stützte sich auf Art. 25 Abs. 2 und 4. Die Prüfung des Wortlauts (VO (EU) 2026/1744, deutsche Fassung) ergibt: **Für den reinen Betreiber trägt das nicht.**

- **Art. 25 Abs. 2 n.F.** verpflichtet den **Erstanbieter gegenüber den *neuen Anbietern***. Der Anspruch entsteht erst **nach** einem Rollenübergang.
- **Art. 25 Abs. 4 n.F.** regelt **Anbieter ↔ Drittzulieferer**. Der Betreiber ist nicht Partei.

**Folge: B zerfällt in zwei rechtlich verschiedene Fälle.**

| | **B1 — Betreiber-Fall (K1)** | **B2 — Übergangsfall (K3)** |
|---|---|---|
| Rechtsanker | Art. 13 · Art. 26 Abs. 1, 5, 6, 9 · Art. 47/48/49(1) mittelbar | Art. 25 Abs. 2 lit. a–c · Abs. 4 UAbs. 1 |
| Häufigkeit | **Regelfall** | Ausnahme |
| Prüfgegenstand | Vollständigkeit und Deckung der **Betriebsanleitung** | **Übergabepaket** |

**Der Hebel von B1:** Der Betreiber kann Art. 26 Abs. 1 („Verwendung gemäß Betriebsanleitung") nicht erfüllen, wenn die Anleitung unvollständig ist. Eine lückenhafte Betriebsanleitung ist ein **Compliance-Defekt beim Betreiber**, obwohl der Anbieter ihn verursacht hat.

**Was der Betreiber ausdrücklich nicht bekommt:** die technische Dokumentation nach Art. 11 / Annex IV. Sie ist Anbieterpflicht **gegenüber Behörden**. Ein Gate, das sie vom Betreiber verlangt, prüft eine Pflicht, die es nicht gibt.

**Der schärfste Einzelfund — die Opt-out-Klausel.** Art. 25 Abs. 2 n.F. gilt nicht, wenn der Erstanbieter „eindeutig festgelegt hat, dass sein KI-System nicht in ein Hochrisiko-KI-System umgewandelt werden darf". Der Anbieter kann sich die Kooperationspflicht also **einseitig und vorab wegbedingen**.

> **Das verschiebt den Prüfzeitpunkt.** Die entscheidende Prüfung findet **vor Vertragsschluss** statt, nicht in der Deployment-Pipeline. Ein Gate, das das erst beim Rollout meldet, meldet es zu spät. Der größte Hebel von B liegt damit in einer **Beschaffungs-Checkliste** — publizierbar, zitierbar, passend zur Zielrolle A.

Details, Formate und E6-Einordnung: `architecture/lieferanten-evidenz.md`.

## 6.9 Warum der Netzbetreiber in der Betreiberrolle bleibt (neu in v0.2)

Die Rollenzuordnung des Artefakts hängt an einer Annahme über die Praxis: bezieht ein Netzbetreiber seine Prognose- und Redispatch-Modelle zu, oder baut er sie selbst?

**HYPOTHESE (nicht belegt):** Der Regelfall ist der Zukauf in einer Form, die den Netzbetreiber in der **Deployer-Rolle** hält. Eine öffentliche Zahl zu Make-or-Buy existiert nicht; die Einstufung ist damit begründet, aber nicht belegt, und wird als Hypothese geführt (2.3).

**Was daraus für den Katalog folgt:** Ist Zukauf der Regelfall, ist **Art. 25 lit. c (Zweckänderung)** der voraussichtliche Haupttrigger des Rollenübergangs, nicht lit. b (wesentliche Veränderung) — wer ein Modell nicht selbst verändert, kann es zweckentfremden. Genau das prüft C-25c in G-OPS-06, und genau deshalb wertet dieser Check die Klassifikationsregel aus G-PRE-01 zweimal aus: einmal vor, einmal nach der Zweckangabe.

**Die Gegenprobe fehlt.** Träfe die Hypothese nicht zu und bauten Netzbetreiber ihre Modelle selbst, verschöbe sich das Gewicht auf lit. b und auf die Anbieterpflichten aus Art. 16 — der größte offene Block des Katalogs. Die Einstufung ist damit revidierbar und als solche gekennzeichnet.

## 6.10 Crosswalk: der Evidenzweg (neu in v0.2)

**Problem:** ISO/IEC 27001 und 27019 sind kostenpflichtig, der Wortlaut ist urheberrechtlich geschützt. Ein Crosswalk auf ISO-Controls ist für Leser ohne die Norm **nicht überprüfbar** — Kollision mit Evidence-First und mit der geplanten Apache-2.0-Veröffentlichung.

| Option | Bewertung |
|---|---|
| Normativ voll belasteter Crosswalk auf Control-Text | **verworfen** — hoher Auditwert, aber nur für Normbesitzer nachprüfbar |
| Reines Struktur-Mapping auf Klauselnummern | **verworfen** — frei publizierbar, aber die Zuordnung wird selbst zur Behauptung |
| **Verankerung auf frei zugänglichen Primärquellen** | **gewählt** |

**Gewählter Weg:** Der Crosswalk wird auf **IT-Sicherheitskatalog BNetzA, NIS2UmsuCG, EnWG und BSI-Veröffentlichungen** verankert — dort wird wörtlich und primärquellenfest gearbeitet. **ISO erscheint nur als Klauselverweis am Rand.** Maximaler überprüfbarer Anteil, kleiner und klar markierter nicht überprüfbarer Anteil. Passt zum Adressaten, für den der IT-Sicherheitskatalog verbindlich und ISO 27019 nur Umsetzungsebene ist.

---


## 6.5 Der Anwendungsfall: Redispatch

**Warum Redispatch:** Bei Engpassmanagement ist die KI eindeutig Sicherheitskomponente über **beide Arme** der Legaldefinition — die Zweckbestimmung ist die Verhinderung von Überlastung, und die Ausfallfolge gefährdet Betriebsmittel und Versorgung. Keine Abgrenzungsdebatte, die vom Eigentlichen ablenkt.

**Drei Konstellationen, die alle drei Rollenkonfigurationen aktivieren:**

| | Anbieter | Betreiber | Aktive Gate-Menge |
|---|---|---|---|
| **K1** Zukauf | Softwarehaus | Netzbetreiber | `DEPLOYER` |
| **K2** Eigenentwicklung | Netzbetreiber | Netzbetreiber | **`BOTH`** — beide Pflichtenmengen gleichzeitig |
| **K3** Zukauf mit wesentlicher Anpassung | Netzbetreiber nach Aufstieg | Netzbetreiber | Übergang plus Nachweis des Übergangsvorgangs |

**Für die Vignette ist K2 die interessanteste Konstellation**, weil sie beide Rollen im selben Artefakt aktiviert. **Nach dem Marktbefund (6.9) ist K1 aber der Regelfall** — die Vignette muss beides tragen und darf K2 nicht als Normalfall darstellen.

### 6.5.1 Reihenfolge: Vignette vor abstrakter Regel (entschieden in v0.2)

**Redispatch wird zuerst durchgearbeitet — als Ableitungs- und Prüffall, nicht als Gegenstand.** Die Klassifikationsregel wird daraus allgemein formuliert und an Redispatch erstmals validiert.

**Begründung:** Die Klassifikation nach Art. 6 in der Omnibus-Fassung hängt an Systemeigenschaften — Eingriff in die Netzstabilität, Autonomie gegenüber Freigabe durch die Leitstelle. Abstrakt entsteht ein Entscheidungsbaum mit nicht durchentscheidbaren Zweigen und ohne Prüfmöglichkeit.

> **Zwingende Auflage: mindestens ein Negativfall** aus derselben Domäne, der bewusst anders ausgeht. Kandidat: **prädiktive Instandhaltung** — Hypothese: keine Sicherheitskomponente, da kein unmittelbarer Netzeingriff. Ungeprüft. **Ein Entscheidungsbaum, der alles auf „hochrisiko" abbildet, beweist nichts.**

**Abgrenzung anderer Anwendungsfälle** (HYPOTHESE, keine Leitlinien vorhanden):

| Anwendungsfall | Einstufung |
|---|---|
| Engpassmanagement / Redispatch | **Sicherheitskomponente — beide Arme** |
| Netzschutz / Störungserkennung | **Sicherheitskomponente** |
| Lastprognose **mit** halbautomatischer Schalthandlung | **Grenzfall — kippt über den Ausfallfolgen-Arm** |
| Lastprognose **ohne** Schalthandlung | Grenzfall, tendenziell nein |
| Prädiktive Instandhaltung | tendenziell keine — **vorgesehener Negativfall** |
| Chatbot, Abrechnung, Marketing | keine |

## H2.9 „Souverän" — die offene Definitionsentscheidung

> **„Souverän" ist im Projekt bislang undefiniert.** Die Literatur ist sich uneins: Adler-Nissen et al. (2024) identifizieren **sechs unterschiedliche Konzeptionen** von digital sovereignty; Christakis (2020) trennt Souveränität als Regulierungsmacht von strategischer Autonomie. Die Recherchedatei `cloud-sovereignty.md` markiert ausdrücklich: **vor Verwendung im Produktnarrativ ist eine explizite Definitionsentscheidung nötig.** Diese Entscheidung steht aus.

Im Handbuch steht dazu nur der Merksatz (3.5). Die Belegstellen stehen hier, weil sie vor jeder Veröffentlichung gebraucht werden — der Begriff steht im Zielstack-Beschluss (D-16) und trägt damit ein Narrativ, das bislang nicht definiert ist.

---

# TEIL H3 — Normenraum: vollständige Referenz


## 4.3 Vollständige Übersicht der Regelwerke

### Verbindliche Regulierung

| Instrument | Status | Bezug zum Vorhaben |
|---|---|---|
| **EU AI Act — VO (EU) 2024/1689** | in Kraft seit 01.08.2024, gestaffelte Anwendung | Kernregelwerk. Erste Normenpackung. |
| **Digital Omnibus on AI — VO (EU) 2026/1744** | angenommen 08.07.2026, veröffentlicht 24.07.2026, **in Kraft 27.07.2026** | Ändert Fristen und Substanz des AI Act. **VERIFIZIERT gegen EUR-Lex.** |
| **DSGVO — VO (EU) 2016/679** | seit 25.05.2018 voll anwendbar | Datenschicht; koppelt über Art. 4a und Art. 27 Abs. 4 in den AI Act |
| **NIS2 — RL (EU) 2022/2555** | Umsetzungsfrist 17.10.2024 verstrichen | Energie ist **Anhang I** — wesentliche Einrichtungen, höchste Stufe |
| **NIS2UmsuCG (Deutschland)** | **in Kraft seit 06.12.2025, ohne Übergangsfrist**; Registrierungsfrist ~06.03.2026 verstrichen | Direkt anwendbar auf den Zieladressaten |
| **EnWG § 11 Abs. 1a/1b + IT-Sicherheitskatalog BNetzA** | bindend | Verpflichtendes, **zertifiziertes** ISMS nach ISO/IEC 27001 mit ISO/IEC 27019 |
| **KRITIS-Dachgesetz / BSI-KritisV** | soll die IT-Sicherheitskataloge erweitern | Physische Sicherheit; ~4.500 KRITIS-Einrichtungen |
| **Maschinenverordnung (EU) 2023/1230** | vom Omnibus mitgeändert | Annex-I-embedded-Pfad — für die aktuelle Branchenwahl nachrangig |
| **Cyber Resilience Act — VO (EU) 2024/2847** | Pflichten phasen ein | Produkte mit digitalen Elementen; Kandidat für spätere Packung |
| **DORA — VO (EU) 2022/2554** | bindend seit 01/2025 | Nur Finanzsektor. **Verworfen** als Zielsegment. |
| **US CLOUD Act** | — | Rechtskonflikt zur DSGVO; in der Masterarbeit als Limitation L9 offengelegt |

### EU-Zertifizierung und Souveränitätsinitiativen

| Instrument | Status im Projekt |
|---|---|
| **EUCS** (EU Cloud Certification Scheme) | Souveränitätsklauseln durch Verteilungskonflikte zwischen Mitgliedstaaten blockiert (Rone 2024). Noch nicht recherchiert. |
| **GAIA-X** | Adler-Nissen (2024) als Fallstudie; Baur (2025): integriert paradox die US-Provider, die es zurückdrängen sollte |
| **CADA** (Cloud and AI Development Act) | Status ungeprüft, niedrige Priorität |
| **ENISA** | Polemi et al. (2024): ENISA-Ansätze vernachlässigen menschliche Faktoren |

### Management- und Risikostandards (freiwillig)

| Standard | Bedeutung |
|---|---|
| **ISO/IEC 42001** | AI-Management-System, **zertifizierbar**. Komplementär zum AI Act: freiwillig/prozessorientiert/organisationsweit vs. verpflichtend/produktzentriert/risikobasiert (Younas et al. 2026). **Keine Konformitätsvermutung.** |
| **ISO/IEC 27001 + 27019** | Für Netzbetreiber über den BNetzA-Katalog **faktisch verpflichtend**. Anschlusspunkt für die Befähigungsachse. |
| **NIST AI RMF 1.0** | Vier Kernfunktionen Govern / Map / Measure / Manage (Tabassi 2023, 255 Zit.). Freiwillig, sektorunabhängig. |
| **NIST SP 800-53** | Song et al. (2026): automatisierter Crosswalk zu AI-RMF-Funktionen, **98,63% Übereinstimmung mit Experten-Mapping** |
| **ALTAI** | Assessment List for Trustworthy AI; von Golpayegani et al. (2023) formal mit AI Act und ISO 42001 verglichen |
| **AI TRiSM** | Rahmenkonzept Trust/Risk/Security Management (Habbal et al. 2024, **284 Zit. — höchstzitierte Quelle im Korpus**) |

> **Wichtig:** Nur **harmonisierte Standards nach Art. 40 EU AI Act**, im Amtsblatt zitiert, lösen Konformitätsvermutung aus. ISO 42001 und NIST AI RMF tun das **nicht** — sie sind Evidenzgerüst, kein rechtlicher Schutzraum.

### Formate für maschinenlesbare Nachweise (neu in v0.2)

| Format | Stand |
|---|---|
| **CycloneDX ML-BOM** | als **ECMA-424** standardisiert; Modelle, Datensätze, Provenienz, Bias- und Datenintegritätsbetrachtungen |
| **SPDX 3.0 AI Profile / Dataset Profile** | Spezifikation 3.0.1 veröffentlicht; SPDX-Kern ist **ISO/IEC 5962:2021** |
| **in-toto / SLSA / Sigstore** | Signierung und Attestierung — Grundlage für **E-1** |
| **OSCAL** | maschinenlesbarer Evidence-Export (Nweke et al. 2026) |

> **Kein neues Format erfinden.** Der Beitrag liegt in der Zuordnung: welche AI-Act-Pflicht wird durch welches Feld welchen Formats belegt — und auf welcher Evidenz-Ebene.

### Security- und Threat-Frameworks

| Framework | Bedeutung |
|---|---|
| **MITRE ATLAS** | Security-/Threat-Taxonomie, **kein Governance-Framework**. Ergänzt ISO 42001 und NIST AI RMF, ersetzt sie nicht. **Nachweisbare Lücken** bei Agentic- und Foundation-Model-Angriffen (Foundjem et al. 2026; Guemmah et al. 2026). |
| **OWASP LLM Top 10** | Kanabar et al. (2026), kombiniert mit ATLAS |
| **OWASP AI Exchange / GenAI, CSA MAESTRO, NERC CIP** | Bausteine der Unified Reference Architecture bei Rashid et al. (2026) |
| **MIT AI Risk Repository** | 43 Frameworks, 2 Taxonomien, 777 Risiken (Carroll 2025) |
| **AI Incident Database** | Quelle für 12 von 93 Threats bei Foundjem et al. (2026) |

### Policy- und Enforcement-Technologien

| Technologie | Einordnung |
|---|---|
| **OPA / Rego** | De-facto-Industriestandard, breite Kubernetes-Integration. **Im Bestand verwendet.** |
| **Conftest** | CI-Konfigurationstests. **Im Bestand verwendet.** |
| **OPA Gatekeeper** | Kubernetes-Admission-Control. **Im Bestand verwendet.** |
| **Cedar** | AWS, in Lean formal verifiziert. **Einzige direkte Vergleichsstudie (Cutler et al. 2024, POPL, 51 Zit.) sieht Cedar bei Performance und Lesbarkeit vor Rego.** |
| **Kyverno** | Alternative Admission-Control-Engine |
| **XACML, OWL/Rei** | Joshi et al. (2026): deontische Policy-Sprachen für Obligation-Lifecycle |
| **OSCAL** | Maschinenlesbarer Evidence-Export (Nweke et al. 2026, IEEE Access) |
| **in-toto / SLSA / Sigstore** | Signierte Attestierung — Grundlage für **E-1** |
| **Cloud Custodian** | Policy-as-Code in YAML (Pasupuleti 2023) |

## 4.4 Regulatorische Zeitachse

| Datum | Ereignis |
|---|---|
| 02.02.2025 | Art. 4 KI-Kompetenz und Art. 5 Verbote anwendbar |
| 02.08.2025 | GPAI-Pflichten, Governance, Sanktionen anwendbar |
| **06.12.2025** | **NIS2UmsuCG in Kraft — ohne Übergangsfrist** |
| ~06.03.2026 | NIS2-Registrierungsfrist verstrichen |
| **27.07.2026** | **VO (EU) 2026/1744 in Kraft** |
| 02.08.2026 | Art. 50 Transparenz anwendbar |
| 02.12.2026 | Art. 50 Übergang für Bestandssysteme; neue Art.-5-Verbote (NCII/CSAM) |
| 02.08.2027 | Regulatory Sandboxes |
| **02.09.2027** | Art. 72 — Leitlinien mit **freiwilligen** PMS-Templates |
| **02.12.2027** | **Annex III Hochrisiko anwendbar — inkl. Nr. 2 kritische Infrastruktur** |
| 02.08.2028 | Annex I embedded Hochrisiko anwendbar |

> **Zentraler Befund:** Der finale Art. 113 enthält **keinen standards-gekoppelten Konditionaltrigger**. Der Kommissionsvorschlag vom November 2025 hatte die Hochrisiko-Fristen an eine Bereitschaftsbewertung gekoppelt; der verabschiedete Text tut das nicht. **Die Fristen sind unbedingte Kalenderdaten.** Ab 02.12.2027 gilt die volle Annex-III-Pflichtenlast — auch wenn die harmonisierten Standards dann noch nicht fertig sind.

---


---

# TEIL H4 — Befunde aus Analyse und Betrieb


## H4.0 Befundregister

Stabile IDs. Die Abschnittsnummern darunter stammen aus dem Handbuch v0.4–v0.6 und bleiben als Fundstelle erhalten.

| ID | Befund | Fundstelle | Status |
|---|---|---|---|
| **B-01** | Gemessene und geprüfte Werte berühren sich nicht — die App misst, die Gates prüfen eine Handdatei | 7.5 (1) | **behoben** SPEC-04 |
| **B-02** | Die Handdatei widerspricht sich selbst: `accuracy` 0.89 und 0.91 für dieselbe Metrik, kein Gate merkt es | 7.5 (1a) | **behoben** — `gate_result` entfernt |
| **B-03** | Drift-Detektor misst Latenz als Proxy und fällt still auf eine fest kodierte Verteilung zurück | 7.5 (2) | Fallback **behoben**; der Proxy bleibt bewusst |
| **B-04** | G-OPS-03 hatte zwei Erzeuger mit unvereinbarer Logik — der Detektor setzte seine eigene `decision` | 7.5 (2a) | **behoben** — der Detektor misst, Rego entscheidet |
| **B-05** | Die Drift-Annotation ist selbst der E-0-Angriffspunkt: geprüft wird, ob jemand *behauptet*, dass gemessen wird | 7.5 (2b) | **behoben** — C-03/C-04 prüfen die Messung |
| **B-06** | `scribe_mock_mode` existiert und wird von keinem Gate gelesen — PASS im Mock-Betrieb möglich | 7.5 (3) | **behoben** — `runtime_mode` versiegelt (D-28) |
| **B-07** | `policy_checks[].evidence_level` seit SPEC-01 überall `null` — die zweite Achse war gebaut und unbenutzt | 7.5 (3a) | **teilweise** — 10 von 47 Checks tragen einen Wert |
| **B-08** | Acht fehlende Messgrößen für Hochrisiko-Betrieb; Kernlücke ist Genauigkeit ohne Ground Truth | 7.6 | **offen** — der aufwendigste Punkt |
| **B-09** | Histogramm-Buckets fehldimensioniert: der gemeldete p95 war eine Konstante (95 ms bei 0,034 ms echter Latenz) | 7.9 | **behoben** — 1 ms Auflösung |
| **B-10** | Ein Wert kann *gemessen* und trotzdem *informationsfrei* sein — `provenance` beantwortet das nicht | 7.9 | **adressiert** — `latency_p95_resolution` |
| **B-11** | Die in SPEC-04 zugesagte Erzwingung des Messdokuments wurde nicht implementiert | 7.9 | **behoben** SPEC-04b Teil 3.2 (Orchestrator) und H4.19 (CI) |
| **B-12** | Die eigene CI meldet „173/173 green" bei 187 gelaufenen Tests — hartkodiert, gegen nichts gehalten | 7.10 | **behoben** SPEC-04b Teil 1 |
| **B-13** | **Außendarstellung überholt den Gate-Stand.** Ein Entwurf zu G-OPS-02 beschreibt Incident-Erzeugung, Eskalationskaskade und Fristenuhr — das Gate prüft drei Pod-Annotationen bei der Zulassung | H4.13 | **offen** — Gate-Stand, nicht Text |
| **B-14** | **Vier G-OPS-Gates feuern bei Admission, ihr Requirement verlangt Laufzeit.** Ein einmaliger Zulassungscheck kann „kontinuierlich" nicht erfüllen | H4.14 | **deklariert** — 8 von 9 Laufzeitpflichten als `declared_gap` |
| **B-15** | **37 `acceptance_criteria` in den Requirements, von nichts gelesen.** Das Requirement nennt seine eigene Definition of Done, und der Katalog hält seine Gates nie dagegen | H4.16 | **behoben** — `ACCEPTANCE_CRITERIA_TRACED` |
| **B-16** | **Der Orchestrator ist fail-open auf dem Evidenzpfad.** `record_to_evidence_store()` liefert einen Rückgabewert, den niemand auswertet — ein Gate kann PASS melden, ohne dass sein Nachweis geschrieben wurde | H4.17 | **behoben** — fail-closed, Exit 3 |
| **B-18** | **Der einzige E-1-Check im Katalog erfüllt die E-1-Definition nicht.** G-OPS-05/C-02 stuft die Hash-Kette als E-1 ein; E-1 verlangt Signatur *und* geprüfte Erzeuger-Identität. Die Kette hat keine Signatur, `inserted_by` ist eine selbstgewählte Zeichenkette, und die Fälschungskosten sind Schreibzugriff, nicht CI-Kompromittierung. In der CI überlebt die Kette den Lauf zudem nicht — die Datenbank liegt in `/tmp` und wird nirgends hochgeladen | H4.21 | **teilbehoben** — Einstufung am 01.09.2026 auf E-0 zurueckgenommen (SPEC-05 Teil 1); Signatur und Artefakt-Upload offen, SPEC-05 Teil 2-6 |
| **B-17** | **Die Anwesenheitspflicht galt überall außer in der CI.** SPEC-04b Teil 3.2 erzwang `required_inputs` im Orchestrator; die CI fährt den Orchestrator nicht, und der Integrity-Check prüfte nur den Orchestrator — beide grün, drei Tage lang, während G-OPS-02 und G-OPS-03 in der Pipeline ohne ihr Pflichtdokument bestanden | H4.19 | **behoben** — `ci_required_inputs.py`, Check beidseitig gegengeprüft |
| **B-19** | **Die Korrektur von B-18 war selbst eine ungeprüfte Behauptung.** Der Satz „kein Check liegt über E-0" stand ab dem 01.09.2026 an zwei Stellen im README und war beim Schreiben falsch — G-OPS-03/C-03 bis C-05 tragen seit dem Drift-Messteil E-3. `README_COUNTS_CURRENT` prüft Zahlen, keine Aussagen, und sah eine Zeile darüber weg | H4.22 | **behoben** — `README_EVIDENCE_CLAIMS_CURRENT`, beidseitig gegengeprüft |
| **B-20** | **Der Wächter gegen unauffindbare Verweise war selbst einer.** `DOC_REFERENCES_ARE_TRACKED` suchte in Stufe 1 nur im Wurzelverzeichnis und trug für `HANDBUCH.md`/`HISTORIE.md` eine hartkodierte Ausnahme. Ein Verweis auf ein Dokument in einem Unterverzeichnis — oder auf gar keines — lief durch, und der Check meldete grün, ohne geprüft zu haben: dieselbe Struktur wie eine Pod-Annotation, die einen Zustand behauptet statt ihn zu belegen. Beleg: AGENTS.md zeigte weiter auf ein Kandidaten-Dokument, das nur unter `legacy/` liegt und von `.gitignore` ausgeschlossen ist | H4.23 | **behoben** (T-03) — Suche über den ganzen Baum, Pfadverweise, relative Links, beide Verweisformen gegengeprüft |
| **B-21** | **Die CI misst `runtime_mode`, prüft ihn — und reicht ihn beim Aufzeichnen nicht weiter.** `eval_runner.py` liest den Modus aus der laufenden Anwendung, der Workflow bricht ab, wenn dort etwas anderes als `mock` steht — und das Quelldokument des Evidence-Records führt das Feld nicht. `record_evidence.py` fällt daraufhin korrekt auf `unknown` zurück. Es fehlt also eine Übergabe, kein Mechanismus. Seit dem 01.09. steht diese Aussage im signierten Manifest: die Signatur macht den Mangel nicht schlimmer, sie macht ihn **haltbar** | H4.25 | **behoben** (T-08, 02.09.) — der Modus wird durchgereicht und fail-closed erzwungen; Lauf 33632326597 signiert `runtime_mode: "mock"`, alle 17 Records tragen ihn |

> **B-02, B-11, B-12, B-13, B-17, B-18, B-19 und B-20 sind derselbe Fehlertyp** in drei Gewändern: eine Zahl oder ein Urteil wird **geschrieben** statt **gelesen**, und niemand hält sie gegen die Wirklichkeit. B-02 im Gate-Input, B-11 in einer Spezifikationszusage, B-12 in der Pipeline, die das Kontrollsystem prüft, B-13 in der Außendarstellung. Der Typ ist offenbar nicht auf Gate-Inputs beschränkt — er tritt überall dort auf, wo eine Behauptung neben ihrem Gegenstand liegt und niemand sie dagegen hält.
>
> **B-17 zeigt die nächste Stufe:** dort war die Behauptung *behoben* worden, und der Test, der sie hielt, prüfte den falschen Aufrufer. Die Lehre daraus steht in H4.19 — bei jedem neuen Mechanismus ist nicht nur zu fragen, ob er wirkt, sondern **wo überall** er wirken muss.
>
> **B-19 zeigt die Stufe danach:** dort war die Behauptung nicht nur unbewacht, sie entstand *in der Korrektur* einer gleichartigen Behauptung — im selben Commit, der den Fehlertyp benannte. Eine Richtigstellung ist eine Aussage wie jede andere und braucht ihr Gegenstück sofort, nicht beim nächsten Durchgang.
>
> **B-20 schließt den Kreis:** diesmal trug nicht die Behauptung, sondern **der Wächter** den Fehler, gegen den er gebaut war. Ein grüner Check ist damit selbst eine Deklaration — und unterliegt derselben Frage wie jede andere: *woran ist gemessen, dass er misst?* Die Antwort ist die Gegenprobe, und sie muss von beiden Seiten geführt werden: vom Gegenstand her **und** vom Prüfer her.

**B-14 ist ein anderer Typ und deshalb interessanter:** dort widersprechen sich nicht Behauptung und Wirklichkeit, sondern **zwei Deklarationen des eigenen Katalogs**. Das Requirement sagt „Runtime", das Gate sagt „Admission", beide sind eingecheckt, beide gelten — und nichts prüft sie gegeneinander. Ein Widerspruch, den man nur findet, wenn man zwei Dateien nebeneinanderlegt.



## 7.2 Evidenzlage zur Werkzeugwahl

**OPA/Rego ist Marktstandard, aber nicht technisch überlegen.** Cutler et al. (2024, *Proceedings of the ACM on Programming Languages* — POPL, 51 Zit.) vergleichen **Cedar direkt gegen Rego und OpenFGA**: Cedar ist in Lean formal verifiziert, in Rust implementiert, und zeigt bessere Lesbarkeit und **deutlich bessere Performance**. Das ist die **erste belastbare „X schlägt Y"-Evidenz im gesamten Projekt**, aus einer Spitzenvenue.

> **Trade-off, bewusst offen:** OPA hat Ökosystem-Reife und Kubernetes-Durchdringung (Gatekeeper, Conftest); Cedar hat technische Exzellenz bei jüngerem Ökosystem. **Die Entscheidung ist nicht rein technisch zu treffen.** Sie ist offen.

**Policy-as-Code ist selbst fehleranfällig.** Sissodiya et al. (2025, *IEEE Access*, 10 Zit.) modellieren RBAC- und Admission-Policies (explizit inkl. Gatekeeper und Kyverno) als First-Order-Logic und nutzen den SMT-Solver Z3 zur Konflikterkennung **vor** dem Deployment. → **Formale Vor-Verifikation der Policies ist ein bislang übersehener Baustein.**

**OSCAL als Evidence-Exportformat.** Nweke et al. (2026, *IEEE Access*) implementieren die direkteste Entsprechung zum eigenen Stack: OPA/Rego, Conftest, Release-Time-Provenance-Gates und **OSCAL-nativer Evidence-Export** (Component Definition, SSP, Assessment Results, POA&M), ohne relevanten Latenz-Overhead. **Als Architektur-Referenz zu prüfen.**

**Das bislang vollständigste Gate-Modell der Literatur.** Butt et al. (2026, *IEEE Access*, 8 Zit.): „Governance as Evidence for AI Pipelines" — fünf Gates (Data, Training, Validation, Release, Operations), **signierte, tamper-evidente Artefakte**, Clause-to-Artifact-Traceability gegen mehrere Regime gleichzeitig. **Direktes Vergleichsobjekt für das eigene Kernartefakt.**

**Die Grenze des Ansatzes.** Joshi et al. (2026): OPA, Cedar und XACML decken nur das **Permit/Prohibit-Subset** ab. Kein Obligation-Lifecycle-Management, keine Meta-Policy-Konfliktauflösung, keine Dispensationen. Ihr Vorschlag ist eine deontische Policy-Sprache (OWL/Rei), außerhalb des LLM durch eine Logik-Engine ausgewertet.

**Qualitätswarnung zur Literaturlage:** In der ersten Suchrunde zu Policy-as-Code hatten **13 von 20 Treffern null oder eine Zitation**, aus Journalen unklarer Reputation, mit auffällig homogenen „X-as-Code"-Titeln. Zwei Lesarten stehen nebeneinander: schnell wachsendes Praktikerfeld mit hinterherhinkender Qualitätssicherung, oder Publikationsmühlen. **Tier-3-Papers nicht als Einzelevidenz zitieren.**

## 7.5 Messgrößen im Betrieb — Bestandsaufnahme (neu in v0.4)

> **Belegstufe:** Die Bestandsaufnahme unten ist am Code verifiziert (Repo `domain_netzbetrieb`, Stand 20.08.). Die Lückenanalyse in 7.6 ist **fachliche Einschätzung**, keine Normauslegung — der AI Act schreibt Post-Market-Monitoring vor, **nennt aber keine Metriken**.

### Was heute tatsächlich gemessen wird

Die App exportiert drei Metriken (`scenarios/.../app/main.py`), der Drift-Detektor drei weitere:

| Metrik | Quelle | Art |
|---|---|---|
| `scribe_requests_total{endpoint,status}` | App | Counter |
| `scribe_latency_seconds{endpoint}` | App | Histogram |
| `scribe_mock_mode` | App | Gauge |
| `genaiops_drift_psi_score` | Drift-Detektor | berechnet |
| `genaiops_drift_jsd_score` | Drift-Detektor | berechnet |
| `genaiops_drift_status` | Drift-Detektor | 0 ok / 1 warn / 2 critical |

### Drei Befunde, die das Bild korrigieren

**(1) Gemessene und geprüfte Werte berühren sich nicht.**
`eval_results.json` ist eine **Handdatei** (`"model_version": "mock-v1.0.0"`); kein Code erzeugt sie, CI und lokale Pipeline lesen sie nur. Die Latenz, die G-DEP-02 prüft, hat nichts mit `scribe_latency_seconds` zu tun. Es existieren zwei getrennte Welten:

```
App misst → scribe_latency_seconds → Prometheus → Drift-Detektor → PSI → (endet hier)
Gate prüft ← eval_results.json (Handdatei, erfundene Werte)
```

**(1a) Und die Handdatei widerspricht sich selbst.** *(neu in v0.5, gefunden beim Schreiben von SPEC-04)*
`quality_metrics.accuracy` steht auf `0.89`. Weiter unten in derselben Datei behauptet `gate_result.details` für dieselbe Metrik `{"metric": "accuracy", "value": 0.91, "result": "PASS"}`. **Zwei erfundene Werte für dieselbe Größe, die nicht einmal untereinander stimmen.**

Kein Gate merkt es, und das ist der eigentliche Punkt: `policy_safety_metrics.rego` prüft `input.quality_metrics.accuracy` gegen den Schwellenwert und `input.gate_result.all_passed` als eigene Regel — die beiden Pfade werden nie gegeneinander gehalten. Ein Prüfling, der sein eigenes Zeugnis mitbringt, und niemand vergleicht die beiden.

> Das ist die kompakteste Illustration des Gesamtbefunds: **Wo die Zahl nicht erzeugt wird, kann sie nicht einmal mit sich selbst konsistent sein.** `gate_result` entfällt deshalb in SPEC-04 ersatzlos.

**(2) Der Drift-Detektor misst nicht, was draufsteht.**
`load_distribution_from_app()` liest **Latenz-Histogramm-Buckets** und nutzt sie laut eigenem Kommentar als *Proxy* für die Eingabeverteilung. Datendrift nach Art. 72 heißt „die Eingaben ändern sich", gemessen wird „die Antwortzeiten ändern sich". Legitimer PoC-Stellvertreter, aber nicht dasselbe — und die Stelle, an der eine Rückfrage sitzt. Zusätzlich schaltet der Detektor ohne erreichbare App still auf eine fest kodierte Verteilung um; das Ergebnis sieht aus wie eine Messung.

**(2a) KORREKTUR an v0.4 — der Detektor umgeht die Policy-Ebene, statt sie nicht zu erreichen.** *(neu in v0.5)*
v0.4 formulierte, die Drift-Messung „speist heute kein Gate". Das ist zu grob. `record_drift_evidence()` schreibt bereits heute einen Evidence-Record unter `gate_id: "G-OPS-03"` — **mit einer in Python berechneten `decision`** (`"FAIL" if status == "critical" else "PASS"`). Parallel dazu bewertet `policy_monitoring_configured.rego` dasselbe Gate über drei Pod-Annotationen.

**Dieselbe Gate-ID trägt damit Evidenz aus zwei Erzeugern mit unvereinbarer Entscheidungslogik.** Das ist gravierender als eine Lücke: Ein Messwerkzeug, das sein eigenes Ergebnis bewertet, verwischt genau die Trennung, die das Artefakt behauptet — *die Messung liefert den Inhalt, die Regel trifft die Entscheidung* (7.7). Auflösungsregel in SPEC-04: **Der Drift-Detektor misst, er entscheidet nicht.**

**(2b) Die Annotation ist selbst der E-0-Angriffspunkt.** *(neu in v0.5)*
`policy_monitoring_configured.rego` prüft `genaiops.io/drift-detection-enabled == "true"`. Die Frage des Gates lautet „läuft Drift-Erkennung?", geprüft wird „**behauptet jemand**, dass Drift-Erkennung läuft?". Der PSI-Wert, der die Frage beantworten könnte, liegt danebenan und wird nicht gelesen. Das ist die Selbstauskunfts-Angriffsfläche aus Teil 10 an einem konkreten Gate — und zugleich die Stelle, an der sich E-0 und E-3 im selben Gate nebeneinander zeigen lassen.

**(3) `scribe_mock_mode` wird von keinem Gate gelesen.**
Eine Metrik, die sagt „ich tue nur so" — und kein Gate schaut hin. Ein Kontrollsystem, das im Mock-Betrieb PASS meldet, ist die peinlichste denkbare Lücke und in einer Zeile zu schließen.

> **Präzisierung in v0.5:** „In einer Zeile zu schließen" war zu optimistisch. Die Prüfung in jede Policy zu schreiben hieße, sie **17-mal zu duplizieren** — und eine Vorbedingung, die 17-mal dupliziert wird, fehlt irgendwann in einer. Sie gehört eine Stufe davor, in den Orchestrator. Begründung und Entwurf in 7.8.

**(3a) Das Feld für die zweite Achse existiert und ist leer.** *(neu in v0.5)*
SPEC-01 hat `policy_checks[].evidence_level` je Check eingeführt. In **allen** Gate-Definitionen steht dort heute `null`. Die Datenstruktur für die Beweiskraft-Achse ist gebaut, aber unbenutzt — E6 lebt bislang nur auf Gate-Ebene (`evidence_level.current`), nicht dort, wo es hingehört. G-OPS-03 wird nach SPEC-04 der erste Gate mit echten Werten je Check und damit der erste Ort, an dem sich E-0 und E-3 **im selben Gate** vorführen lassen.

### Ungenutzte Live-Signale

Vorhanden oder billig zu holen, speisen aber kein Gate:

| Signal | Quelle | Kandidat-Gate | Stufe |
|---|---|---|---|
| `readyReplicas`, Pod-Zustand | K8s-API via `data.inventory` | G-OPS-03, G-OPS-01 | E-2 |
| Existenz ServiceMonitor / NetworkPolicy | K8s-API | G-OPS-03, G-OPS-04 | E-2 |
| `scribe_requests_total{status="error"}` | Prometheus | G-OPS-02 (Fehlerrate statt Behauptung) | E-3 |
| `scribe_latency_seconds` p95 | Prometheus | G-DEP-02 (echte Latenz statt Handdatei) | E-3 |
| `scribe_mock_mode` | Prometheus | **jedes** Gate als Vorbedingung | E-2 |
| Hash-Chain-Länge, Lücken über Zeit | Evidence Store | G-OPS-05 | E-3 |

Die letzte Zeile ist bemerkenswert: G-OPS-05 fragt „ist die Evidenz vollständig", prüft aber eine Pod-Annotation — die Antwort steht in der eigenen Datenbank.

---

## 7.6 Was an Messung fehlt — Lückenanalyse (neu in v0.4)

### Die Kernlücke: Genauigkeit im Betrieb ist nicht messbar

Kein Versäumnis, sondern **das ungelöste Kernproblem des Feldes**. `accuracy` lässt sich im Betrieb nicht messen, weil die **Wahrheit fehlt**: ohne Labels keine Genauigkeit, nur Stellvertreter. Genau deshalb misst der Drift-Detektor Latenz-Buckets — es ist die einzige labelfreie Größe.

> **Der stärkste eigene Beitrag, der hier möglich ist:** Bei einem Ambient Scribe korrigiert der Arzt die Zusammenfassung ohnehin, bevor er sie freigibt. **Diese Korrektur *ist* das Label.** Wird sie erfasst, entsteht echte Post-Market-Performance.
>
> **Die Aufsicht nach Art. 14 erzeugt beiläufig genau die Daten, die Art. 72 braucht.** Der Mensch, der prüft, produziert die Wahrheit, gegen die gemessen wird. Diese Kopplung ist in keinem bekannten Werkzeug ausgeführt und passt zur bereits gesetzten Kopplung Art. 6 ↔ Art. 26 Abs. 2 (C-A7).

### Die acht Lücken

| # | Lücke | Warum sie zählt |
|---|---|---|
| **1** | **Output- und Konzeptdrift** | Gemessen wird nur (proxy-)Eingabe. Output-Drift ist labelfrei messbar und oft das erste Signal; Konzeptdrift braucht Labels |
| **2** | **Wirksamkeit der Aufsicht** | Override-Rate, Zeit bis Entscheidung, Eskalationen, Verfügbarkeit des Override-Pfads. **Eine Override-Rate nahe null ist ein Alarmsignal, kein Erfolg** — genau das symbolische Mitzeichnen, das Art. 14 verhindern will. Diese Umkehrung ist im Markt kaum abgebildet |
| **3** | **Fairness nur beim Deployment** | R013/G-DEP-05 prüft einmal vor Freigabe. Verzerrung entsteht aber *im Betrieb* — durch veränderte Nutzergruppen, Saisonalität, Rückkopplung. Subgruppen-Performance über Zeit fehlt |
| **4** | **Aufbewahrung als Konfiguration statt als Tatsache** | G-DEP-06 prüft, ob `retention_days ≥ 180` im Manifest *steht*. Ob 180 Tage lückenlos *vorliegen*, prüft niemand — obwohl die Antwort in der eigenen DB steht |
| **5** | **Fristenuhr Art. 73** | Zeit von Schwellenwertverletzung → Incident-Record → Meldung ist messbar. Das PDF behauptet „automatisiert ist die Fristenuhr"; im Code nicht auffindbar |
| **6** | **Stiller Modellwechsel** | Vom PDF selbst als Problem benannt, ungelöst. Ohne Anbieter-Attestat bliebe eine Verhaltenssignatur: fester Prüf-Prompt-Satz, Antwortverteilung überwachen |
| **7** | **Robustheit und Angriffsversuche** | Fehlerrate unter Last, Timeout-Quote, abgewiesene Eingaben, erkannte Prompt-Injection. Für ein GenAI-System nicht optional |
| **8** | **Läuft das System echt?** | `scribe_mock_mode` — siehe 7.5 (3) |

### Einschränkung

**VERIFIZIERT** ist nur: Art. 72 Abs. 3 wurde durch die VO 2026/1744 geändert (Monitoring-Plan wird Teil der Annex-IV-Doku), und Art. 4a begründet keine Bias-Pflicht. **Nicht geprüft** sind die Wortlaute von Art. 14, 15, 26 und 72 im Übrigen — sie stehen nicht im Omnibus und sind in 9.2 weiterhin offen. Wo oben „müsste gemessen werden" steht, ist das fachliche Einschätzung. **Für die Thesis-Argumentation ist das eher Vorteil: In diese Lücke hinein ist ein eigener Beitrag möglich.**

---

## 7.7 Der Evidenz-Sprung: was E-1 und E-2 technisch bedeuten (neu in v0.4)

Beides sind **andere Eingaben**, nicht andere Prüflogik. Die E-Stufe steckt in der **Herkunft des Inputs**, nicht in der Regel.

**E-1 — der Input bekommt eine Unterschrift.** Der Job, der die Evaluation durchführt, signiert sein eigenes Ergebnis (`cosign attest-blob`, keyless über OIDC). Kein stehlbarer Schlüssel: der CI-Job holt ein kurzlebiges Token, Fulcio stellt ein Zertifikat mit der Workflow-Identität aus, Rekor protokolliert. Das Gate prüft **zwei** Dinge statt einem — erst Signatur und Erzeuger-Identität, dann den Schwellenwert.

> **E-1 macht die Zahl nicht wahr.** Es macht den *Erzeuger* nachweisbar. Wer eine hartkodierte 0.89 signiert, hat eine kryptografisch einwandfrei bewiesene Lüge. E-1 verlagert Vertrauen von „irgendwer" auf „diese Pipeline" — mehr behauptet es nicht.

**E-2 — der Input *ist* das System.** Nicht die Pod-Annotation lesen (die ist ein Zettel am Pod), sondern über Gatekeeper `data.inventory` den Clusterzustand abfragen: existiert der ServiceMonitor, ist `readyReplicas > 0`. `readyReplicas` schreibt kein Mensch — das zählt der Controller.

**Der eigentliche Sprung liegt zwischen E-1 und E-2, und er ist architektonisch:**

| | Woher kommt die Zahl |
|---|---|
| **E-0 / E-1** | Sie steht **im Input**. Rego bekommt ein Dokument, in dem sie drinsteht |
| **E-2 / E-3** | Sie ist **kein Input mehr**. Sie wird abgefragt bzw. gemessen |

Rego bleibt dabei reine Entscheidungsfunktion und misst nicht selbst (Gatekeeper unterbindet externe Aufrufe standardmäßig, zu Recht). Die Messung liefert den Inhalt, die Signatur die Herkunft — E-1 und E-3 spielen zusammen:

```
drift_detector.py → misst PSI → Gate-Runner signiert das Ergebnis → Rego: "PSI > 0.2?"
```

Es landet wieder in einer Datei — **aber die Vertrauensfrage ist verschoben**: nicht mehr „hat jemand die richtige Zahl eingetragen", sondern „hat der Messprozess, dem ich vertraue, sie erzeugt".

**Grenzen, die im Gespräch zu nennen sind:** E-2 bleibt „der Cluster sagt es" — Cluster-Admins können einen ServiceMonitor ins Leere zeigen lassen. Der Unterschied ist Aufwand, nicht Unmöglichkeit. Für die ganze Kette gilt: Tamper-Evidence, nicht Tamper-Prevention.

---

## 7.8 Provenance je Metrikgruppe — E6 auf der Feldebene (neu in v0.5)

> **Herkunft vor Unterschrift.** Der Leitsatz von SPEC-04, und die Anwendung der Einsicht aus 7.7: Die E-Stufe steckt in der **Herkunft des Inputs**, nicht in der Prüflogik.

### Der Schritt vor E-1

7.7 beschreibt, was E-1 leistet und was nicht: Es macht die Zahl nicht wahr, sondern den Erzeuger nachweisbar. Daraus folgt eine Reihenfolge, die in Teil 11 bereits gesetzt ist — **erst die Herkunft, dann die Signatur**. Die naheliegende Rückfrage im Fachgespräch lautet nicht „ist das signiert?", sondern **„woher kommt die Zahl?"**.

Für den heutigen Bestand ist diese Frage pro Metrik verschieden zu beantworten, und genau das ist bislang nicht ablesbar. Deshalb bekommt jede Metrikgruppe im Ergebnisdokument ein Feld `provenance`:

| Wert | Bedeutung | Beispiel im Bestand |
|---|---|---|
| **`measured`** | Aus einer laufenden Messung gewonnen | `latency_p95_ms` aus `scribe_latency_seconds_bucket` |
| **`derived`** | Aus gemessenen Größen gerechnet | `psi_score`, `jsd_score` |
| **`declared`** | Behauptet — kein Erzeuger, keine Messung | `accuracy`, `safety_score`, `subgroup_analysis` |

### Was das leistet, und was ausdrücklich nicht

**`accuracy` wird dadurch nicht echt.** Der Grund steht in 7.6 und ist kein Versäumnis dieses Repos, sondern das ungelöste Kernproblem des Feldes: Ohne Ground Truth gibt es im Betrieb keine Genauigkeit, nur Stellvertreter.

> **Was der Schritt leistet:** Die Behauptung verschwindet nicht — sie wird **als Behauptung kenntlich**. Nach der Umsetzung ist an jeder einzelnen Zahl ablesbar, ob sie gemessen, gerechnet oder behauptet ist. Damit ist die Rückfrage „woher kommt die Zahl?" **für jede Zahl einzeln** beantwortbar, auch dort, wo die Antwort unbequem ist.

Das ist E6 nicht mehr auf Gate-Ebene, sondern auf Feldebene — die feinste Auflösung, die das Modell bislang erreicht hat. Und es ist billig: keine neue Messung, keine Signatur, kein Cluster.

**Konsequenz für den Gate-Katalog:** Ein Check mit Severity MUST, der auf einer `declared`-Gruppe steht, ist ein Gate, das eine Selbstauskunft blockierend prüft. Das ist kein Fehler, aber es gehört sichtbar gemacht — als **SHOULD-Warnung**, nicht als MUST. Ein MUST würde den Bestand am Tag der Einführung rot färben und träfe eine Lücke, die bewusst offen bleibt.

### Zwei Entwurfsentscheidungen, die begründet gehören

**Erstens: `mock_mode` gehört in den Orchestrator, nicht in die Policies.** Zwei Gründe. Die Prüfung müsste sonst in **jeder der 17 Policies** wiederholt werden, und eine 17-fach duplizierte Vorbedingung fehlt irgendwann in einer. Und: **Rego darf nicht messen.** Gatekeeper unterbindet externe Aufrufe standardmäßig und zu Recht (7.7). Der Wert muss dem Gate als Input **vorgelegt** werden, er darf nicht von ihm geholt werden. Auflösung wie beim Rollenparameter aus SPEC-03, **Default `unknown` statt `live`** — wer nicht weiß, ob das System echt lief, hat keinen Nachweis, dass es echt lief.

**Zweitens: Mock-Betrieb erzwingt kein FAIL.** Die strenge Variante wäre naheliegend und ist falsch. Sie macht den Kolloquiums-Walkthrough unmöglich, obwohl der Mock-Betrieb ein legitimer PoC-Modus und kein Compliance-Verstoß ist — und ein Gate, das immer fehlschlägt, wird binnen Wochen abgeschaltet. Das ist das Schicksal aller schwachen Gates, in 7.3.1 für Richtung B bereits ausformuliert.

**Stattdessen: `runtime_mode` als gehashtes Feld am Evidence-Record.** Ein PASS im Mock-Betrieb bleibt möglich, ist aber von einem PASS im Echtbetrieb **unterscheidbar und nicht nachträglich fälschbar**.

> Die Aufgabe ist nicht, den Mock-Betrieb zu verbieten, sondern ihn **unverbergbar** zu machen. Das ist Tamper-Evidence, nicht Tamper-Prevention — dieselbe Linie wie in 7.7, angewandt auf die Frage „lief hier überhaupt ein Modell?".

Preis dieser Wahl: eine Migration `v05 → v06` und damit der einzige Eingriff in die Hash-Kette. Sie steht in SPEC-04 deshalb **am Ende** der Umsetzungsreihenfolge, nicht am Anfang.

---

## 7.9 Was erst der echte Lauf zeigte (neu in v0.6)

> **Belegstufe:** verifiziert am 25.08. gegen die echte Anwendung im Container (`docker build` + `docker run -p 8080:8080`), nicht gegen einen Stellvertreter.

SPEC-04 ist umgesetzt. Danach wurde die App tatsächlich gestartet — und das förderte eine Fehlerklasse zutage, gegen die Unit-Tests konstruktionsbedingt blind sind.

### Das Messproblem: gemessen, aber informationsfrei

Alle Anfragen fielen in den ersten Histogramm-Bucket. Die Untergrenze lag bei **0,1 s**, die Mock-Antwort braucht **Mikrosekunden**. `histogram_quantile` konnte deshalb nur *innerhalb* des ersten Buckets interpolieren:

| | vorher | nachher |
|---|---|---|
| gemeldeter p95 | 95 ms | 0,95 ms |
| tatsächlicher Mittelwert | unbekannt | **0,034 ms** (exakt) |
| System sagt, dass der p95 nichts aussagt | nein | **ja** |

Die 95 ms waren `0,95 × 0,1 s` — sie wären bei jeder Last dieselben gewesen. **G-DEP-02 wandte eine 2000-ms-Schwelle auf eine Konstante an.** Die Herkunft stimmte seit SPEC-04, die Auflösung nicht.

> **Das ist eine eigene Fehlerklasse und gehört benannt:** Ein Wert kann *gemessen* und trotzdem *informationsfrei* sein. `provenance: measured` beantwortet „woher kommt die Zahl", nicht „sagt sie etwas aus". Die zweite Frage brauchte eine eigene Antwort.

### Zwei Antworten darauf

**Der exakte Mittelwert.** `latency_mean_ms` aus `_sum`/`_count` — keine Bucket-Grenze beteiligt, keine Interpolation. Der erste Latenzwert im ganzen Bestand, der kein Schätzwert ist. Gegen einen Stellvertreter mit 400 ms Kunstverzögerung verifiziert: Mittelwert 400,0 ms.

**Die Schwäche der Messung, maschinenlesbar.** Neues Feld `latency_p95_resolution`:

```json
{ "enclosing_bucket_ms": [0.0, 1.0], "finest_bucket_ms": 1.0, "within_finest_bucket": true }
```

`within_finest_bucket: true` heißt: der Quantilwert bewegt sich mit der **Bucket-Aufteilung**, nicht mit dem System. Eine Schwelle darauf ist eine Schwelle auf ein Artefakt.

> **Das ist E6 eine Ebene unter der Feldebene.** 7.8 machte die *Herkunft* jeder Zahl sichtbar. Hier wird die *Belastbarkeit* derselben Zahl sichtbar. Beide Male gilt dieselbe Bewegung: die Zahl bleibt, ihre Grenze hört auf, unsichtbar zu sein. Ein möglicher Beitrag über E6 hinaus — in keinem bekannten Werkzeug geführt.

### Der eigene Fehler: eine zugesagte Erzwingung, die es nicht gibt

SPEC-04 Abschnitt 5.3 schrieb, die Anwesenheitspflicht des Messdokuments werde „eine Ebene höher, im Orchestrator" erzwungen. **Das wurde nicht implementiert.** Wer das Dokument weglässt, bekommt heute ein grünes G-OPS-03 auf drei Annotationen.

> **Ein MUST-Check, den man durch Weglassen des Inputs umgeht, ist kein MUST.** Es ist dieselbe E-0-Schwäche, die das Gate loswerden sollte — nur eine Ebene verschoben. Der Befund gehört sichtbar stehen, weil er zeigt, wie leicht eine Lücke beim Verschieben überlebt. SPEC-04b schließt sie **zuerst**, vor jeder weiteren Messung.

### Zwei kleinere Befunde

`sprintf` rendert einen JSON-Integer mit `%.0f` als `%!f(int=900)`. Die Rego-Unit-Tests prüfen mit `contains(msg, "C-03")` und sahen den Formatfehler nie — **Tests, die auf Teilstrings prüfen, bestätigen die Regel und nicht die Meldung.** Und das Dockerfile trug seit dem Lizenzwechsel vom 15.08. weiterhin `licenses="CC-BY-NC-4.0"`, als OCI-Label in jedem gebauten Image.

---

## 7.10 Wo „funktionsfähig" wirklich hängt (neu in v0.6)

> **Nicht an Kubernetes.** Diese Klärung war nötig, weil die Verschiebung des Cluster-Themas mit einer Funktionslücke verwechselt wurde.

Zwei Achsen, die unabhängig sind und regelmäßig vermischt werden:

**Achse 1 — Durchsetzungspunkt.** Conftest in der CI *oder* Gatekeeper als K8s-Admission. Zwei Einstiegspunkte für dieselben Policies, keine Stufen einer Leiter; die Rego-Dateien sind dual-mode geschrieben.

**Achse 2 — Beweiskraft (E6).**

| Stufe | Braucht wirklich | Cluster nötig? |
|---|---|---|
| E-0 | eine Datei | nein |
| E-1 | Signatur über CI-Identität (OIDC) | **nein — GitHub Actions ist der natürliche Ort** |
| E-3 | eine **laufende Anwendung** mit `/metrics` | **nein** |
| E-2 | `data.inventory`, `readyReplicas` | **ja, nur hier** |

**Folge: Kubernetes zu verschieben kostet genau eine Stufe — E-2.** Am 25.08. praktisch belegt: die vollständige E-3-Kette lief gegen einen Container mit `-p 8080:8080`, ohne Cluster.

### Der Befund in der eigenen Pipeline

Der CI-Workflow gibt aus:

```
Expected: 173/173 PASS
PASS: 187/187              ← tatsächliches Ergebnis
✅ Rego Unit Tests PASS — 173/173 green
```

Die CI **meldet** 173/173, während 187 Tests liefen. Die Zahl steht hartkodiert im Meldungstext und wird gegen nichts gehalten.

> **Strukturell ist das `gate_result.all_passed`:** eine mitgelieferte Behauptung über ein Ergebnis, die niemand gegen das Ergebnis hält. Diesmal in der Pipeline, die das Kontrollsystem prüft. Der Fehlertyp ist offenbar nicht auf Gate-Inputs beschränkt — er tritt überall dort auf, wo eine Zahl **geschrieben** statt **gelesen** wird.

### Was daraus folgt

Die CI nutzt heute **nichts** von dem, was SPEC-04 gebaut hat: G-DEP-02 liest die eingecheckte Fixture, G-OPS-03 bekommt kein Messdokument, und die drei neuen E-3-Checks bleiben stumm. Das Gate ist im Repo E-0/E-3 gemischt und **in der Umgebung, die zählt, weiterhin E-0**. SPEC-04b adressiert genau das.

---


## 7.3 Neu hinzukommend

| Baustein | Zweck | Souveränitäts-Vorbehalt |
|---|---|---|
| **in-toto / SLSA / Sigstore (cosign)** | Signierte Attestierung — Grundlage für Evidenz-Ebene **E-1** | Die öffentliche Sigstore-Instanz (Fulcio, Rekor) läuft unter der Linux Foundation auf US-Infrastruktur. **Für ein Demo-Setup ausreichend; für einen Produktivbetrieb wäre Selbstbetrieb nötig.** |
| **Gatekeeper `data.inventory`** | Beobachteter Clusterzustand — **E-2** | keiner |
| **Prometheus / Drift-Detektor** | Messung über Zeit — **E-3**, bereits im Bestand | keiner |
| **CycloneDX ML-BOM / SPDX 3.0 AI Profile** (neu) | Maschinenlesbare Lieferantennachweise für Richtung B | keiner; beide sind offene Standards (ECMA-424 bzw. ISO/IEC 5962-Kern) |

### 7.3.1 Zweistufigkeit für Richtung B — Konstruktionsregel

**Gegenposition zuerst:** Die Formate existieren, aber die Anbieter im Energiesoftware-Markt liefern sie mit hoher Wahrscheinlichkeit **nicht**. Ein Gate, das eine signierte ML-BOM verlangt, schlägt bei jedem realen Beschaffungsvorgang fehl und wird binnen Wochen auf `warn` gesetzt oder abgeschaltet — das Schicksal aller schwachen Gates.

1. **Realistische Basisstufe:** Existenz, Zuordnung und Integrität der **gelieferten Dokumente** (Betriebsanleitung, Konformitätserklärung, Vertragsklauseln) — Hash im Evidence Store, Chain-verankert, Verfall bei Modellwechsel.
2. **Zielstufe:** maschinenlesbare, signierte AIBOM. Als **Reifegradstufe** ausgewiesen, nicht als Eintrittsbedingung.

**Ungeprüfte Annahme, vor dem Bau zu klären:** Liefert irgendein Anbieter im Redispatch-Umfeld heute eine maschinenlesbare AIBOM?

## 7.4 Offene Technologiefragen

- **Cedar vs. OPA** — nicht entschieden, siehe Trade-off oben
- **Formale Policy-Vor-Verifikation** (SMT/Z3) — noch nicht im Bestand
- **OSCAL-Export** — noch nicht im Bestand
- **Rollenzustand pro System oder pro System-Version?** (neu) — bei Version wird der Übergang auditierbar, bei System einfacher. Datenmodell-Entscheidung mit Folgen für die Hash-Chain. **Vor Scharfstellung von SPEC-03 zu klären.**
- **Zwei Sicherheitspfade in einer Codebasis:** `TAMPER_DETECTION_SPEC.md` weist für SQLite ausdrücklich „no triggers, no RBAC" aus, die Testartefakte im Repo sind SQLite. Teile der Testsuite laufen gegen den ungeschützten Pfad. **Für business-ready: SQLite entfernen oder hart als nicht-konform kennzeichnen.**

---

## H4.13 Was G-OPS-02 wirklich tut — und was ein Entwurf darüber behauptete (B-13)

> **Anlass:** Ein Beitragsentwurf zu G-OPS-02 (27.08.2026), geprüft gegen den Code Satz für Satz.

**Was das Gate prüft:** drei Pod-Annotationen, bei der Zulassung.

```
genaiops.io/incident-response-configured == "true"
genaiops.io/incident-contact            != ""
genaiops.io/rollback-mechanism          == "true"
```

Das Gate sagt in seiner eigenen Definition, was das wert ist: `evidence_level.current: E-0`, Begründung *„eine Annotation behauptet einen Zustand, sie beweist ihn nicht."*

| Behauptung im Entwurf | Befund am Code |
|---|---|
| Art. 26 Abs. 5 · Art. 73 · R009 · G-OPS-02 · AUTO | **stimmt** |
| „Monitoring-Worker erzeugt Incident Record mit `decision='FAIL'`" | Existiert — aber unter **G-OPS-03**. Seit SPEC-04 entscheidet dort zudem Rego, nicht ein Python-Schwellenwert |
| „Partial Index löst priorisierte Incident-Abfrage aus" | `idx_qgr_failures_partial` existiert. **Ein Index ist passiv** — er macht eine Abfrage schnell, er startet keine. Es gibt keinen Konsumenten |
| „Eskalationslogik an Drift-Detection gekoppelt" | **Existiert nicht.** Einziger Bezug: ein Satz Fließtext in einer Prometheus-Alert-Beschreibung („initiate incident response") |
| Kaskade Anbieter → Einführer/Händler → Marktüberwachung | Keine Zeile Code kennt diese Rollen. **Zusätzlich rechtlich ungeprüft**: Art. 26 steht in 6.2 als nicht EUR-Lex-abgeglichen |
| „Automatisiert sind Incident-Auslösung **und die Fristenuhr**" | **Die Fristenuhr existiert nicht.** `grep -ri "Fristenuhr"` findet genau einen Treffer: die Liste offener Punkte in SPEC-04 |
| „Nicht automatisiert ist die Schwellenwertfrage" | **stimmt** — und ist der stärkste Teil des Entwurfs |

**Zwei Punkte, die tiefer sitzen als einzelne Sätze:**

*„Erkennt im laufenden Betrieb"* ist das Gegenteil dessen, was das Gate tut. Sein `trigger` lautet `kubectl apply — Gatekeeper Admission`. Admission Control feuert **bevor** die Last läuft. Siehe B-14.

*„Fehlklassifikation"* wird nirgends gemessen. Der Drift-Detektor misst Latenz-Buckets als Stellvertreter für die Eingabeverteilung (7.5 (2)); Fehlklassifikation bräuchte Ground Truth, die es nicht gibt (B-08).

> **Der Kern des Befunds:** Die Fristenuhr war intern schon als unbelegt festgehalten (7.6 Lücke 5, *„das PDF behauptet … im Code nicht auffindbar"*) und wanderte trotzdem in einen Text für außen. Der Befund liegt nicht im Entwurf, sondern darin, dass **kein Mechanismus eine Außenaussage gegen den Gate-Stand hält** — anders als beim README, wo `README_COUNTS_CURRENT` genau das tut.

## H4.14 Admission gegen Laufzeit — vier Gates widersprechen ihrem Requirement (B-14)

Systematisch geprüft über alle 17 Gates: Gate-`trigger` gegen `audit_trigger` des verlinkten Requirements.

| Gate | Gate-Trigger | Requirement verlangt |
|---|---|---|
| **G-OPS-01** Human Oversight | `kubectl apply` — einmalig | Runtime (kontinuierlich) + Post-Market |
| **G-OPS-02** Incident Reporting | `kubectl apply` — einmalig | Runtime (**Event-getriggert**) + Post-Market |
| **G-OPS-03** Monitoring | `kubectl apply` — einmalig | Runtime (kontinuierlich) + Post-Market |
| **G-OPS-05** Evidence Completeness | `kubectl apply` — einmalig | Runtime (kontinuierlich) + Post-Market |

**Admission Control feuert einmal, bevor der Workload läuft.** Ein Requirement, das „kontinuierlich" oder „Event-getriggert" verlangt, ist dadurch nicht erfüllbar — nicht schlecht erfüllt, sondern strukturell nicht erfüllbar.

Die anderen 13 Gates sind stimmig: Pre-Deployment- und Deployment-Gates feuern bei PR-Merge oder Image-Build, und ihre Requirements verlangen genau das.

> **G-OPS-03 ist seit SPEC-04b die Ausnahme** und zeigt den Weg: Es behielt die Annotationsprüfung bei der Zulassung (E-0) und bekam eine **zweite Auswertung gegen ein Messdokument** (E-3), samt Frist über C-03. Ein Gate kann beides tragen — Zulassung *und* Laufzeit — wenn es zwei Inputs hat statt einem.
>
> Damit ist B-14 kein Konstruktionsfehler des Modells, sondern eine **nicht nachgezogene Ausbaustufe** bei G-OPS-01, G-OPS-02 und G-OPS-05.

**Warum es niemand gemerkt hat:** Beide Aussagen sind eingecheckt, beide gelten, und **nichts prüft sie gegeneinander**. Der Widerspruch ist nur zu finden, wenn man zwei Dateien nebeneinanderlegt. Genau dafür ist die Integrity-Regression da — dieser Fall fehlt ihr noch.

## H4.15 Gate-Anatomie — die fünf Fragen, und die eine, die das Template nicht stellt

Aus der Frage, ob das Vorgehen aus H4.13 für **jedes** Gate gilt. Es gilt, und die Prüfung hat eine Lücke im Template freigelegt.

| Frage | Wo sie heute im Gate steht |
|---|---|
| **1. Ziel** — welche Pflicht soll erfüllt sein? | `links.requirements` + `legal_refs` je Check |
| **2. Daten** — womit wird geprüft? | `evidence_required`, seit SPEC-04b **`required_inputs`** |
| **3. Ergebnis** — was kommt heraus? | `policy_checks[].severity` → abgeleitete Entscheidung, Evidence-Record |
| **4. Was löst das Gate aus?** (eingehend) | `trigger` |
| **5. Was löst das Gate aus?** (ausgehend) | **nirgends** |

> **Frage 5 fehlt im Template — und das erklärt B-13.** Ein Gate erzeugt heute ein Urteil und einen Evidence-Record. Was daraus *folgt*, steht nirgends: blockiert es den Rollout, eröffnet es einen Vorfall, startet es eine Frist, benachrichtigt es jemanden? Der Orchestrator bricht bei FAIL ab — aber das ist eine Eigenschaft des Orchestrators, nicht eine deklarierte Eigenschaft des Gates.
>
> Wo nichts deklariert ist, füllt die Vorstellung die Lücke. Der Entwurf zu G-OPS-02 beschrieb eine Eskalationskaskade, weil das Gate über seine Wirkung schweigt und eine Meldepflicht ohne Wirkung sinnlos wäre. **Die Behauptung war der plausible Schluss aus einer Leerstelle.**

**Für Art. 26 Abs. 5 ist Frage 5 nicht optional.** Die Norm verlangt eine *Folge* — informieren, melden, fristgerecht —, nicht ein Urteil. Ein Gate, das nur PASS/FAIL kann, kann diese Pflicht konstruktiv nicht abbilden, egal wie gut es prüft.


## H4.16 Die Definition of Done lag schon im Repo (B-15)

Alle 14 Requirements tragen seit der Masterarbeit `acceptance_criteria` — **37 Stück**. Gelesen hat sie nichts. Der einzige Treffer außerhalb von `requirements/` war ein **Kommentar** in einer Policy: *„Checks (derived from R014 acceptance_criteria)"*. Prosa, kein Mechanismus.

**Dritter Fall desselben Musters:** `policy_checks[].evidence_level` stand nach SPEC-01 überall auf `null` (B-07), `scribe_mock_mode` wurde exportiert und von keinem Gate gelesen (B-06), und hier nennt ein Requirement seine eigene Definition of Done, während der Katalog seine Gates nie dagegen hält. R009 sagt *„Meldung erfolgt innerhalb der gesetzlichen Frist"* — es gibt keine Fristenuhr, und niemand hat es bemerkt.

**Auflösung.** Ein Kriterium ist Prosa und maschinell nicht auf einen Check abbildbar. Die Zuordnung wird deshalb **deklariert**, und der Check prüft die Deklaration:

| Status | Bedeutung | Prüfung |
|---|---|---|
| `met` | nennt konkrete Gate-Checks | jede genannte ID muss existieren |
| `gap` | nennt, was fehlt | Begründung ist Pflicht |
| `unverified` | noch nicht zurückverfolgt | **warnt und wird gezählt** |

**Erster Durchgang, konservativ:** 18 belegt, 13 als Lücke begründet, 6 offen. `met` nur, wo auf einen Check gezeigt werden kann — im Zweifel `unverified`, weil Unterbehauptung die sichere Richtung ist.

> `unverified` ist bewusst kein Fehler. Es sagt „das hat noch niemand nachverfolgt", und das ist etwas anderes als eine behauptete Deckung. **Eine Suite, die Ehrlichkeit bestraft, wird umgangen.**

## H4.17 Fail-open auf dem Evidenzpfad (B-16)

`record_to_evidence_store()` im Orchestrator liefert `{"returncode": ..., "stdout": ..., "stderr": ...}`. Der Wert wird an **eine** Stelle weitergereicht: `print_gate_result()` — zur Anzeige. **Niemand wertet ihn aus.**

Schlägt der Schreibvorgang in den Evidence Store fehl, läuft die Pipeline weiter und kann PASS melden.

> **Für ein Kontrollsystem, dessen gesamte Prämisse die manipulationserkennbare Nachweiskette ist, ist ein Gate, das ohne geschriebenen Nachweis besteht, ein Konstruktionsfehler.** Ein Nachweis, der fehlen darf, ist kein Nachweis.

**Die beiden Pfade widersprechen sich.** Der Drift-Detektor macht es richtig und sagt es sogar im Kommentar:

```python
print(f"[evidence] ERROR: Failed to record drift evidence: ...")
sys.exit(1)  # Hard fail — evidence recording is mandatory
```

Zwei Wege in dieselbe Tabelle, zwei verschiedene Antworten auf dieselbe Frage. Wie bei B-04 (zwei Erzeuger für G-OPS-03) ist der Widerspruch nur zu finden, wenn man beide nebeneinanderlegt.

**Fail-closed ist hier die einzige vertretbare Wahl** — mit einer Einschränkung, die mitgedacht gehört: ein Evidence Store, dessen Ausfall jede Pipeline blockiert, wird zum Single Point of Failure. Das ist der Preis und er ist zu benennen, nicht zu umgehen.

## H4.18 Was einem Engineering-Prozess für dieses System noch fehlt

Aus der Frage, ob der DoD-Ansatz vollständig ist. Geprüft gegen das, was beim Bau eines regulierten Systems üblicherweise verlangt wird.

**Vorhanden, unter anderen Namen:** Requirements (R001–R014) · Traceability (sechsstufige Kette) · DoD je Spec · dreischichtige Tests + Integrity-Regression · Change Management (`specs/`, CHANGELOG) · Konfigurationsmanagement (Schemaversionen, Migrationen) · Risikoregister (H8) · Rollen (`owner` je Gate).

**Fehlt:**

| # | Was | Warum es zählt |
|---|---|---|
| 1 | **Definition of Ready** | Existierte nicht. Hätte die Neuausrichtung von G-OPS-02 vermieden — Punkt „Verhältnis zu parallelen Regimen geklärt" war der teuer gelernte |
| 2 | **Wirkungsdeklaration je Gate** (Frage 5) | Ein Gate erzeugt ein Urteil; was daraus folgt, steht nirgends (B-13) |
| 3 | **Validierung, nicht nur Verifikation** | Die Gates prüfen, ob die Spezifikation erfüllt ist. Ob der Gate-**Satz** das regulatorische Risiko tatsächlich senkt, prüft nichts. Genau der Befund von Surve et al. (2026): 89,9 % konform, davon nur 34,3 % mit hoher Assurance |
| 4 | **Fail-open/fail-closed als bewusste Entscheidung** | B-16. Zwei Pfade, zwei Antworten, keine Entscheidung |
| 5 | **Nicht-funktionale Anforderungen an das Kontrollsystem selbst** | Verfügbarkeit, Laufzeit, Wiederanlauf. Ein Gate-System, das steht, blockiert nichts |
| 6 | **Vier-Augen-Prinzip** | Ein Autor schreibt Requirement, Gate, Policy, Test und Prüfung. Für ein Auditartefakt ist das eine benennbare Schwäche |
| 7 | **Retirement-Pfad für Gates** | Deckungsgleich mit der eigenen Limitation L2 und dem Forschungsbefund, dass das Lifecycle-Ende die anerkannte Lücke ist (H7) |
| 8 | **Datenhaltung des Kontrollsystems** | Was geschieht mit Evidenz nach der Aufbewahrungsfrist? Ein Insert-only-Speicher ohne Löschkonzept kollidiert mit Art. 17 DSGVO |

> **Punkt 3 ist der schwerwiegendste.** Er ist keine fehlende Datei, sondern eine fehlende Frage: *Woher weiß ich, dass diese 17 Gates die richtigen 17 sind?* Die Traceability zeigt, dass jedes Gate auf eine Norm zurückgeht. Sie zeigt **nicht**, dass die Normen vollständig abgedeckt sind. Der Weg dahin ist eine Deckungsanalyse Norm → Requirement, nicht mehr Gates.


---

## H4.19 Die Anwesenheitspflicht galt überall außer in der CI (B-17)

Der interessanteste Befund dieser Strecke, weil er nach der Behebung entstand.

SPEC-04b Teil 3.2 hat `required_inputs` eingeführt und im Orchestrator erzwungen: deklariert ein Gate ein Pflichtdokument und liegt es nicht vor, ist das Gate FAIL. Der Integrity-Check `REQUIRED_INPUTS_ENFORCED` hielt das fest. Beides war richtig. Beides war grün.

**Die CI fährt den Orchestrator nicht.** Sie ruft conftest je Gate direkt über `run_gate.sh`. Die Pflicht galt also im Walkthrough und im lokalen Lauf — und nicht in der Pipeline, die darüber entscheidet, ob ein Image gebaut wird. G-OPS-02 und G-OPS-03 deklarierten seit dem 25.08. ein Pflichtdokument, die CI forderte keines an, und beide Gates wurden grün auf Pod-Annotationen allein. Genau der Zustand, den SPEC-04b beseitigen sollte, drei Tage lang, eine Ebene weiter außen.

**Warum der Test es nicht fand.** `REQUIRED_INPUTS_ENFORCED` prüfte, ob `pipeline/gate_orchestrator.py` die Funktionen `check_required_inputs` und `load_gate_required_inputs` enthält. Das tat es. Der Check verifizierte **einen Aufrufer** und nannte die Pflicht damit erzwungen.

> **Die Lehre ist nicht „gründlicher prüfen".** Sie ist: bei einem neuen Mechanismus reicht die Frage „wirkt er?" nicht. Zu fragen ist **„wo überall muss er wirken?"** — und dann jeder dieser Orte einzeln. Ein Mechanismus mit zwei Aufrufern, von denen einer geprüft wird, ist zu 50 % gebaut und zu 100 % dokumentiert.

**Zweiter, kleinerer Befund derselben Art im selben Zug.** Die CI installierte `psycopg2-binary`, aber kein PyYAML. `load_gate_required_inputs()` fängt den ImportError ab, gibt eine Warnung aus und liefert ein leeres Dict zurück. Hätte die CI den Orchestrator gefahren, wäre die Erzwingung *dort* still abgeschaltet gewesen — sichtbar nur als eine Zeile im Log, die niemand liest. Eine Erzwingung, die sich durch ein fehlendes Paket abschalten lässt, ist keine. `ci_required_inputs.py` endet in diesem Fall deshalb mit Exit 2 und sagt, dass nicht geprüft werden konnte.

**Behebung.** `pipeline/ci_required_inputs.py` löst die Deklarationen für einen CI-Lauf auf und legt je Gate ab, was zusätzlich auszuwerten ist (`-inputs.args`) oder welcher Pflichtinput fehlt (`-inputs.fail`). Der Gate-Runner wertet Primärdokument und Pflichtinputs in **ein** Ergebnis, also einen Evidence-Record — die gleiche Form wie `role_scope: BOTH` in SPEC-03. Ein fehlender Input lässt das **Gate** fehlschlagen, nicht den Schritt: sonst bräche der Lauf ab, bevor die Evidenz geschrieben ist, und die Lücke wäre laut statt aktenkundig.

`REQUIRED_INPUTS_ENFORCED` verlangt jetzt zusätzlich, dass der Workflow die Deklarationen auflöst, dass der Gate-Runner das Aufgelöste auch liest, dass jeder deklarierte Input tatsächlich geliefert wird, und dass PyYAML **in jedem Job** installiert ist, der die Erzwingung fährt. Alle vier Hälften wurden durch Brechen gegengeprüft. Die PyYAML-Hälfte fiel bei der ersten Gegenprobe durch: sie suchte `pip install ... PyYAML` in der ganzen Datei und blieb grün, als der Install aus dem Job entfernt wurde, der ihn braucht — ein zweiter Job hatte noch einen. Ein Check, den eine Gegenprobe nicht brechen kann, ist kein Check (B-16), und dieselbe Regel gilt für den Check über dem Check.

## H4.20 Was die CI-Messung zeigt — und was nicht

Zur Einordnung von SPEC-04b Teil 3.1, damit die Außendarstellung nicht wieder den Stand überholt (B-13).

**Was sie zeigt.** Das Driftdokument, das G-OPS-03 beurteilt, entsteht in derselben Pipeline, die es beurteilt: Baseline aus `/metrics` der laufenden Anwendung, zweites Lastprofil mit anderen Textlängen, Messung dagegen. C-03 (Frist) und C-05 (Provenance) prüfen damit erstmals ein Dokument, das nicht eingecheckt wurde. Der Workflow sichert zusätzlich zu, dass `provenance` gleich `derived` ist und die Quelle die Anwendung unter Test — ein `declared` hieße, eine Datei wurde durchgereicht und nichts beobachtet.

**Was sie nicht zeigt: Drift.** Gemessen wurde PSI 0.000000, lokal gegen dieselbe Anwendung nachgestellt. Das ist die Bauart, kein Mangel, und zwar aus zwei unabhängigen Gründen:

1. Das Prometheus-Histogramm ist **kumulativ** über die Prozesslaufzeit. Die „aktuelle" Verteilung enthält die Baseline mit und kann sich nur verdünnen, nie verschieben. Ein echter Drift-Nachweis braucht getrennte Zeitfenster oder zwei Prozesse.
2. Der Mock antwortet in Sub-Millisekunden, weitgehend unabhängig von der Textlänge (B-09). Das zweite Lastprofil *kann* die Latenzverteilung kaum bewegen.

Beides ist eine Aussage über den PoC, nicht über die Architektur. Und beides ändert nichts daran, dass die Messung echt ist — ein gemessenes „keine Drift" ist ein gültiges Ergebnis.

**`build-and-push` hängt an beiden Jobs.** Gates grün *und* Negativfälle bestanden. Ohne die zweite Bedingung wäre die erste wenig wert: ein Katalog, in dem kein Gate mehr rot werden kann — kaputte Policy, falscher conftest-Namespace, ins Leere laufende Anwesenheitspflicht — meldet weiterhin 17/17 PASS und liefert ein Image aus. `NEGATIVE_CASES_GATE_THE_BUILD` hält die eine `needs`-Zeile fest, weil sie beim nächsten Umbau bequem wegfällt und danach nichts falsch aussähe. Fünf Gegenproben; die erste Fassung fiel bei dreien durch, weil sie den Jobtext nach „BLOCK", „PASS" und den Gate-IDs durchsuchte — und diese Wörter stehen auch in der Definition von `expect_gate.sh` und im Summary-Banner. Sie las die Quelle des Helfers und die Dekoration, nicht die Zusicherungen des Jobs. Jetzt prüft sie die Aufrufe.

**Dass die Gates blockieren würden, beweist kein grüner Durchlauf.** Das beweist der Negativfall-Job: gemessene Drift blockiert G-OPS-03, eine verfehlte Sicherheitsmetrik blockiert G-DEP-02, und eine **fehlende** Messung blockiert G-OPS-03 über die Anwesenheitspflicht. Jeder Fall hat eine Gegenprobe daneben, weil Fall 1 identisch aussähe, wenn er aus einem anderen Grund rot wäre — veraltetes Dokument, falscher Namespace. Und `expect_gate.sh` prüft die *Erwartung*, nicht nur den Ausgang: ein Werkzeugfehler meldet ebenfalls null Verstöße und wäre sonst von einem bestandenen Normalfall nicht zu unterscheiden.

## H4.21 Der einzige E-1-Check erfüllt die E-1-Definition nicht (B-18)

Anlass für SPEC-05, gefunden beim Schreiben derselben.

Der Katalog trägt **genau einen** Check oberhalb von E-0: G-OPS-05/C-02, „Hash-Chain-Integrität über alle Evidence-Records", eingestuft als E-1. Die Begründung im Gate lautet, der Verifikationsanteil sei „für sich genommen bereits ein berechneter Integritätsnachweis auf E-1-Niveau".

**Gemessen an der eigenen Definition trifft das nicht zu.** HANDBUCH 3.3 verlangt für E-1 ein „erzeugtes und **signiertes** Artefakt; Signatur und **Erzeuger-Identität** geprüft", mit Fälschungskosten „Kompromittierung der CI-Identität".

| E-1 verlangt | Die Kette leistet |
|---|---|
| Signatur | keine — SHA-256 ist eine Prüfsumme, kein Signaturverfahren |
| geprüfte Erzeuger-Identität | `inserted_by` ist eine Zeichenkette, die der Schreiber selbst wählt (Default `'poc_local'`). Hash-gedeckt, also unveränderlich festgehalten — aber nicht belegt |
| Fälschungskosten = CI-Identität | Schreibzugriff. Wer die Kette ändern will, rechnet sie ab Genesis neu und legt eine formal einwandfreie Kette vor |

Die Kette ist manipulationsevident **gegen Teiländerungen**, und das ist etwas wert. Aber es ist eine Aussage über innere Konsistenz, nicht über Herkunft — nach der Fälschungskosten-Ordnung der E6-Achse also E-0 mit einer Zusatzeigenschaft.

**Der zweite Teil wiegt schwerer.** `EVIDENCE_DB: /tmp/evidence_pipeline.db`, und es gibt keinen `upload-artifact`-Schritt. Die Pipeline legt die Datenbank an, schreibt 17 Records, verifiziert die Kette — und der Runner wird zerstört. Geprüft wird die innere Konsistenz einer Datenbank, die zwanzig Sekunden existiert hat und die niemand je wiedersehen wird.

> Daraus folgt der Leitsatz von SPEC-05: **die Signatur ist keine Verzierung auf der Kette, sie ist das, was die Evidenz eines Laufs aus dem Runner heraussträgt.** Ohne sie ist der lückenlose Audit-Trail eine Eigenschaft, die pro Lauf entsteht und mit dem Lauf vergeht.

**Der Fehlertyp, zum sechsten Mal.** Diesmal trifft er die Beweisstufen-Achse selbst: das Feld `evidence_level` wurde eingeführt, um Beweiskraft prüfbar zu machen, und der einzige Wert oberhalb von E-0, den der Katalog führt, hält seiner eigenen Definition nicht stand. Deshalb ist die Rückstufung Teil 1 von SPEC-05 und hängt an nichts — **eine falsche Einstufung ist schädlicher als eine niedrige**, weil sie den Leser beruhigt.

**Beim Schreiben der SPEC nochmals dieselbe Lehre.** Drei Werkzeugangaben des ersten Entwurfs waren gegen die cosign-Dokumentation zu korrigieren: die Bundle-Endung, die Annahme, ein `verify-blob` ohne Identitätsangabe laufe grün durch (cosign erzwingt die Angabe und bricht sonst ab), und die Einstufung der Transparenzlog-Prüfung als Kür statt als Voreinstellung. Die letzte war die folgenreichste — als SHOULD formuliert hätte der Check die Voreinstellung zur Option erklärt und dazu eingeladen, sie mit `--insecure-ignore-tlog` abzuschalten, wenn der Dienst klemmt. Ein Vorhaben, das Behauptungen gegen ihren Gegenstand hält, fängt bei den eigenen an.

## H4.22 Die Korrektur war selbst eine ungeprüfte Behauptung (B-19)

Am 01.09.2026 wurde mit SPEC-05 Teil 1 die E-1-Einstufung der Hash-Kette zurückgenommen (B-18, H4.21). Derselbe Commit setzte an zwei Stellen ins README: **„kein Check im Katalog liegt heute über E-0"**.

**Der Satz war in dem Moment falsch, in dem er geschrieben wurde.** G-OPS-03/C-03, C-04 und C-05 tragen `evidence_level: "E-3"` — die Messteile des Drift-Monitorings, seit SPEC-04. Gemeint war „kein Check auf E-1"; geschrieben wurde eine Aussage über die ganze Achse, und die traf nicht zu.

**Warum nichts anschlug.** `README_COUNTS_CURRENT` prüft, ob die *Zahlen* des README zum Repository passen — Gates, Checks, Regeln, Tests, Requirements, der DoD-Stand, die Schema-Version, die genannten Technologien. Es prüft keine Aussage über `evidence_level`. Die Zeile „14 of 51 checks carry one today" war gedeckt und stimmte; der Halbsatz dahinter war ungedeckt und stimmte nicht. Die beiden standen nebeneinander.

| | |
|---|---|
| Was geprüft war | die Zahl 14 von 51 |
| Was nicht geprüft war | was diese 14 aussagen |

**Der Wächter, und was er bewusst nicht kann.** `README_EVIDENCE_CLAIMS_CURRENT` (MEDIUM) leitet die Verteilung aus den Gate-Dateien ab und verlangt **einen** daraus gebildeten Satz wörtlich im README — heute „no checks at E-1, 3 at E-3, 11 at E-0, and 37 without a level". Steigt ein Check auf eine andere Stufe, ändert sich der erwartete Satz und der Anker fehlt. Dazu ein enger Widerspruchsdetektor für genau die Satzform, die hier versagt hat: „no/none … above E-0" darf nicht dastehen, solange ein Check über E-0 liegt.

Beides wurde in beide Richtungen gegengeprüft: die Aussage absichtlich wieder falsch gemacht (rot, beide Befunde), zurückgestellt (grün) — und zusätzlich von der anderen Seite, indem C-02 versuchsweise wieder auf E-1 gesetzt wurde: der Check meldete „does not state '1 check at E-1, 3 at E-3, 10 at E-0…'", also den korrigierten Stand des Katalogs. Ein Wächter, der nur die Textseite hält, hätte das durchgelassen.

**Nicht versucht:** die Prosa semantisch zu prüfen. Genau ein Satz ist wortgebunden, der Rest bleibt frei formulierbar. Ein Check, dessen Urteil von Auslegung abhängt, wird diskutiert statt repariert.

> Die Lehre über H4.19 hinaus: dort war zu fragen, **wo überall** ein Mechanismus wirken muss. Hier ist zu fragen, **ob die Korrektur selbst** einen Gegenstand hat. Eine Richtigstellung ohne Wächter ist eine neue Behauptung — und sie ist gefährlicher als die alte, weil sie wie eine Prüfung aussieht.

## H4.23 Der Wächter gegen unauffindbare Verweise war selbst einer (B-20)

`DOC_REFERENCES_ARE_TRACKED` entstand in T-02 gegen einen konkreten Befund: HANDBUCH und HISTORIE lagen außerhalb des Repos, vierzig getrackte Dateien verwiesen darauf, und ein Klonender fand Verweise auf Dokumente, die es bei ihm nicht gab. Der Check fand diesen Fall — 41 Befunde vor dem `git add`, grün danach. Beide Läufe sind dokumentiert.

**Und er hatte denselben Fehler.** Stufe 1 löste einen genannten Dateinamen so auf:

```python
candidate = REPO_ROOT / name          # nur die Wurzel
if candidate.is_file(): ...
elif name in ("HANDBUCH.md", "HISTORIE.md"): ...   # der Rest: hartkodiert
```

Damit prüfte er zwei Fälle: Dokumente in der Wurzel, und zwei namentlich eingetragene. Alles andere lief durch. Der Beleg lag im selben Repo: **AGENTS.md verwies auf ein Kandidaten-Mapping, das nur unter `legacy/` existiert und von `.gitignore` ausgeschlossen ist** — genau die Klasse, gegen die der Check gebaut war, und er meldete grün.

| | |
|---|---|
| Was der Check behauptete | „every document a tracked file names is tracked" |
| Was er prüfte | Dokumente in der Wurzel, plus zwei Ausnahmen |
| Was das strukturell ist | eine Annotation: ein Zustand wird behauptet, nicht belegt (SPEC-01 Abschnitt 2) |

**Warum die Gegenprobe in T-02 das nicht fing.** Sie wurde korrekt geführt — die Dokumente untracked (rot), getrackt (grün), ein erfundener Abschnittsverweis (rot), zurück (grün). Nur prüfte sie den Check **an dem Fall, für den er gebaut war**. Eine Gegenprobe, die den erwarteten Fall bricht, zeigt, dass der Mechanismus greift; sie sagt nichts über seinen Geltungsbereich. B-17 hatte dieselbe Lehre auf der Ebene der Aufrufer gestellt — „wo überall muss er wirken?" —, hier stellt sie sich auf der Ebene der Fälle: **wie viele Formen hat der Gegenstand, und deckt der Test mehr als eine ab?**

**Behoben in T-03:** Suche über den ganzen Baum nach Dateiname statt nur in der Wurzel, keine hartkodierten Namen mehr, pfadförmige Verweise ins eigene Repo, relative Links gegen ihre Quelldatei aufgelöst, `.gitignore` ausgenommen. Gegengeprüft in **beiden** Verweisformen — Name ohne Pfad und Pfad —, weil genau die Unterscheidung der blinde Fleck war.

**Drei weitere Funde fielen sofort an**, die vorher unsichtbar waren: ein Inventar kündigte drei Dokumente als Pfade an, bevor sie geschrieben waren, und benannte eine lokale Gutachten-Datei. Ein Wächter, der seinen Geltungsbereich verfehlt, verbirgt nicht einen Fall, sondern alle, die er nicht ansieht.

## H4.24 Ein Gate an einer unerwarteten Stelle (D-32)

SPEC-05 Teil 5 gibt G-OPS-05 einen zweiten Input: den Signaturnachweis. Beim Bauen zeigte sich, dass die Reihenfolge das nicht hergibt.

**Das Manifest entsteht aus der fertigen Kette.** Signiert wird also, nachdem alle Gates gelaufen sind. Ein Gate, das die Signatur des eigenen Laufs prüft, kann nicht vor ihr stehen — es gibt zu seinem Auswertungszeitpunkt nichts zu prüfen. Dazu kommt die Rechtefrage: GitHub Actions kennt `permissions` nur je Job, und `id-token: write` soll genau einem Job gehören, nicht dem gesamten Katalog.

**Drei Wege standen zur Wahl:**

| | Weg | Warum verworfen bzw. gewählt |
|---|---|---|
| **1** | **G-OPS-05 wandert in den signierenden Job** — `quality-gates` fährt die übrigen Gates, reicht Evidence-Store und Manifest als Artefakt weiter, `sign-evidence` signiert, verifiziert und wertet dann G-OPS-05 aus | **Gewählt.** Der Prüfgegenstand existiert, wenn geprüft wird; C-06 vergleicht den signierten Kopf mit dem Kopf zum Signaturzeitpunkt; die Rechteerhöhung bleibt in einem Job |
| **2** | **G-OPS-05 bleibt stehen und bewertet den Nachweis des VORHERIGEN Laufs** | Verworfen für C-04…C-07. C-06 („der signierte Kopf ist der Kopf der geprüften Kette") wäre per Konstruktion falsch und müsste entfallen oder umdefiniert werden — genau die Lücke, gegen die SPEC-04 „Messung vor Signatur" gesetzt hat, auf der Signaturseite wieder aufgemacht |
| **3** | **Gate und Policy jetzt, CI-Verdrahtung später** | Verworfen. Bis dahin liefe G-OPS-05 in der CI ohne seinen Pflichtinput — der Zustand, den B-17 beschreibt, und ein E-1-Anspruch, der genau dort nicht gilt, wo Images ausgeliefert werden |

> **Weg 2 kommt wieder, und dann ist er richtig.** Für die **Kettenkontinuität über Läufe hinweg** (SPEC-05 Abschnitt 13) ist „der Nachweis des vorherigen Laufs" nicht der Notbehelf, sondern der Gegenstand: dort lautet die Frage, ob zwischen zwei Läufen etwas fehlt. Für C-04…C-07 lautet sie, ob **dieser** Lauf signiert ist. Dieselbe Konstruktion, zwei verschiedene Aussagen — deshalb steht hier, warum sie an der einen Stelle falsch und an der anderen richtig ist.

**Die Selbstbezugsgrenze.** Der Evidence-Record von G-OPS-05 entsteht nach dem Manifest und liegt außerhalb dessen, was G-OPS-05 prüft. Ein Gate kann seinen eigenen Record nicht mitattestieren — eine Unterschrift umfasst sich nicht selbst. Das ist kein Versehen und wird nicht als Kleinigkeit behandelt: es steht in den `notes` des Gates, in SPEC-05 Abschnitt 6.3 und hier. **Wer es selbst entdeckt, hält es für einen Fehler; wem es gesagt wird, für Sorgfalt.**

Nebenbei fiel dabei eine Doppelung an, die vorher niemand sah: der Gate-Runner lag als Heredoc **in** einem Job. Zwei Jobs hätten zwei Kopien bedeutet, die auseinanderlaufen. Er liegt jetzt als `pipeline/ci/run_gate.sh` im Repo — eine Datei, zwei Aufrufer.

## H4.25 Der erste signierte Nachweis sagt „unknown" — und die CI wusste es besser (B-21)

Das erste Manifest, das eine echte Signatur trägt, enthält `"runtime_mode": "unknown"`.

**Der erste Befund war zu freundlich formuliert.** Er lautete: „die CI schreibt ihre Evidence-Records ohne expliziten Modus". Das stimmt und verschweigt das Entscheidende — **die CI kennt den Modus.** `eval_runner.py` liest `scribe_mock_mode` aus der laufenden Anwendung, und der Workflow bricht ab, wenn dort etwas anderes als `mock` steht: ein `live` aus dem Runner wäre ein Befund, kein Fortschritt. Gemessen, geprüft, und beim Schreiben des Records nicht mitgegeben.

`record_evidence.py` verhält sich dabei genau richtig: Fehlt der Modus in Parameter und Quelldokument, ist er `unknown` und niemals `live` — ein stillschweigendes „live" wäre die eine Annahme, die dieses Feld verhindern soll. Die Lücke ist also **eine fehlende Variablenübergabe, kein fehlender Mechanismus.** Das macht sie nicht größer, sondern peinlicher.

**Die Signatur macht den Mangel nicht schlimmer — sie macht ihn haltbar.** Bis hierher war „unbekannt, ob ein echtes Modell lief" eine Zeile in einer Datenbank, die mit dem Runner verschwand. Jetzt ist es eine signierte, im Transparenzlog verankerte Aussage mit Herkunft und Zeitpunkt. Daran wird gut sichtbar, was E-1 leistet: die Beweisstufe sagt, wer etwas wann behauptet hat, nicht ob die Behauptung gut ist. Ein signierter Zweifel bleibt ein Zweifel — er ist nur nicht mehr abstreitbar.

**Behoben am 02.09. (T-08).** Der Messschritt veröffentlicht den Modus, den er ohnehin prüft; Gate-Job und Signier-Job reichen ihn an jeden Record und an das Manifest weiter und brechen ab, wenn die Übergabe leer ankommt. Der Signier-Job **empfängt** ihn, statt einen zweiten abzuleiten — eine zweite Ableitung würde nicht messen, sondern raten. Nichts wurde nachgeschrieben: Records unterhalb des Cutoffs behalten `unknown`. Beleg: Lauf 33632326597, signiertes Manifest mit `"runtime_mode": "mock"`, alle 17 Records ebenso.

**Der Wächter brauchte drei Anläufe.** `RUNTIME_MODE_VISIBLE` prüfte zunächst nur, dass etwas den veröffentlichten Wert *liest* — und blieb grün, als die Zeile gelöscht wurde, die ihn *schreibt*: die Leser standen noch da und verwiesen auf einen Wert, den es nicht mehr gab. Derselbe Fehlertyp wie B-20, eine Ebene kleiner. Er prüft jetzt Erzeuger und Verbraucher.

> **Und noch etwas zeigt der Fall.** Der Befund entstand beim Lesen eines Artefakts, nicht beim Lesen von Code. Erst als das Manifest heruntergeladen und Feld für Feld angesehen wurde, fiel auf, dass dort etwas steht, was der Lauf besser wusste. Ein Nachweis, den niemand aufschlägt, prüft sich nicht selbst.

# TEIL H5 — Diff zur Masterarbeit


# TEIL 8 — Diff zur Masterarbeit

## 8.1 Was unverändert übernommen wird

- Die **fünf Design-Knowledge-Bausteine E1–E5** — sie sind rechtsstands-unabhängig formuliert
- Die **Design-Prinzipien DP1–DP5**
- Das **7-Attribut-Gate-Template** als Standardisierungseinheit
- Die **sechsstufige Traceability-Kette** Norm → Requirement → Gate → Säule → Policy → Evidence
- Der **Evidence Store** mit Schema-Trennung, RLS und Hash-Chain
- Der **Drift-Detektor** — er ist bereits die Referenzimplementierung für E-3
- Die **Testarchitektur** mit Integrity-Regression

## 8.2 Was sich ändert

| Was | Vorher (Masterarbeit) | Jetzt | Grund |
|---|---|---|---|
| **Rechtsstand** | März 2026 (Limitation L6) | Nach VO (EU) 2026/1744 | Omnibus hat Art. 10, 11, 25, 27, 43, 49, 72 geändert |
| **Rollen-Scope** | Deployer-only (Art. 26), Retirement ausgeschlossen (L2) | Rolle als **Architekturparameter**: PROVIDER / DEPLOYER / BOTH | Anwendungsfall verlangt beide Seiten |
| **Severity** | auf Gate-Ebene | auf **Check-Ebene** | Heterogene Prüfgegenstände wurden auf die schwächste Severity gezogen |
| **Klassifikation** | Art. 6 ohne Abs. 1a–1c | Vierstufiger Prüfbaum mit nicht überspringbarem Ausfallfolgen-Test | Neue Absätze und geänderte Legaldefinition |
| **Bias-Gate R013** | SHOULD, begründet mit „Deployer-Pflicht weniger explizit" | ~~Neubewertung~~ **REVIDIERT in v0.3 — SHOULD bleibt** | ~~Art. 4a Abs. 2 nennt Betreiber von Hochrisiko-Systemen ausdrücklich — die Herabstufungsbegründung ist entfallen~~ · **Am deutschen Wortlaut geprüft: die Schlussfolgerung trägt nicht.** Art. 4a Abs. 2 nennt Betreiber zwar ausdrücklich, endet aber mit: „Dieser Absatz begründet keine Verpflichtung, eine solche Erkennung und Korrektur von Verzerrungen vorzunehmen." Art. 4a ist eine **Erlaubnisnorm** — er räumt eine datenschutzrechtliche Schranke aus dem Weg, statt eine Bias-Pflicht zu begründen. Die ursprüngliche Begründung bleibt intakt. Dokumentiert in `requirements/R013.yaml` v0.6. |
| **Plattform** | Azure AKS als Instanziierung | Souverän, Open Source, ohne Vendor-Lock-in | Projektziel |
| **Lizenz** | CC BY-NC 4.0 | Apache 2.0 — **umgesetzt 15.08.** (`6319943`) | CC BY-NC ist nach OSI-Definition keine Open-Source-Lizenz. Nicht rückwirkend: Zenodo-Archiv und `thesis-v1.0` bleiben CC BY-NC. |
| **Domäne** | Healthcare (Ambient AI Scribe) | Netzbetrieb (Redispatch), Healthcare bleibt als erste Vignette | Branchenwahl |

## 8.3 Was neu ist

| Neu | Beschreibung |
|---|---|
| **E6 — Evidenz-Ebenen-Modell** | Zweite Klassifikationsachse: nicht „wie automatisiert", sondern **„wie beweiskräftig"**. Eigener Beitrag, in keinem bekannten Governance-Werkzeug explizit geführt. |
| **Normenraum-Aufnahmeregel** | Prüfbarkeit am KI-Lebenszyklus als Aufnahmekriterium statt einer Normenliste |
| **Rollenparameter** | Rolle als expliziter Architekturparameter mit rollenabhängiger Gate-Aktivierung |
| **Art.-25-Gate im Katalog** | Aus `prospective/` in den regulären Katalog, mit differenzierten Severities und den neuen Übergabeartefakten aus Art. 25 Abs. 2 und 4 |
| **Die Kopplung Art. 6 ↔ Art. 26 Abs. 2** | Die Einstufung als Sicherheitskomponente hängt an der Wirksamkeit der Aufsicht |
| **Richtung B — Lieferanten-Evidenz** (neu in v0.2) | B1: Deckungsprüfung der Betriebsanleitung gegen Art. 13. B2: Übergabepaket nach Art. 25 Abs. 2 lit. a–c inkl. Prüfung auf die Opt-out-Klausel. Plus Beschaffungs-Checkliste als vorgelagerter Prüfpunkt. |
| **Provider-Requirements** | Zweite Ableitung aus Art. 16 lit. a–l — **noch nicht begonnen, größter offener Block** |

## 8.4 Was bewusst wegfällt

- Der methodisch saubere **Einzel-Rollen-Schnitt** — bewusst aufgegeben, Komplexität steigt
- Der **Azure-PoC als Produktbasis** — bleibt Referenz für die Funktionslogik
- Die **zeitliche Dringlichkeitsargumentation** des Abstracts („ab August 2026") — durch die Fristenverschiebung entwertet; die Anforderungsbasis bleibt

## 8.5 Reproduzierbarkeit der publizierten Fassung — REVIDIERT in v0.2

> **v0.1 sagte:** „Vor der ersten Änderung ist ein Git-Tag `thesis-v1.0` zu setzen." **Das ist überholt.**

**Befund:** `thesis-v1.0` **existiert bereits** → `32804b5` (06.07.2026). **Aber die Versionierung ist inkonsistent:** `thesis-v1.0` zeigt auf einen **späteren** Commit als `v2.0.0` (29.05.2026) und `v1.1.0` (30.04.2026). `CITATION.cff` führt `version: 2.0.0`, `date-released: 2026-05-29` und **drei DOIs**.

**Status: VERTAGT** (Entscheidung 14.08.2026).

| | |
|---|---|
| **Nicht blockiert** | Branch anlegen · `.gitignore` ergänzen · SPEC-01 bis 03 umsetzen |
| **Blockiert** | jeder **neue Release-Tag** · jeder Zenodo-Push |

> Solange offen: **Die Reproduzierbarkeit der Publikation ist nicht eindeutig belegbar.** Der Punkt darf nicht stillschweigend verfallen. Zu klären ist, welcher Commit-Stand dem entspricht, was in der eingereichten Arbeit zitiert wird (14 Requirements, 16 Gates, 10 AUTO / 6 HYBRID / 0 MANUAL, 108 Regeln, 141 Unit-Tests).

---


---

# TEIL H6 — Außenwirkung und Begriffsanschluss


# TEIL 12 — Außenwirkung und Begriffsanschluss (neu in v0.6)

## 12.1 Warum der Begriffsanschluss dokumentiert wird

Ein Artefakt, dessen Fachbegriffe nicht anschlussfähig sind, wird nicht gefunden und nicht eingeordnet — auch fachlich nicht. Die Frage ist deshalb nicht kosmetisch: sie entscheidet, ob ein Leser die E6-Achse als das erkennt, was sie ist, oder als Eigenbegriff überliest. Das ist keine Marketingfrage, sondern die Umsetzungsseite der Zielrollenwahl.

## 12.2 Die Begriffslücke, maschinell geprüft

Im gesamten Repo kamen vor der Überarbeitung **null Mal** vor: `ISO 23894` · `AI Management System` · `AI Assurance` · `Responsible AI` · `Continuous Compliance` · `AI-Register` · `Model Validation`. `Compliance-as-Code` stand zweimal im Repo und **kein einziges Mal im README**.

Die Substanz deckte diese Begriffe ab. Die Beschriftung nicht. Behoben durch eine dreisprachige Übersetzungstabelle im README (Repo-Begriff → englischer Fachbegriff → deutscher Fachbegriff).

## 12.3 ISO 42001 und 23894 — Einordnung, kein Mapping

Die eigene Annex-A-Kompilation markiert alle 38 Controls als *„Knowledge-based; verify Tier 2/0"* — der Normtext ist kostenpflichtig und wurde nicht abgerufen.

> **Würde das README ISO-Control-IDs als geprüftes Mapping führen, wiederholte es genau den Fehlertyp, den SPEC-04 aus dem Code entfernt hat.** Entscheidung 6.10 gibt die Antwort bereits vor: Verankerung auf frei zugänglichen Primärquellen, ISO nur als Klauselverweis am Rand. Im README als *placement* formuliert, mit offengelegter Begründung.

## 12.4 Was am README geändert wurde

526 → 328 Zeilen, Commit `2af04a2`. Kern:

- **Kopf positioniert, Rumpf dokumentiert** — geschichtet, nicht ersetzt. Es ist beides
- **„At a glance"**: Disziplin · Regulierung · Standards-Kontext · Technologie · Idee · Ziel business-ready
- **Zwei Mermaid-Diagramme** statt eines PNG-Exports: Kette Norm → Evidenz mit Marktbegriffen am Rand, plus NIST-AI-RMF-Einordnung der Gates
- **„Open points" von 80 % auf 18 %** der Datei — direkt hinter „Status". Was gebaut ist, gefolgt von was nicht
- **Falschangaben entfernt**: LangChain (0 Treffer im Code), ArgoCD (5, alle Kommentare), OpenTelemetry (1), tote Pfade, drei widersprüchliche Testzahlen
- **Integrity-Check `README_COUNTS_CURRENT`** — die Zahlen werden aus dem Repo abgeleitet und müssen wörtlich im README stehen

> **Der Check ist der eigentliche Punkt.** Die alten Zahlen sind *trotz* Sorgfalt veraltet. Richtigkeit durch Sorgfalt herzustellen funktioniert nachweislich nicht; sie muss geprüft werden. Dasselbe Prinzip, das das Artefakt nach außen vertritt, jetzt auf sein eigenes Schaufenster angewandt.

---


---

# TEIL H7 — Forschungsstand


# TEIL 5 — Forschungsstand

**Quellenlage:** Neun Recherchestränge über Consensus, Stand 13.08.2026, jeweils mit Tier-Einordnung. **Alle sind als „Sichtung" gekennzeichnet, keiner als final bewertet.**

> **Datenpflege-Hinweis:** `lifecycle-integration.md` und `lifecycle-governance-agentic-genai.md` sind inhaltlich **identische Dubletten** — identischer Header, identische Queries, identische Quellen, einziger Unterschied ist die Überschrift. Ohne Bereinigung wird jede Lifecycle-Quelle doppelt gezählt. **Eine der beiden gehört gelöscht.**

## 5.1 Die acht wiederkehrenden Befunde

**1 — Die Kernlücke.** Die Schnittmenge aus **EU-Cloud-Sovereignty × technischer AI-Governance-Automatisierung** wird in sechs von sieben inhaltlich verschiedenen Recherchesträngen ausdrücklich als in der Literatur nicht vorhanden markiert. Einziger partieller Gegenbeleg: **Rashid et al. (2026)**, Industrial-Control-/OT-Kontext, nicht explizit EU-Souveränität.
→ **Das ist zugleich das konsistenteste Motiv des Korpus und die zentrale unvalidierte Hypothese des Projekts.** Ein Argumentum ex silentio ist kein Befund.

**2 — Organisation schlägt Technik.** In mindestens vier Strängen. Ye (2026): Awareness ist stärkerer Prädiktor (**β = .486**) als Technologie-Reife (**β = .412**), Basis 847 MSMEs mit SEM + fsQCA und 32 Experteninterviews. de Almeida et al. (2025, QCA über 28 öffentliche Organisationen): Training korreliert am stärksten mit Governance-Reifegrad. Tudor et al. (2025, 27 EU-Staaten, **R² = 0,948**): ICT-Fachkräftedichte ist stärkster Prädiktor für Cloud-Adoption. Kennedy et al. (2026): Haupthindernis ist inkonsistente organisatorische Umsetzung, nicht fehlende Standards.

**3 — Technik allein reicht nicht.** Drei unabhängige Formulierungen desselben Risikos für ein rein technisches Produktnarrativ. Blancato et al. (2024): Technologie allein löst das Vertrauensdefizit zwischen EU-Regierungen und Hyperscalern nicht. Kanabar et al. (2026): viele GenAI-Sicherheitsrisiken sind **strukturell, nicht konfigurierbar** — reine Policy-Kontrollen reichen nicht. Joshi et al. (2026): **OPA/Rego, Cedar und XACML decken nur das Permit/Prohibit-Subset ab** — kein Obligation-Lifecycle-Management („nach Aktion X muss Y innerhalb von Z gemeldet werden").
→ **Das ist die direkteste Relativierung des eigenen Architekturansatzes im gesamten Korpus.**

**4 — KMU sind strukturell benachteiligt.** In vier Strängen: Cafiso (2026, Zertifizierungsnachweis), Judijanto (2025, administrativer Aufwand und fehlender Zugang zu regulatorischer Expertise), Hussein et al. (2026, HAIRA-Reifegradmodell explizit ressourcensensitiv), Kennedy et al. (2026, KMU-Barrieren beim NIST AI RMF).
→ **Nach der Adressatenwahl Netzbetreiber überträgt sich dieser Befund nicht mehr sauber** — siehe Teil 6.4.

**5 — Konformität ≠ Wirksamkeit.** Aus drei Richtungen. Surve et al. (2026): im synthetischen Audit **89,9% der Zeilen konform, aber nur 34,3% davon mit hoher Assurance-Stufe**. Frimpong (2026): „Paper Compliance" — formal abgeschaltet, faktisch weiterwirksam. El Arab et al. (2026, Scoping Review of Reviews über 25 Review-Publikationen): „normativ-operative Lücke" — Empfehlungen sind weiter als die Evidenz zur tatsächlichen Umsetzung.

**6 — Frameworks sind komplementär, und Cross-Framework-Mapping ist automatisierbar.** Younas, Lestari, Filani, Tekeste, Arora und Rashid mappen jeweils drei bis fünf Regelwerke gegeneinander. Song et al. (2026) belegen die maschinelle Machbarkeit mit **98,63% Übereinstimmung** zum Experten-Mapping und **60% mehr validen Controls** als der manuelle Baseline. Golpayegani et al. (2023) und Sabaliauskaitė et al. (2026) liefern die ontologische Methodik (RDF/Turtle, SPARQL).
→ **Der methodisch am breitesten abgestützte Produktbaustein im gesamten Korpus.**

**7 — Das Lifecycle-Ende ist die anerkannte Forschungslücke.** Indaryani (2026): nur **sieben peer-reviewte Studien** zu tatsächlich zurückgezogenen KI-Systemen. Frimpong (2026): „AI Debris" — Residualrisiko nach Abschaltung. Puri (2026): Lifecycle-Governance für Deployment und Retirement ist die am schwächsten ausgeprägte Dimension.

**8 — Regulatorische Fragmentierung ist quantifiziert.** Akekudaga et al. (2025) prüfen eine AI-Analytics-Plattform gegen fünf Datenschutzregime: **43–60% Überlappung, aber 5–33% jurisdiktionsspezifische Anforderungen.** Xu (2026, 12 multinationale Firmen, 48 Interviews, 500 kodierte Events): EU-Firmen zeigen die höchsten Bifurkationswerte (**0,84 ± 0,06**) — Fragmentierung treibt nachweislich Architekturentscheidungen.
→ **Gegenposition der Datei selbst:** Diese Zahlen stammen aus einer einzelnen Studie mit einer Beispielplattform; Generalisierbarkeit ist nicht belegt.

## 5.2 Was ausdrücklich Hypothese bleibt

- Die Marktlücke „Cloud-Sovereignty × technische AI-Governance" — in drei Dateien wörtlich als „weder belegt noch widerlegt" markiert
- Die Portabilität von Compliance-as-Code über Jurisdiktionen — Einzelstudie
- **Michels et al. (2023) als Gegenposition zur Projektprämisse:** Nationalitätsanforderungen an Cloud-Provider wären unverhältnismäßig; empfohlen wird Cybersecurity-Risikomanagement statt EU-only-Zwang
- **Blancato et al. (2024) als eingepreistes Risiko:** Die Trust-Deficit-These widerspricht potenziell einem rein technisch-zentrierten Lösungsansatz

## 5.3 Quellen mit markierter methodischer Schwäche

Nicht als Kernevidenz verwenden: **Hofer et al. (2024)** — „Unknown Journal", Verifikation nötig, obwohl direkteste Business-Modell-Relevanz. **Pervez et al. (2025)** und **Eisenberg et al. (2025)** — ArXiv-Preprints, Tier 2. **Pasupuleti (2023)** — MTTR-Reduktion 60–85% in *synthetischer* Evaluation. **Alevizos (2024)** — simulationsbasiert validiert trotz 60 Zitationen. **Nangi et al. (2025)** — 65% Reduktion behauptet, nicht unabhängig verifiziert. **Li (2026)** — Knowledge-Graph teilweise mit simulierten Provisions. **Rashid et al. (2026)** und **Kanabar et al. (2026)** — Volltext-Lektüre empfohlen, bevor die Befunde weiterverwendet werden.

---


## H7.1 Der nächstliegende publizierte Ansatz — und was er über E6 sagt (27.08.2026)

**Buscemi, A.; Deckenbrunnen, T.; Kabir, F.; Mishchenko, K.; Mowla, N. (2025):** *Assessing High-Risk AI Systems under the EU AI Act: From Legal Requirements to Technical Verification.* arXiv 2512.13907, eingereicht bei ACM. Volltext gelesen.

Gefunden im eigenen Zotero-Ordner „AI and legal AI systems", dort bereits als `CoreCandidate` getaggt. **Das ist die direkteste Vergleichsarbeit zum eigenen Kernartefakt, die bislang identifiziert wurde** — näher als Butt et al. (2026) oder Nweke et al. (2026).

### Was sie tun

Sie zerlegen die AI-Act-Anforderungen in operationalisierbare Sub-Requirements und ordnen jeder eine **Verifikationsaktivität** zu, aufgespannt über zwei orthogonale Achsen:

| Achse | Werte |
|---|---|
| **Verification type** | `controls` (prozessbasierte Absicherung) · `testing` (empirische Evaluation) |
| **Verification target** | `data` · `model` · `processes` · `product` |

Verankert auf ISO/IEC **42001** (25 Nennungen), **23894** (17), 27005, 27001, 5259, 24029, 22989. Fallstudie: Intrusion Detection in vernetzten Fahrzeugen, mit **Scania**.

### Was das für den eigenen Anspruch bedeutet — der wichtigste Satz

Die E6-Neuheitsbehauptung lautete bisher *„in keinem bekannten Governance-Werkzeug explizit geführt"* — ein **Argumentum ex silentio**, gegen das das Handbuch selbst warnt (2.3).

Sie ist jetzt **teilgeprüft und schärfer**, denn die Arbeit hat eine Typ-Achse und erklärt sie ausdrücklich für **nicht** rangig:

> „Controls and testing are complementary rather than **hierarchical**: controls establish accountability and traceability, while testing provides empirical evidence of compliance."

| | Buscemi et al. | E6 |
|---|---|---|
| Werte | 2, binär | 4, geordnet |
| Ordnung | **ausdrücklich keine** | **nach Fälschungskosten** |
| Frage | *welche Art* von Nachweis | *wie schwer zu fälschen* |

> **Das ist die stärkste Stützung, die der E6-Anspruch bisher hat.** Nicht weil niemand in die Nähe kommt — jemand kommt sehr nah —, sondern weil der Nächstliegende die Rangordnung **explizit ablehnt**. Damit ist der Beitrag nicht mehr „das hat noch keiner gemacht", sondern: *„der nächstliegende Ansatz unterscheidet Kontrolle von Test und stellt sie bewusst gleichrangig nebeneinander; E6 ordnet sie stattdessen nach Fälschungskosten."* Das ist zitierbar und angreifbar — beides besser als unwiderlegbar.
>
> Ihr „controls vs. testing" entspricht ungefähr E-0 gegen E-3. Was fehlt, ist alles dazwischen: die Signatur (E-1) und der beobachtete Systemzustand (E-2) — und damit die Aussage, dass ein Test *auch* wertlos sein kann, wenn seine Zahl aus einer Handdatei stammt.

### Zweiter Befund: Art. 73 ist unbesetzt

`serious incident` kommt im gesamten Volltext **nicht vor**. `threshold` nur zweimal, beide Male zu Modellkalibrierung und Audit-Nachverfolgung — nie zur Frage, **ab wann ein Vorfall meldepflichtig** ist.

> Die Schwellenwertfrage aus H4.13 ist damit auch in der nächstliegenden Arbeit unbesetzt. Das ist kein Beweis für eine Marktlücke, aber es ist mehr als vorher: die Arbeit, die den Anspruch hätte erheben können, erhebt ihn nicht.

### Dritter Befund: die ISO-Verankerung ist ein methodischer Unterschied, keine Auslassung

Sie verankern schwer auf ISO. Das eigene Projekt tut das bewusst **nicht** (D-21): frei zugängliche Primärquellen, ISO nur als Klauselverweis, weil ein Crosswalk auf kostenpflichtigen Normtext für Leser ohne die Norm nicht überprüfbar ist.

**Beides ist vertretbar, und der Unterschied gehört benannt statt kaschiert.** Ihre Zuordnung ist reichhaltiger; die eigene ist für einen Leser ohne ISO-Lizenz nachprüfbar. Dass eine ernstzunehmende Arbeit **ISO/IEC 23894** neben 42001 führt, bestätigt zudem die Aufnahme von 23894 in die Außendarstellung (H6).

### Was zu tun bleibt

- **Zitieren, nicht ignorieren.** Die Arbeit gehört in den ersten Fachbeitrag und in die Thesis-Fortschreibung — als nächstliegender Stand der Technik, gegen den E6 sich abgrenzt
- Die restlichen Dokumente des Zotero-Ordners sind **noch nicht gesichtet** — dieser eine war der einschlägigste Treffer, nicht der einzige
- Die Marktlücken-Hypothese (H7, Befund 1) bleibt im Übrigen unvalidiert; geprüft wurde **eine** Achse, nicht die These


---

# TEIL H8 — Risiken und Gegenpositionen


# TEIL 10 — Risiken und Gegenpositionen

| Risiko | Substanz |
|---|---|
| **Selbstauskunft bleibt die Angriffsfläche** | Solange Gates JSON-Felder statt Systemzustand prüfen, besteht jeder Betreiber jedes Gate durch korrektes Ausfüllen. E6 adressiert genau das. |
| **Policy-Kontrollen reichen strukturell nicht** | Kanabar et al. (2026): viele GenAI-Risiken sind strukturell, nicht konfigurierbar. Joshi et al. (2026): OPA/Cedar/XACML decken nur Permit/Prohibit ab. **Direkte Relativierung des eigenen Ansatzes.** |
| **Die Kernlücke ist ein Argumentum ex silentio** | „Keine Studie verbindet Sovereignty mit AI-Governance-Technik" ist eine Hypothese, kein Befund. Sie kann auch bedeuten, dass die Verbindung uninteressant ist. |
| **Gegenposition zur Projektprämisse** | Michels et al. (2023): Nationalitätsanforderungen an Cloud-Provider wären unverhältnismäßig; empfohlen wird Cybersecurity-Risikomanagement statt EU-only-Zwang. |
| **Trust-Deficit** | Blancato et al. (2024): Technologie allein löst das Vertrauensdefizit EU↔Hyperscaler nicht. Als eingepreistes Risiko vermerkt. |
| **Konformität ≠ Wirksamkeit** | Surve et al. (2026): 89,9% konform, aber nur 34,3% mit hoher Assurance. Gilt auch für das eigene Artefakt. |
| **AIBOM-Verfügbarkeit unbelegt** (neu) | Ohne Nachweis, dass Anbieter maschinenlesbare Nachweise liefern, bleibt die Zielstufe von Richtung B Theorie. |
| **Nähe zur Rechtsberatung** (neu) | Eine Beschaffungs-Checkliste ist inhaltlich nah an Rechtsberatung. Abgrenzung nötig — beschreibend, nicht empfehlend. |

---


---

# TEIL H9 — Fassungsgeschichte des Handbuchs


> Die Änderungstabellen der Fassungen v0.1 bis v0.6, bevor der Schnitt in Handbuch und Historie erfolgte. Ab v0.7 werden Änderungen hier fortgeschrieben.


### 0.5 Änderungen von v0.5 auf v0.6

> Diese Fassung trägt die **Umsetzung von SPEC-04** nach — erstmals nicht Analyse, sondern erledigte Arbeit — sowie drei Befunde, die erst der Lauf gegen die **echte App** zutage gefördert hat. Dazu die Positionierungsarbeit am README und ein Strukturbefund über dieses Handbuch selbst.

| Nr. | Was | Wo |
|---|---|---|
| 1 | **SPEC-04 vollständig umgesetzt und gepusht** (`9afc47d`), CI grün. Teil 11 „Sofort" 1–4 erledigt | 9.2, 11 |
| 2 | **Messproblem, das nur der echte Lauf zeigte:** Histogramm-Buckets waren fehldimensioniert — der gemeldete p95 war eine Konstante | neu 7.9 |
| 3 | **Neu: exakter Mittelwert** aus `_sum`/`_count` — der erste Latenzwert ohne Interpolation | 7.9 |
| 4 | **Neu: `latency_p95_resolution`** — die Schwäche der Messung selbst maschinenlesbar. E6 eine Ebene unter der Feldebene | 7.9 |
| 5 | **Eigener Fehler benannt:** die in SPEC-04 zugesagte Erzwingung des Messdokuments wurde nicht implementiert. Ein MUST-Check, den man durch Weglassen des Inputs umgeht, ist kein MUST | 7.9, 9.2 |
| 6 | **Befund in der eigenen CI:** der Workflow meldet „173/173 green", während 187 Tests liefen — strukturell derselbe Fehler wie `gate_result.all_passed` | neu 7.10 |
| 7 | **SPEC-04b geschrieben** — die CI misst wirklich; K8s bleibt bewusst später | 9.2, 11 |
| 8 | **Klärung: „funktionsfähig" hängt nicht an Kubernetes.** Nur E-2 braucht den Cluster; E-3 braucht eine laufende App, E-1 sogar eher die CI | neu 7.10 |
| 9 | **README als Positionierungsdokument überarbeitet** — Fachbegriffe des Marktes, Jobkategorien belegt statt vermutet | neu 12 |
| 10 | **Strukturbefund über dieses Handbuch** — die Pflegeregel erzwingt monotones Wachstum; Vorschlag für einen Schnitt | 0.6 |

---

### 0.6 Zum Handbuch selbst — offener Strukturvorschlag (neu in v0.6)

> **Das Handbuch wächst monoton, weil die Pflegeregel es erzwingt.** v0.4: 929 Zeilen. v0.5: 1016. Pro Fassung rund 90 dazu. Als Forschungsprotokoll ist das richtig — als Datei, die zu Beginn jeder Arbeitssitzung gelesen wird, wird es zum Kostenfaktor.

Die Ursache ist kein Redaktionsfehler, sondern **ein Dokument mit zwei Aufgaben, deren Anforderungen einander widersprechen:**

| Aufgabe | Anforderung |
|---|---|
| Entscheidungsregister, Begründungskette | muss wachsen, nichts darf verschwinden |
| Einstiegskontext für eine neue Sitzung | muss klein bleiben, nur der aktuelle Stand |

Dasselbe Muster wie beim README (Doku **und** Positionierung) und wie bei den Gates (deklariert **und** durchgesetzt). Die Auflösung ist dort jeweils **Schichtung**, nicht Verzicht.

**Vorschlag, nicht entschieden:** `HANDBUCH.md` auf den operativen Stand kürzen (Teile 1–4, 6, 7, 9.1, 11 — rund 250 Zeilen), alles Revidierte, die Änderungstabellen 0.1–0.5 und die erledigten Punkte nach `HANDBUCH-HISTORIE.md`. **Nichts wird gelöscht, es wird verschoben** — damit bleibt die Pflegeregel erfüllt, statt gebrochen zu werden. Präzedenz existiert: `AGENTS.md` im Repo ist bereits ein kleines, stabiles Dauerkontext-Dokument.

**Gegenposition, die mitgedacht gehört:** Zwei Dateien können auseinanderlaufen. Genau das ist bei `lifecycle-integration.md` ≡ `lifecycle-governance-agentic-genai.md` schon passiert (siehe Teil 5). Ein Schnitt braucht deshalb eine Regel, welche Datei bei Widerspruch gilt — analog zu Teil 0 („bei Widersprüchen gilt die Einzeldatei").

---

### 0.4 Änderungen von v0.4 auf v0.5

> Diese Fassung trägt nach, was beim **Schreiben des Umsetzungsauftrags SPEC-04 am Code gefunden wurde**. Kein neuer Rechercheschritt, keine neue Entscheidung — drei Befunde, die die Analyse aus v0.4 an entscheidender Stelle verschärfen, und eine Korrektur an einer eigenen Aussage aus v0.4.

| Nr. | Was | Wo |
|---|---|---|
| 1 | **`eval_results.json` widerspricht sich selbst** — dieselbe Metrik steht zweimal mit verschiedenen Werten in derselben Datei | 7.5 (1a) |
| 2 | **KORREKTUR an v0.4:** „der Drift-Detektor speist kein Gate" ist zu grob. Er schreibt Evidenz unter `G-OPS-03` **mit selbst gesetzter `decision`** — er umgeht die Policy-Ebene, statt sie nicht zu erreichen | 7.5 (2a) |
| 3 | **Die Drift-Annotation ist selbst der E-0-Angriffspunkt** — G-OPS-03 fragt „läuft Drift-Erkennung?" und prüft „behauptet jemand, dass sie läuft?" | 7.5 (2b) |
| 4 | **`policy_checks[].evidence_level` steht seit SPEC-01 überall auf `null`** — das Feld für die zweite Klassifikationsachse existiert und ist unbenutzt | 7.5 (3a), 7.8 |
| 5 | **Neu 7.8 — Provenance je Metrikgruppe.** E6 auf die Feldebene angewandt: `measured` / `derived` / `declared`. Macht die Behauptung nicht wahr, sondern **als Behauptung kenntlich** | neu 7.8 |
| 6 | **SPEC-04 geschrieben** — Teil 11 „Sofort" 1–3 als abarbeitbarer Auftrag, Reihenfolge nach Risiko statt nach Nutzen | 9.2, 11 |
| 7 | **Zwei Entwurfsentscheidungen begründet:** `mock_mode` gehört in den Orchestrator, nicht in 17 Policies; Mock erzwingt **kein** FAIL | 7.8 |
| 8 | Teil 11 redaktionell repariert (doppelte Überschrift „Danach", doppelte Nummer 5) | 11 |
| 9 | Ablageort des Handbuchs präzisiert — die Repo-Fassung ist gitignored und nur Arbeitskopie | 2.4 |

---

### 0.3 Änderungen von v0.3 auf v0.4

> Diese Fassung trägt die **Messgrößen-Analyse** nach: was im Betrieb tatsächlich gemessen wird, was nur behauptet wird, und was für Hochrisiko-Systeme fehlt. Anlass war die Frage, woher die geprüften Werte eigentlich kommen — die Antwort war unbequem.

| Nr. | Was | Wo |
|---|---|---|
| 1 | **Bestandsaufnahme der Live-Messungen** — sechs Metriken insgesamt, davon drei berechnet | neu 7.5 |
| 2 | **Befund: gemessene und geprüfte Werte berühren sich nicht.** `eval_results.json` ist eine Handdatei; die geprüfte Latenz hat nichts mit der gemessenen zu tun | 7.5 (1) |
| 3 | **Befund: der Drift-Detektor misst Latenz als Proxy** für die Eingabeverteilung — und fällt ohne App still auf eine fest kodierte Verteilung zurück | 7.5 (2) |
| 4 | **Befund: `scribe_mock_mode` liest kein Gate** — PASS im Mock-Betrieb ist möglich | 7.5 (3) |
| 5 | **Lückenanalyse: acht fehlende Messgrößen** für Hochrisiko-Betrieb | neu 7.6 |
| 6 | **Kernlücke benannt: ohne Ground Truth keine Genauigkeit im Betrieb** — und der Vorschlag, die Aufsicht nach Art. 14 als Label-Quelle für Art. 72 zu nutzen | 7.6 |
| 7 | **E-1 und E-2 technisch ausformuliert** — die E-Stufe steckt in der Herkunft des Inputs, nicht in der Regel. E-1 macht die Zahl nicht wahr, sondern den Erzeuger nachweisbar | neu 7.7 |
| 8 | **Neun neue offene Punkte**, Teil 11 nach der Analyse neu priorisiert: Verdrahtung vor Signatur | 9.2, 11 |
| 9 | Repo-Stand nachgetragen: Security-Review und Compliance-Audit abgearbeitet, CI repariert und gehärtet | 11 |

---

### 0.2 Änderungen von v0.2 auf v0.3

> Diese Fassung schreibt **Umsetzungsstände** fort. Inhaltlich neu entschieden wurde nichts — was hier steht, ist entweder erledigt, im Wortlaut geprüft oder als Befund aus der Umsetzung zurückgemeldet.

| Nr. | Was | Wo |
|---|---|---|
| 1 | **SPEC-01 bis SPEC-03 umgesetzt**, Branch angelegt, `specs/` eingecheckt, `.gitignore` ergänzt | 9.2, 11 |
| 2 | **Lizenzwechsel auf Apache 2.0 durchgeführt** — nicht rückwirkend, das Zenodo-Archiv und `thesis-v1.0` bleiben CC BY-NC | 8.2, 9.2 |
| 3 | **R013-Neubewertung REVIDIERT** — Art. 4a Abs. 2 ist Erlaubnis-, keine Pflichtnorm; SHOULD bleibt | 8.2 |
| 4 | **Terminologie korrigiert:** amtlich ist **„Sicherheitsbauteil"**, nicht „Sicherheitskomponente" | 3.1 |
| 5 | **Deutsche Sprachfassung teilweise abgeglichen** (Art. 3 Nr. 14, Art. 6 Abs. 1a–1c, Art. 25 Abs. 2/4, Art. 4a) | 9.2 |
| 6 | **Rollenzustand implizit entschieden** — pro Pipeline-Lauf, weil SPEC-03 vor der Klärung umgesetzt wurde | 9.2 |
| 7 | **Versionierungsbefund präzisiert** — `thesis-v1.0` liegt nach `v2.0.0`; Release-Tags bleiben blockiert | 8.5, 9.2 |
| 8 | **Neuer Befund aus der Umsetzung:** G-DEP-01 ist Betreiber-Gate, referenziert aber Art. 10/11 (Anbieterpflichten) | 9.2 |

---

### 0.1 Änderungen von v0.1 auf v0.2

| Nr. | Was | Wo |
|---|---|---|
| 1 | **Scope erweitert:** Pflichten-Prüfer (A) **und** Lieferanten-Prüfer (B), A zuerst | neu 6.7 |
| 2 | **Rechtsanker von B korrigiert** — Art. 25 Abs. 2/4 trägt den reinen Betreiber **nicht**; B zerfällt in B1 und B2 | neu 6.8 |
| 3 | **Marktbefund** zur Beschaffungslage (Anbietermarkt, Digital@EVU 2026) | neu 6.9 |
| 4 | **Art. 25 lit. c statt lit. b** als voraussichtlicher Haupttrigger | 6.5, 9.1 |
| 5 | **Crosswalk-Evidenzweg entschieden** — Verankerung auf frei zugänglichen Primärquellen | neu 6.10 |
| 6 | **Reihenfolge Klassifikationsregel/Vignette entschieden** — Redispatch zuerst, plus Negativfall | 6.5 |
| 7 | **Git-Tag-Punkt REVIDIERT** — von „sofort" auf **vertagt**, mit Folgenabgrenzung | 8.5, 9.2, 11 |
| 8 | Neue Risiken aufgenommen (Einkauf ≠ Compliance, AIBOM-Verfügbarkeit, Opt-out-Klausel) | 10 |

---


---

*Historie · Stand 25.08.2026 · Nur Ergänzung, keine Löschung · Keine Rechtsberatung*
