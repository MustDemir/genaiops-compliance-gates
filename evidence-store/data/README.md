# `evidence-store/data/` — Runtime Artifacts

**This entire folder is gitignored** (`evidence-store/data/` in `.gitignore`).

Runtime outputs from the pipeline orchestrator and evidence-store scripts land here. Source-of-truth schemas live in `../schema/`, source-of-truth migrations in `../migrations/`.

## Layout

| Path | Produced by | Format |
|------|-------------|--------|
| `reports/pipeline_report_<id>.json` | `pipeline/gate_orchestrator.py` | JSON, one file per pipeline run |
| `sqlite/evidence_*.db` | `scripts/record_evidence.py` (SQLite mode) | SQLite 3 |

## Why empty in fresh clones

These artifacts only appear after running pipelines locally. Old runs from before this layout existed are archived in `legacy/runtime-artifacts/` (also gitignored).
