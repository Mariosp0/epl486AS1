# P2 response – Guava 33.7.2

> P2 – README + package list (the agent read only the two attached files).
> Verbatim answer of a fresh Claude sub-agent (no conversation history, no access
> to the analysis results); see `guava/ai/prompts.md` for the procedure.

---

# Guava 33.7.2: an architectural reading based only on the README and package list

> **Caveat:** the two inputs list packages, class counts and a few class names. They do not show any import or dependency data. The dependencies below are therefore **inferred** from package names, class names and the README. They are a hypothesis to check against the source code, not a measured fact.

**Size summary:** 17 packages and 554 top-level classes. `common.collect` alone has 209 classes, about 38% of the total. `common.util.concurrent` has 79, about 14%.

---

## 1. Components (package grouping)

| # | Component | Packages (#classes) | Responsibility (from README and class names) |
|---|---|---|---|
| C1 | **Core Language Utilities** | `common.base` (48), `common.base.internal` (1) | Basic building blocks used everywhere: optional values (`Absent`), string and character handling (`Ascii`, `CaseFormat`, `CharMatcher`), `Charsets`, a basic `AbstractIterator`. `base.internal.Finalizer` handles resource cleanup. |
| C2 | **Primitives & Math** | `common.primitives` (23), `common.math` (14) | Helpers for primitive types (`Booleans`, `Bytes`, `Chars`, `Doubles`, `Floats`). Overflow-safe and exact arithmetic (`IntMath`, `DoubleMath`, `BigIntegerMath`, `BigDecimalMath`), plus simple statistics (`LinearTransformation`). |
| C3 | **Collections** | `common.collect` (209) | New collection types (multimap, multiset, bimap), immutable collections, and iterator and collection helpers (`AbstractBiMap`, `AbstractMapBasedMultimap`, …). The README calls this the main feature. |
| C4 | **Text Escaping** | `common.escape` (9), `common.html` (1), `common.xml` (1) | A general escaper framework (`Escaper`, `CharEscaper`, `ArrayBasedCharEscaper`, `CharEscaperBuilder`) with ready-made escapers for HTML and XML (`HtmlEscapers`, `XmlEscapers`). |
| C5 | **Networking / Internet Addressing** | `common.net` (7), `thirdparty.publicsuffix` (3) | Parsing and checking network identifiers (`HostAndPort`, `InetAddresses`, `InternetDomainName`, `MediaType`) and URL percent-escaping. `thirdparty.publicsuffix` holds the Public Suffix List data and trie that `InternetDomainName` uses. |
| C6 | **Hashing** | `common.hash` (31) | A hash-function abstraction and its implementations (`HashFunction`, `Hasher`, streaming and non-streaming hashers). |
| C7 | **I/O** | `common.io` (35) | Byte and character stream utilities and abstractions (`ByteSource`/`ByteSink`, `ByteArrayDataInput/Output`, `AppendableWriter`, `ByteProcessor`) and binary-to-text encodings (`BaseEncoding`). |
| C8 | **Reflection** | `common.reflect` (14) | Type tokens and type-safe reflection (`Invokable`, `Parameter`, `TypeToInstanceMap` variants), dynamic proxies (`AbstractInvocationHandler`), and classpath scanning (`ClassPath`). |
| C9 | **Concurrency** | `common.util.concurrent` (79) | Futures that support listeners and composition (`AbstractFuture`, `AbstractCatchingFuture`), executor decorators (`AbstractListeningExecutorService`), and service lifecycle management (`AbstractIdleService`, `AbstractExecutionThreadService`). |
| C10 | **Caching** | `common.cache` (19) | In-memory caches built with a builder (`CacheBuilder`, `CacheBuilderSpec`), including loading caches (`CacheLoader`, `AbstractLoadingCache`). |
| C11 | **Graph Library** | `common.graph` (52) | Graph and network data structures and their builders (`AbstractGraph`, `AbstractNetwork`, `AbstractGraphBuilder`, directed and undirected connections). |
| C12 | **Event Bus** | `common.eventbus` (8) | In-process publish/subscribe messaging (`EventBus`, `AsyncEventBus`, `Subscriber`, `Dispatcher`, `DeadEvent`). |
| (ext) | *failureaccess* (separate artifact) | n/a | The only runtime dependency, according to the README. Its name suggests it supports the futures code in C9, but the inputs do not confirm this. |

---

## 2. Layers and allowed dependencies

A strict layering is used. A component may depend on components in **lower** layers and, where stated, on peers in its own layer. It must never depend on a higher layer.

