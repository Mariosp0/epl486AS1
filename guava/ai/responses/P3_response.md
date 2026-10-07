# P3 response (README + packages + all classes + package dependency graph)

## 1. Components and class mapping

14 components. `common.collect` (209 classes) is split into four
sub-components by the role of its classes; every other package maps to one
component. Ordered rules over `package.ClassName` (prefix `com.google.`
removed), first match wins – also stored as `guava/ai/ai_architecture_P3.json`:

```json
[
  ["Graph library", "^common\\.graph\\..*"],
  ["Caching", "^common\\.cache\\..*"],
  ["Concurrency (futures, services, executors)", "^common\\.util\\.concurrent\\..*"],
  ["Event bus", "^common\\.eventbus\\..*"],
  ["Reflection", "^common\\.reflect\\..*"],
  ["I/O", "^common\\.io\\..*"],
  ["Hashing", "^common\\.hash\\..*"],
  ["Escaping, networking & public suffix", "^common\\.(escape|html|xml|net)\\..*|^thirdparty\\..*"],
  ["Primitives & math", "^common\\.(primitives|math)\\..*"],
  ["Ranges & discrete domains", "^common\\.collect\\.(Range|RangeMap|RangeSet|AbstractRangeSet|TreeRangeMap|TreeRangeSet|ImmutableRangeMap|ImmutableRangeSet|Cut|BoundType|DiscreteDomain|ContiguousSet|RegularContiguousSet|EmptyContiguousSet|GeneralRange)$"],
  ["Immutable collections", "^common\\.collect\\.(Immutable|Regular|Singleton|Empty|JdkBacked|Dense|Sparse|Descending|Indexed)\\w*$|^common\\.collect\\.BaseImmutableMultimap$"],
  ["Multi-collections (Multimap, Multiset, BiMap, Table)", "^common\\.collect\\.\\w*(Multimap|Multiset|BiMap|Table)\\w*$"],
  ["Collection utilities, views & ordering", "^common\\.collect\\..*"],
  ["Base utilities", ".*"]
]
```

Ordering rationale: range types are matched before the immutable rule
(`ImmutableRangeSet`, `RegularContiguousSet` belong to the range
abstraction); immutable implementations (`Regular*`, `Singleton*`, `Empty*`,
`JdkBacked*`, `Dense/SparseImmutableTable`) are matched before the
multi-collection rule so that `ImmutableMultimap` & co. stay with the
immutable family; the remaining `collect` classes are the general
utilities (`Lists`, `Maps`, `Sets`, `Iterables`, `Iterators`,
`FluentIterable`, `Ordering`, `Forwarding*`, `Compact*`, `MapMaker`).

## 2. Responsibilities and key classes

| Component | Classes | Responsibility | Key classes |
|---|---|---|---|
| Base utilities | 47 | Argument checking, functional types, strings, `Optional`, timing | `Preconditions`, `Function`, `Predicate`, `MoreObjects`, `Joiner`, `Splitter`, `CharMatcher`, `Stopwatch` |
| Primitives & math | 37 | Primitive arrays/unsigned types; checked integer maths, statistics | `Ints`, `Longs`, `UnsignedLong`, `IntMath`, `LongMath`, `Stats` |
| Collection utilities, views & ordering | 85 | Static utilities, views, iterators, forwarding decorators, ordering, internal hash tables | `Lists`, `Maps`, `Sets`, `Iterators`, `Iterables`, `FluentIterable`, `Ordering`, `ForwardingCollection`, `CompactHashMap` |
| Immutable collections | 48 | Immutable list/set/map/multimap/table families and their specialised implementations | `ImmutableCollection`, `ImmutableList`, `ImmutableMap`, `RegularImmutableMap`, `SingletonImmutableList` |
| Multi-collections | 61 | New collection types and their implementations | `Multimap`, `Multiset`, `BiMap`, `Table`, `HashMultimap`, `TreeMultiset`, `Multimaps`, `Tables` |
| Ranges & discrete domains | 15 | Interval arithmetic over comparables | `Range`, `RangeSet`, `TreeRangeSet`, `DiscreteDomain`, `ContiguousSet`, `Cut` |
| Concurrency | 78 | Listenable futures, combinators, executors, services, synchronisation | `ListenableFuture`, `AbstractFuture`, `Futures`, `MoreExecutors`, `Service`, `RateLimiter`, `Monitor` |
| Caching | 19 | Loading cache with eviction/refresh | `CacheBuilder`, `LocalCache`, `LoadingCache`, `CacheLoader` |
| Graph library | 52 | Graph, value graph and network types, traversal | `Graph`, `ValueGraph`, `Network`, `GraphBuilder`, `EndpointPair`, `Traverser` |
| I/O | 34 | Sources/sinks, streams, files, encodings | `ByteSource`, `CharSource`, `Files`, `BaseEncoding`, `Closer` |
| Hashing | 31 | Hash functions, hash codes, Bloom filter | `Hashing`, `HashFunction`, `HashCode`, `BloomFilter`, `Funnel` |
| Escaping, networking & public suffix | 21 | Escapers, HTML/XML escaping, media types, host/domain names | `Escaper`, `CharEscaper`, `MediaType`, `InternetDomainName`, `InetAddresses` |
| Reflection | 13 | Type tokens, class path, invokables | `TypeToken`, `ClassPath`, `Invokable` |
| Event bus | 8 | Publish/subscribe | `EventBus`, `Subscriber`, `Dispatcher` |

