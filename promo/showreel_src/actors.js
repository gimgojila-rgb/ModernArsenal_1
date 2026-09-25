// ---------------------------------------------------------------------------------------------
// Actors: the mod's own sprites assembled with the same offsets as the game code, plus
// procedural pixel backgrounds (sky, clouds, hills, dirt) and weapon effects.
// ---------------------------------------------------------------------------------------------

// ---------------- procedural pixel backgrounds ----------------
const BG = {};
function pixCanvas(w, h, fn) {       // fn(i,j) -> [r,g,b,a] | null
  const c = mk(w, h), x = ctxOf(c), im = x.createImageData(w, h);
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
    const v = fn(i, j); if (!v) continue; const o = (j * w + i) * 4;
    im.data[o] = v[0]; im.data[o + 1] = v[1]; im.data[o + 2] = v[2]; im.data[o + 3] = v[3] ?? 255;
  }
  x.putImageData(im, 0, 0); return c;
}
function makeCloud(seed, tone) {
  const w = 72, h = 26, blobs = [];
  const n = 5 + Math.floor(hr(seed) * 4);
  for (let k = 0; k < n; k++) blobs.push([10 + hr(seed + k * 3) * 52, 12 + hr(seed + k * 5) * 6 - (k % 2) * 3, 6 + hr(seed + k * 7) * 8]);
  const inside = (i, j) => blobs.some(([bx, by, r]) => (i - bx) ** 2 + ((j - by) * 1.6) ** 2 < r * r) && j < 21;
  const [hi, mid, lo] = tone;
  return pixCanvas(w, h, (i, j) => {
    if (!inside(i, j)) return null;
    const up = !inside(i, j - 2), dn = !inside(i, j + 2);
    return up ? hi : dn ? lo : mid;
  });
}
function makeHills(seed, w, h, amp, base, cols, freqs) {
  const hgt = i => base + freqs.reduce((a, [f, p, s]) => a + Math.sin(i / w * TAU * f + p + seed) * s, 0) * amp;
  return pixCanvas(w, h, (i, j) => {
    const top = Math.round(hgt(i));
    if (j < top) return null;
    if (cols.length > 2 && j < top + 1) return cols[2];
    return (j - top + i) % 17 === 0 && j > top + 3 ? cols[1] : cols[0];
  });
}
function makeGround(w) {        // Terraria-like dirt strip: grass cap, dirt, darker specks, stone lower down
  const h = 60;
  const top = i => Math.round(6 + Math.sin(i / w * TAU * 3) * 2 + Math.sin(i / w * TAU * 7 + 1) * 1.2);
  return pixCanvas(w, h, (i, j) => {
    const t0 = top(i); if (j < t0) return null;
    const d = j - t0;
    if (d === 0) return [120, 196, 72];
    if (d === 1) return [78, 158, 52];
    if (d === 2 && hr(i * 3.3) > 0.4) return [58, 120, 40];
    const n = hr(i * 12.9898 + j * 78.233);
    if (d > 26 + Math.sin(i * 0.2) * 3) return n > 0.85 ? [70, 72, 80] : n > 0.3 ? [98, 100, 108] : [84, 86, 94];
    return n > 0.9 ? [112, 74, 44] : n > 0.78 ? [136, 90, 54] : n > 0.08 ? [151, 101, 62] : [120, 80, 48];
  });
}
function makePlayer() {           // a small generic adventurer silhouette, 12x22 px
  const P = [
    '....hhhh....', '...hhhhhh...', '..hhssssh...', '..hsssese...', '...ssssss...', '....ssss....', '...cccccc...',
    '..cccccccc..', '..cscccccs..', '..cscccccs..', '..sscccccss.', '...cccccc...', '...bbbbbb...', '...pppppp...',
    '...pp..pp...', '...pp..pp...', '...pp..pp...', '...pp..pp...', '..bbb..bbb..', '..bbb..bbb..'];
  const col = { h: [92, 58, 36], s: [240, 190, 150], e: [30, 30, 40], c: [60, 110, 170], b: [56, 42, 34], p: [70, 80, 100] };
  return pixCanvas(12, P.length, (i, j) => { const ch = P[j][i]; return ch === '.' ? null : col[ch]; });
}
function makeHellfire() {
  const P = ['..f.........', 'nbbbbbbbbbff', 'nbwwwwwwbbbe', 'nbbbbbbbbbff', '..f.........'];
  const col = { n: [40, 44, 50], b: [120, 126, 116], w: [168, 172, 160], f: [70, 74, 70], e: [255, 200, 120] };
  return pixCanvas(12, 5, (i, j) => { const ch = P[j][i]; return ch === '.' ? null : col[ch]; });
}
function initActors() {
  BG.cloudsDay = Array.from({ length: 8 }, (_, k) => makeCloud(11 + k * 17, [[226, 234, 244], [190, 204, 222], [150, 168, 194]]));
  BG.cloudsDusk = Array.from({ length: 8 }, (_, k) => makeCloud(31 + k * 13, [[255, 196, 160], [196, 132, 128], [120, 84, 110]]));
  BG.cloudsNight = Array.from({ length: 8 }, (_, k) => makeCloud(71 + k * 19, [[92, 110, 140], [62, 76, 104], [40, 50, 74]]));
  BG.hillsFar = makeHills(1.3, 480, 90, 1, 40, [[46, 58, 82], [52, 64, 88]], [[2, 0, 14], [5, 1.3, 6], [11, 2.2, 3]]);
  BG.hillsNear = makeHills(4.1, 480, 90, 1, 52, [[30, 40, 58], [34, 46, 64]], [[3, 0.7, 12], [7, 2, 5], [13, 0.4, 2]]);
  BG.hillsFarDusk = makeHills(1.3, 480, 90, 1, 40, [[92, 64, 96], [100, 70, 104]], [[2, 0, 14], [5, 1.3, 6], [11, 2.2, 3]]);
  BG.hillsNearDusk = makeHills(4.1, 480, 90, 1, 52, [[52, 38, 66], [58, 42, 72]], [[3, 0.7, 12], [7, 2, 5], [13, 0.4, 2]]);
  BG.ground = makeGround(480);
  BG.player = makePlayer();
  BG.hellfire = makeHellfire();
  // Humvee layer bounding boxes (for exploded-view motion)
  BG.hbox = {};
  for (const n of HUM_ORDER) {
    const img = IMG['HumveeBoss_' + n] || IMG.HumveeBoss_Wheel;
    if (n.startsWith('Wheel')) { const c = n === 'WheelRear' ? HUM.rear : HUM.front; BG.hbox[n] = [c[0], c[1]]; continue; }
    const c = mk(img.width, img.height), x = c.getContext('2d'); x.drawImage(img, 0, 0);
    const d = x.getImageData(0, 0, c.width, c.height).data;
    let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1;
    for (let j = 0; j < c.height; j++) for (let i = 0; i < c.width; i++) if (d[(j * c.width + i) * 4 + 3] > 0) { x0 = Math.min(x0, i); y0 = Math.min(y0, j); x1 = Math.max(x1, i); y1 = Math.max(y1, j); }
    BG.hbox[n] = [(x0 + x1) / 2, (y0 + y1) / 2];
  }
}

