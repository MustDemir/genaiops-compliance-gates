# Handbuch — KI-Compliance-Kontrollsystem für Netzbetreiber

**Version 1.1 · Stand 1. September 2026**
Projekt „Cloud Architect AI Governance" · Mustafa Demir

---

## Teil 0 — Wie dieses Handbuch zu benutzen ist

**Zweck.** Dies ist der Einstieg. Wer nach einer Pause zurückkommt oder neu dazustößt, liest **diese Datei ganz** und ist danach handlungsfähig. Sie sagt, **was gilt** und **was als Nächstes zu tun ist**.

**Die Begründungen stehen in [`HISTORIE.md`](HISTORIE.md).** Warum eine Entscheidung so ausfiel, was einmal galt und revidiert wurde, welche Befunde am Code erhoben wurden, der Forschungsstand, die vollständige Normenreferenz — alles dort, mit stabilen IDs.

### 0.1 Der Schnitt vom 25.08.2026

Bis v0.6 war beides eine Datei, mit der Regel „Fortschreibung statt Neufassung". Sie wuchs monoton — 929 → 1016 → 1205 Zeilen — und wurde als Einstiegskontext untauglich.

> **Die Regel „eine Datei" ist aufgehoben. Ihr Kern gilt weiter, nur woanders:** Nichts wird gelöscht, Revidiertes bleibt sichtbar, die Begründungskette ist wichtiger als der Endzustand — **das gilt jetzt für `HISTORIE.md`**. Dieses Handbuch darf gekürzt und umgeschrieben werden; die Historie nur ergänzt.

### 0.2 Wann du zwingend in die Historie musst

Keine Empfehlung, sondern Auslöser. In diesen Fällen ist Weiterarbeiten ohne die Historie ein Fehler:

| Auslöser | Wohin |
|---|---|
| Du willst eine Entscheidung **revidieren** oder umgehen | `HISTORIE.md` H1, die betreffende `D-xx` |
| Du triffst auf einen **Widerspruch** zwischen zwei Zahlen oder Aussagen | H4, Befundregister — der Fall ist wahrscheinlich schon erhoben |
| Du willst eine **Rechtsaussage** verwenden oder veröffentlichen | H3 Normenreferenz **und** die Einzeldatei; Evidenzstufe prüfen |
| Du willst eine **Norm oder ein Framework** aufnehmen | H3, plus Aufnahmeregel 4.1 hier |
| Du berührst **Messung, Beweiskraft oder Evidence Store** | H4, `B-01` bis `B-12` |
| Du schreibst nach außen (Beitrag, README) | H6 Begriffsanschluss |
| Eine Aussage hier wirkt **veraltet** | H9 Fassungsgeschichte, dann korrigieren — nicht fortschreiben |

**Bei Widerspruch:** Für den *aktuellen Stand* gilt dieses Handbuch, für die *Begründung* die Historie. Widersprechen sich die Sachaussagen, ist das ein Fehler und gehört behoben, nicht ausgelegt. `check_handbuch_konsistenz.py` prüft, dass jede ID auf beiden Seiten existiert.

**Verhältnis zu den Einzeldateien.** Bei Widersprüchen gilt die Einzeldatei (`/compliance/`, `/research/`, `/architecture/`) — und der Widerspruch gehört behoben.

**Was dieses Vorhaben nicht ist:** kein Rechtsgutachten, keine Rechtsberatung, keine Publikation. Rechtsaussagen sind nach Verifikationsstand gekennzeichnet und vor jeder Veröffentlichung gegen Primärquellen zu prüfen.

---

# TEIL 1 — Das Vorhaben

## 1.1 In fünf Sätzen

Aus einer abgeschlossenen Masterarbeit existiert eine lauffähige Referenzarchitektur, die regulatorische Anforderungen als Quality Gates in CI/CD-Pipelines durchsetzt und die Nachweise in einem manipulationserkennbaren Evidence Store ablegt. Diese Architektur wird über den akademischen Stand hinaus zu einem business-ready Artefakt weiterentwickelt und auf eine konkrete Branche angewandt: **Netzbetreiber in der Energieversorgung**. Der Zweck des Kontrollsystems ist, **Konformität nachweisbar statt behauptbar** zu machen: jede regulatorische Anforderung wird auf einen Check abgebildet, jeder Check erzeugt einen Nachweis, und jeder Nachweis sagt, wie beweiskräftig er ist. Der inhaltliche Hebel ist eine Unterscheidung, die im Markt regelmäßig falsch gemacht wird: **wer schuldet welche Pflicht — der Anbieter oder der Betreiber**. Der methodische Hebel ist eine zweite Klassifikationsachse, die bislang niemand explizit führt: **wie beweiskräftig ist die Evidenz, die ein Gate erzeugt**.

## 1.2 Verwertungsform (D-05)

Das Artefakt wird **nicht als Produkt** betrieben: kein SaaS, kein Abonnement, kein Managed Service. Es ist eine Referenzarchitektur mit lauffähigem Nachweis, und diese Festlegung begrenzt, was gebaut wird — Mandantentrennung, Abrechnung und Betriebs-SLAs sind ausdrücklich nicht Gegenstand.

> **Begriffswarnung.** „B" bezeichnet in diesem Projekt zwei verschiedene Dinge: die **verworfene Verwertungsform** (Produktunternehmen, D-05) und ab 4.5 die **Richtung B (Lieferanten-Prüfer)** — ein Bestandteil des Artefakts. Immer ausschreiben.

## 1.3 Was es ausdrücklich nicht ist

Kein Produktunternehmen · nicht der Finanzsektor mit DORA · nicht der Maschinenbau (erzwänge die Anbieterperspektive) · **nicht Modellanbieter als Zielgruppe** (D-25). Der Adressat ist der **Betreiber** eines KI-Systems in der Energieversorgung; jede Zielgruppe, die das Artefakt in die Anbieterrolle zwingen würde, ist damit ausgeschlossen.

## 1.4 Der rote Faden

