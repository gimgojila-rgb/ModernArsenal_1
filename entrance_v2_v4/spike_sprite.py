"""Spike NLOS sprite with the wing deploy, drawn cell by cell (1x) after the reference photo, exported 2x nearest.

Nose to the right. Light grey body (lit top row, darker bottom row), black seeker dome, a darker collar at the wing
roots, a trace of the blue marking. X-configuration main wings hinged at about 40 % from the tail: folded they lie flat
along the body pointing aft (as in the canister), deployed they stand out, the near pair leaning aft and the far pair
leaning forward so the X reads in side view. Four small tail fins pop out at the first deploy frame.

Frames (vertical sheet, 40x34 px each, 2 px gap): 0 folded, 1-3 wings swinging out, 4 deployed.
Writes SpikeNLOS_Deploy.png (sheet) and a zoomed preview next to this file (or to argv[1]).
"""
import math, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
W, H = 20, 17          # cells
C = 8                  # body rows C-1 (lit) and C (shade); outline rows C-2 and C+1
X0, X1 = 1, 16         # tail end .. last body cell before the dome
HX = 7                 # wing hinge column

OUTL = (20, 20, 26)
LIT, MID, SHD, DRK = (222, 222, 216), (186, 186, 180), (146, 146, 142), (110, 110, 108)
DOME, DOME_HI = (16, 16, 18), (92, 96, 104)
BLUE = (64, 104, 186)
WING, WING_HI, WING_FAR, WING_TIP = (78, 80, 86), (124, 126, 132), (52, 54, 60), (160, 162, 166)
FIN, FIN_SH = (196, 196, 190), (150, 150, 146)

# near/far blade angles per frame (degrees from +x, measured upward); 180 = folded flat, pointing aft
NEAR = (180, 152, 128, 104, 106)
FAR = (180, 160, 128, 88, 80)
FINS = (0, 1, 2, 2, 2)          # tail fin height in cells
BLADE = 7.0

def blade(px, root, ang, length, col, tipcol, up, edge=None):
    """a two-cell-wide paddle: the root line in col, a parallel line one cell toward the nose (or outward when folded)
    in the edge colour, the last cells in the tip colour"""
    a = math.radians(ang)
    sy = 1 if up else -1
    dx, dy = math.cos(a), -math.sin(a) * sy
    # root line and edge line
    for off, c0 in ((0.0, col), (1.0, edge or col)):
        rx = root[0] + math.sin(a) * off
        ry = root[1] - sy * max(0.0, -math.cos(a)) * off
        cells = []
        n = int(length * 4)
        for i in range(n + 1):
            t = i / 4
            cc = (int(round(rx + dx * t)), int(round(ry + dy * t)))
            if cc not in cells: cells.append(cc)
        for j, (x, y) in enumerate(cells):
            if 0 <= x < W and 0 <= y < H:
                px[(x, y)] = tipcol if j >= len(cells) - 2 else c0

def frame(k):
    px = {}
    # far blades first (behind the body), hinged one column forward
    blade(px, (HX + 1, C - 2), FAR[k], BLADE, WING_FAR, (78, 80, 86), True, (66, 68, 74))
    blade(px, (HX + 1, C + 1), FAR[k], BLADE, WING_FAR, (78, 80, 86), False, (66, 68, 74))
    # body
    for x in range(X0, X1 + 1):
        px[(x, C - 2)] = OUTL; px[(x, C + 1)] = OUTL
        px[(x, C - 1)] = LIT if 2 < x < X1 else MID
        px[(x, C)] = MID if 2 < x < X1 else SHD
    px[(X0 - 1, C - 1)] = OUTL; px[(X0 - 1, C)] = OUTL
    px[(X0, C - 1)] = SHD; px[(X0, C)] = DRK                    # boat-tail
    px[(HX, C - 1)] = MID; px[(HX, C)] = SHD                     # wing-root collar
    px[(HX + 2, C - 1)] = MID
    px[(11, C)] = BLUE; px[(12, C)] = BLUE; px[(14, C)] = BLUE   # the marking
    # seeker dome
    px[(X1 + 1, C - 1)] = DOME_HI; px[(X1 + 1, C)] = DOME
    px[(X1 + 1, C - 2)] = OUTL; px[(X1 + 1, C + 1)] = OUTL
    px[(X1 + 2, C - 1)] = DOME; px[(X1 + 2, C)] = DOME
    px[(X1 + 3, C - 1)] = OUTL; px[(X1 + 3, C)] = OUTL
    # tail fins
    f = FINS[k]
    for i in range(f):
        for x in (2, 3):
            px[(x - (1 if i == f - 1 and x == 3 else 0), C - 2 - i)] = FIN if i < f - 1 or x == 2 else FIN
            px[(x - (1 if i == f - 1 and x == 3 else 0), C + 1 + i)] = FIN_SH
    if f:
        px[(4, C - 2)] = FIN_SH; px[(4, C + 1)] = FIN_SH
    # near blades over the body
    blade(px, (HX, C - 2), NEAR[k], BLADE, WING, WING_TIP, True, WING_HI)
    blade(px, (HX, C + 1), NEAR[k], BLADE, WING, WING_TIP, False, WING_HI)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for (x, y), c in px.items():
        if 0 <= x < W and 0 <= y < H: im.putpixel((x, y), c + (255,))
    return im

frames = [frame(k) for k in range(len(NEAR))]
FW, FH, GAP = W * 2, H * 2, 2
sheet = Image.new('RGBA', (FW, (FH + GAP) * len(frames) - GAP), (0, 0, 0, 0))
for i, f in enumerate(frames):
    sheet.alpha_composite(f.resize((FW, FH), Image.NEAREST), (0, i * (FH + GAP)))
sheet.save(os.path.join(OUT, 'SpikeNLOS_Deploy.png'))
prev = Image.new('RGBA', ((FW + 8) * len(frames) + 8, FH + 16), (40, 44, 52, 255))
for i, f in enumerate(frames):
    prev.alpha_composite(f.resize((FW, FH), Image.NEAREST), (8 + i * (FW + 8), 8))
prev.resize((prev.width * 5, prev.height * 5), Image.NEAREST).save(os.path.join(OUT, 'SpikeNLOS_Deploy_preview.png'))
print('sheet', sheet.size)
