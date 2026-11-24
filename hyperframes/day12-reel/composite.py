#!/usr/bin/env python3
"""Final composite for Day 12 (15 AI SEO factors), with the 2 s skateboard-fall visual hook in front
(assets/hook/shake_swerve.mp4: "your website is falling like this"). Overlay, captions and SFX are on the
output clock = HOOK + T(original).

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
SRC = HERE / "../../raw/fall.mp4"
OUT = HERE / "../../output/Day12_15_AI_SEO_Factors.mp4"
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
    (0.0, (0.955, 0.985, 1.060), 0.0, .46, .54),        # talking take: wall R/B 1.15, G/B 1.09
    (288 / 30, (0.960, 1.000, 1.050), 0.4, .45, .46),   # over-the-shoulder desk take: wall R/B 1.11, G/B 1.035
]
HOOK = HERE / "assets/hook/shake_swerve.mp4"
HOOK_DUR = 61 / 30                       # 2.033 s, 61 frames
AUDIO_LATENCY = 0.038
AAC_PRIMING = 1024 / 44100
SPLIT = []

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
SPANS = [(0.45, 3.7, 1.12, 1.18), (3.7, 6.3, 1.26, 1.2), (6.3, 9.6, 1.14, 1.2), (9.6, 13.9, 1.0, 1.06), (13.9, 17.7, 1.1, 1.04), (17.7, 23.45, 1.0, 1.06), (23.45, 29.0, 1.1, 1.04), (29.0, 33.4, 1.0, 1.06), (33.4, 38.05, 1.1, 1.04), (38.05, 42.87, 1.0, 1.06), (42.87, 47.3, 1.1, 1.04), (47.3, 50.95, 1.0, 1.06)]
CAM = []
for a, b, z0, z1 in SPANS:
    cy, cx = TAKES[take_of(a)][3], TAKES[take_of(a)][4]
    CAM += [(a + 0.001, z0, cx, cy), (b - 0.001, z1, cx, cy)]
JUMPS = [3.7, 6.3, 13.9, 17.7, 23.45, 29.0, 33.4, 38.05, 42.87, 47.3]
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
SFX = [("whoosh", 0.5, 0.18), ("thud", 3.8, 0.2), ("pop", 4.21, 0.14), ("whoosh", 8.44, 0.18), ("pop", 9.55, 0.13), ("pop", 10.83, 0.13), ("pop", 12.955, 0.13), ("pop", 14.11, 0.13), ("pop", 17.732, 0.13), ("pop", 19.056, 0.13), ("pop", 21.376, 0.13), ("pop", 23.48, 0.13), ("pop", 25.056, 0.13), ("pop", 29.586, 0.13), ("pop", 31.395, 0.13), ("pop", 34.052, 0.13), ("pop", 35.555, 0.13), ("pop", 38.18, 0.13), ("pop", 40.416, 0.13), ("ding", 44.85, 0.12), ("ding", 46.05, 0.12), ("ding", 47.09, 0.12), ("ding", 47.83, 0.12)]


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
    g.append(f"[2:v]fps=30,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p,trim=duration={HOOK_DUR:.4f},setpts=PTS-STARTPTS[hv]")
    g.append(f"[f{len(SPLIT)}]format=yuv420p[fm];[hv][fm]concat=n=2:v=1:a=0[fall]")
    g.append("[fall][1:v]overlay=0:0:format=auto:eof_action=pass[v]")

    g.append(f"[0:a]volume='{gain}':eval=frame,asplit={len(KEEP)}" + "".join(f"[as{i}]" for i in range(len(KEEP))))
    for i, (a, b) in enumerate(KEEP):
        d = b - a
        g.append(f"[as{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[ac{i}]")
    g.append("".join(f"[ac{i}]" for i in range(len(KEEP))) + f"concat=n={len(KEEP)}:v=0:a=1,highpass=f=80,afftdn=nr=14:nf=-42:tn=1,anlmdn=s=4:p=0.002:r=0.006,"
             "agate=threshold=0.012:ratio=1.8:attack=6:release=140:range=0.35,"
             "equalizer=f=280:t=q:w=1.1:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=9000:t=h:w=1:g=1,"
             "acompressor=threshold=0.09:ratio=2.5:attack=8:release=160:makeup=1.6,volume=3.9dB,alimiter=limit=0.85,"
             f"atrim=start={AUDIO_LATENCY:.4f},asetpts=PTS-STARTPTS,apad=pad_dur={AUDIO_LATENCY:.4f}[voice]")
    inputs = ["-i", str(SRC), "-i", str(HERE / "renders/overlay.mov"), "-i", str(HOOK)]
    # hook sound (its own whoosh/crash), a touch quieter than the voice, faded out into the cut
    g.append(f"[2:a]aresample=44100,aformat=sample_rates=44100:channel_layouts=mono,atrim=0:{HOOK_DUR:.4f},asetpts=PTS-STARTPTS,"
             f"apad=whole_dur={HOOK_DUR:.4f},volume=-3dB,afade=t=out:st={HOOK_DUR - 0.15:.4f}:d=0.15[ha]")
    for k, (name, t, gn) in enumerate(SFX):
        inputs += ["-i", str(HERE / f"assets/sfx/{name}.wav")]
        ms = int((HOOK_DUR + T(t)) * 1000)
        g.append(f"[{k + 3}:a]aformat=sample_rates=44100:channel_layouts=mono,volume={gn},adelay={ms}:all=1[sx{k}]")
    g.append("[voice]aformat=sample_rates=44100:channel_layouts=mono[vo0];[ha][vo0]concat=n=2:v=0:a=1[vo];[vo]" + "".join(f"[sx{k}]" for k in range(len(SFX))) +
             f"amix=inputs={1 + len(SFX)}:normalize=0:duration=first,alimiter=limit=0.89,"
             f"atrim=start={AAC_PRIMING:.4f},asetpts=PTS-STARTPTS,apad=pad_dur={AAC_PRIMING:.4f}[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs,
           "-filter_complex", ";\n".join(g), "-map", "[v]", "-map", "[a]",
           "-t", f"{HOOK_DUR + DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", "44100",
           "-movflags", "+faststart+negative_cts_offsets", "-use_editlist", "0", str(out_path)]
    subprocess.run(cmd, check=True)
    print("Wrote", Path(out_path).resolve())


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
