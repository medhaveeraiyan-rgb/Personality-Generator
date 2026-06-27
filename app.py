import streamlit as st
import requests
import json
from datetime import datetime
from fpdf import FPDF
import io
import math
import os
import time
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="✦ Personality Oracle",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── QUESTIONS ────────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "id": 1, "category": "Decision Style",
        "question": "🔒 You find a mysterious locked box — what do you do?",
        "options": [
            "🔍  Search everywhere for the key — systematically",
            "💪  Force it open. Curiosity can't wait",
            "🌿  Leave it. Some things aren't meant to be opened",
            "💬  Ask around — someone must know its story",
        ]
    },
    {
        "id": 2, "category": "Energy",
        "question": "⏰ Pick the time of day you feel most alive",
        "options": [
            "🌙  3AM — the world is quiet and mine",
            "🌅  Sunrise — fresh start energy every day",
            "🌇  Golden hour — everything feels cinematic",
            "☀️  Midday chaos — I thrive in the noise",
        ]
    },
    {
        "id": 3, "category": "Conflict",
        "question": "⚡ A friend disagrees with you publicly — your move?",
        "options": [
            "🤝  Stay calm, address it privately later",
            "⚡  Defend my position with facts, right now",
            "👂  Hear them out — maybe they have a point",
            "😄  Diffuse with humor, argue never",
        ]
    },
    {
        "id": 4, "category": "Creativity",
        "question": "🧩 How do you solve a problem you've never seen before?",
        "options": [
            "📚  Research everything about it first",
            "🔄  Just start — iterate until it works",
            "💭  Sleep on it. The answer comes in dreams",
            "🧠  Brainstorm wildly with others",
        ]
    },
    {
        "id": 5, "category": "Social",
        "question": "🗓️ Your ideal Saturday has how many people in it?",
        "options": [
            "🎵  Zero — just me, music, and silence",
            "💫  One — my person, that's enough",
            "🔥  A small tight crew — 3 to 5",
            "🎉  Everyone — the more the louder",
        ]
    },
    {
        "id": 6, "category": "Ambition",
        "question": "🦸 You get one superpower — which feels most you?",
        "options": [
            "🔮  See the future — plan everything perfectly",
            "⏸️  Pause time — never feel rushed again",
            "🧩  Read minds — finally understand everyone",
            "🚀  Teleport — freedom with no boundaries",
        ]
    },
    {
        "id": 7, "category": "Emotion",
        "question": "🌀 Something goes wrong right before a big moment — you...",
        "options": [
            "⚔️  Pivot instantly — adapt and conquer",
            "🧘  Breathe, reset, keep the plan",
            "🌀  Spiral a little, then get it together",
            "😂  Laugh it off — chaos is my comfort zone",
        ]
    },
]

# ─── SESSION STATE ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "landing",
        "user_name": "",
        "current_q": 0,
        "answers": {},
        "profile": None,
        "reveal_done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── ANIMATED BACKGROUND ─────────────────────────────────────────────────────
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:100%; height:100%; overflow:hidden; background:#000; }
  canvas { display:block; position:fixed; top:0; left:0; width:100vw; height:100vh; }
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
const canvas = document.getElementById('c');
const ctx    = canvas.getContext('2d');
let W, H;

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

const STAR_COUNT = 220;
const stars = Array.from({length: STAR_COUNT}, () => ({
  x: Math.random(),
  y: Math.random(),
  r: Math.random() * 1.4 + 0.3,
  phase: Math.random() * Math.PI * 2,
  speed: 0.4 + Math.random() * 1.2,
}));

const nebulae = [
  { cx:0.15, cy:0.18, rx:0.45, ry:0.45, color:'rgba(124,58,237,', baseA:0.28, phase:0,   speed:0.00035 },
  { cx:0.85, cy:0.80, rx:0.38, ry:0.38, color:'rgba(37,99,235,',  baseA:0.22, phase:1.5, speed:0.00028 },
  { cx:0.50, cy:0.50, rx:0.28, ry:0.28, color:'rgba(14,165,233,', baseA:0.14, phase:3.0, speed:0.00042 },
  { cx:0.20, cy:0.75, rx:0.32, ry:0.32, color:'rgba(168,85,247,', baseA:0.18, phase:4.5, speed:0.00031 },
  { cx:0.75, cy:0.25, rx:0.25, ry:0.25, color:'rgba(244,114,182,',baseA:0.10, phase:2.0, speed:0.00038 },
];

const shoots = [];
function spawnShoot() {
  shoots.push({
    x:  W * (0.3 + Math.random() * 0.7),
    y:  H * (Math.random() * 0.4),
    vx: -(4 + Math.random() * 6),
    vy:  (2 + Math.random() * 4),
    len: 90 + Math.random() * 120,
    life: 1,
    decay: 0.018 + Math.random() * 0.014,
  });
}
let nextShoot = 120 + Math.random() * 200;

const PART_COUNT = 55;
const particles = Array.from({length: PART_COUNT}, () => ({
  x: Math.random(),
  y: Math.random(),
  r: Math.random() * 1.8 + 0.4,
  vx: (Math.random() - 0.5) * 0.00015,
  vy: (Math.random() - 0.5) * 0.00012,
  alpha: Math.random() * 0.25 + 0.05,
  color: ['rgba(167,139,250,', 'rgba(96,165,250,', 'rgba(52,211,153,', 'rgba(251,191,36,'][Math.floor(Math.random()*4)],
}));

const AURORA_COLORS = [
  [167,139,250], [96,165,250], [52,211,153], [244,114,182], [167,139,250]
];
let auroraT = 0;

