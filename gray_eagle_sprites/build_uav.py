"""MQ-1C Gray Eagle side sprite, traced from the reference photo (side.png, nose to the right).
Polygons in photo px -> part masks -> downsampled to 1x cells (majority), shaded from the photo's own luminance,
quantised to a light-grey ramp, outlined, then flipped to face left (NPC textures face left). Export 2x nearest."""
import numpy as np
from PIL import Image, ImageDraw

SRC = Image.open('/home/claude/uav/side.png').convert('RGB')
PH = np.asarray(SRC).astype(np.float32)
X0, Y0, X1, Y1 = 40, 98, 548, 243
S = 5.0                                   # photo px per cell
W, H = int((X1 - X0) / S), int((Y1 - Y0) / S)

# light-grey ramp (Army Gray Eagle grey), outline first
G = [(22, 24, 28), (48, 52, 58), (74, 79, 86), (101, 107, 114), (128, 134, 140), (154, 160, 165), (179, 184, 188),
     (201, 205, 208), (222, 225, 227), (240, 242, 243)]
DARK = [(14, 15, 17), (30, 32, 36), (46, 49, 54), (64, 68, 74)]          # gear, sensor, spinner shadow
HF = {'body': (86, 92, 70), 'dk': (52, 56, 42), 'lt': (118, 124, 96), 'band': (214, 180, 64)}  # Hellfire olive + yellow band

# ---- parts (photo coords) : order = paint order, later wins ----
P = {}
P['fartail'] = [(178, 149), (182, 120), (186, 111), (192, 108), (198, 112), (203, 125), (207, 140), (206, 149)]
P['fartailbar'] = [(152, 104), (194, 103), (195, 106), (153, 107)]
P['farwing'] = [(258, 150), (261, 124), (264, 114), (271, 109), (280, 111), (285, 119), (288, 136), (291, 150)]
P['farwingbar'] = [(251, 109), (273, 107), (274, 111), (252, 113)]
P['fargear'] = [(157, 178), (168, 178), (168, 200), (158, 200)]
P['fartaildown'] = [(129, 176), (149, 176), (151, 222), (133, 224), (129, 214)]
P['maingear'] = [(137, 178), (150, 178), (151, 229), (138, 229)]
P['body'] = [(53, 153), (58, 147), (66, 143), (76, 141), (90, 138), (110, 134), (140, 131), (170, 129), (176, 127),
             (196, 127), (204, 131), (208, 138), (208, 147), (215, 150), (260, 150), (300, 150), (320, 148), (345, 142),
             (370, 137), (400, 134), (440, 133), (465, 138), (485, 148), (500, 162), (508, 175), (510, 183),
             (505, 188), (490, 195), (470, 199), (443, 200), (420, 198), (390, 194), (360, 190), (330, 188), (300, 187),
             (270, 186), (240, 184), (210, 181), (180, 179), (150, 178), (120, 175), (95, 170), (78, 165), (66, 161),
             (56, 158)]
P['spinner'] = [(53, 153), (58, 147), (66, 143), (76, 141), (78, 152), (76, 164), (66, 161), (56, 158)]
P['neartail'] = [(96, 168), (127, 172), (128, 196), (125, 234), (116, 238), (88, 236), (80, 230), (82, 200)]
P['nosegear'] = [(371, 188), (378, 188), (378, 208), (371, 208)]
P['nosewheel'] = [(355, 209), (380, 208), (383, 216), (378, 225), (358, 225), (353, 217)]
P['ball'] = [(437, 198), (456, 198), (459, 205), (454, 213), (440, 213), (435, 205)]
P['pylon'] = [(272, 180), (293, 180), (292, 194), (273, 194)]
P['hellfire'] = [(236, 196), (320, 195), (333, 199), (333, 206), (320, 210), (236, 209)]
P['nearwing'] = [(215, 157), (300, 157), (309, 170), (310, 194), (300, 199), (288, 197), (262, 186), (240, 176), (224, 167)]
P['satcom'] = [(322, 150), (324, 143), (330, 143), (332, 150)]
P['blade'] = [(166, 131), (168, 124), (171, 124), (172, 131)]
P['pitot'] = [(508, 181), (541, 177), (541, 179), (508, 184)]


def rast(poly, scale=1):
    im = Image.new('L', (int((X1 - X0) * scale), int((Y1 - Y0) * scale)), 0)
    ImageDraw.Draw(im).polygon([((x - X0) * scale, (y - Y0) * scale) for x, y in poly], fill=255)
    return np.asarray(im).astype(np.float32) / 255


