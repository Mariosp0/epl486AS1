# JNode: defects found and the fixed jars used for the results

The course's `tools/JNode.jar` (Constantinou et al. 2015) has two defects in
the way it builds the class dependency graph, plus a precision problem in the
CR model. All three change the noise classes it reports. The results use
`tools/JNode-fixed.jar`, which is the course jar with the classes below
replaced. They were decompiled with CFR 0.152, patched (each change is
marked `PATCH` in the source) and recompiled with `javac --release 8`.

| File | Change | Kind |
|---|---|---|
| `ClassycleWorker.java` | Graph fix 1: build each class's out-dependencies from its own entry only | correctness |
| `DependencyCollector.java` | Graph fix 2: do not record a class as depending on itself | correctness |
| `CRModel.java` | Round the CR-model weights to 4 instead of 3 decimals | correctness (precision) |
| `StaticAnalysisWorker.java` | `getPlace`: class-name → index lookup through a `HashMap`, not a linear scan | speed only |
| `ClassAnalysis.java` | `isDependency`: `Set.contains` instead of iterating over the set | speed only |

`tools/JNode-fixed-3dec.jar` has the same changes except `CRModel.java`
(original 3-decimal rounding). It is used only for the comparison in
`guava/results/noise_comparison.csv`.

## Graph fix 1: dependencies taken from the wrong classes (`ClassycleWorker`)

`DependencyCollector` stores the dependencies in a **static** map
(`private static final Map dependencies`) that is shared by all classes and
never cleared. After reading class *X*, `ClassycleWorker` iterated over the
**whole** map and added every target found there as an out-dependency of *X*:

```java
for (String fromClass : dependencies.keySet())            // all classes read so far
    for (String toClass : dependencies.get(fromClass).keySet()) {
        classHashMap.get(className2).addClassForDependency(toClass);   // className2 = X
        classHashMap.get(toClass).addClassForDependendee(fromClass);
    }
```

So *X* inherited the dependencies of every class that came before it in the
jar. The out-edges therefore depend on the order of the entries in the
archive, and the classes read late depend on almost everything. (The
in-edges, `addClassForDependendee(fromClass)`, were correct.) The fix uses
only `dependencies.get(X)`.

## Graph fix 2: self-dependencies (`DependencyCollector.recordDependency`)

The test `targetClass.equals(this.className)` compared the internal name
(`a/b/C`) with the dotted name (`a.b.C`) **before** converting it, so it never
matched and every class that refers to itself (fields, `this` calls) got a
dependency on itself. The fix converts the name first.

## Evidence

* `test/run_order_test.sh` is a toy system with four classes (A uses B, C uses D)
  packed in two archive orders:

  | Archive order | Course `JNode.jar` | `JNode-fixed.jar` |
  |---|---|---|
  | A,B,C,D | A→{A,B}, B→{A,B}, C→{A,B,C,D}, D→{A,B,C,D} | A→{B}, C→{D} |
  | D,C,B,A | A→{A,B,C,D}, B→{C,D}, C→{C,D}, D→{} | A→{B}, C→{D} |

* `test/compare_graph.sh <version>` compares the graph built inside JNode
  with the edges of the course's DependencyExtractor (class-file level,
  distinct, no self-edges):

  | Version | Course `JNode.jar` | `JNode-fixed.jar` | DependencyExtractor |
  |---|---|---|---|
  | 10.0 (1,157 class files) | 710,269 edges, 1,062 of them self-dependencies | 4,239 | 4,239 (identical set) |
  | 33.7.2 (1,948 class files) | 1,929,396 edges, 1,733 of them self-dependencies | 7,764 | 7,764 (identical set) |

  With the fixes the JNode graph is **exactly** the DependencyExtractor
  graph. The original graph contains every correct edge plus
  many wrong ones (167 times for 10.0, 248 times for 33.7.2).

* Effect on the noise: the course jar flags **no** class for Guava 10.0 and
  12.0 (`guava/data/noise_original/`). The fixed jar flags 90 and 98 class
  files, and for 33.7.2 the expected omnipresent classes (`Preconditions`,
  `ImmutableList`, `Iterators`, `Maps`, `Function`, …).

The defects are in the course tool, so they should be reported to the
instructor.

## Precision fix (`CRModel.roundDecimals`)

The CR model sets every class weight to `round(1/n, 3)`. With more than 2,000
class files, `1/n < 0.0005` rounds to **0**. The weights then collapse, the
shortest-path "probabilities" become 0, `1/0 = Infinity`, and the min-max
normalisation sets every SIG to 0, so **no class is flagged**. This happens
for Guava 30.0 (2,010 class files). With 4 decimals the limit moves to 20,000
classes. On the 12 other versions, 3 and 4 decimals flag exactly the same
class files (Jaccard 1.0, `guava/results/noise_comparison.csv`).

## Speed patches

`getPlace` and `isDependency` were called inside the DFS of the subgraph
extraction and scanned lists linearly. The patched versions give the same
result: combined with the original graph code, the output CSV was
byte-identical to the course jar for Guava 10.0 and 12.0. They only reduce the
running time (hours → minutes). With the graph fixes the graph is far
sparser, and a full run takes under a minute per version.

## Rebuild

```bash
mkdir -p /tmp/jn && (cd /tmp/jn && unzip -oq "$OLDPWD/tools/JNode.jar")   # original classes + libraries
javac --release 8 -cp "/tmp/jn:/tmp/jn/*" -d /tmp/jnout tools/jnode-patch/*.java
cp tools/JNode.jar tools/JNode-fixed.jar
cp tools/JNode.jar tools/JNode-fixed-3dec.jar
(cd /tmp/jnout && jar uf "$OLDPWD/tools/JNode-fixed.jar" $(find jnode -name '*.class') \
              && jar uf "$OLDPWD/tools/JNode-fixed-3dec.jar" $(find jnode -name '*.class' ! -name CRModel.class))
```
