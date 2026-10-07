# P2 response (README + packages)

## 1. Components

| Component | Packages (classes) | Responsibility |
|---|---|---|
| **C1 Foundation** | `common.base` (48), `common.base.internal` (1) | Preconditions, Optional, functions/predicates, strings (Joiner, Splitter, CharMatcher), finalizer support |
| **C2 Numeric utilities** | `common.primitives` (23), `common.math` (14) | Primitive helpers, unsigned types, checked math, statistics |
| **C3 Collections** | `common.collect` (209) | Immutable collections, multimap/multiset/bimap/table, ranges, collection utilities and ordering |
| **C4 Concurrency** | `common.util.concurrent` (79) | ListenableFuture, executors, services, rate limiting |
| **C5 Caching** | `common.cache` (19) | Loading caches |
| **C6 I/O & hashing** | `common.io` (35), `common.hash` (31) | Sources/sinks, files, encodings; hash functions, Bloom filters |
| **C7 Graphs** | `common.graph` (52) | Graph/ValueGraph/Network |
| **C8 Text & web** | `common.escape` (9), `common.html` (1), `common.xml` (1), `common.net` (7), `thirdparty.publicsuffix` (3) | Escapers, media types, host and domain names, public-suffix list |
| **C9 Reflection & events** | `common.reflect` (14), `common.eventbus` (8) | TypeToken, ClassPath, Invokable; publish/subscribe |

## 2. Layers

1. **L1 Foundation** – C1.
2. **L2 Core data & numerics** – C2, C3 (may use L1).
3. **L3 Infrastructure** – C4 (uses L1–L2).
4. **L4 Feature libraries** – C5, C6, C7, C8, C9 (use L1–L3; should not depend
   on each other except C5 → C4 and C6 internal).

## 3. Diagram

```
 L4  [C5 cache] [C6 io+hash] [C7 graph] [C8 escape/net] [C9 reflect+eventbus]
          \__________|___________|__________|_______________|
 L3                    [C4 util.concurrent]
                              |
 L2        [C3 collect (209 classes)]   [C2 primitives + math]
                              |
 L1                      [C1 base]
```

## 4. Smells

* **`common.collect` is a god package**: 209 of 554 classes (38 %) in one
  package, mixing public API types, many implementation classes
  (`Regular*`, `Singleton*`, `Filtered*`) and utilities. Package-private
  visibility is used as the encapsulation mechanism, which forces everything
  into one package.
* **`common.util.concurrent`** (79 classes) is the second large package.
* Tiny packages (`html`, `xml` with one class each) exist only to group a
  single factory – fine for API discoverability, irrelevant architecturally.
