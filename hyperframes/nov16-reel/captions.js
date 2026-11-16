// Hinglish subtitles (Roman script only), short punchy groups. Times are on the ORIGINAL (raw/nov16.mp4) clock; T()
// maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length.
// *word* = highlighted.
// No captions between 20.0 and 61.3 s: the GSC results screen is left exactly as recorded (user's request).
const SEGMENTS = [
  [0.28, 2.21, "Zyaadatar *business owners* | ko lagta hai ki"],
  [2.50, 4.69, "*SEO* toh *dead* ho chuka hai, | *performance marketing* best hai,"],
  [4.85, 7.05, "wo spend karte hain, *ads* chalate hain, | *YouTube ads* chalate hain,"],
  [7.18, 8.75, "*display ads* | chalate hain,"],
  [9.19, 11.04, "par wo nahi jaante ki | *SEO ki power* kya hoti hai."],
  [11.68, 13.83, "Aap agar *ads* chalate ho, | *performance marketing* karte ho,"],
  [14.12, 16.20, "toh aapka *ad spend* | itna ho jaata hai ki"],
  [16.34, 18.60, "bas *product ki cost* | nikal paati hai."],
  [18.99, 19.98, "Toh main aapko dikhata hoon | *SEO ki power*."],
  [61.48, 63.49, "Baat hoti hai ki aap | kin *keywords* ko | *target* kar rahe ho."],
  [63.70, 66.23, "Agar ye *trend* mein hai, | toh trend mein isliye hai"],
  [66.37, 69.07, "kyunki hamne | *trendy keywords* ko | target kiya tha."],
  [69.42, 73.30, "Log *exactly kya search* karte hain, | aur yahi *SEO* ka sabse | *important factor* hai,"],
  [73.76, 77.34, "ki hum kin *keywords* ko | target kar rahe hain. | Initially aap *ads* bhi"],
  [77.48, 79.85, "chala loge, | *ads* chala loge,"],
  [80.26, 82.96, "unse *effect* aayega, par | *long-term perspective* | se dekha jaaye toh"],
  [83.08, 86.40, "*SEO* se aapki | *credibility build* hoti hai, | jo *long term* mein fayda deti hai."],
  [86.54, 88.41, "Par *performance marketing* | mein,"],
  [88.82, 90.77, "jab tak *paise* jaa rahe hain, | tab tak hi aap *dikhte* ho."],
  [90.92, 92.55, "Ek baar aapne | *ads band* kar diye,"],
  [92.96, 95.34, "toh phir *SEO ke results* se hi | aap *top* pe dikhte ho."],
  [95.93, 97.14, "*SEO is not dead.*"],
  [97.54, 98.43, "SEO *time leta hai*, | but"],
  [99.05, 102.80, "abhi *khatam nahi* hua hai, | aur ab isme *AI* aa gaya hai, | toh ye aur bhi *important* ho gaya hai."],
  [103.39, 106.27, "So *follow* for more such content | to get your business | *visible in AI search*."],
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
