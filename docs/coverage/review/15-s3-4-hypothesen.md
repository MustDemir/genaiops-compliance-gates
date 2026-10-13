---
titel: S3-4 – HYPOTHESE-Zeilen gegen Quellen prüfen (Teil 1: G1 Anhang III Nr. 2, G4 Art. 79 Abs. 2)
stand: 2026-10-13
basis: Branch review-2c, Stand 5ac2628 (gemessen: in 125, VERIFIZIERT 70, HYPOTHESE 55) · Arbeitsliste claude/s3-4-arbeitsliste.md (Project) · Entscheid S3-4 a (06.10.2026)
status: Vorschlag · G1 und G4 geprüft, Fragen S34-F1 bis S34-F3 an den PO · G2, G3, G5 folgen
---

# Kurz

- **G1 (Anhang III Nr. 2):** Der Leitlinien-Entwurf der Kommission ist jetzt **im Original** gelesen. Er bestätigt FR-B1: Ein Redispatch-Planer mit Freigabe durch die Leitstelle ist **nicht eindeutig** Hochrisiko – nach der Linie des Entwurfs eher nicht. Offen bleibt Arm B (Ausfall gefährdet), den der Entwurf für Nr. 2 nicht prüft, das Gesetz aber kennt.
- **Vorschlag G1:** Zeile bleibt **HYPOTHESE**, mit neuem Grund. Leitfall wechseln auf einen Fall, den der Entwurf selbst als Sicherheitsfunktion nennt (S34-F1).
- **Neu aus dem Entwurf:** Nr. 2 greift nur, wenn der **Betreiber** als kritische Einrichtung bestimmt ist (CER, in Deutschland KRITIS-DachG). G-PRE-01 fragt das nicht ab (S34-F2).
- **G4 (Art. 79 Abs. 2):** am Wortlaut belegbar über die Legaldefinition „Akteur“ (Art. 3 Nr. 8). Vorschlag **VERIFIZIERT**, wenn der PO die Regel so fasst (S34-F3).

```
55 HYPOTHESE ── G1   1 ── geprüft: bleibt HYPOTHESE (neuer Grund)          ◄ diese Review
             ├─ G4   1 ── geprüft: VERIFIZIERT, falls S34-F3 a             ◄ diese Review
             ├─ G2  46 ── offen (Durchschlagsregel 2b E4)
             ├─ G3   6 ── folgt G2 / Art. 73
             └─ G5   1 ── offen (Anhang-I-Weg, FR-8)
```

# Teil 1 – G1: Anhang III Nr. 2 und der Leitfall Redispatch

## Quelle

| Dokument | Seiten | sha256 |
|---|---|---|
| Draft Guidelines on the classification of high-risk AI: General principles | 6 | `b127bbdc50b1741bb2d97e8aff5839cccd1a4484445be4e8cca246c12541fc42` |
| Draft Guidelines … : Annex I of AI Act | 13 | `10f1302c9090d2bcfdb8eacd2b36ff7a09860fc7909f7c1c4b42cc3b9bed3b50` |
| Draft Guidelines … : Annex III of AI Act | 148 | `b1df0ffb30310e126c7e060e03c9b5aab97c0a2ab61a2f3e3e00ede3655e2792` |

- Abgerufen am 13.10.2026 über die Bibliotheksseite der Kommission (digital-strategy.ec.europa.eu, „Draft Commission guidelines on the classification of high-risk AI systems“, 19.05.2026); PDF-Erstellungsdatum 19.05.2026.
- **Status:** Entwurf zur Konsultation. Die Konsultation lief bis 23.07.2026 (verlängert von 23.06.); die endgültigen Leitlinien will die Kommission bis Ende 2026 annehmen. Ein Entwurf ist keine amtliche Auslegung.
- Randnummern (Rn.) unten beziehen sich auf das Dokument „Annex III“, wenn nicht anders genannt. Wiedergabe sinngemäß.

## Was der Entwurf zu Nr. 2 sagt

