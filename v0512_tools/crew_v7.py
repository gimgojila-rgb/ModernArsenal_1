"""
GroundCrew.png v7: the rotor crew drawn in Terraria's NPC style, sized and checked against the Demolitionist / Stylist
sheets the user sent (those are 2x: 18x20 and 13x26 art px). 16x24 art px per frame (32x48 at 2x), frames stacked with a
2 px gap, facing right, feet on the bottom row.
Style points taken from the references:
  - big head, eye = one white pixel and a blue iris, two pixels tall, a dark brow over it, hair framing the back
  - arms on both sides of a narrow torso, the far one a shade darker, bare hands (skin reads better than gloves)
  - saturated colours, shading hue-shifted (skin toward red-brown, olive toward brown), outlines in each material's
    darkest tone, never black
  0 idle  1-4 walk  5-8 walk carrying (arm forward, hand at the shoulder)  9 carry idle  10-11 working with the wrench
"""
from PIL import Image
import numpy as np

C = {
    '1': (36, 32, 18), '2': (92, 88, 52), '3': (128, 122, 74), '4': (170, 162, 104),
    'h': (52, 32, 20), 'H': (88, 56, 32), 'I': (120, 80, 46),
    'a': (120, 66, 46), 'b': (212, 146, 110), 'c': (240, 186, 148), 'd': (252, 214, 184),
    'w': (255, 255, 255), 'i': (58, 108, 204), 'B': (70, 40, 22),
    'E': (40, 34, 20), 'f': (104, 92, 54), 'g': (152, 138, 86), 'j': (206, 190, 130),
    'k': (108, 124, 62), 'l': (196, 162, 106), 'x': (70, 62, 38), 'z': (84, 74, 44),
    'y': (236, 246, 104), 'Y': (180, 192, 44),
    'p': (66, 42, 24), 'q': (132, 94, 56), 'r': (178, 134, 82),
    's': (112, 118, 130), 't': (182, 188, 200), 'u': (52, 56, 66),
}
W, H = 16, 24

HEAD_TORSO = [
    "................",   # 0 (the raised wrench uses it)
    ".....1111111....",   # 1 cap crown
    "....144433331...",   # 2
    "....1333333321..",   # 3
    "....12222222221.",   # 4 band
    "...hHHIbbbbbba11",   # 5 hair at the back, forehead in the brim's shadow, brim tip
    "...hHHhccccBBa..",   # 6 sideburn, brow
    "...hHhbcccwica..",   # 7 small ear, eye at the front
    "...hhhbcccwica..",   # 8
    "...ahhbcccccca..",   # 9 flat front, no nose sticking out (that read as a goblin)
    "....ahbccccba...",   # 10
    ".....abbbba.....",   # 11 chin
    "....EjjjggfE....",   # 12 collar
    "....EgjggfgE....",   # 13 torso (arms go over the edges)
    "....EgxxxfgE....",   # 14 name tape
    "....EkggggfE....",   # 15 camo
    "....EglgkffE....",   # 16
    "....EYyyyyYE....",   # 17 PT belt
    "....EffffffE....",   # 18 hips
]

LEGS = {
    'stand': ["....EzzEgfE.....", "....EzzEgfE.....", "....EzzEgfE.....", "....pqqprrrp....", "....pppppppp...."],
    'a':     ["...EzzE.EgfE....", "..EzzE...EgfE...", "..EzzE....EgfE..", ".pqqp.....prrrp.", ".pppp.....ppppp."],
    'pass':  [".....EzgfE......", ".....EzgfE......", ".....EzgfE......", "....pqqrrrp.....", "....ppppppp....."],
    'b':     ["....EgfEzzE.....", "...EgfE..EzzE...", "..EgfE....EzzE..", ".prrrp....pqqp..", ".ppppp....pppp.."],
}


def paint(g, x, y, s):
    for k, ch in enumerate(s):
        if ch != ' ' and 0 <= x + k < W and 0 <= y < H:
            g[y][x + k] = ch


