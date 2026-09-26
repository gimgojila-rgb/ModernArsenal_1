"""
Idle hover GIFs for the AH-1G and UH-1B: rotor frames over the blur, the tail rotor spun in code, a gentle bob,
and the lights the way the NavLightRig does them (lens tinted in code, additive glow):
  red position light (port side shows when facing left), anti-collision beacon fading on a 72-tick cycle,
  white tail light steady, white strobe 3 ticks every 60. Grid background, 60 ticks a second, one GIF frame per 2 ticks.
"""
import os, sys, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ah1g_sprites'))
import preview_huey as PH          # noqa: E402
import preview as PC               # noqa: E402
import build_cobra as BC           # noqa: E402
import build_huey as BH            # noqa: E402

TICKS, STEP, SCALE = 144, 2, 2
MAIN_DEG, TAIL_MUL = 29.0, 4.86          # the Apache's rotor speeds


def glow_sprite(r):
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    d = np.hypot(xx, yy) / r
    return np.clip(1 - d, 0, 1) ** 2


def add_light(arr, x, y, rgb, k, r=9):
    """lens pixel block plus an additive glow, k 0..1"""
    if k <= 0:
        return
    g = glow_sprite(r) * k
    h, w = arr.shape[:2]
    x0, y0 = int(x) - r, int(y) - r
    for j in range(2 * r + 1):
        for i in range(2 * r + 1):
            yy, xx = y0 + j, x0 + i
            if 0 <= yy < h and 0 <= xx < w and g[j, i] > 0:
                arr[yy, xx, :3] = np.minimum(255, arr[yy, xx, :3] + np.array(rgb) * g[j, i] * 0.9)
    lx, ly = int(x) - 1, int(y) - 1
    core = np.array(rgb) * (0.55 + 0.45 * k) + 255 * 0.35 * k
    arr[max(ly, 0):ly + 2, max(lx, 0):lx + 2, :3] = np.minimum(255, core)


def beacon_k(t):
    return 0.5 - 0.5 * np.cos(2 * np.pi * (t % 72) / 72)


def run(kind, path):
    frames = []
    for t in range(0, TICKS, STEP):
        rot_i = int((t * MAIN_DEG) // 30) % 6
        tail = (t * MAIN_DEG * TAIL_MUL) % 360
        if kind == 'cobra':
            im, (cx, cy) = PC.cobra(rotor_i=rot_i, tail_deg=tail)
            blur, _ = PC.cobra(rotor_i=rot_i, tail_deg=tail, blur=True)
            c = json.load(open(os.path.join(HERE, '..', 'ah1g_sprites', 'out', 'CobraBoss_coords.json')))
            off = lambda x, y: BC.to2x_offset(x, y)
            lights = [('pos', off(42.0, 14.4), (255, 50, 40)), ('beacon', off(54.0, 35.5), (255, 40, 30)),
                      ('tail', off(134.3, 15.4), (255, 250, 235)), ('strobe', off(147.6, 33.3), (255, 255, 255))]
        else:
            im, (cx, cy), c = PH.huey(rotor_i=rot_i, tail_deg=tail)
            blur, _, _ = PH.huey(rotor_i=rot_i, tail_deg=tail, blur=True)
            off = lambda x, y: BH.to2x_offset(x, y)
            lights = [('pos', off(*BH.c((616, 190))), (255, 50, 40)), ('beacon', off(*BH.BEACON), (255, 40, 30)),
                      ('tail', off(*BH.c((1464, 246))), (255, 250, 235)), ('strobe', off(*BH.c((1520, 132))), (255, 255, 255))]
        # spinning look: blur disc with the blade frame over it at part strength
        a = np.asarray(blur).astype(np.float32)
        b = np.asarray(im).astype(np.float32)
        comp = Image.fromarray(np.where(b[..., 3:4] > 0, b * 0.6 + a * 0.4, a).clip(0, 255).astype(np.uint8))
        bob = int(round(1.5 * np.sin(2 * np.pi * t / 96)))
        bg = PC.grid_bg(comp.width, comp.height + 8)
        bg.alpha_composite(comp, (0, 4 + bob))
        arr = np.asarray(bg).astype(np.float32).copy()
        for name, o, rgb in lights:
            x, y = cx + o[0], cy + o[1] + 4 + bob
            k = {'pos': 1.0, 'tail': 0.8, 'beacon': beacon_k(t), 'strobe': 1.0 if t % 60 < 3 else 0.0}[name]
            add_light(arr, x, y, rgb, k, r=10 if name == 'strobe' else 8)
        fr = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert('RGB')
        frames.append(fr.resize((fr.width * SCALE, fr.height * SCALE), Image.NEAREST))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=33, loop=0, optimize=False)


if __name__ == '__main__':
    BC.build(); BH.build()
    dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out')
    os.makedirs(dst, exist_ok=True)
    run('cobra', os.path.join(dst, 'ah1g_idle.gif'))
    run('huey', os.path.join(dst, 'uh1b_idle.gif'))
