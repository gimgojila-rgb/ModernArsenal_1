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
  CobraBoss_Turret.png     square drum chin turret in the notch; draw after the gun so it hides the barrel root
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
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
DITHER = BAYER[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4]      # ordered dither threshold per cell
LONGERON_Y = 17.4                    # upper longeron: the side rolls in toward the deck above it
HUMP_BASE_Y = 27.4


def body():
    """fuselage skin. Light comes from above and a little ahead, as on the Apache sprites. The Cobra is a narrow
    slab: flat sides, the upper side rolling in above the longeron (a bright band along it), a rounded belly with a
    line of reflected light just inside the outline"""
    L = cv.layer('Body')
    fus = L.poly(FUSELAGE, 'od', 4)
    cx0, cx1, cy0, cy1 = CAVITY
    cav = (X > cx0) & (X < cx1) & (Y > cy0) & (Y < cy1)
    fus = fus | cav
    glass = cv.cov_poly(GLASS) >= 0.5
    dtop = runs_from(fus, 'top'); dbot = runs_from(fus, 'bot')
    sill_y = interp_y(SILL, X)
    bt = interp_y(BOOM_TOP, X)

    # --- nose, below the canopy: a blunt cone, lit on its upper cheek, dark under the chin
    nose = fus & (X < 22.4) & ~glass
    L.recolor(nose & (Y > sill_y - 2.2), tone=6)
    L.recolor(nose & (Y <= sill_y - 2.2) & (Y > sill_y - 4.2), tone=5)
    L.recolor(nose & (Y <= sill_y - 4.2), tone=4)
    L.recolor(nose & (dbot <= 3), tone=3)
    L.recolor(nose & (X < 1.2) & (dbot > 1) & (dtop > 1) & (Y < 13.2), tone=3)
    L.P(1.5, 14.4, 'od', 7); L.P(2.5, 14.9, 'od', 7); L.P(0.6, 13.6, 'od', 6)

    # --- centre section side (behind the notch, under the hump)
    side = fus & (X >= 22.4) & (X < 72.5) & (Y <= HUMP_BASE_Y) & ~glass
    L.recolor(side & (Y > LONGERON_Y), tone=5)
    L.recolor(side & (Y > LONGERON_Y) & (Y < LONGERON_Y + 2.0), tone=6)
    L.recolor(side & (Y < 11.2), tone=3)
    L.recolor(side & (dbot <= 3), tone=2)
    # sill: a lit ledge under the canopy rail, a dark shadow line under it
    for x in np.arange(8.9, 37.5, 1.0):
        L.P(x, interp_y(SILL, x) - 0.2, 'od', 7 if 12 < x < 30 else 6)
        L.P(x, interp_y(SILL, x) - 1.2, 'od', 4)

    # --- hump (transmission fairing, engine cowl, aft fairing): a rounded roof over flat sides
    hump = fus & (X >= 37.6) & (X < 72.5) & (Y > HUMP_BASE_Y)
    L.recolor(hump, tone=5)
    L.recolor(hump & (dtop == 3), tone=6)
    L.recolor(hump & (dtop == 2), tone=7)
    L.recolor(hump & (Y < HUMP_BASE_Y + 2.0) & (dtop > 3), tone=4)
    fr = fus & (X >= 37.6) & (X < 41.2) & (Y > HUMP_BASE_Y + 0.2)             # front slope faces forward and up
    L.recolor(fr & (dtop <= 3) & (dtop > 1), tone=7)
    L.recolor(fr & (dtop == 2) & (X > 38.6), tone=8)
    L.recolor(fr & (dtop == 4), tone=6)
    rs = fus & (X >= 62.4) & (X < 72.5) & (Y > 25.0)                          # rear slope turns away
    L.recolor(rs & (dtop > 1), tone=4)
    L.recolor(rs & (dtop == 2), tone=5)
    L.recolor(rs & (dtop > 4) & (Y < 26.5), tone=3)

    # --- engine nacelle: a horizontal cylinder bulging out of the cowl side
    nt = interp_y(NACELLE_TOP, X); nb = interp_y(NACELLE_BOT, X)
    nac = fus & (X > INTAKE[2] - 0.2) & (X < 72.3) & (Y < nt) & (Y > nb)
    L.recolor(nac, tone=4)
    L.recolor(nac & (Y > nt - 1.0), tone=7)
    L.recolor(nac & (Y > nt - 1.0) & (X > 54.0) & (X < 61.0), tone=8)
    L.recolor(nac & (Y <= nt - 1.0) & (Y > nt - 2.4), tone=6)
    L.recolor(nac & (Y <= nt - 2.4) & (Y > nt - 3.6), tone=5)
    L.recolor(nac & (Y < nb + 2.2), tone=3)
    L.recolor(nac & (Y < nb + 1.0), tone=2)
    L.recolor(fus & (X > INTAKE[0]) & (X < 72.2) & (Y < nb) & (Y > nb - 1.0), tone=1)     # its shadow on the side
    L.recolor(fus & (X > INTAKE[0]) & (X < 72.2) & (Y < nb - 1.0) & (Y > nb - 2.0), tone=3)
    L.recolor(fus & (X > INTAKE[2]) & (X < 64.6) & (Y > nt) & (Y < nt + 1.0), tone=2)      # crease above it

    # --- engine air intake: rounded dark mouth with a lit lip and a screen
    x0, y0, x1, y1 = INTAKE
    it = L.fill((X > x0) & (X < x1) & (Y > y0) & (Y < y1) & fus, 'dark', 1)
    for yy in np.arange(y0 + 1.0, y1 - 0.5, 2.0):
        L.recolor(it & (Y > yy) & (Y < yy + 1.0) & (X > x0 + 1.0), tone=3)
    L.recolor(it & (X < x0 + 1.0), tone=0)
    L.recolor(it & (Y > y1 - 1.0), tone=0)
    for (x, y) in ((x0 + 0.5, y1 - 0.5), (x1 - 0.5, y1 - 0.5), (x0 + 0.5, y0 + 0.5), (x1 - 0.5, y0 + 0.5)):
        L.P(x, y, 'od', 3)                                                    # rounded corners
    L.recolor(fus & (X > x0 - 1) & (X < x0) & (Y > y0) & (Y < y1), tone=7)    # lit lip in front
    L.recolor(fus & (X > x0 - 2) & (X < x0 - 1) & (Y > y0) & (Y < y1), tone=5)
    L.recolor(fus & (X > x0) & (X < x1) & (Y > y0 - 1) & (Y < y0), tone=6)    # lit sill under it

    # --- exhaust nozzle: steel, heat tinted, the rim catching the light
    noz = fus & (X > 72.3) & (X < 75.4) & (Y > 19.2) & (Y < 26.2)
    L.recolor(noz, mat='steel', tone=3)
    L.recolor(noz & (Y > 24.0), tone=6)
    L.recolor(noz & (Y > 22.4) & (Y <= 24.0), tone=4)
    L.recolor(noz & (Y < 21.2), tone=1)
    L.recolor(noz & (X < 73.2) & (Y > 21.2), mat='burnt', tone=4)
    L.recolor(noz & (X < 73.2) & (Y > 23.6), mat='burnt', tone=5)
    L.recolor(noz & (X > 74.0), mat='steel', tone=5)
    L.recolor(noz & (X > 74.0) & (Y > 24.0), tone=7)
    L.recolor(noz & (X > 74.0) & (Y < 21.8), tone=2)
    L.recolor(fus & (X > 71.4) & (X < 72.4) & (Y > 19.6) & (Y < 25.6), mat='od', tone=1)

    # --- tail boom: driveshaft cover on top, its shadow, a bright band where the boom's upper side rolls, then down
    # to a dark keel with reflected light at the very bottom
    boom = fus & (X >= 72.3) & (X < 121.5) & ~noz
    L.recolor(boom, tone=4)
    L.recolor(boom & (Y < bt) & (Y > bt - 1.7), tone=5)
    L.recolor(boom & (dtop == 2), tone=6)
    L.recolor(boom & (Y <= bt - 1.7) & (Y > bt - 2.7), tone=2)
    L.recolor(boom & (Y <= bt - 2.7) & (Y > bt - 3.7), tone=7)
    L.recolor(boom & (Y <= bt - 3.7) & (Y > bt - 5.7), tone=5)
    L.recolor(boom & (dbot <= 4), tone=3)
    L.recolor(boom & (dbot <= 2), tone=2)
    # cover segments: short dark joints with a lit lip, every 5 cells
    for x in np.arange(79.5, 119, 5.0):
        c, r = cv.cell(x, interp_y(BOOM_TOP, x) - 0.6)
        if fus[r, c]:
            L.tone[r, c] = 3; L.tone[r, c + 1] = 7

    # --- fin: a thick aerofoil, rounded lit leading edge carrying the driveshaft cover up to the 90 degree gearbox
    fin = fus & (X >= 120.8) & (Y > interp_y(BOOM_TOP, X) - 0.2)
    le_x = interp_y([(p[1], p[0]) for p in FIN_LE], Y)
    te_x = interp_y([(p[1], p[0]) for p in FIN_TE], Y)
    L.recolor(fin, tone=5)
    L.recolor(fin & (X < le_x + 4.6), tone=6)
    L.recolor(fin & (X < le_x + 1.6) & (dtop > 1), tone=7)
    L.recolor(fin & (X > te_x - 4.0) & (Y > 16), tone=4)
    L.recolor(fin & (X > te_x - 1.6) & (Y > 16), tone=3)
    L.recolor(fin & (Y < 19.6) & (X > le_x + 1.6), tone=4)                                # root, in the boom's shade
    L.recolor(fin & (Y > 32.4) & (dtop > 1), tone=6)                                      # tip cap

    # 42 degree gearbox fairing at the fin root
    L.recolor(fus & (cv.cov_ell(121.6, 18.6, 2.4, 1.6) >= 0.5), tone=5)
    L.recolor(fus & (cv.cov_ell(121.2, 19.2, 1.4, 0.8) >= 0.5), tone=7)
    L.recolor(fus & (cv.cov_ell(121.6, 18.6, 2.4, 1.6) >= 0.5) & (Y < 17.8), tone=3)

    # tail rotor gearbox fairing on the fin
    gb = cv.cov_ell(TAIL_HUB[0] + 0.4, TAIL_HUB[1] - 0.3, 3.1, 2.8) >= 0.5
    L.fill(gb & fus, 'od', 4)
    L.recolor(gb & (cv.cov_ell(TAIL_HUB[0] - 0.4, TAIL_HUB[1] + 0.4, 2.0, 1.8) >= 0.5), tone=6)
    L.P(TAIL_HUB[0] - 1.0, TAIL_HUB[1] + 1.2, 'od', 7)
    L.recolor(gb & (Y < TAIL_HUB[1] - 1.4), tone=2)
    ge = gb & ~(shift(gb, 1, 0) & shift(gb, -1, 0) & shift(gb, 0, 1) & shift(gb, 0, -1))
    L.recolor(ge & fus & ~Layer.edge_of(fus), tone=2)

    # the turret notch: shadowed recess, its rear wall catching light
    L.fill(cav, 'dark', 1)
    L.recolor(cav & (Y > cy1 - 1.0), tone=0)
    L.recolor(cav & (X > cx1 - 1.0), tone=2)
    L.fill(fus & (X > cx1) & (X < cx1 + 1.0) & (Y > cy0 + 0.6) & (Y < cy1), 'od', 6)

    # cockpit interior under the glass (shows if the canopy layer is left off)
    L.fill(glass & fus & (dtop > 1), 'dark', 2)

    L._fus = fus
    return L, fus


