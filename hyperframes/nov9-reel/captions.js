// Hinglish subtitles (Roman script only), short punchy groups. Times are on the ORIGINAL (raw/nov9.mp4) clock; T()
// maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length.
// *word* = highlighted.
const SEGMENTS = [
  [0.55, 2.69, "Agar aapne apne business ka | *Google Business Profile* banaya hai,"],
  [3.12, 5.35, "par wo *AI search engines* pe | recommend *nahi* ho raha,"],
  [5.64, 6.62, "toh ye video | *aapke liye* hai."],
  [7.33, 11.79, "Aapki *service*, aapka *product*, | aapke *local area* mein | jo bhi search karte hain,"],
  [12.00, 13.70, "specifically | *AI search engines* pe,"],
  [14.22, 16.76, "aaj AI search engines | sirf aapki *website* nahi, | balki aapki"],
  [16.90, 19.29, "*Google Business Profile* ko bhi | *recommend* karte hain."],
  [19.99, 22.53, "Agar search aapki | *locality* mein ho rahi hai,"],
  [22.67, 25.46, "aapke *nearby area* se, | toh wo aapko | *recommend* kar degi. But"],
  [25.97, 27.85, "agar aapne apni *GMB* pe | kaam nahi kiya, jaise ki"],
  [28.07, 30.30, "aapke *reviews*, | *negative reviews*,"],
  [30.71, 33.43, "reviews ke jo *replies* jaa rahe hain, | wo *keyword optimized* | hone chahiye properly."],
  [33.79, 37.07, "Aapki *new* aur *updated images*, | *videos* honi chahiye, | *products* ke liye,"],
  [37.20, 39.21, "aapki *services* ke liye. | Aur iske saath"],
  [39.47, 43.72, "aapki GMB pe *posts* honi chahiye, | wo bhi har *week* mein, | *regular* posts."],
  [44.09, 47.55, "Isse kya hota hai? | Jo *trending keywords* hain, | unko cover kar paate hain,"],
  [47.85, 50.76, "taaki aapki | saari cheezein | *updated* rahein."],
  [51.09, 53.53, "Uske baad ye aapki *GMB* ko | *recommendation* mein daalta hai."],
  [54.01, 57.95, "Toh basically agar aap chahte hain | ki aapki GMB | *AI search engines* pe recommend ho,"],
  [58.26, 61.64, "toh aapko ye saare *points* | bilkul *yaad* rakhne padenge."],
  [63.37, 66.43, "Okay, so agar aap chahte ho | ki aapka business | *AI search* pe recommend ho,"],
  [66.83, 69.36, "comment karo apna | *business name*, | aur main aapko bhejunga"],
  [69.74, 71.73, "*GMB optimization* ki | poori *checklist*, so that"],
  [71.86, 73.72, "aapka business bhi | *AI search engines* pe | recommend ho."],
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
