---
titel: Grenze statt Teilabdeckung – Einordnung und Hinweisfunktion
stand: 2026-09-28
basis: Branch review-2c · 39 Teilabdeckungen + 3 bisher „gedeckt“ (2d) · PO-Idee 28.09.: Teilabdeckung als Grenze mit Hinweisfunktion
status: VORSCHLAG – Entscheidungsvorlage H1–H4 in Teil 4
---

# Kurzfazit
- „Teilabdeckung“ vermischte zwei Achsen: **Was** wird geprüft (Befund) und **wie stark** ist der Beleg (E-0 bis E-3).
- Getrennt ergibt sich:
  - **26 echte Grenzen:** Ein Element der Pflicht prüft kein Check.
  - **4 Kettengrenzen:** Das Gate prüft, aber kein Requirement trägt die Pflicht (Art. 25, bis R017).
  - **6 gedeckt mit E-0:** Alle Elemente werden geprüft, aber nur als Selbstauskunft.
  - **6 zurückgestellt:** Art. 15 wartet auf F4, Art. 26 Abs. 11 auf Schritt 3.
- **Grenze mit Hinweisfunktion:**
  - Jede Grenze wird am Gate deklariert und bei **jedem** Lauf als Hinweis ausgegeben, auch bei PASS.
  - Das Urteil ändert der Hinweis nicht; ein Wächter hält Pflichtenraum und Gate gegeneinander.
  - Vorbild im Repo: `design_only` und `runtime_coverage: declared_gap` – beides deklarierte Grenzen, die das Gate selbst ausspricht.

# Teil 1 – Das Modell

```
Befund (was)                       Beweisachse (wie stark)
─────────────────────────          ──────────────────────────
gedeckt   alle Elemente geprüft  →  evidence_level E-0 … E-3
grenze    Element X ungeprüft    →  Hinweis in jedem Gate-Lauf
luecke    nichts trifft          →  Paket (P0–P8)
nicht_einschlaegig  keine Pflicht
```

**Gate-Lauf mit Grenze:**
```
G-DEP-04  PASS
  HINWEIS  Grenze Art. 13 Abs. 3 lit. a – Bevollmächtigter des Anbieters nicht geprüft (M-A1)
  HINWEIS  Grenze Art. 26 Abs. 1 – Umsetzung der Einsatzgrenzen aus der Anleitung nicht geprüft (M-E1)
```

- **Hinweis ≠ Warnung:**
  - `warn` heißt im Repo: Ein SHOULD-Check ist am **Input** verletzt.
  - Eine Grenze ist eine Eigenschaft des **Gates**, gleich bei jedem Lauf. Als `warn` stünde jeder Lauf auf Gelb; niemand liest das mehr (Alarmmüdigkeit).
  - Deshalb eine eigene Stufe `hinweis`: sichtbar, aufgezeichnet, ohne Einfluss auf das Urteil.
- **Wo die Grenze steht:**
  - im Pflichtenraum als `befund: grenze` mit `befund_grund` (was ungeprüft ist) und Maßnahme
  - am Gate als `known_limits: [{pflicht, nicht_geprueft, massnahme}]`
  - im Evidence-Record als Liste der Grenzen, unter denen das Urteil gefällt wurde
- **Wächter `GATE_LIMITS_DECLARED`:**
  - Jede `grenze` im Pflichtenraum steht als `known_limits` am genannten Gate, und umgekehrt.
  - Gleiches Muster wie `TRIGGER_MATCHES_REQUIREMENT` für `declared_gap`.

# Teil 2 – Einordnung der 42 Zeilen

Klassen: **G** Grenze (Element ungeprüft) · **K** Kettengrenze (Requirement fehlt) · **D** gedeckt mit E-0 (alles geprüft, nur deklariert) · **F4** zurückgestellt bis Anker · **V** vertagt

