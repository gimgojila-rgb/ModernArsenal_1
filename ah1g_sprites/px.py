"""
Cell-level pixel art helpers for the AH-1G sprites (same idea as humvee_sprites/tools/pix.py).

Reference coordinates: x cells aft of the nose tip, y cells above the skid bottom (1 cell = 1/10.97 m).
A canvas is (w, h) cells with the reference origin at canvas (ox, oy): column c holds x in [c-ox, c-ox+1),
row r holds y in [oy-r-1, oy-r). Everything is drawn at 1x and exported 2x nearest (project rule).
"""
import numpy as np
from PIL import Image, ImageDraw

SS = 8   # supersampling for polygon coverage

RAMPS = {
    # olive drab, a touch browner than the Apache D's (MiniApacheRemote) ramp; shadows cool, lights warm
    'od':     [(21, 22, 18), (32, 37, 30), (44, 50, 38), (58, 64, 45), (74, 79, 53), (91, 95, 62),
               (111, 113, 74), (136, 136, 92), (166, 162, 118)],
    # canopy, same blues as the Apache canopy
    'glass':  [(17, 18, 19), (33, 44, 52), (52, 72, 84), (79, 107, 120), (127, 156, 168), (169, 196, 205),
               (212, 230, 235), (246, 253, 255)],
    'dark':   [(10, 11, 13), (19, 21, 24), (29, 32, 36), (41, 45, 50), (56, 60, 66), (74, 79, 86), (96, 101, 108)],
    'steel':  [(16, 17, 20), (30, 32, 37), (46, 49, 55), (64, 68, 75), (86, 91, 99), (112, 118, 126),
               (146, 151, 158), (190, 194, 199)],
    'burnt':  [(20, 16, 14), (38, 30, 26), (58, 46, 38), (82, 66, 52), (110, 90, 70), (140, 116, 92)],
    'red':    [(48, 8, 8), (86, 14, 12), (128, 22, 18), (172, 34, 26), (212, 56, 40), (240, 110, 84),
               (255, 190, 170)],
    'white':  [(120, 118, 108), (170, 168, 158), (208, 206, 196), (236, 234, 224), (252, 251, 244)],
    'yellow': [(96, 70, 16), (156, 118, 30), (210, 164, 48), (240, 202, 86), (255, 232, 150)],
    'ink':    [(14, 15, 13), (24, 26, 22), (36, 39, 32)],          # stencil paint
}
MATS = list(RAMPS)
MID = {m: i + 1 for i, m in enumerate(MATS)}


class Canvas:
    def __init__(self, w, h, ox, oy):
        self.w, self.h, self.ox, self.oy = w, h, ox, oy
        yy, xx = np.mgrid[0:h, 0:w]
        self.cx = xx - ox + 0.5          # cell centres in reference coordinates
        self.cy = oy - yy - 0.5

    def cell(self, x, y):
        return int(np.floor(x + self.ox)), int(np.floor(self.oy - y))

    def cov_poly(self, pts):
        img = Image.new('L', (self.w * SS, self.h * SS), 0)
        ImageDraw.Draw(img).polygon([((x + self.ox) * SS, (self.oy - y) * SS) for x, y in pts], fill=255)
        a = np.asarray(img, dtype=np.float32) / 255.0
        return a.reshape(self.h, SS, self.w, SS).mean((1, 3))

    def cov_ell(self, cx, cy, rx, ry):
        yy, xx = np.mgrid[0:self.h * SS, 0:self.w * SS]
        px = (xx + 0.5) / SS - self.ox
        py = self.oy - (yy + 0.5) / SS
        m = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0
        return m.reshape(self.h, SS, self.w, SS).mean((1, 3))

    def where(self, fn):
        return fn(self.cx, self.cy)

    def layer(self, name):
        return Layer(self, name)


