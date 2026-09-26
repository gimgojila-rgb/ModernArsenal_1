"""
UH-1B Huey boss sprites (the Cobra's twin), at the Apache body scale (10.97 cells per metre, exported 2x nearest).

Shapes are traced by hand on ref/uh1b_side_render.webp (geom_huey.py). Inside each part the shading comes from the
render itself: every cell takes the average colour of the image pixels under it, and the cell brightness is ranked
within its material and mapped onto that material's ramp (the trace method in 03_도트_스프라이트.md). Painted colour
(yellow band, red cowl stripe) is picked up from the render the same way. Text is left out of the trace (it would read
mirrored) and drawn as unflipped stencils instead.

Layers on the body canvas (all drawn at the same position):
  HueyBoss.png            fuselage, boom, fin, mast, beacon, XM156 mount, skid gear, tail skid
  HueyBoss_Glass.png      windscreen, door and cargo windows, green roof window
  HueyBoss_MarksL/R.png   "ARMY" on the boom, unflipped (L facing left, R facing right)
  HueyBoss_Turret.png     M5 40 mm nose turret with its canvas blast bag
  HueyBoss_Pod.png        rocket pod on the side mount
Own canvases:
  HueyBoss_MainRotor.png  2-blade rotor with the Bell stabiliser bar, 6 frames (30 deg apart), + _MainRotorBlur
  HueyBoss_TailRotor.png  2-blade tail rotor with red/white/red tips, rotated in code, + _TailRotorBlur
"""
import os, sys, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ah1g_sprites'))
from px import Canvas, Layer, RAMPS, MID, save2, shift, over     # noqa: E402
import px                                                          # noqa: E402
from geom_huey import *                                            # noqa: E402

px.RAMPS['grey'] = [(21, 22, 22), (40, 43, 44), (60, 64, 66), (82, 86, 88), (106, 110, 112), (132, 136, 138),
                    (160, 163, 164), (190, 192, 192)]
px.RAMPS['green'] = [(20, 40, 34), (34, 78, 62), (52, 120, 92), (96, 170, 136)]
px.MATS[:] = list(px.RAMPS)
px.MID.clear(); px.MID.update({m: i + 1 for i, m in enumerate(px.MATS)})

OUT = os.path.join(HERE, 'out')
W, H, OX, OY = 145, 47, 8, 47
cv = Canvas(W, H, OX, OY)
X, Y = cv.cx, cv.cy

REF = np.asarray(Image.open(os.path.join(HERE, 'ref', 'uh1b_side_render.webp')).convert('RGB')
                 .transpose(Image.FLIP_LEFT_RIGHT)).astype(np.float32)


def cell_colour():
    """average ref colour under every canvas cell (area average over the image pixels it covers)"""
    col = np.zeros((H, W, 3), np.float32)
    for r in range(H):
        for c_ in range(W):
            x0 = NX + (c_ - OX) * PX_X; x1 = x0 + PX_X
            y1 = GY - (OY - r - 1) * PX_Y; y0 = y1 - PX_Y
            xa, xb = int(np.floor(x0)), int(np.ceil(x1)); ya, yb = int(np.floor(y0)), int(np.ceil(y1))
            if xb <= 0 or yb <= 0 or xa >= REF.shape[1] or ya >= REF.shape[0]:
                continue
            blk = REF[max(ya, 0):yb, max(xa, 0):xb]
            col[r, c_] = blk.reshape(-1, 3).mean(0)
    return col


COL = cell_colour()
LUM = COL @ np.array([0.299, 0.587, 0.114], np.float32)
R_, G_, B_ = COL[..., 0], COL[..., 1], COL[..., 2]
YELLOWISH = (R_ > 140) & (G_ > 115) & (B_ < 95) & (R_ - B_ > 80)
REDDISH = (R_ > 105) & (G_ < 75) & (B_ < 75) & (R_ - G_ > 50)


def smooth_in(m, lum=LUM, k=1):
    """mean brightness over the cell's neighbours that share its mask (calms the render's grime and speckle)"""
    acc = np.zeros_like(lum); n = np.zeros_like(lum)
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            mm = shift(m, dy, dx)
            ll = np.roll(np.roll(lum, dy, 0), dx, 1)
            acc += np.where(mm & m, ll, 0); n += (mm & m)
    return np.where(n > 0, acc / np.maximum(n, 1), lum)


