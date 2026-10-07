# EPL484 Project 1 – Architecture evolution of Spring AI

Recovery and evolution analysis of the architecture of
[Spring AI](https://github.com/spring-projects/spring-ai) over **25 feature
releases** (0.8.0, Feb 2024 → 2.1.0-M1, Sep 2026), following the five phases of
the assignment.

| Phase | Where |
|-------|-------|
| 1 – System selection | [`docs/phase1_project_selection.md`](docs/phase1_project_selection.md), `data/tags.csv`, `scripts/project_stats.sh` |
| 2 – Data acquisition | `scripts/collect_versions.py` → `data/versions.csv`, `data/modules/`, `data/workspace/<v>/bin/*.jar` |
| 3.1 – Size | `results/size.csv`, `results/figures/size_*.png` |
| 3.2 – Class dependencies | `tools/DependencyExtractor.jar` → `data/dependencies/<v>.csv`, `data/rsf/` |
| 3.3 – Widely-used (noise) classes | `tools/JNode-fast-p4.jar` (patched JNode, see below) → `data/noise/<v>.csv`; original-precision outputs in `data/noise_jnode3/`; `results/noise_classes.csv`, `results/noise_comparison.csv`, `results/noise_vs_fanin.csv` |
| 3.4 – Recovery A1–A4 | `scripts/recover.py` (ACDC + k-means) → `results/clusters/<v>_<A1..A4>.rsf` |
| 3.5 – Quality | `scripts/metrics.py` → `results/metrics.csv`, `results/stability.csv`, figures |
| 4 – AI | `ai/prompts.md`, `ai/inputs/`, `ai/responses/`, `scripts/ai_eval.py` → `results/ai_*.csv` |
| 5 – Report | [`report/report.pdf`](report/report.pdf) (generated from `report/report_src.md` by `scripts/report_tables.py`) |

## Requirements

* Java 17+ (tested with OpenJDK 21), Python 3.10+ (tested 3.13)
* `pip install -r requirements.txt`
* Network access to Maven Central and `repo.spring.io/milestone`

## Reproducing everything

```bash
python3 scripts/collect_versions.py      # Phase 2: BOM -> module jars -> 1 merged jar / version
scripts/run_tools.sh                     # Phase 3.2/3.3: DependencyExtractor + JNode (sequential)
#   or: scripts/run_jnode_pool.sh 4      # JNode with 4 parallel workers (~10-20 min per 2k-class version)
python3 scripts/recover.py               # Phase 3.1/3.4/3.5: RSF, ACDC (A1,A2), k-means (A3,A4), metrics
python3 scripts/acdc_params.py           # ACDC parameter experiment on the latest version
python3 scripts/noise_fanin.py           # noise classes vs fan-in
python3 scripts/compare_noise.py         # original (3-decimal) vs fixed (4-decimal) JNode
python3 scripts/module_changes.py        # module-level change log
python3 scripts/ai_inputs.py             # Phase 4: inputs given to the AI tool
python3 scripts/ai_eval.py               # Phase 4: metrics of the AI-recovered architecture
python3 scripts/plots.py                 # figures in results/figures
python3 scripts/report_tables.py && scripts/build_report.sh   # report/report.md + report/report.pdf
```

`data/cache/` (downloaded module jars, ~170 MB) is not committed; it is
recreated by `collect_versions.py`.

## Tools

* `tools/DependencyExtractor.jar`, `tools/JNode.jar` – provided by the course (Blackboard).
* `tools/JNode-fast.jar`, `tools/JNode-fast-p4.jar` – JNode with documented
  patches (`tools/jnode-patch/`): (1) two hash lookups instead of linear scans
  (byte-identical output, >2 h → minutes per version); (2) CR-model rounding
  to 4 instead of 3 decimals, because `round(1/n, 3) = 0` for n > 2,000 class
  files made JNode flag no class at all in 4 versions. The final results use
  `JNode-fast-p4.jar`.
* `tools/acdc.jar` – ACDC (Tzerpos & Holt) built from `tools/acdc/src`, the
  BSD-licensed Java port in [USC ARCADE](https://github.com/usc-softarch/arcade_core)
  (the York wiki link was not reachable). Two documented changes: (1) optional
  CLI arguments `maxClusterSize` and `patterns` (`b`=BodyHeader, `s`=SubGraph,
  `o`=OrphanAdoption) so the parameters can be varied, (2) a hash-map lookup in
  `TAInput` instead of a full tree scan per input line (same output, faster).
  `scripts/recover.py` passes file-style names (`pkg.Class.java`) to ACDC:
  ACDC names a subsystem after its dominator's base name (text before the last
  dot), which for plain Java class names is the package and would merge all
  subsystems of a package; the suffix is stripped again from the output.
  Usage: `java -jar tools/acdc.jar in.rsf out.rsf [maxClusterSize=20] [patterns=bso]`.
* k-means: scikit-learn `KMeans`; k chosen with the elbow method (`kneed`).

## Repository layout

```
ai/        Phase 4 prompts, inputs, responses, AI architecture rules
data/      versions, tags, per-version module lists, merged jars, tool outputs, RSF files
docs/      Phase 1 selection document
report/    report (Markdown source + PDF)
results/   all computed tables, recovered architectures (RSF) and figures
scripts/   analysis code
tools/     course tools and ACDC
```
