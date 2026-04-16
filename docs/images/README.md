# `docs/images/`

Canonical (current) diagrams used by the public README and reference docs.

## Process Model

| File | Purpose |
|------|---------|
| `process_regulation_to_pipeline_v2.html` | **Source** — editable HTML/CSS BPMN diagram (designed for A4) |
| `process_regulation_to_pipeline_v2_export.png` | **Render** — high-DPI PNG (3176×3200) embedded in repo README |

To update: edit the HTML, then re-render via Chrome headless:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new \
  --screenshot=docs/images/process_regulation_to_pipeline_v2_export.png \
  --window-size=794,800 \
  --hide-scrollbars --disable-gpu \
  --force-device-scale-factor=4 \
  "file://$(pwd)/docs/images/process_regulation_to_pipeline_v2.html"
```

## Earlier versions

Previous Mermaid v1, Mermaid v3, the "enterprise adaptation" variant, and a low-DPI v2 PNG live in `legacy/docs/diagrams/` (gitignored). They are kept for DSR iteration traceability but are not referenced from the README.
