# P4 response (follow-up: feedback from the metrics)

Metrics given to the AI tool (2.1.0-M1, from `results/ai_metrics.csv` and
`results/metrics.csv`; full system = 1,016 connected classes, 3,725
dependencies):

| Architecture | #clusters | Cohesion | Coupling | BasicMQ | TurboMQ | TurboMQ/k | Intra-cluster deps |
|---|---|---|---|---|---|---|---|
| AI (P3) | 12 | 0.0284 | 0.00262 | 0.026 | 5.48 | 0.457 | 47.2 % |
| A1 ACDC | 124 | 0.2061 | 0.00154 | 0.205 | 57.94 | 0.467 | 47.3 % |
| A3 k-means | 84 | 0.1348 | 0.00155 | 0.133 | 47.60 | 0.567 | 40.1 % |
| Packages | 282 | 0.1426 | 0.00242 | 0.140 | 56.87 | 0.202 | 22.6 % |

---

**Why the numbers differ.**

1. *Granularity, not quality, drives most of the gap.* My decomposition has 12
   components of 23–214 classes; ACDC has 124 clusters of about 8 classes. Cohesion as
   intra-connectivity (μᵢ/Nᵢ²) divides by the *square* of the cluster size, so a
   component with 200 classes can never reach the density of a 6-class cluster
   even if all its dependencies stay inside it. TurboMQ is a *sum* over
   clusters, so it grows almost linearly with k (5.5 vs 58). The two
   metrics that are less sensitive to k tell a different story: **the share of
   dependencies kept inside components is the same as ACDC's (47.2 % vs
   47.3 %)** with 10× fewer components, and TurboMQ/k is comparable (0.457 vs
   0.467).
2. *My components are defined by responsibility, not by connectivity.* The two
   largest inter-component flows (Model providers → Model API, 516; Vector
   stores → Vector store API, 190) are adapter → port dependencies. In a Ports &
   Adapters design these are **intended** to cross a component border. An
   algorithm that maximises MQ pulls every adapter into the cluster of the
   port it implements, or into a cluster of its own. That raises MQ but hides
   the plug-in structure that matters to a developer.
3. *Hub classes.* About 11 % of the classes (JNode noise) are used almost
   everywhere. Removing them raises my TurboMQ/k from 0.457 to 0.525 and the
   intra share to 52 %. The same happens for ACDC (0.467 → 0.517).

**Would I change the decomposition?** Only in ways that keep its meaning:

* Split **MCP** (163 classes) into *MCP annotations* (`mcp.annotation.*`, ~120
  classes, a self-contained framework) and *MCP integration & transports*
  (`mcp`, `mcp.customizer`, `mcp.*.transport`).
* Split **Boot auto-configuration** (214) by the component it configures
  (models / vector stores / MCP / client-memory-tools). Each auto-configuration
  package depends almost only on its target, so this moves many dependencies
  inside components.
* Move the **observation** packages (`chat.observation`, `vectorstore.observation`,
  `model.observation`, `observation.conventions`) into one *Observability*
  component. They are hubs used by every adapter.

I would **not** merge each provider into the Model API component, even though
that would maximise MQ, because it would erase the port/adapter boundary. That
boundary is the main architectural decision of the framework (design document 02).
