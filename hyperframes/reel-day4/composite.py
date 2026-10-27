#!/usr/bin/env python3
"""Final composite for reel v6 ("Traffic but zero leads? Keyword funnel") built from the rough timeline upload.

  1. Keep only the best takes and cut long pauses (edl.json, see tools/edl.py for the take-by-take decisions),
     with 10 ms audio fades at every join so nothing clicks.
  2. Clean + upscale the 576x1024 WhatsApp source to 1080x1920 (deblock, light denoise, Lanczos, sharpen, gentle grade).
  3. Full-frame shots: every join gets an eased zoom punch; zoom levels alternate so jump cuts read as deliberate.
  4. Split windows: the speaker sits in the bottom half (the overlay fills the top half with B-roll).
  5. HyperFrames overlay (renders/overlay.mov: hook, B-roll, captions) on top, SFX mixed under the voice, one CRF 17 encode (keeps the file under GitHub's 100 MB).

    python3 composite.py [out.mp4]
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "../../raw/v6_timeline.mp4"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "../../output/Traffic_No_Leads_Funnel.mp4"
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
SPLIT = [(2.98, 10.95), (14.63, 37.78), (142.3, 191.99), (192.1, 202.0)]
BROLL = [(90.93, 99.72)]

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
       ("whoosh", 2.55, .28), ("pop", 3.1, .22), ("thud", 8.6, .38), ("thud", 9.1, .38), ("swoosh", 10.75, .2),
       ("pop", 11.15, .2),
       ("whoosh", 14.2, .28), ("pop", 14.75, .18), ("pop", 17.6, .2), ("pop", 18.0, .14), ("pop", 18.3, .14), ("pop", 18.6, .16),
       ("swoosh", 20.5, .2), ("pop", 21.0, .2), ("pop", 21.5, .2), ("pop", 22.0, .2), ("thud", 24.45, .3), ("pop", 24.6, .2),
       ("pop", 28.96, .2), ("pop", 29.6, .2), ("pop", 30.2, .2), ("pop", 32.4, .24), ("thud", 34.1, .36), ("pop", 36.9, .18), ("swoosh", 37.5, .2),
       ("pop", 44.85, .22), ("pop", 51.0, .2),
       ("whip", 90.65, .3), ("pop", 91.4, .22), ("thud", 92.7, .32), ("thud", 95.0, .32), ("thud", 98.35, .45), ("swoosh", 99.45, .2),
       ("whoosh", 141.85, .28), ("pop", 142.6, .2), ("pop", 145.0, .18), ("pop", 147.9, .18), ("pop", 148.9, .18),
       ("swoosh", 150.8, .22), ("pop", 155.4, .2), ("pop", 158.3, .2), ("pop", 165.4, .18), ("swoosh", 168.8, .18),
       ("pop", 169.1, .18), ("pop", 170.8, .22), ("pop", 173.2, .22), ("pop", 177.0, .22), ("pop", 180.85, .18),
       ("pop", 182.0, .22), ("pop", 183.6, .22), ("ding", 186.0, .22), ("swoosh", 191.75, .2),
       ("whoosh", 191.85, .26), ("pop", 192.4, .18), ("swoosh", 194.4, .2), ("ding", 197.95, .26)]

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
    g.append(f"[u1]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*0.22':d=1:s=1080x1920:fps=30[full]")
    g.append("[u2]crop=1080:1160:0:40[half]")
    g.append(f"[full][half]overlay=0:760:enable='{split_en}'[v1]")
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
           "-t", f"{DUR:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-tune", "film", "-r", "30", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(OUT)]
    subprocess.run(cmd, check=True)
    print("Wrote", OUT.resolve())

if __name__ == "__main__":
    main()
