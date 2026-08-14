# SPEC-02 — G-PRE-01: Prüfbaum Sicherheitskomponente nach Art. 6 Abs. 1a–1c

**Status:** Auftrag an Claude Code
**Erstellt:** 2026-08-14
**Voraussetzung:** SPEC-01 umgesetzt (Check-Ebene-Severity wird hier gebraucht)
**Betroffen:** `gate-definitions/pre-deployment/G-PRE-01_risiko_klassifikation.yaml`, `policies/pre-deployment/policy_risk_classification.rego` (+ Tests), Fixtures

---

## 1. Anlass

Die VO (EU) 2026/1744 (Digital Omnibus, in Kraft seit 27.07.2026) hat den Begriff der **Sicherheitskomponente** geändert. Die bestehende `policy_risk_classification.rego` bildet den neuen Stand nicht ab.

Die Einstufung nach **Annex III Nr. 2** hängt vollständig an diesem einen Begriff:

> „AI systems intended to be used as **safety components** in the management and operation of critical digital infrastructure, road traffic, or in the supply of water, gas, heating or electricity."

---

## 2. Rechtsstand (primärquellenverifiziert gegen EUR-Lex)

### 2.1 Art. 3 Nr. 14 i.d.F. der VO (EU) 2026/1744

> „'safety component' means a component of a product or of an AI system which **fulfils a safety function** for that product or AI system, **or** the **failure or malfunctioning of which endangers the health and safety of persons or property**; for the purposes of this definition, a component fulfils a safety function where **its intended purpose is to prevent or mitigate risks to health and safety of persons or property**."

**Zwei oder-verknüpfte Arme:**

- **Arm A — Zweckbestimmung:** Ist der bestimmungsgemäße Zweck, Risiken für Gesundheit und Sicherheit von Personen **oder Sachen** zu verhindern oder zu mindern?
- **Arm B — Ausfallfolge:** Gefährdet Ausfall oder Fehlfunktion Gesundheit und Sicherheit von Personen **oder Sachen**?

**Nicht verkürzen:** Geschützt sind Personen **oder Sachen**. Betriebsmittel eines Netzes sind Sachen.

### 2.2 Art. 6 Abs. 1a und 1b (neu)

> **Abs. 1a:** „AI systems that are solely used for non-safety related aspects of user assistance, performance optimisation, service efficiency, automation or convenience or quality control shall not qualify as safety components."
>
> **Abs. 1b:** „Notwithstanding paragraph 1a, AI systems the failure or malfunctioning of which would endanger health and safety shall qualify as safety components."

**Geltungsbereich:** Abs. 1a und 1b sind **allgemein formuliert** und gelten damit auch für Annex III Nr. 2. Nur **Abs. 1c** verweist ausdrücklich auf „the condition in paragraph 1, point (b)" und ist auf den Annex-I-Pfad beschränkt — **Abs. 1c ist hier nicht umzusetzen**.

### 2.3 Auslegung (Hypothese, keine Leitlinien vorhanden)

Abs. 1a verengt **Arm A**. Abs. 1b schützt **Arm B** vor dieser Verengung. **Folge: Arm B ist der dominante Test.** Wer sich auf „das ist doch nur Optimierung" beruft, muss zusätzlich zeigen, dass die Ausfallfolge unkritisch ist.

**Daraus folgt die zentrale Umsetzungsanforderung:** Schritt 4 des Prüfbaums darf **nicht überspringbar** sein, wenn Abs. 1a geltend gemacht wurde.

---

## 3. Der Prüfbaum

```
1. Einsatz in Verwaltung oder Betrieb der Versorgung mit
   Wasser, Gas, Waerme oder Elektrizitaet (bzw. kritische
   digitale Infrastruktur, Strassenverkehr)?
        nein --> NOT_IN_SCOPE (Annex III Nr. 2 scheidet aus)
        ja   --> weiter

2. ARM A — Zweckbestimmung:
   Ist der bestimmungsgemaesse Zweck, Risiken fuer Gesundheit
   und Sicherheit von Personen ODER SACHEN zu verhindern oder
   zu mindern?
        ja   --> SAFETY_COMPONENT
        nein --> weiter

3. Art. 6 Abs. 1a — Ausschluss geltend gemacht?
   Ausschliesslich Nutzerunterstuetzung / Leistungsoptimierung /
   Serviceeffizienz / Automatisierung / Komfort /
   nicht-sicherheitsbezogene Qualitaetskontrolle?
        ja   --> vorlaeufig kein Safety Component,
                 ABER Schritt 4 ZWINGEND
        nein --> weiter zu Schritt 4

4. ARM B / Art. 6 Abs. 1b — Ausfallfolge:
   Gefaehrdet Ausfall oder Fehlfunktion Gesundheit und
   Sicherheit von Personen ODER SACHEN?
        ja   --> SAFETY_COMPONENT (ueberschreibt Schritt 3)
        nein --> NO_SAFETY_COMPONENT
```

