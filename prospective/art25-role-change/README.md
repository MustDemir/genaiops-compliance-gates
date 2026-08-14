# Prospektiv: Art.-25-Rollenwechsel-Monitoring (F5) — ÜBERFÜHRT

> **Status (2026-08-14): in den enforcten Katalog überführt.**
> Diese Skizze ist durch **`G-OPS-06` (Rollenwechsel)** ersetzt worden:
>
> - Gate-Definition: `gate-definitions/operations/G-OPS-06_rollenwechsel.yaml`
> - Policy: `policies/operations/policy_role_change_monitoring.rego`
> - Tests: `policies/operations/policy_role_change_monitoring_test.rego`
>   (jetzt regulär Teil von `tests/run_all_rego_tests.sh`)
> - Fixtures: `scenarios/healthcare-ambient-ai-scribe/fixtures/art25_*.json`
>
> Die Dateien in diesem Verzeichnis bleiben als **historischer Stand** liegen,
> auf den die Masterarbeit (Forschungsanschluss F5) verweist. Sie sind
> **nicht** mehr Teil der CI und werden nicht mehr gepflegt.

## Was sich bei der Überführung geändert hat (SPEC-03 Abschnitt 5)

**1. Severity gehört an den Check, nicht an das Gate.**
Die Skizze führte alle drei Auslösetatbestände einheitlich als `warn` mit der
Begründung, die Schwellenwerte nach Art. 97 fehlten. Das trifft aber **nur auf
lit. b** zu:

| Check | Tatbestand | Severity | Begründung |
|---|---|---|---|
| C-25a | Art. 25 Abs. 1 lit. a — Rebranding | **MUST** | binär, kein Schwellenwertproblem |
| C-25b | Art. 25 Abs. 1 lit. b — wesentliche Veränderung | SHOULD | Schwelle hängt an Art. 3 Nr. 23 + Art. 97 |
| C-25c | Art. 25 Abs. 1 lit. c — Zweckänderung | **MUST** | binär, stützt sich auf die Art.-6-Klassifikation |
| C-25d | Art. 25 Abs. 2 / Abs. 4 UAbs. 1 n.F. | **MUST** | Übergabeartefakte fehlen |

**2. C-25c prüft gegen die Klassifikationslogik, nicht gegen ein Boolean.**
Die Skizze prüfte `purpose_change.becomes_high_risk_art6 == true` — eine
Selbstauskunft. G-OPS-06 ruft stattdessen die `classification`-Regel aus
`G-PRE-01` (SPEC-02) auf, je einmal für den Zustand vor und nach der
Zweckänderung, und wertet aus, ob sich das Ergebnis von `NO_SAFETY_COMPONENT`
bzw. `NOT_IN_SCOPE` auf `SAFETY_COMPONENT` bewegt.

**3. Neue Evidenzanforderungen aus dem Digital Omnibus.**
Die VO (EU) 2026/1744 hat Art. 25 Abs. 2 und Abs. 4 UAbs. 1 ersetzt. Der
Rollenübergang ist damit ein **zweiseitiger, dokumentierter Vorgang**, kein
einseitiger Statuswechsel: `provider_handover_record`,
`cooperation_commitment_ref` und `written_agreement_ref` sind Pflicht (C-25d).

**4. Carve-out in Art. 25 Abs. 2 letzter Satz** — Befund über SPEC-03 hinaus.
Hat der ursprüngliche Anbieter klar festgelegt, dass sein System nicht in ein
Hochrisiko-System umgewandelt werden soll, entfällt die Kooperations- und
Übergabepflicht. In C-25d als **belegpflichtige** Ausnahme implementiert.

## Ursprüngliche Skizze (historisch)

Richtung: Art. 25 regelt den Aufstieg **Betreiber/Händler/Einführer/Dritter →
Anbieter** (nicht umgekehrt), Forschungsanschluss **F5** der Masterarbeit.
Die Zahlen 14 Requirements / 16 Gates (Kap. 7.4/8.1) beziehen sich auf den
Stand **vor** dieser Überführung und bleiben unter dem Git-Tag `thesis-v1.0`
reproduzierbar.
