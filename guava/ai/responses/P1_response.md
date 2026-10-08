# P1 response – Guava 33.7.2

> P1 – zero context (no attachments; the agent used no tools).
> Verbatim answer of a fresh Claude sub-agent (no conversation history, no access
> to the analysis results); see `guava/ai/prompts.md` for the procedure.

---

# Architecture of Google Guava (target: v33.7.2)

> **Caveat on the version:** The last Guava releases I know well are in the 33.x line (33.0 through about 33.4/33.5, 2024–2025). I cannot confirm that **33.7.2** exists or what it changed. The description below is based on the 33.x architecture, which has been very stable for years: new releases mostly add methods, mark things deprecated, and change build or Java-baseline details. Treat anything version-specific as unverified.

---

## 0. Repository / build-level view

| Artifact / module | Role |
|---|---|
| `guava` | The main library, JRE flavour (Java 8+ baseline; targets newer JDKs where available) |
| `android/guava` | **Android flavour**: a parallel source tree with the same packages, minus APIs that need Java 8+ library features Android lacks (some `Stream`/`java.time` usages). Published as `-android` |
| `guava-testlib` | Test support: collection test-suite builders (`CollectionTestSuiteBuilder`, `MapTestSuiteBuilder`…), `EqualsTester`, `NullPointerTester`, `ClassSanityTester`, `FakeTicker`, `GcFinalization`, `SerializableTester` |
| `guava-tests` | Guava's own tests |
| `guava-gwt` | GWT (GWT-compatible) variants and super-source. **Unsure** whether it still ships in 33.7; GWT support has been shrinking |
| `failureaccess` | Tiny separate jar holding `InternalFutureFailureAccess` (split out so `ListenableFuture` can be shared) |
| `listenablefuture` (9999.0-empty-to-avoid-conflict-with-guava) | Empty placeholder artifact that avoids duplicate `ListenableFuture` classes on Android |
| `guava-bom` | Maven BOM |
| Annotations deps | JSpecify (`@NullMarked`/`@Nullable`, adopted in 33.x), Error Prone annotations, J2ObjC annotations. `com.google.common.annotations` holds `@Beta`, `@GwtCompatible`, `@GwtIncompatible`, `@J2ktIncompatible`, `@VisibleForTesting` |

Since 33.x the main jar also ships a **JPMS `module-info`** (`com.google.common`). I am fairly but not fully sure about when that landed (around 33.4).

---

## 1. Main architectural components (Java packages under `com.google.common`)

### 1.1 Foundation
| Component | Responsibility | Key types |
|---|---|---|
| **`annotations`** | Compatibility and stability markers | `@Beta`, `@GwtCompatible`, `@GwtIncompatible`, `@VisibleForTesting`, `@J2ktIncompatible` |
| **`base`** | Core utilities used by everything else: preconditions, functional types, string helpers, Optional, timing | `Preconditions`, `Verify`, `Objects`/`MoreObjects` (`toStringHelper`), `Optional`, `Function`, `Supplier`/`Suppliers` (`memoize`), `Predicate`/`Predicates`, `Functions`, `Joiner`, `Splitter`, `CharMatcher`, `Strings`, `Ascii`, `CaseFormat`, `Converter`, `Equivalence`, `Stopwatch`, `Ticker`, `Throwables`, `Charsets`, `Enums`, `Defaults`, `FinalizableReferenceQueue` |
| **`base.internal`** | `Finalizer`, loaded in a separate class loader for `FinalizableReferenceQueue` | `Finalizer` |

