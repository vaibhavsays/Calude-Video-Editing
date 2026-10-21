#!/usr/bin/env python3
"""Edit decision list for reel v6, built from the uploaded rough timeline (raw/v6_timeline.mp4).

Take selection (original clock, seconds):
  keep   0.00-10.95  hook ("business owners paying 40-50k... calls & leads zero")
  keep  11.03-14.60  "Welcome to 100 Days of Decoding AI SEO"
  keep  14.63-35.45  best take: agencies target traffic keywords, ToFu/MoFu/BoFu, question keywords -> traffic, no leads
  drop  35.45-44.50  retake of "agencies target traffic keywords"
  keep  44.50-53.41  "ask: is this traffic converting into leads / calls?"
  drop  53.73-90.93  third retake of the same point (+ garbled tracking aside)
  keep  90.93-101.05 "no qualified leads -> stop that marketing"
  drop 101.05-125.10 funnel explained again (duplicate of 14.63)
  drop 125.10-127.75 empty chair
  drop 127.75-142.30 question-based queries point (already covered)
  keep 142.30-200.90 funnel self-check, phone-buying example (top/middle/bottom), CTA

Inside kept takes every pause longer than 0.30 s is shortened to ~0.15 s.

    python3 tools/edl.py   -> edl.json + edl.js
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAKES = [(0.0, 10.95), (11.03, 14.60), (14.63, 35.45), (44.50, 53.41), (90.93, 101.05), (142.30, 200.90)]
LEAD, TAIL = 0.08, 0.07

sil = [tuple(map(float, l.split())) for l in open(HERE / "silences.txt") if l.strip()]
keep = []
for a, b in TAKES:
    t = a
    for s, e in sil:
        if e - s > 0.30 and s > a and e < b:
            if s + LEAD > t: keep.append([round(t, 3), round(s + LEAD, 3)])
            t = e - TAIL
    if b > t: keep.append([round(t, 3), round(b, 3)])
dur = round(sum(b - a for a, b in keep), 3)
(HERE.parent / "edl.json").write_text(json.dumps({"keep": keep, "duration": dur}, indent=1))
(HERE.parent / "edl.js").write_text("window.KEEP = " + json.dumps(keep) + ";\nwindow.EDL_DURATION = " + str(dur) + ";\n")
print(len(keep), "segments, duration", dur)
