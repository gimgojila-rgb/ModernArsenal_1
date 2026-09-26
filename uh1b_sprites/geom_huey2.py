"""
UH-1B outline and details measured on the clean side profile (ref/uh1_profiles_4view.png, top aircraft, nose left).
Nose front x 17, fin trailing tip x 470 -> 12.08 m (39'7.5") = 37.5 px/m; skid bottom y 150; mast x 155, hub y 12.
Everything is given in profile pixels and converted to cells (x aft of the nose, y up from the skid bottom).
"""
NX, GY = 17.0, 150.0
PPC = 37.5 / 10.97


def c(p):
    return ((p[0] - NX) / PPC, (GY - p[1]) / PPC)


def cl(pts):
    return [c(p) for p in pts]


FUSELAGE = cl([                     # top and bottom edges measured column by column on the profile
    (18, 110), (20, 108), (24, 104), (28, 101), (32, 98), (36, 96), (40, 95),               # nose cap
    (45, 90), (50, 84), (55, 79), (60, 73), (65, 69), (70, 66),                             # windscreen
    (80, 66.5), (100, 64.5), (130, 65), (137, 66),                                          # cabin roof
    (140, 61), (145, 56.5), (170, 56), (200, 56.5), (224, 55.5),                            # transmission fairing, cowl
    (228, 52), (232, 51), (235, 54), (239, 59), (241, 66), (243, 74), (247, 79), (252, 81),  # exhaust, cowl end
    (300, 80), (350, 78.5), (390, 77), (405, 75.5),                                         # boom top
    (410, 73), (420, 64), (430, 55), (440, 47), (453, 34), (458, 31),                       # fin leading edge
    (466, 33), (471, 37),                                                                   # fin tip
    (465, 48), (458, 58), (452, 69), (449, 76), (446, 82), (442, 87),                       # fin trailing edge
    (430, 92), (420, 95), (400, 98), (380, 101), (360, 105), (340, 108), (320, 111),        # boom underside
    (300, 115), (280, 118), (260, 121), (240, 125), (220, 128), (200, 132), (190, 133), (180, 135),
    (150, 135.5), (100, 135), (60, 135), (50, 134),                                          # belly
    (45, 132), (40, 131), (36, 130), (32, 129), (28, 127), (24, 124), (20, 119), (18, 114),  # chin
])
NOSE_CAP = cl([(17, 110), (19, 103), (24, 98), (30, 94), (36, 92), (42, 104), (47, 120), (50, 133), (45, 133),
               (35, 131), (27, 128), (21, 122), (17, 115)])
WINDSCREEN = cl([(38, 94), (61, 73), (68, 79), (54, 106), (43, 104)])
DOOR_WIN = cl([(69, 80), (86, 80), (86, 106), (61, 106)])
CARGO_WIN = cl([(106, 84), (137, 84), (137, 105), (106, 105)])
ROOF_WIN = cl([(47, 72), (60, 68.5), (88, 67.5), (88, 70.5), (60, 71.5)])
PILLAR = cl([(52, 108), (70, 78)])                    # windscreen / door pillar
COCKPIT_DOOR = cl([(70, 70), (96, 70), (96, 128), (58, 128)])
CARGO_DOOR = cl([(98, 69), (148, 69), (148, 129), (98, 129)])
LIT_LINE = cl([(36, 110), (90, 110)])                 # the pale rub strip under the cockpit windows
COWL_LINE = cl([(168, 70), (238, 70)])                # where the cowling side rolls under
GRILLE = cl([(205, 58), (232, 58), (232, 72), (205, 72)])
EXHAUST = cl([(229, 50), (237, 50), (238, 58), (230, 58)])
BOOM_SEAM = cl([(252, 88), (405, 86)])                # tail rotor driveshaft cover edge along the boom
STAR_C = c((253, 102))
BAND_X = (c((377, 0))[0], c((405, 0))[0])
MAST_X = c((155, 0))[0]
HUB_Y = c((0, 12))[1]
SWASH_Y = c((0, 52))[1]
COWL_TOP_Y = c((0, 56.5))[1]
TAIL_HUB = c((463, 30))
TAIL_SKID = cl([(442, 88), (469, 95)])
SKID = (c((60, 0))[0], c((186, 0))[0])
STRUTS = (c((102, 0))[0], c((168, 0))[0])
ANTENNA = cl([(74, 66), (80, 54), (86, 66)])
# weapons from the render the user sent first (separate, optional layers): M5 nose turret, XM16 side pod
TURRET_POD = cl([(0, 118), (2, 112), (22, 112), (24, 121), (21, 129), (15, 133), (5, 133), (1, 128)])
TURRET_BAG = cl([(2, 112), (3, 105), (7, 100), (13, 98), (19, 99), (23, 104), (24, 112)])
POD = cl([(114, 135), (160, 135), (160, 147), (114, 147)])
MOUNT = cl([(126, 128), (150, 128), (152, 135), (124, 135)])
