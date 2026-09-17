"""Renders the whitepaper source to PDF.

    pip install playwright && playwright install chromium
    python3 docs/whitepaper/render.py

Set CHROME_PATH to use an existing Chromium instead of a downloaded one.
"""
import os, pathlib
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(__file__).parent
SRC = BASE / "braucht-ki-neue-methoden.html"
OUT = BASE / "Braucht-KI-neue-Methoden_Demir_2026.pdf"
CHROME = os.environ.get("CHROME_PATH")

FOOTER = """
<div style="width:100%; font-family:Arial, 'Liberation Sans', sans-serif; font-size:8pt;
            color:#000; padding:0 18mm; display:flex; justify-content:space-between;
            border-top:0.5pt solid #000; margin-top:4mm; padding-top:2mm;">
  <span>Braucht KI neue Methoden? &middot; M. Demir &middot; 2026</span>
  <span class="pageNumber"></span>
</div>
"""

with sync_playwright() as p:
    launch = {"args": ["--no-sandbox"]}
    if CHROME:
        launch["executable_path"] = CHROME
    browser = p.chromium.launch(**launch)
    page = browser.new_page()
    page.goto(SRC.as_uri(), wait_until="networkidle")
    page.emulate_media(media="print")
    page.pdf(
        path=str(OUT),
        format="A4",
        print_background=True,
        display_header_footer=True,
        header_template="<div></div>",
        footer_template=FOOTER,
        margin={"top": "16mm", "bottom": "17mm", "left": "18mm", "right": "18mm"},
    )
    browser.close()

print("written:", OUT, OUT.stat().st_size, "bytes")
