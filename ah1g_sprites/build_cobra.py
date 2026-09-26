"""
AH-1G Cobra boss sprites, drawn at 1x on the reference grid (geom.py, refs.py) and exported 2x nearest.

Scale: the Apache body scale, 10.97 cells per metre (21.94 px/m at 2x). The main rotor follows the Apache's own rotor
convention (ApacheBoss_MainRotor is 274 px for a 14.63 m rotor), so the Cobra's 13.41 m rotor is 252 px; the tail rotor
likewise follows the Apache tail rotor (58 px for 2.79 m) -> 54 px for 2.59 m.

Layers (all body-canvas layers share one 308x84 canvas and one origin, draw them at the same position):
  CobraBoss.png            fuselage, cockpit interior, mast, beacon, stub wing and racks, skid gear, tail skid
  CobraBoss_Canopy.png     glass and frames (separate so it can crack, fog or open)
  CobraBoss_Shark.png      shark mouth (flip with the body)
  CobraBoss_MarksL/R.png   stencils, drawn unflipped: L when facing left, R when facing right
  CobraBoss_Turret.png     ball chin turret; draw after the gun so the ball hides the barrel root
  CobraBoss_PodIn.png      inboard M158A1 7-tube pod (hidden behind the outboard pod until that one is gone)
  CobraBoss_PodOut.png     outboard M200A1 19-tube pod
Own canvases:
  CobraBoss_Gun.png        M129 40 mm grenade launcher, 2 frames (rest, recoil), pivot in coords json
  CobraBoss_MainRotor.png  2-blade teetering rotor, 6 side-view frames stacked (30 deg apart)
  CobraBoss_MainRotorBlur.png
  CobraBoss_TailRotor.png  2-blade tail rotor, rotated in code like the Apache's
  CobraBoss_TailRotorBlur.png
"""
import json, os
import numpy as np
from PIL import Image
from px import *
from geom import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
W, H, OX, OY = 154, 42, 3, 42
cv = Canvas(W, H, OX, OY)
X, Y = cv.cx, cv.cy


def runs_from(m, direction):
    """for each cell of mask m: 1-based count of mask cells from the nearest edge in the given direction
    ('top' counts down from the first cell under the outside, 'bot' counts up)"""
    d = np.zeros(m.shape, np.int32)
    rows = range(m.shape[0]) if direction == 'top' else range(m.shape[0] - 1, -1, -1)
    prev = np.zeros(m.shape[1], np.int32)
    for r in rows:
        cur = np.where(m[r], prev + 1, 0)
        d[r] = cur; prev = cur
    return d


def interp_y(pts, x):
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    o = np.argsort(xs)
    return np.interp(x, xs[o], ys[o])


