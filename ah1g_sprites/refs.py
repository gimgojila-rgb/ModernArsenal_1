"""
Registers the three AH-1G references onto one frame so every layer is measured in the same units.

Frame: X metres aft of the nose tip, Y metres above the skid bottom. Pixel art cells are 1/10.97 m, the Apache body
scale (ApacheBoss.png: 330 px of body for a 15.04 m fuselage = 21.94 px/m at 2x = 10.97 cells/m at 1x).

  ref/ah1g_bell_ga_209900-9.webp  Bell general arrangement drawing with dimensions. Sets the geometry.
                                  90.04 px/m from the 52'11.65" and 44'5.2" dimension lines; the scan is turned about
                                  0.5 deg, straightened with y' = y - 0.0085 (x - 582). Nose tip x 582, skid bottom y 1160.5.
                                  Checks: nose to mast 4.354 m (spec 14'4" = 4.369 m), tail rotor 2.62 m (spec 8'6" = 2.59 m).
  ref/ah1g_color_profile.png      colour profile (camouflage, shark mouth, stores). Warped onto the drawing piecewise
  ref/ah1g_line_3view.png         line profile of a production aircraft (turret, intake, nacelle, panels). Same warp.
                                  Anchors for both: nose tip, mast, tail rotor hub (x); skid bottom, tail rotor hub (y).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'ref')
CPM = 10.97                                   # 1x cells per metre
MAST_X, HUB_X, HUB_Y = 4.354, 12.519, 2.714   # metres, measured on the Bell drawing


def pw(v, src, dst):
    """piecewise-linear map, extrapolated linearly past both ends"""
    src = np.asarray(src, float); dst = np.asarray(dst, float)
    out = np.interp(v, src, dst)
    lo = v < src[0]; hi = v > src[-1]
    out = np.where(lo, dst[0] + (v - src[0]) * (dst[1] - dst[0]) / (src[1] - src[0]), out)
    out = np.where(hi, dst[-1] + (v - src[-1]) * (dst[-1] - dst[-2]) / (src[-1] - src[-2]), out)
    return out


def src3(X, Y):
    x = 582 + X * 90.04
    y = 1160.5 - Y * 90.04 + 0.0085 * (x - 582)
    return x, y


def src1(X, Y):
    return pw(X, [0, MAST_X, HUB_X], [11, 165, 444.2]), pw(Y, [0, HUB_Y], [318, 225])


def src2(X, Y):
    return pw(X, [0, MAST_X, HUB_X], [133.5, 254.5, 462.5]), pw(Y, [0, HUB_Y], [107.5, 40.8])


def _load(n):
    return np.asarray(Image.open(os.path.join(IMG, n)).convert('RGB')).astype(np.float32)


_R = {}


def ref(k):
    if k not in _R:
        _R[k] = _load({1: 'ah1g_color_profile.png', 2: 'ah1g_line_3view.png', 3: 'ah1g_bell_ga_209900-9.webp'}[k])
    return _R[k]


def sample(img, x, y):
    h, w = img.shape[:2]
    x0 = np.clip(np.floor(x).astype(int), 0, w - 2); y0 = np.clip(np.floor(y).astype(int), 0, h - 2)
    fx = np.clip(x - x0, 0, 1)[..., None]; fy = np.clip(y - y0, 0, 1)[..., None]
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


def warp(k, X, Y):
    f = {1: src1, 2: src2, 3: src3}[k]
    sx, sy = f(X, Y)
    return sample(ref(k), sx, sy)


def grid_xy(x0c, x1c, y0c, y1c, ppc):
    """metre coordinates of a raster covering cells x0c..x1c (aft) and y0c..y1c (up) at ppc pixels per cell"""
    nx = int(round((x1c - x0c) * ppc)); ny = int(round((y1c - y0c) * ppc))
    xs = x0c + (np.arange(nx) + 0.5) / ppc
    ys = y1c - (np.arange(ny) + 0.5) / ppc
    Xc, Yc = np.meshgrid(xs, ys)
    return Xc / CPM, Yc / CPM
