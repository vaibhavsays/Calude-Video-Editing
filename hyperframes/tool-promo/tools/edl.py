#!/usr/bin/env python3
"""Edit decision list for the free AI-visibility audit tool promo, from the uploaded timeline
(raw/tool_promo.mp4, 105.8 s, already assembled by the user).

Clips in the upload (hard cuts, original clock):
   0.00- 9.76  wide seated: hook "Kya aapka business ChatGPT, Google AI Overviews mein dikhta hai?"
   9.76-44.68  close seated: paid tools (Semrush, Ahrefs), what's missing, the free tool, extension vs deep audit
  44.68-51.44  dark desk shot, opening the tool
  51.44-93.40  phone recording of the monitor: URL -> audit -> score, categories, issues, fixes form
  93.40-105.80 CTA "comment TOOL"

No retakes to drop. Inside the timeline, pauses longer than 0.38 s are shortened, keeping 0.20 s after a word
ends and 0.12 s before the next one starts (silence map at -36 dB, d 0.12 s), so the hard cuts flow straight on.

    python3 tools/edl.py   -> edl.json + edl.js
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAKES = [(0.45, 105.35)]  # skip the dead air before the first word and after the last
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
