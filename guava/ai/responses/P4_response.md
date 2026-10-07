# P4 response (follow-up: feedback from the metrics)

Metrics given to the AI tool (33.7.0, from `guava/results/ai_metrics.csv` and
`guava/results/metrics.csv`; full system = 549 connected classes, 2,750
dependencies):

| Architecture | #clusters | Cohesion | Coupling | BasicMQ | TurboMQ | TurboMQ/k | Intra-cluster deps |
|---|---|---|---|---|---|---|---|
| AI (P3) | 14 | 0.0937 | 0.00372 | 0.090 | 8.04 | 0.574 | 55.8 % |
| A1 ACDC | 90 | 0.2542 | 0.00475 | 0.249 | 28.26 | 0.314 | 35.9 % |
| A3 k-means | 69 | 0.1764 | 0.00959 | 0.167 | 22.86 | 0.331 | 28.7 % |
| Packages | 17 | 0.0885 | 0.00425 | 0.084 | 7.97 | 0.469 | 72.0 % |

---

**Why the numbers differ.**

1. *Against ACDC and k-means:* my decomposition is better on the two
   k-independent measures (TurboMQ/k 0.574 vs 0.31–0.33; 56 % vs 29–36 % of
   the dependencies inside components). Guava is a densely connected library
   (5 dependencies per class) whose classes are used through a few hubs
   (`Preconditions`, the immutable collections, `Iterators`, `Maps`). An
   algorithm that only sees the graph cuts these dense regions into 70–90
   small pieces; every cut through `collect` costs many dependencies. Cohesion
   and BasicMQ favour their small clusters (0.25 vs 0.09) only because
   intra-connectivity divides by Nᵢ².
2. *Against the packages:* the packages keep more dependencies inside (72 %)
   because `common.collect` is a single 209-class package that I split into
   four components (immutable, multi-collections, ranges, utilities). Those
   four are strongly inter-dependent (utilities ⇄ immutable 125/37,
   multi → utilities 148), so the split moves ~450 dependencies across
   component borders. On TurboMQ/k I am still ahead (0.574 vs 0.469), because
   the packages also contain tiny, poorly connected packages (`html`, `xml`,
   `base.internal`) and one huge one.
3. *Noise.* Removing the JNode noise classes raises my TurboMQ/k to 0.686 and
   the intra share to 70 %, but JNode's noise set for Guava is odd: it contains
   almost all of `common.base` (expected, these are hubs) **and almost all of
   `common.cache`** (18 of 19 classes, although only `eventbus` uses the cache, with 3 dependencies),
   while it misses collection hubs like `Iterators`, `Ordering`, `Multiset`.

**Would I change the decomposition?**

* *Merge the four collection sub-components back into one "Collections"
  component.* Measured: 11 components, TurboMQ/k 0.624 (from 0.574) and 72.5 %
  of dependencies inside components (from 55.8 %), i.e. better than the
  packages on both measures. For a *coarse* view this is the better
  architecture, and it matches how Guava users think about `collect`.
* *But keep the split as a second level.* For a developer working inside
  `collect`, the immutable family, the multi-collections and ranges are the
  units of change; I would present Collections as one component with four
  sub-components (a hierarchical view), not flatten them.
* Leave `Primitives & math` together and `Base utilities` as the foundation:
  they are leaves used by everyone and do not reduce modularity.
