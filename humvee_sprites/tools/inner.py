"""Internal layers: frame & running gear, powertrain, cabin interior, wheel-well liners."""
import numpy as np
from pix import *
from ext import REAR_ARCH, FRONT_ARCH, DOOR_R, DOOR_F, arch_y

def band(L, m, top=None, bot=None, rows=1):
    """shade a component: top rows lighter, bottom rows darker"""
    ys = np.where(m.any(1))[0]
    if len(ys) == 0: return
    y0, y1 = ys.min(), ys.max()
    if top is not None:
        L.recolor(m & (np.arange(L.h)[:, None] < y0 + rows), tone=top)
    if bot is not None:
        L.recolor(m & (np.arange(L.h)[:, None] > y1 - rows), tone=bot)

def box(L, x0, y0, x1, y1, mat, base, hi=None, lo=None):
    m = L.rect(x0, y0, x1, y1, mat, base)
    if hi is not None: L.rect(x0, y0, x1, y0 + 1, mat, hi)
    if lo is not None: L.rect(x0, y1 - 1, x1, y1, mat, lo)
    return m

# ================================================================== FRAME & RUNNING GEAR
def make_frame():
    L = Layer('Frame')
    # --- suspension (behind rails): coil-over, A-arms, portal hub
    for wx in (22.5, 90.5):
        cx = int(wx)
        # upper / lower A-arm silhouettes
        L.poly([(wx - 5.5, 35.2), (wx + 5.5, 35.2), (wx + 2.0, 37.4), (wx - 2.0, 37.4)], 'chassis', 3)
        L.poly([(wx - 6.5, 43.0), (wx + 6.5, 43.0), (wx + 2.5, 45.2), (wx - 2.5, 45.2)], 'chassis', 3)
        L.rect(cx - 6, 35, cx + 6, 36, 'chassis', 4)
        L.rect(cx - 6, 43, cx + 7, 44, 'chassis', 4)
        # portal geared hub
        box(L, cx - 2, 37, cx + 3, 46, 'chassis', 3, 4, 1)
        L.rect(cx - 1, 39, cx + 2, 44, 'chassis', 2)
        L.P(cx, 40, 'chassis', 4)
        # coil spring over shock
        for i, y in enumerate(range(26, 37)):
            L.rect(cx - 2, y, cx + 3, y + 1, 'steel', 4 if i % 2 == 0 else 2)
            L.P(cx - 2 + (i % 2) * 4, y, 'steel', 5 if i % 2 == 0 else 1)
        L.rect(cx, 25, cx + 1, 37, 'black', 3)      # shock body through the coil
        L.rect(cx - 2, 25, cx + 3, 26, 'steel', 3)   # top perch
        L.P(cx - 2, 25, 'steel', 5)
    # --- differentials (behind hubs, a bit inboard)
    for wx in (22.5, 90.5):
        L.ell(wx, 40.5, 2.6, 2.2, 'alu', 2)
    # --- driveshafts
    L.rect(26, 39, 58, 40, 'steel', 4); L.rect(26, 40, 58, 41, 'steel', 2)
    L.rect(63, 39, 88, 40, 'steel', 4); L.rect(63, 40, 88, 41, 'steel', 2)
    for ux in (26, 57, 63, 87):
        L.rect(ux, 38, ux + 1, 42, 'steel', 5)
    # --- exhaust: manifold downpipe -> pipe -> muffler -> tail pipe (exits in front of rear wheel)
    L.rect(78, 37, 80, 40, 'rust', 2)
    L.rect(78, 37, 79, 40, 'rust', 3)
    L.rect(38, 40, 80, 41, 'rust', 3); L.rect(38, 41, 80, 42, 'rust', 1)
    box(L, 40, 38, 52, 42, 'rust', 2, 4, 1)
    L.rect(41, 39, 51, 40, 'rust', 3)
    for x in (43, 46, 49):
        L.P(x, 40, 'rust', 1)
    L.rect(36, 41, 40, 42, 'rust', 2); L.P(36, 42, 'black', 1); L.P(37, 42, 'black', 1)
    # --- fuel tank (right rear, above the axle, inboard)
    box(L, 24, 26, 37, 33, 'olive', 3, 5, 1)
    L.rect(24, 29, 37, 30, 'olive', 2)
    L.rect(25, 27, 26, 32, 'olive', 4)
    L.rect(31, 23, 33, 26, 'black', 2)            # filler neck to the fuel door
    L.P(31, 23, 'black', 4)
    # --- ladder frame side rail (C-channel)
    rail = L.rect(8, 35, 104, 39, 'chassis', 3)
    L.rect(8, 35, 104, 36, 'chassis', 5)
    L.rect(8, 38, 104, 39, 'chassis', 1)
    L.rect(8, 36, 104, 37, 'chassis', 4)
    for hx in np.arange(12, 102, 6.5):              # lightening holes
        if abs(hx - 22.5) < 4 or abs(hx - 90.5) < 4: continue
        L.P(hx, 36.5, 'chassis', 0); L.P(hx + 1, 36.5, 'chassis', 0)
        L.P(hx, 37.5, 'chassis', 2); L.P(hx + 1, 37.5, 'chassis', 2)
    for rx in np.arange(10, 103, 3.25):             # rivets on the top flange
        L.P(rx, 35.2, 'chassis', 3)
    for cx in (14, 37, 58, 77, 101):                 # crossmember ends
        L.rect(cx, 35, cx + 2, 39, 'chassis', 2)
        L.rect(cx, 35, cx + 2, 36, 'chassis', 4)
    # --- front bumper + tow shackle (tan, bolted to frame)
    L.rect(101, 33, 107, 36, 'tan', 4)
    L.rect(101, 33, 107, 34, 'tan', 6)
    L.rect(101, 35, 107, 36, 'tan', 3)
    L.P(103, 34, 'tan', 3); L.P(105, 34, 'tan', 3)
    L.rect(103, 36, 106, 38, 'black', 2)
    L.P(104, 36, 'black', 0); L.P(103, 36, 'black', 3)
    # --- rear crossmember, pintle hook
    L.rect(7, 34, 11, 37, 'chassis', 2)
    L.rect(7, 34, 11, 35, 'chassis', 4)
    L.rect(6, 37, 10, 39, 'black', 2)
    L.P(6, 37, 'black', 4); L.P(6, 38, 'black', 3)
    L.P(5, 38, 'black', 2)
    return L