```
Anhang III Nr. 2 ── zwei Bedingungen (Abschn. 3.2.1)
  1. Sicherheitsbauteil (Art. 3 Nr. 14) ── direkte Schutzfunktion für die physische Unversehrtheit
       Rn. 180  Maßstab ist die Schutzfunktion des Systems selbst
       Rn. 181  bloß unterstützend, informierend, organisatorisch, optimierend ─► nicht Hochrisiko
       Rn. 184  nur sechs Funktionen: a erkennen · b Wartungsbedarf erkennen · c verhindern
                · d begrenzen/steuern · e Folgen mindern (z. B. Sicherheitsabschaltung) · f überwachen
       Rn. 185  nicht-physische Schäden zählen nicht
       Rn. 186  vorhandene Redundanz/Rückfallebene zählt gegen die Einstufung
  2. kritische Infrastruktur nach CER ── Betreiber muss als kritische Einrichtung bestimmt sein
       Rn. 189 f.  über Art. 3 Nr. 62 → CER-Richtlinie → Delegierte VO (EU) 2023/2450
       Rn. 203 f.  Stromversorgung: Lieferanten, VNB, ÜNB, Erzeuger, NEMO, Marktteilnehmer
```

**Beispiele zur Stromversorgung (S. 47 f.):**

| Hochrisiko nach Entwurf | Nicht Hochrisiko nach Entwurf |
|---|---|
| Perimeterschutz (Kamera, Radar, Drohnen) zum direkten Schutz der Anlage | Netzoptimierung über Lastprognose – Sicherheitsfunktionen laufen getrennt |
| Anomalieerkennung im Netzbetrieb zur Überwachung und Entscheidungsunterstützung bei kritischen Funktionen (Lastverteilung, Netzstabilität, Abschaltverfahren) | Störungsfrüherkennung mit Warnung an die Leitstelle – nur vorsorglich, handelt nicht selbst |
| | Anomalieanalyse, vom Menschen geprüft, als Grundlage künftiger Verbesserungen |
| | Verbrauchsprognose als Assistent |
| | vom Menschen überwachte Ungleichgewichtsprognose (15 min), die Fahrplan und Markt beeinflusst und über eine Fehlfunktion die Netzstabilität treffen kann – nicht Hochrisiko „mangels direkten Zusammenhangs“ mit dem Schaden |
| | Cyber-Monitoring, Qualitätskontrolle Zählereinbau |

**Menschliche Beteiligung und Art. 6 Abs. 3:**

- Rn. 70 f.: Menschliche Beteiligung ändert die Einstufung nicht. Sie zählt nur, um eine Ausnahme nach Art. 6 Abs. 3 zu begründen.
- Rn. 108: Wer einen **konkreten Vorschlag** zum Fall liefert, erledigt keine vorbereitende Aufgabe (lit. d).

## Abgleich mit dem Leitfall

```
Redispatch-Planer beim VNB (heute Leitfall)
  Zweck: Engpässe erkennen, Maßnahmen planen, Freigabe Leitstelle, Abruf über Redispatch 2.0

  Arm A  Sicherheitsfunktion ............ eher NEIN   optimiert den Betrieb (Rn. 181); Netzschutz
                                                       schützt die Betriebsmittel getrennt (Rn. 186)
  Arm B  Ausfall gefährdet .............. OFFEN       Entwurf prüft Arm B bei Nr. 2 nicht (s. u.)
  CER    Betreiber kritische Einrichtung  OFFEN       hängt am VNB, nicht am System (Rn. 190, 204)
  Art. 6 Abs. 3 ......................... greift NICHT  Rn. 70 f., 108: Freigabe ändert nichts,
                                                       ein Maßnahmenplan ist ein konkreter Vorschlag
  ────────────────────────────────────────────────────────
  ⇒ nicht eindeutig Hochrisiko; nach der Linie des Entwurfs eher nicht
```

