#!/usr/bin/env python3
"""extract_norm_units.py — schneidet einen archivierten Rechtstext in Pflichteneinheiten.

Warum es dieses Skript gibt: Stufe 0 der Deckungsanalyse verlangt, dass jede Zeile
des Pflichtenraums ein WOERTLICHES Zitat aus der Quelle traegt. Ein Zitat, das ein
Mensch oder ein Modell abtippt, ist eine Erinnerung; ein Zitat, das ein Skript aus
der Datei schneidet, ist ein Auszug. Nur das zweite ist ohne Vertrauen nachpruefbar.

Deshalb erzeugt dieses Skript die Einheiten, und nichts anderes darf sie erzeugen:

  Artikel -> Absatz -> (Buchstabe) -> Satz

Jede Einheit traegt ihren Zeichen-Offset in der Quelldatei. `verify_norm_quotes.py`
liest die Quelle erneut und prueft, dass an genau diesem Offset genau dieser Text
steht. Weicht ein Zeichen ab, wird die Pruefung rot.

Die Quelle wird NIE veraendert. Fuer den Abgleich werden geschuetzte Leerzeichen
1:1 auf normale Leerzeichen abgebildet — eine Ersetzung, die die Offsets erhaelt,
was das Skript selbst zusichert (assert).

Aufruf:
  python3 tools/legal/extract_norm_units.py <quelle.txt> --artikel 26 27
  python3 tools/legal/extract_norm_units.py <quelle.txt> --alle --json units.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# 1:1-Ersetzungen. Jeder Schluessel ist EIN Zeichen und wird durch EIN Zeichen
# ersetzt, damit die Offsets der normalisierten Fassung auf die Rohdatei passen.
NBSP = {" ": " ", " ": " ", " ": " ", " ": " "}

# Abkuerzungen, hinter denen ein Punkt KEIN Satzende ist. Ohne diese Liste
# zerfaellt "Artikel 79 Absatz 1 birgt" an jedem "Abs." in zwei Saetze, und die
# Satzebene waere unbrauchbar.
ABBREV = [
    "Abs", "Art", "Nr", "lit", "Buchst", "bzw", "ff", "vgl", "ggf", "einschl",
    "z. B", "z.B", "d. h", "d.h", "u. a", "u.a", "s. o", "s. u", "Abl", "ABl",
    "EG", "EU", "EWR", "Ziff", "Unterabs", "UAbs", "S", "Nrn",
]


def load(path: Path) -> tuple[str, str, str]:
    raw = path.read_text(encoding="utf-8")
    norm = raw
    for a, b in NBSP.items():
        norm = norm.replace(a, b)
    assert len(norm) == len(raw), (
        "Normalisierung hat die Laenge veraendert — Offsets waeren wertlos"
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return raw, norm, digest


def index_articles(norm: str) -> list[dict]:
    """Alle Artikel-Ueberschriften des verfuegenden Teils, in Reihenfolge."""
    hits = [(m.group(1), m.start() + 1) for m in re.finditer(r"\nArtikel (\d+)\n", norm)]
    out = []
    for i, (num, start) in enumerate(hits):
        end = hits[i + 1][1] - 1 if i + 1 < len(hits) else len(norm)
        body = norm[start:end]
        lines = [l for l in body.split("\n") if l.strip()]
        title = lines[1].strip() if len(lines) > 1 else ""
        out.append({"artikel": num, "titel": title, "start": start, "end": end})
    return out


def split_absaetze(norm: str, art: dict) -> list[dict]:
    """Absaetze eines Artikels. Ein Artikel ohne Nummerierung ergibt genau einen."""
    body_start = art["start"]
    body = norm[body_start:art["end"]]
    marks = [(m.group(1), m.start()) for m in re.finditer(r"\n\((\d+)\)\s{2,}", body)]
    if not marks:
        # Unnummerierter Artikel: alles nach der Ueberschriftszeile ist Absatz "-"
        lines = body.split("\n")
        skip = len("\n".join(lines[:3])) if len(lines) > 2 else 0
        return [{"absatz": "-", "start": body_start + skip, "end": art["end"]}]
    out = []
    for i, (num, rel) in enumerate(marks):
        s = body_start + rel + 1
        e = body_start + marks[i + 1][1] + 1 if i + 1 < len(marks) else art["end"]
        out.append({"absatz": num, "start": s, "end": e})
    return out


def split_buchstaben(norm: str, ab: dict) -> list[dict]:
    """Buchstaben-Aufzaehlungen innerhalb eines Absatzes."""
    seg = norm[ab["start"]:ab["end"]]
    marks = [(m.group(1), m.start()) for m in re.finditer(r"\n([a-z])\)\n", seg)]
    if not marks:
        return []
    out = []
    for i, (ltr, rel) in enumerate(marks):
        s = ab["start"] + rel + 1
        e = ab["start"] + marks[i + 1][1] + 1 if i + 1 < len(marks) else ab["end"]
        out.append({"buchstabe": ltr, "start": s, "end": e})
    return out


def split_saetze(norm: str, start: int, end: int) -> list[dict]:
    """Saetze einer Einheit, mit Offset. Konservativ: trennt nur an '. ' und
    niemals hinter einer bekannten Abkuerzung."""
    seg = norm[start:end]
    flat = re.sub(r"[\t ]*\n[\t \n]*", " ", seg).strip()
    if not flat:
        return []
    # Offset des geflatteten Textes zurueckrechnen ist nicht eindeutig; deshalb
    # traegt der Satz den Offset SEINER EINHEIT und wird ueber die Einheit geprueft.
    parts, buf = [], ""
    for tok in re.split(r"(?<=\.)\s+", flat):
        buf = (buf + " " + tok).strip() if buf else tok
        stripped = buf.rstrip()
        if not stripped.endswith("."):
            continue
        tail = stripped[:-1].split()[-1] if stripped[:-1].split() else ""
        if tail.rstrip(".") in ABBREV or re.fullmatch(r"\d+", tail):
            continue
        parts.append(buf.strip())
        buf = ""
    if buf.strip():
        parts.append(buf.strip())
    return [{"nr": i + 1, "text": p} for i, p in enumerate(parts)]


def units_for(norm: str, art: dict) -> list[dict]:
    out = []
    for ab in split_absaetze(norm, art):
        letters = split_buchstaben(norm, ab)
        if letters:
            head_end = letters[0]["start"]
            if norm[ab["start"]:head_end].strip():
                out.append(_unit(norm, art, ab["absatz"], None, ab["start"], head_end))
            for lt in letters:
                out.append(_unit(norm, art, ab["absatz"], lt["buchstabe"],
                                 lt["start"], lt["end"]))
        else:
            out.append(_unit(norm, art, ab["absatz"], None, ab["start"], ab["end"]))
    return out


def _unit(norm, art, absatz, buchstabe, start, end) -> dict:
    text = norm[start:end]
    return {
        "id": f"Art. {art['artikel']}"
              + (f" Abs. {absatz}" if absatz != "-" else "")
              + (f" lit. {buchstabe}" if buchstabe else ""),
        "artikel": art["artikel"],
        "artikel_titel": art["titel"],
        "absatz": absatz,
        "buchstabe": buchstabe,
        "offset": start,
        "laenge": end - start,
        "text": re.sub(r"[\t ]*\n[\t \n]*", " ", text).strip(),
        "saetze": split_saetze(norm, start, end),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("quelle", type=Path)
    ap.add_argument("--artikel", nargs="*", help="Artikelnummern; leer = alle")
    ap.add_argument("--alle", action="store_true")
    ap.add_argument("--json", type=Path, help="Einheiten als JSON schreiben")
    ap.add_argument("--zaehlen", action="store_true", help="nur Bilanz drucken")
    a = ap.parse_args()

    raw, norm, digest = load(a.quelle)
    arts = index_articles(norm)
    want = set(a.artikel or []) if not a.alle else {x["artikel"] for x in arts}
    if not want:
        want = {x["artikel"] for x in arts}

    units = []
    for art in arts:
        if art["artikel"] in want:
            units.extend(units_for(norm, art))

    if a.json:
        a.json.write_text(json.dumps(
            {"quelle": str(a.quelle), "sha256": digest,
             "artikel_gesamt": len(arts), "einheiten": units},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{len(units)} Einheiten -> {a.json}")

    print(f"Quelle: {a.quelle}")
    print(f"SHA-256: {digest}")
    print(f"Artikel im Text: {len(arts)} | ausgewertet: {len(want)} | Einheiten: {len(units)}")
    if a.zaehlen:
        return 0
    for u in units:
        print(f"\n[{u['id']}]  offset={u['offset']} laenge={u['laenge']} saetze={len(u['saetze'])}")
        print(f"  {u['text'][:300]}{'…' if len(u['text']) > 300 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
