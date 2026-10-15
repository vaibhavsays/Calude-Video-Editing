#!/usr/bin/env bash
# Final composite. The footage is never re-captured by the browser:
#   1. renders/overlay.mov  = HyperFrames graphics layer (captions, B-roll, motion graphics), ProRes 4444 with alpha
#   2. ffmpeg: hook card (0-4.717s), hard punch-in zooms (Lanczos), overlay, SFX, single CRF 12 encode.
# Usage: ./composite.sh [out.mp4]
#   (render the overlay first: npx hyperframes render --format mov --fps 60 -o renders/overlay.mov;
#    SFX come from: python3 tools/make_sfx.py assets/sfx)
set -euo pipefail
cd "$(dirname "$0")"
SRC=../../raw/day1_invisible.mp4
OUT=${1:-../../output/AI_SEO_Day1_Invisible.mp4}
HOOK_END=4.717

# Punch-ins: start end zoom vertical-focus(0 top .. 1 bottom). Hard cuts in and out, like a jump-cut punch.
ZOOMS="10.41:13.867:1.14:0.30 17.17:18.1:1.25:0.32 27.8:31.2:1.12:0.35"

# SFX: name:time:gain. Times are where each sound starts; whips/whooshes are timed to peak on the visual hit.
SFX="whoosh:0.0:0.32 whip:0.0:0.42
swoosh:4.45:0.40 whip:4.85:0.38 whip:7.86:0.30
flyby:9.75:0.34
whip:13.62:0.40 swoosh:15.35:0.28 whip:16.9:0.40
swoosh:17.85:0.32 whoosh:19.55:0.40 flyby:22.6:0.36
whip:25.03:0.40 swoosh:27.45:0.30
whip:30.93:0.40 swoosh:31.95:0.26 flyby:33.65:0.36 swoosh:35.35:0.26"

inputs=(-i "$SRC" -i renders/overlay.mov -loop 1 -framerate 60 -t 37.8 -i assets/card_mask.png)
n=3; amix="[0:a]"; achain=""
for e in $SFX; do
  IFS=: read -r name t g <<<"$e"
  inputs+=(-i "assets/sfx/$name.wav")
  ms=$(python3 -c "print(int($t*1000))")
  achain+="[$n:a]aresample=48000,adelay=$ms|$ms,volume=$g*0.62[s$n];"; amix+="[s$n]"; n=$((n+1))
done
nin=$((n-3+1))

# zoom layers
nz=$(wc -w <<<"$ZOOMS"); vchain="[0:v]split=$((nz+3))[base][hbg][hcard]"
for i in $(seq 1 $nz); do vchain+="[zs$i]"; done; vchain+=";"
prev=base; i=0
for e in $ZOOMS; do
  i=$((i+1)); IFS=: read -r s en z fy <<<"$e"
  w=$(python3 -c "print(int(1080/$z)//2*2)"); h=$(python3 -c "print(int(1920/$z)//2*2)")
  x=$(( (1080-w)/2 )); y=$(python3 -c "print(int((1920-$h)*$fy))")
  vchain+="[zs$i]crop=$w:$h:$x:$y,scale=1080:1920:flags=lanczos[z$i];[$prev][z$i]overlay=0:0:enable='between(t,$s,$en)'[p$i];"
  prev=p$i
done

ffmpeg -y -v error "${inputs[@]}" -filter_complex "
${vchain}
[hbg]scale=1350:2400:flags=bicubic,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18:saturation=0.8[bg];
[hcard]scale=800:1422:flags=lanczos[cardv];
[cardv][2:v]alphamerge[card];
[bg][card]overlay=140:400:shortest=1[hook];
[$prev][hook]overlay=0:0:enable='lt(t,$HOOK_END)'[v1];
[1:v]fps=60[ov];
[v1][ov]overlay=0:0:format=auto:eof_action=pass[v];
${achain}${amix}amix=inputs=$nin:normalize=0:duration=first,alimiter=limit=0.95[a]
" -map "[v]" -map "[a]" -t 37.75 \
  -c:v libx264 -preset slow -crf 12 -profile:v high -pix_fmt yuv420p -r 60 -tune film \
  -c:a aac -b:a 320k -movflags +faststart "$OUT"
echo "Wrote $OUT"
