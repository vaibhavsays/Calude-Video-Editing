#!/usr/bin/env python3
"""Render every slide of an Instagram carousel (1080x1350 PNGs).

    python3 carousels/render.py carousels/<name>/slides.html

Each <section class="slide" data-n="N"> is shown via the URL hash #N and screenshotted to slide_NN.png next to the HTML.
"""
import re, subprocess, sys, glob
from pathlib import Path

def browser():
    paths = glob.glob(str(Path.home() / ".cache/hyperframes/chrome/*/*/*/chrome-headless-shell"))
    paths += glob.glob("/opt/pw-browsers/chromium_headless_shell-*/*/headless_shell")
    return paths[0]

def main(html_path):
    page = Path(html_path).resolve()
    count = len(re.findall(r'class="slide[^"]*" data-n=', page.read_text()))
    for n in range(1, count + 1):
        out = page.parent / f"slide_{n:02d}.png"
        subprocess.run([browser(), "--headless", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--allow-file-access-from-files", "--virtual-time-budget=3000",
                        "--window-size=1080,1350", f"--screenshot={out}", f"{page.as_uri()}#{n}"],
                       check=True, capture_output=True)
        print("Wrote", out)

if __name__ == "__main__":
    main(sys.argv[1])
