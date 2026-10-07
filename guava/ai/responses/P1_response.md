# P1 response (zero context)

> Caveat from the assistant: I have no access to the 33.7.0 sources here; the
> answer is based on general knowledge of Guava and may miss recent changes.

## 1. Components

| Component | Responsibility | Key types |
|---|---|---|
| **Base** (`com.google.common.base`) | Foundational utilities used by everything: preconditions, `Optional`, functional interfaces, string handling, `Objects`/`MoreObjects`, `Stopwatch`, `Ticker`, `Suppliers` | `Preconditions`, `Optional`, `Function`, `Predicate`, `Joiner`, `Splitter`, `CharMatcher`, `Strings`, `Throwables`, `Verify` |
| **Collections** (`collect`) | The largest part: immutable collections, new collection types, collection utilities and ordering | `ImmutableList/Set/Map`, `Multimap`, `Multiset`, `BiMap`, `Table`, `Range`, `RangeSet`, `Lists`, `Maps`, `Sets`, `Iterables`, `FluentIterable`, `Ordering` |
| **Primitives** (`primitives`) | Utilities and unsigned types for Java primitives | `Ints`, `Longs`, `UnsignedInteger`, `UnsignedLong` |
| **Math** (`math`) | Overflow-checked and rounding integer/double maths, statistics | `IntMath`, `LongMath`, `BigIntegerMath`, `Stats`, `Quantiles` |
| **Concurrency** (`util.concurrent`) | `ListenableFuture` and future combinators, services, executors, rate limiting, striped locks | `ListenableFuture`, `Futures`, `SettableFuture`, `MoreExecutors`, `Service`, `RateLimiter`, `Striped`, `Monitor` |
| **Caching** (`cache`) | In-memory loading cache | `CacheBuilder`, `LoadingCache`, `CacheLoader`, `LocalCache` |
| **I/O** (`io`) | Byte/char sources and sinks, files, resources, encoding | `ByteSource`, `CharSource`, `Files`, `Resources`, `BaseEncoding`, `Closer` |
| **Hashing** (`hash`) | Hash functions and Bloom filters | `Hashing`, `HashFunction`, `HashCode`, `BloomFilter`, `Funnel` |
| **Graph** (`graph`) | Graph, value-graph and network data structures | `Graph`, `ValueGraph`, `Network`, `GraphBuilder`, `Traverser` |
| **Reflection** (`reflect`) | Generic type tokens, class-path scanning, invokables | `TypeToken`, `ClassPath`, `Invokable` |
| **Event bus** (`eventbus`) | Publish/subscribe | `EventBus`, `AsyncEventBus`, `@Subscribe` |
| **Strings/escaping & net** (`escape`, `html`, `xml`, `net`) | Escapers, media types, host/domain names | `Escaper`, `HtmlEscapers`, `MediaType`, `InternetDomainName`, `InetAddresses` |
| **Annotations** | `@Beta`, `@VisibleForTesting`, `@GwtCompatible` | – |

## 2. Dependencies

Everything depends on **base**. **collect** depends on base and primitives/math.
**concurrent, cache, graph, reflect, io, net** build on collect and base;
**cache** also on concurrent (`ListenableFuture` for async refresh); **io**
on hash (hashing sources). Nothing depends on eventbus, graph or reflect.

## 3. Diagram

```
 +-------------------------------------------------------------+
 | eventbus | cache | graph | reflect | io | net/escape | hash   |  feature libs
 +-------------------------------------------------------------+
 |          util.concurrent (ListenableFuture, Service)         |
 +-------------------------------------------------------------+
 |      collect (immutable, multimap/multiset, ranges, utils)   |  core data structures
 +-------------------------------------------------------------+
 |                  primitives   |   math                       |
 +-------------------------------------------------------------+
 |      base (Preconditions, Optional, Function, Strings)       |  foundation
 +-------------------------------------------------------------+
```

## 4. Styles and patterns

A **library** with a layered, package-by-feature structure (no runtime
architecture). Patterns: **Static factory/utility classes** (`Lists`,
`Maps`), **Builder** (`ImmutableList.Builder`, `CacheBuilder`), **Decorator /
Forwarding** (`ForwardingList`), **Immutable object**, **Template Method**
(`AbstractIterator`, `AbstractFuture`, `AbstractService`), **Observer**
(event bus, future listeners), **Strategy** (`Ordering`, `Equivalence`,
`HashFunction`), **Flyweight/Interning** (`Interners`).

Unsure about: the exact list of `@Beta` APIs in 33.7, whether old classes
like `Objects.toStringHelper` or the `common.io` "supplier" APIs are still
present (they were removed long ago), and Android-flavour differences.
