#!/usr/bin/env python3
"""extract_omnibus_units.py — schneidet einen Aenderungsrechtsakt in Einheiten.

T-14.2 (23.09.2026). Der Pflichtenraum des AI Act ist die Grundfassung
2024/1689. Was der Omnibus 2026/1744 neu fasst, einfuegt oder streicht, hatte
bis hierhin keine eigene Zeile — der Nachtlauf vermerkte es im Feld 'omnibus'
einer Grundfassungs-Zeile, und dort war es einmal falsch (Art. 4). Eine
Aenderung, die nur als Kommentar existiert, ist dieselbe Behauptung ohne
Gegenstand, gegen die dieses Repo gebaut ist.

Ein Aenderungsrechtsakt hat eine andere Gestalt als ein Stammgesetz:

  Artikel 1  →  Aenderungsanweisung 'N.'  →  (Unteranweisung 'a)')  →  „neuer Text“

Daraus zwei Arten von Einheiten:

  Anweisung   'Omnibus Art. 1 Nr. 12 lit. a' — der Satz, der sagt, WAS geschieht
              ('Absatz 2 erhaelt folgende Fassung:'), mit ziel und aenderung
  Neuer Text  'Art. 25 Abs. 2 lit. a n.F.' — der eingefuegte oder neu gefasste
              Normtext selbst, zerlegt wie ein Stammgesetz (Absatz, Buchstabe,
              Ziffer), mit Verweis auf seine Anweisung

'n.F.' (neue Fassung) steht an JEDER Einheit dieses Raums, auch an eingefuegten
Normen: die Kennung sagt damit immer, aus welcher Fassung ein Zitat stammt.

Die Anweisungsnummern werden nur akzeptiert, wenn sie ausserhalb der
Anfuehrungszeichen stehen und die Folge 1, 2, 3 … fortsetzen — sonst waere
jedes '(2)' im neuen Text eine Anweisung.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_norm_units import _gliedern, load, split_saetze  # noqa: E402

_VERB = [
    ("gestrichen", "gestrichen"),
    ("erhält folgende Fassung", "neu_gefasst"),
    ("erhalten folgende Fassung", "neu_gefasst"),
    ("eingefügt", "eingefuegt"),
    ("angefügt", "angefuegt"),
    ("hinzugefügt", "angefuegt"),
    ("wie folgt geändert", "geaendert"),
]


def _zitate(text: str, start: int, end: int) -> list[tuple[int, int]]:
    """Aeussere „…“-Spannen zwischen start und end (Inhalt ohne Zeichen)."""
    out, tiefe, auf = [], 0, None
    for m in re.finditer(r"[„“]", text[start:end]):
        p = start + m.start()
        if m.group(0) == "„":
            if tiefe == 0:
                auf = p + 1
            tiefe += 1
        else:
            tiefe -= 1
            if tiefe == 0 and auf is not None:
                out.append((auf, p))
    return out


def _in(p: int, spannen: list[tuple[int, int]]) -> bool:
    return any(a - 1 <= p <= b for a, b in spannen)


def _artikel_bereiche(norm: str) -> list[dict]:
    """Artikel 1..n des verfuegenden Teils (nach 'HABEN FOLGENDE VERORDNUNG ERLASSEN')."""
    ab = norm.find("HABEN FOLGENDE VERORDNUNG ERLASSEN")
    ab = 0 if ab < 0 else ab
    hits, erwartet = [], 1
    for m in re.finditer(r"\nArtikel (\d+)\n", norm[ab:]):
        if int(m.group(1)) == erwartet:
            hits.append((m.group(1), ab + m.start() + 1))
            erwartet += 1
    ende = norm.find("\nGeschehen zu ", ab)
    ende = len(norm) if ende < 0 else ende
    out = []
    for i, (num, s) in enumerate(hits):
        e = hits[i + 1][1] - 1 if i + 1 < len(hits) else ende
        titel = norm[s:e].split("\n")[1].strip() if norm[s:e].count("\n") else ""
        out.append({"artikel": num, "titel": titel, "start": s, "end": e})
    return out


def _anweisungen(norm: str, art: dict) -> list[dict]:
    """Anweisungen 'N.' / '(N)' eines Aenderungsartikels, ausserhalb von Zitaten."""
    zit = _zitate(norm, art["start"], art["end"])
    marken, erwartet = [], 1
    for m in re.finditer(r"\n(?:(\d+)\.|\((\d+)\))(?=\s)", norm[art["start"]:art["end"]]):
        p = art["start"] + m.start() + 1
        n = int(m.group(1) or m.group(2))
        if n == erwartet and not _in(p, zit):
            marken.append((n, p))
            erwartet += 1
    out = []
    for i, (n, p) in enumerate(marken):
        e = marken[i + 1][1] - 1 if i + 1 < len(marken) else art["end"]
        out.append({"nr": n, "start": p, "end": e, "zitate": [z for z in zit if p <= z[0] < e]})
    return out


def _unteranweisungen(norm: str, anw: dict) -> list[dict]:
    """'a) Absatz 2 erhaelt folgende Fassung:' — Buchstaben ausserhalb von Zitaten."""
    marken, erwartet = [], "a"
    for m in re.finditer(r"\n([a-z])\)\s", norm[anw["start"]:anw["end"]]):
        p = anw["start"] + m.start() + 1
        if m.group(1) == erwartet and not _in(p, anw["zitate"]):
            marken.append((m.group(1), p))
            erwartet = chr(ord(erwartet) + 1)
    out = []
    for i, (lit, p) in enumerate(marken):
        e = marken[i + 1][1] - 1 if i + 1 < len(marken) else anw["end"]
        out.append({"lit": lit, "start": p, "end": e,
                    "zitate": [z for z in anw["zitate"] if p <= z[0] < e]})
    return out


def _satz(norm: str, s: int, e: int, zitate) -> tuple[int, int]:
    """Der Anweisungssatz: vom Marker bis zum ersten Zitat oder Ende."""
    ende = min([z[0] - 1 for z in zitate if z[0] > s] + [e])
    return s, ende


def _ziel(anweisung: str, erbe: dict) -> dict:
    """Zielnorm aus dem Anweisungstext.

    Geerbt wird nur von der OBERANWEISUNG und nur, was die Unteranweisung nicht
    selbst nennt; nennt sie eine Stufe, faellt alles darunter weg. 'Einleitung'
    und 'Überschrift' werden nie geerbt.
    """
    stufen = ["anhang_artikel", "abschnitt", "absatz", "nummer", "unterabsatz", "buchstabe"]
    z = {k: v for k, v in erbe.items() if k != "teil"}

    def setze(stufe, schluessel, wert):
        for tiefer in stufen[stufen.index(stufe) + 1:]:
            z.pop(tiefer, None)
        if stufe == "anhang_artikel":
            z.pop("anhang", None)
            z.pop("artikel", None)
        z[schluessel] = wert

    for stufe, schluessel, muster in (
            ("anhang_artikel", "anhang", r"Anhang ([IVXLC]+)\b"),
            ("anhang_artikel", "artikel", r"Artikel (\d+[a-z]?)\b"),
            ("abschnitt", "abschnitt", r"Abschnitt ([A-Z])\b"),
            ("absatz", "absatz", r"Absatz (\d+[a-z]?)\b"),
            ("nummer", "nummer", r"Nummern? (\d+[a-z]?(?: und \d+[a-z]?)?)\b"),
            ("unterabsatz", "unterabsatz", r"Unterabsatz (\d+)\b"),
            ("buchstabe", "buchstabe", r"Buchstaben? ([a-z]{1,2})\b")):
        m = re.search(muster, anweisung)
        if m:
            setze(stufe, schluessel, m.group(1))
    if "Einleitung" in anweisung:
        z["teil"] = "Einleitung"
    if "Überschrift" in anweisung:
        z["teil"] = "Überschrift"
    return z

def _kennung(z: dict) -> str:
    if z.get("anhang"):
        k = f"Anhang {z['anhang']}"
    elif z.get("artikel"):
        k = f"Art. {z['artikel']}"
    else:
        return ""
    for feld, praefix in (("abschnitt", "Abschn."), ("absatz", "Abs."), ("nummer", "Nr."),
                          ("unterabsatz", "UAbs."), ("buchstabe", "lit."), ("ziffer", "Ziff.")):
        if z.get(feld):
            k += f" {praefix} {z[feld]}"
    if z.get("teil"):
        k += f" {z['teil']}"
    return k


def _aenderung(anweisung: str) -> str:
    if "gestrichen" in anweisung:
        return "gestrichen"
    if re.search(r"erh(?:ä|a)lt(?:en)?\b[^.:]*folgende Fassung", anweisung):
        return "neu_gefasst"
    for wort, art in _VERB:
        if wort in anweisung:
            return art
    return "unbestimmt"

def _einheit(norm, s, e, kennung, meta) -> dict:
    text = norm[s:e]
    return {
        "uid": f"{kennung}@{s}", "id": kennung,
        "artikel": meta.get("artikel_ziel") or "", "artikel_titel": meta.get("titel") or "",
        "abschnitt": None, "absatz": None, "nummer": None, "unterabsatz": None,
        "buchstabe": None, "ziffer": None,
        "anweisung": meta["anweisung"], "ziel": meta.get("ziel"), "aenderung": meta.get("aenderung"),
        "offset": s, "laenge": e - s,
        "text": re.sub(r"[\t ]*\n[\t \n]*", " ", text).strip(),
        "saetze": split_saetze(norm, s, e),
    }


def _neuer_text(norm, s, e, z: dict, meta) -> list[dict]:
    """Zerlegt einen zitierten neuen Normtext wie ein Stammgesetz."""
    block = norm[s:e]
    out = []
    # 0) ganzer Anhang ('Anhang XIV\\nVerzeichnis …\\n1. Einleitung …')
    m = re.match(r"Anhang ([IVXLC]+)\n", block)
    if m:
        za = {"anhang": m.group(1)}
        marken = [(n.group(1), n.start()) for n in re.finditer(r"\n(\d+)\.\s", block)]
        erste = marken[0][1] if marken else len(block)
        out.append(_einheit(norm, s, s + erste, _kennung(za) + " n.F.", {**meta, "ziel": _kennung(za)}))
        for i, (nr, rel) in enumerate(marken):
            n_e = s + marken[i + 1][1] if i + 1 < len(marken) else e
            zz = {**za, "nummer": nr}
            out.append(_einheit(norm, s + rel + 1, n_e, _kennung(zz) + " n.F.", {**meta, "ziel": _kennung(zz)}))
        return out
    # 1) ganze Artikel ('Artikel 4a\\nTitel\\n(1) …'), auch mehrere hintereinander
    arts = [(m.group(1), m.start()) for m in re.finditer(r"(?:^|\n)Artikel (\d+[a-z]?)\n", block)]
    if arts and arts[0][1] <= 1:
        for i, (num, rel) in enumerate(arts):
            a_s = s + rel + (1 if block[rel] == "\n" else 0)
            a_e = s + arts[i + 1][1] if i + 1 < len(arts) else e
            out += _absaetze(norm, a_s, a_e, {"artikel": num}, meta, kopf=True)
        return out
    # 2) Absaetze '(2) …', '(1a) …'
    if re.match(r"\(\d+[a-z]?\)", block):
        return _absaetze(norm, s, e, z, meta, kopf=False)
    # 3) Buchstaben 'g) …', 'ba) …'
    if re.match(r"[a-z]{1,2}\)", block):
        return _buchstaben(norm, s, e, z, meta)
    # 4) Nummern '14. …', '14a. …' (Begriffsbestimmungen)
    if re.match(r"\d+[a-z]?\.\s", block):
        marken = [(m.group(1), m.start()) for m in re.finditer(r"(?:^|\n)(\d+[a-z]?)\.\s", block)]
        for i, (nr, rel) in enumerate(marken):
            n_s = s + rel + (1 if block[rel] == "\n" else 0)
            n_e = s + marken[i + 1][1] if i + 1 < len(marken) else e
            zz = {**z, "nummer": nr}
            out.append(_einheit(norm, n_s, n_e, _kennung(zz) + " n.F.", {**meta, "ziel": _kennung(zz)}))
        return out
    # 5) sonst: eine Einheit fuer das Ziel
    k = _kennung(z) or f"{meta['anweisung']} Text"
    if meta.get("aenderung") in ("angefuegt", "eingefuegt"):
        k += " (angefügt)" if meta["aenderung"] == "angefuegt" else " (eingefügt)"
    return [_einheit(norm, s, e, k + " n.F.", {**meta, "ziel": _kennung(z) or None})]


def _absaetze(norm, s, e, z, meta, kopf: bool) -> list[dict]:
    block = norm[s:e]
    # T-15 (A-W7): im Amtsblatt steht Art. 5 Abs. 1b als '1b.' auf eigener Zeile statt
    # '(1b)'; ohne diese Form hing der Absatz an Abs. 1a lit. b.
    marken = [(m.group(1) or m.group(2), m.start())
              for m in re.finditer(r"(?:^|\n)(?:\((\d+[a-z]?)\)\s|(\d+[a-z])\.\n)", block)]
    out = []
    if kopf and not marken:
        # T-15 (A-W7): ein eingefuegter Artikel ohne Absatznummern (Art. 75b). Wie im
        # Extraktor der Grundfassung ist die Ueberschrift keine Einheit; der Text wird
        # nach Buchstaben geschnitten, statt mit der Ueberschrift eine Einheit zu sein.
        zeilen = block.split("\n")
        skip = len("\n".join(zeilen[:2])) + 1 if len(zeilen) > 2 else 0
        while skip < len(block) and block[skip] in "\n \t":
            skip += 1
        return _buchstaben(norm, s + skip, e, {"artikel": z["artikel"]}, meta)
    erste = marken[0][1] if marken else len(block)
    if kopf and block[:erste].strip():
        k = _kennung({"artikel": z["artikel"]})
        out.append(_einheit(norm, s, s + erste, k + " n.F.", {**meta, "ziel": k}))
    for i, (ab, rel) in enumerate(marken):
        a_s = s + rel + (1 if block[rel] == "\n" else 0)
        a_e = s + marken[i + 1][1] if i + 1 < len(marken) else e
        zz = {k: v for k, v in z.items() if k in ("artikel", "anhang", "abschnitt")}
        if zz.get("anhang"):
            zz["nummer"] = ab          # in Anhaengen ist '(21)' eine Nummer
        else:
            zz["absatz"] = ab
            if z.get("absatz") == ab:  # 'Absatz 1 Unterabsatz 1 …', 'Die Einleitung …'
                for feld in ("unterabsatz", "teil"):
                    if z.get(feld):
                        zz[feld] = z[feld]
        out += _buchstaben(norm, a_s, a_e, zz, meta, kopf_einheit=True)
    return out


def _buchstaben(norm, s, e, z, meta, kopf_einheit: bool = False) -> list[dict]:
    """Buchstaben und roemische Ziffern am Zeilenanfang ('a) …', '(b) …', 'ii) …')."""
    block = norm[s:e]
    marken = [(m.start(1) - (1 if block[m.start(1) - 1:m.start(1)] == "(" else 0), "alpha", m.group(1))
              for m in re.finditer(r"(?:^|\n)\(?([a-z]{1,2}|[ivx]+)\)\s", block)]
    # zweibuchstabige Einschuebe ('ba', 'bb') sind eigene Buchstaben
    zwei = [m for m in marken if len(m[2]) == 2 and m[2] not in ("ii", "iv", "vi", "ix", "xi")]
    if zwei:
        items = [{"pos": p, "ebene": "lit", "kennung": lab, "eltern": None, "liste": 1,
                  "eltern_key": None} for p, _, lab in marken]
    else:
        items = _gliedern(marken)
    out = []
    grenzen = [it["pos"] for it in items] + [len(block)]
    if grenzen[0] > 0 and block[:grenzen[0]].strip():
        k = _kennung(z)
        out.append(_einheit(norm, s, s + grenzen[0], k + " n.F.", {**meta, "ziel": k}))
    for i, it in enumerate(items):
        zz = dict(z)
        if it["ebene"] == "ziffer":
            zz["buchstabe"] = it["eltern"]["kennung"]
            zz["ziffer"] = it["kennung"]
        else:
            zz["buchstabe"] = it["kennung"]
        k = _kennung(zz)
        out.append(_einheit(norm, s + it["pos"], s + grenzen[i + 1], k + " n.F.", {**meta, "ziel": k}))
    return out


def omnibus_units(norm: str) -> tuple[list[dict], list[dict]]:
    """Alle Einheiten des Aenderungsrechtsakts; dazu der Anweisungsbericht."""
    units, bericht = [], []
    for art in _artikel_bereiche(norm):
        kopf = f"Omnibus Art. {art['artikel']}"
        anws = _anweisungen(norm, art)
        if not anws:  # z. B. Inkrafttreten
            s = art["start"]
            units.append(_einheit(norm, s, art["end"], kopf,
                                  {"anweisung": kopf, "titel": art["titel"], "aenderung": None}))
            bericht.append({"anweisung": kopf, "einheiten": [kopf]})
            continue
        for anw in anws:
            akenn = f"{kopf} Nr. {anw['nr']}"
            fremd = art["artikel"] != "1"
            unter = [] if fremd else _unteranweisungen(norm, anw)
            satz_s, satz_e = _satz(norm, anw["start"], unter[0]["start"] - 1 if unter else anw["end"],
                                   anw["zitate"])
            satz = norm[satz_s:satz_e]
            z = _ziel(satz, {}) if not fremd else {}
            meta = {"anweisung": akenn, "titel": art["titel"], "aenderung": _aenderung(satz),
                    "ziel": _kennung(z) or None, "artikel_ziel": z.get("artikel")}
            neu = [_einheit(norm, satz_s, satz_e, akenn, meta)]
            if fremd:
                # Aenderungen ANDERER Verordnungen: eine Einheit je Anweisung, samt Zitat
                neu = [_einheit(norm, anw["start"], anw["end"], akenn,
                                {**meta, "ziel": art["titel"].replace("Änderung der ", "")})]
            else:
                if unter:
                    for u in unter:
                        ukenn = f"{akenn} lit. {u['lit']}"
                        us, ue = _satz(norm, u["start"], u["end"], u["zitate"])
                        uz = _ziel(norm[us:ue], z)
                        um = {**meta, "anweisung": ukenn, "aenderung": _aenderung(norm[us:ue]),
                              "ziel": _kennung(uz) or None}
                        neu.append(_einheit(norm, us, ue, ukenn, um))
                        for zs, ze in u["zitate"]:
                            neu += _neuer_text(norm, zs, ze, uz, um)
                else:
                    for zs, ze in anw["zitate"]:
                        neu += _neuer_text(norm, zs, ze, z, meta)
            if neu[0]["ziel"] is None:
                # 'Folgender Artikel wird eingefuegt:' — das Ziel steht erst im neuen Text
                koepfe = []
                for u in neu[1:]:
                    kopf_ziel = re.match(r"(Art\. \d+[a-z]?|Anhang [IVXLC]+)", u["ziel"] or "")
                    if kopf_ziel and kopf_ziel.group(1) not in koepfe:
                        koepfe.append(kopf_ziel.group(1))
                neu[0]["ziel"] = ", ".join(koepfe) or None
            units += neu
            bericht.append({"anweisung": akenn, "einheiten": [u["id"] for u in neu]})
    return [u for u in units if u["text"].strip()], bericht


def main() -> int:
    raw, norm, digest = load(Path(sys.argv[1]))
    units, bericht = omnibus_units(norm)
    print(f"SHA-256 {digest} | Einheiten {len(units)} | Anweisungen {len(bericht)}")
    for u in units:
        print(f"[{u['id']}]  ({u['aenderung']}) ziel={u['ziel']}  {u['text'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
