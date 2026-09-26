"""
UH-1B traced from the clean side profile the user picked (ref/uh1_profiles_4view.png, top aircraft: an early
production UH-1B, 1960). Nose tip x 20, fin trailing tip x 468 -> 12.08 m = 37.1 px/m; skid bottom y 151.

Trace method (03_도트_스프라이트.md): silhouette from the white background, every cell takes the average colour of the
profile under it, the cells are clustered into the profile's own palette, lone cells are voted away, outline around
the outside. Text is lifted out (it would mirror when the sprite flips) and redrawn as stencils; the star insignia
stays in the body.
"""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ah1g_sprites'))
from px import Canvas, Layer, save2          # noqa: E402

REF = np.asarray(Image.open(os.path.join(HERE, 'ref', 'uh1_profiles_4view.png')).convert('RGB')).astype(np.float32)
NX, GY, PPC = 20.0, 151.0, 37.1 / 10.97       # nose tip, skid bottom, image pixels per cell

W, H, OX, OY = 142, 47, 4, 47
cv = Canvas(W, H, OX, OY)
X, Y = cv.cx, cv.cy


def img_xy(x, y):
    return NX + x * PPC, GY - y * PPC


def cells_from_px(pts):
    return [((px - NX) / PPC, (GY - py) / PPC) for px, py in pts]


# --- pixel masks on the profile
Hh, Ww = REF.shape[:2]
yy, xx = np.mgrid[0:Hh, 0:Ww]
nonwhite = REF.min(-1) < 215
region = (yy < 158) & (xx < 500)
caption = (xx > 205) & (xx < 405) & (yy > 12) & (yy < 38)
# tail rotor blades (drawn from their own sprite): a band along the blade line through the hub
hub = np.array([463.0, 30.0]); a0 = np.array([437.0, 0.0]); a1 = np.array([500.0, 67.0])
d = a1 - a0; t = ((xx - a0[0]) * d[0] + (yy - a0[1]) * d[1]) / (d @ d)
dist = np.hypot(xx - (a0[0] + t * d[0]), yy - (a0[1] + t * d[1]))
tail_rotor = (dist < 4.5) & (t > -0.05) & (t < 1.05) & ~((yy > 38) & (xx < 468))
# the main rotor head sits above the cowling; the body keeps only the mast
head = (yy < 44) & (xx > 125) & (xx < 190) & ~((xx >= 152) & (xx <= 160))
next_heli = (yy > 152) & (xx > 170) & (xx < 240)
from scipy import ndimage as ndi
SIL = nonwhite & region & ~caption & ~tail_rotor & ~head & ~next_heli
_filled = ndi.binary_fill_holes(ndi.binary_closing(SIL, iterations=2))
SIL = (SIL | (_filled & (yy < 136))) & region & ~caption & ~head & ~next_heli      # windows, not the gap over the skids

# --- per cell: coverage and mean colour
COV = np.zeros((H, W)); COL = np.zeros((H, W, 3))
for r in range(H):
    for c in range(W):
        x0, y1 = img_xy(c - OX, OY - r - 1)
        x1, y0 = img_xy(c - OX + 1, OY - r)
        xa, xb = int(np.floor(x0)), int(np.ceil(x1)); ya, yb = int(np.floor(y0)), int(np.ceil(y1))
        if xb <= 0 or yb <= 0 or xa >= Ww or ya >= Hh:
            continue
        # weights for partial pixels
        xs = np.arange(max(xa, 0), min(xb, Ww)); ys = np.arange(max(ya, 0), min(yb, Hh))
        wx = np.clip(np.minimum(xs + 1, x1) - np.maximum(xs, x0), 0, 1)
        wy = np.clip(np.minimum(ys + 1, y1) - np.maximum(ys, y0), 0, 1)
        wgt = wy[:, None] * wx[None, :]
        m = SIL[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1] if len(xs) and len(ys) else None
        if m is None or wgt.sum() == 0:
            continue
        COV[r, c] = (wgt * m).sum() / wgt.sum()
        if (wgt * m).sum() > 0:
            blk = REF[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]
            ww = (wgt * m)[..., None]
            COL[r, c] = (blk * ww).sum((0, 1)) / ww.sum()
LUM = COL @ np.array([0.299, 0.587, 0.114])
R_, G_, B_ = COL[..., 0], COL[..., 1], COL[..., 2]


RAMP = {
    'od': [(22, 21, 17), (36, 35, 27), (50, 48, 36), (64, 61, 45), (80, 76, 55), (98, 93, 67), (120, 113, 82),
           (146, 138, 101), (176, 168, 128)],
    'glass': [(52, 72, 84), (79, 107, 120), (127, 156, 168), (190, 214, 222)],
    'yellow': [(170, 128, 34), (220, 176, 52), (246, 214, 96)],
    'red': [(150, 30, 24), (206, 58, 40)],
    'white': [(196, 196, 188), (240, 240, 232)],
    'ink': [(26, 24, 20)],
}


def classify():
    """material per cell from the profile's colour"""
    mat = np.full((H, W), '', object)
    m = COV >= 0.5
    mx = COL.max(-1); mn = COL.min(-1); sat = (mx - mn) / np.maximum(mx, 1)
    mat[m] = 'od'
    mat[m & (LUM > 185) & (sat < 0.25)] = 'white'
    mat[m & (B_ > R_ + 12) & (LUM > 120)] = 'glass'
    mat[m & (R_ > 170) & (G_ > 150) & (B_ < 110)] = 'yellow'
    mat[m & (R_ > 150) & (G_ < 90) & (B_ < 90)] = 'red'
    mat[m & (LUM < 45)] = 'ink'
    return mat


def tone_bins(mask, n):
    """rank the cells of a material by brightness into n bins; each bin's colour is the profile's own mean colour"""
    v = LUM[mask]
    if v.size == 0:
        return {}, None
    q = np.quantile(v, np.linspace(0, 1, n + 1))
    b = np.clip(np.searchsorted(q[1:-1], LUM, side='right'), 0, n - 1)
    cols = {}
    for k in range(n):
        sel = mask & (b == k)
        if sel.any():
            cols[k] = COL[sel].mean(0)
    return cols, b


def mode_clean(img, m, passes=2):
    out = img.copy()
    for _ in range(passes):
        src = out.copy()
        for r in range(1, H - 1):
            for c in range(1, W - 1):
                if not m[r, c]:
                    continue
                nb = [tuple(src[r + dy, c + dx]) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)) if m[r + dy, c + dx]]
                if len(nb) >= 3 and tuple(src[r, c]) not in nb:
                    vals, cnt = np.unique(np.array(nb), axis=0, return_counts=True)
                    if cnt.max() >= 3:
                        out[r, c] = vals[cnt.argmax()]
    return out


def body_image():
    mat = classify()
    m = COV >= 0.5
    img = np.zeros((H, W, 4), np.uint8)
    for name, n in (('od', 7), ('glass', 4), ('yellow', 3), ('red', 2), ('white', 2), ('ink', 1)):
        sel = m & (mat == name)
        cols, b = tone_bins(sel, n)
        ramp = RAMP.get(name)
        for k, cc in cols.items():
            # structure comes from the profile's brightness order; colour from the ramp (the scan leans brown)
            img[sel & (b == k), :3] = ramp[min(k + (1 if name == 'od' else 0), len(ramp) - 1)] if ramp else np.clip(cc, 0, 255)
        img[sel, 3] = 255
    img[..., :3] = mode_clean(img[..., :3], m)
    e = Layer.edge_of(m)
    img[e, :3] = (26, 24, 20)
    return img, mat, m
