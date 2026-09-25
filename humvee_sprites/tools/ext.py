import numpy as np
from pix import *

def bezier(p0, p1, p2, n=200):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t ** 2 * np.array(p2)

def curve_cells(pts):
    out = []
    for x, y in pts:
        c = (int(np.floor(x)), int(np.floor(y)))
        if not out or out[-1] != c:
            out.append(c)
    # thin: drop cells that make L-corners (keep 1px line)
    thin = [out[0]]
    for i in range(1, len(out) - 1):
        a, b, c = thin[-1], out[i], out[i + 1]
        if abs(a[0] - c[0]) <= 1 and abs(a[1] - c[1]) <= 1:
            continue
        thin.append(b)
    thin.append(out[-1])
    return thin

def rivets(L, pts, tone=3, hl=None):
    for x, y in pts:
        L.P(x, y, 'tan', tone)
        if hl is not None:
            L.P(x, y - 1, 'tan', hl)

# ------------------------------------------------------------------ geometry
REAR_ARCH = [(37.6, 41.5), (37.0, 40.2), (36.0, 37.4), (34.6, 34.5), (32.6, 32.0), (30.2, 30.3),
             (27.0, 29.5), (19.5, 29.5), (17.0, 30.2), (15.4, 31.8), (14.7, 34.2)]
FRONT_ARCH = [(99.3, 34.8), (98.8, 33.4), (97.8, 31.8), (96.0, 30.6), (93.0, 30.0), (86.0, 30.0),
              (83.5, 30.8), (81.7, 32.5), (80.5, 34.6), (79.7, 37.0)]
BODY = ([(7.6, 21.0), (8.4, 20.3), (10.0, 20.1), (37.0, 12.1), (37.6, 11.5), (74.5, 11.5), (74.5, 25.5),
         (76.5, 25.5), (76.5, 37.0), (79.7, 37.0), (79.2, 39.0), (78.9, 41.5)] + REAR_ARCH + [(7.6, 34.2)])
HOOD = ([(74.5, 24.1), (80.0, 24.3), (84.0, 24.7), (90.0, 25.5), (95.0, 26.6), (98.4, 27.9), (100.4, 29.0),
         (101.1, 30.0), (101.1, 34.7)] + FRONT_ARCH + [(76.5, 37.0), (76.5, 25.5), (74.5, 25.5)])
DOOR_R = [(37.3, 12.5), (53.6, 12.5), (53.6, 37.6), (37.4, 37.6), (36.5, 33.5), (36.2, 26.0), (36.6, 18.0)]
DOOR_F = [(54.4, 12.5), (72.9, 12.5), (72.9, 37.6), (54.4, 37.6)]
WHEEL_R = (22.5, 41.5)
WHEEL_F = (90.5, 41.5)
WR = 10.5


def arch_y(x, arch):
    xs = [p[0] for p in arch]; ys = [p[1] for p in arch]
    order = np.argsort(xs)
    return np.interp(x, np.array(xs)[order], np.array(ys)[order])

# ------------------------------------------------------------------ top-plane geometry (slightly raised camera)
TP = 2.0                                             # roof / deck plane depth in cells
def slope_near(x):  return 20.1 - (x - 10.0) * 0.2963   # cargo deck near edge
HOOD_NEAR_X = [74.5, 80.0, 86.0, 92.0, 97.0, 100.5, 102.6, 103.8]
HOOD_NEAR_Y = [24.0, 24.1, 24.3, 24.6, 25.1, 25.9, 27.0, 28.6]
HOOD_FAR_Y  = [21.7, 21.8, 22.0, 22.3, 22.8, 23.6, 24.8, 26.8]
def hood_near(x): return np.interp(x, HOOD_NEAR_X, HOOD_NEAR_Y)
def hood_far(x):  return np.interp(x, HOOD_NEAR_X, HOOD_FAR_Y)

BODY2 = ([(7.6, 21.0), (8.4, 20.3), (9.2, 18.4), (10.2, 18.1), (37.0, 10.1), (37.6, 9.5), (74.5, 9.5), (74.5, 25.5),
          (76.5, 25.5), (76.5, 37.0), (79.7, 37.0), (79.2, 39.0), (78.9, 41.5)] + REAR_ARCH + [(7.6, 34.2)])
HOOD2 = ([(74.5, 21.7)] + [(x, y) for x, y in zip(HOOD_NEAR_X[1:], HOOD_FAR_Y[1:])] + [(103.8, 34.7), (101.0, 34.9)]
         + FRONT_ARCH + [(76.5, 37.0), (76.5, 25.5), (74.5, 25.5)])