const SKY = {
  dusk: ['#1a1030', '#6a2f55', '#e0725a'],
  day: ['#2c5d9a', '#5f95cf', '#b9d8ef'],
  night: ['#04060c', '#0b1424', '#1a2a44'],
  storm: ['#0c1018', '#1c2433', '#3a4458'],
};
function skyFill(ctx, pal, y0 = 0, y1 = H) {
  const g = ctx.createLinearGradient(0, y0, 0, y1);
  g.addColorStop(0, pal[0]); g.addColorStop(0.6, pal[1]); g.addColorStop(1, pal[2]);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
// tiled parallax strip
function strip(ctx, img, camX, factor, y, sc) {
  const w = img.width * sc; let o = ((-camX * factor) % w + w) % w - w;
  for (let x = o; x < W; x += w) ctx.drawImage(img, Math.round(x), Math.round(y), w, img.height * sc);
}
function clouds(ctx, set, camX, t, factor, y0, y1, n, sc, a = 1, seed = 1) {
  ctx.save(); ctx.globalAlpha *= a;
  const span = W + 900;
  for (let k = 0; k < n; k++) {
    const img = set[k % set.length];
    const bx = hr(seed + k * 3.7) * span, y = lerp(y0, y1, hr(seed + k * 9.1));
    const x = ((bx - camX * factor - t * 12 * factor) % span + span) % span - 450;
    ctx.drawImage(img, Math.round(x), Math.round(y), img.width * sc, img.height * sc);
  }
  ctx.restore();
}
// full world backdrop; camX = world scroll in px
function world(ctx, t, camX, o = {}) {
  const pal = SKY[o.sky || 'dusk'];
  skyFill(ctx, pal);
  if (o.stars) for (let i = 0; i < 140; i++) rectF(ctx, hr(i * 3.1) * W, hr(i * 7.7) * H * 0.7, 2, 2, '#fff', 0.2 + 0.6 * hr(i * 5 + Math.floor(t * 4) * 0.01));
  if (o.sun) light(ctx, o.sun[0], o.sun[1], 700, 'rgba(255,170,110,1)', 0.55);
  const set = o.sky === 'night' ? BG.cloudsNight : o.sky === 'day' ? BG.cloudsDay : BG.cloudsDusk;
  clouds(ctx, set, camX, t, 0.08, 60, 380, 6, 6, 0.55, 3);
  const gy = o.groundY ?? 900;
  const dusk = o.sky !== 'day';
  strip(ctx, dusk ? BG.hillsFarDusk : BG.hillsFar, camX, 0.15, gy - 330, 5);
  clouds(ctx, set, camX, t, 0.25, 180, 520, 5, 8, 0.8, 9);
  strip(ctx, dusk ? BG.hillsNearDusk : BG.hillsNear, camX, 0.35, gy - 260, 5);
  if (o.haze !== false) { const g = ctx.createLinearGradient(0, gy - 200, 0, gy + 40); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, o.hazeCol || 'rgba(255,140,110,0.18)'); ctx.fillStyle = g; ctx.fillRect(0, gy - 200, W, 240); }
  if (o.ground !== false) strip(ctx, BG.ground, camX, 1, gy - 24, 4);
}
// blueprint / HUD grid backdrop
function gridBG(ctx, t, col = 'rgba(80,160,220,0.10)', base = C.navy, cell = 60, ox = 0, oy = 0) {
  rectF(ctx, 0, 0, W, H, base);
  ctx.save(); ctx.strokeStyle = col; ctx.lineWidth = 1; ctx.beginPath();
  const x0 = ((ox % cell) + cell) % cell, y0 = ((oy % cell) + cell) % cell;
  for (let x = x0; x < W; x += cell) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, H); }
  for (let y = y0; y < H; y += cell) { ctx.moveTo(0, y + 0.5); ctx.lineTo(W, y + 0.5); }
  ctx.stroke();
  ctx.fillStyle = col.replace(/[\d.]+\)$/, '0.35)');
  for (let x = x0; x < W; x += cell * 4) for (let y = y0; y < H; y += cell * 4) ctx.fillRect(x - 3, y, 7, 1), ctx.fillRect(x, y - 3, 1, 7);
  ctx.restore();
}

