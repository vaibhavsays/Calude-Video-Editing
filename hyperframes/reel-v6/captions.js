// Hinglish subtitles for the kept takes. Times are on the ORIGINAL (uploaded timeline) clock; T() maps them onto
// the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length. *word* = yellow box.
const SEGMENTS = [
  [0.00, 4.43, "Toh agar aap bhi ek aise | *business owner* hain | jo agencies ya freelancers ko"],
  [4.92, 7.68, "hazaaron, *40-50 hazaar* | jaise amount pay kar rahe hain,"],
  [7.96, 10.91, "but still aapki *calls* aur *leads* | *zero* hain, | toh ye video aapke liye hai."],
  [11.12, 14.24, "Welcome to *100 Days* of | Decoding *AI SEO*"],
  [14.70, 17.43, "Dekho, generally kya hota hai ki | koi bhi agency ya freelancer"],
  [17.64, 20.00, "aise keywords pe kaam karta hai | jisse *traffic* show kar sake."],
  [20.64, 23.71, "Proper funnels hote hain: | *top of the funnel*, | *middle* aur *bottom* of the funnel."],
  [24.36, 28.67, "Wo generally target karte hain | *top of the funnel* keywords,"],
  [28.96, 31.95, "jaise *what, how, when*: | question-based keywords."],
  [32.26, 37.73, "Unse *traffic* toh le aate hain, | par unse *leads* | aur *conversions zero* hote hain."],
  [44.81, 48.62, "Aapko bhi ek *question* karna hai | ki is traffic se"],
  [49.20, 53.41, "kya hamari *leads convert* ho rahi hain? | Kya *calls* aa rahe hain | hamare business ke liye?"],
  [90.96, 96.13, "Agar is traffic se *leads* nahi aa rahi, | ya leads aa rahi hain | par *qualified* nahi hain,"],
  [96.55, 99.60, "*qualified traffic* nahi hai, | toh wo marketing | wahin *band* karwa deni chahiye."],
  [142.41, 147.11, "Toh hamesha khud se poochiye: | kya hum bas *top of the funnel* | keywords pe ja rahe hain"],
  [147.89, 150.17, "ya *middle* ya *bottom* of the funnel pe?"],
  [150.33, 155.20, "Example ke liye, | agar aap koi *phone* ya bike | purchase karne jaate ho"],
  [155.39, 160.79, "toh directly purchase nahi karte. | Pehle proper *enquiry* karte ho"],
  [161.14, 164.90, "ki ye cheez kaisi hai, | ye kya hai."],
  [165.37, 168.93, "Toh ye mera *top funnel* ho gaya."],
  [169.08, 176.49, "Phir *middle funnel* mein search karunga: | *iPhone vs Samsung*, | *Vivo vs Oppo*,"],
  [176.88, 180.45, "ya inki *specifications*: | battery life, camera quality."],
  [180.81, 185.49, "Phir middle se *bottom* pe aaunga: | iski *price* kya hai, | *price comparison*,"],
  [185.65, 188.97, "yaani *conversion-based*, | *transactional* keywords."],
  [189.47, 191.99, "Toh ye saare keywords hote hain | proper *funnel-wise*."],
  [192.37, 197.09, "Agar aapko apni website ke liye | proper *keyword research* chahiye,"],
  [197.56, 200.84, "reel *share* kijiye, comment kijiye *KEYWORD*, | main bhejunga research | *personalised* to your brand."],
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
