"""
UH-1B Huey boss sprites, second pass: shapes measured on the clean side profile (geom_huey2.py), clean pixel-art shading
by rule like the AH-1G (flat sides, top rolling into the light, belly into shade), details placed cell by cell.
Same scale as the Cobra and the Apache (10.97 cells/m, 2x nearest export).

Body-canvas layers (same position): HueyBoss, HueyBoss_Glass, HueyBoss_MarksL/R (unflipped stencils),
HueyBoss_Turret (M5 nose turret, optional), HueyBoss_Pod (XM16 side rocket pod, optional).
Own canvases: HueyBoss_MainRotor (6 frames, Bell stabiliser bar) + _MainRotorBlur, HueyBoss_TailRotor + _TailRotorBlur.
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ah1g_sprites'))
import px                                                  # noqa: E402
from px import Canvas, Layer, save2, shift                 # noqa: E402
from geom_huey2 import *                                    # noqa: E402

px.RAMPS['hod'] = [(26, 20, 14), (44, 34, 22), (62, 48, 31), (82, 64, 41), (104, 81, 52), (126, 100, 66),
                   (150, 122, 83), (176, 148, 106), (204, 178, 136)]    # the profile's warm 1960 olive drab
px.RAMPS['nose'] = [(20, 19, 20), (34, 32, 34), (50, 47, 49), (68, 64, 66), (90, 86, 86), (118, 114, 112)]
px.RAMPS['green'] = [(20, 40, 34), (34, 78, 62), (52, 120, 92), (96, 170, 136)]
px.RAMPS['navy'] = [(14, 20, 44), (24, 36, 78), (40, 58, 116)]
px.MATS[:] = list(px.RAMPS)
px.MID.clear(); px.MID.update({m: i + 1 for i, m in enumerate(px.MATS)})
MID, RAMPS = px.MID, px.RAMPS

OUT = os.path.join(HERE, 'out')
W, H, OX, OY = 144, 44, 8, 44
cv = Canvas(W, H, OX, OY)
X, Y = cv.cx, cv.cy


def poly(pts, thr=0.5):
    return cv.cov_poly(pts) >= thr


def runs_from(m, direction):
    d = np.zeros(m.shape, np.int32)
    rows = range(m.shape[0]) if direction == 'top' else range(m.shape[0] - 1, -1, -1)
    prev = np.zeros(m.shape[1], np.int32)
    for r in rows:
        cur = np.where(m[r], prev + 1, 0)
        d[r] = cur; prev = cur
    return d


def outlined(L, tone=0, mat='hod'):
    e = Layer.edge_of(L.occ())
    L.tone[e] = tone; L.mat[e] = MID[mat]
    return L


def merge(dst, src):
    m = src.occ()
    dst.mat[m] = src.mat[m]; dst.tone[m] = src.tone[m]; dst.alpha[m] = src.alpha[m]


def seam(L, fus, pts, dt=-2, lo=1, mat='hod'):
    inner = fus & ~Layer.edge_of(fus)
    for a, b in zip(pts[:-1], pts[1:]):
        for cc, rr in L.cells(a[0], a[1], b[0], b[1]):
            if 0 <= cc < W and 0 <= rr < H and inner[rr, cc] and L.is_mat(mat)[rr, cc]:
                L.tone[rr, cc] = max(lo, min(8, L.tone[rr, cc] + dt))


def profile_sample():
    """area-average colour of the clean profile under every cell"""
    from PIL import Image
    ref = np.asarray(Image.open(os.path.join(HERE, 'ref', 'uh1_profiles_4view.png')).convert('RGB')).astype(np.float32)
    col = np.zeros((H, W, 3), np.float32)
    for r in range(H):
        for c_ in range(W):
            x0 = NX + (c_ - OX) * PPC; y1 = GY - (OY - r - 1) * PPC
            xa, xb = int(np.floor(x0)), int(np.ceil(x0 + PPC)); ya, yb = int(np.floor(y1 - PPC)), int(np.ceil(y1))
            if xb <= 0 or yb <= 0 or xa >= ref.shape[1] or ya >= ref.shape[0]:
                continue
            col[r, c_] = ref[max(ya, 0):yb, max(xa, 0):xb].reshape(-1, 3).mean(0)
    return col


PCOL = profile_sample()
PLUM = PCOL @ np.array([0.299, 0.587, 0.114], np.float32)


def med3(v, m):
    out = v.copy()
    for r in range(H):
        for c_ in range(W):
            if m[r, c_]:
                blk = v[max(r - 1, 0):r + 2, max(c_ - 1, 0):c_ + 2][m[max(r - 1, 0):r + 2, max(c_ - 1, 0):c_ + 2]]
                out[r, c_] = np.median(blk)
    return out


def body():
    L = cv.layer('Body')
    fus = poly(FUSELAGE)
    L.fill(fus, 'hod', 4)
    dt = runs_from(fus, 'top'); db = runs_from(fus, 'bot')
    hgt = dt + db - 1
    k = (dt - 1) / np.maximum(hgt - 1, 1)
    form = np.select([dt == 2, dt == 3, k < 0.62, k < 0.84], [6, 5, 4, 4], 3)
    # the profile's own light, ranked inside the skin (markings and windows left out), smoothed a little, then
    # blended 70/30 with the plain form ramp
    skip = poly(WINDSCREEN) | poly(DOOR_WIN) | poly(CARGO_WIN) | poly(NOSE_CAP) | \
        ((X >= BAND_X[0]) & (X <= BAND_X[1])) | (np.hypot(X - STAR_C[0], Y - STAR_C[1]) < 3.6) | \
        ((np.abs(Y - STAR_C[1]) < 1.2) & (np.abs(X - STAR_C[0]) < 8.4)) | \
        ((X > c((282, 0))[0]) & (X < c((340, 0))[0]) & (Y > c((0, 106))[1]) & (Y < c((0, 87))[1]))
    skin = fus & ~skip & ~Layer.edge_of(fus)
    lum = med3(PLUM, skin)
    broad = lum.copy()                                       # broad light only: 5x5 mean inside the skin
    for r in range(H):
        for c_ in range(W):
            if skin[r, c_]:
                sl = (slice(max(r - 2, 0), r + 3), slice(max(c_ - 2, 0), c_ + 3))
                broad[r, c_] = lum[sl][skin[sl]].mean()
    p5, p95 = np.percentile(broad[skin], [5, 95])
    traced = np.clip(1.5 + (broad - p5) / max(p95 - p5, 1) * 5.0, 1, 7)
    L.tone[fus] = form[fus]
    L.tone[skin] = np.round(0.6 * traced[skin] + 0.4 * form[skin]).astype(int)
    # the profile's ink: cells much darker than their smoothed neighbourhood become seam lines
    ink = skin & (PLUM < 0.72 * lum) & (PLUM < 70)
    L.tone[ink] = np.maximum(1, L.tone[ink] - 2)
    L.recolor(fus & (db == 2), tone=2)
    L.recolor(fus & (db == 3), tone=3)
    # cowlings: the doghouse and engine cowl sides lean in, so they carry more light than the cabin side
    cowl = fus & (X > c((165, 0))[0]) & (X < c((244, 0))[0]) & (Y > COWL_LINE[0][1])
    L.recolor(fus & (X > c((165, 0))[0]) & (X < c((244, 0))[0]) & (Y <= COWL_LINE[0][1]) & (Y > COWL_LINE[0][1] - 1.0),
              tone=2)                                                          # the cowl's lower edge casts shade
    L.recolor(fus & (dt == 2) & (X > c((168, 0))[0]) & (X < c((238, 0))[0]), tone=7)
    # tail boom: driveshaft cover along the top, seam, rounded side
    boom = fus & (X > c((250, 0))[0]) & (X < c((408, 0))[0])
    seam_y = np.interp(X, [BOOM_SEAM[0][0], BOOM_SEAM[1][0]], [BOOM_SEAM[0][1], BOOM_SEAM[1][1]])
    L.recolor(boom & (dt == 2), tone=7)
    L.recolor(boom & (Y <= seam_y) & (Y > seam_y - 1.0), tone=3)
    # fin: flat, lit leading edge, darker trailing edge
    fin = fus & (X > c((405, 0))[0]) & (Y > c((0, 80))[1])
    le = np.interp(Y, [c((405, 77))[1], c((458, 31))[1]], [c((405, 77))[0], c((458, 31))[0]])
    L.recolor(fin & (X < le + 2.0) & (dt > 1), tone=6)
    te = np.interp(Y, [c((442, 87))[1], c((471, 37))[1]], [c((442, 87))[0], c((471, 37))[0]])
    L.recolor(fin & (X > te - 1.5) & (dt > 1), tone=3)
    # nose cap: dark metal, rounded, with its vent dots
    nose = poly(NOSE_CAP) & fus
    L.fill(nose, 'nose', 3)
    ndt = runs_from(nose, 'top')
    L.recolor(nose & (ndt <= 2), tone=5)
    L.recolor(nose & (Y < c((0, 124))[1]), tone=2)
    L.P(*c((22, 104)), 'nose', 5)
    for (vx, vy) in ((26, 117), (32, 117), (38, 118), (29, 123), (35, 124), (41, 124)):
        L.P(*c((vx, vy)), 'nose', 1)
    # doors, rails, pillar, rub strip
    seam(L, fus, COCKPIT_DOOR + [COCKPIT_DOOR[0]], dt=-2)
    seam(L, fus, CARGO_DOOR + [CARGO_DOOR[0]], dt=-2)
    seam(L, fus, [c((100, 129)), c((150, 129))], dt=-1)
    seam(L, fus, LIT_LINE, dt=2)
    seam(L, fus, [c((168, 60)), c((168, 131))], dt=-2)                        # cabin / aft fuselage joint
    seam(L, fus, [c((252, 82)), c((252, 118))], dt=-2)                        # boom joint
    # door handles and step markings (yellow in the profile)
    L.P(*c((92, 100)), 'yellow', 2); L.P(*c((144, 100)), 'yellow', 2)
    for (sx, sy0, sy1) in ((178, 108, 118), (190, 100, 112)):
        for y in range(sy0, sy1, 4):
            L.P(*c((sx, y)), 'yellow', 2)
    # red placards on the doghouse side (fire access), as in the profile
    L.P(*c((178, 84)), 'red', 3); L.P(*c((182, 84)), 'red', 2); L.P(*c((190, 84)), 'red', 3)
    # engine air intake grille and exhaust
    g = poly(GRILLE)
    L.fill(g & fus, 'hod', 2)
    for gx in range(207, 232, 4):
        seam(L, fus, [c((gx, 59)), c((gx, 71))], dt=-1)
    ex = poly(EXHAUST, 0.4)
    L.fill(ex, 'steel', 2)
    L.recolor(ex & (runs_from(ex, 'top') == 1), tone=5)
    # national insignia: star in a blue disc with bars, symmetric so it flips with the body
    sx, sy = STAR_C
    L.fill(fus & (np.hypot(X - sx, (Y - sy) * 1.0) < 3.4), 'navy', 1)
    L.fill(fus & (np.abs(Y - sy) < 1.0) & (np.abs(X - sx) < 8.2) & (np.abs(X - sx) > 3.4), 'white', 3)
    L.fill(fus & (np.abs(Y - sy) < 0.5) & (np.abs(X - sx) < 8.2) & (np.abs(X - sx) > 3.4), 'red', 3)
    star = ['..X..', '.XXX.', 'XXXXX', '.XXX.', 'X...X']
    for j, row in enumerate(star):
        for i, ch in enumerate(row):
            if ch == 'X':
                L.P(sx - 2 + i + 0.5, sy + 2 - j, 'white', 4)
    # yellow warning band with its red arrow
    band = fus & (X >= BAND_X[0]) & (X <= BAND_X[1])
    L.fill(band, 'yellow', 3)
    L.recolor(band & (dt == 2), tone=4)
    L.recolor(band & (db <= 2), tone=1)
    ay = c((0, 88))[1]
    for x in np.arange(BAND_X[0] + 1.5, BAND_X[1] - 1.5, 1.0):
        L.P(x, ay, 'red', 3)
    L.P(BAND_X[1] - 2.0, ay + 1, 'red', 3); L.P(BAND_X[1] - 2.0, ay - 1, 'red', 3)
    # cabin interior under the windows (shows if the glass layer is left off)
    glass = (poly(WINDSCREEN) | poly(DOOR_WIN) | poly(CARGO_WIN)) & fus
    L.fill(glass, 'dark', 2)
    L.fill(Layer.edge_of(fus), 'hod', 0)
    return L, fus


def extras(L, fus):
    top = L.occ()
    # mast, swashplate
    m = (X > MAST_X - 1.0) & (X < MAST_X + 1.0) & (Y > COWL_TOP_Y - 0.5) & (Y < HUB_Y - 1.0) & ~top
    L.fill(m & (X < MAST_X), 'steel', 5)
    L.fill(m & (X >= MAST_X), 'steel', 2)
    sw = (X > MAST_X - 2.5) & (X < MAST_X + 2.5) & (np.abs(Y - SWASH_Y) < 0.6) & ~top
    L.fill(sw, 'steel', 3); L.P(MAST_X - 2.0, SWASH_Y, 'steel', 5)
    # VHF antenna on the roof
    for a, b in zip(ANTENNA[:-1], ANTENNA[1:]):
        L.line(a[0], a[1], b[0], b[1], 'steel', 4, only=~fus)
    # skid gear
    G = cv.layer('gear')
    x0, x1 = SKID
    for xs in STRUTS:
        G.fill((X > xs - 1.0) & (X < xs) & (Y > 1.8) & (Y < c((0, 131))[1]), 'hod', 5)
        G.fill((X > xs) & (X < xs + 1.0) & (Y > 1.8) & (Y < c((0, 131))[1]), 'hod', 2)
        for dx in (-1.5, -0.5, 0.5, 1.5):
            G.P(xs + dx, 1.4, 'hod', 3)
    G.fill((X > x0 + 0.5) & (X < x1) & (Y > 1.0) & (Y < 2.0) & ~G.occ(), 'hod', 5)
    G.fill((X > x0 + 0.5) & (X < x1) & (Y > 0.0) & (Y < 1.0), 'hod', 1)
    for x in np.arange(x0 + 3.0, x1 - 2, 4.0):
        G.P(x, 1.5, 'hod', 6)
    G.P(x0, 1.5, 'hod', 5); G.P(x0, 0.5, 'hod', 1)
    G.P(x0 - 1.0, 2.5, 'hod', 5); G.P(x0 - 0.2, 2.5, 'hod', 2)
    G.P(x0 - 1.6, 3.4, 'hod', 4)
    G.P(x1, 1.5, 'hod', 5); G.P(x1 + 0.8, 2.5, 'hod', 4)
    outlined(G)
    T = cv.layer('tailskid')
    (xa, ya), (xb, yb) = TAIL_SKID
    for x in np.arange(xa, xb + 0.01, 0.5):
        y = ya + (yb - ya) * (x - xa) / (xb - xa)
        T.P(x, y, 'steel', 4)
    T.P(xb + 1.0, yb + 1.0, 'steel', 4)
    outlined(T, 0, 'steel')
    merge(L, G); merge(L, T)


def glass_layer(fus):
    Gl = cv.layer('Glass')
    edge = Layer.edge_of(fus)
    for pts, bright in ((WINDSCREEN, 1), (DOOR_WIN, 0), (CARGO_WIN, 0)):
        m = poly(pts) & fus & ~edge
        Gl.fill(m, 'glass', 4 + bright)
        d = runs_from(m, 'top'); b = runs_from(m, 'bot')
        Gl.recolor(m & (d <= 2), tone=5 + bright)
        Gl.recolor(m & (b <= 2), tone=3)
        Gl.recolor(Layer.edge_of(m), mat='hod', tone=1)                       # frame
    for (pa, pb) in ((c((44, 100)), c((58, 80))), (c((72, 104)), c((80, 84))), (c((112, 103)), c((122, 86))),
                     (c((118, 103)), c((128, 86)))):
        Gl.line(pa[0], pa[1], pb[0], pb[1], 'glass', 7, only=Gl.is_mat('glass'))
    Gl.line(*PILLAR[0], *PILLAR[1], 'hod', 1, only=fus & ~edge)
    rw = poly(ROOF_WIN, 0.3) & fus & ~edge
    Gl.fill(rw, 'green', 2)
    Gl.recolor(rw & (runs_from(rw, 'top') == 1), tone=3)
    return Gl


def turret():
    T = cv.layer('Turret')
    pod_ = poly(TURRET_POD); bag = poly(TURRET_BAG) & ~pod_
    rows = sorted(set(np.nonzero(pod_)[0]))
    for i, r in enumerate(rows):
        kk = i / max(1, len(rows) - 1)
        T.fill(pod_ & (np.arange(H)[:, None] == r), 'hod', 6 if kk < 0.2 else 5 if kk < 0.45 else 4 if kk < 0.7 else 2)
    T.fill(bag, 'dark', 2)
    T.recolor(bag & (runs_from(bag, 'top') <= 1), tone=4)
    for (fx, fy) in ((8, 104), (14, 101), (19, 106)):
        T.P(*c((fx, fy)), 'dark', 4)
    bx, by = c((0, 108))
    for dx, t in ((0, 6), (1, 4)):
        T.P(bx + dx, by, 'steel', t); T.P(bx + dx, by - 1, 'steel', 2)
    outlined(T, 0, 'hod')
    return T


def pod():
    P = cv.layer('Pod')
    M = cv.layer('mount')
    mm = poly(MOUNT)
    M.fill(mm, 'hod', 3); M.recolor(mm & (runs_from(mm, 'top') == 1), tone=5)
    outlined(M)
    m = poly(POD)
    rows = sorted(set(np.nonzero(m)[0])); top, bot = rows[0], rows[-1]
    P.fill(m, 'hod', 4)
    inner = rows[1:-1]
    for i, r in enumerate(inner):
        kk = i / max(1, len(inner) - 1)
        P.tone[r, m[r]] = 6 if kk < 0.2 else 5 if kk < 0.45 else 4 if kk < 0.7 else 3 if kk < 0.9 else 2
    cols = np.nonzero(m.any(0))[0]
    for cc in (cols[0], cols[-1]):
        P.mat[top, cc] = 0; P.mat[bot, cc] = 0
    P.tone[top + 1:bot, cols[0] + 1] = 7
    P.tone[top + 1:bot, cols[-1] - 1] = 2
    for bx in (c((126, 0))[0], c((162, 0))[0]):
        cc, _ = cv.cell(bx, 0)
        P.tone[top + 1:bot, cc] = np.maximum(1, P.tone[top + 1:bot, cc] - 2)
    outlined(P)
    merge(M, P)
    return M


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


def to2x_offset(x, y):
    return [round((x + OX) * 2 - W, 1), round((OY - y) * 2 - H, 1)]


def build(write=True):
    import build_huey as BH                    # rotor and tail rotor generators (shared with the first pass)
    os.makedirs(OUT, exist_ok=True)
    Lb, fus = body()
    extras(Lb, fus)
    tx, ty = c((284, 89))
    layers = {
        'HueyBoss': Lb.render(),
        'HueyBoss_Glass': glass_layer(fus).render(),
        'HueyBoss_MarksL': stencil('ARMY', tx, ty, False).render(),
        'HueyBoss_MarksR': stencil('ARMY', tx, ty, True).render(),
        'HueyBoss_Turret': turret().render(),
        'HueyBoss_Pod': pod().render(),
    }
    rs, rb = BH.rotor_sheet()
    tr, trb = BH.tail_rotor()
    layers.update({'HueyBoss_MainRotor': rs, 'HueyBoss_MainRotorBlur': rb, 'HueyBoss_TailRotor': tr,
                   'HueyBoss_TailRotorBlur': trb})
    mast_c = cv.cell(MAST_X, 0)[0]; hub_r = cv.cell(0, HUB_Y)[1]
    coords = {
        'note': '2x pixels. Offsets are from the HueyBoss.png centre with the nose to the left (flip x when facing right).',
        'body_size': [W * 2, H * 2],
        'rotor_axis': [round((mast_c + 0.5) * 2 - W, 1), round((hub_r + 0.5) * 2 - H, 1)],
        'rotor_frame': {'size': [BH.RW * 2, BH.RH * 2], 'stride': BH.RSTRIDE * 2, 'frames': 6, 'deg_per_frame': 30,
                        'hub': [BH.RHUB[0] * 2, BH.RHUB[1] * 2]},
        'tail_rotor_hub': to2x_offset(*TAIL_HUB),
        'tail_rotor_frame': {'size': [BH.TR * 2, BH.TR * 2], 'hub': [BH.TR, BH.TR]},
        'turret_muzzle': to2x_offset(*c((0, 108))),
        'pod_muzzle': to2x_offset(*c((118, 138))),
        'lights': {'position_red': to2x_offset(*c((66, 69))), 'beacon': to2x_offset(*c((233, 51))),
                   'tail_white': to2x_offset(*c((444, 90))), 'strobe': to2x_offset(*c((470, 38)))},
        'skid_bottom_y': round(OY * 2 - H, 1),
    }
    if write:
        for k_, a in layers.items():
            save2(a, os.path.join(OUT, k_ + '.png'))
        with open(os.path.join(OUT, 'HueyBoss_coords.json'), 'w') as f:
            json.dump(coords, f, indent=1)
    return layers, coords


if __name__ == '__main__':
    build()
