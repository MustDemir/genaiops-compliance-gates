#!/usr/bin/env python3
"""element_matrix.py — die Element-Matrix als Daten; 'gate' und 'nachbar_gate' daraus abgeleitet.

Paket 3b (30.09.2026, Review 11), PO-Entscheide M2a (29.09.2026) und M1a (30.09.2026).
Bis hierhin stand die Matrix nur als Tabelle in Review 07, und das Feld 'gate' im
Pflichtenraum war von Hand gesetzt. Es nannte Pruefer, Nachbarn und Ziele durcheinander:
Art. 26 Abs. 7 trug G-DEP-03, obwohl keine Regel die Unterrichtung der Arbeitnehmer
prueft - G-DEP-03 war das Gate, in das ein Check gehoeren wuerde. Ein Pruef-Agent, der
'gate' liest, haette daraus einen Pruefer gemacht.

Jetzt:
  * docs/coverage/matrix/element_matrix.yaml nennt je Pflicht mit Gate-Bezug die Elemente und je
    Element die Regel (Gate, Check, gelesenes Input-Feld) - geprueft, Nachbar oder ungeprueft;
  * pruefen() haelt jede genannte Regel gegen den OPA-AST (tools/rego_inputs.py): eine Regel
    dieses Gates und Checks muss das Feld lesen, der Check muss implementiert sein;
  * pruefen() leitet gate, nachbar_gate und die Befundklasse ab (M1a) und vergleicht mit dem
    Pflichtenraum - in beiden Richtungen: auch eine Zeile ohne Matrix-Eintrag darf kein Gate
    tragen und weder gedeckt noch Teilabdeckung sein;
  * schreiben() traegt gate und nachbar_gate in die Pflichtenraeume ein. Den Befund schreibt es
    nicht: eine Abweichung ist ein Vorschlag an den PO oder ein Fehler, keine Rechenaufgabe.

Aufruf:
  python3 tools/legal/element_matrix.py            # pruefen, Abweichungen zeigen
  python3 tools/legal/element_matrix.py --schreiben
Braucht opa auf PATH.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RAEUME = ("aiact", "omnibus")
STATUS = ("geprueft", "nachbar", "ungeprueft")
KLASSEN = ("gedeckt", "teilabdeckung", "luecke")


def _raum_datei(repo: Path, raum: str) -> Path:
    return repo / "docs" / "coverage" / f"{raum}_pflichtenraum.yaml"


def matrix(repo: Path = REPO_ROOT) -> dict:
    return yaml.safe_load((repo / "docs" / "coverage" / "matrix" / "element_matrix.yaml").read_text(encoding="utf-8")) or {}


def raeume(repo: Path = REPO_ROOT) -> dict[str, dict]:
    out = {}
    for raum in RAEUME:
        doc = yaml.safe_load(_raum_datei(repo, raum).read_text(encoding="utf-8")) or {}
        out[raum] = {e["id"]: e for e in doc.get("einheiten") or []}
    return out


def gate_checks(repo: Path = REPO_ROOT, getrackt: set | None = None) -> dict[str, dict[str, dict]]:
    """gate-id -> check-id -> policy_check (nur Dateien, die ein Klon enthaelt)."""
    out: dict[str, dict[str, dict]] = {}
    for datei in (repo / "gate-definitions").rglob("*.yaml"):
        rel = str(datei.relative_to(repo))
        if "template" in datei.name or (getrackt and rel not in getrackt):
            continue
        g = yaml.safe_load(datei.read_text(encoding="utf-8")) or {}
        if isinstance(g.get("id"), str):
            out[g["id"]] = {c["id"]: c for c in g.get("policy_checks") or []}
    return out


def regeln_mit_check(inv: list[dict], checks: dict[str, dict[str, dict]]) -> list[dict]:
    """Jede Regel mit den Checks, zu denen sie gehoeren kann.

    Traegt die Meldung eine Check-ID, ist es diese. Sonst jeder Check des Gates, der auf ihre
    Policy zeigt - die meisten Meldungen tragen noch keine Check-ID (E2, Paket 5)."""
    out = []
    for r in inv:
        gate = r.get("gate")
        if not gate:
            continue
        if r.get("check") and r["check"] in checks.get(gate, {}):
            kand = {r["check"]}
        else:
            kand = {cid for cid, c in checks.get(gate, {}).items() if c.get("policy") == r["policy"]}
        out.append({**r, "kandidaten": kand})
    return out


def _liest(regel: dict, feld: str) -> bool:
    return any(f == feld or f.endswith("." + feld) for f in regel["felder"])


def ableiten(eintrag: dict, zeile: dict) -> dict:
    """gate, nachbar_gate und Befundklasse aus den Elementen einer Zeile."""
    gate: list[str] = []
    nachbar: list[str] = []
    for el in eintrag.get("elemente") or []:
        ziel = gate if el.get("status") == "geprueft" else nachbar if el.get("status") == "nachbar" else None
        if ziel is None:
            continue
        for r in el.get("regeln") or []:
            if r["gate"] not in ziel:
                ziel.append(r["gate"])
    nachbar = [g for g in nachbar if g not in gate]
    stati = [el.get("status") for el in eintrag.get("elemente") or []]
    if "geprueft" not in stati:
        klasse = "luecke"
    elif all(s == "geprueft" for s in stati) and zeile.get("requirement"):
        klasse = "gedeckt"
    else:
        klasse = "teilabdeckung"
    return {"gate": gate, "nachbar_gate": nachbar, "befund": klasse}


def _register_offen(repo: Path) -> set[str]:
    """IDs, die im Entscheidungsregister nicht umgesetzt und nicht ausserhalb sind."""
    pfad = repo / "docs" / "coverage" / "review" / "entscheidungsregister.md"
    offen = set()
    for line in pfad.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*([A-Z][A-Za-z0-9-]*)\s*\|.*\|\s*([^|]*)\|\s*([^|]*)\|\s*$", line)
        if m and not m.group(2).strip().startswith(("umgesetzt", "außerhalb", "Stand")):
            offen.add(m.group(1))
    return offen


def pruefen(repo: Path = REPO_ROOT, inv: list[dict] | None = None,
            getrackt: set | None = None) -> tuple[list[str], dict]:
    """Befunde (leer = alles stimmt) und Zahlen fuer die Ausgabe."""
    if inv is None:
        sys.path.insert(0, str(repo / "tools"))
        from rego_inputs import inventar  # noqa: E402
        inv = inventar(repo)
    checks = gate_checks(repo, getrackt)
    regeln = regeln_mit_check(inv, checks)
    m = matrix(repo)
    rs = raeume(repo)
    offen = _register_offen(repo)
    befunde: list[str] = []
    zahl = {"zeilen": 0, "elemente": 0, "regeln": 0, "vorbehalt": [], "abgeleitet": 0}

    gesehen: set[tuple[str, str]] = set()
    for e in m.get("zeilen") or []:
        raum, kennung = e.get("raum"), e.get("id")
        wo = f"{raum}: {kennung}"
        if (raum, kennung) in gesehen:
            befunde.append(f"{wo} — steht zweimal in der Matrix")
            continue
        gesehen.add((raum, kennung))
        zeile = rs.get(raum, {}).get(kennung)
        if zeile is None:
            befunde.append(f"{wo} — Matrix-Zeile ohne Einheit im Pflichtenraum")
            continue
        if zeile.get("scope") != "in":
            befunde.append(f"{wo} — Matrix-Zeile fuer eine Einheit mit scope '{zeile.get('scope')}'")
        zahl["zeilen"] += 1
        elemente = e.get("elemente") or []
        if not elemente:
            befunde.append(f"{wo} — keine Elemente")
        for el in elemente:
            zahl["elemente"] += 1
            st, rr = el.get("status"), el.get("regeln") or []
            if st not in STATUS:
                befunde.append(f"{wo} — Element '{el.get('element')}': status '{st}' unbekannt")
                continue
            if st == "ungeprueft" and rr:
                befunde.append(f"{wo} — Element '{el.get('element')}': ungeprueft, nennt aber Regeln")
            if st != "ungeprueft" and not rr:
                befunde.append(f"{wo} — Element '{el.get('element')}': {st} ohne Regel")
            for r in rr:
                zahl["regeln"] += 1
                g, c, f = r.get("gate"), r.get("check"), r.get("feld")
                if g not in checks:
                    befunde.append(f"{wo} — Gate {g} gibt es in gate-definitions/ nicht")
                    continue
                if c not in checks[g]:
                    befunde.append(f"{wo} — {g} hat keinen Check {c}")
                    continue
                if checks[g][c].get("implementation") != "implemented":
                    befunde.append(f"{wo} — {g}/{c} ist {checks[g][c].get('implementation')}, "
                                   f"ohne Regel ist er weder Pruefer noch Nachbar")
                    continue
                if not any(x["gate"] == g and c in x["kandidaten"] and _liest(x, f) for x in regeln):
                    befunde.append(f"{wo} — keine Regel von {g}/{c} liest '{f}' (OPA-AST)")
        soll = ableiten(e, zeile)
        vb = e.get("vorbehalt")
        if vb:
            frage = (vb or {}).get("frage")
            if frage not in offen:
                befunde.append(f"{wo} — Vorbehalt '{frage}' steht im Register nicht offen; "
                               f"die Zeile muss jetzt abgeleitet werden")
            zahl["vorbehalt"].append(f"{kennung} ({frage}: abgeleitet {soll['befund']}, "
                                     f"gate {soll['gate'] or '–'})")
            continue
        zahl["abgeleitet"] += 1
        if set(zeile.get("gate") or []) != set(soll["gate"]):
            befunde.append(f"{wo} — gate ist {zeile.get('gate') or []}, abgeleitet {soll['gate']}")
        if set(zeile.get("nachbar_gate") or []) != set(soll["nachbar_gate"]):
            befunde.append(f"{wo} — nachbar_gate ist {zeile.get('nachbar_gate') or []}, "
                           f"abgeleitet {soll['nachbar_gate']}")
        if zeile.get("befund") in KLASSEN and zeile.get("befund") != soll["befund"]:
            befunde.append(f"{wo} — befund ist '{zeile.get('befund')}', nach den Elementen "
                           f"'{soll['befund']}' (M1a)")

    for raum, zeilen in rs.items():
        for kennung, zeile in zeilen.items():
            if (raum, kennung) in gesehen:
                continue
            wo = f"{raum}: {kennung}"
            if zeile.get("gate") or zeile.get("nachbar_gate"):
                befunde.append(f"{wo} — traegt gate {zeile.get('gate') or []} / nachbar_gate "
                               f"{zeile.get('nachbar_gate') or []} ohne Eintrag in der Element-Matrix")
            if zeile.get("scope") == "in" and zeile.get("befund") in ("gedeckt", "teilabdeckung"):
                befunde.append(f"{wo} — befund '{zeile.get('befund')}' ohne Eintrag in der Element-Matrix")
    return befunde, zahl


def schreiben(repo: Path = REPO_ROOT, inv: list[dict] | None = None) -> list[str]:
    """gate und nachbar_gate aus der Matrix in die Pflichtenraeume. Befund bleibt unberuehrt."""
    m = matrix(repo)
    eintraege = {(e["raum"], e["id"]): e for e in m.get("zeilen") or []}
    geaendert = []
    for raum in RAEUME:
        pfad = _raum_datei(repo, raum)
        doc = yaml.safe_load(pfad.read_text(encoding="utf-8"))
        for z in doc["einheiten"]:
            e = eintraege.get((raum, z["id"]))
            if e is not None and e.get("vorbehalt"):
                continue
            soll = ableiten(e, z) if e is not None else {"gate": [], "nachbar_gate": []}
            vorher = (list(z.get("gate") or []), list(z.get("nachbar_gate") or []))

            def _reihe(alt: list[str], neu: list[str]) -> list[str]:
                # was bleibt, behaelt seinen Platz; Neues kommt dahinter
                return [g for g in alt if g in neu] + [g for g in neu if g not in alt]

            if set(vorher[0]) != set(soll["gate"]):
                z["gate"] = _reihe(vorher[0], soll["gate"])
            if set(vorher[1]) != set(soll["nachbar_gate"]):
                if soll["nachbar_gate"]:
                    z["nachbar_gate"] = _reihe(vorher[1], soll["nachbar_gate"])
                else:
                    z.pop("nachbar_gate", None)
            nachher = (list(z.get("gate") or []), list(z.get("nachbar_gate") or []))
            if nachher != vorher:
                geaendert.append(f"{raum}: {z['id']}: gate {vorher[0]} -> {nachher[0]}; "
                                 f"nachbar_gate {vorher[1]} -> {nachher[1]}")
        pfad.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return geaendert


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--schreiben", action="store_true", help="gate und nachbar_gate eintragen")
    a = ap.parse_args()
    if a.schreiben:
        for x in schreiben():
            print(x)
    befunde, zahl = pruefen()
    print(f"{zahl['zeilen']} Zeilen, {zahl['elemente']} Elemente, {zahl['regeln']} Regelangaben; "
          f"abgeleitet {zahl['abgeleitet']}, unter Vorbehalt {len(zahl['vorbehalt'])}")
    for v in zahl["vorbehalt"]:
        print("  Vorbehalt:", v)
    for b in befunde:
        print("  -", b)
    return 1 if befunde else 0


if __name__ == "__main__":
    sys.exit(main())