# ------------------------------------------------------------------ BODY
def make_body():
    L = Layer('Body')
    sil = L.poly(BODY2, 'tan', 5)
    # side faces: gentle top-to-bottom falloff
    L.recolor(sil & mask_ref(lambda x, y: (y > 27.5)), tone=4)
    L.recolor(sil & mask_ref(lambda x, y: (y > 32.5) & (x < 37)), tone=3)
    # rear face (turning away)
    L.recolor(mask_ref(lambda x, y: (x < 8.6)), tone=3)
    L.recolor(mask_ref(lambda x, y: (x >= 8.6) & (x < 9.6) & (y > 21)), tone=4)
    # cargo deck plane + roof plane (bright), near edges hottest
    deck = mask_ref(lambda x, y: (x > 8.4) & (x < 37.6) & (y < slope_near(x)) & (y > slope_near(x) - TP - 0.3))
    L.recolor(deck & sil, tone=6)
    L.recolor(mask_ref(lambda x, y: (x > 8.4) & (x < 37.6) & (y < slope_near(x)) & (y > slope_near(x) - 1.0)) & sil, tone=7)
    roof = mask_ref(lambda x, y: (x > 37.0) & (x < 74.5) & (y > 9.5) & (y < 11.5))
    L.recolor(roof, tone=6)
    L.recolor(mask_ref(lambda x, y: (x > 37.0) & (x < 74.5) & (y > 10.5) & (y < 11.5)), tone=7)
    # tie-down rings / seams on the deck
    for x in (14.0, 22.0, 30.0):
        L.P(x, slope_near(x) - 1.4, 'tan', 4)
    # side face just below the deck edge: a lit bevel then a crease
    L.recolor(mask_ref(lambda x, y: (x > 9) & (x < 37.5) & (y >= slope_near(x)) & (y < slope_near(x) + 1.0)) & sil, tone=6)
    # roof rail below roof plane
    L.recolor(mask_ref(lambda x, y: (x > 37.0) & (x < 74.5) & (y > 11.5) & (y < 12.5)), tone=5)
    L.recolor(mask_ref(lambda x, y: (x > 37.5) & (x < 70.0) & (y > 11.5) & (y < 12.5)), tone=4)
    # rocker / running board ledge
    L.recolor(mask_ref(lambda x, y: (x > 37) & (x < 79.5) & (y > 37.6) & (y < 41.5)), tone=4)
    L.recolor(mask_ref(lambda x, y: (x > 37) & (x < 79.5) & (y > 37.6) & (y < 38.6)), tone=7)
    L.recolor(mask_ref(lambda x, y: (x > 37) & (x < 79.5) & (y > 38.6) & (y < 39.6)), tone=5)
    L.recolor(mask_ref(lambda x, y: (x > 37) & (x < 79.5) & (y > 40.4) & (y < 41.5)), tone=3)
    L.recolor(mask_ref(lambda x, y: (x > 37.3) & (x < 73.0) & (y > 37.6) & (y < 38.6)), tone=3)   # doors cast shadow
    L.recolor(mask_ref(lambda x, y: (x > 72.9) & (x < 73.9) & (y > 12.5) & (y < 38.6)), tone=3)
    for sx in (41, 46.5, 52, 57.5, 63, 68.5):          # step recesses
        L.P(sx, 39.2, 'tan', 1); L.P(sx + 1, 39.2, 'tan', 1)
        L.P(sx, 40.2, 'tan', 2); L.P(sx + 1, 40.2, 'tan', 3)
    for x in np.arange(39.5, 78.0, 3.0):
        L.P(x, 40.9, 'tan', 2)
    # A-pillar / windshield edge + cowl side
    L.recolor(mask_ref(lambda x, y: (x > 72.9) & (x < 74.5) & (y > 11.5) & (y < 25.5)), tone=4)
    L.recolor(mask_ref(lambda x, y: (x > 73.6) & (x < 74.5) & (y > 12.4) & (y < 23.6)), mat='glass', tone=3)
    L.recolor(mask_ref(lambda x, y: (x > 73.6) & (x < 74.5) & (y > 13.4) & (y < 16.4)), mat='glass', tone=6)
    L.recolor(mask_ref(lambda x, y: (x > 72.9) & (x < 76.5) & (y > 25.5) & (y < 37.6)), tone=5)
    L.recolor(mask_ref(lambda x, y: (x > 72.9) & (x < 73.9) & (y > 25.5) & (y < 37.6)), tone=6)
    L.recolor(mask_ref(lambda x, y: (x > 75.6) & (x < 76.5) & (y > 25.5) & (y < 37.6)), tone=4)
    for y in np.arange(26.5, 37.0, 2.5):
        L.P(74.6, y, 'tan', 3)
    # fuel filler door (recessed disc)
    L.ell(31.0, 27.6, 1.9, 1.8, 'black', 2)
    L.P(30, 26.5, 'black', 1); L.P(31, 26.5, 'black', 1)
    L.P(31, 28.5, 'black', 4); L.P(32, 27.5, 'black', 3)
    L.P(30, 29.5, 'tan', 6); L.P(31, 29.5, 'tan', 6); L.P(32, 28.6, 'tan', 6)
    # tail light + reflector
    L.rect(9, 31, 13, 33, 'tan', 3)
    L.rect(10, 31, 12, 32, 'red', 3); L.P(12, 31, 'red', 2)
    L.P(10, 31, 'red', 5)
    L.rect(8, 28, 9, 30, 'white', 2); L.P(8, 28, 'white', 3)
    # spare carrier arm + upper latch
    L.poly([(4.6, 24.6), (8.0, 24.6), (8.0, 27.6), (6.5, 27.6)], 'tan', 4)
    L.recolor(mask_ref(lambda x, y: (x > 4.5) & (x < 8.1) & (y > 24.6) & (y < 25.6)), tone=6)
    L.rect(7, 18, 10, 21, 'tan', 5)
    L.rect(7, 18, 10, 19, 'tan', 7); L.P(9, 20, 'tan', 3)
    # mud flap
    L.rect(11, 36, 13, 51, 'rubber', 2)
    L.rect(11, 36, 12, 51, 'rubber', 3)
    L.rect(11, 36, 14, 37, 'steel', 3)
    # rear arch flare: lit lip, shadow band inside
    lip = mask_ref(lambda x, y: (x > 14.5) & (x < 37.8) & (y < arch_y(x, REAR_ARCH)) & (y > arch_y(x, REAR_ARCH) - 1.2))
    L.recolor(lip & sil, tone=6)
    L.recolor(mask_ref(lambda x, y: (x > 14.5) & (x < 37.8) & (y <= arch_y(x, REAR_ARCH) - 1.2) & (y > arch_y(x, REAR_ARCH) - 2.2)) & sil, tone=3)
    for x in np.arange(17.0, 36.0, 3.0):
        L.P(x, arch_y(x, REAR_ARCH) - 0.7, 'tan', 4)
    # cargo side bolts (sparse)
    for x in np.arange(13.0, 36.0, 4.0):
        L.P(x, slope_near(x) + 2.2, 'tan', 4)
    # door apertures: keep a 1-cell jamb ring (hidden under the doors), open the rest
    for poly in (DOOR_R, DOOR_F):
        d = cov_poly(poly) >= 0.5
        p = np.pad(d, 1)
        inner = d & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        L.fill(d & ~inner, 'tan', 2)
        L.erase(inner)
    return L, sil