def finish_skin(L, fus):
    """weathering and the outline, after all the panel work"""
    bt = interp_y(BOOM_TOP, X)
    od = L.is_mat('od')
    inner = fus & ~Layer.edge_of(fus) & od
    # exhaust soot: a stepped darker patch over the boom top that ends in a ragged edge, no dither
    soot = inner & (X > 75.2) & (Y > bt - 3.7 - np.clip((84 - X) / 3.0, 0, 3)) & (X < 84 + 3 * ((Y * 2).astype(int) % 2))
    L.tone[soot] = np.maximum(1, L.tone[soot] - 1)
    # --- outline last (outer edge of the whole fuselage): near-black, a shade lighter along the lit top
    e = Layer.edge_of(fus)
    L.fill(e, 'od', 0)


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


def groove(L, fus, pts, skip=None, rivet=0, roff=-1, bevel=False, dt=-2):
    """a panel line cut into the skin: a dark groove with its far wall lit (the cell below a horizontal line, to the
    right of a vertical one), optional rivet row beside it (every `rivet` cells, `roff` cells to the other side)"""
    inner = fus & ~Layer.edge_of(fus) & L.is_mat('od')
    if skip is not None:
        inner &= ~skip
    def ok(c, r):
        return 0 <= c < W and 0 <= r < H and inner[r, c]
    line = []
    for a, b in zip(pts[:-1], pts[1:]):
        horiz = abs(b[0] - a[0]) >= abs(b[1] - a[1])
        for c, r in L.cells(a[0], a[1], b[0], b[1]):
            if (c, r) not in [p[:2] for p in line]:
                line.append((c, r, horiz))
    cellset = {(c, r) for c, r, _ in line}
    for c, r, _ in line:
        if ok(c, r):
            L.tone[r, c] = max(1, min(L.tone[r, c], 4) + dt)
    if bevel:
        for c, r, horiz in line:
            cc, rr = (c, r + 1) if horiz else (c + 1, r)
            if ok(cc, rr) and (cc, rr) not in cellset:
                L.tone[rr, cc] = min(8, L.tone[rr, cc] + 1)
    if rivet:
        for i, (c, r, horiz) in enumerate(line):
            if i % rivet:
                continue
            cc, rr = (c, r + roff) if horiz else (c + roff, r)
            if ok(cc, rr) and (cc, rr) not in cellset:
                L.tone[rr, cc] = min(8, L.tone[rr, cc] + 1)