# ----------------------------------------------------------------------------------------------------------- body
def body():
    L = cv.layer('Body')
    fus = L.poly(FUSELAGE, 'od', 4)
    cx0, cx1, cy0, cy1 = CAVITY
    cav = (X > cx0) & (X < cx1) & (Y > cy0) & (Y < cy1)
    fus = fus | cav
    glass = cv.cov_poly(GLASS) >= 0.5
    dtop = runs_from(fus, 'top'); dbot = runs_from(fus, 'bot')

    # --- broad form: the sides are flat, the top and bottom roll away
    L.recolor(fus & (dtop == 2), tone=6)
    L.recolor(fus & (dtop == 3), tone=5)
    L.recolor(fus & (dbot == 2), tone=2)
    L.recolor(fus & (dbot == 3), tone=3)

    # nose below the sill: round, so it darkens toward the chin and the tip
    sill_y = interp_y(SILL, X)
    nose = fus & (X < 38) & (Y < sill_y)
    L.recolor(nose & (Y < sill_y - 1) & (Y >= sill_y - 3), tone=5)
    L.recolor(nose & (Y < sill_y - 3), tone=4)
    chin_mid = interp_y(CHIN + BELLY[::-1], X)
    L.recolor(nose & (Y < chin_mid + 2.2) & (dbot > 1), tone=3)
    L.recolor(nose & (X < 2.2) & (dbot > 1) & (dtop > 1), tone=3)
    L.recolor(nose & (X >= 0.5) & (X < 2.5) & (Y > 13.2) & (dtop > 1), tone=5)
    L.P(0.6, 13.6, 'od', 7)
    L.P(1.5, 14.4, 'od', 6)
    # sill: a lit ledge under the canopy rail
    for x in np.arange(8.9, 37.0, 1.0):
        L.P(x, interp_y(SILL, x) - 0.2, 'od', 6)

    # centre section: hump sides lit (the cowls lean in toward the top), fuselage side plain
    hump = fus & (X >= 37.6) & (X < 72.5) & (Y > 27.4)
    L.recolor(hump & (dtop > 3), tone=5)
    L.recolor(hump & (dtop > 3) & (Y < 30.2), tone=4)
    # hump front slope faces forward and up
    fr = fus & (X >= 37.6) & (X < 41.2) & (Y > 27.6)
    L.recolor(fr & (dtop <= 2), tone=7)
    L.recolor(fr & (dtop == 3), tone=6)
    # hump top edge
    L.recolor(fus & (X >= 41) & (X < 62) & (dtop == 2), tone=7)
    # rear slope of the transmission fairing, turning away from the light
    rs = fus & (X >= 61.5) & (X < 72.5) & (Y > 25.0)
    L.recolor(rs & (dtop == 2), tone=5)

    # engine nacelle: a horizontal cylinder bulging out of the cowl side
    nt = interp_y(NACELLE_TOP, X); nb = interp_y(NACELLE_BOT, X)
    nac = fus & (X > INTAKE[2] - 0.2) & (X < 72.3) & (Y < nt) & (Y > nb)
    L.recolor(nac, tone=4)
    L.recolor(nac & (Y > nt - 1.0), tone=6)
    L.recolor(nac & (Y <= nt - 1.0) & (Y > nt - 2.4), tone=5)
    L.recolor(nac & (Y < nb + 2.2), tone=3)
    L.recolor(nac & (Y < nb + 1.0), tone=2)
    L.recolor(fus & (X > INTAKE[0]) & (X < 72.2) & (Y < nb) & (Y > nb - 1.0), tone=2)     # its shadow on the side
    L.recolor(fus & (X > INTAKE[2]) & (X < 64.6) & (Y > nt) & (Y < nt + 1.0), tone=3)      # crease above it

    # engine air intake: dark grille
    x0, y0, x1, y1 = INTAKE
    it = L.fill((X > x0) & (X < x1) & (Y > y0) & (Y < y1) & fus, 'dark', 2)
    for yy in np.arange(y0 + 1.0, y1 - 0.5, 2.0):
        L.recolor(it & (Y > yy) & (Y < yy + 1.0), tone=4)
    L.recolor(it & (X < x0 + 1.0), tone=1)
    L.recolor(fus & (X > x0 - 1) & (X < x0) & (Y > y0) & (Y < y1), tone=6)                # lit lip in front

    # exhaust nozzle: burnt steel, rim catching light at the back
    noz = fus & (X > 72.3) & (X < 75.4) & (Y > 19.2) & (Y < 26.2)
    L.recolor(noz, mat='steel', tone=3)
    L.recolor(noz & (Y > 24.0), tone=5)
    L.recolor(noz & (Y > 22.4) & (Y <= 24.0), tone=4)
    L.recolor(noz & (Y < 21.2), tone=1)
    L.recolor(noz & (X < 73.2) & (Y > 21.2), mat='burnt', tone=4)            # heat tint behind the rim
    L.recolor(noz & (X > 74.0), mat='steel', tone=5)               # rim
    L.recolor(noz & (X > 74.0) & (Y > 24.0), tone=7)
    L.recolor(noz & (X > 74.0) & (Y < 21.8), tone=2)
    L.recolor(fus & (X > 71.4) & (X < 72.4) & (Y > 19.6) & (Y < 25.6), mat='od', tone=1)   # joint to the nacelle

    # tail boom: driveshaft fairing along the top, seam under it, then the tapering side
    boom = fus & (X >= 72) & (X < 121.5)
    bt = interp_y(BOOM_TOP, X)
    L.recolor(boom & (Y < bt) & (Y > bt - 1.7) & (dtop > 1), tone=5)
    L.recolor(boom & (dtop == 2), tone=6)
    L.recolor(boom & (Y <= bt - 1.7) & (Y > bt - 2.7), tone=3)
    L.recolor(boom & (Y <= bt - 2.7) & (Y > bt - 3.7), tone=5)
    # soot from the exhaust over the fairing
    for x in range(76, 96):
        k = (x - 76) / 20.0
        for yy in (bt[0, 0] * 0 + interp_y(BOOM_TOP, x) - 1.3, interp_y(BOOM_TOP, x) - 2.3):
            if ((x * 7 + int(yy * 3)) % 5) / 5.0 > k * 1.2:
                c, r = cv.cell(x, yy)
                if fus[r, c] and L.tone[r, c] > 2:
                    L.tone[r, c] -= 2

    # fin: flat plate, leading edge rounded (lit), trailing edge thin (darker)
    fin = fus & (X >= 120.8) & (Y > interp_y(BOOM_TOP, X) - 0.2)
    le_x = interp_y([(p[1], p[0]) for p in FIN_LE], Y)          # x of the leading edge at this height
    L.recolor(fin & (X < le_x + 2.2) & (dtop > 1), tone=5)
    L.recolor(fin & (X < le_x + 1.1) & (dtop > 1), tone=6)
    te_x = interp_y([(p[1], p[0]) for p in FIN_TE], Y)
    L.recolor(fin & (X > te_x - 1.6) & (Y > 16), tone=3)

    # tail rotor gearbox fairing on the fin
    gb = cv.cov_ell(TAIL_HUB[0] + 0.4, TAIL_HUB[1] - 0.3, 3.1, 2.8) >= 0.5
    L.fill(gb & fus, 'od', 4)
    L.recolor(gb & (cv.cov_ell(TAIL_HUB[0] - 0.4, TAIL_HUB[1] + 0.4, 2.0, 1.8) >= 0.5), tone=6)
    L.recolor(gb & (Y < TAIL_HUB[1] - 1.4), tone=3)

    # the turret notch: the inside of the recess behind the turret is in shadow; its rear wall catches light
    L.fill(cav, 'dark', 1)
    L.recolor(cav & (Y > cy1 - 1.0), tone=0)
    L.fill(fus & (X > cx1) & (X < cx1 + 1.0) & (Y > cy0 + 0.6) & (Y < cy1), 'od', 6)

    # cockpit interior under the glass (shows if the canopy layer is left off)
    L.fill(glass & fus & (dtop > 1), 'dark', 2)

    # --- outline last (outer edge of the whole fuselage)
    e = Layer.edge_of(fus)
    L.fill(e, 'od', 0)
    return L, fus




