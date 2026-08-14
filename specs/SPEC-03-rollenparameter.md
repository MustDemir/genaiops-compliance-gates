# SPEC-03 — Rollenparameter: PROVIDER / DEPLOYER / BOTH

**Status:** Auftrag an Claude Code
**Erstellt:** 2026-08-14
**Voraussetzung:** SPEC-01 umgesetzt
**Betroffen:** alle Gate-Definitionen, `pipeline/gate_orchestrator.py`, `requirements/`, `prospective/art25-role-change/`, Evidence-Schema, Tests

---

## 1. Anlass

Die Referenzarchitektur ist vollständig **Deployer-zentriert** (Art. 26 EU AI Act). Das war eine bewusste und methodisch saubere Scope-Entscheidung der Masterarbeit (Limitation L2).

Für die Weiterentwicklung reicht das nicht mehr: Der Zielanwendungsfall **Redispatch bei Netzbetreibern** kommt in drei Konstellationen vor, von denen zwei die Anbieterrolle aktivieren.

**Die Rolle wird damit vom Scope-Rand zum Architekturparameter.**

---

## 2. Die normative Grundlage

### 2.1 Die Merkformel

> **Der Anbieter schuldet die Beschaffenheit des Systems. Der Betreiber schuldet die Beschaffenheit der Verwendung.**

**Art. 16 lit. a** ist der Schlüssel: „ensure that their high-risk AI systems are compliant with the requirements set out in **Section 2**". Section 2 = Kapitel III Abschnitt 2 = **Art. 8–15**. Damit sind Art. 9–15 **Anbieterpflichten**, nicht Betreiberpflichten.

### 2.2 Zuordnung

| Thema | Anbieter | Betreiber |
|---|---|---|
| Risikomanagement | Art. 9 | Art. 26 Abs. 5 (Überwachung, Aussetzen, Meldung) |
| Daten | Art. 10 (Trainings-/Validierungs-/Testdaten) | Art. 26 Abs. 4 (**Eingabedaten**, soweit kontrolliert) |
| Technische Doku | Art. 11, Art. 18 | — |
| Protokollierung | Art. 12, Art. 19 | Art. 26 Abs. 6 (Aufbewahrung ≥ 6 Monate) |
| Transparenz | Art. 13 (Betriebsanleitung erstellen) | Art. 26 Abs. 1 (danach verwenden), Abs. 11 (Betroffene informieren) |
| Menschliche Aufsicht | Art. 14 (**Gestaltung**) | Art. 26 Abs. 2 (**Besetzung** — Kompetenz, Schulung, Befugnis) |
| Robustheit, Cybersicherheit | Art. 15 | mittelbar über Abs. 1 und Abs. 5 |
| Konformität, CE, Registrierung | Art. 16 lit. f–i, Art. 43, 47, 48, 49(1) | **nur öffentliche Stellen**: Art. 26 Abs. 8 |
| Korrekturmaßnahmen | Art. 16 lit. j, Art. 20 | Art. 26 Abs. 5 (Mitwirkung) |
| Grundrechte-Folgenabschätzung | — | Art. 27 (nur bestimmte Betreiber) |

### 2.3 Die drei Konstellationen am Redispatch-Fall

| | Anbieter | Betreiber | Aktive Gate-Menge |
|---|---|---|---|
| **K1** Zukauf | Softwarehaus | Netzbetreiber | `DEPLOYER` |
| **K2** Eigenentwicklung | Netzbetreiber | Netzbetreiber | **`BOTH`** — beide Pflichtenmengen gleichzeitig, nicht wahlweise |
| **K3** Zukauf mit wesentlicher Anpassung | Netzbetreiber (nach Aufstieg) | Netzbetreiber | Übergang `DEPLOYER` → `PROVIDER` plus Nachweis des Übergangsvorgangs |

---

## 3. Umsetzung Teil 1 — `role_scope` auf Gate-Ebene

Ergänzung des Gate-Templates aus SPEC-01:

```yaml
role_scope: ["deployer"]     # ["provider"] | ["deployer"] | ["provider","deployer"]
```

**Alle 16 bestehenden Gates erhalten `role_scope: ["deployer"]`.** Das ist keine Abwertung, sondern die korrekte Kennzeichnung des Ist-Zustands.

---

## 4. Umsetzung Teil 2 — Laufzeitkonfiguration und Gate-Filterung

**Konfigurationsparameter**, in dieser Reihenfolge aufgelöst:

1. Umgebungsvariable `AI_ACT_ROLE`
2. Feld `role` im Szenario-Manifest
3. Default: `DEPLOYER` (rückwärtskompatibel zum Bestand)