# ================================================================== POWERTRAIN
from sprites import PAL, ENGINE, SEAT, STEER, RADIO

def make_engine():
    L = Layer('Engine')
    # transfer case (under the tunnel, feeds both driveshafts)
    box(L, 57, 32, 63, 39, 'alu', 2, 4, 1)
    L.rect(58, 34, 62, 35, 'alu', 3)
    L.P(58, 36, 'alu', 4); L.P(61, 36, 'alu', 4); L.P(59, 38, 'alu', 1)
    # 4-speed automatic: ribbed case, pan below
    L.poly([(62.6, 31.0), (72.8, 30.4), (72.8, 36.4), (62.6, 36.4)], 'alu', 2)
    L.poly([(62.6, 31.0), (72.8, 30.4), (72.8, 31.4), (62.6, 32.0)], 'alu', 4)
    for x in range(64, 73, 2):
        L.rect(x, 32, x + 1, 36, 'alu', 3)
    L.rect(63, 36, 72, 37, 'black', 2)
    # bell housing flaring up to the engine
    L.poly([(72.6, 30.0), (78.6, 27.6), (78.6, 37.0), (72.6, 36.4)], 'alu', 3)
    L.poly([(72.6, 30.0), (78.6, 27.6), (78.6, 28.6), (72.6, 31.0)], 'alu', 5)
    L.P(74, 33, 'alu', 1); L.P(76, 32, 'alu', 1); L.P(76, 35, 'alu', 1)
    box(L, 74, 34, 77, 36, 'black', 2, 3, 1)                             # starter
    # engine proper (hand-placed map)
    stamp(L, ENGINE, 77, 22, PAL)
    return L

