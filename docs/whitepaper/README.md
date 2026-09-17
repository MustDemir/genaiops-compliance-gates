# Whitepaper

**Braucht KI neue Methoden? Der Engpass ist nicht Fähigkeit, sondern Nachweisbarkeit**

An evidence-based examination of whether established process models — Scrum and the TOGAF
ADM — have to be replaced for productive use of generative AI, or whether they already hold
the control points that make such use verifiable. The artefact in this repository serves as
the worked instantiation (chapter 9).

German, 29 pages, 67 sources, each marked as peer-reviewed or preprint.

| File | Role |
|---|---|
| `braucht-ki-neue-methoden.html` | The source. Everything else is derived from it. |
| `render.py` | Renders the source to PDF via Playwright/Chromium. |
| `Braucht-KI-neue-Methoden_Demir_2026.pdf` | The rendered export. |

## Reproducing the PDF

```bash
pip install playwright && playwright install chromium
python3 docs/whitepaper/render.py          # or: CHROME_PATH=/path/to/chrome python3 …
```

The render is deterministic: same source, same byte count.

## Two deviations, declared

**The PDF export is tracked here.** `.gitignore` excludes `HANDBUCH.pdf` on the principle that
an export is an artefact of the source, not the source. That principle still holds for the
handbook, whose source sits in the repository root and is read far more often than its export.
It is set aside here for one reason: this document is distributed as a PDF, and a reader who
clones the repository should be able to see what was distributed without first installing a
browser engine. The source and the renderer are tracked alongside it, so the export remains
checkable against its origin rather than standing on its own.

**This is positioning material in a repository that keeps such material out.** `.gitignore`
excludes `STRATEGIE.md` because market and positioning content does not belong in a public
artefact under a DOI. The distinction drawn here: the whitepaper makes no claim about the
market, prices nothing and names no counterparty. It argues a methodological position and
cites its evidence — including the evidence against it. What it says about this artefact is
what the artefact's own documentation says, and no more.

## Licence

The repository is Apache-2.0. This whitepaper is authored text rather than code; reuse of its
wording is governed by ordinary attribution expectations for written work, and the figures and
tables carry their sources inline. Where the document reports findings from third-party
publications, those publications are the authority, not this text.
