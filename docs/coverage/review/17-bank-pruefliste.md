---
titel: Leitfall Bank – kritische Prüfung, was an Pflichtenraum, Gates und Rechtsquellen angepasst werden muss
stand: 2026-10-13
basis: Branch domain_bank = c4a1ce9 (gemessen) · Review 16 (Leitfall Bank) · Auftrag PO 13.10.2026 („kritisch prüfen, welche Regularien und Gesetzestexte wir für die Bank anpassen müssen“)
status: Vorschlag · nichts im Pflichtenraum geändert · BK-F3 b, BK-F4 a, BK-F5 c entschieden 13.10.2026
---

# Kurz

- **Die Architektur trägt die Bank. Der Pflichtenraum und drei Gates tun es noch nicht** – sie sind auf Anhang III Nr. 2 zugeschnitten.
- **AI Act + Omnibus:** 16 Zeilen kommen für die Bank hinzu, 6 Zeilen gehören nur noch zu Fall 2 oder 3, Art. 26 Abs. 11 wird einschlägig. Zwei PO-Entscheide kippen (Q1, Q11).
- **Gates:** G-PRE-01 (keine Prüfung für Nr. 5 lit. b), G-OPS-02 (Meldelogik für Nr. 2 unter CER/NIS2), G-OPS-03 (Finanzinstitute überwachen über ihr Governance-Recht).
- **Rechtsquellen:** Der AI Act verweist für die Bank selbst auf Recht, das im Repo fehlt – Finanzdienstleistungsrecht zur internen Governance (Art. 26 Abs. 5, 6), anderweitige Erläuterungsrechte (Art. 86 Abs. 3), die DSFA (Art. 26 Abs. 9). Der DSGVO-Raum liegt vor, ist aber in keiner Zeile eingeordnet.
- **Entfällt für den Leitfall:** NIS2/BSIG, KRITIS-DachG, EnWG – für Finanzunternehmen gilt DORA als sektorspezifischer Rechtsakt (NIS2 Art. 4 Abs. 1, ErwG 28). Sie bleiben für Fall 3.

```
                  AI Act + Omnibus        Gates                 Rechtsquellen
heute (Netz)      Nr. 2 zugeschnitten     Nr.-2-Logik           NIS2 · BSIG · KRITIS-DachG · EnWG · DSGVO (uneingeordnet)
                        │                     │                         │
Bank braucht      +16 in · 6 nur Fall 2/3  G-PRE-01 · G-OPS-02    DORA · CRD Art. 74 / KWG § 25a · Verbraucherkredit
                  Q1, Q11 kippen           G-OPS-03 · R012        (BGB, KWG § 18a, BDSG § 37a) · DSGVO Art. 22, 35, 13–15
```

# Wer was übernimmt

```
KI (WIE)                                         PO (WAS)
──────────────────────────────────────           ──────────────────────────────────
Zeilen vermessen, Vorschlag je Zeile        ──►  scope in/out und Stufe je Zeile
Wortlaute holen, hashen, schneiden          ──►  welche Quellen in den Stapel kommen
Entscheidungsdatei, Wächter, Gegenprobe     ──►  GO zur Prüfliste
Gates und Checks bauen (Paket 5/6)          ──►  MUST/SHOULD, evidence_level, implemented
README, HANDBUCH, Register nachziehen       ──►  Push-Freigabe
```

# Teil 1 – AI Act und Omnibus: Neueinordnung (gemessen auf c4a1ce9)

