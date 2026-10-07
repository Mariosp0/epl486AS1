#!/usr/bin/env bash
# Phase 3.3 - run JNode for all versions with N parallel workers.
# Each worker claims a version through an atomic lock directory.
# Usage: scripts/run_jnode_pool.sh [workers]
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data/noise logs locks
worker() {
  for v in $(tail -n +2 data/versions.csv | cut -d, -f1 | tac); do
    [ -s "data/noise/$v.csv" ] && continue
    mkdir "locks/$v" 2>/dev/null || continue
    java -Xmx3g -jar tools/JNode-fast.jar "data/workspace/$v" > "logs/jnode_$v.log" 2>&1
    mv "data/workspace/$v/jnodeOutput_$v.csv" "data/noise/$v.csv" && echo "done $v"
  done
}
for i in $(seq "${1:-4}"); do worker & sleep 1; done
wait
