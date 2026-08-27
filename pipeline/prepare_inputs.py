#!/usr/bin/env python3
"""
prepare_inputs.py — erzeugt die Dokumente, die Gates als required_inputs verlangen.

SPEC-04b Teil 3.2. Seit ein Gate erklaeren kann, welches Dokument es
vorgelegt bekommen muss, faellt es durch, wenn es fehlt — das ist der Punkt.
Damit ein Walkthrough trotzdem laufen kann, muss das Dokument vorher
ERZEUGT werden, nicht eingecheckt.

Warum nicht eingecheckt: C-03 prueft, ob die Messung frisch ist. Ein
eingechecktes Messdokument veraltet nach 15 Minuten und faerbt jeden
spaeteren Lauf rot — und ein Dokument, das man deshalb von der Frist
ausnimmt, ist wieder eine Handdatei.

Das Ergebnis eines Fixture-Laufs traegt `provenance: declared` und loest
G-OPS-03/C-05 als Warnung aus. Das ist beabsichtigt: ein Walkthrough ist
ein legitimer Weg, dieses Repository zu fahren, aber er ist kein
Betriebsnachweis, und die Evidenz sagt das.

Aufruf:
    python3 pipeline/prepare_inputs.py --scenario pipeline/scenarios/poc_healthcare_pass.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def erzeuge_drift_measurement(quelle: str, ziel: str, baseline: str) -> bool:
    """Ruft den Drift-Detektor. Er misst; die Entscheidung faellt spaeter in Rego."""
    cmd = [
        sys.executable, str(REPO_ROOT / "monitoring" / "drift_detector.py"),
        "--source", quelle,
        "--baseline", baseline,
        "--measurement-out", ziel,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    # Exit 1 heisst "Drift erkannt" — das ist ein gueltiges Messergebnis,
    # kein Fehler. Nur ein Abbruch (2) bedeutet, dass nicht gemessen wurde.
    if proc.returncode == 2:
        print(f"  FEHLER: Messung nicht moeglich\n{proc.stdout}{proc.stderr}")
        return False
    return Path(ziel if Path(ziel).is_absolute() else REPO_ROOT / ziel).exists()


def erzeuge_incident_thresholds(quelle: str, ziel: str, _baseline: str) -> bool:
    """Konvertiert die Schwellenwert-Festlegung von YAML nach JSON.

    In YAML AUTORIERT, weil sie Kommentare traegt: Rechtsgrundlagen,
    Kommissions-Randnummern, Begruendungen fuer offene Schwellen. Rego
    liest JSON. Die Konvertierung ist deshalb ein Erzeugungsschritt und
    kein Nebenprodukt — die YAML-Fassung ist die Quelle, die JSON-Fassung
    das Gate-Eingabedokument.
    """
    try:
        import yaml
    except ImportError:
        print("  FEHLER: pyyaml fehlt — Schwellenwert-Dokument nicht konvertierbar")
        return False

    src = Path(quelle if Path(quelle).is_absolute() else REPO_ROOT / quelle)
    dst = Path(ziel if Path(ziel).is_absolute() else REPO_ROOT / ziel)
    if not src.exists():
        print(f"  FEHLER: {quelle} fehlt")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(
        json.dumps(yaml.safe_load(src.read_text(encoding="utf-8")),
                   indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    return True


# Die Input-Typen, die heute existieren. Die Tabelle macht sichtbar, dass
# weitere hier andocken — und dass ein unbekannter Typ ein Fehler ist und
# nicht stillschweigend uebersprungen wird.
ERZEUGER = {
    "drift_measurement": erzeuge_drift_measurement,
    "incident_thresholds": erzeuge_incident_thresholds,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Erzeugt required_inputs eines Szenarios")
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--baseline", default="monitoring/fixtures/baseline_normal.json")
    args = ap.parse_args()

    pfad = Path(args.scenario)
    if not pfad.is_absolute():
        pfad = REPO_ROOT / args.scenario
    config = json.loads(pfad.read_text(encoding="utf-8"))

    erzeugt, fehler = 0, 0
    for gate in config.get("gates", []):
        quellen = gate.get("input_sources") or {}
        ziele = gate.get("inputs") or {}
        for kind, quelle in quellen.items():
            ziel = ziele.get(kind)
            if not ziel:
                print(f"  {gate['gate_id']}: input_sources nennt '{kind}', "
                      f"inputs nennt kein Ziel — nichts zu erzeugen")
                fehler += 1
                continue
            if kind not in ERZEUGER:
                print(f"  {gate['gate_id']}: kein Erzeuger fuer Input-Typ '{kind}' bekannt")
                fehler += 1
                continue
            print(f"  {gate['gate_id']}: erzeuge {kind} aus {quelle} -> {ziel}")
            if ERZEUGER[kind](quelle, ziel, args.baseline):
                erzeugt += 1
            else:
                fehler += 1

    print(f"[prepare_inputs] {erzeugt} erzeugt, {fehler} fehlgeschlagen")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
