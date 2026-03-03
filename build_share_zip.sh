#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

ZIP_NAME="portfolio-dashboard-share.zip"
rm -f "$ZIP_NAME"

zip -r "$ZIP_NAME" \
  dashboard.py \
  main.py \
  portfolio_data.json \
  readme.md \
  requirements-dashboard.txt \
  run_dashboard.sh \
  README-FRIEND.md

echo "Created: $(pwd)/$ZIP_NAME"