// ---------------- AH-64E Apache Guardian ----------------
const AP = { MAIN: [-45, -24], TAIL: [151, -4], GUN: [-105, 36], RADAR: [-45, -39], BEACON: [-31, -16], WINGL: [-15, 20], TAILL: [171, -17], TUBE: [-88, 34], TADS: [-152, 18], VAPOR: [[-184, -24], [94, -24], [0, 6]] };
const ROTOR_W = 1740 * Math.PI / 180;       // 29 deg per tick at 60 ticks/s
function apW(p, off) { const r = rot(off, p.tilt || 0); return [p.x + r[0] * p.s, p.y + r[1] * p.s]; }
// p: {x,y,s,tilt,t,gun,sil,lights,a,beaconBoost}
function drawApache(ctx, p) {
  const t = p.t, I = n => p.sil ? tint(IMG[n], p.sil) : IMG[n];
  ctx.save(); ctx.globalAlpha *= p.a ?? 1;
  ctx.translate(p.x, p.y); ctx.rotate(p.tilt || 0); ctx.scale(p.s, p.s);
  spr(ctx, I('ApacheEBoss_Gun'), AP.GUN[0], AP.GUN[1], { ox: 33, oy: 7, r: p.gun ?? -0.14 });
  spr(ctx, I('ApacheEBoss'), 0, 0, { ox: 186, oy: 63 });
  spr(ctx, I('ApacheEBoss_Radar'), AP.RADAR[0], AP.RADAR[1]);
  spr(ctx, I('ApacheEBoss_TailRotorBlur'), AP.TAIL[0], AP.TAIL[1], { ox: 33, oy: 33 });
  spr(ctx, I('ApacheEBoss_TailRotor'), AP.TAIL[0], AP.TAIL[1], { ox: 33, oy: 33, r: -t * ROTOR_W * 4.86, a: 0.55 });
  spr(ctx, I('ApacheEBoss_MainRotorBlur'), AP.MAIN[0], AP.MAIN[1]);
  const f = Math.floor(t * ROTOR_W / (Math.PI / 12)) % 6;
  spr(ctx, I('ApacheEBoss_MainRotor'), AP.MAIN[0], AP.MAIN[1], { sy: f * 20, sw: 278, sh: 18, ox: 139, oy: 9, a: 0.7 });
  if (p.lights !== false && !p.sil) {
    const ph = (t % 1.0);
    const bea = (ph < 0.05 || (ph > 0.12 && ph < 0.17)) ? 1 : 0.08;
    glow(ctx, AP.BEACON[0], AP.BEACON[1], 44, C.port, bea * (p.beaconBoost || 1));
    glow(ctx, AP.WINGL[0], AP.WINGL[1], 26, C.port, 0.85);
    glow(ctx, AP.TAILL[0], AP.TAILL[1], 24, '#fffaf0', 0.7);
  }
  ctx.restore();
}
// vapour trails off the rotor tips and wing tip: path(tt) -> {x,y,tilt}
function apacheVapor(ctx, t, path, s, level = 1, n = 26, dt = 1 / 60) {
  ctx.save(); ctx.lineCap = 'round';
  for (const [e, off] of AP.VAPOR.entries()) {
    let prev = null;
    for (let i = 0; i < n; i++) {
      const st = path(t - i * dt); if (!st) break;
      const r = rot(off, st.tilt || 0), P = [st.x + r[0] * s, st.y + r[1] * s + i * 0.35 * s];
      if (prev) line(ctx, prev[0], prev[1], P[0], P[1], '#e6eef8', (e === 2 ? 1.2 : 2) * s * 0.6, level * 0.5 * (1 - i / n) ** 1.4 * (e === 2 ? 0.6 : 1));
      prev = P;
    }
  }
  ctx.restore();
}
function muzzle(ctx, x, y, ang, s, t, seed) {
  const k = 0.7 + 0.3 * hr(seed + Math.floor(t * 60));
  ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.globalCompositeOperation = 'lighter';
  ctx.fillStyle = '#fff2b0';
  ctx.beginPath(); ctx.moveTo(0, -5 * s); ctx.lineTo(-38 * s * k, 0); ctx.lineTo(0, 5 * s); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.moveTo(-6 * s, 0); ctx.lineTo(-14 * s, -14 * s * k); ctx.lineTo(-10 * s, 0); ctx.lineTo(-14 * s, 14 * s * k); ctx.closePath(); ctx.fill();
  ctx.restore();
  glow(ctx, x, y, 90 * s, '#ffc860', 0.9 * k);
}
function tracer(ctx, x0, y0, x1, y1, col, lw, a = 1) {
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
  line(ctx, x0, y0, x1, y1, col, lw * 3, a * 0.25); line(ctx, x0, y0, x1, y1, '#fff8e0', lw, a); ctx.restore();
}

