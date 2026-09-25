"""
GroundCrew.png v8: built on the Terraria Nurse's proportions (the user's reference: 13x26 art px, small face framed by
hair, narrow body, both arms at the sides with hands, thin legs, small feet), in our own drawing and colours.
Drawn facing left like Terraria's NPC sheets, then mirrored so the sheet faces right. 16x26 art px per frame (the figure
is 13 wide, with room in front for the raised arm), 32x52 at 2x, 2 px gap, feet on the bottom row.
  0 idle  1-4 walk  5-8 walk carrying (hand up at the shoulder)  9 carry idle  10-11 working with the wrench
"""
from PIL import Image
import numpy as np

C = {
    # patrol cap
    '1': (34, 34, 20), '2': (78, 78, 46), '3': (112, 110, 68), '4': (148, 144, 96),
    # hair and outlines around it (the Nurse's brown ramp)
    'M': (48, 26, 23), 'J': (92, 51, 35), 'O': (126, 79, 54), 'P': (150, 105, 74),
    # skin (Terraria's warm ramp), pupil, eye white, mouth
    'Q': (230, 114, 51), 'R': (249, 155, 97), 'U': (255, 193, 157), 'T': (96, 44, 39), 'S': (43, 18, 18),
    'F': (247, 247, 247), 'b': (176, 84, 62),
    # OCP coverall: outline, dark, mid, light, name tape, camo
    'B': (30, 26, 16), 'A': (58, 52, 32), 'd': (100, 92, 60), 'g': (146, 134, 92), 'j': (190, 178, 128),
    'x': (70, 64, 40), 'k': (110, 122, 70), 'l': (188, 156, 104),
    # reflective PT belt
    'Y': (184, 196, 46), 'y': (238, 248, 110),
    # boots
    'p': (58, 36, 20), 'q': (122, 86, 50), 'r': (166, 124, 76),
    # wrench
    's': (112, 118, 130), 't': (190, 196, 206), 'u': (52, 56, 66),
}
FW, FH, OX = 16, 26, 3   # frame size, figure offset from the left (room in front for the arm)

HEAD = [
    ".............",   # 0
    ".............",   # 1
    "....11111....",   # 2 cap crown
    "...1443331...",   # 3
    "..143333331..",   # 4
    "1122222222M..",   # 5 band, brim out front
    "..MRRRRJOPM..",   # 6 forehead under the brim, sideburn, hair behind
    "..MQRRRJOPPM.",   # 7
    ".MRSFRRQJOPM.",   # 8 eye: pupil to the front, white behind it
    ".MRTFRRQUJOM.",   # 9 lower eye, ear
    ".MRRRRRQQJOM.",   # 10
    "..MRbRRQJJM..",   # 11 mouth
    "...MQQQQM....",   # 12 chin
]
BODY = [
    "..AjjjjjgdA..",   # 13 shoulders
    ".AjAgjxggAdA.",   # 14 arms at the sides, name tape
    ".AgAkgggdAdA.",   # 15
    ".AgAgglgdAdA.",   # 16
    ".ARAYyyyYARA.",   # 17 hands, PT belt
    ".AQAdddddAQA.",   # 18
]
LEGS = {
    'stand': ["...AddAddA...", "...AggAddA...", "...AggAddA...", "...AggAddA...", "...AggAddA...", "..prrpqqqp...", "..pppppppp..."],
    'a':     ["...AddAddA...", "..AggAAddA...", "..AggA.AddA..", ".AggA..AddA..", ".AggA...AddA.", "prrp....pqqp.", "pppp....pppp."],
    'pass':  ["...AddAddA...", "....AggdA....", "....AggdA....", "....AggdA....", "....AggdA....", "...prrqqp....", "...pppppp...."],
    'b':     ["...AddAddA...", "..AddAAggA...", "..AddA.AggA..", ".AddA..AggA..", ".AddA...AggA.", "pqqp....prrp.", "pppp....pppp."],
}


def blank():
    return [['.'] * FW for _ in range(FH)]


def paint(g, x, y, s):
    for k, ch in enumerate(s):
        if ch not in '. ' and 0 <= x + k < FW and 0 <= y < FH:
            g[y][x + k] = ch


