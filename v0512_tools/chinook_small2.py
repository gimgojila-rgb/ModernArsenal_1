"""
GuardianChinook.png v2: the Humvee fight's CH-47 brought down to the Apache's scale (0.583) without the mush of v1.
v1 area-averaged every cell and snapped the result to the palette, which turned flat panels into speckle, broke the
panel lines, washed out the dithered lower hull and made the "U.S. ARMY" decal unreadable. v2 works in layers on the
1x art (one cell per 2x2 block), then exports 2x nearest:
  1. fill   - each target cell takes the colour that covers most of it (no averaging, so flat panels stay flat);
              where the source is a two-colour checker dither, the cell keeps a checker in the same two colours.
  2. lines  - 1-px panel lines, seams and highlight rims are found in the source (a pixel darker/lighter than both
              neighbours across the line, with the line continuing along it) and projected pixel-centre to target,
              so every line comes through unbroken. Dark lines win over light ones where two land on one cell.
  3. decal  - the "U.S. ARMY" letters are lifted out before the fill and re-set in a 4-px pixel font.
  4. edge   - the silhouette edge is redrawn in the original's outline colour.
The rotor sheets are not touched here (chinook_small.py makes them at 1.25x the Apache's disk).
"""
from PIL import Image
import numpy as np

SRC = '/mnt/user-data/uploads/ModSources--ModernArsenal/Content/NPCs/Humvee/HumveeChinook.png'
OUT = '/home/claude/art/out/'
K = 0.583

a = np.array(Image.open(SRC).convert('RGBA'))[::2, ::2].astype(np.int32)   # 1x art, 131 x 328
H1, W1 = a.shape[:2]
op = a[..., 3] > 0
lum = a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11
OUTLINE = (16, 19, 16)

# ---- 3a. lift the decal out: text pixels take the pylon colour around them ----
TX0, TX1, TY0, TY1 = 246, 279, 30, 36
box = a[TY0:TY1 + 1, TX0:TX1 + 1]
dark = box[..., :3].sum(-1) < 200
bgc = box[~dark][:, :3]
vals, cnt = np.unique(bgc, axis=0, return_counts=True)
pylon = vals[np.argmax(cnt)]
text_col = tuple(np.unique(box[dark][:, :3], axis=0, return_counts=True)[0][0])
a[TY0:TY1 + 1, TX0:TX1 + 1][dark, :3] = pylon
lum = a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11

# palette index map
keys = a[..., 0] * 65536 + a[..., 1] * 256 + a[..., 2]
keys[~op] = -1

def lumk(q):
    return ((q >> 16) & 255) * 0.3 + ((q >> 8) & 255) * 0.59 + (q & 255) * 0.11


h, w = round(H1 * K), round(W1 * K)
out = np.zeros((h, w, 4), np.uint8)

# ---- 1. fill ----
for y in range(h):
    for x in range(w):
        y0, y1 = y / K, (y + 1) / K
        x0, x1 = x / K, (x + 1) / K
        wts = {}
        area = 0.0
        for yy in range(int(y0), min(H1, int(np.ceil(y1)))):
            for xx in range(int(x0), min(W1, int(np.ceil(x1)))):
                f = (min(y1, yy + 1) - max(y0, yy)) * (min(x1, xx + 1) - max(x0, xx))
                area += f
                k = int(keys[yy, xx])
                wts[k] = wts.get(k, 0.0) + f
        if wts.get(-1, 0.0) / area > 0.5:
            continue
        wts.pop(-1, None)
        ranked = sorted(wts.items(), key=lambda t: -t[1])
        k = ranked[0][0]
        darks = [(q, wv) for q, wv in ranked if lumk(q) < 34 and q != ranked[0][0]]
        if darks and darks[0][1] / area >= 0.3 and lumk(k) >= 34:
            k = darks[0][0]   # narrow dark slots and gaps (door window, seams) survive the shrink
        elif len(ranked) > 1 and ranked[1][1] / area > 0.3:
            # checker dither in the source? look at a slightly wider window for alternation of the two colours
            c1, c2 = ranked[0][0], ranked[1][0]
            ys, ye = max(0, int(y0) - 1), min(H1, int(np.ceil(y1)) + 1)
            xs, xe = max(0, int(x0) - 1), min(W1, int(np.ceil(x1)) + 1)
            win = keys[ys:ye, xs:xe]
            pair = np.isin(win, [c1, c2])
            alt = (win[:, 1:] != win[:, :-1]) & pair[:, 1:] & pair[:, :-1]
            if alt.sum() >= 0.45 * max(1, (pair[:, 1:] & pair[:, :-1]).sum()):
                lo, hi = sorted([c1, c2], key=lambda q: ((q >> 16) & 255) + ((q >> 8) & 255) + (q & 255))
                k = lo if (x + y) % 2 == 0 else hi
        out[y, x] = ((k >> 16) & 255, (k >> 8) & 255, k & 255, 255)

