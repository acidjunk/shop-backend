#!/usr/bin/env bash
# Export every .drawio source in docs/diagrams/ to an SVG under
# docs/assets/diagrams/, so the mkdocs site can embed them without
# drawio being installed on the build server (e.g. on Read the Docs).
#
# Requires the drawio desktop CLI on your PATH (or DRAWIO_BIN env var):
#   macOS:   brew install --cask drawio
#   Linux:   https://github.com/jgraph/drawio-desktop/releases
#   Windows: ditto
#
# Run from the repo root after editing any .drawio file:
#   bin/export-diagrams.sh
#
# Commit the resulting SVGs alongside your .drawio changes.

set -euo pipefail

SRC_DIR="docs/diagrams"
OUT_DIR="docs/assets/diagrams"
DRAWIO_BIN="${DRAWIO_BIN:-drawio}"

if ! command -v "$DRAWIO_BIN" >/dev/null 2>&1; then
  echo "error: '$DRAWIO_BIN' not found on PATH." >&2
  echo "Install drawio desktop (see header comment) or set DRAWIO_BIN." >&2
  exit 1
fi

if [ ! -d "$SRC_DIR" ]; then
  echo "error: $SRC_DIR does not exist. Run this script from the repo root." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

shopt -s nullglob
count=0
for src in "$SRC_DIR"/*.drawio; do
  name="$(basename "$src" .drawio)"
  # Collapse spaces and non-ASCII to keep URLs friendly.
  safe="$(echo "$name" | tr ' ' '_' )"
  dst="$OUT_DIR/${safe}.svg"
  echo "Exporting: $src -> $dst"
  "$DRAWIO_BIN" --export --format svg --output "$dst" "$src"
  count=$((count + 1))
done

if [ "$count" -eq 0 ]; then
  echo "No .drawio files found in $SRC_DIR — nothing to export."
else
  echo "Exported $count diagram(s) to $OUT_DIR."
fi
