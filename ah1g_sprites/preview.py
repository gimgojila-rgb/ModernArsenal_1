"""
Previews for the AH-1G layers: the assembled aircraft on the project's grid background, next to the AH-64E at the
same scale, plus a layer breakdown. Run build_cobra.py first (or import it, as below).
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
import build_cobra as B

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
APACHE = os.path.join(HERE, '..', 'entrance_gif_v5_final', 'assets')
BG, LINE = (40, 44, 52, 255), (47, 52, 61, 255)


def grid_bg(w, h, step=16):
    im = Image.new('RGBA', (w, h), BG)
    d = ImageDraw.Draw(im)
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=LINE)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=LINE)
    return im


def L(name):
    return Image.open(os.path.join(OUT, name + '.png')).convert('RGBA')


def frame(sheet, i, h, stride):
    return sheet.crop((0, i * stride, sheet.width, i * stride + h))


def cobra(rotor_i=0, gun_i=0, gun_deg=0.0, tail_deg=30.0, flip=False, shark=True, pods=True, blur=False,
          canopy=True, turret=True):
    """assembled Cobra on a transparent canvas with room for the rotors; returns (image, body origin in it)"""
    c = json.load(open(os.path.join(OUT, 'CobraBoss_coords.json')))
    pad_x, pad_y = 40, 16
    Wc, Hc = c['body_size'][0] + 2 * pad_x, c['body_size'][1] + 2 * pad_y
    im = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0))
    cx, cy = pad_x + c['body_size'][0] / 2, pad_y + c['body_size'][1] / 2

    def at(off):
        return (cx + (-off[0] if flip else off[0]), cy + off[1])

    def paste(img, pos, origin, fl=flip):
        if fl:
            img = img.transpose(Image.FLIP_LEFT_RIGHT); origin = (img.width - origin[0], origin[1])
        im.alpha_composite(img, (int(round(pos[0] - origin[0])), int(round(pos[1] - origin[1]))))

    body_origin = (c['body_size'][0] / 2, c['body_size'][1] / 2)
    paste(L('CobraBoss'), (cx, cy), body_origin)
    if shark:
        paste(L('CobraBoss_Shark'), (cx, cy), body_origin)
    marks = L('CobraBoss_MarksR' if flip else 'CobraBoss_MarksL')
    im.alpha_composite(marks, (int(cx - body_origin[0]), int(cy - body_origin[1])))
    if canopy:
        paste(L('CobraBoss_Canopy'), (cx, cy), body_origin)
    # gun: rotate about its pivot, then the turret housing over its breech
    gf = c['gun_frame']
    g = frame(L('CobraBoss_Gun'), gun_i, gf['size'][1], gf['stride'])
    piv = gf['pivot']
    big = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    big.alpha_composite(g, (int(32 - piv[0]), int(32 - piv[1])))
    big = big.rotate(gun_deg, resample=Image.NEAREST, center=(32, 32))
    paste(big, at(c['gun_pivot']), (32, 32))
    if turret:
        paste(L('CobraBoss_Turret'), (cx, cy), body_origin)
    if pods:
        paste(L('CobraBoss_PodIn'), (cx, cy), body_origin)
        paste(L('CobraBoss_PodOut'), (cx, cy), body_origin)
    # tail rotor (rotated in code, as for the Apache)
    trn = L('CobraBoss_TailRotorBlur' if blur else 'CobraBoss_TailRotor')
    tr = trn.rotate(tail_deg, resample=Image.NEAREST, center=(trn.width / 2, trn.height / 2))
    paste(tr, at(c['tail_rotor_hub']), (tr.width / 2, tr.height / 2))
    # main rotor
    rf = c['rotor_frame']
    rot = L('CobraBoss_MainRotorBlur') if blur else frame(L('CobraBoss_MainRotor'), rotor_i, rf['size'][1], rf['stride'])
    paste(rot, at(c['rotor_axis']), rf['hub'])
    return im, (cx, cy)


def apache():
    """AH-64E assembled the same way as in the v5 entrance renderer (texture centre origin)"""
    body = Image.open(os.path.join(APACHE, 'ApacheEBoss.png')).convert('RGBA')
    rot = Image.open(os.path.join(APACHE, 'ApacheEBoss_MainRotor.png')).convert('RGBA').crop((0, 0, 278, 18))
    tr = Image.open(os.path.join(APACHE, 'ApacheEBoss_TailRotor.png')).convert('RGBA').rotate(30, resample=Image.NEAREST)
    gun = Image.open(os.path.join(APACHE, 'ApacheEBoss_Gun.png')).convert('RGBA')
    rad = Image.open(os.path.join(APACHE, 'ApacheEBoss_Radar.png')).convert('RGBA')
    im = Image.new('RGBA', (372 + 80, 126 + 32), (0, 0, 0, 0))
    ox, oy = 40, 16
    im.alpha_composite(gun, (ox + 81 - 33, oy + 99 - 7))
    im.alpha_composite(body, (ox, oy))
    im.alpha_composite(rad, (ox + 141 - 15, oy + 24 - 10))
    im.alpha_composite(tr, (ox + 337 - 33, oy + 59 - 33))
    im.alpha_composite(rot, (ox + 141 - 139, oy + 39 - 9))
    return im, (ox + 186, oy + 63), oy + 123         # image, body centre, wheel bottom y


def comparison(path, scale=2):
    ci, (ccx, ccy) = cobra()
    ai, (acx, acy), a_ground = apache()
    c = json.load(open(os.path.join(OUT, 'CobraBoss_coords.json')))
    c_ground = ccy + c['skid_bottom_y']
    Wd = ci.width + ai.width + 20
    Hd = max(ci.height, ai.height) + 40
    ground = Hd - 30
    bg = grid_bg(Wd, Hd)
    bg.alpha_composite(ai, (0, int(ground - a_ground)))
    bg.alpha_composite(ci, (ai.width + 20, int(ground - c_ground)))
    d = ImageDraw.Draw(bg)
    d.line([(0, ground), (Wd, ground)], fill=(90, 96, 108, 255))
    d.text((8, Hd - 22), 'AH-64E  15.04 m', fill=(170, 176, 186, 255))
    d.text((ai.width + 28, Hd - 22), 'AH-1G  13.54 m   (same 21.94 px/m)', fill=(170, 176, 186, 255))
    bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST).save(path)


def closeup(path, scale=4, **kw):
    ci, _ = cobra(**kw)
    bg = grid_bg(ci.width, ci.height)
    bg.alpha_composite(ci)
    bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST).save(path)


def breakdown(path, scale=3):
    names = ['CobraBoss', 'CobraBoss_Canopy', 'CobraBoss_Shark', 'CobraBoss_MarksL', 'CobraBoss_Turret',
             'CobraBoss_PodIn', 'CobraBoss_PodOut']
    tiles = [L(n) for n in names]
    extra = [L('CobraBoss_Gun'), L('CobraBoss_TailRotor'), L('CobraBoss_TailRotorBlur'),
             L('CobraBoss_MainRotor'), L('CobraBoss_MainRotorBlur')]
    w = max(t.width for t in tiles + extra) + 16
    h = sum(t.height + 18 for t in tiles) + sum(t.height + 18 for t in extra) + 8
    bg = grid_bg(w, h)
    d = ImageDraw.Draw(bg)
    y = 6
    for n, t in zip(names + ['Gun (rest, recoil)', 'TailRotor', 'TailRotorBlur', 'MainRotor (6 frames)', 'MainRotorBlur'],
                    tiles + extra):
        d.text((8, y), n, fill=(180, 186, 196, 255))
        bg.alpha_composite(t, (8, y + 12))
        y += t.height + 18
    bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST).save(path)


if __name__ == '__main__':
    B.build()
    dst = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(dst, exist_ok=True)
    comparison(os.path.join(dst, 'preview_vs_apache.png'))
    closeup(os.path.join(dst, 'preview_cobra_x4.png'))
    closeup(os.path.join(dst, 'preview_cobra_right_x4.png'), flip=True, rotor_i=2)
    breakdown(os.path.join(dst, 'preview_layers.png'))
