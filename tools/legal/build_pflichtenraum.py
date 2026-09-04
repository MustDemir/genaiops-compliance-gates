#!/usr/bin/env python3
"""build_pflichtenraum.py — erzeugt das Geruest des Pflichtenraums aus der Quelle.

Stufe 0 der Deckungsanalyse (HANDBUCH Teil 7 Punkt 9). Das Skript zaehlt JEDE
Einheit des Rechtstexts durch — Artikel, Absatz, Buchstabe — und legt fuer jede
eine Zeile an, deren Belegzitat aus der Datei geschnitten ist. Die Analysefelder
bleiben leer und werden von Hand gefuellt.

Der Zuschnitt ist Absicht: Vollstaendigkeit entsteht durch Aufzaehlung, nicht durch
Behauptung. Auch eine Einheit, die offensichtlich nicht einschlaegig ist, bekommt
eine Zeile und muss auf scope 'out' MIT GRUND gesetzt werden. Stilles Weglassen
waere sonst nicht unterscheidbar von Uebersehen — und genau das ist der Fehler,
den eine Deckungsanalyse ausschliessen soll.

Bestehende Zeilen werden beim erneuten Lauf NICHT ueberschrieben: das Skript
mischt neue Einheiten hinzu und meldet, welche in der Quelle verschwunden sind.

Aufruf:
  python3 tools/legal/build_pflichtenraum.py \
      --quelle docs/legal/wortlaut/aiact_2024-1689_DE.txt \
      --ziel   docs/coverage/aiact_pflichtenraum.yaml \
      --artikel 26 27
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_norm_units import index_articles, load, units_for  # noqa: E402

LEER = {
    "adressat": None,        # betreiber | anbieter | behoerde | sonstige
    "pflicht": None,         # CLAIM: die Pflicht in einem Satz
    "scope": None,           # in | out
    "scope_grund": None,
    "verifikation": None,    # VERIFIZIERT | SEKUNDAERQUELLE | HYPOTHESE
    "hypothese_grund": None,
    "omnibus": None,         # unveraendert | geaendert durch 2026/1744 Nr. N
    "requirement": [],
    "gate": [],
    "befund": None,          # gedeckt | teilabdeckung | luecke | nicht_einschlaegig
    "befund_grund": None,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quelle", type=Path, required=True)
    ap.add_argument("--ziel", type=Path, required=True)
    ap.add_argument("--artikel", nargs="*")
    ap.add_argument("--url", default="")
    ap.add_argument("--fassung", default="")
    a = ap.parse_args()

    raw, norm, digest = load(a.quelle)
    arts = index_articles(norm)
    want = set(a.artikel) if a.artikel else {x["artikel"] for x in arts}

    neu = []
    for art in arts:
        if art["artikel"] in want:
            for u in units_for(norm, art):
                neu.append({
                    "id": u["id"],
                    "artikel": u["artikel"],
                    "artikel_titel": u["artikel_titel"],
                    "absatz": u["absatz"],
                    "buchstabe": u["buchstabe"],
                    "offset": u["offset"],
                    "laenge": u["laenge"],
                    "saetze": len(u["saetze"]),
                    "beleg": u["text"],
                    **LEER,
                })

    if a.ziel.exists():
        doc = yaml.safe_load(a.ziel.read_text(encoding="utf-8")) or {}
        alt = {e["id"]: e for e in (doc.get("einheiten") or [])}
    else:
        doc, alt = {}, {}

    zusammen, unveraendert, ergaenzt = [], 0, 0
    for e in neu:
        if e["id"] in alt:
            vorhanden = alt[e["id"]]
            # Quelle gewinnt bei Beleg und Offsets, Analyse bleibt erhalten
            vorhanden.update({k: e[k] for k in
                              ("offset", "laenge", "saetze", "beleg",
                               "artikel_titel", "absatz", "buchstabe")})
            zusammen.append(vorhanden)
            unveraendert += 1
        else:
            zusammen.append(e)
            ergaenzt += 1

    verwaist = sorted(set(alt) - {e["id"] for e in neu})

    doc["quelle"] = {
        "datei": str(a.quelle),
        "sha256": digest,
        "url": a.url or (doc.get("quelle") or {}).get("url", ""),
        "fassung": a.fassung or (doc.get("quelle") or {}).get("fassung", ""),
        "abgerufen": (doc.get("quelle") or {}).get("abgerufen", date.today().isoformat()),
        "artikel_im_text": len(arts),
    }
    doc["einheiten"] = zusammen

    a.ziel.parent.mkdir(parents=True, exist_ok=True)
    a.ziel.write_text(
        yaml.dump(doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    print(f"Quelle:  {a.quelle}")
    print(f"SHA-256: {digest}")
    print(f"Ziel:    {a.ziel}")
    print(f"Einheiten: {len(zusammen)} ({ergaenzt} neu, {unveraendert} fortgeschrieben)")
    if verwaist:
        print(f"WARNUNG — {len(verwaist)} Eintraege haben in der Quelle keine Entsprechung "
              f"mehr: {', '.join(verwaist[:10])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
