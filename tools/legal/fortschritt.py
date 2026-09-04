#!/usr/bin/env python3
"""fortschritt.py — wo steht der Pflichtenraum, und wo geht es weiter.

Die Deckungsanalyse laeuft ueber mehrere Sitzungen, die einander nicht kennen.
Der Pflichtenraum SELBST ist der Zustand: eine Einheit ohne `scope` ist offen,
eine mit `scope` ist bearbeitet. Dieses Skript liest das aus und sagt, welche
Einheiten als naechste dran sind — damit kein Lauf raten muss, wo der vorige
aufgehoert hat, und keiner Arbeit doppelt macht.

Aufruf:
  python3 tools/legal/fortschritt.py docs/coverage/aiact_pflichtenraum.yaml
  python3 tools/legal/fortschritt.py <datei> --naechste 20
  python3 tools/legal/fortschritt.py <datei> --artikel 26 8 9 10 11 12 13 14 15
"""

from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

import yaml


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pflichtenraum", type=Path)
    ap.add_argument("--naechste", type=int, default=15,
                    help="wie viele offene Einheiten aufgelistet werden")
    ap.add_argument("--artikel", nargs="*",
                    help="nur diese Artikel betrachten")
    a = ap.parse_args()

    doc = yaml.safe_load(a.pflichtenraum.read_text(encoding="utf-8"))
    units = doc.get("einheiten") or []
    if a.artikel:
        units = [u for u in units if u.get("artikel") in set(a.artikel)]

    offen = [u for u in units if not u.get("scope")]
    fertig = [u for u in units if u.get("scope")]
    unbestaetigt = [u for u in fertig if u.get("po_bestaetigt") is False]

    befunde = collections.Counter(u.get("befund") for u in fertig if u.get("scope") == "in")
    stufen = collections.Counter(u.get("verifikation") for u in fertig)
    scopes = collections.Counter(u.get("scope") for u in fertig)

    print(f"Datei:    {a.pflichtenraum}")
    print(f"Quelle:   {doc['quelle']['datei']}")
    print(f"SHA-256:  {doc['quelle']['sha256']}")
    if a.artikel:
        print(f"Filter:   Artikel {', '.join(a.artikel)}")
    print()
    print(f"Einheiten gesamt:  {len(units)}")
    print(f"  bearbeitet:      {len(fertig)}")
    print(f"  offen:           {len(offen)}")
    print(f"  ohne PO-Bestaetigung: {len(unbestaetigt)}")
    print()
    if scopes:
        print("Scope:        " + ", ".join(f"{k}={v}" for k, v in sorted(scopes.items(), key=lambda x: str(x[0]))))
    if befunde:
        print("Befund (in):  " + ", ".join(f"{k}={v}" for k, v in sorted(befunde.items(), key=lambda x: str(x[0]))))
    if stufen:
        print("Verifikation: " + ", ".join(f"{k}={v}" for k, v in sorted(stufen.items(), key=lambda x: str(x[0]))))

    if offen:
        print(f"\nNaechste {min(a.naechste, len(offen))} offene Einheiten — hier weitermachen:")
        for u in offen[:a.naechste]:
            print(f"  {u['id']:28} offset={u['offset']:<8} {u['beleg'][:90]}")
        if len(offen) > a.naechste:
            print(f"  … und {len(offen) - a.naechste} weitere")
    else:
        print("\nAlle Einheiten dieses Ausschnitts sind bearbeitet.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
