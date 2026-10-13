---
titel: Drei Fälle in einem Pflichtenraum – Entwurf des Profil-Mechanismus (BK-F3 b)
stand: 2026-10-13
basis: Branch domain_bank = 73e2673 · Review 17 (Bank-Prüfliste) · Entscheide BK-F3 b, BK-F4 a, BK-F5 c (PO, 13.10.2026)
status: BK-F6 a (13.10.2026) · M1 gebaut · M2 Prüfliste Bank vorgelegt · Fragen R-10, BK-F7 an den PO
---

# Entscheide vom 13.10.2026

| ID | Entscheid | Folge |
|---|---|---|
| BK-F3 b | Ein Pflichtenraum für alle drei Fälle zugleich – Profil-Mechanismus | löst FR-7 b ab; FR-B2 (121 Zeilen nur wegen Nr. 2 `out`) geht darin auf |
| BK-F4 a | Leitfall ist eine private Geschäftsbank, die das Scoring zukauft (K1, nur Betreiber) | Art. 49 Abs. 3, Anhang VIII Abschn. C bleiben `out`; Schalter S3-1 („Betreiber ist Behörde“) für die Bank `false` – für die Klinik kann er greifen |
| BK-F5 c | Rechtsquellen der Bank erst im Sektorstapel nach dem Agenten (Plan C) | Art. 86 Abs. 3 und Art. 26 Abs. 5 UAbs. 2 verweisen auf Recht, das nicht im Repo liegt: die Zeilen bleiben HYPOTHESE, der Agent meldet „Verweisnorm nicht geprüft“ – wie „Anker offen“ bei F4 |

# Entwurf

```
docs/coverage/faelle/faelle.yaml            Fallregister
  bank    Leitfall  Art. 6 Abs. 2 + Anhang III Nr. 5 lit. b   private Bank, Zukauf (K1)   ab 02.12.2027
  klinik  Fall 2    Art. 6 Abs. 1 + Anhang I Abschn. A Nr. 11  Krankenhaus                 ab 02.08.2028
  netz    Fall 3    Art. 6 Abs. 2 + Anhang III Nr. 2           Verteilnetzbetreiber        ab 02.12.2027
        │
Pflichtenraum-Zeile
  scope: in | out                    wie heute; in = für mindestens einen Fall einschlägig
  faelle: [bank, netz]               nur, wenn die Zeile nicht für alle drei Fälle gilt
  befund_je_fall: {netz: …}          nur, wo ein Fall abweicht (Art. 26 Abs. 11: netz n.e., bank Lücke)
  verifikation_je_fall: {netz: …}    nur, wo die Stufe am Fall hängt (Anhang III Nr. 2: HYPOTHESE nur für netz)
        │
Manifest eines Laufs:  referenzfall: bank   ──►  Gates und Agent lesen nur die Zeilen dieses Falls
```

**Regeln**

1. **Fallregister** ist die eine Stelle für Einstufungsweg, Betreiber, Stichtag und die Entscheide je Fall.
2. **`faelle` fehlt = alle drei Fälle.** Steht es da, gilt die Zeile nur für die genannten.
3. **Abweichungen je Fall** stehen als `befund_je_fall` und `verifikation_je_fall`; alles andere erbt die Zeile.
4. **Neuer Wächter `CASE_SCOPE_DECLARED`:**
   - jeder Wert in `faelle` und in den `_je_fall`-Feldern ist ein Fall aus dem Register;
   - jede Zeile mit fallabhängiger Begründung (Systemtyp, Bereichsausnahme, Adressat Finanzinstitut oder Behörde) nennt `faelle` ausdrücklich – keine Zeile gilt stillschweigend für alle;
   - jeder Fall hat seine Einstufungsnorm `in` (bank: Anhang III Nr. 5 lit. b · klinik: Anhang I Abschn. A Nr. 11 · netz: Anhang III Nr. 2).
5. **Die bestehenden Wächter bleiben** und lesen `scope` wie bisher; `IN_UNITS_VERIFICATION_DECLARED` prüft die Überschreibungen mit.
6. **Entscheidungsdateien** setzen `faelle` wie jedes andere Feld (`setze: {faelle: [bank]}`), `po_entscheide.py` lernt die neuen Felder.

**Schritte**

