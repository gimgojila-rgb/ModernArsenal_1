// ---------------------------------------------------------------------------------------------
// MODERN ARSENAL showreel - core: timing, easing, assets, drawing primitives, post-processing.
// Every frame is a pure function of time t (seconds), so frames can be rendered in any order.
// ---------------------------------------------------------------------------------------------
const W = 1920, H = 1080, FPS = 60, DUR = 76;
const B0 = 0.085, SPB = 0.5;                     // "Low Altitude Assault": 120 BPM, first downbeat 0.085 s
const bt = k => B0 + SPB * k;                    // time of beat k
const TAU = Math.PI * 2;

// palette
const C = {
  ink: '#07090d', navy: '#0d131c', steel: '#1a2230', grid: 'rgba(120,170,220,0.07)',
  white: '#f2f5f8', dim: '#8a97a8', cyan: '#35c8ff', cyanD: '#0f6f9a', red: '#ff3b2f', redD: '#8a1410',
  amber: '#ffb21e', amberD: '#8a5a06', lime: '#c4ff8c', port: '#ff2e22', stbd: '#3cff6e', hot: '#fff3c8',
};

// ---------------- math / easing ----------------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, t) => a + (b - a) * t;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const E = {
  lin: t => t,
  inQ: t => t * t, outQ: t => 1 - (1 - t) * (1 - t),
  inC: t => t * t * t, outC: t => 1 - Math.pow(1 - t, 3),
  ioC: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  outQn: t => 1 - Math.pow(1 - t, 5),
  inX: t => t <= 0 ? 0 : Math.pow(2, 10 * t - 10),
  outX: t => t >= 1 ? 1 : 1 - Math.pow(2, -10 * t),
  ioX: t => t <= 0 ? 0 : t >= 1 ? 1 : t < .5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2,
  outB: t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  outEl: t => t <= 0 ? 0 : t >= 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (TAU / 3)) + 1,
  sm: t => t * t * (3 - 2 * t),
};
const ease = (a, b, x, f = E.outC) => f(inv(a, b, x));        // eased 0..1 between times a and b
const win = (t, a, b) => t >= a && t < b;
// hashed noise, deterministic
const hr = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453123; return x - Math.floor(x); };
const hs = n => hr(n) * 2 - 1;
const vnoise = x => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return lerp(hs(i), hs(i + 1), u); };
const rot = (v, a) => [v[0] * Math.cos(a) - v[1] * Math.sin(a), v[0] * Math.sin(a) + v[1] * Math.cos(a)];
// damped spring step response (0 -> 1), for overshooting settles
const spring = (x, k = 9, z = 0.35) => x <= 0 ? 0 : 1 - Math.exp(-z * k * x) * Math.cos(k * Math.sqrt(1 - z * z) * x);

