// ---------------------------------------------------------------------------------------------
// Scenes. Timeline locked to "Low Altitude Assault" (120 BPM): bar = 2 s, beat = 0.5 s, downbeats at 0.085 + 2n.
// Video 0-48.06 = song 0-48.06, video 48.06-59.6 = song 168.06-end (final phrase), so the grid never breaks.
// ---------------------------------------------------------------------------------------------
const CUES = [];                          // sound design cues for the audio mix: {t, k, g}
const cue = (t, k, g = 1) => CUES.push({ t: +t.toFixed(4), k, g });
const T = { BOOT: 0, LOCK: bt(16), TITLE: bt(32), APACHE: bt(40), SPIKE: bt(56), DRONE: bt(64), HUMVEE: bt(80), BREAK: bt(92), DPACHE: 48.06, MONT: 64.06, END: 71.03 };

// ---------------- text helpers that need offscreen buffers ----------------
const _tc = new Map();
function textCanvas(s, o) {
  const key = s + JSON.stringify(o);
  if (_tc.has(key)) return _tc.get(key);
  const tmp = mk(8, 8).getContext('2d');
  const w = Math.ceil(measure(tmp, s, o)) + 40, h = Math.ceil((o.size || 32) * 1.5);
  const c = mk(w, h), x = c.getContext('2d');
  txt(x, s, 20, h * 0.78, { ...o, align: 'left' });
  const r = { c, w, h, base: h * 0.78 }; _tc.set(key, r); return r;
}
// sliced / rgb-split glitch text centred on x
function glitch(ctx, s, x, y, o, amt, seed = 1) {
  const r = textCanvas(s, o);
  const x0 = (o.align === 'left' ? x - 20 : x - r.w / 2), y0 = y - r.base;
  if (amt <= 0.001) { ctx.drawImage(r.c, x0, y0); return; }
  const n = 9, sh = r.h / n, fr = Math.floor(performance.now ? 0 : 0);
  ctx.save();
  for (let i = 0; i < n; i++) {
    const off = hs(seed * 13 + i * 7.1) * 90 * amt * (hr(seed + i) > 0.45 ? 1 : 0.1);
    ctx.drawImage(r.c, 0, i * sh, r.w, sh, x0 + off, y0 + i * sh, r.w, sh);
  }
  ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.6 * amt;
  ctx.drawImage(tint(r.c, '#ff2020'), x0 - 14 * amt, y0); ctx.drawImage(tint(r.c, '#20e0ff'), x0 + 14 * amt, y0);
  ctx.restore();
}
function kr(ctx, s, x, y, o = {}) { txt(ctx, s, x, y, { f: 'KR', w: 700, size: 30, col: C.dim, ...o }); }
function statBar(ctx, x, y, w, label, val, max, p, col) {
  txt(ctx, label, x, y, { f: 'Mono', size: 20, w: 700, col: C.dim, track: 2 });
  const v = Math.round(val * E.outC(p));
  txt(ctx, v.toLocaleString('en-US'), x + w, y, { f: 'Mono', size: 26, w: 700, col: C.white, align: 'right' });
  rectF(ctx, x, y + 12, w, 10, 'rgba(255,255,255,0.08)');
  const segs = 30, fill = Math.round(segs * (val / max) * E.outC(p));
  for (let i = 0; i < fill; i++) rectF(ctx, x + i * (w / segs), y + 12, w / segs - 3, 10, col);
}
function spec(ctx, x, y, label, value, p, col) {
  if (p <= 0) return;
  txt(ctx, label, x, y, { f: 'Mono', size: 18, w: 700, col: col, track: 3, a: clamp(p * 3) });
  decode(ctx, value, x, y + 34, p, { f: 'Chakra', size: 28, w: 700, col: C.white, track: 1 }, value.length);
}

// ======================================= SCENE 1: BOOT =======================================
function sBoot(ctx, t) {
  rectF(ctx, 0, 0, W, H, C.ink);
  const ga = ease(0.3, 2.5, t);
  gridBG(ctx, t, `rgba(80,160,220,${0.09 * ga})`, C.ink, 60, 0, t * 8);
  // CRT power-on line
  if (t < 0.9) {
    const a = ease(0.09, 0.3, t, E.outX), b = ease(0.3, 0.6, t, E.outX), f = 1 - ease(0.5, 0.9, t);
    const lh = 2 + b * 180;
    rectF(ctx, W / 2 - a * W / 2, H / 2 - lh / 2, a * W, lh, '#dff6ff', f * (1 - b * 0.7));
    light(ctx, W / 2, H / 2, 700 * a, 'rgba(120,220,255,1)', f * 0.6);
  }
  FX.scan = 0.18;
  // datalink log
  const LOG = ['MODERN ARSENAL // TACTICAL DATALINK  v0.5.9', '> AH-64D APACHE ............. LINK OK', '> AH-64E GUARDIAN ........... LINK OK', '> MQ-1C GRAY EAGLE .......... LINK OK',
    '> RQ-7B SHADOW .............. LINK OK', '> M1151 HUMVEE .............. LINK OK', '> SPIKE NLOS ................ ARMED'];
  LOG.forEach((s, i) => {
    const t0 = bt(1 + i), p = ease(t0, t0 + 0.35, t, E.lin);
    if (p > 0) decode(ctx, s, 70, 110 + i * 34, p, { f: 'Mono', size: 20, w: 700, col: i === 0 ? C.white : C.cyan, a: 0.85 * (1 - ease(7.6, 8.085, t)) }, i + 2);
  });
  // radar, lower left
  const ra = ease(1.0, 1.6, t) * (1 - ease(7.7, 8.085, t));
  if (ra > 0) {
    radar(ctx, 200, 870, 130 * E.outB(ease(1.0, 1.6, t, E.lin)), t, C.cyan, ra, [[0.4, -0.3], [-0.5, 0.2], [0.1, 0.62]]);
    txt(ctx, 'FCR // SCAN', 200, 1040, { f: 'Mono', size: 16, w: 700, col: C.cyan, align: 'center', a: ra * 0.8 });
  }
  // right column: readouts
  const rc = ease(1.6, 2.2, t) * (1 - ease(7.7, 8.085, t));
  if (rc > 0) {
    const rows = [['LAT', (37.5665 + Math.sin(t) * 0.0003).toFixed(4)], ['LON', (126.978 + t * 0.00007).toFixed(4)], ['ALT', String(Math.round(1200 + 40 * vnoise(t * 2))).padStart(5, '0') + ' FT'], ['HDG', String(Math.round(270 + 3 * vnoise(t))).padStart(3, '0')], ['WX', 'CLEAR']];
    rows.forEach(([k, v], i) => { txt(ctx, k, W - 330, 120 + i * 34, { f: 'Mono', size: 18, w: 700, col: C.dim, a: rc }); txt(ctx, v, W - 70, 120 + i * 34, { f: 'Mono', size: 20, w: 700, col: C.white, align: 'right', a: rc }); });
  }
  // kinetic words: DEMONS / DRAGONS / GODS / ... AIR SUPPORT
  const words = [[bt(2), bt(3), bt(5), 'YOUR WORLD HAS', 'DEMONS.', '악마가 있고'], [bt(5), bt(6), bt(9), 'IT HAS', 'DRAGONS.', '드래곤이 있고'], [bt(9), bt(10), bt(12), 'IT EVEN HAS', 'GODS.', '신까지 있죠'], [bt(12), 99, 99, 'BUT IT HAS NEVER HAD', '', '하지만 이건 없었어요']];
  for (const [a, b, c, small, big, k] of words) {
    if (t < a - 0.01 || t > c + 0.2) continue;
    const out = ease(c - 0.12, c, t);
    const sa = 1 - out;
    riseText(ctx, small, W / 2, 440, ease(a, a + 0.35, t, E.lin), { f: 'Chakra', size: 46, w: 600, col: C.dim, align: 'center', track: 10, a: sa });
    if (big && t >= b) {
      const age = t - b;
      const gl = age < 0.08 ? 1 - age / 0.08 : out;
      ctx.save(); ctx.globalAlpha = sa;
      const sc = lerp(1.25, 1, E.outX(clamp(age / 0.3)));
      ctx.translate(W / 2, 620); ctx.scale(sc, sc);
      glitch(ctx, big, 0, 0, { f: 'Anton', size: 190, col: C.white, track: 8 }, gl, Math.floor(t * 30));
      ctx.restore();
      kr(ctx, k, W / 2, 710, { align: 'center', a: sa * ease(b + 0.1, b + 0.4, t), size: 30 });
    }
    if (!big) kr(ctx, k, W / 2, 500, { align: 'center', a: ease(a + 0.2, a + 0.6, t) * 0.9, size: 28 });
  }
  // tension: red flicker in the last bar
  if (t > bt(14)) { const k = ease(bt(14), bt(16), t, E.inC); rectF(ctx, 0, 0, W, H, C.redD, k * 0.25 * (0.6 + 0.4 * hr(Math.floor(t * 30)))); }
}

// ======================================= SCENE 2: LOCK =======================================
const LOCK_BEEPS = [];
function sLock(ctx, t) {
  const t0 = T.LOCK;
  // phase 1: AIR SUPPORT slam (8.085 - 9.585)
  const seekA = ease(bt(19), bt(19) + 0.3, t);
  if (seekA < 1) {
    rectF(ctx, 0, 0, W, H, '#0a0406');
    light(ctx, W / 2, H / 2, 900, 'rgba(255,40,30,1)', 0.35 * (1 - seekA));
    stripes(ctx, 0, 0, W, H, 'rgba(255,50,40,0.06)', t * 60, 6);
    ctx.save(); ctx.globalAlpha = 1 - seekA;
    slam(ctx, 'AIR SUPPORT.', W / 2, 610, t - t0, { f: 'Anton', size: 230, col: C.white, align: 'center', track: 6, from: 2.6, ghost: C.red });
    kr(ctx, '항공 지원', W / 2, 720, { align: 'center', size: 40, col: C.red, w: 900, a: ease(t0 + 0.15, t0 + 0.4, t) });
    ctx.restore();
  }
  if (seekA > 0) {
    // EO seeker feed
    ctx.save(); ctx.globalAlpha = seekA;
    const z = lerp(1, 1.9, ease(bt(19), bt(31), t, E.ioC));
    const px = 960, gy = 860;
    ctx.save(); ctx.translate(px + 14 * vnoise(t * 0.9 + 4), 700 + 10 * vnoise(t * 0.8 + 9)); ctx.rotate(0.012 * vnoise(t * 0.6)); ctx.scale(z, z); ctx.translate(-px, -700);
    world(ctx, t, 400 + (t - t0) * 30, { sky: 'storm', groundY: gy, haze: false });
    targetMark(ctx, px, gy - 70, 1.1, '#f2f8fa', t, 1, 1 - ease(bt(19), bt(31), t));
    // the Shadow drifts across the feed on its orbit
    const dk = inv(bt(21), bt(26), t);
    if (dk > 0 && dk < 1) drawDrone(ctx, 'ShadowUAV', lerp(2100, -300, dk), 420 + Math.sin(t * 2) * 8, 3.2, t, { sil: '#e4eaee' });
    ctx.restore();
    ctx.globalCompositeOperation = 'saturation'; rectF(ctx, 0, 0, W, H, '#808080');
    ctx.globalCompositeOperation = 'multiply'; rectF(ctx, 0, 0, W, H, '#b8d0d8');
    ctx.globalCompositeOperation = 'source-over';
    for (let i = 0; i < 6; i++) { const y = (hr(i * 7 + Math.floor(t * 20)) * H); rectF(ctx, 0, y, W, 2, '#fff', 0.05); }
    ctx.restore();
    FX.scan = 0.22 * seekA; FX.grain = 0.16;
    // HUD
    const hudA = seekA;
    ctx.save(); ctx.globalAlpha = hudA;
    brackets(ctx, 60, 110, W - 120, H - 220, 60, '#e8f4f8', 3);
    line(ctx, 0, 700, W, 700, '#e8f4f8', 1, 0.25); line(ctx, 960, 0, 960, H, '#e8f4f8', 1, 0.25);
    txt(ctx, 'SPIKE NLOS    EO    NFOV x2', 100, 170, { f: 'Mono', size: 24, w: 700, col: '#e8f4f8' });
    txt(ctx, 'DL  AH-64E  LINK OK', 100, 204, { f: 'Mono', size: 20, w: 400, col: '#e8f4f8', a: 0.8 });
    const lp = ease(bt(20), bt(31), t, E.lin);
    const rng = Math.round(lerp(4200, 32, E.inC(lp)));
    txt(ctx, `RNG ${String(rng).padStart(4, '0')} M`, W - 100, 170, { f: 'Mono', size: 24, w: 700, col: '#e8f4f8', align: 'right' });
    txt(ctx, `TTI ${Math.max(0, (bt(32) - t)).toFixed(1)} S`, W - 100, 204, { f: 'Mono', size: 20, w: 400, col: '#e8f4f8', align: 'right', a: 0.8 });
    // target box tightening on the player
    const k = ease(bt(19), bt(31), t, E.outC);
    const tx = 960, ty = 700 - 30;
    const bw = lerp(640, 150, k), bh = lerp(460, 260, k);
    const blink = LOCK_BEEPS.some(b => t >= b && t < b + 0.05);
    brackets(ctx, tx - bw / 2, ty - bh / 2, bw, bh, 28, blink ? C.red : '#e8f4f8', 4);
    line(ctx, tx - bw / 2 - 120, ty, tx - bw / 2 - 12, ty, '#e8f4f8', 2); line(ctx, tx + bw / 2 + 12, ty, tx + bw / 2 + 120, ty, '#e8f4f8', 2);
    // LASE bar
    const bx = 660, by = 930, bwid = 600;
    txt(ctx, 'LASE', bx, by - 14, { f: 'Mono', size: 20, w: 700, col: '#e8f4f8' });
    txt(ctx, `${Math.round(lp * 100)}%`, bx + bwid, by - 14, { f: 'Mono', size: 20, w: 700, col: lp >= 1 ? C.red : '#e8f4f8', align: 'right' });
    for (let i = 0; i < 24; i++) rectF(ctx, bx + i * 25, by, 20, 16, i < Math.floor(lp * 24) ? (lp >= 1 ? C.red : '#e8f4f8') : 'rgba(232,244,248,0.15)');
    // countdown & LOCK
    const cd = [[bt(28), '3'], [bt(29), '2'], [bt(30), '1']];
    for (const [c0, s] of cd) if (t >= c0 && t < c0 + 0.5) {
      const age = t - c0, sc = lerp(1.35, 1, E.outX(clamp(age / 0.25)));
      ctx.save(); ctx.translate(tx + 330, ty + 40); ctx.scale(sc, sc);
      txt(ctx, s, 0, 0, { f: 'Anton', size: 260, col: null, stroke: '#e8f4f8', lw: 5, align: 'center', a: 1 - ease(c0 + 0.3, c0 + 0.5, t) });
      ctx.restore();
    }
    if (t >= bt(31)) {
      const age = t - bt(31);
      ring(ctx, tx, ty, 90 + 900 * E.outC(clamp(age / 0.5)), C.red, 6, 1 - clamp(age / 0.5));
      slam(ctx, 'TRK LOCK', tx, ty - bh / 2 - 56, age, { f: 'Chakra', size: 56, w: 700, col: C.red, align: 'center', track: 10, from: 1.6 });
      kr(ctx, '표적 고정', tx, ty - bh / 2 - 18, { align: 'center', size: 26, col: C.red, a: clamp(age * 5) });
      FX.flash = E.inC(clamp(age / 0.5)) * 0.95;
    }
    ctx.restore();
  }
  // the mod's own TARGETED cutscene frame
  cutFrame(ctx, t, ease(t0, t0 + 0.45, t, E.outX), C.cyan, 'TARGETED', '표적 지정됨', t - t0);
}

