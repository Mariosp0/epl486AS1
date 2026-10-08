# P3 response – Guava 33.7.2

> P3 – README + packages + all classes + package dependency graph (the agent read
> only the four attached files). Verbatim answer of a fresh Claude sub-agent (no
> conversation history, no access to the analysis results); see `guava/ai/prompts.md`.
> All numbers below are the AI's own; the class counts per component are its
> estimate and are measured later by `scripts/ai_eval.py` (report, Table 10).

---

# Architecture Recovery: Guava 33.7.2

## 1. Components and mapping rules

I defined **14 components**. Four of them split the two biggest packages: `common.collect` (209 classes) becomes 3 components and `common.util.concurrent` (79 classes) becomes 2. Some small packages that work closely together are merged.

| # | Component | Source | #classes |
|---|---|---|---|
| C1 | Base | common.base, common.base.internal | 49 |
| C2 | PrimitivesMath | common.primitives, common.math | 37 |
| C3 | Collect.Immutable | common.collect (Immutable*/Regular*/Singleton*/Empty* …) | 53 |
| C4 | Collect.Types | common.collect (Multimap/Multiset/BiMap/Table/Range families …) | 77 |
| C5 | Collect.Utilities | rest of common.collect | 79 |
| C6 | Concurrent.Futures | rest of common.util.concurrent | 56 |
| C7 | Concurrent.ServicesSync | common.util.concurrent (Service*, Monitor, RateLimiter, Striped …) | 23 |
| C8 | Cache | common.cache | 19 |
| C9 | EventBus | common.eventbus | 8 |
| C10 | Graph | common.graph | 52 |
| C11 | Hash | common.hash | 31 |
| C12 | IO | common.io | 35 |
| C13 | Reflect | common.reflect | 14 |
| C14 | EscapeNet | common.escape, common.html, common.xml, common.net, thirdparty.publicsuffix | 21 |

The class counts add up to 554, which matches the total in `packages.md`.

Ordered rules (first match wins, fullmatch semantics):

```json
[
  ["Collect.Immutable", "common\\.collect\\.(\\w*Immutable\\w*|Regular\\w*|Singleton\\w*|Empty\\w*|ContiguousSet)"],
  ["Collect.Types", "common\\.collect\\.(\\w*(Multimap|Multiset|BiMap|Table|Range)\\w*|Cut|BoundType|DiscreteDomain|Count|ClassToInstanceMap|MutableClassToInstanceMap|EvictingQueue|MinMaxPriorityQueue)"],
  ["Collect.Utilities", "common\\.collect\\..*"],
  ["Concurrent.ServicesSync", "common\\.util\\.concurrent\\.(Service|AbstractService|AbstractIdleService|AbstractExecutionThreadService|AbstractScheduledService|ServiceManager|ServiceManagerBridge|ListenerCallQueue|Monitor|RateLimiter|SmoothRateLimiter|Striped|CycleDetectingLockFactory|AtomicDouble|AtomicDoubleArray|AtomicLongMap|TimeLimiter|SimpleTimeLimiter|FakeTimeLimiter|Uninterruptibles|ForwardingLock|ForwardingCondition|OverflowAvoidingLockSupport)"],
  ["Concurrent.Futures", "common\\.util\\.concurrent\\..*"],
  ["Cache", "common\\.cache\\..*"],
  ["EventBus", "common\\.eventbus\\..*"],
  ["Graph", "common\\.graph\\..*"],
  ["Hash", "common\\.hash\\..*"],
  ["IO", "common\\.io\\..*"],
  ["Reflect", "common\\.reflect\\..*"],
  ["EscapeNet", "common\\.(escape|html|xml|net)\\..*|thirdparty\\.publicsuffix\\..*"],
  ["PrimitivesMath", "common\\.(primitives|math)\\..*"],
  ["Base", "common\\.base(\\.internal)?\\..*"],
  ["Base", ".*"]
]
```

The last rule is only a safety net. Every class in the listing is already matched by one of the earlier, package-specific rules.

## 2. Responsibilities and key classes