def rank_tones(L, m, mat, lo, hi, lum=LUM, gamma=1.0):
    """trace shading: rank the cell brightness inside mask m and spread it over tones lo..hi"""
    if not m.any():
        return
    v = lum[m]
    order = v.argsort().argsort() / max(1, len(v) - 1)
    t = lo + np.floor((order ** gamma) * (hi - lo + 0.999)).astype(int)
    L.mat[m] = MID[mat]; L.tone[m] = np.clip(t, lo, hi)


def runs_from(m, direction):
    d = np.zeros(m.shape, np.int32)
    rows = range(m.shape[0]) if direction == 'top' else range(m.shape[0] - 1, -1, -1)
    prev = np.zeros(m.shape[1], np.int32)
    for r in rows:
        cur = np.where(m[r], prev + 1, 0)
        d[r] = cur; prev = cur
    return d


def outlined(L, tone=0, mat='od'):
    e = Layer.edge_of(L.occ())
    L.tone[e] = tone; L.mat[e] = MID[mat]
    return L


def merge(dst, src):
    m = src.occ()
    dst.mat[m] = src.mat[m]; dst.tone[m] = src.tone[m]; dst.alpha[m] = src.alpha[m]


def poly(pts, thr=0.5):
    return cv.cov_poly(pts) >= thr


# ----------------------------------------------------------------------------------------------------------- body
def body():
    L = cv.layer('Body')
    fus = poly(FUSELAGE)
    glass = poly(WINDSCREEN) | poly(DOOR_WIN) | poly(CARGO_WIN)
    # the white boom lettering is traced over (it would come out mirrored) and redrawn as a stencil
    text_zone = fus & (X > 70) & (X < 100) & (Y > 11) & (Y < 20)
    bright = LUM > 150
    skin = fus & ~glass
    nose = skin & (X < NOSE_CAP_X)
    band = skin & (X >= BAND_X[0]) & (X <= BAND_X[1])
    red = skin & REDDISH & ~band & (X > 60) & (X < 70)      # the red stripe on the engine cowl
    od = skin & ~nose & ~band & ~red
    base = od & ~(text_zone & bright)
    rank_tones(L, base, 'od', 1, 6, lum=smooth_in(base, k=2), gamma=0.9)
    # blend the render's light with a plain form ramp (top rolls into the light, belly into shade) so the grime and
    # reflections of the render don't read as camouflage
    dtb = runs_from(fus, 'top'); dbb = runs_from(fus, 'bot')
    hgt = dtb + dbb - 1
    k = (dtb - 1) / np.maximum(hgt - 1, 1)
    form = np.select([k < 0.12, k < 0.3, k < 0.62, k < 0.85], [6, 5, 4, 3], 2)
    L.tone[base] = np.round((L.tone[base] + form[base]) / 2.0).astype(int)
    # lettering cells take the tone of the skin right above them
    for r, c_ in zip(*np.nonzero(od & text_zone & bright)):
        rr = r
        while rr > 0 and (text_zone[rr, c_] and bright[rr, c_]):
            rr -= 1
        L.mat[r, c_] = MID['od']; L.tone[r, c_] = L.tone[rr, c_] if L.mat[rr, c_] else 3
    rank_tones(L, nose, 'grey', 2, 6, lum=smooth_in(nose, k=1))
    # yellow warning band: its span is fixed from the render, the red arrow inside it is kept
    bspan = skin & (X >= BAND_X[0]) & (X <= BAND_X[1])
    rank_tones(L, bspan, 'yellow', 1, 4, lum=smooth_in(bspan, k=1))
    L.fill(bspan & REDDISH, 'red', 3)
    rank_tones(L, red, 'red', 2, 4)
    # doors, the cargo door rail and the engine exhaust, from the render
    inner = fus & ~Layer.edge_of(fus)
    def seam(pts, dt=-2):
        for a_, b_ in zip(pts[:-1], pts[1:]):
            for cc, rr in L.cells(*c(a_), *c(b_)):
                if 0 <= cc < W and 0 <= rr < H and inner[rr, cc] and L.is_mat('od')[rr, cc]:
                    L.tone[rr, cc] = max(1, L.tone[rr, cc] + dt)
    seam([(604, 204), (702, 204), (702, 350)])                  # cockpit door
    seam([(706, 212), (800, 212), (800, 346)])                  # cargo door
    seam([(700, 300), (905, 300)], dt=-1)                       # cargo door lower rail
    seam([(560, 262), (560, 350)])                              # nose cap joint
    ex = poly(cl([(1018, 170), (1034, 176), (1040, 196), (1024, 198)]), 0.4) & fus
    L.fill(ex, 'dark', 1)
    L.recolor(ex & (runs_from(ex, 'top') == 1), mat='steel', tone=4)
    # cabin interior where the windows are (shows if the glass layer is left off)
    L.fill(glass & fus, 'dark', 2)
    # top edges catch the light
    dt = runs_from(fus, 'top')
    L.recolor(fus & (dt == 2) & L.is_mat('od'), dt=1, hi=7)
    e = Layer.edge_of(fus)
    L.fill(e, 'od', 0)
    return L, fus


