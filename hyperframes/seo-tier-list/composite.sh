#!/usr/bin/env bash
# Colour-grade the footage, lay the HyperFrames graphics layer (tier board, item tiles, captions, B-roll cards;
# ProRes 4444 with alpha) over it, mix SFX timed to each item, and encode once at CRF 14.
# Usage: ./composite.sh [out.mp4]
#   (render the overlay first: npx hyperframes render --format mov --fps 30 -o renders/overlay.mov;
#    SFX come from: python3 tools/make_sfx.py assets/sfx)
set -euo pipefail
cd "$(dirname "$0")"
SRC=../../raw/seo_tier_list.mp4
OUT=${1:-../../output/SEO_Tier_List.mp4}

# Grade: light denoise for the phone codec, a touch more contrast and colour, cool shadows, gentle S-curve, light sharpen.
GRADE="hqdn3d=1:1:3:3,eq=contrast=1.06:saturation=1.1:brightness=0.012,colorbalance=rs=-0.02:bs=0.03:rm=-0.01:bm=0.01,curves=master='0/0.015 0.25/0.235 0.5/0.505 0.75/0.775 1/0.985',unsharp=5:5:0.5:5:5:0"

# item: intro time, place time, tier  (keep in sync with ITEMS in index.html)
ITEMS="0.12:1.45:C 6.93:8.1:A 12.53:13.7:A 23.11:24.85:B 30.4:34.2:B 44.82:46.9:B 60.08:62.6:A 71.99:72.8:S"
# B-roll cards above the head
CARDS="8.3 16.6 24.9 37.4 64.8 72.9"

SFX="swoosh:0.0:0.30"
for e in $ITEMS; do
  IFS=: read -r it pl tier <<<"$e"
  SFX+=" swoosh:$(python3 -c "print(max(0,round($it-0.2,3)))"):0.26"      # item card pops up next to its name
  SFX+=" whip:$(python3 -c "print(round($pl+0.14,3))"):0.30"               # flies to the board
  SFX+=" thud:$(python3 -c "print(round($pl+0.38,3))"):0.55"               # lands in its row
  case $tier in S|A) SFX+=" ding:$(python3 -c "print(round($pl+0.42,3))"):$([ $tier = S ] && echo 0.30 || echo 0.18)";; esac
done
for c in $CARDS; do SFX+=" pop:$c:0.22"; done

inputs=(-i "$SRC" -i renders/overlay.mov)
n=2; amix=""; achain=""
for e in $SFX; do
  IFS=: read -r name t gain <<<"$e"
  inputs+=(-i "assets/sfx/$name.wav")
  ms=$(python3 -c "print(int($t*1000))")
  achain+="[$n:a]aresample=48000,adelay=$ms|$ms,volume=$gain*0.7[s$n];"; amix+="[s$n]"; n=$((n+1))
done
nin=$((n-2+1))

ffmpeg -y -v error "${inputs[@]}" -filter_complex "
[0:v]$GRADE[g];
[g][1:v]overlay=0:0:format=auto:eof_action=pass[v];
${achain}[0:a]aresample=48000[a0];[a0]${amix}amix=inputs=$nin:normalize=0:duration=first,alimiter=limit=0.95[a]
" -map "[v]" -map "[a]" \
  -c:v libx264 -preset slow -crf 14 -profile:v high -pix_fmt yuv420p -tune film -r 30 -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 320k -movflags +faststart "$OUT"
echo "Wrote $OUT"