# ------------------------------------------------------------------ DOORS
def make_door(front):
    L = Layer('DoorFront' if front else 'DoorRear')
    poly = DOOR_F if front else DOOR_R
    L.poly(poly, 'tan', 5)
    if front:
        fx0, fx1, fy0, fy1 = 57.5, 71.2, 16.0, 25.6
        px0, px1, py0, py1 = 56.5, 68.0, 26.8, 36.0
        lock = (61.8, 33.6); hx = 55.0; mirror = True
    else:
        fx0, fx1, fy0, fy1 = 39.5, 51.2, 16.4, 25.6
        px0, px1, py0, py1 = 39.5, 51.0, 26.8, 36.0
        lock = (44.0, 33.4); hx = 37.9; mirror = False
    L.recolor(mask_ref(lambda x, y: (y > 30.0)) & (L.tone == 5), tone=4)
    # armored window frame: protrudes -> bevel + cast shadow below/right
    L.poly([(fx0 + 0.6, fy1), (fx1 + 0.6, fy1), (fx1 + 0.6, fy1 + 1), (fx0 + 0.6, fy1 + 1)], 'tan', 3)
    L.poly([(fx1, fy0 + 0.6), (fx1 + 1, fy0 + 0.6), (fx1 + 1, fy1 + 0.6), (fx1, fy1 + 0.6)], 'tan', 3)
    L.poly([(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)], 'tan', 5)
    L.recolor(mask_ref(lambda x, y: (x > fx0) & (x < fx1) & (y > fy0) & (y < fy0 + 1)), tone=7)
    L.recolor(mask_ref(lambda x, y: (x > fx0) & (x < fx0 + 1) & (y > fy0) & (y < fy1)), tone=6)
    L.recolor(mask_ref(lambda x, y: (x > fx0) & (x < fx1) & (y > fy1 - 1) & (y < fy1)), tone=4)
    L.recolor(mask_ref(lambda x, y: (x > fx1 - 1) & (x < fx1) & (y > fy0) & (y < fy1)), tone=4)
    # glass: deep inset (frame inner edge dark on top/left), faint see-through
    gx0, gx1, gy0, gy1 = fx0 + 1.2, fx1 - 1.2, fy0 + 1.2, fy1 - 1.2
    g = L.poly([(gx0, gy0), (gx1, gy0), (gx1, gy1), (gx0, gy1)], 'glass', 3, alpha=230)
    L.recolor(g & mask_ref(lambda x, y: (y < gy0 + 1)), tone=0)
    L.recolor(g & mask_ref(lambda x, y: (x < gx0 + 1)), tone=1)
    L.recolor(g & mask_ref(lambda x, y: (y > gy0 + 1) & (y < gy0 + 2.2) & (x > gx0 + 1)), tone=2)
    L.recolor(g & mask_ref(lambda x, y: (y > gy1 - 1)), tone=4)
    # sky reflection glints (two diagonal streaks)
    base = gx0 + (4.0 if front else 2.5)
    for i in range(6):
        for dx, t in ((0, 6), (1, 5), (3, 5)):
            xx, yy = base + dx + i, gy1 - 1.5 - i
            if gx0 + 1 < xx < gx1 - 0.3 and gy0 + 1.2 < yy < gy1 - 1:
                L.P(xx, yy, 'glass', t, 230)
    L.P(gx1 - 1.5, gy0 + 1.3, 'glass', 6, 230)
    # frame bolts
    for x in np.arange(fx0 + 1.5, fx1 - 1.0, 2.5):
        L.P(x, fy0 + 0.2, 'tan', 5)
        L.P(x, fy1 - 0.8, 'tan', 3)
    # lower armour plate: raised, bevelled, with drop shadow
    L.poly([(px0 + 0.6, py1), (px1 + 0.6, py1), (px1 + 0.6, py1 + 1), (px0 + 0.6, py1 + 1)], 'tan', 3)
    L.poly([(px1, py0 + 0.6), (px1 + 1, py0 + 0.6), (px1 + 1, py1), (px1, py1)], 'tan', 3)
    L.poly([(px0, py0), (px1, py0), (px1, py1), (px0, py1)], 'tan', 5)
    L.recolor(mask_ref(lambda x, y: (x > px0) & (x < px1) & (y > py0) & (y < py0 + 1)), tone=7)
    L.recolor(mask_ref(lambda x, y: (x > px0) & (x < px0 + 1) & (y > py0) & (y < py1)), tone=6)
    L.recolor(mask_ref(lambda x, y: (x > px0) & (x < px1) & (y > py1 - 1) & (y < py1)), tone=3)
    L.recolor(mask_ref(lambda x, y: (x > px1 - 1) & (x < px1) & (y > py0) & (y < py1)), tone=4)
    L.recolor(mask_ref(lambda x, y: (x > px0 + 1) & (x < px1 - 1) & (y > py0 + 4.2) & (y < py1 - 1)), tone=4)
    sy = py0 + 4.2
    L.recolor(mask_ref(lambda x, y: (x > px0 + 1) & (x < px1 - 1) & (y > sy - 1) & (y < sy)), tone=3)
    for x in np.arange(px0 + 1.5, px1 - 1.0, 2.5):
        L.P(x, py0 + 1.2, 'tan', 4)
    # lock (recessed)
    lx, ly = lock
    L.rect(lx - 1, ly - 1, lx + 1, ly + 1, 'black', 1)
    L.P(lx - 1, ly - 1, 'black', 0); L.P(lx, ly, 'black', 3)
    L.P(lx - 1, ly + 1, 'tan', 6); L.P(lx, ly + 1, 'tan', 6); L.P(lx + 1, ly, 'tan', 5)
    L.P(lx - 1, ly - 2, 'tan', 3); L.P(lx, ly - 2, 'tan', 3)
    # handle latch at the rear edge
    L.rect(hx - 0.5, 27, hx + 1.5, 30, 'tan', 6)
    L.rect(hx, 28, hx + 1, 30, 'black', 2)
    L.P(hx - 0.5, 30, 'tan', 3); L.P(hx + 0.5, 30, 'tan', 3)
    # thick armoured door: bevel on the ring just inside the seam
    d = L.occ()
    p = np.pad(d, 1)
    e1 = d & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]          # inside the seam ring
    p1 = np.pad(e1, 1)
    e2 = e1 & p1[:-2, 1:-1] & p1[2:, 1:-1] & p1[1:-1, :-2] & p1[1:-1, 2:]
    ring = e1 & ~e2
    up = ring & ~p1[:-2, 1:-1]; dn = ring & ~p1[2:, 1:-1]
    lf = ring & ~p1[1:-1, :-2]; rt = ring & ~p1[1:-1, 2:]
    L.tone[lf & (L.mat == MID['tan'])] = 6
    L.tone[rt & (L.mat == MID['tan'])] = 3
    L.tone[dn & (L.mat == MID['tan'])] = 3
    L.tone[up & (L.mat == MID['tan'])] = 7
    if mirror:   # side mirror on the front door
        L.rect(70, 14, 72, 21, 'black', 2)
        L.rect(70, 14, 71, 21, 'black', 3)
        L.P(70, 14, 'black', 4); L.P(71, 20, 'black', 1)
        L.rect(72, 16, 73, 18, 'steel', 3)
    return L