| Layer | Name | Components | Allowed to depend on |
|---|---|---|---|
| **L4** | Higher-level frameworks | C10 Caching, C11 Graph, C12 Event Bus | L3, L2, L1. Not on each other. |
| **L3** | Infrastructure services | C4 Escaping, C5 Networking, C6 Hashing, C7 I/O, C8 Reflection, C9 Concurrency | L2, L1. Peer dependencies only where clearly justified, and with no cycles. Examples: Networking → Escaping (percent-escaping); I/O ↔ Hashing in one direction only. |
| **L2** | Core data structures | C3 Collections | L1 only |
| **L1** | Foundation | C1 Core Language Utilities, C2 Primitives & Math | JDK only. Inside L1, Primitives & Math may use Base, but not the other way round. |
| **L0** | Platform | JDK 8+ / Android API 24+, failureaccess, annotation-only dependencies | n/a |

Rules:

1. **Downward only.** No package may import from a higher layer. For example, `collect` must not import `cache`, `graph` or `util.concurrent`.
2. **Foundation is a leaf.** `base`, `primitives` and `math` depend only on the JDK. Every other component can rely on them.
3. **`*.internal` is private.** `base.internal` may only be used by `base`, or at most by other Guava packages. It must never be used by client code.
4. **L4 components are independent of each other.** Cache, Graph and EventBus should never depend on one another, so each could in principle be split out on its own.
5. **Expected inferred dependencies:**
   - `cache` → `util.concurrent`: loading caches likely use futures.
   - `cache` → `collect`
   - `eventbus` → `util.concurrent` (executors for `AsyncEventBus`) and `collect` (subscriber registries).
   - `graph` → `collect`
   - `net` → `escape` (`PercentEscaper`) and `thirdparty.publicsuffix`.
   - `html`, `xml` → `escape`
   - `util.concurrent` → failureaccess.

---

## 3. Layered component diagram

```
+=====================================================================================+
| L4  HIGHER-LEVEL FRAMEWORKS                                                         |
|   +----------------+        +----------------+        +-----------------+          |
|   |  C10 Caching   |        |  C11 Graph     |        |  C12 Event Bus  |          |
|   |  common.cache  |        |  common.graph  |        | common.eventbus |          |
|   +-------+--------+        +-------+--------+        +--------+--------+          |
+===========|=========================|==========================|====================+
            | (futures)               |                          | (executors)
            v                         |                          v
+=====================================================================================+
| L3  INFRASTRUCTURE SERVICES                                                          |
|  +----------------------+ +-------------+ +-----------+ +-----------+ +-----------+ |
|  | C9 Concurrency       | | C7 I/O      | | C6 Hash   | | C8 Reflect| | C5 Net    | |
|  | common.util.concurrent| | common.io   | |common.hash| |common.    | |common.net | |
|  +----------+-----------+ +------+------+ +-----+-----+ | reflect   | |+thirdparty| |
|             |                    |              |       +-----+-----+ |.publicsuff| |
|             |                    |              |             |       +-----+-----+ |
|             |                    |              |             |             |       |
|             |                    |              |             |   +---------v-----+ |
|             |                    |              |             |   | C4 Escaping   | |
|             |                    |              |             |   | common.escape | |
|             |                    |              |             |   | .html  .xml   | |
|             |                    |              |             |   +-------+-------+ |
+=============|====================|==============|=============|===========|=========+
              |                    |              |             |           |
              v                    v              v             v           v
+=====================================================================================+
| L2  CORE DATA STRUCTURES                                                             |
|                     +---------------------------------------------+                 |
|                     |  C3 Collections   common.collect  (209!)    |                 |
|                     +----------------------+----------------------+                 |
+============================================|========================================+
                                             v
+=====================================================================================+
| L1  FOUNDATION                                                                       |
|   +------------------------------------+     +-------------------------------+      |
|   | C1 Core Language Utilities         |<----| C2 Primitives & Math          |      |
|   | common.base  (+ base.internal)     |     | common.primitives  common.math|      |
|   +------------------------------------+     +-------------------------------+      |
+=====================================================================================+
                                             |
                                             v
+=====================================================================================+
| L0  PLATFORM:  JDK 8+ (JRE flavor) | Android API 24+ (Android flavor)                |
|                failureaccess 1.0.3 (runtime) | annotation-only deps                  |
+=====================================================================================+

Legend:  A --> B  means "A may depend on B".  Every layer may also skip down to any
         lower layer (relaxed layering); for example, every component may use L1 directly.
```