def back_arm(g, dx=0):
    # far arm, a shade darker, just behind the torso outline
    paint(g, 3, 12, 'E')
    for y in (13, 14):
        paint(g, 2, y, 'Ef')
    for y in (15, 16):
        paint(g, 2 + dx, y, 'Ef')
    paint(g, 2 + dx, 17, 'ab')
    paint(g, 2 + dx, 18, 'aa')


def front_arm(g, dx=0):
    paint(g, 10, 12, 'jfE')
    for y in (13, 14):
        paint(g, 10, y, 'gfE')
    for y in (15, 16):
        paint(g, 10 + dx, y, 'gfE')
    paint(g, 10 + dx, 17, 'cba')
    paint(g, 10 + dx, 18, 'aa')


def front_arm_carry(g):
    # forward at the shoulder; the hand steadies the blade resting there
    paint(g, 10, 11, 'EEEE')
    paint(g, 10, 12, 'jjgfE')
    paint(g, 10, 13, 'gfffE')
    paint(g, 14, 11, 'cb')
    paint(g, 15, 12, 'a')
    paint(g, 14, 10, 'aa')
    paint(g, 10, 14, 'EEEE')


def front_arm_work(g, up):
    if up:
        paint(g, 10, 12, 'jfE')
        for k, y in enumerate(range(11, 4, -1)):
            paint(g, 11 + k // 3, y, 'gfE')
        paint(g, 12, 4, 'cb')
        paint(g, 12, 3, 'ts')
        paint(g, 13, 2, 'ts')
        paint(g, 13, 1, 'u')
        paint(g, 14, 3, 'u')
    else:
        front_arm_carry(g)
        paint(g, 15, 10, 't')
        paint(g, 15, 9, 's')
        paint(g, 15, 8, 'u')


def frame(legs, arms):
    g = [list(r.ljust(W, '.')[:W]) for r in HEAD_TORSO] + [list(r) for r in LEGS[legs]]
    assert len(g) == H, len(g)
    arms(g)
    a = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            if g[y][x] not in '. ':
                a[y, x] = C[g[y][x]] + (255,)
    return a


def up2(a):
    return a.repeat(2, axis=0).repeat(2, axis=1)


def main():
    def idle(g):
        back_arm(g)
        front_arm(g)
    frames = [frame('stand', idle)]
    for legs, sw in (('a', 1), ('pass', 0), ('b', -1), ('pass', 0)):
        frames.append(frame(legs, lambda g, sw=sw: (back_arm(g, -sw), front_arm(g, sw))))
    for legs, sw in (('a', 1), ('pass', 0), ('b', -1), ('pass', 0)):
        frames.append(frame(legs, lambda g, sw=sw: (back_arm(g, -sw), front_arm_carry(g))))
    frames.append(frame('stand', lambda g: (back_arm(g), front_arm_carry(g))))
    frames.append(frame('stand', lambda g: (back_arm(g), front_arm_work(g, True))))
    frames.append(frame('stand', lambda g: (back_arm(g), front_arm_work(g, False))))

    fw, fh, gap = W * 2, H * 2, 2
    sheet = np.zeros(((fh + gap) * len(frames) - gap, fw, 4), np.uint8)
    for k, fr in enumerate(frames):
        sheet[k * (fh + gap):k * (fh + gap) + fh] = up2(fr)
    Image.fromarray(sheet, 'RGBA').save('/home/claude/art/out/GroundCrew.png')

    refs = [Image.open('/root/.claude/uploads/898ddf96-b567-5c1c-be87-f72bb69c4ab6/546b8512-image.png').convert('RGBA'),
            Image.open('/root/.claude/uploads/898ddf96-b567-5c1c-be87-f72bb69c4ab6/cc9d0210-image.png').convert('RGBA')]
    prev = Image.new('RGBA', (len(frames) * 38 + 100, 60), (120, 150, 180, 255))
    x = 4
    for r in refs:
        prev.alpha_composite(r, (x, 58 - r.height))
        x += r.width + 8
    for fr in frames:
        prev.alpha_composite(Image.fromarray(up2(fr), 'RGBA'), (x, 58 - fh))
        x += 38
    prev.resize((prev.width * 3, prev.height * 3), Image.NEAREST).save('/home/claude/art/crew_preview.png')


if __name__ == '__main__':
    main()