def extras(L):
    top = L.occ()
    # mast, from the transmission cowl up to the hub, swashplate at its foot
    m = (X > MAST_X - 1.0) & (X < MAST_X + 1.0) & (Y > MAST_BASE_Y) & (Y < HUB_Y - 1.0) & ~top
    L.fill(m & (X < MAST_X), 'steel', 5)
    L.fill(m & (X >= MAST_X), 'steel', 2)
    sw = (X > MAST_X - 3.0) & (X < MAST_X + 3.0) & (Y > MAST_BASE_Y) & (Y < MAST_BASE_Y + 1.0)
    L.fill(sw, 'steel', 3)
    L.P(MAST_X - 2.5, MAST_BASE_Y + 0.5, 'steel', 5)
    # beacon (lens neutral, tinted in code)
    bx, by = BEACON
    L.P(bx, by + 0.3, 'white', 3); L.P(bx + 1, by + 0.3, 'white', 1)
    L.P(bx, by + 1.3, 'od', 0); L.P(bx + 1, by + 1.3, 'od', 0)
    # XM156 mount under the cabin
    M = cv.layer('mount')
    mm = M.fill(poly(MOUNT), 'od', 3)
    rank_tones(M, mm, 'od', 1, 5)
    outlined(M)
    # skid gear
    G = cv.layer('gear')
    x0, x1 = SKID
    for xs in STRUTS:
        G.fill((X > xs - 1.0) & (X < xs) & (Y > 1.8) & (Y < 6.4), 'od', 5)
        G.fill((X > xs) & (X < xs + 1.0) & (Y > 1.8) & (Y < 6.4), 'od', 2)
        for dx in (-1.5, -0.5, 0.5, 1.5):
            G.P(xs + dx, 1.4, 'od', 3)
    G.fill((X > x0 + 0.5) & (X < x1) & (Y > 1.0) & (Y < 2.0) & ~G.occ(), 'od', 5)
    G.fill((X > x0 + 0.5) & (X < x1) & (Y > 0.0) & (Y < 1.0), 'od', 1)
    for x in np.arange(x0 + 3.0, x1 - 2, 4.0):
        G.P(x, 1.5, 'od', 6)
    G.P(x0, 1.5, 'od', 5); G.P(x0, 0.5, 'od', 1)
    G.P(x0 - 1.0, 2.5, 'od', 5); G.P(x0 - 0.2, 2.5, 'od', 2)
    G.P(x0 - 1.6, 3.4, 'od', 4)
    G.P(x1 - 0.5, 1.5, 'od', 3)
    outlined(G)
    # tail skid (the render paints it in yellow and black bands)
    T = cv.layer('tailskid')
    (xa, ya), (xb, yb) = TAIL_SKID
    for i, x in enumerate(np.arange(xa, xb + 0.01, 1.0)):
        y = ya + (yb - ya) * (x - xa) / (xb - xa)
        T.P(x, y, 'yellow' if (i // 2) % 2 == 0 else 'dark', 3 if (i // 2) % 2 == 0 else 1)
    T.P(xb + 1.0, yb + 1.0, 'dark', 1)
    outlined(T, 0, 'dark')
    for part in (M, G, T):
        merge(L, part)


# ------------------------------------------------------------------------------------------------------ glass
def glass_layer(fus):
    Gl = cv.layer('Glass')
    edge = Layer.edge_of(fus)
    for pts, lo, hi in ((WINDSCREEN, 2, 6), (DOOR_WIN, 1, 5), (CARGO_WIN, 1, 5)):
        m = poly(pts) & fus & ~edge
        rank_tones(Gl, m, 'glass', lo, hi)
        fr = Layer.edge_of(m)
        Gl.recolor(fr & ~edge, mat='od', tone=1)           # window frames
    rw = poly(ROOF_WIN, 0.3) & fus & ~Layer.edge_of(fus)
    Gl.fill(rw, 'green', 2)
    Gl.recolor(rw & (runs_from(rw, 'top') == 1), tone=3)
    # a glint across the windscreen and the door window, as on the Apache canopy
    for (xa, ya, xb, yb) in ((9.2, 16.5, 12.8, 25.0), (16.8, 15.0, 19.6, 21.6), (30.6, 15.4, 33.4, 21.2)):
        Gl.line(xa, ya, xb, yb, 'glass', 7, only=Gl.is_mat('glass'))
    return Gl


# ----------------------------------------------------------------------------------------------- turret, pod
def turret():
    """M5 nose turret: a pod shaded as a horizontal drum, the black canvas blast bag bunched over the gun with a
    few lit folds, the short 40 mm barrel poking out of the bag"""
    T = cv.layer('Turret')
    pod_ = poly(TURRET_POD); bag = poly(TURRET_BAG) & ~pod_
    rows = sorted(set(np.nonzero(pod_)[0]))
    for i, r in enumerate(rows):
        k = i / max(1, len(rows) - 1)
        t = 6 if k < 0.2 else 5 if k < 0.4 else 4 if k < 0.6 else 3 if k < 0.8 else 2
        T.fill(pod_ & (np.arange(H)[:, None] == r), 'od', t)
    T.recolor(pod_ & (X < c((452, 0))[0]), dt=1, hi=7)                  # front of the drum faces the light
    T.fill(bag, 'dark', 2)
    T.recolor(bag & (smooth_in(bag) > np.percentile(LUM[bag], 70)), tone=4)   # folds catching light
    T.recolor(bag & (runs_from(bag, 'top') == 1), tone=3)
    bx, by = c((441, 296))
    for dx, t in ((0, 6), (1, 4), (2, 4)):
        T.P(bx + dx, by, 'steel', t); T.P(bx + dx, by - 1, 'steel', 2)
    T.P(bx - 1, by, 'steel', 1); T.P(bx - 1, by - 1, 'steel', 0)
    outlined(T)
    return T


def pod():
    P = cv.layer('Pod')
    m = poly(POD)
    rows = sorted(set(np.nonzero(m)[0])); top, bot = rows[0], rows[-1]
    rank_tones(P, m, 'od', 2, 6)
    inner = rows[1:-1]
    for i, r in enumerate(inner):                          # cylinder: the render's light plus a firm top light
        k = i / max(1, len(inner) - 1)
        if k < 0.15:
            P.tone[r, m[r]] = np.maximum(P.tone[r, m[r]], 6)
        elif k > 0.8:
            P.tone[r, m[r]] = np.minimum(P.tone[r, m[r]], 2)
    cols = np.nonzero(m.any(0))[0]
    for c_ in (cols[0], cols[-1]):
        P.mat[top, c_] = 0; P.mat[bot, c_] = 0
    P.tone[top + 1:bot, cols[0] + 1] = 7                   # lit front rim
    P.tone[top + 1:bot, cols[-1] - 1] = 1
    outlined(P)
    return P


# ------------------------------------------------------------------------------------------------------ stencil
FONT5 = {
    'A': ['.X.', 'X.X', 'XXX', 'X.X', 'X.X'], 'R': ['XX.', 'X.X', 'XX.', 'X.X', 'X.X'],
    'M': ['X.X', 'XXX', 'XXX', 'X.X', 'X.X'], 'Y': ['X.X', 'X.X', '.X.', '.X.', '.X.'],
}


def stencil(text, x0, y_top, flip, mat='white', tone=3):
    D = cv.layer('Marks')
    cols = []
    for ch in text:
        g = FONT5[ch]
        for i in range(len(g[0])):
            cols.append([row[i] for row in g])
        cols.append(['.'] * 5)
    cols = cols[:-1]
    c0, r0 = cv.cell(x0, y_top)
    if flip:
        c0 = W - (c0 + len(cols))
    for i, col in enumerate(cols):
        for j, v in enumerate(col):
            if v == 'X':
                D.put(c0 + i, r0 + j, mat, tone)
    return D


# ------------------------------------------------------------------------------------------------------- rotors
RW, RH, RSTRIDE = 128, 9, 10
RHUB = (64.0, 3.5)
RR = 62.5


def rotor_frame(theta):
    a = np.zeros((RH, RW, 4), np.uint8)

    def put(c_, r, mat, t, al=255):
        if 0 <= c_ < RW and 0 <= r < RH:
            a[r, int(c_), :3] = RAMPS[mat][t]; a[r, int(c_), 3] = al
    ct, st = np.cos(theta), np.sin(theta)
    cx = RHUB[0]
    for sgn, near in ((1, st <= 0), (-1, st > 0)):
        Lb = RR * abs(ct)
        d = sgn * np.sign(ct) if abs(ct) > 1e-6 else sgn
        x_tip = max(Lb, 3.6 * abs(st))
        for u in np.arange(3.0, x_tip + 0.001, 1.0):
            c_ = int(np.floor(cx + d * u)) if d > 0 else int(np.floor(cx - u))
            if x_tip - u < 2.0:
                put(c_, 3, 'yellow', 3 if near else 1)
            else:
                glint = near and 0.45 < u / RR < 0.62
                put(c_, 3, 'dark', 5 if glint else (2 if near else 1))
                if u < 7:
                    put(c_, 4, 'dark', 1 if near else 0)
    # Bell stabiliser bar, square to the blades, one row under them, with its end weights
    sb = 11.0 * abs(st)
    for u in np.arange(-sb, sb + 0.01, 1.0):
        put(int(np.floor(cx + u)), 5, 'dark', 2)
    if sb > 2:
        for s in (-1, 1):
            e = int(np.floor(cx + s * sb))
            put(e, 5, 'steel', 4); put(e, 6, 'steel', 2); put(e - s, 6, 'steel', 1)
    gw = 1.5 + 3.0 * abs(ct)
    for u in np.arange(-gw, gw + 0.01, 1.0):
        put(int(np.floor(cx + u)), 3, 'steel', 3)
        put(int(np.floor(cx + u)), 4, 'steel', 1)
    for u in (-1, 0):
        put(int(cx + u), 2, 'steel', 5 if u < 0 else 3)
        put(int(cx + u), 1, 'steel', 6 if u < 0 else 4)
        put(int(cx + u), 0, 'steel', 5 if u < 0 else 3)      # the tall Huey mast nut
    for k in (1, -1):
        px_ = cx + k * 2.4 * st
        for r in (5, 6, 7, 8):
            put(int(np.floor(px_)), r, 'steel', 4 if k > 0 else 2)
    return a


def rotor_sheet():
    frames = [rotor_frame(np.radians(30 * i)) for i in range(6)]
    sheet = np.zeros((RSTRIDE * 6, RW, 4), np.uint8)
    for i, f in enumerate(frames):
        sheet[i * RSTRIDE:i * RSTRIDE + RH] = f
    blur = np.zeros((RH, RW, 4), np.uint8)
    col = np.array(RAMPS['dark'][3], np.uint8)
    for c_ in range(RW):
        u = abs(c_ + 0.5 - RHUB[0]) / RR
        if u > 1.0:
            continue
        for r, b0, g0 in ((2, 42, 22), (3, 90, 48), (4, 70, 40), (5, 38, 16)):
            blur[r, c_, :3] = col; blur[r, c_, 3] = int(b0 + g0 * (1 - u))
        if u > 0.965:
            blur[3, c_, :3] = RAMPS['yellow'][2]; blur[3, c_, 3] = 120
    hub = rotor_frame(np.radians(45))
    hc = slice(int(RHUB[0]) - 12, int(RHUB[0]) + 12)
    sub = hub[:, hc]; m = sub[..., 3] > 0
    blk = blur[:, hc]; blk[m] = sub[m]; blur[:, hc] = blk
    return sheet, blur


TR = 29


def tail_rotor():
    a = np.zeros((TR, TR, 4), np.uint8)

    def put(c_, r, mat, t):
        if 0 <= c_ < TR and 0 <= r < TR:
            a[r, c_, :3] = RAMPS[mat][t]; a[r, c_, 3] = 255
    c0 = TR // 2; R = 13
    for sgn in (1, -1):
        for u in range(2, R + 1):
            c_ = c0 + sgn * u
            band = R - u                                     # red / white / red tip bands, as on the render
            if band < 2:
                m1, t1, t2 = 'red', 4, 2
            elif band < 4:
                m1, t1, t2 = 'white', 3, 1
            elif band < 5:
                m1, t1, t2 = 'red', 4, 2
            else:
                m1, t1, t2 = 'dark', 6, 3
            put(c_, c0 - 1, m1, t1); put(c_, c0, m1, t2)
        put(c0 + sgn * (R + 1), c0 - 1, 'dark', 0); put(c0 + sgn * (R + 1), c0, 'dark', 0)
    for dc in (-1, 0, 1):
        for dr in (-1, 0, 1):
            put(c0 + dc, c0 + dr, 'steel', 3)
    put(c0, c0, 'steel', 6); put(c0 - 1, c0 - 1, 'steel', 5); put(c0 + 1, c0 + 1, 'steel', 1)
    for dc in (-2, 2):
        for dr in range(-2, 3):
            put(c0 + dc, c0 + dr, 'dark', 0)
    for dr in (-2, 2):
        for dc in (-1, 0, 1):
            put(c0 + dc, c0 + dr, 'dark', 0)
    b = np.zeros((TR, TR, 4), np.uint8)
    yy, xx = np.mgrid[0:TR, 0:TR]
    rr = np.hypot(xx - c0, yy - c0)
    disc = rr <= R + 0.5
    b[disc, :3] = RAMPS['dark'][3]; b[disc, 3] = 58
    b[(rr > R - 0.9) & disc, :3] = RAMPS['dark'][1]; b[(rr > R - 0.9) & disc, 3] = 105
    ring = (rr > R - 3.0) & (rr <= R - 0.9)
    b[ring, :3] = RAMPS['red'][3]; b[ring, 3] = 70
    b[(rr > 5.6) & (rr < 6.6), 3] = 70
    hub = (abs(xx - c0) <= 2) & (abs(yy - c0) <= 2)
    b[hub] = a[hub]
    return a, b


# ------------------------------------------------------------------------------------------------------- export
def to2x_offset(x, y):
    return [round((x + OX) * 2 - W, 1), round((OY - y) * 2 - H, 1)]


def build(write=True):
    os.makedirs(OUT, exist_ok=True)
    Lb, fus = body()
    extras(Lb)
    tx0, ty = c((1110, 253))
    layers = {
        'HueyBoss': Lb.render(),
        'HueyBoss_Glass': glass_layer(fus).render(),
        'HueyBoss_MarksL': stencil('ARMY', tx0, ty, False).render(),
        'HueyBoss_MarksR': stencil('ARMY', tx0, ty, True).render(),
        'HueyBoss_Turret': turret().render(),
        'HueyBoss_Pod': pod().render(),
    }
    rs, rb = rotor_sheet()
    layers['HueyBoss_MainRotor'] = rs
    layers['HueyBoss_MainRotorBlur'] = rb
    tr, trb = tail_rotor()
    layers['HueyBoss_TailRotor'] = tr
    layers['HueyBoss_TailRotorBlur'] = trb
    mast_c = cv.cell(MAST_X, 0)[0]
    hub_r = cv.cell(0, HUB_Y)[1]
    coords = {
        'note': '2x pixels. Offsets are from the HueyBoss.png centre with the nose to the left (flip x when facing '
                'right).',
        'body_size': [W * 2, H * 2],
        'rotor_axis': [round((mast_c + 0.5) * 2 - W, 1), round((hub_r + 0.5) * 2 - H, 1)],
        'rotor_frame': {'size': [RW * 2, RH * 2], 'stride': RSTRIDE * 2, 'frames': 6, 'deg_per_frame': 30,
                        'hub': [RHUB[0] * 2, RHUB[1] * 2]},
        'tail_rotor_hub': to2x_offset(*TAIL_HUB),
        'tail_rotor_frame': {'size': [TR * 2, TR * 2], 'hub': [TR, TR]},
        'turret_muzzle': to2x_offset(*c((441, 296))),
        'pod_muzzle': to2x_offset(*c((750, 368))),
        'beacon': to2x_offset(*BEACON),
        'skid_bottom_y': round(OY * 2 - H, 1),
    }
    if write:
        for k, a in layers.items():
            save2(a, os.path.join(OUT, k + '.png'))
        with open(os.path.join(OUT, 'HueyBoss_coords.json'), 'w') as f:
            json.dump(coords, f, indent=1)
    return layers, coords


if __name__ == '__main__':
    layers, coords = build()
    print(json.dumps(coords, indent=1))
