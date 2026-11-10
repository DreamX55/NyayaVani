/**
 * NyayaVani (न्यायवाणी) — Living Chromatic Sphere & Audio-Reactive Canvas
 *
 * Tier 1 (Free - Bharat Grassroots Aid):
 *   Primary: Coral Blue (#0ea5e9)
 *   Core: Ivory White (#fffff0)
 *   Accent: Electric Purple (#a855f7) (stardust particles & highlights only)
 *
 * Tier 2 (Pro - Enterprise Legal Suite):
 *   Primary: Solar Gold (#f59e0b)
 *   Surface: Obsidian Slate (#05070b)
 *   Accent: Emerald Green (#10b981) (stardust particles & highlights only)
 */

export const TIER_STATE_COLORS = {
  free: {
    idle: {
      primary: [14, 165, 233],     // Coral Blue (#0ea5e9)
      secondary: [15, 35, 65],     // Deep Coral Navy
      accent: [168, 85, 247],      // Electric Purple Accent (#a855f7)
      core: [255, 255, 240],       // Ivory White Core (#fffff0)
      glow: 'rgba(168, 85, 247, 0.35)'
    },
    listening: {
      primary: [255, 255, 240],    // Ivory White
      secondary: [2, 132, 199],    // Vibrant Coral Blue (#0284c7)
      accent: [192, 132, 252],     // Electric Purple Accent (#c084fc)
      core: [255, 255, 240],
      glow: 'rgba(192, 132, 252, 0.45)'
    },
    thinking: {
      primary: [168, 85, 247],     // Electric Purple Accent
      secondary: [14, 165, 233],   // Coral Blue
      accent: [255, 255, 240],     // Ivory White
      core: [255, 255, 240],
      glow: 'rgba(168, 85, 247, 0.5)'
    },
    speaking: {
      primary: [56, 189, 248],     // Radiant Coral Blue
      secondary: [18, 42, 78],     // Deep Coral Marine
      accent: [168, 85, 247],      // Electric Purple Accent
      core: [255, 255, 240],
      glow: 'rgba(56, 189, 248, 0.55)'
    }
  },
  pro: {
    idle: {
      primary: [245, 158, 11],     // Regal Gold (#f59e0b)
      secondary: [15, 17, 24],     // Obsidian Black
      accent: [16, 185, 129],      // Emerald Accent (#10b981)
      core: [251, 191, 36],        // Solar Gold Core
      glow: 'rgba(16, 185, 129, 0.35)'
    },
    listening: {
      primary: [251, 191, 36],     // Solar Gold
      secondary: [10, 12, 16],     // Pure Black
      accent: [52, 211, 153],      // Bright Emerald Accent (#34d399)
      core: [251, 191, 36],
      glow: 'rgba(52, 211, 153, 0.45)'
    },
    thinking: {
      primary: [16, 185, 129],     // Emerald Accent
      secondary: [217, 119, 6],    // Warm Amber Gold
      accent: [251, 191, 36],      // Solar Gold
      core: [251, 191, 36],
      glow: 'rgba(16, 185, 129, 0.5)'
    },
    speaking: {
      primary: [245, 158, 11],     // Gold
      secondary: [18, 20, 28],     // Carbon Black
      accent: [52, 211, 153],      // Emerald Accent
      core: [251, 191, 36],
      glow: 'rgba(245, 158, 11, 0.55)'
    }
  }
};

// Aliases
TIER_STATE_COLORS.BHARAT_GRASSROOTS_AID = TIER_STATE_COLORS.free;
TIER_STATE_COLORS.ENTERPRISE_LEGAL_SUITE = TIER_STATE_COLORS.pro;

let canvas = null;
let ctx = null;
let animId = null;
let orbState = 'idle';
let currentTier = 'free';
let analyserNode = null;
let dataArray = null;
const stardustParticles = [];