let frame = 0;
function draw() {
  requestAnimationFrame(draw);
  frame++;
  auroraT += 0.003;

  ctx.fillStyle = '#06041a';
  ctx.fillRect(0, 0, W, H);

  const t = frame;
  nebulae.forEach(n => {
    n.phase += n.speed;
    const px = (n.cx + Math.sin(n.phase * 1.3) * 0.07) * W;
    const py = (n.cy + Math.cos(n.phase * 0.9) * 0.06) * H;
    const r  = n.rx * W * (1 + Math.sin(n.phase * 0.7) * 0.12);
    const a  = n.baseA * (0.75 + 0.25 * Math.sin(n.phase * 1.1));
    const grd = ctx.createRadialGradient(px, py, 0, px, py, r);
    grd.addColorStop(0,   n.color + a + ')');
    grd.addColorStop(0.4, n.color + (a*0.5) + ')');
    grd.addColorStop(1,   n.color + '0)');
    ctx.globalCompositeOperation = 'screen';
    ctx.beginPath();
    ctx.ellipse(px, py, r, r * 0.85, n.phase * 0.1, 0, Math.PI * 2);
    ctx.fillStyle = grd;
    ctx.fill();
  });
  ctx.globalCompositeOperation = 'source-over';

  for (let i = 0; i < 5; i++) {
    const yBase = H * (0.12 + i * 0.16);
    const [r,g,b] = AURORA_COLORS[i];
    const alpha = 0.04 + 0.07 * Math.abs(Math.sin(auroraT * 0.8 + i * 1.2));
    ctx.globalCompositeOperation = 'screen';
    ctx.beginPath();
    ctx.moveTo(0, yBase);
    for (let x = 0; x <= W; x += 6) {
      const y = yBase
        + Math.sin(x * 0.008 + auroraT * 1.1 + i) * 18
        + Math.sin(x * 0.004 + auroraT * 0.6 + i * 2) * 12;
      ctx.lineTo(x, y);
    }
    ctx.strokeStyle = `rgba(${r},${g},${b},${alpha})`;
    ctx.lineWidth = 2.5 + 2 * Math.abs(Math.sin(auroraT + i));
    ctx.stroke();
  }
  ctx.globalCompositeOperation = 'source-over';

  stars.forEach(s => {
    s.phase += s.speed * 0.012;
    const alpha = 0.08 + 0.85 * (0.5 + 0.5 * Math.sin(s.phase));
    const flicker = 1 + 0.35 * Math.sin(s.phase * 2.3);
    const sx = s.x * W, sy = s.y * H;
    ctx.beginPath();
    ctx.arc(sx, sy, s.r * flicker, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${alpha})`;
    ctx.fill();
    if (s.r > 1.1 && alpha > 0.6) {
      ctx.strokeStyle = `rgba(255,255,255,${alpha * 0.4})`;
      ctx.lineWidth = 0.5;
      const arm = s.r * 3.5;
      ctx.beginPath();
      ctx.moveTo(sx - arm, sy); ctx.lineTo(sx + arm, sy);
      ctx.moveTo(sx, sy - arm); ctx.lineTo(sx, sy + arm);
      ctx.stroke();
    }
  });

  particles.forEach(p => {
    p.x += p.vx; p.y += p.vy;
    if (p.x < 0) p.x = 1; if (p.x > 1) p.x = 0;
    if (p.y < 0) p.y = 1; if (p.y > 1) p.y = 0;
    const grd = ctx.createRadialGradient(p.x*W, p.y*H, 0, p.x*W, p.y*H, p.r * 6);
    grd.addColorStop(0, p.color + p.alpha + ')');
    grd.addColorStop(1, p.color + '0)');
    ctx.globalCompositeOperation = 'screen';
    ctx.beginPath();
    ctx.arc(p.x*W, p.y*H, p.r * 6, 0, Math.PI * 2);
    ctx.fillStyle = grd;
    ctx.fill();
    ctx.globalCompositeOperation = 'source-over';
  });

  nextShoot--;
  if (nextShoot <= 0) {
    spawnShoot();
    nextShoot = 150 + Math.random() * 280;
  }
  shoots.forEach((s, i) => {
    s.x += s.vx; s.y += s.vy;
    s.life -= s.decay;
    const grd = ctx.createLinearGradient(s.x, s.y, s.x + s.len * (-s.vx/Math.hypot(s.vx,s.vy)), s.y + s.len * (-s.vy/Math.hypot(s.vx,s.vy)));
    grd.addColorStop(0, `rgba(255,255,255,${s.life * 0.9})`);
    grd.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.beginPath();
    ctx.moveTo(s.x, s.y);
    ctx.lineTo(s.x + s.len * (-s.vx/Math.hypot(s.vx,s.vy)), s.y + s.len * (-s.vy/Math.hypot(s.vx,s.vy)));
    ctx.strokeStyle = grd;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(s.x, s.y, 1.8, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${s.life})`;
    ctx.fill();
  });
  for (let i = shoots.length - 1; i >= 0; i--) {
    if (shoots[i].life <= 0) shoots.splice(i, 1);
  }
}
draw();
</script>
</body>
</html>
""", height=1, scrolling=False)

# ─── CSS GLOBAL STYLES ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 4rem; max-width: 1400px; padding-left: 2rem; padding-right: 2rem; }

iframe {
    position: fixed !important;
    top: 0 !important; left: 0 !important;
    width: 100vw !important; height: 100vh !important;
    z-index: 0 !important;
    pointer-events: none !important;
    border: none !important;
}

.stApp,
.stApp > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
section[data-testid="stMain"],
.main,
.main .block-container,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {
    background: transparent !important;
}

[data-testid="stAppViewContainer"] > * { position: relative; z-index: 2; }
.main > div { position: relative; z-index: 2; }
[data-testid="stVerticalBlock"] { position: relative; z-index: 2; }

/* ── DRAMATIC REVEAL ANIMATIONS ── */
@keyframes cosmicPulse {
    0%   { transform: scale(0.5) rotate(-10deg); opacity: 0; filter: blur(20px) brightness(3); }
    40%  { transform: scale(1.15) rotate(3deg); opacity: 1; filter: blur(0px) brightness(1.5); }
    60%  { transform: scale(0.97) rotate(-1deg); filter: brightness(1.2); }
    100% { transform: scale(1) rotate(0deg); opacity: 1; filter: brightness(1); }
}
@keyframes shockwaveRing {
    0%   { transform: scale(0); opacity: 1; }
    100% { transform: scale(4); opacity: 0; }
}
@keyframes slideReveal {
    0%   { transform: translateY(40px); opacity: 0; filter: blur(8px); }
    100% { transform: translateY(0); opacity: 1; filter: blur(0); }
}
@keyframes fadeGlow {
    0%   { opacity: 0; transform: scale(0.95); }
    100% { opacity: 1; transform: scale(1); }
}
@keyframes textTypeIn {
    0%   { opacity: 0; letter-spacing: 0.5em; }
    100% { opacity: 1; letter-spacing: normal; }
}
@keyframes borderPulse {
    0%,100% { box-shadow: 0 0 20px rgba(167,139,250,0.15); }
    50%      { box-shadow: 0 0 60px rgba(167,139,250,0.45), 0 0 120px rgba(167,139,250,0.1); }
}
@keyframes particleBurst {
    0%   { transform: translateY(0) scale(1); opacity: 1; }
    100% { transform: translateY(-80px) scale(0); opacity: 0; }
}
@keyframes counterUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes floatIcon {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-10px); }
}
@keyframes oracleOrb {
    0%   { transform: scale(0) rotate(0deg); opacity: 0; filter: blur(30px); }
    30%  { transform: scale(1.3) rotate(180deg); opacity: 1; filter: blur(5px); }
    60%  { transform: scale(0.9) rotate(300deg); filter: blur(2px); }
    100% { transform: scale(1) rotate(360deg); opacity: 1; filter: blur(0); }
}
@keyframes scanLine {
    0%   { transform: translateY(-100%); opacity: 0.8; }
    100% { transform: translateY(100vh); opacity: 0; }
}
@keyframes glitchFlash {
    0%,100% { clip-path: inset(0 0 100% 0); opacity: 0; }
    10%      { clip-path: inset(20% 0 60% 0); opacity: 1; }
    20%      { clip-path: inset(60% 0 20% 0); opacity: 1; }
    30%      { clip-path: inset(0 0 0 0); opacity: 1; }
    100%     { clip-path: inset(0 0 0 0); opacity: 1; }
}

/* Reveal classes */
.reveal-hero {
    animation: cosmicPulse 1.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
.reveal-section-1 {
    opacity: 0;
    animation: slideReveal 0.7s ease forwards;
    animation-delay: 1.4s;
}
.reveal-section-2 {
    opacity: 0;
    animation: slideReveal 0.7s ease forwards;
    animation-delay: 1.8s;
}
.reveal-section-3 {
    opacity: 0;
    animation: slideReveal 0.7s ease forwards;
    animation-delay: 2.2s;
}
.reveal-section-4 {
    opacity: 0;
    animation: slideReveal 0.7s ease forwards;
    animation-delay: 2.6s;
}
.reveal-section-5 {
    opacity: 0;
    animation: slideReveal 0.7s ease forwards;
    animation-delay: 3.0s;
}
.reveal-section-6 {
    opacity: 0;
    animation: slideReveal 0.7s ease forwards;
    animation-delay: 3.4s;
}
.reveal-section-7 {
    opacity: 0;
    animation: slideReveal 0.7s ease forwards;
    animation-delay: 3.8s;
}

/* Shockwave overlay */
.shockwave-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 9999;
}
.shockwave-ring {
    position: absolute;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 3px solid rgba(167,139,250,0.8);
    top: -50px;
    left: -50px;
    animation: shockwaveRing 1.5s ease-out forwards;
}
.shockwave-ring:nth-child(2) { animation-delay: 0.2s; border-color: rgba(96,165,250,0.6); }
.shockwave-ring:nth-child(3) { animation-delay: 0.4s; border-color: rgba(244,114,182,0.4); }

/* Loading oracle animation */
.oracle-loading-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    padding: 4rem 0;
}
.oracle-orb {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, rgba(167,139,250,0.9), rgba(96,165,250,0.5), rgba(13,13,28,0.8));
    border: 2px solid rgba(167,139,250,0.4);
    box-shadow:
        0 0 40px rgba(167,139,250,0.5),
        0 0 80px rgba(96,165,250,0.3),
        inset 0 0 40px rgba(167,139,250,0.2);
    margin-bottom: 2rem;
    position: relative;
    animation: borderPulse 2s ease-in-out infinite;
}
.oracle-orb::before {
    content: '✦';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 2.5rem;
    color: rgba(255,255,255,0.9);
    animation: oracleOrb 3s cubic-bezier(0.25, 0.46, 0.45, 0.94) infinite;
}
.oracle-orb::after {
    content: '';
    position: absolute;
    inset: -15px;
    border-radius: 50%;
    border: 1px solid rgba(167,139,250,0.2);
    animation: shockwaveRing 2s ease-out infinite;
}
.loading-phase {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: rgba(167,139,250,0.8);
    font-size: 1rem;
    text-align: center;
    min-height: 1.5rem;
    animation: fadeGlow 0.5s ease;
}
.loading-dots {
    display: inline-flex;
    gap: 6px;
    margin-top: 1rem;
}
.loading-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(167,139,250,0.6);
    animation: particleBurst 1.2s ease-in-out infinite;
}
.loading-dot:nth-child(2) { animation-delay: 0.2s; background: rgba(96,165,250,0.6); }
.loading-dot:nth-child(3) { animation-delay: 0.4s; background: rgba(244,114,182,0.6); }

/* Scan line effect on reveal */
.scan-line {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,0.8), rgba(96,165,250,0.8), transparent);
    animation: scanLine 1.5s ease-in 0s forwards;
    z-index: 9998;
    pointer-events: none;
}

.oracle-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: clamp(1.8rem, 5vw, 3rem);
    background: linear-gradient(135deg, #e8e8f0 0%, #a78bfa 50%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    line-height: 1.3;
    margin-bottom: 0.5rem;
}
.oracle-sub {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: #8b8bad;
    text-align: center;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

.card {
    background: rgba(13,13,28,0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
}
.card-glow {
    background: rgba(13,13,28,0.7);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 18px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 0 30px rgba(167,139,250,0.06);
}

.landing-icon {
    font-size: 3.5rem;
    display: block;
    margin: 0 auto 1rem;
    animation: floatIcon 3s ease-in-out infinite;
    filter: drop-shadow(0 0 20px rgba(167,139,250,0.7));
    text-align: center;
}

.input-wrapper {
    background: rgba(13,13,28,0.7);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 18px;
    padding: 1.5rem 1.75rem 1.25rem;
    margin: 0 auto 1.25rem;
    max-width: 420px;
    box-shadow: 0 0 30px rgba(167,139,250,0.06);
}

.progress-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 100px;
    height: 3px;
    margin-bottom: 1.5rem;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    transition: width 0.4s ease;
}

.question-card {
    background: rgba(13,13,28,0.75);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 1.5rem;
}
.question-category {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: #a78bfa;
    margin-bottom: 0.5rem;
}
.question-text {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.1rem, 2.5vw, 1.5rem);
    line-height: 1.4;
    color: #e8e8f0;
}

.archetype-hero {
    text-align: center;
    padding: 2.5rem 1rem;
    background: rgba(13,13,28,0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(167,139,250,0.18);
    border-radius: 22px;
    margin-bottom: 1.25rem;
    box-shadow: 0 0 60px rgba(167,139,250,0.08);
}
.archetype-aura {
    font-size: 4rem;
    margin-bottom: 1rem;
    display: block;
    filter: drop-shadow(0 0 25px rgba(167,139,250,0.7));
}
.archetype-name {
    font-family: 'Cinzel Decorative', serif;
    font-size: clamp(1.3rem, 4vw, 2.2rem);
    background: linear-gradient(135deg, #ffffff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.75rem;
    line-height: 1.3;
}
.essence-quote {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: #8b8ba8;
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 1.25rem;
}
.traits-wrap {
    display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-top: 0.75rem;
}
.trait-chip {
    display: inline-block;
    padding: 0.3rem 0.9rem;
    background: rgba(167,139,250,0.12);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 100px;
    font-size: 0.8rem;
    color: #a78bfa;
    letter-spacing: 0.05em;
}

.stat-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; }
.stat-label { font-size: 0.75rem; color: #6b6b8a; width: 80px; flex-shrink: 0; text-transform: uppercase; letter-spacing: 0.08em; }
.stat-bar-bg { flex: 1; height: 6px; background: rgba(255,255,255,0.06); border-radius: 100px; overflow: hidden; }
.stat-bar-fill { height: 100%; border-radius: 100px; background: linear-gradient(90deg, #a78bfa, #60a5fa); }
.stat-val { font-size: 0.8rem; width: 28px; text-align: right; color: #e8e8f0; }

.duality-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 0;
    border: 1px solid rgba(255,255,255,0.07); border-radius: 18px; overflow: hidden; margin-bottom: 1.25rem;
}
.duality-side { padding: 1.5rem; text-align: center; backdrop-filter: blur(12px); }
.duality-light { background: rgba(251,191,36,0.06); border-right: 1px solid rgba(255,255,255,0.07); }
.duality-shadow { background: rgba(168,85,247,0.07); }
.duality-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 0.5rem; }
.duality-light .duality-label { color: #fbbf24; }
.duality-shadow .duality-label { color: #a78bfa; }
.duality-name { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 1.05rem; margin-bottom: 0.75rem; color: #e8e8f0; }
.duality-trait { font-size: 0.85rem; color: #6b6b8a; margin-bottom: 0.25rem; }

.trading-card {
    background: linear-gradient(135deg, rgba(13,13,28,0.9), rgba(26,26,46,0.9));
    backdrop-filter: blur(20px);
    border-radius: 20px; padding: 1.75rem;
    max-width: 320px; margin: 0 auto;
    text-align: center;
}
.card-rarity { font-size: 0.7rem; letter-spacing: 0.2em; color: #fbbf24; text-transform: uppercase; margin-bottom: 0.75rem; }
.card-emoji { font-size: 3rem; margin-bottom: 0.75rem; display: block; filter: drop-shadow(0 0 12px rgba(167,139,250,0.6)); }
.card-name { font-family: 'Cinzel Decorative', serif; font-size: 0.85rem; margin-bottom: 1.25rem; background: linear-gradient(135deg, #fff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.card-rare-badge { font-size: 0.7rem; color: #fbbf24; margin-top: 1rem; letter-spacing: 0.1em; }

.quote-block {
    background: rgba(13,13,28,0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #a78bfa;
    border-radius: 0 18px 18px 0;
    padding: 2rem; margin-bottom: 1.25rem; position: relative;
}
.quote-mark { font-size: 5rem; color: rgba(167,139,250,0.08); font-family: 'Playfair Display', serif; line-height: 0.5; position: absolute; top: 1.5rem; left: 1rem; }
.quote-text { font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.15rem; line-height: 1.7; color: #e8e8f0; position: relative; z-index: 1; padding-left: 1rem; margin-bottom: 0.75rem; }
.quote-source { font-size: 0.75rem; color: #6b6b8a; text-transform: uppercase; letter-spacing: 0.15em; padding-left: 1rem; }

.sw-item { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; font-size: 0.9rem; line-height: 1.5; color: #c8c8d8; }
.dot-green { color: #4ade80; flex-shrink: 0; }
.dot-red { color: #f87171; flex-shrink: 0; }

.future-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.15em; color: #60a5fa; margin-bottom: 0.3rem; }
.future-name { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem; color: #e8e8f0; }
.future-desc { color: #8b8ba8; font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.25rem; }

.portfolio-hero {
    background: rgba(167,139,250,0.07);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 18px; padding: 2rem; text-align: center; margin-bottom: 1.25rem;
}
.port-headline { font-family: 'Cinzel Decorative', serif; font-size: clamp(1.1rem, 3vw, 1.7rem); background: linear-gradient(135deg, #fff, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem; line-height: 1.3; }
.port-tagline { font-family: 'Playfair Display', serif; font-style: italic; color: #6b6b8a; font-size: 0.95rem; }
.port-block { margin-bottom: 1.5rem; }
.port-block-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.2em; color: #a78bfa; margin-bottom: 0.5rem; font-weight: 600; }
.port-text { font-size: 0.93rem; line-height: 1.8; color: rgba(232,232,240,0.85); }
.sp-item { display: flex; gap: 0.75rem; margin-bottom: 0.75rem; align-items: flex-start; }
.sp-icon { width: 30px; height: 30px; border-radius: 8px; background: rgba(167,139,250,0.15); border: 1px solid rgba(167,139,250,0.3); display: flex; align-items: center; justify-content: center; font-size: 0.9rem; flex-shrink: 0; padding-top: 5px; }
.sp-text { font-size: 0.9rem; line-height: 1.5; color: rgba(232,232,240,0.85); padding-top: 0.35rem; }
.sig-move { background: rgba(251,191,36,0.06); border: 1px solid rgba(251,191,36,0.2); border-radius: 12px; padding: 1rem 1.25rem; font-style: italic; font-family: 'Playfair Display', serif; font-size: 1rem; color: rgba(232,232,240,0.9); }

.section-divider {
    display: flex; align-items: center; gap: 1rem;
    margin: 2rem 0; color: #3a3a5a; font-size: 0.7rem;
    text-transform: uppercase; letter-spacing: 0.2em;
}
.section-divider::before, .section-divider::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.06); }

div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div { gap: 0.75rem; flex-direction: column; }
div[data-testid="stRadio"] > div > label {
    background: rgba(13,13,28,0.7) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    padding: 1rem 1.25rem !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
div[data-testid="stRadio"] > div > label:hover {
    border-color: rgba(167,139,250,0.5) !important;
    background: rgba(167,139,250,0.08) !important;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    border: none !important;
    border-radius: 100px !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s !important;
    width: 100%;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 0 30px rgba(124,58,237,0.4) !important;
}
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #f59e0b, #fbbf24) !important;
    border: none !important;
    border-radius: 100px !important;
    color: #000 !important;
    font-weight: 700 !important;
    padding: 0.6rem 2rem !important;
    width: 100%;
}
div[data-testid="stTextInput"] > div > div > input {
    background: rgba(13,13,28,0.8) !important;
    border: 1px solid rgba(167,139,250,0.25) !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
    backdrop-filter: blur(8px) !important;
}
div[data-testid="stTextInput"] > label {
    color: rgba(167,139,250,0.7) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)


# ─── ANTHROPIC API ────────────────────────────────────────────────────────────
def call_groq(answers: dict, user_name: str) -> dict:
    answer_lines = []
    for q in QUESTIONS:
        ans_idx = answers.get(q["id"])
        if ans_idx is not None:
            chosen = q["options"][ans_idx]
            answer_lines.append(f'Q{q["id"]} ({q["category"]}): "{q["question"]}" -> "{chosen.strip()}"')

    prompt = f"""You are a deeply insightful personality oracle. The user's name is {user_name}. Analyze these answers and generate a rich, cinematic personality profile.

