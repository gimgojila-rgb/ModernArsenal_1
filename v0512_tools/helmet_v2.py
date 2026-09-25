"""IHADSS helmet icon v2 (16x16 art, 32x32 at 2x): HGU-56/P shell shaded as a sphere lit from the upper left, the smoked
visor down under its housing, the IHADSS monocle on its arm, ear seal, boom mic and the cable off the back."""
from PIL import Image
import numpy as np, math

SHELL = [(40, 44, 28), (62, 68, 44), (86, 94, 60), (112, 120, 80), (144, 152, 104), (186, 192, 142)]
W = 16
img = np.zeros((W, W, 4), np.uint8)
mask = np.zeros((W, W), bool)
cx, cy, r = 7.2, 7.4, 6.4
L = np.array([-0.55, -0.7, 0.45]); L /= np.linalg.norm(L)
for y in range(W):
    for x in range(W):
        dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
        if dx * dx + dy * dy > 1.0 or y > 12:
            continue
        if x >= 9 and y >= 8:
            continue   # face opening
        dz = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
        lum = max(0.0, float(np.dot([dx, dy, dz], L)))
        t = min(4, int(lum * 5.2))
        img[y, x] = SHELL[1 + t] + (255,) if t < 4 else SHELL[5] + (255,)
        mask[y, x] = True


def put(x, y, c):
    img[y, x] = c + (255,)
    mask[y, x] = True


# visor housing (darker band over the brow, standing proud of the shell) and the smoked visor under it
for x in range(7, 15):
    put(x, 5, SHELL[1] if x > 7 else SHELL[2])
for x in range(8, 15):
    put(x, 6, (36, 44, 58))
    put(x, 7, (28, 34, 46))
put(12, 6, (118, 160, 190)); put(13, 6, (190, 222, 236))   # the visor's glint
put(14, 7, (22, 26, 36))
# ear seal / cup
for (x, y) in ((5, 8), (6, 8), (5, 9), (6, 9), (5, 10), (6, 10)):
    put(x, y, (58, 54, 48))
put(5, 8, (84, 80, 70))
# IHADSS monocle on its arm, lens toward the eye, cyan glint
put(9, 8, (40, 42, 50)); put(10, 9, (40, 42, 50)); put(11, 9, (70, 74, 86)); put(12, 9, (70, 74, 86))
put(11, 10, (40, 42, 50)); put(12, 10, (40, 42, 50)); put(13, 9, (60, 205, 255)); put(13, 10, (30, 120, 170))
# boom mic in front of the mouth
put(8, 11, (40, 42, 50)); put(9, 12, (40, 42, 50)); put(10, 12, (40, 42, 50)); put(11, 12, (74, 74, 80))
# chin strap and the cable off the back
put(7, 12, SHELL[0]); put(8, 12, SHELL[1])
for (x, y) in ((2, 11), (1, 12), (1, 13), (2, 14), (3, 14)):
    put(x, y, (34, 34, 40))
put(3, 13, (60, 60, 68))
# outline: darkest shell tone around everything
out = img.copy()
for y in range(W):
    for x in range(W):
        if mask[y, x]:
            continue
        if any(0 <= x + a < W and 0 <= y + b < W and mask[y + b, x + a] for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            out[y, x] = (24, 26, 18, 255)
Image.fromarray(out.repeat(2, 0).repeat(2, 1), 'RGBA').save('/home/claude/art/out/GuardianHelmet.png')
Image.fromarray(out.repeat(12, 0).repeat(12, 1), 'RGBA').save('/home/claude/art/helmet_zoom.png')
