#!/usr/bin/env bash
# Day 4 reel: both HyperFrames layers, then the final composite.
#   1. python3 composite.py base && python3 tools/matte.py <BiRefNet-portrait.onnx>   (speaker mattes, once)
#   2. ./render.sh
set -euo pipefail
cd "$(dirname "$0")"
trap 'sed -i "s/^window.LAYER = .*/window.LAYER = \"front\";/" layer.js' EXIT
sed -i 's/^window.LAYER = .*/window.LAYER = "behind";/' layer.js
npx hyperframes render --format mov --fps 30 -o renders/behind.mov
sed -i 's/^window.LAYER = .*/window.LAYER = "front";/' layer.js
npx hyperframes render --format mov --fps 30 -o renders/overlay.mov
python3 composite.py
