"""RQ-7 Shadow side sprite, traced from the MVR side render (side.png, 2560x1440, nose to the LEFT already).
Part polygons in photo px -> 1x cells (coverage), shaded from the render's own luminance, outlined. Export 2x nearest.
Lenses are neutral; colours come from NavLightRig in code (port red / starboard green by facing)."""
import json
import numpy as np
from PIL import Image, ImageDraw

SRC = np.asarray(Image.open('/home/claude/shadow/side.png').convert('RGB')).astype(np.float32)
X0, Y0, X1, Y1 = 368, 428, 2232, 934
SX, SY = 24.5, 14.5      # ~76 px long drawn 1:1 (1 texture px per screen px): 1/5 of the Apache without losing detail
S = SX
K = 17.0 / SX
W, H = int((X1 - X0) / SX), int((Y1 - Y0) / SY)

G = [(22, 24, 28), (48, 52, 58), (74, 79, 86), (101, 107, 114), (128, 134, 140), (154, 160, 165), (179, 184, 188),
     (201, 205, 208), (222, 225, 227), (240, 242, 243)]
DARK = [(14, 15, 17), (28, 30, 34), (44, 47, 52), (62, 66, 72)]
RED = (176, 36, 30)

P = {}   # paint order: later wins
P['farwing'] = [(930, 600), (962, 566), (990, 528), (1004, 505), (1022, 490), (1090, 488), (1072, 520), (1052, 558),
                (1046, 590), (1062, 615), (1000, 612)]
P['farwingdome'] = [(996, 505), (1004, 490), (1018, 484), (1034, 486), (1044, 498), (1040, 507)]
P['tail'] = [(1832, 622), (1898, 480), (1915, 468), (2005, 466), (2020, 480), (2175, 612), (2175, 624)]
P['tailant'] = [(1970, 468), (1972, 440), (1982, 440), (1984, 468)]
P['topbox'] = [(478, 632), (484, 588), (505, 584), (530, 590), (532, 622)]
P['topfair'] = [(1100, 612), (1108, 582), (1228, 582), (1232, 612)]
P['body'] = [(420, 690), (430, 668), (452, 648), (482, 632), (522, 620), (562, 611), (600, 605), (700, 600), (800, 598),
             (900, 596), (1000, 596), (1100, 604), (1200, 612), (1262, 614), (1262, 690), (1200, 698), (1100, 704),
             (1000, 712), (900, 716), (800, 718), (700, 719), (600, 719), (520, 718), (470, 715), (440, 708), (424, 700)]
P['boom'] = [(1200, 622), (2150, 624), (2200, 632), (2216, 640), (2200, 648), (2150, 656), (1200, 660)]
P['engine'] = [(1262, 582), (1348, 582), (1350, 684), (1262, 686)]
P['ball'] = [(778, 720), (800, 706), (852, 700), (905, 706), (926, 730), (920, 770), (895, 795), (852, 802), (810, 795),
             (784, 770)]
P['gearplate'] = [(1000, 700), (1062, 700), (1070, 790), (1040, 818), (1012, 790)]
P['wheelfar'] = [(1044, 780), (1062, 742), (1100, 736), (1130, 760), (1130, 800), (1100, 822), (1062, 818)]
P['wheel'] = [(1018, 868), (1030, 826), (1075, 808), (1120, 826), (1134, 868), (1120, 910), (1075, 928), (1030, 910)]
P['nosestrut'] = [(468, 712), (482, 716), (446, 742), (440, 776), (470, 812), (492, 836), (476, 846), (452, 820),
                  (426, 782), (428, 740)]
P['nosewheel'] = [(444, 860), (452, 832), (480, 822), (508, 832), (518, 860), (508, 886), (480, 896), (452, 886)]
P['nearwing'] = [(736, 668), (752, 638), (790, 622), (860, 614), (1000, 612), (1100, 628), (1200, 652), (1300, 678),
                 (1412, 704), (1300, 704), (1200, 702), (1100, 703), (1000, 708), (880, 712), (790, 706), (748, 692)]
P['pitot'] = [(384, 686), (422, 686), (422, 694), (384, 694)]

THIN = ('pitot', 'tailant', 'nosestrut')


def cells(poly):
    im = Image.new('L', (int(W * SX), int(H * SY)), 0)
    ImageDraw.Draw(im).polygon([(x - X0, y - Y0) for x, y in poly], fill=255)
    m = np.asarray(im.resize((W * 10, H * 10), Image.BOX)).astype(np.float32) / 255
    return m.reshape(H, 10, W, 10).mean(axis=(1, 3))


_L = Image.fromarray(SRC[Y0:Y0 + int(H * SY), X0:X0 + int(W * SX)].mean(-1).astype(np.uint8)).resize((W, H), Image.BOX)
lum = np.asarray(_L).astype(np.float32)
label = np.full((H, W), '', dtype=object)
for n, poly in P.items():
    c = cells(poly)
    label[c >= (0.22 if n in THIN else 0.45)] = n