// ---------------- UAVs ----------------
const UAV = { GrayEagle: { fh: 54, gap: 4 }, ShadowUAV: { fh: 13, gap: 2 } };
// draws facing left at (x,y) scale s; o.r rotation, o.sil silhouette colour
function drawDrone(ctx, key, x, y, s, t, o = {}) {
  const L = JSONS[key], u = UAV[key], I = n => o.sil ? tint(IMG[n], o.sil) : IMG[n];
  ctx.save(); ctx.globalAlpha *= o.a ?? 1; ctx.translate(x, y); if (o.r) ctx.rotate(o.r); ctx.scale(s, s);
  const ax = L.prop_axis;
  spr(ctx, I(key + '_PropBlur'), ax[0], ax[1]);
  spr(ctx, I(key), 0, 0);
  if (key === 'GrayEagle') spr(ctx, I('GrayEagle_MarksL'), 0, 0);
  const f = Math.floor(t * 60) % 6;
  spr(ctx, I(key + '_Prop'), ax[0], ax[1], { sy: f * (u.fh + u.gap), sh: u.fh, sw: IMG[key + '_Prop'].width });
  if (!o.sil && o.lights !== false) {
    spr(ctx, tint(IMG[key + '_Slime'], C.lime), 0, 0, { op: 'lighter', a: 0.75 });
    const k = key === 'GrayEagle' ? 1 : 0.6, ph = t % 1;
    glow(ctx, L.near_wingtip[0], L.near_wingtip[1], 26 * k, C.port, 0.95);
    glow(ctx, L.far_wingtip[0], L.far_wingtip[1], 18 * k, C.stbd, 0.55);
    glow(ctx, L.tail_white[0], L.tail_white[1], 16 * k, '#fffaf0', 0.65);
    const pulse = 0.35 + 0.65 * Math.pow(0.5 + 0.5 * Math.sin(t * TAU * 1.2), 3);
    glow(ctx, L.beacon_top[0], L.beacon_top[1], 26 * k, C.port, pulse);
    glow(ctx, L.beacon_bottom[0], L.beacon_bottom[1], 26 * k, C.port, pulse * 0.8);
    if (ph < 0.05) for (const st of L.strobe) glow(ctx, st[0], st[1], 60 * k, '#ffffff', 1);
  }
  ctx.restore();
}
// wingtip vortices / prop wash behind a drone moving along path(tt) -> [x,y]
function droneTrail(ctx, key, t, path, s, n = 34, dt = 1 / 60) {
  const L = JSONS[key];
  for (const [src, wid, a0] of [[L.near_wingtip, 1.3, 0.45], [L.far_wingtip, 1, 0.25], [L.tail_white, 1.8, 0.3]]) {
    let prev = null;
    for (let i = 0; i < n; i++) {
      const p = path(t - i * dt); if (!p) break;
      const P = [p[0] + src[0] * s, p[1] + src[1] * s];
      if (prev) line(ctx, prev[0], prev[1], P[0], P[1], '#dde6f2', wid * s * 0.7, a0 * (1 - i / n) ** 1.5);
      prev = P;
    }
  }
}

