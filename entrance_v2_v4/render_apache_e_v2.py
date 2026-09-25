"""AH-64E Guardian entrance preview, v2 (a different shot list from the D's entrance).

The D dives in from far off and high, and the camera swings over to it. The E ambushes instead: the camera stays low on the
player with the right side empty, rotor wash starts kicking dust at the right edge, and the E bursts in from off screen at
nap-of-the-earth height, nose down, dragging a dust tail. It hauls into a hard flare (nose up, decoy flares) close to the
player, paints the player with the FCR, slews the gun and lases (title), then fires a Spike NLOS that lofts high and dives.
The camera leans after it as it bursts in, chases the Spike, and ends on a wide shot of the smoke arc.

GIF only (no game code yet). Same sprites, offsets, rotor rates, light positions and HUD pieces as the D renderer
(ApacheBoss.Lights.cs, CutsceneDraw.AlertFrame, ApacheWarningSystem). Inputs are read from assets/ next to this file, or from this file's own folder: the E sprites,
CutsceneStripes.png and HumveeChinook_Glow.png (copies of the mod textures). Run: python3 render_apache_e_v2.py [out_dir]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
AS = os.path.join(HERE, 'assets') if os.path.isdir(os.path.join(HERE, 'assets')) else HERE   # handover folder: sprites sit next to this file
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
def L(n): return Image.open(os.path.join(AS, n)).convert('RGBA')
BODY, GUN, RADAR = L('ApacheEBoss.png'), L('ApacheEBoss_Gun.png'), L('ApacheEBoss_Radar.png')
TAIL, TAILB = L('ApacheEBoss_TailRotor.png'), L('ApacheEBoss_TailRotorBlur.png')
MAIN, MAINB = L('ApacheEBoss_MainRotor.png'), L('ApacheEBoss_MainRotorBlur.png')
SPIKE_OPEN, SPIKE_SHUT = L('SpikeNLOS.png'), L('SpikeNLOS_folded.png')
STRIPES = L('CutsceneStripes.png')
GLOW = np.asarray(L('HumveeChinook_Glow.png'))[..., 3].astype(np.float32) / 255

FWID, FHEI = 1000, 720
FD = '/usr/share/fonts/opentype/noto/'
FONT_T = ImageFont.truetype(FD + 'NotoSansCJK-Black.ttc', 44)
FONT_S = ImageFont.truetype(FD + 'NotoSansCJK-Bold.ttc', 20)
FONT_W = ImageFont.truetype(FD + 'NotoSansCJK-Black.ttc', 30)
FONT_WS = ImageFont.truetype(FD + 'NotoSansCJK-Bold.ttc', 18)
FONT_H = ImageFont.truetype(FD + 'NotoSansCJK-Bold.ttc', 17)
FONT_M = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 13)

# ---- constants mirrored from the C# (2x px from the body centre, facing left) ----
MAIN_AXIS, TAIL_HUB, GUN_PIVOT, RADAR_C, TADS = (-45, -24), (151, -4), (-105, 36), (-45, -39), (-152, 18)
GUN_ORIGIN = (33, 7)
BEACON, WINGL, TAILL = (-31, -16), (-15, 20), (171, -17)
TUBE = (-88, 34)
VAPOR_FROM = [(-184, -24), (94, -24), (0, 6)]

def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
def smooth(t): t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)
def smoother(t): t = min(max(t, 0.0), 1.0); return t * t * t * (t * (6 * t - 15) + 10)

# ---- terrain: flat ground, then a ridge in 16 px tiles: a plateau (crest y = -144) and a stone outcrop behind it (-192) ----
CREST, ROCK = -144, -192
def _profile(x):
    return 0.0
def surface(x):
    c = math.floor(x / 16) * 16 + 8
    return round(_profile(c) / 16) * 16
def above(p, pad=1): return p[1] < surface(p[0]) - pad

PLAYER = (0.0, -21.0)
face = -1                                            # faces the player (left): the textures face left, no mirror

# ---- timeline (ticks at 60 per second) ----
ENTER, RUN = 44, 78              # bursts in from off screen right, brakes into a hover
PINGS = (128, 146)               # FCR sweeps
SLEW = 170                       # gun onto the player, TADS lase, title
LAUNCH = 300                     # Spike NLOS
BLEND_IN, FRAME_OUT_A, FRAME_OUT_B = 45, 262, 312
START = (1520.0, -96.0)
HOVER = (452.0, -158.0)

def heli_pos(t):
    if t < ENTER: return START
    u = (t - ENTER) / RUN
    if u < 1:
        x = HOVER[0] + (START[0] - HOVER[0]) * (1 - u) ** 2          # constant hard braking: 27 px/tick in, 0 at the end
        y = START[1] + (HOVER[1] - START[1]) * smooth((u - 0.35) / 0.65) - 10 * math.sin(math.pi * min(u / 0.5, 1))
        return (x, y)
    w = t - ENTER - RUN
    return (HOVER[0] - 6 * (1 - math.exp(-w / 12)), HOVER[1] + math.sin(w * 0.06) * 3 * smooth(w / 20))

class Heli: pass
h = Heli()
h.c = heli_pos(0); h.vel = (0.0, 0.0); h.tilt = 0.0; h.tiltv = 0.0; h.rotor = 0.0; h.tail = 0.0; h.gun = math.pi; h.t = 0
h.vap = [[] for _ in VAPOR_FROM]; h.vlevel = 0.4
def world(off): return add(h.c, rot(off, h.tilt))

parts = []    # [x, y, vx, vy, life, maxlife, size, col, kind, back]
rng = random.Random(11)
st = {'cam': None, 'shake': 0.0, 'banner': None, 'hit_ping': None, 'impact': None, 'wide': None}
ping_hits = []

def puff(x, y, vx, vy, life, size, col, kind, back=False):
    parts.append([x, y, vx, vy, life, life, size, col, kind, back])

def step():
    h.t += 1
    t = h.t
    tgt = heli_pos(t)
    v = sub(tgt, h.c)
    ax = v[0] - h.vel[0]
    tilt_t = max(-0.45, min(0.45, v[0] * 0.03 + ax * 1.6))
    if SLEW <= t: tilt_t += face * 0.08 * smooth((t - SLEW) / 20)
    h.tiltv += 0.22 * 0.22 * (tilt_t - h.tilt) - 2 * 0.8 * 0.22 * h.tiltv
    h.tilt += h.tiltv
    h.vel = v; h.c = tgt
    h.rotor = (h.rotor + math.radians(29)) % (math.pi / 2)
    h.tail = (h.tail + math.radians(29) * 4.86) % (2 * math.pi)
    piv = world(GUN_PIVOT)
    stowed = add(piv, rot((face * 400, 0), h.tilt))
    aim = lerp(stowed, PLAYER, smooth((t - SLEW) / 14))
    a = math.atan2(aim[1] - piv[1], aim[0] - piv[0])
    fwd = math.pi + h.tilt
    rel = (a - fwd + math.pi) % (2 * math.pi) - math.pi
    h.gun = fwd + max(math.radians(-70), min(math.radians(15), rel))
    # vapour trails (ApacheBoss.Lights: faint all the time, VaporFloor 0.4)
    want = max(0.4, min(max((math.hypot(*h.vel) - 8) / 10, 0), 1))
    h.vlevel += (want - h.vlevel) * (0.25 if want > h.vlevel else 0.08)
    for e, off in enumerate(VAPOR_FROM):
        lst = h.vap[e]
        for q in lst: q[1] += 0.35
        lst.insert(0, [*world(off), h.vlevel * (0.6 if e == 2 else 1)])
        del lst[26:]
    if t == SLEW: st['shake'] = 4.0
    # rotor wash on the ground under it: a dragged tail on the run, a ring under the hover
    alt = -(h.c[1] + 60)
    s = max(0.0, 1 - alt / 240)
    if t % 2 == 0 and s > 0.02 and h.c[0] < 1700:
        fast = abs(h.vel[0]) > 6
        for _ in range(6 if fast else 3):
            dx = rng.uniform(-200, 230) if fast else rng.uniform(-220, 220)
            x = h.c[0] + dx
            out = 1 if dx > 0 else -1
            vx = (rng.uniform(1, 4) + h.vel[0] * -0.25 if fast else out * rng.uniform(2, 6)) * s
            puff(x, -3, vx, rng.uniform(-2.4, -0.4) * s, 50, rng.uniform(6, 11) * s, (178, 166, 138), 'smoke')
    if t == ENTER + 16: st['shake'] = 6.0                        # it tears past the camera's edge
    u = t - (ENTER + RUN - 34)
    if 0 <= u < 24 and u % 4 == 0:                             # decoy flares on the flare, kicked up and back
        for side_ in (-1, 1):
            p0 = world((20, 30))
            puff(p0[0], p0[1], rng.uniform(2, 5), rng.uniform(-3.5, -1.5) + side_ * 0.8, 56, 3, (255, 236, 190), 'flare')
    spike_step(t)
    for p in list(parts):
        if p[8] == 'flare':
            p[3] += 0.13
            if t % 2 == 0: puff(p[0], p[1], 0, -0.2, 60, rng.uniform(2.5, 4), (205, 205, 200), 'smoke')
    for p in parts:
        p[0] += p[2]; p[1] += p[3]; p[4] -= 1
        p[2] *= 0.94; p[3] *= 0.94; p[3] -= 0.01
    parts[:] = [p for p in parts if p[4] > 0]

# ---- Spike NLOS: launched from behind the ridge, lofts over it and dives onto the target ----
class Msl: pass
m = Msl(); m.alive = False; m.p = (0, 0); m.v = (0, 0); m.phase = ''; m.age = 0
APEX = (PLAYER[0] + 230, -610)
def spike_step(t):
    if t - LAUNCH == 0:
        m.alive = True; m.p = world(TUBE); m.v = add(rot((-4.5, 0), h.tilt), h.vel); m.phase = 'eject'; m.age = 0
        st['shake'] = 2.5
        for _ in range(16):
            puff(m.p[0], m.p[1], rng.uniform(-3, 1.5), rng.uniform(-1.4, 0.8), 34, rng.uniform(5, 9), (200, 196, 186), 'smoke', True)
    if not m.alive: return
    m.age += 1
    if m.phase == 'eject':
        m.v = (m.v[0] * 0.97, m.v[1] + 0.12)
        if m.age >= 9: m.phase = 'climb'
    else:
        tgt = APEX if m.phase == 'climb' else PLAYER
        spd = min(16, math.hypot(*m.v) + 0.6) if m.phase == 'climb' else min(23, math.hypot(*m.v) + 0.55)
        want = math.atan2(tgt[1] - m.p[1], tgt[0] - m.p[0]); cur = math.atan2(m.v[1], m.v[0])
        d = (want - cur + math.pi) % (2 * math.pi) - math.pi
        turn = 0.085 if m.phase == 'climb' else 0.11
        cur += max(-turn, min(turn, d))
        m.v = (math.cos(cur) * spd, math.sin(cur) * spd)
        if m.phase == 'climb' and (m.p[1] < APEX[1] + 70 or m.age > 80): m.phase = 'dive'
        tail = sub(m.p, (math.cos(cur) * 14, math.sin(cur) * 14))
        puff(tail[0], tail[1], -m.v[0] * 0.05, -m.v[1] * 0.05, 8, rng.uniform(4, 6), (255, 190, 90), 'fire', True)
        for k in range(3):
            q = lerp(tail, sub(tail, m.v), k / 3)
            puff(q[0] + rng.uniform(-1, 1), q[1] + rng.uniform(-1, 1), rng.uniform(-0.15, 0.15), rng.uniform(-0.25, 0), 280, rng.uniform(3.5, 5.5), (196, 194, 188), 'smoke', True)
    m.p = add(m.p, m.v)
    if m.phase == 'dive' and (m.p[1] >= PLAYER[1] + 14 or math.hypot(m.p[0] - PLAYER[0], m.p[1] - PLAYER[1]) < 16):
        m.alive = False; st['impact'] = t; st['shake'] = 12.0
        for _ in range(30):
            a_ = rng.uniform(math.pi, 2 * math.pi); sp = rng.uniform(1, 7.5)
            puff(PLAYER[0], PLAYER[1] + 10, math.cos(a_) * sp, math.sin(a_) * sp, 26, rng.uniform(8, 17), (255, rng.randint(120, 200), 60), 'fire')
        for _ in range(36):
            a_ = rng.uniform(math.pi, 2 * math.pi); sp = rng.uniform(0.5, 4)
            puff(PLAYER[0] + rng.uniform(-24, 24), PLAYER[1] + 6, math.cos(a_) * sp * 1.4, math.sin(a_) * sp, 110, rng.uniform(10, 19), (84, 80, 76), 'smoke')
        for _ in range(28):
            puff(PLAYER[0], PLAYER[1] + 8, rng.uniform(-7, 7), rng.uniform(-9, -2), 30, 2, (255, 230, 150), 'spark')

# ---- drawing helpers ----
VSPR = {}
for n in range(2, 20):
    g = Image.fromarray((GLOW * 255).astype(np.uint8)).resize((n, n), Image.BILINEAR)
    sp = Image.new('RGBA', (n, n), (236, 240, 246, 0)); sp.putalpha(g); VSPR[n] = sp

def grid(cam):
    im = Image.new('RGBA', (FWID, FHEI), (40, 44, 52, 255))
    d = ImageDraw.Draw(im)
    ox = int(-cam[0]) % 16; oy = int(-cam[1]) % 16
    for x in range(ox, FWID, 16): d.line([(x, 0), (x, FHEI)], fill=(47, 52, 61))
    for y in range(oy, FHEI, 16): d.line([(0, y), (FWID, y)], fill=(47, 52, 61))
    return im

def ground(im, cam):
    """grass on top, dirt below; the outcrop above the plateau line is stone"""
    a = np.asarray(im).copy()
    xs = np.arange(FWID) + int(cam[0])
    surf = np.array([surface(x) for x in xs]) - cam[1]
    yy = np.arange(FHEI)[:, None]
    wx = xs[None, :]; depth = yy - surf[None, :]
    wy = yy + int(cam[1])
    noise = ((wx // 4 * 73856093) ^ (wy // 4 * 19349663)) % 7
    dirt = np.stack([95 + noise * 3, 67 + noise * 2, 45 + noise * 2], -1)
    stone = np.stack([104 + noise * 4, 104 + noise * 4, 110 + noise * 4], -1)
    grass = np.stack([62 + noise * 4, 118 + noise * 4, 48 + noise * 2], -1)
    rockzone = np.zeros_like(wx, dtype=bool) & (wy < 0)
    base = np.where(rockzone[..., None], stone, dirt)
    col = np.where((depth < 6)[..., None], grass, base)
    col = np.where(((depth >= 6) & (depth < 8))[..., None], np.where(rockzone[..., None], np.array([78, 78, 86]), np.array([70, 52, 36])), col)
    m_ = depth >= 0
    a[..., :3][m_] = col[m_]
    a[..., 3][m_] = 255
    return Image.fromarray(a.astype(np.uint8), 'RGBA')

def _clip(im, r, x, y):
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(r.width, FWID - x), min(r.height, FHEI - y)
    if x1 <= x0 or y1 <= y0: return
    im.alpha_composite(r.crop((x0, y0, x1, y1)), (x + x0, y + y0))

def paste_rot(im, spr, origin, pos, ang):
    if abs(ang) < 1e-4:
        _clip(im, spr, int(round(pos[0] - origin[0])), int(round(pos[1] - origin[1]))); return
    w, hh = spr.size
    r = spr.rotate(-math.degrees(ang), resample=Image.NEAREST, expand=True)
    off = rot((origin[0] - w / 2, origin[1] - hh / 2), ang)
    _clip(im, r, int(round(pos[0] - (r.width / 2 + off[0]))), int(round(pos[1] - (r.height / 2 + off[1]))))

def draw_apache(im, S):
    c = S(h.c)
    Sw = lambda off: S(world(off))
    paste_rot(im, GUN, GUN_ORIGIN, Sw(GUN_PIVOT), h.gun - math.pi)
    paste_rot(im, BODY, (186, 63), c, h.tilt)
    paste_rot(im, RADAR, (RADAR.width / 2, RADAR.height / 2), Sw(RADAR_C), h.tilt)
    paste_rot(im, TAILB, (33, 33), Sw(TAIL_HUB), h.tilt)
    tr = TAIL.copy(); tr.putalpha(tr.getchannel('A').point(lambda v: int(v * 0.55)))
    paste_rot(im, tr, (33, 33), Sw(TAIL_HUB), h.tilt - h.tail)
    paste_rot(im, MAINB, (MAINB.width / 2, MAINB.height / 2), Sw(MAIN_AXIS), h.tilt)
    f = int(h.rotor / math.radians(15)) % 6
    mr = MAIN.crop((0, f * 20, MAIN.width, f * 20 + 18)); mr.putalpha(mr.getchannel('A').point(lambda v: int(v * 0.7)))
    paste_rot(im, mr, (MAIN.width / 2, 9), Sw(MAIN_AXIS), h.tilt)

def disc(im, x, y, r, col, a):
    if r < 0.5 or a <= 0.01: return
    ov = Image.new('RGBA', (int(2 * r) + 2, int(2 * r) + 2), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse([0, 0, 2 * r, 2 * r], fill=col + (int(255 * min(a, 1)),))
    _clip(im, ov, int(x - r), int(y - r))

def draw_parts(im, S, back):
    for p in parts:
        if p[9] != back: continue
        x, y = S((p[0], p[1])); u = p[4] / p[5]
        if x < -40 or x > FWID + 40 or y < -40 or y > FHEI + 40: continue
        if p[8] == 'smoke':
            disc(im, x, y, p[6] * (1.6 - 0.6 * u), p[7], 0.55 * min(1, u * 1.6))
        elif p[8] == 'fire':
            disc(im, x, y, p[6] * (0.4 + 0.6 * u), p[7], min(1, 1.3 * u))
        elif p[8] == 'flare':
            ImageDraw.Draw(im).rectangle([x - 2, y - 2, x + 1, y + 1], fill=p[7])
        else:
            ImageDraw.Draw(im).rectangle([x - 1, y - 1, x + 1, y], fill=p[7])

def draw_spike(im, S):
    if m.alive:
        ang = math.atan2(m.v[1], m.v[0])
        sp = SPIKE_OPEN if m.age > 5 else SPIKE_SHUT
        paste_rot(im, sp, (sp.width / 2, sp.height / 2), S(m.p), ang)

# ---- HUD (CutsceneDraw.AlertFrame and ApacheWarningSystem, air style, laid out for this frame size) ----
RED = (255, 48, 32); DEEP = (50, 4, 4)
def tint(c, k): return tuple(int(v * k) for v in c)
def mixw(c, k): return tuple(int(v + (255 - v) * k) for v in c)
def btext(d, xy, s, font, fill, anchor='la', w=1):
    for dx in range(-w, w + 1):
        for dy in range(-w, w + 1):
            if dx or dy: d.text((xy[0] + dx, xy[1] + dy), s, font=font, fill=(0, 0, 0, fill[3]), anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

def alert_frame(im, amount, tick, line):
    strip = 14
    bar = int(FHEI * 0.08 * amount)
    if bar < strip + 4: return
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(0, bar - strip, 3):
        sh = min(3, bar - strip - y)
        k = 0.88 + (0.45 - 0.88) * y / (bar - strip)
        d.rectangle([0, y, FWID, y + sh - 1], fill=DEEP + (int(255 * k),))
        d.rectangle([0, FHEI - y - sh, FWID, FHEI - y - 1], fill=DEEP + (int(255 * k),))
    top, bot = bar - strip, FHEI - bar
    sa = np.asarray(STRIPES).astype(np.float32)
    for y0, scroll in ((top, tick // 2), (bot, -tick // 2)):
        d.rectangle([0, y0, FWID, y0 + strip - 1], fill=(0, 0, 0, 153))
        im.alpha_composite(ov); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        row = Image.new('RGBA', (FWID + 64, strip), (0, 0, 0, 0))
        tile = sa.copy(); tile[..., :3] = tile[..., :3] * np.array(RED, np.float32) / 255; tile[..., 3] *= amount
        tile = Image.fromarray(tile.clip(0, 255).astype(np.uint8), 'RGBA')
        for x in range(0, FWID + 64, 32): row.alpha_composite(tile, (x, 0))
        off = scroll % 32
        im.alpha_composite(row.crop((off, 0, off + FWID, strip)), (0, y0))
        lite = mixw(RED, 0.3)
        d.line([(0, y0 - 2), (FWID, y0 - 2)], fill=(0, 0, 0, int(204 * amount)))
        d.line([(0, y0 - 1), (FWID, y0 - 1)], fill=lite + (int(255 * amount),))
        d.line([(0, y0 + strip), (FWID, y0 + strip)], fill=lite + (int(255 * amount),))
        d.line([(0, y0 + strip + 1), (FWID, y0 + strip + 1)], fill=(0, 0, 0, int(204 * amount)))
    # label plate
    head = 'WARNING'
    hw = d.textlength(head, font=FONT_H); lw = d.textlength(line, font=FONT_H)
    plateH = bar - strip - 3
    plateW = int(24 + 22 + 10 + hw + 20 + lw + 22)
    for y in range(plateH):
        slant = int((plateH - y) * 0.6)
        d.line([(0, y), (plateW + slant, y)], fill=DEEP + (int(230 * amount),))
    d.rectangle([0, 0, 3, plateH], fill=RED + (int(255 * amount),))
    cy = plateH / 2 + 1
    on = tick > 56 or (tick // 7) % 2 == 0
    hc = (mixw(RED, 0.35) if on else tint(RED, 0.55)) + (int(255 * amount),)
    tx, ty = 24, cy - 9
    d.polygon([(tx + 11, ty), (tx + 22, ty + 18), (tx, ty + 18)], fill=hc)
    d.rectangle([tx + 10, ty + 6, tx + 11, ty + 11], fill=DEEP + (int(255 * amount),))
    d.rectangle([tx + 10, ty + 14, tx + 11, ty + 15], fill=DEEP + (int(255 * amount),))
    btext(d, (24 + 22 + 10, cy), head, FONT_H, hc, 'lm')
    x = 24 + 22 + 10 + hw + 10
    d.rectangle([x, cy - 9, x + 1, cy + 9], fill=RED + (int(178 * amount),))
    btext(d, (x + 10, cy), line, FONT_H, (255, 255, 255, int(235 * amount)), 'lm')
    clock = f'T+{tick // 3600:02d}:{tick // 60 % 60:02d}.{tick % 60 // 6}'
    cw = d.textlength(clock, font=FONT_M)
    btext(d, (FWID - 28 - cw, cy), clock, FONT_M, (255, 255, 255, int(190 * amount)), 'lm')
    if (tick // 20) % 2 == 0:
        d.rectangle([FWID - 28 - cw - 16, cy - 4, FWID - 28 - cw - 9, cy + 3], fill=RED + (int(255 * amount),))
    im.alpha_composite(ov)

def banner(im, t, line):
    """the centred WARNING banner (ApacheWarningSystem), from the moment the FCR paints the player"""
    if st['banner'] is None: return
    DUR = 110
    age = t - st['banner']; timer = DUR - age
    if age < 0 or timer <= 0: return
    alpha = timer / 20 if timer < 20 else min(1.0, age / 4)
    blink = age > 56 or (age // 7) % 2 == 0
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    cx, cy = FWID / 2, FHEI * 0.2
    x0, y0, x1, y1 = cx - 250, cy - 36, cx + 250, cy + 36
    A_ = lambda k: int(255 * k * alpha)
    d.rectangle([x0, y0, x1, y1], fill=(70, 6, 6, A_(0.6)))
    d.rectangle([x0, y0, x1, y0 + 3], fill=RED + (A_(1),))
    d.rectangle([x0, y1 - 3, x1, y1], fill=RED + (A_(1),))
    for i in range(4):
        d.rectangle([x0 + 8 + i * 12, y0 + 12, x0 + 13 + i * 12, y1 - 12], fill=RED + (A_(0.8),))
        d.rectangle([x1 - 14 - i * 12, y0 + 12, x1 - 9 - i * 12, y1 - 12], fill=RED + (A_(0.8),))
    hc = (mixw(RED, 0.35) if blink else tint(RED, 0.55)) + (A_(1),)
    btext(d, (cx, cy - 10), 'WARNING', FONT_W, hc, 'mm', 2)
    btext(d, (cx, cy + 20), line, FONT_WS, (255, 255, 255, A_(1)), 'mm')
    im.alpha_composite(ov)

def title(im, k):
    """title card, lower-left third this time: an accent spine, the name sliding in, the loadout line under a rule"""
    if k <= 0.01: return
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    a = int(255 * k)
    x0, y0 = 58, FHEI * 0.66
    slide = (1 - k) * 40
    name = 'AH-64E 아파치 가디언'
    nw = d.textlength(name, font=FONT_T)
    d.rectangle([x0, y0 - 30, x0 + 4, y0 + 58], fill=RED + (a,))
    btext(d, (x0 + 20 - slide, y0), name, FONT_T, (255, 255, 255, a), 'lm', 2)
    d.rectangle([x0 + 20, y0 + 28, x0 + 20 + (nw + 30) * k, y0 + 30], fill=RED + (a,))
    btext(d, (x0 + 20 + slide * 0.5, y0 + 46), '롱보우 · 스파이크 NLOS', FONT_S, RED + (a,), 'lm')
    im.alpha_composite(ov)

def bracket(d, x, y, r, a, label):
    col = (255, 60, 40, a)
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.line([(x + sx * r, y + sy * r), (x + sx * (r - 9), y + sy * r)], fill=col, width=2)
            d.line([(x + sx * r, y + sy * r), (x + sx * r, y + sy * (r - 9))], fill=col, width=2)
    if label:
        d.text((x + r + 6, y - r), label, font=FONT_WS, fill=(255, 90, 60, a))

def hud_track(im, S, t):
    """FCR track on the player once the sweep paints it, then the Spike seeker bracket while the missile is out"""
    d = ImageDraw.Draw(im)
    x, y = S((PLAYER[0], PLAYER[1] - 2))
    if st['hit_ping'] is not None and st['hit_ping'] <= t < SLEW + 30:
        age = t - st['hit_ping']
        k = smooth(age / 10)
        r = 40 - 12 * k
        flash = any(0 <= t - h_ < 6 for h_ in ping_hits)
        a = int(255 * k) if flash or (t // 5) % 2 else int(150 * k)
        bracket(d, x, y, r, a, 'FCR')
    s_ = t - LAUNCH
    if -20 <= s_ and st['impact'] is None:
        k = smooth((s_ + 20) / 12)
        r = 34 - 14 * k
        a = int(255 * k) if (t // 4) % 2 or s_ > 0 else int(140 * k)
        bracket(d, x, y, r, a, 'SPIKE NLOS')

def hitbox(im, S):
    x, y = S(PLAYER)
    d = ImageDraw.Draw(im)
    d.rectangle([x - 10, y - 21, x + 10, y + 21], outline=(225, 230, 240, 200))

# ---- camera: a shot list instead of one follow ----
def shot_focus(t):
    if t < LAUNCH + 8:
        lean = max(0.0, min(260.0, (h.c[0] - HOVER[0]) * 0.32)) if ENTER + 8 <= t else 0.0
        return (318 + lean, -232 - 10 * smooth((t - ENTER - RUN) / 60))
    return None

def camera(t):
    f = shot_focus(t)
    if f is None:
        if st['impact'] is None:        # chase the Spike with a lead, never dropping the ground out of frame
            if m.alive:
                lead = add(m.p, (m.v[0] * 9, m.v[1] * 9))
                f = (lead[0], min(lead[1], -210))
            else:
                f = st['cam']
        else:
            u = t - st['impact']
            hold = st.setdefault('hold', st['cam'])
            f = lerp(hold, (300, -330), smoother((u - 24) / 64))
        k = 0.16
    else:
        k = 0.2
    last = st['cam'] or f
    st['cam'] = lerp(last, f, k)
    return st['cam']

def draw(t):
    cf = camera(t)
    pf = (PLAYER[0], PLAYER[1] - 60)
    blend = smooth(t / BLEND_IN)
    cf = lerp(pf, cf, blend)
    sh = st['shake']; st['shake'] *= 0.82
    cam = (cf[0] - FWID / 2 + rng.uniform(-sh, sh), cf[1] - FHEI / 2 + rng.uniform(-sh * 0.45, sh * 0.45))
    S = lambda p: (p[0] - cam[0], p[1] - cam[1])

    im = grid(cam)
    # behind the ridge: vapour, the helicopter, the Spike and its trail (the ground covers what is below the crest)
    vap_layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    for lst in h.vap:
        for i in range(len(lst) - 1, 0, -1):
            s_ = lst[i][2]
            if s_ < 0.02: continue
            u = i / 26
            spread = min(max(math.hypot(lst[i][0] - lst[i - 1][0], lst[i][1] - lst[i - 1][1]) / 6, 0.2), 1)
            a = 0.4 * s_ * (1 - u) * spread
            spr = VSPR[max(2, int(4 + 14 * u))]
            for k in range(3):
                q = lerp(lst[i][:2], lst[i - 1][:2], k / 3)
                x, y = S(q)
                sp = spr.copy(); sp.putalpha(sp.getchannel('A').point(lambda v, a=a: int(v * a)))
                _clip(vap_layer, sp, int(x - sp.width / 2), int(y - sp.height / 2))
    im.alpha_composite(vap_layer)
    draw_apache(im, S)
    draw_parts(im, S, True)
    draw_spike(im, S)
    im = ground(im, cam)
    draw_parts(im, S, False)
    hitbox(im, S)

    # additive: FCR sweeps, lights, TADS lase, motor glow (anything under the ground stays hidden)
    arr = np.asarray(im).astype(np.float32)
    def add_mask(mask, pos_w, color, k):
        if not above(pos_w, -2): return
        pos = S(pos_w)
        x0, y0 = int(pos[0] - mask.shape[1] / 2), int(pos[1] - mask.shape[0] / 2)
        xs, ys = max(0, x0), max(0, y0); xe, ye = min(FWID, x0 + mask.shape[1]), min(FHEI, y0 + mask.shape[0])
        if xe > xs and ye > ys:
            arr[ys:ye, xs:xe, :3] += mask[ys - y0:ye - y0, xs - x0:xe - x0, None] * np.array(color, np.float32) * k
    def scaled(mask, s):
        n = max(2, int(mask.shape[0] * s))
        return np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((n, n), Image.BILINEAR)).astype(np.float32) / 255
    def plot(pw, color, k, th=2, tw=1):
        if not above(pw): return
        x, y = S(pw); x = int(x); y = int(y)
        if 0 <= x < FWID - tw and 0 <= y < FHEI - th:
            arr[y:y + th, x:x + tw, :3] += np.array(color, np.float32) * k

    dome = world(RADAR_C)
    to_p = math.atan2(PLAYER[1] - dome[1], PLAYER[0] - dome[0])
    dist_p = math.hypot(PLAYER[0] - dome[0], PLAYER[1] - dome[1])
    for p0 in PINGS:
        r = (t - p0) * 21
        if r <= 0 or r > 1000: continue
        if r >= dist_p and p0 not in [x for x, _ in ping_hits_src]:
            ping_hits_src.append((p0, t)); ping_hits.append(t)
            if st['hit_ping'] is None: st['hit_ping'] = t
            if st['banner'] is None: st['banner'] = t
        fade = 1 - (r / 1050) ** 2
        span = 0.62
        n = int(r * span * 2 / 1.1) + 2
        for i in range(n):
            ang = to_p - span + 2 * span * i / (n - 1)
            edge = 1 - abs(ang - to_p) / span
            k = fade * (0.35 + 0.65 * edge) * 0.9
            for dr, kk in ((0, 1.0), (-2, 0.8), (-6, 0.35), (-12, 0.18), (-20, 0.08)):
                plot((dome[0] + math.cos(ang) * (r + dr), dome[1] + math.sin(ang) * (r + dr)), (255, 70, 50), k * kk, 2, 2)
    # radar dome sparkle while it paints
    for p0 in PINGS:
        if 0 <= t - p0 < 8:
            add_mask(scaled(GLOW, 0.7), dome, (255, 80, 60), 0.9 * (1 - (t - p0) / 8))
            add_mask(scaled(GLOW, 0.18), dome, (255, 255, 255), 0.8 * (1 - (t - p0) / 8))

    Sw = world
    if (t % 60) < 40:
        add_mask(scaled(GLOW, 30 / 64), Sw(WINGL), (255, 50, 40), 0.85); add_mask(scaled(GLOW, 8 / 64), Sw(WINGL), (255, 255, 255), 0.6)
    else:
        add_mask(scaled(GLOW, 24 / 64), Sw(TAILL), (255, 250, 235), 0.7)
    bt = t % 66
    if bt < 5 or 12 <= bt < 17:
        add_mask(scaled(GLOW, 46 / 64), Sw(BEACON), (255, 40, 30), 0.95); add_mask(scaled(GLOW, 9 / 64), Sw(BEACON), (255, 255, 255), 0.7)
        stk = np.asarray(Image.fromarray((GLOW * 255).astype(np.uint8)).resize((160, 10), Image.BILINEAR)).astype(np.float32) / 255
        add_mask(stk, Sw(BEACON), (255, 70, 50), 0.5)
    if SLEW <= t < SLEW + 40:
        fade = smooth((t - SLEW) / 4) * (1 - smooth((t - SLEW - 28) / 12))
        fl = 0.75 + 0.25 * math.sin(t * 1.9)
        lens = Sw(TADS)
        n = int(math.hypot(PLAYER[0] - lens[0], PLAYER[1] - lens[1]))
        for i in range(n):
            plot(lerp(lens, PLAYER, i / n), (255, 40, 30), 0.6 * fade * fl)
        add_mask(scaled(GLOW, 0.35), lens, (255, 50, 40), 0.9 * fade)
        add_mask(scaled(GLOW, 0.3), PLAYER, (255, 50, 40), 0.7 * fade * fl)
    for p in parts:
        if p[8] == 'flare':
            add_mask(scaled(GLOW, 0.45), (p[0], p[1]), (255, 200, 120), 0.8)
            add_mask(scaled(GLOW, 0.12), (p[0], p[1]), (255, 255, 255), 0.8)
    s_ = t - LAUNCH
    if 0 <= s_ < 6:
        add_mask(scaled(GLOW, 0.8), world(TUBE), (255, 220, 170), 0.8 * (1 - s_ / 6))
    if m.alive and m.phase != 'eject':
        ang = math.atan2(m.v[1], m.v[0])
        tail = sub(m.p, (math.cos(ang) * 14, math.sin(ang) * 14))
        add_mask(scaled(GLOW, 0.55), tail, (255, 170, 80), 0.9)
        add_mask(scaled(GLOW, 0.2), tail, (255, 255, 230), 0.8)
    if st['impact'] is not None:
        u = t - st['impact']
        if 0 <= u < 16:
            add_mask(scaled(GLOW, 4.2), (PLAYER[0], PLAYER[1] - 4), (255, 190, 110), 1.25 * (1 - u / 16))
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')

    hud_track(im, S, t)
    banner(im, t, '위치 발각됨')
    amount = smooth(t / BLEND_IN) * (1 - smooth((t - FRAME_OUT_A) / (FRAME_OUT_B - FRAME_OUT_A)))
    alert_frame(im, amount, t, '위치 발각됨')
    k = smooth((t - SLEW - 4) / 16) * (1 - smooth((t - (FRAME_OUT_A - 6)) / 26)) if t >= SLEW else 0
    title(im, k)
    return im.convert('RGB')

ping_hits_src = []
STEP = 3
END = LAUNCH + 230
frames, keys = [], {}
marks = {'empty': 30, 'burst': ENTER + 20, 'run': ENTER + 34, 'flare': ENTER + RUN - 16, 'ping': PINGS[0] + 12,
         'lase': SLEW + 16, 'title': SLEW + 60, 'launch': LAUNCH + 12, 'loft': LAUNCH + 40, 'apex': LAUNCH + 62, 'dive': LAUNCH + 80}
for tick in range(1, END):
    step()
    if tick % STEP == 0:
        frames.append(draw(tick))
        for name, at in marks.items():
            if abs(tick - at) < 2 and name not in keys: keys[name] = len(frames) - 1
        if st['impact'] and 'boom' not in keys and tick >= st['impact'] + 3: keys['boom'] = len(frames) - 1
keys['end'] = len(frames) - 1
print('frames', len(frames), 'impact tick', st['impact'], keys)
picks = [frames[i] for i in sorted(set(keys.values()))]
mont = Image.new('RGB', (FWID, FHEI * len(picks)))
for j, f in enumerate(picks): mont.paste(f, (0, FHEI * j))
pal = mont.quantize(colors=255, method=Image.MEDIANCUT)
q = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
q[0].save(os.path.join(OUT, 'apache_e_entrance_v2.gif'), save_all=True, append_images=q[1:], duration=int(1000 * STEP / 60), loop=0, optimize=True, disposal=1)
for k_, i in keys.items(): frames[i].save(os.path.join(OUT, f'ape2_{k_}.png'))