### 1.2 Data-structure layer
| Component | Responsibility | Key types |
|---|---|---|
| **`collect`** (the largest package by far) | Immutable collections, new collection types, collection utilities, ordering | **Immutable**: `ImmutableCollection`, `ImmutableList`, `ImmutableSet`, `ImmutableSortedSet`, `ImmutableMap`, `ImmutableSortedMap`, `ImmutableBiMap`, `ImmutableMultimap`/`ImmutableListMultimap`/`ImmutableSetMultimap`, `ImmutableMultiset`, `ImmutableTable`, `ImmutableRangeSet`/`RangeMap`, `RegularImmutable*`/`SingletonImmutable*` implementations. **New types**: `Multiset`, `Multimap`, `ListMultimap`, `SetMultimap`, `BiMap`, `Table`, `RangeSet`, `RangeMap`, `Range`, `ClassToInstanceMap`, `SortedMultiset`. **Implementations**: `HashMultimap`, `ArrayListMultimap`, `LinkedHashMultimap`, `TreeMultimap`, `HashMultiset`, `TreeMultiset`, `ConcurrentHashMultiset`, `HashBiMap`, `HashBasedTable`, `TreeBasedTable`, `ArrayTable`, `TreeRangeSet`, `MinMaxPriorityQueue`, `EvictingQueue`, `Interner`/`Interners`. **Utilities**: `Lists`, `Sets`, `Maps`, `Multimaps`, `Multisets`, `Iterables`, `Iterators`, `FluentIterable`, `Collections2`, `Queues`, `Tables`, `Streams`, `MoreCollectors`, `Comparators`, `Ordering`, `ComparisonChain`, `ContiguousSet`, `DiscreteDomain`. **Extension SPI**: `Forwarding*` classes, `AbstractIterator`, `UnmodifiableIterator`, `AbstractSequentialIterator`, `PeekingIterator`. **Infrastructure**: `MapMaker`/`MapMakerInternalMap`, `CollectPreconditions`, `Hashing` (internal), `ObjectArrays` |
| **`primitives`** | Utilities and immutable arrays for primitive types; unsigned arithmetic | `Ints`, `Longs`, `Shorts`, `Bytes`, `Chars`, `Doubles`, `Floats`, `Booleans`, `SignedBytes`, `UnsignedBytes`, `UnsignedInts`, `UnsignedLongs`, `UnsignedInteger`, `UnsignedLong`, `ImmutableIntArray`/`ImmutableLongArray`/`ImmutableDoubleArray`, `Primitives` |
| **`math`** | Overflow-checked and rounding integer/float math, statistics | `IntMath`, `LongMath`, `BigIntegerMath`, `DoubleMath`, `BigDecimalMath`, `Stats`, `StatsAccumulator`, `PairedStats`, `Quantiles`, `LinearTransformation` |
| **`graph`** | Graph data structures (`@Beta` for a long time) | `Graph`, `ValueGraph`, `Network`, `MutableGraph`/`MutableValueGraph`/`MutableNetwork`, `GraphBuilder`, `ValueGraphBuilder`, `NetworkBuilder`, `ImmutableGraph`…, `EndpointPair`, `ElementOrder`, `Graphs`, `Traverser`, `SuccessorsFunction`/`PredecessorsFunction`, internal `ConfigurableValueGraph`, `GraphConnections` |

