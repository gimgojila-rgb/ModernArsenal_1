"""
ModernArsenal v0.5.12 item art. Drawn at 1x on a grid, then exported 2x nearest (project rule).
Style follows M4A1.png / MiniApacheRemote.png: 1 px dark outline, 3-4 flat tones per material, light on top edges,
dark on bottom edges, one highlight pixel here and there.
"""
from PIL import Image
import numpy as np

OUT = '/home/claude/art/out'
K = (20, 20, 26, 255)
MAT = {
    # gunmetal (M4A1 palette)
    'g': [(37, 39, 49), (53, 56, 70), (74, 79, 97), (103, 109, 132), (143, 150, 174)],
    # darker blued steel for the M230 (Apache gun palette)
    's': [(27, 31, 36), (42, 48, 55), (62, 70, 80), (90, 100, 112), (144, 151, 160)],
    # olive drab (MiniApacheRemote palette)
    'o': [(34, 36, 34), (52, 60, 38), (76, 86, 54), (102, 114, 70), (136, 148, 92)],
    # brass
    'b': [(96, 70, 30), (140, 106, 44), (184, 148, 64), (214, 184, 96), (240, 222, 150)],
    # helmet grey-green (HGU-56/P)
    'h': [(52, 56, 48), (72, 78, 64), (98, 106, 86), (128, 136, 112), (164, 172, 146)],
    # visor smoke
    'v': [(22, 26, 34), (32, 38, 50), (48, 58, 76), (84, 110, 130), (170, 206, 220)],
    # screen (Guardian data-link deep navy)
    'n': [(3, 14, 24), (3, 20, 36), (8, 32, 52), (14, 48, 72), (30, 80, 110)],
    # Gray Eagle / Guardian light grey
    'e': [(70, 74, 80), (96, 102, 110), (128, 134, 142), (160, 166, 172), (200, 206, 212)],
}
FIX = {
    'C': (60, 205, 255), 'c': (150, 232, 255), 'W': (240, 250, 255), 'R': (220, 40, 30), 'r': (255, 120, 90),
    'Y': (236, 170, 60), 'k': (20, 20, 26), 'B': (18, 20, 26),
}


class Sprite:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.mat = [[None] * w for _ in range(h)]    # material key or None
        self.tone = [[2] * w for _ in range(h)]      # 0..4
        self.fix = {}                                # (x,y) -> rgb, drawn over everything
        self.noshade = set()

    def rect(self, x0, y0, x1, y1, m, tone=None):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < self.w and 0 <= y < self.h:
                    self.mat[y][x] = m
                    if tone is not None:
                        self.tone[y][x] = tone
                        self.noshade.add((x, y))

    def px(self, x, y, m, tone=None):
        self.rect(x, y, x, y, m, tone)

    def put(self, x, y, key):
        self.fix[(x, y)] = FIX[key]

    def clear(self, x, y):
        self.mat[y][x] = None
        self.fix.pop((x, y), None)

    def shade(self):
        # top edge light, bottom edge dark, per material region
        for y in range(self.h):
            for x in range(self.w):
                m = self.mat[y][x]
                if m is None or (x, y) in self.noshade:
                    continue
                up = self.mat[y - 1][x] if y > 0 else None
                dn = self.mat[y + 1][x] if y + 1 < self.h else None
                t = 2
                if up != m:
                    t = 3
                if dn != m:
                    t = 1
                if up != m and dn != m:
                    t = 2
                self.tone[y][x] = t

    def image(self):
        img = np.zeros((self.h, self.w, 4), np.uint8)
        for y in range(self.h):
            for x in range(self.w):
                m = self.mat[y][x]
                if m is not None:
                    img[y, x] = MAT[m][self.tone[y][x]] + (255,)
        for (x, y), c in self.fix.items():
            img[y, x] = c + (255,)
        # outline: transparent pixels 4-adjacent to an opaque one
        a = img[:, :, 3] > 0
        out = img.copy()
        for y in range(self.h):
            for x in range(self.w):
                if a[y, x]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < self.w and 0 <= yy < self.h and a[yy, xx]:
                        out[y, x] = K
                        break
        return Image.fromarray(out, 'RGBA')


