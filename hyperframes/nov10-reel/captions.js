// Hinglish subtitles (Roman script only), short punchy groups. Times are on the ORIGINAL (raw/nov10.mp4) clock; T()
// maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length.
// *word* = highlighted.
const SEGMENTS = [
  [1.15, 4.36, "Last video mein humne | baat ki thi | *SEO* aur *GEO* ke baare mein."],
  [4.48, 6.69, "Is video mein | *AEO* aur *GEO*,"],
  [6.85, 8.19, "jiska matlab hai | *Answer Engine Optimization*"],
  [8.85, 9.89, "aur *Generative Engine* | *Optimization*."],
  [10.64, 12.68, "*Answer Engine Optimization* | ka matlab hota hai ki"],
  [13.01, 16.34, "jaise koi bhi *query* | aap search karoge, | aapko *Google AI Overviews* mein,"],
  [16.47, 18.91, "*voice search* mein, | ya phir *featured snippets* mein"],
  [19.05, 20.79, "*direct answers* | mil jaate hain."],
  [22.16, 23.50, "Aur iska | *exact opposite*,"],
  [23.79, 26.20, "*Generative Engine Optimization* | ka matlab hota hai ki"],
  [26.36, 28.05, "jaisa humne last video mein | baat ki thi,"],
  [28.37, 30.26, "*ChatGPT* hoga, | *DeepSeek* hoga, | *Perplexity* hoga,"],
  [30.73, 32.57, "wahan pe wo hamein | ek *answer generate* karega"],
  [32.71, 36.49, "alag alag *websites* se | answer utha utha ke."],
  [36.67, 38.62, "Toh ye hai | *basic difference*"],
  [38.74, 40.52, "*AEO* aur *GEO* | ke beech mein."],
  [41.20, 42.77, "But ye dono | *kaam kaise* karte hain?"],
  [42.91, 44.55, "*Answer Engine Optimization* | mein aapko"],
  [44.84, 46.38, "*to-the-point* | *direct answers* likhne padte hain."],
  [46.51, 48.22, "Aapne dekha hoga, | koi bhi search karo,"],
  [48.93, 50.99, "toh *Google AI* | aapko wo *answer* dikhata hai."],
  [51.18, 52.98, "Toh hamein apne | *business* ke liye"],
  [53.14, 54.46, "aise hi *answers* | likhne padte hain,"],
  [54.58, 57.33, "taaki jab *crawler* | inhe read karta hai,"],
  [57.69, 59.31, "toh wo inhe | *direct answer* ki tarah | show kar sake."],
];

SEGMENTS.forEach(([s, e, text]) => {
  const phrases = text.split("|").map((p) => p.trim());
  const lens = phrases.map((p) => p.replace(/\*/g, "").length + 4);
  const total = lens.reduce((a, b) => a + b, 0);
  let t = s;
  phrases.forEach((p, i) => {
    const d = (e - s) * lens[i] / total;
    CUES.push([T(t), T(i === phrases.length - 1 ? e : t + d), p]);
    t += d;
  });
});
