# P4 response (follow-up: feedback from the metrics)

Metrics given to the AI tool (33.7.0, course definitions; from
`guava/results/ai_metrics.csv`, `guava/results/metrics.csv` and
`guava/results/mojofm.csv`; full system = 549 connected classes, 2,750
dependencies):

| Architecture | #clusters | Largest | Cohesion | Coupling | MQ | MoJoFM to packages |
|---|---|---|---|---|---|---|
| AI (P3) | 14 | 85 | 0.0937 | 0.00372 | 0.090 | 94.4 % |
| A1 ACDC | 90 | 47 | 0.2542 | 0.00475 | 0.249 | 70.8 % |
| A3 k-means | 69 | 40 | 0.1764 | 0.00959 | 0.167 | 73.6 % |
| Packages | 17 | 209 | 0.0885 | 0.00425 | 0.084 | – |

---

**Why the numbers differ.**

1. *MQ rewards small clusters.* MQ is mean cohesion minus mean coupling, and
   cohesion divides the internal dependencies of a cluster by Nᵢ². ACDC's 90
   clusters have 6 classes on average and can be dense. My components have
   8–85 classes, and a component of 85 classes would need thousands of internal
   dependencies to reach the same density. The coupling terms are small for
   all architectures (0.004–0.010), so the MQ ranking is decided almost entirely
   by cluster size: ACDC (0.249) > k-means (0.167) > my architecture (0.090) >
   packages (0.084).
2. *Against the packages:* with a similar number of components (14 vs 17), my
   architecture has a slightly higher MQ (0.090 vs 0.084) and is very close to
   them (MoJoFM 94.4 %). The main difference is that I split `common.collect`
   (209 classes, the packages' largest "cluster") into four components. That
   gives smaller, denser components (higher cohesion, 0.094 vs 0.088), and I
   group very small packages (escape/html/xml/net, primitives/math).
3. *Noise.* Without the JNode noise classes my coupling halves (0.0037 →
   0.0019), but cohesion falls too (0.094 → 0.085), so MQ changes little (0.083).
   JNode's noise set is odd for Guava: it contains almost all of `common.base`
   (expected, these are hubs) **and almost all of `common.cache`** (18 of 19
   classes, although only `eventbus` uses the cache, with 3 dependencies),
   while it misses collection hubs like `Iterators`, `Ordering`, `Multiset`.

**Would I change the decomposition?**

* *Merging the four collection components back into one "Collections"
  component* (11 components) makes the view even closer to the packages
  (MoJoFM 94.9 %), but MQ falls to 0.083, because the merged component has
  ~200 classes. For the course's quality measure the split is better. It
  also gives developers the units they work with inside `collect`
  (immutable family, multi-collections, ranges, utilities).
* *To raise MQ further* I would have to split large components into smaller,
  dense groups, e.g. `util.concurrent` into futures / services / executors /
  synchronisation, and `graph` into API vs implementation. That is what ACDC
  does automatically. Beyond a point it turns an architecture view into a
  class-family view, so I would present it as a second, finer level
  (hierarchical architecture), not replace the component view.