// ======================================= SCENE 3: TITLE =======================================
function titleLogo(ctx, t, t0, x, y, o = {}) {
  const word = 'ARSENAL', size = o.size || 300;
  ctx.save();
  setFont(ctx, 'Anton', size, 400); ctx.letterSpacing = '10px';
  const widths = [...word].map(ch => ctx.measureText(ch).width + 10);
  const total = widths.reduce((a, b) => a + b, 0);
  let cx = x - total / 2;
  [...word].forEach((ch, i) => {
    const a0 = t0 + i * 0.0625, age = t - a0;
    if (age >= 0) {
      const p = clamp(age / 0.3), sc = lerp(2.8, 1, E.outX(p));
      const dy = (1 - E.outX(p)) * -80;
      ctx.save(); ctx.translate(cx + widths[i] / 2, y + dy); ctx.scale(sc, sc);
      txt(ctx, ch, 0, 0, { f: 'Anton', size, col: o.col || C.white, align: 'center', a: clamp(age / 0.05) });
      if (age < 0.12) txt(ctx, ch, 0, 0, { f: 'Anton', size, col: C.red, align: 'center', a: 1 - age / 0.12, op: 'lighter' });
      ctx.restore();
    }
    cx += widths[i];
  });
  ctx.restore();
  // MODERN above, tracked wide
  const mp = ease(t0 + 0.2, t0 + 0.7, t, E.lin);
  if (mp > 0) decode(ctx, 'M O D E R N', x - total / 2 + 8, y - size * 0.86, mp, { f: 'Chakra', size: size * 0.24, w: 700, col: C.red, track: size * 0.07 }, 5);
  // underline bar with stripes
  const up = ease(t0 + 0.5, t0 + 0.9, t, E.outX);
  if (up > 0) {
    rectF(ctx, x - total / 2, y + 26, total * up, 14, C.red);
    stripes(ctx, x - total / 2, y + 44, total * up, 12, 'rgba(255,59,47,0.8)', t * 80, 0.9);
  }
  return total;
}
function sTitle(ctx, t) {
  const t0 = T.TITLE;
  rectF(ctx, 0, 0, W, H, '#0b0506');
  light(ctx, W / 2, H * 0.55, 1100, 'rgba(255,40,30,1)', 0.35);
  // rotating diagonal hazard band behind
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(-0.22);
  stripes(ctx, -W, -60, W * 2, 120, 'rgba(255,59,47,0.10)', t * 200, 8);
  ctx.restore();
  // pixel embers
  for (let i = 0; i < 60; i++) {
    const sp = 40 + hr(i) * 120, x = hr(i * 3) * W, y = H - ((t * sp + hr(i * 7) * H) % (H + 40));
    rectF(ctx, x + Math.sin(t + i) * 20, y, 4, 4, i % 3 ? C.red : C.amber, 0.25 + 0.4 * hr(i * 11));
  }
  const total = titleLogo(ctx, t, t0, W / 2, 600);
  // shockwave from the slam
  const age = t - t0;
  ring(ctx, W / 2, 520, 200 + 1600 * E.outC(clamp(age / 0.8)), '#ffffff', 16 * (1 - clamp(age / 0.8)), 0.7 * (1 - clamp(age / 0.8)));
  burst(ctx, t, t0, 91, 90, W / 2, 520, { speed: 2400, life: 1.2, g: 500, size: 8, add: true, col: q => q > 0.5 ? '#fff0d0' : C.red });
  // subtitle
  const sp = ease(bt(34), bt(34) + 0.6, t, E.lin);
  if (sp > 0) decode(ctx, 'MODERN MILITARY HARDWARE FOR TERRARIA', W / 2 - 520, 740, sp, { f: 'Chakra', size: 38, w: 600, col: C.white, track: 6 }, 11);
  kr(ctx, '테라리아에 현대 군사 장비를 들여오는 모드', W / 2, 790, { align: 'center', a: ease(bt(35), bt(36), t) * 0.8, size: 26 });
  // tag plates, one per beat
  const tags = [['tModLoader', C.white], ['PLAYS WITH CALAMITY  (OPTIONAL)', C.white], ['v0.5.9', C.red]];
  let tx = W / 2 - 520;
  tags.forEach(([s, col], i) => {
    const tt = bt(36 + i), p = ease(tt, tt + 0.2, t, E.outB);
    const w = measure(ctx, s, { f: 'Mono', size: 20, w: 700, track: 2 }) + 40;
    if (p > 0) {
      ctx.save(); ctx.translate(tx + w / 2, 860); ctx.scale(p, p);
      plate(ctx, -w / 2, -24, w, 44, { line: col, lw: 2, c: 10, fill: 'rgba(255,255,255,0.04)' });
      txt(ctx, s, 0, 6, { f: 'Mono', size: 20, w: 700, col, align: 'center', track: 2 });
      ctx.restore();
    }
    tx += w + 22;
  });
}

// ======================================= SCENE 4: APACHE =======================================
const APS = 2.3;
function apacheState(t) {
  const a = T.APACHE;
  const u = ease(a - 0.5, a + 2.0, t, E.outC);
  let x = lerp(2900, 1250, u), y = lerp(120, 500, u);
  let tilt = -0.3 * (1 - ease(a + 0.6, a + 1.4, t, E.ioC)) + 0.26 * ease(a + 0.9, a + 1.5, t, E.ioC) * (1 - ease(a + 1.8, a + 2.9, t, E.ioC));
  y += Math.sin(t * 2.1) * 8 * ease(a + 1.5, a + 2.5, t); tilt += Math.sin(t * 1.3) * 0.015;
  // 360 evasive loop
  const L0 = bt(50), L1 = bt(54) - 0.1;
  if (t > L0) {
    const ph = TAU * E.ioC(inv(L0, L1, t)), RX = 720, RY = 390;
    const cx = 1250, cy = 500 - RY;
    x = cx - Math.sin(ph) * RX; y = cy + Math.cos(ph) * RY;
    tilt = Math.atan2(RY * Math.sin(ph), RX * Math.cos(ph)); if (ph > Math.PI) tilt += TAU;
  }
  // exit: dash left, nose down
  const X0 = bt(54) + 0.2;
  if (t > X0) { const e = ease(X0, X0 + 1.2, t, E.inC); x -= e * 2900; y += e * 120; tilt = -0.32 * ease(X0, X0 + 0.4, t, E.ioC); }
  return { x, y, tilt };
}
function sApache(ctx, t) {
  const a = T.APACHE;
  // camera zoom out for the loop; the grid and the ground pull back with it
  const z = 1 - 0.5 * ease(bt(49) + 0.3, bt(50) + 0.1, t, E.ioC) * (1 - ease(bt(54), bt(55), t, E.ioC));
  world(ctx, t, (t - a) * 260 + 3000, { sky: 'dusk', groundY: (1010 - 540 + (1 - z) * 560) * z + 540, zoom: z, glow: [1250, 520, 900, 'rgba(255,70,50,1)', 0.10] });
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2 + (1 - z) * 560);
  const st = apacheState(t);
  const lvl = t < a + 2 ? 1 : 0.5;
  apacheVapor(ctx, t, tt => ({ ...apacheState(tt) }), APS, lvl);
  // flares on the loop entry
  flares(ctx, t, bt(50) + 0.05, 17, 12, tt => { const s2 = apacheState(tt); return apW({ ...s2, s: APS }, [70, 30]); }, 1, 1.4);
  // gun: slews onto the target, then bursts
  let gun = -0.14;
  const g0 = bt(47) + 0.05, g1 = bt(49) - 0.1;
  gun = lerp(-0.14, -0.42, ease(bt(46), g0, t, E.ioC)) * (1 - ease(g1, g1 + 0.3, t)) + -0.14 * ease(g1, g1 + 0.3, t);
  const p = { ...st, s: APS, t, gun, beaconBoost: 1.2 };
  drawApache(ctx, p);
  if (t > g0 && t < g1) {
    const piv = apW(p, AP.GUN), ang = st.tilt + gun;
    const mz = [piv[0] - Math.cos(ang) * 33 * APS, piv[1] - Math.sin(ang) * 33 * APS];
    const fi = Math.floor((t - g0) * 60);
    if (fi % 5 < 2) muzzle(ctx, mz[0], mz[1], ang, APS * 0.9, t, 5);
    for (let k = 0; k < 7; k++) {
      const tb = g0 + k * 0.1 + Math.floor((t - g0) / 0.7) * 0.7, age = t - tb;
      if (age < 0 || age > 0.35) continue;
      const d0 = age * 5200, d1 = d0 + 220;
      tracer(ctx, mz[0] - Math.cos(ang) * d0, mz[1] - Math.sin(ang) * d0, mz[0] - Math.cos(ang) * d1, mz[1] - Math.sin(ang) * d1, '#ffcc66', 3);
    }
  }
  // Longbow radar ping
  for (const tp of [bt(44), bt(45)]) {
    const age = t - tp; if (age < 0 || age > 1.2) continue;
    const rc = apW(p, AP.RADAR);
    ring(ctx, rc[0], rc[1], 20 + age * 900, C.cyan, 4 * (1 - age / 1.2), 1 - age / 1.2, -Math.PI * 0.95, -Math.PI * 0.05);
    glow(ctx, rc[0], rc[1], 160, C.cyan, 1 - age / 0.4);
  }
  ctx.restore();
  // callouts (camera is identity before the loop)
  const fade = 1 - ease(bt(49) + 0.2, bt(50), t);
  if (fade > 0) {
    ctx.save(); ctx.globalAlpha = fade;
    const q = { ...apacheState(t), s: APS };
    const rc = apW(q, AP.RADAR), gp = apW(q, AP.GUN), tb = apW(q, AP.TUBE);
    callout(ctx, rc[0], rc[1], 560, 330, 'LONGBOW RADAR', 'FCR PAINTS YOU: TARGETED', ease(bt(45), bt(46) + 0.3, t, E.lin), C.cyan, -1);
    callout(ctx, gp[0] - 30, gp[1] + 6, 560, 560, 'M230 30MM CHAIN GUN', 'HEDP: BURSTS ON IMPACT', ease(bt(46), bt(47) + 0.3, t, E.lin), C.amber, -1);
    callout(ctx, tb[0], tb[1], 560, 790, 'SPIKE NLOS', 'COLD EJECT > CLIMB > DIVE', ease(bt(47), bt(48) + 0.3, t, E.lin), C.red, -1);
    ctx.restore();
  }
  // title plate
  const tp = ease(bt(45), bt(45) + 0.4, t, E.outX) * (1 - ease(bt(55), bt(56), t));
  if (tp > 0) {
    ctx.save(); ctx.globalAlpha = tp; ctx.translate(-(1 - tp) * 200, 0);
    rectF(ctx, 80, 92, 8, 128, C.red);
    txt(ctx, 'AH-64E APACHE GUARDIAN', 110, 170, { f: 'Anton', size: 84, col: C.white, track: 3, shadow: 'rgba(0,0,0,0.5)', blur: 20 });
    plate(ctx, 112, 190, 92, 34, { fill: C.red, c: 8 });
    txt(ctx, 'BOSS', 158, 215, { f: 'Mono', size: 20, w: 700, col: '#fff', align: 'center', track: 3 });
    kr(ctx, '아파치 가디언  ·  5페이즈', 222, 216, { size: 24, col: '#ffd6cf' });
    ctx.restore();
  }
  // evasive loop caption
  const lp = t - bt(50) - 0.1;
  if (lp > 0 && t < bt(55)) {
    const la = 1 - ease(bt(54) + 0.2, bt(55), t);
    ctx.save(); ctx.globalAlpha = la;
    slam(ctx, '360° EVASIVE LOOP', 100, 940, lp, { f: 'Anton', size: 110, col: C.white, track: 2, from: 1.8 });
    decode(ctx, 'DUMPS FLARES  //  TAKES 60% LESS DAMAGE UNTIL IT COMES OUT', 104, 995, ease(bt(51), bt(52), t, E.lin), { f: 'Mono', size: 22, w: 700, col: C.amber, track: 1 }, 4);
    kr(ctx, '360도 회피 기동', 104, 1036, { size: 24, a: ease(bt(51), bt(52), t) });
    ctx.restore();
  }
}

