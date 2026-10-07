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
