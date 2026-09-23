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
from extract_norm_units import (index_anhaenge, index_articles,
                                 index_paragraphen, load, units_for)  # noqa: E402

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


# Felder, die aus der Quelle kommen. Alles andere an einer Zeile ist Analyse.
STRUKTUR = ("uid", "id", "artikel", "artikel_titel", "abschnitt", "absatz", "nummer",
            "unterabsatz", "buchstabe", "ziffer", "offset", "laenge", "saetze", "beleg",
            "anweisung", "ziel", "aenderung", "fassung_2026_1744")


def _analyse(e: dict) -> dict:
    return {k: v for k, v in e.items() if k not in STRUKTUR and k not in ("migriert_von", "migration")}


def _hat_analyse(e: dict) -> bool:
    return any(v not in (None, [], "") for v in _analyse(e).values())


def _migrieren(zusammen: list, alt: dict, verwaist: list, bericht: Path) -> tuple[list, list]:
    """Traegt die Analyse verwaister Zeilen auf die neuen Einheiten derselben Stelle.

    Anlass T-14: der Extraktor schneidet feiner (Nummern, Ziffern, Abschnitte).
    Eine Zeile, die gestern 'Art. 5 Abs. 1 lit. i' hiess, heisst heute 'Art. 5
    Abs. 1 lit. c Ziff. i' — dieselbe Stelle, derselbe Offset. Und wo eine alte
    Zeile heute in mehrere zerfaellt, erbt jede neue die Analyse der alten.

      kennung_geaendert  gleicher Offset: die Analyse gehoert unveraendert dazu
      geerbt             die neue Einheit liegt INNERHALB der alten: die Analyse
                         ist eine Vorlage, keine Entscheidung — po_bestaetigt
                         wird false, wo es gesetzt war

    Eine verwaiste Zeile wird nur entfernt, wenn ihre Analyse mindestens eine
    neue Einheit erreicht hat oder sie keine traegt. Sonst bleibt sie und wird
    gemeldet — Analyse wird nicht stillschweigend weggeworfen.
    """
    alte = [alt[k] for k in verwaist]
    nach_offset = {e["offset"]: e for e in alte}
    zuordnung: dict[str, list] = {k: [] for k in verwaist}
    for e in zusammen:
        if e["uid"] in alt:
            continue  # unveraendert fortgeschrieben
        quelle, art = None, None
        if e["offset"] in nach_offset:
            quelle, art = nach_offset[e["offset"]], "kennung_geaendert"
        else:
            enthalten = [o for o in alte + list(alt.values())
                         if o["offset"] <= e["offset"] < o["offset"] + o["laenge"]
                         and o["uid"] != e["uid"]]
            if enthalten:
                quelle = min(enthalten, key=lambda o: o["laenge"])
                art = "geerbt"
        if quelle is None or not _hat_analyse(quelle):
            continue
        uebernahme = _analyse(quelle)
        if art == "geerbt" and "po_bestaetigt" in uebernahme:
            uebernahme["po_bestaetigt"] = False
        e.update(uebernahme)
        e["migriert_von"] = quelle["uid"]
        e["migration"] = art
        if quelle["uid"] in zuordnung:
            zuordnung[quelle["uid"]].append(e["uid"])

    bleibt, entfernt = [], []
    for k in verwaist:
        if zuordnung[k] or not _hat_analyse(alt[k]):
            entfernt.append(k)
        else:
            bleibt.append(k)
    bericht.parent.mkdir(parents=True, exist_ok=True)
    bericht.write_text(yaml.dump({
        "anlass": "T-14 — Extraktor schneidet Nummern, Ziffern, Unterabsaetze, Abschnitte",
        "verwaist": len(verwaist),
        "entfernt": len(entfernt),
        "bleibt_mit_analyse": bleibt,
        "zuordnung": {k: zuordnung[k] for k in verwaist},
        "geerbt": sorted(e["uid"] for e in zusammen if e.get("migration") == "geerbt"),
    }, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    return zusammen, bleibt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quelle", type=Path, required=True)
    ap.add_argument("--ziel", type=Path, required=True)
    ap.add_argument("--artikel", nargs="*")
    ap.add_argument("--verwaiste-entfernen", action="store_true",
                    help="Eintraege loeschen, die in der Quelle keine Entsprechung mehr "
                         "haben. Nur bewusst benutzen: sie koennen Analyse tragen.")
    ap.add_argument("--migrieren", type=Path, metavar="BERICHT",
                    help="Analyse verwaister Zeilen auf die neuen Einheiten derselben "
                         "Textstelle uebertragen (T-14) und den Zuordnungsbericht "
                         "alte uid -> neue uid(s) nach BERICHT schreiben.")
    ap.add_argument("--omnibus", action="store_true",
                    help="Die Quelle ist ein Aenderungsrechtsakt (T-14.2): Einheiten je "
                         "Anweisung und je neu gefasstem oder eingefuegtem Normtext.")
    ap.add_argument("--pdf", type=Path, help="Amtliches PDF, aus dem die Quelle abgeleitet ist")
    ap.add_argument("--ableitung", default="", help="Wie die Quelle aus dem PDF entstand")
    ap.add_argument("--url", default="")
    ap.add_argument("--fassung", default="")
    a = ap.parse_args()

    raw, norm, digest = load(a.quelle)
    if a.omnibus:
        from extract_omnibus_units import omnibus_units
        einheiten, anweisungen = omnibus_units(norm)
        arts = anweisungen
        quellen_einheiten = einheiten
    else:
        arts = index_articles(norm) + index_paragraphen(norm) + index_anhaenge(norm)
        want = set(a.artikel) if a.artikel else {x["artikel"] for x in arts}
        quellen_einheiten = [u for art in arts if art["artikel"] in want
                             for u in units_for(norm, art)]

    neu = []
    for u in quellen_einheiten:
        if True:
            if True:
                neu.append({
                    "uid": u["uid"],
                    "id": u["id"],
                    "artikel": u["artikel"],
                    "artikel_titel": u["artikel_titel"],
                    "abschnitt": u["abschnitt"],
                    "absatz": u["absatz"],
                    "nummer": u["nummer"],
                    "unterabsatz": u["unterabsatz"],
                    "buchstabe": u["buchstabe"],
                    "ziffer": u["ziffer"],
                    "offset": u["offset"],
                    "laenge": u["laenge"],
                    "saetze": len(u["saetze"]),
                    "beleg": u["text"],
                    **{k: u[k] for k in ("anweisung", "ziel", "aenderung") if k in u},
                    **LEER,
                })

    if a.ziel.exists():
        doc = yaml.safe_load(a.ziel.read_text(encoding="utf-8")) or {}
        # Auf uid zusammenfuehren, nicht auf id: die lesbare Kennung ist nicht
        # eindeutig. Bestandszeilen ohne uid bekommen sie aus ihrem Offset —
        # dieselbe Bildungsregel wie im Extraktor.
        alt = {}
        for e in (doc.get("einheiten") or []):
            key = e.get("uid") or f"{e['id']}@{e.get('offset')}"
            e.setdefault("uid", key)
            alt[key] = e
    else:
        doc, alt = {}, {}
    # Stand VOR dem Fortschreiben: die Migration braucht die alten Spannen,
    # und das Fortschreiben setzt Offset und Laenge auf den neuen Zuschnitt.
    alt_vorher = {k: dict(v) for k, v in alt.items()}

    zusammen, unveraendert, ergaenzt = [], 0, 0
    for e in neu:
        if e["uid"] in alt:
            vorhanden = alt[e["uid"]]
            # Quelle gewinnt bei Beleg und Offsets, Analyse bleibt erhalten
            vorhanden.update({k: e[k] for k in STRUKTUR
                              if k in e and k not in ("uid", "id", "artikel")})
            zusammen.append(vorhanden)
            unveraendert += 1
        else:
            zusammen.append(e)
            ergaenzt += 1

    verwaist = sorted(set(alt) - {e["uid"] for e in neu})
    if a.migrieren:
        zusammen, verwaist = _migrieren(zusammen, alt_vorher, verwaist, a.migrieren)
    if verwaist and not a.verwaiste_entfernen:
        # Nicht stillschweigend wegwerfen: eine verwaiste Zeile kann Analyse
        # tragen, die jemand geschrieben hat. Sie bleibt, bis es jemand sagt.
        zusammen.extend(alt[k] for k in verwaist)

    doc["quelle"] = {
        "datei": str(a.quelle),
        "sha256": digest,
        "url": a.url or (doc.get("quelle") or {}).get("url", ""),
        "fassung": a.fassung or (doc.get("quelle") or {}).get("fassung", ""),
        "abgerufen": (doc.get("quelle") or {}).get("abgerufen", date.today().isoformat()),
        "artikel_im_text": len(arts),
    }
    if a.omnibus:
        doc["quelle"]["anweisungen_im_text"] = doc["quelle"].pop("artikel_im_text")
    if a.pdf:
        import hashlib
        doc["quelle"]["pdf"] = str(a.pdf)
        doc["quelle"]["pdf_sha256"] = hashlib.sha256(a.pdf.read_bytes()).hexdigest()
    if a.ableitung:
        doc["quelle"]["ableitung"] = a.ableitung
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