# ------------------------------------------------------------------------------------------ things in front of the skin
def merge(dst, src):
    m = src.occ()
    dst.mat[m] = src.mat[m]; dst.tone[m] = src.tone[m]; dst.alpha[m] = src.alpha[m]


def outlined(src, tone=0, mat='od'):
    e = Layer.edge_of(src.occ())
    src.tone[e] = tone; src.mat[e] = MID[mat]
    return src


def seam(L, fus, pts, dt=-2, lo=1, skip=None):
    """a panel line: darken the skin along a polyline, never touching the outline"""
    inner = fus & ~Layer.edge_of(fus)
    if skip is not None:
        inner &= ~skip
    for a, b in zip(pts[:-1], pts[1:]):
        for c, r in L.cells(a[0], a[1], b[0], b[1]):
            if 0 <= c < W and 0 <= r < H and inner[r, c] and L.is_mat('od')[r, c]:
                L.tone[r, c] = max(lo, L.tone[r, c] + dt)


def rivets(L, fus, pts, every=3, dt=1):
    inner = fus & ~Layer.edge_of(fus)
    for a, b in zip(pts[:-1], pts[1:]):
        for i, (c, r) in enumerate(L.cells(a[0], a[1], b[0], b[1])):
            if i % every == 1 and 0 <= c < W and 0 <= r < H and inner[r, c] and L.is_mat('od')[r, c]:
                L.tone[r, c] = min(7, L.tone[r, c] + dt)


def details(L, fus):
    glass = cv.cov_poly(GLASS) >= 0.5
    # panel lines from the production profile
    seam(L, fus, [(9.6, 8.9), (9.6, 14.6)])                                   # nose cone joint
    seam(L, fus, [(22.7, 5.5), (22.7, 17.0)], skip=glass)
    seam(L, fus, [(42.6, 5.4), (42.6, 27.0)])
    seam(L, fus, [(53.4, 5.2), (53.4, 20.6)])
    seam(L, fus, [(53.4, 28.6), (53.4, 33.6)], dt=-1)
    seam(L, fus, [(61.6, 5.2), (61.6, 20.4)])
    seam(L, fus, [(68.6, 5.4), (68.6, 17.6)], dt=-2, lo=1)                    # tail boom joint
    for x in (85.2, 112.4):
        seam(L, fus, [(x, 6.0), (x, interp_y(BOOM_TOP, x) - 1.8)])
    seam(L, fus, [(23.0, 17.35), (42.6, 17.35)], dt=-1, skip=glass)          # side panel line
    seam(L, fus, [(42.6, 17.4), (48.4, 17.4)], dt=-1)
    seam(L, fus, [(53.4, 17.4), (68.6, 17.4)], dt=-1)
    rivets(L, fus, [(42.6, 6.2), (42.6, 16.6)], every=3)
    rivets(L, fus, [(68.6, 6.0), (68.6, 16.8)], every=3)
    # transmission cowl door on the hump
    seam(L, fus, [(40.9, 30.4), (46.4, 30.4), (46.4, 33.4)], dt=-1)
    L.P(45.8, 31.4, 'od', 2)
    # oil level window
    L.fill((X > 56.2) & (X < 57.9) & (Y > 24.2) & (Y < 26.6) & fus, 'dark', 2)
    L.P(56.6, 25.8, 'glass', 5)
    # ammunition bay door and its latch, fuel cap
    door = [(57.6, 11.4), (60.2, 11.4), (60.2, 16.6), (57.6, 16.6), (57.6, 11.4)]
    seam(L, fus, door, dt=-2)
    seam(L, fus, [(58.6, 15.6), (58.6, 12.4)], dt=1)                          # lit inner edge
    L.P(59.4, 14.0, 'dark', 2)
    L.P(62.7, 12.6, 'od', 2); L.P(62.7, 13.6, 'od', 6)


def mast_beacon_pitot(L):
    top = L.occ()
    m = (X > 46.9) & (X < 48.9) & (Y > 35.0) & (Y < 39.6) & ~top
    L.fill(m & (X < 48.0), 'steel', 5)
    L.fill(m & (X >= 48.0), 'steel', 2)
    sw = (X > 45.4) & (X < 50.6) & (Y > 35.0) & (Y < 36.0)                   # swashplate
    L.fill(sw, 'steel', 3)
    L.P(45.5, 35.5, 'steel', 1); L.P(50.5, 35.5, 'steel', 1); L.P(46.5, 35.5, 'steel', 5)
    # anti-collision beacon on the engine cowl (lens is neutral, the code tints it)
    L.P(53.5, 34.5, 'steel', 2); L.P(54.5, 34.5, 'steel', 2)
    L.P(53.5, 35.5, 'white', 3); L.P(54.5, 35.5, 'white', 1)
    L.P(53.5, 36.5, 'od', 0); L.P(54.5, 36.5, 'od', 0)
    L.P(52.5, 35.5, 'od', 0); L.P(55.5, 35.5, 'od', 0)
    # pitot tube
    L.P(-1.5, 14.2, 'steel', 5); L.P(-0.5, 14.2, 'steel', 4); L.P(-2.5, 14.2, 'steel', 6)


