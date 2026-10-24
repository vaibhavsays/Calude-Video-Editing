#!/usr/bin/env bash
# Final assembly for the GBP AI Visibility reel.
#
# The footage is cut and laid out here with FFmpeg and encoded once; the
# graphics (B-roll panel, scenes, CTA text) come from the HyperFrames render
# as a transparent MOV. The cut list and every time live in edit.py.
#
#   python3 edit.py
#   npx --yes hyperframes@0.8.189 render --format mov --fps 30 --video-frame-format png -o renders/overlay.mov
#   ./build.sh
set -euo pipefail
cd "$(dirname "$0")"

RAW=../../raw/gbp-ai-visibility
OUT=../../output/GBP_AI_Visibility_reel.mp4

CTA_IN=0.6        # CTA clip: start of the spoken line
CTA_OUT=5.2       # CTA clip: before the camera swings away
CTA_GAIN=3.9dB    # CTA was recorded quieter (-30.4 vs -26.5 LUFS)

# Main clip with the pauses removed: one trim per kept segment, short audio
# fades at each cut so the joins don't click.
AROLL=$(python3 - <<'EOF'
import json
e = json.load(open("edit.json"))
segs = e["segments"]
parts, labels = [], []
for i, (a, b) in enumerate(segs):
    d = b - a
    parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];")
    parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d - 0.012:.3f}:d=0.012[a{i}];")
    labels.append(f"[v{i}][a{i}]")
parts.append("".join(labels) + f"concat=n={len(segs)}:v=1:a=1[av][aa];")
print("".join(parts))
EOF
)
SPLIT_START=$(python3 -c 'import json;print(json.load(open("edit.json"))["split_start"])')
CTA_HOLD=$(python3 -c 'import json;print(json.load(open("edit.json"))["cta_hold"])')

ffmpeg -y \
  -i "$RAW/main.mp4" \
  -i "$RAW/cta.mov" \
  -i renders/overlay.mov \
  -filter_complex "
    ${AROLL}
    [av]fps=30,hflip,split[full][sp];
    [sp]crop=1080:1090:0:280,pad=1080:1920:0:830:color=0xfbf3ee[low];
    [full][low]overlay=0:0:enable='gte(t,${SPLIT_START})'[aroll];
    [1:v]trim=${CTA_IN}:${CTA_OUT},setpts=PTS-STARTPTS,fps=30,scale=1080:1920,setsar=1,gblur=sigma=38,eq=brightness=-0.10:saturation=0.8,tpad=stop_mode=clone:stop_duration=${CTA_HOLD}[cta];
    [aroll][cta]concat=n=2:v=1:a=0[base];
    [base][2:v]overlay=0:0:format=auto,format=yuv420p[v];
    [1:a:0]atrim=${CTA_IN}:${CTA_OUT},asetpts=PTS-STARTPTS,volume=${CTA_GAIN},afade=t=in:d=0.03,apad=pad_dur=${CTA_HOLD}[a1];
    [aa][a1]concat=n=2:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 15 -preset slow -profile:v high -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 256k -movflags +faststart \
  "$OUT"

echo "Wrote $OUT"
