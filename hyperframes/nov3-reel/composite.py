#!/usr/bin/env python3
"""Final composite for the Nov 3 reel (backlink hierarchy), styled after the user's reference. Same treatment as before:
no sound effects, professional camera moves, B-roll that sometimes takes the whole frame.

  1. Tighten the user's timeline (edl.json, see tools/edl.py), 10 ms audio fades at every join.
  2. Voice: denoise (static/hiss), a gentle gate against the room tail, less boxiness, a little presence,
     gentle compression, limiter. Nothing else in the mix.
  3. Picture: 30 fps, artifact removal, noise reduction, colour correction (neutral
     white balance), natural-skin colour grading with cinematic contrast, sharpening.
  4. Camera: slow push-ins on every shot and an eased punch at every hard cut.
  5. Split windows: the speaker sits below the B-roll panel (head below 790 px). Full-screen B-roll windows are
     opaque in the overlay, so only the graphics show there while the voice carries on.
  6. HyperFrames overlay (renders/overlay.mov: B-roll, chips, captions) on top, one CRF 15 encode.

    python3 composite.py [out.mp4]
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "../../raw/nov3.mp4"
OUT = HERE / "../../output/Backlink_Hierarchy.mp4"
edl = json.loads((HERE / "edl.json").read_text())
KEEP, DUR = edl["keep"], edl["duration"]

def T(x):
    acc = 0.0
    for a, b in KEEP:
        if x < a: return acc
        if x <= b: return acc + x - a
        acc += b - a
    return acc

# Hard cuts in the upload (original clock) and per-clip voice gain in dB
CLIPS = [(0.0, 0.0), (2.57, 0.0), (8.40, 0.0), (36.37, 0.0)]
# The upload's picture runs ~0.2 s behind its sound (mouth still moving after the voice stops, e.g. at 36.1 s), and
# the voice chain adds ~0.04 s: take each video segment this much later than its audio so lips match the voice.
VIDEO_OFFSET = 0.18
# Split windows (original clock) with the source crop top for the speaker; same windows as MODES in index.html
SPLIT = [(9.90, 32.75, 330)]  # backlink pyramid on top, speaker below (head starts ~835 px)

# House look (see CLAUDE.md), in order:
#   artifact removal  - deblock the phone's compression blocks
#   noise reduction   - light temporal/spatial denoise (hqdn3d)
#   color correction  - neutral white balance off the white wall (measured for this clip: R/B 1.06)
#   color grading     - natural skin tones (no saturation/vibrance boost), brighter mids, lifted shadows,
#                       cinematic contrast (gentle S-curve: deeper blacks, rolled-off highlights)
#   sharpening        - contrast-adaptive sharpening (cas); sources below 1080x1920 are Lanczos-upscaled first
GRADE = ("deblock=filter=weak:block=8,hqdn3d=1.8:1.4:3.5:3.5,colorchannelmixer=rr=0.975:gg=0.993:bb=1.035,"
         "eq=brightness=0.015:saturation=0.97:gamma=1.04,"
         "curves=master='0/0 0.12/0.10 0.3/0.30 0.5/0.535 0.75/0.80 0.92/0.94 1/0.99',cas=strength=0.5")

# Camera keyframes on the ORIGINAL clock: (time, zoom, centre x, centre y) as fractions of the frame.
# Between keys the move is eased (smoothstep); a key with the same values holds.
# one slow push-in on the full-frame layer (only seen under the split, which covers the frame)
CAM = [(0.0, 1.0, .5, .32), (2.55, 1.05, .5, .32),      # slow push-ins per clip (the user's cuts at 2.57, 8.40, 36.37)
       (2.58, 1.06, .5, .32), (8.38, 1.0, .5, .32),
       (8.42, 1.0, .5, .32), (36.35, 1.06, .5, .32),
       (36.38, 1.08, .5, .32), (40.4, 1.02, .5, .32)]
CUTS = [c for c, _ in CLIPS]


def cam_expr():
    """zoompan z/x/y expressions on the output clock (it), with an eased kick after every hard cut."""
    keys = [(T(t), z, cx, cy) for t, z, cx, cy in CAM]
    zs, xs, ys = "1", ".5", ".5"
    for i in reversed(range(len(keys) - 1)):
        t0, z0, x0, y0 = keys[i]
        t1, z1, x1, y1 = keys[i + 1]
        d = max(t1 - t0, 1e-3)
        c = f"clip((it-{t0:.3f})/{d:.3f},0,1)"
        s = f"({c}*{c}*(3-2*{c}))"
        cond = f"lt(it,{t1:.3f})"
        zs = f"if({cond},{z0}+({z1}-{z0})*{s},{zs})"
        xs = f"if({cond},{x0}+({x1}-{x0})*{s},{xs})"
        ys = f"if({cond},{y0}+({y1}-{y0})*{s},{ys})"
    kick = "0"
    for c in reversed(CUTS):
        t0 = T(c)
        kick = f"if(gte(it,{t0:.3f}),0.06*exp(-(it-{t0:.3f})/0.14),{kick})"
    z = f"({zs})*(1+{kick})"
    x = f"clip(iw*({xs})-iw/zoom/2,0,iw-iw/zoom)"
    y = f"clip(ih*({ys})-ih/zoom/2,0,ih-ih/zoom)"
    return z, x, y

gain = "1"
for c, db in CLIPS:  # last cut outermost, so the latest matching clip wins
    gain = f"if(gte(t,{c}),{10 ** (db / 20):.4f},{gain})"


def main(out_path):
    n = len(KEEP)
    z, x, y = cam_expr()
    g = [f"[0:v]split={n}" + "".join(f"[vs{i}]" for i in range(n))]
    for i, (a, b) in enumerate(KEEP):
        g.append(f"[vs{i}]trim={a + VIDEO_OFFSET:.3f}:{b + VIDEO_OFFSET:.3f},setpts=PTS-STARTPTS[vc{i}]")
    g.append("".join(f"[vc{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,fps=30,{GRADE},split={1 + len(SPLIT)}[u0]" +
             "".join(f"[u{k + 1}]" for k in range(len(SPLIT))))
    g.append(f"[u0]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1080x1920:fps=30[f0]")
    for k, (a, b, top) in enumerate(SPLIT):
        g.append(f"[u{k + 1}]crop=1080:1160:0:{top}[h{k}]")
        g.append(f"[f{k}][h{k}]overlay=0:760:enable='between(t,{T(a):.3f},{T(b) - 0.001:.3f})'[f{k + 1}]")
    g.append(f"[f{len(SPLIT)}][1:v]overlay=0:0:format=auto:eof_action=pass[v]")

    g.append(f"[0:a]volume='{gain}':eval=frame,asplit={n}" + "".join(f"[as{i}]" for i in range(n)))
    for i, (a, b) in enumerate(KEEP):
        d = b - a
        g.append(f"[as{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[ac{i}]")
    g.append("".join(f"[ac{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,highpass=f=80,afftdn=nr=14:nf=-42:tn=1,anlmdn=s=4:p=0.002:r=0.006,"
             "agate=threshold=0.012:ratio=1.8:attack=6:release=140:range=0.35,"   # tame the room tail between words
             "equalizer=f=280:t=q:w=1.1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=9000:t=h:w=1:g=1,"
             "acompressor=threshold=0.09:ratio=2.5:attack=8:release=160:makeup=1.6,volume=3.7dB,alimiter=limit=0.85[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(SRC), "-i", str(HERE / "renders/overlay.mov"),
           "-filter_complex", ";\n".join(g), "-map", "[v]", "-map", "[a]",
           "-t", f"{DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", "44100", "-movflags", "+faststart", str(out_path)]
    subprocess.run(cmd, check=True)
    print("Wrote", Path(out_path).resolve())


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
