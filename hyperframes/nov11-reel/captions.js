// Hinglish subtitles (Roman script only), short punchy groups. Times are on the ORIGINAL (raw/nov11.mp4) clock; T()
// maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length.
// *word* = highlighted.
const SEGMENTS = [
  [1.26, 4.86, "Dekho, agar *2026* ke end tak | aap abhi tak | *lambe lambe blogs*"],
  [4.99, 6.76, "likh rahe ho, | *2000, 3000, 4000 words* ke,"],
  [6.96, 9.36, "toh *likhna band karo*, | ye koi nahi padhne wala."],
  [9.98, 12.98, "So welcome to *Day 8* | of 100 Days of | *Decoding AI SEO* with Vaibhav."],
  [13.88, 16.01, "Toh baat aisi hai ki pehle | *word count* badhane se,"],
  [16.44, 19.01, "*keyword stuffing* se | *ranking* mil jaati thi, | but ab aisa nahi hota,"],
  [19.47, 21.29, "kyunki ab hamein | *to-the-point* baat karni padti hai."],
  [21.43, 23.58, "Ye koi *SERP*, | *Google search* ka"],
  [23.89, 26.33, "khel nahi hai, | ye *AI search engines* ka khel hai."],
  [26.50, 28.48, "Wo unhi ko *ranking* dete hain, | unhi ko *recommend* karte hain"],
  [28.95, 31.43, "jo *to-the-point* baat karte hain, | bilkul *point-to-point*."],
  [32.00, 33.57, "Agar koi | *marz ki dawa* poochh raha hai,"],
  [34.12, 35.65, "toh *dawa* batani hai, | na ki poora"],
  [36.01, 38.65, "*hospital* khol ke | baith jaana hai."],
  [39.05, 42.52, "Aapse agar koi service ki *cost* | poochh raha hai, | service ke *benefits* poochh raha hai,"],
  [42.82, 44.80, "toh aapko | *to-the-point* baat karni hai."],
  [44.94, 46.74, "Agar *blog* mein karni hai | toh blog mein,"],
  [47.20, 50.10, "*service pages* pe, | *to-the-point* baat karni hai."],
  [50.26, 52.64, "So *follow* for more | *AI SEO tips*."],
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