// ---------------- canvas helpers ----------------
function mk(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function ctxOf(c) { const x = c.getContext('2d'); x.imageSmoothingEnabled = false; return x; }

const IMG = {};
const ASSETS = ['ApacheDBoss', 'ApacheDBoss_Radar', 'ApacheEBoss', 'ApacheEBoss_Gun', 'ApacheEBoss_MainRotor', 'ApacheEBoss_MainRotorBlur', 'ApacheEBoss_Radar',
  'ApacheEBoss_TailRotor', 'ApacheEBoss_TailRotorBlur', 'CutsceneStripes', 'GrayEagle', 'GrayEagle_MarksL',
  'GrayEagle_Prop', 'GrayEagle_PropBlur', 'GrayEagle_Slime', 'ShadowUAV', 'ShadowUAV_Prop', 'ShadowUAV_PropBlur',
  'ShadowUAV_Slime', 'SpikeNLOS_Deploy', 'HumveeChinook_Glow', 'HumveeBoss', 'HumveeBoss_Antenna', 'HumveeBoss_Body',
  'HumveeBoss_Cabin', 'HumveeBoss_DoorFront', 'HumveeBoss_DoorRear', 'HumveeBoss_Engine', 'HumveeBoss_Frame',
  'HumveeBoss_Gun', 'HumveeBoss_Hood', 'HumveeBoss_Interior', 'HumveeBoss_Spare', 'HumveeBoss_Turret',
  'HumveeBoss_TurretShield', 'HumveeBoss_WellFront', 'HumveeBoss_WellRear', 'HumveeBoss_Wheel', 'M230ChainGun',
  'Mk19Launcher', 'GuardianHelmet', 'GuardianSummon', 'GrayEagleTerminal', 'GrayEagleBuff'];
const JSONS = {};

async function loadAll() {
  await Promise.all(ASSETS.map(n => new Promise((res, rej) => {
    const im = new Image(); im.onload = () => { IMG[n] = im; res(); }; im.onerror = () => rej(new Error('img ' + n)); im.src = 'assets/' + n + '.png';
  })));
  for (const k of ['GrayEagle', 'ShadowUAV']) JSONS[k] = await (await fetch('assets/' + k + '_lights.json')).json();
  const faces = ['400 40px Anton', '400 40px BlackOps', '500 40px Chakra', '600 40px Chakra', '700 40px Chakra',
    '400 40px Mono', '700 40px Mono', '700 40px KR', '900 40px KR', '400 40px Pix'];
  await Promise.all(faces.map(f => document.fonts.load(f, f.includes('KR') ? '표적지정됨항공지원' : 'AZaz09')));
}

// tinted copy of an image's alpha (cached)
const _tint = new Map();
function tint(img, col) {
  const key = (img.src || img.id || img.width + 'x' + img.height) + col;
  if (_tint.has(key)) return _tint.get(key);
  const c = mk(img.width, img.height), x = ctxOf(c);
  x.drawImage(img, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = col; x.fillRect(0, 0, c.width, c.height);
  _tint.set(key, c); return c;
}
// silhouette with a flat colour, same as tint but kept separate for readability
const silhouette = tint;

// draw sprite (or sub-rect) with origin, scale, rotation
function spr(ctx, img, x, y, o = {}) {
  const s = o.s ?? 1, r = o.r ?? 0, a = o.a ?? 1;
  const sx = o.sx ?? 0, sy = o.sy ?? 0, sw = o.sw ?? img.width, sh = o.sh ?? img.height;
  const ox = o.ox ?? sw / 2, oy = o.oy ?? sh / 2;
  if (a <= 0.001) return;
  ctx.save(); ctx.globalAlpha *= a;
  if (o.op) ctx.globalCompositeOperation = o.op;
  ctx.translate(x, y); if (r) ctx.rotate(r); ctx.scale(s * (o.fx ? -1 : 1), s);
  ctx.drawImage(img, sx, sy, sw, sh, -ox, -oy, sw, sh);
  ctx.restore();
}

// glow blob using the mod's own soft glow mask
function glow(ctx, x, y, size, col, a = 1) {
  if (a <= 0.003 || size < 1) return;
  const g = tint(IMG.HumveeChinook_Glow, col);
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = clamp(a, 0, 1);
  ctx.imageSmoothingEnabled = true; ctx.drawImage(g, x - size / 2, y - size / 2, size, size); ctx.restore();
}
// radial gradient light (large, smooth)
function light(ctx, x, y, r, col, a = 1) {
  if (a <= 0.003) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = clamp(a, 0, 1); ctx.fillStyle = g;
  ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore();
}

// ---------------- text ----------------
function setFont(ctx, fam, size, weight = 400) { ctx.font = `${weight} ${size}px ${fam}`; }
function txt(ctx, s, x, y, o = {}) {
  ctx.save();
  setFont(ctx, o.f || 'Chakra', o.size || 32, o.w || 700);
  ctx.letterSpacing = (o.track || 0) + 'px';
  ctx.textAlign = o.align || 'left'; ctx.textBaseline = o.base || 'alphabetic';
  ctx.globalAlpha *= o.a ?? 1;
  if (o.op) ctx.globalCompositeOperation = o.op;
  if (o.shadow) { ctx.shadowColor = o.shadow; ctx.shadowBlur = o.blur ?? 20; }
  if (o.stroke) { ctx.lineWidth = o.lw || 2; ctx.strokeStyle = o.stroke; ctx.strokeText(s, x, y); }
  if (o.col !== null) { ctx.fillStyle = o.col || C.white; ctx.fillText(s, x, y); }
  ctx.restore();
}
function measure(ctx, s, o = {}) {
  ctx.save(); setFont(ctx, o.f || 'Chakra', o.size || 32, o.w || 700); ctx.letterSpacing = (o.track || 0) + 'px';
  const m = ctx.measureText(s).width; ctx.restore(); return m;
}
const GLYPHS = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789#/<>=+*';
// decode / scramble reveal: p 0..1
function decode(ctx, s, x, y, p, o = {}, seed = 1) {
  const n = s.length, shown = Math.floor(p * (n + 3));
  let out = '';
  for (let i = 0; i < n; i++) {
    if (s[i] === ' ') { out += ' '; continue; }
    if (i < shown - 3) out += s[i];
    else if (i < shown) out += GLYPHS[Math.floor(hr(seed * 91 + i * 7 + Math.floor(p * 40)) * GLYPHS.length)];
    else out += ' ';
  }
  txt(ctx, out, x, y, o);
}
// text rising out of a clip line; p 0..1
function riseText(ctx, s, x, y, p, o = {}) {
  const size = o.size || 32, a = o.align || 'left';
  const w = measure(ctx, s, o) + 40;
  const x0 = a === 'center' ? x - w / 2 : a === 'right' ? x - w : x - 20;
  ctx.save(); ctx.beginPath(); ctx.rect(x0, y - size * 1.05, w, size * 1.35); ctx.clip();
  const dy = (1 - E.outX(clamp(p))) * size * 1.25;
  txt(ctx, s, x, y + dy, o); ctx.restore();
}
// big slam: scales down from `from` to 1 with ghost echoes
function slam(ctx, s, x, y, age, o = {}) {
  if (age < 0) return;
  const d = o.dur || 0.28, p = clamp(age / d), sc = lerp(o.from || 2.2, 1, E.outX(p));
  const a = clamp(age / 0.06) * (o.a ?? 1);
  ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
  if (p < 1) for (let k = 3; k >= 1; k--) {
    const gs = 1 + k * 0.06 * (1 - p);
    ctx.save(); ctx.scale(gs, gs); txt(ctx, s, 0, 0, { ...o, a: a * 0.18 * (1 - p), col: o.ghost || o.col }); ctx.restore();
  }
  txt(ctx, s, 0, 0, { ...o, a }); ctx.restore();
}

// ---------------- shapes / HUD primitives ----------------
function chamfer(ctx, x, y, w, h, c = 12) {
  ctx.beginPath(); ctx.moveTo(x + c, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + h - c); ctx.lineTo(x + w - c, y + h);
  ctx.lineTo(x, y + h); ctx.lineTo(x, y + c); ctx.closePath();
}
function plate(ctx, x, y, w, h, o = {}) {
  ctx.save(); ctx.globalAlpha *= o.a ?? 1;
  chamfer(ctx, x, y, w, h, o.c ?? 12);
  if (o.fill) { ctx.fillStyle = o.fill; ctx.fill(); }
  if (o.line) { ctx.lineWidth = o.lw || 2; ctx.strokeStyle = o.line; ctx.stroke(); }
  ctx.restore();
}
function brackets(ctx, x, y, w, h, len, col, lw = 3, a = 1) {
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath();
  for (const [cx, cy, sx, sy] of [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]]) {
    ctx.moveTo(cx, cy + sy * len); ctx.lineTo(cx, cy); ctx.lineTo(cx + sx * len, cy);
  }
  ctx.stroke(); ctx.restore();
}
function line(ctx, x0, y0, x1, y1, col, lw = 2, a = 1, dash) {
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = col; ctx.lineWidth = lw; if (dash) ctx.setLineDash(dash);
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke(); ctx.restore();
}
function ring(ctx, x, y, r, col, lw = 2, a = 1, a0 = 0, a1 = TAU) {
  if (r <= 0 || a <= 0.003) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath(); ctx.arc(x, y, r, a0, a1); ctx.stroke(); ctx.restore();
}
function rectF(ctx, x, y, w, h, col, a = 1) { ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = col; ctx.fillRect(x, y, w, h); ctx.restore(); }

// hazard stripes from the mod's own CutsceneStripes tile, tinted, scrolled
function stripes(ctx, x, y, w, h, col, off = 0, sc = 3) {
  const tile = tint(IMG.CutsceneStripes, col);
  const tw = tile.width * sc, th = tile.height * sc;
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  const o = ((off % tw) + tw) % tw;
  for (let yy = y; yy < y + h; yy += th) for (let xx = x - o - tw; xx < x + w; xx += tw) ctx.drawImage(tile, xx, yy, tw, th);
  ctx.restore();
}
// the mod's cutscene frame: bevelled hazard bars top and bottom with a label plate and a running clock
function cutFrame(ctx, t, k, col, label, sub, clockT) {
  if (k <= 0) return;
  const bh = 64, sh = 16, y0 = lerp(-bh - sh - 6, 0, k), y1 = lerp(H + 6, H - bh - sh, k);
  rectF(ctx, 0, y0, W, bh, '#0a0e14', 0.94);
  line(ctx, 0, y0 + bh, W, y0 + bh, col, 2, 0.8);
  stripes(ctx, 0, y0 + bh + 2, W, sh, col, t * 90, 1.15);
  rectF(ctx, 0, y1 + sh, W, bh, '#0a0e14', 0.94);
  line(ctx, 0, y1 + sh - 1, W, y1 + sh - 1, col, 2, 0.8);
  stripes(ctx, 0, y1, W, sh, col, -t * 90, 1.15);
  // label
  ctx.save(); ctx.translate(34, y0 + 42);
  ctx.strokeStyle = col; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(0, -12); ctx.lineTo(12, 0); ctx.lineTo(0, 12); ctx.lineTo(-12, 0); ctx.closePath(); ctx.stroke();
  rectF(ctx, -4, -4, 8, 8, col);
  txt(ctx, label, 26, 9, { f: 'Chakra', size: 27, w: 700, col: col, track: 2 });
  const lw = measure(ctx, label, { f: 'Chakra', size: 27, w: 700, track: 2 });
  line(ctx, 40 + lw, -12, 40 + lw, 14, col, 2, 0.6);
  txt(ctx, sub, 54 + lw, 9, { f: 'KR', size: 23, w: 700, col: C.white, a: 0.9 });
  ctx.restore();
  if (clockT !== undefined) {
    const s = Math.max(0, clockT), mm = Math.floor(s / 60), ss = (s % 60).toFixed(1).padStart(4, '0');
    rectF(ctx, W - 250, y0 + 34, 10, 10, col);
    txt(ctx, `T+${String(mm).padStart(2, '0')}:${ss}`, W - 232, y0 + 45, { f: 'Mono', size: 22, w: 700, col: C.white, a: 0.85 });
  }
}

// crosshair reticle
function reticle(ctx, x, y, r, col, t, a = 1, spin = 0.6) {
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y);
  ctx.strokeStyle = col; ctx.lineWidth = 2.5;
  ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke();
  ctx.rotate(t * spin);
  for (let i = 0; i < 4; i++) { ctx.rotate(TAU / 4); ctx.beginPath(); ctx.moveTo(r * 0.55, 0); ctx.lineTo(r * 1.3, 0); ctx.stroke(); }
  ctx.lineWidth = 1.5;
  for (let i = 0; i < 36; i++) { const aa = i / 36 * TAU, l = i % 9 === 0 ? 14 : 6; ctx.beginPath(); ctx.moveTo(Math.cos(aa) * (r + 8), Math.sin(aa) * (r + 8)); ctx.lineTo(Math.cos(aa) * (r + 8 + l), Math.sin(aa) * (r + 8 + l)); ctx.stroke(); }
  ctx.restore();
}
// leader-line callout: from anchor to label; p 0..1 draws it
function callout(ctx, ax, ay, lx, ly, title, sub, p, col = C.cyan, side = -1) {
  if (p <= 0) return;
  const p1 = E.outC(inv(0, 0.35, p)), p2 = E.outC(inv(0.25, 0.6, p)), p3 = inv(0.45, 1, p);
  // anchor dot
  ring(ctx, ax, ay, 10 * E.outB(inv(0, 0.3, p)), col, 2.5);
  rectF(ctx, ax - 3, ay - 3, 6, 6, col);
  const ex = lx, ey = ly;
  const mx = lerp(ax, ex, 0.5), mid = [lerp(ax, ex - side * 0, 1), ey];
  // elbow: diagonal to (ex + side*? , ey) then horizontal
  const kx = ex + side * -60, ky = ey;
  const d1 = [lerp(ax, kx, p1), lerp(ay, ky, p1)];
  line(ctx, ax, ay, d1[0], d1[1], col, 2);
  if (p2 > 0) line(ctx, kx, ky, lerp(kx, ex + side * 260, p2), ky, col, 2);
  if (p3 > 0) {
    const tx = side < 0 ? ex - 260 : ex + 16;
    decode(ctx, title, side < 0 ? ex - 250 : ex + 20, ey - 12, p3, { f: 'Chakra', size: 30, w: 700, col: C.white, track: 1 }, title.length);
    if (sub) decode(ctx, sub, side < 0 ? ex - 250 : ex + 20, ey + 30, inv(0.2, 1, p3), { f: 'Mono', size: 19, w: 400, col: col, track: 1 }, sub.length + 3);
  }
}
// PPI radar
function radar(ctx, x, y, R, t, col, a = 1, blips = []) {
  ctx.save(); ctx.globalAlpha *= a;
  for (let i = 1; i <= 4; i++) ring(ctx, x, y, R * i / 4, col, 1.5, 0.35);
  line(ctx, x - R, y, x + R, y, col, 1, 0.25); line(ctx, x, y - R, x, y + R, col, 1, 0.25);
  const ang = t * 2.2;
  const g = ctx.createConicGradient(ang - 1.2, x, y);
  g.addColorStop(0, 'rgba(53,200,255,0)'); g.addColorStop(1.2 / TAU, 'rgba(53,200,255,0.35)'); g.addColorStop(1.2 / TAU + 0.001, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, R, 0, TAU); ctx.fill();
  line(ctx, x, y, x + Math.cos(ang) * R, y + Math.sin(ang) * R, col, 2, 0.9);
  for (const [bx, by] of blips) {
    const ba = Math.atan2(by, bx); let d = ((ang - ba) % TAU + TAU) % TAU;
    const fade = Math.exp(-d * 1.1);
    rectF(ctx, x + bx * R - 4, y + by * R - 4, 8, 8, col, 0.25 + 0.75 * fade);
    glow(ctx, x + bx * R, y + by * R, 40, col, 0.6 * fade);
  }
  ctx.restore();
}

