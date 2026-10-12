import React from 'react';
import {
  AbsoluteFill,
  Img,
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

/* ---------- 5. "Aap game me bahut peeche ho" — dark/red, AI app card (ref 5) ---------- */

const Peeche: React.FC = () => {
  const frame = useCurrentFrame();
  const top = usePop(0);
  const big = usePop(4, 10);
  const card = usePop(2, 11);
  const flying = [
    {x: -80, y: 380, r: -20, s: 1.1, v: 9},
    {x: 820, y: 120, r: 25, s: 0.9, v: 7},
    {x: 760, y: 1250, r: -30, s: 1.3, v: 11},
    {x: -40, y: 1400, r: 15, s: 1.0, v: 8},
  ];
  return (
    <Shell bg="#0a0a0a">
      {flying.map((f, i) => (
        <div key={i} style={{position: 'absolute', left: f.x, top: f.y + frame * f.v, width: 360 * f.s, height: 200 * f.s, background: 'linear-gradient(135deg,#5b5b5b,#2b2b2b)', borderRadius: 20, transform: `rotate(${f.r + frame * 0.6}deg)`, filter: 'blur(14px)', opacity: 0.8}} />
      ))}
      <div style={{position: 'absolute', top: 400, width: '100%', textAlign: 'center', fontFamily: MONT, lineHeight: 1}}>
        <div style={{fontSize: 96, fontWeight: 800, color: '#fff', opacity: top, transform: `translateY(${(1 - top) * 30}px)`}}>
          game me{' '}
          <span style={{color: RED, fontStyle: 'italic', fontWeight: 600, textShadow: `0 0 30px ${RED}, 0 0 60px rgba(255,43,43,.6)`}}>bahut</span>
        </div>
        <div style={{fontSize: 196, fontWeight: 900, letterSpacing: -4, background: 'linear-gradient(180deg,#ffffff,#8d8d8d)', WebkitBackgroundClip: 'text', color: 'transparent', opacity: big, transform: `scale(${0.8 + big * 0.2})`}}>
          PEECHE
        </div>
      </div>
      <div style={{position: 'absolute', left: 210, top: 860, width: 660, background: '#fff', borderRadius: 18, overflow: 'hidden', boxShadow: '0 40px 80px rgba(0,0,0,.6)', transform: `translateY(${(1 - card) * 200}px) scale(${0.85 + card * 0.15})`, opacity: card}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 12, padding: '22px 26px', fontFamily: POP, fontWeight: 600, fontSize: 32, color: '#222'}}>
          <svg width={34} height={34} viewBox="0 0 32 32">
            <path d="M16 2c1.2 7 4 10.8 12 14-8 3.2-10.8 7-12 14-1.2-7-4-10.8-12-14 8-3.2 10.8-7 12-14z" fill="#222" />
          </svg>
          AI Search
          <div style={{marginLeft: 'auto', fontSize: 26, color: '#999'}}>•••</div>
        </div>
        <div style={{position: 'relative', margin: '0 18px', height: 560, borderRadius: 8, overflow: 'hidden', isolation: 'isolate'}}>
          <Img src={staticFile('face_crop.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'grayscale(1) contrast(1.25) brightness(1.1)'}} />
          <div style={{position: 'absolute', inset: 0, background: '#ff1e1e', mixBlendMode: 'color'}} />
          <div style={{position: 'absolute', inset: 0, background: 'rgba(255,30,30,.18)', mixBlendMode: 'multiply'}} />
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '22px 26px', fontFamily: POP, fontWeight: 600, fontSize: 30, color: RED}}>
          <svg width={30} height={30} viewBox="0 0 24 24">
            <path d="M12 4v15M5 12l7 7 7-7" fill="none" stroke={RED} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Your business: not found
        </div>
      </div>
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
  {id: 'Peeche', from: 28.8, to: 30.0, Component: Peeche},
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
