#!/usr/bin/env python3
"""Final composite for the Day 4 reel ("Why ChatGPT ignores your business").

  1. Tighten the user's timeline (edl.json, see tools/edl.py), 10 ms audio fades at every join so nothing clicks.
  2. Voice: each source clip is gained to the same loudness (some takes were recorded ~8 dB quieter), then light
     denoise, high-pass, a little presence, gentle compression and a limiter.
  3. Picture: 60 -> 30 fps, deblock + denoise for the 1.7 Mbps upload, mild sharpen, colour boost (contrast,
     saturation, vibrance) and a soft S-curve.
  4. Full-frame shots: an eased zoom punch at every hard cut of the original timeline, zoom levels alternate per
     clip so each cut reads as deliberate. Split windows: the speaker sits below the B-roll panel (head below 790 px).
  5. Text behind the speaker for the hook and "Day 4" intro: renders/behind.mov goes over the picture, then the
     speaker cut out with per-frame BiRefNet mattes (renders/masks) goes back on top of it.
  6. HyperFrames front overlay (renders/overlay.mov: B-roll, chips, captions) on top, SFX under the voice, one CRF 17 encode (keeps the file under GitHub's 100 MB).

    python3 composite.py base     -> renders/base_frames/*.png (picture for the matte window, for tools/matte.py)
    python3 composite.py [out.mp4]
"""
import json, math, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "../../raw/day4.mp4"
OUT = HERE / "../../output/AI_SEO_Day4_ChatGPT_Ignores.mp4"
edl = json.loads((HERE / "edl.json").read_text())
KEEP, DUR = edl["keep"], edl["duration"]

def T(x):
    acc = 0.0
    for a, b in KEEP:
        if x < a: return acc
        if x <= b: return acc + x - a
        acc += b - a
    return acc

# Hard cuts in the uploaded timeline and per-clip voice gain (dB, measured through the voice chain) so every clip
# lands at the same loudness
CLIPS = [(0.0, 0.0), (5.92, 2.8), (9.21, 2.0), (14.05, 6.8), (25.53, 6.4), (35.69, 8.5), (61.44, 6.0),
         (84.97, 4.7), (95.93, 4.5), (105.77, 5.1)]
# Split windows (original clock) with the source crop top for the speaker, same windows as MODES in index.html
SPLIT = [(9.21, 14.05, 680), (14.05, 29.0, 440), (35.69, 52.9, 440), (64.3, 83.3, 440), (105.77, 111.0, 440)]
# Text-behind-speaker window (original clock): hook + "Day 4" intro
MATTE_END = 9.21
MATTE_FRAMES = math.ceil(T(MATTE_END) * 30)

GRADE = ("deblock=filter=weak:block=8,hqdn3d=2.5:2:4:4,unsharp=5:5:0.5:5:5:0,"
         "eq=contrast=1.06:saturation=1.06,vibrance=intensity=0.12,colorbalance=rs=-0.02:bs=0.02:rm=-0.01:bm=0.01,"
         "curves=master='0/0.015 0.25/0.235 0.5/0.5 0.75/0.775 1/0.985'")

# zoom: one level per original clip (alternating) + an eased kick that settles ~0.3 s after each hard cut
cuts = [T(c) for c, _ in CLIPS]
z = "1"
for i in reversed(range(len(cuts))):
    t0, lvl = cuts[i], (1.0 if i % 2 == 0 else 1.08)
    kick = 0.12 if i == 0 else 0.08
    z = f"if(gte(it,{t0:.3f}),{lvl}+{kick}*exp(-(it-{t0:.3f})/0.14),{z})"

gain = "1"
for c, db in CLIPS:  # last cut outermost, so the latest matching clip wins
    gain = f"if(gte(t,{c}),{10 ** (db / 20):.4f},{gain})"

