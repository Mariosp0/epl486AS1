# P4 response – Guava 33.7.2

> P4 – follow-up in the P3 conversation (same sub-agent) with the metrics that our
> scripts measured for its P3 architecture; the agent used no tool in this turn.
> Verbatim answer; see `guava/ai/prompts.md` for the prompt and the procedure.
> Statements marked by the AI as estimates were not measured by it.

---

# P4: Why the metrics differ, and how I would revise the decomposition

## 1. What the numbers say

**This MQ rewards small clusters, so the comparison is not neutral.**
- Cohesion is A_i = mu_i / N_i², averaged over clusters without weighting by size.
- Your system has 2,750 dependencies over 549 classes, so the average out-degree is about 5. Even if every dependency of a cluster stayed inside it, mu_i is at most about 5·N_i, so A_i can be at most about 5/N_i. That is my estimate from your totals.

| Architecture | Clusters | Mean size | Cohesion ceiling (≈ 5 / mean size) | Measured cohesion |
|---|---|---|---|---|
| ACDC | 90 | ≈ 6 | ≈ 0.8 | 0.254 |
| k-means | 69 | ≈ 8 | ≈ 0.6 | 0.176 |
| Mine | 14 | ≈ 39 | ≈ 0.13 | 0.082 |
| Packages | 17 | ≈ 32 | ≈ 0.15 | 0.089 |

- Two examples: a cluster of 5 classes with 2 internal edges already gets A = 0.08. My largest cluster (80 classes) would need about 522 internal edges for the same score, which is more than such a cluster can have.
- So ACDC's and k-means' MQ lead (0.249 and 0.167 against 0.078) comes mostly from being 5–6 times finer. It does not show that their cuts are 3 times "better".
- **Coupling, which is less sensitive to size, favours my decomposition.** Mine has the lowest coupling of all four: 0.00352, against packages 0.00425, ACDC 0.00475 and k-means 0.00959. Few dependencies cross my boundaries. That fits the acyclic, layered package graph from P3.

**Against the package baseline, which is the fair comparison at similar granularity:**
- My MQ is 0.078 against 0.084. Coupling is better (0.00352 against 0.00425), but cohesion is a little lower (0.0816 against 0.0885).
- Splitting `collect` (209 classes) should have raised cohesion. So the loss must come from my other choices:
  1. **Merged components with few internal links.**
     - PrimitivesMath: only 5 dependencies from math to primitives.
     - EscapeNet: escape, html and xml link to net with only 2 dependencies each, and publicsuffix with 3.
     - Two well-linked packages joined by a thin bridge make a larger N² denominator with almost no extra mu.
  2. **Splits made by concept rather than by dependencies.**
     - Immutable / Types / Utilities inside `collect`: for example, `ImmutableMultimap` implements `Multimap`, and `Maps` creates `ImmutableMap`.
     - Futures / ServicesSync inside `util.concurrent`: `AbstractService` and `ServiceManager` use `ListenableFuture` and `MoreExecutors`.
     - These cuts probably put many edges between components rather than inside them. That lowers mu_i, and the cut edges are the cycles I predicted in P3.
- Two smaller observations:
  - The largest cluster has 80 classes, while I counted 79 for Collect.Utilities. One class probably matched a different rule than I intended; a `collect` class not covered by my Types regex would fall into Utilities.
  - The 549 total (against 554) presumably drops classes that have no dependencies.

**MoJoFM:**
- Mine is 94.38 % similar to the packages, because it was built from packages with only a few merges and splits. That is good for developer meaning.
- ACDC and k-means are only about 71–74 % similar to the packages. They cut along actual dependency clusters (for example builder + implementation + helpers) and break the package structure.
- They are a bit further from my architecture (65 % and 67 %) than from the packages (71 % and 74 %). So my extra cuts inside `collect` and `util.concurrent` do not match where the dependency-based tools cut. This again points to those cuts being the weak part.

## 2. Would I change it? Yes, a little, and guided by the data

I would not chase ACDC's 90 clusters. Clusters of about 6 classes beat the metric but no longer describe a library that developers understand (Base, Collections, Concurrency, Cache, Graph, …). I would fix the three weak spots identified above.

1. **Undo the merges with few internal links.**
   - Split PrimitivesMath into **Primitives** and **Math**.
   - Split EscapeNet into **Escaping** (escape, html, xml, plus `net.PercentEscaper` and `net.UrlEscapers`, which are escapers in purpose and in dependencies) and **Net** (the rest of net, plus `thirdparty.publicsuffix`).
2. **Split `collect` by type family instead of by implementation style.**
   - Each interface goes with its abstract base, its mutable and immutable implementations, and its static helper class, because those classes depend on each other most:
     - **Collect.Core**: ImmutableCollection, ImmutableList/Set/Map/SortedX and their Regular*, Singleton*, JdkBacked* and Empty* implementations, plus Lists, Sets, Maps.
     - **Collect.Multi**: the Multimap, Multiset and BiMap families, including the Immutable* versions, Multimaps, Multisets and MultimapBuilder.
     - **Collect.TableRange**: the Table and Range/RangeSet/RangeMap families, including the Immutable* versions, Cut, DiscreteDomain and Tables.
     - **Collect.Utilities**: iteration (Iterables, Iterators, FluentIterable), Ordering and comparators, Forwarding*, Streams and collectors, compact hashing, MapMaker, Interners and internal helpers.
   - This still reads like the Guava user guide, and it should move edges from between components to inside them.
3. **Merge `util.concurrent` back into one Concurrency component, or check the split first.**
   - Futures and Services are very likely mutually dependent. Unless the edge counts show Services/Sync is loosely connected, keeping it separate only adds coupling and a cycle.
   - A cheaper alternative is to keep only the clearly separate sync primitives apart: RateLimiter, Striped, Monitor and the atomics.
4. **Fix the regex leak** behind the 80-class cluster: list the boundary classes explicitly and check the per-cluster counts.

**Result:**
- About 16 components: Base, Primitives, Math, Collect × 4, Concurrency, Cache, EventBus, Graph, Hash, IO, Reflect, Escaping, Net.
- That is one more than the 8–15 limit set in P3. If the limit is strict, keep Primitives and Math merged (they are the smallest pair). I estimate this costs the least cohesion of the merges.
- **Expected effect (my estimate, not measured):**
  - Cohesion should rise to at least the package level, roughly 0.09–0.10.
  - Coupling should stay near 0.0035–0.004.
  - MoJoFM to packages should stay around 90 % or higher.
  - Similarity to ACDC and k-means should rise slightly, because family-based clusters in `collect` are closer to what those tools find.
- To validate: recompute A_i for each cluster and E_ij for each pair. Any cluster with A_i well below about 0.5 × (5/N_i) is a merge with few internal links, and any pair with high E_ij is a cut through a dependency cluster. Revise only those, and keep names that reflect the package structure.

**Bottom line:** the gap to ACDC and k-means mostly comes from how MQ is defined, which favours small clusters. The gap to packages is real but small, and it comes from my two merges and two splits made by concept. Fixing those keeps the decomposition easy for developers to understand, without breaking it into very small clusters.
