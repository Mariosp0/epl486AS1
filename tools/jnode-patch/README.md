# JNode performance patch

`tools/JNode-fast.jar` = the course's `tools/JNode.jar` with two classes replaced
(decompiled with CFR 0.152, patched, recompiled with `javac --release 8`):

* `jnode.workers.StaticAnalysisWorker.getPlace` – class-name → index lookup via a
  `HashMap` (first occurrence wins, as in the original linear scan) instead of a
  linear scan of the class list on every DFS step of the subgraph extraction.
* `jnode.modelEntities.ClassAnalysis.isDependency` – `Set.contains` instead of
  iterating over the set.

No other logic is touched (CR model, Dijkstra, SIG and the noise threshold are
unchanged). Validation: the output CSV is **byte-identical** to the original
JNode for 0.8.0, 1.0.0-M1 and 1.0.0-M2 (originals kept in `data/noise_original/`).
Runtime for 1.0.0-M1 dropped from ~9 min to ~1.3 min; the original needed >2 h
per 2k-class version.

Rebuild:
```bash
cp tools/JNode.jar tools/JNode-fast.jar
mkdir -p /tmp/jn && (cd /tmp/jn && unzip -oq ../../$PWD/tools/JNode.jar)   # original classes + libs
javac --release 8 -cp "/tmp/jn:/tmp/jn/*" -d out tools/jnode-patch/*.java
(cd out && jar uf ../tools/JNode-fast.jar jnode/modelEntities/ClassAnalysis.class jnode/workers/StaticAnalysisWorker.class)
```

## Precision fix: `tools/JNode-fast-p4.jar` (used for the final results)

`JNode-fast.jar` + `jnode.workers.CRModel.roundDecimals` rounding to **4** instead
of 3 decimals.

Why: the CR model initialises every class weight with `round(1/n, 3)`. For more
than 2,000 class files `1/n < 0.0005` rounds to **0**; the weights collapse, the
shortest-path "probabilities" become 0, `1/0 = Infinity`, and the min-max
normalisation turns every SIG into 0, so **no class is flagged**. This happened
for exactly the four versions with > 2,000 class files (2.0.0-M2: 2,025,
2.0.0-M3: 2,177, 2.0.0-M4: 2,184, 2.1.0-M1: 2,015). With 4 decimals the limit
moves to 20,000 classes. All 25 versions were re-run with the 4-decimal
variant for consistency; `scripts/compare_noise.py` compares it with the
original (3-decimal) outputs kept in `data/noise_jnode3/`
(`results/noise_comparison.csv`).

Rebuild: compile `tools/jnode-patch/CRModel.java` the same way and
`jar uf tools/JNode-fast-p4.jar jnode/workers/CRModel.class` on a copy of
`JNode-fast.jar`.