# ------------------------------------------------------------------ HOOD / tilting front clip
def make_hood():
    L = Layer('Hood')
    sil = L.poly(HOOD2, 'tan', 5)
    # hood top plane
    plane = mask_ref(lambda x, y: (y < hood_near(x)) & (x > 74.4))
    L.recolor(plane & sil, tone=6)
    L.recolor(mask_ref(lambda x, y: (y < hood_near(x)) & (y > hood_near(x) - 1.0) & (x > 74.4)) & sil, tone=7)
    L.recolor(mask_ref(lambda x, y: (y < hood_far(x) + 1.0) & (x > 74.4)) & sil, tone=5)   # far edge falls off
    # raised centre panel of the hood (two ribs)
    for x in np.arange(79.0, 100.0, 1.0):
        L.P(x, (hood_near(x) + hood_far(x)) / 2 - 0.1, 'tan', 5 if int(x) % 3 else 4)
    # louvred vent on the hood top, near the nose
    for x in range(93, 99):
        L.P(x, hood_far(x) + 0.7, 'black', 2 if x % 2 else 3)
    # fender side face below the plane
    L.recolor(mask_ref(lambda x, y: (y >= hood_near(x)) & (y < hood_near(x) + 1.0) & (x > 76.5) & (x < 102.5)) & sil, tone=6)
    L.recolor(mask_ref(lambda x, y: (y >= hood_near(x) + 3.0) & (x > 76.5)) & sil, tone=4)
    # nose / grille face turning away
    L.recolor(mask_ref(lambda x, y: (x > 102.8) & (y > hood_far(x) + 1.0)), tone=3)
    L.recolor(mask_ref(lambda x, y: (x > 101.8) & (x < 102.8) & (y > hood_near(x) + 0.5)), tone=4)
    for y in range(30, 35):
        L.P(103.2, y + 0.2, 'tan', 2 if y % 2 else 4)
    # headlight lens peeking out of the nose + turn signal on the fender
    L.rect(103, 28, 105, 30, 'white', 2); L.P(103, 28, 'white', 3); L.P(104, 29, 'white', 1)
    L.rect(99, 27, 102, 28, 'amber', 2); L.P(99, 27, 'amber', 3); L.P(101, 27, 'amber', 1)
    L.rect(99, 28, 102, 29, 'tan', 6)
    # front arch flare
    L.recolor(mask_ref(lambda x, y: (x > 79.5) & (x < 99.5) & (y < arch_y(x, FRONT_ARCH)) & (y > arch_y(x, FRONT_ARCH) - 1.2)) & sil, tone=6)
    L.recolor(mask_ref(lambda x, y: (x > 79.5) & (x < 99.5) & (y <= arch_y(x, FRONT_ARCH) - 1.2) & (y > arch_y(x, FRONT_ARCH) - 2.2)) & sil, tone=3)
    for x in np.arange(82.0, 99.0, 3.0):
        L.P(x, arch_y(x, FRONT_ARCH) - 0.7, 'tan', 4)
    # hood rear seam + bolts
    L.recolor(mask_ref(lambda x, y: (x > 76.5) & (x < 77.5) & (y > hood_near(x) + 1) & (y < 37)), tone=6)
    for y in np.arange(27.5, 36.0, 2.5):
        L.P(77.6, y, 'tan', 3)
    # side vent / intake duct recess
    L.poly([(79.0, 26.4), (81.0, 26.4), (83.6, 30.6), (81.6, 30.6)], 'black', 1)
    L.poly([(80.0, 26.4), (81.0, 26.4), (83.6, 30.6), (82.6, 30.6)], 'black', 2)
    L.recolor(mask_ref(lambda x, y: (x > 81.6) & (x < 84.6) & (y > 30.4) & (y < 31.4)), tone=7)
    # air-intake cap sitting on the near fender top
    L.rect(75, 19, 80, 21, 'black', 2)
    L.rect(75, 19, 80, 20, 'black', 4); L.P(75, 19, 'black', 3)
    L.rect(76, 21, 79, 24, 'black', 1)
    L.rect(76, 21, 77, 24, 'black', 3)
    return L

