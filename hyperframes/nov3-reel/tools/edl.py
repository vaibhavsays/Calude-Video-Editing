#!/usr/bin/env python3
"""Edit decision list for the Nov 3 reel ("Backlink hierarchy: tier 1 / 2 / 3"), from raw/nov3.mp4
(40.8 s, 25 Mbps, one seated take with the user's own cuts at 2.57, 8.40 and 36.37 s; the raw file lives in the
NOVEMBER3 GitHub release because it is over 100 MB).

No retakes to drop. Inside the timeline, pauses longer than 0.38 s are shortened, keeping 0.20 s after a word
ends and 0.12 s before the next one starts (silence map at -36 dB, d 0.12 s), so the hard cuts flow straight on.

    python3 tools/edl.py   -> edl.json + edl.js
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAKES = [(0.0, 40.35)]  # stop before the dead air after the last word
LEAD, TAIL, MIN_PAUSE = 0.20, 0.12, 0.38

sil = [tuple(map(float, l.split())) for l in open(HERE / "silences.txt") if l.strip()]
keep = []
for a, b in TAKES:
    t = a
    for s, e in sil:
        if e - s > MIN_PAUSE and s > a and e < b:
            if s + LEAD > t: keep.append([round(t, 3), round(s + LEAD, 3)])
            t = e - TAIL
    if b > t: keep.append([round(t, 3), round(b, 3)])
dur = round(sum(b - a for a, b in keep), 3)
(HERE.parent / "edl.json").write_text(json.dumps({"keep": keep, "duration": dur}, indent=1))
(HERE.parent / "edl.js").write_text("window.KEEP = " + json.dumps(keep) + ";\nwindow.EDL_DURATION = " + str(dur) + ";\n")
print(len(keep), "segments, duration", dur)
