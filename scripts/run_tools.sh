#!/usr/bin/env bash
# Phase 3.2 / 3.3 - run the course tools on every collected version.
#   DependencyExtractor.jar -> data/dependencies/<version>.csv
#   JNode.jar               -> data/noise/<version>.csv
# Usage: scripts/run_tools.sh [version ...]   (default: all in data/versions.csv)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data/dependencies data/noise logs
VERSIONS=("$@")
if [ ${#VERSIONS[@]} -eq 0 ]; then
  mapfile -t VERSIONS < <(tail -n +2 data/versions.csv | cut -d, -f1)
fi
for v in "${VERSIONS[@]}"; do
  ws="data/workspace/$v"
  if [ ! -s "data/dependencies/$v.csv" ]; then
    java -jar tools/DependencyExtractor.jar "$ws/bin/spring-ai-$v.jar" "data/dependencies/$v.csv" > "logs/deps_$v.log" 2>&1
  fi
  if [ ! -s "data/noise/$v.csv" ]; then
    java -Xmx6g -jar tools/JNode-fast.jar "$ws" > "logs/jnode_$v.log" 2>&1
    mv "$ws/jnodeOutput_$v.csv" "data/noise/$v.csv"
  fi
  echo "done $v"
done
