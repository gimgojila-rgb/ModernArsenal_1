"""
Mk19 item sprite v5, same method as m230_v5.py. The user's photo (ref/mk19.png, on its tripod, seen from the front left)
is turned 13 deg so the barrel is level (ref/mk19_level.png); parts are laid out on a grid measured off that (1 cell =
8 px, origin (180, 72)); inside each part the shading comes from the photo's brightness in the cell; top edges lifted a
step, bottom edges dropped a step, outline. The tripod is left off (it's an item you hold); the cradle and its plate stay.
"""
from PIL import Image, ImageDraw
import numpy as np

SRC = np.asarray(Image.open('/home/claude/art/ref/mk19_level.png').convert('RGB')).astype(np.float32)
X0, Y0, S = 180, 72, 8
W, H = 58, 22
OUT = (20, 20, 26)
RAMP = {
    'blk': [(26, 27, 33), (38, 40, 48), (54, 57, 66), (74, 78, 89), (100, 105, 118), (134, 140, 154)],
    'olv': [(40, 52, 36), (58, 74, 50), (80, 98, 66), (106, 126, 88)],
    'bar': [(34, 36, 42), (52, 55, 63), (74, 78, 88), (104, 109, 120)],
}


def cell_lum(x, y):
    blk = SRC[Y0 + y * S:Y0 + (y + 1) * S, X0 + x * S:X0 + (x + 1) * S]
    m = blk.min(-1) < 238
    return blk.mean(-1)[m].mean() if m.any() else None


lab = np.full((H, W), '', dtype=object)


def fill(x0, y0, x1, y1, part):
    lab[y0:y1 + 1, x0:x1 + 1] = part


seg = np.zeros((H, W), int)      # which piece each cell belongs to (for the seam lines only)
_n = [0]


def poly(points_photo, part, thr=0.45, same=False, seam_only=False):
    """rasterise a polygon given in photo px and mark the cells it mostly covers"""
    im = Image.new('L', (W * S, H * S), 0)
    ImageDraw.Draw(im).polygon([(x - X0, y - Y0) for x, y in points_photo], fill=255)
    cov = np.asarray(im, np.float32).reshape(H, S, W, S).mean(axis=(1, 3)) / 255
    if not same:
        _n[0] += 1
    m = cov >= thr
    if seam_only:
        m &= lab != ''
    else:
        lab[m] = part
    seg[m] = _n[0]


# ---- layout (photo px, levelled photo) ----
# arched ribbed grip and the brace down to the receiver top: a triangle frame with its hole
poly([(206, 128), (201, 112), (202, 96), (208, 83), (218, 76), (230, 78), (228, 88), (220, 92), (214, 104), (213, 118), (215, 130)], 'blk')
poly([(222, 86), (232, 86), (290, 126), (280, 134)], 'blk', 0.4)
# rear rail with its holes, and the knob under it
poly([(182, 124), (240, 124), (240, 142), (182, 142)], 'blk')
poly([(208, 142), (222, 142), (222, 152), (208, 152)], 'blk')
# receiver: the raised rear section, the long top cover, the body, the rounded end cap, the lower rear step
poly([(236, 126), (322, 126), (322, 206), (236, 206)], 'blk')
poly([(318, 142), (460, 136), (472, 150), (472, 206), (318, 206)], 'blk')
poly([(318, 142), (460, 136), (472, 150), (472, 154), (318, 156)], 'blk', seam_only=True)   # the top cover over the body
poly([(230, 158), (252, 158), (254, 202), (230, 202)], 'blk')
poly([(254, 200), (332, 200), (332, 216), (254, 216)], 'blk')
poly([(470, 158), (480, 158), (480, 176), (470, 176)], 'blk')
# the cradle: black mounting plate with the notch, the olive plate and its arm
poly([(364, 204), (466, 204), (466, 240), (364, 240)], 'blk')
poly([(356, 186), (438, 186), (440, 204), (356, 204)], 'olv')
poly([(392, 186), (408, 184), (448, 244), (434, 248)], 'olv')
# barrel and flash suppressor
poly([(478, 172), (596, 172), (596, 189), (478, 189)], 'bar', 0.4)
poly([(590, 166), (642, 166), (642, 192), (590, 192)], 'bar')

