// Hinglish subtitles. Times are on the ORIGINAL (uploaded timeline) clock; T() maps them onto the tight cut (edl.js).
// "|" splits a segment into phrases sharing its time by text length. *word* = yellow box.
// 5.92-9.21 ("Welcome to Day 4...") has no caption: the intro title says it.
const SEGMENTS = [
  [0.05, 2.27, "Okay, toh *ChatGPT* aur | other *AI search engines*"],
  [2.27, 4.28, "aapke *business* ko | *recommend* kyun nahi kar rahe?"],
  [4.81, 5.90, "Did you ever think | about that?"],
  [9.25, 12.30, "Toh dekho, reasons | bilkul *simple* hain, | mainly *3 reasons* hain"],
  [12.60, 14.00, "aur *third one* is | really important."],
  [14.10, 18.02, "Toh aapka *first reason* ye hai | ki agar aapne apni website ki"],
  [18.02, 23.35, "*robots.txt* files mein | apne *AI crawlers* ko | *allow* nahi kiya hai, | matlab *disallow* kiya hua hai,"],
  [23.83, 29.05, "toh wo aapka *content read* | nahi kar paayenge. | Aur agar wo read nahi kar paa rahe, | toh *recommend* bhi nahi kar paayenge."],
  [29.44, 35.65, "So always make sure | ki aapke *AI crawlers* | always and always | *allowed* hon | aapki *robots.txt* file mein."],
  [35.75, 37.08, "*Second reason* hai"],
  [37.58, 41.37, "*third-party validation*. | Third-party validation | se mera matlab hai ki"],
  [41.37, 43.55, "aapki *website* aur | aapke *business* ke baare mein"],
  [44.14, 46.95, "*other websites* pe bhi | *discussions* ho rahe hain ya nahi,"],
  [47.36, 49.86, "*Quora* pe, *Reddit* pe, | *reviews* mein,"],
  [49.86, 52.70, "*communities* mein | aapke baare mein | kya baat ho rahi hai,"],
  [53.10, 54.14, "aur aapke *reviews*."],
  [54.54, 57.79, "*Third-party validation* | is the *most important* thing"],
  [58.25, 61.32, "jo decide karta hai ki | aapka content *recommend* hoga ya nahi | *AI search engines* mein."],
  [61.78, 64.29, "Now *third* and most important: | *machine readability*."],
  [64.29, 69.54, "Machine readability matlab | agar aapki website mein | *structured data*, | matlab *schemas* lage hi nahi hain,"],
  [70.00, 74.89, "kyunki *AI* aapke content ko | *human* ki tarah nahi padhta, | wo padhta hai | *structured data* ki help se."],
  [75.29, 77.97, "Proper *schema markup*:"],
  [77.97, 80.85, "aapka *FAQ schema*, | content *review* aur *rating schema*,"],
  [80.85, 83.23, "aapka *organization*, | *person* aur *author* schema."],
  [83.23, 86.28, "Aapka content | kisi bhi cheez se *related* ho,"],
  [86.28, 89.33, "aapki website mein | *schema* hona chahiye, | chahe kisi bhi"],
  [89.33, 91.61, "kind of website ho, | *Webflow* pe ho,"],
  [91.61, 93.68, "*WordPress* pe ho, | *WooCommerce* pe ho | ya phir"],
  [94.09, 95.80, "*Shopify* pe ho,"],
  [95.80, 97.52, "*schema* bahut | *zaroori* hai."],
  [97.91, 100.38, "Agar *schema* nahi hai, | toh aapka content | *readable* nahi hai."],
  [100.82, 105.63, "Aur *AI search engines* ke liye | apne *AI crawlers* ko | *allow* karke rakhiye."],
  [106.01, 108.20, "So comment *SCHEMA* | and I will tell you"],
  [108.20, 110.95, "aapki website ke liye | *exact schema* | kya zaroori hai."],
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
