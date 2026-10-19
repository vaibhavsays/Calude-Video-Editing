// Hinglish subtitles on the speech segments (silence detection). "|" splits a segment into phrases that share
// its time by text length. Times are on the ORIGINAL clock; T() maps them onto the tight cut (edl.js).
// *word* = yellow highlight box (multi-word: *a b*).
const SEGMENTS = [
  [0.31, 3.24, "Agar aapko bhi lagta hai ki | *AI* aapke content ko | *punish* kar raha hai"],
  [3.38, 5.00, "ya AI search engines, | toh ye video aapke liye hai"],
  [5.64, 8.17, "Chaliye dekhte hain | ki *AI search engines*"],
  [8.46, 10.95, "aur search engines | aapke content ko | *kyun punish* karte hain"],
  [11.31, 15.61, "Chahe wo *AI search engine* ho, | *Google* ka search engine ho | ya *Bing* ka search engine ho"],
  [15.97, 20.75, "ye aapke *AI content* ko | isliye punish karta hai | kyunki aap AI se content likhwa ke"],
  [21.13, 23.88, "as it is *draft* karke | *publish* kar dete ho. | Par aisa nahi hota."],
  [24.23, 30.79, "Agar aapke content mein | proper *E-E-A-T* algo | follow nahi hua, | toh aapka content kabhi *rank* nahi hoga, | kabhi *AI visibility* mein | nahi aane wala."],
  [31.25, 34.00, "E-E-A-T ka matlab hai | *Expertise, Experience,* | *Authority, Trust*"],
  [34.36, 38.63, "Suppose aap koi content le rahe ho, | aur hum baat karte hain | kisi *doctor* ki"],
  [38.97, 43.35, "aise content ki | jismein *health issues* | ya health ki baat ho rahi hai"],
  [43.71, 49.68, "Ab agar ek *doctor* | content likhega, | toh apne *perspective* se likhega, | apne *experience* se likhega, | apni *expertise* se likhega"],
  [51.07, 53.59, "Dusri taraf agar | koi *content writer* likhta hai"],
  [53.99, 58.80, "toh wo bas ye sochega | ki ye content likhwa lunga | *ChatGPT* se, *Claude* se"],
  [60.45, 61.00, "kisi bhi tool se, right?"],
  [61.42, 65.94, "Hamein yahi karna hota hai | ki agar hum kisi bhi tool se | apna content likhwa rahe hain"],
  [66.34, 71.18, "toh usmein apni *expertise* | aur *experience* | show karna padta hai, | chahe apne *client* se poochein"],
  [71.54, 74.05, "ya hamari *website* se | kuch ideas lein"],
  [74.34, 78.21, "kisi directory se, | kisi aur website se, | *Reddit* se, *Quora* se, | kaise bhi lein"],
  [78.62, 83.09, "par aapko ye cheez | *show* karni padegi, | warna aapka content | kabhi *rank* nahi hone wala"],
  [83.43, 86.54, "Aur isliye maine ek | complete *SOP guide* banayi hai"],
  [86.85, 93.79, "jo har ek *niche* ke | blogs ke liye applicable hai. | Agar aapko SOP chahiye, | toh comment karo *SOP*, | main directly aapke *DMs* mein bhej dunga"],
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