| Gruppe | Zeilen | heute | Vorschlag Bank | Stufe (Vorschlag) |
|---|---|---|---|---|
| Einstufung | Anhang III Nr. 5, Nr. 5 lit. b | `out` (Systemtyp) | `in`, nicht einschlägig – steuernd für G-PRE-01 | VERIFIZIERT: Wortlaut; Leitlinien-Entwurf, Beispiel nach Rn. 309 |
| FRIA | Art. 27 Abs. 1, lit. a–f, Abs. 2, Abs. 3; Art. 27 Abs. 4 n.F. (10) | `out` (Bereichsausnahme Nr. 2) | `in`; Befund je Element (G-PRE-02/05 prüfen heute nur eine interne FRIA) | VERIFIZIERT: Abs. 1 nennt Nr. 5 lit. b |
| Erläuterung | Art. 86 Abs. 1, Abs. 2, Abs. 3 | `out` | `in`; Abs. 1 Lücke, Abs. 2 und 3 steuernd | HYPOTHESE: Reichweite nach Abs. 3 (BK-B6) |
| Finanzinstitute | Art. 26 Abs. 5 UAbs. 2 Satz 1 | `out` (Adressat Finanzinstitut) | `in`, steuernd: verändert die Überwachungspflicht aus Satz 1 | VERIFIZIERT |
| Betroffene informieren | Art. 26 Abs. 11 | `in`, nicht einschlägig (Q11 a) | einschlägig, Lücke; Schalter aus FR-1 a für die Bank immer `true` | VERIFIZIERT |
| Nr.-2-Pfad | Anhang III Nr. 2, Art. 3 Nr. 62, Art. 3 Nr. 14 n.F., Art. 6 Abs. 1a n.F., Art. 6 Abs. 1b n.F. | `in`, nicht einschlägig | `out`: „nur Fall 3 – Schalter Nr. 2“ (BK-F3) | – |
| Anhang-I-Pfad | Art. 6 Abs. 1c n.F. | `in`, HYPOTHESE (G5) | `out`: „nur Fall 2 – Schalter Anhang I“ (BK-F3); G5 erledigt sich für den Leitfall | – |
| Registrierung | Art. 49 Abs. 3, Anhang VIII Abschn. C (6) | `out` | bleibt `out` – nur Betreiber, die Behörden sind (BK-F4) | – |
| Übergang Behörde | Art. 111 Abs. 2 Satz 2 n.F. | `in`, Lücke, Schalter S3-1 | unverändert; Schalter nur bei öffentlich-rechtlicher Bank fraglich (BK-F4) | – |

- **Unverändert:** die allgemeinen Betreiberpflichten (Art. 4 n.F., Art. 26 Abs. 1, 2, 4, 5 UAbs. 1, 6, 7, 9, 12, Art. 25, Art. 73) – ihre Befunde bleiben.
- **Nur Begründung neu**, Einordnung bleibt: Art. 5 Abs. 1 lit. d, Art. 13 Abs. 3 lit. e, Art. 14 Abs. 4 lit. b, Anhang III (Einleitung), Art. 73 Abs. 9 – sie begründen heute mit Redispatch.
- **Art. 27 Abs. 4 (Grundfassung)** bleibt `out`, jetzt als „ersetzt durch n.F.“ (A-F2 a).

# Teil 2 – Requirements, Gates, Fixtures

| Baustein | heute | für die Bank |
|---|---|---|
| R012 FRIA (G-PRE-02, G-PRE-05/C-01) | `anker: intern` (Q1 b) | Anker Art. 27 Abs. 1; Ehrlichkeitsfelder neu (PO) |
| Art. 26 Abs. 11, Art. 86 | kein Requirement, kein Check | neues Requirement oder Erweiterung R007 (Paket 5) |
| G-PRE-01 | C-A1–C-A7 nur für `no2_critical_infrastructure` | Checks für Nr. 5 lit. b: natürliche Person, keine Betrugserkennung, wesentliche Dienstleistung, Profiling (BK-B2) |
| G-OPS-02 (R009) | Reduktion nach Art. 73 Abs. 9 für Nr. 2 unter CER/NIS2 | Reduktion nur, wenn der **Anbieter** gleichwertig meldepflichtig ist – für DORA offen; Kernarm Art. 3 Nr. 49 lit. c (Grundrechte) |
| G-OPS-03 (R010) | Drift-Messung | Art. 26 Abs. 5 UAbs. 2: Überwachung gilt als erfüllt mit dem Governance-Nachweis – zweiter Nachweisweg |
| G-DEP-05 (R013) | Bias-Prüfung | Art. 4a Abs. 2 n.F.; Schalter `special_categories_for_bias` (P2-F4 c) für Scoring wahrscheinlich `true` |
| R001, R003 | `anker: offen`, Hypothese NIS2/BSIG | Kandidat für die Bank: DORA Kap. II (IKT-Risikomanagement) – HYPOTHESE |
| Fixtures | 6 Art.-6-Fixtures aus dem Netz, Healthcare-Szenario | neue Bank-Fixtures (FR-2): Scoring positiv, Betrugserkennung negativ, reines Pricing negativ |

# Teil 3 – Rechtsquellen: vorhanden und nötig

