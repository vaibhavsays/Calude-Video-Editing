#!/usr/bin/env bash
# Lay the HyperFrames graphics layer (logos + captions, ProRes 4444 with alpha) over the untouched footage,
# mix in the SFX, and encode once at CRF 12.
# Usage: ./composite.sh [out.mp4]
#   (render the overlay first: npx hyperframes render --format mov --fps 30 -o renders/overlay.mov;
#    SFX come from: python3 tools/make_sfx.py assets/sfx)
set -euo pipefail
cd "$(dirname "$0")"
SRC=../../raw/ai_seo_tools.mp4
OUT=${1:-../../output/AI_SEO_Tools.mp4}

# Each logo group enters at G; its whoosh peaks as the tag lands and each of the 3 cards gets a pop as it lands.
GROUPS="0.95 3.15 5.35 7.35 10.6"
SFX=""
for g in $GROUPS; do
  SFX+=" whoosh:$(python3 -c "print(round($g-0.38,3))"):0.30"
  for i in 0 1 2; do SFX+=" pop:$(python3 -c "print(round($g+0.16+$i*0.12,3))"):0.32"; done
done

inputs=(-i "$SRC" -i renders/overlay.mov)
n=2; amix="[0:a]"; achain=""
for e in $SFX; do
  IFS=: read -r name t gain <<<"$e"
  [[ $(python3 -c "print(1 if $t>=0 else 0)") == 1 ]] || t=0
  inputs+=(-i "assets/sfx/$name.wav")
  ms=$(python3 -c "print(int($t*1000))")
  achain+="[$n:a]aresample=48000,adelay=$ms|$ms,volume=$gain[s$n];"; amix+="[s$n]"; n=$((n+1))
done
nin=$((n-2+1))

ffmpeg -y -v error "${inputs[@]}" -filter_complex "
[0:v][1:v]overlay=0:0:format=auto:eof_action=pass[v];
${achain}[0:a]aresample=48000[a0];[a0]${amix#\[0:a\]}amix=inputs=$nin:normalize=0:duration=first,alimiter=limit=0.95[a]
" -map "[v]" -map "[a]" \
  -c:v libx264 -preset slow -crf 12 -profile:v high -pix_fmt yuv420p -tune film -r 30 \
  -c:a aac -b:a 320k -movflags +faststart "$OUT"
echo "Wrote $OUT"
