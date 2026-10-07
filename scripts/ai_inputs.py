#!/usr/bin/env python3
"""Phase 4 - prepare the information given to the AI tool (latest version).

Writes to ai/inputs/:
  modules.md            - Maven modules of the release with #class files
  packages.md           - packages with #classes and example class names
  package_deps.md       - package-level dependency graph (edge weight = number
                          of class-level dependencies), strongest edges first
"""
import csv
import os
import sys
from collections import Counter, defaultdict

from common import DATA, ROOT, load_dependencies, package, versions

PFX = "org.springframework.ai."


def short(p):
    return p[len(PFX):] if p.startswith(PFX) else p


def main():
    v = sys.argv[1] if len(sys.argv) > 1 else versions()[-1]
    out = os.path.join(ROOT, "ai", "inputs")
    os.makedirs(out, exist_ok=True)
    nodes, dep, _ = load_dependencies(v)

    with open(os.path.join(DATA, "modules", f"{v}.csv")) as f:
        mods = list(csv.DictReader(f))
    with open(os.path.join(out, "modules.md"), "w") as f:
        f.write(f"# Spring AI {v} - Maven modules (class files per module)\n\n")
        for m in mods:
            f.write(f"- {m['module']} ({m['class_files']})\n")

    by_pkg = defaultdict(list)
    for n in nodes:
        by_pkg[package(n)].append(n.rsplit(".", 1)[1])
    with open(os.path.join(out, "packages.md"), "w") as f:
        f.write(f"# Spring AI {v} - packages (prefix org.springframework.ai. omitted)\n\n")
        f.write("package | #classes | sample classes\n---|---|---\n")
        for p in sorted(by_pkg):
            cl = sorted(by_pkg[p])
            f.write(f"{short(p)} | {len(cl)} | {', '.join(cl[:6])}\n")

    pe = Counter()
    for (s, d) in dep:
        ps, pd = package(s), package(d)
        if ps != pd:
            pe[(short(ps), short(pd))] += 1
    with open(os.path.join(out, "package_deps.md"), "w") as f:
        f.write(f"# Spring AI {v} - package dependencies (from -> to : #class deps)\n\n")
        for (a, b), w in pe.most_common():
            f.write(f"{a} -> {b} : {w}\n")
    print(len(mods), "modules,", len(by_pkg), "packages,", len(pe), "package edges")


if __name__ == "__main__":
    main()
