#!/usr/bin/env python3
"""Clean edit of raw/chrome_extension.mp4: colour grade, light denoise + sharpen, clean dissolves, loudness.

Every frame of the demo stays. Only two cuts: the breath before the closing line, and the look-down after it.
The only other frames replaced are the ones inside each dissolve.
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

# Source frame ranges to keep (inclusive). Frames 2562-2588 (85.40-86.30s) are the silence and the breath
# before "Okay so tell me..."; the cut-out sits in digital silence and the cut-in on the first syllable.
# The video ends on frame 2704 (90.13s, the last word), before the look down to stop recording.
KEEP = [(0, 2561), (2589, 2704)]
OUT_FRAMES = [n for a, b in KEEP for n in range(a, b + 1)]

# Dissolves in output frames: (first, last, last clean outgoing source frame, first clean incoming source frame).
# The originals at 18.6s and 85.5s were glitchy luma-key blends; 33.6s was a hard cut.
DISSOLVES = [
    (553, 566, 557, 562),
    (1002, 1013, 1007, 1008),
    (2557, 2567, 2561, 2589),
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
        src = [OUT_FRAMES[o] for o in range(a, b + 1)]
        need |= {min(n, lo) for n in src} | {max(n, li) for n in src}
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
            sn = OUT_FRAMES[n]
            mix = blur(fr[min(sn, lo)], sigma) * (1 - k) + blur(fr[max(sn, li)], sigma) * k
            enc.stdin.write(np.clip(mix * 257, 0, 65535).astype(np.uint16).tobytes())
        enc.stdin.close(); enc.wait()
        patches.append((a, path))
    return patches

def edited_audio():
    """Cut the audio at the same frame boundaries; a short fade-in on each later piece avoids clicks."""
    wav = WORK / "audio_edit.wav"
    parts, labels = [], []
    for i, (a, b) in enumerate(KEEP):
        f = f"[0:a]atrim={a / FPS}:{(b + 1) / FPS},asetpts=PTS-STARTPTS"
        if i:
            f += ",afade=t=in:d=0.015"
        if i == len(KEEP) - 1:
            f += f",afade=t=out:st={(b - a + 1) / FPS - 0.04}:d=0.04"
        parts.append(f + f"[a{i}]"); labels.append(f"[a{i}]")
    graph = ";".join(parts) + f";{''.join(labels)}concat=n={len(KEEP)}:v=0:a=1[a]"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-filter_complex", graph, "-map", "[a]",
         "-c:a", "pcm_s24le", str(wav)])
    return wav

def loudnorm_params(wav):
    out = run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af",
               "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
              capture_output=True, text=True).stderr
    m = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    return (f"highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
            f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")

def main():
    patches = build_patches()
    wav = edited_audio()
    keep = "+".join(f"between(n\\,{a}\\,{b})" for a, b in KEEP)
    inputs = ["-i", str(SRC), "-i", str(wav)]
    chain = f"[0:v]{graded_chain()},select='{keep}',setpts=N/{FPS}/TB[v0]"
    for i, (start, path) in enumerate(patches, 1):
        inputs += ["-i", str(path)]
        chain += (f";[{i + 1}:v]format=yuv444p,setpts=PTS-STARTPTS+{start}/{FPS}/TB[p{i}]"
                  f";[v{i-1}][p{i}]overlay=eof_action=pass:format=auto[v{i}]")
    chain += f";[v{len(patches)}]format=yuv420p[vout]"
    OUT.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", chain, "-map", "[vout]", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "7M", "-bufsize", "14M", "-profile:v", "high", "-tune", "film",
         "-af", loudnorm_params(wav), "-ar", "48000", "-c:a", "aac", "-b:a", "256k",
         "-movflags", "+faststart", str(OUT)])
    print("Wrote", OUT)

if __name__ == "__main__":
    main()
