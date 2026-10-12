#!/usr/bin/env bash
# High-quality render: the B-roll inserts are rendered losslessly (PNG frames -> ProRes 4444)
# and laid over the untouched original, which is encoded only once. The original audio is copied as-is.
set -euo pipefail
cd "$(dirname "$0")"
BROWSER=${BROWSER:-$(ls -d /opt/pw-browsers/chromium_headless_shell-*/*/headless_shell 2>/dev/null | head -1)}
OUT=${1:-../output/AI_SEO_Day1_broll.mp4}
mkdir -p inserts
# id:startFrame (30 fps), must match INSERTS in src/Main.tsx
INSERTS="WebsiteBusiness:30 Invisible:96 AIRing:465 GoogleScale:666 FallingBehind:788"
inputs=(-i ../raw/main.mp4); chain="[0:v]null[v0]"; n=0
for e in $INSERTS; do
  id=${e%%:*}; start=${e##*:}
  # Reuse an already-rendered insert unless FORCE=1.
  [[ -f "inserts/$id.mov" && -z "${FORCE:-}" ]] || npx remotion render src/index.ts "$id" "inserts/$id.mov" --codec=prores --prores-profile=4444 \
    --image-format=png --browser-executable="$BROWSER" --log=error
  inputs+=(-i "inserts/$id.mov"); n=$((n+1))
  chain+=";[$n:v]setpts=PTS-STARTPTS+$start/30/TB[i$n];[v$((n-1))][i$n]overlay=eof_action=pass:format=auto[v$n]"
done
ffmpeg -y -v error "${inputs[@]}" -filter_complex "$chain" -map "[v$n]" -map 0:a \
  -c:v libx264 -preset slow -crf 15 -profile:v high -pix_fmt yuv420p -tune film \
  -c:a copy -movflags +faststart "$OUT"
echo "Wrote $OUT"