def cells(m):
    """fraction of each cell covered"""
    h, w = int(H * S), int(W * S)
    m = m[:h, :w]
    return m.reshape(H, int(S), W, int(S)).mean(axis=(1, 3))


lum_full = PH[Y0:Y0 + int(H * S), X0:X0 + int(W * S)].mean(-1)
lum = lum_full.reshape(H, int(S), W, int(S)).mean(axis=(1, 3))

label = np.full((H, W), '', dtype=object)
cover = {}
for name, poly in P.items():
    c = cells(rast(poly))
    cover[name] = c
    thin = name in ('pitot', 'fartailbar', 'farwingbar', 'blade', 'satcom', 'nosegear')
    thr = 0.25 if thin else 0.45
    label[c >= thr] = name

img = np.zeros((H, W, 4), np.uint8)


def put(y, x, col):
    img[y, x] = (*col, 255)


# grey skin: shade from the photo's luminance, stretched per part so every part uses the ramp well
GREYPARTS = ('body', 'fartail', 'fartailbar', 'farwing', 'farwingbar', 'fartaildown', 'neartail', 'nearwing', 'pylon',
             'satcom', 'blade', 'nosewheel', 'pitot')
sk = np.isin(label, GREYPARTS)
lo, hi = np.percentile(lum[sk], 4), np.percentile(lum[sk], 97)
for y in range(H):
    for x in range(W):
        n = label[y, x]
        if not n:
            continue
        if n in GREYPARTS:
            t = np.clip((lum[y, x] - lo) / (hi - lo), 0, 1)
            i = int(round(2 + t * 6.4))          # 2..8, 9 kept for speculars
            if n in ('fartail', 'fartailbar', 'farwing', 'farwingbar', 'fartaildown'):
                i = max(2, i - 1)               # far side sits a notch darker
            put(y, x, G[min(8, i)])
        elif n == 'spinner':
            t = np.clip((lum[y, x] - 40) / 160, 0, 1)
            put(y, x, G[int(1 + t * 4)])
        elif n in ('maingear', 'fargear', 'nosegear'):
            put(y, x, DARK[1] if n != 'nosegear' else G[5])
        elif n == 'ball':
            put(y, x, DARK[2])
        elif n == 'hellfire':
            put(y, x, HF['body'])

# ---- hand touches (cell coords before the flip; nose is to the right here) ----
def cx(px): return int((px - X0) / S)
def cy(py): return int((py - Y0) / S)

# sensor ball: glass window facing forward-down, a glint
for (x, y, col) in [(cx(452), cy(205), (79, 107, 120)), (cx(452), cy(207), (127, 156, 168)), (cx(447), cy(203), (246, 253, 255))]:
    if img[y, x, 3]:
        put(y, x, col)
# Hellfire: nose seeker, olive body with the yellow band, dark fins
hy = cy(203)
for x in range(cx(236), cx(333) + 1):
    for y in range(cy(196), cy(209) + 1):
        if label[y, x] == 'hellfire':
            put(y, x, HF['lt'] if y == cy(197) else (HF['dk'] if y >= cy(206) else HF['body']))
for x in (cx(267), cx(303)):
    for y in range(cy(196), cy(209) + 1):
        if label[y, x] == 'hellfire':
            put(y, x, HF['band'])
xs = [x for x in range(W) if (label[:, x] == 'hellfire').any()]
if xs:
    for y in range(H):
        if label[y, max(xs)] == 'hellfire':
            put(y, max(xs), DARK[2])          # seeker dome
# nose landing gear wheel fairing darker at the bottom, main gear wheel
for x in range(W):
    for y in range(H):
        if label[y, x] == 'nosewheel' and y >= cy(221):
            put(y, x, G[3])

# ---- outline: any opaque cell touching transparency or a different part gets darkened at the silhouette ----
a = img[..., 3] > 0
out = img.copy()
for y in range(H):
    for x in range(W):
        if not a[y, x]:
            continue
        edge = False
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            yy, xx = y + dy, x + dx
            if not (0 <= yy < H and 0 <= xx < W) or not a[yy, xx]:
                edge = True
        if edge and label[y, x] not in ('pitot', 'fartailbar', 'farwingbar', 'blade', 'satcom', 'nosegear', 'maingear', 'fargear'):
            out[y, x, :3] = G[0] if label[y, x] != 'hellfire' else (26, 28, 21)
img = out
# part seams: where a near part overlaps the body (near wing root, near tail root), draw its edge
for y in range(1, H - 1):
    for x in range(1, W - 1):
        n = label[y, x]
        if n in ('nearwing', 'neartail', 'pylon', 'hellfire') and img[y, x, 3]:
            for dy, dx in ((-1, 0), (0, -1), (0, 1)):
                m = label[y + dy, x + dx]
                if m and m != n and m not in ('nearwing', 'neartail', 'pylon', 'hellfire'):
                    img[y, x, :3] = G[1]
                    break