// ---------------- Spike NLOS ----------------
// frame 0 = folded in the tube, 1..4 = wings swinging out. nose right.
function drawSpike(ctx, x, y, ang, s, frame, t, motor = true, sil) {
  const img = sil ? tint(IMG.SpikeNLOS_Deploy, sil) : IMG.SpikeNLOS_Deploy;
  const fr = clamp(Math.floor(frame), 0, 4);
  if (motor) {
    const tail = [x + Math.cos(ang) * -19 * s, y + Math.sin(ang) * -19 * s];
    const fl = 0.75 + 0.25 * hr(Math.floor(t * 60) * 3.3);
    ctx.save(); ctx.translate(tail[0], tail[1]); ctx.rotate(ang); ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = '#ffd890'; ctx.beginPath(); ctx.moveTo(0, -3 * s); ctx.lineTo(-26 * s * fl, 0); ctx.lineTo(0, 3 * s); ctx.fill();
    ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.moveTo(0, -1.5 * s); ctx.lineTo(-11 * s * fl, 0); ctx.lineTo(0, 1.5 * s); ctx.fill();
    ctx.restore();
    glow(ctx, tail[0], tail[1], 70 * s, '#ffb050', 0.9);
  }
  spr(ctx, img, x, y, { s, r: ang, sy: fr * 36, sh: 34, sw: 40, ox: 20, oy: 16 });
}
function drawHellfire(ctx, x, y, ang, s, t, motor = true) {
  if (motor) { const tx = x - Math.cos(ang) * 7 * s, ty = y - Math.sin(ang) * 7 * s; glow(ctx, tx, ty, 50 * s, '#ffb050', 0.9); }
  spr(ctx, BG.hellfire, x, y, { s, r: ang + Math.PI, ox: 6, oy: 2.5 });   // sprite drawn nose-left
}

