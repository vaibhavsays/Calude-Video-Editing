// Speech segments (from silence detection on the original audio) and what is said in each.
// "|" splits a segment into on-screen phrases; phrases share the segment's time by text length.
// *word* = yellow highlight. A segment with deva:true is shown in Devanagari.
const SEGMENTS = [
  [0.05, 1.57, "क्या आपका बिज़नेस", { deva: true }],
  [1.71, 2.22, "*visible* hai"],
  [2.47, 4.30, "*ChatGPT*, *Gemini* | aur AI search engines pe?"],
  [4.85, 9.78, "Agar aapke shehar mein | koi aapke business ko | AI searches mein | search karta hai | toh kya aapka business | *recommend* hota hai?"],
  [10.41, 13.12, "Welcome to *Day 1* | of 100 Days of | Decoding *AI SEO* | with AISEO.Vaibhav"],
  [13.89, 16.79, "Maximum business owners | ko lagta hai ki | agar unke business ki | *website* ban gayi"],
  [17.17, 17.81, "तो काम ख़तम!", { deva: true }],
  [18.11, 19.94, "लेकिन ऐसा नहीं होता", { deva: true }],
  [19.94, 22.30, "*AI visibility* mein | aane ke liye | AI ke paas aapke business | aur website ka"],
  [22.30, 25.04, "*proper data* hona chahiye | aur agar wo data | uske paas nahi hai"],
  [25.49, 26.46, "toh wo aapke *competitors* ko"],
  [26.80, 27.42, "*recommend* karta hai"],
  [27.80, 30.99, "Aur wo data | AI tak pahunchane | ke liye"],
  [31.28, 33.17, "properly apne *keywords* | pe kaam karna padta hai"],
  [33.72, 35.84, "aur *visibility* pe | kaam karna padta hai"],
  [36.02, 37.50, "*brand* ki | *AI visibility* pe!"],
];

SEGMENTS.forEach(([s, e, text, opts]) => {
  const phrases = text.split("|").map((p) => p.trim());
  const lens = phrases.map((p) => p.replace(/\*/g, "").length + 4);
  const total = lens.reduce((a, b) => a + b, 0);
  let t = s;
  phrases.forEach((p, i) => {
    const d = (e - s) * lens[i] / total;
    CUES.push([t, i === phrases.length - 1 ? e + 0.15 : t + d, p, opts || {}]);
    t += d;
  });
});