WING_STAMP = [          # stub wing tip seen end on, x 41..53, rows y 15.5 .. 12.5 ('o' outline, digits = OD tone)
    '..ooooooo....',
    '.o77666666oo.',
    'o655555555544o',
    '.oo333333oooo',
]
ELEV_STAMP = [          # synchronised elevator end on, x 98..109, rows y 13.5 .. 11.5
    '.ooooooo....',
    'o7766655544o',
    '.ooooooooooo',
]


def stamp_od(L, rows, x0, y_top, light_mat='od'):
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            L.P(x0 + i + 0.5, y_top - j, light_mat, 0 if ch == 'o' else int(ch))


def wing_and_racks():
    R = cv.layer('rack')
    rk = R.poly(RACK, 'steel', 2)
    R.recolor(rk & (Y > 12.0), tone=3)
    R.P(45.3, 11.9, 'steel', 5); R.P(48.9, 11.9, 'steel', 5)
    outlined(R, 0, 'steel')
    Wg = cv.layer('wing')
    stamp_od(Wg, WING_STAMP, 41, 15.5)
    Wg.P(42.5, 14.5, 'white', 2)                                              # wingtip position light lens
    return R, Wg


def elevator_skid_antenna():
    E_ = cv.layer('elev')
    stamp_od(E_, ELEV_STAMP, 98, 13.5)
    T = cv.layer('tailskid')
    (x0, y0), (x1, y1) = TAIL_SKID
    for x in np.arange(x0, x1 + 0.01, 0.5):
        y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        T.P(x, y + 0.5, 'od', 4)
        T.P(x, y - 0.5, 'od', 1)
    T.P(x1 + 1.0, y1 + 0.5, 'od', 4); T.P(x1 + 1.0, y1 + 1.5, 'od', 1)
    outlined(T)
    A = cv.layer('antenna')
    for (x, y) in [(79.6, 5.6), (79.9, 4.6), (80.3, 3.8)]:
        A.P(x, y, 'od', 1)
    return E_, T, A


def skid_gear():
    G = cv.layer('gear')
    x0, x1 = SKID
    # struts (cross tube legs): lit face, dark side, rounded top
    for xs in STRUTS:
        G.fill((X > xs - 1.0) & (X < xs) & (Y > 1.8) & (Y < 6.2), 'od', 5)
        G.fill((X > xs) & (X < xs + 1.0) & (Y > 1.8) & (Y < 6.2), 'od', 2)
        G.P(xs - 0.5, 6.4, 'od', 4)
        G.P(xs - 0.5, 1.4, 'od', 3); G.P(xs + 0.5, 1.4, 'od', 3)             # saddle clamp
        G.P(xs - 1.5, 1.4, 'od', 3); G.P(xs + 1.5, 1.4, 'od', 3)
    # skid tube
    G.fill((X > x0 + 0.5) & (X < x1) & (Y > 1.0) & (Y < 2.0) & ~G.occ(), 'od', 5)
    G.fill((X > x0 + 0.5) & (X < x1) & (Y > 0.0) & (Y < 1.0), 'od', 1)
    for x in np.arange(x0 + 3.0, x1 - 2, 4.0):
        G.P(x, 1.5, 'od', 6)
    # upturned toe
    G.P(x0, 1.5, 'od', 5); G.P(x0, 0.5, 'od', 1)
    G.P(x0 - 1.0, 2.5, 'od', 5); G.P(x0 - 0.2, 2.5, 'od', 2)
    G.P(x0 - 1.6, 3.4, 'od', 4)
    # capped heel
    G.P(x1 - 0.5, 1.5, 'od', 3)
    outlined(G)
    return G


def body_full():
    L, fus = body()
    details(L, fus)
    mast_beacon_pitot(L)
    G = skid_gear()
    E_, T, A = elevator_skid_antenna()
    R, Wg = wing_and_racks()
    for part in (A, T, E_, G, R, Wg):
        merge(L, part)
    return L, fus


