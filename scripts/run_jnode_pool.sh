#!/usr/bin/env bash
# Phase 3.3 - run JNode for all versions with N parallel workers.
# Each worker claims a version through an atomic lock directory.
# Usage: [JNODE_JAR=tools/JNode-fixed-3dec.jar] [OUT=data/noise_jnode3] scripts/run_jnode_pool.sh [workers]
# Versions whose output CSV already exists are SKIPPED: delete stale outputs
# (e.g. after changing the JNode jar) before re-running.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/tools"
cd "$ROOT/${PROJECT:-guava}"   # project folder (default guava/)
JAR="${JNODE_JAR:-$TOOLS/JNode-fixed.jar}"
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