def dots(L, fus, x0, x1, y, every=3, skip=None, dt=2):
    """a rivet row: light dots every `every` cells along a height (a number or a function of x)"""
    inner = fus & ~Layer.edge_of(fus) & L.is_mat('od')
    if skip is not None:
        inner &= ~skip
    for x in np.arange(x0, x1 + 0.01, every):
        yy = y(x) if callable(y) else y
        c, r = cv.cell(x, yy)
        if 0 <= c < W and 0 <= r < H and inner[r, c]:
            L.tone[r, c] = min(8, L.tone[r, c] + dt)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


def latch(L, x, y):
    """a flush latch: dark slot with a lit lip under it"""
    L.P(x, y, 'od', 1); L.P(x + 1, y, 'od', 2); L.P(x, y - 1, 'od', 6)


def details(L, fus):
    glass = cv.cov_poly(GLASS) >= 0.5
    ix0, iy0, ix1, iy1 = INTAKE
    keep = glass | ((X > ix0 - 2.1) & (X < ix1 + 0.1) & (Y > iy0 - 1.1) & (Y < iy1 + 0.1))
    # --- stations (vertical joints): plain dark lines, as on the Apache
    groove(L, fus, [(9.6, 9.8), (9.6, 14.2)])                                  # nose cone joint
    groove(L, fus, [(22.7, 5.5), (22.7, 16.9)], skip=keep)
    groove(L, fus, [(34.6, 5.2), (34.6, 19.4)], skip=keep)                    # cockpit aft bulkhead
    groove(L, fus, [(42.6, 5.4), (42.6, 27.0)], skip=keep)
    groove(L, fus, [(53.4, 5.2), (53.4, 20.2)], skip=keep)
    groove(L, fus, [(61.6, 5.2), (61.6, 20.0)], skip=keep)
    groove(L, fus, [(68.6, 5.4), (68.6, 19.6)], skip=keep)                    # tail boom joint
    for x in (85.2, 99.0, 112.4):
        groove(L, fus, [(x, interp_y(BOOM_BOT, x) + 1.2), (x, interp_y(BOOM_TOP, x) - 2.0)])
    # --- longitudinal joints
    groove(L, fus, [(22.8, LONGERON_Y), (48.0, LONGERON_Y)], skip=keep)
    groove(L, fus, [(51.4, LONGERON_Y), (72.0, LONGERON_Y)], skip=keep)
    groove(L, fus, [(22.8, 8.6), (68.6, 8.6)], skip=keep)                    # belly panel
    groove(L, fus, [(38.6, HUMP_BASE_Y), (62.6, HUMP_BASE_Y)], skip=keep)    # hump sits on the deck
    # --- rivet rows: light dots down the middle of the panels (the Apache's look)
    for x0, x1 in ((23.5, 34.0), (35.5, 42.0), (43.5, 53.0), (54.5, 61.0), (62.5, 68.0)):
        dots(L, fus, x0, x1, 15.5, skip=keep)
        dots(L, fus, x0, x1, 10.5, skip=keep)
    for x0, x1 in ((69.5, 85.0), (86.5, 99.0), (100.0, 112.0), (113.5, 119.0)):
        dots(L, fus, x0, x1, lambda x: interp_y(BOOM_TOP, x) - 4.4)
    dots(L, fus, 43.5, 52.5, 29.5, skip=keep)
    # --- hump: transmission cowl door with latches, engine cowl door with cooling louvres
    groove(L, fus, rect(40.9, 28.6, 46.4, 33.2), dt=-2)
    latch(L, 43.5, 29.4); latch(L, 45.5, 32.4)
    groove(L, fus, [(53.4, 28.4), (53.4, 33.4)])
    groove(L, fus, rect(54.4, 28.8, 61.4, 32.6), dt=-2)
    for y in (31.5, 29.5):                                                    # cooling louvres: slit, lit lip
        L.line(55.6, y, 60.2, y, 'dark', 1, only=fus)
        L.line(55.6, y - 1.0, 60.2, y - 1.0, 'od', 6, only=fus)
    latch(L, 62.5, 30.4)
    # --- side doors: avionics bay under the pilot, ammunition bay and fuel filler aft of the wing
    groove(L, fus, rect(26.6, 10.0, 32.8, 15.2), rivet=0)
    latch(L, 31.5, 14.2); latch(L, 31.5, 11.2)
    groove(L, fus, rect(62.6, 7.6, 66.4, 12.8))
    latch(L, 65.5, 11.8)
    L.P(67.6, 10.2, 'od', 1); L.P(68.0, 10.2, 'od', 2); L.P(67.6, 9.2, 'od', 6)     # fuel cap
    # oil level window on the cowl
    L.fill((X > 56.2) & (X < 57.9) & (Y > 24.2) & (Y < 26.6) & fus, 'dark', 1)
    L.P(56.6, 25.8, 'glass', 5); L.P(57.4, 24.8, 'glass', 3)
    # kick-in steps under the cockpits
    for (x, y) in [(24.5, 7.5), (36.5, 12.5)]:
        L.P(x, y, 'dark', 0); L.P(x, y - 1, 'od', 6)
    # position light on the fin tip, anti-collision strobe on the boom (lenses neutral, tinted in code)
    L.P(147.5, 33.0, 'white', 2)
    # fin: driveshaft cover edge behind the leading edge, the tip cap joint
    groove(L, fus, [(126.4, 19.6), (139.4, 30.2)], dt=-2)
    groove(L, fus, [(141.2, 32.4), (147.6, 32.4)], dt=-1)


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
    finish_skin(L, fus)
    mast_beacon_pitot(L)
    G = skid_gear()
    E_, T, A = elevator_skid_antenna()
    R, Wg = wing_and_racks()
    for part in (A, T, E_, G, R, Wg):
        merge(L, part)
    return L, fus