# ================================================================== CABIN SHELL (far walls, roof structure)
def make_cabin():
    L = Layer('Cabin')
    cab = L.poly([(36.8, 12.6), (73.6, 12.6), (73.6, 37.2), (36.8, 37.2)], 'tan', 2)
    L.recolor(cab & mask_ref(lambda x, y: (y < 14.0)), tone=1)
    L.recolor(cab & mask_ref(lambda x, y: (y > 25.4) & (y < 26.4)), tone=3)
    for (x0, x1, y0, y1) in [(40.8, 50.4, 17.6, 25.0), (58.8, 70.4, 17.4, 25.0)]:
        w = mask_ref(lambda x, y: (x > x0) & (x < x1) & (y > y0) & (y < y1))
        L.erase(w)
        L.recolor(mask_ref(lambda x, y: (x > x0 - 1) & (x < x1 + 1) & (y > y0 - 1) & (y < y1 + 1)) & ~w, tone=3)
    L.rect(44, 27, 49, 33, 'tan', 3); L.rect(44, 27, 49, 28, 'tan', 4)
    L.rect(61, 27, 67, 33, 'tan', 3); L.rect(61, 27, 67, 28, 'tan', 4)
    L.rect(53, 12, 55, 37, 'tan', 1); L.rect(53, 12, 54, 37, 'tan', 2)
    L.rect(73, 13, 74, 37, 'tan', 1)
    # cargo shell inside
    L.poly([(9.0, 21.0), (36.8, 13.8), (36.8, 34.2), (9.0, 34.2)], 'tan', 1)
    L.recolor(mask_ref(lambda x, y: (x > 9) & (x < 36.8) & (y < 20.1 - (x - 10) * 0.2963 + 2.0)), tone=0)
    # turret ring under the roof opening + traverse handle
    L.rect(38, 12, 69, 14, 'steel', 2)
    L.rect(38, 12, 69, 13, 'steel', 4)
    for x in range(40, 68, 4):
        L.P(x, 13, 'steel', 1)
    L.rect(63, 14, 64, 17, 'black', 2); L.rect(62, 17, 65, 18, 'black', 3)
    # gunner's sling seat hanging from the ring
    L.line(47, 14, 50, 22, 'black', 2)
    L.line(58, 14, 55, 22, 'black', 2)
    L.rect(50, 22, 56, 24, 'black', 3); L.rect(50, 22, 56, 23, 'black', 4)
    return L

# ================================================================== CABIN INTERIOR (seats, controls, kit)
def make_interior():
    L = Layer('Interior')
    # floor + low centre tunnel
    L.rect(37, 35, 73, 37, 'rubber', 2); L.rect(37, 35, 73, 36, 'rubber', 3)
    L.poly([(44, 30.4), (72.6, 29.8), (72.6, 35.0), (44, 35.0)], 'olive', 1)
    L.rect(44, 30, 73, 31, 'olive', 2)
    # shift levers on the tunnel
    L.line(64, 29, 63, 25, 'black', 2); L.P(63, 24, 'black', 4); L.P(62, 24, 'black', 3)
    L.line(61, 29, 60, 26, 'black', 2); L.P(60, 25, 'red', 3)
    # dashboard + instrument cluster
    L.poly([(66.4, 21.4), (73.4, 20.6), (73.4, 27.6), (69.4, 27.6), (67.8, 24.6)], 'black', 2)
    L.poly([(66.4, 21.4), (73.4, 20.6), (73.4, 21.6), (66.6, 22.4)], 'black', 4)
    L.P(70, 23, 'green', 2); L.P(71, 23, 'amber', 3); L.P(72, 23, 'green', 1)
    L.P(70, 25, 'alu', 4); L.P(71, 25, 'alu', 3); L.P(72, 25, 'red', 3)
    stamp(L, STEER, 63, 19, PAL)
    L.line(71, 30, 70, 34, 'black', 3); L.rect(69, 34, 71, 35, 'black', 4)   # pedal
    # seat bases: battery box (front, as on the real truck) and stowage box (rear)
    box(L, 58, 32, 69, 35, 'olive', 3, 4, 1)
    for x in range(59, 68, 2):
        L.P(x, 33, 'olive', 1)
    L.P(60, 32, 'red', 3); L.P(66, 32, 'black', 1)
    box(L, 40, 32, 51, 35, 'olive', 2, 3, 1)
    L.P(45, 33, 'alu', 4)
    # seats
    for sx in (55, 37):
        stamp(L, SEAT, sx, 19, PAL)
        L.line(sx + 5, 20, sx + 7, 28, 'black', 2)        # harness
        L.P(sx + 7, 28, 'alu', 4)
    # rear cargo: wheelhouse box, radio stack, ammo cans, extinguisher
    L.rect(9, 33, 37, 35, 'rubber', 2); L.rect(9, 33, 37, 34, 'rubber', 3)
    box(L, 15, 28, 36, 33, 'tan', 2, 3, 1)
    stamp(L, RADIO, 25, 19, PAL)
    L.line(25, 21, 24, 23, 'black', 2)
    for x0 in (15, 20):
        box(L, x0, 23, x0 + 4, 28, 'olive', 3, 5, 2)
        L.rect(x0, 25, x0 + 4, 26, 'yellow', 1)
        L.P(x0 + 1, 23, 'olive', 1); L.P(x0 + 2, 23, 'olive', 1)
    box(L, 35, 27, 37, 33, 'red', 2, 4, 1)
    L.rect(35, 26, 37, 27, 'black', 3); L.P(35, 28, 'red', 5)
    return L
