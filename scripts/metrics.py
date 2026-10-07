"""Architecture quality metrics (Phase 3.5), as defined in Lecture 6-7.

Computed on the directed, unweighted class dependency graph restricted to the
classes of the clustering (k clusters, N_i classes in cluster i):

Cohesion - mean intra-connectivity A_i = mu_i / N_i^2,
           mu_i = dependencies inside cluster i.
Coupling - mean inter-connectivity E_ij = eps_ij / (2 N_i N_j) over all cluster
           pairs, eps_ij = dependencies between clusters i and j.
MQ       - Modularization Quality (1/k) sum A_i - (2/(k(k-1))) sum E_ij,
           i.e. mean cohesion - mean coupling, in [-1, 1].
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
    a = {c: mu[c] / (size[c] ** 2) for c in size}
    cohesion = sum(a.values()) / k if k else 0.0
    pairs = k * (k - 1) / 2
    e_sum = sum(v / (2 * size[i] * size[j]) for (i, j), v in eps_pair.items())
    coupling = e_sum / pairs if pairs else 0.0
    mq = cohesion - coupling if k > 1 else cohesion
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
        "mq": round(mq, 5),
    }