- **Gegenargument zu Arm A:** Engpassmanagement hält Ströme unter thermischen Grenzen, und die schützen Betriebsmittel physisch. Ruft das System Maßnahmen **ohne** Freigabe selbst ab, rückt es an Rn. 184 lit. d heran. Der Entwurf nennt diesen Fall nicht.
- **Arm B – die Lücke im Entwurf:** Art. 3 Nr. 14 n.F. kennt zwei Alternativen (Sicherheitsfunktion **oder** Ausfall gefährdet). Der Omnibus hält Arm B zusätzlich in Art. 6 Abs. 1b n.F. fest (ABl. vom 24.07.2026, also **nach** dem Entwurf). Der Anhang-I-Teil des Entwurfs prüft beide Alternativen (Annex I, Rn. 34, 38, 42 f.: sogar ein Effizienz-Optimierer kann über Arm B Sicherheitsbauteil sein). Der Nr.-2-Teil prüft nur Arm A (Rn. 180–184). Für Redispatch ist Arm B die eigentliche Frage. Der Entwurf beantwortet sie nicht ausdrücklich, deutet mit dem Beispiel der Ungleichgewichtsprognose aber eine enge Linie an.
- **CER-Bedingung in Deutschland:** Die CER-Richtlinie setzt das KRITIS-DachG um. Ein VNB ist danach „Betreiber kritischer Anlagen“ (§ 2 Nr. 1, 3), wenn seine Anlage die Schwelle der Rechtsverordnung nach § 5 erreicht, und registriert sich (§ 8). Nach Sekundärquellen gilt das Gesetz seit 17.03.2026; die Rechtsverordnung lag am 21.09.2026 als Entwurf vom 26.05.2026 vor, Regelwert 500.000 versorgte Einwohner. Viele VNB liegen darunter – ihre KI wäre nach dem Entwurf dann **gar nicht** Nr.-2-Hochrisiko, gleich welche Funktion sie hat.
- **Fixture:** `art6_redispatch_pass.json` bejaht Arm A und Arm B als Selbstauskunft und beschreibt einen Übertragungsnetzbetreiber, nicht den VNB des Leitfalls.

## Was ein eindeutiger Nr.-2-Fall wäre

- Der Ersatz aus der Arbeitsliste („KI im Lastausgleich, deren Ausfall Versorgungsunterbrechungen verursacht“) trägt nach dem Entwurf **nicht**: Versorgungsausfall allein reicht nicht, verlangt ist eine physische Gefahr für Personen oder Sachen (Rn. 180, 183, 185).
- Eindeutig sind Funktionen aus Rn. 184, die der Entwurf auch im Anhang-I-Teil als Sicherheitsfunktion führt. Im Netzbetrieb am nächsten:
  - **Zustandsüberwachung der Betriebsmittel** (Rn. 184 lit. b): KI erkennt Verschleiß oder Schäden an Transformatoren, Leitungen, Schaltanlagen, die ohne Wartung direkt zu physischem Schaden führen können. Das war bisher der geplante **Negativfall** (HANDBUCH 4.4, D-22) – nach dem Entwurf ist es ein Positivfall.
  - **Anomalieerkennung im Netzbetrieb** mit Entscheidungsunterstützung bei kritischen Funktionen (Beispiel „Hochrisiko“ S. 47). Grenzt eng an drei Beispiele „nicht Hochrisiko“ derselben Seite.
- **Ein Wechsel innerhalb von Nr. 2 lässt die bisherigen Entscheide stehen:** Q1 b (Art. 27 nimmt Nr. 2 aus), Q11 a (Entscheidungen betreffen Betriebsmittel, nicht Personen), FR-B2 (121 Zeilen wegen Nr. 2 `out`).

## Vorschlag je Zeile

| Zeile | heute | Vorschlag | Fundstelle |
|---|---|---|---|
| Anhang III Nr. 2 | HYPOTHESE (Grund: keine Leitlinien, keine Rechtsprechung) | **bleibt HYPOTHESE**, Grund neu: „Leitlinien-Entwurf vom 19.05.2026 im Original gelesen (Annex III Rn. 180–186, 190, 204, S. 47 f.): verlangt eine direkte Schutzfunktion (Arm A) und einen Betreiber, der als kritische Einrichtung bestimmt ist; ein Planungswerkzeug mit Freigabe ist danach eher nicht Hochrisiko. Arm B (Art. 3 Nr. 14 2. Alt., Art. 6 Abs. 1b n.F.) prüft der Entwurf für Nr. 2 nicht. Entwurf, nicht endgültig.“ | Annex III Rn. 70 f., 108, 180–186, 189 f., 203 f., S. 47 f.; Annex I Rn. 34, 38, 42 f. |

