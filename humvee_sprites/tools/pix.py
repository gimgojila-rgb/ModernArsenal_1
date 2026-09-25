"""Cell-level pixel art helpers. Coordinates are in reference cells (x right = front, y down).
Canvas cell = ref cell + (OX, OY). Every layer is a pair of int arrays: mat (0 = empty) and tone."""
import numpy as np
from PIL import Image, ImageDraw

W, H = 112, 60
OX, OY = 1, 6
SS = 8  # supersampling for shape coverage

RAMPS = {
    'tan':    [(38,29,20),(70,56,40),(102,84,60),(134,112,82),(163,139,104),(188,165,126),(209,188,150),(229,213,180)],
    'glass':  [(10,14,16),(20,27,30),(32,42,46),(48,62,66),(70,90,94),(108,130,132),(170,190,188)],
    'rubber': [(10,10,10),(22,22,21),(34,33,31),(50,48,45),(68,65,60),(90,86,79)],
    'steel':  [(12,13,16),(24,26,30),(38,41,47),(56,60,67),(80,85,93),(110,115,123),(152,157,164),(198,202,206)],
    'chassis':[(14,13,11),(26,24,21),(40,37,32),(56,52,45),(76,71,62),(100,94,82)],
    'olive':  [(20,23,16),(34,39,27),(50,57,39),(68,77,53),(88,98,68),(110,120,85),(138,146,108)],
    'rust':   [(34,18,12),(62,34,22),(94,54,34),(126,76,46),(156,102,64),(186,134,90)],
    'alu':    [(48,48,46),(76,76,73),(106,106,101),(138,137,131),(170,169,162),(204,203,196)],
    'red':    [(44,8,6),(92,18,14),(142,30,22),(192,52,36),(232,104,80),(250,170,150)],
    'amber':  [(70,38,8),(140,80,16),(206,132,32),(244,184,70),(255,226,150)],
    'green':  [(10,40,20),(30,120,60),(90,220,130),(190,255,210)],
    'yellow': [(90,70,20),(160,130,40),(206,176,70),(236,214,120)],
    'white':  [(120,120,116),(180,180,174),(226,226,220),(250,250,246)],
    'black':  [(8,8,9),(16,16,18),(26,26,29),(38,38,42),(54,54,58)],
}
MATS = list(RAMPS.keys())
MID = {m: i + 1 for i, m in enumerate(MATS)}


def cov_poly(pts):
    """coverage (H,W) float of a polygon given in ref cell coords"""
    img = Image.new('L', (W * SS, H * SS), 0)
    d = ImageDraw.Draw(img)
    d.polygon([((x + OX) * SS, (y + OY) * SS) for x, y in pts], fill=255)
    a = np.asarray(img, dtype=np.float32) / 255.0
    return a.reshape(H, SS, W, SS).mean((1, 3))


def cov_ellipse(cx, cy, rx, ry):
    yy, xx = np.mgrid[0:H * SS, 0:W * SS]
    px = (xx + 0.5) / SS - OX
    py = (yy + 0.5) / SS - OY
    m = ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0
    return m.reshape(H, SS, W, SS).mean((1, 3))


def cov_rect(x0, y0, x1, y1):
    return cov_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