---

## 4. Possible architectural smells

| # | Smell | Evidence | Why it matters / suggestion |
|---|---|---|---|
| 1 | **God package / low cohesion** | `common.collect` has 209 classes, about 38% of the library. Its contents range from multimaps, multisets and bimaps to immutable collections and iterator helpers. | It is hard to navigate, hard to test on its own and hard to split. A change in one area of it risks the rest. Possible sub-packages: `collect.immutable`, `collect.multimap`, `collect.iterators`, and so on. `util.concurrent` (79 classes: futures, executors and service lifecycle) shows the same pattern on a smaller scale. |
| 2 | **Fragmented concept / tiny packages** | Escaping is spread across four packages: `escape` (9 classes), `html` (1), `xml` (1), and `PercentEscaper` inside `net`. | A package holding a single class adds namespace overhead without adding cohesion. `HtmlEscapers` and `XmlEscapers` (and arguably `PercentEscaper`) could live under `escape`. |
| 3 | **Duplicated abstraction** | `AbstractIterator` exists in both `common.base` and `common.collect`. | Two classes with the same name and purpose in different layers confuse users and need duplicate maintenance. This suggests the layer boundary was drawn after the fact. |
| 4 | **"Kitchen-sink" foundation package** | `common.base` mixes optional values (`Absent`), ASCII and case conversion, character matching and `Charsets`. | Low cohesion in the most depended-upon package makes it unstable, because many unrelated reasons can cause changes. `Charsets` also overlaps with `common.io` and with the JDK's own `StandardCharsets`. |
| 5 | **Internal code exposed as a public package** | `common.base.internal.Finalizer` | Java packages give no real encapsulation without JPMS. A public `internal` package can still be reached by clients, which weakens the strong compatibility promise. |
| 6 | **Inconsistent package naming / namespace placement** | `common.util.concurrent` is nested under `util`, while every other package is flat under `common`. `thirdparty.publicsuffix` sits outside `common` altogether. | Irregular naming hides the structure. Bundling third-party data (the public suffix list) inside the same artifact couples Guava's releases to an external data source that changes often. |
| 7 | **Monolithic deployment unit** | One `guava` artifact contains unrelated frameworks: cache, graph, event bus, reflection and hashing. Meanwhile a tiny piece (`failureaccess`) has been split into its own artifact. | Clients take on the whole library and its binary-compatibility burden even if they use one class. Modularisation is inconsistent: a small part was split out while large independent features were not. The independent L4 components are natural candidates for separate modules. |
| 8 | **Platform-specific code in the core / parallel codebases** | `DoublesMethodsForWeb` in `primitives`. The README describes two flavors (JRE and Android), with the Android one kept in a separate `android` source directory. It also warns that `common.io` may not work correctly on non-Linux platforms. | Concerns for specific platforms (web, Android, OS) leak into what should be portable core packages. Keeping two parallel source trees is a duplication and divergence risk. |
| 9 | **Stability boundaries not aligned with package boundaries** | `@Beta` is applied per class or method, not per package, and stable and unstable APIs sit side by side. | Users need an external tool (Guava Beta Checker) to stay safe. An architectural boundary, such as separate packages or modules for incubating APIs, would make stability visible. |
| 10 | **Inheritance-heavy public API** | Many published `Abstract*` base classes (`AbstractFuture`, `AbstractCache`, `AbstractGraph`, `AbstractHasher`, `AbstractMapBasedMultimap`, …), combined with the README's promise of binary compatibility for the indefinite future. | Every public abstract class becomes a fixed extension point (the fragile base-class problem). Together with the "never remove" policy, this makes the internals very hard to refactor. |
| 11 | **Fixed serialization and trust model** | The README warns that serialized forms of all objects may change and that classes are not hardened against malicious callers. | This is not a structural smell, but it is a quality-attribute constraint for any architecture that uses Guava across process or trust boundaries. |
| 12 | **Documentation drift** | The README's examples use version **33.7.0**, while the package list is for **33.7.2**. | This is a minor point, but it shows the documentation is not generated from the build. |

**Overall:** Guava looks like a **utility library with a rough layered structure**: a foundation, then collections, then infrastructure services, then frameworks. Its main architectural risks are **size imbalance** (`collect`, `util.concurrent`), **fragmented or duplicated concepts** (escaping, `AbstractIterator`), and a **monolithic artifact** whose layers are not enforced. Confirming the inferred dependency directions, especially that no cycles exist between L3 peers and that `collect` does not depend upward, needs import-level analysis of the source code.
