#!/usr/bin/env python3
"""Edit decision list for the Nov 6 reel (Day 6: SEO vs GEO), from raw/nov6.mp4 (53.5 s; four takes,
cut at 11.43, 15.67 and 49.03 s; the raw file lives in the RAWVIDEONOVEMBER6 GitHub release, over 100 MB).

No retakes to drop. Inside the timeline, pauses longer than 0.38 s are shortened, keeping 0.20 s after a word
ends and 0.12 s before the next one starts (silence map at -36 dB, d 0.12 s), so the hard cuts flow straight on.

    python3 tools/edl.py   -> edl.json + edl.js
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAKES = [(0.08, 53.2)]
LEAD, TAIL, MIN_PAUSE = 0.20, 0.12, 0.30

sil = [tuple(map(float, l.split())) for l in open(HERE / "silences.txt") if l.strip()]
keep = []
for a, b in TAKES:
    t = a
    for s, e in sil:
        if e - s > MIN_PAUSE and s > a and e < b:
            if s + LEAD > t: keep.append([round(t, 3), round(s + LEAD, 3)])
            t = e - TAIL
    if b > t: keep.append([round(t, 3), round(b, 3)])
# merge joins that remove almost nothing (a cut there would only add a jump)
m = []
for a, b in keep:
    if m and a - m[-1][1] < 0.1: m[-1][1] = max(m[-1][1], b)
    else: m.append([a, b])
keep = m
dur = round(sum(b - a for a, b in keep), 3)
(HERE.parent / "edl.json").write_text(json.dumps({"keep": keep, "duration": dur}, indent=1))
(HERE.parent / "edl.js").write_text("window.KEEP = " + json.dumps(keep) + ";\nwindow.EDL_DURATION = " + str(dur) + ";\n")
print(len(keep), "segments, duration", dur)
