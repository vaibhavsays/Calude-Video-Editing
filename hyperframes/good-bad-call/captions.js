// Hinglish subtitles (Roman script only), ORIGINAL clock; T() maps onto the tight cut. "|" splits phrases, *word* = yellow box.
const SEGMENTS = [
  [1.40, 2.70, "*Publishing daily content*."],
  [2.80, 4.60, "Publishing daily content | is *not okay*."],
  [4.70, 7.10, "Daily content agar aap publish kar rahe ho, | toh *quality compromise* hoti hai,"],
  [7.20, 11.10, "jabki Google *quality* ko | prioritise karta hai | aur usi ko *recommend* karta hai."],
  [11.50, 16.10, "Agar aap bas isliye *content publish* kar rahe ho | ki aapke *keywords cover* ho jaayein,"],
  [16.60, 20.70, "aur saara content publish karo, | lekin jab *user search* kare | aur aap us *query* pe dikho hi nahi, | toh wo important nahi hai."],
  [22.25, 23.35, "*Service pages*."],
  [23.40, 25.20, "Service page is definitely | a *good call*."],
  [25.30, 30.40, "Agar aap *ek se zyada services* offer karte ho, | toh generally log | *ek hi service page* bana dete hain."],
  [30.50, 36.20, "Sab ek page pe target karte hain, | toh *Google* samajh nahi paata | ki aap *kaunsi service* target kar rahe ho."],
  [36.60, 38.70, "Isliye aapke har *service* ka | *page alag* hona chahiye."],
  [39.95, 41.20, "*Location pages*."],
  [41.25, 43.50, "Location pages are definitely | again a *good call*."],
  [43.60, 48.50, "Agar aap *ek se zyada location* pe operate karte ho, | agar aapka business itna bada hai ki"],
  [48.60, 51.50, "aap *Hyderabad, Chennai, Mumbai*, | different locations pe service dete ho,"],
  [52.00, 57.10, "toh aapke *alag location pages* hone chahiye, | so that aap us location ki | *target audience* ko cover kar sako."],
  [57.80, 60.20, "*Programmatic SEO*."],
  [60.30, 63.10, "Ye *bad call* isliye hai | ki agar aapko koi bhi *keyword* target karna hai,"],
  [63.55, 69.30, "toh programmatic SEO mein | aap *template-based* ek page bana lete ho | aur us page ko"],
  [69.85, 74.95, "har *different keyword* ke saath | add kar dete ho. | Usmein har section | *hamesha same order* mein hota hai."],
  [75.00, 80.10, "Lekin agar aapke *keyword* ka | *intent alag* hai, keyword alag hai, | toh har page *different* hona chahiye,"],
  [80.20, 87.70, "ek *flexible* way mein, | taaki aap kisi bhi page ka section | *upar-neeche* kar sako, | content ke hisaab se."],
  [88.15, 89.90, "Par *programmatic SEO* mein | aap ye nahi kar sakte."],
  [90.70, 91.95, "*AI content*."],
  [92.35, 96.70, "AI content isliye *bad call* hai, | kyunki agar aap *ChatGPT* ya | doosre tools ka content"],
  [96.80, 100.30, "direct *publish* kar rahe ho, | bina koi *extra value* add kiye,"],
  [100.85, 106.40, "toh wo content *index* hi nahi hoga, | aur AI use kabhi | *read* aur *recommend* nahi karega."],
  [106.95, 109.50, "*Internal linking*."],
  [109.60, 114.20, "Internal linking is again | definitely a *good call*."],
  [114.30, 118.80, "Ek bhi page *orphan* nahi hona chahiye. | Agar aapka ek bhi page orphan hai, | toh *Google* use index nahi karega."],
  [122.40, 123.10, "*Backlinks*."],
  [123.15, 129.20, "Backlinks are a *good call*. | Agar backlinks nahi hain, | toh aapki website ke baare mein | koi baat hi nahi ho rahi."],
  [129.40, 132.80, "Isse *third-party validation* | kehte hain."],
  [133.15, 137.10, "Agar aap *tier 1* aur *tier 2* | backlinks bana rahe ho, | matlab *guest posting*,"],
  [137.15, 140.95, "*PR submission*, *digital PR*, | *listings* aur *directories*,"],
  [141.00, 143.40, "toh ye definitely | *good call* hai."],
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