# ------------------------------------------------------------------------------------------------------- canopy
def canopy(fus):
    C = cv.layer('Canopy')
    skin_edge = Layer.edge_of(fus)
    g = (cv.cov_poly(GLASS) >= 0.5) & fus & ~skin_edge
    C.fill(g, 'glass', 4)
    dt = runs_from(g, 'top'); db = runs_from(g, 'bot')
    C.recolor(g & (dt <= 2), tone=5)
    C.recolor(g & (dt == 1), tone=6)
    C.recolor(g & (db <= 3), tone=3)
    # what shows through: glare shields, the gunner's sight, seat backs and headrests
    inside = [
        [(9.2, 15.6), (13.4, 16.6), (13.4, 17.8), (9.8, 17.4)],             # gunner's panel
        [(12.2, 17.6), (13.6, 17.6), (14.2, 20.6), (13.0, 20.9)],           # gunner's sight column
        [(16.6, 17.4), (19.0, 18.0), (19.4, 22.8), (18.3, 23.4), (17.0, 22.4)],   # gunner's seat back and headrest
        [(22.8, 18.6), (26.6, 19.3), (26.6, 20.4), (23.2, 20.3)],           # pilot's glare shield
        [(25.2, 20.3), (26.2, 20.3), (26.2, 21.5), (25.2, 21.5)],           # reflex sight
        [(33.0, 20.4), (35.8, 21.4), (36.4, 24.6), (35.0, 25.4), (33.6, 24.2)],   # pilot's seat back and headrest
    ]
    for poly in inside:
        m = (cv.cov_poly(poly) >= 0.45) & g
        C.recolor(m, tone=2)
        C.recolor(m & (runs_from(m, 'top') == 1), tone=3)
    # glints (/), two per pane, as on the Apache canopy
    for (xa, ya, xb, yb, t) in [(11.0, 17.4, 15.2, 24.8, 7), (13.6, 17.8, 16.9, 23.8, 6),
                                (25.4, 20.6, 29.2, 26.6, 7), (28.0, 20.9, 31.3, 26.4, 6)]:
        C.line(xa, ya, xb, yb, 'glass', t, only=g)
    # frames: front bow, gunner / pilot divider, rear bow, bottom rail
    C.line(*FRONT_FRAME[0], *FRONT_FRAME[1], 'od', 0, only=fus)
    C.line(*DIVIDER[0], *DIVIDER[1], 'od', 0, only=fus)
    C.line(DIVIDER[0][0] + 1.0, DIVIDER[0][1] - 0.4, DIVIDER[1][0] + 1.0, DIVIDER[1][1] + 0.3, 'od', 4, only=g)
    C.line(*REAR_FRAME[0], *REAR_FRAME[1], 'od', 0, only=fus)
    gb = interp_y(GLASS_BOT, X); sl = interp_y(SILL, X)
    rail = fus & ~skin_edge & (X > 8.2) & (X < 38.2) & (Y < gb + 0.5) & (Y > sl)
    C.fill(rail & ~g, 'od', 1)
    C.recolor(g & (db == 1), mat='od', tone=1)
    return C


# ------------------------------------------------------------------------------------------------------ turret
def turret():
    """chin turret after the photo: a drum with a lid, square with rounded corners side on, lit lid, dark seam under
    the lid, drum lighter at the front, gun slot in the upper front face"""
    T = cv.layer('Turret')
    for j, row in enumerate(TURRET_STAMP):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            x, y = TURRET_X0 + i + 0.5, TURRET_TOP - j
            if ch == 'o':
                T.P(x, y, 'od', 0)
            elif ch == 's':
                T.P(x, y, 'dark', 0)
            else:
                T.P(x, y, 'od', int(ch))
    return T


def gun_frames():
    """M129 40 mm grenade launcher barrel: stubby, a flash suppressor ring at the muzzle. Muzzle to the left, pivot on
    the elevation axis inside the drum (only the stub ahead of the front face shows). Frames: 0 rest, 1 recoil."""
    length = GUN_PIVOT[0] - MUZZLE_X
    w, h = int(np.ceil(length)) + 2, 4
    frames = []
    for recoil in (0, 1):
        a = np.zeros((h, w, 4), np.uint8)
        def put(c, r, mat, t):
            if 0 <= c < w and 0 <= r < h:
                a[r, c, :3] = RAMPS[mat][t]; a[r, c, 3] = 255
        x0 = recoil
        for c in range(x0 + 1, w):
            put(c, 0, 'steel', 0); put(c, 1, 'steel', 4); put(c, 2, 'steel', 2); put(c, 3, 'steel', 0)
        put(x0, 0, 'steel', 0); put(x0, 1, 'steel', 6); put(x0, 2, 'steel', 3); put(x0, 3, 'steel', 0)   # muzzle ring
        put(x0 + 1, 1, 'steel', 1); put(x0 + 1, 2, 'steel', 0)                                           # bore shadow
        frames.append(a)
    return frames, (length + 0.5, 2.0)


# -------------------------------------------------------------------------------------------------------- pods
def pod(x0, x1, y0, y1, name, bands):
    """rocket pod side on: a cylinder (hard highlight on top, dark belly), rounded ends, a lit rim at the open front,
    darker aft cap, strap bands"""
    P = cv.layer(name)
    m = P.fill((X > x0) & (X < x1) & (Y > y0) & (Y < y1), 'od', 4)
    rows = sorted(set(np.nonzero(m)[0]))
    top, bot = rows[0], rows[-1]
    cols = np.nonzero(m.any(0))[0]; c0, c1 = cols[0], cols[-1]
    inner = rows[1:-1]
    ramp = {1: [5], 2: [6, 3], 3: [6, 4, 2], 4: [6, 5, 3, 2]}[len(inner)]
    for r, t in zip(inner, ramp):
        P.tone[r, m[r]] = t
    for c in (c0, c1):                                  # round the ends
        P.mat[top, c] = 0; P.mat[bot, c] = 0
    for bx in bands:
        c, _ = cv.cell(bx, y0)
        P.tone[top + 1:bot, c] = np.maximum(1, P.tone[top + 1:bot, c] - 2)
    P.tone[top + 1:bot, c0 + 1] = np.minimum(7, P.tone[top + 1:bot, c0 + 1] + 1)   # lit front rim
    P.tone[top + 1, c0 + 1] = 7
    P.tone[top + 1:bot, c1 - 1] = np.maximum(1, P.tone[top + 1:bot, c1 - 1] - 1)   # aft cap
    outlined(P)
    return P


