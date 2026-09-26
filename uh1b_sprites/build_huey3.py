"""
UH-1B Huey boss sprites, third pass: geometry from the clean line drawing (ref/uh1b_line_profile.png), paint and light
from the colour profile (ref/uh1_profiles_4view.png, top aircraft) registered onto it. Same scale as the Cobra.

Line drawing: nose tip x 13, fin trailing tip x 513 -> 12.08 m = 41.4 px/m (3.774 px per cell); skid bottom y 158.5;
mast x 164.5. Colour profile -> line drawing: x' = 13 + (x - 17) * 500/453, y' = 158.5 - (150 - y) * 500/453.
The silhouette is the drawing's closed outline filled; the drawing's inner lines become one-cell seams.
"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ah1g_sprites'))
import px                                                   # noqa: E402
from px import Canvas, Layer, save2, shift                  # noqa: E402

px.RAMPS['hod'] = [(26, 20, 14), (44, 34, 22), (62, 48, 31), (82, 64, 41), (104, 81, 52), (126, 100, 66),
                   (150, 122, 83), (176, 148, 106), (204, 178, 136)]
px.RAMPS['nose'] = [(20, 19, 20), (34, 32, 34), (50, 47, 49), (68, 64, 66), (90, 86, 86), (118, 114, 112)]
px.RAMPS['green'] = [(20, 40, 34), (34, 78, 62), (52, 120, 92), (96, 170, 136)]
px.RAMPS['navy'] = [(14, 20, 44), (24, 36, 78), (40, 58, 116)]
px.MATS[:] = list(px.RAMPS)
px.MID.clear(); px.MID.update({m: i + 1 for i, m in enumerate(px.MATS)})
MID, RAMPS = px.MID, px.RAMPS

NX, GY, PPC = 13.0, 158.5, 41.4 / 10.97
K = 500.0 / 453.0                                          # colour profile px -> line drawing px
OUT = os.path.join(HERE, 'out')
W, H, OX, OY = 142, 43, 6, 43
cv = Canvas(W, H, OX, OY)
X, Y = cv.cx, cv.cy


def c(p):
    """line-drawing pixel -> cell"""
    return ((p[0] - NX) / PPC, (GY - p[1]) / PPC)


def cp(p):
    """colour-profile pixel -> cell"""
    return c((13 + (p[0] - 17) * K, 158.5 - (150 - p[1]) * K))


# ------------------------------------------------------------------------------------------ the line drawing
_im = Image.open(os.path.join(HERE, 'ref', 'uh1b_line_profile.png')).convert('RGBA')
_bg = Image.new('RGBA', _im.size, (255, 255, 255, 255)); _bg.alpha_composite(_im)
LG = np.asarray(_bg.convert('L')).astype(np.float32)
INK = LG < 170
Hh, Ww = LG.shape
_yy, _xx = np.mgrid[0:Hh, 0:Ww]
# gear, tail skid, pitot and the mast stub are drawn by hand; keep them out of the filled body
_gear = (_yy > 141) | ((_xx > 470) & (_yy > 82)) | (_xx < 12)
_mast = (_yy < 49) & (_xx > 150) & (_xx < 180)
_filled = ndi.binary_fill_holes(ndi.binary_closing(INK & ~_gear & ~_mast, iterations=1))
SIL = _filled & ~_gear & ~_mast


def per_cell(mask):
    out = np.zeros((H, W))
    for r in range(H):
        for c_ in range(W):
            x0 = NX + (c_ - OX) * PPC; y1 = GY - (OY - r - 1) * PPC
            xa, xb = int(np.floor(x0)), int(np.ceil(x0 + PPC)); ya, yb = int(np.floor(y1 - PPC)), int(np.ceil(y1))
            if xb <= 0 or yb <= 0 or xa >= Ww or ya >= Hh:
                continue
            out[r, c_] = mask[max(ya, 0):yb, max(xa, 0):xb].mean()
    return out


COV = per_cell(SIL)
INKC = per_cell(INK & SIL)


def centre_ink():
    """a drawn line becomes a seam only in the cells it passes through near their centre: one cell thick"""
    out = np.zeros((H, W), bool)
    for r in range(H):
        for c_ in range(W):
            cx_ = NX + (c_ - OX + 0.5) * PPC; cy_ = GY - (OY - r - 0.5) * PPC
            xa, xb = int(cx_ - 1), int(cx_ + 1) + 1; ya, yb = int(cy_ - 1), int(cy_ + 1) + 1
            if 0 <= xa and xb < Ww and 0 <= ya and yb < Hh:
                out[r, c_] = INK[ya:yb, xa:xb].mean() > 0.3
    return out


INK1 = centre_ink()

# windows: the drawing's own closed panes, picked by a point inside each (line drawing px)
_free = ndi.binary_fill_holes(INK | _gear | _mast) & ~INK
_lab, _ = ndi.label(_free)
PANE_SEEDS = {'windscreen': (44, 100), 'door_front': (60, 103), 'door': (76, 97), 'door_top': (76, 79), 'cargo': (125, 95)}
PANES = {}
for _k, (_sx, _sy) in PANE_SEEDS.items():
    _l = _lab[_sy, _sx]
    PANES[_k] = per_cell(_lab == _l) >= 0.5 if _l else np.zeros((H, W), bool)
NOSE_PANEL = per_cell((_lab == _lab[125, 25]) | (INK & ndi.binary_dilation(_lab == _lab[125, 25], iterations=2))) >= 0.5

# ------------------------------------------------------------------------------------------ the colour profile
_ref = np.asarray(Image.open(os.path.join(HERE, 'ref', 'uh1_profiles_4view.png')).convert('RGB')).astype(np.float32)
PCOL = np.zeros((H, W, 3), np.float32)
for r in range(H):
    for c_ in range(W):
        lx0 = NX + (c_ - OX) * PPC; ly1 = GY - (OY - r - 1) * PPC
        x0 = 17 + (lx0 - 13) / K; x1 = x0 + PPC / K
        y1 = 150 - (158.5 - ly1) / K; y0 = y1 - PPC / K
        xa, xb = int(np.floor(x0)), int(np.ceil(x1)); ya, yb = int(np.floor(y0)), int(np.ceil(y1))
        if xb <= 0 or yb <= 0 or xa >= _ref.shape[1] or ya >= _ref.shape[0]:
            continue
        PCOL[r, c_] = _ref[max(ya, 0):yb, max(xa, 0):xb].reshape(-1, 3).mean(0)
PLUM = PCOL @ np.array([0.299, 0.587, 0.114], np.float32)

# landmarks (line drawing px)
MAST_X = c((164.5, 0))[0]
FAIRING_TOP = c((0, 50))[1]
HUB_Y = cp((0, 12))[1]
TAIL_HUB = c((507, 27))
SKID = (c((60, 0))[0], c((198, 0))[0])
STRUTS = (c((105, 0))[0], c((180, 0))[0])
TAIL_SKID = [c((483, 88)), c((513, 95))]
BAND_X = (cp((377, 0))[0], cp((405, 0))[0])
STAR_C = cp((253, 102))


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


def merge(dst, src):
    m = src.occ()
    dst.mat[m] = src.mat[m]; dst.tone[m] = src.tone[m]; dst.alpha[m] = src.alpha[m]


def body():
    L = cv.layer('Body')
    fus = COV >= 0.5
    L.fill(fus, 'hod', 4)
    edge = Layer.edge_of(fus)
    dt = runs_from(fus, 'top'); db = runs_from(fus, 'bot')
    k = (dt - 1) / np.maximum(dt + db - 2, 1)
    form = np.select([dt == 2, dt == 3, k < 0.62, k < 0.84], [6, 5, 4, 4], 3)
    # glass: light in the colour profile, forward of the cargo door's rear edge, above the belly
    glass = np.zeros((H, W), bool)
    for pm in PANES.values():
        glass |= pm
    glass &= fus & ~edge
    # markings left out of the light trace
    skip = glass | ((X >= BAND_X[0]) & (X <= BAND_X[1])) | (np.hypot(X - STAR_C[0], Y - STAR_C[1]) < 3.6) | \
        ((np.abs(Y - STAR_C[1]) < 1.2) & (np.abs(X - STAR_C[0]) < 8.4)) | \
        ((X > cp((282, 0))[0]) & (X < cp((340, 0))[0]) & (Y > cp((0, 106))[1]) & (Y < cp((0, 87))[1]))
    skin = fus & ~edge & ~skip
    broad = PLUM.copy()
    for r in range(H):
        for c_ in range(W):
            if skin[r, c_]:
                sl = (slice(max(r - 2, 0), r + 3), slice(max(c_ - 2, 0), c_ + 3))
                broad[r, c_] = np.median(PLUM[sl][skin[sl]])
    p5, p95 = np.percentile(broad[skin], [5, 95])
    traced = np.clip(1.5 + (broad - p5) / max(p95 - p5, 1) * 5.0, 1, 7)
    L.tone[fus] = form[fus]
    L.tone[skin] = form[skin]                              # clean form light (the profile's scan grain read as grime)
    L.recolor(skin & (dt >= 4) & (dt <= 5) & (Y > c((0, 100))[1]), tone=5)
    # nose cap: the drawing's panel at the nose, dark metal in the profile
    nose = fus & NOSE_PANEL & ~glass & ~edge
    L.fill(nose, 'nose', 3)
    L.recolor(nose & (runs_from(nose, 'top') <= 2), tone=5)
    L.recolor(nose & (runs_from(nose, 'bot') <= 3), tone=2)
    # the drawing's own lines: doors, panels, cowl louvres, fairing, the elevator, the fin rib
    seam = fus & ~edge & INK1 & ~glass
    L.tone[seam] = np.maximum(1, L.tone[seam] - 2)
    # paint: star insignia, yellow band with its arrow, step marks, placards
    sx, sy = STAR_C
    L.fill(fus & ~edge & (np.hypot(X - sx, Y - sy) < 3.4), 'navy', 1)
    L.fill(fus & ~edge & (np.abs(Y - sy) < 1.0) & (np.abs(X - sx) < 8.2) & (np.abs(X - sx) > 3.4), 'white', 3)
    L.fill(fus & ~edge & (np.abs(Y - sy) < 0.5) & (np.abs(X - sx) < 8.2) & (np.abs(X - sx) > 3.4), 'red', 3)
    for j, row in enumerate(['..X..', '.XXX.', 'XXXXX', '.XXX.', 'X...X']):
        for i, ch in enumerate(row):
            if ch == 'X':
                L.P(sx - 2 + i + 0.5, sy + 2 - j, 'white', 4)
    band = fus & ~edge & (X >= BAND_X[0]) & (X <= BAND_X[1])
    L.fill(band, 'yellow', 3)
    L.recolor(band & (dt == 2), tone=4); L.recolor(band & (db <= 2), tone=1)
    ay = cp((0, 88))[1]
    for x in np.arange(BAND_X[0] + 1.5, BAND_X[1] - 1.5, 1.0):
        L.P(x, ay, 'red', 3)
    L.P(BAND_X[1] - 2.0, ay + 1, 'red', 3); L.P(BAND_X[1] - 2.0, ay - 1, 'red', 3)
    for p in ((178, 84), (190, 84)):
        L.P(*cp(p), 'red', 3)
    for (sx_, y0_, y1_) in ((178, 108, 118), (190, 100, 112)):
        for y in range(y0_, y1_, 4):
            L.P(*cp((sx_, y)), 'yellow', 2)
    L.fill(glass, 'dark', 2)
    L.fill(edge, 'hod', 0)
    return L, fus, glass


def extras(L, fus):
    top = L.occ()
    m = (X > MAST_X - 1.0) & (X < MAST_X + 1.0) & (Y > FAIRING_TOP - 0.6) & (Y < HUB_Y - 1.0) & ~top
    L.fill(m & (X < MAST_X), 'steel', 5); L.fill(m & (X >= MAST_X), 'steel', 2)
    sw_y = FAIRING_TOP + 1.2
    L.fill((X > MAST_X - 3.0) & (X < MAST_X + 3.0) & (np.abs(Y - sw_y) < 0.6) & ~top, 'steel', 3)
    L.fill((X > MAST_X - 2.0) & (X < MAST_X + 2.0) & (np.abs(Y - sw_y - 1.0) < 0.6) & ~top, 'steel', 2)
    L.P(MAST_X - 2.5, sw_y, 'steel', 5)
    G = cv.layer('gear')
    x0, x1 = SKID
    belly = c((0, 140))[1]
    for xs in STRUTS:
        G.fill((X > xs - 1.0) & (X < xs) & (Y > 1.8) & (Y < belly), 'hod', 5)
        G.fill((X > xs) & (X < xs + 1.0) & (Y > 1.8) & (Y < belly), 'hod', 2)
        for dx in (-1.5, -0.5, 0.5, 1.5):
            G.P(xs + dx, 1.4, 'hod', 3)
    G.fill((X > x0 + 0.5) & (X < x1) & (Y > 1.0) & (Y < 2.0) & ~G.occ(), 'hod', 5)
    G.fill((X > x0 + 0.5) & (X < x1) & (Y > 0.0) & (Y < 1.0), 'hod', 1)
    for x in np.arange(x0 + 3.0, x1 - 2, 4.0):
        G.P(x, 1.5, 'hod', 6)
    G.P(x0, 1.5, 'hod', 5); G.P(x0, 0.5, 'hod', 1)
    G.P(x0 - 1.0, 2.5, 'hod', 5); G.P(x0 - 0.2, 2.5, 'hod', 2); G.P(x0 - 1.6, 3.4, 'hod', 4)
    G.P(x1, 1.5, 'hod', 5); G.P(x1 + 0.8, 2.5, 'hod', 4)
    outlined(G)
    T = cv.layer('tailskid')
    (xa, ya), (xb, yb) = TAIL_SKID
    for x in np.arange(xa, xb + 0.01, 0.5):
        T.P(x, ya + (yb - ya) * (x - xa) / (xb - xa), 'steel', 4)
    T.P(xb + 0.8, yb + 1.0, 'steel', 4)
    outlined(T, 0, 'steel')
    merge(L, G); merge(L, T)
    L.P(*c((8, 115)), 'steel', 5); L.P(*c((4, 115)), 'steel', 6)          # pitot


def glass_layer(fus, glass):
    Gl = cv.layer('Glass')
    Gl.fill(glass, 'glass', 4)
    d = runs_from(glass, 'top'); b = runs_from(glass, 'bot')
    Gl.recolor(glass & (d <= 2), tone=5)
    Gl.recolor(glass & (d == 1), tone=6)
    Gl.recolor(glass & (b <= 2), tone=3)
    # the drawing's frames cross the glass
    Gl.recolor(Layer.edge_of(glass) & INK1, mat='hod', tone=1)
    gl = Gl.is_mat('glass')
    for (pa, pb) in ((c((22, 118)), c((34, 96))), (c((50, 110)), c((58, 90))), (c((110, 105)), c((122, 88))),
                     (c((116, 105)), c((128, 88)))):
        Gl.line(pa[0], pa[1], pb[0], pb[1], 'glass', 7, only=gl)
    return Gl


FONT5 = {'A': ['.X.', 'X.X', 'XXX', 'X.X', 'X.X'], 'R': ['XX.', 'X.X', 'XX.', 'X.X', 'X.X'],
         'M': ['X.X', 'XXX', 'XXX', 'X.X', 'X.X'], 'Y': ['X.X', 'X.X', '.X.', '.X.', '.X.']}


def stencil(text, x0, y_top, flip):
    D = cv.layer('Marks')
    cols = []
    for ch in text:
        g = FONT5[ch]
        for i in range(3):
            cols.append([row[i] for row in g])
        cols.append(['.'] * 5)
    cols = cols[:-1]
    c0, r0 = cv.cell(x0, y_top)
    if flip:
        c0 = W - (c0 + len(cols))
    for i, col in enumerate(cols):
        for j, v in enumerate(col):
            if v == 'X':
                D.put(c0 + i, r0 + j, 'white', 3)
    return D


def weapons():
    """optional: M5 nose turret with its canvas bag, XM16 side rocket pod (from the render the user sent first)"""
    T = cv.layer('Turret')
    pod_ = (np.hypot((X - c((10, 0))[0]) / 3.2, (Y - c((0, 124))[1]) / 2.3) < 1)
    bag = (np.hypot((X - c((12, 0))[0]) / 2.8, (Y - c((0, 114))[1]) / 2.0) < 1) & ~pod_
    T.fill(pod_, 'hod', 4); T.recolor(pod_ & (runs_from(pod_, 'top') <= 2), tone=6)
    T.recolor(pod_ & (runs_from(pod_, 'bot') <= 2), tone=2)
    T.fill(bag, 'dark', 2); T.recolor(bag & (runs_from(bag, 'top') == 1), tone=4)
    bx, by = c((0, 118))
    T.P(bx, by, 'steel', 6); T.P(bx + 1, by, 'steel', 4); T.P(bx, by - 1, 'steel', 2); T.P(bx + 1, by - 1, 'steel', 2)
    outlined(T)
    P = cv.layer('Pod')
    mm = (X > c((135, 0))[0]) & (X < c((158, 0))[0]) & (Y > c((0, 140))[1]) & (Y < c((0, 133))[1])
    P.fill(mm, 'hod', 3)
    m = (X > c((120, 0))[0]) & (X < c((170, 0))[0]) & (Y > c((0, 152))[1]) & (Y < c((0, 140))[1])
    rows = sorted(set(np.nonzero(m)[0]))
    for i, r in enumerate(rows):
        kk = i / max(1, len(rows) - 1)
        P.fill(m & (np.arange(H)[:, None] == r), 'hod', 6 if kk < 0.25 else 5 if kk < 0.5 else 3 if kk < 0.8 else 2)
    cols = np.nonzero(m.any(0))[0]
    P.tone[rows[0]:rows[-1] + 1, cols[0]] = 7
    outlined(P)
    return T, P


def to2x_offset(x, y):
    return [round((x + OX) * 2 - W, 1), round((OY - y) * 2 - H, 1)]


def build(write=True):
    import build_huey as BH
    os.makedirs(OUT, exist_ok=True)
    Lb, fus, glass = body()
    extras(Lb, fus)
    T, P = weapons()
    tx, ty = cp((284, 89))
    layers = {
        'HueyBoss': Lb.render(), 'HueyBoss_Glass': glass_layer(fus, glass).render(),
        'HueyBoss_MarksL': stencil('ARMY', tx, ty, False).render(),
        'HueyBoss_MarksR': stencil('ARMY', tx, ty, True).render(),
        'HueyBoss_Turret': T.render(), 'HueyBoss_Pod': P.render(),
    }
    rs, rb = BH.rotor_sheet(); tr, trb = BH.tail_rotor()
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
        'turret_muzzle': to2x_offset(*c((0, 118))), 'pod_muzzle': to2x_offset(*c((120, 146))),
        'lights': {'position_red': to2x_offset(*c((70, 62))), 'beacon': to2x_offset(*c((248, 46))),
                   'tail_white': to2x_offset(*c((486, 90))), 'strobe': to2x_offset(*c((511, 40)))},
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