### 1.3 Service layer (higher-level infrastructure)
| Component | Responsibility | Key types |
|---|---|---|
| **`cache`** | In-memory caching with loading, eviction, expiry and stats. Superseded in practice by Caffeine, but still maintained | `Cache`, `LoadingCache`, `CacheBuilder`, `CacheBuilderSpec`, `CacheLoader`, `LocalCache` (segmented, ConcurrentHashMap-like core), `RemovalListener`/`RemovalNotification`/`RemovalCause`, `Weigher`, `CacheStats`, `AbstractCache`, `ForwardingCache` |
| **`util.concurrent`** | Futures, executors, services, rate limiting, concurrency helpers | `ListenableFuture`, `AbstractFuture` (+ `AbstractFutureState` and `AggregateFuture` internals), `SettableFuture`, `Futures`, `FluentFuture`, `ClosingFuture`, `FutureCallback`, `ListeningExecutorService`, `MoreExecutors`, `ListeningScheduledExecutorService`, `Service`, `AbstractService`, `AbstractIdleService`, `AbstractExecutionThreadService`, `AbstractScheduledService`, `ServiceManager`, `RateLimiter`/`SmoothRateLimiter`, `Monitor`, `Striped`, `CycleDetectingLockFactory`, `AtomicDouble`, `AtomicLongMap`, `ThreadFactoryBuilder`, `Uninterruptibles`, `TimeLimiter`/`SimpleTimeLimiter`, `ExecutionSequencer`, `ExecutionList`, `SequentialExecutor` |
| **`hash`** | Non-cryptographic and cryptographic hashing, Bloom filters | `HashFunction`, `Hasher`, `HashCode`, `Hashing` (murmur3, sipHash24, farmHash, crc32c, sha256, goodFastHash…), `Funnel`/`Funnels`, `PrimitiveSink`, `BloomFilter`/`BloomFilterStrategies`, `AbstractHashFunction`, `AbstractStreamingHasher`, `HashingInputStream`/`OutputStream`, `LongAddable` |
| **`io`** | Source/sink I/O abstraction, encodings, file and resource helpers | `ByteSource`, `ByteSink`, `CharSource`, `CharSink`, `Files`, `MoreFiles`, `Resources`, `ByteStreams`, `CharStreams`, `BaseEncoding` (base64/32/16), `Closer`, `LineProcessor`, `ByteProcessor`, `CountingInputStream`, `LittleEndianDataInputStream`, `FileWriteMode`, `RecursiveDeleteOption` |
| **`eventbus`** | In-process publish/subscribe (now discouraged by the Guava team) | `EventBus`, `AsyncEventBus`, `@Subscribe`, `@AllowConcurrentEvents`, `Subscriber`, `SubscriberRegistry`, `Dispatcher`, `DeadEvent`, `SubscriberExceptionHandler` |

### 1.4 Specialised / auxiliary components
| Component | Responsibility | Key types |
|---|---|---|
| **`reflect`** | Generic type tokens, invocation helpers, classpath scanning | `TypeToken`, `TypeResolver`, `Types`, `TypeCapture`, `Invokable`, `Parameter`, `Reflection` (`newProxy`), `AbstractInvocationHandler`, `ClassPath`, `ImmutableTypeToInstanceMap`, `MutableTypeToInstanceMap` |
| **`net`** | Network-related value types | `HostAndPort`, `InetAddresses`, `InternetDomainName`, `MediaType`, `HttpHeaders`, `UrlEscapers`, `PercentEscaper`, `HostSpecifier` |
| **`escape`** | Escaping framework | `Escaper`, `CharEscaper`, `UnicodeEscaper`, `Escapers`, `ArrayBasedCharEscaper`, `CharEscaperBuilder` |
| **`html`, `xml`** | Concrete escapers | `HtmlEscapers`, `XmlEscapers` |
| **`thirdparty.publicsuffix`** | Generated public-suffix data used by `InternetDomainName` | `PublicSuffixPatterns`, `PublicSuffixType` |

---

## 2. Dependencies between components

Dependencies are mostly hierarchical and acyclic **at the package level**, with a few known exceptions. Edges listed are the important ones; I have not checked them against the 33.7.2 import graph.

