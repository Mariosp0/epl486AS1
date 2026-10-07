#!/usr/bin/env python3
"""Guava - package- and class-level change log between consecutive analysed
versions -> guava/results/package_changes.csv (Guava is a single module, so
this replaces the module change log used for multi-module systems)."""
import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
os.environ.setdefault("PROJECT", "guava")
from common import DATA, RESULTS, load_dependencies, package, versions, write_csv  # noqa: E402


def main():
    vs = versions()
    pk, cl = {}, {}
    for v in vs:
        with open(os.path.join(DATA, "packages", f"{v}.csv")) as f:
            pk[v] = {r["package"] for r in csv.DictReader(f)}
        cl[v] = load_dependencies(v)[0]
    rows = []
    for a, b in zip(vs, vs[1:]):
        rows.append({"from": a, "to": b, "packages": len(pk[b]),
                     "added": len(pk[b] - pk[a]), "removed": len(pk[a] - pk[b]),
                     "classes_added": len(cl[b] - cl[a]), "classes_removed": len(cl[a] - cl[b]),
                     "added_packages": " ".join(sorted(pk[b] - pk[a])),
                     "removed_packages": " ".join(sorted(pk[a] - pk[b]))})
    write_csv(os.path.join(RESULTS, "package_changes.csv"), rows)
    for r in rows:
        print(r["to"], r["packages"], r["added"], r["removed"], r["classes_added"],
              r["classes_removed"], r["added_packages"], "|", r["removed_packages"])


if __name__ == "__main__":
    main()