# ---- lights (photo coords): near wingtip red, far wingtip green, tail white, anti-collision red on the SATCOM hump ----
LIGHTS = {'red': ((305, 195), (228, 232, 234)), 'white': ((84, 226), (250, 250, 240)),
          'beacon': ((327, 144), (230, 40, 30))}
for k, ((px, py), col) in LIGHTS.items():
    x, y = cx(px), cy(py)
    put(y, x, col)

# prop axis (for the prop texture), in cells before the flip
PROP_AXIS = (cx(77), cy(152))

# ---- flip to face left ----
img = img[:, ::-1].copy()
label = label[:, ::-1]


def fx(x): return W - 1 - x


# "ARMY" on the aft fuselage side, dark, after the flip so it reads the right way
FONT = {'A': ['111', '101', '111', '101', '101'], 'R': ['110', '101', '110', '101', '101'],
        'M': ['101', '111', '111', '101', '101'], 'Y': ['101', '101', '010', '010', '010']}
# "ARMY" lives on its own decal layers so it reads the right way on both sides (the body texture gets mirrored)
tx0, ty = fx(cx(203)), cy(152) + 1
marksL = np.zeros_like(img); marksR = np.zeros_like(img)
def stamp_text(dst, x0, lab):
    x = x0
    for ch in 'ARMY':
        g = FONT[ch]
        for r in range(5):
            for c in range(3):
                if g[r][c] == '1' and lab[ty + r, x + c] == 'body':
                    dst[ty + r, x + c] = (*G[1], 255)
        x += 4
stamp_text(marksL, tx0, label)
span = 4 * 4 - 1
stamp_text(marksR, W - tx0 - span, label[:, ::-1])
Image.fromarray(marksL).resize((W * 2, H * 2), Image.NEAREST).save('/home/claude/uav/out/GrayEagle_MarksL.png')
Image.fromarray(marksR).resize((W * 2, H * 2), Image.NEAREST).save('/home/claude/uav/out/GrayEagle_MarksR.png')

lights = {k: (fx(cx(p[0])), cy(p[1])) for k, (p, _) in LIGHTS.items()}
# ---- Hellfire, pylon and near wing redrawn by hand after the flip (the trace alone reads as a black bar / a hook) ----
HL, HR_ = fx(cx(333)), fx(cx(236))
for y in range(17, 26):                                    # clear the traced missile
    for x in range(HL - 2, HR_ + 3):
        if label[y, x] == 'hellfire':
            img[y, x] = 0
# the mod's own Hellfire (ApacheHellfire.png, the Longbow L), turned nose-left, with an IR/laser seeker instead of the radome
HFS = np.asarray(Image.open('/mnt/user-data/uploads/ModernArsenal/Content/Projectiles/Apache/ApacheHellfire.png').convert('RGBA'))[::2, ::2]
HFS = np.ascontiguousarray(HFS.transpose(1, 0, 2)).copy()   # nose left, lit side up
SEEK = {3: [(150, 178, 190), (212, 230, 235), (127, 156, 168), (100, 128, 142)],   # rows 3..5, cols 1..4 of the nose
        4: [(79, 107, 120), (60, 84, 98), (127, 156, 168), (79, 107, 120)],
        5: [(36, 48, 58), (46, 62, 74), (36, 48, 58), (30, 40, 48)]}
for r, cols in SEEK.items():
    for i, col in enumerate(cols):
        if HFS[r, 1 + i, 3]:
            HFS[r, 1 + i, :3] = col
MX0, MY0 = 38, 17
for r in range(HFS.shape[0]):
    for c in range(HFS.shape[1]):
        if HFS[r, c, 3]:
            img[MY0 + r, MX0 + c] = HFS[r, c]
# pylon
for y in (17, 18):
    for x in range(fx(cx(292)), fx(cx(274)) + 1):
        img[y, x] = (*G[3], 255) if y == 18 else (*G[4], 255)
# near wing: underside mid-grey, leading edge catching light, tip light kept
nw = [(y, x) for y in range(H) for x in range(W) if label[y, x] == 'nearwing']
for (y, x) in nw:
    left = x - 1 >= 0 and label[y, x - 1] == 'nearwing'
    up = y - 1 >= 0 and label[y - 1, x] == 'nearwing'
    down = y + 1 < H and label[y + 1, x] == 'nearwing'
    right = x + 1 < W and label[y, x + 1] == 'nearwing'
    if not left or not down:
        img[y, x] = (*G[0], 255)
    elif not right and not up:
        img[y, x] = (*G[0], 255)
    elif x - 2 >= 0 and label[y, x - 2] != 'nearwing':
        img[y, x] = (*G[7], 255)                           # leading edge
    else:
        img[y, x] = (*G[4 if y < 15 else 3], 255)
