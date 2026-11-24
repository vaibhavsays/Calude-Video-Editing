# align_words.py <wav> <parakeet_tokens.tsv> <script.txt> <out.json>
# script.txt: one Descript segment per line: "<start>\t<end>\t<words with | cue breaks and *highlights*>"
import sys, json, re, difflib, numpy as np, soundfile as sf
wav, tokf, scf, outf = sys.argv[1:5]
a, sr = sf.read(wav, dtype="float32")
hop = 160  # 10 ms
rms = np.sqrt(np.convolve(a ** 2, np.ones(400) / 400, mode="same")[::hop])
db = 20 * np.log10(rms + 1e-9)
voiced = db > (np.percentile(db, 95) - 30)   # speech frames

def vt(t0, t1):  # voiced frames between t0 and t1
    return voiced[int(t0 * 100):int(t1 * 100)]

# parakeet words with times
pw = []
for line in open(tokf):
    t, tok = line.rstrip("\n").split("\t")
    t = float(t)
    if tok.startswith(" ") or not pw:
        pw.append([tok.strip(), t, t])
    else:
        pw[-1][0] += tok; pw[-1][2] = t
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
pw = [(norm(w), s, e + 0.06) for w, s, e in pw if norm(w)]

def syl(w):
    w = norm(w)
    return max(1, len(re.findall(r"[aeiouy]+", w))) if not w.isdigit() else 2

segs = []
for line in open(scf):
    if not line.strip(): continue
    s, e, txt = line.rstrip("\n").split("\t")
    segs.append((float(s), float(e), txt))

words = []  # dicts: w (display), cue_break_before, seg
for si, (s, e, txt) in enumerate(segs):
    for k, chunk in enumerate(txt.split("|")):
        for j, w in enumerate(chunk.split()):
            words.append({"w": w, "brk": j == 0, "seg": si})
# a cue also breaks where the text explicitly starts a new chunk at the segment start
# anchors: segment boundaries
anchor = {}
idx = 0
for si, (s, e, txt) in enumerate(segs):
    ids = [i for i, w in enumerate(words) if w["seg"] == si]
    anchor[ids[0]] = ("s", s)
    anchor[ids[-1]] = anchor.get(ids[-1], ("e", e)) if ids[0] != ids[-1] else ("s", s)
    words[ids[-1]]["seg_end"] = e
# parakeet anchors: global fuzzy alignment of normalized word sequences
mine = [norm(w["w"]) for w in words]
theirs = [p[0] for p in pw]
sm = difflib.SequenceMatcher(None, mine, theirs, autojunk=False)
pk = {}
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        i, j = blk.a + k, blk.b + k
        if len(mine[i]) >= 2: pk[i] = pw[j]
# fuzzy extra matches for near-identical words inside unmatched gaps
for i, m in enumerate(mine):
    if i in pk or len(m) < 4: continue
    seg = words[i]["seg"]; s0, s1 = segs[seg][0] - 0.3, segs[seg][1] + 0.3
    best = max(((difflib.SequenceMatcher(None, m, p[0]).ratio(), p) for p in pw if s0 <= p[1] <= s1), default=(0, None))
    if best[0] >= 0.8: pk[i] = best[1]
# assign times segment by segment
for si, (s, e, txt) in enumerate(segs):
    ids = [i for i, w in enumerate(words) if w["seg"] == si]
    fixed = {ids[0]: s}
    for i in ids:
        if i in pk and s - 0.05 <= pk[i][1] <= e + 0.05 and i != ids[0]:
            fixed[i] = pk[i][1]
    fixed_end = e
    keys = sorted(fixed)
    # enforce monotonic anchors
    clean = []
    for i in keys:
        if not clean or fixed[i] > clean[-1][1] + 0.05: clean.append((i, fixed[i]))
    clean.append((ids[-1] + 1, fixed_end))
    for (i0, t0), (i1, t1) in zip(clean, clean[1:]):
        run = list(range(i0, i1))
        v = vt(t0, t1); total = v.sum() or 1
        cum = np.cumsum(v) / total
        weights = np.array([syl(words[i]["w"]) for i in run], float); wc = np.cumsum(weights) / weights.sum()
        prev = 0.0
        for i, c in zip(run, wc):
            f0 = np.searchsorted(cum, prev); f1 = np.searchsorted(cum, c)
            words[i]["s"] = round(t0 + f0 / 100, 3); words[i]["e"] = round(t0 + max(f1, f0 + 8) / 100, 3)
            prev = c
        if i0 in pk and i0 != ids[0]:
            words[i0]["s"] = round(t0, 3)
print(sum(1 for i in pk), "parakeet anchors of", len(words), "words")
json.dump(words, open(outf, "w"), ensure_ascii=False, indent=0)
