#!/usr/bin/env python3
"""Clean edit of raw/chrome_extension.mp4: colour grade, light denoise + sharpen, clean dissolves, loudness.

Nothing is cut: every frame of the demo stays. The only frames replaced are the ones inside each dissolve.
Single video encode (x264 CRF 18, capped at 7 Mbit/s: about 3x the 2.4 Mbit/s source, since the
phone-filmed screen noise otherwise balloons the file without adding real detail); audio is normalised to -14 LUFS for social.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "raw/chrome_extension.mp4"
OUT = ROOT / "output/AI_SEO_Chrome_Extension_clean.mp4"
WORK = ROOT / "work/chrome_ext"
W, H, FPS = 1080, 1920, 30

# Talking head <-> screen boundaries (s). The screen demo is filmed on a phone, so it gets its own grade.
SCREEN = (18.65, 85.65)
TALK = (
    "hqdn3d=1.5:1.5:4:4,"
    "colorbalance=rh=-0.03:bh=0.03:rm=-0.02:bm=0.01,"
    "eq=contrast=1.05:saturation=1.04,vibrance=intensity=0.12,"
    "cas=strength=0.35"
)
SCREEN_GRADE = (
    "hqdn3d=2:2:5:5,"
    # Whites measured at ~223/225/228 (slightly blue) and blacks ~10: stretch to clean white, neutral.
    "colorlevels=rimin=0.035:gimin=0.035:bimin=0.035:rimax=0.895:gimax=0.902:bimax=0.915,"
    "eq=contrast=1.04:saturation=1.10,"
    "cas=strength=0.6"
)

def graded_chain():
    s, e = SCREEN
    on = f"between(t,{s},{e})"
    off = f"not({on})"
    talk = ",".join(f"{f}:enable='{off}'" for f in TALK.split(","))
    scr = ",".join(f"{f}:enable='{on}'" for f in SCREEN_GRADE.split(","))
    return f"{talk},{scr}"

# Dissolves: (first frame, last frame, last clean outgoing frame, first clean incoming frame).
# The originals at 18.6s and 85.5s were glitchy luma-key blends; 33.6s was a hard cut.
DISSOLVES = [
    (553, 566, 557, 562),
    (1002, 1013, 1007, 1008),
    (2561, 2577, 2565, 2573),
]

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)

def graded_frames(frames):
    """Decode the whole clip through the grade (so the temporal denoiser has context) and keep `frames`."""
    sel = "+".join(f"eq(n\\,{n})" for n in frames)
    raw = run(["ffmpeg", "-v", "error", "-i", str(SRC), "-vf", f"{graded_chain()},select='{sel}'",
               "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb48le", "-"], capture_output=True).stdout
    arr = np.frombuffer(raw, np.uint16).reshape(-1, H, W, 3)
    assert len(arr) == len(frames), (len(arr), len(frames))
    return dict(zip(sorted(frames), arr))

BLUR = 22  # peak blur radius (px) at the middle of a dissolve

def blur(frame16, sigma):
    img = Image.fromarray((frame16 >> 8).astype(np.uint8))
    if sigma > 0.5:
        img = img.filter(ImageFilter.GaussianBlur(float(sigma)))
    return np.asarray(img, np.float32)

def build_patches():
    need = set()
    for a, b, lo, li in DISSOLVES:
        need |= {min(n, lo) for n in range(a, b + 1)} | {max(n, li) for n in range(a, b + 1)}
    fr = graded_frames(sorted(need))
    WORK.mkdir(parents=True, exist_ok=True)
    patches = []
    for i, (a, b, lo, li) in enumerate(DISSOLVES):
        path = WORK / f"dissolve_{i}.mkv"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "ffv1",
                                "-pix_fmt", "yuv444p16le", str(path)], stdin=subprocess.PIPE)
        span = b - a + 2
        for n in range(a, b + 1):
            t = (n - a + 1) / span
            k = t * t * (3 - 2 * t)  # smoothstep
            # Blur both shots towards the middle so the face and the bright screen never ghost through each other.
            sigma = BLUR * np.sin(np.pi * t)
            mix = blur(fr[min(n, lo)], sigma) * (1 - k) + blur(fr[max(n, li)], sigma) * k
            enc.stdin.write(np.clip(mix * 257, 0, 65535).astype(np.uint16).tobytes())
        enc.stdin.close(); enc.wait()
        patches.append((a, path))
    return patches

def loudnorm_params():
    out = run(["ffmpeg", "-hide_banner", "-i", str(SRC), "-af",
               "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
              capture_output=True, text=True).stderr
    m = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    return (f"highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
            f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")

def main():
    patches = build_patches()
    inputs = ["-i", str(SRC)]
    chain = f"[0:v]{graded_chain()}[v0]"
    for i, (start, path) in enumerate(patches, 1):
        inputs += ["-i", str(path)]
        chain += (f";[{i}:v]format=yuv444p,setpts=PTS-STARTPTS+{start}/{FPS}/TB[p{i}]"
                  f";[v{i-1}][p{i}]overlay=eof_action=pass:format=auto[v{i}]")
    chain += f";[v{len(patches)}]format=yuv420p[vout]"
    OUT.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", chain, "-map", "[vout]", "-map", "0:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "7M", "-bufsize", "14M", "-profile:v", "high", "-tune", "film",
         "-af", loudnorm_params(), "-ar", "48000", "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", str(OUT)])
    print("Wrote", OUT)

if __name__ == "__main__":
    main()