for k, ((px, py), col) in LIGHTS.items():
    img[lights[k][1], lights[k][0]] = (*col, 255)
# ---- light fittings (1x cells, facing left). Lenses are neutral so a mirrored sprite never shows the wrong colour;
# the colour comes from the glow drawn in code (NavLights): port red / starboard green by facing ----
FIT = {
    'near_wingtip': (47, 19),      # nav light on the visible wingtip: red when facing left, green when facing right
    'far_wingtip': (55, 2),        # the far wingtip peeking over the fuselage: the other colour, dimmer
    'tail_white': (92, 25),        # steady white on the tail's trailing edge
    'beacon_top': (43, 9),         # red anti-collision beacons, top and belly centreline
    'beacon_bottom': (38, 17),
    'strobe': [(47, 19), (55, 2), (92, 25)],   # white high-intensity strobes (wingtips, tail)
}
LENS = (228, 232, 234)
for k in ('near_wingtip', 'far_wingtip', 'tail_white'):
    x, y = FIT[k]
    img[y, x] = (*LENS, 255)
for k in ('beacon_top', 'beacon_bottom'):
    x, y = FIT[k]
    img[y, x] = (200, 60, 50, 255)
# slime (formation) strips: pale electroluminescent panels, off-state tint; glow comes from GrayEagle_Slime.png
SLIME = [(x, 14) for x in range(13, 19)] + [(85, y) for y in range(18, 23)] + [(x, 12) for x in range(88, 92)]
slime = np.zeros_like(img)
for (x, y) in SLIME:
    if img[y, x, 3]:
        img[y, x] = (176, 198, 160, 255)
        slime[y, x] = (255, 255, 255, 255)
Image.fromarray(slime).resize((W * 2, H * 2), Image.NEAREST).save('/home/claude/uav/out/GrayEagle_Slime.png')
import json
def off2(p):   # 1x cell -> 2x px offset from the texture centre (cell centre)
    return [p[0] * 2 + 1 - W, p[1] * 2 + 1 - H]
json.dump({k: ([off2(p) for p in v] if isinstance(v, list) else off2(v)) for k, v in FIT.items()} | {'prop_axis': off2(axis if 'axis' in dir() else (93, 10))},
          open('/home/claude/uav/out/GrayEagle_lights.json', 'w'), indent=1)
Image.fromarray(img).save('/home/claude/uav/out/gray_eagle_1x.png')
Image.fromarray(img).resize((W * 2, H * 2), Image.NEAREST).save('/home/claude/uav/out/GrayEagle.png')
axis = (fx(PROP_AXIS[0]), PROP_AXIS[1])
lights = {k: (fx(cx(p[0])), cy(p[1])) for k, (p, _) in LIGHTS.items()}
print('cells', W, H, 'prop axis', axis, 'lights', lights)

# ---- prop: 3 blades seen edge-on (vertical), 6 frames; plus a blur disc ----
R = 12
FW, FH = 3, 2 * R + 3
sheet = np.zeros((FH * 6 + 2 * 5, FW, 4), np.uint8)
import math
for f in range(6):
    y0 = f * (FH + 2)
    c = y0 + FH // 2
    for k in range(3):
        ang = math.radians(f * 20 + k * 120)
        ext = R * math.sin(ang)
        a0, a1 = sorted((0, int(round(ext))))
        for y in range(a0, a1 + 1):
            tip = abs(y) >= abs(int(round(ext))) - 1 and abs(ext) > 3
            sheet[c + y, 1] = (*(G[4] if tip else G[1]), 255)
    sheet[c - 1:c + 2, 0:3] = (*DARK[1], 255)
Image.fromarray(sheet).resize((FW * 2, sheet.shape[0] * 2), Image.NEAREST).save('/home/claude/uav/out/GrayEagle_Prop.png')
blur = np.zeros((FH, 5, 4), np.uint8)
for y in range(FH):
    d = abs(y - FH // 2) / (R + 1)
    if d <= 1:
        al = int(90 * (1 - d * d) + 25)
        blur[y, 1:4] = (*G[3], al)
        blur[y, 2] = (*G[2], min(255, al + 30))
Image.fromarray(blur).resize((10, FH * 2), Image.NEAREST).save('/home/claude/uav/out/GrayEagle_PropBlur.png')
