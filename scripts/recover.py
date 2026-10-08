#!/usr/bin/env python3
"""Phase 3.1, 3.4 and 3.5 - architecture recovery and evaluation per version.

For every version:
  * builds the top-level class dependency graph (DependencyExtractor output),
  * writes the ACDC input files data/rsf/<v>_full.rsf and <v>_nonoise.rsf
    (one "depends A B" line per distinct dependency A -> B),
  * A1/A2: runs ACDC (tools/acdc.jar) with and without the noise classes,
  * A3/A4: runs k-means (scikit-learn) with and without the noise classes,
  * populations (common.populations): A1/A3/PKG cluster the connected
    classes; A2/A4/PKG_nonoise the connected classes minus the noise classes
    (classes left without dependencies by the noise removal are kept; ACDC
    only sees classes that occur in a dependency, so each of them becomes a
    singleton cluster of A2),
  * PKG : the developers' package decomposition, used as a reference,
  * evaluates every recovered architecture with scripts/metrics.py
    (cohesion, coupling, MQ).

Outputs: results/size.csv, results/metrics.csv, results/kselection.csv,
         results/noise_classes.csv, results/clusters/<v>_<arch>.rsf
Usage: [JOBS=n] python3 scripts/recover.py [version ...]
"""
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict

import numpy as np
from scipy import sparse
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from kneed import KneeLocator

from common import (DATA, RESULTS, ROOT, load_noise, package, populations,
                    versions, write_csv)
from metrics import evaluate

ACDC = os.path.join(ROOT, "tools", "acdc.jar")
SEED = 42


def write_rsf(path, edges):
    with open(path, "w") as f:
        for s, d in sorted(edges):
            f.write(f"depends {s} {d}\n")


def run_acdc(rsf, out, max_size=20, patterns="bso"):
    """Run ACDC and return {class: cluster}.

    ACDC was designed for file names ("foo.c") and names every subsystem
    after its dominator's *base name* (text before the last dot) + ".ss".
    With Java class names that base name is the package, so all subsystems
    dominated by classes of the same package would get the same name and
    collapse into one cluster in the output. We therefore pass file-style
    names ("pkg.Class.java") to ACDC - the base name is then the full class
    name - and strip the suffix again from the output.
    """
    tmp = out + ".in"
    with open(rsf) as f, open(tmp, "w") as g:
        for line in f:
            rel, s, d = line.split()
            g.write(f"{rel} {s}.java {d}.java\n")
    subprocess.run(["java", "-jar", ACDC, tmp, out, str(max_size), patterns],
                   check=True, capture_output=True)
    os.remove(tmp)
    clusters = {}
    with open(out) as f:
        lines = f.read().split("\n")
    with open(out, "w") as f:
        for line in lines:
            if not line.strip():
                continue
            _, c, cls = line.split()
            c = c[:-len(".java.ss")] + ".ss" if c.endswith(".java.ss") else c
            cls = cls[:-len(".java")] if cls.endswith(".java") else cls
            clusters[cls] = c
            f.write(f"contain {c} {cls}\n")
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
    """Choose k with the elbow method on the k-means inertia curve (the
    elbow point is located automatically with the Kneedle algorithm), then
    cluster with k-means."""
    x = embedding(nodes, edges)
    ks, inertia = k_candidates(len(nodes)), []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=5, random_state=SEED).fit(x)
        inertia.append(km.inertia_)
        ksel_rows.append({"version": version, "arch": arch, "k": k,
                          "inertia": round(float(km.inertia_), 3)})
    k, rule = KneeLocator(ks, inertia, curve="convex", direction="decreasing").knee, "kneedle"
    if k is None:
        # Kneedle found no knee: take the candidate farthest from the straight
        # line between the first and the last point of the inertia curve.
        y = np.array(inertia)
        xs = np.array(ks, dtype=float)
        chord = y[0] + (y[-1] - y[0]) * (xs - xs[0]) / (xs[-1] - xs[0])
        k, rule = int(xs[np.argmax(chord - y)]), "max-distance"
    labels = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit_predict(x)
    return {n: f"km{l}" for n, l in zip(nodes, labels)}, k, rule


def complete(clusters, population, path):
    """Put every class of the population that ACDC did not see (no dependency
    in the input graph) into its own singleton cluster and rewrite the RSF."""
    missing = [c for c in population if c not in clusters]
    for c in missing:
        clusters[c] = f"{c}.single"
    if missing:
        write_clusters(path, clusters)
    return clusters


def analyse(v):
    """Recover and evaluate all architectures of one version."""
    size_rows, metric_rows, ksel_rows, noise_rows = [], [], [], []
    pop = populations(v)
    nodes, raw, edges, connected = pop["nodes"], pop["raw"], pop["edges"], pop["connected"]
    noise, nn_nodes, e_nn = pop["noise"], pop["nn_nodes"], pop["e_nn"]
    sig = load_noise(v)[1]
    isolated_nn = len(set(nn_nodes) - {c for e in e_nn for c in e})

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
        "classes_without_noise": len(nn_nodes),
        "isolated_after_noise_removal": isolated_nn,
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
        "A1": complete(run_acdc(full_rsf, os.path.join(cdir, f"{v}_A1.rsf")),
                       connected, os.path.join(cdir, f"{v}_A1.rsf")),
        "A2": complete(run_acdc(nn_rsf, os.path.join(cdir, f"{v}_A2.rsf")),
                       nn_nodes, os.path.join(cdir, f"{v}_A2.rsf")),
    }
    res["A3"], k3, rule3 = run_kmeans(connected, edges, v, "A3", ksel_rows)
    res["A4"], k4, rule4 = run_kmeans(nn_nodes, e_nn, v, "A4", ksel_rows)
    k_rule = {"A3": rule3, "A4": rule4}
    res["PKG"] = {c: package(c) for c in connected}
    res["PKG_nonoise"] = {c: package(c) for c in nn_nodes}
    for a in ("A3", "A4", "PKG", "PKG_nonoise"):
        write_clusters(os.path.join(cdir, f"{v}_{a}.rsf"), res[a])
    for a, cl in res.items():
        graph = e_nn if a in ("A2", "A4", "PKG_nonoise") else edges
        row = {"version": v, "arch": a}
        row.update(evaluate(cl, graph))
        row["k_rule"] = k_rule.get(a, "")
        metric_rows.append(row)
    print(v, {m["arch"]: m["mq"] for m in metric_rows},
          f"k3={k3} k4={k4} noise={len(noise)}", flush=True)
    return v, res, size_rows, metric_rows, ksel_rows, noise_rows


def main():
    vs = sys.argv[1:] or versions()
    os.makedirs(os.path.join(DATA, "rsf"), exist_ok=True)
    os.makedirs(os.path.join(RESULTS, "clusters"), exist_ok=True)
    size_rows, metric_rows, ksel_rows, noise_rows = [], [], [], []
    jobs = int(os.environ.get("JOBS", os.cpu_count() or 1))
    with ProcessPoolExecutor(jobs) as ex:
        for v, res, sz, mt, ks, nz in ex.map(analyse, vs):  # keeps version order
            size_rows += sz
            metric_rows += mt
            ksel_rows += ks
            noise_rows += nz

    if len(vs) == len(versions()):
        write_csv(os.path.join(RESULTS, "size.csv"), size_rows)
        write_csv(os.path.join(RESULTS, "metrics.csv"), metric_rows)
        write_csv(os.path.join(RESULTS, "kselection.csv"), ksel_rows)
        write_csv(os.path.join(RESULTS, "noise_classes.csv"), noise_rows)


if __name__ == "__main__":
    main()
