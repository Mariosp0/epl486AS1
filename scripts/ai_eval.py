#!/usr/bin/env python3
"""Phase 4 - evaluate the architecture recovered with the AI tool.

Maps every class of the latest version to a component using the ordered
(component, regex-over-package) rules returned by the AI (first match wins),
then computes the same metrics as for ACDC/k-means (cohesion, coupling, MQ)
and the component dependency matrix. The MoJoFM comparison with the other
architectures is done in scripts/lecture_metrics.py.

Populations as for the other architectures (common.populations): "AI (full)"
= connected classes, "AI (no noise)" = connected classes minus the noise classes.

Outputs: results/ai_metrics.csv, results/ai_component_deps.csv,
         results/ai_components.csv, results/clusters/<v>_AI.rsf
"""
import json
import os
import re
import sys
from collections import Counter

from common import (PREFIX, PROJECT_DIR, RESULTS, package, populations,
                    versions, write_csv)
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
    pop = populations(v)
    edges, connected = pop["edges"], pop["connected"]

    by_class = cfg.get("match") == "class"  # rules over "pkg.Class" instead of "pkg"

    def component(cls):
        p = cls if by_class else package(cls)
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

    # same populations as A2/A4: connected classes minus the JNode noise classes
    e_nn = pop["e_nn"]
    ai_nn = {c: ai[c] for c in pop["nn_nodes"]}

    rows = []
    for label, cl, graph in (("AI (full)", ai, edges), ("AI (no noise)", ai_nn, e_nn)):
        r = {"version": v, "arch": label}
        r.update(evaluate(cl, graph))
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
