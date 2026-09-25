"""
Recovered-record lore items, 16x16 art (32x32 at 2x). Outlines in each material's darkest tone, light from the upper left.
  LoreHumvee    Dagger Two-One's field notebook: olive waterproof cover, elastic band, a pencil clipped to it
  LoreApache    One-One's flight data recorder: the orange box with reflective stripes, handle, locator beacon
  LoreGuardian  the data transfer cartridge out of the Guardian: dark case, cyan label, gold contacts
"""
from PIL import Image
import numpy as np

OUT = '/home/claude/art/out/'


def grid_to_img(rows, pal):
    h, w = len(rows), len(rows[0])
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        assert len(r) == w, (y, len(r), r)
        for x, ch in enumerate(r):
            if ch != '.':
                a[y, x] = pal[ch] + (255,)
    return a


def save(a, name):
    Image.fromarray(a.repeat(2, 0).repeat(2, 1), 'RGBA').save(OUT + name + '.png')
    return a


# field notebook, three-quarter tilt, cover facing us
NOTE = {
    'o': (30, 34, 20), '1': (58, 66, 38), '2': (82, 92, 54), '3': (108, 120, 70), '4': (140, 152, 94),
    'p': (226, 222, 196), 'P': (190, 184, 156),           # page edges
    'e': (26, 26, 28), 'E': (60, 60, 64),                 # elastic
    'y': (230, 186, 60), 'Y': (170, 128, 36), 'k': (60, 44, 30), 'g': (160, 164, 170),   # pencil
    'w': (214, 208, 180),                                 # label
}
notebook = [
    "................",
    "..........oo....",
    "...ooooooooyo...",
    "..o4443333oyYo..",
    "..o43333333yYo..",
    "..o33wwwww3yYo..",
    "..o33wkkkw3yYo..",
    "..o33wwwww2yYo..",
    "..o3333322ogoo..",
    "..eeeeeeeeeeeEEo",
    "..o3333222221Po.",
    "..o3332222221Po.",
    "..o3322222211Po.",
    "..o2222221111Po.",
    "...ooooooooooPo.",
    "............oo..",
]

# flight data recorder: orange box, white reflective bands, carry handle, locator beacon cylinder on the front
FDR = {
    'o': (70, 26, 8), '1': (170, 64, 18), '2': (214, 96, 30), '3': (246, 134, 48), '4': (255, 176, 96),
    'w': (236, 236, 228), 'W': (184, 184, 176),
    'k': (34, 34, 38), 'K': (70, 70, 78), 's': (120, 124, 134), 'S': (170, 174, 184),
}
fdr = [
    "................",
    "....kkkkkk......",
    "....k....k......",
    "..ooKooooKooo...",
    "..o444433333o...",
    "..o433333332o...",
    "..owwwwwwwwWo...",
    "..o333333322o...",
    "..o333333222okk.",
    "..o332222221oSKk",
    "..owwwwwwwwWoSKk",
    "..o322222111oSKk",
    "..o222221111okk.",
    "..o211111111o...",
    "..oooooooooooo..",
    "................",
]

# data transfer cartridge: dark case, cyan label with a lock diamond, gold contacts
DTC = {
    'o': (14, 16, 22), '1': (34, 38, 48), '2': (52, 58, 72), '3': (76, 84, 102), '4': (112, 122, 144),
    'c': (60, 205, 255), 'C': (24, 120, 170), 'n': (3, 20, 36), 'w': (220, 250, 255),
    'g': (236, 196, 90), 'G': (170, 128, 44),
}
dtc = [
    "................",
    "................",
    "...oooooooooo...",
    "..o4433333332o..",
    "..o4ccccccccCo..",
    "..o3cnnwnnnnCo..",
    "..o3cnwnwnnnCo..",
    "..o3cnnwnnnnCo..",
    "..o3CCCCCCCCCo..",
    "..o3222222221o..",
    "..o3232323221o..",
    "..o2222222211o..",
    "...oGgGgGgGgo...",
    "....gGgGgGgG....",
    "................",
    "................",
]

if __name__ == '__main__':
    parts = [save(grid_to_img(notebook, NOTE), 'LoreHumvee'), save(grid_to_img(fdr, FDR), 'LoreApache'), save(grid_to_img(dtc, DTC), 'LoreGuardian')]
    prev = Image.new('RGBA', (3 * 40 + 8, 44), (120, 150, 180, 255))
    for k, a in enumerate(parts):
        prev.alpha_composite(Image.fromarray(a.repeat(2, 0).repeat(2, 1), 'RGBA'), (6 + k * 40, 6))
    prev.resize((prev.width * 5, prev.height * 5), Image.NEAREST).save('/home/claude/art/lore_preview.png')
    print('ok')
