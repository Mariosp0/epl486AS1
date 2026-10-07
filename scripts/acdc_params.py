#!/usr/bin/env python3
"""ACDC parameter experiment on the latest version (tutorial suggestion).

Varies the maximum cluster size of the SubGraph pattern and the set of
patterns used (b = BodyHeader, s = SubGraph, o = OrphanAdoption) and evaluates
each result. Output: results/acdc_params.csv
"""
import os
import sys
import tempfile

from common import DATA, RESULTS, versions, write_csv
from metrics import evaluate
from recover import run_acdc


def main():
    v = sys.argv[1] if len(sys.argv) > 1 else versions()[-1]
    rows = []
    for variant in ("full", "nonoise"):
        rsf = os.path.join(DATA, "rsf", f"{v}_{variant}.rsf")
        edges = [tuple(l.split()[1:]) for l in open(rsf)]
        for patterns in ("bso", "so", "bs"):
            for size in (5, 10, 20, 40, 80):
                with tempfile.NamedTemporaryFile(suffix=".rsf") as out:
                    cl = run_acdc(rsf, out.name, size, patterns)
                row = {"version": v, "graph": variant, "patterns": patterns,
                       "max_cluster_size": size}
                row.update(evaluate(cl, edges))
                rows.append(row)
                print(row, flush=True)
    write_csv(os.path.join(RESULTS, "acdc_params.csv"), rows)


if __name__ == "__main__":
    main()
