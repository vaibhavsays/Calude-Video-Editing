#!/usr/bin/env python3
"""Instagram carousel: "Get your business recommended by ChatGPT" (7 GEO steps), 10 slides at 1080x1350 (4:5).

Same look as the Reel covers (thumbnails/STYLE.md): pastel radial background, Playfair Display titles,
Montserrat body, Instrument Serif big numbers, official logos. Slide 1 is the cover with Vaibhav's cut-out.

    python3 thumbnails/carousels/ai-recommendations/build.py   -> slide-01.png ... slide-10.png
"""
import glob, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TH = HERE.parent.parent  # thumbnails/
A = (TH / "assets").as_uri()
BG_C, BG_E, INK, BIG = "#e8f0fa", "#b7cfec", "#1d3a63", "#9dbbe0"  # powder blue theme
ACC = "#2f6fdb"
N = 10


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
         box-shadow: 0 24px 60px rgba(29,58,99,.18); }}
.tip {{ position: absolute; left: 80px; right: 80px; bottom: 110px; display: flex; gap: 18px; align-items: flex-start;
        background: rgba(255,255,255,.55); border: 2px solid rgba(255,255,255,.9); border-radius: 26px; padding: 22px 28px;
        font-weight: 600; font-size: 30px; line-height: 1.35; }}