```
Masterarbeit (Artefakt)
   -> normagnostisches Gate-Kontrollsystem
      -> Normenpackungen (EU AI Act, NIS2, EnWG § 11 ...)
         -> Adressat Netzbetreiber
            -> Anwendungsfall Redispatch
```

---

# TEIL 2 — Arbeitsweise

## 2.1 Der oberste Grundsatz (D-04)

> **Die Masterarbeit ist NICHT Single Source of Truth. Sie ist Ansatzpunkt.**
>
> Kein Befund, keine Anforderung, keine Designentscheidung und keine Technologiewahl daraus gilt als gesetzt. Jeder übernommene Punkt wird geprüft auf **Aktualität · innere Logik · State of the Art · Sicherheit · Compliance**. Anspruchsniveau ist **business ready** — nicht PoC, nicht akademische Hinlänglichkeit. Was die Prüfung nicht besteht, wird verworfen oder neu gebaut, auch wenn es begutachtet ist.
>
> Der Grundsatz gilt auch für die eigene Arbeitsproduktion: Sekundärquellen werden gegen Primärquellen gegengeprüft. Abgelegte Aussagen werden **korrigiert statt fortgeschrieben**.

## 2.2 Die vier Modi

| Modus | Gegenstand | Quellenlogik |
|---|---|---|
| **RESEARCH** | Akademische Recherche, Forschungsstand | Peer-reviewed, Zitationszahlen, Tier-Einordnung |
| **COMPLIANCE** | Regulatorische Primärquellen (EUR-Lex, ENISA, BNetzA), Fristen | Primärquelle oder ausdrücklich als ungeprüft markiert |
| **BIZDEV** | Marktlücken, Zielgruppen, Positionierung | Immer mit eingebauter Gegenposition |
| **ENGINEER** | Architektur, Policy-as-Code, CI/CD/CT, Gate-Design | Lauffähig und getestet oder als Entwurf gekennzeichnet |

Akademische und regulatorische Evidenz werden **getrennt gehalten**.

## 2.3 Evidenzstufen

| Stufe | Bedeutung |
|---|---|
| **VERIFIZIERT** | Gegen die Primärquelle geprüft, wörtlich zitierbar |
| **SEKUNDÄRQUELLE** | Zuverlässig, aber nicht primär; vor Verwendung zu prüfen |
| **HYPOTHESE** | Eigene Auslegung; ausdrücklich nicht als Befund verwendbar |
| **REVIDIERT** | War einmal Stand, ist es nicht mehr; Begründung bleibt in der Historie |

