# Standard thumbnail style (Instagram Reel covers)

Every Reel gets a cover in exactly this design. Reference: `style_reference.webp`, four examples of the same template in different colours.

## Canvas
- 1080×1920 (9:16), PNG.
- Instagram's profile grid crops the cover to the centre 3:4 (1080×1440, y 240–1680). Keep the title, the big word and the face inside it.

## Background
- One soft pastel colour per video: peach, mint, powder blue, blush pink, or a new pastel that suits the topic.
- Lighter towards the centre (soft radial glow); no texture, no clutter.
- A thin glowing white curved line (arc/swoosh) behind the person.

## Typography (three layers, top to bottom)
1. **Title**: elegant high-contrast serif (Didone style: Playfair Display / Bodoni Moda), bold, in a dark shade of the background colour (deep brown on peach, dark teal on mint, navy on blue, burgundy on pink). 1–3 words of the video's topic.
2. **Subtitle**: small text centred between two thin horizontal rules, same dark tone. E.g. "— Skill with AI?? —", "— TOOLKIT —", "— Worth it? —".
3. **Big word**: one huge, condensed high-contrast serif word in a light tint of the background colour, sitting behind the person (the person overlaps its lower part). E.g. "INSANE", "2026", "FLASH".

## Logos (optional)
- Logos at the very top, centred, separated by a thin vertical rule (e.g. Claude | ElevenLabs). Keep them large enough to read at a glance (~100px tall on the 1080×1920 canvas).
- Use the tools or AI search/LLM platforms the video actually covers: ChatGPT, Perplexity, Gemini, Google AI Overviews, Claude, the PPCBlogPro extension, and so on. Official logo files only.

## Person
- Clean background-removed cut-out of Vaibhav, waist-up, centred, anchored to the bottom edge, smiling at camera, with a gesture (pointing, hand on chest, arms crossed).
- Outfit colour ideally matches the background colour (monochrome look). Soft, natural shadow; no hard outlines or strokes.
- Use studio-quality photos from his photo set; video frames are a fallback only.

## Per-video inputs
Title, subtitle, big word, background colour, photo, logos. Everything else stays fixed.

## How to make one
1. Background-removed photo: `python3 thumbnails/cutout.py <photo.jpg> thumbnails/assets/<name>_cutout.png` (works for plain white/light backdrops).
2. Logos go in `thumbnails/assets/logos/` (official files only; current set from the `simple-icons` and `@lobehub/icons-static-svg` npm packages).
3. Write `thumbnails/<video>/config.json` (theme: blue / peach / mint / pink / lavender; title; subtitle; big_word; logos; photo) and run
   `python3 thumbnails/render.py thumbnails/<video>/config.json` to write `cover.png` (1080×1920).