.tip i {{ font-style: normal; font-size: 36px; }}
.swipe {{ position: absolute; right: 70px; bottom: 44px; font-weight: 700; font-size: 26px; letter-spacing: 3px; opacity: .7; }}
.handle {{ position: absolute; left: 70px; bottom: 44px; font-weight: 700; font-size: 26px; opacity: .7; }}
.row {{ display: flex; align-items: center; gap: 18px; font-weight: 600; font-size: 36px; padding: 16px 0; border-bottom: 2px solid #eef2f8; }}
.row:last-child {{ border-bottom: none; }}
.ck {{ width: 44px; height: 44px; border-radius: 12px; background: #e3f6ea; color: #12a150; display: grid; place-items: center; font-weight: 900; font-size: 28px; flex: none; }}
.x {{ background: #fde8e8; color: #e5383b; }}
.lg {{ height: 52px; }}
.chip {{ display: inline-block; font-weight: 700; font-size: 32px; padding: 10px 20px; border-radius: 14px; background: #eaf1fd; color: {ACC}; margin: 8px 10px 8px 0; }}
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
.c-sw {{ position: absolute; right: 40px; bottom: 300px; font-weight: 800; font-size: 30px; letter-spacing: 2px; color: #fff; background: {INK}; padding: 14px 26px; border-radius: 40px; box-shadow: 0 14px 30px rgba(29,58,99,.3); }}
</style>
<div class="c-big">AI</div>{ARC.format(cy=980)}
<img class="person" src="{A}/vaibhav_suit_cutout.png">
<div class="c-logos">{logo("openai.svg", 84)}<span class="r"></span>{logo("gemini-color.svg", 84)}<span class="r"></span>{logo("perplexity-color.svg", 84)}<span class="r"></span>{logo("google-color.svg", 84)}</div>
<div class="c-title">Get Recommended by ChatGPT</div>
<div class="c-sub"><span class="l"></span><span>7 STEPS FOR BUSINESSES</span><span class="l"></span></div>
<div class="c-sw">SWIPE →</div>
""")

# 2 the shift
SLIDES.append(ARC.format(cy=1180) + chrome(2) + f"""
<div class="kick">THE SHIFT</div>
<h1 style="right:80px">Your customers stopped scrolling Google. They ask AI.</h1>
<div class="card" style="top:430px">
  <div style="display:flex;gap:14px;align-items:center;margin-bottom:22px">{logo("openai.svg",44)}{logo("gemini-color.svg",44)}{logo("perplexity-color.svg",44)}<span style="font-weight:700;font-size:26px;opacity:.6">AI search</span></div>
  <div style="margin-left:auto;width:fit-content;background:#1d3a63;color:#fff;font-weight:600;font-size:32px;padding:14px 24px;border-radius:24px 24px 6px 24px">Best CA firm in Pune for a startup?</div>
  <div style="margin-top:20px;background:#f4f7fc;border-radius:24px;padding:20px 26px;font-weight:600;font-size:30px;line-height:1.5">
    ✨ Top picks:<br>1. <b style="color:{ACC}">Firm A</b> – startup specialists<br>2. <b style="color:{ACC}">Firm B</b> – 4.9★, 300+ reviews<br>3. <b style="color:{ACC}">Firm C</b> – GST + funding help</div>
</div>
<div class="tip"><i>👉</i><div>AI names <b>3 businesses</b>, not 10 blue links. If you're not one of them, you're invisible.</div></div>
""")

STEPS = [
    ("Complete your Google Business Profile",
     "Gemini and Google's AI Overviews pull straight from it. Fill <b>every</b> field.",
     "".join(f'<div class="row"><span class="ck">✓</span>{t}</div>' for t in
             ["Exact categories + services", "Hours, area served, attributes", "20+ real photos", "A post every week"]),
     "Half-filled profiles look unreliable to AI. Complete ones get quoted."),
    ("Get reviews that say <i>what</i> you did",
     "AI reads review text. \"Great service\" says nothing. Specifics get you recommended.",
     f'<div style="font-size:44px;color:#fbbc04;letter-spacing:4px">★★★★★</div><div style="font-family:PF;font-size:34px;font-weight:600;line-height:1.35;margin-top:8px">"Best <span style="background:#fff2b3">dentist in Baner</span> for <span style="background:#fff2b3">painless root canal</span>. Done in one visit."</div>',
     "Ask happy customers to mention the <b>service</b> and your <b>area</b> in the review."),
    ("Add schema markup to your website",
     "Schema is a label AI can read: who you are, what you sell, where, and your rating.",
     '<div class="mono">{ "@type": "LocalBusiness",\n  "name": "Your Brand",\n  "areaServed": "Pune",\n  "aggregateRating": "4.8" }</div>',
     "Start with <b>LocalBusiness</b>, <b>FAQ</b> and <b>Product</b> schema."),
    ("Answer real customer questions",
     "AI picks pages that answer a question directly. Write the answer in the first 2 lines.",
     "".join(f'<div class="row"><span class="ck" style="background:#eaf1fd;color:{ACC}">?</span>{t}</div>' for t in
             ["How much does it cost?", "Which is best for my budget?", "How long does it take?", "You vs competitor: what's the difference?"]),
     "One clear page per question beats one long page about everything."),
    ("Get mentioned on other websites",
     "AI trusts what <b>others</b> say about you more than what you say about yourself.",
     "".join(f'<span class="chip">{t}</span>' for t in
             ["📰 News & PR", "✍️ Guest posts", "📒 Directories", "💬 Reddit & Quora", "🎙️ Podcasts", "🏆 'Best of' lists"]),
     "Third-party validation is the backbone of GEO."),
    ("Keep your details identical everywhere",
     "Name, address, phone, services: the same on every platform, so AI is confident it's you.",
     f'<div class="row"><span class="ck">✓</span>Website · Google profile · LinkedIn</div><div class="row"><span class="ck">✓</span>Justdial · IndiaMART · Practo</div><div class="row"><span class="ck x">✕</span>Old address on one listing = confused AI</div>',
     "Audit your listings once; fix every mismatch."),
    ("Track your AI visibility monthly",
     "Ask the AI tools what your customers ask, and note who gets named.",
     f'<div style="display:flex;gap:16px;align-items:center;margin-bottom:16px">{logo("openai.svg",48)}{logo("gemini-color.svg",48)}{logo("perplexity-color.svg",48)}</div><div style="background:#f4f7fc;border-radius:20px;padding:18px 24px;font-weight:700;font-size:32px">"Best <span style="color:{ACC}">[your service]</span> in <span style="color:{ACC}">[your city]</span>?"</div><div style="margin-top:16px;font-weight:600;font-size:29px">Named? ✅ Not named? Fix steps 1–6.</div>',
     "Same prompts every month, so you can see the progress."),
]
for k, (t, b, v, tip) in enumerate(STEPS, 1):
    SLIDES.append(step(k + 2, k, t, b, v, tip))

# 10 CTA
SLIDES.append(f"""
<style>
.cta-h {{ position: absolute; left: 70px; right: 70px; top: 150px; text-align: center; font-family: "PF"; font-weight: 700; font-size: 76px; line-height: 1.08; }}
.cta-s {{ position: absolute; left: 90px; right: 90px; top: 430px; text-align: center; font-weight: 600; font-size: 34px; line-height: 1.45; }}
.btn {{ position: absolute; left: 50%; transform: translateX(-50%); white-space: nowrap; font-weight: 800; font-size: 38px; padding: 22px 44px; border-radius: 60px; }}
.p2 {{ position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 430px; filter: drop-shadow(0 24px 40px rgba(20,40,70,.22)); }}
</style>
{ARC.format(cy=1150)}{chrome(10)}
<div class="cta-h">Does AI recommend <i>your</i> business?</div>
<div class="cta-s">I'll check ChatGPT, Gemini &amp; Perplexity for you and show you what's missing.</div>
<div class="btn" style="top:580px;background:{INK};color:#fff">DM me "AUDIT" 📩</div>
<div class="btn" style="top:690px;background:#fff;color:{INK}">💾 Save · 📤 Share with a business owner</div>
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
