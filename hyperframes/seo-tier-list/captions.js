// English subtitles (translated from the spoken Hinglish), on the speech segments found by silence detection.
// "|" splits a segment into on-screen phrases sharing its time by text length. *word* = cyan.
// name:true = the item-name card (big cyan, with the item's icon beside it).
const SEGMENTS = [
  [0.12, 0.88, "Domain Authority", { name: true }],
  [1.39, 6.16, "*C tier.* It's good, | but even without it | our pages, blogs and keywords | still rank well."],
  [6.93, 7.69, "Internal Linking", { name: true }],
  [8.07, 11.56, "*A tier,* because it helps | Google crawl your website | and index your pages."],
  [12.53, 13.24, "Topical Authority", { name: true }],
  [13.64, 19.08, "*A tier.* It helps Google understand | how much *topical authority* | your business has,"],
  [19.34, 22.65, "like how many keywords and topics | you cover. | Cover *all the topics.*"],
  [23.11, 24.22, "Schema Markup", { name: true }],
  [24.80, 29.75, "*B tier.* It gets you *rich results,* | but it has nothing to do | with ranking itself."],
  [30.40, 30.93, "Page Speed", { name: true }],
  [31.49, 36.96, "Page speed and *Core Web Vitals* | are important. *B tier,* | because if your page doesn't load,"],
  [37.40, 44.43, "your *bounce rate* goes up, | because users bounce back | from your page."],
  [44.82, 45.53, "E-E-A-T", { name: true }],
  [46.04, 56.24, "E-E-A-T is *B tier,* | because it builds your | *experience, expertise,* | *authority and trust,* | and shows how much | authority you have."],
  [56.62, 59.79, "Your *experience* counts, | your *expertise* counts."],
  [60.08, 61.20, "Original Data & Research", { name: true }],
  [61.66, 71.48, "Original data and research is *A tier,* | because AI search crawlers and bots | need *original data and research* | to show your results in AI search, | because it's *unique.*"],
  [71.99, 77.65, "Digital PR is *S tier,* | because it's very important | for your *Domain Authority* | and your *backlink profile.*"],
];

SEGMENTS.forEach(([s, e, text, opts]) => {
  const phrases = text.split("|").map((p) => p.trim());
  const lens = phrases.map((p) => p.replace(/\*/g, "").length + 4);
  const total = lens.reduce((a, b) => a + b, 0);
  let t = s;
  phrases.forEach((p, i) => {
    const d = (e - s) * lens[i] / total;
    CUES.push([t, i === phrases.length - 1 ? e + 0.12 : t + d, p, opts || {}]);
    t += d;
  });
});
