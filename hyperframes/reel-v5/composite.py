#!/usr/bin/env python3
"""Final composite for the "AI content punished?" reel (tight cut).

  1. Cut the long pauses and "um" fillers out of the original (edl.json, see tools/edl.py), with 10 ms audio fades at
     every join so nothing clicks.
  2. Clean + upscale the 576x1024 WhatsApp source to 1080x1920 (deblock, light denoise, Lanczos, sharpen, gentle grade).
  3. Full-frame shots: every join gets an eased zoom punch; zoom levels alternate so jump cuts read as deliberate.
  4. Split windows: the speaker sits in the bottom half (the overlay fills the top half with B-roll).
  5. HyperFrames overlay (renders/overlay.mov: hook, B-roll, captions) on top, SFX mixed under the voice, one CRF 14 encode.

    python3 composite.py [out.mp4]
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "../../raw/geo_video.mp4"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "../../output/AI_Content_Punished.mp4"
edl = json.loads((HERE / "edl.json").read_text())
KEEP, DUR = edl["keep"], edl["duration"]

def T(x):
    acc = 0.0
    for a, b in KEEP:
        if x < a: return acc
        if x <= b: return acc + x - a
        acc += b - a
    return acc

# Same windows as MODES in index.html (original clock)
SPLIT = [(5.5, 15.75), (31.1, 50.3), (61.38, 78.4), (83.3, 94.533)]
BROLL = [(15.8, 24.05), (50.4, 61.35)]

UP = ("deblock=filter=strong:block=8,hqdn3d=1.5:1.5:4:4,scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,"
      "unsharp=5:5:0.7:5:5:0,eq=contrast=1.05:saturation=1.08,"
      "curves=master='0/0.01 0.25/0.235 0.5/0.505 0.75/0.775 1/0.99'")

# zoom: one level per kept segment (alternating), plus an eased kick that settles ~0.3 s after each join
joins, acc = [], 0.0
for a, b in KEEP:
    joins.append(acc); acc += b - a
levels = [1.0 if i % 2 == 0 else 1.1 for i in range(len(joins))]
z = "1"
for i in reversed(range(len(joins))):
    t0 = joins[i]
    kick = 0.12 if i == 0 else 0.07
    z = f"if(gte(it,{t0:.3f}),{levels[i]}+{kick}*exp(-(it-{t0:.3f})/0.13),{z})"
split_en = "+".join(f"between(t,{T(a):.3f},{T(b):.3f})" for a, b in SPLIT)

# SFX on the original clock: name, time, gain
SFX = [("whoosh", 0.0, .22), ("whip", 0.0, .28),
       ("whoosh", 5.05, .28), ("pop", 5.6, .2), ("pop", 7.1, .2), ("thud", 10.15, .42), ("swoosh", 11.2, .2),
       ("pop", 11.8, .24), ("pop", 12.8, .24), ("pop", 14.3, .24), ("pop", 14.8, .18),
       ("whip", 15.52, .3), ("pop", 15.9, .18), ("swoosh", 16.4, .2), ("pop", 17.7, .2), ("pop", 19.4, .14),
       ("pop", 21.4, .26), ("pop", 22.0, .22), ("thud", 22.4, .3), ("thud", 23.35, .42), ("swoosh", 23.8, .22),
       ("pop", 25.6, .22), ("thud", 28.25, .32), ("thud", 29.35, .32),
       ("whoosh", 30.65, .28), ("pop", 32.2, .24), ("pop", 32.7, .24), ("pop", 33.2, .24), ("pop", 33.7, .24),
       ("swoosh", 34.15, .22), ("pop", 35.3, .22), ("pop", 40.5, .22), ("swoosh", 43.6, .18), ("swoosh", 44.1, .2),
       ("pop", 45.9, .24), ("pop", 47.3, .24), ("pop", 48.7, .24), ("swoosh", 50.05, .22),
       ("whip", 50.12, .3), ("pop", 51.1, .18), ("pop", 52.2, .22), ("pop", 55.0, .22), ("swoosh", 57.4, .18), ("pop", 57.7, .24), ("pop", 58.6, .24),
       ("swoosh", 58.7, .18), ("thud", 60.5, .32), ("thud", 60.8, .32),
       ("whoosh", 60.95, .28), ("pop", 61.5, .18), ("pop", 63.6, .2), ("pop", 63.9, .2), ("pop", 64.2, .2), ("swoosh", 66.25, .2), ("pop", 67.2, .24), ("pop", 67.9, .24), ("pop", 70.2, .24),
       ("pop", 72.2, .24), ("pop", 74.6, .24), ("pop", 76.4, .24), ("swoosh", 78.1, .22),
       ("pop", 79.6, .22), ("thud", 82.1, .32),
       ("whoosh", 82.85, .28), ("pop", 83.4, .18), ("swoosh", 85.0, .22),
       ("pop", 87.4, .18), ("pop", 87.8, .18), ("pop", 88.3, .18), ("pop", 88.7, .18), ("ding", 90.85, .26)]

def main():
    n = len(KEEP)
    inputs = ["-i", str(SRC), "-i", str(HERE / "renders/overlay.mov")]
    g = [f"[0:v]split={n}" + "".join(f"[vs{i}]" for i in range(n)),
         f"[0:a]asplit={n}" + "".join(f"[as{i}]" for i in range(n))]
    for i, (a, b) in enumerate(KEEP):
        d = b - a
        g.append(f"[vs{i}]trim={a}:{b},setpts=PTS-STARTPTS[vc{i}]")
        g.append(f"[as{i}]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, d - 0.012):.3f}:d=0.012[ac{i}]")
    g.append("".join(f"[vc{i}][ac{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vcat][acat]")
    g.append(f"[vcat]{UP},split[u1][u2]")
    g.append(f"[u1]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.36':d=1:s=1080x1920:fps=30[full]")
    g.append("[u2]crop=1080:960:0:560[half]")
    g.append(f"[full][half]overlay=0:960:enable='{split_en}'[v1]")
    g.append("[v1][1:v]overlay=0:0:format=auto:eof_action=pass[v]")
    mix = ["[acat]"]
    for k, (name, t, gain) in enumerate(SFX):
        idx = 2 + k
        inputs += ["-i", str(HERE / f"assets/sfx/{name}.wav")]
        ms = int(max(0.0, T(t)) * 1000)
        g.append(f"[{idx}:a]aresample=48000,adelay={ms}|{ms},volume={gain * 0.75:.3f}[s{k}]")
        mix.append(f"[s{k}]")
    g.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.95[a]")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";\n".join(g), "-map", "[v]", "-map", "[a]",
           "-t", f"{DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(OUT)]
    subprocess.run(cmd, check=True)
    print("Wrote", OUT.resolve())

if __name__ == "__main__":
    main()
