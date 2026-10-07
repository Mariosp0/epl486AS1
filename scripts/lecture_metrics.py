#!/usr/bin/env python3
"""Analyses taken directly from the course lectures (L5, L6-7).

1. MoJoFM (L6-7, slides 28-32): similarity of a recovered architecture A to a
   reference architecture R, MoJoFM(A,R) = (1 - mno(A,R)/max mno(.,R)) * 100 %,
   computed with the original MoJo 2.0 implementation (tools/mojo.jar).
   Spring AI and Guava have no expert ("ground-truth") architecture, so we use
   (a) the developers' package structure for every version and (b) the AI
   architecture (Phase 4) for the latest version as reference architectures.
   -> results/mojofm.csv
2. MoJoFM between consecutive versions (architectural change over time)
   -> results/mojofm_stability.csv
3. Omnipresent classes with the Bunch rule (L6-7, slides 39-41: in-degree >
   3 x average in-degree) compared with JNode (Constantinou et al. 2015), and
   the effect of removing each set on ACDC, as in slide 49 ("System" vs
   "Noise" vs "Bunch") -> results/bunch_noise.csv
5. Dependencies added/removed between versions (L1-2, law of increasing
   complexity, Eclipse example) -> results/dependency_changes.csv
4. Architectural smells and their evolution (L5, slides 28-34; Fontana et al.
   2016, Sas et al. 2019), normalised by #classes or #packages:
   * cyclic dependency  - packages (and classes) that take part in a
     dependency cycle (strongly connected component of size > 1);
   * hub-like dependency - class with fan-in and fan-out above the system
     medians and |fan-in - fan-out| < 0.25 (fan-in + fan-out) (slide 29);
   * unstable dependency - package P (instability I = Ce / (Ca + Ce)) of which
     more than 30 % of the package dependencies point to packages less stable
     than P (threshold used by the Arcan tool of Fontana et al.);
   * god component - package with more classes than mean + 2 std of the
     package sizes (the lecture leaves the threshold open; we measure size in
     top-level classes because we analyse bytecode).
   -> results/smells.csv
"""
import os
import statistics as st
import subprocess
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import networkx as nx

from common import (RESULTS, ROOT, load_dependencies, load_noise, package,
                    versions, write_csv)
from metrics import evaluate
from recover import run_acdc, write_rsf

MOJO = os.path.join(ROOT, "tools", "mojo.jar")
CDIR = os.path.join(RESULTS, "clusters")


def mojofm(a, b):
    """MoJoFM(A -> B) in % for two 'contain cluster entity' RSF files."""
    out = subprocess.run(["java", "-jar", MOJO, a, b, "-fm"], capture_output=True, text=True)
    return round(float(out.stdout.strip().splitlines()[-1]), 2)


def cpath(v, arch):
    return os.path.join(CDIR, f"{v}_{arch}.rsf")


def smells(nodes, edges):
    pkg_of = {c: package(c) for c in nodes}
    pk_edges = Counter((pkg_of[s], pkg_of[d]) for s, d in edges if pkg_of[s] != pkg_of[d])
    pg = nx.DiGraph(list(pk_edges))
    pg.add_nodes_from(set(pkg_of.values()))
    cg = nx.DiGraph(list(edges))
    pk_cyc = sum(len(c) for c in nx.strongly_connected_components(pg) if len(c) > 1)
    cl_cyc = sum(len(c) for c in nx.strongly_connected_components(cg) if len(c) > 1)
    fin = {n: cg.in_degree(n) for n in cg}
    fout = {n: cg.out_degree(n) for n in cg}
    mi, mo = st.median(fin.values()), st.median(fout.values())
    hubs = [n for n in cg if fin[n] > mi and fout[n] > mo
            and abs(fin[n] - fout[n]) < 0.25 * (fin[n] + fout[n])]
    inst = {}
    for p in pg:
        ca, ce = pg.in_degree(p), pg.out_degree(p)
        inst[p] = ce / (ca + ce) if ca + ce else 0.0
    ud = [p for p in pg if pg.out_degree(p)
          and sum(inst[q] > inst[p] for q in pg.successors(p)) / pg.out_degree(p) > 0.3]
    size = Counter(pkg_of.values())
    thr = st.mean(size.values()) + 2 * st.pstdev(size.values())
    gc = [p for p, n in size.items() if n > thr]
    npk, ncl = len(size), len(nodes)
    return {
        "classes": ncl, "packages": npk,
        "cyclic_packages": pk_cyc, "cyclic_packages_pct": round(100 * pk_cyc / npk, 2),
        "cyclic_classes": cl_cyc, "cyclic_classes_pct": round(100 * cl_cyc / ncl, 2),
        "hub_like_classes": len(hubs), "hub_like_pct": round(100 * len(hubs) / ncl, 2),
        "unstable_dep_packages": len(ud), "unstable_dep_pct": round(100 * len(ud) / npk, 2),
        "god_components": len(gc), "god_component_threshold": round(thr, 1),
        "god_component_names": " ".join(sorted(gc)),
    }


