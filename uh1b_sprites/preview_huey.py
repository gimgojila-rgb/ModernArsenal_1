"""Previews for the UH-1B layers: assembled on the grid background, and beside the AH-1G at the same scale."""
import os, sys, json
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ah1g_sprites'))
import build_huey as BH                     # noqa: E402
import preview as PC                        # noqa: E402  (Cobra preview helpers)

OUT = os.path.join(HERE, 'out')


def L(n):
    return Image.open(os.path.join(OUT, n + '.png')).convert('RGBA')


def huey(rotor_i=0, tail_deg=70.0, flip=False, blur=False):
    c = json.load(open(os.path.join(OUT, 'HueyBoss_coords.json')))
    pad_x, pad_y = 40, 16
    Wc, Hc = c['body_size'][0] + 2 * pad_x, c['body_size'][1] + 2 * pad_y
    im = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0))
    cx, cy = pad_x + c['body_size'][0] / 2, pad_y + c['body_size'][1] / 2
    bo = (c['body_size'][0] / 2, c['body_size'][1] / 2)

    def at(off):
        return (cx + (-off[0] if flip else off[0]), cy + off[1])

    def paste(img, pos, origin, fl=flip):
        if fl:
            img = img.transpose(Image.FLIP_LEFT_RIGHT); origin = (img.width - origin[0], origin[1])
        im.alpha_composite(img, (int(round(pos[0] - origin[0])), int(round(pos[1] - origin[1]))))

    trn = L('HueyBoss_TailRotorBlur' if blur else 'HueyBoss_TailRotor')
    tr = trn.rotate(tail_deg, resample=Image.NEAREST, center=(trn.width / 2, trn.height / 2))
    paste(L('HueyBoss'), (cx, cy), bo)
    paste(L('HueyBoss_Glass'), (cx, cy), bo)
    im.alpha_composite(L('HueyBoss_MarksR' if flip else 'HueyBoss_MarksL'), (int(cx - bo[0]), int(cy - bo[1])))
    paste(L('HueyBoss_Turret'), (cx, cy), bo)
    paste(L('HueyBoss_Pod'), (cx, cy), bo)
    paste(tr, at(c['tail_rotor_hub']), (tr.width / 2, tr.height / 2))
    rf = c['rotor_frame']
    rot = L('HueyBoss_MainRotorBlur') if blur else PC.frame(L('HueyBoss_MainRotor'), rotor_i, rf['size'][1], rf['stride'])
    paste(rot, at(c['rotor_axis']), rf['hub'])
    return im, (cx, cy), c


def closeup(path, scale=4, **kw):
    im, _, _ = huey(**kw)
    bg = PC.grid_bg(im.width, im.height); bg.alpha_composite(im)
    bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST).save(path)


def pair(path, scale=2):
    hi, (hx, hy), hc = huey()
    ci, (cx_, cy_) = PC.cobra()
    cc = json.load(open(os.path.join(HERE, '..', 'ah1g_sprites', 'out', 'CobraBoss_coords.json')))
    Wd = hi.width + ci.width + 20; Hd = max(hi.height, ci.height) + 40; ground = Hd - 30
    bg = PC.grid_bg(Wd, Hd)
    bg.alpha_composite(hi, (0, int(ground - (hy + hc['skid_bottom_y']))))
    bg.alpha_composite(ci, (hi.width + 20, int(ground - (cy_ + cc['skid_bottom_y']))))
    d = ImageDraw.Draw(bg)
    d.line([(0, ground), (Wd, ground)], fill=(90, 96, 108, 255))
    d.text((8, Hd - 22), 'UH-1B  12.08 m', fill=(170, 176, 186, 255))
    d.text((hi.width + 28, Hd - 22), 'AH-1G  13.54 m   (same 21.94 px/m)', fill=(170, 176, 186, 255))
    bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST).save(path)


if __name__ == '__main__':
    BH.build()
    PC.B.build()
    dst = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(dst, exist_ok=True)
    closeup(os.path.join(dst, 'preview_huey_x4.png'))
    pair(os.path.join(dst, 'preview_huey_cobra.png'))