img = np.zeros((H, W, 4), np.uint8)


def put(y, x, col):
    img[y, x] = (*col, 255)


GREY = ('body', 'farwing', 'farwingdome', 'tail', 'topbox', 'topfair', 'boom', 'gearplate', 'nearwing', 'pitot',
        'tailant', 'nosestrut')
sk = np.isin(label, GREY)
lo, hi = np.percentile(lum[sk], 4), np.percentile(lum[sk], 97)
for y in range(H):
    for x in range(W):
        n = label[y, x]
        if not n:
            continue
        if n in GREY:
            t = np.clip((lum[y, x] - lo) / (hi - lo), 0, 1)
            i = int(round(2 + t * 6.4))
            if n in ('farwing', 'farwingdome'):
                i = max(2, i - 1)
            put(y, x, G[min(8, i)])
        elif n == 'engine':
            put(y, x, DARK[2])
        elif n == 'ball':
            t = np.clip((lum[y, x] - 60) / 150, 0, 1)
            put(y, x, G[int(2 + t * 5)])
        elif n in ('wheel', 'wheelfar', 'nosewheel'):
            put(y, x, DARK[1] if n != 'wheelfar' else DARK[0])


def cx(px): return int((px - X0) / SX)
def cy(py): return int((py - Y0) / SY)


# wheel hubs, engine cooling fins, boom red bands
for (px, py) in [(1075, 868), (480, 860)]:
    put(cy(py), cx(px), G[5])
for x in range(cx(1266), cx(1346) + 1):
    for y in range(cy(584), cy(682) + 1):
        if label[y, x] == 'engine':
            put(y, x, DARK[3] if (x + y) % 2 == 0 else DARK[1])
# sensor ball window (looking forward-down)
put(cy(772), cx(812), (79, 107, 120)); put(cy(760), cx(812), (127, 156, 168))

# outline
a = img[..., 3] > 0
out = img.copy()
for y in range(H):
    for x in range(W):
        if not a[y, x] or label[y, x] in THIN:
            continue
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yy, xx = y + dy, x + dx
            if not (0 <= yy < H and 0 <= xx < W) or not a[yy, xx]:
                out[y, x, :3] = G[0]
                break
img = out
# boom: a clean round rod (the trace alone is all outline at this size)
bx0, bx1 = cx(1236), cx(2212)
by0 = cy(624)
for x in range(bx0, bx1 + 1):
    tip = x >= bx1 - 2
    rows = [(by0, G[0]), (by0 + 1, G[8]), (by0 + 2, G[5]), (by0 + 3, G[0])] if not tip else [(by0 + 1, G[0]), (by0 + 2, G[0])]
    if x == bx1:
        rows = [(by0 + 1, G[0]), (by0 + 2, G[0])]
    for (y, col) in rows:
        if label[y, x] in ('boom', '') or label[y, x] == 'tail' and y >= by0:
            put(y, x, col)
for bx in (1305, 1595):
    x = cx(bx)
    put(by0 + 1, x, (214, 64, 54)); put(by0 + 2, x, RED)
# near wing: lit upper face, darker underside, clean outline
nw = [(y, x) for y in range(H) for x in range(W) if label[y, x] == 'nearwing']
for (y, x) in nw:
    up = label[y - 1, x] == 'nearwing'; dn = y + 1 < H and label[y + 1, x] == 'nearwing'
    lf = label[y, x - 1] == 'nearwing'; rt = x + 1 < W and label[y, x + 1] == 'nearwing'
    if not (up and dn and lf and rt):
        put(y, x, G[0])
    elif not (label[y - 2, x] == 'nearwing'):
        put(y, x, G[8])
    else:
        put(y, x, G[5] if label[y + 2, x] == 'nearwing' else G[3])
# near wing sits in front of the body: its upper edge gets a seam line

# wheels and sensor ball are drawn round (the squat sampling would make them ovals)
def disc(pcx, pcy, r, fill, rim, hub=None):
    ccx, ccy = (pcx - X0) / SX, (pcy - Y0) / SY
    for y in range(H):
        for x in range(W):
            d = ((x + 0.5 - ccx) ** 2 + (y + 0.5 - ccy) ** 2) ** 0.5
            if d <= r:
                put(y, x, rim if d > r - 1 else fill)
    if hub:
        put(int(ccy), int(ccx), hub)
for n in ('wheel', 'wheelfar', 'nosewheel', 'ball'):
    for y in range(H):
        for x in range(W):
            if label[y, x] == n:
                img[y, x] = 0
