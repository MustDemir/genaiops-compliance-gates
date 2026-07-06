# Prospektiv: Art.-25-Rollenwechsel-Monitoring (F5)

> **Status: NICHT Teil des enforcten Katalogs.** Diese Skizze liegt bewusst
> **außerhalb** der 14 Requirements / 16 Gates der Referenzarchitektur. Sie ist
> **nicht** in der CI-Pipeline, **nicht** in `tests/run_all_rego_tests.sh` und
> **nicht** in den 141 Unit-Tests enthalten. Die Zahlen 14/16 (Kap. 7.4/8.1)
> bleiben unberührt.

## Zweck
Illustrative, **ausdrücklich prospektive** Abbildung des Betreiber-zu-Anbieter-
Aufstiegs nach **Art. 25 Abs. 1 lit. a–c EU AI Act (2024)** — der
Forschungsanschluss **F5** der Masterarbeit. Sie zeigt, *wie* sich ein künftiger
Art.-25-Aufstieg im bestehenden Requirement-/Gate-Schema (Abschn. 4.6 / 5.2.1)
abbilden ließe, **sobald** die delegierten Rechtsakte nach **Art. 97** und die
CEN/CENELEC-Standards konkrete Schwellenwerte liefern.

## Richtung (wichtig)
Art. 25 regelt den Aufstieg **Betreiber/Händler/Einführer/Dritter → Anbieter**
(nicht umgekehrt). Die drei Trigger:
- **(a)** Rebranding: eigener Name/Marke auf einem bereits in Verkehr gebrachten
  Hochrisiko-KI-System.
- **(b)** Wesentliche Veränderung, sodass es ein Hochrisiko-System nach Art. 6 bleibt.
- **(c)** Zweckänderung eines nicht-hochriskanten Systems (auch GPAI) zu einem
  Hochrisiko-System nach Art. 6.

## Warum `warn` statt `deny`
Weil die Schwellenwerte (Art. 97) **noch nicht final** sind, ist der Charakter
**advisory / SHOULD / non-blocking**. Die Rego-Skizze nutzt daher `warn`-Regeln
(Conftest: Warnung, Exit 0 — **kein** Deployment-Blocking), nicht `deny`.
Entscheidung: **HYBRID** — Compliance-Officer-Review.

## Manuell ausführen (nicht Teil der CI)
```bash
# Unit-Tests der Skizze
opa test prospective/art25-role-change/ -v

# Advisory-Check gegen ein Change-Event
conftest test prospective/art25-role-change/change_event_sample.json \
  -p prospective/art25-role-change/policy_role_change_monitoring.rego \
  --namespace genaiops.prospective.role_change_monitoring
```

## Überführung in ein echtes Gate
Erst wenn Art. 97 / CEN-CENELEC die Schwellenwerte definieren, ließe sich der
`contract` konkretisieren, `warn` ggf. zu `deny` verschärfen und die Skizze als
regulär gezähltes Gate aufnehmen. Bis dahin bleibt sie prospektiv.
