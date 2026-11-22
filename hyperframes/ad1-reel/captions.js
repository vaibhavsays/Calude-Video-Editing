// Hinglish subtitles (Roman script only), short punchy groups. Times are on the ORIGINAL (raw/ad1.mp4) clock; T()
// maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length.
// *word* = highlighted.
const SEGMENTS = [
  [0.29, 3.43, "*Hello business owners*, | toh kya aap bhi chahte hain ki | *ChatGPT*, *Google AI Overviews*"],
  [3.46, 6.11, "mein aapka *business* aaye | aur zyada se zyada | *customers* aap tak pahunchein?"],
  [6.72, 8.23, "Toh *rukiye!* | Mera naam"],
  [8.23, 9.50, "*Vaibhav* hai, | aur main"],
  [9.91, 13.27, "pichhle *5 saalon* se *SEO* kar raha hoon, | aur ab tak maine | *kai businesses* ko"],
  [13.68, 17.61, "Google par *online visibility* badhane | aur *naye customers* | tak pahunchne mein"],
  [17.84, 21.26, "unki help ki hai. | Jaise kuch businesses: | *e-commerce*, *products*, *services*,"],
  [21.61, 25.74, "*B2B*, *B2C*, *D2C*. | Aur projects ki baat karein toh | *VCL*, *Shree Radhey*,"],
  [26.00, 29.52, "*Zussio Berry* aur kuch | *international projects* | jaise ki"],
  [30.13, 32.22, "*Charcoal Factory*, | *Friendly Bamboo*, *Oakalleng*"],
  [32.46, 35.21, "aur *Party Sparkz*. | Aur in saare businesses ko"],
  [35.35, 36.58, "*Google AI Overviews* mein | *cite* kiya gaya hai"],
  [36.99, 39.98, "aur *mention* kiya gaya hai. | Kyunki aaj *buyers* Google par | sirf search nahi karte,"],
  [40.19, 43.93, "wo *ChatGPT*, *AI Overviews* aur *Gemini* mein | direct poochhte hain | *best service* kaun si hai,"],
  [44.36, 48.12, "kis company ki. | Aur hum businesses ko | *AI Overviews* aur *ChatGPT* jaise"],
  [48.46, 51.22, "*AI search engines* par | *visible* hone mein | help karte hain."],
  [51.24, 54.87, "Aur agar aap bhi apne business ke liye | *AI SEO expert* dhoondh rahe hain, | jo aapki help kare"],
  [54.87, 58.22, "business ko *AI Overviews* | aur *AI search engines* | mein laane mein,"],
  [58.74, 61.55, "toh main aapki *help* kar sakta hoon. | Neeche *button* pe click karein | aur *strategic call* book karein."],
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