| Component | Responsibility | Key classes |
|---|---|---|
| **Base** | Core language utilities: argument checks, functional interfaces, `Optional`, string handling, equivalence, timing, finalization support | Preconditions, Verify, Objects, MoreObjects, Optional, Function, Predicate, Supplier, Functions, Predicates, Suppliers, Joiner, Splitter, CharMatcher, Strings, CaseFormat, Ascii, Converter, Equivalence, Stopwatch, Ticker, Throwables, FinalizableReferenceQueue, internal.Finalizer |
| **PrimitivesMath** | Static helpers for primitive types, unsigned arithmetic, immutable primitive arrays; overflow-safe integer math, rounding, statistics | Ints, Longs, Doubles, Bytes, UnsignedInteger, UnsignedLong, UnsignedInts, ImmutableIntArray, Primitives; IntMath, LongMath, DoubleMath, BigIntegerMath, Stats, StatsAccumulator, Quantiles, PairedStats |
| **Collect.Immutable** | Immutable collection hierarchy, with public APIs and hidden optimized implementations (Regular, Singleton, JdkBacked, Empty) | ImmutableCollection, ImmutableList, ImmutableSet, ImmutableMap, ImmutableSortedMap/Set, ImmutableMultimap, ImmutableMultiset, ImmutableTable, ImmutableBiMap, ImmutableRangeSet/Map, ContiguousSet, RegularImmutableMap, SingletonImmutableList |
| **Collect.Types** | New collection abstractions and their mutable implementations: multimap, multiset, bimap, table, range, bounded queues | Multimap, ListMultimap, SetMultimap, MultimapBuilder, Multimaps, Multiset, Multisets, HashMultiset, TreeMultiset, BiMap, HashBiMap, Table, HashBasedTable, Tables, Range, RangeSet, TreeRangeSet, DiscreteDomain, Cut, MinMaxPriorityQueue, EvictingQueue |
| **Collect.Utilities** | Static helpers for JDK collections, iteration, ordering and comparison, forwarding decorators, streams and collectors, compact hashing, interning, internal helpers | Iterables, Iterators, FluentIterable, Lists, Sets, Maps, Collections2, Queues, Ordering, Comparators, ComparisonChain, Forwarding* (Collection/List/Map/Set …), Streams, MoreCollectors, CollectCollectors, CompactHashMap, MapMaker, MapMakerInternalMap, Interners, ObjectArrays, CollectPreconditions, Platform |
| **Concurrent.Futures** | `ListenableFuture` model, future composition, executors and adapters | ListenableFuture, AbstractFuture, Futures, FluentFuture, SettableFuture, ClosingFuture, AggregateFuture, ListeningExecutorService, MoreExecutors, ExecutionSequencer, SequentialExecutor, ThreadFactoryBuilder, JdkFutureAdapters, FutureCallback |
| **Concurrent.ServicesSync** | Service lifecycle management plus higher-level synchronization: monitors, rate limiting, lock striping, atomics, time limits | Service, AbstractService, AbstractIdleService, AbstractScheduledService, ServiceManager, Monitor, RateLimiter, SmoothRateLimiter, Striped, CycleDetectingLockFactory, AtomicLongMap, TimeLimiter, Uninterruptibles |
| **Cache** | In-memory caching with eviction, expiry, weak/soft references, loading and statistics | CacheBuilder, CacheBuilderSpec, Cache, LoadingCache, CacheLoader, LocalCache, CacheStats, RemovalListener, Weigher |
| **EventBus** | In-process publish/subscribe via annotated subscribers | EventBus, AsyncEventBus, Subscriber, SubscriberRegistry, Dispatcher, DeadEvent |
| **Graph** | Graph, value-graph and network data structures, plus traversal | Graph, ValueGraph, Network, GraphBuilder, NetworkBuilder, ImmutableGraph, StandardMutableGraph, Graphs, Traverser, EndpointPair, ElementOrder |
| **Hash** | Hash functions, hash codes, Bloom filters | HashFunction, Hasher, HashCode, Hashing, Funnel, Funnels, PrimitiveSink, BloomFilter, Murmur3_128HashFunction, SipHashFunction, FarmHashFingerprint64 |
| **IO** | Byte/char source and sink abstractions, stream utilities, files, resources, encodings | ByteSource, ByteSink, CharSource, CharSink, ByteStreams, CharStreams, Files, MoreFiles, Resources, Closer, BaseEncoding, LittleEndianDataInputStream |
| **Reflect** | Generic type tokens and resolution, invokables, classpath scanning | TypeToken, TypeResolver, Types, Invokable, Parameter, ClassPath, Reflection, TypeToInstanceMap |
| **EscapeNet** | Text escaping framework (HTML/XML/URL) and network value types (hosts, IPs, domains, media types), backed by the public-suffix data | Escaper, CharEscaper, UnicodeEscaper, Escapers, HtmlEscapers, XmlEscapers, UrlEscapers, PercentEscaper, InternetDomainName, InetAddresses, HostAndPort, MediaType, PublicSuffixPatterns |

