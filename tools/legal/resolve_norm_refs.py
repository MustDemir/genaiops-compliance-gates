#!/usr/bin/env python3
"""resolve_norm_refs.py — haelt jede Normverweisung der Gates und Requirements gegen den Pflichtenraum.

T-14.4 (28.09.2026), Befund T4. Bisher wurde nur eine Richtung geprueft: jede
Zeile des Pflichtenraums traegt ein wortgleiches Zitat (LEGAL_QUOTES_VERBATIM).
Die Gegenrichtung fehlte. G-OPS-02 berief sich auf 'Art. 3 Abs. 49', eine Stelle,
die es nicht gibt — Art. 3 zaehlt in Nummern —, und keine Pruefung sah es, weil
der String plausibel aussah (berichtigt am 28.09.2026). Dieselbe Deklaration ohne
Gegenstand, gegen die dieses Repo gebaut ist (B-20).

Aufgeloest wird gegen den Pflichtenraum der Grundfassung und den des Omnibus:

  genau      die Kennung gibt es ('Art. 26 Abs. 4')
  n.F.       es gibt sie als Neufassung ('Art. 6 Abs. 1a' -> 'Art. 6 Abs. 1a n.F.'), oder die
             Einheit der Grundfassung ist ganz ersetzt (neufassung: ersetzt, A-F2a) und die
             Verweisung folgt ihrem Feld fassung_2026_1744 ('Art. 25 Abs. 2' -> 'Art. 25 Abs. 2
             n.F.' und lit. a-c) — bewertet wird nur die geltende Fassung
  gestrichen die Einheit hat der Omnibus gestrichen (neufassung: gestrichen)
  gruppe     sie ist ein Oberbegriff vorhandener Einheiten ('Art. 15' -> 'Art. 15 Abs. 1' …,
             'Art. 26 Abs. 5' -> seine Saetze seit T-14.3)
  offen      nichts davon — die Verweisung zeigt ins Leere

Aufgeloest heisst nur: die Stelle existiert. Ob sie eine Betreiberpflicht ist,
steht im scope der getroffenen Einheiten und wird mitgemeldet ('in', 'out',
'unbewertet'); das zu bewerten ist Sache des PO (Deckungsanalyse 2b, Teil 4).

Aufruf:
  python3 tools/legal/resolve_norm_refs.py            # Tabelle aller Verweisungen
  python3 tools/legal/resolve_norm_refs.py --offen    # nur, was nicht aufloest
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REF_SCHLUESSEL = ("legal_refs", "eu_ai_act_refs")
RAEUME = ("aiact_pflichtenraum.yaml", "omnibus_pflichtenraum.yaml")


def _zerlegen(ref: str) -> list[str]:
    """'Art. 10 Abs. 1, Abs. 6' -> ['Art. 10 Abs. 1', 'Art. 10 Abs. 6']."""
    teile = [t.strip() for t in str(ref).split(",") if t.strip()]
    if not teile:
        return []
    kopf = re.match(r"(Art\. \d+[a-z]?|Anhang [IVXLC]+)", teile[0])
    out = [teile[0]]
    for t in teile[1:]:
        out.append(f"{kopf.group(1)} {t}" if kopf and not t.startswith(("Art.", "Anhang")) else t)
    return out


def verweisungen(repo_root: Path = REPO_ROOT) -> list[dict]:
    """Jede Verweisung mit Fundort: Datei, Gate/Requirement, Check."""
    out: list[dict] = []

    def gehen(o, datei: Path, traeger: str, check: str | None):
        if isinstance(o, dict):
            check = o.get("id") if isinstance(o.get("id"), str) and o.get("id", "").startswith("C-") else check
            for k, v in o.items():
                if k in REF_SCHLUESSEL:
                    for ref in (v if isinstance(v, list) else [v]):
                        for teil in _zerlegen(ref):
                            out.append({"datei": str(datei.relative_to(repo_root)), "traeger": traeger,
                                        "check": check, "schluessel": k, "roh": str(ref), "ref": teil})
                else:
                    gehen(v, datei, traeger, check)
        elif isinstance(o, list):
            for x in o:
                gehen(x, datei, traeger, check)

    dateien = sorted((repo_root / "gate-definitions").rglob("*.yaml")) + \
        sorted((repo_root / "requirements").rglob("*.yaml"))
    for datei in dateien:
        if "template" in datei.name:
            continue
        doc = yaml.safe_load(datei.read_text(encoding="utf-8")) or {}
        gehen(doc, datei, str(doc.get("id") or datei.stem), None)
    return out


def _raeume(repo_root: Path) -> dict[str, dict]:
    einheiten: dict[str, dict] = {}
    for name in RAEUME:
        pfad = repo_root / "docs" / "coverage" / name
        if not pfad.exists():
            continue
        for e in (yaml.safe_load(pfad.read_text(encoding="utf-8")) or {}).get("einheiten") or []:
            einheiten[e["id"]] = {"scope": e.get("scope"), "raum": name,
                                  "neufassung": e.get("neufassung"),
                                  "fassung": [u.split("@")[0] for u in e.get("fassung_2026_1744") or []]}
    return einheiten


def aufloesen(repo_root: Path = REPO_ROOT) -> list[dict]:
    einheiten = _raeume(repo_root)
    ergebnis = []
    for v in verweisungen(repo_root):
        ref = v["ref"]
        treffer, art = [], "offen"
        if ref in einheiten and einheiten[ref]["neufassung"] == "gestrichen":
            treffer, art = [], "gestrichen"
        elif ref in einheiten and einheiten[ref]["neufassung"] == "ersetzt":
            treffer, art = [t for t in einheiten[ref]["fassung"] if t in einheiten], "n.F."
        elif ref in einheiten:
            treffer, art = [ref], "genau"
        elif f"{ref} n.F." in einheiten:
            treffer, art = [f"{ref} n.F."], "n.F."
        else:
            gruppe = [i for i in einheiten if i.startswith(ref + " ")]
            if gruppe:
                treffer, art = gruppe, "gruppe"
        scopes = {einheiten[t]["scope"] for t in treffer}
        scope = ("in" if "in" in scopes else "out" if "out" in scopes else "unbewertet") if treffer else None
        ergebnis.append({**v, "aufloesung": art, "einheiten": len(treffer), "treffer": treffer,
                         "scope": scope})
    return ergebnis


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offen", action="store_true", help="nur Verweisungen ohne Einheit")
    a = ap.parse_args()
    erg = aufloesen()
    zeilen = [e for e in erg if e["aufloesung"] in ("offen", "gestrichen")] if a.offen else erg
    for e in zeilen:
        wo = e["traeger"] + (f"/{e['check']}" if e["check"] else "")
        print(f"{e['aufloesung']:<10} {str(e['scope'] or '-'):<10} {e['ref']:<26} {wo:<16} {e['datei']}")
    arten = Counter(e["aufloesung"] for e in erg)
    distinct = {e["ref"]: e for e in erg}
    print(f"\n{len(erg)} Verweisungen, {len(distinct)} verschiedene · "
          + " · ".join(f"{k} {n}" for k, n in sorted(arten.items())))
    print("verschiedene nach scope: " + " · ".join(
        f"{k} {n}" for k, n in sorted(Counter(str(e['scope']) for e in distinct.values()).items())))
    return 1 if arten.get("offen") or arten.get("gestrichen") else 0


if __name__ == "__main__":
    sys.exit(main())
