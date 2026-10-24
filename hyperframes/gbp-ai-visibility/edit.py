#!/usr/bin/env python3
"""Cut list and timing for the GBP AI Visibility reel.

Everything here is in *source* time (seconds into raw main.mp4). The script
removes the pauses between phrases, maps every event to output time, and
writes:
  - timing.js   constants read by index.html
  - edit.json   kept segments + key times read by build.sh
and rewrites the data-start / data-duration of the B-roll <video> tags in
index.html to match.

Run it after changing anything below, then render and build.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent

# Pauses found with: silencedetect=n=-33dB:d=0.22 (after a 90 Hz high-pass).
PAUSES = [
    (7.08, 7.31), (7.45, 7.67), (10.12, 10.56), (12.16, 12.54), (14.28, 14.66),
    (16.55, 16.91), (18.35, 18.67), (21.08, 21.48), (21.78, 22.07), (23.40, 23.73),
    (26.41, 27.04), (29.73, 30.11), (34.35, 34.67), (35.49, 35.86), (37.51, 37.78),
    (40.13, 40.46), (40.55, 40.94), (43.37, 43.71), (44.36, 44.75), (47.36, 47.74),
]
KEEP_AROUND = 0.07   # silence kept on each side of a pause
# Fumbles cut whole (no words in the captions there), source time.
FUMBLES = [
    (17.75, 20.10),  # between "like what" and "questions are being asked"
]
SRC_END = 49.39      # last word ends ~49.27

CTA_LEN = 5.2 - 0.6  # CTA clip in/out, see build.sh
CTA_HOLD = 1.2
# CTA line "Okay, so comment 'TOOL' and I will send the tool link directly in your DMs."
CTA_COMMENT = 0.68  # "comment", seconds into the CTA
CTA_TOOL = 1.08     # "'TOOL'"
CTA_DM = 2.28       # "send the tool link..."

# Events, source time, each on the line it illustrates (see captions.json).
HOOK_CUT_1 = 4.73    # "If not," - hook cards leave
HOOK_CUT_2 = 7.63
SPLIT_START = 9.0    # "go to the tool."
ASK = (15.07, 23.67)  # "and it will tell you exactly everything ... in which regions."
BAND = (30.1, 33.8)  # "Which top referrals are suggesting you."
ZERO = (46.33, SRC_END)  # "And with such results, you can show this report to anyone."
GLOW_ON = 11.0
CLICK = 12.4         # button click lands near the end of shot 0

# B-roll clips: html id -> (source start, source end, media start, rate)
VIDEOS = {
    "shot-video-0": (9.0, 12.7, 7.9, 1),       # "go to the tool. In the tool, ..."
    "shot-video-1": (12.7, 15.07, 18.5, 1.4),  # "website. You need to update it,"
    "shot-video-4": (23.67, 27.16, 5.6, 1),    # "Which keywords ... missing."
    "shot-video-5": (27.16, 30.1, 9.6, 0.7),   # "Which competitors are ranking above you."
    "shot-video-6": (30.1, 33.8, 12.0, 0.8),   # "Which top referrals are suggesting you."
    "shot-video-7": (33.8, 42.58, 15.0, 0.65), # "content gaps ... long-tail keywords ... fill them in."
    "shot-video-3": (42.58, 46.33, 0.3, 1),    # "export the entire report."
    "zero-video": (46.33, SRC_END, 3.5, 0.5),  # "with such results ..."
}


def keep_segments():
    cuts = [(s + KEEP_AROUND, e - KEEP_AROUND) for s, e in PAUSES]
    cuts = [c for c in cuts if c[1] - c[0] >= 0.08] + list(FUMBLES)
    merged = []
    for a, b in sorted(cuts):
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    segs, t = [], 0.0
    for a, b in merged:
        segs.append((t, a))
        t = b
    segs.append((t, SRC_END))
    return segs


SEGS = keep_segments()


def out(t):
    """Source time -> output time. Times inside a removed pause snap to the cut."""
    acc = 0.0
    for a, b in SEGS:
        if t <= a:
            return round(acc, 3)
        if t <= b:
            return round(acc + (t - a), 3)
        acc += b - a
    return round(acc, 3)


AROLL_END = out(SRC_END)
TOTAL = round(AROLL_END + CTA_LEN + CTA_HOLD, 3)


def caption_groups():
    """Words (read from the Kapwing captions, see captions.json) -> on-screen groups of up to 3 words."""
    caps = json.loads((HERE / "captions.json").read_text())
    words = [(w["w"], out(w["src"])) for w in caps["main"]]
    words += [(w["w"], round(AROLL_END + w["cta"], 3)) for w in caps["cta"]]
    groups, cur = [], []
    for i, (w, s) in enumerate(words):
        nxt = words[i + 1][1] if i + 1 < len(words) else s + 0.6
        cur.append({"w": w, "s": s, "e": round(min(nxt, s + 0.8), 3)})
        chars = sum(len(x["w"]) + 1 for x in cur)
        nxt_len = len(words[i + 1][0]) if i + 1 < len(words) else 0
        if (w[-1] in ".,?!" and len(cur) >= 2) or len(cur) == 3 or chars + nxt_len > 20 or nxt - s > 0.8 or i + 1 == len(words):
            groups.append({"s": cur[0]["s"], "e": cur[-1]["e"], "words": cur})
            cur = []
    return groups

timing = {
    "HOOK_CUT_1": out(HOOK_CUT_1),
    "HOOK_CUT_2": out(HOOK_CUT_2),
    "SPLIT_START": out(SPLIT_START),
    "ASK": [out(ASK[0]), out(ASK[1])],
    "ZERO": [out(ZERO[0]), out(ZERO[1])],
    "BAND": [out(BAND[0]), out(BAND[1])],
    "GLOW_ON": out(GLOW_ON),
    "CLICK": out(CLICK),
    "AROLL_END": AROLL_END,
    "CTA_COMMENT": round(AROLL_END + CTA_COMMENT, 3),
    "CTA_TOOL": round(AROLL_END + CTA_TOOL, 3),
    "CTA_DM": round(AROLL_END + CTA_DM, 3),
    "CAPTIONS": caption_groups(),
    "TOTAL": TOTAL,
    "SHOTS": {k: [out(v[0]), out(v[1])] for k, v in VIDEOS.items()},
}

(HERE / "timing.js").write_text(
    "// Generated by edit.py. Output-video seconds.\nwindow.EDIT = " + json.dumps(timing, indent=2) + ";\n"
)
(HERE / "edit.json").write_text(
    json.dumps({"segments": SEGS, "split_start": timing["SPLIT_START"], "aroll_end": AROLL_END, "cta_hold": CTA_HOLD}, indent=2) + "\n"
)

html_path = HERE / "index.html"
html = html_path.read_text()
for vid, (s, e, media, rate) in VIDEOS.items():
    a, b = out(s), out(e)
    pattern = re.compile(r'(<video id="' + re.escape(vid) + r'"[^>]*?) data-start="[^"]*" data-duration="[^"]*"')
    html, n = pattern.subn(rf'\1 data-start="{a}" data-duration="{round(b - a, 3)}"', html)
    assert n == 1, vid
html = re.sub(r'(data-composition-id="main" data-start="0" data-duration=")[^"]*"', rf'\g<1>{TOTAL}"', html)
html_path.write_text(html)

print(f"{len(SEGS)} segments, removed {SRC_END - AROLL_END:.2f}s of pauses; a-roll {AROLL_END}s, total {TOTAL}s")