# ------------------------------------------------------------------------------------------------------- canopy
def canopy(fus):
    """glass after the Apache canopy: sky reflected in the upper glass, darker toward the sill, two broad glints per
    pane, black frames. Only the headrests show through."""
    C = cv.layer('Canopy')
    skin_edge = Layer.edge_of(fus)
    g = (cv.cov_poly(GLASS) >= 0.5) & fus & ~skin_edge
    C.fill(g, 'glass', 4)
    dt = runs_from(g, 'top'); db = runs_from(g, 'bot')
    C.recolor(g & (dt <= 3), tone=5)
    C.recolor(g & (dt == 1), tone=6)
    C.recolor(g & (db <= 3), tone=3)
    C.recolor(g & (db <= 1), tone=2)
    # headrests through the glass (gunner's, pilot's)
    for poly in ([(17.2, 20.0), (19.0, 20.4), (19.2, 22.6), (17.6, 22.6)],
                 [(33.2, 22.0), (35.2, 22.6), (35.6, 25.0), (33.8, 25.0)]):
        m = (cv.cov_poly(poly) >= 0.45) & g
        C.recolor(m, tone=2)
        C.recolor(m & (runs_from(m, 'top') == 1), tone=3)
    # glints: broad bar then a thin one, raked like the Apache's
    for (xa, ya, xb, yb) in [(10.6, 16.6, 15.8, 25.4), (25.2, 19.8, 29.6, 27.2)]:
        for k, t in ((0.0, 7), (1.0, 7), (2.0, 6)):
            C.line(xa + k, ya, xb + k, yb, 'glass', t, only=g)
        C.line(xa + 4.0, ya, xb + 4.0, yb, 'glass', 6, only=g)
    # frames: front bow, gunner / pilot divider (with its lit edge), rear bow, bottom rail
    C.line(*FRONT_FRAME[0], *FRONT_FRAME[1], 'od', 0, only=fus)
    C.line(*DIVIDER[0], *DIVIDER[1], 'od', 0, only=fus)
    C.line(DIVIDER[0][0] + 1.0, DIVIDER[0][1] - 0.4, DIVIDER[1][0] + 1.0, DIVIDER[1][1] + 0.3, 'od', 5, only=g)
    C.line(*REAR_FRAME[0], *REAR_FRAME[1], 'od', 0, only=fus)
    gb = interp_y(GLASS_BOT, X); sl = interp_y(SILL, X)
    rail = fus & ~skin_edge & (X > 8.2) & (X < 38.2) & (Y < gb + 0.5) & (Y > sl)
    C.fill(rail & ~g, 'od', 1)
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
    """shark mouth after the colour profile: a wedge opening back to a pointed corner, red inside going to a dark
    throat, triangular white teeth (two-cell base, one-cell tip) on both jaws, interlocking, a dark lip all round and
    a cheek line from the corner. The lower lip rides just above the turret notch."""
    D = cv.layer('Shark')
    xs = list(range(10, 28))
    top = [13, 13, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15, 15, 14, 14, 13, 13]      # interior rows (cell y)
    bot = [12, 12, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 13]
    mouth = np.zeros((H, W), bool)
    T = {}; B_ = {}
    for x, t, b in zip(xs, top, bot):
        T[x], B_[x] = t, b
        for y in range(b, t + 1):
            c, r = cv.cell(x + 0.5, y + 0.5)
            mouth[r, c] = True
    for r, c in zip(*np.nonzero(mouth)):
        x = c - OX
        D.put(c, r, 'red', 4 if x < 13 else 3 if x < 18 else 2)
    dtm = runs_from(mouth, 'top'); dbm = runs_from(mouth, 'bot')
    D.recolor(mouth & (dtm > 1) & (dbm > 1) & (X > 18.0), tone=1)              # throat
    D.recolor(mouth & (dtm > 1) & (dbm > 1) & (X > 22.0), tone=0)

    def tooth(x, y_base, down):
        c, r = cv.cell(x + 0.5, y_base + 0.5)
        for dc in (0, 1):
            if mouth[r, c + dc]:
                D.put(c + dc, r, 'white', 3)
        rt = r + 1 if down else r - 1
        if 0 <= rt < H and mouth[rt, c] and (T[x] - B_[x] >= 2):
            D.put(c, rt, 'white', 1)
    for x in range(11, 24, 3):                    # upper teeth hang from the top row
        tooth(x, T[x], True)
    for x in range(13, 23, 3):                    # lower teeth stand on the bottom row, between the upper ones
        tooth(x, B_[x], False)
    # dark lip all round, the cheek line from the corner
    grow = mouth.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grow |= shift(mouth, dy, dx)
    D.fill(grow & ~mouth, 'red', 0)
    for (x, y) in [(28.5, 13.5), (29.5, 14.5)]:
        D.P(x, y, 'red', 0)
    D.erase(~fus | Layer.edge_of(fus))
    return D


FONT = {
    'U': ['X.X', 'X.X', 'X.X', 'XXX'], 'S': ['.XX', 'X..', '..X', 'XX.'], 'A': ['.X.', 'X.X', 'XXX', 'X.X'],
    'R': ['XX.', 'X.X', 'XX.', 'X.X'], 'M': ['X...X', 'XX.XX', 'X.X.X', 'X...X'], 'Y': ['X.X', 'X.X', '.X.', '.X.'],
    '.': ['.', '.', '.', 'X'], ' ': ['', '', '', ''],          # a space is just one more gap
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
        'CobraBoss_MarksL': stencil('U.S. ARMY', 67.6, 13.6, False).render(),
        'CobraBoss_MarksR': stencil('U.S. ARMY', 67.6, 13.6, True).render(),
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