# ------------------------------------------------------------------ TURRET (M1151 O-GPK)
# measured from the M1151 side render, then scaled x1.15 / y1.25 about its base so it matches this taller hull
TUR_PLATE = [(34.06, 0.1), (57.29, 0.1), (60.28, 8.35), (69.02, 8.35), (69.71, 9.35), (69.71, 11.6), (37.74, 11.6), (37.17, 10.47)]
def tur_rear_x(y):  return 34.06 + (y - 0.1) * 0.30
def tur_front_x(y): return 57.29 + (y - 0.1) * 0.3624

def make_turret():
    L = Layer('Turret')
    # rear stowage bin (lower, behind the plate)
    bin_ = L.poly([(31.8, 6.0), (38.0, 5.8), (38.0, 11.4), (32.2, 11.4)], 'tan', 4)
    L.recolor(bin_ & mask_ref(lambda x, y: (y < 6.9)), tone=6)
    L.recolor(bin_ & mask_ref(lambda x, y: (x < 33.0)), tone=3)
    L.recolor(bin_ & mask_ref(lambda x, y: (y > 10.4)), tone=3)
    L.P(34, 8, 'tan', 2); L.P(35, 8, 'tan', 2); L.P(34, 9, 'tan', 6)
    # main side plate
    pl = L.poly(TUR_PLATE, 'tan', 5)
    L.recolor(pl & mask_ref(lambda x, y: (y < 1.1)), tone=7)
    L.recolor(pl & mask_ref(lambda x, y: (y > 7.4)), tone=4)
    L.recolor(pl & mask_ref(lambda x, y: (x < tur_rear_x(y) + 1.0)), tone=6)                    # rear bevel, lit
    L.recolor(pl & mask_ref(lambda x, y: (y < 8.3) & (x > tur_front_x(y) - 1.0)), tone=4)       # front slope, away
    L.recolor(pl & mask_ref(lambda x, y: (x > 60.3) & (y > 8.3) & (y < 9.3)), tone=7)          # chin top
    L.recolor(pl & mask_ref(lambda x, y: (x > 60.3) & (y > 9.3) & (y < 10.3)), tone=5)
    L.recolor(pl & mask_ref(lambda x, y: (x > 68.8) & (y > 9.3)), tone=3)                       # chin nose
    L.recolor(pl & mask_ref(lambda x, y: (y > 9.4) & (y < 10.3) & (x < 60.3)), tone=3)          # lower seam
    for x in np.arange(39.5, 60.0, 2.8):
        L.P(x, 10.6, 'tan', 3)
    for x, y in ((36.2, 3.5), (36.9, 6.2), (37.6, 8.6), (58.4, 4.2), (59.3, 6.7), (63.0, 9.8), (66.5, 9.8)):
        L.P(x, y, 'tan', 3)
    # two big ballistic windows
    def win(x0, x1, y0, y1):
        L.poly([(x0 + 0.6, y1), (x1 + 0.6, y1), (x1 + 0.6, y1 + 0.9), (x0 + 0.6, y1 + 0.9)], 'tan', 3)
        L.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'tan', 6)
        L.recolor(mask_ref(lambda x, y: (x > x0) & (x < x1) & (y > y0) & (y < y0 + 1)), tone=7)
        L.recolor(mask_ref(lambda x, y: (x > x1 - 1) & (x < x1) & (y > y0) & (y < y1)), tone=4)
        L.recolor(mask_ref(lambda x, y: (x > x0) & (x < x1) & (y > y1 - 1) & (y < y1)), tone=4)
        gx0, gx1, gy0, gy1 = x0 + 1, x1 - 1, y0 + 1, y1 - 1
        g = L.poly([(gx0, gy0), (gx1, gy0), (gx1, gy1), (gx0, gy1)], 'glass', 2, alpha=235)
        L.recolor(g & mask_ref(lambda x, y: (y < gy0 + 1)), tone=0)
        L.recolor(g & mask_ref(lambda x, y: (x < gx0 + 1)), tone=1)
        L.recolor(g & mask_ref(lambda x, y: (y > gy1 - 1)), tone=3)
        for i in range(5):
            for dx, t in ((0, 5), (1, 4)):
                xx, yy = gx0 + 1.6 + dx + i, gy1 - 1.4 - i
                if gx0 + 1 < xx < gx1 and gy0 + 1 < yy < gy1 - 1:
                    L.P(xx, yy, 'glass', t, 235)
        L.P(gx1 - 1.3, gy0 + 1.2, 'glass', 6, 235)
    win(41.0, 47.4, 1.1, 8.9)
    win(47.8, 55.8, 1.1, 8.9)
    # pintle post under the gun cradle
    L.rect(62, 6, 64, 8, 'steel', 2)
    L.rect(62, 6, 63, 8, 'steel', 4)
    L.rect(61, 7, 65, 8, 'steel', 1)
    # turret ring collar on the roof
    L.poly([(37.7, 11.4), (69.4, 11.4), (69.4, 12.2), (37.7, 12.2)], 'tan', 3)
    return L

