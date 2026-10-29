// Hinglish subtitles (Roman script only). Times are on the ORIGINAL (uploaded timeline) clock; T() maps them onto
// the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length. *word* = yellow box.
const SEGMENTS = [
  [0.05, 2.90, "*Negative reviews* are killing | your website's *AI recommendations*."],
  [3.00, 6.45, "Sirf *2 negative reviews* | aapki website ko | *AI recommendations* se bahar kar sakte hain."],
  [6.60, 9.80, "Okay, so welcome to *Day 5* | of 100 Days of *Decoding AI SEO*."],
  [9.84, 13.11, "Toh *AI search engines* | aapki *website* aur aapke *content* ke saath-saath"],
  [13.11, 16.39, "ye bhi dekhte hain | ki *internet* pe | aapke baare mein kya chal raha hai,"],
  [16.39, 19.37, "*third-party validation* se, | jaise ki *Reddit*, *Quora* mein."],
  [19.37, 21.09, "Theek, *review management* | toh hai hi,"],
  [21.09, 25.40, "aapke baare mein | kya *baatein* ho rahi hain, | aapke *business* ke baare mein | wo saari cheezein dekhta hai."],
  [25.58, 28.16, "Agar aapke business ke | *reviews bekaar* hain,"],
  [28.16, 30.75, "aapke business ke | *third-party validations*, matlab"],
  [30.75, 34.32, "wahan aapka *content bekaar* hai. | Jaise humne *last videos* mein | baat ki thi,"],
  [34.32, 37.98, "*schema* ki baat ki thi, | *third-party validations* | ki baat ki thi."],
  [37.98, 41.78, "Aur *parasite SEO*, let's say, | alag cheez hai, | wo hum *next video* mein dekhenge."],
  [41.78, 44.15, "Third-party validation mein | *reviews* aate hain,"],
  [44.15, 47.87, "*review management*, | *parasite SEO* aa jaata hai, | *community forums* aa jaate hain."],
  [47.87, 53.28, "Aur ye saari cheezein uthakar | AI ek *general answer* banata hai | aur *decide* karta hai"],
  [53.28, 56.10, "ki aapki website ko | *AI search engines* mein | *recommend* kare ya na kare."],
  [56.15, 61.21, "Toh *reviews* bahut important hain, | ye ek *deciding call* hai | ki aapki website,"],
  [61.21, 66.10, "aapka *business content*, | aapki *business website* | *AI search engines* mein | *recommend* hogi ya nahi."],
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
