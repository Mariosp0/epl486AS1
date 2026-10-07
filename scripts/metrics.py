"""Architecture quality metrics (Phase 3.5).

All metrics are computed on the directed, unweighted class dependency graph
restricted to the classes of the clustering.

Cohesion  - mean intra-connectivity A_i = mu_i / N_i^2 over clusters
            (Mancoridis et al., 1998), mu_i = intra-cluster edges of cluster i.
Coupling  - mean inter-connectivity E_ij = eps_ij / (2 N_i N_j) over all
            cluster pairs, eps_ij = edges between clusters i and j.
BasicMQ   - mean(A_i) - mean(E_ij) (Mancoridis et al., 1998); in [-1, 1].
TurboMQ   - sum_i CF_i, CF_i = 2 mu_i / (2 mu_i + eps_i) with eps_i all edges
            crossing the border of cluster i (Mitchell & Mancoridis, 2006).
TurboMQn  - TurboMQ / k (normalised to [0, 1], comparable across k).
IntraRatio- share of dependencies that stay inside a cluster.
"""
from collections import defaultdict


def evaluate(clusters, edges):
    """clusters: {class: cluster_id}; edges: iterable of (src, dst)."""
    size = defaultdict(int)
    for c in clusters.values():
        size[c] += 1
    k = len(size)
    mu = defaultdict(int)
    eps_pair = defaultdict(int)
    eps = defaultdict(int)
    m = 0
    for s, d in edges:
        if s not in clusters or d not in clusters or s == d:
            continue
        m += 1
        cs, cd = clusters[s], clusters[d]
        if cs == cd:
            mu[cs] += 1
        else:
            eps_pair[(min(cs, cd), max(cs, cd))] += 1
            eps[cs] += 1
            eps[cd] += 1
    a = {c: mu[c] / (size[c] ** 2) for c in size}
    cohesion = sum(a.values()) / k if k else 0.0
    pairs = k * (k - 1) / 2
    e_sum = sum(v / (2 * size[i] * size[j]) for (i, j), v in eps_pair.items())
    coupling = e_sum / pairs if pairs else 0.0
    basic_mq = cohesion - coupling if k > 1 else cohesion
    cf = {c: (2 * mu[c] / (2 * mu[c] + eps[c]) if mu[c] else 0.0) for c in size}
    turbo = sum(cf.values())
    intra = sum(mu.values())
    sizes = sorted(size.values())
    return {
        "classes": len(clusters),
        "edges": m,
        "clusters": k,
        "singletons": sum(1 for s in sizes if s == 1),
        "max_cluster": sizes[-1] if sizes else 0,
        "mean_cluster": round(len(clusters) / k, 3) if k else 0,
        "cohesion": round(cohesion, 5),
        "coupling": round(coupling, 6),
        "basic_mq": round(basic_mq, 5),
        "turbo_mq": round(turbo, 3),
        "turbo_mq_norm": round(turbo / k, 4) if k else 0,
        "intra_ratio": round(intra / m, 4) if m else 0,
    }
