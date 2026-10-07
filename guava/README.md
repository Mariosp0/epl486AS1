# EPL484 Project 1 – Architecture evolution of Google Guava

Second analysed system (the first, Spring AI, is at the repository root).
13 sparse releases: every second major release 10.0 … 32.0 plus the latest
release 33.7.0 (2011–2026); Phase 4 (AI) uses only 33.7.0.

| Phase | Where |
|-------|-------|
| 1 – Selection | [`docs/phase1_project_selection.md`](docs/phase1_project_selection.md), `data/tags.csv` |
| 2 – Data | `scripts/collect_versions.py` → `data/versions.csv`, `data/packages/`, `data/workspace/<v>/bin/guava-<v>.jar` |
| 3.1–3.5 | `data/dependencies/`, `data/noise/`, `data/rsf/`, `results/` (size, metrics, stability, noise, ACDC experiment, clusters, figures) |
| 4 – AI | `ai/prompts.md`, `ai/inputs/`, `ai/responses/P1–P4`, `ai/ai_architecture_P3.json`, `results/ai_*.csv` |
| 5 – Report | [`report/report.pdf`](report/report.pdf) (source `report/report_src.md`) |

## Reproduce (from the repository root)

```bash
python3 guava/scripts/collect_versions.py
PROJECT=guava scripts/run_tools.sh            # or: PROJECT=guava scripts/run_jnode_pool.sh 4
PROJECT=guava python3 scripts/recover.py
PROJECT=guava python3 scripts/acdc_params.py
PROJECT=guava python3 scripts/noise_fanin.py
python3 guava/scripts/package_changes.py
PROJECT=guava python3 scripts/ai_inputs.py
PROJECT=guava python3 scripts/ai_eval.py
PROJECT=guava python3 scripts/plots.py
PROJECT=guava python3 scripts/report_tables.py && PROJECT=guava scripts/build_report.sh
```
