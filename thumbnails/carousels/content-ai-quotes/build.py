#!/usr/bin/env python3
"""Instagram carousel: "Content AI loves to quote" (comparison pages, original data, freshness), 5 slides at 1080x1350 (4:5).

Same look as the Reel covers (thumbnails/STYLE.md): pastel radial background, Playfair Display titles,
Montserrat body, Instrument Serif big numbers, official logos. Slide 1 is the cover with Vaibhav's cut-out.

    python3 thumbnails/carousels/content-ai-quotes/build.py   -> slide-01.png ... slide-10.png
"""
import glob, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TH = HERE.parent.parent  # thumbnails/
A = (TH / "assets").as_uri()
BG_C, BG_E, INK, BIG = "#e3f5f0", "#b9e3d8", "#1f4a44", "#a6d8cb"  # mint theme
ACC = "#0f8a6c"
N = 5


def browser():
    p = glob.glob(str(Path.home() / ".cache/hyperframes/chrome/*/*/*/chrome-headless-shell"))
    p += glob.glob("/opt/pw-browsers/chromium_headless_shell-*/*/headless_shell")
    return p[0]


CSS = f"""
@font-face {{ font-family: "PF"; src: url("{A}/fonts/PlayfairDisplay-var.woff2"); font-weight: 400 900; }}
@font-face {{ font-family: "IS"; src: url("{A}/fonts/InstrumentSerif-400.woff2"); }}
@font-face {{ font-family: "MS"; src: url("{A}/fonts/Montserrat-var.woff2"); font-weight: 100 900; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1350px; overflow: hidden; }}
body {{ position: relative; font-family: "MS"; color: {INK};
       background: radial-gradient(ellipse 85% 65% at 50% 48%, {BG_C} 0%, {BG_E} 100%); }}
.arc {{ position: absolute; inset: 0; }}
.top {{ position: absolute; left: 70px; right: 70px; top: 56px; display: flex; justify-content: space-between; align-items: center;
        font-weight: 700; font-size: 28px; letter-spacing: 1px; opacity: .8; }}
.num {{ position: absolute; right: 70px; top: 130px; font-family: "IS"; font-size: 260px; line-height: .8; color: {BIG}; }}
.kick {{ position: absolute; left: 80px; top: 170px; font-weight: 700; font-size: 30px; letter-spacing: 5px; color: {ACC}; }}
h1 {{ position: absolute; left: 80px; right: 250px; top: 220px; font-family: "PF"; font-weight: 700; font-size: 66px; line-height: 1.08; letter-spacing: -1px; }}
.body {{ position: absolute; left: 80px; right: 90px; font-weight: 500; font-size: 36px; line-height: 1.45; }}
.body b {{ font-weight: 800; }}
.card {{ position: absolute; left: 80px; right: 80px; background: #fff; border-radius: 34px; padding: 34px 40px;
         box-shadow: 0 24px 60px rgba(31,74,68,.18); }}
.tip {{ position: absolute; left: 80px; right: 80px; bottom: 110px; display: flex; gap: 18px; align-items: flex-start;
        background: rgba(255,255,255,.55); border: 2px solid rgba(255,255,255,.9); border-radius: 26px; padding: 22px 28px;
        font-weight: 600; font-size: 30px; line-height: 1.35; }}
.tip i {{ font-style: normal; font-size: 36px; }}
.swipe {{ position: absolute; right: 70px; bottom: 44px; font-weight: 700; font-size: 26px; letter-spacing: 3px; opacity: .7; }}
.handle {{ position: absolute; left: 70px; bottom: 44px; font-weight: 700; font-size: 26px; opacity: .7; }}
.row {{ display: flex; align-items: center; gap: 18px; font-weight: 600; font-size: 36px; padding: 16px 0; border-bottom: 2px solid #e8f3ef; }}
.row:last-child {{ border-bottom: none; }}
.ck {{ width: 44px; height: 44px; border-radius: 12px; background: #e3f6ea; color: #12a150; display: grid; place-items: center; font-weight: 900; font-size: 28px; flex: none; }}
.x {{ background: #fde8e8; color: #e5383b; }}
.lg {{ height: 52px; }}
.chip {{ display: inline-block; font-weight: 700; font-size: 32px; padding: 10px 20px; border-radius: 14px; background: #e6f6f1; color: {ACC}; margin: 8px 10px 8px 0; }}
.mono {{ font-family: ui-monospace, "DejaVu Sans Mono", monospace; font-size: 32px; line-height: 1.5; color: #304a6e; white-space: pre; }}
"""

