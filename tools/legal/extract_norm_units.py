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


# Das Ende des verfuegenden Teils. Danach folgen Schlussformel, Unterschriften,
# Fussnoten und Anhaenge — kein Normtext des letzten Artikels.
_SCHLUSSFORMELN = (
    "\nDiese Verordnung ist in allen ihren Teilen verbindlich",
    "\nDiese Richtlinie ist an die Mitgliedstaaten gerichtet",
    "\nGeschehen zu ",
)


def _ende_des_verfuegenden_teils(norm: str, ab: int) -> int:
    """Wo der letzte Artikel wirklich aufhoert.

    Ohne diese Grenze laeuft der letzte Artikel bis zum Dateiende und
    verschluckt Schlussformel, Unterschriften, Fussnoten und Anhaenge. Beim
    AI Act ergab das 58 Schein-Absaetze in Art. 113 — es waren die 58
    Quellenfussnoten —, waehrend die ECHTEN Absaetze des Artikels fehlten:
    ausgerechnet die Geltungsdaten, an denen die ganze Zeitschiene haengt.
    Der Befund kam aus dem Lauf vom 04.09. und ist der Grund fuer diese
    Funktion. Ein Extraktor, der am Ende ins Leere laeuft, erfindet Struktur.
    """
    kandidaten = [norm.find(m, ab) for m in _SCHLUSSFORMELN]
    kandidaten = [k for k in kandidaten if k > 0]
    return min(kandidaten) if kandidaten else len(norm)


def index_articles(norm: str) -> list[dict]:
    """Alle Artikel-Ueberschriften des verfuegenden Teils, in Reihenfolge.

    Gefiltert auf eine STRENG STEIGENDE Folge ab Artikel 1. Eine Zeile
    "Artikel 27" mitten in einer Aenderungsvorschrift ist eine Verweisung,
    keine Ueberschrift — bei NIS2 ergaeben die ungefilterten Treffer 73
    Artikel fuer 46 echte, mit der Folge ... 45, 27, 46. Wer daraus schneidet,
    bekommt Einheiten, die es nicht gibt.
    """
    roh = [(m.group(1), m.start() + 1) for m in re.finditer(r"\nArtikel (\d+)\n", norm)]
    hits: list[tuple[str, int]] = []
    erwartet = 1
    for num, start in roh:
        if int(num) == erwartet:
            hits.append((num, start))
            erwartet += 1
    if not hits:
        return []

    schluss = _ende_des_verfuegenden_teils(norm, hits[-1][1])
    out = []
    for i, (num, start) in enumerate(hits):
        end = hits[i + 1][1] - 1 if i + 1 < len(hits) else schluss
        body = norm[start:end]
        lines = [l for l in body.split("\n") if l.strip()]
        title = lines[1].strip() if len(lines) > 1 else ""
        out.append({"artikel": num, "titel": title, "start": start, "end": end})
    return out


def index_paragraphen(norm: str) -> list[dict]:
    """Deutsche Gesetze zaehlen in Paragraphen, nicht in Artikeln.

    EnWG, BSIG und KRITIS-Dachgesetz tragen dieselbe Pflichtenlage wie der
    AI Act auf demselben Adressaten, aber eine andere Gliederung: '§ 30
    Risikomanagementmassnahmen ...' statt 'Artikel 26'. Der Verbatim-Check
    bleibt unveraendert — nur das Schneiden ist normabhaengig, und genau
    deshalb steht es hier und nicht im Waechter.
    """
    hits = [(m.group(1), m.start() + 1)
            for m in re.finditer(r"\n§ (\d+[a-z]?) [^\n]+\n", norm)]
    # Dasselbe Problem wie bei den Artikeln, nur haeufiger: '§ 14 Absatz 2
    # Satz 1,' am Zeilenanfang im Fliesstext ist eine VERWEISUNG, keine
    # Ueberschrift. Ueberschriften laufen aufsteigend, Verweisungen nicht.
    # Der Filter nimmt nur, was die Zaehlung vorantreibt.
    eindeutig: list[tuple[str, int]] = []
    letzte = 0
    for num, start in hits:
        zahl = int(re.match(r"\d+", num).group())
        buchstabe = num[len(str(zahl)):]
        if zahl > letzte or (zahl == letzte and buchstabe):
            eindeutig.append((num, start))
            letzte = zahl
    out = []
    for i, (num, start) in enumerate(eindeutig):
        end = eindeutig[i + 1][1] - 1 if i + 1 < len(eindeutig) else len(norm)
        body = norm[start:end]
        erste = body.split("\n", 1)[0]
        titel = erste.split(" ", 2)[2].strip() if erste.count(" ") >= 2 else ""
        out.append({"artikel": f"§ {num}", "titel": titel,
                    "start": start, "end": end, "ist_paragraph": True})
    return out


