import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {MONT, POP} from './fonts';

// Brand colours sampled from the original edit.
const LIME = '#C8FE3C';
const RED = '#FF2B2B';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const usePop = (delay: number, damping = 12) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: frame - delay, fps, config: {damping, mass: 0.6}});
};

// Quick zoom/blur cut-in and a short dissolve out, shared by every insert.
const Shell: React.FC<{children: React.ReactNode; bg: string}> = ({children, bg}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const scale = interpolate(frame, [0, 5], [1.1, 1], clamp);
  const blur = interpolate(frame, [0, 4], [10, 0], clamp);
  const opacity = interpolate(frame, [durationInFrames - 3, durationInFrames], [1, 0], clamp);
  return (
    <AbsoluteFill style={{background: bg, opacity, overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${scale})`, filter: `blur(${blur}px)`}}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- 1. "Website hai, aur business bhi" — white minimal (ref 4) ---------- */

const BrowserCard: React.FC<{w: number}> = ({w}) => (
  <div
    style={{
      width: w,
      height: w * 0.66,
      background: '#fff',
      borderRadius: 22,
      boxShadow: '0 30px 60px rgba(0,0,0,.18)',
      overflow: 'hidden',
      border: '1px solid #e4e4e4',
    }}
  >
    <div style={{height: w * 0.1, background: '#f1f1f1', display: 'flex', alignItems: 'center', gap: 10, padding: '0 20px'}}>
      {['#ff5f57', '#febc2e', '#28c840'].map((c) => (
        <div key={c} style={{width: 14, height: 14, borderRadius: 7, background: c}} />
      ))}
      <div style={{marginLeft: 16, flex: 1, height: w * 0.05, borderRadius: 20, background: '#fff', fontFamily: POP, fontSize: w * 0.032, color: '#777', display: 'flex', alignItems: 'center', paddingLeft: 16}}>
        yourbusiness.com
      </div>
    </div>
    <div style={{padding: w * 0.06}}>
      <div style={{width: '70%', height: w * 0.05, background: '#222', borderRadius: 8}} />
      <div style={{width: '90%', height: w * 0.025, background: '#ddd', borderRadius: 6, marginTop: 22}} />
      <div style={{width: '80%', height: w * 0.025, background: '#ddd', borderRadius: 6, marginTop: 14}} />
      <div style={{width: w * 0.28, height: w * 0.075, background: LIME, borderRadius: 40, marginTop: 30}} />
    </div>
  </div>
);

const WebsiteBusiness: React.FC = () => {
  const frame = useCurrentFrame();
  const l1 = usePop(1);
  const l2 = usePop(9);
  const mark = interpolate(frame, [14, 24], [0, 1], clamp);
  const drift = (s: number) => frame * s;
  return (
    <Shell bg="#f8f8f6">
      <div style={{position: 'absolute', left: -120, top: 120, transform: `rotate(-14deg) translateY(${drift(0.6)}px)`, filter: 'blur(18px)', opacity: 0.8}}>
        <BrowserCard w={620} />
      </div>
      <div style={{position: 'absolute', right: -90, top: 330, transform: `rotate(-12deg) translate(${-drift(0.8)}px, ${drift(0.4)}px)`}}>
        <BrowserCard w={480} />
      </div>
      <div style={{position: 'absolute', left: -60, bottom: 230, transform: `rotate(16deg) translate(${drift(0.7)}px, ${-drift(0.5)}px)`}}>
        <BrowserCard w={440} />
      </div>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 6}}>
        <div style={{fontFamily: POP, fontStyle: 'italic', fontSize: 76, color: '#666', opacity: l1, transform: `translateY(${(1 - l1) * 30}px)`}}>
          Website hai,
        </div>
        <div style={{fontFamily: POP, fontSize: 76, color: '#666', opacity: l2, transform: `translateY(${(1 - l2) * 30}px)`}}>
          aur{' '}
          <span style={{position: 'relative', fontFamily: MONT, fontWeight: 800, color: '#333'}}>
            <span style={{position: 'absolute', left: -6, right: -6, bottom: 10, height: 18, background: LIME, borderRadius: 10, transformOrigin: 'left', transform: `scaleX(${mark})`, zIndex: -1}} />
            Business
          </span>{' '}
          bhi
        </div>
      </AbsoluteFill>
    </Shell>
  );
};

/* ---------- 2. "AI search me visible nahi hai" — black kinetic type (ref 1) ---------- */

const Invisible: React.FC = () => {
  const frame = useCurrentFrame();
  const a = usePop(0, 14);
  const b = usePop(3, 9);
  const c = usePop(9, 14);
  // "visible" flickers out once he says "nahi hai" — the word itself goes invisible.
  const flicker = frame < 15 ? 1 : frame < 27 ? ([1, 0.2, 0.9, 0.1, 0.7, 0.15][Math.floor((frame - 15) / 2)] ?? 0.2) : 0.18;
  const glow = `0 0 40px rgba(200,254,60,.45)`;
  return (
    <Shell bg="#000">
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{fontFamily: MONT, color: LIME, lineHeight: 0.95, textShadow: glow, transform: 'translateX(-20px)'}}>
          <div style={{fontSize: 92, fontWeight: 600, opacity: a, transform: `translateY(${(1 - a) * 40}px)`}}>AI search me</div>
          <div style={{fontSize: 210, fontWeight: 800, letterSpacing: -6, opacity: Math.min(b, flicker), transform: `scale(${0.6 + b * 0.4})`, transformOrigin: 'left center'}}>
            visible
          </div>
          <div style={{fontSize: 104, fontWeight: 600, textAlign: 'right', opacity: c, transform: `translateY(${(1 - c) * 40}px)`}}>
            nahi hai.
          </div>
        </div>
      </AbsoluteFill>
    </Shell>
  );
};

/* ---------- 3. ChatGPT / AI Overviews / Perplexity — glowing icon ring (ref 2) ---------- */

const stroke = {fill: 'none', stroke: '#fff', strokeWidth: 2.2, strokeLinecap: 'round', strokeLinejoin: 'round'} as const;
const ICONS: Record<string, React.ReactNode> = {
  chat: (
    <g {...stroke}>
      <path d="M5 6h22a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3H14l-6 5v-5H5a3 3 0 0 1-3-3V9a3 3 0 0 1 3-3z" />
      <path d="M9 13h14M9 18h9" />
    </g>
  ),
  sparkle: <path {...stroke} d="M16 2c1.2 7 4 10.8 12 14-8 3.2-10.8 7-12 14-1.2-7-4-10.8-12-14 8-3.2 10.8-7 12-14z" />,
  burst: (
    <g {...stroke}>
      <path d="M16 3v26M5 9.5l22 13M27 9.5l-22 13" />
      <circle cx="16" cy="16" r="5" />
    </g>
  ),
  search: (
    <g {...stroke}>
      <circle cx="13" cy="13" r="9" />
      <path d="M20 20l9 9" />
    </g>
  ),
  chip: (
    <g {...stroke}>
      <rect x="8" y="8" width="16" height="16" rx="3" />
      <path d="M12 8V3M20 8V3M12 29v-5M20 29v-5M8 12H3M8 20H3M29 12h-5M29 20h-5" />
      <text x="16" y="19.5" fill="#fff" stroke="none" fontSize="7" fontWeight="700" textAnchor="middle" fontFamily="sans-serif">AI</text>
    </g>
  ),
  globe: (
    <g {...stroke}>
      <circle cx="16" cy="16" r="13" />
      <path d="M3 16h26M16 3c4 4 5.5 8.5 5.5 13S20 25 16 29c-4-4-5.5-8.5-5.5-13S12 7 16 3z" />
    </g>
  ),
};
// Clockwise from the top; ChatGPT / AI Overviews / Perplexity light up as he names them.
const RING = [
  {icon: 'chat', label: 'ChatGPT', on: [0, 27]},
  {icon: 'sparkle', label: 'AI Overviews', on: [28, 70]},
  {icon: 'search', label: '', on: [-1, -1]},
  {icon: 'burst', label: 'Perplexity', on: [71, 999]},
  {icon: 'chip', label: '', on: [-1, -1]},
  {icon: 'globe', label: '', on: [-1, -1]},
] as const;

const AIRing: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const rot = frame * 0.25;
  const active = RING.find((r) => frame >= r.on[0] && frame <= r.on[1]);
  const activeStart = active ? active.on[0] : 0;
  const labelIn = spring({frame: frame - activeStart, fps, config: {damping: 12}});
  const R = 270;
  return (
    <Shell bg="radial-gradient(circle at 50% 45%, #2a1d5c 0%, #160f33 45%, #0c0820 100%)">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: -300 + i * 380 + frame * 1.5,
            top: -200 + i * 650,
            width: 1400,
            height: 260,
            background: 'rgba(120,80,255,.35)',
            filter: 'blur(90px)',
            transform: 'rotate(-38deg)',
          }}
        />
      ))}
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{position: 'relative', width: 0, height: 0, transform: `rotate(${rot}deg)`}}>
          {RING.map((r, i) => {
            const pop = spring({frame: frame - i * 2, fps, config: {damping: 11}});
            const on = r === active;
            const ang = (i / RING.length) * Math.PI * 2 - Math.PI / 2;
            const size = 158;
            return (
              <div
                key={r.icon}
                style={{
                  position: 'absolute',
                  left: Math.cos(ang) * R - size / 2,
                  top: Math.sin(ang) * R - size / 2,
                  width: size,
                  height: size,
                  borderRadius: '50%',
                  border: `5px solid ${on ? LIME : '#fff'}`,
                  boxShadow: on
                    ? `0 0 40px ${LIME}, inset 0 0 25px rgba(200,254,60,.5)`
                    : '0 0 30px rgba(210,190,255,.8), inset 0 0 20px rgba(210,190,255,.5)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transform: `rotate(${-rot}deg) scale(${pop * (on ? 1.22 : 1)})`,
                  background: on ? 'rgba(200,254,60,.12)' : 'rgba(255,255,255,.04)',
                }}
              >
                <svg width={78} height={78} viewBox="0 0 32 32" style={{filter: 'drop-shadow(0 0 6px rgba(255,255,255,.9))'}}>
                  {ICONS[r.icon]}
                </svg>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
      <div style={{position: 'absolute', top: 1340, width: '100%', textAlign: 'center', fontFamily: MONT, fontWeight: 800, fontSize: 92, color: '#fff', textShadow: `0 0 30px rgba(200,254,60,.6)`, opacity: labelIn, transform: `translateY(${(1 - labelIn) * 30}px)`}}>
        {active?.label}
      </div>
      <div style={{position: 'absolute', top: 480, width: '100%', textAlign: 'center', fontFamily: POP, fontSize: 40, color: 'rgba(255,255,255,.75)', letterSpacing: 6}}>
        AI SEARCH ENGINES
      </div>
      <div style={{position: 'absolute', bottom: 120, width: '100%', textAlign: 'center', fontFamily: POP, fontSize: 34, color: 'rgba(255,255,255,.8)'}}>
        AI SEO · Vaibhav · Day 1/100
      </div>
    </Shell>
  );
};

/* ---------- 4. "Even according to Google, daily 100M+" — grey grid (ref 3) ---------- */

const ResultCard: React.FC<{w: number; hero?: boolean}> = ({w, hero}) => (
  <div style={{width: w, height: w * 0.36, background: hero ? '#fff' : '#cfcfcc', borderRadius: w * 0.18, display: 'flex', alignItems: 'center', gap: w * 0.04, padding: `0 ${w * 0.07}px`, boxShadow: hero ? '0 40px 50px rgba(0,0,0,.25)' : '0 10px 20px rgba(0,0,0,.12)'}}>
    <svg width={w * 0.13} height={w * 0.13} viewBox="0 0 32 32">
      <path d="M16 2c1.2 7 4 10.8 12 14-8 3.2-10.8 7-12 14-1.2-7-4-10.8-12-14 8-3.2 10.8-7 12-14z" fill={hero ? '#222' : '#aaa'} />
    </svg>
    {hero ? (
      <div style={{fontFamily: POP, fontWeight: 600, fontSize: w * 0.075, color: '#222'}}>Ask AI anything…</div>
    ) : (
      <div style={{flex: 1, height: w * 0.05, background: '#b5b5b2', borderRadius: 10}} />
    )}
  </div>
);

const GoogleScale: React.FC = () => {
  const frame = useCurrentFrame();
  const t = usePop(0);
  const g = usePop(4, 10);
  const hero = usePop(6, 10);
  const bottom = usePop(10);
  const sharpen = interpolate(frame, [14, 30], [9, 0], clamp);
  const side = [-1, 1].flatMap((d) => [1, 2, 3, 4].map((k) => ({d, k})));
  return (
    <Shell bg="radial-gradient(circle at 50% 50%, #f7f7f5 0%, #e8e8e5 60%, #cfcfcc 100%)">
      {/* dashed layout grid, as in the reference */}
      {[300, 780].map((x) => (
        <div key={x} style={{position: 'absolute', left: x, top: 560, height: 820, borderLeft: '2px dashed rgba(0,0,0,.12)'}} />
      ))}
      {[620, 1290].map((y) => (
        <div key={y} style={{position: 'absolute', top: y, left: 120, width: 840, borderTop: '2px dashed rgba(0,0,0,.12)'}} />
      ))}
      <div style={{position: 'absolute', top: 400, width: '100%', textAlign: 'center'}}>
        <div style={{fontFamily: POP, fontSize: 56, color: '#222', opacity: t}}>Even according to</div>
        <div style={{fontFamily: MONT, fontWeight: 800, fontSize: 150, color: '#1d1d1d', lineHeight: 1, opacity: g, transform: `scale(${0.7 + g * 0.3})`}}>Google</div>
      </div>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', top: 120}}>
        {side.map(({d, k}) => (
          <div key={`${d}${k}`} style={{position: 'absolute', transform: `translateX(${d * (230 + k * 120) - frame * d * 1.2}px) translateY(${-k * 22}px) scale(${1 - k * 0.15})`, opacity: 1 - k * 0.15, filter: `blur(${k * 0.8}px)`}}>
            <ResultCard w={380} />
          </div>
        ))}
        <div style={{transform: `scale(${hero}) translateY(${(1 - hero) * 80}px)`}}>
          <ResultCard w={560} hero />
        </div>
      </AbsoluteFill>
      <div style={{position: 'absolute', top: 1320, width: '100%', textAlign: 'center', opacity: bottom}}>
        <div style={{fontFamily: POP, fontSize: 56, color: '#222'}}>daily</div>
        <div style={{fontFamily: MONT, fontWeight: 800, fontSize: 94, color: '#1d1d1d', lineHeight: 1, whiteSpace: 'nowrap', filter: `blur(${sharpen}px)`}}>100M+ AI searches</div>
      </div>
    </Shell>
  );
};

/* ---------- 5. "Agar aapka business AI searches me visible nahi hai, to aap game me bahut peeche ho" ---------- */

// Local frame cues (sequence starts at 26.25s), matched to the burned-in captions.
const CUE = {business: 22, notFound: 52, race: 66, peeche: 82};

const Check: React.FC<{ok: boolean}> = ({ok}) => (
  <div style={{width: 46, height: 46, borderRadius: 23, background: ok ? LIME : RED, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0}}>
    <svg width={26} height={26} viewBox="0 0 24 24">
      <path d={ok ? 'M5 12.5l4.5 4.5L19 7.5' : 'M6 6l12 12M18 6L6 18'} fill="none" stroke={ok ? '#111' : '#fff'} strokeWidth={3.2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  </div>
);

const RIVALS = ['Competitor A', 'Competitor B', 'Competitor C'];

const AIAnswer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const card = usePop(0, 13);
  const typed = 'Best business for this?';
  const shown = typed.slice(0, Math.floor(interpolate(frame, [2, 16], [0, typed.length], clamp)));
  const youIn = spring({frame: frame - 38, fps, config: {damping: 12}});
  const fail = frame >= CUE.notFound;
  const shake = fail ? Math.sin((frame - CUE.notFound) * 2.2) * interpolate(frame, [CUE.notFound, CUE.notFound + 10], [14, 0], clamp) : 0;
  const strike = interpolate(frame, [CUE.notFound, CUE.notFound + 5], [0, 1], clamp);
  const row = (i: number) => spring({frame: frame - (14 + i * 7), fps, config: {damping: 12}});
  return (
    <div style={{width: 820, background: '#151515', border: '1px solid #2c2c2c', borderRadius: 34, padding: 40, boxShadow: '0 40px 90px rgba(0,0,0,.6)', transform: `scale(${0.9 + card * 0.1})`, opacity: card}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 14, fontFamily: POP, fontWeight: 600, fontSize: 34, color: '#fff'}}>
        <svg width={38} height={38} viewBox="0 0 32 32">
          <path d="M16 2c1.2 7 4 10.8 12 14-8 3.2-10.8 7-12 14-1.2-7-4-10.8-12-14 8-3.2 10.8-7 12-14z" fill={LIME} />
        </svg>
        AI Search
      </div>
      <div style={{marginTop: 26, marginLeft: 'auto', width: 'fit-content', background: '#2a2a2a', borderRadius: 26, padding: '16px 26px', fontFamily: POP, fontSize: 32, color: '#eee', minHeight: 48}}>
        {shown}
        <span style={{opacity: frame % 10 < 5 && frame < 20 ? 1 : 0}}>|</span>
      </div>
      <div style={{marginTop: 26, display: 'flex', flexDirection: 'column', gap: 16}}>
        {RIVALS.map((name, i) => (
          <div key={name} style={{display: 'flex', alignItems: 'center', gap: 20, background: '#1f1f1f', borderRadius: 20, padding: '18px 22px', opacity: row(i), transform: `translateX(${(1 - row(i)) * 80}px)`}}>
            <Check ok />
            <div style={{fontFamily: POP, fontWeight: 600, fontSize: 36, color: '#fff'}}>{name}</div>
            <div style={{marginLeft: 'auto', fontFamily: POP, fontSize: 26, color: LIME}}>recommended</div>
          </div>
        ))}
        <div style={{display: 'flex', alignItems: 'center', gap: 20, borderRadius: 20, padding: '18px 22px', border: `3px dashed ${fail ? RED : '#555'}`, opacity: youIn, transform: `translateX(${(1 - youIn) * 80 + shake}px)`, background: fail ? 'rgba(255,43,43,.12)' : 'transparent'}}>
          {fail ? <Check ok={false} /> : <div style={{width: 46, height: 46, borderRadius: 23, border: '3px solid #555'}} />}
          <div style={{position: 'relative', fontFamily: MONT, fontWeight: 800, fontSize: 38, color: fail ? '#999' : '#fff'}}>
            Your Business
            <div style={{position: 'absolute', left: -4, right: -4, top: '52%', height: 5, background: RED, transformOrigin: 'left', transform: `scaleX(${strike})`}} />
          </div>
          <div style={{marginLeft: 'auto', fontFamily: POP, fontWeight: 600, fontSize: 26, color: RED, opacity: strike}}>not mentioned</div>
        </div>
      </div>
    </div>
  );
};

const RACE = [
  {name: 'Competitor A', to: 0.92, rank: '#1'},
  {name: 'Competitor B', to: 0.8, rank: '#2'},
  {name: 'Competitor C', to: 0.7, rank: '#3'},
  {name: 'Your Business', to: 0.07, rank: '#47', you: true},
];

const Race: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const inP = spring({frame, fps, config: {damping: 13}});
  const grow = interpolate(frame, [3, 26], [0, 1], {...clamp, easing: (t) => 1 - Math.pow(1 - t, 3)});
  const pulse = 1 + Math.sin(frame * 0.5) * 0.08;
  return (
    <div style={{width: 860, opacity: inP, transform: `translateY(${(1 - inP) * 120}px)`}}>
      <div style={{fontFamily: POP, fontWeight: 600, fontSize: 34, letterSpacing: 6, color: 'rgba(255,255,255,.7)', textAlign: 'center', marginBottom: 34}}>AI VISIBILITY RACE</div>
      {RACE.map((r) => (
        <div key={r.name} style={{marginBottom: 30}}>
          <div style={{display: 'flex', justifyContent: 'space-between', fontFamily: POP, fontWeight: 600, fontSize: 32, color: r.you ? RED : '#fff', marginBottom: 10}}>
            <span>{r.name}</span>
            <span style={{fontFamily: MONT, fontWeight: 800, transform: r.you ? `scale(${pulse})` : undefined}}>{r.rank}</span>
          </div>
          <div style={{height: 34, borderRadius: 17, background: '#222', overflow: 'hidden', border: r.you ? `2px solid ${RED}` : '2px solid #2c2c2c'}}>
            <div style={{height: '100%', width: `${r.to * grow * 100}%`, borderRadius: 17, background: r.you ? RED : LIME, boxShadow: r.you ? `0 0 20px ${RED}` : `0 0 20px rgba(200,254,60,.6)`}} />
          </div>
        </div>
      ))}
    </div>
  );
};

const Headline: React.FC = () => {
  const frame = useCurrentFrame();
  const beat = frame < CUE.business ? 0 : frame < CUE.notFound ? 1 : frame < CUE.race ? 2 : 3;
  const starts = [0, CUE.business, CUE.notFound, CUE.race];
  const p = usePop(starts[beat], 12);
  const big = usePop(CUE.peeche, 10);
  const lines: React.ReactNode[] = [
    <span key="0" style={{color: '#fff'}}>agar aapka</span>,
    <span key="1">
      <span style={{color: LIME}}>business</span> <span style={{color: '#fff'}}>AI searches me</span>
    </span>,
    <span key="2">
      <span style={{color: '#fff'}}>visible</span> <span style={{color: RED, fontStyle: 'italic', textShadow: `0 0 30px ${RED}`}}>nahi hai</span>
    </span>,
    <span key="3">
      <span style={{color: '#fff'}}>to aap game me</span> <span style={{color: RED, fontStyle: 'italic', textShadow: `0 0 30px ${RED}`}}>bahut</span>
    </span>,
  ];
  return (
    <div style={{position: 'absolute', top: 300, width: '100%', textAlign: 'center', fontFamily: MONT, lineHeight: 1}}>
      <div style={{fontSize: 68, fontWeight: 800, opacity: p, transform: `translateY(${(1 - p) * 30}px)`}}>{lines[beat]}</div>
      {beat === 3 && (
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, marginTop: 10, opacity: big, transform: `scale(${0.75 + big * 0.25})`}}>
          <span style={{fontSize: 168, fontWeight: 900, letterSpacing: -4, background: 'linear-gradient(180deg,#ffffff,#8d8d8d)', WebkitBackgroundClip: 'text', color: 'transparent'}}>PEECHE</span>
          <svg width={90} height={124} viewBox="0 0 24 32">
            <path d="M12 3v24M4 19l8 8 8-8" fill="none" stroke={RED} strokeWidth={3.5} strokeLinecap="round" strokeLinejoin="round" style={{filter: `drop-shadow(0 0 8px ${RED})`}} />
          </svg>
        </div>
      )}
    </div>
  );
};

const FallingBehind: React.FC = () => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [CUE.race - 6, CUE.race], [1, 0], clamp);
  const glow = interpolate(frame, [CUE.notFound, CUE.race], [0, 1], clamp);
  return (
    <Shell bg="#0a0a0a">
      <AbsoluteFill style={{background: `radial-gradient(circle at 50% 60%, rgba(200,254,60,${0.1 * (1 - glow)}) 0%, rgba(255,43,43,${0.16 * glow}) 35%, transparent 70%)`}} />
      <AbsoluteFill style={{backgroundImage: 'linear-gradient(rgba(255,255,255,.04) 2px, transparent 2px), linear-gradient(90deg, rgba(255,255,255,.04) 2px, transparent 2px)', backgroundSize: '90px 90px'}} />
      <Headline />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', top: 220}}>
        {frame < CUE.race ? (
          <div style={{opacity: out, transform: `translateY(${(1 - out) * -100}px)`}}>
            <AIAnswer />
          </div>
        ) : (
          <Sequence from={CUE.race} layout="none">
            <Race />
          </Sequence>
        )}
      </AbsoluteFill>
    </Shell>
  );
};

/* ---------- Timeline ---------- */

// Times in seconds, matched to the burned-in captions of AI_SEO_Day1_final.mp4.
export const INSERTS = [
  {id: 'WebsiteBusiness', from: 1.0, to: 2.4, Component: WebsiteBusiness},
  {id: 'Invisible', from: 3.2, to: 4.5, Component: Invisible},
  {id: 'AIRing', from: 15.5, to: 18.4, Component: AIRing},
  {id: 'GoogleScale', from: 22.2, to: 23.4, Component: GoogleScale},
  {id: 'FallingBehind', from: 26.25, to: 30.05, Component: FallingBehind},
];

export const Main: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <OffthreadVideo src={staticFile('main.mp4')} />
      {INSERTS.map(({id, from, to, Component}) => (
        <Sequence key={id} from={Math.round(from * fps)} durationInFrames={Math.round((to - from) * fps)}>
          <Component />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
