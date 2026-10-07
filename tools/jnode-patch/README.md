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
JNode for Guava 10.0 and 12.0 (original outputs kept in
`guava/data/noise_original/`). The original needed more than two hours for
the larger versions; the patched tool needs minutes.

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
for Guava 30.0, the only analysed version with more than 2,000 class files
(2,010). With 4 decimals the limit moves to 20,000 classes. All 13 versions
were run with the 4-decimal variant for consistency; `scripts/compare_noise.py`
compares it with the 3-decimal outputs kept in `guava/data/noise_jnode3/`
(`guava/results/noise_comparison.csv`).

Rebuild: compile `tools/jnode-patch/CRModel.java` the same way and
`jar uf tools/JNode-fast-p4.jar jnode/workers/CRModel.class` on a copy of
`JNode-fast.jar`.