def save(img, name):
    img.resize((img.width * 2, img.height * 2), Image.NEAREST).save(f'{OUT}/{name}.png')
    img.save(f'{OUT}/_1x_{name}.png')


# ---------------------------------------------------------------- Mk19 Mod 3 (40 x 15 at 1x, muzzle right)
def mk19():
    s = Sprite(42, 17)
    ox, oy = 1, 1
    def R(x0, y0, x1, y1, t, m='g'):
        s.rect(x0 + ox, y0 + oy, x1 + ox, y1 + oy, m, t)
    # spade grips: two handles off the back plate, butterfly trigger tucked against the plate
    R(0, 3, 2, 4, 2); R(0, 3, 2, 3, 3); R(0, 4, 0, 4, 1)
    R(0, 10, 2, 11, 2); R(0, 10, 2, 10, 3); R(0, 11, 2, 11, 1)
    R(3, 2, 4, 12, 1); R(3, 2, 4, 2, 2)
    R(2, 7, 2, 7, 3)
    # receiver: light top cover over a darker body
    R(5, 2, 24, 5, 3); R(5, 2, 24, 2, 4); R(24, 3, 24, 5, 2)
    R(5, 6, 24, 6, 0)                          # cover seam
    R(5, 7, 24, 12, 2); R(5, 12, 24, 12, 1)
    R(18, 7, 18, 11, 1)                        # side plate seam
    for x in (7, 11, 15):
        R(x, 4, x, 4, 1)
    R(9, 0, 10, 1, 3); R(9, 0, 9, 0, 4)        # leaf sight
    R(19, 8, 21, 9, 4); R(19, 9, 21, 9, 3); R(22, 8, 22, 9, 0)   # charging handle
    R(6, 9, 6, 9, 3)
    # the belt of 40 mm rounds hanging out of the feed
    for x in (9, 12, 15):
        s.rect(x + ox, 13 + oy, x + 1 + ox, 13 + oy, 'b', 3)
        s.rect(x + ox, 14 + oy, x + 1 + ox, 14 + oy, 'b', 1)
    s.rect(9 + ox, 13 + oy, 9 + ox, 13 + oy, 'b', 4)
    # front plate, ribbed jacket, barrel, muzzle
    R(25, 3, 26, 11, 1); R(25, 3, 26, 3, 3)
    R(27, 5, 32, 10, 2); R(27, 5, 32, 5, 3); R(27, 10, 32, 10, 1)
    for x in (28, 30, 32):
        R(x, 5, x, 10, 1)
    R(33, 6, 37, 9, 2); R(33, 6, 37, 6, 4); R(33, 9, 37, 9, 1)
    R(38, 5, 39, 10, 1); R(38, 5, 39, 5, 3); R(39, 7, 39, 8, 0)
    return s.image()


# ---------------------------------------------------------------- M230 chain gun (salvaged, 46 x 14 at 1x)
def m230():
    s = Sprite(49, 17)
    ox, oy = 1, 1
    def R(x0, y0, x1, y1, t, m='s'):
        s.rect(x0 + ox, y0 + oy, x1 + ox, y1 + oy, m, t)
    # drive motor at the back
    R(0, 5, 2, 10, 2); R(0, 5, 2, 5, 3); R(0, 10, 2, 10, 1); R(1, 7, 1, 8, 4)
    # receiver
    R(3, 3, 17, 11, 2); R(3, 3, 17, 3, 4); R(3, 4, 17, 4, 3); R(3, 11, 17, 11, 1)
    R(3, 7, 17, 7, 1)
    for x in (6, 10, 14):
        R(x, 5, x, 5, 4)
    R(8, 9, 12, 10, 1)                          # ejection port
    # the cut ammo chute off the top (olive)
    s.rect(9 + ox, 0 + oy, 14 + ox, 2 + oy, 'o', 2)
    for x in (9, 12):
        s.rect(x + ox, 0 + oy, x + ox, 2 + oy, 'o', 1)
    s.rect(10 + ox, 0 + oy, 11 + ox, 0 + oy, 'o', 3)
    # improvised pistol grip, taped, and the trigger
    s.rect(5 + ox, 12 + oy, 7 + ox, 14 + oy, 'o', 2)
    s.rect(5 + ox, 13 + oy, 7 + ox, 13 + oy, 'o', 1)
    s.rect(5 + ox, 12 + oy, 5 + ox, 14 + oy, 'o', 3)
    R(9, 12, 9, 12, 3)
    # recoil adapter: a fat ribbed can
    R(18, 4, 23, 10, 2); R(18, 4, 23, 4, 4); R(18, 5, 23, 5, 3); R(18, 10, 23, 10, 1)
    R(20, 4, 20, 10, 1); R(22, 4, 22, 10, 1)
    # barrel with a mid clamp and a slotted muzzle
    R(24, 6, 44, 8, 2); R(24, 6, 44, 6, 4); R(24, 8, 44, 8, 1)
    R(33, 5, 34, 9, 1); R(33, 5, 34, 5, 3)
    R(45, 5, 46, 9, 2); R(45, 5, 46, 5, 3); R(46, 7, 46, 7, 0)
    return s.image()


