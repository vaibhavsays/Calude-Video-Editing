// Hinglish subtitles (Roman script only), short punchy groups. Times are on the ORIGINAL (raw/nov6.mp4) clock; T()
// maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length.
// *word* = highlighted.
const SEGMENTS = [
  [0.18, 1.74, "Aapne abhi | haal-filhaal mein,"],
  [2.37, 4.95, "pichhle ek-do mahine mein | ek naya word suna hoga: | *GEO*."],
  [5.31, 8.37, "*SEO* aur marketing mein, | jiska matlab hai | *Generative Engine* | *Optimization*."],
  [9.35, 11.10, "Ab Generative Engine Optimization | hota *kya hai*?"],
  [11.46, 15.15, "Welcome to *Day 6* | of 100 Days of | *Decoding AI SEO* | with Vaibhav."],
  [16.09, 19.39, "Ab baat aati hai, | *SEO* aur *GEO* mein | *difference* kya hai? | Simple hai."],
  [19.83, 24.42, "*SEO* matlab | *Search Engine Optimization*, | jahan hum *Google*, *Bing* pe | kuch search karte the"],
  [24.78, 26.73, "aur ye *blue links* pe | redirect karte the."],
  [27.18, 29.44, "Toh wo tha | *Search Engine Optimization*."],
  [29.44, 31.36, "Aur *GEO* ka matlab hai | *Generative Engine Optimization*,"],
  [31.49, 33.81, "yahan pe hum | *AI search* pe kaam karte hain."],
  [34.22, 35.42, "Apne liye | ya *clients* ke liye,"],
  [35.78, 38.80, "as a professional, | hum clients ke liye | is pe *zyada kaam* karte hain."],
  [39.13, 42.12, "Jaise *ChatGPT*, | *Gemini*, *DeepSeek*,"],
  [42.26, 46.29, "*Perplexity*, yahan aap | koi bhi *long-form* ya | *short-form* query search karte ho"],
  [46.74, 48.64, "aur aapko *direct answer* | generate hoke milta hai."],
  [49.28, 53.10, "So *save this reel* | so that you never forget | the difference between | *SEO* and *GEO*."],
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