ARC = """<svg class="arc" width="1080" height="1350" viewBox="0 0 1080 1350"><defs><filter id="g" x="-20%" y="-20%" width="140%" height="140%">
<feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<ellipse cx="540" cy="{cy}" rx="620" ry="240" transform="rotate(-14 540 {cy})" fill="none" stroke="#fff" stroke-width="4" stroke-opacity=".85" filter="url(#g)"/></svg>"""


def chrome(i, extra=""):
    return (f'<div class="top"><span>@aiseovaibhav</span><span>{i:02d} / {N:02d}</span></div>' +
            (f'<div class="swipe">SWIPE →</div>' if i < N else "") + extra)


def logo(n, h=52):
    return f'<img class="lg" style="height:{h}px" src="{A}/logos/{n}">'


def step(i, k, title, body, visual, tip, body_top=440, vis_top=620):
    return (ARC.format(cy=1180) + chrome(i) + f'<div class="num">{k}</div><div class="kick">STEP {k} OF 7</div><h1>{title}</h1>'
            f'<div class="body" style="top:{body_top}px">{body}</div>'
            f'<div class="card" style="top:{vis_top}px">{visual}</div>'
            f'<div class="tip"><i>💡</i><div>{tip}</div></div>')


SLIDES = []

# 1 cover
SLIDES.append(f"""
<style>
.c-logos {{ position: absolute; top: 70px; left: 0; right: 0; display: flex; justify-content: center; align-items: center; gap: 40px; }}
.c-logos img {{ height: 84px; }} .c-logos .r {{ width: 3px; height: 74px; background: {INK}; opacity: .5; }}
.c-title {{ position: absolute; top: 196px; width: 100%; text-align: center; font-family: "PF"; font-weight: 700; font-size: 64px; line-height: 1.05; letter-spacing: -1px; }}
.c-sub {{ position: absolute; top: 284px; width: 100%; display: flex; justify-content: center; align-items: center; gap: 24px; font-weight: 600; font-size: 34px; letter-spacing: 4px; }}
.c-sub .l {{ width: 110px; height: 2px; background: {INK}; opacity: .6; }}
.c-big {{ position: absolute; top: 340px; width: 100%; text-align: center; font-family: "IS"; font-size: 520px; line-height: .8; color: {BIG}; letter-spacing: 6px; }}
.person {{ position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 760px; filter: drop-shadow(0 24px 40px rgba(20,40,70,.22)); }}
.c-sw {{ position: absolute; right: 40px; bottom: 300px; font-weight: 800; font-size: 30px; letter-spacing: 2px; color: #fff; background: {INK}; padding: 14px 26px; border-radius: 40px; box-shadow: 0 14px 30px rgba(31,74,68,.3); }}
</style>
<div class="c-big" style="font-size:300px;top:410px;letter-spacing:2px">QUOTE</div>{ARC.format(cy=980)}
<img class="person" src="{A}/vaibhav_suit_cutout.png">
<div class="c-logos">{logo("openai.svg", 84)}<span class="r"></span>{logo("perplexity-color.svg", 84)}<span class="r"></span>{logo("gemini-color.svg", 84)}<span class="r"></span>{logo("google-color.svg", 84)}</div>
<div class="c-title">Content AI Loves to Quote</div>
<div class="c-sub"><span class="l"></span><span>3 TYPES THAT GET CITED</span><span class="l"></span></div>
<div class="c-sw">SWIPE →</div>
""")

def item(i, k, title, body, visual, tip):
    return (ARC.format(cy=1180) + chrome(i) + f'<div class="num">{k}</div><div class="kick">CONTENT TYPE {k} OF 3</div><h1>{title}</h1>'
            f'<div class="body" style="top:440px">{body}</div><div class="card" style="top:620px">{visual}</div>'
            f'<div class="tip"><i>💡</i><div>{tip}</div></div>')


# 2 comparison pages
SLIDES.append(item(2, 1, "Comparison pages",
    "People ask AI <b>\"X or Y?\"</b> all the time. A clear, honest comparison is easy for AI to quote.",
    f"""<div style="display:grid;grid-template-columns:1.1fr 1fr 1fr;font-size:30px;font-weight:600;row-gap:14px">
      <div></div><div style="font-weight:800;color:{ACC}">Root canal</div><div style="font-weight:800;color:{ACC}">Extraction</div>
      <div style="opacity:.7">Saves tooth</div><div>✅ Yes</div><div>❌ No</div>
      <div style="opacity:.7">Visits</div><div>1–2</div><div>1</div>
      <div style="opacity:.7">Best for</div><div>Infected tooth</div><div>Badly broken tooth</div></div>""",
    "Use a simple <b>table</b> + a one-line verdict: <b>\"Choose X if…, choose Y if…\"</b>"))