// HUD target glyph: curly braces around a centre pip, "{ • }". open: 1 = wide, 0 = tight
function targetMark(ctx, x, y, s = 1, col = '#ffffff', t = 0, a = 1, open = 1) {
  if (a <= 0.003) return;
  const h = 46 * s, w = (22 + 26 * open) * s, u = s;
  ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = col; ctx.lineWidth = 5 * s; ctx.lineCap = 'square'; ctx.lineJoin = 'miter';
  for (const sd of [-1, 1]) {
    const bx = x + sd * w;
    const P = [[12, -h], [0, -h + 10 * u], [0, -12 * u], [-11, 0], [0, 12 * u], [0, h - 10 * u], [12, h]];
    ctx.beginPath();
    P.forEach(([px, py], i) => { const X = bx - sd * (px === 12 || px === -11 ? px * u : px), Y = y + py; i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); });
    ctx.stroke();
  }
  const pulse = 0.75 + 0.25 * Math.sin(t * 9);
  ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x, y - 9 * s); ctx.lineTo(x + 9 * s, y); ctx.lineTo(x, y + 9 * s); ctx.lineTo(x - 9 * s, y); ctx.closePath(); ctx.fill();
  ctx.restore();
  glow(ctx, x, y, 120 * s, col, 0.35 * pulse * a);
}

