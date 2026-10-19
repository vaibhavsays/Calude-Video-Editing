#!/usr/bin/env bash
# Final composite for the "AI content punished?" reel.
#  1. Clean + upscale the 576x1024 WhatsApp source to 1080x1920 (deblock, light denoise, Lanczos, sharpen, gentle grade).
#  2. Full-frame shots: smooth eased zoom punches at the cuts (zoompan on a 2x canvas so the motion stays smooth).
#  3. Split windows: speaker cropped into the bottom half (B-roll fills the top half from the overlay).
#  4. HyperFrames overlay (hook, B-roll, captions; ProRes 4444 alpha) on top, SFX mixed under the voice, one CRF 14 encode.
# Usage: ./composite.sh [out.mp4]   (render the overlay first: npx hyperframes render --format mov --fps 30 -o renders/overlay.mov)
set -euo pipefail
cd "$(dirname "$0")"
SRC=../../raw/geo_video.mp4
OUT=${1:-../../output/AI_Content_Punished.mp4}

UP="deblock=filter=strong:block=8,hqdn3d=1.5:1.5:4:4,scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,unsharp=5:5:0.7:5:5:0,eq=contrast=1.05:saturation=1.08,curves=master='0/0.01 0.25/0.235 0.5/0.505 0.75/0.775 1/0.99'"

# Split windows (speaker in the bottom half) - keep in sync with MODES in index.html
SPLIT="between(t,5.5,15.75)+between(t,31.1,50.3)+between(t,61.3,78.4)+between(t,83.3,94.6)"

# Zoom on full-frame shots: level + an eased kick that settles in ~0.3s after each cut.
k() { echo "$2+$3*exp(-(it-$1)/0.13)"; }
Z="if(lt(it,3.38),$(k 0 1.0 0.14),if(lt(it,5.5),$(k 3.38 1.12 0.07),if(between(it,24.05,31.1),$(k 24.05 1.08 0.08),if(between(it,78.4,83.3),$(k 78.4 1.13 0.07),1))))"

# SFX: name:start:gain
SFX="whoosh:0.0:0.22 whip:0.0:0.28 swoosh:3.15:0.18
whoosh:5.05:0.28 pop:5.75:0.2 pop:6.3:0.2 thud:8.75:0.4 pop:11.35:0.22 pop:12.9:0.22 pop:13.8:0.22 pop:14.6:0.22
whip:15.52:0.3 pop:17.5:0.16 pop:19.45:0.25 thud:21.2:0.3 thud:22.3:0.42 swoosh:23.8:0.22
whoosh:30.65:0.28 pop:31.9:0.22 pop:32.4:0.22 pop:33.0:0.22 pop:33.5:0.22 swoosh:34.15:0.22 pop:39.0:0.22 swoosh:43.5:0.22 pop:45.0:0.22 pop:46.7:0.22 pop:48.1:0.22
whip:50.12:0.3 pop:55.6:0.22 pop:57.6:0.22 swoosh:58.0:0.2 thud:59.15:0.32 thud:60.15:0.32
whoosh:60.85:0.28 pop:66.5:0.22 pop:68.0:0.22 pop:70.3:0.22 pop:71.6:0.22 pop:75.6:0.22 swoosh:78.1:0.22
whoosh:82.85:0.28 swoosh:83.5:0.2 ding:89.4:0.26"

inputs=(-i "$SRC" -i renders/overlay.mov)
n=2; amix=""; achain=""
for e in $SFX; do
  IFS=: read -r name t gain <<<"$e"
  inputs+=(-i "assets/sfx/$name.wav")
  ms=$(python3 -c "print(int($t*1000))")
  achain+="[$n:a]aresample=48000,adelay=$ms|$ms,volume=$gain*0.75[s$n];"; amix+="[s$n]"; n=$((n+1))
done
nin=$((n-2+1))

ffmpeg -y -v error "${inputs[@]}" -filter_complex "
[0:v]$UP,split[u1][u2];
[u1]scale=2160:3840:flags=lanczos,zoompan=z='$Z':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.36':d=1:s=1080x1920:fps=30[full];
[u2]crop=1080:960:0:560[half];
[full][half]overlay=0:960:enable='$SPLIT'[v1];
[v1][1:v]overlay=0:0:format=auto:eof_action=pass[v];
${achain}[0:a]aresample=48000[a0];[a0]${amix}amix=inputs=$nin:normalize=0:duration=first,alimiter=limit=0.95[a]
" -map "[v]" -map "[a]" \
  -c:v libx264 -preset slow -crf 14 -profile:v high -pix_fmt yuv420p -tune film -r 30 -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 320k -movflags +faststart "$OUT"
echo "Wrote $OUT"