# -------------------------------------------------------------------------------------------------------- decals
def shark(fus):
    """shark mouth after the colour profile: red mouth, raked white teeth three cells apart that interlock, a dark
    lip line all round, pointed corner with the cheek line running back"""
    D = cv.layer('Shark')
    # the lower jaw rides just above the turret notch, so the mouth is a wedge that deepens toward the corner
    # the lower jaw rides just above the turret notch, then drops behind the notch wall, so the mouth is a wedge
    # that opens toward the corner
    top = {10: 13.5, 11: 14.5}
    top.update({x: 14.5 for x in range(12, 17)})
    top.update({x: 15.5 for x in range(17, 25)})
    top.update({25: 14.5, 26: 13.5})
    bot = {10: 11.5, 11: 11.5, 12: 11.5, 13: 11.5, 14: 11.5, 15: 11.5, 16: 11.5, 17: 11.5, 18: 10.5, 19: 10.5,
           20: 10.5, 21: 9.5, 22: 8.5, 23: 8.5, 24: 9.5, 25: 10.5, 26: 12.5}
    mouth = np.zeros((H, W), bool)
    for x in top:
        for y in np.arange(top[x] - 1.0, bot[x] + 0.5, -1.0):
            c, r = cv.cell(x + 0.5, y)
            mouth[r, c] = True
    # red, brighter at the front, a dark throat at the back
    for r, c in zip(*np.nonzero(mouth)):
        x = c - OX
        k = (x - 10) / 13.0
        D.put(c, r, 'red', 4 if k < 0.2 else 3 if k < 0.5 else 2)
    dt = runs_from(mouth, 'top'); db = runs_from(mouth, 'bot')
    throat = mouth & (dt > 2) & (db > 2) & (X > 16.0)
    D.recolor(throat, tone=1)
    # teeth: bases two cells of every three along each jaw, tips raked back, upper and lower offset to interlock
    for r, c in zip(*np.nonzero(mouth)):
        x = c - OX
        if x < 11:
            continue
        n = dt[r, c] + db[r, c] - 1                          # interior height of this column
        if n <= 2:                                            # thin front of the mouth: upper teeth only
            if dt[r, c] == 1 and x % 2 == 0:
                D.put(c, r, 'white', 3)
            continue
        if dt[r, c] == 1 and x % 3 != 1:
            D.put(c, r, 'white', 3)
        elif dt[r, c] == 2 and x % 3 == 0 and n >= 4:
            D.put(c, r, 'white', 2)
        elif db[r, c] == 1 and x % 3 != 2:
            D.put(c, r, 'white', 2)
        elif db[r, c] == 2 and x % 3 == 1 and n >= 5:
            D.put(c, r, 'white', 1)
    # lip line all round, then the cheek line from the corner
    grow = mouth.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow |= shift(mouth, dy, dx)
    lip = grow & ~mouth
    D.fill(lip, 'red', 0)
    for (x, y, t) in [(27.5, 13.5, 0), (28.5, 14.5, 0), (29.5, 14.5, 0)]:
        D.P(x, y, 'red', t)
    D.erase(~fus | Layer.edge_of(fus))
    return D


FONT = {
    'U': ['X.X', 'X.X', 'X.X', 'XXX'], 'S': ['XXX', 'XX.', '..X', 'XXX'], 'A': ['.X.', 'X.X', 'XXX', 'X.X'],
    'R': ['XX.', 'X.X', 'XX.', 'X.X'], 'M': ['X.X', 'XXX', 'X.X', 'X.X'], 'Y': ['X.X', 'X.X', '.X.', '.X.'],
    '.': ['.', '.', '.', 'X'], ' ': ['.', '.', '.', '.'],
}


def stencil(text, x0, y_top, flip):
    D = cv.layer('Marks')
    cols = []
    for ch in text:
        g = FONT[ch]
        for i in range(len(g[0])):
            cols.append([row[i] for row in g])
        cols.append(['.'] * 4)
    cols = cols[:-1]
    c0, r0 = cv.cell(x0, y_top)
    wtxt = len(cols)
    if flip:
        c0 = W - (c0 + wtxt)
    for i, col in enumerate(cols):
        for j, v in enumerate(col):
            if v == 'X':
                D.put(c0 + i, r0 + j, 'ink', 1)
    return D


