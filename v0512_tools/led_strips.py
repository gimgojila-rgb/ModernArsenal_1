"""
Formation ("slime") light strips on the Gray Eagle and the Shadow, redone as LED bars: lit cells with a darker, deeper
green separator every two or three cells, and the glow mask (_Slime.png) cut at the separators so the glow comes out
segmented too. Gray Eagle art is 2x (cells are 2x2 blocks), the Shadow is drawn 1:1 (cells are single pixels).
"""
from PIL import Image
import numpy as np

B = '/mnt/user-data/uploads/ModSources--ModernArsenal/Content/NPCs/Guardian/'
OUT = '/home/claude/art/out/'
LIT_HI = (204, 228, 182)   # first cell of each lit pair, a touch hotter
LIT = (176, 198, 160)      # the original strip colour
SEP = (70, 90, 62)         # separator: darker, deeper green housing between cells


def paint(name, cells, scale):
    body = np.array(Image.open(B + name + '.png').convert('RGBA'))
    mask = np.array(Image.open(B + name + '_Slime.png').convert('RGBA'))
    for strip, pattern in cells:
        for (x, y), ch in zip(strip, pattern):
            col = {'H': LIT_HI, 'L': LIT, 'D': SEP}[ch]
            for dy in range(scale):
                for dx in range(scale):
                    X, Y = x * scale + dx, y * scale + dy
                    assert mask[Y, X, 3] > 0, (name, X, Y)
                    body[Y, X, :3] = col
                    if ch == 'D':
                        mask[Y, X] = 0
    Image.fromarray(body, 'RGBA').save(OUT + name + '.png')
    Image.fromarray(mask, 'RGBA').save(OUT + name + '_Slime.png')


eagle = [
    ([(88 + i, 12) for i in range(4)], 'HLDH'),
    ([(13 + i, 14) for i in range(6)], 'HLDHLD'),
    ([(85, 18 + i) for i in range(5)], 'HLDHL'),
]
shadow = [
    ([(69, 7), (70, 8), (71, 9)], 'HDL'),
    ([(54 + i, 14) for i in range(4)], 'HLDH'),
    ([(7 + i, 15) for i in range(6)], 'HLDHLD'),
]
paint('GrayEagleUAV', eagle, 2)
paint('ShadowUAV', shadow, 1)

# preview: before / after, zoomed on the strips
for name, boxes, z in (('GrayEagleUAV', [(160, 16, 196, 50), (16, 20, 48, 36)], 8), ('ShadowUAV', [(0, 4, 76, 20)], 8)):
    before = Image.open(B + name + '.png').convert('RGBA')
    after = Image.open(OUT + name + '.png').convert('RGBA')
    tiles = []
    for bx in boxes:
        for im in (before, after):
            t = Image.new('RGBA', (bx[2] - bx[0], bx[3] - bx[1]), (70, 90, 120, 255))
            t.alpha_composite(im.crop(bx))
            tiles.append(t.resize((t.width * z, t.height * z), Image.NEAREST))
    W = sum(t.width + 10 for t in tiles)
    H = max(t.height for t in tiles)
    sheet = Image.new('RGBA', (W, H), (30, 30, 30, 255))
    x = 0
    for t in tiles:
        sheet.alpha_composite(t, (x, 0))
        x += t.width + 10
    sheet.save('/home/claude/art/led_' + name + '.png')
print('ok')
