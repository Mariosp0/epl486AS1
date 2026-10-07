#!/usr/bin/env bash
# Phase 3.3 - run JNode for all versions with N parallel workers.
# Each worker claims a version through an atomic lock directory.
# Usage: [JNODE_JAR=tools/JNode-fast.jar] [OUT=data/noise] scripts/run_jnode_pool.sh [workers]
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
JAR="${JNODE_JAR:-tools/JNode-fast-p4.jar}"
OUT="${OUT:-data/noise}"
LOCKS="locks/$(basename "$OUT")"
mkdir -p "$OUT" logs "$LOCKS"
worker() {
  for v in $(tail -n +2 data/versions.csv | cut -d, -f1 | tac); do
    [ -s "$OUT/$v.csv" ] && continue
    mkdir "$LOCKS/$v" 2>/dev/null || continue
    ws="$(mktemp -d)/$v"; mkdir -p "$ws/bin"
    cp "data/workspace/$v/bin/"*.jar "$ws/bin/"
    java -Xmx3g -jar "$JAR" "$ws" > "logs/jnode_$(basename "$OUT")_$v.log" 2>&1
    mv "$ws/jnodeOutput_$v.csv" "$OUT/$v.csv" && echo "done $v"
    rm -rf "$(dirname "$ws")"
  done
}
for i in $(seq "${1:-4}"); do worker & sleep 1; done
wait
