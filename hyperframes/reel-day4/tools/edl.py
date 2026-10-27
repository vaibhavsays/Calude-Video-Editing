#!/usr/bin/env python3
"""Edit decision list for reel v6, built from the uploaded rough timeline (raw/v6_timeline.mp4).

Take selection (original clock, seconds):
  keep   0.00-10.95  hook ("business owners paying 40-50k... calls & leads zero")
  keep  11.03-14.60  "Welcome to 100 Days of Decoding AI SEO"
  keep  14.63-37.78  best take: agencies target traffic keywords, ToFu/MoFu/BoFu, question keywords -> traffic, no leads
  drop  37.78-44.50  retake of "agencies target traffic keywords"
  keep  44.50-53.41  "ask: is this traffic converting into leads / calls?"
  drop  53.73-90.93  third retake of the same point (+ garbled tracking aside)
  keep  90.93-99.72  "no qualified leads -> stop that marketing" (ends on "chahiye")
  drop  99.72-125.10 funnel explained again (duplicate of 14.63)
  drop 125.10-127.75 empty chair
  drop 127.75-142.30 question-based queries point (already covered)
  keep 142.30-201.93 funnel self-check, phone-buying example (top/middle/bottom), CTA

Inside kept takes only pauses longer than 0.50 s are shortened, keeping 0.22 s after a word ends and 0.15 s
before the next one starts (silence map at -38 dB, so soft word endings are never treated as silence).

    python3 tools/edl.py   -> edl.json + edl.js
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAKES = [(0.0, 10.95), (11.03, 14.60), (14.63, 37.78), (44.50, 53.60), (90.93, 99.72), (142.30, 201.93)]
LEAD, TAIL = 0.22, 0.15

sil = [tuple(map(float, l.split())) for l in open(HERE / "silences.txt") if l.strip()]
keep = []
for a, b in TAKES:
    t = a
    for s, e in sil:
        if e - s > 0.50 and s > a and e < b:
            if s + LEAD > t: keep.append([round(t, 3), round(s + LEAD, 3)])
            t = e - TAIL
    if b > t: keep.append([round(t, 3), round(b, 3)])
dur = round(sum(b - a for a, b in keep), 3)
(HERE.parent / "edl.json").write_text(json.dumps({"keep": keep, "duration": dur}, indent=1))
(HERE.parent / "edl.js").write_text("window.KEEP = " + json.dumps(keep) + ";\nwindow.EDL_DURATION = " + str(dur) + ";\n")
print(len(keep), "segments, duration", dur)
