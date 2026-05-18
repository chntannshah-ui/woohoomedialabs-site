#!/usr/bin/env bash
# preview.sh — run locally to see the site working in your real browser
#
# Usage: bash preview.sh
# Opens at http://localhost:8000

cd "$(dirname "$0")"
echo ""
echo "──────────────────────────────────────────────"
echo "  Woo Hoo Media Labs — Local Preview"
echo "──────────────────────────────────────────────"
echo ""
echo "  Open in browser: http://localhost:8000"
echo "  Press Ctrl+C to stop"
echo ""
python3 -m http.server 8000