class Layer:
    def __init__(self, name, w=W, h=H):
        self.name = name
        self.w, self.h = w, h
        self.mat = np.zeros((h, w), np.int32)
        self.tone = np.zeros((h, w), np.int32)
        self.alpha = np.full((h, w), 255, np.int32)
        self.lock = np.zeros((h, w), bool)   # cells excluded from auto outline recolor

    # ---- raw ops (canvas cell coords) ----
    def put(self, x, y, mat, tone, alpha=255):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.mat[y, x] = MID[mat]
            self.tone[y, x] = tone
            self.alpha[y, x] = alpha

    def fill(self, mask, mat, tone, alpha=255):
        self.mat[mask] = MID[mat]
        self.tone[mask] = tone
        self.alpha[mask] = alpha

    def recolor(self, mask, tone=None, dt=None, mat=None):
        m = mask & (self.mat > 0)
        if mat is not None:
            self.mat[m] = MID[mat]
        if tone is not None:
            self.tone[m] = tone
        if dt is not None:
            self.tone[m] += dt

    def erase(self, mask):
        self.mat[mask] = 0

    # ---- ref-coordinate ops ----
    def P(self, x, y, mat, tone, alpha=255):
        self.put(int(np.floor(x)) + OX, int(np.floor(y)) + OY, mat, tone, alpha)

    def poly(self, pts, mat, tone, thr=0.5, alpha=255):
        m = cov_poly(pts) >= thr
        self.fill(m, mat, tone, alpha)
        return m

    def ell(self, cx, cy, rx, ry, mat, tone, thr=0.5, alpha=255):
        m = cov_ellipse(cx, cy, rx, ry) >= thr
        self.fill(m, mat, tone, alpha)
        return m

    def rect(self, x0, y0, x1, y1, mat, tone, alpha=255):
        """integer ref cells inclusive x0..x1-1"""
        m = np.zeros((self.h, self.w), bool)
        m[int(y0) + OY:int(y1) + OY, int(x0) + OX:int(x1) + OX] = True
        self.fill(m, mat, tone, alpha)
        return m

    def line(self, x0, y0, x1, y1, mat, tone, alpha=255):
        """Bresenham between integer ref cells"""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        pts = []
        while True:
            pts.append((x0, y0))
            self.put(x0 + OX, y0 + OY, mat, tone, alpha)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy
        return pts

    def cells(self, pts, mat, tone, alpha=255):
        for x, y in pts:
            self.put(x + OX, y + OY, mat, tone, alpha)

    def occ(self):
        return self.mat > 0

    # ---- shading ----
    def outline2(self, vsil, seam=1, ext=0):
        """edge cells: darkest if they touch the outside of the whole vehicle, seam tone otherwise"""
        o = self.occ()
        p = np.pad(o, 1)
        nb = p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        e = o & ~nb & ~self.lock
        out = ~np.pad(vsil, 1)
        touch_out = out[:-2, 1:-1] | out[2:, 1:-1] | out[1:-1, :-2] | out[1:-1, 2:]
        self.tone[e & touch_out] = ext
        self.tone[e & ~touch_out] = np.minimum(self.tone[e & ~touch_out], seam)
        return e

    def outline(self, color_mat=None, tone=0, keep=None):
        """recolor cells on the silhouette edge (4-neighbour to empty) to darkest tone"""
        o = self.occ()
        e = np.zeros_like(o)
        p = np.pad(o, 1)
        nb = p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        e = o & ~nb
        if keep is not None:
            e &= ~keep
        e &= ~self.lock
        self.tone[e] = tone
        if color_mat:
            self.mat[e] = MID[color_mat]
        return e

    def render(self):
        img = np.zeros((self.h, self.w, 4), np.uint8)
        for m, i in MID.items():
            sel = self.mat == i
            if not sel.any():
                continue
            ramp = np.array(RAMPS[m], np.uint8)
            t = np.clip(self.tone[sel], 0, len(ramp) - 1)
            img[sel, :3] = ramp[t]
            img[sel, 3] = self.alpha[sel]
        return img


def composite(layers, bg=None, w=W, h=H):
    out = np.zeros((h, w, 4), np.float32)
    if bg is not None:
        out[..., :3] = bg; out[..., 3] = 255
    for L in layers:
        src = L.render().astype(np.float32) if isinstance(L, Layer) else L.astype(np.float32)
        a = src[..., 3:4] / 255.0
        out[..., :3] = src[..., :3] * a + out[..., :3] * (1 - a)
        out[..., 3:4] = np.maximum(out[..., 3:4], src[..., 3:4])
    return out.astype(np.uint8)


def save_scaled(arr, path, s=2, flip=False):
    im = Image.fromarray(arr, 'RGBA')
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im.resize((im.width * s, im.height * s), Image.NEAREST).save(path)


def mask_ref(fn):
    """boolean canvas mask from a predicate on ref cell centers"""
    yy, xx = np.mgrid[0:H, 0:W]
    return fn(xx - OX + 0.5, yy - OY + 0.5)


def stamp(L, rows, x0, y0, pal, alpha=255):
    """draw an ASCII pixel map; top-left cell at ref (x0, y0); '.' = skip"""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.' or ch == ' ':
                continue
            m, t = pal[ch]
            L.put(int(x0) + i + OX, int(y0) + j + OY, m, t, alpha)
