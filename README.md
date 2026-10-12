# Calude-Video-Editing

Video editing project.

## AI SEO Day 1: B-roll and motion graphics

- `raw/main.mp4`: the original edit.
- `output/AI_SEO_Day1_broll.mp4`: the original with five full-screen B-roll inserts. The original audio is unchanged.
- `broll/`: the Remotion project that builds the inserts (`broll/src/Main.tsx`).

| Time | Spoken line | Insert | Reference style |
|---|---|---|---|
| 1.0–2.4s | "website hai aur aapka business" | Website hai, aur Business bhi | White minimal, floating cards |
| 3.2–4.5s | "AI search me visible nahi hai" | "visible" flickers out | Black kinetic type |
| 15.5–18.4s | "ChatGPT, AI Overviews and Perplexity" | Glowing icon ring, lights up as each is named | Purple neon icons |
| 22.2–23.4s | "even according to Google, daily 100M+" | Google + AI search bar | Grey grid, hero object |
| 26.25–30.05s | "agar aapka business AI searches me visible nahi hai, to aap game me bahut peeche ho" | AI answer recommends competitors and not your business, then an "AI visibility race" with your business at #47, then "bahut PEECHE" | Dark/red, lime vs red |

To re-render:

```bash
cd broll
npm install
npm run setup
npm run render -- --browser-executable=<path to chrome-headless-shell>
```
