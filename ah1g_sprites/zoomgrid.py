"""gridded close-up of the assembled aircraft (preview.cobra) with reference cell numbers, for checking pixel work"""
import sys, numpy as np
from PIL import Image, ImageDraw
import build_cobra as B
import preview as P


def zoom(x0, x1, y0, y1, path, s=12, **kw):
    B.build()
    im, _ = P.cobra(**kw)
    padc_x, padc_y = 20, 8                      # preview padding (40, 16 px at 2x) in cells
    one = im.resize((im.width // 2, im.height // 2), Image.NEAREST)
    c0 = int(np.floor(x0 + B.OX)) + padc_x; c1 = int(np.floor(x1 + B.OX)) + padc_x
    r0 = int(np.floor(B.OY - y1)) + padc_y; r1 = int(np.floor(B.OY - y0)) + padc_y
    crop = one.crop((c0, r0, c1 + 1, r1 + 1))
    bg = Image.new('RGBA', crop.size, (40, 44, 52, 255)); bg.alpha_composite(crop)
    w, h = bg.size
    big = bg.resize((w * s, h * s), Image.NEAREST)
    d = ImageDraw.Draw(big)
    for i in range(w + 1):
        x = c0 - padc_x + i - B.OX
        d.line([(i * s, 0), (i * s, h * s)], fill=(255, 0, 255) if x % 5 == 0 else (64, 70, 82))
        if x % 5 == 0 and i < w:
            d.text((i * s + 2, 1), str(x), fill=(255, 255, 0))
    for j in range(h + 1):
        y = B.OY - (r0 - padc_y + j)
        d.line([(0, j * s), (w * s, j * s)], fill=(255, 0, 255) if y % 5 == 0 else (64, 70, 82))
        if y % 5 == 0 and j < h:
            d.text((1, j * s + 1), str(y - 1), fill=(255, 255, 0))
    big.save(path)


if __name__ == '__main__':
    a = [float(v) for v in sys.argv[1:5]]
    zoom(*a, sys.argv[5], s=int(sys.argv[6]) if len(sys.argv) > 6 else 12)
