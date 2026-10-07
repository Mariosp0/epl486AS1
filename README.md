# EPL484 Project 1 – Architecture evolution of Google Guava

Recovery and evolution analysis of the architecture of
[Google Guava](https://github.com/google/guava) over **13 sparse releases**
(every second major release 10.0 … 32.0 plus the latest release 33.7.0,
2011 → 2026), following the five phases of the assignment. Phase 4 (AI) uses
only the latest release.

| Phase | Where |
|-------|-------|
| 1 – System selection | [`guava/docs/phase1_project_selection.md`](guava/docs/phase1_project_selection.md), `guava/data/tags.csv`, `scripts/project_stats.sh` |
| 2 – Data acquisition | `guava/scripts/collect_versions.py` → `guava/data/versions.csv`, `guava/data/packages/`, `guava/data/workspace/<v>/bin/guava-<v>.jar` |
| 3.1 – Size | `guava/results/size.csv`, `guava/results/package_changes.csv`, figures `size_*.png` |
| 3.2 – Class dependencies | `tools/DependencyExtractor.jar` → `guava/data/dependencies/<v>.csv`, `guava/data/rsf/` |
| 3.3 – Widely-used (noise) classes | `tools/JNode-fast-p4.jar` (patched JNode, see below) → `guava/data/noise/<v>.csv`; `guava/results/noise_classes.csv`, `noise_vs_fanin.csv`, `noise_comparison.csv` |
| 3.4 – Recovery A1–A4 | `scripts/recover.py` (ACDC + k-means) → `guava/results/clusters/<v>_<A1..A4>.rsf` |
| 3.5 – Quality | `scripts/metrics.py` → `guava/results/metrics.csv`, `stability.csv`; `scripts/lecture_metrics.py` → MoJoFM, Bunch vs JNode, architectural smells, dependency changes |
| 4 – AI | `guava/ai/prompts.md`, `guava/ai/inputs/`, `guava/ai/responses/`, `guava/ai/ai_architecture_P3.json`, `scripts/ai_eval.py` → `guava/results/ai_*.csv` |
| 5 – Report | [`guava/report/report.pdf`](guava/report/report.pdf) (generated from `guava/report/report_src.md` by `scripts/report_tables.py`) |

## Requirements

* Java 17+ (tested with OpenJDK 21), Python 3.10+ (tested 3.13)
* `pip install -r requirements.txt` (+ `networkx`)
* Network access to Maven Central

## Reproducing everything (from the repository root)

```bash
python3 guava/scripts/collect_versions.py   # Phase 2: Maven jars -> guava/data/workspace
scripts/run_tools.sh                        # DependencyExtractor + JNode (sequential)
#   or: scripts/run_jnode_pool.sh 4         # JNode with 4 parallel workers
python3 scripts/recover.py                  # RSF, ACDC (A1,A2), k-means (A3,A4), metrics
python3 scripts/acdc_params.py              # ACDC parameter experiment (latest version)
python3 scripts/noise_fanin.py              # noise classes vs fan-in
python3 scripts/compare_noise.py            # original (3-decimal) vs fixed (4-decimal) JNode
python3 scripts/lecture_metrics.py          # MoJoFM, Bunch vs JNode, smells, deps added/removed
python3 scripts/activity.py <guava clone>   # commits per month between releases (law IV)
python3 guava/scripts/package_changes.py    # package/class changes between versions
python3 scripts/ai_inputs.py                # Phase 4: inputs given to the AI tool
python3 scripts/ai_eval.py                  # Phase 4: metrics of the AI architecture
python3 scripts/plots.py                    # figures in guava/results/figures
python3 scripts/report_tables.py && scripts/build_report.sh   # guava/report/report.pdf
```

The scripts work on the project folder `guava/` (override with
`PROJECT=<folder>`; the folder holds `project.json`, `data/`, `results/`, `ai/`,
`report/`).

## Tools

* `tools/DependencyExtractor.jar`, `tools/JNode.jar` – provided by the course (Blackboard).
* `tools/JNode-fast.jar`, `tools/JNode-fast-p4.jar` – JNode with documented
  patches (`tools/jnode-patch/`): (1) two hash lookups instead of linear scans
  (identical output, much faster); (2) CR-model rounding to 4 instead of 3
  decimals, because `round(1/n, 3) = 0` for n > 2,000 class files makes JNode
  flag no class at all. The final results use `JNode-fast-p4.jar`.
* `tools/acdc.jar` – ACDC (Tzerpos & Holt) built from `tools/acdc/src`, the
  BSD-licensed Java port in [USC ARCADE](https://github.com/usc-softarch/arcade_core)
  (the York wiki link was not reachable). Changes: optional CLI arguments
  `maxClusterSize` and `patterns` (`b`=BodyHeader, `s`=SubGraph,
  `o`=OrphanAdoption) and a hash-map lookup in `TAInput` (same output, faster).
  `scripts/recover.py` passes file-style names (`pkg.Class.java`) to ACDC,
  because ACDC names a subsystem after its dominator's base name (text before
  the last dot), which for plain Java class names is the package.
  Usage: `java -jar tools/acdc.jar in.rsf out.rsf [maxClusterSize=20] [patterns=bso]`.
* `tools/mojo.jar` – MoJo 2.0 (York University, via USC ARCADE; source in
  `tools/mojo/src`) for MoJoFM (`java -jar tools/mojo.jar A.rsf B.rsf -fm`).
* k-means: scikit-learn `KMeans`; k chosen with the elbow method (`kneed`).
* Quality measures follow Lecture 6–7: cohesion Aᵢ = μᵢ/Nᵢ², coupling
  Eᵢⱼ = εᵢⱼ/(2NᵢNⱼ), **MQ = mean(A) − mean(E)** (column `basic_mq`); TurboMQ,
  TurboMQ/k and the intra-cluster share are supplementary.

## Repository layout

```
guava/       the analysed system: data, results, AI material, report, docs, collection scripts
scripts/     analysis code (shared pipeline)
tools/       course tools (DependencyExtractor, JNode + patches), ACDC, MoJo
```
