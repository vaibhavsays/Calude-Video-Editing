#!/usr/bin/env python3
"""Build the tight-cut edit decision list from the silence map of the original audio.

    python3 tools/edl.py            -> writes edl.json  {"keep": [[a,b], ...], "duration": d}
    python3 tools/edl.py map 12.3   -> prints the new-timeline time for original time 12.3

Rules: every pause longer than 0.30 s is shortened to ~0.15 s; filler islands ("um") are cut out completely.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
END = 94.533
FILLERS = [(58.87, 59.35), (59.60, 60.09)]   # "um", "um" (checked with Whisper)
LEAD, TAIL = 0.08, 0.07                       # audio kept after speech ends / before it starts

sil = [tuple(map(float, l.split())) for l in open(HERE / "silences.txt") if l.strip()]
cuts = []
for s, e in sil:
    if e - s > 0.30 and s > 0.0:
        cuts.append((s + LEAD, e - TAIL))
for a, b in FILLERS:   # remove filler plus the gaps around it
    before = max([s for s, e in sil if s <= a] or [a])
    after = min([e for s, e in sil if e >= b] or [b])
    cuts.append((before + LEAD, after - TAIL))
cuts.sort()
merged = []
for a, b in cuts:
    if merged and a <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], b))
    else:
        merged.append((a, b))
keep, t = [], 0.0
for a, b in merged:
    if a > t: keep.append([round(t, 3), round(a, 3)])
    t = b
if t < END: keep.append([round(t, 3), END])

def tmap(x):
    acc = 0.0
    for a, b in keep:
        if x < a: return round(acc, 3)
        if x <= b: return round(acc + x - a, 3)
        acc += b - a
    return round(acc, 3)

if len(sys.argv) > 2 and sys.argv[1] == "map":
    print(tmap(float(sys.argv[2])))
else:
    dur = round(sum(b - a for a, b in keep), 3)
    (HERE.parent / "edl.json").write_text(json.dumps({"keep": keep, "duration": dur}, indent=1))
    (HERE.parent / "edl.js").write_text("window.KEEP = " + json.dumps(keep) + ";\nwindow.EDL_DURATION = " + str(dur) + ";\n")
    print(len(keep), "segments, new duration", dur, "s (was", END, ")")