# ---------------------------------------------------------------- Gray Eagle ground control terminal (16 x 16)
def gcs():
    s = Sprite(16, 16)
    s.rect(1, 3, 14, 14, 'o')
    s.rect(0, 6, 0, 10, 'o', 1)
    s.rect(15, 6, 15, 10, 'o', 1)
    s.rect(12, 0, 12, 2, 'g', 2)            # antenna stub
    s.rect(3, 5, 12, 11, 'n', 1)            # screen
    s.shade()
    for x in range(3, 13):
        s.tone[5][x] = 0
        s.noshade.add((x, 5))
    s.rect(3, 5, 12, 11, 'n', 1)
    # the Gray Eagle from above on the screen: straight wing, fuselage, V tail
    for x in range(4, 12):
        s.put(x, 8, 'C')
    for y in range(6, 11):
        s.put(7, y, 'c')
    s.put(6, 10, 'C')
    s.put(8, 10, 'C')
    s.put(7, 6, 'W')
    s.put(11, 6, 'R')                       # REC
    # screen corners (reticle), keys
    s.put(3, 5, 'C'); s.put(12, 11, 'C')
    for x in (3, 5, 7, 9, 11):
        s.px(x, 13, 'o', 1)
    s.put(12, 13, 'Y')
    return s.image()


# ---------------------------------------------------------------- IHADSS helmet (16 x 16, facing right)
def helmet():
    s = Sprite(16, 16)
    cx, cy, r = 7.0, 7.5, 6.3
    for y in range(16):
        for x in range(16):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and y <= 12:
                s.px(x, y, 'h')
    # face opening
    for y in range(8, 13):
        for x in range(10, 16):
            s.mat[y][x] = None
    s.shade()
    # visor down over the brow
    s.rect(9, 5, 13, 7, 'v', 2)
    s.rect(9, 5, 13, 5, 'v', 3)
    s.px(12, 6, 'v', 4)
    # ear cup and chin strap
    s.rect(5, 8, 7, 11, 'h', 1)
    s.px(6, 9, 'h', 3)
    s.rect(8, 12, 9, 12, 'h', 0)
    # the monocle (HDU) on its arm in front of the right eye
    s.rect(10, 8, 10, 9, 'g', 2)
    s.rect(11, 9, 13, 10, 'g', 2)
    s.rect(11, 9, 13, 9, 'g', 3)
    s.put(13, 10, 'C')
    s.put(14, 10, 'c')
    # cable off the back
    s.rect(1, 12, 2, 12, 'g', 1)
    s.rect(0, 13, 1, 14, 'g', 0)
    s.put(4, 3, 'W')
    return s.image()