| # | Einheit | Kl. | Was ungeprüft ist bzw. warum D | Maßnahme |
|---|---|---|---|---|
| 1 | Art. 13 Abs. 1 | G | „hinreichend transparent“ – materielle Qualität | M-A2 |
| 2 | Art. 13 Abs. 2 | G | präzise, vollständig, verständlich, barrierefrei | M-A2 |
| 3 | Art. 13 Abs. 3 | G | Pflichtinhalte lit. a–f | M-A1 |
| 4 | Art. 13 Abs. 3 lit. a | G | Bevollmächtigter (Art. 22) | M-A1 |
| 5 | Art. 13 Abs. 3 lit. b | G | Pflichtinhalte Ziff. i–vii | M-A1 |
| 6 | … lit. b Ziff. i | G | Zweckbestimmung in der Anleitung | M-A1 |
| 7 | … lit. b Ziff. ii | G | Genauigkeits-/Robustheitsmaße in der Anleitung | M-A1 |
| 8 | … lit. b Ziff. iii | G | bekannte Risikoumstände in der Anleitung | M-A1 |
| 9 | … lit. b Ziff. v | G | Leistung für Personengruppen in der Anleitung | M-A1 |
| 10 | … lit. b Ziff. vi | G | Eingabedaten-Spezifikation in der Anleitung | M-A1 |
| 11 | Art. 13 Abs. 3 lit. d | G | Aufsichtsmaßnahmen in der Anleitung | M-A1 |
| 12 | Art. 13 Abs. 3 lit. f | G | Protokollierungsmechanismen in der Anleitung | M-A1 |
| 13 | Art. 14 Abs. 1 | G | Beaufsichtigbarkeit als Systemeigenschaft | M-B4 |
| 14 | Art. 14 Abs. 3 | **D** | Angemessenheit wird im manuellen Review der HYBRID-Gates geprüft – Beleg ist das Review | – |
| 15 | Art. 14 Abs. 3 lit. b | G | Kette Anbieter-Vorgabe → Betreiber-Umsetzung | M-B4 |
| 16 | Art. 14 Abs. 4 | G | Befähigung der Aufsichtspersonen | M-B2 (P2) |
| 17 | Art. 14 Abs. 4 lit. a | G | Fähigkeit, Anomalien zu erkennen | M-B2 (P2) |
| 18 | Art. 14 Abs. 4 lit. d | **D** | Override-Möglichkeit ist geprüft (G-OPS-01); ob er genutzt wird, ist Beweis, nicht Element | Beweis: M-B1 (P5) |
| 19 | Art. 14 Abs. 4 lit. e | G | „sicher zum Stillstand“ | M-B3 |
| 20 | Art. 26 Abs. 2 | G | Kompetenz, Ausbildung, Befugnis, Unterstützung | M-B2 (P2) |
| 21 | Art. 25 Abs. 1 | G | Folgepflichten nach Art. 16 – bewusst offen (K2/K3) | – |
| 22 | Art. 25 Abs. 1 lit. a | **K** | Requirement fehlt (G-OPS-06 hängt an R001) | R017 (F6) |
| 23 | Art. 25 Abs. 1 lit. b | **K** | Requirement fehlt; Schwelle fehlt (SHOULD) | R017, M-D2 |
| 24 | Art. 25 Abs. 1 lit. c | **K** | Requirement fehlt | R017 |
| 25 | Art. 25 Abs. 2 | **K** | Requirement fehlt; `notify` nur deklariert | R017, M-D3 |
| 26 | Art. 26 Abs. 1 | G | technische und organisatorische Maßnahmen für die Verwendung nach der Anleitung | M-E1 |
| 27 | Art. 26 Abs. 5 UAbs. 1 Satz 1 | G | Information an den Anbieter | M-E2 |
| 28 | Art. 26 Abs. 5 UAbs. 1 Satz 3 | G | Reihenfolge der Meldekette | M-E3 (P6) |
| 29 | Art. 26 Abs. 5 UAbs. 1 Satz 4 | G | Fallback bei unerreichbarem Anbieter | M-E4 (P6) |
| 30 | Art. 26 Abs. 6 | **D** | Aufbewahrung ≥ 180 Tage ist geprüft, aber als Konfiguration | Beweis: M-E5 (E-3) |
| 31 | Art. 26 Abs. 11 | V | Q11 | Schritt 3 |
| 32 | Art. 73 Abs. 1 | G | dass Art. 73 dem Betreiber nur im Fallback gilt | M-F1 |
| 33 | Art. 73 Abs. 2 UAbs. 1 Satz 1 | G | Fristbeginn bei Kenntnis des Betreibers | M-F1 |
| 34 | Art. 73 Abs. 2 UAbs. 2 Satz 1 | **D** | Abstufung nach Schwere in C-04 abgebildet | Beweis: M-F3 (Uhr) |
| 35 | Art. 73 Abs. 3 | **D** | 48 h korrekt in C-04 | Beweis: M-F3 |
| 36 | Art. 73 Abs. 4 | **D** | 10 Tage korrekt in C-04 | Beweis: M-F3 |
| 37 | Art. 73 Abs. 9 | G | Reduktion an falscher Bedingung (Anbieter- statt Betreiberstatus) | M-F2 |
| 38–42 | Art. 15 Abs. 1, 3, 4 UAbs. 1 Satz 1 und 2, Abs. 5 | F4 | Einordnung, sobald der Anker steht | – |

