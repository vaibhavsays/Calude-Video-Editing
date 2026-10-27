#!/usr/bin/env python3
"""Edit decision list for the Day 4 reel ("Why ChatGPT ignores your business"), from the uploaded timeline
(raw/day4.mp4, 111.0 s, already assembled by the user from several takes).

Clips in the upload (hard cuts, original clock):
   0.00- 5.92  seated: hook "ChatGPT aur other AI search engines aapke business ko recommend kyun nahi kar rahe?"
   5.92- 9.21  seated: "Welcome to Day 4 of 100 Days of Decoding AI SEO"
   9.21-14.05  standing with mic: "3 reasons... third one is really important"
  14.05-61.44  reason 1 (robots.txt / AI crawlers) and reason 2 (third-party validation), jump cuts at 25.5 and 35.7
  61.44-105.77 reason 3 (machine readability / schema), jump cuts at 85.0 and 96.0
 105.77-111.01 CTA "comment SCHEMA"

No retakes to drop. Inside the timeline, pauses longer than 0.38 s are shortened, keeping 0.20 s after a word
ends and 0.12 s before the next one starts (silence map at -40 dB, d 0.12 s), so the hard cuts flow straight on.

    python3 tools/edl.py   -> edl.json + edl.js
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAKES = [(0.0, 111.0)]
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
