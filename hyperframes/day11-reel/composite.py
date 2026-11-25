#!/usr/bin/env python3
"""Final composite for Day 11 (keywords are dead, meet entities: what entity SEO is).

  1. One continuous take, nothing cut (no pause in the delivery is long enough to tighten), on the 30 fps grid.
  2. Voice: denoise (static/hiss), gentle gate against the room tail, less boxiness, a little presence,
     compression, ~-14 LUFS. Subtle SFX (whoosh / pop / ding) under the voice on the graphic beats.
  3. Picture: artifact removal, noise reduction, white balance neutralised off the white wall (R/B 1.075, G/B 1.067),
     clean natural-skin grade (brighter mids, lifted shadows, gentle S-curve), crisp sharpening on a 4K-upscaled frame.
  4. Camera: alternating punch-in / wide holds on each beat, eased kick at every change, centred on the face.
  5. HyperFrames overlay (renders/overlay.mov) on top, one CRF 18 encode (CRF 15 is 131 MB, over the 100 MB GitHub limit), MP4 without edit lists.

    python3 composite.py [out.mp4]
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "../../raw/day11_entities.mp4"
OUT = HERE / "../../output/Day11_Keywords_Dead_Meet_Entities.mp4"
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
    (0.0, (0.955, 0.965, 1.030), 0.0, .47, .62),        # one take: wall R/B 1.075, G/B 1.067 -> neutral
]
AUDIO_LATENCY = 0.038
AAC_PRIMING = 1024 / 44100
SPLIT = []

TAIL = ("eq=brightness=0.018:saturation=0.97:gamma=1.05,"
        "curves=master='0/0.01 0.12/0.105 0.3/0.30 0.5/0.54 0.75/0.80 0.92/0.94 1/0.985',cas=strength=0.55")
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
SPANS = [(0.03, 4.12, 1.4, 1.34), (4.12, 9.3, 1.18, 1.26), (9.3, 11.7, 1.4, 1.34), (11.7, 15.26, 1.18, 1.26), (15.26, 19.42, 1.4, 1.34), (19.42, 23.4, 1.18, 1.26), (23.4, 27.37, 1.4, 1.34), (27.37, 31.08, 1.18, 1.26), (31.08, 35.07, 1.4, 1.34), (35.07, 39.12, 1.18, 1.26), (39.12, 43.48, 1.4, 1.34), (43.48, 46.48, 1.18, 1.26), (46.48, 50.08, 1.4, 1.34), (50.08, 54.32, 1.18, 1.26), (54.32, 56.6, 1.4, 1.34)]
CAM = []
for a, b, z0, z1 in SPANS:
    cy, cx = TAKES[take_of(a)][3], TAKES[take_of(a)][4]
    CAM += [(a + 0.001, z0, cx, cy), (b - 0.001, z1, cx, cy)]
JUMPS = [4.12, 9.3, 11.7, 15.26, 19.42, 23.4, 27.37, 31.08, 35.07, 39.12, 43.48, 46.48, 50.08, 54.32]
CUTS = sorted(set([a for a, _ in KEEP[1:]] + JUMPS))


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
SFX = [('whoosh', 0.08, 0.2), ('thud', 0.9, 0.22), ('pop', 1.82, 0.16), ('whoosh', 4.14, 0.16), ('pop', 5.2, 0.12), ('pop', 5.42, 0.12), ('pop', 5.65, 0.12), ('pop', 6.15, 0.13), ('pop', 8.6, 0.13), ('whoosh', 9.32, 0.16), ('ding', 11.12, 0.1), ('whoosh', 11.74, 0.16), ('whoosh', 15.28, 0.16), ('pop', 23.8, 0.12), ('pop', 25.2, 0.12), ('thud', 26.34, 0.24), ('whoosh', 27.39, 0.16), ('pop', 30.67, 0.12), ('pop', 32.27, 0.12), ('pop', 33.41, 0.12), ('pop', 34.53, 0.12), ('pop', 35.86, 0.12), ('thud', 37.1, 0.22), ('whoosh', 39.14, 0.16), ('swoosh', 41.1, 0.16), ('ding', 43.9, 0.1), ('whoosh', 46.5, 0.16), ('whip', 48.4, 0.2), ('whoosh', 50.1, 0.16), ('pop', 51.38, 0.13), ('ding', 54.36, 0.14)]


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
                 f"zoompan=z='{z}':x='clip(iw*0.33-iw/zoom/2,0,iw-iw/zoom)':y='(ih-ih/zoom)*0.30':d=1:s=1080x1160:fps=30[h{k}]")
        g.append(f"[f{k}][h{k}]overlay=0:760:enable='between(t,{T(a):.3f},{T(b) - 0.001:.3f})'[f{k + 1}]")
    g.append(f"[f{len(SPLIT)}][1:v]overlay=0:0:format=auto:eof_action=pass[v]")

    g.append(f"[0:a]volume='{gain}':eval=frame,asplit={len(KEEP)}" + "".join(f"[as{i}]" for i in range(len(KEEP))))
    for i, (a, b) in enumerate(KEEP):
        d = b - a
        g.append(f"[as{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[ac{i}]")
    g.append("".join(f"[ac{i}]" for i in range(len(KEEP))) + f"concat=n={len(KEEP)}:v=0:a=1,highpass=f=80,afftdn=nr=14:nf=-42:tn=1,anlmdn=s=4:p=0.002:r=0.006,"
             "agate=threshold=0.012:ratio=1.8:attack=6:release=140:range=0.35,"
             "equalizer=f=280:t=q:w=1.1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=9000:t=h:w=1:g=1,"
             "acompressor=threshold=0.09:ratio=2.5:attack=8:release=160:makeup=1.6,volume=6.6dB,alimiter=limit=0.85:level=0,"
             f"atrim=start={AUDIO_LATENCY:.4f},asetpts=PTS-STARTPTS,apad=pad_dur={AUDIO_LATENCY:.4f}[voice]")
    inputs = ["-i", str(SRC), "-i", str(HERE / "renders/overlay.mov")]
    for k, (name, t, gn) in enumerate(SFX):
        inputs += ["-i", str(HERE / f"assets/sfx/{name}.wav")]
        ms = int(T(t) * 1000)
        g.append(f"[{k + 2}:a]aformat=sample_rates=44100:channel_layouts=mono,volume={gn},adelay={ms}:all=1[sx{k}]")
    g.append("[voice]aformat=sample_rates=44100:channel_layouts=mono[vo];[vo]" + "".join(f"[sx{k}]" for k in range(len(SFX))) +
             f"amix=inputs={1 + len(SFX)}:normalize=0:duration=first,alimiter=limit=0.89:level=0,"
             f"atrim=start={AAC_PRIMING:.4f},asetpts=PTS-STARTPTS,apad=pad_dur={AAC_PRIMING:.4f}[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs,
           "-filter_complex", ";\n".join(g), "-map", "[v]", "-map", "[a]",
           "-t", f"{DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", "44100",
           "-movflags", "+faststart+negative_cts_offsets", "-use_editlist", "0", str(out_path)]
    subprocess.run(cmd, check=True)
    print("Wrote", Path(out_path).resolve())


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
