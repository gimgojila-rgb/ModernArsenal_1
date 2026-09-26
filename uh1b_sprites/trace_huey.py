"""
UH-1B body by a straight trace of the render (what the user asked for): every cell takes a centre-weighted sample of
a sharpened copy of the render, the samples are clustered into the render's own palette, lone pixels are voted away,
and the silhouette gets a dark outline. Text cells are refilled from the skin around them and redrawn as stencils.
"""
import numpy as np
from PIL import Image, ImageFilter
import build_huey as B
from build_huey import cv, X, Y, H, W, OX, OY, poly, runs_from
from px import Layer
from geom_huey import *

SRC = Image.open(B.os.path.join(B.HERE, 'ref', 'uh1b_side_render.webp')).convert('RGB').transpose(Image.FLIP_LEFT_RIGHT)
SHARP = np.asarray(SRC.filter(ImageFilter.UnsharpMask(radius=3, percent=120, threshold=2))).astype(np.float32)


def sample():
    out = np.zeros((H, W, 3), np.float32)
    for r in range(H):
        for c_ in range(W):
            x0 = NX + (c_ - OX) * PX_X; y1 = GY - (OY - r - 1) * PX_Y; y0 = y1 - PX_Y
            # centre 60% of the cell, median: keeps panel lines and edges crisp instead of averaging them away
            xa = int(round(x0 + 0.2 * PX_X)); xb = int(round(x0 + 0.8 * PX_X)) + 1
            ya = int(round(y0 + 0.2 * PX_Y)); yb = int(round(y0 + 0.8 * PX_Y)) + 1
            if xb <= 0 or yb <= 0 or xa >= SHARP.shape[1] or ya >= SHARP.shape[0]:
                continue
            blk = SHARP[max(ya, 0):yb, max(xa, 0):xb].reshape(-1, 3)
            out[r, c_] = np.median(blk, 0)
    return out


def kmeans(v, k, it=30, seed=3):
    rng = np.random.default_rng(seed)
    cen = v[rng.choice(len(v), k, replace=False)]
    for _ in range(it):
        d = ((v[:, None, :] - cen[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        for j in range(k):
            if (lab == j).any():
                cen[j] = v[lab == j].mean(0)
    return cen, lab


def mode_clean(idx, m, passes=2):
    """a cell that differs from 3+ of its 4 neighbours (and they agree) takes their value"""
    for _ in range(passes):
        new = idx.copy()
        for r in range(1, H - 1):
            for c_ in range(1, W - 1):
                if not m[r, c_]:
                    continue
                nb = [idx[r - 1, c_], idx[r + 1, c_], idx[r, c_ - 1], idx[r, c_ + 1]]
                nbm = [m[r - 1, c_], m[r + 1, c_], m[r, c_ - 1], m[r, c_ + 1]]
                vals = [v for v, ok in zip(nb, nbm) if ok]
                if len(vals) >= 3 and idx[r, c_] not in vals:
                    u, cnt = np.unique(vals, return_counts=True)
                    if cnt.max() >= 3:
                        new[r, c_] = u[cnt.argmax()]
        idx = new
    return idx


def trace_layer(mask, k, text=None, seed=3):
    col = S.copy()
    if text is not None:                      # refill lettering from the skin above it
        for r, c_ in zip(*np.nonzero(text)):
            rr = r
            while rr > 0 and text[rr, c_]:
                rr -= 1
            col[r, c_] = col[rr, c_]
    v = col[mask]
    cen, lab = kmeans(v.copy(), k, seed=seed)
    idx = np.full((H, W), -1); idx[mask] = lab
    idx = mode_clean(idx, mask)
    img = np.zeros((H, W, 4), np.uint8)
    img[mask, :3] = cen[idx[mask]].clip(0, 255).astype(np.uint8); img[mask, 3] = 255
    return img


S = sample()
LUMS = S @ np.array([0.299, 0.587, 0.114], np.float32)
