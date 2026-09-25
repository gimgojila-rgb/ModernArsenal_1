"""
GuardianChinook*.png: the Humvee fight's CH-47 resampled onto the Apache's scale for the Guardian delivery.
The Humvee-fight Chinook is drawn at about 42 px per metre (656 px for a 15.5 m fuselage) to match the truck; the Apache
and the Gray Eagle are at about 25 px per metre (372 px for a 15 m fuselage), so next to the Guardian it looked 1.7x too
big. Scale 0.583, done on the 1x art (each 2x2 block is one cell) and exported 2x again, so the pixel grid stays whole:
area-average the cells, keep a cell where it's at least half covered (a third for the thin rotor blades), map its colour
to the nearest colour of the original palette, and redraw the silhouette edge in the original's darkest tone.
Order: run this first (rotor sheets, the v1 body, the printed constants), then chinook_small2.py, which
replaces GuardianChinook.png with the v2 body (layered shrink, no mush).
"""
from PIL import Image
import numpy as np

SRC = '/mnt/user-data/uploads/ModSources--ModernArsenal/Content/NPCs/Humvee/'
OUT = '/home/claude/art/out/'
K = 0.583


def palette(a):
    cols = a[a[..., 3] > 0][:, :3]
    return np.unique(cols, axis=0).astype(np.float32)


def shrink(a1, w, h, thr, pal, outline):
    """a1: 1x RGBA art -> w x h, area-averaged, palette-snapped"""
    H1, W1 = a1.shape[:2]
    out = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            y0, y1 = y * H1 / h, (y + 1) * H1 / h
            x0, x1 = x * W1 / w, (x + 1) * W1 / w
            acc = np.zeros(3); wa = 0.0; area = 0.0
            for yy in range(int(y0), int(np.ceil(y1))):
                for xx in range(int(x0), int(np.ceil(x1))):
                    fy = min(y1, yy + 1) - max(y0, yy)
                    fx = min(x1, xx + 1) - max(x0, xx)
                    f = fy * fx
                    area += f
                    if a1[yy, xx, 3] > 0:
                        acc += a1[yy, xx, :3] * f
                        wa += f
            if wa / area >= thr:
                c = acc / wa
                i = np.argmin(((pal - c) ** 2).sum(1))
                out[y, x] = tuple(pal[i].astype(np.uint8)) + (255,)
    if outline is not None:
        m = out[..., 3] > 0
        edge = m.copy()
        edge[1:-1, 1:-1] = m[1:-1, 1:-1] & ~(m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:])
        out[edge & m, :3] = outline
    return out


def up2(a):
    return a.repeat(2, 0).repeat(2, 1)


body = np.array(Image.open(SRC + 'HumveeChinook.png').convert('RGBA'))[::2, ::2]
pal = palette(body)
dark = tuple(pal[np.argmin(pal.sum(1))].astype(np.uint8))
bw, bh = round(body.shape[1] * K), round(body.shape[0] * K)
small = shrink(body, bw, bh, 0.5, pal, dark)
Image.fromarray(up2(small), 'RGBA').save(OUT + 'GuardianChinook.png')

rot = np.array(Image.open(SRC + 'HumveeChinook_Rotor.png').convert('RGBA'))[::2, ::2]   # 318 x 96: 8 frames of 11, stride 12
rpal = palette(rot)
RK = 1.25 * 137 / 318    # rotor on its own scale: one CH-47 disk is 1.25x an AH-64 disk (18.29 m vs 14.63 m), and
#                            the Apache's drawn rotor is 274 px (137 art px), so 342 px here instead of the body's 0.583
fw, fh = round(318 * RK), 6
frames = []
for f in range(8):
    fr = rot[f * 12:f * 12 + 11]
    frames.append(shrink(fr, fw, fh, 0.3, rpal, None))
sheet = np.zeros((8 * (fh + 1) - 1, fw, 4), np.uint8)
for f, fr in enumerate(frames):
    sheet[f * (fh + 1):f * (fh + 1) + fh] = fr
Image.fromarray(up2(sheet), 'RGBA').save(OUT + 'GuardianChinook_Rotor.png')

blur = np.array(Image.open(SRC + 'HumveeChinook_RotorBlur.png').convert('RGBA'))[::2, ::2]    # 318 x 12
# the blur is translucent: average colour and alpha together instead of snapping
H1, W1 = blur.shape[:2]
bh2 = round(H1 * K)
bl = np.array(Image.fromarray(blur, 'RGBA').resize((fw, bh2), Image.BOX))
Image.fromarray(up2(bl), 'RGBA').save(OUT + 'GuardianChinook_RotorBlur.png')

sx, sy = small.shape[1] * 2 / 656, small.shape[0] * 2 / 262
rx, ry = fw * 2 / 636, fh * 2 / 22
print('body', small.shape[1] * 2, small.shape[0] * 2, 'scale', round(sx, 4), round(sy, 4))
print('rotor frame', fw * 2, fh * 2, 'stride', (fh + 1) * 2, 'rscale', round(rx, 4), round(ry, 4))
print('blur', fw * 2, bh2 * 2)
for name, (x, y) in {'anchor': (328, 167)}.items():
    print(name, round(x * sx, 1), round(y * sy, 1))
for name, (x, y) in {'fwd': (-240.5, -97.4), 'aft': (228.8, -150.5), 'hook': (1.3, 58.6), 'btop': (-49.4, -58.4),
                     'bbot': (-1.5, 53.5)}.items():
    print(name, round(x * sx, 1), round(y * sy, 1))
print('hubInFrame', round(318 * rx, 1), round(14 * ry, 1), '(blur hub', round(318 * rx, 1), round(14 * bh2 * 2 / 24, 1), ')')

# scale check: the Guardian next to the new Chinook and the old one
g = Image.open('/mnt/user-data/uploads/ModSources--ModernArsenal/Content/NPCs/Apache/ApacheGuardian.png').convert('RGBA')
old = Image.open(SRC + 'HumveeChinook.png').convert('RGBA')
new = Image.open(OUT + 'GuardianChinook.png').convert('RGBA')
cv = Image.new('RGBA', (old.width + new.width + 60, old.height + g.height + 40), (120, 150, 180, 255))
cv.alpha_composite(old, (10, 10)); cv.alpha_composite(g, (10, old.height + 30))
cv.alpha_composite(new, (old.width + 40, 10 + old.height - new.height)); cv.alpha_composite(g, (old.width + 40, old.height + 30))
cv.save('/home/claude/art/chinook_scale.png')
