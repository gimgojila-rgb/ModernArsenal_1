"""
GroundCrew.png v3: the rotor crew drawn like Terraria's town NPCs: big head with white-and-iris eyes, hair showing under
the cap, short body, arms drawn over the torso, outlines in a darker hue instead of black. 20x24 art px per frame
(40x48 at 2x), frames stacked with a 2 px gap, facing right, feet on the bottom row. Light from the upper left.
  0 idle  1-4 walk  5-8 walk carrying (hand up at the shoulder)  9 carry idle  10-11 working with the wrench
Kit: OCP coveralls, patrol cap, reflective PT belt, gloves, coyote boots.
"""
from PIL import Image
import numpy as np

P = {
    'o': (44, 34, 30),
    'H': (146, 138, 102), 'C': (114, 108, 80), 'c': (86, 82, 60),
    'r': (72, 50, 36), 'R': (98, 70, 50),
    'S': (240, 188, 148), 's': (210, 152, 114), 'q': (174, 120, 88),
    'w': (250, 250, 250), 'e': (70, 50, 38),
    'L': (170, 160, 122), 'T': (140, 131, 98), 't': (112, 104, 78), 'd': (86, 80, 60),
    'G': (114, 122, 86), 'g': (94, 100, 70),
    'Y': (222, 234, 84), 'y': (170, 182, 58),
    'W': (66, 60, 52), 'V': (90, 82, 70),
    'B': (142, 114, 80), 'b': (104, 82, 58),
    'm': (170, 176, 186), 'M': (104, 110, 120),
}

BODY = [
    "......oooooo........",   # 0
    ".....oHHHCCCo.......",   # 1
    "....oHHCCCCCCo......",   # 2
    "....oHCCCCCCCCo.....",   # 3
    "....occcccccccccoo..",   # 4  band and brim
    "....orrSSSSSSSSo....",   # 5
    "....orsSSSSSweSo....",   # 6  eye
    "....orsqSSSSweSo....",   # 7  ear, eye
    "....orsSSSSSSSSo....",   # 8
    ".....osSSSSSqSo.....",   # 9  mouth
    "......ossSSSSo......",   # 10
    ".......oLLTTo.......",   # 11 collar
    "......oLLTTTTo......",   # 12
    ".....oLTTGTTTto.....",   # 13
    ".....oTTGGTTtto.....",   # 14
    ".....oyYYYYYyyo.....",   # 15 belt
    ".....ottTTTttdo.....",   # 16
]

LEGS = {
    0: [
        "......otTTtdo.......",
        "......otTotdo.......",
        "......otTotdo.......",
        "......otdotdo.......",
        ".....obBBobBBo......",
        ".....oooooooooo.....",
    ],
    1: [
        "......otTTtdo.......",
        ".....otTo..otdo.....",
        "....otTo....otdo....",
        "...otdo......otdo...",
        "..obBBo......obBBBo.",
        "..oooo.......ooooo..",
    ],
    2: [
        "......otTTtdo.......",
        "......otTtdo........",
        "......otTtdo........",
        "......otddo.........",
        ".....obBBBBo........",
        ".....oooooo.........",
    ],
    3: [
        "......otTTtdo.......",
        "......otTootTo......",
        ".....otTo..otTo.....",
        "....otdo....otdo....",
        "...obBBo...obBBBo...",
        "...oooo....oooooo...",
    ],
}
LEGS[4] = LEGS[2]


def arm_down(swing=0):
    # hanging arm; swing moves the forearm and glove back (-1) or forward (+1) for the walk
    d = {}
    for y in range(12, 16):
        k = swing if y >= 14 else 0
        d[(9 + k, y)] = 'L' if y == 12 else 'T'
        d[(10 + k, y)] = 't'
        d[(11 + k, y)] = 'o'
    d[(9 + swing, 16)] = 'W'
    d[(10 + swing, 16)] = 'V'
    d[(11 + swing, 16)] = 'o'
    d[(9 + swing, 17)] = 'o'
    d[(10 + swing, 17)] = 'o'
    if swing < 0:
        d[(10, 14)] = 'T'
        d[(10, 15)] = 't'
    return d