// ======================================= SCENE 5: SPIKE NLOS =======================================
const SPK = { s: 1.5, x: 1320, y: 520 };
function spikeMissile(t) {                     // world state of the missile
  const tl = T.SPIKE + 0.02, age = t - tl;
  const tube = apW({ x: SPK.x, y: SPK.y, s: SPK.s, tilt: 0 }, AP.TUBE);
  if (age < 0) return { x: tube[0], y: tube[1], ang: Math.PI, fr: 0, motor: false, age };
  const IG = 0.32;
  if (age < IG) return { x: tube[0] - 40 * age, y: tube[1] + 70 * age + 260 * age * age, ang: Math.PI - 0.05 * age / IG, fr: age * 60 < 3 ? 0 : 1 + (age * 60 - 3) / 2, motor: false, age };
  // after ignition: integrate speed/pitch
  let x = tube[0] - 40 * IG, y = tube[1] + 70 * IG + 260 * IG * IG, a = 0, dt = 1 / 240;
  const tt = age - IG;
  for (let s = 0; s < tt; s += dt) {
    const th = Math.PI + 1.25 * E.outC(clamp(s / 0.55)), v = 250 + 2600 * s;
    x += Math.cos(th) * v * dt; y += Math.sin(th) * v * dt; a = th;
  }
  return { x, y, ang: a || Math.PI, fr: 4, motor: true, age };
}
function seekerView(ctx, t, x, y, w, h, k) {   // k: dive progress 0..1
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  rectF(ctx, x, y, w, h, '#1b1f22');
  const hor = y + h * lerp(0.42, -0.2, E.inC(k));          // horizon climbs out of frame as it pitches down
  rectF(ctx, x, y, w, Math.max(0, hor - y), '#2c3236');
  // ground grid in perspective, rushing in
  const cx = x + w / 2, spd = lerp(1, 12, E.inC(k));
  ctx.strokeStyle = 'rgba(210,225,230,0.35)'; ctx.lineWidth = 2;
  for (let i = -14; i <= 14; i++) { ctx.beginPath(); ctx.moveTo(cx + i * 30, hor); ctx.lineTo(cx + i * w * 0.25, y + h + 400); ctx.stroke(); }
  const ph = (t * spd) % 1;
  for (let j = 0; j < 14; j++) { const d = Math.pow((j + ph) / 14, 2.2); const yy = lerp(hor, y + h + 200, d); line(ctx, x, yy, x + w, yy, 'rgba(210,225,230,0.3)', 1.5); }
  // target
  const ts = lerp(0.35, 6, E.inX(k)), ty = lerp(hor + 30, y + h * 0.55, E.ioC(k));
  targetMark(ctx, cx, ty - 11 * ts, 0.3 * ts, '#eef4f6', t, 0.95, 0.3);
  brackets(ctx, cx - 16 * ts - 20, ty - 30 * ts - 20, 32 * ts + 40, 34 * ts + 40, 18, '#ffffff', 3);
  line(ctx, cx - 60 - 16 * ts, ty - 11 * ts, cx - 16 * ts - 20, ty - 11 * ts, '#fff', 2); line(ctx, cx + 16 * ts + 20, ty - 11 * ts, cx + 60 + 16 * ts, ty - 11 * ts, '#fff', 2);
  // noise
  for (let i = 0; i < 40 * (0.3 + k); i++) rectF(ctx, x + hr(i + t * 97) * w, y + hr(i * 3 + t * 71) * h, 2 + hr(i) * 30, 2, '#fff', 0.15);
  ctx.globalCompositeOperation = 'saturation'; rectF(ctx, x, y, w, h, '#808080'); ctx.globalCompositeOperation = 'source-over';
  // hud
  txt(ctx, 'SPIKE NLOS   EO   NFOV x2', x + 26, y + 40, { f: 'Mono', size: 20, w: 700, col: '#eef' });
  txt(ctx, 'DL AH-64E  LINK OK', x + 26, y + 68, { f: 'Mono', size: 16, w: 400, col: '#eef', a: 0.8 });
  const rng = Math.round(lerp(3200, 0, E.inC(k)));
  txt(ctx, `RNG ${String(rng).padStart(4, '0')} M`, x + w - 26, y + 40, { f: 'Mono', size: 20, w: 700, col: '#eef', align: 'right' });
  txt(ctx, `TTI ${(lerp(3.0, 0, k)).toFixed(1)} S`, x + w - 26, y + 68, { f: 'Mono', size: 16, w: 400, col: '#eef', align: 'right', a: 0.8 });
  if (Math.floor(t * 4) % 2 === 0) txt(ctx, 'TRK LOCK', cx, y + h - 36, { f: 'Mono', size: 22, w: 700, col: '#fff', align: 'center' });
  brackets(ctx, x + 14, y + 14, w - 28, h - 28, 34, '#eef', 3);
  ctx.restore();
}
function sSpike(ctx, t) {
  const a = T.SPIKE;
  // punch-in on the tube, then follow the climb
  const pin = ease(a - 0.1, a + 0.25, t, E.outC) * (1 - ease(a + 0.4, a + 1.0, t, E.ioC));
  const m = spikeMissile(t);
  const tube = apW({ x: SPK.x, y: SPK.y, s: SPK.s, tilt: 0 }, AP.TUBE);
  const z = 1 + 0.8 * pin;
  const follow = ease(a + 0.5, a + 1.3, t, E.ioC);
  const fx = lerp(tube[0], W / 2, 1 - pin), fy = lerp(tube[1], H / 2, 1 - pin) + follow * -260;
  world(ctx, t, (t - a) * 160 + 9000, { sky: 'dusk', groundY: 1010 + follow * 260 });
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-fx, -fy);
  // back-blast cloud from the canister
  for (let i = 0; i < 12; i++) {
    const age = t - a - 0.01; if (age < 0) break;
    const dir = -0.2 + hs(i * 3) * 0.5, sp = 200 + hr(i) * 400, f = (1 - Math.exp(-3 * age)) / 3;
    const q = clamp(age / 2.2);
    puff(ctx, tube[0] + 60 + Math.cos(dir) * sp * f, tube[1] + Math.sin(dir) * sp * f - age * 20, (10 + 30 * q + hr(i * 5) * 10) * 1.2, 'smoke', 0.8 * (1 - q));
  }
  const bob = Math.sin(t * 2.1) * 6;
  drawApache(ctx, { x: SPK.x, y: SPK.y + bob, s: SPK.s, tilt: Math.sin(t * 1.3) * 0.015 - 0.04 * ease(a, a + 0.1, t) * (1 - ease(a + 0.2, a + 0.8, t)), t });
  // smoke trail from the ignition point
  smokeTrail(ctx, t, a + 0.34, a + 3, 55, tt => { const s = spikeMissile(tt); return s.motor ? [s.x - Math.cos(s.ang) * 20, s.y - Math.sin(s.ang) * 20] : null; }, { life: 2.2, r0: 8, r1: 44, a: 0.75, rise: 18, seed: 3 });
  if (m.age > -0.1 && m.y > -2000) drawSpike(ctx, m.x, m.y + (m.age < 0 ? bob : 0), m.ang, 2 * SPK.s / 1.5, m.fr, t, m.motor);
  if (m.motor && m.age < 0.45) glow(ctx, m.x, m.y, 300, '#ffb060', 1 - (m.age - 0.32) / 0.13);
  ctx.restore();
  // caption
  const cp = t - bt(58);
  if (cp > 0) {
    const ca = 1 - ease(bt(60) - 0.2, bt(60) + 0.1, t);
    ctx.save(); ctx.globalAlpha = ca;
    slam(ctx, 'SPIKE NLOS', 100, 900, cp, { f: 'Anton', size: 130, col: C.white, track: 3, from: 1.8 });
    decode(ctx, 'COLD EJECT. CLIMB OUT OF SIGHT. DIVE ON YOU.', 104, 960, ease(bt(58) + 0.2, bt(59) + 0.2, t, E.lin), { f: 'Mono', size: 24, w: 700, col: C.red, track: 1 }, 6);
    kr(ctx, '냉발사 → 시야 밖 급상승 → 급강하', 104, 1004, { size: 26, a: ease(bt(59), bt(59) + 0.4, t) });
    ctx.restore();
  }
  // seeker picture-in-picture, then takes over the screen
  const pip = ease(bt(58), bt(58) + 0.3, t, E.outX);
  if (pip > 0) {
    const full = ease(bt(60), bt(60) + 0.35, t, E.ioX);
    const px0 = lerp(1180, 0, full), py0 = lerp(170, 0, full), pw = lerp(680, W, full), ph = lerp(440, H, full);
    const slide = (1 - pip) * 800;
    ctx.save(); ctx.translate(slide, 0);
    if (full < 1) plate(ctx, px0 - 6, py0 - 6, pw + 12, ph + 12, { fill: '#000', c: 14 });
    seekerView(ctx, t, px0, py0, pw, ph, ease(bt(59), bt(64), t, E.lin));
    ctx.restore();
    if (full > 0) { FX.scan = 0.25 * full; FX.grain = 0.14 + 0.2 * ease(bt(62), bt(64), t); }
    const st = ease(bt(63), bt(64), t, E.inC);
    if (st > 0) { for (let i = 0; i < 90; i++) rectF(ctx, 0, hr(i + Math.floor(t * 60) * 0.37) * H, W, 3 + hr(i * 2) * 10, '#fff', st * 0.3 * hr(i * 5 + t)); FX.flash = st * 0.9; }
  }
}

