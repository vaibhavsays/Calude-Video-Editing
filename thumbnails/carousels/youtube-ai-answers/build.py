#!/usr/bin/env python3
"""Instagram carousel: "Get your videos into AI answers" (YouTube titles, chapters, descriptions), 5 slides at 1080x1350 (4:5).

Same look as the Reel covers (thumbnails/STYLE.md): pastel radial background, Playfair Display titles,
Montserrat body, Instrument Serif big numbers, official logos. Slide 1 is the cover with Vaibhav's cut-out.

    python3 thumbnails/carousels/youtube-ai-answers/build.py   -> slide-01.png ... slide-10.png
"""
import glob, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TH = HERE.parent.parent  # thumbnails/
A = (TH / "assets").as_uri()
BG_C, BG_E, INK, BIG = "#fbe9df", "#f2c9b4", "#4a2a1c", "#efc2a8"  # peach theme
ACC = "#d9480f"
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
         box-shadow: 0 24px 60px rgba(74,42,28,.18); }}
.tip {{ position: absolute; left: 80px; right: 80px; bottom: 110px; display: flex; gap: 18px; align-items: flex-start;
        background: rgba(255,255,255,.55); border: 2px solid rgba(255,255,255,.9); border-radius: 26px; padding: 22px 28px;
        font-weight: 600; font-size: 30px; line-height: 1.35; }}
.tip i {{ font-style: normal; font-size: 36px; }}
.swipe {{ position: absolute; right: 70px; bottom: 44px; font-weight: 700; font-size: 26px; letter-spacing: 3px; opacity: .7; }}
.handle {{ position: absolute; left: 70px; bottom: 44px; font-weight: 700; font-size: 26px; opacity: .7; }}
.row {{ display: flex; align-items: center; gap: 18px; font-weight: 600; font-size: 36px; padding: 16px 0; border-bottom: 2px solid #f6ece6; }}
.row:last-child {{ border-bottom: none; }}
.ck {{ width: 44px; height: 44px; border-radius: 12px; background: #e3f6ea; color: #12a150; display: grid; place-items: center; font-weight: 900; font-size: 28px; flex: none; }}
.x {{ background: #fde8e8; color: #e5383b; }}
.lg {{ height: 52px; }}
.chip {{ display: inline-block; font-weight: 700; font-size: 32px; padding: 10px 20px; border-radius: 14px; background: #fff0e6; color: {ACC}; margin: 8px 10px 8px 0; }}
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
.c-sw {{ position: absolute; right: 40px; bottom: 300px; font-weight: 800; font-size: 30px; letter-spacing: 2px; color: #fff; background: {INK}; padding: 14px 26px; border-radius: 40px; box-shadow: 0 14px 30px rgba(74,42,28,.3); }}
</style>
<div class="c-big" style="font-size:300px;top:410px;letter-spacing:2px">VIDEO</div>{ARC.format(cy=980)}
<img class="person" src="{A}/vaibhav_suit_cutout.png">
<div class="c-logos"><span style="font-size:80px;line-height:1">▶️</span><span class="r"></span>{logo("google-color.svg", 84)}<span class="r"></span>{logo("openai.svg", 84)}<span class="r"></span>{logo("gemini-color.svg", 84)}</div>
<div class="c-title">Get Your Videos Into AI</div>
<div class="c-sub"><span class="l"></span><span>3 YOUTUBE FIXES</span><span class="l"></span></div>
<div class="c-sw">SWIPE →</div>
""")

def item(i, k, title, body, visual, tip):
    return (ARC.format(cy=1180) + chrome(i) + f'<div class="num">{k}</div><div class="kick">STEP {k} OF 3</div><h1>{title}</h1>'
            f'<div class="body" style="top:440px">{body}</div><div class="card" style="top:620px">{visual}</div>'
            f'<div class="tip"><i>💡</i><div>{tip}</div></div>')


# 2 title = the question
SLIDES.append(item(2, 1, "Title = the exact question",
    "People ask AI full questions. Name your video <b>the way customers ask</b>, not with your brand name.",
    f"""<div class="row"><span class="ck x">✕</span><span>"CoolFix Vlog #12 🔥"</span></div>
      <div class="row"><span class="ck">✓</span><span><b>"Why is my AC noisy after service? (3 easy fixes)"</b></span></div>""",
    "Use the questions customers ask you on calls and WhatsApp. That's your <b>title list</b>."))

# 3 answer first + chapters
SLIDES.append(item(3, 2, "Answer in the first 30 seconds",
    "Give the answer <b>first</b>, then explain. Add <b>chapters</b> so AI can jump to the exact part.",
    f"""<div style="display:flex;flex-direction:column;gap:10px;font-size:29px;font-weight:600">
      <div><span style="font-family:ui-monospace,monospace;color:{ACC};font-weight:800">0:00</span>&nbsp; The quick answer</div>
      <div><span style="font-family:ui-monospace,monospace;color:{ACC};font-weight:800">0:30</span>&nbsp; Fix 1: tighten the fan screw</div>
      <div><span style="font-family:ui-monospace,monospace;color:{ACC};font-weight:800">1:10</span>&nbsp; Fix 2: clip the indoor panel back</div>
      <div><span style="font-family:ui-monospace,monospace;color:{ACC};font-weight:800">1:50</span>&nbsp; When to call a technician</div></div>""",
    "Chapters = timestamps in your description, starting at <b>0:00</b>."))

# 4 description + captions
SLIDES.append(item(4, 3, "Words AI can read",
    "AI can't watch your video like a human. It reads the <b>text around it</b>.",
    "".join(f'<div class="row"><span class="ck">✓</span><span>{t}</span></div>' for t in [
        "<b>Description:</b> answer it in 3–4 lines", "<b>Captions:</b> fix the auto-captions",
        "<b>Link</b> to the matching page on your site", "<b>Embed</b> the video on that page"]),
    "Your Reels can be reused as <b>YouTube Shorts</b>. Same video, more places to be found."))

# 5 CTA
SLIDES.append(f"""
<style>
.cta-h {{ position: absolute; left: 70px; right: 70px; top: 150px; text-align: center; font-family: "PF"; font-weight: 700; font-size: 74px; line-height: 1.08; }}
.cta-s {{ position: absolute; left: 90px; right: 90px; top: 430px; text-align: center; font-weight: 600; font-size: 34px; line-height: 1.45; }}
.btn {{ position: absolute; left: 50%; transform: translateX(-50%); white-space: nowrap; font-weight: 800; font-size: 38px; padding: 22px 44px; border-radius: 60px; }}
.p2 {{ position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 430px; filter: drop-shadow(0 24px 40px rgba(20,40,70,.22)); }}
</style>
{ARC.format(cy=1150)}{chrome(5)}
<div class="cta-h">Already making videos?</div>
<div class="cta-s">Let's make sure Google &amp; AI can actually find them and send you customers.</div>
<div class="btn" style="top:580px;background:{INK};color:#fff">DM me "VIDEO" 📩</div>
<div class="btn" style="top:690px;background:#fff;color:{INK}">💾 Save · 📤 Share with your video editor</div>
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