| # | Schritt | Wer | Umfang |
|---|---|---|---|
| M1 | Fallregister, Schema, Werkzeug, Wächter mit Gegenprobe; alle heutigen Entscheide werden das Profil `netz` | KI | M |
| M2 | Prüfliste Bank: die Zeilen aus Review 17 Teil 1 (16 neu, 6 nur Fall 2/3, Art. 26 Abs. 11, Q1/Q11) als `faelle`-Vorschläge | KI → PO | S–M |
| M3 | Prüfliste Klinik: Anhang-I-Weg (Systemtyp-Zeilen zu Anhang I, Art. 2 Abs. 13 n.F., Art. 73 Abs. 10, Art. 113 Abs. 3 lit. c Ziff. ii n.F.) | KI → PO | M, mit FR-2/FR-8 |
| M4 | Gates lesen `referenzfall` (G-PRE-01 je Einstufungsweg, G-OPS-02 je Meldepfad) | KI, Ehrlichkeitsfelder PO | Paket 5/6 |

- **Was sich für den Leser ändert:** Jede Zeile sagt, für welchen Fall sie gilt. Eine Zahl wie „`in` 125“ wird je Fall ausgewiesen (bank · klinik · netz) plus die Vereinigung.
- **Preis:** drei weitere Felder, ein Wächter, ein Register; die Prüflisten M2 und M3 sind PO-Arbeit wie IN-1.

# Frage

| # | Frage | Optionen |
|---|---|---|
| BK-F6 | Wann bauen wir M1 und M2? | a) **jetzt, vor S3-4 G2** – der Leitfall braucht seinen Pflichtenraum, sonst prüft S3-4 Zeilen eines anderen Falls · b) mit Paket 5, wie FR-B2 geplant war; S3-4 G2 vorher |

**Entschieden 13.10.2026:** BK-F6 **a** – M1 und M2 jetzt, vor S3-4 G2.

# M1 – gebaut (13.10.2026)

- **Fallregister** `docs/coverage/faelle/faelle.yaml`: bank, klinik, netz mit Einstufungsweg, Einstufungsnorm, Betreiber, Stichtag, Entscheiden; `pflichtenraum: geprueft` nur für netz. Liegt in einem Unterordner, weil `LEGAL_QUOTES_VERBATIM` jede YAML-Datei direkt unter `docs/coverage/` als Pflichtenraum liest.
- **Werkzeug** `tools/legal/faelle.py`: erkennt fallabhängige Zeilen an Textmarken der Begründung (Systemtyp, Bereichsausnahme, Redispatch, Anhang III Nr. …, Finanzinstitut …) oder an der Liste im Register; `--migrieren` schreibt `faelle` aus dem heutigen `scope` (= Netz).
- **Migration:** 185 fallabhängige Zeilen tragen jetzt `faelle` (AI Act 140, Omnibus 45): 20 `in` mit `faelle: [netz]`, 165 `out` mit `faelle: []`. Keine Zeile hat `scope`, Befund oder Stufe geändert.
- **Stand je Fall:** `in` netz 125 · bank 105 · klinik 105 – bank und klinik sind `offen`; die 105 sind die fallunabhängigen Zeilen, die für alle gelten.
- **Wächter** `CASE_SCOPE_DECLARED` (MEDIUM, Vorschlag R-10) in `make verify`.
- `po_entscheide.py` braucht keine Änderung: es setzt jedes Feld einer Entscheidungsdatei, also auch `faelle`.

| # | Frage | Optionen |
|---|---|---|
| R-10 | Severity `CASE_SCOPE_DECLARED` | a) **MEDIUM** – wie `IN_UNITS_VERIFICATION_DECLARED`: versteckt keine Pflicht, lässt aber eine Entscheidung für den falschen Fall gelten · b) HIGH – ein Agent-Urteil für die Bank auf Netz-Zeilen wäre ein falsches Urteil |

# M2 – Prüfliste Bank (Vorschlag)

- Liegt im Project als `claude/pruefliste-m2-bank.md`. Gruppen A–J, je Zeile `faelle`, Befund, Stufe.
- **Ergebnis bei GO:** `in` für die Bank 134 Zeilen (105 fallunabhängig + 29 fallabhängig), Vereinigung 141; netz unverändert 125; Fallregister `bank: geprueft`.
- Abweichungen je Fall: Art. 26 Abs. 11 (Lücke, für netz n.e. nach Q11 a), Art. 73 Abs. 9 (eigene HYPOTHESE für bank).
- `befund_je_fall` und `verifikation_je_fall` tragen ihren Grund: `{befund: …, befund_grund: …}` bzw. `{verifikation: …, hypothese_grund: …}`; `faelle.py` prüft beide Formen.

| # | Frage | Optionen |
|---|---|---|
| BK-F7 | Prüfliste M2 Bank (Gruppen A–J) | a) **alles wie vorgeschlagen** · b) mit Abweichungen je Gruppe |

# Ehrlich zur Methode

- Entwurf, nicht gebaut. Die Feldnamen sind Vorschlag; was eine Zeile je Fall ist (`in`/`out`, Befund, Stufe), entscheidet der PO über die Prüflisten M2 und M3.
- Umfangsangaben sind Schätzungen.