// ======================================= SCENE 6: DRONES =======================================
const EAG = 3.0, SHD = 3.3;
function sweepEagle(tt) { const k = inv(T.DRONE + 0.12, T.DRONE + 0.95, tt); return [lerp(2400, -900, k), 330 + Math.sin(tt * 3) * 6]; }
function sweepShadow(tt) { const k = inv(T.DRONE + 0.28, T.DRONE + 1.02, tt); return [lerp(2300, -500, k), 660 + Math.sin(tt * 4) * 5]; }
function shadowLase(tt) { return [lerp(1180, 860, inv(bt(72), bt(80), tt)), 330 + Math.sin(tt * 1.7) * 14]; }
function eagleLase(tt) { return [lerp(1760, 1540, inv(bt(72), bt(80), tt)), 150 + Math.sin(tt * 1.3) * 10]; }
const PLAYER = [960, 900];
function sDrones(ctx, t) {
  const a = T.DRONE;
  if (t < bt(66)) {
    // --- sweep past through the smoke of the Spike hit
    world(ctx, t, (t - a) * 600 + 14000, { sky: 'dusk', groundY: 1000 });
    explosion(ctx, t, a, 960, 960, 1.4, 21);
    smokeTrail(ctx, t, a + 0.1, a + 3, 14, () => [960, 930], { life: 3, r0: 30, r1: 160, a: 0.8, rise: 80, shade: 'dark', seed: 8, wind: -30 });
    droneTrail(ctx, 'GrayEagle', t, tt => tt < a + 0.12 ? null : sweepEagle(tt), EAG);
    droneTrail(ctx, 'ShadowUAV', t, tt => tt < a + 0.28 ? null : sweepShadow(tt), SHD);
    const e = sweepEagle(t), s = sweepShadow(t);
    drawDrone(ctx, 'GrayEagle', e[0], e[1], EAG, t);
    drawDrone(ctx, 'ShadowUAV', s[0], s[1], SHD, t);
    // speed lines
    for (let i = 0; i < 26; i++) { const y = hr(i * 3.3) * H, x = W - ((t * 5200 + hr(i) * 3000) % (W + 1400)); line(ctx, x, y, x + 300 + hr(i * 7) * 300, y, '#fff', 2, 0.12 * ease(a, a + 0.2, t) * (1 - ease(a + 0.9, a + 1.0, t))); }
  } else if (t < bt(72)) {
    // --- spec cards, split on a slanted divider
    const d = ease(bt(66), bt(66) + 0.3, t, E.outX);
    const topX = 1110, botX = 810;
    // left: Gray Eagle over a fast day sky
    ctx.save(); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(lerp(-400, topX, d), 0); ctx.lineTo(lerp(-700, botX, d), H); ctx.lineTo(0, H); ctx.closePath(); ctx.clip();
    world(ctx, t, t * 1400, { sky: 'day', groundY: 1500, ground: false, haze: false });
    for (let i = 0; i < 18; i++) { const y = hr(i * 3.3) * H, x = W - ((t * 2600 + hr(i) * 3000) % (W + 1400)); line(ctx, x, y, x + 260, y, '#fff', 2, 0.25); }
    const ep = [560 + Math.sin(t * 1.4) * 14, 430 + Math.sin(t * 2.2) * 10];
    droneTrail(ctx, 'GrayEagle', t, tt => [ep[0] + (t - tt) * 1400, ep[1]], 3.6);
    drawDrone(ctx, 'GrayEagle', ep[0], ep[1], 3.6, t);
    const la = ease(bt(66) + 0.1, bt(67), t, E.outX);
    ctx.save(); ctx.globalAlpha = la; ctx.translate((1 - la) * -120, 0);
    txt(ctx, 'MQ-1C GRAY EAGLE', 90, 700, { f: 'Anton', size: 84, col: C.white, track: 2, shadow: 'rgba(0,20,60,0.4)' });
    kr(ctx, '그레이 이글  ·  원거리 헬파이어 지원', 94, 746, { size: 26, col: '#e8f2ff' });
    statBar(ctx, 94, 812, 560, 'HULL', 9000, 9000, ease(bt(67), bt(68), t, E.lin), C.white);
    spec(ctx, 94, 880, 'ARMAMENT', 'AGM-114 HELLFIRE', ease(bt(67), bt(68), t, E.lin), '#dff');
    spec(ctx, 94, 960, 'SUPPORT', 'GUARDIAN TAKES 12% LESS DAMAGE', ease(bt(67) + 0.15, bt(68) + 0.3, t, E.lin), '#dff');
    ctx.restore();
    ctx.restore();
    // right: RQ-7B Shadow at night
    ctx.save(); ctx.beginPath(); ctx.moveTo(lerp(-400, topX, d), 0); ctx.lineTo(W, 0); ctx.lineTo(W, H); ctx.lineTo(lerp(-700, botX, d), H); ctx.closePath(); ctx.clip();
    world(ctx, t, t * 900, { sky: 'night', groundY: 1300, ground: false });
    const sp = [1420 + Math.sin(t * 1.9) * 12, 380 + Math.sin(t * 2.6) * 10];
    droneTrail(ctx, 'ShadowUAV', t, tt => [sp[0] + (t - tt) * 900, sp[1]], 5);
    drawDrone(ctx, 'ShadowUAV', sp[0], sp[1], 5, t);
    const rb = ease(bt(68), bt(68) + 0.4, t, E.outX);
    ctx.save(); ctx.globalAlpha = rb; ctx.translate((1 - rb) * 120, 0);
    txt(ctx, 'RQ-7B SHADOW', 1100, 700, { f: 'Anton', size: 84, col: C.white, track: 2 });
    kr(ctx, '섀도  ·  레이저로 표적 지시', 1104, 746, { size: 26, col: '#ffd9d4' });
    statBar(ctx, 1104, 812, 560, 'HULL', 3000, 9000, ease(bt(69), bt(70), t, E.lin), C.red);
    spec(ctx, 1104, 880, 'SENSOR', 'LASER DESIGNATOR', ease(bt(69), bt(70), t, E.lin), '#fcc');
    spec(ctx, 1104, 960, 'SUPPORT', 'GUARDIAN +5% SPEED, LINKED SALVOS', ease(bt(69) + 0.15, bt(70) + 0.3, t, E.lin), '#fcc');
    ctx.restore();
    ctx.restore();
    // divider
    line(ctx, lerp(-400, topX, d), 0, lerp(-700, botX, d), H, '#fff', 6, 0.9);
    const fl = t > bt(70) ? Math.exp(-(t - bt(70)) * 6) : 0; if (fl > 0.01) line(ctx, topX, 0, botX, H, C.cyan, 30, fl * 0.5);
  } else {
    // --- lase, lock, linked salvo
    world(ctx, t, 20000 + (t - bt(72)) * 90, { sky: 'dusk', groundY: 1000 });
    const s = shadowLase(t), e = eagleLase(t);
    drawDrone(ctx, 'GrayEagle', e[0], e[1], 2.2, t);
    // laser
    const sen = [s[0] + JSONS.ShadowUAV.sensor[0] * 3.3, s[1] + JSONS.ShadowUAV.sensor[1] * 3.3];
    const la0 = bt(73), lock = bt(77);
    if (t > la0 && t < 39.6) {
      const fl = 0.7 + 0.3 * hr(Math.floor(t * 60));
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      line(ctx, sen[0], sen[1], PLAYER[0], PLAYER[1] - 40, C.port, 8, 0.25 * fl); line(ctx, sen[0], sen[1], PLAYER[0], PLAYER[1] - 40, '#ff8a80', 2.5, 0.9 * fl);
      ctx.restore();
      glow(ctx, PLAYER[0], PLAYER[1] - 40, 90, C.port, fl);
    }
    drawDrone(ctx, 'ShadowUAV', s[0], s[1], 3.3, t);
    targetMark(ctx, PLAYER[0], PLAYER[1] - 40, 1.2, t > bt(77) ? C.red : '#ffe0dc', t, t < bt(79) + 0.02 ? 1 : 1 - ease(bt(79), bt(79) + 0.2, t), 1 - ease(bt(73), bt(77), t));
    // lock ring
    const lp = ease(la0 + 0.2, lock, t, E.lin);
    if (t > la0 && t < 39.6) {
      const r = lerp(230, 90, E.outC(lp));
      ring(ctx, PLAYER[0], PLAYER[1] - 40, r, lp >= 1 ? C.red : '#ffe0dc', 3, 0.9);
      ring(ctx, PLAYER[0], PLAYER[1] - 40, r + 16, lp >= 1 ? C.red : C.port, 8, 0.95, -Math.PI / 2, -Math.PI / 2 + TAU * lp);
      reticle(ctx, PLAYER[0], PLAYER[1] - 40, r * 0.5, lp >= 1 ? C.red : '#ffe0dc', t, 0.6);
    }
    // hellfire from the Gray Eagle, linked Spikes from above
    const hf0 = lock + 0.05, hit = bt(79) + 0.02;
    if (t > hf0 && t < hit) {
      const k = inv(hf0, hit, t), e0 = eagleLase(hf0);
      const bx = lerp(lerp(e0[0], e0[0] - 80, k), lerp(e0[0] - 80, PLAYER[0], k), k), by = lerp(lerp(e0[1] + 30, e0[1] + 260, k), lerp(e0[1] + 260, PLAYER[1] - 30, k), k);
      const ang = Math.atan2(lerp(230, PLAYER[1] - 30 - e0[1] - 260, k), lerp(-80, PLAYER[0] - e0[0] + 80, k));
      drawHellfire(ctx, bx, by, ang, 3, t, k > 0.15);
    }
    [[680, 0.25], [1040, 0.35], [1330, 0.45]].forEach(([sx, d], i) => {
      const s0 = lock + d, path = tt => { const k = inv(s0, hit, tt); return tt < s0 ? null : [lerp(sx, PLAYER[0] + (i - 1) * 60, E.inQ(k)), lerp(-120, PLAYER[1] - 20, E.inQ(k))]; };
      smokeTrail(ctx, t, s0, hit, 50, path, { life: 1.2, r0: 6, r1: 30, a: 0.6, rise: 10, seed: 40 + i });
      if (t > s0 && t < hit) { const p0 = path(t), p1 = path(t - 0.01) || p0; drawSpike(ctx, p0[0], p0[1], Math.atan2(p0[1] - p1[1], p0[0] - p1[0]) || Math.PI / 2, 2.2, 4, t, true); }
    });
    explosion(ctx, t, hit, PLAYER[0], PLAYER[1] - 30, 1.6, 55);
    // HUD
    ctx.save(); ctx.globalAlpha = ease(bt(72), bt(72) + 0.3, t) * (1 - ease(39.8, 40.085, t));
    txt(ctx, 'RQ-7B  LASING', 90, 170, { f: 'Mono', size: 26, w: 700, col: '#ffd0cc', track: 2 });
    txt(ctx, `HOLD THE LOCK  ${Math.min(2.0, Math.max(0, t - la0 - 0.2)).toFixed(1)} / 2.0 S`, 90, 210, { f: 'Mono', size: 22, w: 400, col: '#fff' });
    kr(ctx, '시야를 끊거나 섀도를 때리면 락이 풀려요', 90, 250, { size: 22, col: '#ffd9d4' });
    if (t > lock) {
      slam(ctx, 'LOCKED', W - 100, 560, t - lock, { f: 'Anton', size: 120, col: C.red, align: 'right', track: 4, from: 2 });
      slam(ctx, 'LINKED SALVO', W - 100, 660, t - lock - 0.25, { f: 'Anton', size: 80, col: C.white, align: 'right', track: 3, from: 1.8 });
      kr(ctx, '락온 → 가디언이 스파이크 연계 사격', W - 100, 706, { size: 24, align: 'right', col: '#ffd9d4', a: ease(lock + 0.4, lock + 0.7, t) });
    }
    ctx.restore();
  }
  // the Hellfire hits end in an amber hazard wipe (drawn by the transition)
}

// ======================================= SCENE 7: HUMVEE =======================================
const HUMS = 4, HX = 960, HY = 830;
const PART_SEQ = ['Frame', 'Engine', 'WellRear', 'WellFront', 'Cabin', 'Interior', 'WheelRear', 'WheelFront', 'Body', 'DoorRear', 'DoorFront', 'Hood', 'Spare', 'Antenna', 'TurretShield', 'Turret'];
const PART_LABEL = { Frame: 'LADDER FRAME', Engine: '6.5L V8 DIESEL', WellRear: 'REAR WHEEL WELL', WellFront: 'FRONT WHEEL WELL', Cabin: 'CABIN', Interior: 'CREW SEATS', WheelRear: 'REAR WHEEL', WheelFront: 'FRONT WHEEL', Body: 'ARMOURED BODY', DoorRear: 'REAR DOOR', DoorFront: 'FRONT DOOR', Hood: 'HOOD', Spare: 'SPARE TYRE', Antenna: 'ANTENNA', TurretShield: 'GUNNER SHIELD', Turret: 'M2 .50 CAL TURRET' };
function partState(n, t) {
  const key = n === 'Gun' ? 'Turret' : n;
  const i = PART_SEQ.indexOf(key), ta = T.HUMVEE + i * 0.25, dur = 0.3;
  if (t < ta - dur) return { a: 0 };
  const c = BG.hbox[n === 'Gun' ? 'Turret' : n] || [112, 60];
  let dx = c[0] - 112, dy = c[1] - 64; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l;
  dx += hs(i * 3) * 0.4; dy += hs(i * 5) * 0.4 - 0.3;
  const dist = 190 + 60 * hr(i), p = E.outQn(clamp((t - (ta - dur)) / dur));
  const age = t - ta;
  return { a: clamp(p * 3), dx: dx * dist * (1 - p), dy: dy * dist * (1 - p), r: hs(i * 7) * 0.9 * (1 - p), flash: age >= 0 ? Math.exp(-age * 12) : 0 };
}
function sHumvee(ctx, t) {
  const a = T.HUMVEE;
  gridBG(ctx, t, 'rgba(255,178,30,0.09)', '#110c05', 64, -t * 20, 0);
  txt(ctx, 'M1151', W / 2 + 200 - (t - a) * 40, 760, { f: 'Anton', size: 560, col: C.amber, align: 'center', a: 0.05, track: 20 });
  light(ctx, HX, HY - 200, 900, 'rgba(255,170,40,1)', 0.12);
  // blueprint dimension lines
  const dl = ease(a, a + 0.8, t, E.outC);
  const x0 = HX - 112 * HUMS, x1 = HX + 112 * HUMS;
  line(ctx, x0, HY + 60, lerp(x0, x1, dl), HY + 60, C.amber, 2, 0.6);
  line(ctx, x0, HY + 44, x0, HY + 76, C.amber, 2, 0.6 * dl); line(ctx, x1, HY + 44, x1, HY + 76, C.amber, 2, 0.6 * dl);
  txt(ctx, 'M1151 // SIDE ELEVATION // 1 CELL = 2 PX', HX, HY + 100, { f: 'Mono', size: 20, w: 700, col: C.amber, align: 'center', a: 0.7 * dl, track: 3 });
  line(ctx, 0, HY, W, HY, C.amber, 1, 0.25);
  // cold start then idle bob, gun, drive off
  const catchT = bt(89), fire0 = catchT + 0.05, fire1 = bt(91), go = bt(91) + 0.05;
  const drive = ease(go, go + 0.9, t, E.inC);
  const hx = HX - drive * 1500;
  const bob = t > catchT ? Math.sin(t * 55) * 0.5 : 0;
  const gun = t > bt(88) ? -0.06 * ease(bt(88), bt(88) + 0.3, t, E.ioC) + (t > fire0 && t < fire1 ? hs(Math.floor(t * 60)) * 0.015 : 0) : 0;
  const lights = t < bt(88) ? 0 : t < catchT ? (0.25 + 0.2 * Math.abs(Math.sin(t * 34))) : 1;
  // dust when driving
  if (t > go) for (let i = 0; i < 16; i++) { const ts = go + i * 0.06; if (t < ts) continue; const age = t - ts, wx = HX - 1500 * E.inC(inv(go, go + 0.9, ts)) + (HUM.rear[0] - 112) * HUMS; puff(ctx, wx + age * 120, HY - 20 - age * 40, 20 + age * 60, 'dust', 0.6 * (1 - clamp(age / 0.9))); }
  drawHumvee(ctx, hx, HY, HUMS, { part: t < bt(88) ? (n => partState(n, t)) : null, wheel: drive * 40, gun, lights, bob, brake: false });
  // exhaust smoke & flame on the catch
  if (t > catchT - 0.05) {
    const ex = [hx + (HUM.exhaust[0] - 112) * HUMS, HY + (HUM.exhaust[1] - HUM.ground) * HUMS];
    const age = t - catchT;
    if (age > 0 && age < 0.18) glow(ctx, ex[0] + 20, ex[1] - 10, 160, '#ff8a20', 1 - age / 0.18);
    smokeTrail(ctx, t, catchT, catchT + 0.5, 30, () => ex, { life: 1.4, r0: 12, r1: 70, a: 0.85, rise: 90, shade: 'dark', seed: 77, wind: 60 });
  }
  // part labels (last three stay readable)
  if (t < bt(89)) PART_SEQ.forEach((n, i) => {
    const ta = a + i * 0.25, age = t - ta; if (age < 0 || age > 0.5) return;
    const c = BG.hbox[n]; const sx = HX + (c[0] - 112) * HUMS, sy = HY + (c[1] - HUM.ground) * HUMS;
    const al = clamp(age / 0.06) * (1 - clamp((age - 0.3) / 0.2));
    const ly = 250 + (i % 2) * 46, lx = clamp(sx, 330, W - 330);
    ctx.save(); ctx.globalAlpha = al;
    line(ctx, sx, sy, sx, ly + 12, C.amber, 1.5, 0.7); line(ctx, sx, ly + 12, lx, ly + 12, C.amber, 1.5, 0.7);
    rectF(ctx, sx - 4, sy - 4, 8, 8, C.amber);
    txt(ctx, `${String(i + 1).padStart(2, '0')}  ${PART_LABEL[n]}`, lx, ly, { f: 'Mono', size: 22, w: 700, col: C.white, align: 'center', track: 2 });
    ctx.restore();
  });
  // counter
  const nOn = PART_SEQ.filter((n, i) => t >= a + i * 0.25).length;
  if (t < bt(88) + 0.3) txt(ctx, `ASSEMBLY  ${String(nOn).padStart(2, '0')}/16`, W / 2, 110, { f: 'Mono', size: 26, w: 700, col: C.amber, align: 'center', track: 4, a: ease(a, a + 0.2, t) * (1 - ease(bt(88), bt(88) + 0.3, t)) });
  // M2: red tracers at ~470 rpm
  if (t > fire0 && t < fire1 + 0.3) {
    const mz = humveeMuzzle(hx, HY + bob * HUMS, HUMS, gun);
    const k = Math.floor((t - fire0) / 0.128);
    if (t < fire1 && ((t - fire0) % 0.128) < 0.04) muzzle(ctx, mz[0], mz[1], gun, 2.2, t, 9);
    for (let j = Math.max(0, k - 4); j <= k; j++) {
      const tb = fire0 + j * 0.128, age = t - tb; if (tb > fire1 || age < 0 || age > 0.4) continue;
      const d0 = age * 4200; tracer(ctx, mz[0] - Math.cos(gun) * d0, mz[1] - Math.sin(gun) * d0, mz[0] - Math.cos(gun) * (d0 + 160), mz[1] - Math.sin(gun) * (d0 + 160), '#ff3020', 3.5);
      burst(ctx, t, tb, 300 + j, 1, mz[0] + 60 * HUMS * 0.2, mz[1] + 10, { speed: 260, life: 0.8, g: 1800, size: 6, col: '#e8b040', a0: -Math.PI * 0.6, a1: -Math.PI * 0.4 });
    }
  }
  // title
  const tp = ease(bt(88), bt(88) + 0.4, t, E.outX) * (1 - ease(bt(91) + 0.2, bt(92), t));
  if (tp > 0) {
    ctx.save(); ctx.globalAlpha = tp; ctx.translate(-(1 - tp) * 200, 0);
    rectF(ctx, 80, 92, 8, 128, C.amber);
    txt(ctx, 'M1151 HUMVEE', 110, 170, { f: 'Anton', size: 96, col: C.white, track: 3 });
    plate(ctx, 112, 190, 92, 34, { fill: C.amber, c: 8 });
    txt(ctx, 'BOSS', 158, 215, { f: 'Mono', size: 20, w: 700, col: '#1a1000', align: 'center', track: 3 });
    kr(ctx, '험비  ·  치누크 강습 공수 → 냉간 시동 → M2', 222, 216, { size: 24, col: '#ffe3b0' });
    ctx.restore();
  }
}

