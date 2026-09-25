import os, json, numpy as np
from PIL import Image, ImageDraw
from pix import *
from ext import *
from assemble import build_parts, compose, gun_on_canvas, ORDER, WHEEL_TL

OUT = 'export'
os.makedirs(f'{OUT}/npc', exist_ok=True); os.makedirs(f'{OUT}/gores', exist_ok=True); os.makedirs(f'{OUT}/preview', exist_ok=True)

def to_tex(arr, flip=True):
    im = Image.fromarray(arr, 'RGBA')
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((im.width * 2, im.height * 2), Image.NEAREST)

P = build_parts()
wheel_layers = make_wheel_frames()
wf = [f.render() for f in wheel_layers]
gun = make_gun()

# ---------------- NPC textures (all same canvas & origin, face LEFT, 2x)
layer_names = ['Frame', 'Engine', 'Cabin', 'Interior', 'WellRear', 'WellFront', 'Spare', 'Body',
               'DoorRear', 'DoorFront', 'Hood', 'Antenna', 'TurretShield', 'Turret']
for k in layer_names:
    to_tex(P[k].render()).save(f'{OUT}/npc/HumveeBoss_{k}.png')
full = compose(P, wf[0], gun, ORDER)
to_tex(full).save(f'{OUT}/npc/HumveeBoss.png')

# wheel sheet: 4 frames stacked vertically, 42x42 each, 2px gap (same layout rule as the Apache rotor sheet)
sheet = Image.new('RGBA', (42, 42 * 4 + 2 * 3), (0, 0, 0, 0))
for i, f in enumerate(wf):
    sheet.alpha_composite(to_tex(f), (0, i * 44))
sheet.save(f'{OUT}/npc/HumveeBoss_Wheel.png')
# gun, facing left
to_tex(gun.render()).save(f'{OUT}/npc/HumveeBoss_Gun.png')

# ---------------- gores: cropped detachable parts (face left)
def crop_layer(k):
    im = to_tex(P[k].render())
    bb = im.getbbox()
    return im.crop(bb), bb
gore_info = {}
for k in ('DoorRear', 'DoorFront', 'Hood', 'Turret', 'Spare'):
    im, bb = crop_layer(k)
    im.save(f'{OUT}/gores/Humvee{k}.png'); gore_info[k] = {'bbox_px_in_canvas': bb, 'size': im.size}
w0 = to_tex(wf[0]); w0.save(f'{OUT}/gores/HumveeWheel.png'); gore_info['Wheel'] = {'size': w0.size}

# ---------------- coordinates for the code (texture pixels, left-facing canvas 2x)
CW, CH = W * 2, H * 2
def ref_to_px(x, y):
    """continuous ref-cell point -> pixel in the flipped 2x canvas"""
    cx, cy = x + OX, y + OY
    return [round((W - cx) * 2, 1), round(cy * 2, 1)]
info = {
    'canvas_px': [CW, CH], 'faces': 'left', 'scale': '1 cell = 2x2 px (nearest)',
    'draw_order': ['Frame', 'Engine', 'Cabin', 'Interior', 'WellRear', 'WellFront', 'Spare', 'Wheel(rear)', 'Wheel(front)',
                   'Body', 'DoorRear', 'DoorFront', 'Hood', 'Antenna', 'TurretShield', 'Gun', 'Turret'],
    'wheel_centers_px': {'rear': ref_to_px(22.5, 41.5), 'front': ref_to_px(90.5, 41.5)},
    'wheel_sheet': {'frame_px': [42, 42], 'gap_px': 2, 'frames': 4, 'deg_per_frame': 11.25,
                    'pivot_in_frame_px': [21, 21]},
    'gun': {'size_px': [GUN_W * 2, GUN_H * 2], 'pivot_in_tex_px': [(GUN_W - GUN_PIVOT[0]) * 2, GUN_PIVOT[1] * 2],
            'pivot_in_canvas_px': ref_to_px(*GUN_PIVOT_REF), 'muzzle_len_px': (GUN_W - GUN_PIVOT[0]) * 2,
            'note': 'draw after TurretShield and before Turret: the side plate hides the receiver, the barrel passes in front of the shield'},
    'ground_contact_y_px': ref_to_px(0, 52.0)[1],
    'gores': gore_info,
}
json.dump(info, open(f'{OUT}/humvee_coords.json', 'w'), indent=1)