**Keine erfundenen Quellen, DOIs, Zahlen oder Zitate.** Ein Argumentum ex silentio („keine Studie verbindet X mit Y") ist eine Hypothese, kein Befund.

## 2.4 Wie ein Gate entsteht — DoR, DoD, Wirkung

Ein Gate ist nie absolut fertig. Es ist **fertig auf einer erklärten Beweisstufe** — und muss diese Stufe aussprechen. Das folgt aus E6 (3.3): nicht jedes Gate muss E-3 erreichen, jedes muss die Stufe erreichen, die seine Pflicht verlangt.

### Definition of Ready — bevor gebaut wird

| # | Kriterium | Warum |
|---|---|---|
| 1 | Requirement **primärquellengeprüft** (EUR-Lex, nicht Volltextwiedergabe) | Sonst automatisierst du eine ungeprüfte Auslegung |
| 2 | **Rollenzuordnung** geklärt: Anbieter oder Betreiber | G-DEP-01 zeigt, was sonst passiert |
| 3 | **Datenquelle benannt und verfügbar** | Sonst endet es bei einer Annotation |
| 4 | Schwellenwerte gesetzt **oder** als offen deklariert mit Grund | Zustand von G-OPS-02 heute |
| 5 | **Negativfall benannt** | Ein Prüfbaum, der alles auf „ja" abbildet, beweist nichts |
| 6 | Verhältnis zu **parallelen Regimen** geklärt (NIS2, CER, EnWG, DSGVO) | Art. 73 Abs. 9 halbiert die Pflicht — teuer gelernt bei G-OPS-02 |

### Definition of Done — je Gate

| # | Kriterium | Geprüft durch |
|---|---|---|
| 1 | Alle fünf Fragen aus 3.4 beantwortet, **inkl. Frage 5** | ✅ `GATE_DECLARES_EFFECT` |
| 2 | Kein Check `design_only` | ✅ `GATE_IMPLEMENTATION_HONEST` |
| 3 | `evidence_level.current` erreicht die für die Pflicht nötige Stufe | ⬜ manuell |
| 4 | Laufzeitpflicht gedeckt **oder** deklariert | ✅ `TRIGGER_MATCHES_REQUIREMENT` |
| 5 | Inputs **erzeugt**, nicht eingecheckt | ✅ `REQUIRED_INPUTS_ENFORCED` |
| 6 | **Negativfall** getestet — ein grüner Lauf beweist nur, dass nichts blockiert | ⬜ manuell |
| 7 | Alle `acceptance_criteria` zeigen auf einen Check oder eine begründete Lücke | ✅ `ACCEPTANCE_CRITERIA_TRACED` |

> **Aktueller Erfüllungsgrad: siehe README.** Die Zahl wird aus dem Katalog abgeleitet und von `README_COUNTS_CURRENT` gegen das README gehalten — sie steht bewusst **nicht** hier, weil sie sich mit jedem implementierten `design_only`-Check und jedem zurückverfolgten Kriterium bewegt und hier veralten würde.

> **Woher die DoD-Kriterien kommen, nach Autorität:** Normtext (objektiv prüfbar, z. B. Fristen) → Kommissionsleitlinien (Auslegung) → `acceptance_criteria` im Requirement → Gate-Deklaration (`evidence_level.target`, `required_inputs`) → Integrity-Suite (ausführbar). **Die dritte Quelle lag zwei Jahre unbenutzt im Repo** (B-15).

### Was dem Prozess noch fehlt

Vier Punkte, die kein Dokument, sondern eine Entscheidung brauchen — Begründung in `HISTORIE.md` H4.18:

1. **Validierung statt nur Verifikation.** Die Gates prüfen, ob die Spezifikation erfüllt ist. Ob der Gate-*Satz* das regulatorische Risiko senkt, prüft nichts. *Woher weiß ich, dass diese 17 die richtigen 17 sind?* — **der schwerwiegendste offene Punkt**
2. ~~**Fail-open oder fail-closed?**~~ **Entschieden am 27.08.: fail-closed.** Ein fehlgeschlagener Evidence-Schreibvorgang hält den Lauf an, Exit 3 statt 1, damit ein blockierendes Gate von einem nicht aufgezeichneten unterscheidbar bleibt. Preis benannt: der Evidence Store wird zum Single Point of Failure (B-16)
3. **Vier-Augen-Prinzip.** Ein Autor schreibt Requirement, Gate, Policy, Test und Prüfung
4. **Retirement-Pfad** für Gates und Systeme — deckungsgleich mit Limitation L2

## 2.5 Wo liegt was

| Ort | Inhalt |
|---|---|
| **Repo-Wurzel** `HANDBUCH.md`, `HISTORIE.md` | **Kanonisch.** Der Stand und seine Begründung. Jede andere Ablage ist Kopie und wird nicht fortgeschrieben |
| **Repo** `specs/`, `AGENTS.md`, `CHANGELOG.md`, `README.md` | Aufträge, Dauergrundsätze, Änderungsbegründung je Commit, Außendarstellung mit geprüften Zahlen |
| **Repo** Code, Policies, Gates, Tests | Der lauffähige Nachweis. Was hier nicht läuft, gilt nicht als umgesetzt |
| **Außerhalb des Repos** | Primärquellen-Analysen und Recherchestränge. Sie sind **nicht Teil des veröffentlichten Artefakts**; wo dieses Handbuch eine Rechtsaussage trägt, steht ihre Evidenzstufe dabei (2.3) |

> **Eine Quelle, nicht zwei.** Diese beiden Dateien liegen im Repo und werden dort geändert. Eine Zweitfassung, die parallel gepflegt wird, läuft auseinander — genau das war der Zustand bis zum 01.09.2026, und der Unterschied war zu diesem Zeitpunkt vier Abschnitte und drei Befunde groß.

## 2.6 Arbeitsteilung (D-17)

**Cowork:** Recherche, Register, Spezifikationen, Architektur- und BIZDEV-Dokumente — alles, was über Sessions hinweg gilt.
**Claude Code im Repo:** Implementierung, Rego, `opa test`, `conftest`, `pytest`, Integrity-Regression, git, CI.
**Übergabe:** Spezifikationen entstehen in Cowork, werden nach `specs/` gelegt, Claude Code liest sie dort als Auftrag.

> **Für echte Messungen (E-3)** wird die Anwendung per Docker gestartet — **kein Kubernetes nötig** (D-29). Nur E-2 (Gatekeeper gegen `data.inventory`) braucht einen Cluster.

---

# TEIL 3 — Glossar

## 3.1 Rollen nach EU AI Act

| Begriff | Bedeutung |
|---|---|
| **Anbieter / Provider** | Entwickelt ein KI-System und bringt es in Verkehr. Schuldet die **Beschaffenheit des Systems** (Art. 16). |
| **Betreiber / Deployer** | Verwendet ein KI-System unter eigener Verantwortung. Schuldet die **Beschaffenheit der Verwendung** (Art. 26). |
| **Rollenaufstieg** | Betreiber wird Anbieter nach Art. 25 Abs. 1 — Rebranding (a), wesentliche Veränderung (b), Zweckänderung zu Hochrisiko (c). |
| **Sicherheitsbauteil** | **Amtlicher Terminus** (Art. 3 Nr. 14) — *nicht* „Sicherheitskomponente". Zwei ODER-verknüpfte Arme: Zweckbestimmung **oder** Ausfallfolge, jeweils zum Schutz von Personen **oder Eigentum**. |
| **Übergabepaket** | Die drei Artefakte aus Art. 25 Abs. 2 n.F. lit. a–c: technische Unterlagen, Unterrichtung über Einschränkungen, gezielter technischer Zugang. |

> **Merkformel:** Der Anbieter schuldet die Beschaffenheit des Systems. Der Betreiber schuldet die Beschaffenheit der Verwendung. Die schärfste Abgrenzung ist **Art. 14 ↔ Art. 26 Abs. 2**: Anbieter schuldet die **Gestaltung**, Betreiber die **Besetzung**.

## 3.2 Bausteine der Masterarbeit

| ID | Bezeichnung |
|---|---|
| **E1–E5** | CDV-Framework · D3×D2-Override / Automation Ceiling · Drei-Säulen-Policy-Engine · Hash-Chain-Tamper-Evidence · CAC/AAC-Distinktion |
| **E6** | **Evidenz-Ebenen-Modell — neu, nicht Teil der Masterarbeit** (D-10) |
| **DP1–DP5** | Lifecycle-Prozess · Traceability · Gate-Template · Ebenen-Trennung · Cloud-native Integrierbarkeit |
| **D1 / D2 / D3** | Gate-Eignung · Automatisierbarkeit · Oversight-Typ |
| **G-PRE / G-DEP / G-OPS** | Gate-Präfixe nach Lifecycle-Phase |
| **R001–R014** | Requirements aus Art. 9–15 und Art. 26 |

## 3.3 Evidenz-Ebenen (E6) — die zentrale eigene Achse

| Ebene | Was geprüft wird | Fälschungskosten | Braucht |
|---|---|---|---|
| **E-0** | Ein Dokument, das jemand geschrieben hat | Textänderung | nichts |
| **E-1** | Ein erzeugtes und **signiertes** Artefakt; Signatur und Erzeuger-Identität geprüft | Kompromittierung der CI-Identität | **CI** (OIDC) |
| **E-2** | Der tatsächliche Clusterzustand über die Kubernetes-API | Manipulation des laufenden Systems | **Cluster** |
| **E-3** | Eine Eigenschaft **über Zeit**, gemessen statt konfiguriert | Manipulation der Telemetriekette | **laufende App** |

**Automatisierbarkeit und Beweiskraft sind orthogonale Achsen.** Ein HYBRID-Gate kann E-3 tragen, ein AUTO-Gate auf E-0 stehen.

> **Der Neuheitsanspruch, teilgeprüft (27.08.):** Buscemi et al. (2025) führen die nächstliegende Achse — `controls` gegen `testing` — und erklären sie **ausdrücklich für nicht-hierarchisch**. E6 ordnet stattdessen nach Fälschungskosten und füllt E-1/E-2 dazwischen. Damit ist der Beitrag zitierbar abgegrenzt statt ex silentio behauptet. Details: H7.1.

**Zwei Erweiterungen (Begründung: H4):**
- **Provenance je Metrikgruppe** — `measured` / `derived` / `declared`. E6 auf der Feldebene. Macht die Behauptung nicht wahr, sondern **als Behauptung kenntlich**.
- **Auflösung der Messung** — ein Wert kann *gemessen* und trotzdem *informationsfrei* sein (B-10). `latency_p95_resolution` macht die Grenze maschinenlesbar.

## 3.4 Gate-Anatomie — die fünf Fragen an jedes Gate

Der Prüfrahmen, der für **jedes** Gate gilt. Wer ein Gate baut, bewertet oder darüber schreibt, beantwortet diese fünf Fragen — und zwar am Code, nicht aus der Erinnerung.

| # | Frage | Wo es im Gate steht |
|---|---|---|
| **1** | **Ziel** — welche Pflicht soll erfüllt sein? | `links.requirements` + `legal_refs` je Check |
| **2** | **Daten** — womit wird geprüft? | `evidence_required` · **`required_inputs`** (SPEC-04b) |
| **3** | **Ergebnis** — was kommt heraus? | `severity` je Check → abgeleitete Entscheidung + Evidence-Record |
| **4** | **Auslöser eingehend** — wann feuert es? | `trigger` |
| **5** | **Auslöser ausgehend** — was folgt daraus? | `triggers` — seit 27.08. auf jedem Gate des Katalogs |

> **Frage 5 war bis 27.08. nicht deklarierbar** — und wo nichts deklariert ist, füllt die Vorstellung die Lücke (B-13). Jedes Gate nennt jetzt seine Wirkung: `halt_pipeline` · `record_only` · `open_incident` · `start_deadline` · `notify`, je mit `implementation: implemented | declared_only`.
>
> **Stand: die Mehrheit der deklarierten Wirkungen ist gebaut, ein Rest nicht — die Aufteilung nennt das README, geprüft von `GATE_DECLARES_EFFECT`.** G-OPS-02 deklariert `start_deadline` und `open_incident` als `declared_only` — für Art. 26 Abs. 5 ist Frage 5 nicht optional, die Norm verlangt eine *Folge*, kein Urteil, und ein Gate, das nur PASS/FAIL kann, bildet diese Pflicht konstruktiv nicht ab. Geprüft von `GATE_DECLARES_EFFECT`.

**Zwei Gate-Arten, die nicht vermischt werden dürfen:**

| Art | Feuert | Beweiskraft möglich |
|---|---|---|
| **Präventiv** (Zulassung) | einmal, vor dem Lauf — PR-Merge, Image-Build, `kubectl apply` | E-0 bis E-2 |
| **Operativ** (Laufzeit) | wiederholt oder ereignisgetrieben, am laufenden System | E-3 |

Ein präventives Gate kann ein Requirement, das „kontinuierlich" verlangt, **strukturell nicht** erfüllen. Genau das ist bei vier G-OPS-Gates der Fall (B-14). G-OPS-03 zeigt den Ausweg: **beides in einem Gate**, mit zwei Inputs — Annotation bei der Zulassung (E-0) *und* Messdokument mit Frist (E-3).

## 3.5 Offene Terminologie

**„Souverän" ist undefiniert.** Die Literatur ist uneins (Adler-Nissen et al. 2024: sechs Konzeptionen). Vor Verwendung im Produktnarrativ ist eine Definitionsentscheidung nötig. **Steht aus.**

**Namenskollisionen:** Cedar (AWS) ≠ CEDAR-42001 (ISO-Assurance) · NIST AI RMF ≠ NIST CSF · Zielrolle B ≠ Richtung B.

---

# TEIL 4 — Normenraum und Fokus

## 4.1 Aufnahmeregel statt Normenliste (D-09)

> **Eine Anforderung gehört in den Normenraum, wenn sie am Lebenszyklus eines KI-Systems prüfbar anfällt.**

**Drin:** Cybersicherheit, Datenschutz, Managementsystem-Anforderungen und sektorspezifische Anforderungen — jeweils **soweit sie das KI-System betreffen**.
**Draußen:** allgemeine Unternehmens-Governance ohne KI-Bezug.

*Warum eine Regel und keine Liste: Listen wachsen unkontrolliert und erzeugen Scope-Drift.* Vollständige Regelwerksübersicht: `HISTORIE.md` H3.

## 4.2 Drei Artefakttypen, methodisch zu trennen (D-20)

| Typ | Gegenstand | Ergebnisform |
|---|---|---|
| **Typ 3 — Klassifikationsregel** | **ob** ein System hochrisiko ist | Entscheidungsbaum, als Policy prüfbar |
| **Typ 2 — Crosswalk** | wie die KI-Pflichtenlage am bestehenden ISMS hängt | Mapping-Tabelle mit **Restlücke**. Kein Rego. Auf frei zugänglichen Primärquellen verankert, ISO nur als Klauselverweis (D-21) |
| **Typ 1 — Requirements** | verpflichtende Normaussage → prüfbare Anforderung | Gate, rollenannotiert |

**Reihenfolge:** Typ 3 → Typ 2 → Typ 1 parallel als Delta-Pflege.

> **Warnung:** NIS2 und EnWG § 11 sind **keine KI-Normen**. Wer daraus naiv Requirements ableitet, baut ein zweites ISO-27001-Kontrollset. Der Wert des Crosswalks liegt in den **Lücken**, nicht in den Deckungen.

## 4.3 Die drei Fristen, die zählen (D-02)

| Datum | Ereignis |
|---|---|
| **27.07.2026** | VO (EU) 2026/1744 (Omnibus) in Kraft — **VERIFIZIERT** |
| **02.12.2027** | **Annex III Hochrisiko anwendbar, inkl. Nr. 2 kritische Infrastruktur** |
| 02.08.2028 | Annex I embedded Hochrisiko anwendbar |

> **Die Fristen sind unbedingte Kalenderdaten.** Der finale Art. 113 enthält keinen standards-gekoppelten Konditionaltrigger. Ab 02.12.2027 gilt die volle Annex-III-Pflichtenlast, auch ohne fertige harmonisierte Standards. Vollständige Zeitachse: H3.

## 4.4 Branche, Adressat, Anwendungsfall (D-06, D-07, D-08)

**Branche:** Energie / Kritische Infrastruktur. **Adressat:** Verteilnetzbetreiber mittlerer bis großer Größe (~850–900 in DE), **ÜNB-Rigorosität als Maßstab**. **Region:** Südwestdeutschland.

**Der Normenstapel auf einem Adressaten — vier Regelwerke gleichzeitig:** EnWG § 11 + IT-Sicherheitskatalog BNetzA (zertifiziertes ISMS) · NIS2UmsuCG (Anhang I, in Kraft ohne Übergangsfrist) · KRITIS-Dachgesetz · EU AI Act Annex III Nr. 2 ab 02.12.2027.

> Der Adressat hat bereits ein zertifiziertes ISMS. Die Frage ist nicht „wie fange ich an", sondern **„wie hängt die KI-Pflichtenlage an meinem bestehenden ISMS"** — ein Übersetzungsproblem, kein Aufbauproblem.

**Anwendungsfall Redispatch:** Bei Engpassmanagement ist die KI eindeutig Sicherheitsbauteil über **beide Arme** der Legaldefinition. Drei Konstellationen: K1 Zukauf (`DEPLOYER`, **Regelfall**), K2 Eigenentwicklung (`BOTH`), K3 Zukauf mit wesentlicher Anpassung (Übergang). Voraussichtlicher Haupttrigger ist **Art. 25 lit. c** (Zweckänderung), nicht lit. b — Hypothese aus dem Marktbefund (D-23). **Zwingende Auflage: mindestens ein Negativfall** aus derselben Domäne — Kandidat: prädiktive Instandhaltung (D-22).

## 4.5 Differenzierungsachsen (D-14)

| Rang | Achse | Rolle |
|---|---|---|
| **1** | **Beweiskraft (E6)** | Der Adressat kennt Auditlogik. Seine Frage ist „wie beweise ich das prüffest", nicht „warum überhaupt". |
| **2** | **Befähigung** | Übersetzung zwischen bestehendem ISMS und neuer KI-Pflichtenlage. |
| **3** | **Lifecycle-Vollständigkeit** | Ausbaustufe, inkl. Retirement (D-03, nachrangig gestellt). |

**Richtung A (Pflichten-Prüfer) und Richtung B (Lieferanten-Prüfer) sind beide im Scope, A zuerst** (D-19). B1 ist der Regelfall und hängt an Art. 13 / Art. 26; der größte Hebel von B liegt in einer **Beschaffungs-Checkliste vor Vertragsschluss**, weil die Opt-out-Klausel in Art. 25 Abs. 2 die wirksame Prüfung dorthin verschiebt. Begründung und Rechtsanker: H2.

---

# TEIL 5 — Stand der Umsetzung

## 5.1 Bestand im Repo

**Die Zählstände stehen im README, nicht hier.** Gates, Checks, Policies, Regeln, Testfälle, Requirements und der Umfang der Integrity-Suite werden dort aus dem Repository abgeleitet und von `README_COUNTS_CURRENT` wörtlich dagegen gehalten; die Aussagen über die Beweisstufen hält `README_EVIDENCE_CLAIMS_CURRENT`. Eine zweite Zählung an dieser Stelle hätte keinen Wächter und wäre binnen weniger Commits falsch — genau so entstanden B-12 und B-19.

| Ebene | Stand |
|---|---|
| **Gates** | Drei Lifecycle-Phasen: pre-deployment, deployment, operations. Automatisierungsgrad AUTO/HYBRID, kein Gate MANUAL. Zahlen: README |
| **Policies** | OPA/Rego, `deny`/`warn`/`violation`, je Policy eine Testdatei. Zahlen: README |
| **Enforcement** | Conftest (CI), OPA Gatekeeper (K8s Admission), Decision Logs |
| **Evidence Store** | PostgreSQL, Schema **v06**, Insert-only, SHA-256-Hash-Chain, RLS. Gehashte Felder: `ai_act_role`, `derived_decision`, `runtime_mode` |
| **Messung** | `eval_runner.py` erzeugt das Evaluationsdokument aus der laufenden App · Drift-Detektor (PSI/JSD) misst, **Rego entscheidet** |
| **Qualitätssicherung** | Integrity-Regression, Hash-Parity über alle Payload-Varianten, Chain-Migration, Fail-closed-Nachweis |
| **CI** | GitHub Actions: Rego-Tests, alle Gates, Evidence-Recording, Hash-Chain-Verifikation je Lauf · App läuft im Runner und wird gemessen · Negativfall-Job mit Gegenproben, an dem der Image-Build hängt |
| **Lizenz** | Apache 2.0 seit 15.08. (D-15), nicht rückwirkend — Zenodo-Archiv und `thesis-v1.0` bleiben CC BY-NC |
| **Zielstack** | souverän, Open Source, ohne Vendor-Lock-in (D-16); Azure AKS nur exemplarisch, die Bindung sitzt in `infrastructure/scripts/` |
| **Szenarien** | Healthcare-PoC bleibt als erste Vignette (D-18), Netzbetrieb-Vignette kommt dazu |

**Zwei Zahlen sind hier nicht delegierbar und stehen deshalb doch:** das **Evidence-Schema v06** — es ist keine Zählung, sondern der Name eines Migrationsstands, an dem die Hash-Payload hängt; und **v05 → v06** als letzte Migration. Beide ändern sich nur durch eine bewusste Schemaänderung, nicht durch das Wachsen des Katalogs.

**Lokale Baseline:** die Kommandos stehen im README unter „Run the checks". Alle müssen grün sein, bevor etwas als umgesetzt gilt.

## 5.2 Umgesetzte Spezifikationen

| Spec | Was | Stand |
|---|---|---|
| SPEC-01 | `schema_version: 2` — E6-Achse, Severity je Check (D-11), abgeleitete Gate-Entscheidung | ✅ |
| SPEC-02 | Art.-6-Prüfbaum in G-PRE-01 (C-A1…C-A7) | ✅ |
| SPEC-03 | Rollenparameter PROVIDER/DEPLOYER/BOTH (D-12), Rollenübergangs-Gate G-OPS-06 (D-13), Schema v04 | ✅ |
| SPEC-04 | **Messung vor Signatur** (D-27) — gemessene Inputs, Provenance, `runtime_mode` versiegelt (v06, D-28) | ✅ `9afc47d` |
| SPEC-04b | **Die CI misst wirklich** — Erzwingung, App im Runner, Drift in der CI, Negativfaelle | ✅ vollstaendig (28.08.) |
| SPEC-05 | **E-1: die Signatur, die eine Erzeuger-Identität trägt** — Evidenz-Manifest, `cosign` keyless/OIDC, identitätsgebundene Verifikation | 🟡 Teil 1 (Rückstufung) und Teil 2 (Evidenz-Manifest) umgesetzt; Signieren, Verifizieren und die Gate-Checks offen |

## 5.3 Wo die Beweiskraft heute wirklich steht

> **Ehrlich, weil es der Kern des Vorhabens ist:** `evidence_level.current` steht auf **jedem Gate auf E-0**. Nur ein Teil der Checks trägt einen eigenen Wert; **die aktuelle Verteilung über E-0, E-1, E-3 und „ohne Angabe" steht im README** und wird dort von `README_EVIDENCE_CLAIMS_CURRENT` gegen den Katalog gehalten. Das Gate-weite Feld bleibt bewusst auf dem schwächsten Bestandteil — ein Gate ist so beweiskräftig wie sein schwächster MUST-Check, nicht wie sein bester.
>
> **Die E-1-Sprosse ist leer.** Sie war es nicht immer: ein Check führte E-1 für die Hash-Kette, und diese Einstufung hielt der eigenen Definition nicht stand (B-18). Eine Prüfsumme ist keine Signatur, und `inserted_by` ist eine selbstgewählte Zeichenkette. Die Rückstufung ist der ehrliche Zwischenzustand, bis SPEC-05 das signierte Evidenz-Manifest liefert.
>
> **Seit dem 28.08. nutzt die CI die E-3-Checks.** G-DEP-02 prüft das Dokument, das `eval_runner.py` im Runner erzeugt hat; G-OPS-03 wird gegen das Manifest **und** gegen ein im Runner gemessenes Driftdokument gewertet, in *einem* Gate-Lauf.
>
> **Was diese Messung nicht zeigt: Drift.** Sie misst PSI 0.000000, und das ist die Bauart, kein Mangel — das Prometheus-Histogramm ist kumulativ über die Prozesslaufzeit, die aktuelle Verteilung enthält die Baseline also mit. Ein Messwert, der nicht ausschlagen *kann*, ist als Beleg für Stabilität wertlos; er belegt nur, dass der Pfad läuft.

**Was SPEC-04 bereits behoben hat:** der stille Fallback im Drift-Detektor (B-03), die Doppelzuständigkeit bei G-OPS-03 (B-04), die Annotation als einziger Prüfgegenstand (B-05) und das ungelesene `scribe_mock_mode` (B-06). Details je Befund: `HISTORIE.md` H4.

**Was E-1/E-2/E-3 brauchen:** E-1 die CI (nicht den Cluster), E-3 eine laufende App (nicht den Cluster), **nur E-2 den Cluster** (D-29).

---

# TEIL 6 — Offene Punkte

Nach Priorität. Erledigtes wandert mit Nachweis nach `HISTORIE.md`, es wird nicht gelöscht.

## 6.1 Hoch

| Punkt | Stand |
|---|---|
| **Anwesenheitspflicht des Messdokuments erzwingen** (B-11) | ✅ SPEC-04b Teil 3.2 (Orchestrator) und 28.08. (CI, `pipeline/ci_required_inputs.py`). Der Nachweis ist Negativfall 3: ohne Dokument fällt G-OPS-03 mit benanntem Input |
| **CI misst wirklich** (B-12) | ✅ 28.08., SPEC-04b vollständig. Ohne Kubernetes, wie vorgesehen |
| **Art. 13 Wortlaut** vollständig erschließen — die Inhaltsliste der Betriebsanleitung ist die Checkliste von B1 | offen |
| **NIS2 / NIS2UmsuCG** Primärquellenrecherche, Fokus Anhang I Energie | offen |
| **EnWG § 11 + IT-Sicherheitskatalog**, inkl. Verhältnis zu NIS2UmsuCG (lex specialis?) | offen |
| **Provider-Pflichten** Art. 16–20, 43, 47–49 — größter offener Block; `AI_ACT_ROLE=PROVIDER` trifft heute kein Gate | offen, strukturell vorbereitet |
| **Feedback-Kanal für Ground Truth** (B-08) — ohne Labels keine Genauigkeit im Betrieb. **Vorher in die Redispatch-Domäne übersetzen:** dort ist die Leitstellen-Freigabe das Label, nicht die Arztkorrektur | offen, aufwendigster Punkt |
| **Kommissions-Entwurf zu Art. 73 erschließen** (26.09.2025, Leitlinien + Meldetemplate, Konsultation bis 07.11.2025) — klärt laut Sekundärquellen, **wann ein Vorfall „schwerwiegend" ist**, und nennt Meldefristen von 2 bis 15 Tagen | **NEU 27.08.** Beantwortet teilweise die Frage, die als eigener Beitrag geführt wird. Ohne ihn wäre `incident_thresholds.yaml` uninformiert. Definition nennt „critical infrastructure" ausdrücklich — der Zieladressat wörtlich |
| **Schwellenwerte in `governance/incident_thresholds.yaml` setzen** — beide `unset`. Voraussetzungen in dieser Reihenfolge: (1) Subgruppen festlegen (fachlich **und** datenschutzrechtlich), (2) Maß für Ungleichverteilung wählen, (3) Rechtsauslegung „ab wann schwerwiegend", (4) Fairness-Messung im Betrieb bauen (B-08 Lücke 3) | **NEU 27.08.** Schritt 1–3 sind **keine Technikfragen** und nicht delegierbar. Ohne sie kann G-OPS-02 keinen Vorfall erkennen — C-03 warnt sichtbar darauf, die Lücke ist aktenkundig statt unsichtbar |

### G-OPS-02 business ready — die Ausbaustufe

Ausformuliert nach den fünf Fragen aus 3.4, weil dieses Gate die Lücke am deutlichsten zeigt (B-13). Dasselbe Schema gilt für G-OPS-01 und G-OPS-05.

| Frage | **Heute** | **Business ready** |
|---|---|---|
| **1 Ziel** | Ein Incident-Prozess ist *deklariert* | Ein schwerwiegender Vorfall wird **erkannt**, dokumentiert und fristgerecht gemeldet (Art. 26 Abs. 5, Art. 73) |
| **2 Daten** | 3 Pod-Annotationen | Fehlerrate aus `scribe_requests_total{status="error"}` · Drift aus G-OPS-03 · Override-Rate der Aufsicht · **Schwellenwert-Definition als eigenes Artefakt** |
| **3 Ergebnis** | PASS/FAIL bei Zulassung | Incident-Record mit Zeitstempel, Auslöser und Schwellenwert-Bezug — in der Hash-Kette versiegelt |
| **4 Auslöser ein** | `kubectl apply`, einmalig | **ereignisgetrieben**: Schwellenwertverletzung im Betrieb |
| **5 Auslöser aus** | *nichts deklariert* | **Fristenuhr startet** · Meldekaskade wird als Aufgabe erzeugt · Ablauf ohne Meldung ist selbst ein Befund |

**Die vier Schritte, in dieser Reihenfolge:**

1. **Frage 5 ins Gate-Template** — Feld `triggers` (was folgt aus dem Urteil). Ohne das bleibt jede Meldepflicht eine Behauptung, und die Leerstelle lädt zum Ausschmücken ein
2. **Schwellenwert-Artefakt** — `incident_thresholds.yaml`: ab wann ist eine Fehlklassifikation ein *schwerwiegender* Vorfall. **Bewusst nicht automatisiert**, aber versioniert, begründet und zitierbar. Das ist die eigentliche Lücke im Feld, und ein publizierbares Artefakt
3. **Ereignisgetriebener Pfad** — G-OPS-02 bekommt wie G-OPS-03 einen zweiten Input (`required_inputs: incident_record`) und behält die Annotationsprüfung bei der Zulassung. Zulassung **und** Laufzeit in einem Gate
4. **Fristenuhr** — Zeit von Schwellenwertverletzung → Record → Meldung, gemessen (E-3). Ablaufende Frist ohne Meldung = eigener Befund

> **Zwingende Vorbedingung, nicht verhandelbar:** Art. 26 Abs. 5 und Art. 73 sind **nicht EUR-Lex-abgeglichen** (6.2). Die Meldekaskade und die Fristen dürfen erst gebaut *und erst recht nicht publiziert* werden, wenn der Wortlaut geprüft ist. Sonst automatisiert das Artefakt eine Rechtsauslegung, die es selbst als ungeprüft führt.

**Was zuerst fehlt, ist aber nicht Code:** ohne Ground Truth gibt es keine Fehlklassifikationserkennung (B-08). Schritt 2 ist deshalb der einzige, der **sofort** möglich ist — und der wertvollste, weil er die Frage beantwortet, an der das Feld hängt.

## 6.2 Mittel

| Punkt | Stand |
|---|---|
| Hartkodierte Zählstände aus dem CI-Workflow entfernen (B-12) | ✅ SPEC-04b Teil 1 |
| **Feld `triggers` ins Gate-Template** (Frage 5 aus 3.4) — was folgt aus dem Urteil | B-13. Ohne das bleibt jede Meldepflicht eine Behauptung |
| **G-OPS-01, G-OPS-02, G-OPS-05 auf Laufzeit nachziehen** — sie feuern bei Admission, ihr Requirement verlangt „kontinuierlich" | B-14. G-OPS-03 zeigt den Weg: zwei Inputs, ein Gate |
| **Integrity-Check `TRIGGER_MATCHES_REQUIREMENT`** — Gate-`trigger` gegen `audit_trigger` des Requirements | B-14 blieb unbemerkt, weil nichts die beiden gegeneinander hält |
| **Außenaussagen gegen den Gate-Stand prüfen** — Beiträge behaupteten Fähigkeiten, die das Gate nicht hat | B-13. Analog zu `README_COUNTS_CURRENT`, nur für Beitragsentwürfe |
| **`incident_thresholds.yaml`** — ab wann ist eine Fehlklassifikation ein schwerwiegender Vorfall | Bewusst manuell, aber versioniert und begründet. Sofort möglich, unabhängig von Ground Truth |
| `policy_checks[].evidence_level` weiter füllen (B-07) | 10 von 47 |
| Bucket-Auflösung für den Produktivfall prüfen (B-09) | 1 ms passt zum Mock, nicht zwingend zu einem echten Modell |
| Art. 49 Abs. 1 — welche Registrierungsdaten sind öffentlich abfragbar? Entscheidet, ob E-2 für Fremdnachweise erreichbar ist | offen |
| Art. 3 Nr. 23 („wesentliche Änderung") im Wortlaut; Schwelle bei Fine-Tuning und RAG | offen — deshalb bleibt C-25b advisory |
| Deutsche Sprachfassung: Art. 9–15, 26, 27, 72, 73 abgleichen | teilweise |
| EUR-Lex-Abgleich Art. 16 und Art. 26 | offen (Art. 25 erledigt) |
| Definitionsentscheidung „souverän" (3.5) | offen |
| Cedar vs. OPA | offen |
| G-DEP-01 rollenscharf ziehen — referenziert Art. 10/11 (Anbieterpflichten), ist aber Betreiber-Gate | bewusst nicht gefixt, gehört zur Provider-Ableitung |
| Beschaffungs-Checkliste als eigenes Artefakt (Richtung B1) | existiert nicht |
| **Gardhouse et al. (2026) und Hacker & Holweg (2026) zitieren** — Pflichtenlage bei Agenten; Gardhouse benennt zudem das **Kausalitätsproblem** bei zusammengesetzten Systemen, das die Vorfallzurechnung trifft | `zotero-klassifikation-ai-compliance.md`. 7 von 10 Dokumenten des Tags sind Legal Tech und gehören nicht in den Korpus |
| **Buscemi et al. (2025) in Fachbeitrag und Thesis zitieren** — nächstliegender Stand der Technik, gegen den E6 sich abgrenzt | H7.1. Zotero-Ordner im Übrigen erst zu einem Dokument gesichtet |
| Aufsichtsmetriken, Output-Drift, Fairness im Betrieb, Fristenuhr Art. 73 (B-08) | offen |
| Tag- und Versionierungsfrage (D-24) — Release-Tags und Zenodo-Pushes bleiben blockiert | vertagt, nicht erledigt |
| Drift-CronJob im Cluster nicht lauffähig — braucht conftest und Policies im Image, kein Dockerfile vorhanden | dokumentiert |
| Redispatch-Vignette bauen, inkl. Negativfall | offen — macht die Branchenwahl erst sichtbar |
| Ersten Fachbeitrag zur Rollenabgrenzung schreiben | braucht EUR-Lex-Abgleich |

## 6.3 Pflege

- Robustheitssignale, ISO 42001/27019, Art. 99 Sanktionen, CEN/CENELEC, CADA, GAIA-X/EUCS, DSGVO-Volltext — niedrig
- **Quellenlage der Rechtsaussagen nachziehen:** jede Aussage in Teil 4 und in H3 trägt ihre Evidenzstufe (2.3). Was auf `SEKUNDÄRQUELLE` steht, ist vor einer Veröffentlichung gegen EUR-Lex zu prüfen

---

# TEIL 7 — Wie es weitergeht

**SPEC-04b ist seit dem 28.08. vollständig** — Punkte 1 bis 4 erledigt, in dieser Reihenfolge gebaut:

1. ✅ **Anwesenheitspflicht des Messdokuments erzwingen** — im Orchestrator *und* in der CI
2. ✅ **Hartkodierte Zählstände aus dem Workflow entfernen**
3. ✅ **App im Runner starten, `eval_runner` in der CI** — ohne Kubernetes
4. ✅ **Drift im Runner, Negativfälle als eigener Job** — drei Fälle, je mit Gegenprobe

**Sofort als Nächstes:**

5. **E-1-Signatur (SPEC-05)** — jetzt sinnvoll, nicht vorher: eine Signatur auf einem erfundenen Wert demonstriert die These nur halb, und die Rückfrage wäre „woher kommt die Zahl?". Sie ist beantwortet.
6. **Vier-Augen-Prinzip und Retirement-Pfad** — die zwei Prozesslücken aus 2.4
7. **Deckungsanalyse Norm → Requirement** — Validierung statt Verifikation: woher weiß ich, dass der Katalog die richtigen Gates enthält?

**Danach:**

8. Art. 13 im Wortlaut — Grundlage für Richtung B1
9. NIS2 und EnWG § 11 als Primärquellen
10. **Redispatch-Vignette inkl. Negativfall** — hängt an keinem Recherchepunkt und macht die Branchenwahl sichtbar
11. Ersten Fachbeitrag zur Rollenabgrenzung

**Mittelfristig:**

12. Feedback-Kanal für Ground Truth, in die Redispatch-Domäne übersetzt
13. Provider-Requirements aus Art. 16 ableiten
14. Tag- und Versionierungsfrage klären

---

## Anhang — Verweise

| Datei | Inhalt |
|---|---|
| **[`HISTORIE.md`](HISTORIE.md)** | Begründungen (D-01…D-31), Befunde (B-01…B-19), Forschungsstand, Normenreferenz, Revidiertes, Fassungsgeschichte |
| [`README.md`](README.md) | Außendarstellung und alle Zählstände, maschinell gegen das Repository gehalten |
| [`specs/`](specs/) | SPEC-01…05 — die Aufträge, aus denen der Code entstanden ist |
| [`CHANGELOG.md`](CHANGELOG.md) | Vollständige Begründung je Codeänderung |
| [`AGENTS.md`](AGENTS.md) | Dauergrundsätze für die Arbeit im Repo |

Alle Verweise dieser Tabelle zeigen auf Dateien **in diesem Repository**. Rechtsaussagen dieses Handbuchs tragen ihre Evidenzstufe (2.3) und den Normbezug in H3 — sie setzen keine Datei voraus, die hier nicht liegt.

---

*Handbuch v1.1 · 01.09.2026 · Der Stand — Begründungen in HISTORIE.md · Zählstände im README · Keine Rechtsberatung*

