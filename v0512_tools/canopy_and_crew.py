"""
v0.5.12 mount art, derived at 1x and exported 2x nearest.
  ApacheGuardian_Canopy.png   the pilot's (rear) canopy pane of ApacheGuardian.png alone, same 372x126 canvas
  ApacheGuardian_Cockpit.png  what shows through when that pane swings up: dark cockpit, seat back, headrest, glareshield
  GroundCrew.png              four-man rotor crew, 12 frames of 12x22 (24x44 at 2x) stacked with a 2 px gap, facing right:
                              0 idle, 1-4 walk, 5-8 walk carrying (hands up at the shoulder), 9 carry idle, 10-11 working
"""
from PIL import Image
import numpy as np

SRC = '/mnt/user-data/uploads/ModSources--ModernArsenal/Content/NPCs/Apache/ApacheGuardian.png'
OUT = '/home/claude/art/out'


def up2(a):
    return a.repeat(2, axis=0).repeat(2, axis=1)


def canopy():
    A = np.array(Image.open(SRC).convert('RGBA'))
    one = A[::2, ::2].copy()
    h, w = one.shape[:2]
    glass = np.zeros((h, w), bool)
    for y in range(24, 38):
        for x in range(46, 61):
            r, g, b, al = [int(v) for v in one[y, x]]
            if al == 0:
                continue
            if b > r + 15 or (r > 235 and g > 240 and b > 240):
                glass[y, x] = True
    # the pane's own frame: dark pixels touching the glass (not reaching into the fuselage below)
    frame = np.zeros_like(glass)
    for y in range(23, 39):
        for x in range(45, 62):
            if glass[y, x]:
                continue
            r, g, b, al = [int(v) for v in one[y, x]]
            if al == 0 or max(r, g, b) > 60:
                continue
            if any(glass[y + dy, x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                frame[y, x] = True
    pane = np.zeros_like(one)
    pane[glass | frame] = one[glass | frame]
    # cockpit behind it, only where the glass was
    cock = np.zeros_like(one)
    ys, xs = np.nonzero(glass)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    for y, x in zip(ys, xs):
        u = (y - y0) / max(1, y1 - y0)
        base = (int(20 + 10 * u), int(24 + 10 * u), int(30 + 8 * u), 255)
        cock[y, x] = base
    # seat back and headrest near the rear of the pane (left-facing sprite: rear = larger x)
    for y in range(y0 + 3, y1 + 1):
        for x in range(x1 - 4, x1 - 1):
            if glass[y, x]:
                cock[y, x] = (52, 56, 60, 255) if x != x1 - 4 else (74, 78, 82, 255)
    for x in range(x1 - 5, x1 - 1):
        for y in (y0 + 2, y0 + 3):
            if glass[y, x]:
                cock[y, x] = (62, 66, 70, 255)
    # glareshield and a lit MFD low at the front
    for x in range(x0, x0 + 5):
        for y in range(y1 - 2, y1 + 1):
            if glass[y, x]:
                cock[y, x] = (34, 38, 36, 255)
    for (x, y) in ((x0 + 2, y1 - 2), (x0 + 3, y1 - 2)):
        if glass[y, x]:
            cock[y, x] = (80, 200, 120, 255)
    Image.fromarray(up2(pane), 'RGBA').save(f'{OUT}/ApacheGuardian_Canopy.png')
    Image.fromarray(up2(cock), 'RGBA').save(f'{OUT}/ApacheGuardian_Cockpit.png')
    # preview: closed / open
    body = Image.open(SRC).convert('RGBA')
    crop = (60, 30, 160, 90)
    a = body.crop(crop)
    b = body.copy()
    b.alpha_composite(Image.fromarray(up2(cock), 'RGBA'))
    p = Image.fromarray(up2(pane), 'RGBA')
    hinge = (186 - 67, 63 - 10)
    rot = p.rotate(-66, center=hinge, resample=Image.NEAREST)   # PIL: positive = counter-clockwise
    b.alpha_composite(rot)
    b = b.crop(crop)
    sheet = Image.new('RGBA', (220, 60), (90, 110, 130, 255))
    sheet.alpha_composite(a, (0, 0))
    sheet.alpha_composite(b, (110, 0))
    sheet.resize((880, 240), Image.NEAREST).save('/home/claude/art/canopy_preview.png')
    print('glass px', glass.sum(), 'hinge rear-top', (x1 + 1, y0), '-> 2x offset', ((x1 + 1) * 2 - 186, y0 * 2 - 63))


# ---------------------------------------------------------------- crew
PAL = {
    'K': (20, 20, 26), 'c': (70, 72, 52), 'C': (96, 98, 70),           # patrol cap (OCP dark)
    's': (150, 108, 78), 'S': (196, 150, 110),                        # skin
    'u': (92, 90, 66), 'U': (122, 118, 88), 'v': (70, 70, 52),         # OCP coverall shades
    'y': (200, 214, 64),                                               # reflective belt
    'b': (44, 38, 32), 'B': (66, 58, 48),                              # boots
    'g': (34, 34, 36),                                                 # gloves
    'w': (150, 156, 164),                                              # wrench
}

BASE = [
    "....KKKK....",
    "...KcCCCK...",
    "..KcccccKK..",
    "...KSSsK....",
    "...KSSSK....",
    "....KsK.....",
    "...KUUUuK...",
    "..KUUUUuuK..",
    "..KUUUUuuK..",
    "..KUuUUuuK..",
    "..KUuUUuuK..",
    "..KuuuuvvK..",
    "..KyyyyyyK..",
    "..KuuuuvvK..",
    "...KuKvuK...",
    "...KuKvuK...",
    "...KuKvuK...",
    "...KuKvuK...",
    "...KuKvuK...",
    "...KbKbbK...",
    "..KbbKbbbK..",
    "..KKK.KKK...",
]


def grid(rows):
    return [list(r) for r in rows]


def legs(g, phase):
    # rows 14..21: redraw the legs for a walk phase (0 stand, 1..4 stride)
    for y in range(14, 22):
        for x in range(12):
            g[y][x] = '.'
    pos = {0: (4, 7), 1: (3, 8), 2: (4, 7), 3: (5, 6), 4: (4, 7)}[phase]
    back, front = pos
    for y in range(14, 19):
        for x, shade in ((back, 'v'), (front, 'u')):
            g[y][x] = shade
            g[y][x - 1] = 'K' if g[y][x - 1] == '.' else g[y][x - 1]
            g[y][x + 1] = 'K' if g[y][x + 1] == '.' else g[y][x + 1]
    for x, lift in ((back, phase in (1,)), (front, phase in (3,))):
        yb = 19 if not lift else 18
        g[yb][x] = 'b'
        g[yb + 1][x] = 'b'
        g[yb + 1][x + 1] = 'b'
        for (xx, yy) in ((x - 1, yb), (x - 1, yb + 1), (x + 2, yb + 1), (x + 1, yb), (x - 1, yb + 2), (x, yb + 2), (x + 1, yb + 2), (x + 2, yb + 2)):
            if 0 <= xx < 12 and 0 <= yy < 22 and g[yy][xx] == '.':
                g[yy][xx] = 'K'
    return g


def arms_down(g):
    # arm down the front of the body, glove at the hip
    for y in range(7, 12):
        g[y][8] = 'u'
    g[12][8] = 'g'
    g[12][9] = 'K'
    return g


def arms_carry(g):
    # both hands up at the shoulder holding the blade (the blade itself is drawn by the game)
    for y in (4, 5, 6):
        g[y][8] = 'u'
        g[y][9] = 'K'
    g[3][8] = 'g'
    g[3][9] = 'K'
    g[2][8] = 'K'
    return g


def arms_work(g, up):
    # reaching up with the wrench to the blade grip
    if up:
        for y in range(1, 7):
            g[y][9] = 'u'
            g[y][10] = 'K'
        g[0][9] = 'g'
        g[0][10] = 'w'
        g[0][11] = 'w'
    else:
        for y in range(3, 7):
            g[y][9] = 'u'
            g[y][10] = 'K'
        g[2][9] = 'g'
        g[2][10] = 'w'
        g[1][10] = 'w'
    return g


def render(g):
    a = np.zeros((22, 12, 4), np.uint8)
    for y, row in enumerate(g):
        for x, ch in enumerate(row):
            if ch != '.':
                a[y, x] = PAL[ch] + (255,)
    return a


def crew():
    frames = []
    frames.append(arms_down(legs(grid(BASE), 0)))
    for ph in (1, 2, 3, 4):
        frames.append(arms_down(legs(grid(BASE), ph)))
    for ph in (1, 2, 3, 4):
        frames.append(arms_carry(legs(grid(BASE), ph)))
    frames.append(arms_carry(legs(grid(BASE), 0)))
    frames.append(arms_work(legs(grid(BASE), 0), True))
    frames.append(arms_work(legs(grid(BASE), 0), False))
    fw, fh, gap = 24, 44, 2
    sheet = np.zeros(((fh + gap) * len(frames) - gap, fw, 4), np.uint8)
    for i, f in enumerate(frames):
        sheet[i * (fh + gap):i * (fh + gap) + fh] = up2(render(f))
    Image.fromarray(sheet, 'RGBA').save(f'{OUT}/GroundCrew.png')
    # preview row
    prev = Image.new('RGBA', (len(frames) * 30, 50), (150, 170, 190, 255))
    for i, f in enumerate(frames):
        prev.alpha_composite(Image.fromarray(up2(render(f)), 'RGBA'), (i * 30 + 3, 3))
    prev.resize((prev.width * 3, prev.height * 3), Image.NEAREST).save('/home/claude/art/crew_preview.png')


if __name__ == '__main__':
    import os
    os.makedirs(OUT, exist_ok=True)
    canopy()
    crew()