# 3 original data
SLIDES.append(item(3, 2, "Your own numbers",
    "AI needs facts to back its answers. <b>Original data</b> from your business is something nobody else has.",
    f"""<div style="display:flex;gap:18px">
      <div style="flex:1;background:#f2faf7;border-radius:20px;padding:18px;text-align:center"><div style="font-family:IS;font-size:76px;color:{ACC};line-height:1">500+</div><div style="font-weight:700;font-size:26px">ACs repaired<br>in Baner</div></div>
      <div style="flex:1;background:#f2faf7;border-radius:20px;padding:18px;text-align:center"><div style="font-family:IS;font-size:76px;color:{ACC};line-height:1">45 min</div><div style="font-weight:700;font-size:26px">average<br>repair time</div></div>
      <div style="flex:1;background:#f2faf7;border-radius:20px;padding:18px;text-align:center"><div style="font-family:IS;font-size:76px;color:{ACC};line-height:1">4.9★</div><div style="font-weight:700;font-size:26px">from 300+<br>reviews</div></div></div>
      <div style="font-size:24px;opacity:.6;margin-top:10px">Example numbers: use your real ones</div>""",
    "Only publish numbers you can <b>prove</b>. Wrong data hurts trust."))

# 4 freshness
SLIDES.append(item(4, 3, "Fresh, dated updates",
    "AI prefers answers that look <b>current</b>. Old pages with 2021 prices quietly lose to newer ones.",
    f"""<div style="display:flex;align-items:center;gap:18px">
      <div style="flex:1;border:3px solid #f1c3c3;border-radius:20px;padding:16px 20px;opacity:.7"><div style="font-weight:800;font-size:28px">AC service price</div><div style="font-size:24px;color:#e5383b;font-weight:700">Last updated: 2021 ❌</div></div>
      <div style="font-size:50px">→</div>
      <div style="flex:1;border:3px solid {ACC};border-radius:20px;padding:16px 20px"><div style="font-weight:800;font-size:28px">AC service price</div><div style="font-size:24px;color:{ACC};font-weight:700">Updated: this month ✅</div></div></div>""",
    "Show an <b>\"Updated on\"</b> date and refresh prices, offers & FAQs every few months."))

# 5 CTA
SLIDES.append(f"""
<style>
.cta-h {{ position: absolute; left: 70px; right: 70px; top: 150px; text-align: center; font-family: "PF"; font-weight: 700; font-size: 74px; line-height: 1.08; }}
.cta-s {{ position: absolute; left: 90px; right: 90px; top: 430px; text-align: center; font-weight: 600; font-size: 34px; line-height: 1.45; }}
.btn {{ position: absolute; left: 50%; transform: translateX(-50%); white-space: nowrap; font-weight: 800; font-size: 38px; padding: 22px 44px; border-radius: 60px; }}
.p2 {{ position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 430px; filter: drop-shadow(0 24px 40px rgba(20,40,70,.22)); }}
</style>
{ARC.format(cy=1150)}{chrome(5)}
<div class="cta-h">Is your content <i>quotable</i> by AI?</div>
<div class="cta-s">I'll review your website and tell you which pages AI will skip, and what to add.</div>
<div class="btn" style="top:580px;background:{INK};color:#fff">DM me "QUOTE" 📩</div>
<div class="btn" style="top:690px;background:#fff;color:{INK}">💾 Save · 📤 Share with your team</div>
<img class="p2" src="{A}/vaibhav_suit_cutout.png">
<div class="btn" style="bottom:40px;background:{ACC};color:#fff;font-size:32px;padding:16px 34px">Follow @aiseovaibhav</div>
""")


def main():
    b = browser()
    for i, s in enumerate(SLIDES, 1):
        page = HERE / f"_s{i}.html"
        page.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{s}</body></html>')
        out = HERE / f"slide-{i:02d}.png"
        subprocess.run([b, "--headless", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--allow-file-access-from-files", "--virtual-time-budget=3000", "--window-size=1080,1350",
                        f"--screenshot={out}", page.as_uri()], check=True, capture_output=True)
        page.unlink()
        print("Wrote", out.name)


if __name__ == "__main__":
    main()