def clear(g, x, y):
    if 0 <= x < FW and 0 <= y < FH:
        g[y][x] = '.'


def figure(legs):
    g = blank()
    for y, r in enumerate(HEAD + BODY + LEGS[legs]):
        assert len(r) == 13, (y, r)
        paint(g, OX, y, r)
    return g


def front_arm_carry(g):
    # the front arm (toward the face) comes up: hand at the shoulder where the blade rests
    for y in (14, 15, 16, 17, 18):
        for x in (1, 2):
            clear(g, OX + x, y)
    paint(g, OX + 1, 14, 'A')
    paint(g, OX - 1, 12, 'AA')
    paint(g, OX - 1, 13, 'ARQ')
    paint(g, OX + 0, 14, 'Ajg')
    paint(g, OX + 0, 15, 'AA')


def front_arm_work(g, up):
    for y in (14, 15, 16, 17, 18):
        for x in (1, 2):
            clear(g, OX + x, y)
    paint(g, OX + 1, 14, 'A')
    if up:
        # reaching up past the brim with the wrench
        for y in range(6, 14):
            paint(g, OX - 1, y, 'Agj' if y > 9 else 'Ag')
        paint(g, OX - 1, 5, 'AR')
        paint(g, OX - 1, 4, 'AQ')
        paint(g, OX - 2, 3, 'ut')
        paint(g, OX - 2, 2, 'ts')
        paint(g, OX - 2, 1, 'u')
    else:
        # forward at chest height, the wrench turned up
        paint(g, OX - 3, 13, 'AAAA')
        paint(g, OX - 3, 14, 'RAgj')
        paint(g, OX - 3, 15, 'QAAA')
        paint(g, OX - 3, 12, 't')
        paint(g, OX - 3, 11, 's')
        paint(g, OX - 3, 10, 'u')


def render(g):
    a = np.zeros((FH, FW, 4), np.uint8)
    for y in range(FH):
        for x in range(FW):
            ch = g[y][x]
            if ch != '.':
                a[y, x] = C[ch] + (255,)
    return a[:, ::-1]   # mirror: the sheet faces right


def up2(a):
    return a.repeat(2, axis=0).repeat(2, axis=1)


def main():
    frames = [render(figure('stand'))]
    for legs in ('a', 'pass', 'b', 'pass'):
        frames.append(render(figure(legs)))
    for legs in ('a', 'pass', 'b', 'pass'):
        g = figure(legs)
        front_arm_carry(g)
        frames.append(render(g))
    g = figure('stand'); front_arm_carry(g); frames.append(render(g))
    g = figure('stand'); front_arm_work(g, True); frames.append(render(g))
    g = figure('stand'); front_arm_work(g, False); frames.append(render(g))

    fw, fh, gap = FW * 2, FH * 2, 2
    sheet = np.zeros(((fh + gap) * len(frames) - gap, fw, 4), np.uint8)
    for k, fr in enumerate(frames):
        sheet[k * (fh + gap):k * (fh + gap) + fh] = up2(fr)
    Image.fromarray(sheet, 'RGBA').save('/home/claude/art/out/GroundCrew.png')

    refs = [Image.open('/root/.claude/uploads/898ddf96-b567-5c1c-be87-f72bb69c4ab6/546b8512-image.png').convert('RGBA'),
            Image.open('/root/.claude/uploads/898ddf96-b567-5c1c-be87-f72bb69c4ab6/cc9d0210-image.png').convert('RGBA')]
    show = [0, 1, 2, 5, 10, 11]
    prev = Image.new('RGBA', (80 + len(show) * 36, 60), (120, 150, 180, 255))
    x = 4
    for r in refs:
        prev.alpha_composite(r, (x, 58 - r.height))
        x += r.width + 6
    for k in show:
        prev.alpha_composite(Image.fromarray(up2(frames[k]), 'RGBA'), (x, 58 - fh))
        x += 36
    prev.resize((prev.width * 4, prev.height * 4), Image.NEAREST).save('/home/claude/art/crew_preview.png')


if __name__ == '__main__':
    main()