(class counts = classes with at least one dependency)

## 3. Dependencies between components

Strongest aggregated dependencies (class-level):

| From → To | # |
|---|---|
| Multi-collections → Collection utilities | 148 |
| Immutable collections → Collection utilities | 125 |
| Collection utilities → Base utilities | 76 |
| Concurrency → Base utilities | 67 |
| Multi-collections → Base utilities | 57 |
| Graph → Base / Collection utilities / Immutable | 45 / 37 / 20 |
| I/O → Base utilities | 43 |
| Immutable collections → Multi-collections | 42 |
| Ranges → Collection utilities | 41 |
| Collection utilities → Immutable collections | 37 |

Cycles exist **only inside the collections subsystem**: Collection utilities ⇄
Immutable (125/37), ⇄ Multi-collections (148/18), ⇄ Ranges (41/7) and
Immutable ⇄ Multi-collections (42/10), Immutable ⇄ Ranges (4/21). This is
expected: the utilities (`Maps`, `Sets`, `Multimaps`) create immutable and
multi-collections, and those reuse the utilities. Between the other
components the graph is acyclic.

```
 ┌──────────────────────────────────────────────────────────────────────┐
 │ L4  Graph (52) │ Caching (19) │ Reflection (13) │ Event bus (8) │ I/O (34) │
 └──────┬───────────────┬────────────────────────────────────┬─────────┘
        │        ┌──────▼─────────┐                          │
 L3     │        │ Concurrency(78)│        Hashing (31) ◄────┘
        │        └──────┬─────────┘        Escaping/net (21)
 ┌──────▼───────────────▼─────────────────────────────────────────────┐
 │ L2  Collections subsystem (cyclic inside):                          │
 │     Immutable (48) ⇄ Utilities/views/ordering (85) ⇄ Multi (61)     │
 │                          ⇄ Ranges (15)                              │
 └──────┬──────────────────────────────────────────────────────────────┘
 ┌──────▼──────────────────────┐
 │ L1  Primitives & math (37)  │
 └──────┬──────────────────────┘
 ┌──────▼──────────────────────────────────────────────────────────────┐
 │ L0  Base utilities (47): Preconditions, Function, Predicate, ...     │
 └──────────────────────────────────────────────────────────────────────┘
```

## 4. Hubs

* Packages: `common.base` is used by 12 of the other 16 packages,
  `common.primitives` by 10, `common.collect` by 8.
* Classes: `Preconditions` is by far the most used class; then the core
  collection types and utilities `ImmutableList`, `UnmodifiableIterator`,
  `Maps`, `ImmutableSet`, `Iterators`, `ImmutableMap`, `Ordering`, `Multiset`,
  `CollectPreconditions`, plus `Function`, `Predicate`, `Ints`,
  `MoreObjects` and `ListenableFuture`. These are the omnipresent classes
  that a noise filter should remove.

## 5. Modularity assessment

* **Strong:** a clean layering – foundation → numerics → collections →
  concurrency → feature libraries; feature packages (graph, cache, io,
  hash, net, reflect, eventbus) are leaves that never depend on each other
  except Caching → Concurrency and I/O → Hashing/Graph (a few classes).
  Package-by-feature makes the public API easy to discover.
* **Weak:** `common.collect` is one package of 209 classes with internal
  cycles between its sub-parts; its encapsulation relies on package-private
  visibility, so it cannot be split without making internals public. Base
  (`Preconditions`) and collect are hubs on which everything depends, so a
  change there ripples through the whole library (mitigated by Guava's
  strict API-compatibility policy).