- **`base`** depends only on the JDK (plus `annotations`). Everything else depends on `base`, mainly `Preconditions`, `Function`/`Supplier`/`Predicate`, `Objects`, `Ticker` and `Optional`.
- **`primitives`** → `base`. There is a small mutual coupling with `collect`: `Ints.asList`, and `ImmutableIntArray` interacting with lists. I'm unsure how strong the `primitives → collect` edge is.
- **`math`** → `base`, `primitives`. `Quantiles`/`Stats` use `primitives` (`Doubles`).
- **`collect`** → `base`, `primitives`, `math` (`IntMath` for capacity and overflow). `collect` also uses `j2objc`/Error Prone annotations.
- **`graph`** → `collect`, `base`, `math`.
- **`escape`** → `base`. **`html`/`xml`** → `escape`. **`net`** → `escape`, `base`, `collect`, `primitives`, `hash` (`MediaType`?), `thirdparty.publicsuffix`. The `net → hash` edge is uncertain.
- **`hash`** → `base`, `primitives`, `math` (`BloomFilter` sizing). `BloomFilter` uses `util.concurrent`-style atomic arrays (`LongAddable`/`AtomicLongArray`).
- **`io`** → `base`, `collect`, `hash` (`ByteSource.hash`), `math`, `primitives`.
- **`util.concurrent`** → `base`, `collect`, `primitives`, `math`. It also depends on the separate `failureaccess` artifact.
- **`cache`** → `base` (`Ticker`, `Supplier`, `Equivalence`, `Stopwatch`), `collect`, `util.concurrent` (`ListenableFuture`, `SettableFuture`, `Futures`, `Uninterruptibles`, `ExecutionError`, `UncheckedExecutionException`), `primitives`, `math`.
- **`eventbus`** → `base`, `collect`, `util.concurrent` (`MoreExecutors.directExecutor`), `reflect` (`TypeToken` to resolve subscriber event types), `cache` (`LoadingCache` caches subscriber methods per class in `SubscriberRegistry`).
- **`reflect`** → `base`, `collect`, `primitives`, `io` (`ClassPath` reads JARs/resources).
- **`base`**: `FinalizableReferenceQueue` loads `base.internal.Finalizer` reflectively, through a separate class loader. This deliberately avoids a static dependency.
- **`guava-testlib`** → `guava` (all packages), JUnit, Truth (**partly**; I'm unsure of the exact current test-dependency set).

Notable cross-cutting coupling: **`collect` ↔ `util.concurrent`** is avoided in one direction (`collect` does not use futures). `MapMaker` in `collect` and `LocalCache` in `cache` are structurally similar but separate implementations.

---

## 3. Layered component diagram

```
+--------------------------------------------------------------------------------+
|                     CLIENT APPLICATIONS / OTHER LIBRARIES                       |
+--------------------------------------------------------------------------------+
        |  (public, mostly static-factory / builder APIs)
        v
+--------------------------------------------------------------------------------+
| L4  HIGH-LEVEL FRAMEWORK SERVICES                                              |
|   +------------+    +-------------+                                            |
|   |  eventbus  |--->|   cache     |   (eventbus uses LoadingCache + reflect)   |
|   +------------+    +-------------+                                            |
|         |                 |                                                    |
+---------|-----------------|----------------------------------------------------+
          v                 v
+--------------------------------------------------------------------------------+
| L3  INFRASTRUCTURE SERVICES                                                    |
|  +-------------------+  +--------+  +--------+  +---------+  +------------+    |
|  | util.concurrent   |  |   io   |->|  hash  |  | reflect |->|    io      |    |
|  | (futures,services,|  +--------+  +--------+  +---------+  +------------+    |
|  |  RateLimiter...)  |                                                         |
|  +-------------------+  +------------------------------------------------+     |
|        |                |  net --> escape <-- html, xml                  |     |
|        |                |   \--> thirdparty.publicsuffix                 |     |
|        |                +------------------------------------------------+     |
+--------|-----------------------------------------------------------------------+
         v
+--------------------------------------------------------------------------------+
| L2  DATA STRUCTURES & ALGORITHMS                                               |
|   +--------------------+   +---------+                                         |
|   |   graph            |-->| collect |  (Immutable*, Multimap, Multiset,       |
|   +--------------------+   +---------+   BiMap, Table, Range, Ordering ...)    |
|                                 |                                              |
|                     +-----------+-----------+                                  |
|                     v                       v                                  |
|               +-----------+          +-------------+                           |
|               |   math    |--------->| primitives  |                           |
|               +-----------+          +-------------+                           |
+--------------------------------------------------------------------------------+
         |
         v
+--------------------------------------------------------------------------------+
| L1  FOUNDATION                                                                 |
|   base  (Preconditions, Optional, Function/Supplier/Predicate, Joiner,         |
|          Splitter, CharMatcher, Stopwatch/Ticker, Throwables, Equivalence)     |
|   base.internal (Finalizer - loaded reflectively)                              |
|   annotations  (@Beta, @GwtCompatible, @VisibleForTesting, ...)                |
+--------------------------------------------------------------------------------+
         |
         v
+--------------------------------------------------------------------------------+
| L0  PLATFORM & EXTERNAL                                                        |
|   JDK (java.util, java.util.concurrent, java.lang.ref, java.nio)               |
|   failureaccess.jar | JSpecify | Error Prone annotations | j2objc annotations  |
+--------------------------------------------------------------------------------+

  Side artifacts (outside the runtime layers):
    guava-testlib  --> guava (all layers), JUnit, Truth
    android/guava  == parallel flavour of the same layered structure
    guava-gwt      == GWT super-source variants (status in 33.7 unsure)
    guava-bom      == version alignment
```

This is a **relaxed** layering: higher layers may call any lower layer directly. For example, `cache` uses `base.Ticker` directly.

---

## 4. Architectural styles and design patterns

### Architectural styles
- **Library / toolkit architecture**: no runtime, no main loop, no container. It is a set of loosely coupled utility packages.
- **Relaxed layered architecture**: `base` at the bottom, data structures in the middle, services on top.
- **Modular, package-by-feature decomposition**: each package is a cohesive feature area with its own public API and package-private internals.
- **Product-line / multi-flavour variant management**: JRE, Android and GWT/J2CL/J2ObjC targets are built from parallel source trees (`android/`), annotations (`@GwtIncompatible`, `@J2ktIncompatible`) and super-source.
- **Immutability-first, value-oriented design**: a functional style (`Function`, `Predicate`, `FluentIterable`, `FluentFuture`).
- **Publish-subscribe** (`eventbus`) and **asynchronous, callback-based (future/promise) style** (`util.concurrent`).
- **API-stability policy as architecture**: `@Beta` marks unstable APIs, and deprecation precedes removal.

### Design patterns (with examples)
| Pattern | Where |
|---|---|
| **Static Factory Method** (everywhere) | `ImmutableList.of`, `Lists.newArrayList`, `Hashing.murmur3_128`, `Optional.of`, `MediaType.create` |
| **Builder** | `ImmutableList.Builder`, `ImmutableMap.Builder`, `CacheBuilder`, `MapMaker`, `GraphBuilder`/`NetworkBuilder`, `ThreadFactoryBuilder`, `MultimapBuilder`, `CharEscaperBuilder`, `MoreObjects.ToStringHelper` |
| **Fluent Interface** | `FluentIterable`, `FluentFuture`, `Splitter`/`Joiner` (`.omitEmptyStrings().trimResults()`), `Ordering` |
| **Immutable Object / Value Object** | `Immutable*` collections, `HashCode`, `HostAndPort`, `MediaType`, `Range`, `UnsignedInteger` |
| **Decorator / Forwarding** | `ForwardingList`, `ForwardingMap`, `ForwardingCache`, `ForwardingListenableFuture`, `ForwardingExecutorService`, `Collections2.filter`/`Lists.transform` (views) |
| **View / Proxy (live views)** | `Maps.filterKeys`, `Multimap.asMap()`, `Sets.union`, `Lists.reverse`, `Iterables.concat`; `Reflection.newProxy` (dynamic proxy) |
| **Adapter** | `Converter`, `MoreExecutors.listeningDecorator`, `JdkFutureAdapters`, `Funnel`, `Ints.asList`, `ByteSource.asCharSource` |
| **Template Method** | `AbstractService` (`doStart`/`doStop`), `AbstractIterator.computeNext`, `AbstractFuture`, `AbstractExecutionThreadService.run`, `AbstractScheduledService`, `CacheLoader.load`, `AbstractInvocationHandler`, `AbstractHashFunction` |
| **Strategy** | `Equivalence`, `Ordering`/`Comparator`, `CharMatcher`, `Weigher`, `RemovalListener`, `Dispatcher` (EventBus), `BloomFilterStrategies`, `DiscreteDomain`, `ElementOrder`, `Ticker` (testable time) |
| **Observer / Publish-Subscribe** | `EventBus` + `@Subscribe`; `ListenableFuture.addListener`/`FutureCallback`; `Service.Listener`; `ServiceManager.Listener`; `RemovalListener` |
| **State (state machine)** | `Service.State` lifecycle in `AbstractService` (NEW → STARTING → RUNNING → STOPPING → TERMINATED/FAILED); `AbstractFuture` state via CAS |
| **Singleton / Flyweight** | Empty immutable singletons (`RegularImmutableList.EMPTY`), `Optional.absent()`, `CharMatcher` constants, `Interners` (flyweight/interning), cached `Hashing` instances (enum-holder singletons) |
| **Null Object** | `Optional.absent()`, `MoreExecutors.directExecutor()`, `NullOutputStream` (`ByteStreams.nullOutputStream`), no-op `RemovalListener`s |
| **Iterator** | `AbstractIterator`, `PeekingIterator`, `UnmodifiableIterator`, `Traverser` (graph traversals) |
| **Composite** | `Predicates.and/or`, `CharMatcher.or/and`, `Funnels.sequentialFunnel`, `Hashing.concatenating` |
| **Memoization / Lazy Initialization / Proxy** | `Suppliers.memoize`, `LoadingCache`, lazily computed `hashCode`/`asList` in immutables |
| **Facade / Utility-class ("static helper") pattern** | `Lists`, `Maps`, `Futures`, `MoreExecutors`, `Files`, `Hashing`, `Preconditions` |
| **Resource management (Disposer)** | `Closer`, `ClosingFuture` |
| **Token Bucket algorithm** | `RateLimiter`/`SmoothRateLimiter` (`SmoothBursty`, `SmoothWarmingUp`) |
| **Lock striping / segmentation** | `Striped`, `LocalCache` segments, `MapMakerInternalMap` |
| **Serialization Proxy (Effective Java)** | `ImmutableCollection.SerializedForm`, `writeReplace` in immutables |
| **Type Token (super-type token)** | `TypeToken`, `TypeCapture` |

---

## 5. Explicit uncertainties

1. **Version 33.7.2**: I cannot verify that this release exists or what it changed. The analysis reflects the 33.x architecture as I know it, up to roughly 33.4–33.5.
2. **Exact dependency edges**: package-level edges come from memory of usage, not from a dependency-analysis tool. Edges I'm least sure of are `net → hash`, `primitives → collect`, and the precise reach of `reflect → io`. Use a tool such as jdeps, Structure101 or Sonargraph to confirm.
3. **Cycles**: Guava has historically had a few package-level cycles, notably between `collect` and `primitives`/`math`, and possibly `base` ↔ `collect` through internal helpers. My diagram shows a clean ordering that may be idealised.
4. **Module status**: I don't know the current status of `guava-gwt`, of J2CL/J2ObjC/Kotlin-Native (`@J2ktIncompatible`) support, or of the `module-info` details in this version.
5. **`@Beta` status**: some APIs, such as `graph` and parts of `util.concurrent` and `reflect`, may have graduated from or stayed in `@Beta`. I can't confirm the 33.7.2 status.
6. **Internal class names**: names such as `AbstractFutureState`, `AggregateFuture`, `LocalCache`, `MapMakerInternalMap` and `RegularImmutable*` are subject to refactoring and may differ in this release.
7. **Layer assignment**: putting `reflect`, `net` and `io` in "L3" and `cache`/`eventbus` in "L4" is my own architectural interpretation, not something Guava documents.