// ---------------- M1151 Humvee ----------------
const HUM = { rear: [177, 95], front: [41, 95], gunPivot: [93.8, 22.4], gunTex: [49, 13], ground: 116, head: [14, 69], marker: [20, 66], tail: [198, 74], muzzleLen: 49, exhaust: [206, 60] };
const HUM_ORDER = ['Frame', 'Engine', 'Cabin', 'Interior', 'WellRear', 'WellFront', 'Spare', 'WheelRear', 'WheelFront', 'Body', 'DoorRear', 'DoorFront', 'Hood', 'Antenna', 'TurretShield', 'Gun', 'Turret'];
// (x,y) = ground contact under the centre; o.part(name) -> {dx,dy,r,a,flash}; o.wheel angle rad; o.gun elev rad
function drawHumvee(ctx, x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.translate(-112, -HUM.ground);
  if (o.bob) ctx.translate(0, o.bob);
  const wf = Math.floor(((o.wheel || 0) / (11.25 * Math.PI / 180)) % 4 + 4) % 4;
  for (const n of HUM_ORDER) {
    const P = o.part ? o.part(n) : null;
    if (P && P.a <= 0.001) continue;
    const c = BG.hbox[n];
    ctx.save();
    if (P) { ctx.globalAlpha *= P.a ?? 1; ctx.translate(c[0] + (P.dx || 0), c[1] + (P.dy || 0)); ctx.rotate(P.r || 0); ctx.translate(-c[0], -c[1]); }
    const draw = (img) => {
      if (n.startsWith('Wheel')) { const wc = n === 'WheelRear' ? HUM.rear : HUM.front; ctx.drawImage(img, 0, wf * 44, 42, 42, wc[0] - 21, wc[1] - 21, 42, 42); }
      else if (n === 'Gun') { ctx.save(); ctx.translate(HUM.gunPivot[0], HUM.gunPivot[1]); ctx.rotate(o.gun || 0); ctx.drawImage(img, -HUM.gunTex[0], -HUM.gunTex[1]); ctx.restore(); }
      else ctx.drawImage(img, 0, 0);
    };
    const key = n.startsWith('Wheel') ? 'HumveeBoss_Wheel' : 'HumveeBoss_' + n;
    draw(o.sil ? tint(IMG[key], o.sil) : IMG[key]);
    if (P && P.flash > 0.01) { ctx.save(); ctx.globalAlpha = P.flash; ctx.globalCompositeOperation = 'lighter'; draw(tint(IMG[key], '#ffe0a0')); ctx.restore(); }
    ctx.restore();
  }
  if (o.lights) {
    const L = o.lights;
    glow(ctx, HUM.head[0], HUM.head[1], 40, '#fff4d0', L);
    glow(ctx, HUM.marker[0], HUM.marker[1], 18, '#ffb020', L * 0.8);
    glow(ctx, HUM.tail[0], HUM.tail[1], 20, '#ff2a1a', L * (o.brake ? 1 : 0.6));
    // beam
    if (L > 0.05) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.22 * L;
      const g = ctx.createLinearGradient(HUM.head[0], 0, HUM.head[0] - 260, 0); g.addColorStop(0, 'rgba(255,240,200,1)'); g.addColorStop(1, 'rgba(255,240,200,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(HUM.head[0], HUM.head[1] - 2); ctx.lineTo(HUM.head[0] - 260, HUM.head[1] - 30); ctx.lineTo(HUM.head[0] - 260, HUM.head[1] + 40); ctx.lineTo(HUM.head[0], HUM.head[1] + 3); ctx.fill(); ctx.restore();
    }
  }
  ctx.restore();
}
function humveeMuzzle(x, y, s, gun) {       // world position of the M2 muzzle
  const tip = rot([-HUM.muzzleLen, 0], gun);
  return [x + (HUM.gunPivot[0] + tip[0] - 112) * s, y + (HUM.gunPivot[1] + tip[1] - HUM.ground) * s];
}

// ---------------- flares ----------------
function flares(ctx, t, t0, seed, n, origin, dir = 1, s = 1) {
  const age0 = t - t0; if (age0 < 0) return;
  for (let i = 0; i < n; i++) {
    const ti = t0 + i * 0.07, age = t - ti; if (age < 0 || age > 2.2) continue;
    const o = typeof origin === 'function' ? origin(ti) : origin;
    const vx = dir * (160 + 220 * hr(seed + i)) * s, vy = (-120 + 260 * hr(seed + i * 3)) * s;
    const path = tt => { const a = tt - ti; if (a < 0) return null; const k = 1.6, f = (1 - Math.exp(-k * a)) / k; return [o[0] + vx * f, o[1] + vy * f + 0.5 * 260 * s * a * a]; };
    smokeTrail(ctx, t, ti, ti + 2.2, 40, path, { life: 1.1, r0: 4 * s, r1: 18 * s, a: 0.5, rise: 10, seed: seed + i });
    const p = path(t), q = 1 - age / 2.2;
    glow(ctx, p[0], p[1], 90 * s * q, '#ffd070', 1);
    glow(ctx, p[0], p[1], 34 * s, '#ffffff', q);
    rectF(ctx, p[0] - 3 * s, p[1] - 3 * s, 6 * s, 6 * s, '#fffbe8', q);
  }
}
