#!/usr/bin/env python3
"""Render an Instagram Reel cover in the standard style (see STYLE.md) from a per-video config.json.

    python3 thumbnails/render.py thumbnails/<video>/config.json
"""
import json, subprocess, sys, glob
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent

# Pastel themes from the reference: centre glow, edge, dark ink, big-word tint.
THEMES = {
    "blue":  ("#e8f0fa", "#b7cfec", "#1d3a63", "#9dbbe0"),
    "peach": ("#fbe9df", "#f2c9b4", "#4a2a1c", "#efc2a8"),
    "mint":  ("#e3f5f0", "#b9e3d8", "#1f4a44", "#a6d8cb"),
    "pink":  ("#fbe6ec", "#f1c3d0", "#6b1f36", "#e8a9bb"),
}

def browser():
    paths = glob.glob(str(Path.home() / ".cache/hyperframes/chrome/*/*/*/chrome-headless-shell"))
    paths += glob.glob("/opt/pw-browsers/chromium_headless_shell-*/*/headless_shell")
    return paths[0]

def main(cfg_path):
    cfg_path = Path(cfg_path).resolve()
    cfg = json.loads(cfg_path.read_text())
    bg_center, bg_edge, ink, big = THEMES[cfg.get("theme", "blue")]
    logos = '<span class="rule"></span>'.join(
        f'<img src="assets/logos/{name}">' for name in cfg.get("logos", []))
    html = Template((HERE / "template.html").read_text()).substitute(
        bg_center=bg_center, bg_edge=bg_edge, ink=ink, big_color=big,
        title=cfg["title"], subtitle=cfg["subtitle"], big_word=cfg["big_word"],
        title_size=cfg.get("title_size", "112px"), sub_top=cfg.get("sub_top", "534px"),
        big_top=cfg.get("big_top", "605px"), big_size=cfg.get("big_size", "520px"),
        person_width=cfg.get("person_width", "980px"), photo=cfg["photo"], logos=logos)
    page = HERE / "_render.html"
    page.write_text(html)
    out = cfg_path.parent / cfg.get("output", "cover.png")
    subprocess.run([browser(), "--headless", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--allow-file-access-from-files", "--virtual-time-budget=3000",
                    "--window-size=1080,1920", f"--screenshot={out}", page.as_uri()],
                   check=True, capture_output=True)
    page.unlink()
    print("Wrote", out)

if __name__ == "__main__":
    main(sys.argv[1])
