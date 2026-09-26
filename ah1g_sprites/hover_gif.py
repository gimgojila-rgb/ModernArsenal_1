"""
Hover loop GIF of the AH-1G layers with the rotor and nav-light VFX, drawn the way the game draws the Apache
(entrance_gif_v5_final/render_apache_e_v5.py): main rotor blur under the current side-view frame at 70 %, tail rotor
blur under its frame at 55 % turned in code, lights as additive glows from HumveeChinook_Glow.png.

Lights (lenses are neutral in the sprite, tinted here as in NavLightRig):
  port red on the near (left) wingtip, steady; white tail light on the fin tip, steady;
  red rotating beacon on the engine cowl: a sweep that flares once per 36 ticks (the lamp turning past the viewer),
  with a horizontal streak at the peak. The AH-1G has no white anti-collision strobes, so there are none.

usage: python3 hover_gif.py [out.gif]      (60 ticks a second, one tick per GIF frame)
"""
import math, os, sys, json
import numpy as np
from PIL import Image
import build_cobra as B
import preview as P

HERE = os.path.dirname(os.path.abspath(__file__))
GLOW = np.asarray(Image.open(os.path.join(HERE, '..', 'entrance_gif_v5_final', 'assets',
                                          'HumveeChinook_Glow.png')).convert('RGBA'))[..., 3].astype(np.float32) / 255
TICKS = 144
FW, FH = 480, 200                      # frame, 2x game pixels
PORT, TAILW, BEAC = (255, 50, 40), (255, 250, 235), (255, 40, 30)


def glow(n):
    n = max(2, int(n))
    return np.asarray(Image.fromarray((GLOW * 255).astype(np.uint8)).resize((n, n), Image.BILINEAR)).astype(np.float32) / 255


def add(arr, mask, pos, col, k):
    h, w = mask.shape
    x0, y0 = int(round(pos[0] - w / 2)), int(round(pos[1] - h / 2))
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(arr.shape[1], x0 + w), min(arr.shape[0], y0 + h)
    if xe > xs and ye > ys:
        arr[ys:ye, xs:xe, :3] += mask[ys - y0:ye - y0, xs - x0:xe - x0, None] * np.array(col, np.float32) * k


def fade(img, k):
    img = img.copy(); img.putalpha(img.getchannel('A').point(lambda v: int(v * k)))
    return img


