# Calude-Video-Editing

Short-form video editing (9:16 Reels/Shorts). Source footage lives in `raw/`, finished renders in `output/`.

## Tools
- **HyperFrames** (`hyperframes/`): HTML + GSAP compositions rendered to MP4. Default for new edits. Skills are in `.claude/skills/` (start with `/hyperframes`; `/talking-head-recut` for overlays on talking-head footage, `/embedded-captions` for captions, `/motion-graphics` for short graphics). Projects are folders under `hyperframes/`, e.g. `hyperframes/ai-seo-day1/`.
- **Remotion** (`broll/`): the AI SEO Day 1 B-roll edit. Re-render with `broll/render.sh`.
- **FFmpeg** is installed system-wide.

## Thumbnails
- Every Instagram Reel gets a cover in the standard style in `thumbnails/STYLE.md` (reference: `thumbnails/style_reference.webp`). Follow it exactly; only the per-video inputs change.
- Only make a thumbnail when the user asks for one.

## Environment gotchas (cloud sessions)
- The network blocks `cdn.jsdelivr.net`, Google Fonts' file host as seen by Chrome, and Hugging Face. Load GSAP from `vendor/gsap.min.js` (copy from `hyperframes/node_modules/gsap/dist/`), and bundle fonts locally (see `broll/public/fonts/`), never from a CDN.
- Transcription (`hyperframes transcribe`, Whisper) needs model downloads from Hugging Face, which is blocked. Read burned-in subtitles from frames, or ask the user for an `.srt` file.
- Keep quality: lay graphics over the untouched original and encode once, at CRF 15 or lower. Never render the footage through JPEG frame capture.

## Look & sound (user's standing brief, every video)
- Skin must look natural, never red/orange. Neutralise white balance off a white/grey surface (the iPhone footage runs warm), no saturation or vibrance boost, slight contrast, brighter mids, lifted (not muddy) shadows. Reference grade: `GRADE` in `hyperframes/content-tier-list/composite.py`.
- Light denoise + gentle sharpening only; no motion blur, no compression artifacts.
- Voice crisp and front-and-center: denoise static/hiss, tame room echo (gentle gate), cut boxiness, a little presence, ~-14 LUFS.
- Professional, stable talking-head framing for Reels/YouTube.
- Chat file uploads are limited to 30 MB.
