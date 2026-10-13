#!/usr/bin/env python3
"""faelle.py — one duty space, three reference cases (BK-F3 b, review 18).

Until 13 Oct 2026 every row's `scope` answered one question: does this duty bind the
operator of the redispatch system? The lead case is now a bank, the hospital and the
grid follow, and a row that is `out` for the grid can be `in` for the bank (Art. 27,
Art. 86) or for the hospital (the Annex I path). A single `scope` cannot say that.

The case register (docs/coverage/faelle/faelle.yaml) names the cases. A row whose application
depends on the case carries `faelle`: the cases it is `in` for. Everything else applies
to every case alike. This script

  * finds the case-dependent rows — by text markers in their reasoning, or because the
    register lists them,
  * checks rows and register against each other (pruefen), which is what the guard
    CASE_SCOPE_DECLARED runs, and
  * with --migrieren writes `faelle` onto case-dependent rows that do not carry it yet,
    derived from today's `scope` — which, until the bank and hospital checklists are
    decided, is the grid case's scope. It decides nothing new and leaves every row
    that already carries `faelle` alone.

Calls:
  python3 tools/legal/faelle.py              # report per case, findings
  python3 tools/legal/faelle.py --migrieren  # write `faelle` from today's scope (grid)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER = Path("docs") / "coverage" / "faelle" / "faelle.yaml"

# Reasoning that ties a row to a classification path, a sector or a kind of operator.
# A row whose reasoning says this has to say for which cases it holds.
MARKER = re.compile(
    r"Systemtyp|Bereichsausnahme|Redispatch|Netzbetreib|Verteilnetz|Anhang III Nr\.? ?\d|"
    r"Anhang I Abschn|Finanzinstitut|Referenzfall|Leitfall|kritische[nr]? Infrastruktur|"
    r"Strafverfolgungsbehoerden sind|Betreiber ist Behoerde|Behoerde verwenden"
)
GRUNDFELDER = ("scope_grund", "befund_grund", "hypothese_grund")
BEFUNDE = {"gedeckt", "teilabdeckung", "luecke", "nicht_einschlaegig"}
STUFEN = {"VERIFIZIERT", "SEKUNDAERQUELLE", "HYPOTHESE"}


def register(repo_root: Path = REPO_ROOT) -> dict:
    return yaml.safe_load((repo_root / REGISTER).read_text(encoding="utf-8")) or {}


def _gelistet(reg: dict) -> set[tuple[str, str]]:
    return {(g["raum"], i) for g in reg.get("fallabhaengig") or [] for i in g["ids"]}


def raeume(repo_root: Path = REPO_ROOT) -> dict[str, tuple[Path, dict]]:
    out = {}
    for pfad in sorted((repo_root / "docs" / "coverage").glob("*_pflichtenraum.yaml")):
        out[pfad.name.removesuffix("_pflichtenraum.yaml")] = (
            pfad, yaml.safe_load(pfad.read_text(encoding="utf-8")) or {})
    return out


def fallabhaengig(raum: str, e: dict, gelistet: set[tuple[str, str]]) -> str | None:
    """Why this row depends on the case, or None."""
    if (raum, e["id"]) in gelistet:
        return "im Fallregister gelistet"
    for feld in GRUNDFELDER:
        m = MARKER.search(str(e.get(feld) or ""))
        if m:
            return f"{feld} nennt '{m.group(0)}'"
    return None


def faelle_der_zeile(e: dict, alle: list[str]) -> list[str]:
    """The cases a row is `in` for: its `faelle`, or every case when it has none."""
    if e.get("scope") != "in":
        return list(e.get("faelle") or [])
    return list(e["faelle"]) if "faelle" in e else list(alle)


def pruefen(repo_root: Path = REPO_ROOT) -> tuple[list[str], dict]:
    reg = register(repo_root)
    faelle = reg.get("faelle") or {}
    alle = list(faelle)
    gelistet = _gelistet(reg)
    findings: list[str] = []
    je_fall: Counter = Counter()
    fallabh = 0
    zeilen: dict[tuple[str, str], dict] = {}

    for raum, (pfad, doc) in raeume(repo_root).items():
        for e in doc.get("einheiten") or []:
            zeilen[(raum, e["id"])] = e
            scope = e.get("scope")
            if scope not in ("in", "out"):
                continue  # not scoped yet (sector stack): nothing to say per case
            grund = fallabhaengig(raum, e, gelistet)
            if grund:
                fallabh += 1
                if "faelle" not in e:
                    findings.append(f"{pfad.name}: {e['id']} — fallabhaengig ({grund}), nennt keine `faelle`")
                    continue
            if "faelle" in e:
                f = e["faelle"]
                if not isinstance(f, list):
                    findings.append(f"{pfad.name}: {e['id']} — `faelle` ist keine Liste")
                    continue
                for k in f:
                    if k not in faelle:
                        findings.append(f"{pfad.name}: {e['id']} — Fall '{k}' steht nicht im Fallregister")
                if len(set(f)) != len(f):
                    findings.append(f"{pfad.name}: {e['id']} — `faelle` nennt einen Fall doppelt")
                if (scope == "in") != bool(f):
                    findings.append(f"{pfad.name}: {e['id']} — scope '{scope}', aber faelle {f}: "
                                    f"`in` heisst einschlaegig fuer mindestens einen Fall")
            gilt = faelle_der_zeile(e, alle)
            for feld, schluessel, erlaubt in (("befund_je_fall", "befund", BEFUNDE),
                                              ("verifikation_je_fall", "verifikation", STUFEN)):
                for k, v in (e.get(feld) or {}).items():
                    if k not in gilt:
                        findings.append(f"{pfad.name}: {e['id']} — {feld} nennt '{k}', "
                                        f"die Zeile gilt nicht fuer diesen Fall")
                    # a plain value, or {befund|verifikation: …, <its reason>: …}
                    wert = v.get(schluessel) if isinstance(v, dict) else v
                    if wert not in erlaubt:
                        findings.append(f"{pfad.name}: {e['id']} — {feld}.{k} = {wert!r} ist kein gueltiger Wert")
                    if feld == "verifikation_je_fall" and wert == "HYPOTHESE" and not (
                            isinstance(v, dict) and str(v.get("hypothese_grund") or "").strip()):
                        findings.append(f"{pfad.name}: {e['id']} — verifikation_je_fall.{k} HYPOTHESE ohne Grund")
            if scope == "in":
                for k in gilt:
                    je_fall[k] += 1

    for raum, kennung in sorted(gelistet):
        if (raum, kennung) not in zeilen:
            findings.append(f"faelle.yaml: {raum} {kennung} — als fallabhaengig gelistet, nicht im Pflichtenraum")
    for name, fall in faelle.items():
        if fall.get("pflichtenraum") not in ("geprueft", "offen"):
            findings.append(f"faelle.yaml: {name} — pflichtenraum ist weder 'geprueft' noch 'offen'")
        for ref in fall.get("einstufung") or []:
            z = zeilen.get((ref["raum"], ref["id"]))
            if z is None:
                findings.append(f"faelle.yaml: {name} — Einstufungsnorm {ref['id']} fehlt im Pflichtenraum")
            elif fall.get("pflichtenraum") == "geprueft" and name not in faelle_der_zeile(z, alle):
                findings.append(f"faelle.yaml: {name} ist geprueft, aber seine Einstufungsnorm "
                                f"{ref['id']} ist fuer ihn nicht `in`")

    stand = {"faelle": alle, "je_fall": dict(je_fall), "fallabhaengig": fallabh,
             "geprueft": [n for n, f in faelle.items() if f.get("pflichtenraum") == "geprueft"]}
    return findings, stand


def migrieren(repo_root: Path = REPO_ROOT) -> dict[str, int]:
    """Write `faelle` onto case-dependent rows without it, from today's scope (grid case)."""
    reg = register(repo_root)
    gelistet = _gelistet(reg)
    geschrieben: dict[str, int] = {}
    for raum, (pfad, doc) in raeume(repo_root).items():
        n = 0
        for e in doc.get("einheiten") or []:
            if e.get("scope") not in ("in", "out") or "faelle" in e:
                continue
            if fallabhaengig(raum, e, gelistet):
                e["faelle"] = ["netz"] if e["scope"] == "in" else []
                n += 1
        if n:
            pfad.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
        geschrieben[raum] = n
    return geschrieben


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--migrieren", action="store_true",
                    help="`faelle` aus dem heutigen scope (Netz) auf fallabhaengige Zeilen schreiben")
    a = ap.parse_args()
    if a.migrieren:
        for raum, n in migrieren().items():
            print(f"{raum}: {n} Zeilen erhalten `faelle`")
    findings, stand = pruefen()
    print("in je Fall: " + " · ".join(f"{k} {stand['je_fall'].get(k, 0)}" for k in stand["faelle"])
          + f" · fallabhaengige Zeilen {stand['fallabhaengig']} · geprueft: {', '.join(stand['geprueft']) or '-'}")
    for f in findings:
        print(f"  - {f}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