**Summe:** G 26 · K 4 · D 6 · F4 5 · V 1 = 42

**Ergebnis nach Umstellung (AI-Act-Raum):** gedeckt 6 (alle E-0) · grenze 30 · luecke 28 · Art. 15/Art. 26 Abs. 11 wie bisher offen. Die 6 „gedeckt“ sind ehrlich, weil die Beweisachse daneben steht: E-0, Ziel höher.

# Teil 3 – Was sich wo ändert

| Ort | Änderung | Wann |
|---|---|---|
| Pflichtenraum | `teilabdeckung` → `grenze` bzw. `gedeckt`; neue Entscheidungsdatei | nach deinem Entscheid, sofort |
| `verify_norm_quotes.py`, T-13-Raster | Befundwert `grenze` statt `teilabdeckung`, Definition: „Element ungeprüft, benannt, mit Maßnahme oder bewusst offen“ | sofort, mit dem Pflichtenraum |
| Gate-Definitionen (17) | Feld `known_limits` | Schritt 4 (Bedarfsanalyse) → Bau Schritt 5 |
| Orchestrator, Report, Evidence-Record | Stufe `hinweis`, Ausgabe bei jedem Lauf | Schritt 5 |
| Integrity-Suite | `GATE_LIMITS_DECLARED` (bidirektional) | Schritt 5, im selben Commit wie `known_limits` |

# Teil 4 – Entscheidungsvorlage

**a ist jeweils die Empfehlung.**

| # | Entscheidung | Optionen |
|---|---|---|
| **H1** | Befundwert `teilabdeckung` heißt künftig `grenze` (Element ungeprüft, benannt) | a) ja · b) Name bleibt, Bedeutung wird enger gefasst |
| **H2** | Die 6 D-Zeilen werden `gedeckt`; ihre Schwäche steht auf der Beweisachse (E-0) | a) ja · b) bleiben Grenze |
| **H3** | Die 4 Art.-25-Zeilen sind Kettengrenzen und werden mit R017 gedeckt (ersetzt D1; Zeile 4 ersetzt D2) | a) ja · b) nein |
| **H4** | Hinweisfunktion: `known_limits` am Gate, Stufe `hinweis` in jedem Lauf, Urteil unverändert, Wächter `GATE_LIMITS_DECLARED` | a) so, Bau in Schritt 5 · b) als `warn` (SHOULD-Logik) · c) nur im Pflichtenraum, keine Ausgabe im Lauf |

Unverändert offen aus 05: **E1** (G-DEP-06 auf Abs. 6), **E2** (Check-ID in Rego-Meldungen), **E3** (R007-Kriterium auf `gap`).
