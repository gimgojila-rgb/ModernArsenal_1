import sys, numpy as np
from PIL import Image, ImageDraw
import build_cobra as B
from px import over

def zoom(x0, x1, y0, y1, path, s=12, layers=None):
    L, _ = B.build(write=False)
    names = layers or ['CobraBoss', 'CobraBoss_Shark', 'CobraBoss_MarksL', 'CobraBoss_Canopy', 'CobraBoss_Turret',
                       'CobraBoss_PodIn', 'CobraBoss_PodOut']
    img = np.zeros_like(L['CobraBoss'])
    for n in names:
        img = over(img, L[n])
    c0, r0 = B.cv.cell(x0, y1); c1, r1 = B.cv.cell(x1, y0)
    crop = img[r0:r1 + 1, c0:c1 + 1]
    h, w = crop.shape[:2]
    bg = np.zeros((h, w, 4), np.uint8); bg[..., :3] = (40, 44, 52); bg[..., 3] = 255
    im = Image.fromarray(over(bg, crop)).resize((w * s, h * s), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for i in range(w + 1):
        x = c0 + i - B.OX
        d.line([(i * s, 0), (i * s, h * s)], fill=(255, 0, 255) if x % 5 == 0 else (70, 76, 88))
    for j in range(h + 1):
        y = B.OY - (r0 + j)
        d.line([(0, j * s), (w * s, j * s)], fill=(255, 0, 255) if y % 5 == 0 else (70, 76, 88))
    for i in range(w):
        x = c0 + i - B.OX
        if x % 5 == 0:
            d.text((i * s + 2, 1), str(x), fill=(255, 255, 0))
    for j in range(h):
        y = B.OY - (r0 + j) - 1
        if y % 5 == 0:
            d.text((1, j * s + 1), str(y), fill=(255, 255, 0))
    im.save(path)

if __name__ == '__main__':
    a = [float(v) for v in sys.argv[1:5]]
    zoom(*a, sys.argv[5], s=int(sys.argv[6]) if len(sys.argv) > 6 else 12)