def main():
    vs = versions()
    latest = vs[-1]
    mojo_rows, stab_rows, bunch_rows, smell_rows = [], [], [], []

    jobs = []
    for v in vs:
        for a in ("A1", "A2", "A3", "A4", "AI"):
            if a == "AI" and v != latest:
                continue
            ref = "PKG_nonoise" if a in ("A2", "A4") else "PKG"
            jobs.append(("mojo", v, a, ref))
    for a in ("A1", "A2", "A3", "A4", "PKG"):
        jobs.append(("mojo", latest, a, "AI"))
    for prev, cur in zip(vs, vs[1:]):
        for a in ("A1", "A2", "A3", "A4"):
            jobs.append(("stab", cur, a, prev))

    def run(job):
        kind, v, a, ref = job
        if kind == "mojo":
            return job, mojofm(cpath(v, a), cpath(v, ref))
        return job, mojofm(cpath(v, a), cpath(ref, a))

    with ThreadPoolExecutor(os.cpu_count() or 2) as ex:
        res = dict(ex.map(run, jobs))

    for v in vs:
        row = {"version": v}
        for a in ("A1", "A2", "A3", "A4"):
            row[f"{a}_vs_PKG"] = res[("mojo", v, a, "PKG_nonoise" if a in ("A2", "A4") else "PKG")]
        if v == latest:
            row["AI_vs_PKG"] = res[("mojo", v, "AI", "PKG")]
            for a in ("A1", "A2", "A3", "A4", "PKG"):
                row[f"{a}_vs_AI"] = res[("mojo", v, a, "AI")]
        mojo_rows.append(row)
    for prev, cur in zip(vs, vs[1:]):
        stab_rows.append({"from": prev, "to": cur,
                          **{a: res[("stab", cur, a, prev)] for a in ("A1", "A2", "A3", "A4")}})

    tmp = tempfile.mkdtemp()
    for v in vs:
        nodes, dep, _ = load_dependencies(v)
        edges = set(dep)
        conn = {c for e in edges for c in e}
        jnode, _, _, _ = load_noise(v)
        jnode &= conn
        fin = Counter(d for _, d in edges)
        avg = sum(fin[c] for c in conn) / len(conn)
        bunch = {c for c in conn if fin[c] > 3 * avg}
        e_b = {(s, d) for s, d in edges if s not in bunch and d not in bunch}
        rsf = os.path.join(tmp, f"{v}_bunch.rsf")
        write_rsf(rsf, e_b)
        out = os.path.join(CDIR, f"{v}_A2bunch.rsf")
        cl = run_acdc(rsf, out)
        m = evaluate(cl, e_b)
        union = jnode | bunch
        bunch_rows.append({
            "version": v, "avg_in_degree": round(avg, 2), "bunch_threshold": round(3 * avg, 2),
            "bunch_noise": len(bunch), "jnode_noise": len(jnode), "common": len(jnode & bunch),
            "jaccard": round(len(jnode & bunch) / len(union), 3) if union else 1.0,
            "mq_A1_system": None, "mq_A2_jnode": None, "mq_A2_bunch": m["basic_mq"],
            "mojofm_A1_system": res[("mojo", v, "A1", "PKG")],
            "mojofm_A2_jnode": res[("mojo", v, "A2", "PKG_nonoise")],
            "mojofm_A2_bunch": mojofm(out, cpath(v, "PKG")),
            "bunch_classes": " ".join(sorted(c.rsplit(".", 1)[1] for c in bunch)),
        })
        sm = {"version": v}
        sm.update(smells(conn, edges))
        smell_rows.append(sm)
        print(v, "bunch", len(bunch), "jnode", len(jnode), "common", len(jnode & bunch),
              {k: sm[k] for k in ("cyclic_packages_pct", "cyclic_classes_pct", "hub_like_pct",
                                  "unstable_dep_pct", "god_components")}, flush=True)

    import csv
    with open(os.path.join(RESULTS, "metrics.csv")) as f:
        mq = {(r["version"], r["arch"]): r["basic_mq"] for r in csv.DictReader(f)}
    for r in bunch_rows:
        r["mq_A1_system"] = mq[(r["version"], "A1")]
        r["mq_A2_jnode"] = mq[(r["version"], "A2")]

    write_csv(os.path.join(RESULTS, "mojofm.csv"), mojo_rows,
              fields=list(mojo_rows[-1].keys()))
    write_csv(os.path.join(RESULTS, "mojofm_stability.csv"), stab_rows)
    write_csv(os.path.join(RESULTS, "bunch_noise.csv"), bunch_rows)
    write_csv(os.path.join(RESULTS, "smells.csv"), smell_rows)

    # Lecture 1-2 (law II, Eclipse example): dependencies added / removed
    dep_rows, prev = [], None
    for v in vs:
        e = set(load_dependencies(v)[1])
        if prev is not None:
            dep_rows.append({"from": prev[0], "to": v, "dependencies": len(e),
                             "added": len(e - prev[1]), "removed": len(prev[1] - e)})
        prev = (v, e)
    write_csv(os.path.join(RESULTS, "dependency_changes.csv"), dep_rows)


if __name__ == "__main__":
    main()