# -------------------------------------------------------------------------------------------------------- rotors
RW, RH, RSTRIDE = 128, 9, 10          # main rotor frame, cells (2x: 256 x 18, stacked every 20 px like the Apache)
RHUB = (64.0, 3.5)                    # hub centre in frame cells (x, row centre)
RR = 62.5                             # blade radius in cells (Apache convention, 252 px tip to tip)


def rotor_frame(theta):
    a = np.zeros((RH, RW, 4), np.uint8)
    def put(c, r, mat, t, al=255):
        if 0 <= c < RW and 0 <= r < RH:
            a[r, int(c), :3] = RAMPS[mat][t]; a[r, int(c), 3] = al
    ct, st = np.cos(theta), np.sin(theta)
    cx = RHUB[0]
    # blades: A points (cos, sin), B opposite; sin > 0 means A leans away from the viewer
    for sgn, near in ((1, st <= 0), (-1, st > 0)):
        L = RR * abs(ct)
        d = sgn * np.sign(ct) if abs(ct) > 1e-6 else sgn
        chord = 3.6 * abs(st)                        # blade chord foreshortening near end-on
        x_root = 3.0
        x_tip = max(L, chord)
        xs = np.arange(x_root, x_tip + 0.001, 1.0)
        for i, u in enumerate(xs):
            c = int(np.floor(cx + d * u)) if d > 0 else int(np.floor(cx - u))
            tip = x_tip - u < 2.0
            if tip:
                put(c, 3, 'yellow', 3 if near else 1)
            else:
                glint = near and 0.45 < u / RR < 0.62
                put(c, 3, 'dark', 5 if glint else (2 if near else 1))
                if u < 7:                            # grip and cuff: thicker near the hub
                    put(c, 4, 'dark', 1 if near else 0)
        # end-on: the near blade tip reads as a short yellow chord slice over the hub
    # hub: yoke, grips (their width follows the rotation), mast nut
    gw = 1.5 + 3.0 * abs(ct)
    for u in np.arange(-gw, gw + 0.01, 1.0):
        put(int(np.floor(cx + u)), 3, 'steel', 3)
        put(int(np.floor(cx + u)), 4, 'steel', 1)
    for u in (-1, 0):
        put(int(cx + u), 2, 'steel', 5 if u < 0 else 3)
        put(int(cx + u), 1, 'steel', 6 if u < 0 else 4)
    # pitch links down to the swashplate, leading the blades by 90 degrees
    for k in (1, -1):
        px_ = cx + k * 2.4 * st
        for r in (5, 6, 7):
            put(int(np.floor(px_)), r, 'steel', 4 if k > 0 else 2)
    return a


def rotor_sheet():
    frames = [rotor_frame(np.radians(30 * i)) for i in range(6)]
    sheet = np.zeros((RSTRIDE * 6, RW, 4), np.uint8)
    for i, f in enumerate(frames):
        sheet[i * RSTRIDE:i * RSTRIDE + RH] = f
    blur = np.zeros((RH, RW, 4), np.uint8)
    col = np.array(RAMPS['dark'][3], np.uint8)
    for c in range(RW):
        u = abs(c + 0.5 - RHUB[0]) / RR
        if u > 1.0:
            continue
        near_hub = 1.0 - u
        for r, base, gain in ((2, 42, 22), (3, 90, 48), (4, 70, 40), (5, 38, 16)):
            blur[r, c, :3] = col; blur[r, c, 3] = int(base + gain * near_hub)
        if u > 0.965:
            blur[3, c, :3] = RAMPS['yellow'][2]; blur[3, c, 3] = 120
    hub = rotor_frame(0.0)
    hc = slice(int(RHUB[0]) - 5, int(RHUB[0]) + 5)
    m = hub[:, hc, 3] > 0
    blur[:, hc][m] = hub[:, hc][m]
    return sheet, blur


TR = 29                                # tail rotor canvas cells, hub at the centre cell


def tail_rotor():
    a = np.zeros((TR, TR, 4), np.uint8)
    def put(c, r, mat, t, al=255):
        if 0 <= c < TR and 0 <= r < TR:
            a[r, c, :3] = RAMPS[mat][t]; a[r, c, 3] = al
    c0 = TR // 2
    R = 13
    for sgn in (1, -1):
        for u in range(2, R + 1):
            c = c0 + sgn * u
            tip = u > R - 2
            # planform: leading edge row lit, trailing row dark (blade is seen flat)
            put(c, c0 - 1, 'yellow' if tip else 'dark', 3 if tip else 6)
            put(c, c0, 'yellow' if tip else 'dark', 1 if tip else 1)
    # hub and pitch change plate
    for dc in (-1, 0, 1):
        for dr in (-1, 0, 1):
            put(c0 + dc, c0 + dr, 'steel', 3)
    put(c0, c0, 'steel', 6); put(c0 - 1, c0 - 1, 'steel', 5); put(c0 + 1, c0 + 1, 'steel', 1)
    for sgn in (1, -1):                                   # dark end caps so the tips read on a light sky
        put(c0 + sgn * (R + 1), c0 - 1, 'dark', 0); put(c0 + sgn * (R + 1), c0, 'dark', 0)
    for dc in (-2, 2):
        for dr in (-2, -1, 0, 1, 2):
            put(c0 + dc, c0 + dr, 'dark', 0)
    for dr in (-2, 2):
        for dc in (-1, 0, 1):
            put(c0 + dc, c0 + dr, 'dark', 0)
    # blur disc
    b = np.zeros((TR, TR, 4), np.uint8)
    yy, xx = np.mgrid[0:TR, 0:TR]
    rr = np.hypot(xx - c0, yy - c0)
    disc = rr <= R + 0.5
    b[disc, :3] = RAMPS['dark'][3]; b[disc, 3] = 58
    b[(rr > R - 0.9) & disc, :3] = RAMPS['dark'][1]; b[(rr > R - 0.9) & disc, 3] = 105
    b[(rr > R - 2.0) & (rr <= R - 0.9), :3] = RAMPS['yellow'][1]; b[(rr > R - 2.0) & (rr <= R - 0.9), 3] = 70
    b[(rr > 5.6) & (rr < 6.6), 3] = 70
    hub = (abs(xx - c0) <= 1) & (abs(yy - c0) <= 1)
    b[hub] = a[hub]
    return a, b


