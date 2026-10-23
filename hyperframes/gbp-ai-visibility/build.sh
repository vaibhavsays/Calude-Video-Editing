#!/usr/bin/env bash
# Final assembly for the GBP AI Visibility reel.
#
# The footage is cut and laid out here with FFmpeg and encoded once; the
# graphics (B-roll panel, divider, 0% card, CTA text) come from the HyperFrames
# render as a transparent MOV. Times must match the constants in index.html.
#
#   npx --yes hyperframes@0.8.189 render --format mov --fps 30 --video-frame-format png -o renders/overlay.mov
#   ./build.sh
set -euo pipefail
cd "$(dirname "$0")"

RAW=../../raw/gbp-ai-visibility
OUT=../../output/GBP_AI_Visibility_reel.mp4

AROLL_END=49.75   # main clip is cut here (just before the trailing silence)
SPLIT_START=10.1  # speaker drops to the bottom half under the screen recording
CTA_IN=0.6        # CTA clip: start of the spoken line
CTA_OUT=5.2       # CTA clip: before the camera swings away
CTA_HOLD=1.2      # freeze on the last CTA frame so the text can be read
CTA_GAIN=3.9dB    # CTA was recorded quieter (-30.4 vs -26.5 LUFS)

ffmpeg -y \
  -i "$RAW/main.mp4" \
  -i "$RAW/cta.mov" \
  -i renders/overlay.mov \
  -filter_complex "
    [0:v]trim=0:${AROLL_END},setpts=PTS-STARTPTS,fps=30,hflip,split[full][sp];
    [sp]crop=1080:1090:0:280,pad=1080:1920:0:830:color=0xfbf3ee[low];
    [full][low]overlay=0:0:enable='gte(t,${SPLIT_START})'[aroll];
    [1:v]trim=${CTA_IN}:${CTA_OUT},setpts=PTS-STARTPTS,fps=30,scale=1080:1920,setsar=1,gblur=sigma=38,eq=brightness=-0.10:saturation=0.8,tpad=stop_mode=clone:stop_duration=${CTA_HOLD}[cta];
    [aroll][cta]concat=n=2:v=1:a=0[base];
    [base][2:v]overlay=0:0:format=auto,format=yuv420p[v];
    [0:a]atrim=0:${AROLL_END},asetpts=PTS-STARTPTS,afade=t=out:st=$(echo "${AROLL_END} - 0.04" | bc):d=0.04[a0];
    [1:a:0]atrim=${CTA_IN}:${CTA_OUT},asetpts=PTS-STARTPTS,volume=${CTA_GAIN},afade=t=in:d=0.03,apad=pad_dur=${CTA_HOLD}[a1];
    [a0][a1]concat=n=2:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 15 -preset slow -profile:v high -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 256k -movflags +faststart \
  "$OUT"

echo "Wrote $OUT"
