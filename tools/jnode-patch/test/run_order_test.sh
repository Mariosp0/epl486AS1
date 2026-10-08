#!/usr/bin/env bash
# Order test for the JNode graph fix (tools/jnode-patch/README.md).
# Toy system: A uses B, C uses D. The same four classes are packed in two
# archive orders (A,B,C,D and D,C,B,A); the dependency graph that JNode builds
# (ClassycleWorker) is printed for the course JNode.jar and for the fixed jar.
# Expected (correct) graph in both orders: A -> [B], B -> [], C -> [D], D -> [].
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$(cd "$HERE/../.." && pwd)"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
mkdir -p "$W/lib" "$W/cls"
(cd "$W/lib" && unzip -oq "$TOOLS/JNode.jar" '*.jar')          # ant, asm, commons-math
javac -nowarn -d "$W/cls" "$HERE"/t/*.java
(cd "$W/cls" && jar cf "$W/abcd.jar" t/A.class t/B.class t/C.class t/D.class \
             && jar cf "$W/dcba.jar" t/D.class t/C.class t/B.class t/A.class)
for J in JNode JNode-fixed; do
  mkdir -p "$W/p_$J"
  javac -nowarn -cp "$TOOLS/$J.jar:$W/lib/*" -d "$W/p_$J" "$HERE/Probe.java"
  for o in abcd dcba; do
    echo "== $J.jar, archive order $o"
    java -cp "$W/p_$J:$TOOLS/$J.jar:$W/lib/*" Probe "$W/$o.jar" 2>/dev/null | grep -- '->'
  done
done