// ======================================= SCENE 8: BREAK =======================================
function sBreak(ctx, t) {
  const a = T.BREAK;
  rectF(ctx, 0, 0, W, H, '#070203');
  const pulse = [bt(92), bt(93), bt(94), bt(95)].reduce((m, b) => Math.max(m, t >= b ? Math.exp(-(t - b) * 5) : 0), 0);
  light(ctx, W / 2, H / 2, 1200, 'rgba(255,30,20,1)', 0.25 + 0.35 * pulse);
  // guardian silhouette crossing behind the text
  drawApache(ctx, { x: lerp(1700, 300, inv(a - 0.2, a + 2.2, t)), y: 470 + Math.sin(t * 2) * 10, s: 2.6, tilt: -0.08, t, sil: '#000000' });
  const on = Math.floor((t - a) / 0.25) % 2 === 0;
  ctx.save(); ctx.translate(W / 2, 600); const sc = 1 + 0.04 * pulse; ctx.scale(sc, sc);
  txt(ctx, 'WARNING', 0, 0, { f: 'Anton', size: 280, col: on ? C.red : null, stroke: C.red, lw: 5, align: 'center', track: 20, a: 0.95 });
  ctx.restore();
  decode(ctx, 'HOSTILE AIR ACTIVITY  //  5 PHASES  //  NO BLACK BARS', W / 2 - 470, 700, ease(a + 0.2, a + 1.0, t, E.lin), { f: 'Mono', size: 26, w: 700, col: '#ffd0cc', track: 2 }, 13);
  kr(ctx, '적 항공기 접근 중', W / 2, 750, { align: 'center', col: C.red, size: 30, a: ease(a + 0.5, a + 0.9, t) });
  cutFrame(ctx, t, ease(a, a + 0.3, t, E.outX), C.red, 'WARNING', '경고', t - a);
  // shutters close on the downbeat of the last phrase
  const sh = ease(bt(95), T.DPACHE, t, E.inX);
  if (sh > 0) {
    const hh = sh * H / 2;
    rectF(ctx, 0, 0, W, hh, '#120405'); stripes(ctx, 0, hh - 24, W, 24, C.red, t * 200, 1.7);
    rectF(ctx, 0, H - hh, W, hh, '#120405'); stripes(ctx, 0, H - hh, W, 24, C.red, -t * 200, 1.7);
  }
}