# ---------------------------------------------------------------- MUM-T datalink terminal (Guardian summon, 16 x 18)
def datalink():
    s = Sprite(16, 18)
    s.rect(2, 4, 13, 17, 's')
    s.rect(0, 8, 1, 10, 's', 1)
    s.rect(11, 0, 11, 3, 's', 1)
    s.shade()
    s.put(11, 0, 'W')
    s.rect(4, 6, 11, 12, 'n', 1)
    # the cyan lock diamond on the screen
    for (x, y) in ((7, 7), (8, 7), (6, 8), (9, 8), (6, 10), (9, 10), (7, 11), (8, 11)):
        s.put(x, y, 'C')
    s.put(6, 9, 'C'); s.put(9, 9, 'C')
    s.put(7, 9, 'c'); s.put(8, 9, 'c')
    s.put(4, 6, 'C'); s.put(11, 12, 'C')
    for y in (14, 16):
        for x in (4, 6, 8, 10):
            s.px(x, y, 's', 0)
    s.put(11, 14, 'R')
    return s.image()


# ---------------------------------------------------------------- buff icons (16 x 16, MiniApacheBuff frame)
def frame():
    img = np.zeros((16, 16, 4), np.uint8)
    img[:, :] = FIX['B'] + (255,)
    grad = [(70, 94, 128), (70, 94, 128), (70, 94, 128), (70, 94, 128), (58, 78, 108), (70, 94, 128), (70, 94, 128),
            (58, 78, 108), (58, 78, 108), (48, 64, 90), (58, 78, 108), (48, 64, 90), (48, 64, 90), (48, 64, 90)]
    for y in range(1, 15):
        img[y, 1:15] = grad[y - 1] + (255,)
    return img


def buff_eagle():
    img = frame()
    s = Sprite(16, 16)
    # the Gray Eagle from above, nose up: long straight wing, slim fuselage, V tail, pusher prop
    s.rect(7, 2, 8, 12, 'e', 2)
    s.rect(7, 2, 7, 12, 'e', 3)
    s.rect(2, 6, 13, 6, 'e', 3)
    s.rect(3, 7, 12, 7, 'e', 1)
    s.rect(7, 6, 8, 7, 'e', 2)
    s.rect(5, 11, 6, 11, 'e', 3); s.rect(9, 11, 10, 11, 'e', 1)
    s.rect(4, 12, 4, 12, 'e', 3); s.rect(11, 12, 11, 12, 'e', 1)
    s.rect(6, 13, 9, 13, 'g', 1)
    s.px(7, 3, 'e', 4)
    body = np.array(s.image())
    m = body[:, :, 3] > 0
    img[m] = body[m]
    img[0, :] = FIX['B'] + (255,); img[15, :] = FIX['B'] + (255,); img[:, 0] = FIX['B'] + (255,); img[:, 15] = FIX['B'] + (255,)
    return Image.fromarray(img, 'RGBA')


def buff_guardian(mini_buff_path):
    # the mini Apache buff art, recoloured from olive to the Guardian's grey, and a cyan dot on the radar
    img = np.array(Image.open(mini_buff_path).convert('RGBA'))[::2, ::2].copy()
    remap = {
        (52, 60, 38): (70, 74, 80), (76, 86, 54): (96, 102, 110), (102, 114, 70): (128, 134, 142),
        (136, 148, 92): (170, 176, 182), (22, 24, 18): (20, 20, 26), (34, 36, 34): (40, 42, 48),
    }
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            c = tuple(int(v) for v in img[y, x, :3])
            if c in remap:
                img[y, x, :3] = remap[c]
    return Image.fromarray(img, 'RGBA')


if __name__ == '__main__':
    import os
    os.makedirs(OUT, exist_ok=True)
    save(mk19(), 'Mk19Launcher')
    save(m230(), 'M230ChainGun')
    save(gcs(), 'GrayEagleTerminal')
    save(helmet(), 'GuardianHelmet')
    save(datalink(), 'GuardianSummon')
    save(buff_eagle(), 'GrayEagleBuff')
    save(buff_guardian('/mnt/user-data/uploads/ModSources--ModernArsenal/Content/Buffs/MiniApacheBuff.png'), 'GuardianMountBuff')
    Image.new('RGBA', (2, 2), (0, 0, 0, 0)).save(f'{OUT}/GuardianMount_Back.png')
    print('ok')