class Layer:
    def __init__(self, cv, name):
        self.cv, self.name = cv, name
        self.mat = np.zeros((cv.h, cv.w), np.int32)
        self.tone = np.zeros((cv.h, cv.w), np.int32)
        self.alpha = np.full((cv.h, cv.w), 255, np.int32)

    # ---- filling ----
    def fill(self, m, mat, tone, alpha=255):
        self.mat[m] = MID[mat]; self.tone[m] = tone; self.alpha[m] = alpha
        return m

    def poly(self, pts, mat, tone, thr=0.5):
        return self.fill(self.cv.cov_poly(pts) >= thr, mat, tone)

    def ell(self, cx, cy, rx, ry, mat, tone, thr=0.5):
        return self.fill(self.cv.cov_ell(cx, cy, rx, ry) >= thr, mat, tone)

    def put(self, c, r, mat, tone, alpha=255):
        if 0 <= c < self.cv.w and 0 <= r < self.cv.h:
            self.mat[r, c] = MID[mat]; self.tone[r, c] = tone; self.alpha[r, c] = alpha

    def P(self, x, y, mat, tone, alpha=255):
        c, r = self.cv.cell(x, y)
        self.put(c, r, mat, tone, alpha)

    def cells(self, x0, y0, x1, y1):
        """Bresenham cells between two reference points"""
        c0, r0 = self.cv.cell(x0, y0); c1, r1 = self.cv.cell(x1, y1)
        dc, dr = abs(c1 - c0), -abs(r1 - r0)
        sc, sr = (1 if c0 < c1 else -1), (1 if r0 < r1 else -1)
        err = dc + dr; out = []
        while True:
            out.append((c0, r0))
            if c0 == c1 and r0 == r1:
                break
            e2 = 2 * err
            if e2 >= dr:
                err += dr; c0 += sc
            if e2 <= dc:
                err += dc; r0 += sr
        return out

    def line(self, x0, y0, x1, y1, mat, tone, only=None):
        for c, r in self.cells(x0, y0, x1, y1):
            if only is None or (0 <= c < self.cv.w and 0 <= r < self.cv.h and only[r, c]):
                self.put(c, r, mat, tone)

    def polyline(self, pts, mat, tone, only=None):
        for a, b in zip(pts[:-1], pts[1:]):
            self.line(a[0], a[1], b[0], b[1], mat, tone, only)

    def recolor(self, m, tone=None, dt=None, mat=None, lo=None, hi=None):
        m = m & (self.mat > 0)
        if mat is not None:
            self.mat[m] = MID[mat]
        if tone is not None:
            self.tone[m] = tone
        if dt is not None:
            t = self.tone[m] + dt
            if lo is not None:
                t = np.maximum(t, lo)
            if hi is not None:
                t = np.minimum(t, hi)
            self.tone[m] = t
        return m

    def erase(self, m):
        self.mat[m] = 0

    def occ(self):
        return self.mat > 0

    def is_mat(self, mat):
        return self.mat == MID[mat]

    # ---- edges ----
    @staticmethod
    def edge_of(o, conn4=True):
        p = np.pad(o, 1)
        if conn4:
            nb = p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        else:
            nb = np.ones_like(o)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nb &= p[1 + dy:1 + dy + o.shape[0], 1 + dx:1 + dx + o.shape[1]]
        return o & ~nb

    def outline(self, tone=0, mat=None, keep=None, conn4=True):
        e = self.edge_of(self.occ(), conn4)
        if keep is not None:
            e &= ~keep
        self.tone[e] = tone
        if mat is not None:
            self.mat[e] = MID[mat]
        return e

    # ---- output ----
    def render(self):
        img = np.zeros((self.cv.h, self.cv.w, 4), np.uint8)
        for m, i in MID.items():
            sel = self.mat == i
            if not sel.any():
                continue
            ramp = np.array(RAMPS[m], np.uint8)
            t = np.clip(self.tone[sel], 0, len(ramp) - 1)
            img[sel, :3] = ramp[t]
            img[sel, 3] = self.alpha[sel]
        return img


def over(dst, src):
    """alpha composite of two uint8 RGBA arrays (src over dst)"""
    d = dst.astype(np.float32); s = src.astype(np.float32)
    sa = s[..., 3:4] / 255.0; da = d[..., 3:4] / 255.0
    oa = sa + da * (1 - sa)
    rgb = np.where(oa > 0, (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6), 0)
    return np.concatenate([rgb, oa * 255], -1).round().astype(np.uint8)


def up2(a):
    return a.repeat(2, axis=0).repeat(2, axis=1)


def save2(arr, path):
    Image.fromarray(up2(arr), 'RGBA').save(path)


def shift(m, dy=0, dx=0):
    """shift a boolean mask by (dy rows, dx cols), zero fill"""
    out = np.zeros_like(m)
    h, w = m.shape
    ys = slice(max(dy, 0), h + min(dy, 0)); yd = slice(max(-dy, 0), h + min(-dy, 0))
    xs = slice(max(dx, 0), w + min(dx, 0)); xd = slice(max(-dx, 0), w + min(-dx, 0))
    out[ys, xs] = m[yd, xd]
    return out
