#!/usr/bin/env python3
"""po_entscheide.py — schreibt PO-Entscheide aus docs/coverage/entscheide/ in die Pflichtenraeume.

T-14.5 (28.09.2026), PO-Festlegung P-4. Bis hierhin standen die Entscheide der
Deckungsanalyse nur in den Review-Dokumenten; im Pflichtenraum trug keine Zeile
po_bestaetigt: true, und 22 Zeilen standen noch auf 'nicht_einschlaegig', obwohl
der PO sie am 23.09. anders eingeordnet hatte. Ein Entscheid, der nur in Prosa
steht, ist fuer jede Maschine, die den Pflichtenraum liest, nicht gefallen.

Eine Entscheidungsdatei nennt je Eintrag: Raum, Kennungen, die Felder, die
gesetzt werden, den Beleg (wo der Entscheid steht) und ob die Zeile damit
bestaetigt ist. Das Skript

  * setzt die Felder,
  * haengt '<Datum> · <Beleg>' an das Feld po_entscheid der Zeile,
  * setzt po_bestaetigt: true, wo ein Eintrag bestaetigt: true traegt,

und bricht ab, wenn eine Kennung im Raum fehlt. Es entscheidet nichts: was nicht
in einer Entscheidungsdatei steht, bleibt, wie es ist. Mehrfaches Ausfuehren
aendert nichts (idempotent).

Aufruf:
  python3 tools/legal/po_entscheide.py            # eintragen
  python3 tools/legal/po_entscheide.py --pruefen  # nur zeigen, was abweicht
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _raum_datei(repo_root: Path, raum: str) -> Path:
    return repo_root / "docs" / "coverage" / f"{raum}_pflichtenraum.yaml"


def erwartet(repo_root: Path = REPO_ROOT) -> dict[tuple[str, str], dict]:
    """Soll-Zustand je (raum, id) aus allen Entscheidungsdateien, in Dateireihenfolge."""
    soll: dict[tuple[str, str], dict] = {}
    for datei in sorted((repo_root / "docs" / "coverage" / "entscheide").glob("*.yaml")):
        doc = yaml.safe_load(datei.read_text(encoding="utf-8")) or {}
        if "eintraege" not in doc:
            continue  # z. B. satzebene.yaml — eine Schnittliste, kein Feldentscheid
        datum = str(doc.get("entschieden") or "")
        for e in doc["eintraege"]:
            for kennung in e["ids"]:
                s = soll.setdefault((e["raum"], kennung),
                                    {"felder": {}, "belege": [], "bestaetigt": False,
                                     "quelle": str(datei.relative_to(repo_root))})
                s["felder"].update(e.get("setze") or {})
                beleg = f"{datum} · {e['beleg']}"
                if beleg not in s["belege"]:
                    s["belege"].append(beleg)
                s["bestaetigt"] = s["bestaetigt"] or bool(e.get("bestaetigt"))
    return soll


def abweichungen(repo_root: Path = REPO_ROOT) -> list[str]:
    """Was im Pflichtenraum nicht dem Soll entspricht — in beiden Richtungen."""
    soll = erwartet(repo_root)
    raeume: dict[str, dict] = {}
    for raum in sorted({r for r, _ in soll} | {"aiact", "omnibus"}):
        pfad = _raum_datei(repo_root, raum)
        if pfad.exists():
            einheiten = (yaml.safe_load(pfad.read_text(encoding="utf-8")) or {}).get("einheiten") or []
            raeume[raum] = {e["id"]: e for e in einheiten}
    befunde = []
    for (raum, kennung), s in soll.items():
        zeile = raeume.get(raum, {}).get(kennung)
        if zeile is None:
            befunde.append(f"{raum}: {kennung} — entschieden in {s['quelle']}, im Pflichtenraum nicht vorhanden")
            continue
        for feld, wert in s["felder"].items():
            if zeile.get(feld) != wert:
                befunde.append(f"{raum}: {kennung} — {feld} ist {str(zeile.get(feld))[:60]!r}, "
                               f"entschieden ist {str(wert)[:60]!r}")
        fehlend = [b for b in s["belege"] if b not in (zeile.get("po_entscheid") or [])]
        if fehlend:
            befunde.append(f"{raum}: {kennung} — po_entscheid nennt nicht: {'; '.join(fehlend)}")
        if s["bestaetigt"] and zeile.get("po_bestaetigt") is not True:
            befunde.append(f"{raum}: {kennung} — entschieden und bestaetigt, po_bestaetigt ist nicht true")
    for raum, zeilen in raeume.items():
        for kennung, zeile in zeilen.items():
            if zeile.get("po_bestaetigt") is True and not soll.get((raum, kennung), {}).get("bestaetigt"):
                befunde.append(f"{raum}: {kennung} — po_bestaetigt: true ohne Entscheid mit bestaetigt: true "
                               f"in docs/coverage/entscheide/")
    return befunde


def anwenden(repo_root: Path = REPO_ROOT) -> dict[str, int]:
    soll = erwartet(repo_root)
    gezaehlt: dict[str, int] = {}
    for raum in sorted({r for r, _ in soll}):
        pfad = _raum_datei(repo_root, raum)
        doc = yaml.safe_load(pfad.read_text(encoding="utf-8"))
        zeilen = {e["id"]: e for e in doc["einheiten"]}
        fehlt = sorted(k for r, k in soll if r == raum and k not in zeilen)
        if fehlt:
            raise SystemExit(f"FEHLER — {raum}: entschieden, aber nicht im Pflichtenraum: {', '.join(fehlt)}")
        for (r, kennung), s in soll.items():
            if r != raum:
                continue
            z = zeilen[kennung]
            z.update(s["felder"])
            z["po_entscheid"] = list(dict.fromkeys((z.get("po_entscheid") or []) + s["belege"]))
            if s["bestaetigt"]:
                z["po_bestaetigt"] = True
        pfad.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
        gezaehlt[raum] = sum(1 for r, _ in soll if r == raum)
    return gezaehlt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pruefen", action="store_true", help="nichts schreiben, Abweichungen zeigen")
    a = ap.parse_args()
    if not a.pruefen:
        for raum, n in anwenden().items():
            print(f"{raum}: {n} Zeilen nach den Entscheiden gesetzt")
    befunde = abweichungen()
    for b in befunde:
        print(f"  - {b}")
    soll = erwartet()
    print(f"{len(soll)} entschiedene Zeilen, davon bestaetigt {sum(s['bestaetigt'] for s in soll.values())}; "
          f"Abweichungen: {len(befunde)}")
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
