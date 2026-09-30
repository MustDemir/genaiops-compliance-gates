#!/usr/bin/env python3
"""extract_norm_units.py — schneidet einen archivierten Rechtstext in Pflichteneinheiten.

Warum es dieses Skript gibt: Stufe 0 der Deckungsanalyse verlangt, dass jede Zeile
des Pflichtenraums ein WOERTLICHES Zitat aus der Quelle traegt. Ein Zitat, das ein
Mensch oder ein Modell abtippt, ist eine Erinnerung; ein Zitat, das ein Skript aus
der Datei schneidet, ist ein Auszug. Nur das zweite ist ohne Vertrauen nachpruefbar.

Deshalb erzeugt dieses Skript die Einheiten, und nichts anderes darf sie erzeugen:

  Artikel | Paragraph | Anhang -> (Abschnitt) -> (Absatz) -> (Nummer) -> (Unterabsatz)
      -> (Buchstabe) -> (Ziffer) -> Satz            (Gliederung seit T-14)

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


# T-15 (A-W9, Review 10): Kapitel- und Abschnittsueberschriften stehen zwischen zwei
# Artikeln auf eigener Zeile. Ohne Grenze hingen sie am letzten Glied des Artikels davor
# ('Art. 4' endete mit 'KAPITEL II VERBOTENE PRAKTIKEN IM KI-BEREICH') - 53 Belege in
# AI Act, DSGVO und NIS2 trugen Text, der kein Normtext ist.
_UEBERSCHRIFT = re.compile(r"\n(?:KAPITEL [IVXLC]+|ABSCHNITT \d+|Abschnitt \d+|TITEL [IVXLC]+)\n")

# T-15 (A-W3): die Fusszeile des Amtsblatts am Dateiende ('ELI: … ISSN …') ist kein
# Normtext; sie hing am letzten Glied des letzten Anhangs (Anhang XIII lit. g).
_DOKUMENTFUSS = re.compile(r"\nELI: http")


def _ohne_ueberschrift(norm: str, start: int, end: int) -> int:
    """Ende eines Artikels vor der ersten Kapitel- oder Abschnittsueberschrift danach."""
    m = _UEBERSCHRIFT.search(norm, start, end)
    return m.start() if m else end


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
        end = _ohne_ueberschrift(norm, start, end)
        body = norm[start:end]
        lines = [l for l in body.split("\n") if l.strip()]
        title = lines[1].strip() if len(lines) > 1 else ""
        out.append({"artikel": num, "titel": title, "start": start, "end": end})
    return out


# Woerter, mit denen eine Verweisung beginnt, aber keine Ueberschrift:
# '§ 32 Absatz 2 bis 5 und § 36 des BSI-Gesetzes sind entsprechend anzuwenden.'
_VERWEIS_START = re.compile(
    r"(Absatz|Abs\.|Satz|Nummer|Nr\.|Buchstabe|und|bis|des|der|oder|in|nach|"
    r"gilt|gelten|ist|sind|findet|finden)\b")


def index_paragraphen(norm: str) -> list[dict]:
    """Deutsche Gesetze zaehlen in Paragraphen, nicht in Artikeln.

    EnWG, BSIG und KRITIS-Dachgesetz tragen dieselbe Pflichtenlage wie der
    AI Act auf demselben Adressaten, aber eine andere Gliederung: '§ 30
    Risikomanagementmassnahmen ...' statt 'Artikel 26'. Der Verbatim-Check
    bleibt unveraendert — nur das Schneiden ist normabhaengig, und genau
    deshalb steht es hier und nicht im Waechter.

    T-14 (23.09.2026): Zwei Fehler, die beim EnWG zusammentrafen. Die
    Ueberschrift in der ERSTEN Zeile der Datei wurde nie gefunden (das Muster
    verlangte einen Zeilenumbruch davor) — § 5c fehlte. Und eine Verweisung am
    Zeilenanfang ('§ 32 Absatz 2 bis 5 ... sind entsprechend anzuwenden.')
    trieb die Zaehlung auf 32, sodass § 5e und § 11 als 'nicht aufsteigend'
    verworfen wurden und als Scheinabsaetze eines § 32 endeten. Eine
    Ueberschrift beginnt nicht mit einem Verweiswort und endet nicht mit Punkt.
    """
    text = "\n" + norm  # die erste Zeile mitnehmen; Index in text == Index in norm des '§'
    hits = []
    for m in re.finditer(r"\n§ (\d+[a-z]?) ([^\n]+)\n", text):
        rest = m.group(2).strip()
        if _VERWEIS_START.match(rest) or rest.endswith("."):
            continue
        hits.append((m.group(1), m.start()))
    # Dasselbe Problem wie bei den Artikeln, nur haeufiger: Ueberschriften
    # laufen aufsteigend, Verweisungen nicht. Der Filter nimmt nur, was die
    # Zaehlung vorantreibt.
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
        fuss = _DOKUMENTFUSS.search(norm, start, end)
        if fuss:
            end = fuss.start()
        body = norm[start:end]
        lines = [l for l in body.split("\n") if l.strip()]
        title = lines[1].strip() if len(lines) > 1 else ""
        out.append({"artikel": f"Anhang {num}", "titel": title,
                    "start": start, "end": end, "ist_anhang": True})
    return out


# ── Gliederung unterhalb von Artikel, Paragraph und Anhang ──────────────────
#
# T-14 (23.09.2026). Bis hierhin kannte der Extraktor genau zwei Ebenen unter
# dem Artikel: Absatz und Buchstabe. Das Recht kennt mehr, und jede fehlende
# Ebene erzeugte doppelte oder falsche Kennungen:
#   * Nummern: Art. 3 (68 Begriffsbestimmungen) war EINE Einheit mit 10.818
#     Zeichen, die Buchstaben darin hiessen 'Art. 3 lit. a' — dreimal.
#   * roemische Ziffern: 'i)' wurde als Buchstabe i gelesen ('Art. 13 Abs. 3
#     lit. i'), 'ii)' gar nicht.
#   * mehrere Buchstabenlisten in einem Absatz (Art. 43 Abs. 1): zweimal 'lit. a'.
#   * Abschnitte in Anhaengen (Anhang VIII A/B/C): dreimal 'Nr. 1'.
#   * deutsche Gesetze setzen '1.' und 'a)' ans ZEILENENDE ('gelten 1.\n').
# Jede Stufe traegt jetzt ihre Kennung; eine Kennung ist eindeutig, weil der
# Pfad eindeutig ist — und NORM_UNIT_IDS_UNIQUE haelt das fest.

_ROEMISCH = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
             "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"]


def _marken(seg: str, *, deutsch: bool, anhang: bool) -> list[tuple[int, str, str]]:
    """Alle Gliederungsmarken eines Ausschnitts: (Position, Art, Kennung).

    EU-Texte setzen Marken auf eine eigene Zeile ('\\n1.\\n', '\\nc)\\n').
    Deutsche Gesetze setzen sie ans Zeilenende ('gelten 1.\\n', 'die a)\\n').
    In Anhaengen stehen Nummern auch mit Titel ('1.   Schengener ...') und
    mehrstufig ('3.1.').
    """
    vor = r"(?:(?<=\n)|(?<=[ :]))" if deutsch else r"(?<=\n)"
    if anhang:
        nr = re.compile(vor + r"(\d+(?:\.\d+)*)\.(?:\n|[ \t]{2,}|\t)")
    else:
        nr = re.compile(vor + r"(\d+)\.\n")
    alpha = re.compile(vor + r"([a-z]{1,5})\)\n")
    out = [(m.start(1), "nr", m.group(1)) for m in nr.finditer(seg)]
    out += [(m.start(1), "alpha", m.group(1)) for m in alpha.finditer(seg)
            if len(m.group(1)) == 1 or m.group(1) in _ROEMISCH]
    return sorted(out)


def _gliedern(marken: list[tuple[int, str, str]], *, fortsetzung_erlaubt: bool = False) -> list[dict]:
    """Ordnet Marken zu einem Baum: Nummer > Buchstabe > Ziffer.

    Eine Marke zaehlt nur, wenn sie die Folge fortsetzt (1, 2, 3 / a, b, c /
    i, ii, iii) oder eine neue Folge beginnt (1 / a / i). Mehrdeutig sind 'i)'
    und 'v)': Buchstabe, wenn die Buchstabenfolge genau dort steht und nicht
    'ii)' folgt; sonst roemische Ziffer unter dem laufenden Buchstaben.
    """
    items: list[dict] = []
    nr_next = "1"
    cur_nr = None
    letter_next = None
    letter_lists: dict = {}
    cur_letter = None
    roman_next = None
    for i, (pos, art, lab) in enumerate(marken):
        nach = marken[i + 1][2] if i + 1 < len(marken) else None
        if art == "nr":
            # T-15 (A-W2): in einem Anhang darf eine Liste mit einer hoeheren Zahl
            # beginnen, wenn die naechste Nummer sie fortsetzt - Anhang I Abschn. B
            # zaehlt 13 bis 20 weiter. Nur in Anhaengen: in deutschen Gesetzen haette
            # dieselbe Regel die Begriffsbestimmungen des § 2 BSIG umgeschnitten, deren
            # erste Nummer der Extraktor nicht erkennt (Befund A-W10, Sektorstapel).
            folge = next((m[2] for m in marken[i + 1:] if m[1] == "nr"), None)
            fortsetzung = (fortsetzung_erlaubt and cur_nr is None and "." not in lab and lab.isdigit()
                           and folge == str(int(lab) + 1))
            if "." in lab or lab == nr_next or (lab == "1" and cur_nr is None) or fortsetzung:
                cur_nr = {"pos": pos, "ebene": "nr", "kennung": lab, "eltern": None}
                items.append(cur_nr)
                if "." not in lab:
                    nr_next = str(int(lab) + 1)
                letter_next, cur_letter, roman_next = None, None, None
            continue
        # alpha
        if roman_next and lab == roman_next and cur_letter is not None:
            roman = True
        elif letter_next and lab == letter_next and not (lab == "i" and nach == "ii"):
            roman = False
        elif lab == "i" and cur_letter is not None:
            roman = True
        elif lab == "a":
            roman = False
        elif len(lab) == 1 and letter_next is None and lab not in ("i", "v", "x"):
            roman = False  # Liste beginnt nicht mit a — als Buchstabe fuehren, Pruefung meldet es
        else:
            continue  # passt in keine Folge: keine Marke, sondern Text
        if roman:
            it = {"pos": pos, "ebene": "ziffer", "kennung": lab, "eltern": cur_letter}
            items.append(it)
            idx = _ROEMISCH.index(lab)
            roman_next = _ROEMISCH[idx + 1] if idx + 1 < len(_ROEMISCH) else None
        else:
            eltern_key = id(cur_nr) if cur_nr is not None else None
            if lab == "a" or letter_next is None:
                letter_lists[eltern_key] = letter_lists.get(eltern_key, 0) + 1
            cur_letter = {"pos": pos, "ebene": "lit", "kennung": lab, "eltern": cur_nr,
                          "liste": letter_lists.get(eltern_key, 1), "eltern_key": eltern_key}
            items.append(cur_letter)
            letter_next = chr(ord(lab) + 1) if len(lab) == 1 else None
            roman_next = None
    return items


def _einzelfolgen(items: list[dict]) -> set[int]:
    """Positionen von Marken, deren Folge nur aus einem Glied besteht.

    Eine Liste mit nur '1.' oder nur 'a)' ist fast immer eine Verweisung am
    Zeilenende ('nach Absatz 1.\\n'), keine Gliederung.
    """
    from collections import defaultdict
    gruppen = defaultdict(list)
    for it in items:
        if it["ebene"] == "nr" and "." not in it["kennung"]:
            gruppen[("nr",)].append(it)
        elif it["ebene"] == "lit":
            gruppen[("lit", it["eltern_key"], it["liste"])].append(it)
        elif it["ebene"] == "ziffer":
            gruppen[("ziffer", id(it["eltern"]))].append(it)
    return {g[0]["pos"] for g in gruppen.values() if len(g) == 1}


def _abschnitte(norm: str, art: dict) -> list[dict]:
    """Abschnitte eines Anhangs ('Abschnitt A — ...', 'Abschnitt 1')."""
    body = norm[art["start"]:art["end"]]
    marks = [(m.group(1), m.start() + 1)
             for m in re.finditer(r"\n(?:Abschnitt|ABSCHNITT) ([A-Z0-9]+)\b[^\n]*\n", body)]
    if not marks:
        return [{"abschnitt": None, "start": art["start"], "end": art["end"]}]
    out = [{"abschnitt": None, "start": art["start"], "end": art["start"] + marks[0][1]}]
    for i, (lab, rel) in enumerate(marks):
        e = art["start"] + marks[i + 1][1] if i + 1 < len(marks) else art["end"]
        out.append({"abschnitt": lab, "start": art["start"] + rel, "end": e})
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
        return _unnummerierte_absaetze(norm, body_start + skip, art["end"])
    out = []
    for i, (num, rel) in enumerate(marks):
        s = body_start + rel + 1
        e = body_start + marks[i + 1][1] + 1 if i + 1 < len(marks) else art["end"]
        out.append({"absatz": num, "start": s, "end": e})
    return out


_LISTENMARKE = re.compile(r"\n(?:[a-z]{1,5}\)|\d+(?:\.\d+)*\.)\n")


def _unnummerierte_absaetze(norm: str, start: int, end: int) -> list[dict]:
    """Absaetze eines Artikels ohne Absatznummern.

    T-15 (A-W1, Review 08/10). Art. 113 AI Act hat drei Absaetze ohne Nummer; der
    Extraktor fuehrte sie als eine Einheit 'Art. 113' und die Buchstaben als
    'Art. 113 lit. a'. Das Gesetz selbst zitiert 'Artikel 113 Absatz 3 Buchstabe a'
    (VO (EU) 2026/1744 Art. 1 Nr. 40 und Art. 111 Abs. 2 n.F.). Deshalb: Bloecke vor
    der ersten Listenmarke, getrennt durch eine Leerzeile, sind Absaetze 1..n; die
    Liste gehoert zum letzten. Ein einziger Block bleibt Absatz '-' (Kennung ohne Abs.).
    Beginnt ein Block mit '„', ist er zitierter Text einer Aenderungsanweisung
    (Art. 102-110) und kein Absatz.
    """
    seg = norm[start:end]
    liste = _LISTENMARKE.search(seg)
    kopf = seg[:liste.start()] if liste else seg
    bloecke = []
    pos = 0
    for teil in re.split(r"(\n[ \t]*\n)", kopf):
        if teil.strip() and not re.fullmatch(r"\n[ \t]*\n", teil):
            bloecke.append(pos + (len(teil) - len(teil.lstrip())))
        pos += len(teil)
    texte = [kopf[b:].lstrip() for b in bloecke]
    if len(bloecke) < 2 or any(t.startswith("„") for t in texte):
        return [{"absatz": "-", "start": start, "end": end}]
    out = []
    for i, b in enumerate(bloecke):
        e = start + bloecke[i + 1] if i + 1 < len(bloecke) else end
        out.append({"absatz": str(i + 1), "start": start + b, "end": e})
    return out


def split_saetze(norm: str, start: int, end: int) -> list[dict]:
    """Saetze einer Einheit. Konservativ: trennt nur an '. ' und niemals hinter
    einer bekannten Abkuerzung.

    Bleibt bewusst unveraendert (T-14.3): das Feld `saetze` aller Pflichtenraeume
    ist mit dieser Zaehlung erzeugt. Sie zaehlt eine Fundstelle am Satzende zu
    kurz ('gemaess Artikel 72. Haben …' ist fuer sie EIN Satz). Wo es auf die
    Saetze ankommt, schneidet `satz_spannen` — mit Offset und mit dieser Regel.
    """
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


# ── Satzebene (T-14.3) ──────────────────────────────────────────────────────
#
# PO-Festlegung P-2 = b (23.09.2026): nur Absaetze, die mehr als eine Pflicht
# tragen, werden in Saetze geschnitten; die Liste fuehrt der PO in
# docs/coverage/entscheide/satzebene.yaml. Anlass war Art. 26 Abs. 5 — vier Pflichten, ein
# Befund, und die vierte ('setzen die Verwendung ... aus') war nirgends
# abgebildet, weil der Sammelbefund 'teilabdeckung' sie verdeckte.

# Vor einer Zahl mit Punkt: dann ist die Zahl eine Fundstelle oder ein Jahr, und
# der Punkt beendet den Satz ('gemaess Artikel 72. Haben …', '… bis zum
# 2. August 2030.'). Sonst ist sie eine Ordnungszahl ('vor dem 2. August 2026').
_FUNDSTELLE = {"Artikel", "Artikels", "Absatz", "Absatzes", "Unterabsatz", "Nummer",
               "Satz", "Anhang", "Anhangs", "Buchstabe"}
_MONATE = {"Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
           "September", "Oktober", "November", "Dezember"}
_ABBREV_SET = set(ABBREV)


def _ist_satzende(seg: str, anfang: int, punkt: int) -> bool:
    """Endet bei `punkt` (Index des '.') der Satz, der bei `anfang` beginnt?"""
    tokens = seg[anfang:punkt].split()
    if not tokens:
        return False
    tail = tokens[-1]
    if tail.rstrip(".") in _ABBREV_SET or " ".join(tokens[-2:]).rstrip(".") in _ABBREV_SET:
        return False
    rest = seg[punkt + 1:].lstrip()
    if re.fullmatch(r"\d+[a-z]?", tail):
        vorher = tokens[-2] if len(tokens) > 1 else ""
        if not (vorher in _FUNDSTELLE or vorher in _MONATE or not rest):
            return False
    # Ein Satz beginnt gross, mit Anfuehrungszeichen oder Klammer — sonst ist der
    # Punkt Teil einer Abkuerzung, die ABBREV nicht kennt.
    return not rest or rest[0].isupper() or rest[0] in "„\"(«"


def satz_spannen(norm: str, start: int, end: int) -> list[tuple[int, int]]:
    """Saetze eines Ausschnitts als (start, ende) in der Quelle.

    Anders als `split_saetze` mit echten Offsets: jeder Satz wird eine eigene
    Einheit und muss sich an seiner Stelle in der Quelle wortgleich pruefen
    lassen (LEGAL_QUOTES_VERBATIM).
    """
    seg = norm[start:end]
    spannen: list[tuple[int, int]] = []
    anfang = len(seg) - len(seg.lstrip())
    for m in re.finditer(r"\.(?=\s|$)", seg):
        p = m.start()
        if p < anfang or not _ist_satzende(seg, anfang, p):
            continue
        spannen.append((start + anfang, start + p + 1))
        rest = seg[p + 1:]
        anfang = p + 1 + (len(rest) - len(rest.lstrip()))
    if seg[anfang:].strip():
        ende = len(seg.rstrip())
        spannen.append((start + anfang, start + ende))
    return spannen


_ABSATZMARKE = re.compile(r"\(\d+[a-z]?\)\s+")
_UNTERABSATZ = re.compile(r"\n[ \t]*\n\s*")


def auf_satzebene(norm: str, units: list[dict], ids: list[str]) -> tuple[list[dict], dict]:
    """Ersetzt jede gelistete Einheit durch ihre Saetze.

    Kennung: '<Einheit> Satz N', bei mehr als einem Unterabsatz '<Einheit>
    UAbs. U Satz N' — so wird im Unionsrecht zitiert, und 'Art. 26 Abs. 5
    Satz 6' gibt es nicht. Unterabsaetze erkennt der Schnitt an der Leerzeile,
    mit der die Quelle sie trennt. Die Absatzmarke '(5)' gehoert zu keinem Satz.

    Eine gelistete Einheit, die es nicht gibt, die Unterglieder hat oder die in
    weniger als zwei Saetze zerfaellt, ist ein Fehler der Liste und bricht ab:
    eine PO-Festlegung, die still nicht greift, ist keine.
    """
    gesucht = set(ids)
    vorhanden = {u["id"] for u in units}
    fehlt = sorted(gesucht - vorhanden)
    if fehlt:
        raise ValueError(f"Satzebene: Einheit(en) nicht in der Quelle: {', '.join(fehlt)}")

    out: list[dict] = []
    zuordnung: dict[str, list[str]] = {}
    for u in units:
        if u["id"] not in gesucht:
            out.append(u)
            continue
        s, e = u["offset"], u["offset"] + u["laenge"]
        kinder = [x["id"] for x in units if x is not u and s < x["offset"] < e]
        if kinder:
            raise ValueError(f"Satzebene: {u['id']} hat Unterglieder ({', '.join(kinder[:3])}) "
                             f"— geschnitten wird nur, was keine Gliederung mehr hat")
        seg = norm[s:e]
        m = _ABSATZMARKE.match(seg)
        koerper = s + (m.end() if m else 0)
        grenzen = [koerper] + [s + g.end() for g in _UNTERABSATZ.finditer(seg)
                               if s + g.end() > koerper and s + g.end() < e]
        uabs = [(a, grenzen[i + 1] if i + 1 < len(grenzen) else e)
                for i, a in enumerate(grenzen) if norm[a:(grenzen[i + 1] if i + 1 < len(grenzen) else e)].strip()]
        basis, nf = (u["id"][:-5], " n.F.") if u["id"].endswith(" n.F.") else (u["id"], "")
        neu = []
        for ui, (ua, ue) in enumerate(uabs, start=1):
            for si, (ss, se) in enumerate(satz_spannen(norm, ua, ue), start=1):
                kennung = basis + (f" UAbs. {ui}" if len(uabs) > 1 else "") + f" Satz {si}" + nf
                text = re.sub(r"[\t ]*\n[\t \n]*", " ", norm[ss:se]).strip()
                neu.append({**u, "uid": f"{kennung}@{ss}", "id": kennung,
                            "unterabsatz": str(ui) if len(uabs) > 1 else u.get("unterabsatz"),
                            "satz": str(si), "offset": ss, "laenge": se - ss, "text": text,
                            "saetze": [{"nr": 1, "text": text}]})
        if len(neu) < 2:
            raise ValueError(f"Satzebene: {u['id']} ergibt {len(neu)} Satz — nichts zu schneiden")
        zuordnung[u["uid"]] = [x["uid"] for x in neu]
        out.extend(neu)
    return out, zuordnung


def units_for(norm: str, art: dict) -> list[dict]:
    """Einheiten eines Artikels, Paragraphen oder Anhangs.

    Leere Ausschnitte werden verworfen. Sie entstehen, wo eine Ueberschrift
    ohne Text folgt — ein Artefakt der Gliederung, kein Normtext. Eine Einheit
    ohne Beleg ist nicht pruefbar, und was nicht pruefbar ist, hat in einem
    Pflichtenraum nichts verloren.

    Jede Einheit reicht von ihrer Marke bis zur naechsten Marke gleich welcher
    Ebene. Hat ein Glied Unterglieder, ist seine Einheit der Kopf davor — wie
    bisher der Absatzkopf vor den Buchstaben.
    """
    anhang = art.get("ist_anhang", False)
    deutsch = art.get("ist_paragraph", False)
    if anhang:
        behaelter = [{"absatz": None, **b} for b in _abschnitte(norm, art)]
        # der Anhangkopf (Ueberschrift, Titel) ist kein Normtext einer Nummer
        kopf = behaelter[0]
        lines = norm[kopf["start"]:kopf["end"]].split("\n")
        skip = len("\n".join(lines[:3])) if len(lines) > 2 else 0
        kopf["start"] = min(kopf["start"] + skip, kopf["end"])
    else:
        behaelter = [{"abschnitt": None, **b} for b in split_absaetze(norm, art)]

    out = []
    for b in behaelter:
        seg = norm[b["start"]:b["end"]]
        marken = _marken(seg, deutsch=deutsch, anhang=anhang)
        items = _gliedern(marken, fortsetzung_erlaubt=anhang)
        weg = _einzelfolgen(items)
        if weg:
            marken = [m for m in marken if m[0] not in weg]
            items = _gliedern(marken, fortsetzung_erlaubt=anhang)
        # Wie viele Buchstabenlisten hat jedes Elternglied? Nur bei mehr als
        # einer bekommt die Kennung ein 'UAbs.'.
        listen: dict = {}
        for it in items:
            if it["ebene"] == "lit":
                listen[it["eltern_key"]] = max(listen.get(it["eltern_key"], 0), it["liste"])
        grenzen = [it["pos"] for it in items] + [len(seg)]
        start_kopf = 0
        ende_kopf = grenzen[0]
        if seg[start_kopf:ende_kopf].strip():
            out.append(_unit(norm, art, b, {}, b["start"] + start_kopf, b["start"] + ende_kopf))
        # Wie viele Unterabsaetze stehen im Elternglied schon vor der Liste? Der Kopf
        # des Absatzes kann mehrere tragen; jeder Folgeabsatz zaehlt weiter.
        uabs_bisher: dict = {None: max(1, _bloecke(seg[:grenzen[0]]))}
        for k, it in enumerate(items):
            if it["ebene"] == "nr":
                kinder = [x for x in items[k + 1:] if x.get("eltern") is it]
                bis = kinder[0]["pos"] if kinder else grenzen[k + 1]
                uabs_bisher[id(it)] = max(1, _bloecke(seg[it["pos"]:bis]))
        for k, it in enumerate(items):
            pfad = _pfad(it, listen)
            s = b["start"] + it["pos"]
            e = b["start"] + grenzen[k + 1]
            nach = items[k + 1] if k + 1 < len(items) else None
            # Deutsche Gesetze zaehlen den Text hinter einer Aufzaehlung als Satz des
            # Absatzes, nicht als Unterabsatz - dort bleibt der Schnitt, wie er war.
            folge = _folgeabsaetze(norm, s, e) if not deutsch and _listenende(it, nach) else []
            out.append(_unit(norm, art, b, pfad, s, folge[0] if folge else e))
            for j, fs in enumerate(folge):
                fe = folge[j + 1] if j + 1 < len(folge) else e
                pfad_u, schluessel = _uabs_pfad(it)
                uabs_bisher[schluessel] = uabs_bisher.get(schluessel, 1) + 1
                pfad_u["unterabsatz"] = str(uabs_bisher[schluessel])
                out.append(_unit(norm, art, b, pfad_u, fs, fe))
    return [u for u in out if u["text"].strip()]


def _listenende(it: dict, nach: dict | None) -> bool:
    """Endet mit diesem Glied eine Liste, ohne dass ein Geschwister folgt?

    Folgt ein Geschwister (naechster Buchstabe derselben Liste, naechste Nummer,
    naechste Ziffer) oder ein Unterglied, gehoert jeder Absatz im Glied zum Glied
    selbst (Anhang III Nr. 1 lit. a: 'Dazu gehoeren nicht …'). Nur hinter dem letzten
    Glied beginnt der naechste Unterabsatz des Elternglieds.
    """
    if nach is None:
        return True
    if nach.get("eltern") is it:
        return False
    kette = []
    x = it
    while x is not None:
        kette.append(x)
        x = x.get("eltern")
    for g in kette:
        if nach["ebene"] == g["ebene"] and nach.get("eltern") is g.get("eltern"):
            if g["ebene"] == "lit" and nach.get("liste") != g.get("liste"):
                return True  # eine neue Liste beginnt: davor steht ihr Einleitungssatz
            return False
    return True


def _folgeabsaetze(norm: str, s: int, e: int) -> list[int]:
    """Startpositionen von Unterabsaetzen, die hinter dem letzten Glied einer Liste stehen.

    T-15 Teil 2 (A-W11, Review 10). Der Text nach einer Aufzaehlung ist der naechste
    Unterabsatz des Elternglieds, nicht mehr Teil des letzten Buchstabens: 'Ungeachtet
    des Unterabsatzes 1 gilt ein in Anhang III aufgefuehrtes KI-System immer dann als
    hochriskant, wenn …' stand bis hierhin in Art. 6 Abs. 3 lit. d. Erkannt an der
    Leerzeile, mit der die Quelle Unterabsaetze trennt: ein Block, der gross beginnt,
    hinter einem Block, der mit Punkt oder Doppelpunkt endet. Zitierter Text ('„(3) …')
    gehoert zur Aenderungsanweisung davor und beginnt keinen Unterabsatz.
    """
    seg = norm[s:e]
    bloecke, pos = [], 0
    for teil in re.split(r"(\n[ \t]*\n)", seg):
        if teil.strip() and not re.fullmatch(r"\n[ \t]*\n", teil):
            t = teil.strip()
            if not re.fullmatch(r"\(?[a-z]{1,5}\)|\d+(?:\.\d+)*\.|\t*", t):
                bloecke.append((pos + len(teil) - len(teil.lstrip()), t))
        pos += len(teil)
    starts = []
    for i in range(1, len(bloecke)):
        vorher, jetzt = bloecke[i - 1][1], bloecke[i][1]
        if starts or (vorher.rstrip().endswith((".", ":")) and re.match(r"[A-ZÄÖÜ]", jetzt)):
            starts.append(s + bloecke[i][0])
    return starts


def _bloecke(text: str) -> int:
    """Wie viele Unterabsaetze ein Ausschnitt traegt: Bloecke zwischen Leerzeilen,
    ohne Gliederungsmarken und ohne die Absatzmarke '(n)'."""
    n = 0
    for teil in re.split(r"\n[ \t]*\n", text):
        t = re.sub(r"^\(\d+[a-z]?\)\s*", "", teil.strip())
        if t and not re.fullmatch(r"\(?[a-z]{1,5}\)|\d+(?:\.\d+)*\.|\t*", t):
            n += 1
    return n


def _uabs_pfad(it: dict) -> tuple[dict, object]:
    """Pfad eines Unterabsatzes hinter der Liste, zu der `it` gehoert, und der Schluessel
    seines Elternglieds (Nummer oder Absatz). Gezaehlt wird im Aufrufer: die Unterabsaetze
    des Kopfes zuerst, dann jeder Folgeabsatz - Art. 43 Abs. 1 hat einen Kopf, eine Liste,
    UAbs. 2 mit der zweiten Liste, dann UAbs. 3."""
    x = it
    while x.get("ebene") != "lit" and x.get("eltern") is not None:
        x = x["eltern"]
    if x.get("ebene") == "nr":  # Liste von Nummern ohne Buchstaben: Unterabsatz am Absatz
        return {"nummer": None, "unterabsatz": None, "buchstabe": None, "ziffer": None}, None
    eltern = x.get("eltern")
    return ({"nummer": eltern["kennung"] if eltern else None, "unterabsatz": None,
             "buchstabe": None, "ziffer": None}, id(eltern) if eltern else None)


def _pfad(it: dict, listen: dict) -> dict:
    """Nummer, Unterabsatz, Buchstabe, Ziffer eines Glieds."""
    pfad = {"nummer": None, "unterabsatz": None, "buchstabe": None, "ziffer": None}
    kette = []
    x = it
    while x is not None:
        kette.append(x)
        x = x.get("eltern")
    for g in kette:
        if g["ebene"] == "nr":
            pfad["nummer"] = g["kennung"]
        elif g["ebene"] == "lit":
            pfad["buchstabe"] = g["kennung"]
            if listen.get(g["eltern_key"], 1) > 1:
                pfad["unterabsatz"] = str(g["liste"])
        elif g["ebene"] == "ziffer":
            pfad["ziffer"] = g["kennung"]
    return pfad


def _unit(norm, art, behaelter, pfad, start, end) -> dict:
    text = norm[start:end]
    ist_anhang = art.get("ist_anhang", False)
    eigenname = ist_anhang or art.get("ist_paragraph", False)
    kopf = art["artikel"] if eigenname else f"Art. {art['artikel']}"
    absatz = behaelter.get("absatz")
    abschnitt = behaelter.get("abschnitt")
    kennung = kopf
    if abschnitt:
        kennung += f" Abschn. {abschnitt}"
    if absatz and absatz != "-":
        kennung += f" Abs. {absatz}"
    if pfad.get("nummer"):
        kennung += f" Nr. {pfad['nummer']}"
    if pfad.get("unterabsatz"):
        kennung += f" UAbs. {pfad['unterabsatz']}"
    if pfad.get("buchstabe"):
        kennung += f" lit. {pfad['buchstabe']}"
    if pfad.get("ziffer"):
        kennung += f" Ziff. {pfad['ziffer']}"
    return {
        # Die lesbare Kennung ist seit T-14 eindeutig (NORM_UNIT_IDS_UNIQUE).
        # Zusammengefuehrt wird trotzdem auf uid = Kennung@Offset: der Offset ist
        # innerhalb einer gehashten Quelle stabil, die Kennung haengt am
        # Extraktor — und der hat sich schon zweimal geaendert.
        "uid": f"{kennung}@{start}",
        "id": kennung,
        "artikel": art["artikel"],
        "artikel_titel": art["titel"],
        "abschnitt": abschnitt,
        "absatz": absatz,
        "nummer": pfad.get("nummer"),
        "unterabsatz": pfad.get("unterabsatz"),
        "buchstabe": pfad.get("buchstabe"),
        "ziffer": pfad.get("ziffer"),
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