# ------------------------------------------------------------------------------------------------------- export
def to2x_offset(x, y):
    """reference point -> 2x pixel offset from the body texture centre (the draw origin in code)"""
    return [round((x + OX) * 2 - W, 1), round((OY - y) * 2 - H, 1)]


def build(write=True):
    os.makedirs(OUT, exist_ok=True)
    Lb, fus = body_full()
    layers = {
        'CobraBoss': Lb.render(),
        'CobraBoss_Canopy': canopy(fus).render(),
        'CobraBoss_Shark': shark(fus).render(),
        'CobraBoss_MarksL': stencil('U.S. ARMY', 70.2, 14.6, False).render(),
        'CobraBoss_MarksR': stencil('U.S. ARMY', 70.2, 14.6, True).render(),
        'CobraBoss_Turret': turret().render(),
        'CobraBoss_PodIn': pod(*POD_IN[:2], 7.4, 11.4, 'PodIn', bands=(41.0, 54.4)).render(),
        'CobraBoss_PodOut': pod(POD_OUT[0], POD_OUT[1], 6.4, 11.4, 'PodOut', bands=(40.4, 54.9)).render(),
    }
    guns, gpiv = gun_frames()
    gh = guns[0].shape[0]
    gun_sheet = np.zeros((len(guns) * (gh + 1) - 1, guns[0].shape[1], 4), np.uint8)
    for i, g in enumerate(guns):
        gun_sheet[i * (gh + 1):i * (gh + 1) + gh] = g
    layers['CobraBoss_Gun'] = gun_sheet
    rs, rb = rotor_sheet()
    layers['CobraBoss_MainRotor'] = rs
    layers['CobraBoss_MainRotorBlur'] = rb
    tr, trb = tail_rotor()
    layers['CobraBoss_TailRotor'] = tr
    layers['CobraBoss_TailRotorBlur'] = trb
    mast_col = cv.cell(MAST_X, 0)[0]
    coords = {
        'note': '2x pixels. Offsets are from the CobraBoss.png centre with the nose to the left (flip x when facing right). '
                'Sheet frames list their own origin in frame pixels.',
        'body_size': [W * 2, H * 2],
        'rotor_axis': [(51.0) * 2 - W, round((1.5) * 2 - H, 1)],
        'rotor_frame': {'size': [RW * 2, RH * 2], 'stride': RSTRIDE * 2, 'frames': 6, 'deg_per_frame': 30,
                        'hub': [RHUB[0] * 2, RHUB[1] * 2]},
        'tail_rotor_hub': to2x_offset(137.5, 29.5),
        'tail_rotor_frame': {'size': [TR * 2, TR * 2], 'hub': [TR, TR]},
        'gun_pivot': to2x_offset(*GUN_PIVOT),
        'gun_frame': {'size': [guns[0].shape[1] * 2, gh * 2], 'stride': (gh + 1) * 2, 'frames': len(guns),
                      'pivot': [gpiv[0] * 2, gpiv[1] * 2], 'barrel_length': gpiv[0] * 2,
                      'frame_use': '0 rest, 1 recoil', 'aim_limits_deg': {'up': 20, 'down': 60}},
        'pod_out_muzzle': to2x_offset(POD_OUT[0], 8.9),
        'pod_in_muzzle': to2x_offset(POD_IN[0], 9.4),
        'pod_out_centre': to2x_offset((POD_OUT[0] + POD_OUT[1]) / 2, 8.9),
        'exhaust': to2x_offset(75.0, 22.6),
        'beacon': to2x_offset(54.0, 35.5),
        'wingtip_light': to2x_offset(42.0, 14.4),
        'pitot_tip': to2x_offset(-2.5, 14.2),
        'skid_bottom_y': round(OY * 2 - H, 1),
        'hitbox_suggest': [290, 64],
    }
    if write:
        for k, a in layers.items():
            save2(a, os.path.join(OUT, k + '.png'))
        with open(os.path.join(OUT, 'CobraBoss_coords.json'), 'w') as f:
            json.dump(coords, f, indent=1)
    return layers, coords


if __name__ == '__main__':
    layers, coords = build()
    print(json.dumps(coords, indent=1))