# SFX on the original clock: name, time, gain
SFX = [("whoosh", 0.0, .24), ("thud", 0.25, .32), ("pop", 2.4, .2), ("whip", 5.75, .3), ("thud", 6.3, .34), ("pop", 7.7, .2),
       ("whoosh", 9.0, .28), ("pop", 9.9, .2), ("pop", 10.6, .2), ("pop", 11.3, .2), ("ding", 12.8, .22),
       ("whoosh", 13.85, .26), ("pop", 14.4, .2), ("pop", 17.0, .18), ("thud", 20.9, .34), ("pop", 22.2, .18),
       ("pop", 26.5, .18), ("swoosh", 28.75, .22), ("pop", 29.5, .2), ("ding", 33.3, .2),
       ("whip", 35.45, .3), ("pop", 36.1, .2), ("pop", 38.2, .18), ("pop", 44.5, .2), ("pop", 47.4, .2), ("pop", 48.2, .2),
       ("pop", 48.9, .2), ("pop", 50.3, .2), ("whoosh", 52.65, .28), ("pop", 53.3, .2), ("pop", 55.0, .2), ("ding", 58.6, .22),
       ("whip", 61.3, .3), ("thud", 62.6, .34), ("swoosh", 64.05, .22), ("pop", 65.0, .18), ("pop", 70.3, .2), ("pop", 72.6, .2),
       ("pop", 75.4, .18), ("pop", 78.2, .2), ("pop", 79.3, .2), ("pop", 81.0, .2), ("pop", 81.9, .2), ("pop", 82.6, .2),
       ("swoosh", 83.05, .22), ("whoosh", 89.05, .28), ("pop", 89.9, .2), ("pop", 91.8, .2), ("pop", 92.6, .2), ("pop", 94.2, .2),
       ("ding", 95.9, .22), ("swoosh", 97.3, .22), ("thud", 98.3, .36), ("swoosh", 100.4, .2), ("pop", 101.2, .2),
       ("whoosh", 105.5, .28), ("pop", 106.1, .2), ("ding", 107.0, .26)]


def picture(g):
    """Cut, grade, zoom and split; leaves the speaker picture in [v1]."""
    n = len(KEEP)
    g.append(f"[0:v]split={n}" + "".join(f"[vs{i}]" for i in range(n)))
    for i, (a, b) in enumerate(KEEP):
        g.append(f"[vs{i}]trim={a}:{b},setpts=PTS-STARTPTS[vc{i}]")
    g.append("".join(f"[vc{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,fps=30,{GRADE},split={1 + len(SPLIT)}[u0]" +
             "".join(f"[u{k + 1}]" for k in range(len(SPLIT))))
    g.append(f"[u0]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.30':d=1:s=1080x1920:fps=30[f0]")
    for k, (a, b, top) in enumerate(SPLIT):
        g.append(f"[u{k + 1}]crop=1080:1160:0:{top}[h{k}]")
        g.append(f"[f{k}][h{k}]overlay=0:760:enable='between(t,{T(a):.3f},{T(b) - 0.001:.3f})'[f{k + 1}]")
    g.append(f"[f{len(SPLIT)}]null[v1]")


def base():
    out = HERE / "renders/base_frames"
    out.mkdir(parents=True, exist_ok=True)
    g = []
    picture(g)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(SRC), "-filter_complex", ";\n".join(g), "-map", "[v1]",
                    "-frames:v", str(MATTE_FRAMES), str(out / "f_%05d.png")], check=True)
    print("Wrote", MATTE_FRAMES, "frames to", out)


def main(out_path):
    n = len(KEEP)
    inputs = ["-i", str(SRC), "-i", str(HERE / "renders/overlay.mov"), "-i", str(HERE / "renders/behind.mov"),
              "-framerate", "30", "-i", str(HERE / "renders/masks/m_%05d.png")]
    g = []
    picture(g)
    me = MATTE_FRAMES / 30
    g.append("[v1]split[v1a][pb]")
    g.append("[v1a][2:v]overlay=0:0:format=auto:eof_action=pass[v2]")
    g.append(f"[3:v]format=gray,gblur=sigma=1.2[mk]")
    g.append(f"[pb]trim=end={me:.4f},setpts=PTS-STARTPTS,format=yuva420p[pb2]")
    g.append("[pb2][mk]alphamerge[person]")
    g.append(f"[v2][person]overlay=0:0:format=auto:eof_action=pass:enable='lt(t,{me:.4f})'[v3]")
    g.append("[v3][1:v]overlay=0:0:format=auto:eof_action=pass[v]")

    g.append(f"[0:a]volume='{gain}':eval=frame,asplit={n}" + "".join(f"[as{i}]" for i in range(n)))
    for i, (a, b) in enumerate(KEEP):
        d = b - a
        g.append(f"[as{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[ac{i}]")
    g.append("".join(f"[ac{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,afftdn=nr=8:nf=-45,highpass=f=75,"
             "equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=220:t=q:w=1:g=-1.5,"
             "acompressor=threshold=0.09:ratio=2.5:attack=8:release=160:makeup=1.6,volume=4dB[voice]")
    mix = ["[voice]"]
    for k, (name, t, gn) in enumerate(SFX):
        idx = 4 + k
        inputs += ["-i", str(HERE / f"assets/sfx/{name}.wav")]
        ms = int(max(0.0, T(t)) * 1000)
        g.append(f"[{idx}:a]aresample=48000,adelay={ms}|{ms},volume={gn * 0.75:.3f}[s{k}]")
        mix.append(f"[s{k}]")
    g.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.85[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";\n".join(g), "-map", "[v]", "-map", "[a]",
           "-t", f"{DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(out_path)]
    subprocess.run(cmd, check=True)
    print("Wrote", Path(out_path).resolve())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "base":
        base()
    else:
        main(Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