---

## 4. Erwartete Eingabestruktur

Erweiterung des Klassifikations-Manifests (Fixture-Name: `risk_classification.json`):

```json
{
  "system": {
    "name": "redispatch-optimizer",
    "version": "1.4.2",
    "deployment_context": "electricity_supply_operation",
    "annex_iii_candidate": "no2_critical_infrastructure"
  },
  "art6_assessment": {
    "arm_a_intended_purpose": {
      "prevents_or_mitigates_risk_to_health_safety_or_property": true,
      "justification": "Verhinderung von Betriebsmittelueberlastung im Uebertragungsnetz"
    },
    "art6_1a_exclusion_claimed": {
      "claimed": false,
      "sole_use_categories": []
    },
    "arm_b_failure_impact": {
      "assessed": true,
      "endangers_health_safety_persons_or_property": true,
      "justification": "Fehlentscheidung laesst Engpass bestehen -> Betriebsmittelschaden, Versorgungsunterbrechung",
      "human_control_between_output_and_action": true,
      "human_control_effectiveness_evidence_ref": "evidence://gates/operations/G-OPS-01"
    }
  }
}
```

**Zulässige Werte für `sole_use_categories`** (wörtlich aus Art. 6 Abs. 1a):
`user_assistance` · `performance_optimisation` · `service_efficiency` · `automation` · `convenience` · `quality_control`

**Zulässige Werte für `deployment_context`** (aus Annex III Nr. 2):
`critical_digital_infrastructure` · `road_traffic` · `water_supply` · `gas_supply` · `heating_supply` · `electricity_supply_operation`

---

## 5. Umzusetzende Checks in `policy_risk_classification.rego`

Package beibehalten. Ergänzen (Check-IDs nach SPEC-01):

| ID | Severity | Regel |
|---|---|---|
| **C-A1** | MUST | `art6_assessment` fehlt vollständig → deny |
| **C-A2** | MUST | `deployment_context` fehlt oder liegt außerhalb der zulässigen Werte, obwohl `annex_iii_candidate == "no2_critical_infrastructure"` → deny |
| **C-A3** | MUST | **Der Kern:** `art6_1a_exclusion_claimed.claimed == true`, aber `arm_b_failure_impact.assessed != true` → deny. **Schritt 4 ist nicht überspringbar.** |
| **C-A4** | MUST | `art6_1a_exclusion_claimed.claimed == true`, aber `sole_use_categories` leer oder enthält unzulässige Werte → deny |
| **C-A5** | MUST | Arm A oder Arm B mit `true` beantwortet, aber `justification` fehlt oder ist leer → deny |
| **C-A6** | MUST | Einstufung als `NO_SAFETY_COMPONENT` obwohl `arm_b_failure_impact.endangers_... == true` → deny (Art. 6 Abs. 1b überschreibt) |
| **C-A7** | SHOULD | `human_control_between_output_and_action == true`, aber `human_control_effectiveness_evidence_ref` fehlt → warn (siehe Abschnitt 6) |

**Zusätzlich:** Eine Regel `classification` (kein deny/warn, sondern ein berechnetes Ergebnis), die den Prüfbaum aus Abschnitt 3 auswertet und einen der Werte `NOT_IN_SCOPE` / `SAFETY_COMPONENT` / `NO_SAFETY_COMPONENT` zurückgibt. Dieses Ergebnis gehört in den Evidence-Record.

---

## 6. Der gekoppelte Befund — C-A7 ist der inhaltlich interessante Check

Bei Systemen, deren Ausgabe erst über eine menschliche Entscheidung wirksam wird (z. B. Lastprognose mit halbautomatischer Schalthandlung), entscheidet über Arm B, ob eine **wirksame** Kontrolle dazwischensteht.

> **Damit hängt die Einstufung nach Art. 6 an der Aufsichtsqualität nach Art. 26 Abs. 2.** Je schwächer der Override, desto eher ist das System Sicherheitskomponente und damit Hochrisiko.
>
> Wer sich als „kein Hochrisiko" einstuft, **weil** ein Mensch dazwischensteht, schuldet den Nachweis, dass diese Aufsicht wirksam ist.

