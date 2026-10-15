#!/usr/bin/env bash
# Final composite. The footage is never re-captured by the browser:
#   1. renders/overlay.mov  = HyperFrames graphics layer (captions, B-roll, motion graphics), ProRes 4444 with alpha
#   2. ffmpeg: hook card (0-4.717s), hard punch-in zooms, overlay, SFX, single CRF 15 encode.
# Usage: ./composite.sh [out.mp4]   (render the overlay first: npx hyperframes render --format mov --fps 60 -o renders/overlay.mov)
set -euo pipefail
cd "$(dirname "$0")"
SRC=../../raw/day1_invisible.mp4
OUT=${1:-../../output/AI_SEO_Day1_Invisible.mp4}
HOOK_END=4.717

# Punch-in zoom: z(t) and vertical focus (0 = top, 0.5 = centre). Hard cuts in/out, like a jump-cut punch.
Z="if(between(it,10.41,13.86),1.14,if(between(it,17.17,18.09),1.25,if(between(it,27.8,31.2),1.12,1)))"

# SFX cue times (seconds)
WHOOSH="4.6 5.0 9.62 13.78 13.95 17.72 18.02 19.9 24.78 25.2 27.52 31.1 33.6"
HIT="0.25 8.1 15.6 17.17 26.6 32.2 34.2 34.45 35.6"

inputs=(-i "$SRC" -i renders/overlay.mov -loop 1 -framerate 60 -t 37.8 -i assets/card_mask.png)
n=3; amix="[0:a]"; achain=""
for t in $WHOOSH; do inputs+=(-i assets/sfx/whoosh.wav); ms=$(python3 -c "print(int($t*1000))"); achain+="[$n:a]adelay=$ms|$ms,volume=0.35[s$n];"; amix+="[s$n]"; n=$((n+1)); done
for t in $HIT;    do inputs+=(-i assets/sfx/hit.wav);    ms=$(python3 -c "print(int($t*1000))"); achain+="[$n:a]adelay=$ms|$ms,volume=0.45[s$n];"; amix+="[s$n]"; n=$((n+1)); done
nin=$((n-3+1))

ffmpeg -y -v error "${inputs[@]}" -filter_complex "
[0:v]split=3[base][hbg][hcard];
[base]zoompan=z='$Z':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.38':d=1:s=1080x1920:fps=60[zoomed];
[hbg]scale=1350:2400,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18:saturation=0.8[bg];
[hcard]scale=800:1422[cardv];
[cardv][2:v]alphamerge[card];
[bg][card]overlay=140:400:shortest=1[hook];
[zoomed][hook]overlay=0:0:enable='lt(t,$HOOK_END)'[v1];
[1:v]fps=60[ov];
[v1][ov]overlay=0:0:format=auto:eof_action=pass[v];
${achain}${amix}amix=inputs=$nin:normalize=0:duration=first,alimiter=limit=0.95[a]
" -map "[v]" -map "[a]" -t 37.75 \
  -c:v libx264 -preset slow -crf 15 -profile:v high -pix_fmt yuv420p -r 60 \
  -c:a aac -b:a 256k -movflags +faststart "$OUT"
echo "Wrote $OUT"