# ---- 2. lines ----
T = 10.0
def is_line(yy, xx, darker):
    s = 1 if darker else -1
    c = lum[yy, xx] * s
    res = []
    if 0 < yy < H1 - 1 and op[yy - 1, xx] and op[yy + 1, xx]:
        if c + T <= lum[yy - 1, xx] * s and c + T <= lum[yy + 1, xx] * s:
            res.append('h')
    if 0 < xx < W1 - 1 and op[yy, xx - 1] and op[yy, xx + 1]:
        if c + T <= lum[yy, xx - 1] * s and c + T <= lum[yy, xx + 1] * s:
            res.append('v')
    return res

cand = {True: {}, False: {}}
for darker in (True, False):
    for yy in range(H1):
        for xx in range(W1):
            if op[yy, xx]:
                r = is_line(yy, xx, darker)
                if r:
                    cand[darker][(yy, xx)] = r
layer = {}
for darker in (False, True):   # light first, dark overwrites
    cd = cand[darker]
    for (yy, xx), dirs in cd.items():
        keep = False
        for d in dirs:
            nb = [(yy, xx - 1), (yy, xx + 1)] if d == 'h' else [(yy - 1, xx), (yy + 1, xx)]
            if any(d in cd.get(n, []) for n in nb):
                keep = True
        if not keep:
            continue
        ty, tx = int((yy + 0.5) * K), int((xx + 0.5) * K)
        if out[ty, tx, 3]:
            layer[(ty, tx)] = tuple(a[yy, xx, :3])
for (ty, tx), c in layer.items():
    out[ty, tx, :3] = c

# ---- 2b. clean-up: a lone pixel whose 8 neighbours all share one colour takes that colour (weathering specks that
#          came through as noise); a checker keeps its diagonals, so dither survives ----
fixed = set(layer)
o2 = out.copy()
for y in range(1, h - 1):
    for x in range(1, w - 1):
        if not out[y, x, 3] or (y, x) in fixed:
            continue
        nb = out[y - 1:y + 2, x - 1:x + 2].reshape(9, 4)
        others = np.delete(nb, 4, 0)
        if (others == others[0]).all() and (others[0] != out[y, x]).any():
            o2[y, x] = others[0]
out = o2

# ---- 3a'. portholes: the 6x6 round windows come out as 4x4 rounded ones, colours from the source ----
rim, hi, top, low = (tuple(a[76, 108, :3]), tuple(a[76, 109, :3]), tuple(a[76, 111, :3]), tuple(a[78, 110, :3]))
PH = ['.RR.', 'RHTR', 'RLLR', '.RR.']
for px in (109, 149, 189, 229):
    cx, cy = int(round((px + 3) * K)) - 2, int(round((76 + 3) * K)) - 2
    for r in range(4):
        for c in range(4):
            ch = PH[r][c]
            if ch != '.':
                out[cy + r, cx + c, :3] = {'R': rim, 'H': hi, 'T': top, 'L': low}[ch]

# ---- 3b. decal: "U.S. ARMY" in a 4-px font ----
G = {
    'U': ['#.#', '#.#', '#.#', '###'],
    'S': ['.##', '#..', '..#', '##.'],
    'A': ['.#.', '#.#', '###', '#.#'],
    'R': ['##.', '#.#', '##.', '#.#'],
    'M': ['#.#', '###', '#.#', '#.#'],
    'Y': ['#.#', '#.#', '.#.', '.#.'],
    '.': ['.', '.', '.', '#'],
    ' ': ['..', '..', '..', '..'],
}
text = 'U.S. ARMY'
cols = []
for i, ch in enumerate(text):
    g = G[ch]
    for cx in range(len(g[0])):
        cols.append([g[r][cx] == '#' for r in range(4)])
    if i < len(text) - 1 and ch != ' ' and text[i + 1] != ' ':
        cols.append([False] * 4)
tw = len(cols)
cx0 = int(round(((TX0 + TX1) / 2 + 0.5) * K - tw / 2))
cy0 = int(round(((TY0 + 1 + TY1) / 2 + 0.5) * K - 2))
for i, col in enumerate(cols):
    for r in range(4):
        if col[r] and out[cy0 + r, cx0 + i, 3]:
            out[cy0 + r, cx0 + i, :3] = text_col

# ---- 4. edge ----
m = out[..., 3] > 0
edge = m.copy()
edge[1:-1, 1:-1] = m[1:-1, 1:-1] & ~(m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:])
out[edge, :3] = OUTLINE

Image.fromarray(out.repeat(2, 0).repeat(2, 1), 'RGBA').save(OUT + 'GuardianChinook.png')
print('body', w * 2, h * 2, 'text', tw, 'at', cx0, cy0, 'col', text_col)