def make_turret_shield():
    """front gun shield: a transverse plate, so from the side it is a thin leaning slab"""
    L = Layer('TurretShield')
    sh = L.poly([(68.9, -4.9), (70.5, -4.9), (73.8, 11.6), (72.2, 11.6)], 'tan', 5)
    L.recolor(sh & mask_ref(lambda x, y: (x < 68.9 + (y + 4.9) * 0.2 + 0.8)), tone=7)
    L.recolor(sh & mask_ref(lambda x, y: (x > 68.9 + (y + 4.9) * 0.2 + 1.2)), tone=3)
    L.recolor(sh & mask_ref(lambda x, y: (y < -3.9)), tone=6)
    L.lock[:] = True
    return L

# ------------------------------------------------------------------ ANTENNAS (behind the turret)
def make_antenna():
    L = Layer('Antenna')
    for (p0, p1, p2) in [((8.6, 17.4), (20, 3.0), (32.6, 5.6)), ((16.8, 17.6), (24, 10.0), (32.0, 7.8))]:
        pts = curve_cells(bezier(p0, p1, p2, 600))
        for i in range(len(pts) - 1):
            L.line(*pts[i], *pts[i + 1], 'steel', 2)
        for i in range(0, len(pts), 8):
            L.put(pts[i][0] + OX, pts[i][1] + OY, 'steel', 4)
    L.rect(8, 17, 10, 18, 'black', 3)
    L.rect(16, 17, 18, 18, 'black', 3)
    L.lock[:] = True
    return L