export const LivingSphere = {
  init(canvasId = 'orb-canvas') {
    canvas = document.getElementById(canvasId);
    if (!canvas) return;
    ctx = canvas.getContext('2d');
    this.resize();
    window.addEventListener('resize', () => this.resize());

    // Initialize 40 ambient stardust particles
    stardustParticles.length = 0;
    for (let i = 0; i < 42; i++) {
      stardustParticles.push({
        angle: Math.random() * Math.PI * 2,
        dist: 70 + Math.random() * 85,
        speed: (Math.random() - 0.5) * 0.015,
        size: 1.2 + Math.random() * 2.2,
        alpha: 0.3 + Math.random() * 0.6,
        phase: Math.random() * Math.PI * 2
      });
    }

    this.startLoop();
  },

  resize() {
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const w = rect.width || 320;
    const h = rect.height || 320;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    if (ctx) ctx.scale(dpr, dpr);
  },

  setState(state) {
    if (['idle', 'listening', 'thinking', 'speaking'].includes(state)) {
      orbState = state;
    }
  },

  getState() {
    return orbState;
  },

  setTier(tier) {
    if (tier === 'BHARAT_GRASSROOTS_AID' || tier === 'free') {
      currentTier = 'free';
    } else {
      currentTier = 'pro';
    }
  },

  connectAudioAnalyser(analyser) {
    analyserNode = analyser;
    if (analyserNode) {
      analyserNode.fftSize = 64;
      dataArray = new Uint8Array(analyserNode.frequencyBinCount);
    }
  },

  startLoop() {
    if (animId) cancelAnimationFrame(animId);
    const render = (time) => {
      this.draw(time);
      animId = requestAnimationFrame(render);
    };
    animId = requestAnimationFrame(render);
  },

  draw(time) {
    if (!canvas || !ctx) return;
    const rect = canvas.getBoundingClientRect();
    const width = rect.width || 320;
    const height = rect.height || 320;

    ctx.clearRect(0, 0, width, height);
    const cx = width / 2;
    const cy = height / 2;
    const t = time * 0.0015;

    // Real-time audio volume
    let audioLevel = 0;
    if (analyserNode && orbState === 'listening' && dataArray) {
      analyserNode.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < 16; i++) sum += dataArray[i];
      audioLevel = Math.min(1.0, (sum / 16) / 105.0);
    } else if (orbState === 'speaking') {
      audioLevel = 0.35 + 0.32 * Math.sin(time * 0.009) * Math.cos(time * 0.013);
    } else if (orbState === 'thinking') {
      audioLevel = 0.22 + 0.16 * Math.sin(time * 0.012);
    }

    const tierColors = TIER_STATE_COLORS[currentTier] || TIER_STATE_COLORS.free;
    const colors = tierColors[orbState] || tierColors.idle;

    // 1. Draw Stardust particles
    stardustParticles.forEach(p => {
      p.angle += p.speed * (1.0 + audioLevel * 1.5);
      const curDist = p.dist + (orbState === 'listening' ? audioLevel * 25 : Math.sin(t + p.phase) * 6);
      const px = cx + Math.cos(p.angle) * curDist;
      const py = cy + Math.sin(p.angle) * curDist;
      const pAlpha = p.alpha * (0.6 + 0.4 * Math.sin(t * 2 + p.phase));

      ctx.beginPath();
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${colors.accent.join(',')}, ${pAlpha})`;
      ctx.fill();
    });

    // 2. Draw Multi-Layer Chromatic Liquid Nebula with 'screen' blending
    ctx.save();
    ctx.globalCompositeOperation = 'screen';

    const layers = [
      { r: 76, color: colors.secondary, rot: t * 0.7, varAmp: 14 + 32 * audioLevel, n: 7 },
      { r: 68, color: colors.primary,   rot: -t * 1.1, varAmp: 18 + 42 * audioLevel, n: 6 },
      { r: 54, color: colors.accent,    rot: t * 1.6, varAmp: 12 + 25 * audioLevel, n: 8 }
    ];

    layers.forEach(layer => {
      const pts = [];
      for (let i = 0; i < layer.n; i++) {
        const a = (i / layer.n) * Math.PI * 2 + layer.rot;
        const variance = Math.sin(t * 2.5 + i * 1.5) * layer.varAmp;
        const r = layer.r + variance;
        pts.push({ x: cx + Math.cos(a) * r, y: cy + Math.sin(a) * r });
      }

      ctx.beginPath();
      const n = pts.length;
      ctx.moveTo(pts[0].x, pts[0].y);
      for (let i = 0; i < n; i++) {
        const p0 = pts[(i - 1 + n) % n];
        const p1 = pts[i];
        const p2 = pts[(i + 1) % n];
        const p3 = pts[(i + 2) % n];
        const c1x = p1.x + (p2.x - p0.x) / 6;
        const c1y = p1.y + (p2.y - p0.y) / 6;
        const c2x = p2.x - (p3.x - p1.x) / 6;
        const c2y = p2.y - (p3.y - p1.y) / 6;
        ctx.bezierCurveTo(c1x, c1y, c2x, c2y, p2.x, p2.y);
      }
      ctx.closePath();

      const grad = ctx.createRadialGradient(cx, cy, 10, cx, cy, layer.r + layer.varAmp);
      grad.addColorStop(0, `rgba(${layer.color.join(',')}, 0.85)`);
      grad.addColorStop(0.7, `rgba(${layer.color.join(',')}, 0.4)`);
      grad.addColorStop(1, `rgba(${layer.color.join(',')}, 0.0)`);
      ctx.fillStyle = grad;
      ctx.fill();
    });

    // 3. Central Molten Core
    const coreR = 38 + (audioLevel * 14);
    const coreGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, coreR);
    coreGrad.addColorStop(0, currentTier === 'free' ? '#fffff0' : '#ffffff');
    coreGrad.addColorStop(0.35, `rgba(${colors.core.join(',')}, 0.95)`);
    coreGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.beginPath();
    ctx.arc(cx, cy, coreR, 0, Math.PI * 2);
    ctx.fillStyle = coreGrad;
    ctx.fill();

    // 4. Center Mic Badge
    ctx.restore();
    ctx.beginPath();
    ctx.arc(cx, cy, 22, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(5, 7, 11, 0.55)';
    ctx.fill();

    // Microphone Icon
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.roundRect(cx - 5, cy - 9, 10, 14, 5);
    ctx.fill();

    ctx.beginPath();
    ctx.arc(cx, cy - 1, 8, 0, Math.PI);
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#ffffff';
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(cx, cy + 7);
    ctx.lineTo(cx, cy + 11);
    ctx.moveTo(cx - 5, cy + 11);
    ctx.lineTo(cx + 5, cy + 11);
    ctx.stroke();
  }
};
