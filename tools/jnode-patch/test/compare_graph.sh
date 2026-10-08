#!/usr/bin/env bash
# Compares the class dependency graph built inside JNode with the graph of the
# course's DependencyExtractor for one analysed version (class-file level,
# distinct edges, self-dependencies excluded).
# Usage: tools/jnode-patch/test/compare_graph.sh [version]   (default 10.0)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$(cd "$HERE/../.." && pwd)"
ROOT="$(cd "$TOOLS/.." && pwd)"
V="${1:-10.0}"
JAR="$(ls "$ROOT/guava/data/workspace/$V/bin/"*.jar | head -1)"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
mkdir -p "$W/lib"; (cd "$W/lib" && unzip -oq "$TOOLS/JNode.jar" '*.jar')
for J in JNode JNode-fixed; do
  mkdir -p "$W/p_$J"
  javac -nowarn -cp "$TOOLS/$J.jar:$W/lib/*" -d "$W/p_$J" "$HERE/Probe.java"
  java -cp "$W/p_$J:$TOOLS/$J.jar:$W/lib/*" Probe "$JAR" 2>/dev/null | grep -- ' -> ' > "$W/$J.txt"
done
python3 - "$W" "$ROOT/guava/data/dependencies/$V.csv" <<'PY'
import csv, sys
w, dep = sys.argv[1], sys.argv[2]
de = {(r["dependeeClass"], r["dependencyClass"]) for r in csv.DictReader(open(dep))
      if r["dependeeClass"] != r["dependencyClass"]}
for j in ("JNode", "JNode-fixed"):
    e = set()
    for line in open(f"{w}/{j}.txt"):
        a, b = line.rstrip().split(" -> ")
        e |= {(a, d) for d in b.strip("[]").split(", ") if d}
    print(f"{j}.jar: {len(e)} edges ({sum(a == b for a, b in e)} self-dependencies); "
          f"DependencyExtractor: {len(de)}; common {len(e & de)}, "
          f"only JNode {len(e - de)}, only DependencyExtractor {len(de - e)}")
PY
