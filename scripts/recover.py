#!/usr/bin/env python3
"""Phase 3.1, 3.4 and 3.5 - architecture recovery and evaluation per version.

For every version:
  * builds the top-level class dependency graph (DependencyExtractor output),
  * writes the ACDC input files data/rsf/<v>_full.rsf and <v>_nonoise.rsf
    (one "depends A B" line per distinct dependency A -> B),
  * A1/A2: runs ACDC (tools/acdc.jar) with and without the noise classes,
  * A3/A4: runs k-means (scikit-learn) with and without the noise classes,
  * PKG : the developers' package decomposition, used as a reference,
  * evaluates every recovered architecture with scripts/metrics.py,
  * also stores how stable each architecture is between consecutive versions
    (adjusted Rand index over the classes present in both versions).

Outputs: results/size.csv, results/metrics.csv, results/kselection.csv,
         results/stability.csv, results/clusters/<v>_<arch>.rsf
Usage: python3 scripts/recover.py [version ...]
"""
import os
import subprocess
import sys
from collections import defaultdict

import numpy as np
from scipy import sparse
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import normalize
from kneed import KneeLocator

from common import (DATA, RESULTS, ROOT, load_dependencies, load_noise,
                    package, versions, write_csv)
from metrics import evaluate

ACDC = os.path.join(ROOT, "tools", "acdc.jar")
SEED = 42


def write_rsf(path, edges):
    with open(path, "w") as f:
        for s, d in sorted(edges):
            f.write(f"depends {s} {d}\n")


def run_acdc(rsf, out, max_size=20, patterns="bso"):
    subprocess.run(["java", "-jar", ACDC, rsf, out, str(max_size), patterns],
                   check=True, capture_output=True)
    clusters = {}
    with open(out) as f:
        for line in f:
            _, c, cls = line.split()
            clusters[cls] = c
    return clusters


def write_clusters(path, clusters):
    with open(path, "w") as f:
        for cls, c in sorted(clusters.items(), key=lambda x: (str(x[1]), x[0])):
            f.write(f"contain {c} {cls}\n")


def embedding(nodes, edges, dims=64):
    """Structural feature vector of every class.

    Each class is described by its row of the symmetric adjacency matrix
    (A + A^T + I: whom it uses and who uses it, plus itself). Rows are
    L2-normalised and reduced with truncated SVD (LSA) so that k-means works on
    a dense, low-dimensional space where Euclidean distance approximates
    cosine distance between dependency profiles.
    """
    idx = {n: i for i, n in enumerate(nodes)}
    rows, cols = [], []
    for s, d in edges:
        rows += [idx[s], idx[d]]
        cols += [idx[d], idx[s]]
    n = len(nodes)
    a = sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    a.data[:] = 1.0
    a = a + sparse.identity(n, format="csr")
    x = normalize(a)
    d = min(dims, n - 1)
    x = TruncatedSVD(n_components=d, random_state=SEED).fit_transform(x)
    return normalize(x)