// ---------------- particles (analytic) ----------------
// burst of square pixels from (x,y). returns nothing; everything from (t - t0)
function burst(ctx, t, t0, seed, n, x, y, o = {}) {
  const age = t - t0; if (age < 0) return;
  const life = o.life || 0.8, sp = o.speed || 600, g = o.g ?? 900, k = o.drag ?? 3, sz = o.size || 6;
  const a0 = o.a0 ?? 0, a1 = o.a1 ?? TAU;
  ctx.save(); if (o.add) ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const L = life * (0.5 + 0.5 * hr(seed + i * 3.1));
    if (age > L) continue;
    const ang = lerp(a0, a1, hr(seed + i * 1.7)), v = sp * (0.25 + 0.75 * hr(seed + i * 5.3));
    const f = (1 - Math.exp(-k * age)) / k;
    const px = x + Math.cos(ang) * v * f, py = y + Math.sin(ang) * v * f + 0.5 * g * age * age;
    const q = 1 - age / L;
    const s = sz * (0.5 + hr(seed + i * 9.1)) * (o.shrink ? q : 1);
    ctx.globalAlpha = clamp(q * 1.4) * (o.a ?? 1);
    ctx.fillStyle = typeof o.col === 'function' ? o.col(q, i) : (o.col || C.hot);
    ctx.fillRect(Math.round(px - s / 2), Math.round(py - s / 2), s, s);
  }
  ctx.restore();
}
// pre-rendered pixel puff (shaded blocky circle)
const PUFFS = {};
function puffSprite(shade) {
  if (PUFFS[shade]) return PUFFS[shade];
  const n = 24, c = mk(n, n), x = ctxOf(c), img = x.createImageData(n, n);
  const base = { smoke: [150, 156, 164], dark: [58, 60, 64], fire: [255, 170, 60], hot: [255, 240, 200], dust: [168, 142, 104] }[shade];
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
    const dx = i + 0.5 - n / 2, dy = j + 0.5 - n / 2, d = Math.hypot(dx, dy) / (n / 2);
    const edge = 1 - d + 0.12 * hs(i * 13 + j * 7);
    if (edge <= 0) continue;
    const lit = clamp(0.72 + (-dx - dy) / n * 0.7 + 0.06 * hs(i * 3 + j * 11));
    const q = Math.round(lit * 4) / 4;           // posterise: pixel-art tones
    const o = (j * n + i) * 4;
    img.data[o] = base[0] * (0.62 + 0.45 * q); img.data[o + 1] = base[1] * (0.62 + 0.45 * q); img.data[o + 2] = base[2] * (0.62 + 0.45 * q);
    img.data[o + 3] = 255;
  }
  x.putImageData(img, 0, 0); PUFFS[shade] = c; return c;
}
function puff(ctx, x, y, r, shade, a) {
  if (a <= 0.004 || r < 1) return;
  ctx.save(); ctx.globalAlpha = clamp(a); ctx.imageSmoothingEnabled = false;
  const s = puffSprite(shade); ctx.drawImage(s, x - r, y - r, 2 * r, 2 * r); ctx.restore();
}
// smoke trail left by an emitter moving along path(ts); puffs spawned at `rate` per second between ta and tb
function smokeTrail(ctx, t, ta, tb, rate, path, o = {}) {
  const life = o.life || 1.6, r0 = o.r0 || 10, r1 = o.r1 || 46;
  const i0 = Math.max(0, Math.floor((t - life - ta) * rate)), i1 = Math.floor((Math.min(t, tb) - ta) * rate);
  for (let i = i1; i >= i0; i--) {
    const ts = ta + i / rate, age = t - ts; if (age < 0 || age > life) continue;
    const p = path(ts); if (!p) continue;
    const q = age / life;
    const dx = hs(i * 1.3 + (o.seed || 0)) * 30 * q + (o.wind || 0) * age, dy = hs(i * 2.9 + (o.seed || 0)) * 20 * q - (o.rise ?? 25) * age;
    const r = lerp(r0, r1, E.outC(q));
    puff(ctx, p[0] + dx, p[1] + dy, r, o.shade || 'smoke', (o.a ?? 0.7) * (1 - q) * clamp(age * 12));
  }
}
function explosion(ctx, t, t0, x, y, s = 1, seed = 7) {
  const age = t - t0; if (age < 0 || age > 3.5) return;
  light(ctx, x, y, 620 * s, 'rgba(255,190,110,1)', 1.3 * Math.exp(-age * 3.5));
  const rp = clamp(age / 0.6);
  ring(ctx, x, y, 40 + 1000 * s * E.outC(rp), '#fff4d8', 12 * (1 - rp), 0.85 * (1 - rp));
  // lingering smoke column (drawn first, behind the fireball)
  for (let i = 0; i < 18; i++) {
    const st = 0.12 + hr(seed + i * 13) * 0.4, a = age - st; if (a < 0) continue;
    const q = clamp(a / 2.8), ang = -Math.PI / 2 + hs(seed + i * 3) * 1.1;
    const d = (60 + 200 * hr(seed + i * 17)) * s * E.outC(clamp(a / 1.2));
    puff(ctx, x + Math.cos(ang) * d, y + Math.sin(ang) * d * 0.8 - a * 110 * s, (28 + 40 * hr(seed + i)) * s * (0.7 + q), i % 3 ? 'smoke' : 'dark', 0.85 * (1 - q) * clamp(a * 6));
  }
  // fireball: many small hot puffs cooling from white to orange to soot
  for (let i = 0; i < 34; i++) {
    const a = hr(seed + i) * TAU, r0 = hr(seed + i * 2);
    const d = (20 + 170 * r0) * s * E.outX(clamp(age / 0.35));
    const life = 0.35 + 0.6 * hr(seed + i * 5), q = clamp(age / life);
    if (q >= 1) continue;
    const px = x + Math.cos(a) * d, py = y + Math.sin(a) * d * 0.75 - age * 70 * s;
    const r = (14 + 26 * hr(seed + i * 7)) * s * (0.8 + 0.8 * q);
    puff(ctx, px, py, r, q < 0.18 ? 'hot' : q < 0.55 ? 'fire' : 'dark', q < 0.55 ? 1 : 1 - (q - 0.55) / 0.45);
  }
  burst(ctx, t, t0, seed, 90, x, y, { speed: 1500 * s, life: 1.1, g: 1300, size: 6 * s, add: true, col: q => q > 0.6 ? '#fff6d0' : q > 0.3 ? '#ffb040' : '#ff5a1a' });
  burst(ctx, t, t0, seed + 50, 30, x, y, { speed: 1000 * s, life: 1.6, g: 1700, size: 8 * s, col: '#2a2420', a0: Math.PI * 1.05, a1: Math.PI * 1.95 });
}