// ======================================= SCENE 8b: AH-64D APACHE =======================================
// the original boss: reveal, sortie, long charges, ram charge with rockets, Hydra rain, strafing run
const DS = 2.2, DG = 1000, OLIVE = '#a4c250';
const TGT = [960, DG - 72];
function hydra(ctx, x, y, ang, s = 1.6) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
  rectF(ctx, -10 * s, -1.5 * s, 20 * s, 3 * s, '#dcdcd0'); rectF(ctx, 7 * s, -1.5 * s, 3 * s, 3 * s, '#4c4c44'); rectF(ctx, -10 * s, -3 * s, 3 * s, 6 * s, '#8a8a80');
  ctx.restore();
  glow(ctx, x - Math.cos(ang) * 12 * s, y - Math.sin(ang) * 12 * s, 46 * s, '#ffb050', 0.95);
}
function band(ctx, x0, y0, x1, y1, w, t, a, col = C.red) {           // telegraphed corridor with flowing chevrons
  if (a <= 0.003) return;
  const ang = Math.atan2(y1 - y0, x1 - x0), L = Math.hypot(x1 - x0, y1 - y0);
  ctx.save(); ctx.translate(x0, y0); ctx.rotate(ang); ctx.globalAlpha *= a;
  rectF(ctx, 0, -w / 2, L, w, col, 0.14);
  line(ctx, 0, -w / 2, L, -w / 2, col, 3, 0.85); line(ctx, 0, w / 2, L, w / 2, col, 3, 0.85);
  ctx.strokeStyle = col; ctx.lineWidth = 7; ctx.globalAlpha *= 0.55;
  const sp = 110, off = (t * 1100) % sp;
  for (let d = off; d < L; d += sp) { ctx.beginPath(); ctx.moveTo(d - 22, -w * 0.24); ctx.lineTo(d + 4, 0); ctx.lineTo(d - 22, w * 0.24); ctx.stroke(); }
  ctx.restore();
}
function edgeArrow(ctx, side, y, t, a) {                               // blinking arrow on the screen edge
  if (a <= 0.003 || Math.floor(t * 8) % 2) return;
  const x = side < 0 ? 56 : W - 56;
  ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = C.red; ctx.beginPath();
  ctx.moveTo(x + side * 34, y); ctx.lineTo(x - side * 22, y - 44); ctx.lineTo(x - side * 22, y + 44); ctx.closePath(); ctx.fill(); ctx.restore();
  glow(ctx, x, y, 240, C.red, 0.55 * a);
}
function approachBanner(ctx, t, a) {
  if (a <= 0.003) return;
  const on = Math.floor(t * 6) % 2 === 0;
  ctx.save(); ctx.globalAlpha *= a;
  plate(ctx, W / 2 - 340, 300, 680, 92, { fill: 'rgba(36,6,6,0.88)', line: C.red, lw: 3, c: 16 });
  stripes(ctx, W / 2 - 332, 308, 44, 76, C.red, t * 60, 1.2); stripes(ctx, W / 2 + 288, 308, 44, 76, C.red, -t * 60, 1.2);
  txt(ctx, 'HIGH-SPEED APPROACH', W / 2, 344, { f: 'Chakra', size: 34, w: 700, col: on ? '#ffffff' : '#ffb0a8', align: 'center', track: 4 });
  kr(ctx, '고속 접근 경보', W / 2, 378, { align: 'center', size: 24, col: C.red });
  ctx.restore();
}
function dCaption(ctx, t, t0, t1, big, sub, k) {
  const age = t - t0; if (age < 0 || t > t1) return;
  ctx.save(); ctx.globalAlpha = 1 - ease(t1 - 0.2, t1, t);
  rectF(ctx, 80, 104, 8, 176, OLIVE);
  slam(ctx, big, 110, 186, age, { f: 'Anton', size: 96, col: C.white, track: 3, from: 1.6 });
  decode(ctx, sub, 114, 234, ease(t0 + 0.1, t0 + 0.6, t, E.lin), { f: 'Mono', size: 22, w: 700, col: OLIVE, track: 2 }, big.length);
  if (k) kr(ctx, k, 114, 272, { size: 24, col: '#e6f2c8', a: ease(t0 + 0.3, t0 + 0.6, t) });
  ctx.restore();
}
function linPath(t, t0, t1, a, b, tilt, flip) { if (t < t0 || t > t1) return null; const k = inv(t0, t1, t); return { x: lerp(a[0], b[0], k), y: lerp(a[1], b[1], k), tilt, flip }; }
function drawD(ctx, st, t, ghosts = 0) {
  if (!st) return;
  for (let k = ghosts; k >= 1; k--) {
    const g = st.path ? st.path(t - k * 0.018) : null;
    if (g) drawApache(ctx, { ...g, model: 'D', s: DS, t, a: 0.16 * (1 - k / (ghosts + 1)), lights: false });
  }
  drawApache(ctx, { ...st, model: 'D', s: DS, t });
}
// --- reveal + sortie
function dReveal(t) {
  const a = T.DPACHE, u = ease(a, a + 1.2, t, E.outC);
  let x = lerp(2500, 1220, u), y = lerp(860, 540, u);
  let tilt = -0.32 * (1 - ease(a + 0.4, a + 1.0, t, E.ioC)) + 0.22 * ease(a + 0.7, a + 1.1, t, E.ioC) * (1 - ease(a + 1.3, a + 2.2, t, E.ioC));
  y += Math.sin(t * 2.2) * 7; tilt += Math.sin(t * 1.4) * 0.015;
  const c0 = bt(102);                                       // sortie: straight climb out of the map
  if (t > c0) { const k = t - c0; y -= 60 * k + 1500 * k * k; tilt += -0.05 * ease(c0, c0 + 0.2, t); }
  return { x, y, tilt };
}
// --- long charges: horizontal from the right, dive from the upper left, low from the left
const LC = [
  { tel: bt(104), go: bt(104) + 0.75, dur: 0.4, a: [2350, TGT[1] - 20], b: [-950, TGT[1] - 20], tilt: -0.14, flip: false, side: 1, ay: TGT[1] - 20 },
  { tel: bt(106) + 0.25, go: bt(108), dur: 0.36, a: [-640, -330], b: [2500, 2140], tilt: 0.62, flip: true, side: -1, ay: 240 },
  { tel: bt(109), go: bt(110) + 0.25, dur: 0.4, a: [-950, TGT[1] - 30], b: [2400, TGT[1] - 30], tilt: 0.14, flip: true, side: -1, ay: TGT[1] - 30 },
];
function lcState(t) {
  for (const c of LC) { const st = linPath(t, c.go, c.go + c.dur, c.a, c.b, c.tilt, c.flip); if (st) return { ...st, path: tt => linPath(tt, c.go, c.go + c.dur, c.a, c.b, c.tilt, c.flip) }; }
  return null;
}
// --- ram charge with rockets thrown out both sides
const RAMS = [{ t0: bt(113) + 0.2, t1: bt(114) + 0.15, x0: 1480, x1: 620, flip: false }, { t0: bt(114) + 0.8, t1: bt(115) + 0.75, x0: 620, x1: 1480, flip: true }];
const RAM_Y = 640;
function ramState(t) {
  const a = bt(112);
  if (t < a || t > bt(116) + 0.2) return null;
  let x = lerp(2400, 1480, ease(a, a + 0.35, t, E.outC)), flip = false, tilt = 0.02 + Math.sin(t * 1.4) * 0.015;
  for (const r of RAMS) {
    if (t >= r.t0) { x = lerp(r.x0, r.x1, ease(r.t0, r.t1, t, E.ioC)); flip = r.flip; tilt = (r.flip ? 1 : -1) * 0.2 * Math.sin(Math.PI * inv(r.t0, r.t1, t)); }
  }
  if (t > bt(116) - 0.2) { const k = ease(bt(116) - 0.2, bt(116) + 0.2, t, E.inC); x += k * 1400; tilt = 0.25 * k; flip = true; }
  return { x, y: RAM_Y + Math.sin(t * 2.3) * 6, tilt, flip };
}
function ramRockets() {
  const out = [];
  RAMS.forEach((r, j) => {
    for (let i = 0; i * 5 / 60 < r.t1 - r.t0; i++) {
      const ts = r.t0 + i * 5 / 60, k = E.ioC(inv(r.t0, r.t1, ts));
      const x = lerp(r.x0, r.x1, k), dir = r.flip ? 0 : Math.PI, th = (30 + 20 * hr(j * 31 + i)) * Math.PI / 180;
      out.push({ ts, x, y: RAM_Y + 30, ang: dir + (i % 2 ? th : -th) * (r.flip ? -1 : 1), down: i % 2 === 1 });
    }
  });
  return out;
}
let RAMR = null;
// --- Hydra rain
const HY_N = 38, HY_L = bt(118), HY_DT = 2 / 60, HY_FL = 0.42;
function hydraOrigin(t) { const u = ease(bt(116), bt(116) + 0.5, t, E.outC); let x = lerp(2400, 1180, u), y = lerp(80, 230, u); if (t > bt(122) + 0.2) { const k = t - bt(122) - 0.2; y -= 1400 * k * k; x -= 300 * k; } return { x, y: y + Math.sin(t * 2) * 5, tilt: -0.1 }; }
function hydraTarget(i) { return [240 + 1440 * (i / (HY_N - 1)) + hs(i * 7.7) * 30, DG - 4]; }
// --- strafing run
const SR0 = bt(124) + 0.2, SR1 = bt(127) + 0.2;
function strafeState(t) { return linPath(t, SR0, SR1, [2450, DG - 250], [-950, DG - 250], -0.12, false); }
function smallBoom(ctx, t, t0, x, y, seed, s = 1) {
  const age = t - t0; if (age < 0 || age > 1.2) return;
  light(ctx, x, y, 260 * s, 'rgba(255,170,90,1)', 0.9 * Math.exp(-age * 7));
  for (let i = 0; i < 4; i++) { const q = clamp(age / (0.5 + hr(seed + i) * 0.6)); if (q >= 1) continue; puff(ctx, x + hs(seed + i) * 26 * s, y - 14 * s - age * 60 * s - i * 8, (14 + 16 * q) * s, q < 0.2 ? 'hot' : q < 0.45 ? 'fire' : 'dark', 1 - q); }
  burst(ctx, t, t0, seed, 14, x, y, { speed: 700 * s, life: 0.6, g: 1400, size: 5 * s, add: true, col: q => q > 0.5 ? '#fff0c0' : '#ff8a30', a0: Math.PI * 1.1, a1: Math.PI * 1.9 });
  burst(ctx, t, t0, seed + 9, 8, x, y, { speed: 500 * s, life: 0.9, g: 1600, size: 6 * s, col: '#6a4a30', a0: Math.PI * 1.15, a1: Math.PI * 1.85 });
}
function sDpache(ctx, t) {
  const a = T.DPACHE;
  world(ctx, t, 50000 + (t - a) * 180, { sky: 'dusk', groundY: DG, glow: [960, 600, 1000, 'rgba(160,200,80,1)', 0.06] });
  // target on the ground once the attacks start
  const tg = ease(bt(104) - 0.3, bt(104), t) * (1 - ease(bt(116) - 0.3, bt(116), t)) + ease(bt(124), bt(124) + 0.2, t) * (1 - ease(T.MONT - 0.2, T.MONT, t));
  targetMark(ctx, TGT[0], TGT[1], 1.1, '#f2f8fa', t, tg, 0.6);

  // ---------- reveal & sortie
  if (t < bt(104)) {
    const st = dReveal(t);
    if (t > bt(102)) flares(ctx, t, bt(102) + 0.05, 83, 8, tt => [dReveal(tt).x + 40, dReveal(tt).y + 60], 1, 1.3);
    apacheVapor(ctx, t, tt => dReveal(tt), DS, t < a + 1.2 || t > bt(102) ? 1 : 0.45);
    drawD(ctx, st, t);
    const tp = ease(bt(97), bt(97) + 0.4, t, E.outX) * (1 - ease(bt(103), bt(104), t));
    if (tp > 0) {
      ctx.save(); ctx.globalAlpha = tp; ctx.translate(-(1 - tp) * 200, 0);
      rectF(ctx, 80, 92, 8, 128, OLIVE);
      txt(ctx, 'AH-64D APACHE', 110, 170, { f: 'Anton', size: 96, col: C.white, track: 3 });
      plate(ctx, 112, 190, 92, 34, { fill: OLIVE, c: 8 });
      txt(ctx, 'BOSS', 158, 215, { f: 'Mono', size: 20, w: 700, col: '#16200a', align: 'center', track: 3 });
      kr(ctx, '아파치 D형  ·  첫 번째 보스', 222, 216, { size: 24, col: '#e6f2c8' });
      statBar(ctx, 114, 820, 560, 'HULL', 46000, 46000, ease(bt(98), bt(99), t, E.lin), OLIVE);
      spec(ctx, 114, 890, 'PHASES', '4  //  SPEED x1.0 > x1.4', ease(bt(99), bt(100), t, E.lin), OLIVE);
      spec(ctx, 114, 970, 'LOADOUT', 'HYDRA x38  //  HELLFIRE x8', ease(bt(100), bt(101), t, E.lin), OLIVE);
      ctx.restore();
    }
    const sp = t - bt(102);
    if (sp > 0) {
      ctx.save(); ctx.globalAlpha = 1 - ease(bt(104) - 0.15, bt(104), t);
      slam(ctx, 'SORTIE', W - 110, 900, sp, { f: 'Anton', size: 120, col: C.white, align: 'right', track: 4, from: 1.7 });
      kr(ctx, '출격 · 맵 밖으로 상승 이탈', W - 110, 950, { align: 'right', size: 26, col: '#e6f2c8', a: ease(bt(102) + 0.1, bt(102) + 0.4, t) });
      ctx.restore();
    }
  }
  // ---------- long charges
  else if (t < bt(112)) {
    for (const c of LC) {
      const ta = ease(c.tel, c.tel + 0.15, t) * (1 - ease(c.go + c.dur * 0.6, c.go + c.dur, t));
      if (ta > 0) {
        band(ctx, c.a[0], c.a[1], c.b[0], c.b[1], 190, t, ta);
        edgeArrow(ctx, c.side, c.ay, t, ta * (t < c.go ? 1 : 0));
        approachBanner(ctx, t, ta * (t < c.go + 0.1 ? 1 : 0));
      }
    }
    const st = lcState(t);
    if (st) {
      for (let i = 0; i < 26; i++) { const y = st.y - 200 + hr(i * 3.3) * 400, x = (st.x + (st.flip ? -1 : 1) * (200 + hr(i) * 900)); line(ctx, x, y, x + (st.flip ? -1 : 1) * 380, y, '#ffffff', 2, 0.18); }
      drawD(ctx, st, t, 5);
    }
    dCaption(ctx, t, bt(104), bt(112), 'LONG CHARGE', 'THROUGH YOU, OFF THE MAP, BACK IN FROM ANY SIDE', '데오갓식 긴 돌진 · 왕복 최대 4회');
  }
  // ---------- ram charge + rockets
  else if (t < bt(116)) {
    if (!RAMR) RAMR = ramRockets();
    const st = ramState(t);
    for (const [i, r] of RAMS.entries()) band(ctx, r.x0, RAM_Y, r.x1 + (r.flip ? 380 : -380), RAM_Y, 150, t, ease(r.t0 - 0.45, r.t0 - 0.3, t) * (1 - ease(r.t0, r.t0 + 0.15, t)));
    for (const [i, r] of RAMR.entries()) {
      const age = t - r.ts; if (age < 0) continue;
      const v = 1700, dx = Math.cos(r.ang), dy = Math.sin(r.ang);
      const tHit = r.down ? (DG - r.y) / (v * dy) : 9;
      const path = tt => { const g = Math.min(tt - r.ts, tHit); return g < 0 ? null : [r.x + dx * v * g, r.y + dy * v * g]; };
      smokeTrail(ctx, t, r.ts, r.ts + Math.min(tHit, 0.8), 40, path, { life: 0.8, r0: 5, r1: 22, a: 0.55, rise: 12, seed: 300 + i });
      if (age < tHit && age < 0.8) { const p = path(t); hydra(ctx, p[0], p[1], r.ang, 1.4); }
      if (r.down) smallBoom(ctx, t, r.ts + tHit, r.x + dx * v * tHit, DG - 6, 500 + i, 1);
    }
    if (st) drawD(ctx, { ...st, path: tt => ramState(tt) }, t, RAMS.some(r => t > r.t0 && t < r.t1) ? 4 : 0);
    dCaption(ctx, t, bt(112), bt(116), 'RAM CHARGE', 'SHORT DASH, ROCKETS THROWN OUT BOTH SIDES', '짧은 돌진 + 양옆으로 로켓 살포');
  }
  // ---------- Hydra rain
  else if (t < bt(124)) {
    const st = hydraOrigin(t);
    const pod = [st.x - 70 * DS * 0.5, st.y + 40];
    for (let i = 0; i < HY_N; i++) {
      const tl = bt(116) + 0.55 + i * 0.012, tr = HY_L + i * HY_DT, tg2 = hydraTarget(i);
      const la = ease(tl, tl + 0.08, t) * (1 - ease(tr + HY_FL * 0.6, tr + HY_FL, t));
      const o0 = [1180 - 35 * DS * 0.5, 230 + 40];
      if (la > 0) line(ctx, o0[0], o0[1], tg2[0], tg2[1], C.red, 2, 0.55 * la, [14, 10]);
      if (la > 0) { rectF(ctx, tg2[0] - 10, tg2[1] - 2, 20, 4, C.red, la * 0.8); }
      const age = t - tr;
      if (age >= 0 && age < HY_FL) {
        const k = age / HY_FL, p = [lerp(o0[0], tg2[0], k), lerp(o0[1], tg2[1], k)];
        smokeTrail(ctx, t, tr, tr + HY_FL, 50, tt => { const kk = clamp((tt - tr) / HY_FL); return [lerp(o0[0], tg2[0], kk), lerp(o0[1], tg2[1], kk)]; }, { life: 0.5, r0: 4, r1: 16, a: 0.4, rise: 8, seed: 700 + i });
        hydra(ctx, p[0], p[1], Math.atan2(tg2[1] - o0[1], tg2[0] - o0[0]), 1.3);
      }
      smallBoom(ctx, t, tr + HY_FL, tg2[0], tg2[1], 900 + i, 0.9);
    }
    drawD(ctx, st, t);
    const left = HY_N - clamp(Math.floor((t - HY_L) / HY_DT) + 1, 0, HY_N);
    dCaption(ctx, t, bt(116), bt(124), 'HYDRA RAIN', 'EVERY TRACK DRAWN FIRST, THEN 38 ROCKETS DOWN THEM', '궤적을 먼저 전부 깔고, 그 선 그대로 38발');
    if (t > bt(116) + 0.3) {
      txt(ctx, 'HYDRA', W - 440, 180, { f: 'Mono', size: 22, w: 700, col: OLIVE, track: 3, a: 1 - ease(bt(123), bt(124), t) });
      txt(ctx, String(left).padStart(2, '0') + ' / 38', W - 110, 180, { f: 'Mono', size: 40, w: 700, col: C.white, align: 'right', a: 1 - ease(bt(123), bt(124), t) });
    }
  }
  // ---------- strafing run
  else {
    const st = strafeState(t);
    if (st) {
      const aim = st.x - 360;
      for (let j = 0; j < 40; j++) {
        const tb = SR0 + j * 0.05, age = t - tb; if (age < 0 || tb > SR1) continue;
        const sb = strafeState(tb); if (!sb) continue;
        const mx = sb.x - 105 * DS, my = sb.y + 36 * DS, hx = sb.x - 360, hy = DG - 6;
        if (age < 0.12) { const k = age / 0.12; tracer(ctx, lerp(mx, hx, k), lerp(my, hy, k), lerp(mx, hx, Math.max(0, k - 0.3)), lerp(my, hy, Math.max(0, k - 0.3)), '#ffcc66', 3); }
        if (hx > -50 && hx < W + 50) {
          burst(ctx, t, tb + 0.12, 1200 + j, 6, hx, hy, { speed: 600, life: 0.45, g: 1500, size: 5, add: true, col: '#ffd890', a0: Math.PI * 1.1, a1: Math.PI * 1.9 });
          if (age > 0.12 && age < 1.4) puff(ctx, hx - (age - 0.12) * 40, hy - 16 - (age - 0.12) * 50, 14 + (age - 0.12) * 40, 'dust', 0.7 * (1 - (age - 0.12) / 1.3));
        }
      }
      const g = st.x - 105 * DS;
      if (Math.floor(t * 60) % 4 < 2) muzzle(ctx, g - 20, st.y + 36 * DS, -0.55 + Math.PI, 1.6, t, 4);
      drawD(ctx, { ...st, path: strafeState }, t, 3);
    }
    dCaption(ctx, t, bt(124), T.MONT + 0.2, 'STRAFING RUN', 'LOW ACROSS THE FLOOR, GUN AND ROCKETS', '저공 기총소사 돌파');
  }
  // shutters opening out of the WARNING break
  const op = 1 - ease(a, a + 0.35, t, E.outX);
  if (op > 0) {
    const hh = op * H / 2;
    rectF(ctx, 0, 0, W, hh, '#120405'); stripes(ctx, 0, hh - 24, W, 24, C.red, t * 200, 1.7);
    rectF(ctx, 0, H - hh, W, hh, '#120405'); stripes(ctx, 0, H - hh, W, 24, C.red, -t * 200, 1.7);
  }
}
function dCues() {
  const a = T.DPACHE;
  impact(a, { shake: 26, ca: 9, flash: 0.35, zoom: 0.05, dec: 4.5 });
  cue(a, 'boom', 1.0); cue(a + 0.05, 'rotor', 0.8);
  for (let k = 97; k <= 101; k++) cue(bt(k), 'chirp', 0.45);
  cue(bt(102), 'whoosh', 0.9); cue(bt(102) + 0.05, 'flares', 0.6); impact(bt(102), { shake: 8, ca: 3 });
  for (const c of LC) {
    for (let i = 0; i < 3; i++) cue(c.tel + i * 0.25, 'alarm', 0.5);
    cue(c.go - 0.1, 'whoosh', 1.0);
    const tc = c.go + c.dur * (c.flip ? (c.tilt > 0.3 ? 0.55 : 0.56) : 0.42);
    impact(tc, { shake: 24, ca: 8, zoom: 0.03, dec: 6 }); cue(tc, 'hit', 0.9);
  }
  if (!RAMR) RAMR = ramRockets();
  for (const r of RAMS) { cue(r.t0 - 0.45, 'alarm', 0.4); cue(r.t0, 'whoosh', 0.7); impact(r.t0 + 0.1, { shake: 10, ca: 4 }); }
  for (const r of RAMR) { cue(r.ts, 'rocket', 0.35); if (r.down) { const tHit = (DG - r.y) / (1700 * Math.sin(r.ang)); cue(r.ts + tHit, 'pop', 0.5); } }
  cue(bt(116), 'whoosh', 0.6); cue(bt(116) + 0.55, 'chirp', 0.5);
  for (let i = 0; i < HY_N; i++) { cue(HY_L + i * HY_DT, 'rocket', 0.18); cue(HY_L + i * HY_DT + HY_FL, 'pop', 0.3); if (i % 6 === 0) impact(HY_L + i * HY_DT + HY_FL, { shake: 7, ca: 2 }); }
  cue(bt(124), 'whoosh', 0.8); cue(SR0 + 0.4, 'gun30', 0.8); cue(SR0 + 0.9, 'gun30', 0.8); cue(SR0 + 1.4, 'gun30', 0.7);
  for (let j = 0; j < 40; j += 3) cue(SR0 + j * 0.05 + 0.12, 'pop', 0.2);
  impact(SR0 + 0.8, { shake: 12, ca: 4 });
}