| Quelle | Art | Wo der AI Act darauf zeigt | für die Bank | im Repo |
|---|---|---|---|---|
| AI Act, Omnibus | EU-Verordnung | – | Kern | ✅ Wortlaut gehasht, Raum eingeordnet |
| DSGVO Art. 22, 35, 13–15 | EU-Verordnung | Art. 26 Abs. 9, Art. 27 Abs. 4 n.F., Art. 86 Abs. 3 | hoch | Wortlaut ✅ · Raum: 780 Zeilen, **keine eingeordnet** |
| CRD (RL 2013/36/EU) Art. 74 → KWG § 25a, MaRisk | Richtlinie → Gesetz; MaRisk ist Verwaltungsvorschrift | Art. 26 Abs. 5 UAbs. 2, Abs. 6 UAbs. 2 („interne Unternehmensführung“) | hoch | ❌ |
| DORA (VO (EU) 2022/2554) | EU-Verordnung | mittelbar: Art. 73 Abs. 9 (gleichwertige Meldepflicht?) | hoch: IKT-Risiko, IKT-Vorfälle, IKT-Drittdienstleister | ❌ |
| Verbraucherkredit: RL (EU) 2023/2225 → BGB §§ 505a ff., KWG § 18a (BGBl. I 2026 Nr. 139) | Richtlinie → Gesetz | Art. 86 Abs. 3 | hoch: Kreditwürdigkeitsprüfung, ab 20.11.2026 | ❌ |
| BDSG § 37a (neu, Scoring) | Gesetz | DSGVO-Öffnungsklausel | hoch | ❌ – auf gesetze-im-internet.de noch nicht abrufbar (gilt ab 20.11.2026) |
| Wohnimmobilienkredit-RL 2014/17/EU | Richtlinie → BGB | – | mittel, wenn Baufinanzierung im Fall | ❌ |
| AGG §§ 19, 20 | Gesetz | – | mittel: Diskriminierung, Reichweite bei Kreditverträgen strittig | ❌ |
| EBA/GL/2020/06 | Leitlinie (Soft Law) | – | mittel: automatisierte Kreditmodelle | ❌ |
| KI-MIG | Gesetz | Art. 74 Abs. 6 (BaFin) | Zuständigkeit | ❌ (Sekundärquelle) |
| NIS2, BSIG, KRITIS-DachG, EnWG | vorhanden | – | für die Bank weitgehend verdrängt (DORA, NIS2 Art. 4 Abs. 1) | ✅ – bleiben für Fall 3 |

- **Abrufbar aus der Cloud (geprüft):** gesetze-im-internet.de antwortet (KWG § 25a). EUR-Lex lieferte auf den Shell-Abruf eine leere Antwort – EU-Texte also über das Amtsblatt-PDF, wie beim Omnibus.

# Befunde

| # | Befund | Wohin |
|---|---|---|
| BK-B6 | Art. 86 gilt nur, soweit das Erläuterungsrecht nicht anderweitig im Unionsrecht festgelegt ist (Abs. 3). Für Kreditscoring kommen DSGVO Art. 22 Abs. 3, Art. 15 Abs. 1 lit. h und die Verbraucherkredit-RL 2023/2225 dafür in Frage. Das README nennt Art. 86 ohne diesen Vorbehalt | Paket 4: mit der Neueinordnung; README nachziehen |
| BK-B7 | Art. 26 Abs. 5 UAbs. 2 erklärt für Finanzinstitute nur die Überwachungspflicht (UAbs. 1 Satz 1) für erfüllt, wenn sie ihr Governance-Recht einhalten – die Meldepflichten (Sätze 2–4) bleiben. G-OPS-03/R010 brauchen dafür einen zweiten Nachweisweg | Paket 5 |
| BK-B8 | Art. 26 Abs. 6 steht als eine Zeile mit zwei Unterabsätzen; UAbs. 2 (Finanzinstitute) hat keine eigene Einheit, „gedeckt“ gilt nur für UAbs. 1. Art. 26 Abs. 5 UAbs. 2 ist dagegen geschnitten | Paket 4 (Werkzeug wie A-W11) |
| BK-B9 | G-OPS-02 begründet die Reduktion nach Art. 73 Abs. 9 mit Nr. 2 unter CER/NIS2. Art. 73 Abs. 9 knüpft an den Anbieter und gleichwertige Meldepflichten; ob DORA dazu zählt, ist offen. Kernarm für die Bank: Art. 3 Nr. 49 lit. c | Paket 5 |
| BK-B10 | Der DSGVO-Pflichtenraum ist vollständig uneingeordnet (780 Zeilen ohne `scope`). Für die Bank verweist der AI Act direkt hinein – Art. 22, 35, 13–15 können nicht bis nach dem Agenten warten | BK-F5 (Paket 4) |
| BK-B11 | Es fehlen die Wortlaute, auf die der AI Act für die Bank verweist: CRD Art. 74/KWG § 25a, Verbraucherkredit (BGB, KWG § 18a), BDSG § 37a; dazu DORA, AGG, EBA/GL/2020/06 | BK-F5 (Paket 4) |
| BK-B12 | NIS2/BSIG, KRITIS-DachG, EnWG treffen die Bank weitgehend nicht – DORA ist sektorspezifischer Rechtsakt (NIS2 Art. 4 Abs. 1, ErwG 28). Damit fällt auch die Anker-Hypothese von R001/R003 (NIS2/BSIG) für die Bank; Kandidat DORA Kap. II | Paket 5 (mit F4) |
| BK-B13 | Art. 5 Abs. 1 lit. c (Sozialbewertung) wird für Scoring relevant: Daten aus fremden sozialen Kontexten sind das Abgrenzungsrisiko; die Verbraucherkreditreform schließt Daten aus sozialen Netzwerken aus | Paket 5 (R015) |
| BK-B14 | DORA Art. 28–30 (IKT-Drittdienstleister, Vertragsinhalte) und Art. 25 Abs. 2 n.F. (Übergabebelege beim Rollenwechsel) treffen dieselbe Beschaffung; ein Nachweis könnte beides tragen (HYPOTHESE) | Paket 5 (mit P3-F3) |