ANSWERS:
{chr(10).join(answer_lines)}

Return ONLY a valid JSON object (no markdown, no code blocks):
{{
  "archetype_name": "The [Evocative Title]",
  "essence_quote": "One deeply personal one-liner",
  "aura_color": "#hexcode matching their energy",
  "aura_color2": "#second hex for gradient (complementary)",
  "aura_emoji": "one emoji representing their energy",
  "rarity": "LEGENDARY or RARE or UNCOMMON or COMMON",
  "rarity_percentage": "X%",
  "traits": ["Trait1","Trait2","Trait3","Trait4"],
  "strengths": ["Strength one","Strength two","Strength three"],
  "weaknesses": ["Shadow trait one","Shadow trait two","Shadow trait three"],
  "future": {{
    "career_tendencies": "2 sentence career description",
    "leadership_style_name": "The [Name]",
    "leadership_style_desc": "One sentence",
    "learning_style": "2 sentence learning description"
  }},
  "personal_quote": "A 2-3 line cinematic quote",
  "light_side": {{
    "name": "The [Light Archetype]",
    "traits": ["Trait 1","Trait 2","Trait 3"]
  }},
  "shadow_side": {{
    "name": "The [Shadow Archetype]",
    "traits": ["Trait 1","Trait 2","Trait 3"]
  }},
  "stats": {{
    "creativity": 75,
    "empathy": 68,
    "chaos": 82,
    "logic": 71,
    "intuition": 88
  }},
  "pdf_theme": "calm or bold or mystical or energetic (choose based on personality)",
  "portfolio": {{
    "headline": "5-7 word personal brand statement",
    "tagline": "One evocative sentence",
    "about": "3-4 sentences first person, deeply personal",
    "superpowers": ["Superpower 1 -- one sentence","Superpower 2 -- one sentence","Superpower 3 -- one sentence"],
    "life_philosophy": "2-3 sentences worldview",
    "ideal_environment": "2 sentences where they thrive",
    "growth_edge": "2 sentences growth opportunity",
    "signature_move": "One sentence unique to them"
  }}
}}"""

    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError(
            "No Groq API key found. Add GROQ_API_KEY to .streamlit/secrets.toml "
            "or set it as an environment variable before running."
        )

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.9,
            "max_tokens": 2000,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise ValueError(resp.json().get("error", {}).get("message", "Groq API error"))

    content = resp.json()["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content.strip())


# ─── PDF GENERATOR ─────────────────────────────────────────────────────────────
def hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return (100, 80, 200)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def strip_emoji(text: str) -> str:
    result = []
    for ch in str(text):
        cp = ord(ch)
        if cp < 256:
            result.append(ch)
    return "".join(result).strip()

def build_pdf(p: dict, user_name: str) -> bytes:
    port   = p.get("portfolio", {})
    theme  = p.get("pdf_theme", "mystical")
    stats  = p.get("stats", {})
    future = p.get("future", {})
    aura1  = p.get("aura_color", "#7c3aed")
    aura2  = p.get("aura_color2", "#2563eb")
    r1, g1, b1 = hex_to_rgb(aura1)
    r2, g2, b2 = hex_to_rgb(aura2)

    themes = {
        "calm":     {"bg": (245, 248, 252), "bg2": (235, 242, 250), "ink": (30, 35, 60),   "muted": (100, 110, 140), "accent_light": (220, 230, 250)},
        "bold":     {"bg": (252, 248, 242), "bg2": (248, 238, 225), "ink": (35, 25, 20),   "muted": (120, 100, 85),  "accent_light": (250, 230, 210)},
        "mystical": {"bg": (246, 244, 252), "bg2": (238, 234, 252), "ink": (30, 20, 55),   "muted": (100, 85, 135),  "accent_light": (225, 218, 252)},
        "energetic":{"bg": (248, 252, 246), "bg2": (232, 248, 238), "ink": (20, 45, 30),   "muted": (80, 120, 90),   "accent_light": (210, 245, 220)},
    }
    t = themes.get(theme, themes["mystical"])

    class PortfolioPDF(FPDF):
        def header(self): pass
        def footer(self): pass

    pdf = PortfolioPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    W, H = 210, 297

    def draw_bg(pdf, page_num):
        pdf.set_fill_color(*t["bg"])
        pdf.rect(0, 0, W, H, "F")

        def blend(c1, c2, ratio):
            return tuple(int(c1[i] * (1-ratio) + c2[i] * ratio) for i in range(3))

        circle_color = blend(t["bg"], (r1, g1, b1), 0.12)
        pdf.set_fill_color(*circle_color)
        for i in range(5):
            size = 80 - i * 10
            pdf.ellipse(-size//2, -size//2, size, size, "F")

        circle_color2 = blend(t["bg"], (r2, g2, b2), 0.10)
        pdf.set_fill_color(*circle_color2)
        for i in range(4):
            size = 60 - i * 8
            pdf.ellipse(W - size//2, H - size//2, size, size, "F")

        pdf.set_fill_color(r1, g1, b1)
        pdf.rect(0, 0, W, 1.5, "F")
        pdf.set_fill_color(r2, g2, b2)
        pdf.rect(0, 1.5, W, 0.6, "F")
        pdf.set_fill_color(r1, g1, b1)
        pdf.rect(0, H - 1.5, W, 1.5, "F")

        left_sb = blend(t["bg"], (r1, g1, b1), 0.07)
        pdf.set_fill_color(*left_sb)
        pdf.rect(0, 0, 42, H, "F")
        pdf.set_draw_color(r1, g1, b1)
        pdf.set_line_width(0.3)
        pdf.line(42, 0, 42, H)

        if page_num == 2:
            pdf.set_draw_color(*t["muted"])
            pdf.set_line_width(0.12)
            for i in range(0, 50, 10):
                pdf.line(W - 50 + i, 0, W, 50 - i)

    pdf.add_page()
    draw_bg(pdf, 1)

    pdf.set_xy(2, 14)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(r1, g1, b1)
    pdf.cell(38, 12, "*", align="C", ln=True)

    pdf.set_xy(2, 30)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(r1, g1, b1)
    pdf.multi_cell(38, 5, strip_emoji(user_name.upper()), align="C")

    pdf.set_draw_color(r1, g1, b1)
    pdf.set_line_width(0.4)
    yy = pdf.get_y() + 2
    pdf.line(6, yy, 36, yy)

    pdf.set_xy(2, yy + 4)
    pdf.set_font("Helvetica", "I", 6)
    pdf.set_text_color(*t["muted"])
    pdf.multi_cell(38, 4, strip_emoji(p.get("archetype_name", "")), align="C")

    yy = pdf.get_y() + 3
    pdf.set_draw_color(*t["muted"])
    pdf.set_line_width(0.15)
    pdf.line(6, yy, 36, yy)

    pdf.set_xy(2, yy + 3)
    pdf.set_font("Helvetica", "B", 5.5)
    pdf.set_text_color(r1, g1, b1)
    pdf.multi_cell(38, 3.5, f"{strip_emoji(p.get('rarity','LEGENDARY'))}\n{p.get('rarity_percentage','4%')} of people", align="C")

    yy = pdf.get_y() + 3
    pdf.set_draw_color(*t["muted"])
    pdf.line(6, yy, 36, yy)

    pdf.set_xy(2, yy + 3)
    pdf.set_font("Helvetica", "", 5.5)
    pdf.set_text_color(*t["muted"])
    for tr in p.get("traits", []):
        pdf.set_xy(2, pdf.get_y())
        pdf.cell(38, 5, strip_emoji(f"* {tr}"), align="C", ln=True)

    yy = pdf.get_y() + 4
    pdf.set_draw_color(*t["muted"])
    pdf.set_line_width(0.15)
    pdf.line(6, yy, 36, yy)
    pdf.set_xy(2, yy + 3)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_text_color(r1, g1, b1)
    pdf.cell(38, 4, "POWER STATS", align="C", ln=True)

    bar_x = 5
    bar_max = 30
    sy = pdf.get_y() + 2
    for stat_name, val in stats.items():
        if sy > H - 20:
            break
        pdf.set_xy(2, sy)
        pdf.set_font("Helvetica", "", 5.5)
        pdf.set_text_color(*t["muted"])
        pdf.cell(38, 3, stat_name.capitalize(), align="C", ln=True)
        sy = pdf.get_y()
        def blend_local(c1, c2, r): return tuple(int(c1[i]*(1-r)+c2[i]*r) for i in range(3))
        pdf.set_fill_color(*t["accent_light"])
        pdf.rect(bar_x, sy, bar_max, 3, "F")
        fill = bar_max * val / 100
        half = fill / 2
        pdf.set_fill_color(r1, g1, b1)
        pdf.rect(bar_x, sy, half, 3, "F")
        pdf.set_fill_color(r2, g2, b2)
        pdf.rect(bar_x + half, sy, fill - half, 3, "F")
        pdf.set_xy(bar_x + bar_max + 1, sy)
        pdf.set_font("Helvetica", "B", 5)
        pdf.set_text_color(*t["ink"])
        pdf.cell(6, 3, str(val))
        sy += 6

    margin_l = 47
    col_gap = 5
    col_w = (W - margin_l - col_gap - 8) / 2
    c1x = margin_l
    c2x = margin_l + col_w + col_gap

    def section_hdr(x, y, text, w):
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(r1, g1, b1)
        pdf.cell(w, 3.5, strip_emoji(text).upper(), ln=True)
        pdf.set_draw_color(r1, g1, b1)
        pdf.set_line_width(0.25)
        pdf.line(x, y + 4, x + w * 0.45, y + 4)
        return y + 7

    def body(x, y, text, w, size=7):
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(*t["ink"])
        pdf.multi_cell(w, 4, strip_emoji(text))
        return pdf.get_y() + 1.5

    def bullets(x, y, items, w, bullet="-"):
        safe_bullet = strip_emoji(bullet)
        if not safe_bullet:
            safe_bullet = "-"
        for item in items:
            pdf.set_xy(x, y)
            pdf.set_font("Helvetica", "", 6.5)
            pdf.set_text_color(r1, g1, b1)
            pdf.cell(4, 4, safe_bullet)
            pdf.set_xy(x + 4, y)
            pdf.set_text_color(*t["ink"])
            pdf.multi_cell(w - 4, 4, strip_emoji(item))
            y = pdf.get_y() + 0.5
        return y + 1.5

    pdf.set_fill_color(*t["accent_light"])
    pdf.rect(margin_l - 3, 8, W - margin_l - 3, 13, "F")
    pdf.set_xy(margin_l, 9)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*t["ink"])
    pdf.multi_cell(W - margin_l - 6, 4.5, f'"{strip_emoji(p.get("essence_quote",""))}"', align="C")

    start_y = 26

    cy1 = start_y
    cy1 = section_hdr(c1x, cy1, "About Me", col_w)
    cy1 = body(c1x, cy1, port.get("about", ""), col_w)
    cy1 = section_hdr(c1x, cy1, "Strengths", col_w)
    cy1 = bullets(c1x, cy1, p.get("strengths", []), col_w, "+")
    cy1 = section_hdr(c1x, cy1, "Shadow Traits", col_w)
    cy1 = bullets(c1x, cy1, p.get("weaknesses", []), col_w, "o")
    cy1 = section_hdr(c1x, cy1, "Superpowers", col_w)
    cy1 = bullets(c1x, cy1, port.get("superpowers", []), col_w, "~")

    cy2 = start_y
    cy2 = section_hdr(c2x, cy2, "Career Path", col_w)
    cy2 = body(c2x, cy2, future.get("career_tendencies", ""), col_w)
    cy2 = section_hdr(c2x, cy2, future.get("leadership_style_name", "Leadership"), col_w)
    cy2 = body(c2x, cy2, future.get("leadership_style_desc", ""), col_w)
    cy2 = section_hdr(c2x, cy2, "How I Learn", col_w)
    cy2 = body(c2x, cy2, future.get("learning_style", ""), col_w)
    cy2 = section_hdr(c2x, cy2, "Life Philosophy", col_w)
    cy2 = body(c2x, cy2, port.get("life_philosophy", ""), col_w)
    cy2 = section_hdr(c2x, cy2, "Where I Thrive", col_w)
    cy2 = body(c2x, cy2, port.get("ideal_environment", ""), col_w)

    q_y = max(cy1, cy2) + 4
    if q_y < H - 22:
        pdf.set_fill_color(*t["accent_light"])
        pdf.set_draw_color(r1, g1, b1)
        pdf.set_line_width(0.7)
        pdf.rect(margin_l - 3, q_y, W - margin_l - 3, 16, "F")
        pdf.line(margin_l - 3, q_y, margin_l - 3, q_y + 16)
        pdf.set_xy(margin_l, q_y + 2)
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*t["ink"])
        pdf.multi_cell(W - margin_l - 6, 4.5, f'"{strip_emoji(p.get("personal_quote",""))}"', align="C")

    pdf.set_xy(0, H - 7)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*t["muted"])
    pdf.cell(W, 5, "1 / 2", align="C")

    pdf.add_page()
    draw_bg(pdf, 2)

    pdf.set_xy(2, 14)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(r1, g1, b1)
    pdf.cell(38, 4, "PROFILE", align="C", ln=True)
    pdf.set_draw_color(r1, g1, b1)
    pdf.set_line_width(0.3)
    pdf.line(5, 19, 37, 19)

    pdf.set_xy(2, 22)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(r1, g1, b1)
    pdf.multi_cell(38, 4.5, strip_emoji(user_name.upper()), align="C")

    pdf.set_xy(2, pdf.get_y() + 1)
    pdf.set_font("Helvetica", "I", 5.5)
    pdf.set_text_color(*t["muted"])
    pdf.multi_cell(38, 3.5, strip_emoji(p.get("archetype_name", "")), align="C")

    yy2 = pdf.get_y() + 3
    pdf.set_draw_color(*t["muted"])
    pdf.set_line_width(0.15)
    pdf.line(5, yy2, 37, yy2)

    pdf.set_xy(2, yy2 + 2)
    pdf.set_font("Helvetica", "B", 6)
    pdf.set_text_color(r1, g1, b1)
    pdf.cell(38, 4, "POWER STATS", align="C", ln=True)

    sy = pdf.get_y() + 1
    bar_x = 4
    bar_max = 30
    for stat_name, val in stats.items():
        if sy > H - 60:
            break
        pdf.set_xy(2, sy)
        pdf.set_font("Helvetica", "", 5.5)
        pdf.set_text_color(*t["muted"])
        pdf.cell(38, 3, stat_name.capitalize(), align="C", ln=True)
        sy = pdf.get_y()
        pdf.set_fill_color(*t["accent_light"])
        pdf.rect(bar_x, sy, bar_max, 3, "F")
        fill = bar_max * val / 100
        half = fill / 2
        pdf.set_fill_color(r1, g1, b1)
        pdf.rect(bar_x, sy, half, 3, "F")
        pdf.set_fill_color(r2, g2, b2)
        pdf.rect(bar_x + half, sy, fill - half, 3, "F")
        pdf.set_xy(bar_x + bar_max + 1, sy)
        pdf.set_font("Helvetica", "B", 5)
        pdf.set_text_color(*t["ink"])
        pdf.cell(6, 3, str(val))
        sy += 6

    yy2 = sy + 3
    pdf.set_draw_color(*t["muted"])
    pdf.set_line_width(0.15)
    pdf.line(5, yy2, 37, yy2)

    pdf.set_xy(2, yy2 + 3)
    pdf.set_font("Helvetica", "B", 5.5)
    pdf.set_text_color(r1, g1, b1)
    pdf.cell(38, 3.5, "SIGNATURE MOVE", align="C", ln=True)
    pdf.set_xy(2, pdf.get_y() + 1)
    pdf.set_font("Helvetica", "I", 5.5)
    pdf.set_text_color(*t["ink"])
    pdf.multi_cell(38, 3.5, strip_emoji(port.get("signature_move", "")), align="C")

    pdf.set_xy(margin_l, 8)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*t["ink"])
    pdf.cell(W - margin_l - 4, 7, strip_emoji(port.get("headline", "")), align="C", ln=True)
    pdf.set_xy(margin_l, 16)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*t["muted"])
    pdf.cell(W - margin_l - 4, 5, strip_emoji(port.get("tagline", "")), align="C", ln=True)

    pdf.set_draw_color(r1, g1, b1)
    pdf.set_line_width(0.5)
    mid_x = (margin_l + W) / 2
    pdf.line(mid_x - 25, 22, mid_x + 25, 22)

    start_y2 = 28
    cy1 = start_y2
    cy2 = start_y2

    cy1 = section_hdr(c1x, cy1, "My Duality", col_w)
    light  = p.get("light_side", {})
    shadow = p.get("shadow_side", {})

    lbox_h = 22
    pdf.set_fill_color(*t["accent_light"])
    pdf.rect(c1x, cy1, col_w, lbox_h, "F")
    pdf.set_xy(c1x + 1, cy1 + 1)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(180, 140, 20)
    pdf.cell(col_w - 2, 4, strip_emoji(f"[Light] {light.get('name','')}"), ln=True)
    for tr in light.get("traits", []):
        pdf.set_xy(c1x + 3, pdf.get_y())
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*t["ink"])
        pdf.cell(col_w - 4, 4, strip_emoji(f"- {tr}"), ln=True)
    cy1 = max(pdf.get_y() + 2, cy1 + lbox_h + 2)

    darker_accent = tuple(min(c + 8, 255) for c in t["accent_light"])
    pdf.set_fill_color(*darker_accent)
    pdf.rect(c1x, cy1, col_w, lbox_h, "F")
    pdf.set_xy(c1x + 1, cy1 + 1)
    pdf.set_font("Helvetica", "B", 6.5)
    pdf.set_text_color(r1, g1, b1)
    pdf.cell(col_w - 2, 4, strip_emoji(f"[Shadow] {shadow.get('name','')}"), ln=True)
    for tr in shadow.get("traits", []):
        pdf.set_xy(c1x + 3, pdf.get_y())
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*t["ink"])
        pdf.cell(col_w - 4, 4, strip_emoji(f"- {tr}"), ln=True)
    cy1 = max(pdf.get_y() + 3, cy1 + lbox_h + 3)

    cy1 = section_hdr(c1x, cy1, "Growth Edge", col_w)
    cy1 = body(c1x, cy1, port.get("growth_edge", ""), col_w)
    cy1 = section_hdr(c1x, cy1, "Life Philosophy", col_w)
    cy1 = body(c1x, cy1, port.get("life_philosophy", ""), col_w)

    cy2 = section_hdr(c2x, cy2, "Career Tendencies", col_w)
    cy2 = body(c2x, cy2, future.get("career_tendencies", ""), col_w)
    cy2 = section_hdr(c2x, cy2, future.get("leadership_style_name", "Leadership"), col_w)
    cy2 = body(c2x, cy2, future.get("leadership_style_desc", ""), col_w)
    cy2 = section_hdr(c2x, cy2, "How I Learn", col_w)
    cy2 = body(c2x, cy2, future.get("learning_style", ""), col_w)
    cy2 = section_hdr(c2x, cy2, "Ideal Environment", col_w)
    cy2 = body(c2x, cy2, port.get("ideal_environment", ""), col_w)
    cy2 = section_hdr(c2x, cy2, "About Me", col_w)
    cy2 = body(c2x, cy2, port.get("about", ""), col_w)

    pdf.set_xy(margin_l, H - 10)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*t["muted"])
    pdf.cell((W - margin_l) / 2, 5, f"Generated {datetime.now().strftime('%B %Y')}  -  Personality Oracle", align="L")
    pdf.set_xy(margin_l + (W - margin_l) / 2, H - 10)
    pdf.cell((W - margin_l) / 2, 5, "2 / 2", align="R")

    return bytes(pdf.output())


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def divider(text: str):
    st.markdown(f'<div class="section-divider">{text}</div>', unsafe_allow_html=True)


LOADING_PHASES = [
    "Mapping your cosmic fingerprint...",
    "Decoding your decision patterns...",
    "Consulting the stars...",
    "Unveiling your archetype...",
    "Crystallizing your essence...",
]


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: LANDING
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.markdown("""
    <div style="text-align:center; padding: 3rem 0 1rem;">
      <span class="landing-icon">✦</span>
      <div class="oracle-title">Personality Oracle</div>
      <div class="oracle-sub">Seven questions. One mirror.<br>The profile you've always known existed but never saw written down.</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        name = st.text_input(
            "Your name",
            placeholder="Enter your name to begin...",
            value=st.session_state.user_name,
            label_visibility="collapsed",
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Begin My Reading ✦", use_container_width=True):
            if not name.strip():
                st.error("Please enter your name to begin.")
            else:
                st.session_state.user_name = name.strip()
                st.session_state.page = "quiz"
                st.session_state.current_q = 0
                st.session_state.answers = {}
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: QUIZ
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "quiz":

    cq    = st.session_state.current_q
    q     = QUESTIONS[cq]
    total = len(QUESTIONS)
    pct   = int((cq / total) * 100)

    st.markdown(f"""
    <div class="progress-wrap">
      <div class="progress-fill" style="width:{pct}%"></div>
    </div>
    <div class="question-card">
      <div class="question-category">✦ {q["category"]}  —  Question {cq+1} of {total}</div>
      <div class="question-text">{q["question"]}</div>
    </div>
    """, unsafe_allow_html=True)

    selected = st.radio(
        "Choose your answer",
        options=q["options"],
        index=st.session_state.answers.get(q["id"], 0),
        key=f"radio_{cq}",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_spacer, col_next = st.columns([1, 2, 1])

    with col_back:
        if cq > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state.answers[q["id"]] = q["options"].index(selected)
                st.session_state.current_q -= 1
                st.rerun()

    with col_next:
        label = "Continue →" if cq < total - 1 else "Reveal My Oracle ✦"
        if st.button(label, use_container_width=True):
            st.session_state.answers[q["id"]] = q["options"].index(selected)
            if cq < total - 1:
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.session_state.page = "results"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: RESULTS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "results":

    if st.session_state.profile is None:
        # ── CINEMATIC LOADING SCREEN ──────────────────────────────────────────
        st.markdown(f"""
        <div class="oracle-loading-wrap">
          <div class="oracle-orb"></div>
          <div class="oracle-title" style="font-size:1.6rem; margin-bottom:0.5rem;">
            Reading {st.session_state.user_name}...
          </div>
        </div>
        """, unsafe_allow_html=True)

        phase_slot = st.empty()

        # Cycle through loading phases while the API call happens
        # We launch the API call and animate simultaneously using a thread-free approach:
        # show phases for a beat, then call API, continue animating via rerun if needed.

        phase_slot.markdown(f"""
        <div style="text-align:center;">
          <div class="loading-phase">{LOADING_PHASES[0]}</div>
          <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        try:
            import threading

            # Capture from session_state BEFORE entering the thread —
            # Streamlit session_state is not thread-safe.
            answers_snapshot = dict(st.session_state.get("answers", {}))
            name_snapshot    = str(st.session_state.get("user_name", ""))

            profile_result = [None]
            error_result   = [None]

            def fetch_profile():
                try:
                    profile_result[0] = call_groq(answers_snapshot, name_snapshot)
                except Exception as e:
                    error_result[0] = e

            thread = threading.Thread(target=fetch_profile)
            thread.start()

            # Animate loading phases while API fetches
            phase_idx = 0
            while thread.is_alive():
                phase_slot.markdown(f"""
                <div style="text-align:center;">
                  <div class="loading-phase">{LOADING_PHASES[phase_idx % len(LOADING_PHASES)]}</div>
                  <div class="loading-dots">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                phase_idx += 1
                time.sleep(1.8)

            thread.join()

            if error_result[0] is not None:
                raise error_result[0]

            st.session_state.profile = profile_result[0]
            st.session_state.reveal_done = False
            st.rerun()

        except ValueError as e:
            st.error(f"API Error: {e}")
            if st.button("← Try Again"):
                st.session_state.page = "quiz"
                st.rerun()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            if st.button("← Try Again"):
                st.session_state.page = "quiz"
                st.rerun()

    else:
        p      = st.session_state.profile
        port   = p.get("portfolio", {})
        stats  = p.get("stats", {})
        future = p.get("future", {})
        aura   = p.get("aura_color", "#a78bfa")
        aura2  = p.get("aura_color2", "#60a5fa")
        emoji  = p.get("aura_emoji", "🌌")
        name   = st.session_state.user_name

        st.markdown(f"<style>:root{{--aura:{aura};--aura2:{aura2};}}</style>", unsafe_allow_html=True)

        # ── BLACKOUT → DRAMATIC REVEAL (only on first render after fetch) ───────
        if not st.session_state.get("reveal_done", False):
            st.markdown(f"""
            <style>
            #oracle-blackout {{
                position: fixed; inset: 0; background: #000;
                z-index: 99999; pointer-events: none;
                animation: blackoutFade 0.6s ease-out 1.2s forwards;
            }}
            @keyframes blackoutFade {{
                0%   {{ opacity: 1; }}
                100% {{ opacity: 0; pointer-events: none; }}
            }}
            #oracle-burst {{
                position: fixed; inset: 0; z-index: 99998; pointer-events: none;
                background: radial-gradient(circle at 50% 50%, {aura}cc 0%, {aura2}66 25%, transparent 70%);
                opacity: 0;
                animation: burstFlash 0.7s ease-out 1.2s forwards;
            }}
            @keyframes burstFlash {{
                0%   {{ opacity: 0; transform: scale(0.3); }}
                30%  {{ opacity: 1; transform: scale(1.1); }}
                100% {{ opacity: 0; transform: scale(2);   }}
            }}
            #oracle-rings {{ position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%); pointer-events: none; z-index: 99997; }}
            .o-ring {{
                position: absolute; width: 140px; height: 140px;
                border-radius: 50%; top: -70px; left: -70px;
                opacity: 0; border: 2px solid {aura};
            }}
            .o-ring:nth-child(1) {{ animation: shockRing 1.2s ease-out 1.2s forwards; border-color: {aura}; }}
            .o-ring:nth-child(2) {{ animation: shockRing 1.2s ease-out 1.4s forwards; border-color: {aura2}; }}
            .o-ring:nth-child(3) {{ animation: shockRing 1.2s ease-out 1.6s forwards; border-color: #f0abfc; }}
            @keyframes shockRing {{
                0%   {{ transform: scale(0); opacity: 1; }}
                100% {{ transform: scale(7); opacity: 0; }}
            }}
            #oracle-scan {{
                position: fixed; top: 0; left: 0; width: 100%; height: 3px;
                background: linear-gradient(90deg, transparent, {aura}, {aura2}, transparent);
                z-index: 99996; opacity: 0; pointer-events: none;
                animation: scanDown 1.0s ease-in 1.25s forwards;
            }}
            @keyframes scanDown {{
                0%   {{ top: 0; opacity: 1; }}
                90%  {{ opacity: 0.6; }}
                100% {{ top: 100vh; opacity: 0; }}
            }}
            </style>
            <div id="oracle-blackout"></div>
            <div id="oracle-burst"></div>
            <div id="oracle-rings">
              <div class="o-ring"></div>
              <div class="o-ring"></div>
              <div class="o-ring"></div>
            </div>
            <div id="oracle-scan"></div>
            """, unsafe_allow_html=True)
            st.session_state.reveal_done = True

        # ── HERO ──────────────────────────────────────────────────────────────
        traits_html = "".join([f'<span class="trait-chip">{t}</span>' for t in p.get("traits", [])])
        st.markdown(f"""
        <div class="archetype-hero reveal-hero" style="border-color:{aura}44; box-shadow: 0 0 80px {aura}22, 0 0 160px {aura}11;">
          <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.2em;color:#6b6b8a;margin-bottom:0.75rem;">
            ✦ {name}'s Reading ✦
          </div>
          <span class="archetype-aura">{emoji}</span>
          <div class="archetype-name">{p.get("archetype_name","")}</div>
          <div class="essence-quote">{p.get("essence_quote","")}</div>
          <div class="traits-wrap">{traits_html}</div>
          <div style="font-size:0.7rem;color:#fbbf24;margin-top:1rem;letter-spacing:0.1em;">
            ✦ {p.get("rarity","LEGENDARY")} — Only {p.get("rarity_percentage","4%")} share this type ✦
          </div>
        </div>""", unsafe_allow_html=True)

        # ── STRENGTHS & WEAKNESSES ────────────────────────────────────────────
        st.markdown('<div class="reveal-section-1">', unsafe_allow_html=True)
        divider("Your Nature")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col_s, col_w_col = st.columns(2)
        with col_s:
            st.markdown("<span style='color:#4ade80;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.15em;font-weight:600;'>Strengths</span>", unsafe_allow_html=True)
            for s in p.get("strengths", []):
                st.markdown(f'<div class="sw-item"><span class="dot-green">✓</span> {s}</div>', unsafe_allow_html=True)
        with col_w_col:
            st.markdown("<span style='color:#f87171;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.15em;font-weight:600;'>Shadow Traits</span>", unsafe_allow_html=True)
            for w in p.get("weaknesses", []):
                st.markdown(f'<div class="sw-item"><span class="dot-red">◦</span> {w}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        # ── FUTURE YOU ────────────────────────────────────────────────────────
        st.markdown('<div class="reveal-section-2">', unsafe_allow_html=True)
        divider("Future You")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="future-label">Career Trajectory</div><div class="future-desc">{future.get("career_tendencies","")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="future-label">Leadership Style</div><div class="future-name">{future.get("leadership_style_name","")}</div><div class="future-desc">{future.get("leadership_style_desc","")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="future-label">How You Learn</div><div class="future-desc" style="margin-bottom:0">{future.get("learning_style","")}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        # ── PERSONAL QUOTE ────────────────────────────────────────────────────
        st.markdown('<div class="reveal-section-3">', unsafe_allow_html=True)
        divider("Your Quote")
        st.markdown(f"""
        <div class="quote-block">
          <div class="quote-mark">"</div>
          <div class="quote-text">{p.get("personal_quote","")}</div>
          <div class="quote-source">— Your Personality Oracle</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── DUALITY ───────────────────────────────────────────────────────────
        st.markdown('<div class="reveal-section-4">', unsafe_allow_html=True)
        divider("Your Duality")
        light  = p.get("light_side", {})
        shadow = p.get("shadow_side", {})
        lt_html = "".join([f'<div class="duality-trait">{t}</div>' for t in light.get("traits", [])])
        sh_html = "".join([f'<div class="duality-trait">{t}</div>' for t in shadow.get("traits", [])])
        st.markdown(f"""
        <div class="duality-grid">
          <div class="duality-side duality-light">
            <div class="duality-label">☀ Light Side</div>
            <div class="duality-name">{light.get("name","")}</div>
            {lt_html}
          </div>
          <div class="duality-side duality-shadow">
            <div class="duality-label">☽ Shadow Side</div>
            <div class="duality-name">{shadow.get("name","")}</div>
            {sh_html}
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── TRADING CARD ──────────────────────────────────────────────────────
        st.markdown('<div class="reveal-section-5">', unsafe_allow_html=True)
        divider("Your Card")
        stat_html = "".join([
            f"""<div class="stat-row">
              <div class="stat-label">{k.capitalize()}</div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{v}%;background:linear-gradient(90deg,{aura},{aura2});"></div></div>
              <div class="stat-val">{v}</div>
            </div>"""
            for k, v in stats.items()
        ])
        st.markdown(f"""
        <div class="trading-card" style="border:2px solid {aura};box-shadow:0 0 40px {aura}44;">
          <div class="card-rarity">✦ {p.get("rarity","LEGENDARY")} ✦</div>
          <div class="card-emoji">{emoji}</div>
          <div class="card-name">{p.get("archetype_name","")}</div>
          {stat_html}
          <div class="card-rare-badge">✦ Only {p.get("rarity_percentage","4%")} share this type ✦</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── PORTFOLIO ─────────────────────────────────────────────────────────
        st.markdown('<div class="reveal-section-6">', unsafe_allow_html=True)
        divider("Your Portfolio")
        sp_icons = ["⚡", "🌊", "🔥"]
        sp_html = "".join([
            f'<div class="sp-item"><div class="sp-icon">{sp_icons[i] if i < 3 else "✦"}</div><div class="sp-text">{s}</div></div>'
            for i, s in enumerate(port.get("superpowers", []))
        ])
        st.markdown(f"""
        <div class="portfolio-hero">
          <div class="port-headline">{port.get("headline","")}</div>
          <div class="port-tagline">{port.get("tagline","")}</div>
        </div>
        <div class="card">
          <div class="port-block">
            <div class="port-block-label">About Me</div>
            <div class="port-text">{port.get("about","")}</div>
          </div>
          <div class="port-block">
            <div class="port-block-label">My Superpowers</div>
            {sp_html}
          </div>
          <div class="port-block">
            <div class="port-block-label">Life Philosophy</div>
            <div class="port-text">{port.get("life_philosophy","")}</div>
          </div>
          <div class="port-block">
            <div class="port-block-label">Where I Thrive</div>
            <div class="port-text">{port.get("ideal_environment","")}</div>
          </div>
          <div class="port-block">
            <div class="port-block-label">My Growth Edge</div>
            <div class="port-text">{port.get("growth_edge","")}</div>
          </div>
          <div class="port-block">
            <div class="port-block-label">My Signature Move</div>
            <div class="sig-move">{port.get("signature_move","")}</div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── ACTIONS ───────────────────────────────────────────────────────────
        st.markdown('<div class="reveal-section-7">', unsafe_allow_html=True)
        divider("Actions")

        pdf_bytes = build_pdf(p, name)
        pdf_filename = f"{name.lower().replace(' ','-')}-personality-portfolio.pdf"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="📄 Download PDF Portfolio",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True,
            )
        with col2:
            share_text = f'{name} — "{p.get("archetype_name","")}" ✦\n\n"{p.get("essence_quote","")}"'
            st.download_button(
                label="📋 Save Profile Text",
                data=share_text,
                file_name=f"{name.lower().replace(' ','-')}-profile.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col3:
            if st.button("🔄 Retake Quiz", use_container_width=True):
                st.session_state.profile = None
                st.session_state.answers = {}
                st.session_state.current_q = 0
                st.session_state.reveal_done = False
                st.session_state.page = "landing"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)