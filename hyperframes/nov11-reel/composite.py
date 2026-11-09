#!/usr/bin/env python3
"""Final composite for the Nov 11 reel (Day 8: stop writing long blogs, write to-the-point answers).

  1. Tighten the timeline (edl.json, see tools/edl.py), 10 ms audio fades at every join, cuts on the 30 fps grid.
  2. Voice: denoise (static/hiss), gentle gate against the room tail, less boxiness, a little presence,
     compression, ~-14 LUFS. Subtle SFX (whoosh / pop / ding) under the voice on the graphic beats.
  3. Picture: artifact removal, noise reduction, per-take white balance measured off the white wall
     (the wide take runs warmer than the close one), natural-skin grade with a gentle S-curve, sharpening.
  4. Camera: alternating slow push-in / pull-out, a punch-in on "GEO", an eased kick at every cut.
  5. Split windows: SEO / GEO panels on top, speaker below (head ~860 px). Full-screen B-roll is opaque in the overlay.
  7. HyperFrames overlay (renders/overlay.mov) on top, one CRF 15 encode, MP4 without edit lists.

    python3 composite.py [out.mp4]
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "../../raw/nov11.mp4"
OUT = HERE / "../../output/Day8_Stop_Long_Blogs.mp4"
edl = json.loads((HERE / "edl.json").read_text())
KEEP = [[round(a * 30) / 30, round(b * 30) / 30] for a, b in edl["keep"]]
DUR = round(sum(b - a for a, b in KEEP), 3)


def T(x):
    acc = 0.0
    for a, b in KEEP:
        if x < a: return acc
        if x <= b: return acc + x - a
        acc += b - a
    return acc


# Takes (original clock): start, white balance (rr, gg, bb) from the wall, voice gain dB, face centre y
TAKES = [
    (0.0, (0.960, 0.985, 1.060), 1.4, .38, .64),        # wall R/B 1.115, G/B 1.077
    (292 / 30, (0.955, 0.985, 1.065), 0.0, .37, .66),   # main take: R/B 1.128, G/B 1.085
    (1503 / 30, (0.970, 0.990, 1.045), 1.7, .37, .60),  # closing take: R/B 1.082, G/B 1.061
]
AUDIO_LATENCY = 0.038
AAC_PRIMING = 1024 / 44100
SPLIT = [(13.70, 50.12, 330)]         # panel on top, speaker below (head ~900 px); full-screen B-roll is opaque in the overlay

TAIL = ("eq=brightness=0.015:saturation=0.97:gamma=1.04,"
        "curves=master='0/0 0.12/0.10 0.3/0.30 0.5/0.535 0.75/0.80 0.92/0.94 1/0.99',cas=strength=0.5")
PRE = "deblock=filter=weak:block=8,hqdn3d=1.8:1.4:3.5:3.5"


def take_of(t):
    k = 0
    for i, tk in enumerate(TAKES):
        if t >= tk[0] - 1e-6: k = i
    return k


# pieces = KEEP split at take boundaries, so each piece gets its own white balance
PIECES = []
for a, b in KEEP:
    cuts = [tk[0] for tk in TAKES if a < tk[0] < b]
    pts = [a] + cuts + [b]
    PIECES += [(x, y) for x, y in zip(pts, pts[1:])]

# Camera spans on the original clock: (from, to, zoom from, zoom to)
SPANS = [(1.1, 6.9, 1.00, 1.05), (6.9, 8.226, 1.13, 1.10), (8.33, 9.578, 1.0, 1.04), (9.853, 13.321, 1.04, 1.0),
         (13.759, 19.224, 1.0, 1.06), (19.348, 23.9, 1.06, 1.0), (23.9, 28.701, 1.0, 1.06), (28.833, 35.9, 1.06, 1.0),
         (35.9, 41.0, 1.0, 1.05), (41.0, 46.946, 1.05, 1.0), (47.077, 50.1, 1.0, 1.05), (50.1, 52.75, 1.08, 1.04)]
CAM = []
for a, b, z0, z1 in SPANS:
    cy, cx = TAKES[take_of(a)][3], TAKES[take_of(a)][4]
    CAM += [(a + 0.001, z0, cx, cy), (b - 0.001, z1, cx, cy)]
CUTS = sorted(set([a for a, _ in KEEP[1:]]))


def cam_expr():
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
for tk in TAKES:
    gain = f"if(gte(t,{tk[0]}),{10 ** (tk[2] / 20):.4f},{gain})"

# SFX on the original clock: name, time, gain (kept low: under the voice)
SFX = [("whoosh", 1.2, .16), ("pop", 5.0, .15), ("whip", 6.95, .22), ("thud", 7.1, .22), ("whoosh", 10.0, .18), ("pop", 10.4, .14),
       ("whoosh", 13.8, .2), ("pop", 16.5, .14), ("whip", 18.0, .2), ("ding", 19.5, .12), ("whoosh", 21.45, .2), ("pop", 24.0, .14),
       ("ding", 29.0, .12), ("whoosh", 32.0, .2), ("pop", 34.15, .15), ("thud", 36.1, .2), ("whoosh", 39.1, .18), ("pop", 40.2, .14),
       ("pop", 41.2, .14), ("ding", 42.9, .12), ("pop", 45.0, .14), ("pop", 47.25, .14), ("whoosh", 50.3, .16), ("ding", 51.0, .12)]


def main(out_path):
    n = len(PIECES)
    z, x, y = cam_expr()
    g = [f"[0:v]split={n}" + "".join(f"[vs{i}]" for i in range(n))]
    for i, (a, b) in enumerate(PIECES):
        rr, gg, bb = TAKES[take_of(a)][1]
        g.append(f"[vs{i}]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS,{PRE},colorchannelmixer=rr={rr}:gg={gg}:bb={bb}[vc{i}]")
    g.append("".join(f"[vc{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,fps=30,{TAIL},split={1 + len(SPLIT)}[u0]" +
             "".join(f"[u{k + 1}]" for k in range(len(SPLIT))))
    g.append(f"[u0]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1080x1920:fps=30[f0]")
    for k, (a, b, top) in enumerate(SPLIT):
        g.append(f"[u{k + 1}]crop=1080:1160:0:{top},scale=2160:2320:flags=lanczos,"
                 f"zoompan=z='{z}':x='clip(iw*0.66-iw/zoom/2,0,iw-iw/zoom)':y='(ih-ih/zoom)*0.30':d=1:s=1080x1160:fps=30[h{k}]")
        g.append(f"[f{k}][h{k}]overlay=0:760:enable='between(t,{T(a):.3f},{T(b) - 0.001:.3f})'[f{k + 1}]")
    g.append(f"[f{len(SPLIT)}][1:v]overlay=0:0:format=auto:eof_action=pass[v]")

    g.append(f"[0:a]volume='{gain}':eval=frame,asplit={len(KEEP)}" + "".join(f"[as{i}]" for i in range(len(KEEP))))
    for i, (a, b) in enumerate(KEEP):
        d = b - a
        g.append(f"[as{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[ac{i}]")
    g.append("".join(f"[ac{i}]" for i in range(len(KEEP))) + f"concat=n={len(KEEP)}:v=0:a=1,highpass=f=80,afftdn=nr=14:nf=-42:tn=1,anlmdn=s=4:p=0.002:r=0.006,"
             "agate=threshold=0.012:ratio=1.8:attack=6:release=140:range=0.35,"
             "equalizer=f=280:t=q:w=1.1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=9000:t=h:w=1:g=1,"
             "acompressor=threshold=0.09:ratio=2.5:attack=8:release=160:makeup=1.6,volume=7.2dB,alimiter=limit=0.85,"
             f"atrim=start={AUDIO_LATENCY:.4f},asetpts=PTS-STARTPTS,apad=pad_dur={AUDIO_LATENCY:.4f}[voice]")
    inputs = ["-i", str(SRC), "-i", str(HERE / "renders/overlay.mov")]
    for k, (name, t, gn) in enumerate(SFX):
        inputs += ["-i", str(HERE / f"assets/sfx/{name}.wav")]
        ms = int(T(t) * 1000)
        g.append(f"[{k + 2}:a]aformat=sample_rates=44100:channel_layouts=mono,volume={gn},adelay={ms}:all=1[sx{k}]")
    g.append("[voice]aformat=sample_rates=44100:channel_layouts=mono[vo];[vo]" + "".join(f"[sx{k}]" for k in range(len(SFX))) +
             f"amix=inputs={1 + len(SFX)}:normalize=0:duration=first,alimiter=limit=0.89,"
             f"atrim=start={AAC_PRIMING:.4f},asetpts=PTS-STARTPTS,apad=pad_dur={AAC_PRIMING:.4f}[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs,
           "-filter_complex", ";\n".join(g), "-map", "[v]", "-map", "[a]",
           "-t", f"{DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", "44100",
           "-movflags", "+faststart+negative_cts_offsets", "-use_editlist", "0", str(out_path)]
    subprocess.run(cmd, check=True)
    print("Wrote", Path(out_path).resolve())


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