// ---------------- camera fx: impacts drive shake, flash, chroma, zoom-punch ----------------
const IMPACTS = [];   // {t, shake, flash, ca, zoom, dec}
function impact(t, o) { IMPACTS.push({ t, shake: 0, flash: 0, ca: 0, zoom: 0, dec: 7, ...o }); }
function fxAt(t) {
  let sh = 0, fl = 0, ca = 0, zm = 0;
  for (const m of IMPACTS) {
    const age = t - m.t; if (age < 0 || age > 3) continue;
    const e = Math.exp(-age * m.dec);
    sh += m.shake * e; fl += m.flash * Math.exp(-age * (m.fdec || 9)); ca += m.ca * Math.exp(-age * 6); zm += m.zoom * spring(age, 18, 0.5) * Math.exp(-age * 5);
  }
  return { sh, fl, ca, zm };
}
// extra fx channels scenes can push per frame
const FX = { ca: 0, flash: 0, flashCol: '#ffffff', grain: 0.07, vig: 0.55, scan: 0, bloom: 0.35 };

// ---------------- post ----------------
let OUT, S, SC, T1, T2, T3, BL, BLC, VIG, GRAIN = [];
function setupPost() {
  const cv = document.getElementById('c'); OUT = cv.getContext('2d');
  S = mk(W, H); SC = ctxOf(S);
  T1 = mk(W, H); T2 = mk(W, H); T3 = mk(W, H);
  BL = mk(480, 270); BLC = BL.getContext('2d');
  VIG = mk(W, H); const v = VIG.getContext('2d');
  const g = v.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,1)'); v.fillStyle = g; v.fillRect(0, 0, W, H);
  for (let k = 0; k < 8; k++) {
    const c = mk(480, 270), x = c.getContext('2d'), im = x.createImageData(480, 270);
    for (let i = 0; i < im.data.length; i += 4) { const n = Math.floor(hr(k * 1e6 + i) * 255); im.data[i] = im.data[i + 1] = im.data[i + 2] = n; im.data[i + 3] = 255; }
    x.putImageData(im, 0, 0); GRAIN.push(c);
  }
}
function chromaSplit(src, amt) {
  const chans = [[T1, '#ff0000', -amt], [T2, '#00ff00', 0], [T3, '#0000ff', amt]];
  for (const [c, col, dx] of chans) {
    const x = c.getContext('2d'); x.globalCompositeOperation = 'source-over'; x.fillStyle = '#000'; x.fillRect(0, 0, W, H);
    x.drawImage(src, dx, dx * 0.25); x.globalCompositeOperation = 'multiply'; x.fillStyle = col; x.fillRect(0, 0, W, H);
  }
  OUT.save(); OUT.fillStyle = '#000'; OUT.fillRect(0, 0, W, H); OUT.globalCompositeOperation = 'lighter';
  for (const [c] of chans) OUT.drawImage(c, 0, 0); OUT.restore();
}
function post(t, f) {
  const fx = fxAt(t);
  // camera shake & punch-in applied when copying the scene buffer
  const sh = fx.sh, zm = 1 + fx.zm;
  const dx = sh * vnoise(t * 38 + 3.1), dy = sh * vnoise(t * 41 + 9.7), dr = sh * 0.0009 * vnoise(t * 29 + 5);
  const T = T1.getContext('2d');
  // compose shaken scene into T1-free buffer (reuse OUT directly when no CA)
  const ca = fx.ca + FX.ca;
  const target = ca > 0.4 ? T3 : null;
  const draw = (ctx) => {
    ctx.save(); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
    ctx.translate(W / 2 + dx, H / 2 + dy); ctx.rotate(dr); ctx.scale(zm, zm); ctx.translate(-W / 2, -H / 2);
    ctx.imageSmoothingEnabled = true; ctx.drawImage(S, 0, 0); ctx.restore();
  };
  if (ca > 0.4) {
    // shaken scene -> BUF, then split into OUT
    if (!post.buf) post.buf = mk(W, H);
    draw(post.buf.getContext('2d')); chromaSplit(post.buf, ca);
  } else draw(OUT);
  // bloom: highlights only (contrast crush), blurred at quarter res, screened back
  if (FX.bloom > 0) {
    BLC.save(); BLC.globalCompositeOperation = 'source-over'; BLC.filter = 'brightness(0.55) contrast(3.2) blur(7px)';
    BLC.drawImage(OUT.canvas, 0, 0, 480, 270); BLC.restore();
    OUT.save(); OUT.globalCompositeOperation = 'screen'; OUT.globalAlpha = FX.bloom; OUT.imageSmoothingEnabled = true;
    OUT.drawImage(BL, 0, 0, W, H); OUT.restore();
  }
  // scanlines (HUD scenes)
  if (FX.scan > 0) { OUT.save(); OUT.globalAlpha = FX.scan; OUT.fillStyle = '#000'; for (let y = 0; y < H; y += 4) OUT.fillRect(0, y, W, 2); OUT.restore(); }
  // vignette
  OUT.save(); OUT.globalAlpha = FX.vig; OUT.drawImage(VIG, 0, 0); OUT.restore();
  // grain
  OUT.save(); OUT.globalCompositeOperation = 'overlay'; OUT.globalAlpha = FX.grain; OUT.imageSmoothingEnabled = true;
  OUT.drawImage(GRAIN[f % 8], 0, 0, W, H); OUT.restore();
  // flash
  const fl = clamp(fx.fl + FX.flash);
  if (fl > 0.003) { OUT.save(); OUT.globalAlpha = fl; OUT.fillStyle = FX.flashCol; OUT.fillRect(0, 0, W, H); OUT.restore(); }
}

// ---------------- frame entry ----------------
let READY = null;
window.boot = async () => { await loadAll(); setupPost(); if (window.initScenes) initScenes(); READY = true; return true; };
window.renderFrame = (f) => {
  const t = f / FPS;
  FX.ca = 0; FX.flash = 0; FX.flashCol = '#ffffff'; FX.grain = 0.07; FX.vig = 0.55; FX.scan = 0; FX.bloom = 0.35;
  SC.setTransform(1, 0, 0, 1, 0, 0); SC.globalAlpha = 1; SC.globalCompositeOperation = 'source-over'; SC.imageSmoothingEnabled = false;
  SC.fillStyle = '#000'; SC.fillRect(0, 0, W, H);
  drawScenes(SC, t);
  post(t, f);
};
window.grab = (q = 0.95) => document.getElementById('c').toDataURL('image/jpeg', q);
