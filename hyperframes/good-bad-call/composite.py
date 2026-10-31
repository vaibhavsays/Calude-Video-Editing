#!/usr/bin/env python3
"""Final composite for the "Good call / Bad call" reel. Same treatment as the tool promo and Day 5:
no sound effects, professional camera moves, B-roll that sometimes takes the whole frame.

  1. Tighten the user's timeline (edl.json, see tools/edl.py), 10 ms audio fades at every join.
  2. Voice: per-clip gain so every shot sits at the same loudness, light denoise, high-pass, a little presence,
     gentle compression, limiter. Nothing else in the mix.
  3. Picture: 30 fps, deblock + denoise, mild sharpen, clean colour boost and soft S-curve.
  4. Camera: slow push-ins on every shot and an eased punch at every hard cut.
  5. Split windows: the speaker sits below the B-roll panel (head below 790 px). Full-screen B-roll windows are
     opaque in the overlay, so only the graphics show there while the voice carries on.
  6. HyperFrames overlay (renders/overlay.mov: B-roll, chips, captions) on top, one CRF 15 encode.

    python3 composite.py [out.mp4]
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "../../raw/good_bad_call.mp4"
OUT = HERE / "../../output/Good_Call_Bad_Call.mp4"
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
CLIPS = [(0.0, 0.0), (20.93, 2.5), (38.80, 1.6), (56.60, 1.9), (90.00, 1.2), (107.17, 2.8), (121.53, 0.5)]
# Split windows (original clock) with the source crop top for the speaker; same windows as MODES in index.html
SPLIT = [(a, b, 430) for a, b in [(1.2, 7.0), (21.3, 27.5), (39.3, 45.4), (57.1, 64.0), (90.2, 95.0), (106.6, 113.5),
                                   (121.6, 128.0), (141.0, 143.5)]]  # the board windows in beats.js

GRADE = ("deblock=filter=weak:block=8,hqdn3d=2:1.5:3:3,unsharp=5:5:0.45:5:5:0,"
         "eq=contrast=1.06:saturation=1.08,vibrance=intensity=0.10,"
         "curves=master='0/0.012 0.25/0.235 0.5/0.5 0.75/0.775 1/0.988'")

# Camera keyframes on the ORIGINAL clock: (time, zoom, centre x, centre y) as fractions of the frame.
# Between keys the move is eased (smoothstep); a key with the same values holds.
CAM = [  # alternate slow push-ins and pull-outs per clip
    (0.0, 1.00, .5, .40), (20.90, 1.06, .5, .38),
    (20.93, 1.07, .5, .38), (38.75, 1.00, .5, .40),
    (38.80, 1.00, .5, .40), (56.55, 1.06, .5, .38),
    (56.60, 1.07, .5, .38), (89.95, 1.00, .5, .40),
    (90.00, 1.00, .5, .40), (107.1, 1.06, .5, .38),
    (107.17, 1.07, .5, .38), (121.5, 1.00, .5, .40),
    (121.53, 1.00, .5, .40), (143.5, 1.06, .5, .38),
]
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
        g.append(f"[vs{i}]trim={a}:{b},setpts=PTS-STARTPTS[vc{i}]")
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
    g.append("".join(f"[ac{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,afftdn=nr=8:nf=-45,highpass=f=75,"
             "equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=220:t=q:w=1:g=-1.5,"
             "acompressor=threshold=0.09:ratio=2.5:attack=8:release=160:makeup=1.6,volume=4.6dB,alimiter=limit=0.85[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(SRC), "-i", str(HERE / "renders/overlay.mov"),
           "-filter_complex", ";\n".join(g), "-map", "[v]", "-map", "[a]",
           "-t", f"{DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", "44100", "-movflags", "+faststart", str(out_path)]
    subprocess.run(cmd, check=True)
    print("Wrote", Path(out_path).resolve())


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