# ------------------------------------------------------------------ WHEEL WELLS (shadowed liner, not pitch black)
def make_well(front):
    L = Layer('WellFront' if front else 'WellRear')
    if front:
        m = L.poly(FRONT_ARCH[::-1] + [(79.7, 43), (99.3, 43)], 'tan', 1)
    else:
        m = L.poly(REAR_ARCH + [(37.6, 43), (14.7, 43)], 'tan', 1)
    L.recolor(m & mask_ref(lambda x, y: (y > 30.2) & (y < 31.2)), tone=2)
    L.recolor(m & mask_ref(lambda x, y: (y > 32.5)), tone=0)
    L.lock[:] = True
    return L

# ------------------------------------------------------------------ SPARE (tread faces viewer)
def make_spare():
    L = Layer('Spare')
    s = L.poly([(0.4, 19.5), (1.4, 17.3), (3.2, 16.4), (7.8, 16.4), (9.6, 17.3), (10.6, 19.5), (10.6, 34.0),
                (9.6, 36.3), (7.8, 37.2), (3.2, 37.2), (1.4, 36.3), (0.4, 34.0)], 'rubber', 2)
    # rounded shading: centre column lighter, edges darker
    L.recolor(mask_ref(lambda x, y: (x > 2.2) & (x < 8.6)), tone=3)
    L.recolor(mask_ref(lambda x, y: (x > 3.2) & (x < 6.6) & (y > 18) & (y < 30)), tone=4)
    # tread lugs: staggered blocks
    for r, y in enumerate(np.arange(17.5, 36.5, 1.5)):
        for x in ((1.6, 5.2) if r % 2 == 0 else (3.2, 7.0)):
            L.P(x, y, 'rubber', 1)
            L.P(x + 1, y, 'rubber', 1)
            L.P(x, y - 1, 'rubber', 5 if y < 30 else 4)
    return L