def frame(t, layers, c):
    bg = P.grid_bg(FW, FH)
    ground = FH - 14
    bob = round(2.0 * math.sin(2 * math.pi * t / 144))               # slow hover bob, whole pixels
    cx, cy = FW // 2, ground - 34 - c['skid_bottom_y'] + bob            # body centre, skids 34 px above the ground
    # ground shadow and the ground line
    sh = Image.new('RGBA', (240, 8), (0, 0, 0, 0))
    a = np.zeros((8, 240, 4), np.uint8)
    yy, xx = np.mgrid[0:8, 0:240]
    e = ((xx - 120) / 120.0) ** 2 + ((yy - 4) / 4.0) ** 2
    a[..., 3] = np.where(e < 1, (70 - bob * 4) * np.sqrt(np.clip(1 - e, 0, 1)), 0).astype(np.uint8)
    bg.alpha_composite(Image.fromarray(a), (cx - 120 + 6, ground - 4))
    from PIL import ImageDraw
    ImageDraw.Draw(bg).line([(0, ground), (FW, ground)], fill=(90, 96, 108, 255))

    W2, H2 = c['body_size']
    ox, oy = cx - W2 // 2, cy - H2 // 2
    def at(off):
        return (cx + off[0], cy + off[1])
    def put(img, pos, origin):
        bg.alpha_composite(img, (int(round(pos[0] - origin[0])), int(round(pos[1] - origin[1]))))
    # gun, then body layers, turret over the breech, pods
    gf = c['gun_frame']
    g = layers['CobraBoss_Gun'].crop((0, 0, gf['size'][0], gf['size'][1]))
    put(g, at(c['gun_pivot']), gf['pivot'])
    for n in ('CobraBoss', 'CobraBoss_Shark', 'CobraBoss_MarksL', 'CobraBoss_Canopy', 'CobraBoss_Turret',
              'CobraBoss_PodIn', 'CobraBoss_PodOut'):
        bg.alpha_composite(layers[n], (ox, oy))
    # tail rotor: blur, then the blades turning (about 41 degrees a tick) at 55 %
    tb = layers['CobraBoss_TailRotorBlur']; tr = layers['CobraBoss_TailRotor']
    put(tb, at(c['tail_rotor_hub']), (tb.width / 2, tb.height / 2))
    r = fade(tr.rotate(-41.0 * t, resample=Image.NEAREST, center=(tr.width / 2, tr.height / 2)), 0.55)
    put(r, at(c['tail_rotor_hub']), (tr.width / 2, tr.height / 2))
    # main rotor: blur, then the side-view frame for this tick at 70 %
    rf = c['rotor_frame']
    mb = layers['CobraBoss_MainRotorBlur']
    put(mb, at(c['rotor_axis']), rf['hub'])
    fr = layers['CobraBoss_MainRotor'].crop((0, (t % 6) * rf['stride'], rf['size'][0], (t % 6) * rf['stride'] + rf['size'][1]))
    put(fade(fr, 0.7), at(c['rotor_axis']), rf['hub'])

    # lights
    arr = np.asarray(bg).astype(np.float32)
    add(arr, glow(28), at(c['wingtip_light']), PORT, 0.85); add(arr, glow(7), at(c['wingtip_light']), (255, 255, 255), 0.6)
    tail = at(B.to2x_offset(147.5, 33.0))
    add(arr, glow(22), tail, TAILW, 0.7); add(arr, glow(5), tail, (255, 255, 255), 0.5)
    ph = (t % 36) / 36.0
    sweep = max(0.0, math.cos(2 * math.pi * ph)) ** 6                    # lamp facing the viewer at ph 0
    bpos = at(c['beacon'])
    add(arr, glow(18), bpos, BEAC, 0.35)                               # the lens is always lit a little
    if sweep > 0.02:
        add(arr, glow(18 + 30 * sweep), bpos, BEAC, 0.95 * sweep)
        add(arr, glow(8), bpos, (255, 255, 255), 0.7 * sweep)
        stk = np.asarray(Image.fromarray((GLOW * 255).astype(np.uint8)).resize((int(40 + 110 * sweep), 8),
                                                                                  Image.BILINEAR)).astype(np.float32) / 255
        add(arr, stk, bpos, (255, 70, 50), 0.5 * sweep)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def main(path):
    B.build()
    c = json.load(open(os.path.join(B.OUT, 'CobraBoss_coords.json')))
    names = ['CobraBoss', 'CobraBoss_Shark', 'CobraBoss_MarksL', 'CobraBoss_Canopy', 'CobraBoss_Turret',
             'CobraBoss_PodIn', 'CobraBoss_PodOut', 'CobraBoss_Gun', 'CobraBoss_TailRotor', 'CobraBoss_TailRotorBlur',
             'CobraBoss_MainRotor', 'CobraBoss_MainRotorBlur']
    layers = {n: P.L(n) for n in names}
    frames = []
    for t in range(TICKS):
        f = frame(t, layers, c)
        frames.append(f.convert('RGB').resize((FW * 2, FH * 2), Image.NEAREST))
    strip = Image.new('RGB', (frames[0].width, frames[0].height * 4))
    for i, k in enumerate((0, 9, 18, 27)):                            # beacon peak, fading, dark: all in the palette
        strip.paste(frames[k], (0, i * frames[0].height))
    pal = strip.quantize(colors=255, method=Image.MEDIANCUT)
    out = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    out[0].save(path, save_all=True, append_images=out[1:], duration=20, loop=0, optimize=False, disposal=1)
    frames[0].save(os.path.splitext(path)[0] + '_peak.png')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(B.OUT, 'cobra_hover.gif'))
