// Hinglish subtitles (Roman script only), short punchy groups like the reference. Times are on the ORIGINAL
// (raw/nov3.mp4) clock; T() maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its
// time by text length. *word* = highlighted.
const SEGMENTS = [
  [0.05, 2.50, "Generally log | *backlinks* | *bulk* mein banate hain."],
  [2.60, 4.85, "Generally log kya karte hain? | *backlinks* banate hain,"],
  [4.95, 7.35, "toh bas *SBM*, | *classifieds*, | *profiles*."],
  [7.45, 9.80, "Par aisa nahi hota, | ek *format* hota hai."],
  [9.95, 12.05, "Humein decide karna hota hai | *tier 1*, *tier 2* | aur *tier 3*."],
  [12.64, 15.40, "*Tier 1* mein aati hain | hamari *guest posts* | aur *PR submissions*,"],
  [15.92, 17.80, "phir aati hain | hamari *business listings*."],
  [18.17, 21.99, "Phir *tier 2* mein | aate hain"],
  [22.39, 26.43, "hamare *SBM*, | hamari *profiles*, | hamare *classifieds*."],
  [26.82, 29.38, "Aur *tier 3* mein aati hain"],
  [29.74, 32.57, "hamari *PDF submission*, | *video submission*, | *image submission*."],
  [32.97, 36.15, "Kyunki *Google* ne | saare tiers define kiye hain | on the basis of *content*."],
  [36.46, 38.10, "Comment *BACKLINKS*"],
  [38.10, 40.30, "aur main aapko directly | DM mein bhejunga | complete *backlink hierarchy*."],
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
