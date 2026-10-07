#!/usr/bin/env python3
"""Phase 4 - evaluate the architecture recovered with the AI tool.

Maps every class of the latest version to a component using the ordered
(component, regex-over-package) rules returned by the AI (first match wins),
then computes the same metrics as for ACDC/k-means, the component dependency
matrix, and the agreement (adjusted Rand index) with A1-A4 and the packages.

Outputs: results/ai_metrics.csv, results/ai_component_deps.csv,
         results/ai_components.csv, results/clusters/<v>_AI.rsf
"""
import json
import os
import re
import sys
from collections import Counter

from sklearn.metrics import adjusted_rand_score

from common import (PREFIX, PROJECT_DIR, RESULTS, load_dependencies, load_noise,
                    package, versions, write_csv)
from metrics import evaluate

PFX = PREFIX


def read_clusters(path):
    out = {}
    with open(path) as f:
        for line in f:
            _, c, cls = line.split()
            out[cls] = c
    return out


def main():
    spec = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT_DIR, "ai", "ai_architecture_P3.json")
    cfg = json.load(open(spec))
    v = cfg.get("version", versions()[-1])
    rules = [(name, re.compile(rx)) for name, rx in cfg["rules"]]
    nodes, dep, _ = load_dependencies(v)
    edges = set(dep)
    connected = sorted({c for e in edges for c in e})

    def component(cls):
        p = package(cls)
        p = p[len(PFX):] if p.startswith(PFX) else p
        for name, rx in rules:
            if rx.fullmatch(p):
                return name
        return "unmapped"

    ai = {c: component(c) for c in connected}
    cdir = os.path.join(RESULTS, "clusters")
    with open(os.path.join(cdir, f"{v}_AI.rsf"), "w") as f:
        for c in sorted(ai, key=lambda x: (ai[x], x)):
            f.write(f"contain {ai[c].replace(' ', '_')} {c}\n")

    noise, _, _, _ = load_noise(v)
    e_nn = {(s, d) for s, d in edges if s not in noise and d not in noise}
    ai_nn = {c: k for c, k in ai.items() if c not in noise and any(c in e for e in e_nn)}

    rows = []
    for label, cl, graph in (("AI (full)", ai, edges), ("AI (no noise)", ai_nn, e_nn)):
        r = {"version": v, "arch": label}
        r.update(evaluate(cl, graph))
        for other in ("A1", "A2", "A3", "A4", "PKG"):
            o = read_clusters(os.path.join(cdir, f"{v}_{other}.rsf"))
            common = sorted(set(o) & set(cl))
            r[f"ari_vs_{other}"] = round(adjusted_rand_score(
                [o[c] for c in common], [cl[c] for c in common]), 4)
        rows.append(r)
        print(r)
    write_csv(os.path.join(RESULTS, "ai_metrics.csv"), rows)

    size = Counter(ai.values())
    write_csv(os.path.join(RESULTS, "ai_components.csv"),
              [{"component": k, "classes": n} for k, n in size.most_common()])
    cd = Counter((ai[s], ai[d]) for s, d in edges if ai[s] != ai[d])
    write_csv(os.path.join(RESULTS, "ai_component_deps.csv"),
              [{"from": a, "to": b, "class_dependencies": n} for (a, b), n in cd.most_common()])


if __name__ == "__main__":
    main()