def k_candidates(n):
    step = max(2, n // 100)
    return list(range(4, max(6, n // 3), step))


def run_kmeans(nodes, edges, version, arch, ksel_rows):
    """Choose k with the elbow method (Kneedle on the k-means inertia curve),
    then cluster with k-means. The silhouette coefficient is recorded too."""
    x = embedding(nodes, edges)
    ks, inertia = k_candidates(len(nodes)), []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=5, random_state=SEED).fit(x)
        inertia.append(km.inertia_)
        sil = silhouette_score(x, km.labels_, metric="cosine", random_state=SEED)
        ksel_rows.append({"version": version, "arch": arch, "k": k,
                          "inertia": round(float(km.inertia_), 3),
                          "silhouette": round(float(sil), 4)})
    k = KneeLocator(ks, inertia, curve="convex", direction="decreasing").knee
    labels = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit_predict(x)
    return {n: f"km{l}" for n, l in zip(nodes, labels)}, k


def main():
    vs = sys.argv[1:] or versions()
    os.makedirs(os.path.join(DATA, "rsf"), exist_ok=True)
    os.makedirs(os.path.join(RESULTS, "clusters"), exist_ok=True)
    size_rows, metric_rows, ksel_rows, noise_rows = [], [], [], []
    archs = {}
    for v in vs:
        nodes, dep, raw = load_dependencies(v)
        noise, sig, _, fallback = load_noise(v)
        edges = set(dep)
        connected = sorted({c for e in edges for c in e})
        noise &= set(connected)
        e_nn = {(s, d) for s, d in edges if s not in noise and d not in noise}
        nn_nodes = sorted({c for e in e_nn for c in e})

        size_rows.append({
            "version": v,
            "classes": len(nodes),
            "packages": len({package(n) for n in nodes}),
            "class_dependencies": len(edges),
            "raw_dependency_rows": raw,
            "connected_classes": len(connected),
            "isolated_classes": len(nodes) - len(connected),
            "noise_classes": len(noise),
            "noise_pct": round(100 * len(noise) / len(connected), 2),
            "noise_fallback": fallback,
            "classes_without_noise": len(nn_nodes),
            "dependencies_without_noise": len(e_nn),
        })
        for c in sorted(noise, key=lambda c: -sig.get(c, 0)):
            noise_rows.append({"version": v, "class": c, "sig": sig.get(c)})

        full_rsf = os.path.join(DATA, "rsf", f"{v}_full.rsf")
        nn_rsf = os.path.join(DATA, "rsf", f"{v}_nonoise.rsf")
        write_rsf(full_rsf, edges)
        write_rsf(nn_rsf, e_nn)
        cdir = os.path.join(RESULTS, "clusters")
        res = {
            "A1": run_acdc(full_rsf, os.path.join(cdir, f"{v}_A1.rsf")),
            "A2": run_acdc(nn_rsf, os.path.join(cdir, f"{v}_A2.rsf")),
        }
        res["A3"], k3 = run_kmeans(connected, edges, v, "A3", ksel_rows)
        res["A4"], k4 = run_kmeans(nn_nodes, e_nn, v, "A4", ksel_rows)
        res["PKG"] = {c: package(c) for c in connected}
        res["PKG_nonoise"] = {c: package(c) for c in nn_nodes}
        for a in ("A3", "A4", "PKG", "PKG_nonoise"):
            write_clusters(os.path.join(cdir, f"{v}_{a}.rsf"), res[a])
        for a, cl in res.items():
            graph = e_nn if a in ("A2", "A4", "PKG_nonoise") else edges
            row = {"version": v, "arch": a}
            row.update(evaluate(cl, graph))
            ref = res["PKG" if a in ("A1", "A3") else "PKG_nonoise"]
            common = sorted(set(cl) & set(ref))
            row["ari_vs_packages"] = round(adjusted_rand_score(
                [ref[c] for c in common], [cl[c] for c in common]), 4)
            metric_rows.append(row)
        archs[v] = res
        print(v, {a: r["turbo_mq_norm"] for a, r in
                  [(m["arch"], m) for m in metric_rows if m["version"] == v]},
              f"k3={k3} k4={k4} noise={len(noise)}", flush=True)

    stab_rows = []
    for prev, cur in zip(vs, vs[1:]):
        row = {"from": prev, "to": cur}
        for a in ("A1", "A2", "A3", "A4", "PKG"):
            p, c = archs[prev][a], archs[cur][a]
            common = sorted(set(p) & set(c))
            row[a] = round(adjusted_rand_score([p[x] for x in common],
                                               [c[x] for x in common]), 4)
        stab_rows.append(row)

    if len(vs) == len(versions()):
        write_csv(os.path.join(RESULTS, "size.csv"), size_rows)
        write_csv(os.path.join(RESULTS, "metrics.csv"), metric_rows)
        write_csv(os.path.join(RESULTS, "kselection.csv"), ksel_rows)
        write_csv(os.path.join(RESULTS, "stability.csv"), stab_rows)
        write_csv(os.path.join(RESULTS, "noise_classes.csv"), noise_rows)


if __name__ == "__main__":
    main()
