#!/usr/bin/env python3
"""verify_norm_quotes.py — haelt jedes Belegzitat gegen die archivierte Quelle.

Das ist der Waechter der Deckungsanalyse. Jede Zeile des Pflichtenraums traegt ein
Zitat und einen Offset; dieses Skript liest die Quelldatei erneut und prueft, dass
dort genau dieses Zitat steht. Ein Zitat, das jemand umformuliert, kuerzt, aus dem
Gedaechtnis ergaenzt oder erfindet, faellt hier auf — unabhaengig davon, wie
plausibel es klingt.

Zusaetzlich geprueft:
  * Der SHA-256 der Quelle stimmt mit dem im Pflichtenraum vermerkten ueberein.
    Aendert sich die Quelle, sind alle Offsets ungueltig und die Ableitung veraltet.
  * Jede Einheit traegt eine Verifikationsstufe, und HYPOTHESE ist nur zulaessig,
    wo eine Begruendung danebensteht.
  * Kein Eintrag ohne Scope-Entscheidung: 'out' verlangt einen Grund. Stilles
    Weglassen ist der gefaehrlichste Fehler und deshalb hier ein Fehlschlag.

Aufruf:
  python3 tools/legal/verify_norm_quotes.py docs/coverage/aiact_pflichtenraum.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

NBSP = {" ": " ", " ": " ", " ": " ", " ": " "}
STUFEN = {"VERIFIZIERT", "SEKUNDAERQUELLE", "HYPOTHESE"}
BEFUNDE = {"gedeckt", "teilabdeckung", "luecke", "nicht_einschlaegig"}


def normalise(text: str) -> str:
    for a, b in NBSP.items():
        text = text.replace(a, b)
    return text


def flatten(text: str) -> str:
    """Wie der Extraktor: Zeilenumbrueche und Tabs zu einem Leerzeichen."""
    return re.sub(r"[\t ]*\n[\t \n]*", " ", text).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pflichtenraum", type=Path)
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    a = ap.parse_args()

    doc = yaml.safe_load(a.pflichtenraum.read_text(encoding="utf-8"))
    q = doc["quelle"]
    src_path = a.repo_root / q["datei"]

    findings: list[str] = []

    raw = src_path.read_text(encoding="utf-8")
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if digest != q["sha256"]:
        findings.append(
            f"Quelle {q['datei']}: SHA-256 ist {digest}, der Pflichtenraum nennt "
            f"{q['sha256']} — jeder Offset darin ist damit unbelegt"
        )
        _report(findings, 0)
        return 1

    norm = normalise(raw)
    units = doc.get("einheiten") or []
    ok = 0

    for u in units:
        uid = u.get("id", "<ohne id>")
        off, ln = u.get("offset"), u.get("laenge")
        beleg = u.get("beleg")

        if off is None or ln is None or not beleg:
            findings.append(f"{uid}: offset, laenge oder beleg fehlt — nicht pruefbar")
            continue

        actual = flatten(norm[off:off + ln])
        if actual != flatten(beleg):
            findings.append(
                f"{uid}: der Beleg steht nicht bei offset {off}.\n"
                f"      Quelle:  {actual[:160]}\n"
                f"      Eintrag: {flatten(beleg)[:160]}"
            )
            continue

        stufe = u.get("verifikation")
        if stufe not in STUFEN:
            findings.append(f"{uid}: verifikation '{stufe}' ist nicht {sorted(STUFEN)}")
        elif stufe == "HYPOTHESE" and not (u.get("hypothese_grund") or "").strip():
            findings.append(
                f"{uid}: HYPOTHESE ohne hypothese_grund — eine ungekennzeichnete "
                f"Auslegung ist der Fehler, gegen den diese Analyse gebaut ist"
            )

        scope = u.get("scope")
        if scope not in ("in", "out"):
            findings.append(f"{uid}: scope '{scope}' ist weder 'in' noch 'out'")
        elif scope == "out" and not (u.get("scope_grund") or "").strip():
            findings.append(f"{uid}: scope 'out' ohne Grund — stilles Weglassen")
        elif scope == "in":
            bef = u.get("befund")
            if bef not in BEFUNDE:
                findings.append(f"{uid}: befund '{bef}' ist nicht {sorted(BEFUNDE)}")
            elif bef in ("teilabdeckung", "luecke") and not (u.get("befund_grund") or "").strip():
                findings.append(f"{uid}: befund '{bef}' ohne befund_grund")

        ok += 1

    _report(findings, ok, len(units))
    return 1 if findings else 0


def _report(findings: list[str], ok: int, total: int = 0) -> None:
    if findings:
        print(f"\nLEGAL_QUOTES_VERBATIM — {len(findings)} Befund(e):\n")
        for f in findings:
            print(f"  - {f}")
        print(f"\n{ok} von {total} Einheiten wortgleich belegt.")
        print("FEHLGESCHLAGEN\n")
    else:
        print(f"\nLEGAL_QUOTES_VERBATIM — {ok} von {total} Einheiten wortgleich "
              f"gegen die Quelle geprueft, SHA-256 stimmt.")
        print("BESTANDEN\n")


if __name__ == "__main__":
    sys.exit(main())