// ======================================= SCENE 9: MONTAGE =======================================
function montageBG(ctx, pal) { const g = ctx.createLinearGradient(0, 0, W, H); g.addColorStop(0, pal[0]); g.addColorStop(1, pal[1]); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }
function bigWord(ctx, s, age, o = {}) {
  const x = o.x ?? W / 2, y = o.y ?? 620;
  slam(ctx, s, x, y, age, { f: 'Anton', size: o.size || 240, col: o.col || C.white, align: o.align || 'center', track: 6, from: 1.5, dur: 0.18 });
  if (o.kr) kr(ctx, o.kr, x, y + 70, { align: o.align || 'center', size: 32, col: o.krCol || C.white, a: clamp(age * 8) * 0.9 });
}
const SHOTS = [];
function initMontage() {
  const m = T.MONT;
  const S = (t0, dur, fn) => SHOTS.push({ t0, t1: t0 + dur, fn });
  S(m, bt(129) - m, (ctx, t, age) => {       // 30mm
    world(ctx, t, t * 300, { sky: 'dusk', groundY: 1400 });
    const p = { x: 1330, y: 400, s: 6, tilt: 0.02, t, gun: -0.25 };
    drawApache(ctx, p);
    const piv = apW(p, AP.GUN), ang = p.tilt + p.gun, mz = [piv[0] - Math.cos(ang) * 33 * 6, piv[1] - Math.sin(ang) * 33 * 6];
    if (Math.floor(age * 60) % 5 < 2) muzzle(ctx, mz[0], mz[1], ang, 3.5, t, 3);
    for (let k = 0; k < 5; k++) { const d0 = ((age * 60 + k * 5) % 25) / 25 * 1400; tracer(ctx, mz[0] - Math.cos(ang) * d0, mz[1] - Math.sin(ang) * d0, mz[0] - Math.cos(ang) * (d0 + 200), mz[1] - Math.sin(ang) * (d0 + 200), '#ffcc66', 5); }
    bigWord(ctx, '30MM', age, { x: 120, y: 900, align: 'left', size: 260, kr: 'M230 체인건' });
  });
  S(bt(129), 0.5, (ctx, t, age) => {        // spike
    world(ctx, t, t * 200 + 500, { sky: 'dusk', groundY: 1300 });
    const x = 1300 - age * 1400, y = 700 - age * 1000;
    smokeTrail(ctx, t, bt(129) - 0.4, bt(129) + 0.5, 60, tt => [1300 - (tt - bt(129)) * 1400 + 40, 700 - (tt - bt(129)) * 1000 + 30], { life: 0.9, r0: 20, r1: 90, a: 0.8, rise: 5, seed: 12 });
    drawSpike(ctx, x, y, Math.atan2(-1000, -1400), 6, 4, t, true);
    bigWord(ctx, 'SPIKE NLOS', age, { x: W - 120, y: 950, align: 'right', size: 200, kr: '대전차 유도탄' });
  });
  S(bt(130), 0.5, (ctx, t, age) => {        // gray eagle
    world(ctx, t, t * 3000, { sky: 'day', groundY: 1500, ground: false });
    for (let i = 0; i < 24; i++) { const y = hr(i * 3.3) * H, x = W - ((t * 6000 + hr(i) * 3000) % (W + 1400)); line(ctx, x, y, x + 400, y, '#fff', 2, 0.35); }
    drawDrone(ctx, 'GrayEagle', 900 + age * 120, 460, 6.5, t);
    bigWord(ctx, 'MQ-1C', age, { x: 120, y: 980, align: 'left', size: 220, kr: '그레이 이글' });
  });
  S(bt(131), 0.5, (ctx, t, age) => {        // shadow at night
    world(ctx, t, t * 800, { sky: 'night', groundY: 1500, ground: false });
    drawDrone(ctx, 'ShadowUAV', 1100 - age * 100, 420, 10, t + 0.97 - age * 0.02);
    bigWord(ctx, 'RQ-7B', age, { x: W - 120, y: 980, align: 'right', size: 220, kr: '섀도', krCol: '#ffd0cc' });
  });
  S(bt(132), 0.5, (ctx, t, age) => {       // humvee headlights
    world(ctx, t, t * 600, { sky: 'night', groundY: 960 });
    drawHumvee(ctx, 1300, 960, 7.5, { lights: 1, wheel: t * 20 });
    bigWord(ctx, 'M1151', age, { x: W - 120, y: 300, align: 'right', size: 220, col: C.amber, kr: '험비', krCol: '#ffe3b0' });
  });
  S(bt(133), 0.5, (ctx, t, age) => {       // items
    gridBG(ctx, t, 'rgba(80,160,220,0.10)', C.navy, 60);
    const items = ['M230ChainGun', 'Mk19Launcher', 'GuardianHelmet', 'GuardianSummon', 'GrayEagleTerminal', 'GrayEagleBuff'];
    items.forEach((n, i) => {
      const p = E.outB(clamp((age - i * 0.04) / 0.15)); if (p <= 0) return;
      const x = 330 + i * 250, y = 460;
      plate(ctx, x - 100, y - 100, 200, 200, { fill: 'rgba(255,255,255,0.04)', line: 'rgba(120,200,255,0.5)', c: 18, a: p });
      spr(ctx, IMG[n], x, y, { s: (IMG[n].width > 60 ? 3 : 5) * p });
    });
    bigWord(ctx, 'NEW GEAR', age, { y: 800, size: 170, kr: '무기 · 장비 · 소환 아이템' });
  });
  S(bt(134), 0.5, (ctx, t, age) => {       // loop silhouette
    world(ctx, t, 400 + age * 900, { sky: 'dusk', groundY: 1200 });
    const ph = Math.PI * 0.8 + age * 1.6;
    drawApache(ctx, { x: 960, y: 480, s: 3.2, tilt: ph, t });
    flares(ctx, t, bt(134) - 0.3, 61, 10, [1060, 560], 1, 2);
    bigWord(ctx, '360° LOOP', age, { y: 980, size: 180, kr: '회피 기동' });
  });
  S(bt(135), 0.5, (ctx, t, age) => {       // cutscene frame
    world(ctx, t, 5000 + t * 100, { sky: 'storm', groundY: 1000 });
    drawApache(ctx, { x: 1100, y: 500, s: 2.2, tilt: 0.02, t });
    cutFrame(ctx, t, E.outX(clamp(age / 0.15)), C.cyan, 'TARGETED', '표적 지정됨', 3.6 + age);
    bigWord(ctx, 'CINEMATIC ENTRANCES', age, { y: 900, size: 120, kr: '보스 등장 컷신' });
  });
  const stamps = [['FLARES', ['#2a0806', '#6a1410'], '플레어'], ['LOCK-ON', ['#041620', '#0c3a52'], '락온'], ['HELLFIRE', ['#241604', '#6a4406'], '헬파이어'], ['LINKED SALVOS', ['#2a0806', '#5a0c0a'], '연계 사격'],
    ['NAV LIGHTS', ['#02040a', '#0c1830'], '항법등'], ['5 PHASES', ['#050505', '#1a1a1a'], '5페이즈'], ['BOSS THEME', ['#041620', '#0c3a52'], '전용 보스 음악'], ['PLAYS WITH CALAMITY', ['#1a0a24', '#3a1450'], '칼라미티 호환 (선택)']];
  stamps.forEach(([w, pal, k], i) => S(bt(136) + i * 0.25, 0.25, (ctx, t, age) => {
    montageBG(ctx, pal);
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(-0.22); stripes(ctx, -W, 330, W * 2, 60, 'rgba(255,255,255,0.06)', t * 400, 4); ctx.restore();
    // a prop per stamp
    if (i === 0) flares(ctx, t, t - age - 0.2, 70 + i, 8, [700, 300], -1, 2);
    if (i === 1) reticle(ctx, W / 2, 560, 300, C.cyan, t, 0.6, 3);
    if (i === 2) drawHellfire(ctx, W / 2 + 400 - age * 1600, 300 + age * 400, Math.atan2(400, -1600), 10, t);
    if (i === 3) for (let j = 0; j < 3; j++) drawSpike(ctx, 500 + j * 450, 200 + age * 900, Math.PI / 2, 4, 4, t, true);
    if (i === 4) drawDrone(ctx, 'ShadowUAV', W / 2, 330, 7, 0.001 + age * 0.2);
    if (i === 5) for (let j = 0; j < 5; j++) rectF(ctx, 620 + j * 140, 300, 110, 30, j <= Math.floor(age * 20) ? C.red : 'rgba(255,255,255,0.15)');
    if (i === 6) for (let j = 0; j < 32; j++) { const hh = 40 + 220 * Math.abs(Math.sin(j * 1.7 + t * 18) * Math.sin(j * 0.3 + t * 7)); rectF(ctx, 330 + j * 40, 420 - hh, 28, hh, C.cyan, 0.8); }
    if (i === 7) drawApache(ctx, { x: W / 2, y: 300, s: 1.6, t, tilt: 0 });
    bigWord(ctx, w, age, { y: 680, size: w.length > 10 ? 180 : 250, kr: k });
  }));
  // converge: silhouettes rush to the centre, whiteout
  S(bt(140), T.END - bt(140), (ctx, t, age) => {
    rectF(ctx, 0, 0, W, H, '#050608');
    const k = E.inC(clamp(age / (T.END - bt(140))));
    for (let i = 0; i < 60; i++) { const an = hr(i) * TAU, r0 = 1400 - k * 1300 - hr(i * 3) * 300; line(ctx, W / 2 + Math.cos(an) * r0, H / 2 + Math.sin(an) * r0, W / 2 + Math.cos(an) * (r0 + 300), H / 2 + Math.sin(an) * (r0 + 300), '#fff', 2, 0.4); }
    const S2 = (dx, dy) => [W / 2 + dx * (1 - k), H / 2 + dy * (1 - k)];
    let p = S2(-800, -300); drawApache(ctx, { x: p[0], y: p[1], s: 2 - k, t, sil: '#ffffff' });
    p = S2(900, -250); drawDrone(ctx, 'GrayEagle', p[0], p[1], 3 - k * 2, t, { sil: '#ffffff' });
    p = S2(800, 350); drawDrone(ctx, 'ShadowUAV', p[0], p[1], 4 - k * 3, t, { sil: '#ffffff' });
    p = S2(-700, 420); drawHumvee(ctx, p[0], p[1], 2.4 - k * 1.8, { sil: '#ffffff' });
    FX.flash = E.inX(clamp(age / (T.END - bt(140))));
  });
}
function sMontage(ctx, t) {
  for (const s of SHOTS) if (t >= s.t0 && t < s.t1) { s.fn(ctx, t, t - s.t0); return; }
}

