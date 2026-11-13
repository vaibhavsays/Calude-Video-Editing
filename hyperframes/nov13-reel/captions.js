// Hinglish subtitles (Roman script only), short punchy groups. Times are on the ORIGINAL (raw/nov13.mp4) clock; T()
// maps them onto the tight cut (edl.js). "|" splits a segment into phrases sharing its time by text length.
// *word* = highlighted.
const SEGMENTS = [
  [0.35, 3.04, "Aapne notice kiya hoga ki | jab bhi aap apne *business* ke baare mein"],
  [3.23, 4.62, "*search engines* mein | search karte ho,"],
  [5.15, 7.90, "toh wo *Reddit*, *Quora* se | answers kyun uthate hain, | unke *suggestions* kyun dete hain?"],
  [8.94, 12.01, "So welcome to *Day 9* | of 100 Days of | *Decoding AI SEO* with Vaibhav."],
  [12.50, 16.18, "Kyunki search engines ko lagta hai | ki yahan pe *real log* hain, | *real baatein* ho rahi hain,"],
  [16.33, 18.67, "*businesses* ki baatein ho rahi hain, | *problems solve* ho rahi hain."],
  [19.10, 22.04, "Log wahan apni *problems* | aur apna *opinion share* karte hain,"],
  [22.39, 25.08, "toh aapko *answers* mil jaate hain, | answers *read* kar sakte ho wahan pe."],
  [25.54, 27.20, "Aapki koi bhi | *problem* hoti hai,"],
  [27.56, 29.81, "aap apni problem ki | *exact query* search karte ho,"],
  [30.17, 32.99, "toh aapko *exact real solution* milta hai, | jo *real logon* ne bataya hota hai."],
  [33.15, 34.74, "Aur *same cheez* | aapke *business* ke saath hoti hai."],
  [35.22, 37.48, "Aapke business ke baare mein | koi bhi kahin bhi | *search* karta hai,"],
  [38.07, 40.21, "toh hamein bhi | *Reddit*, *Quora* aur | *other forums* pe hona chahiye,"],
  [40.42, 42.40, "jahan se search engines | *recommendations* uthate hain."],
  [43.34, 44.96, "Aur *follow* this page | for more such content."],
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
