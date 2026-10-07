#!/usr/bin/env python3
"""Module-level change log between consecutive versions -> results/module_changes.csv"""
import csv
import os

from common import DATA, RESULTS, versions, write_csv


def main():
    vs = versions()
    mods = {}
    for v in vs:
        with open(os.path.join(DATA, "modules", f"{v}.csv")) as f:
            mods[v] = {r["module"] for r in csv.DictReader(f)}
    rows = []
    for a, b in zip(vs, vs[1:]):
        add, rem = sorted(mods[b] - mods[a]), sorted(mods[a] - mods[b])
        rows.append({"from": a, "to": b, "modules": len(mods[b]),
                     "added": len(add), "removed": len(rem),
                     "added_modules": " ".join(add), "removed_modules": " ".join(rem)})
    write_csv(os.path.join(RESULTS, "module_changes.csv"), rows)


if __name__ == "__main__":
    main()
