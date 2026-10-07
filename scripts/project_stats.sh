#!/usr/bin/env bash
# Phase 1 - verify the selection criteria from the Git history of Guava.
# Usage: scripts/project_stats.sh [clone_dir]
set -euo pipefail
DIR="${1:-/tmp/guava}"
[ -d "$DIR" ] || git clone -q --filter=blob:none https://github.com/google/guava "$DIR"
cd "$DIR"
git fetch -q --tags
echo "first commit        : $(git log --reverse --format='%ad' --date=short | head -1)"
echo "last commit         : $(git log -1 --format='%ad' --date=short)"
echo "total commits       : $(git rev-list --count HEAD)"
echo "commits since 2024  : $(git rev-list --count --since=2024-01-01 HEAD)"
echo "tags                : $(git tag | wc -l)"
LATEST="$(git tag -l "v*" --sort=creatordate | tail -1)"
git checkout -q "$LATEST"
FILES=$(find guava/src -name '*.java' | wc -l)
echo "latest tag          : $LATEST ($FILES production .java files)"
find guava/src -name '*.java' -print0 | xargs -0 cat | python3 -c '
import re, sys
s = re.sub(r"/\*.*?\*/", "", sys.stdin.read(), flags=re.S)
print("NCLOC               :", sum(1 for l in s.splitlines() if l.strip() and not l.strip().startswith("//")))'
git for-each-ref --sort=creatordate --format='%(refname:short),%(creatordate:short)' refs/tags
