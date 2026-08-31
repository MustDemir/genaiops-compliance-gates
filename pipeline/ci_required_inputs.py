#!/usr/bin/env python3
"""
ci_required_inputs.py — traegt die Anwesenheitspflicht in die CI.

SPEC-04b Teil 3.2 hat `required_inputs` eingefuehrt und im Orchestrator
erzwungen. Die CI faehrt den Orchestrator aber nicht: sie ruft conftest je
Gate direkt ueber run_gate.sh. Damit galt die Erzwingung genau dort nicht,
wo sie zaehlt — G-OPS-02 und G-OPS-03 deklarieren ein Pflichtdokument, die
Pipeline hat es nie angefordert und ist gruen geworden. Deklaration
vorhanden, Mechanismus nicht: derselbe Fehlertyp, den SPEC-04b benennt,
eine Ebene weiter aussen.

Dieses Skript loest die Deklarationen fuer einen CI-Lauf auf und legt je
Gate ab, was run_gate.sh zusaetzlich auszuwerten hat:

    <out>/<gate>-inputs.args   eine Zeile je Input: pfad TAB policy TAB namespace
    <out>/<gate>-inputs.fail   Meldungen, wenn ein Pflichtinput fehlt

Ein fehlender Input ist ein GATE-Fehler, kein Werkzeugfehler — deshalb
endet dieses Skript in dem Fall mit 0 und laesst das Gate fehlschlagen.
Mit 2 endet es nur, wenn die Pruefung selbst nicht stattfinden konnte
(kein pyyaml, keine Gate-Definitionen). Eine Erzwingung, die sich still
abschalten laesst, ist keine.

Die Frist prueft dieses Skript NICHT. Ein veraltetes Messdokument ist
vorhanden; es faellt ueber G-OPS-03/C-03 in Rego, wo die Frist steht.
Anwesenheit und Frische sind zwei Fragen und gehoeren nicht vermischt.

Aufruf:
    python3 pipeline/ci_required_inputs.py --out-dir /tmp \
        --supplied G-OPS-03:drift_measurement=/tmp/drift_measurement.json
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gate_orchestrator import (  # noqa: E402
    REPO_ROOT,
    check_required_inputs,
    load_gate_required_inputs,
)


def namespace_of(policy_path: str) -> str:
    """Namespace aus der `package`-Zeile der Policy — wie im Orchestrator.

    Ohne --namespace wertet conftest nur `main` aus und meldet fuer jede
    Eingabe null Verstoesse. Ein Check, der nicht fehlschlagen kann, ist
    keiner; deshalb ist ein fehlender package-Name hier ein Fehler und
    kein Standardwert.
    """
    m = re.search(
        r"^package\s+([\w.]+)",
        (REPO_ROOT / policy_path).read_text(encoding="utf-8"),
        re.M,
    )
    return m.group(1) if m else ""


def parse_supplied(eintraege: list) -> dict:
    """'G-OPS-03:drift_measurement=/tmp/x.json' -> {gate: {kind: pfad}}"""
    geliefert: dict = {}
    for eintrag in eintraege:
        try:
            gate_und_kind, pfad = eintrag.split("=", 1)
            gate_id, kind = gate_und_kind.split(":", 1)
        except ValueError:
            raise SystemExit(
                f"--supplied erwartet GATE:kind=pfad, bekam: {eintrag!r}"
            )
        geliefert.setdefault(gate_id.strip(), {})[kind.strip()] = pfad.strip()
    return geliefert


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", default="/tmp")
    ap.add_argument("--supplied", action="append", default=[],
                    help="GATE:kind=pfad, wiederholbar")
    args = ap.parse_args()

    geliefert = parse_supplied(args.supplied)
    deklariert = load_gate_required_inputs()

    if not deklariert:
        # Entweder fehlt pyyaml, oder die Gate-Definitionen wurden nicht
        # gefunden. In beiden Faellen waere die Erzwingung stumm — und eine
        # stumme Erzwingung ist schlimmer als keine, weil sie beruhigt.
        print("::error::Keine required_inputs-Deklaration gelesen. Entweder fehlt "
              "pyyaml, oder gate-definitions/ ist leer. Die Anwesenheitspflicht "
              "kann nicht erzwungen werden, und ein stiller Durchlauf waere "
              "genau der Zustand, den SPEC-04b beseitigt.")
        return 2

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    gates_mit_fehler = 0

    for gate_id, deklarationen in sorted(deklariert.items()):
        basis = out / f"{gate_id.lower()}-inputs"
        gate_cfg = {"inputs": geliefert.get(gate_id, {})}
        fehler = [f["msg"] for f in
                  check_required_inputs(gate_id, gate_cfg, deklarationen)]

        zeilen = []
        if not fehler:
            for decl in deklarationen:
                kind = decl.get("kind", "<unnamed>")
                pfad = gate_cfg["inputs"][kind]
                policy = decl.get("evaluated_by")
                if not policy or not (REPO_ROOT / policy).exists():
                    fehler.append(
                        f"{gate_id}/INPUT ({kind}): evaluated_by nennt keine "
                        f"lesbare Policy ({policy!r}). Ein Dokument, das niemand "
                        f"liest, ist kein Nachweis."
                    )
                    continue
                ns = namespace_of(policy)
                if not ns:
                    fehler.append(
                        f"{gate_id}/INPUT ({kind}): {policy} deklariert kein "
                        f"package. conftest wuerde nur den Namespace 'main' "
                        f"auswerten und fuer jede Eingabe null Verstoesse melden."
                    )
                    continue
                zeilen.append(f"{pfad}\t{policy}\t{ns}")

        if fehler:
            basis.with_suffix(".fail").write_text("\n".join(fehler) + "\n",
                                                  encoding="utf-8")
            basis.with_suffix(".args").unlink(missing_ok=True)
            gates_mit_fehler += 1
            print(f"  {gate_id}: {len(fehler)} Pflichtinput(s) fehlen — Gate FAIL")
            for f in fehler:
                print(f"    → {f}")
        else:
            basis.with_suffix(".args").write_text("\n".join(zeilen) + "\n",
                                                  encoding="utf-8")
            basis.with_suffix(".fail").unlink(missing_ok=True)
            print(f"  {gate_id}: {len(zeilen)} Pflichtinput(s) aufgeloest")
            for z in zeilen:
                print(f"    → {z.replace(chr(9), '  ')}")

    print(f"[ci_required_inputs] {len(deklariert)} Gate(s) mit Deklaration, "
          f"{gates_mit_fehler} davon unvollstaendig")
    # Bewusst 0: ein fehlender Input laesst das GATE fehlschlagen, nicht den
    # Schritt. Sonst braeche der Lauf ab, bevor die Evidenz geschrieben ist —
    # und die Luecke waere nicht aktenkundig, sondern nur laut.
    return 0


if __name__ == "__main__":
    sys.exit(main())
