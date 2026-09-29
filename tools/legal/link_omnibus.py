#!/usr/bin/env python3
"""link_omnibus.py — verbindet Grundfassung und Aenderungsrechtsakt (T-14.2).

Der Pflichtenraum des AI Act ist die Grundfassung; der Omnibus-Pflichtenraum
traegt die neuen Fassungen. Dieses Skript zieht die Verbindung:

  * jede Grundfassungs-Einheit, deren Text der Omnibus NEU FASST oder STREICHT,
    bekommt das Feld 'fassung_2026_1744' mit den uids der Omnibus-Einheiten,
    die an ihre Stelle treten (oder der Streichungsanweisung)
  * ein Bericht listet jede Anweisung Art. 1 Nr. 1-43 mit ihren Einheiten und
    ihren Grundfassungs-Zielen — und jede Anweisung, deren Ziel sich in der
    Grundfassung nicht finden liess

Das Feld ist Struktur, keine Analyse: es sagt, WELCHER Text gilt, nicht was er
bedeutet. Das Analysefeld 'omnibus' bleibt unberuehrt — es ist eine Aussage des
Nachtlaufs und wird vom PO korrigiert, nicht von einem Skript.

Aufruf:
  python3 tools/legal/link_omnibus.py docs/coverage/aiact_pflichtenraum.yaml \\
      docs/coverage/omnibus_pflichtenraum.yaml docs/coverage/migration/t14-2_omnibus.yaml
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


def _kandidaten(ziel: str) -> list[str]:
    """Wie die Grundfassung dieselbe Stelle nennt: exakt, ohne UAbs., ohne Abs."""
    out = [ziel]
    ohne_uabs = re.sub(r" UAbs\. \d+", "", ziel)
    out.append(ohne_uabs)
    out.append(re.sub(r" Abs\. \d+[a-z]?", "", ohne_uabs, count=1))
    return list(dict.fromkeys(out))


def main() -> int:
    grund_p, omni_p, bericht_p = map(Path, sys.argv[1:4])
    grund = yaml.safe_load(grund_p.read_text(encoding="utf-8"))
    omni = yaml.safe_load(omni_p.read_text(encoding="utf-8"))
    g_units = grund["einheiten"]
    g_ids = {e["id"] for e in g_units}

    for e in g_units:
        e.pop("fassung_2026_1744", None)

    anweisungen: dict[str, dict] = {}
    for u in omni["einheiten"]:
        a = anweisungen.setdefault(u["anweisung"], {"einheiten": [], "ziele_grundfassung": [],
                                                     "aenderung": set()})
        a["einheiten"].append(u["id"])
        if u.get("aenderung"):
            a["aenderung"].add(u["aenderung"])
        # 'wird wie folgt geaendert' mit vollem neuem Text (Art. 3 Nr. 14) ersetzt ebenfalls
        if u.get("aenderung") not in ("neu_gefasst", "gestrichen", "geaendert") or not u.get("ziel"):
            continue
        if u["id"].startswith("Omnibus ") and u["aenderung"] != "gestrichen":
            continue  # die Anweisung selbst ersetzt nichts; der neue Text tut es
        for ziel in re.split(r", ", u["ziel"]):
            treffer = None
            nur_kopf = False
            m = re.fullmatch(r"(.+) UAbs\. (\d+)", ziel)
            if m and int(m.group(2)) >= 2 and ziel not in g_ids and m.group(1) in g_ids:
                kinder = [e["id"] for e in g_units if e["id"].startswith(m.group(1) + " ")]
                if kinder:
                    # A-W6 (Review 09): the extractor appends a later subparagraph to the last
                    # subdivision of the paragraph (Art. 96 Abs. 1 lit. f carries UAbs. 2 and 3).
                    # The new UAbs. 2 replaces that unit, not every letter of the paragraph.
                    treffer, nur_kopf = [kinder[-1]], True
            for k in ([] if treffer else _kandidaten(ziel)):
                if " und " in k:  # 'Nr. 7 und 9'
                    stamm, rest = k.rsplit(" Nr. ", 1)
                    ks = [f"{stamm} Nr. {n}" for n in rest.split(" und ")]
                    if all(x in g_ids for x in ks):
                        treffer = ks
                        break
                elif k in g_ids:
                    treffer = [k]
                    break
            if not treffer:
                # A-W5 (Review 09): since T-14.3 some paragraphs exist only as sentence units
                # ('Art. 111 Abs. 2 Satz 1', 'Satz 2'). A new version of the paragraph replaces
                # every sentence; without this the link was lost silently.
                for k in _kandidaten(ziel):
                    saetze = [e["id"] for e in g_units if e["id"].startswith(k + " Satz ")]
                    if saetze:
                        treffer, nur_kopf = saetze, True
                        break
            if not treffer and ziel.endswith(" Einleitung"):
                # 'Die Einleitung erhaelt folgende Fassung' ersetzt den Kopf, nicht die Buchstaben
                for k in _kandidaten(ziel[:-len(" Einleitung")]):
                    if k in g_ids:
                        treffer, nur_kopf = [k], True
                        break
            if not treffer:
                # neue Untergliederung einer neu gefassten Stelle ('Art. 25 Abs. 2 lit. a n.F.'
                # gab es in der Grundfassung nicht): sie gehoert zur Elternstelle
                eltern = ziel
                while not treffer and re.search(r" (lit\.|Ziff\.|Nr\.) [0-9a-z]+$", eltern):
                    eltern = re.sub(r" (lit\.|Ziff\.|Nr\.) [0-9a-z]+$", "", eltern)
                    for k in _kandidaten(eltern):
                        if k in g_ids:
                            treffer, nur_kopf = [k], True
                            break
            if not treffer:
                continue  # z. B. Ueberschriften: sie sind keine Einheiten
            for e in g_units:
                # die Stelle selbst und alles darunter ('Art. 4' ersetzt 'Art. 4 Abs. 1 …')
                if any(e["id"] == t or (not nur_kopf and e["id"].startswith(t + " "))
                       for t in treffer):
                    e.setdefault("fassung_2026_1744", [])
                    if u["uid"] not in e["fassung_2026_1744"]:
                        e["fassung_2026_1744"].append(u["uid"])
                    if e["id"] not in a["ziele_grundfassung"]:
                        a["ziele_grundfassung"].append(e["id"])

    grund_p.write_text(yaml.dump(grund, allow_unicode=True, sort_keys=False, width=100),
                       encoding="utf-8")

    art1 = {k: v for k, v in anweisungen.items() if re.fullmatch(r"Omnibus Art\. 1 Nr\. \d+", k)
            or re.fullmatch(r"Omnibus Art\. 1 Nr\. \d+ lit\. [a-z]", k)}
    haupt = sorted({int(re.search(r"Nr\. (\d+)", k).group(1)) for k in art1})
    # Ersetzende Anweisungen, deren Ziel die Grundfassung nicht als Einheit kennt
    # (Ueberschriften sind keine Einheiten): gemeldet, nicht verschwiegen
    ohne_ziel = [k for k, v in art1.items()
                 if v["aenderung"] & {"neu_gefasst", "gestrichen"} and not v["ziele_grundfassung"]]
    bericht = {
        "anlass": "T-14.2 — Omnibus VO (EU) 2026/1744 als zweite Quelle",
        "anweisungen_art_1": len(haupt),
        "anweisungen_art_1_lueckenlos_1_bis_43": haupt == list(range(1, 44)),
        "einheiten_omnibus": len(omni["einheiten"]),
        "grundfassung_mit_neuer_fassung": sum(1 for e in g_units if e.get("fassung_2026_1744")),
        "neu_gefasst_oder_gestrichen_ohne_grundfassungsziel": sorted(ohne_ziel),
        "anweisungen": {k: {"aenderung": sorted(v["aenderung"]), "einheiten": v["einheiten"],
                            "ziele_grundfassung": v["ziele_grundfassung"]}
                        for k, v in anweisungen.items()},
    }
    bericht_p.parent.mkdir(parents=True, exist_ok=True)
    bericht_p.write_text(yaml.dump(bericht, allow_unicode=True, sort_keys=False, width=100),
                         encoding="utf-8")
    print(f"Anweisungen Art. 1: {len(haupt)} (lueckenlos 1-43: {haupt == list(range(1, 44))})")
    print(f"Grundfassungs-Einheiten mit neuer Fassung: {bericht['grundfassung_mit_neuer_fassung']}")
    print(f"neu gefasst/gestrichen ohne Grundfassungsziel: {len(ohne_ziel)} {sorted(ohne_ziel)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