# Fragen

| # | Frage | Optionen |
|---|---|---|
| BK-F3 | Mechanik für drei Fälle im Pflichtenraum | a) **`scope` gilt dem Leitfall Bank; Zeilen nur für Fall 2 oder 3 gehen `out` mit Schalter-Vermerk** – wie FR-7 b · b) `scope` gilt allen drei Fällen zugleich (Profil-Mechanismus, FR-7 a wieder auf) |
| BK-F4 | Welche Bank ist der Leitfall? | a) **private Geschäftsbank, Scoring zugekauft** (K1, nur Betreiber) · b) Sparkasse/öffentlich-rechtliche Bank – dann Art. 27 „Einrichtung des öffentlichen Rechts“, ggf. Art. 49 Abs. 3 und Art. 111 Abs. 2 Satz 2 n.F. (HYPOTHESE) · c) Eigenentwicklung (K2) – Bank wird Anbieter, Art. 16 ff. (größter offener Block) |
| BK-F5 | Rechtsquellen für die Bank | a) **jetzt, begrenzt auf die Verweisnormen**: DSGVO Art. 22, 35, 13–15 einordnen; CRD Art. 74/KWG § 25a, Verbraucherkredit (BGB, KWG § 18a), BDSG § 37a als Wortlaut holen · b) alles erst im Sektorstapel nach dem Agenten (Plan C) · c) jetzt vollständig inkl. DORA |

**Entschieden 13.10.2026:** BK-F3 **b** (ein Pflichtenraum für alle drei Fälle – Profil-Mechanismus, löst FR-7 b ab; Entwurf in [Review 18](18-profil-mechanismus.md)) · BK-F4 **a** (private Geschäftsbank, Scoring zugekauft) · BK-F5 **c** (Rechtsquellen erst im Sektorstapel nach dem Agenten; BK-B10, BK-B11 dorthin).

# Ehrlich zur Methode

- Zeilen am Pflichtenraum auf c4a1ce9 gemessen (`scope_grund` „Systemtyp“, „Bereichsausnahme“, „Adressat … Finanzinstitute“ und Begründungen mit Redispatch/Nr. 2). Eine Gegenprobe auf Vollständigkeit läuft mit der Neueinordnung über die Wächter.
- AI-Act-Wortlaut im Repo geprüft: Art. 26 Abs. 5 UAbs. 2, Abs. 6 UAbs. 2, Art. 27 Abs. 1, Art. 49 Abs. 3, Art. 73 Abs. 9, Art. 86 Abs. 3; NIS2 Art. 4 Abs. 1 und ErwG 28.
- Nicht am Wortlaut geprüft (kein Text im Repo): DORA, CRD, Verbraucherkredit-RL und ihre Umsetzung, BDSG § 37a, AGG, EBA-Leitlinien, KI-MIG. Aussagen dazu sind Einordnung, kein Befund am Text. Kein Rechtsrat.