# ---------------- previews on a grid background (no characters, neutral captions)
def grid_bg(w, h, cell=16):
    im = Image.new('RGBA', (w, h), (58, 64, 74, 255))
    d = ImageDraw.Draw(im)
    for x in range(0, w, cell): d.line([(x, 0), (x, h)], fill=(68, 75, 86, 255))
    for y in range(0, h, cell): d.line([(0, y), (w, y)], fill=(68, 75, 86, 255))
    return im

def shot(show, gun_ang=0.0, wfi=0):
    return to_tex(compose(P, wf[wfi], gun, show, gun_ang))

views = [
    ('Complete', ORDER),
    ('Doors and hood removed', [k for k in ORDER if k not in ('DoorRear', 'DoorFront', 'Hood')]),
    ('Body shell removed', ['Frame', 'Engine', 'Cabin', 'Interior', 'Spare', 'Wheels', 'TurretShield', 'Gun', 'Turret']),
    ('Chassis, powertrain, seats', ['Frame', 'Engine', 'Interior', 'Wheels']),
    ('Frame and running gear', ['Frame', 'Wheels']),
]
Z = 3
pw, ph = CW * Z, CH * Z
sheet = grid_bg(pw * 2 + 60, (ph + 40) * 3 + 20)
d = ImageDraw.Draw(sheet)
for i, (cap, show) in enumerate(views):
    im = shot(show)
    im = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
    x = 20 + (i % 2) * (pw + 20); y = 20 + (i // 2) * (ph + 40)
    sheet.alpha_composite(im, (x, y))
    d.text((x, y + ph + 6), cap, fill=(200, 205, 212, 255))
# gun elevation / wheel frames strip in the last slot
x = 20 + pw + 20; y = 20 + 2 * (ph + 40)
im = shot(ORDER, gun_ang=-0.26, wfi=2)
im = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
sheet.alpha_composite(im, (x, y)); d.text((x, y + ph + 6), 'Gun elevated 15 deg, wheel frame 3', fill=(200, 205, 212, 255))
sheet.save(f'{OUT}/preview/humvee_breakdown.png')

# exploded layer list
names = ['Frame', 'Engine', 'Cabin', 'Interior', 'WellRear', 'WellFront', 'Spare', 'Body', 'DoorRear', 'DoorFront', 'Hood', 'Antenna', 'TurretShield', 'Turret']
Z2 = 2
cols = 3
tw, th = CW * Z2, CH * Z2
ex = grid_bg(cols * (tw + 20) + 20, ((len(names) + 2 + cols - 1) // cols) * (th + 34) + 20)
d = ImageDraw.Draw(ex)
items = [(n, to_tex(P[n].render())) for n in names]
items.append(('Wheel x4 frames', None)); items.append(('Gun', to_tex(gun.render())))
for i, (n, im) in enumerate(items):
    x = 20 + (i % cols) * (tw + 20); y = 20 + (i // cols) * (th + 34)
    if n.startswith('Wheel'):
        for j, f in enumerate(wf):
            t = to_tex(f).resize((42 * Z2, 42 * Z2), Image.NEAREST)
            ex.alpha_composite(t, (x + j * (42 * Z2 + 8), y + 40))
    else:
        im2 = im.resize((im.width * Z2, im.height * Z2), Image.NEAREST)
        ex.alpha_composite(im2, (x, y + (0 if im.height > 20 else 90)))
    d.text((x, y + th + 8), n, fill=(200, 205, 212, 255))
ex.save(f'{OUT}/preview/humvee_layers.png')
print(json.dumps(info['wheel_centers_px']), info['gun'])