// ======================================= SCENE 10: END CARD =======================================
function sEnd(ctx, t) {
  const a = T.END;
  world(ctx, t, 30000 + (t - a) * 40, { sky: 'dusk', groundY: 1080 });
  rectF(ctx, 0, 0, W, H, '#050204', 0.45);
  light(ctx, W / 2, 820, 1000, 'rgba(255,90,50,1)', 0.5);
  // the Guardian holding behind the logo, backlit
  const hv = { x: W / 2 + 40, y: 330 + Math.sin(t * 2.1) * 6, s: 2.0, tilt: Math.sin(t * 1.3) * 0.015, t };
  const pz = 1 + 0.05 * ease(a, 60, t, E.outC);
  ctx.save(); ctx.translate(W / 2, 600); ctx.scale(pz, pz); ctx.translate(-W / 2, -600);
  drawApache(ctx, { ...hv, sil: '#0a0608' });
  drawApache(ctx, { ...hv, a: 0.28 });
  const total = titleLogo(ctx, t, a, W / 2, 740, { size: 260 });
  // sheen across the word
  const sh = ease(a + 0.9, a + 1.6, t, E.ioC);
  if (sh > 0 && sh < 1) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const x = lerp(W / 2 - total / 2 - 200, W / 2 + total / 2 + 200, sh);
    const g = ctx.createLinearGradient(x - 120, 0, x + 120, 0); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,255,255,0.5)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.fillRect(x - 160, 500, 320, 260); ctx.restore();
  }
  const tp = ease(a + 0.6, a + 1.4, t, E.lin);
  decode(ctx, 'MODERN MILITARY HARDWARE FOR TERRARIA', W / 2 - 470, 850, tp, { f: 'Chakra', size: 34, w: 600, col: C.white, track: 6 }, 17);
  kr(ctx, '아파치 D · 아파치 가디언 · 그레이 이글 · 섀도 · 험비', W / 2, 900, { align: 'center', size: 26, a: ease(a + 1.2, a + 1.8, t) * 0.85 });
  const bp = ease(a + 1.6, a + 2.2, t);
  txt(ctx, 'tModLoader MOD   •   v0.5.9   •   CALAMITY OPTIONAL', W / 2, 980, { f: 'Mono', size: 20, w: 700, col: C.dim, align: 'center', track: 3, a: bp });
  txt(ctx, 'MUSIC  “LOW ALTITUDE ASSAULT”  ORIGINAL SCORE', W / 2, 1014, { f: 'Mono', size: 16, w: 400, col: C.dim, align: 'center', track: 3, a: bp * 0.8 });
  ctx.restore();
  cutFrame(ctx, t, ease(a + 0.1, a + 0.5, t, E.outX), C.red, 'MODERN ARSENAL', '모던 아스날', t - a);
  FX.flash = Math.max(FX.flash, 0);
  const fo = ease(75.0, 75.9, t, E.inQ);
  if (fo > 0) rectF(ctx, 0, 0, W, H, '#000', fo);
}

// ======================================= timeline =======================================
const SCENES = [
  { a: T.BOOT, b: T.LOCK, draw: sBoot },
  { a: T.LOCK, b: T.TITLE, draw: sLock },
  { a: T.TITLE, b: T.APACHE, draw: sTitle, out: { type: 'slash', dur: 0.5 } },
  { a: T.APACHE, b: T.SPIKE, draw: sApache, out: { type: 'whip', dur: 0.45 } },
  { a: T.SPIKE, b: T.DRONE, draw: sSpike },
  { a: T.DRONE, b: T.HUMVEE, draw: sDrones, out: { type: 'stripes', dur: 0.4, col: C.amber } },
  { a: T.HUMVEE, b: T.BREAK, draw: sHumvee, out: { type: 'slash', dur: 0.3 } },
  { a: T.BREAK, b: T.DPACHE, draw: sBreak },
  { a: T.DPACHE, b: T.MONT, draw: sDpache },
  { a: T.MONT, b: T.END, draw: sMontage },
  { a: T.END, b: DUR + 1, draw: sEnd },
];
let TR = null;
function drawScenes(ctx, t) {
  const i = SCENES.findIndex(s => t >= s.a && t < s.b); if (i < 0) return;
  const sc = SCENES[i], nx = SCENES[i + 1], tr = sc.out;
  if (tr && nx && t >= sc.b - tr.dur) {
    const p = (t - (sc.b - tr.dur)) / tr.dur;
    if (!TR) TR = mk(W, H);
    const tc = ctxOf(TR); tc.setTransform(1, 0, 0, 1, 0, 0); tc.globalAlpha = 1; tc.globalCompositeOperation = 'source-over';
    tc.fillStyle = '#000'; tc.fillRect(0, 0, W, H); sc.draw(tc, t);          // outgoing scene -> buffer
    if (tr.type === 'slash') {
      nx.draw(ctx, t);
      const e = lerp(-500, W + 500, E.ioC(p)), sl = 0.45 * H;
      ctx.save(); ctx.beginPath(); ctx.moveTo(e + sl, 0); ctx.lineTo(W + 600, 0); ctx.lineTo(W + 600, H); ctx.lineTo(e - sl, H); ctx.closePath(); ctx.clip(); ctx.drawImage(TR, 0, 0); ctx.restore();
      line(ctx, e + sl, 0, e - sl, H, '#ffffff', 8, 1); line(ctx, e + sl + 22, 0, e - sl + 22, H, C.red, 4, 0.9);
    } else if (tr.type === 'whip') {
      const off = E.inC(p) * W * 1.2, inn = (1 - E.outC(p)) * W;
      ctx.save(); ctx.translate(inn, 0); nx.draw(ctx, t); ctx.restore();
      ctx.save(); for (let k = 0; k < 4; k++) { ctx.globalAlpha = (k === 0 ? 1 : 0.25) * (1 - p * 0.3); ctx.drawImage(TR, -off - k * 90 * p, 0); } ctx.restore();
      for (let k = 0; k < 30; k++) { const y = hr(k * 3.7) * H; line(ctx, 0, y, W, y, '#fff', 1 + hr(k) * 3, 0.15 * Math.sin(Math.PI * p)); }
    } else if (tr.type === 'stripes') {
      nx.draw(ctx, t);
      const cover = p < 0.5 ? E.outC(p * 2) : 1, reveal = p < 0.5 ? 0 : E.inC((p - 0.5) * 2);
      if (p < 0.5) ctx.drawImage(TR, 0, 0);
      ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(-0.35);
      const bw = W * 2.4, x0 = -bw / 2 + reveal * bw, x1 = -bw / 2 + cover * bw;
      rectF(ctx, x0, -H * 1.2, Math.max(0, x1 - x0), H * 2.4, '#140c02');
      stripes(ctx, x0, -H * 1.2, Math.max(0, x1 - x0), H * 2.4, tr.col, t * 300, 8);
      ctx.restore();
    }
  } else sc.draw(ctx, t);
}

// ======================================= camera impacts & sound cues =======================================
function initScenes() {
  initActors();
  BG.hbox.Gun = HUM.gunPivot; BG.hbox.Turret = BG.hbox.Turret || [120, 24];
  initMontage();
  // lock beeps accelerate into the lock
  for (let x = bt(20); x < bt(31);) { LOCK_BEEPS.push(x); const k = inv(bt(20), bt(31), x); x += lerp(0.5, 0.0625, E.inQ(k)); }
  // --- impacts
  impact(0.09, { flash: 0.25, shake: 4 });
  for (const b of [bt(3), bt(6), bt(10)]) impact(b, { shake: 10, ca: 4, zoom: 0.02 });
  impact(T.LOCK, { flash: 0.55, shake: 26, ca: 9, zoom: 0.05, dec: 5 });
  impact(T.TITLE, { flash: 1, fdec: 3.5, shake: 34, ca: 12, zoom: 0.07, dec: 4 });
  impact(bt(40) + 0.4, { shake: 6 });
  impact(bt(44), { shake: 6, ca: 3 });
  impact(bt(50), { shake: 8, ca: 4, zoom: 0.02 });
  impact(T.SPIKE + 0.35, { shake: 12, flash: 0.2, ca: 4 });
  impact(T.DRONE, { flash: 1, fdec: 4, shake: 34, ca: 12, dec: 3.5 });
  impact(T.DRONE + 0.55, { shake: 16, ca: 5 });
  impact(T.DRONE + 0.7, { shake: 10, ca: 3 });
  impact(bt(66), { shake: 8, ca: 6, zoom: 0.02 });
  impact(bt(77), { shake: 8, ca: 5 });
  impact(bt(79) + 0.02, { flash: 0.7, shake: 30, ca: 10, dec: 4 });
  for (let i = 0; i < 16; i++) impact(T.HUMVEE + i * 0.25, { shake: 3 + (i % 4 === 0 ? 3 : 0), ca: i % 4 === 0 ? 2 : 0 });
  impact(bt(89), { shake: 10, ca: 3 });
  impact(T.BREAK, { shake: 12, ca: 6 }); impact(bt(94), { shake: 8, ca: 4 });
  impact(T.MONT, { shake: 22, ca: 8, flash: 0.35, zoom: 0.05 });
  for (let k = 129; k <= 135; k++) impact(bt(k), { shake: 10, ca: 5, zoom: 0.03 });
  for (let i = 0; i < 8; i++) impact(bt(136) + i * 0.25, { shake: 12, ca: 6, zoom: 0.03, flash: 0.08 });
  impact(T.END, { flash: 1, fdec: 2.2, shake: 30, ca: 12, zoom: 0.06, dec: 3.5 });
  // --- sound cues (mixed under the score by mix.py)
  cue(0.09, 'boot', 0.9);
  for (let i = 0; i < 7; i++) cue(bt(1 + i), 'chirp', 0.5);
  for (const b of [bt(3), bt(6), bt(10)]) cue(b, 'hit', 0.8);
  for (const b of [bt(2), bt(5), bt(9), bt(12)]) cue(b, 'swish', 0.4);
  cue(bt(14), 'riser', 0.5);
  cue(T.LOCK, 'boom', 1);
  for (const b of LOCK_BEEPS) cue(b, 'beep', 0.45);
  for (const b of [bt(28), bt(29), bt(30)]) cue(b, 'tick', 0.8);
  cue(bt(31), 'lock', 0.9); cue(bt(30), 'riser', 0.7);
  cue(T.TITLE, 'boom', 1.1);
  for (let i = 0; i < 7; i++) cue(T.TITLE + i * 0.0625, 'stamp', 0.35);
  for (let i = 0; i < 3; i++) cue(bt(36 + i), 'chirp', 0.5);
  cue(T.APACHE - 0.3, 'whoosh', 0.9); cue(T.APACHE - 0.5, 'rotor', 1);
  cue(bt(44), 'ping', 0.8); cue(bt(45), 'ping', 0.6);
  for (let i = 0; i < 3; i++) cue(bt(45 + i), 'chirp', 0.45);
  cue(bt(47) + 0.05, 'gun30', 0.9); cue(bt(47) + 0.75, 'gun30', 0.9);
  cue(bt(50) + 0.05, 'flares', 0.8); cue(bt(50), 'whoosh', 0.6); cue(bt(54) + 0.3, 'whoosh', 0.9);
  cue(T.SPIKE + 0.02, 'eject', 0.9); cue(T.SPIKE + 0.34, 'missile', 1);
  cue(bt(58), 'hit', 0.6); cue(bt(60), 'swish', 0.6); cue(bt(62), 'riser', 0.6); cue(bt(63), 'static', 0.6);
  cue(T.DRONE, 'explode', 1.2); cue(T.DRONE + 0.48, 'passEagle', 1); cue(T.DRONE + 0.63, 'passShadow', 1);
  cue(bt(66), 'swish', 0.7); for (let i = 0; i < 4; i++) cue(bt(66 + i), 'chirp', 0.4);
  cue(bt(73), 'laser', 0.7);
  for (let x = bt(73) + 0.2, k = 0; x < bt(77); k++) { cue(x, 'beep', 0.35); x += lerp(0.4, 0.09, k / 20); }
  cue(bt(77), 'lock', 0.9); cue(bt(77) + 0.1, 'missile', 0.6); cue(bt(77) + 0.3, 'missile', 0.5);
  cue(bt(79) + 0.02, 'explode', 1.2);
  cue(39.85, 'whoosh', 0.8);
  for (let i = 0; i < 16; i++) cue(T.HUMVEE + i * 0.25, 'clank', 0.55 + (i % 4 === 0 ? 0.25 : 0));
  cue(bt(88), 'crank', 0.9); cue(bt(89), 'engine', 1);
  cue(bt(89) + 0.05, 'm2', 1);
  cue(bt(91) + 0.05, 'drive', 0.8);
  cue(T.BREAK - 0.2, 'whoosh', 0.7);
  for (let k = 0; k < 4; k++) cue(bt(92 + k), 'alarm', 0.5);
  cue(bt(95), 'riser', 0.6);
  cue(T.MONT, 'boom', 0.9);
  for (let k = 129; k <= 135; k++) cue(bt(k), 'hit', 0.6);
  cue(T.MONT + 0.02, 'gun30', 0.6); cue(bt(129), 'missile', 0.5);
  for (let i = 0; i < 8; i++) cue(bt(136) + i * 0.25, 'stamp', 0.7);
  cue(bt(140), 'riser', 0.9);
  cue(T.END, 'boom', 1.2);
  for (let i = 0; i < 7; i++) cue(T.END + i * 0.0625, 'stamp', 0.3);
  cue(T.END + 0.9, 'shimmer', 0.5);
  cue(T.END + 0.1, 'rotor', 0.5);
  dCues();
  CUES.sort((p, q) => p.t - q.t);
  window.CUES = CUES;
}
