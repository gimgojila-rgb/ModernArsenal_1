"""AH-64E Guardian entrance preview, v5 (final pass over v4).

Shot list:
  1. A slow pan off the player finds the Guardian far out on the right, gliding in nose down. It settles about 1500 px out
     and its FCR paints the player: the Guardian's own warning (cyan data-link colours, a cut-corner plate, chevrons
     closing in, a diamond lock glyph, TARGETED).
  2. Spike NLOS from stand-off range. The launch plays in slow motion at a 2x punch-in: the back-blast cloud out of the
     rear of the canister, the missile clearing the tube, the wings swinging out (SpikeNLOS_Deploy.png), ignition.
     The camera rides with the missile through the loft, then cuts to the seeker feed for the terminal dive (the missile
     and its own trail are not in its own picture), and whites out on impact.
  3. The hit from the side: fireball, dirt thrown out and falling back, a smoke column, a scorch left on the ground.
     Whip pan back to the Guardian. The MQ-1C (over the rotor) and the RQ-7B (under the skids) sweep past from right to
     left with their props, nav lights and wingtip vortices; the camera leans after the Gray Eagle. Title card.

Smoke is puffs on their own clocks (fade in fast, grow, thin as (1-u)^2), so a trail thins from the launcher end first.
GIF only. Same sprites, offsets, rotor rates and light positions as the game code (ApacheGuardian*, GrayEagleUAV*,
ShadowUAV*, NavLightRig). Inputs are read from assets/ next to this file, or from this file's own folder.
Run: python3 render_apache_e_v5.py [out_dir]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
AS = os.path.join(HERE, 'assets') if os.path.isdir(os.path.join(HERE, 'assets')) else HERE
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
def L(n): return Image.open(os.path.join(AS, n)).convert('RGBA')
BODY, GUN, RADAR = L('ApacheEBoss.png'), L('ApacheEBoss_Gun.png'), L('ApacheEBoss_Radar.png')
TAIL, TAILB = L('ApacheEBoss_TailRotor.png'), L('ApacheEBoss_TailRotorBlur.png')
MAIN, MAINB = L('ApacheEBoss_MainRotor.png'), L('ApacheEBoss_MainRotorBlur.png')
_SD = L('SpikeNLOS_Deploy.png')                      # spike_sprite.py: 5 frames, 40x34, 2 px gap, nose right
SPIKE_FR = [_SD.crop((0, i * 36, 40, i * 36 + 34)) for i in range(5)]
SPIKE_ORIGIN = (20, 16)
def spike_frame(age): return SPIKE_FR[0 if age < 3 else min(4, 1 + (age - 3) // 2)]   # folded in the tube, out over 6 ticks
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
FONT_MB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 15)

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
def mul(a, k): return (a[0] * k, a[1] * k)
def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
def smooth(t): t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)
def smoother(t): t = min(max(t, 0.0), 1.0); return t * t * t * (t * (6 * t - 15) + 10)
def surface(x): return 0.0
def above(p, pad=1): return p[1] < surface(p[0]) - pad

PLAYER = (0.0, -21.0)
face = -1

# ---- timeline (ticks at 60 per second) ----
GLIDE = 200                      # slow glide in from far out
START, STAND = (2780.0, -340.0), (1500.0, -300.0)
DESIG = 128                      # FCR paints the player: TARGETED
LAUNCH = 214                     # Spike NLOS from stand-off
PUNCH_A, PUNCH_B = LAUNCH - 3, LAUNCH + 16   # slow-motion 2x punch-in on the launch
# after the impact (tick set at run time): hold on the explosion, whip pan back, UAV pass, title
HOLD, PAN, UAV_DUR, TITLE_DUR = 40, 30, 96, 96

def heli_pos(t):
    if t < GLIDE:
        u = t / GLIDE
        x = STAND[0] + (START[0] - STAND[0]) * (1 - u) ** 2
        y = START[1] + (STAND[1] - START[1]) * smooth(u)
        return (x, y)
    w = t - GLIDE
    return (STAND[0] - 5 * (1 - math.exp(-w / 14)), STAND[1] + math.sin(w * 0.055) * 3 * smooth(w / 24))

class Heli: pass
h = Heli()
h.c = heli_pos(0); h.vel = (-12.8, 0.0); h.tilt = -0.3; h.tiltv = 0.0; h.rotor = 0.0; h.tail = 0.0; h.gun = math.pi; h.t = 0
h.vap = [[] for _ in VAPOR_FROM]; h.vlevel = 0.6
def world(off): return add(h.c, rot(off, h.tilt))

parts = []    # [x, y, vx, vy, life, maxlife, size, col, kind]
rng = random.Random(23)
st = {'cam': None, 'shake': 0.0, 'banner': None, 'impact': None, 'seeker': None, 'uav0': None}

def puff(x, y, vx, vy, life, size, col, kind):
    parts.append([x, y, vx, vy, life, life, size, col, kind])

def cloud(x, y, vx, vy, life, s0, s1, alpha, col, kind='cloud'):
    """one smoke puff left in the world on its own clock (SmokeTrails.cs): fades in fast, grows, thins as (1-u)^2"""
    parts.append([x, y, vx, vy, life, life, (s0, s1, alpha), col, 'cloud'])

def launch_blast(at):
    """WeaponFx.LaunchBlast: the cloud thrown out of the rear of the canister (the tube faces left, so back is +x)"""
    for _ in range(18):
        a_ = rng.uniform(-0.55, 0.45); sp = rng.uniform(1.5, 7.5)
        cloud(at[0] + 16, at[1] + rng.uniform(-4, 4), math.cos(a_) * sp, math.sin(a_) * sp * 0.8 - 0.3, rng.randint(80, 150),
              rng.uniform(8, 12), rng.uniform(34, 58), 0.55, (214, 210, 202))
    for _ in range(6):
        cloud(at[0] - 6, at[1] + rng.uniform(-3, 5), rng.uniform(-2, 0.5), rng.uniform(0.2, 1.4), rng.randint(50, 90),
              rng.uniform(6, 9), rng.uniform(18, 28), 0.4, (206, 202, 196))
    for _ in range(12):
        puff(at[0] + 12, at[1], rng.uniform(2, 9), rng.uniform(-2.5, 2), 14, 2, (255, 214, 140), 'spark')

# ---- UAV placeholders (boxes until the sprites exist). Sizes follow the Apache's scale (about 19 px per metre) ----
import json
class Uav: pass
UAVS = []
for name, key, dy, spd, delay, fh, gap in (('MQ-1C', 'GrayEagle', -110, 19.0, 0, 54, 4), ('RQ-7B', 'ShadowUAV', 95, 16.0, 12, 13, 2)):
    u = Uav(); u.name = name; u.dy = dy; u.spd = spd; u.delay = delay; u.p = None; u.trail = []; u.k = 0
    u.body = L(key + '.png')
    if os.path.exists(os.path.join(AS, key + '_MarksL.png')): u.body.alpha_composite(L(key + '_MarksL.png'))   # facing left
    u.slime = np.asarray(L(key + '_Slime.png'))[..., 3].astype(np.float32) / 255
    pr = L(key + '_Prop.png'); u.prop = [pr.crop((0, f * (fh + gap), pr.width, f * (fh + gap) + fh)) for f in range(6)]
    u.blur = L(key + '_PropBlur.png')
    u.L = json.load(open(os.path.join(AS, key + '_lights.json')))
    u.size = u.body.size
    UAVS.append(u)


def step():
    h.t += 1
    t = h.t
    tgt = heli_pos(t)
    v = sub(tgt, h.c)
    ax = v[0] - h.vel[0]
    tilt_t = max(-0.45, min(0.45, v[0] * 0.03 + ax * 1.6))
    h.tiltv += 0.22 * 0.22 * (tilt_t - h.tilt) - 2 * 0.8 * 0.22 * h.tiltv
    h.tilt += h.tiltv
    h.vel = v; h.c = tgt
    h.rotor = (h.rotor + math.radians(29)) % (math.pi / 2)
    h.tail = (h.tail + math.radians(29) * 4.86) % (2 * math.pi)
    piv = world(GUN_PIVOT)
    h.gun = math.pi + h.tilt + math.radians(-8)
    want = max(0.4, min(max((math.hypot(*h.vel) - 8) / 10, 0), 1))
    h.vlevel += (want - h.vlevel) * (0.25 if want > h.vlevel else 0.08)
    for e, off in enumerate(VAPOR_FROM):
        lst = h.vap[e]
        for q in lst: q[1] += 0.35
        lst.insert(0, [*world(off), h.vlevel * (0.6 if e == 2 else 1)])
        del lst[26:]
    if t == DESIG: st['banner'] = t
    spike_step(t)
    # UAVs: start once the camera is back on the Guardian
    if st['uav0'] is not None:
        for u in UAVS:
            k = t - st['uav0'] - u.delay
            if k >= 0 and u.p is None:
                u.p = (h.c[0] + 720, h.c[1] + u.dy)
            if u.p is not None:
                u.p = (u.p[0] - u.spd, u.p[1] + math.sin(k * 0.05) * 0.4); u.k = k
                u.trail.insert(0, u.p); del u.trail[40:]
                if abs(u.p[0] - h.c[0]) < u.spd / 2 + 0.5: st['shake'] = max(st['shake'], 5.0 if u.size[0] > 100 else 3.5)
    for p in parts:
        p[0] += p[2]; p[1] += p[3]; p[4] -= 1
        if p[8] in ('cloud', 'trail'): p[2] = p[2] * 0.95 + 0.004; p[3] = p[3] * 0.95 - 0.012
        elif p[8] == 'clod':                                           # dirt thrown out of the crater: falls, bounces once, stops
            p[3] += 0.32; p[2] *= 0.995
            if p[1] > -1 and p[3] > 0:
                p[1] = -1; p[3] = -p[3] * 0.25; p[2] *= 0.45
        else: p[2] *= 0.94; p[3] *= 0.94; p[3] -= 0.01
    parts[:] = [p for p in parts if p[4] > 0]

# ---- Spike NLOS ----
class Msl: pass
m = Msl(); m.alive = False; m.p = (0, 0); m.v = (0, 0); m.phase = ''; m.age = 0
APEX = (760.0, -820.0)
def spike_step(t):
    if t - LAUNCH == 0:
        m.alive = True; m.p = world(TUBE); m.v = add(rot((-4.5, 0), h.tilt), h.vel); m.phase = 'eject'; m.age = 0
        st['shake'] = 3.0
        st['punch_at'] = add(m.p, (-44, 4))
        launch_blast(m.p)
    if not m.alive: return
    m.age += 1
    if m.phase == 'eject':
        m.v = (m.v[0] * 0.97, m.v[1] + 0.12)
        if m.age >= 10: m.phase = 'climb'
    else:
        tgt = APEX if m.phase == 'climb' else PLAYER
        spd = min(17, math.hypot(*m.v) + 0.55) if m.phase == 'climb' else min(25, math.hypot(*m.v) + 0.5)
        want = math.atan2(tgt[1] - m.p[1], tgt[0] - m.p[0]); cur = math.atan2(m.v[1], m.v[0])
        d = (want - cur + math.pi) % (2 * math.pi) - math.pi
        turn = 0.06 if m.phase == 'climb' else 0.09
        cur += max(-turn, min(turn, d))
        m.v = (math.cos(cur) * spd, math.sin(cur) * spd)
        if m.phase == 'climb' and (m.p[1] < APEX[1] + 90 or m.p[0] < APEX[0]): m.phase = 'dive'
        tail = sub(m.p, (math.cos(cur) * 19, math.sin(cur) * 19))
        puff(tail[0], tail[1], -m.v[0] * 0.05, -m.v[1] * 0.05, 5, rng.uniform(3.5, 5), (255, 190, 90), 'motor')
        for k in range(3):
            q = lerp(tail, sub(tail, m.v), k / 3)
            cloud(q[0] + rng.uniform(-1, 1), q[1] + rng.uniform(-1, 1), rng.uniform(-0.2, 0.2) - m.v[0] * 0.02, rng.uniform(-0.3, 0.05) - m.v[1] * 0.02,
                  rng.randint(130, 260), rng.uniform(3.5, 5), rng.uniform(13, 22), 0.5, (200, 198, 192), 'trail')
    m.p = add(m.p, m.v)
    if m.phase == 'dive' and st['seeker'] is None and math.hypot(m.p[0] - PLAYER[0], m.p[1] - PLAYER[1]) < 700:
        st['seeker'] = t
    if m.phase == 'dive' and (m.p[1] >= PLAYER[1] + 14 or math.hypot(m.p[0] - PLAYER[0], m.p[1] - PLAYER[1]) < 16):
        m.alive = False; st['impact'] = t; st['shake'] = 13.0
        for _ in range(34):
            a_ = rng.uniform(math.pi, 2 * math.pi); sp = rng.uniform(1, 8)
            puff(PLAYER[0], PLAYER[1] + 10, math.cos(a_) * sp, math.sin(a_) * sp, 28, rng.uniform(9, 18), (255, rng.randint(120, 200), 60), 'fire')
        for _ in range(40):
            a_ = rng.uniform(math.pi, 2 * math.pi); sp = rng.uniform(0.5, 4.2)
            puff(PLAYER[0] + rng.uniform(-26, 26), PLAYER[1] + 6, math.cos(a_) * sp * 1.4, math.sin(a_) * sp, 120, rng.uniform(10, 20), (84, 80, 76), 'smoke')
        for _ in range(30):
            puff(PLAYER[0], PLAYER[1] + 8, rng.uniform(-7.5, 7.5), rng.uniform(-9.5, -2), 32, 2, (255, 230, 150), 'spark')
        for _ in range(34):                                            # dirt clods
            a_ = rng.uniform(-math.pi * 0.92, -math.pi * 0.08); sp = rng.uniform(3, 10.5)
            puff(PLAYER[0] + rng.uniform(-10, 10), -4, math.cos(a_) * sp, math.sin(a_) * sp, rng.randint(80, 120), rng.choice((4, 4, 6)),
                 rng.choice(((95, 67, 45), (80, 56, 38), (62, 118, 48), (70, 52, 36))), 'clod')
        for i in range(16):                                            # the smoke column, on its own clocks
            cloud(PLAYER[0] + rng.uniform(-18, 18), PLAYER[1] - 8 - i * 3, rng.uniform(-0.6, 0.6), rng.uniform(-2.6, -0.8), rng.randint(140, 220),
                  rng.uniform(14, 22), rng.uniform(48, 80), 0.6, (70, 66, 62))
        st['scorch'] = True

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
    a = np.asarray(im).copy()
    xs = np.arange(FWID) + int(cam[0])
    yy = np.arange(FHEI)[:, None]
    wx = xs[None, :]; depth = yy - (0 - cam[1])
    wy = yy + int(cam[1])
    noise = ((wx // 4 * 73856093) ^ (wy // 4 * 19349663)) % 7
    dirt = np.stack([95 + noise * 3, 67 + noise * 2, 45 + noise * 2], -1)
    grass = np.stack([62 + noise * 4, 118 + noise * 4, 48 + noise * 2], -1)
    depth = np.broadcast_to(depth, (FHEI, FWID))
    col = np.where((depth < 6)[..., None], grass, dirt)
    col = np.where(((depth >= 6) & (depth < 8))[..., None], np.array([70, 52, 36]), col)
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
    if c[0] < -400 or c[0] > FWID + 400 or c[1] < -300 or c[1] > FHEI + 300: return
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

def draw_parts(im, S, seeker=False):
    for p in parts:
        if seeker and p[8] in ('trail', 'motor'): continue
        x, y = S((p[0], p[1])); u = p[4] / p[5]
        if x < -60 or x > FWID + 60 or y < -60 or y > FHEI + 60: continue
        if p[8] in ('cloud', 'trail'):
            s0, s1, a0 = p[6]; age = 1 - u
            size = s0 + (s1 - s0) * (1 - (1 - age) ** 2)
            disc(im, x, y, size / 2, p[7], a0 * min(1, age * 8) * (1 - age) ** 2)
        elif p[8] == 'clod':
            k = int(p[6]); xi, yi = int(x) // 2 * 2, int(y) // 2 * 2
            ImageDraw.Draw(im).rectangle([xi, yi, xi + k - 1, yi + k - 1], fill=p[7])
        elif p[8] == 'motor':
            disc(im, x, y, p[6] * (0.4 + 0.6 * u), p[7], min(1, 1.3 * u))
        elif p[8] == 'smoke':
            disc(im, x, y, p[6] * (1.6 - 0.6 * u), p[7], 0.55 * min(1, u * 1.6))
        elif p[8] == 'fire':
            disc(im, x, y, p[6] * (0.4 + 0.6 * u), p[7], min(1, 1.3 * u))
        else:
            ImageDraw.Draw(im).rectangle([x - 1, y - 1, x + 1, y], fill=p[7])

def draw_spike(im, S):
    if m.alive:
        ang = math.atan2(m.v[1], m.v[0])
        paste_rot(im, spike_frame(m.age), SPIKE_ORIGIN, S(m.p), ang)

PORT, STBD, LIME, WHITE, BEAC, TAILW = (255, 46, 34), (60, 255, 110), (196, 255, 140), (255, 255, 250), (255, 34, 22), (255, 250, 236)
def draw_uavs(im, S, t):
    """the real sprites, facing left (flying right to left): prop blur and frame at the pusher, body with its left-side
    decals, then NavLightRig: port red on the near wingtip, starboard green dimmer on the far one, formation (slime)
    lights, white tail light, pulsing red beacons, 3-tick white strobes every 60 ticks"""
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for u in UAVS:
        if u.p is None: continue
        nw = u.L['near_wingtip']; tw = u.L['tail_white']
        for src, wid, a0 in ((nw, 1, 60), (u.L['far_wingtip'], 1, 34), (tw, 2, 36)):   # wingtip vortices and prop wash, faint
            for i in range(1, len(u.trail)):
                a = int(a0 * (1 - i / len(u.trail)) ** 1.5)
                x0, y0 = S(add(u.trail[i - 1], src)); x1, y1 = S(add(u.trail[i], src))
                d.line([(x0, y0), (x1, y1)], fill=(222, 230, 242, a), width=wid)
    im.alpha_composite(ov)
    for u in UAVS:
        if u.p is None: continue
        c = S(u.p); W_, H_ = u.size
        bx, by = int(round(c[0] - W_ / 2)), int(round(c[1] - H_ / 2))
        if bx > FWID + 40 or bx + W_ < -40: continue
        ax = add(c, u.L['prop_axis'])
        _clip(im, u.blur, int(round(ax[0] - u.blur.width / 2)), int(round(ax[1] - u.blur.height / 2)))
        _clip(im, u.body, bx, by)
        fr = u.prop[t % 6]
        _clip(im, fr, int(round(ax[0] - fr.width / 2)), int(round(ax[1] - fr.height / 2)))
    arr = np.asarray(im).astype(np.float32)
    def blob(p, size, col, k):
        n = max(3, int(size))
        mk = np.asarray(Image.fromarray((GLOW * 255).astype(np.uint8)).resize((n, n), Image.BILINEAR)).astype(np.float32) / 255
        x0, y0 = int(p[0] - n / 2), int(p[1] - n / 2)
        xs, ys = max(0, x0), max(0, y0); xe, ye = min(FWID, x0 + n), min(FHEI, y0 + n)
        if xe > xs and ye > ys:
            arr[ys:ye, xs:xe, :3] += mk[ys - y0:ye - y0, xs - x0:xe - x0, None] * np.array(col, np.float32) * k
    for u in UAVS:
        if u.p is None: continue
        c = S(u.p); W_, H_ = u.size
        bx, by = int(round(c[0] - W_ / 2)), int(round(c[1] - H_ / 2))
        if bx > FWID + 40 or bx + W_ < -40: continue
        sc = 1.0 if u.size[0] > 120 else 0.6                         # NavLightRig.Size
        P = lambda off: add(c, off)
        x0, y0 = max(0, bx), max(0, by); x1, y1 = min(FWID, bx + W_), min(FHEI, by + H_)
        if x1 > x0 and y1 > y0:
            arr[y0:y1, x0:x1, :3] += u.slime[y0 - by:y1 - by, x0 - bx:x1 - bx, None] * np.array(LIME, np.float32) * 0.75
        blob(P(u.L['near_wingtip']), 26 * sc, PORT, 1.0); blob(P(u.L['near_wingtip']), 6, (255, 255, 255), 0.6)
        blob(P(u.L['far_wingtip']), 16 * sc, STBD, 0.6)
        blob(P(tw), 16 * sc, TAILW, 0.65)
        for i, off in enumerate((u.L['beacon_top'], u.L['beacon_bottom'])):
            ph = ((t + i * 36) % 72) / 72; pulse = max(0, math.sin(ph * 2 * math.pi)) ** 2
            blob(P(off), 30 * sc, BEAC, 0.15 + 0.85 * pulse)
        ph = (t + (0 if sc == 1 else 23)) % 60
        if ph < 3:
            for off in u.L['strobe']:
                blob(P(off), 64 * sc, WHITE, 0.95 * (1, 0.7, 0.35)[ph])
    im.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA'))

# ---- HUD. The Guardian gets its own warning style: cyan data-link colours, TARGETED ----
ACC = (60, 205, 255); DEEP = (3, 20, 36)            # the Guardian's cyan data-link colours (as in v4)
TITLE_ACC = ACC
def tint(c, k): return tuple(int(v * k) for v in c)
def mixw(c, k): return tuple(int(v + (255 - v) * k) for v in c)
def btext(d, xy, s, font, fill, anchor='la', w=1):
    for dx in range(-w, w + 1):
        for dy in range(-w, w + 1):
            if dx or dy: d.text((xy[0] + dx, xy[1] + dy), s, font=font, fill=(0, 0, 0, fill[3]), anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

HEAD, LINE = 'TARGETED', '표적 지정됨'

def link_glyph(d, x, cy, col):
    """a small diamond lock glyph with a dot, instead of the red warning triangle"""
    d.polygon([(x + 11, cy - 10), (x + 21, cy), (x + 11, cy + 10), (x + 1, cy)], outline=col, width=2)
    d.rectangle([x + 9, cy - 2, x + 13, cy + 2], fill=col)

def alert_frame(im, amount, tick):
    strip = 14
    bar = int(FHEI * 0.08 * amount)
    if bar < strip + 4: return
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(0, bar - strip, 3):
        sh = min(3, bar - strip - y)
        k = 0.88 + (0.45 - 0.88) * y / (bar - strip)
        d.rectangle([0, y, FWID, y + sh - 1], fill=DEEP + (int(255 * k),))
        d.rectangle([0, FHEI - y - sh, FWID, FHEI - y - 1], fill=DEEP + (int(255 * k),))
    im.alpha_composite(ov); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    top, bot = bar - strip, FHEI - bar
    sa = np.asarray(STRIPES).astype(np.float32)
    tile = sa.copy(); tile[..., :3] = tile[..., :3] * np.array(ACC, np.float32) / 255; tile[..., 3] *= amount
    tile = Image.fromarray(tile.clip(0, 255).astype(np.uint8), 'RGBA')
    row = Image.new('RGBA', (FWID + 64, strip), (0, 0, 0, 0))
    for x in range(0, FWID + 64, 32): row.alpha_composite(tile, (x, 0))
    for y0, scroll in ((top, tick // 2), (bot, -tick // 2)):
        base = Image.new('RGBA', (FWID, strip), (0, 0, 0, 153)); im.alpha_composite(base, (0, y0))
        off = scroll % 32
        im.alpha_composite(row.crop((off, 0, off + FWID, strip)), (0, y0))
        lite = mixw(ACC, 0.3)
        d.line([(0, y0 - 2), (FWID, y0 - 2)], fill=(0, 0, 0, int(204 * amount)))
        d.line([(0, y0 - 1), (FWID, y0 - 1)], fill=lite + (int(255 * amount),))
        d.line([(0, y0 + strip), (FWID, y0 + strip)], fill=lite + (int(255 * amount),))
        d.line([(0, y0 + strip + 1), (FWID, y0 + strip + 1)], fill=(0, 0, 0, int(204 * amount)))
    hw = d.textlength(HEAD, font=FONT_H); lw = d.textlength(LINE, font=FONT_H)
    plateH = bar - strip - 3
    plateW = int(24 + 22 + 10 + hw + 20 + lw + 22)
    for y in range(plateH):
        slant = int((plateH - y) * 0.6)
        d.line([(0, y), (plateW + slant, y)], fill=DEEP + (int(230 * amount),))
    d.rectangle([0, 0, 3, plateH], fill=ACC + (int(255 * amount),))
    cy = plateH / 2 + 1
    on = st['banner'] is None or tick - st['banner'] > 56 or ((tick - st['banner']) // 7) % 2 == 0
    hc = (mixw(ACC, 0.35) if on else tint(ACC, 0.55)) + (int(255 * amount),)
    link_glyph(d, 24, cy, hc)
    btext(d, (24 + 22 + 10, cy), HEAD, FONT_H, hc, 'lm')
    x = 24 + 22 + 10 + hw + 10
    d.rectangle([x, cy - 9, x + 1, cy + 9], fill=ACC + (int(178 * amount),))
    btext(d, (x + 10, cy), LINE, FONT_H, (255, 255, 255, int(235 * amount)), 'lm')
    clock = f'T+{tick // 3600:02d}:{tick // 60 % 60:02d}.{tick % 60 // 6}'
    cw = d.textlength(clock, font=FONT_M)
    btext(d, (FWID - 28 - cw, cy), clock, FONT_M, (255, 255, 255, int(190 * amount)), 'lm')
    if (tick // 20) % 2 == 0:
        d.rectangle([FWID - 28 - cw - 16, cy - 4, FWID - 28 - cw - 9, cy + 3], fill=ACC + (int(255 * amount),))
    im.alpha_composite(ov)

def banner(im, t):
    """the Guardian's banner: a cut-corner plate, chevrons closing in from both ends, a scan bar sweeping across"""
    if st['banner'] is None: return
    DUR = 120
    age = t - st['banner']; timer = DUR - age
    if age < 0 or timer <= 0: return
    alpha = timer / 20 if timer < 20 else min(1.0, age / 4)
    open_ = smoother(age / 8)
    blink = age > 56 or (age // 7) % 2 == 0
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    cx, cy = FWID / 2, FHEI * 0.2
    hw_, hh_ = 250 * open_, 36
    A_ = lambda k: int(255 * k * alpha)
    c = 12
    poly = [(cx - hw_ + c, cy - hh_), (cx + hw_ - c, cy - hh_), (cx + hw_, cy - hh_ + c), (cx + hw_, cy + hh_ - c),
            (cx + hw_ - c, cy + hh_), (cx - hw_ + c, cy + hh_), (cx - hw_, cy + hh_ - c), (cx - hw_, cy - hh_ + c)]
    d.polygon(poly, fill=DEEP + (A_(0.72),))
    d.line(poly + [poly[0]], fill=ACC + (A_(1),), width=2)
    d.line([(cx - hw_ + 18, cy - hh_ + 5), (cx + hw_ - 18, cy - hh_ + 5)], fill=ACC + (A_(0.45),), width=1)
    d.line([(cx - hw_ + 18, cy + hh_ - 5), (cx + hw_ - 18, cy + hh_ - 5)], fill=ACC + (A_(0.45),), width=1)
    if open_ > 0.9:
        # chevrons marching inward
        for i in range(3):
            ph = ((age * 0.5 + i * 8) % 24) / 24
            k = 0.35 + 0.65 * (1 - abs(ph - 0.5) * 2)
            for sgn in (-1, 1):
                x = cx + sgn * (hw_ - 30 - i * 16)
                pts = [(x + sgn * 6, cy - 14), (x - sgn * 4, cy), (x + sgn * 6, cy + 14)]
                d.line(pts, fill=ACC + (A_(k),), width=4)
        # scan bar
        sx = cx - hw_ + ((age * 14) % (2 * hw_))
        d.rectangle([sx, cy - hh_ + 8, sx + 1, cy + hh_ - 8], fill=ACC + (A_(0.35),))
        hc = (mixw(ACC, 0.45) if blink else tint(ACC, 0.6)) + (A_(1),)
        btext(d, (cx, cy - 10), HEAD, FONT_W, hc, 'mm', 2)
        btext(d, (cx, cy + 20), LINE, FONT_WS, (255, 255, 255, A_(1)), 'mm')
    im.alpha_composite(ov)

def title(im, k):
    if k <= 0.01: return
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    a = int(255 * k)
    x0, y0 = 58, FHEI * 0.66
    slide = (1 - k) * 40
    name = 'AH-64E 아파치 가디언'
    nw = d.textlength(name, font=FONT_T)
    d.rectangle([x0, y0 - 30, x0 + 4, y0 + 58], fill=TITLE_ACC + (a,))
    btext(d, (x0 + 20 - slide, y0), name, FONT_T, (255, 255, 255, a), 'lm', 2)
    d.rectangle([x0 + 20, y0 + 28, x0 + 20 + (nw + 30) * k, y0 + 30], fill=TITLE_ACC + (a,))
    btext(d, (x0 + 20 + slide * 0.5, y0 + 46), '롱보우 · 스파이크 NLOS · 유무인 복합', FONT_S, mixw(ACC, 0.2) + (a,), 'lm')   # Cutscene.GuardianSubtitle
    im.alpha_composite(ov)

def hitbox(im, S):
    x, y = S(PLAYER)
    ImageDraw.Draw(im).rectangle([x - 10, y - 21, x + 10, y + 21], outline=(225, 230, 240, 200))

# ---- the world pass (everything but the frame HUD) ----
def render_world(cam, t, lights=True, seeker=False):
    S = lambda p: (p[0] - cam[0], p[1] - cam[1])
    im = grid(cam)
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
                if -30 < x < FWID + 30 and -30 < y < FHEI + 30:
                    sp = spr.copy(); sp.putalpha(sp.getchannel('A').point(lambda v, a=a: int(v * a)))
                    _clip(vap_layer, sp, int(x - sp.width / 2), int(y - sp.height / 2))
    im.alpha_composite(vap_layer)
    draw_apache(im, S)
    if not seeker: draw_spike(im, S)
    im = ground(im, cam)
    if st.get('scorch'):                                               # scorch on the ground where it hit
        x, y = S((PLAYER[0], 0))
        d = ImageDraw.Draw(im)
        for w_, a_ in ((64, 110), (44, 150), (26, 190)):
            d.rectangle([int(x - w_) // 2 * 2, int(y), int(x + w_) // 2 * 2, int(y) + 3], fill=(30, 24, 20, a_))
    draw_parts(im, S, seeker)
    hitbox(im, S)
    if not lights: return im, S
    arr = np.asarray(im).astype(np.float32)
    def add_mask(mask, pos_w, color, k):
        pos = S(pos_w)
        x0, y0 = int(pos[0] - mask.shape[1] / 2), int(pos[1] - mask.shape[0] / 2)
        xs, ys = max(0, x0), max(0, y0); xe, ye = min(FWID, x0 + mask.shape[1]), min(FHEI, y0 + mask.shape[0])
        if xe > xs and ye > ys:
            arr[ys:ye, xs:xe, :3] += mask[ys - y0:ye - y0, xs - x0:xe - x0, None] * np.array(color, np.float32) * k
    def scaled(mask, s):
        n = max(2, int(mask.shape[0] * s))
        return np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((n, n), Image.BILINEAR)).astype(np.float32) / 255
    if (t % 60) < 40:
        add_mask(scaled(GLOW, 30 / 64), world(WINGL), (255, 50, 40), 0.85); add_mask(scaled(GLOW, 8 / 64), world(WINGL), (255, 255, 255), 0.6)
    else:
        add_mask(scaled(GLOW, 24 / 64), world(TAILL), (255, 250, 235), 0.7)
    bt = t % 66
    if bt < 5 or 12 <= bt < 17:
        add_mask(scaled(GLOW, 46 / 64), world(BEACON), (255, 40, 30), 0.95); add_mask(scaled(GLOW, 9 / 64), world(BEACON), (255, 255, 255), 0.7)
        stk = np.asarray(Image.fromarray((GLOW * 255).astype(np.uint8)).resize((160, 10), Image.BILINEAR)).astype(np.float32) / 255
        add_mask(stk, world(BEACON), (255, 70, 50), 0.5)
    # FCR / data-link pulse off the dome when it designates
    for d0 in (DESIG - 8, DESIG, DESIG + 8):
        if 0 <= t - d0 < 8:
            add_mask(scaled(GLOW, 0.8), world(RADAR_C), ACC, 0.9 * (1 - (t - d0) / 8))
            add_mask(scaled(GLOW, 0.2), world(RADAR_C), (255, 255, 255), 0.8 * (1 - (t - d0) / 8))
    for d0 in (DESIG - 8, DESIG, DESIG + 8):
        r = (t - d0) * 26
        if 0 < r < 900:
            dome = world(RADAR_C)
            fade = 1 - (r / 900) ** 2
            for i in range(90):
                ang = math.pi - 0.55 + 1.1 * i / 89
                for dr, kk in ((0, 1.0), (-3, 0.5), (-8, 0.2)):
                    x, y = S((dome[0] + math.cos(ang) * (r + dr), dome[1] + math.sin(ang) * (r + dr)))
                    x = int(x); y = int(y)
                    if 0 <= x < FWID - 2 and 0 <= y < FHEI - 2:
                        arr[y:y + 2, x:x + 2, :3] += np.array(ACC, np.float32) * 0.8 * fade * kk
    s_ = t - LAUNCH
    if 0 <= s_ < 6:
        add_mask(scaled(GLOW, 0.9), world(TUBE), (255, 220, 170), 0.9 * (1 - s_ / 6))
    if m.alive and m.phase != 'eject' and not seeker:
        ang = math.atan2(m.v[1], m.v[0])
        tail = sub(m.p, (math.cos(ang) * 19, math.sin(ang) * 19))
        add_mask(scaled(GLOW, 0.6), tail, (255, 170, 80), 0.95)
        add_mask(scaled(GLOW, 0.22), tail, (255, 255, 230), 0.85)
    if st['impact'] is not None:
        u = t - st['impact']
        if 0 <= u < 18:
            add_mask(scaled(GLOW, 4.4), (PLAYER[0], PLAYER[1] - 4), (255, 190, 110), 1.3 * (1 - u / 18))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA'), S

# ---- the Spike's seeker feed (terminal dive) ----
def seeker_frame(t):
    rng_px = math.hypot(m.p[0] - PLAYER[0], m.p[1] - PLAYER[1])
    z = 2 if rng_px > 720 else (3 if rng_px > 430 else (4 if rng_px > 210 else 6))   # stepped FOV
    aim = (PLAYER[0] + rng.uniform(-1.5, 1.5), PLAYER[1] - 6 + rng.uniform(-1.5, 1.5))
    cam = (aim[0] - FWID / 2, aim[1] - FHEI / 2)
    im, S = render_world(cam, t, lights=True, seeker=True)
    cw, chh = FWID // z, FHEI // z
    x0, y0 = FWID // 2 - cw // 2, FHEI // 2 - chh // 2
    crop = im.crop((x0, y0, x0 + cw, y0 + chh)).resize((cw * z, chh * z), Image.NEAREST).crop((0, 0, FWID, FHEI))
    roll = 0.05 * math.sin(t * 0.33) + 0.03 * math.sin(t * 0.9)               # the airframe rolling under the seeker
    crop = crop.rotate(math.degrees(roll), resample=Image.NEAREST, fillcolor=(24, 26, 30, 255))
    g = np.asarray(crop.convert('L')).astype(np.float32)
    g = np.clip((g - 30) * 1.35, 0, 255)
    g += np.random.default_rng(t).normal(0, 9, g.shape)
    g[::3] *= 0.82
    yy, xx = np.mgrid[0:FHEI, 0:FWID]
    vig = 1 - 0.45 * (((xx - FWID / 2) / (FWID / 2)) ** 2 + ((yy - FHEI / 2) / (FHEI / 2)) ** 2)
    g = np.clip(g * vig, 0, 255)
    rgb = np.stack([g * 0.86, g * 1.0, g * 0.9], -1)
    out = Image.fromarray(rgb.clip(0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    d = ImageDraw.Draw(out)
    W = (225, 240, 230, 255)
    cx, cy = FWID / 2, FHEI / 2
    for sgn in (-1, 1):
        d.line([(cx + sgn * 26, cy), (cx + sgn * 150, cy)], fill=W, width=2)
        d.line([(cx, cy + sgn * 26), (cx, cy + sgn * 110)], fill=W, width=2)
    # track gate on the target, sized by the zoom
    px_, py_ = cx + (PLAYER[0] - aim[0]) * z, cy + (PLAYER[1] - aim[1]) * z
    gw, gh = 14 * z, 26 * z
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.line([(px_ + sx * gw, py_ + sy * gh), (px_ + sx * (gw - 12), py_ + sy * gh)], fill=W, width=2)
            d.line([(px_ + sx * gw, py_ + sy * gh), (px_ + sx * gw, py_ + sy * (gh - 12))], fill=W, width=2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x_, y_ = cx + sx * 440, cy + sy * 280
            d.line([(x_, y_), (x_ - sx * 40, y_)], fill=W, width=3)
            d.line([(x_, y_), (x_, y_ - sy * 40)], fill=W, width=3)
    fov = {2: 'WFOV', 3: 'MFOV', 4: 'NFOV', 6: 'NFOV x2'}[z]
    spd = math.hypot(*m.v)
    tti = rng_px / max(spd, 1) / 60
    d.text((70, 60), f'SPIKE NLOS   EO   {fov}', font=FONT_MB, fill=W)
    d.text((70, 82), 'DL  AH-64E  LINK OK', font=FONT_M, fill=W)
    d.text((FWID - 70, 60), f'RNG {tti * 240:04.0f} M', font=FONT_MB, fill=W, anchor='ra')     # ~240 m/s terminal
    d.text((FWID - 70, 82), f'TTI {tti:3.1f} S', font=FONT_M, fill=W, anchor='ra')
    if (t // 4) % 2 == 0:
        d.text((cx, FHEI - 92), 'TRK LOCK', font=FONT_MB, fill=W, anchor='mm')
    return out

# ---- camera ----
def camera(t):
    imp = st['impact']
    if imp is None and t < LAUNCH + 6:
        f = add(h.c, (-230, 70))                                     # side-on tracking of the glide, lead space ahead
        k = 0.18
    elif imp is None:
        dirv = math.atan2(m.v[1], m.v[0])
        lead = 60 + 170 * smooth(m.age / 50)
        side = 60 * math.sin(m.age * 0.035)                           # drift around it a little as it arcs
        f = add(add(m.p, (math.cos(dirv) * lead, math.sin(dirv) * lead)), (-math.sin(dirv) * side, math.cos(dirv) * side))
        k = 0.2
    else:
        u = t - imp
        if u == 0: st['cam'] = (60, -200)                             # hard cut to the side view of the hit
        if u < HOLD: f = (60 + u * 0.6, -200 - u * 0.4); k = 0.3
        else:
            f = add(h.c, (-160, 60)); k = 0.12 + 0.1 * smooth((u - HOLD) / PAN)
            e = UAVS[0]
            if e.p is not None:                                        # lean after the Gray Eagle as it tears past
                f = add(f, (max(-120.0, min(60.0, (e.p[0] - h.c[0]) * 0.18)), 0))
            if u == HOLD + PAN - 6: st['uav0'] = t
    last = st['cam'] or f
    st['cam'] = lerp(last, f, k)
    return st['cam']

def cam_tick(t):
    cf = camera(t)
    pf = (PLAYER[0], PLAYER[1] - 60)
    st['cf'] = lerp(pf, cf, smoother(t / 96))                        # slow reveal pan off the player
    st['sh'] = st['shake']; st['shake'] *= 0.82
    if m.alive and m.phase != 'eject': st['sh'] = max(st['sh'], 1.2)

def draw(t):
    cf, sh = st['cf'], st['sh']
    imp = st['impact']
    if st['seeker'] is not None and imp is None:
        im = seeker_frame(t)
    elif PUNCH_A <= t <= PUNCH_B:
        # slow-motion punch-in on the launcher: the whole frame at 2x (every pixel the same size), so the wings read
        P = st.get('punch_at') or add(world(TUBE), (-44, 4))
        cam = (P[0] - FWID / 2 + rng.uniform(-sh, sh) * 0.5, P[1] - FHEI / 2 + rng.uniform(-sh, sh) * 0.2)
        im, S = render_world(cam, t)
        im = im.crop((FWID // 4, FHEI // 4, FWID // 4 + FWID // 2, FHEI // 4 + FHEI // 2)).resize((FWID, FHEI), Image.NEAREST)
    else:
        cam = (cf[0] - FWID / 2 + rng.uniform(-sh, sh), cf[1] - FHEI / 2 + rng.uniform(-sh * 0.45, sh * 0.45))
        im, S = render_world(cam, t)
        draw_uavs(im, S, t)
        if imp is not None and t - imp < 3:                          # white-out as the feed dies
            im = Image.blend(im, Image.new('RGBA', im.size, (255, 255, 255, 255)), 0.85 - 0.35 * (t - imp))
    banner(im, t)
    end = (imp + HOLD + PAN + UAV_DUR + TITLE_DUR) if imp else 10 ** 9
    amount = smooth(t / 45) * (1 - smooth((t - (end - 40)) / 40))
    alert_frame(im, amount, t)
    if imp is not None:
        t0 = imp + HOLD + PAN + UAV_DUR - 30
        k = smooth((t - t0) / 16) * (1 - smooth((t - (end - 44)) / 24))
        title(im, k)
    return im.convert('RGB')

STEP = 3
frames, keys = [], {}
tick = 0
while True:
    tick += 1
    step()
    cam_tick(tick)
    imp = st['impact']
    if imp and tick >= imp + HOLD + PAN + UAV_DUR + TITLE_DUR: break
    if tick > 2000: raise SystemExit('no impact')
    slowmo = PUNCH_A <= tick <= PUNCH_B
    if tick % STEP == 0 or slowmo:
        frames.append(draw(tick))
        marks = {'d0': LAUNCH + 1, 'd1': LAUNCH + 4, 'd2': LAUNCH + 6, 'd3': LAUNCH + 8, 'd4': LAUNCH + 12, 'glide': 60, 'glide2': 110, 'desig': DESIG + 14, 'launch': LAUNCH + 12, 'climb': LAUNCH + 36, 'over': LAUNCH + 70}
        if st['seeker']: marks.update({'seek1': st['seeker'] + 4, 'seek2': st['seeker'] + 20, 'seek3': st['seeker'] + 36})
        if imp: marks.update({'after': imp + 24, 'after2': imp + 38, 'boom': imp + 6, 'pan': imp + HOLD + 14, 'uav1': imp + HOLD + PAN + 20, 'uav2': imp + HOLD + PAN + 44, 'title': imp + HOLD + PAN + UAV_DUR + 10})
        for name, at in marks.items():
            if abs(tick - at) < 2 and name not in keys: keys[name] = len(frames) - 1
keys['end'] = len(frames) - 1
print('frames', len(frames), 'seeker', st['seeker'], 'impact', st['impact'], keys)
picks = [frames[i] for i in sorted(set(keys.values()))]
mont = Image.new('RGB', (FWID, FHEI * len(picks)))
for j, f in enumerate(picks): mont.paste(f, (0, FHEI * j))
pal = mont.quantize(colors=255, method=Image.MEDIANCUT)
q = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
q[0].save(os.path.join(OUT, 'apache_e_entrance_v5.gif'), save_all=True, append_images=q[1:], duration=int(1000 * STEP / 60), loop=0, optimize=True, disposal=1)
for k_, i in keys.items(): frames[i].save(os.path.join(OUT, f'ape5_{k_}.png'))
