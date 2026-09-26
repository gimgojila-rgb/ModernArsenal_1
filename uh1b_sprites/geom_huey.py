"""
UH-1B outline traced on ref/uh1b_side_render.webp (flipped so the nose points left), in image pixels, and the
mapping to cells. Nose cap front x 492, fin trailing tip x 1532 -> 12.08 m fuselage (39'7.5") = 86.1 px/m across;
skid bottom y 398, mast top y 25 -> 14'7" = 83.8 px/m up (the camera sits a little above the aircraft).
"""
NX, GY = 492.0, 398.0
PX_X = 86.1 / 10.97            # image pixels per cell, across
PX_Y = 83.8 / 10.97            # image pixels per cell, up


def c(p):
    """image pixel (flipped image) -> reference cell (x aft of the nose, y up from the skid bottom)"""
    return ((p[0] - NX) / PX_X, (GY - p[1]) / PX_Y)


def cl(pts):
    return [c(p) for p in pts]


FUSELAGE = cl([
    (492, 322), (494, 305), (500, 292), (510, 280), (522, 270), (538, 264), (552, 262),            # nose cap
    (560, 250), (570, 232), (582, 212), (592, 198), (600, 190),                                      # windscreen
    (620, 186), (700, 184), (760, 182), (798, 176),                                                  # cabin roof
    (805, 160), (815, 152), (850, 150), (870, 155), (900, 158), (960, 160), (1000, 162), (1015, 168),  # cowlings
    (1030, 185), (1045, 205), (1060, 218),
    (1100, 222), (1200, 223), (1300, 224), (1395, 222),                                              # boom top
    (1420, 205), (1450, 180), (1475, 155), (1490, 135), (1495, 128),                                 # fin leading edge
    (1510, 125), (1528, 130), (1533, 140),                                                           # fin tip
    (1520, 165), (1505, 190), (1485, 215), (1468, 240), (1462, 250),                                 # fin trailing edge
    (1450, 252), (1400, 254), (1300, 268), (1200, 285), (1100, 303), (1000, 322), (950, 335),        # boom underside
    (930, 345), (900, 352), (800, 353), (700, 353), (600, 352), (560, 352),                          # belly
    (530, 350), (510, 345), (498, 335),
])
NOSE_CAP_X = c((560, 0))[0]           # the grey nose cap ends at the seam here
WINDSCREEN = cl([(550, 264), (598, 190), (611, 196), (607, 286), (562, 289)])     # windscreen and chin window
DOOR_WIN = cl([(612, 214), (661, 214), (661, 288), (612, 288)])
CARGO_WIN = cl([(715, 225), (792, 225), (792, 290), (715, 290)])
ROOF_WIN = cl([(610, 186), (666, 185), (666, 194), (610, 195)])
MAST_X = c((828, 0))[0]
HUB_Y = c((0, 55))[1]
MAST_BASE_Y = c((0, 150))[1]
BEACON = c((1000, 152))
TAIL_HUB = c((1500, 118))
TAIL_SKID = cl([(1452, 250), (1526, 257)])
SKID = (c((598, 0))[0], c((910, 0))[0])
STRUTS = (c((695, 0))[0], c((868, 0))[0])
# M5 40 mm nose turret: pod below, black canvas blast bag over the gun on top, traced
TURRET = cl([(441, 300), (446, 285), (458, 273), (475, 268), (492, 270), (505, 280), (507, 300), (505, 330),
             (500, 345), (488, 352), (460, 352), (447, 342), (441, 325)])
# side armament: XM156 mount and the M158 pod under the cabin
MOUNT = cl([(772, 305), (848, 305), (852, 345), (768, 345)])
POD = cl([(750, 342), (898, 342), (898, 395), (750, 395)])
TURRET_POD = cl([(441, 318), (446, 306), (505, 306), (507, 330), (500, 345), (488, 352), (460, 352), (447, 342)])
TURRET_BAG = cl([(446, 306), (447, 290), (455, 278), (470, 270), (488, 270), (500, 277), (506, 292), (505, 306)])
BAND_X = (c((1310, 0))[0], c((1386, 0))[0])        # yellow warning band on the boom