## 3. Dependencies between components

The input gives dependencies only between packages, so I added up the package edges to get component edges (counts are class-level dependencies). Dependencies between sub-components of the same package, such as C3, C4 and C5 inside `common.collect`, are not in the data.

**Strongest edges:**

| From -> To | n |
|---|---|
| Collections (C3–C5) -> Base | 184 |
| Concurrent (C6/C7) -> Base | 67 |
| Graph -> Collections | 65 |
| Graph -> Base | 45 |
| Concurrent -> Collections | 44 |
| IO -> Base | 43 |
| PrimitivesMath -> Base | 40 (25 primitives + 15 math) |
| Reflect -> Collections | 27 |
| Cache -> Base | 27 |
| EscapeNet -> Base | 26 (net 18 + escape 8) |
| Collections -> PrimitivesMath | 24 (17 + 7) |
| Reflect -> Base | 23 |
| Hash -> Base | 22 |
| EscapeNet -> Collections | 15 (net 12 + publicsuffix 3) |
| Cache -> Collections | 14 |
| Cache -> Concurrent | 11 |
| IO -> Collections | 10 |
| EventBus -> Base | 10 |
| Hash -> PrimitivesMath | 9 |
| IO -> Hash | 7 |
| EventBus -> Collections | 7 |

**Weak or surprising edges:**
- IO -> Graph (4): probably file-tree traversal via `Traverser`/`SuccessorsFunction`.
- Reflect -> IO (3): `ClassPath` reads resources.
- EventBus -> Cache (3): subscriber-method caching.
- EventBus -> Reflect (1): `TypeToken` flattening of event types.
- Net -> Hash (3), Net -> IO (2).

**Cycles:**
- **At package level the graph has no cycles.** No edge points back into `common.base`, `common.collect` or `common.primitives` from a higher package, and `base` depends only on `base.internal`.
- **Inside my splits, cycles are almost certain, but this is my estimate, not data.** C3, C4 and C5 depend on each other: `ImmutableMultimap` implements `Multimap`, `Maps`/`Sets` return immutable views, and `Multimaps` builds `ImmutableListMultimap`. Similarly, `ServiceManager` and `AbstractService` (C7) use `ListenableFuture` and `MoreExecutors` (C6), and C6 may use `Uninterruptibles` (C7). So the package boundary is acyclic, while the intra-package sub-components are not.

**Layered diagram** (a layer is the longest dependency path from Base; arrows point down):

```
L6                      +-----------+
                        | EventBus  |
                        +-----+-----+
                              | (cache, reflect, concurrent, collect, base)
L5        +---------+         |          +-----------+
          | Reflect |<--------+          | EscapeNet |
          +----+----+                    +-----+-----+
               | (io)                          | (io, hash, collect)
L4        +----v----+      +--------+          |
          |   IO    |      | Cache  |<---------+---(EventBus)
          +----+----+      +---+----+
               | (graph,hash)  | (concurrent, collect)
L3   +---------v+    +---------v---------------------------+
     |  Graph   |    | Concurrent: Futures <-> ServicesSync |
     +----+-----+    +---------------+-----------------------+
          |                          |
L2   +----v--------------------------v---------+   +--------+
     | Collections: Immutable <-> Types <->    |   |  Hash  |
     |              Utilities                  |   +---+----+
     +---------------------+-------------------+       |
                           | (24)                      | (9)
L1                  +------v---------------------------v-+
                    |       PrimitivesMath                |
                    +------------------+------------------+
                                       | (40)
L0  +----------------------------------v------------------+
    |                      Base                           |
    +-----------------------------------------------------+
   (almost every component also depends directly on Base)
```

