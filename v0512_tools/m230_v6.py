"""
M230 item sprite v5. The shapes are placed by hand on a grid measured off the user's photo (ref/m230.png; 1 cell = 7 photo
px, origin (24, 16)), like the M4A1 was; inside each part the shading comes from the photo's own brightness in that cell
(stretched per part onto its ramp), so the panel lines, the drive drum and the ribs carry over from the photo instead of
being flat fills. Then top edges lifted a step, bottom edges dropped a step, outline. 1x art, exported 2x nearest.
"""
from PIL import Image
import numpy as np

SRC = np.asarray(Image.open('/home/claude/art/ref/m230.png').convert('RGB')).astype(np.float32)
X0, Y0, S = 24, 16, 7
W, H = 66, 12
OUT = (20, 20, 26)
RAMP = {
    'blk': [(26, 27, 33), (38, 40, 48), (54, 57, 66), (74, 78, 89), (100, 105, 118), (134, 140, 154)],
    'chr': [(72, 76, 86), (112, 117, 128), (156, 161, 170), (198, 202, 208), (234, 236, 240)],
    'bar': [(40, 43, 50), (60, 64, 72), (84, 89, 98), (116, 122, 132)],
    'brz': [(70, 62, 48), (104, 94, 74), (142, 130, 104)],
}


def cell_lum(x, y):
    blk = SRC[Y0 + y * S:Y0 + (y + 1) * S, X0 + x * S:X0 + (x + 1) * S]
    m = blk.min(-1) < 240
    return blk.mean(-1)[m].mean() if m.any() else None


lab = np.full((H, W), '', dtype=object)
seg = np.zeros((H, W), int)      # which piece each cell belongs to (for the seam lines only)
_n = [0]


def fill(x0, y0, x1, y1, part, same=False):
    if not same:
        _n[0] += 1
    lab[y0:y1 + 1, x0:x1 + 1] = part
    seg[y0:y1 + 1, x0:x1 + 1] = _n[0]


# ---- layout, measured on the photo grid (cells) ----
fill(0, 2, 7, 10, 'blk'); fill(0, 1, 1, 1, 'blk', True); fill(5, 1, 6, 1, 'blk', True)        # rear drive block, its back lip, the knob
fill(8, 3, 14, 10, 'blk'); fill(8, 4, 13, 7, 'chr')                             # middle, the drive drum
fill(10, 10, 17, 11, 'blk')                                                     # lower box
fill(15, 1, 17, 11, 'blk'); fill(15, 0, 15, 0, 'blk', True)                           # tall centre plate and its bump
fill(18, 1, 23, 9, 'blk')                                                       # feeder block
fill(24, 6, 34, 8, 'blk')                                                       # recoil sleeve
for x in (25, 27, 29, 31, 33):
    lab[5, x] = 'blk'; lab[9, x] = 'blk'                                        # its ribs
    seg[5, x] = seg[9, x] = seg[7, 30]
fill(35, 5, 36, 9, 'brz'); fill(37, 5, 38, 9, 'chr')                            # ring, clamp
fill(39, 6, 55, 7, 'bar')                                                       # barrel
fill(56, 6, 57, 8, 'bar')                                                       # brake base
fill(58, 6, 63, 8, 'chr'); fill(64, 7, 65, 7, 'chr', True)                            # brake, tip

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
        # form: the top face catches the light, the underside falls away
        if y == 0 or lab[y - 1, x] != part:
            i = min(len(ramp) - 1, i + 1)
        elif y == H - 1 or lab[y + 1, x] != part:
            i = max(0, i - 1)
        img[y, x] = ramp[i] + (255,)


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

# ---- hand touches the grid can't carry ----
def put(x, y, c):
    img[y, x] = c + (255,)

put(3, 9, (226, 220, 176)); put(4, 9, (70, 64, 44)); put(5, 9, (226, 220, 176))       # data plate, rear
put(20, 7, (226, 220, 176)); put(21, 7, (70, 64, 44)); put(22, 7, (226, 220, 176))    # data plate, feeder
for x in (59, 61, 63):
    put(x, 7, (34, 36, 42))                                                             # brake slots
for x in (25, 27, 29, 31, 33):
    put(x, 6, RAMP['blk'][4])                                                           # rib crowns catch the light
# the drive drum as a cylinder: lit top, specular band, falling off underneath, darker rings
C = RAMP['chr']
for x in range(8, 14):
    put(x, 4, C[3]); put(x, 5, C[4]); put(x, 6, C[2]); put(x, 7, C[0])
for x in (10, 12):
    put(x, 4, C[1]); put(x, 5, C[3]); put(x, 6, C[1]); put(x, 7, C[0])
for y in range(4, 8):
    put(14, y, RAMP['blk'][0])
# the lighter T-shaped panel on the drive block, with its shadow
B = RAMP['blk']
for x in range(2, 7):
    put(x, 3, B[3]); put(x, 4, B[2])
for y in (5, 6, 7):
    put(3, y, B[3]); put(4, y, B[2])
for y in (5, 6, 7):
    put(5, y, B[0])
# the feeder block's top housing: two horizontal lines
for x in range(19, 24):
    put(x, 2, B[3]); put(x, 3, B[1])

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
im.resize((im.width * 2, im.height * 2), Image.NEAREST).save('/home/claude/art/out/M230ChainGun.png')

big = im.resize((im.width * 10, im.height * 10), Image.NEAREST)
ph = Image.open('/home/claude/art/ref/m230.png').convert('RGBA').crop((X0 - 7, Y0 - 7, X0 + (W + 1) * S, Y0 + (H + 1) * S))
ph = ph.resize((big.width, int(ph.height * big.width / ph.width)), Image.LANCZOS)
sheet = Image.new('RGBA', (big.width + 20, big.height + ph.height + 30), (200, 205, 210, 255))
sheet.alpha_composite(ph, (10, 10)); sheet.alpha_composite(big, (10, ph.height + 20))
sheet.save('/home/claude/art/m230_cmp.png')
print(im.size)