Zulässige Werte: `PROVIDER` · `DEPLOYER` · `BOTH`

**Filterregel im `gate_orchestrator.py`:**

```
AI_ACT_ROLE = DEPLOYER  -> nur Gates mit "deployer" in role_scope
AI_ACT_ROLE = PROVIDER  -> nur Gates mit "provider" in role_scope
AI_ACT_ROLE = BOTH      -> alle Gates (Vereinigungsmenge, keine Doppelausfuehrung)
```

**Wichtig:** Bei `BOTH` darf ein Gate mit `role_scope: ["provider","deployer"]` **nur einmal** ausgeführt werden und **einen** Evidence-Record erzeugen.

**Evidence-Schema:** Die Tabelle `compliance.quality_gate_results` erhält eine zusätzliche Spalte `ai_act_role TEXT NOT NULL`. Da sie Teil der Hash-Payload werden muss, ist eine Migration mit **Schema-Versionierung** nötig (Muster: `evidence-store/migrations/v02_to_v03_add_decision_method.sql`). Der Hash-Chain-Trigger `compliance.set_hash_chain()` ist entsprechend zu erweitern.

> **Achtung Hash-Chain:** Bestehende Records wurden ohne dieses Feld gehasht. Die Migration darf die bestehende Kette **nicht** brechen. Entweder das Feld erst ab einem definierten `audit_id` in die Payload aufnehmen und das in `verify_hash_chain.py` abbilden, oder eine neue Kette beginnen und den Bruch dokumentieren. **Variante bitte vorschlagen, bevor implementiert wird** — das ist die risikoreichste Änderung dieser SPEC.

---

## 5. Umsetzung Teil 3 — Art.-25-Gate aus `prospective/` überführen

Das Gate in `prospective/art25-role-change/` ist heute bewusst außerhalb des Katalogs und durchgängig `warn`. Beides ändert sich.

### 5.1 Severity je Check (nach SPEC-01)

| Check | Auslöser | Severity | Begründung |
|---|---|---|---|
| **C-25a** | Art. 25 Abs. 1 lit. a — eigener Name oder Marke auf einem bereits in Verkehr gebrachten Hochrisiko-System | **MUST** | Binärer Tatbestand, kein Schwellenwertproblem |
| **C-25b** | Art. 25 Abs. 1 lit. b — wesentliche Veränderung, System bleibt Hochrisiko | **SHOULD** | Schwellenwerte hängen an Art. 3 Nr. 23 und den delegierten Rechtsakten nach Art. 97 |
| **C-25c** | Art. 25 Abs. 1 lit. c — Zweckänderung macht das System zum Hochrisiko-System | **MUST** | Binär; stützt sich auf die Art.-6-Klassifikation aus SPEC-02 |

Die bisherige Begründung „alles advisory, weil die Art.-97-Schwellenwerte fehlen" trifft ausschließlich auf **lit. b** zu.

### 5.2 C-25c gegen die Klassifikationslogik prüfen, nicht gegen ein Boolean

Die heutige Skizze prüft `input.change_event.purpose_change.becomes_high_risk_art6 == true` — eine Selbstauskunft im Manifest.

**Stattdessen:** C-25c ruft die `classification`-Regel aus SPEC-02 auf und wertet aus, ob sich das Ergebnis durch die Zweckänderung von `NO_SAFETY_COMPONENT` bzw. `NOT_IN_SCOPE` auf `SAFETY_COMPONENT` bewegt. Das Manifest liefert dann die Zweckangaben vor und nach der Änderung, nicht das Ergebnis.

### 5.3 Neue Evidenzanforderungen aus dem Omnibus

Die VO (EU) 2026/1744 hat **Art. 25 Abs. 2 und Abs. 4 UAbs. 1 ersetzt** (primärquellenverifiziert):

- Abs. 2 n.F.: Der ursprüngliche Anbieter „shall no longer be considered to be a provider" des betreffenden Systems, muss aber eng mit den neuen Anbietern zusammenarbeiten und die erforderlichen **Informationen, den technischen Zugang und Unterstützung** bereitstellen.
- Abs. 4 UAbs. 1 n.F.: Anbieter und Drittzulieferer legen die erforderlichen Informationen, Fähigkeiten und technischen Zugänge **durch schriftliche Vereinbarung** fest.

**Der Rollenübergang ist damit ein zweiseitiger, dokumentierter Vorgang, kein einseitiger Statuswechsel.**

`evidence_required` entsprechend erweitern:

