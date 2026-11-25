#!/usr/bin/env python3
"""words.json -> captions.js (WCUES on the original clock; index.html maps them through T())."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
W = json.loads((HERE / "words.json").read_text())
cues = []
for w in W:
    if w["brk"] or not cues: cues.append([])
    cues[-1].append(w)
out = []
for k, c in enumerate(cues):
    s = round(c[0]["s"] - 0.04, 3)
    e = round(cues[k + 1][0]["s"] - 0.04, 3) if k + 1 < len(cues) else round(c[-1]["e"] + 0.3, 3)
    if k + 1 < len(cues) and e - c[-1]["e"] > 0.6: e = round(c[-1]["e"] + 0.35, 3)
    out.append([s, e, [[round(w["s"], 3), w["w"]] for w in c]])
js = ("// Word-timed Hinglish captions (Roman script) on the ORIGINAL (raw/day11_entities.mp4) clock: Descript segment starts +\n"
      "// Parakeet anchors + voiced-audio fit (tools/align_words.py). Each cue: [start, end, [[word_start, word], ...]].\n"
      "const WCUES = " + json.dumps(out, ensure_ascii=False) + ";\n"
      "WCUES.forEach(([s, e, ws]) => CUES.push([T(s), T(e), ws.map(([t, x]) => [T(t), x])]));\n")
(HERE.parent / "captions.js").write_text(js)
for c in out: print(f"{c[0]:6.2f} {c[1]:6.2f}  " + " ".join(f"{w}@{t:.2f}" for t, w in c[2]))