def arm_carry():
    # upper arm down to the elbow, forearm back up, glove at the shoulder under the blade
    d = {(9, 12): 'L', (9, 13): 'T', (10, 13): 't', (10, 14): 't', (11, 14): 'T', (11, 13): 'T', (11, 12): 'T',
         (12, 11): 'W', (11, 11): 'V', (12, 12): 'o', (12, 13): 'o', (12, 14): 'o', (11, 15): 'o', (10, 15): 'o',
         (13, 11): 'o', (12, 10): 'o', (11, 10): 'o'}
    return d


def arm_work(up):
    d = {(9, 12): 'L'}
    if up:
        for y in range(5, 12):
            d[(11, y)] = 'T'
            d[(12, y)] = 't'
            d[(13, y)] = 'o'
            d[(10, y)] = 'o' if y < 10 else 'T'
        d[(11, 4)] = 'W'
        d[(12, 4)] = 'V'
        d[(13, 4)] = 'o'
        d[(10, 4)] = 'o'
        d[(11, 3)] = 'o'
        d[(12, 3)] = 'm'
        d[(12, 2)] = 'm'
        d[(13, 2)] = 'M'
        d[(13, 1)] = 'm'
        d[(14, 1)] = 'o'
        d[(14, 2)] = 'o'
        d[(12, 1)] = 'o'
    else:
        for i, (x, y) in enumerate(((10, 12), (11, 11), (12, 10), (13, 9))):
            d[(x, y)] = 'T'
            d[(x + 1, y)] = 't'
            d[(x, y + 1)] = d.get((x, y + 1), 'o')
            d[(x + 1, y + 1)] = 'o'
        d[(14, 8)] = 'W'
        d[(15, 8)] = 'o'
        d[(14, 7)] = 'o'
        d[(15, 7)] = 'm'
        d[(16, 6)] = 'm'
        d[(16, 5)] = 'M'
        d[(17, 5)] = 'o'
        d[(17, 6)] = 'o'
        d[(15, 6)] = 'o'
    return d


def frame(legs, arm):
    rows = BODY + LEGS[legs]
    g = [list(r) for r in rows]
    assert all(len(r) == 20 for r in g), [len(r) for r in g]
    for (x, y), k in arm.items():
        g[y][x] = k
    a = np.zeros((24, 20, 4), np.uint8)
    for y in range(len(g)):
        for x, ch in enumerate(g[y]):
            if ch != '.':
                a[y + 1, x] = P[ch] + (255,)   # row 0 left clear
    return a


def up2(a):
    return a.repeat(2, axis=0).repeat(2, axis=1)


def main():
    frames = [frame(0, arm_down())]
    frames += [frame(p, arm_down(sw)) for p, sw in ((1, -1), (2, 0), (3, 1), (4, 0))]
    frames += [frame(p, arm_carry()) for p in (1, 2, 3, 4)]
    frames += [frame(0, arm_carry()), frame(0, arm_work(True)), frame(0, arm_work(False))]
    fw, fh, gap = 40, 48, 2
    sheet = np.zeros(((fh + gap) * len(frames) - gap, fw, 4), np.uint8)
    for i, f in enumerate(frames):
        sheet[i * (fh + gap):i * (fh + gap) + fh] = up2(f)
    Image.fromarray(sheet, 'RGBA').save('/home/claude/art/out/GroundCrew.png')
    prev = Image.new('RGBA', (len(frames) * 44 + 4, 56), (120, 150, 180, 255))
    for i, f in enumerate(frames):
        prev.alpha_composite(Image.fromarray(up2(f), 'RGBA'), (i * 44 + 4, 4))
    prev.resize((prev.width * 3, prev.height * 3), Image.NEAREST).save('/home/claude/art/crew_preview.png')


if __name__ == '__main__':
    main()
