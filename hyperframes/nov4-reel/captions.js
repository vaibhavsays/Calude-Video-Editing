// Hinglish subtitles (Roman script only), short punchy groups. Times are on the ORIGINAL (raw/nov4.mp4) clock; T()
// maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length.
// *word* = highlighted.
const SEGMENTS = [
  [1.64, 2.12, "*Schema*."],
  [2.57, 4.75, "Schema is definitely | in *S tier*, because"],
  [4.81, 7.88, "schema aapki *website* ko | help karta hai"],
  [8.24, 12.54, "aapka *content read* karne mein | *AI search engines* ko | aur content ko *recommend* karne mein."],
  [13.46, 14.43, "*Digital PR*."],
  [14.64, 16.00, "Digital PR is again | in *S tier*,"],
  [16.23, 20.00, "kyunki digital PR | ek *tier 1 backlinks* process hai,"],
  [20.40, 22.45, "jo ki ek | *third-party validation* bhi hai."],
  [23.30, 24.45, "*Internal linking*."],
  [24.47, 26.74, "Internal linking is again | in *B tier*."],
  [26.74, 28.87, "Internal linking aapko | ek tarah se batati hai,"],
  [29.39, 33.29, "*crawlers* ko, ki aapke pages | *internally connected* hain."],
  [34.86, 36.07, "*Alt text tags*."],
  [36.07, 38.20, "Alt text tags | will be in *C tier*,"],
  [38.20, 42.02, "kyunki ye aapki ranking mein | help nahi karte, bas aapki | *image ranking* increase karte hain."],
  [43.00, 44.74, "*FAQ on product* pages."],
  [44.74, 47.07, "FAQ on product | will be in *A tier*,"],
  [47.07, 51.46, "kyunki FAQs aapke *product pages* | ko help karte hain | *AI crawlers* se read karwane mein."],
  [52.03, 53.16, "*Merchant Center*."],
  [53.16, 54.78, "Merchant Center | would be in *S tier*."],
  [55.57, 57.57, "*Meta description*."],
  [57.57, 59.98, "Itna important nahi hai, | ye jaayega *C tier* mein, | kyunki"],
  [59.98, 62.14, "*Google* aapka meta description | khud *rewrite* kar deta hai."],
  [62.66, 65.18, "*Guest posting* | would be in *A tier*"],
  [65.18, 67.63, "because guest posting | is again *third-party validation*."],
  [68.33, 69.37, "*Product reviews*."],
  [69.37, 71.42, "Product reviews | would be in *S tier*, because"],
  [71.42, 75.30, "product reviews se hi *Google* | aur *crawlers* ko pata chalta hai"],
  [75.74, 78.97, "aur aapki *target audience* ko | ki aapka product | *loyal aur trustable* hai ki nahi."],
];

SEGMENTS.forEach(([s, e, text]) => {
  const phrases = text.split("|").map((p) => p.trim());
  const lens = phrases.map((p) => p.replace(/\*/g, "").length + 4);
  const total = lens.reduce((a, b) => a + b, 0);
  let t = s;
  phrases.forEach((p, i) => {
    const d = (e - s) * lens[i] / total;
    CUES.push([T(t), T(i === phrases.length - 1 ? e + 0.1 : t + d), p]);
    t += d;
  });
});
