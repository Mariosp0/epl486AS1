#!/usr/bin/env bash
# Phase 5 - build report/report.pdf from report/report.md (pandoc + headless Chromium).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/report"
pandoc report.md -s --toc --toc-depth=2 --embed-resources --css style.css \
  --resource-path=.:.. -o report.html
CHROME="${CHROME:-$(command -v chromium || command -v google-chrome || echo /opt/pw-browsers/chromium-1194/chrome-linux/chrome)}"
"$CHROME" --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$ROOT/report/report.pdf" "file://$ROOT/report/report.html" 2>/dev/null
echo "report/report.pdf written"