# Teil 2 – G4: Art. 79 Abs. 2

- **Wortlaut:** „Die betreffenden Akteure arbeiten erforderlichenfalls mit der Marktüberwachungsbehörde … zusammen.“ Art. 3 Nr. 8 definiert „Akteur“ und nennt den Betreiber wörtlich; die Begriffsbestimmungen gelten „für die Zwecke dieser Verordnung“ (Art. 3 Einleitungssatz).
- **Regel S3-3 heute:** VERIFIZIERT, wenn die Einheit den Betreiber nennt oder eine Betreiber-Norm wörtlich auf sie verweist. Art. 79 Abs. 2 tut keins von beiden – er nennt einen Begriff, den eine Legaldefinition auf den Betreiber erstreckt. Das ist Wortlaut, aber nicht von der Regel erfasst (S34-F3).
- **Reichweite:** Unter den 55 HYPOTHESE-Zeilen trägt nur Art. 79 Abs. 2 seine Einordnung allein über „Akteur“. Art. 3 Nr. 61 lit. b nennt „Akteur“ auch, hängt aber an Art. 73 (G3).
- **Grenze der Pflicht:** Marktrücknahme und Rückruf (UAbs. 2) treffen praktisch den Anbieter. Für den Betreiber trägt die Zusammenarbeit (UAbs. 1 Satz 4). Die Zeile ist `luecke` (P6); daran ändert die Stufe nichts.

| Zeile | heute | Vorschlag | Fundstelle |
|---|---|---|---|
| Art. 79 Abs. 2 | HYPOTHESE (Grund: nennt „Akteure“, nicht den Betreiber) | **VERIFIZIERT**, falls S34-F3 a: „Art. 79 Abs. 2 UAbs. 1 Satz 4 verpflichtet ‚die betreffenden Akteure‘; Art. 3 Nr. 8 nennt den Betreiber wörtlich als Akteur.“ | Art. 79 Abs. 2 UAbs. 1 Satz 4 i.V.m. Art. 3 Nr. 8 |

# Befunde

| # | Befund | Wohin |
|---|---|---|
| S34-B1 | Leitlinien-Entwurf (19.05.2026) im Original: Nr. 2 verlangt eine direkte Schutzfunktion (Rn. 180–184), optimierende Systeme sind ausgenommen (Rn. 181), Redundanz spricht dagegen (Rn. 186), Prognose-, Empfehlungs- und Warnsysteme mit menschlicher Prüfung sind nicht Hochrisiko (S. 47 f.); menschliche Freigabe ändert nichts, Art. 6 Abs. 3 greift für einen Maßnahmenplan nicht (Rn. 70 f., 108). Der Redispatch-Planer ist danach nicht eindeutig Hochrisiko, eher nicht | S3-4 (Paket 4): Anhang III Nr. 2 bleibt HYPOTHESE, Grund neu; Leitfall S34-F1 |
| S34-B2 | Der Nr.-2-Teil des Entwurfs prüft nur Arm A; Arm B (Art. 3 Nr. 14 2. Alt., Art. 6 Abs. 1b n.F., Omnibus nach dem Entwurf erlassen) bleibt dort ungeprüft, während der Anhang-I-Teil beide Arme prüft (Annex I Rn. 34, 38, 42 f.) | FR-5 (juristische Zweitprüfung, Paket 9) |
| S34-B3 | CER-Bedingung (Rn. 190, 204): Nr. 2 nur, wenn der Betreiber als kritische Einrichtung bestimmt ist – in Deutschland Betreiber kritischer Anlagen nach KRITIS-DachG (§ 2 Nr. 1, 3, § 5, § 8); Rechtsverordnung mit Schwellen laut Sekundärquelle noch Entwurf. G-PRE-01 fragt den Status nicht ab | Paket 5: Schalter nach S34-F2 |
| S34-B4 | HANDBUCH 4.4 nennt die Redispatch-KI „eindeutig Sicherheitsbauteil über beide Arme“ (widerspricht HYPOTHESE und HANDBUCH 1.4 „Einstufung offen bis S3-4“) und plant prädiktive Instandhaltung als Negativfall (D-22), die nach Rn. 184 lit. b eine Sicherheitsfunktion ist | mit S34-F1 (Paket 4): HANDBUCH 1.4/4.4 nachziehen |
| S34-B5 | Fixture `art6_redispatch_pass.json` beschreibt einen Übertragungsnetzbetreiber; der Leitfall ist ein Verteilnetzbetreiber | FR-2 (Paket 6) |
| S34-B6 | Review 14 (FR-B1) nennt Konsultation bis 23.06.2026; sie lief bis 23.07.2026, die endgültigen Leitlinien sind bis Ende 2026 angekündigt – Wiedervorlage für G1, sobald sie erscheinen | jederzeit |