# ------------------------------------------------------------------ WHEEL sheet (4 frames x 21x21)
def make_wheel_frames(n=4):
    D = 21
    frames = []
    yy, xx = np.mgrid[0:D, 0:D]
    dx = xx + 0.5 - D / 2; dy = yy + 0.5 - D / 2
    r = np.hypot(dx, dy); ang = np.arctan2(dy, dx)
    deg = np.degrees(ang)            # -180..180, -90 = up
    tl = (deg > -165) & (deg < -60)  # lit arc (top / upper-left)
    br = (deg > 20) & (deg < 150)    # shadow arc (bottom)
    for f in range(n):
        L = Layer('Wheel', D, D)
        rot = f * (np.pi / 4) / n
        tire = r <= 10.5
        L.fill(tire, 'rubber', 2)
        # tread: 16 knobs around the rim
        k = ((ang - rot * 2) / (2 * np.pi) * 16) % 1.0
        tread = tire & (r > 8.3)
        L.fill(tread, 'rubber', 1)
        L.fill(tread & (k < 0.5), 'rubber', 3)
        L.fill(tread & (k < 0.5) & br, 'rubber', 2)
        L.fill(tread & (k < 0.5) & tl, 'rubber', 5)
        # sidewall with a soft bulge highlight
        side = tire & (r <= 8.3) & (r > 5.6)
        L.fill(side, 'rubber', 2)
        L.fill(side & (r > 6.4) & (r < 8.3) & tl, 'rubber', 4)
        L.fill(side & (r > 6.4) & (r < 8.3) & ((deg > -178) & (deg < -30)) & ~tl, 'rubber', 3)
        L.fill(side & (r > 6.4) & (r < 8.3) & br, 'rubber', 1)
        L.fill(side & (r <= 6.4), 'rubber', 1)                       # bead shadow
        # rim (wheel centre sits on a cell centre, so offsets are integers)
        rim = r <= 5.45
        fl = rim & (r > 4.3)
        L.fill(fl, 'tan', 3); L.fill(fl & tl, 'tan', 5); L.fill(fl & br, 'tan', 2)
        face = rim & (r <= 4.3) & (r > 2.3)
        L.fill(face, 'tan', 5); L.fill(face & tl, 'tan', 6); L.fill(face & br, 'tan', 4)
        grv = rim & (r <= 2.3) & (r > 1.5)
        L.fill(grv, 'tan', 3); L.fill(grv & br, 'tan', 2)
        hub = rim & (r <= 1.5)
        L.fill(hub, 'tan', 6); L.fill(hub & (dx < 0) & (dy < 0), 'tan', 7); L.fill(hub & (dx + dy > 0.5), 'tan', 4)
        L.fill(rim & (r < 0.5), 'tan', 5)
        for i in range(8):
            a = rot + i * np.pi / 4 + np.pi / 8
            nx = D / 2 + 3.3 * np.cos(a); ny = D / 2 + 3.3 * np.sin(a)
            L.put(int(np.floor(nx)), int(np.floor(ny)), 'tan', 2)
        L.outline()
        frames.append(L)
    return frames

# ------------------------------------------------------------------ GUN (M2HB on its cradle), texture faces right
GUN_ROWS = [
    "........LL..........................",
    "..LUUUUUUUUUUUUU.LLL................",
    "KKLTTTTTTTTTTTTTSSSSTsTsT........KKK",
    "KLLSSSSSSVSSSSSSSkSkSSSSSSSSSSSSSKLK",
    "KKLsssssssssssss....................",
    "..........KK.K......................",
    "...........KK.......................",
]
GUN_W, GUN_H = 36, 7
GUN_PIVOT = (11.5, 6.5)          # cradle trunnion, texture cells (continuous)
GUN_PIVOT_REF = (64.1, 5.2)      # where it sits on the vehicle (ref cells)
GUN_PAL = {'k': ('black', 1), 'K': ('black', 2), 'L': ('black', 3), 'M': ('black', 4),
           's': ('steel', 2), 'S': ('steel', 3), 'T': ('steel', 4), 'U': ('steel', 5), 'V': ('steel', 6)}

def make_gun():
    L = Layer('Gun', GUN_W, GUN_H)
    for j, row in enumerate(GUN_ROWS):
        for i, ch in enumerate(row.ljust(GUN_W, '.')):
            if ch != '.':
                m, t = GUN_PAL[ch]
                L.put(i, j, m, t)
    return L