## 4. Hubs

Total package-level edge weight in the file is 771 class dependencies.

**Hub packages:**
- **`common.base`** is the dominant hub. 12 of the 16 other packages use it, with 487 incoming dependencies (about 63% of all edges).
- **`common.collect`** is second: 8 packages and 182 incoming dependencies (about 24%). Together, base and collect receive about 87% of all edges.
- **`common.primitives`** has the widest reach after base: 10 packages use it, but only 39 dependencies in total.
- **`common.math`**: 6 packages, 17 dependencies.

Every other package has 13 or fewer incoming dependencies (`util.concurrent` 13, `hash` 10).

**Hub classes.** These are my estimates, because the data has no class-level counts:
- From base: `Preconditions`, `Objects`/`MoreObjects`, `Function`/`Predicate`/`Supplier`, `Optional`, `Ticker`, `Throwables`, `Joiner`/`Splitter`, `CharMatcher`.
- From collect: `ImmutableList`/`ImmutableSet`/`ImmutableMap`, `Iterables`/`Iterators`, `Lists`/`Maps`/`Sets`, `Ordering`, `Forwarding*`.
- From primitives and math: `Ints`/`Longs`, `IntMath`/`LongMath`.

## 5. Modularity assessment

**Strong points**
- **No package cycles.** The graph is a clean DAG with a clear layering: base, then primitives/math, then collect/hash, then concurrency/graph, then io/cache, then reflect/net, then eventbus.
- **`common.base` is a true foundation.** Its only outgoing dependency is its own `internal` sub-package (1 dependency).
- **Feature packages are cohesive and loosely coupled to each other.** Cache, eventbus, graph, hash, io, reflect and net mostly depend only on the foundation layers. Sideways edges between features are few and small (3–11).
- **Leaf packages are well isolated.** `html` and `xml` each depend only on `escape` (2 dependencies). `thirdparty.publicsuffix` is used only by `net`.
- **Deliberate duplication avoids coupling.** Internal helpers are repeated per package instead of shared: `Platform` (5 packages), `SneakyThrows` (4), `NullnessCasts` (3), `Internal` (3), `Java8Compatibility` (2). This keeps cross-package dependencies small.
- **Clear API vs. implementation split.** Public interfaces and factories (`Cache`/`CacheBuilder`, `Graph`/`GraphBuilder`, `HashFunction`/`Hashing`) hide implementation classes (`LocalCache`, `Standard*`, `Murmur3_*`).

**Weak points**
- **`common.collect` is a 209-class monolith.** It holds 38% of all classes and mixes interfaces, immutable implementations, mutable implementations, utilities and internals. Its internal parts are most likely tightly interdependent, so it cannot be split cleanly by package.
- **Very high fan-in on base and collect.** Any change there affects almost everything, and nobody can use a feature package (for example hash or io) without pulling in base, and usually collect too. Guava still ships as one jar.
- **`common.base` is a mixed bag.** It combines preconditions, strings, functional types, timing (`Stopwatch`/`Ticker`) and phantom-reference finalization (`Finalizable*`).
- **`util.concurrent` is also large (79 classes)** and combines futures, executors, service lifecycle and locking.
- **Some cross-feature edges are questionable:**
  - io -> graph (traversal),
  - eventbus -> cache and reflect,
  - net -> io and hash.

  These raise the layer height and couple features that users might want to use separately.
- **Duplication has costs.** There are duplicate names with different meanings: `AbstractIterator` in base and collect, `Hashing` in collect and hash, `ForwardingBlockingDeque` in collect and util.concurrent. There are also many per-package `Platform` classes. All of this causes confusion and maintenance overhead.
- **Package-private visibility forces internals into big packages.** Splitting them into sub-packages would require public API, which Guava avoids because of its compatibility promise (README: non-`@Beta` APIs stay binary-compatible indefinitely). The architecture is therefore frozen at the package level.
