#!/usr/bin/env python3
"""Final composite for the Nov 16 reel (Day 13: SEO is not dead, with Google Search Console proof).

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
SRC = HERE / "../../raw/nov16.mp4"
OUT = HERE / "../../output/Day13_SEO_Not_Dead.mp4"
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
    (0.0, (0.985, 0.985, 1.020), 0.0, .31, .46),          # talking, near-neutral wall (R/B 1.05)
    (600 / 30, (1.0, 1.0, 1.0), 0.0, .5, .5),             # GSC screen recording: untouched (see PROTECT)
    (1839 / 30, (0.840, 0.970, 1.220), 0.3, .32, .46),    # warm lamp take: wall R/B 2.03, G/B 1.44 -> left slightly warm
    (2876 / 30, (0.965, 0.985, 1.045), 0.3, .40, .50),    # square close take: R/B 1.12, G/B 1.08
]
# The user asked for NO edits while the GSC results screen is shown: these original frames are laid on top of
# everything (grade, zoom, overlay, captions) for exactly this window, so it plays as recorded.
PROTECT = (600 / 30, 1839 / 30)
SQUARE = 2876 / 30
AUDIO_LATENCY = 0.038
AAC_PRIMING = 1024 / 44100
SPLIT = [(61.30, 95.867, 200)]        # panel on top, speaker below (head ~860 px)

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
SPANS = [(0.25, 4.8, 1.00, 1.05), (4.8, 8.97, 1.05, 1.0), (9.07, 13.8, 1.0, 1.06), (13.8, 20.0, 1.06, 1.0),
         (20.0, 61.3, 1.0, 1.0), (61.3, 69.4, 1.0, 1.06), (69.4, 73.52, 1.06, 1.0), (73.64, 81.0, 1.0, 1.06),
         (81.0, 88.5, 1.06, 1.0), (88.5, 95.867, 1.0, 1.06), (95.867, 106.3, 1.0, 1.0)]
CAM = []
for a, b, z0, z1 in SPANS:
    cy, cx = TAKES[take_of(a)][3], TAKES[take_of(a)][4]
    CAM += [(a + 0.001, z0, cx, cy), (b - 0.001, z1, cx, cy)]
CUTS = sorted(set([a for a, _ in KEEP[1:] if not (PROTECT[0] - 0.01 <= a <= PROTECT[1])]))


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
SFX = [("whoosh", 0.3, .16), ("thud", 0.6, .2), ("pop", 4.9, .14), ("pop", 5.6, .14), ("pop", 7.2, .14),
       ("whoosh", 9.2, .18), ("pop", 11.7, .14), ("swoosh", 14.2, .16), ("whoosh", 19.0, .16),
       ("whoosh", 61.6, .18), ("pop", 64.0, .14), ("pop", 66.5, .14), ("swoosh", 69.5, .16), ("ding", 72.4, .12),
       ("whoosh", 77.5, .18), ("pop", 81.2, .14), ("ding", 84.0, .12), ("whip", 91.0, .2), ("ding", 93.2, .12),
       ("thud", 96.0, .22), ("pop", 99.2, .14), ("whoosh", 103.4, .16)]


def main(out_path):
    n = len(PIECES)
    z, x, y = cam_expr()
    g = [f"[0:v]split={n + 1}" + "".join(f"[vs{i}]" for i in range(n)) + "[vraw]"]
    for i, (a, b) in enumerate(PIECES):
        rr, gg, bb = TAKES[take_of(a)][1]
        look = "null" if PROTECT[0] - 1e-3 <= a < PROTECT[1] else f"{PRE},colorchannelmixer=rr={rr}:gg={gg}:bb={bb},{TAIL}"
        g.append(f"[vs{i}]trim={a:.4f}:{b:.4f},setpts=PTS-STARTPTS,{look}[vc{i}]")
    g.append("".join(f"[vc{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,fps=30,split={2 + len(SPLIT)}[u0][uq]" +
             "".join(f"[u{k + 1}]" for k in range(len(SPLIT))))
    g.append(f"[u0]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1080x1920:fps=30[f0]")
    for k, (a, b, top) in enumerate(SPLIT):
        g.append(f"[u{k + 1}]crop=1080:1160:0:{top},scale=2160:2320:flags=lanczos,"
                 f"zoompan=z='{z}':x='clip(iw*0.46-iw/zoom/2,0,iw-iw/zoom)':y='(ih-ih/zoom)*0.30':d=1:s=1080x1160:fps=30[h{k}]")
        g.append(f"[f{k}][h{k}]overlay=0:760:enable='between(t,{T(a):.3f},{T(b) - 0.001:.3f})'[f{k + 1}]")
    # square take: sharp square over a blurred, dimmed fill of itself (no upscaling), slow push-in on the square
    q0, q1 = T(SQUARE), DUR
    sq = f"clip((it-{q0:.3f})/{q1 - q0:.3f},0,1)"
    g.append("[uq]crop=1064:1064:8:428,split[qa][qb]")
    g.append("[qa]scale=1920:1920,crop=1080:1920,gblur=sigma=38,eq=brightness=-0.10:saturation=0.85[qbg]")
    g.append(f"[qb]scale=2160:2160:flags=lanczos,zoompan=z='1+0.06*{sq}*{sq}*(3-2*{sq})':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.4':d=1:s=1080x1080:fps=30[qfg]")
    g.append("[qbg][qfg]overlay=0:420[qq]")
    g.append(f"[f{len(SPLIT)}][qq]overlay=0:0:enable='gte(t,{q0 - 0.001:.3f})'[fq]")
    g.append("[fq][1:v]overlay=0:0:format=auto:eof_action=pass[vo]")
    # protected GSC window: the original frames, untouched, on top of everything
    p0, p1 = T(PROTECT[0]), T(PROTECT[1])
    g.append(f"[vraw]trim={PROTECT[0]:.4f}:{PROTECT[1]:.4f},setpts=PTS-STARTPTS+{p0:.4f}/TB,format=yuv420p[gsc]")
    g.append(f"[vo][gsc]overlay=0:0:eof_action=pass:enable='between(t,{p0:.4f},{p1 - 0.001:.4f})'[v]")

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
           "-t", f"{DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", "44100",
           "-movflags", "+faststart+negative_cts_offsets", "-use_editlist", "0", str(out_path)]
    subprocess.run(cmd, check=True)
    print("Wrote", Path(out_path).resolve())


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