def index_anhaenge(norm: str) -> list[dict]:
    """Anhaenge als eigene Einheiten-Traeger.

    Anhaenge sind Normtext, nicht Beiwerk: Anhang III des AI Act traegt die
    Hochrisiko-Einstufung, an der dieses ganze Vorhaben haengt (Nr. 2,
    kritische Infrastruktur), und Anhang I der NIS2-Richtlinie entscheidet, ob
    der Adressat eine wesentliche Einrichtung ist.

    Bis zum 07.09. hat der Extraktor sie uebersehen — sie steckten stillschweigend
    im letzten Artikel, weil dessen Ausschnitt bis zum Dateiende lief. Eine
    Einheit, die niemand als eigene sieht, wird auch von niemandem geprueft.
    """
    roh = [(m.group(1), m.start() + 1) for m in re.finditer(r"\n(?:ANHANG|Anhang) ([IVXLC]+)\n", norm)]
    # Dieselbe Ueberschrift steht zweimal in der Datei: einmal im
    # Inhaltsverzeichnis am Kopf, einmal als echter Anhang am Ende. Das
    # Verzeichnis liefert Ausschnitte von zwanzig Zeichen Laenge — es zaehlt
    # das LETZTE Vorkommen je Nummer.
    letzte: dict[str, int] = {}
    for num, start in roh:
        letzte[num] = start
    hits = sorted(letzte.items(), key=lambda kv: kv[1])
    out = []
    for i, (num, start) in enumerate(hits):
        end = hits[i + 1][1] - 1 if i + 1 < len(hits) else len(norm)
        body = norm[start:end]
        lines = [l for l in body.split("\n") if l.strip()]
        title = lines[1].strip() if len(lines) > 1 else ""
        out.append({"artikel": f"Anhang {num}", "titel": title,
                    "start": start, "end": end, "ist_anhang": True})
    return out


def split_nummern(norm: str, art: dict) -> list[dict]:
    """Nummerierte Punkte eines Anhangs: '1.', '2.', ... je auf eigener Zeile."""
    body_start = art["start"]
    body = norm[body_start:art["end"]]
    marks = [(m.group(1), m.start()) for m in re.finditer(r"\n(\d+)\.\n", body)]
    if not marks:
        lines = body.split("\n")
        skip = len("\n".join(lines[:3])) if len(lines) > 2 else 0
        return [{"absatz": "-", "start": body_start + skip, "end": art["end"]}]
    out = []
    for i, (num, rel) in enumerate(marks):
        s = body_start + rel + 1
        e = body_start + marks[i + 1][1] + 1 if i + 1 < len(marks) else art["end"]
        out.append({"absatz": num, "start": s, "end": e})
    return out


def split_absaetze(norm: str, art: dict) -> list[dict]:
    """Absaetze eines Artikels. Ein Artikel ohne Nummerierung ergibt genau einen."""
    body_start = art["start"]
    body = norm[body_start:art["end"]]
    # EU-Texte setzen '(1)   ' mit drei Leerzeichen, deutsche Gesetze '(1) ' mit
    # einem. Ein Muster fuer beide, statt zwei Parser fuer denselben Gedanken.
    marks = [(m.group(1), m.start()) for m in re.finditer(r"\n\((\d+)\)\s+", body)]
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
    """Einheiten eines Artikels, Paragraphen oder Anhangs.

    Leere Ausschnitte werden verworfen. Sie entstehen, wo eine Ueberschrift
    ohne Text folgt — ein Artefakt der Gliederung, kein Normtext. Eine Einheit
    ohne Beleg ist nicht pruefbar, und was nicht pruefbar ist, hat in einem
    Pflichtenraum nichts verloren.
    """
    out = []
    teile = split_nummern(norm, art) if art.get("ist_anhang") else split_absaetze(norm, art)
    for ab in teile:
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
    return [u for u in out if u["text"].strip()]


def _unit(norm, art, absatz, buchstabe, start, end) -> dict:
    text = norm[start:end]
    ist_anhang = art.get("ist_anhang", False)
    eigenname = ist_anhang or art.get("ist_paragraph", False)
    kopf = art["artikel"] if eigenname else f"Art. {art['artikel']}"
    stufe = "Nr." if ist_anhang else "Abs."
    kennung = (kopf
               + (f" {stufe} {absatz}" if absatz != "-" else "")
               + (f" lit. {buchstabe}" if buchstabe else ""))
    return {
        # Die lesbare Kennung ist NICHT eindeutig: ein Artikel ohne nummerierte
        # Absaetze kann dieselbe Buchstabenaufzaehlung mehrfach fuehren — Art. 3
        # (Begriffsbestimmungen) traegt 'lit. a' dreimal. Wer darauf zusammenfuehrt,
        # ueberschreibt fremde Analyse, ohne dass es auffaellt; genau das ist am
        # 07.09. passiert und wurde zurueckgenommen. Der Offset macht sie eindeutig,
        # und er ist innerhalb einer gehashten Quelle stabil.
        "uid": f"{kennung}@{start}",
        "id": kennung,
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
    arts = index_articles(norm) + index_paragraphen(norm) + index_anhaenge(norm)
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