disc(1085, 790, 3.0 * K, DARK[0], DARK[0])
disc(1075, 868, 3.6 * K, DARK[1], G[0], G[5])
disc(480, 860, 2.4 * K, DARK[1], G[0], G[5])
disc(852, 752, 3.1 * K, G[5], G[0])
ccx, ccy = (852 - X0) / SX, (752 - Y0) / SY
put(int(ccy) + 1, int(ccx) - 2, (79, 107, 120)); put(int(ccy), int(ccx) - 2, (127, 156, 168)); put(int(ccy) - 2, int(ccx) - 1, G[8])

# ---- light fittings (1x cells, facing left) ----
FIT = {
    'near_wingtip': (cx(760), cy(664)),     # the red dome on the wingtip pod in the render: neutral lens here
    'far_wingtip': (cx(1016), cy(496)),     # top of the far wing
    'tail_white': (cx(2212), cy(640)),      # boom tail tip
    'beacon_top': (cx(700), cy(600)),
    'beacon_bottom': (cx(650), cy(719)),
    'strobe': [(cx(760), cy(664)), (cx(1016), cy(496)), (cx(2212), cy(640))],
}
LENS = (228, 232, 234)
for k in ('near_wingtip', 'far_wingtip', 'tail_white'):
    x, y = FIT[k]; put(y, x, LENS)
for k in ('beacon_top', 'beacon_bottom'):
    x, y = FIT[k]; put(y, x, (200, 60, 50))
# near wing pod: the lens housing around the nav light
x, y = FIT['near_wingtip']
put(y, x + 1, G[7])

# formation strips: fuselage side, boom, tail
SLIME = [(x, cy(655)) for x in range(cx(560), cx(700))] + [(x, cy(642)) for x in range(cx(1700), cx(1800))] + \
        [(cx(2060) + i, cy(530) + i) for i in range(3)]
slime = np.zeros_like(img)
for (x, y) in SLIME:
    if img[y, x, 3]:
        put(y, x, (176, 198, 160)); slime[y, x] = (255, 255, 255, 255)

# "ARMY" decal on the fuselage (per-facing layers, never mirrored)
FONT = {'A': ['111', '101', '111', '101', '101'], 'R': ['110', '101', '110', '101', '101'],
        'M': ['101', '111', '111', '101', '101'], 'Y': ['101', '101', '010', '010', '010']}
marksL = np.zeros_like(img); marksR = np.zeros_like(img)
tx0, ty = cx(850), cy(634)
def stamp_text(dst, x0, lab):
    x = x0
    for ch in 'ARMY':
        for r in range(5):
            for c in range(3):
                if FONT[ch][r][c] == '1' and lab[ty + r, x + c] == 'body':
                    dst[ty + r, x + c] = (*G[1], 255)
        x += 4
stamp_text(marksL, tx0, label)
stamp_text(marksR, W - tx0 - 15, label[:, ::-1])

OUT = '/home/claude/shadow/out_fine/'
import os; os.makedirs(OUT, exist_ok=True)
def save2(arr, name): Image.fromarray(arr).save(OUT + name)   # 1:1
Image.fromarray(img).save(OUT + 'shadow_1x.png')
save2(img, 'ShadowUAV.png'); save2(slime, 'ShadowUAV_Slime.png')
def off2(p): return [round(p[0] + 0.5 - W / 2, 1), round(p[1] + 0.5 - H / 2, 1)]
PROP = (cx(1352), cy(632))
json.dump({k: ([off2(p) for p in v] if isinstance(v, list) else off2(v)) for k, v in FIT.items()} | {'prop_axis': off2(PROP), 'sensor': off2((cx(852), cy(752)))},
          open(OUT + 'ShadowUAV_lights.json', 'w'), indent=1)
print('cells', W, H, FIT, 'prop', PROP)

# 2-blade pusher prop, edge-on: 6 frames + blur
import math
R = 5
FH = 2 * R + 3
sheet = np.zeros((FH * 6 + 2 * 5, 3, 4), np.uint8)
for f in range(6):
    c = f * (FH + 2) + FH // 2
    for k in range(2):
        ext = R * math.sin(math.radians(f * 30 + k * 180 + 15))
        a0, a1 = sorted((0, int(round(ext))))
        for yy in range(a0, a1 + 1):
            sheet[c + yy, 1] = (*(G[4] if abs(yy) >= abs(int(round(ext))) - 1 and abs(ext) > 2 else DARK[2]), 255)
    sheet[c - 1:c + 2, 0:3] = (*DARK[1], 255)
Image.fromarray(sheet).save(OUT + 'ShadowUAV_Prop.png')
blur = np.zeros((FH, 5, 4), np.uint8)
for yy in range(FH):
    d = abs(yy - FH // 2) / (R + 1)
    if d <= 1:
        al = int(90 * (1 - d * d) + 25)
        blur[yy, 1:4] = (*G[3], al); blur[yy, 2] = (*G[2], min(255, al + 30))
Image.fromarray(blur).save(OUT + 'ShadowUAV_PropBlur.png')