# Fragen

| # | Frage | Optionen |
|---|---|---|
| S34-F1 | Leitfall Netzbetrieb nach G1 | a) **wechseln auf Zustandsüberwachung der Betriebsmittel** (Rn. 184 lit. b, auch im Anhang-I-Teil als Sicherheitsfunktion), Betreiber ist Betreiber kritischer Anlagen; Redispatch bleibt als Grenzfall-Fixture, an dem der Agent „Einstufung strittig“ zeigt · b) wechseln auf Anomalieerkennung im Netzbetrieb (Beispiel „Hochrisiko“ S. 47), Redispatch als Grenzfall · c) Redispatch halten, Einstufung über Arm B, HYPOTHESE bleibt |
| S34-F2 | Status „Betreiber kritischer Anlagen“ (CER / KRITIS-DachG) als Bedingung für Nr. 2 im Manifest | a) **ja, als Einzelschalter wie FR-1 a** (Bau Paket 5); G-PRE-01 meldet „Nr. 2 nach Entwurf nicht erfüllt“, wenn der Status fehlt, Vermerk „Entwurf“ · b) erst nach den endgültigen Leitlinien |
| S34-F3 | Regel für VERIFIZIERT (S3-3) erweitern: am Wortlaut belegt ist auch eine Einheit, die einen Begriff verwendet, den eine Legaldefinition des AI Act wörtlich auf den Betreiber erstreckt | a) **ja** – Art. 79 Abs. 2 wird VERIFIZIERT (heute die einzige Zeile, die das trifft) · b) nein, Art. 79 Abs. 2 bleibt HYPOTHESE |

**Entschieden 13.10.2026 (nur auf `domain_bank`):** S34-F1 – keine der Optionen: Leitfall wird eine Bank mit Kreditscoring (Anhang III Nr. 5 lit. b), Netzbetrieb Fall 3, eigene Branch `domain_bank` ([Review 16](16-leitfall-bank.md)). S34-F2 und S34-F3 offen.

# Ehrlich zur Methode

- Der Entwurf ist im Original gelesen (Text aus den PDFs mit pdftotext, Hashes oben). Wiedergabe sinngemäß, keine amtliche Übersetzung; deutsche Sprachfassung gibt es nicht.
- Zum KRITIS-DachG: Begriffe und Paragraphen am Wortlaut im Repo (`docs/legal/wortlaut/kritisdachg_DE.txt`, abgeleitete Zusammenstellung vom 07.09.2026). Inkrafttreten 17.03.2026, Stand der Rechtsverordnung und Regelwert 500.000 aus Kanzleibeiträgen (Advant Beiten 21.09.2026, beck-aktuell 06.03.2026) – **SEKUNDÄRQUELLE**.
- Ob Redispatch Arm B erfüllt, ist eine technische und rechtliche Wertung (Netzschutz als Redundanz, Ausfallfolgen). Diese Review ordnet ein, sie entscheidet nicht – kein Rechtsrat.
- G2, G3, G5 sind noch nicht geprüft.
