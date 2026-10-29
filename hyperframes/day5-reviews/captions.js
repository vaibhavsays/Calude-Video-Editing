// Hinglish subtitles (Roman script only). Times are on the ORIGINAL (uploaded timeline) clock; T() maps them onto
// the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length. *word* = yellow box.
const SEGMENTS = [
  [0.64, 5.00, "Kya aapka *business* | *ChatGPT*, *Google AI Overviews* | jaise AI generative engines mein dikhta hai?"],
  [5.37, 9.30, "Agar nahi, toh chaliye | ye pata karne ka | *simple, effective* aur *free* tareeka batata hoon."],
  [10.08, 14.20, "Dekho, waise toh market mein | already bahut saare *tools* hain | jo aapko *report export* karke de sakte hain,"],
  [14.58, 18.25, "jaise *Ahrefs*, *Semrush*. | Lekin unke saath | *teen major problems* hain."],
  [18.65, 20.37, "Pehla toh, wo tools | *paid* hain."],
  [20.58, 23.90, "Doosri baat, wo *sign-up* lete hain, | jisse aapki *information* | dusron ke saath *share* ho jaati hai,"],
  [24.30, 25.30, "jo aap karna nahi chahte."],
  [25.53, 29.62, "Teesri baat, wo *bahut zyada time* lete hain"],
  [30.05, 32.18, "aapko *real AI visibility report* | dikhane mein."],
  [32.62, 35.79, "Aur isi jagah mujhe | ek *free AI tool* mila hai"],
  [36.20, 39.20, "jismein na aapko *sign-up* karna hai, | na aapko *paise* dene hain,"],
  [39.53, 44.22, "jo mushkil se *2 minute* leta hai | aur poori *AI visibility report* | aapke saamne rakh deta hai."],
  [44.94, 47.76, "Toh aapko simply | is *AI tool* pe aa jaana hai"],
  [48.11, 52.54, "aur yahaan pe aake | apni *website paste* kar deni hai | aur *Audit my website* pe jaana hai."],
  [52.98, 55.40, "Aur yahaan pe aapko | *30 to 90 seconds* mein | poori report mil jaayegi,"],
  [55.60, 58.21, "jabki *other tools* | *15 se 20 minute* lete hain."],
  [59.42, 62.72, "Aapka *AI crawler access* | hai ya nahi,"],
  [63.08, 66.71, "*answer-ready content* hai ya nahi, | *structured data* sirf *74%* hai,"],
  [67.14, 70.44, "*trust & credibility*, | *technical health*, | *brand entity*:"],
  [70.70, 74.58, "ye cheezein bahut zyada *important* hain | aapki *AI search visibility* | laane mein."],
  [74.95, 77.21, "Inke bina | koi bhi *AI search engine* | aapko recommend nahi karega."],
  [77.55, 81.79, "Lekin agar aapko *poori report* chahiye, | toh yahaan pe | apni details daal dijiye."],
  [82.16, 87.98, "Koi *sign-up* nahi karna. | Ye information sirf isliye li jaati hai | taaki ye *AI tool* aapki website ko | properly *audit* kar sake"],
  [88.37, 91.65, "aur jo aapka *audit* hai | wo aapko directly | aapke *Gmail* mein send kar sake."],
  [92.10, 93.07, "Bas yahi, | aur kuch nahi."],
  [93.51, 97.87, "Aur *new tool* hone ke baavjood | isko *thousands of daily active users* | use kar rahe hain."],
  [98.30, 101.40, "Agar aapko bhi apni website ki | *AI visibility report* | generate karni hai,"],
  [101.50, 105.00, "toh comment kijiye *TOOL*, | aur main aapko directly | *DM* mein tool bhej dunga."],
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