```yaml
evidence_required:
  - "change_log_record"
  - "fine_tuning_manifest"
  - "rag_config_diff"
  - "provider_handover_record"        # NEU — Art. 25 Abs. 2 n.F.
  - "cooperation_commitment_ref"      # NEU — Art. 25 Abs. 2 n.F.
  - "written_agreement_ref"           # NEU — Art. 25 Abs. 4 UAbs. 1 n.F.
```

Zusätzlicher Check:

| Check | Severity | Regel |
|---|---|---|
| **C-25d** | MUST | Ein Auslöser (C-25a oder C-25c) hat ausgelöst, aber `written_agreement_ref` oder `provider_handover_record` fehlt → deny. Der Übergang ist ohne die Übergabeartefakte nicht wirksam dokumentiert. |

### 5.4 Überführung und Zählstände

Wenn das Gate aus `prospective/` in `gate-definitions/operations/` wandert, ändern sich die in der Masterarbeit zitierten Zählstände (16 Gates, 10 AUTO / 6 HYBRID).

**Nicht stillschweigend überschreiben.** Der Tag `thesis-v1.0` aus SPEC-01 friert den Thesis-Stand ein; im `CHANGELOG.md` ist die Änderung der Zählstände ausdrücklich zu vermerken, mit dem Hinweis, dass die Kennzahlen der Publikation weiterhin unter dem Tag reproduzierbar sind.

Vergabe einer regulären ID: `G-OPS-06_rollenwechsel.yaml`, `role_scope: ["deployer"]` (der Übergang wird vom Betreiber aus beobachtet).

---

## 6. Umsetzung Teil 4 — Provider-Requirements (Vorbereitung, nicht Vollausbau)

Die 14 bestehenden Requirements sind vollständig Deployer-gefiltert; jedes trägt ein Feld `deployer_implication`.

**In dieser SPEC nur die Struktur schaffen:**

- Feld `role` in `requirements/_requirement_template.yaml` ergänzen: `provider` | `deployer` | `both`
- Alle 14 bestehenden Requirements auf `role: deployer` setzen
- Feld `provider_implication` als Gegenstück zu `deployer_implication` im Template anlegen (bei den bestehenden 14 leer lassen)

**Nicht in dieser SPEC:** Die Ableitung der Provider-Requirements aus Art. 16 lit. a–l nebst Art. 17, 18, 19, 20, 43, 47, 48, 49(1). Das ist ein eigener, größerer Arbeitsblock und braucht zuerst die Primärquellenrecherche zu diesen Artikeln.

---

## 7. Tests

- Filterregel: je ein Lauf mit `AI_ACT_ROLE=DEPLOYER`, `=PROVIDER`, `=BOTH`; bei `PROVIDER` ist die Gate-Menge derzeit **leer** — das muss sauber und mit verständlicher Meldung durchlaufen, nicht mit einer Exception.
- `BOTH`: Nachweis, dass Gates mit beiden Rollen im `role_scope` nur **einen** Evidence-Record erzeugen.
- Hash-Chain: `verify_hash_chain.py` muss nach der Migration über die gesamte Kette laufen (Exit 0).
- Art.-25-Gate: Fixtures für alle drei Auslöser plus den Negativfall aus C-25d (Auslöser ohne Übergabeartefakte).
- Integrity-Regression um die Prüfung erweitern, dass jedes Gate ein gültiges `role_scope` trägt.

---

## 8. Definition of Done

- [ ] `role_scope` im Template und auf allen 16 Gates gesetzt
- [ ] `AI_ACT_ROLE` mit dreistufiger Auflösung implementiert, Default `DEPLOYER`
- [ ] Filterregel im Orchestrator, `BOTH` ohne Doppelausführung
- [ ] **Hash-Chain-Migrationsvariante vorgeschlagen und abgestimmt, bevor implementiert**
- [ ] Evidence-Schema um `ai_act_role` erweitert, `verify_hash_chain.py` angepasst, Kette verifiziert
- [ ] Art.-25-Gate als `G-OPS-06` überführt, Severities C-25a MUST / C-25b SHOULD / C-25c MUST
- [ ] C-25c wertet die `classification`-Regel aus SPEC-02 aus, nicht ein Manifest-Boolean
- [ ] C-25d implementiert, Übergabeartefakte in `evidence_required`
- [ ] `role` und `provider_implication` im Requirement-Template, 14 Requirements auf `role: deployer`
- [ ] Zählstandsänderung im `CHANGELOG.md` dokumentiert, Tag `thesis-v1.0` unberührt
- [ ] Gesamttestsuite grün