img = np.zeros((H, W, 4), np.uint8)
for part, ramp in RAMP.items():
    cells = [(y, x) for y in range(H) for x in range(W) if lab[y, x] == part]
    raw = {(y, x): cell_lum(x, y) for y, x in cells}
    # calm the photo noise: each cell takes the median of itself and its same-part neighbours
    lums = []
    for y, x in cells:
        near = [raw.get((y + dy, x + dx)) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
        near = [v for v in near if v is not None]
        lums.append(float(np.median(near)) if near else None)
    vals = [v for v in lums if v is not None]
    lo, hi = np.percentile(vals, 5), np.percentile(vals, 95)
    for (y, x), v in zip(cells, lums):
        t = 0.5 if v is None else float(np.clip((v - lo) / max(1.0, hi - lo), 0, 1))
        i = min(len(ramp) - 1, int(t * len(ramp)))
        if y == 0 or lab[y - 1, x] != part:
            i = min(len(ramp) - 1, i + 1)
        elif y == H - 1 or lab[y + 1, x] != part:
            i = max(0, i - 1)
        img[y, x] = ramp[i] + (255,)


def cell(px, py):
    return int((px - X0) / S), int((py - Y0) / S)


def put(px, py, c):
    x, y = cell(px, py)
    if lab[y, x]:
        img[y, x] = c + (255,)



# ---- seams: a dark line where one part meets another, so the parts read apart (shading untouched elsewhere) ----
def seams():
    for y in range(H):
        for x in range(W):
            if not lab[y, x]:
                continue
            left = x > 0 and lab[y, x - 1] and seg[y, x - 1] != seg[y, x]
            up = y > 0 and lab[y - 1, x] and seg[y - 1, x] != seg[y, x]
            if left or up:
                ramp = RAMP[lab[y, x]]
                dark = ramp[0] if tuple(img[y, x, :3]) != ramp[0] else OUT
                img[y, x] = dark + (255,)


seams()

# ---- hand touches ----
B = RAMP['blk']
# ribs on the grip: every other cell along the arc a step lighter
arc = sorted({cell(px, py) for px, py in [(207, 124), (204, 116), (203, 108), (204, 100), (207, 92), (211, 85), (217, 80), (224, 78)]}, key=lambda c: -c[1])
for k, (x, y) in enumerate(arc):
    if lab[y, x]:
        img[y, x] = (B[4] if k % 2 else B[1]) + (255,)
# the long feed slot along the side, lit
for px in range(274, 360, S):
    put(px, 183, (196, 200, 208))
put(274, 183, (230, 232, 236))
# pivot bolt on the cradle, the charging knob, the data plate on the cradle
put(397, 183, (200, 204, 210))
put(338, 164, (150, 154, 162))
put(372, 197, (220, 216, 190))
put(380, 197, (220, 216, 190))
# flash suppressor slots
for px in (606, 622):
    put(px, 172, (20, 20, 26))
# the hole in the grip triangle
x, y = cell(236, 112)
if lab[y, x]:
    img[y, x] = (0, 0, 0, 0)
    lab[y, x] = ''

# ---- outline ----
pad = np.zeros((H + 2, W + 2, 4), np.uint8)
pad[1:-1, 1:-1] = img
pa = pad[..., 3] > 0
out = pad.copy()
for y in range(H + 2):
    for x in range(W + 2):
        if not pa[y, x] and any(0 <= y + dy < H + 2 and 0 <= x + dx < W + 2 and pa[y + dy, x + dx]
                                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[y, x] = OUT + (255,)
im = Image.fromarray(out, 'RGBA')
im.resize((im.width * 2, im.height * 2), Image.NEAREST).save('/home/claude/art/out/Mk19Launcher.png')

big = im.resize((im.width * 10, im.height * 10), Image.NEAREST)
ph = Image.open('/home/claude/art/ref/mk19_level.png').convert('RGBA').crop((X0 - S, Y0 - S, X0 + (W + 1) * S, Y0 + (H + 1) * S))
ph = ph.resize((big.width, int(ph.height * big.width / ph.width)), Image.LANCZOS)
sheet = Image.new('RGBA', (big.width * 2 + 30, big.height + 20), (200, 205, 210, 255))
sheet.alpha_composite(ph, (10, 10)); sheet.alpha_composite(big, (big.width + 20, 10))
sheet.save('/home/claude/art/mk19_cmp.png')
print(im.size)