C-A7 erzwingt genau diesen Verweis. Das Ziel ist die Verknüpfung zu **G-OPS-01**, das die Wirksamkeitsbedingungen bereits prüft (Causal Power, Epistemic Access, Self-Control, Fitting Intentions).

**Severity bewusst SHOULD, nicht MUST:** Der Verweis kann zum Zeitpunkt der Pre-Deployment-Klassifikation noch nicht auflösbar sein, weil G-OPS-01 in der Operations-Phase läuft. Die Verschärfung auf MUST ist eine Folge-Iteration, sobald die Reihenfolge geklärt ist.

---

## 7. Test-Fixtures

Anzulegen unter `scenarios/` (neues Szenario `grid-redispatch/fixtures/`, siehe SPEC-03 für den Szenario-Rahmen — falls dieser noch nicht existiert, vorläufig unter `scenarios/healthcare-ambient-ai-scribe/fixtures/` mit Präfix `art6_`):

| Fixture | Erwartetes Ergebnis |
|---|---|
| `art6_redispatch_pass.json` | `SAFETY_COMPONENT` über Arm A **und** Arm B, keine Verstöße |
| `art6_lastprognose_boundary.json` | `SAFETY_COMPONENT` über Arm B; C-A7 als `warn`, weil kein Aufsichtsnachweis referenziert |
| `art6_predictive_maintenance.json` | `NO_SAFETY_COMPONENT`; 1a geltend gemacht **und** Arm B bewertet und verneint — muss sauber durchlaufen |
| `art6_chatbot_out_of_scope.json` | `NOT_IN_SCOPE` |
| `art6_optimization_claim_without_failure_assessment.json` | **C-A3 deny** — 1a behauptet, Arm B nicht bewertet. Das ist der wichtigste Negativtest der ganzen SPEC. |
| `art6_contradiction.json` | **C-A6 deny** — Selbsteinstufung `NO_SAFETY_COMPONENT` bei bejahter Ausfallgefährdung |

---

## 8. Anpassung der Gate-Definition

`gate-definitions/pre-deployment/G-PRE-01_risiko_klassifikation.yaml`:

- `policy_checks` um C-A1 bis C-A7 erweitern (Objektform nach SPEC-01)
- `legal_refs` je Check setzen: `["Art. 3 Nr. 14", "Art. 6 Abs. 1a", "Art. 6 Abs. 1b", "Anhang III Nr. 2"]`
- `evidence_required` ergänzen um `art6_assessment_record`
- `evidence_level.current`: **E-0** (Selbstauskunft im Manifest)
- `evidence_level.target`: **E-2** — mit dieser `rationale`:
  > „Ob ein System Schalthandlungen auslöst, ist am Systemzustand prüfbar (Leitsystem-Anbindung, Schnittstellen, Berechtigungen) und muss nicht der Selbstauskunft überlassen bleiben."

---

## 9. Wichtige Einschränkungen

- **Die Auslegung in Abschnitt 2.3 ist Hypothese.** Es liegen weder Leitlinien der Kommission noch Rechtsprechung zu Art. 6 Abs. 1a/1b vor. Das gehört als Kommentarblock in die Rego-Datei.
- **Nur die englische Sprachfassung wurde geprüft.** Die deutsche Fassung gilt gleichermaßen verbindlich; bei „safety function", „intended purpose" und „endangers" können Nuancen abweichen. **Vor einer Veröffentlichung abzugleichen**, für die Implementierung unkritisch.
- **Art. 6 Abs. 1c ist bewusst nicht umgesetzt** — er betrifft ausschließlich den Annex-I-Pfad.

---

## 10. Definition of Done

- [ ] Prüfbaum aus Abschnitt 3 in `policy_risk_classification.rego` abgebildet
- [ ] C-A1 bis C-A7 implementiert, Check-IDs nach SPEC-01-Konvention in den Meldungen
- [ ] `classification`-Regel liefert `NOT_IN_SCOPE` / `SAFETY_COMPONENT` / `NO_SAFETY_COMPONENT`
- [ ] Alle sechs Fixtures angelegt, Unit-Tests grün
- [ ] **Negativtest `art6_optimization_claim_without_failure_assessment.json` schlägt fehl wie vorgesehen**
- [ ] G-PRE-01-Gate-Definition aktualisiert inkl. `evidence_level`
- [ ] Rechtsstand-Kommentarblock mit Hypothesen-Kennzeichnung in der Rego-Datei
- [ ] Integrity-Regression und Gesamttestsuite grün
