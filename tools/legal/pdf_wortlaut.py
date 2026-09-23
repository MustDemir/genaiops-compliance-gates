#!/usr/bin/env python3
"""pdf_wortlaut.py — leitet aus einem Amtsblatt-PDF einen pruefbaren Wortlaut ab.

Warum es dieses Skript gibt (T-14.2): Der Omnibus VO (EU) 2026/1744 liegt nur als
PDF im Repo. Belegzitate brauchen einen Text mit stabilen Zeichen-Offsets, und ein
PDF hat keine. Der Text wird deshalb ABGELEITET — nicht abgetippt, nicht
redigiert —, und zwar so, dass jeder denselben Text wieder erzeugen kann:

  1. pdftotext (poppler) im Lesemodus, UTF-8, ohne -layout
  2. Seitenmobiliar entfernen — ganze Zeilen, die nur Kopf- oder Fusszeile sind:
     'ELI: http://data.europa.eu/eli/reg/…/oj', 'NN/41', 'DE', 'ABl. L vom …'
  3. Silbentrennung am Zeilenende aufloesen: weiches Trennzeichen (U+00AD) plus
     Zeilenumbruch wird entfernt; sonst wird kein Zeichen veraendert
  4. drei und mehr Zeilenumbrueche zu zwei

Mehr passiert nicht. Die Quelle bleibt das PDF: sein SHA-256 und die
pdftotext-Version stehen im Pflichtenraum neben dem Hash des Textes. Eine andere
pdftotext-Version kann anders umbrechen — dann weicht der Text-Hash ab, und das
ist genau das Signal, das man dann haben will.

Aufruf:
  python3 tools/legal/pdf_wortlaut.py docs/legal/OJ_L_202601744_DE.pdf \\
      docs/legal/wortlaut/omnibus_2026-1744_DE.txt
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

MOBILIAR = [
    re.compile(r"^\f?ELI: http://data\.europa\.eu/eli/reg/\d{4}/\d+/oj$"),
    re.compile(r"^\f?\d+/\d+$"),
    re.compile(r"^\f?DE$"),
    re.compile(r"^\f?ABl\. L vom \d{1,2}\.\d{1,2}\.\d{4}$"),
]


def ableiten(pdf: Path) -> tuple[str, str]:
    version = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True)
    kennung = (version.stderr or version.stdout).splitlines()[0].strip()
    roh = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                         capture_output=True, check=True).stdout.decode("utf-8")
    zeilen = [z for z in roh.split("\n") if not any(m.match(z) for m in MOBILIAR)]
    text = "\n".join(zeilen).replace("\f", "")
    text = text.replace("­\n", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, kennung


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    pdf, ziel = Path(sys.argv[1]), Path(sys.argv[2])
    text, kennung = ableiten(pdf)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(text, encoding="utf-8")
    print(f"PDF:      {pdf}  SHA-256 {hashlib.sha256(pdf.read_bytes()).hexdigest()}")
    print(f"Werkzeug: {kennung}")
    print(f"Text:     {ziel}  SHA-256 {hashlib.sha256(text.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
