import numpy as np, json
from PIL import Image
from pix import *
from ext import *
from inner import make_frame, make_engine, make_interior, make_cabin

ORDER = ['Frame', 'Engine', 'Cabin', 'Interior', 'WellRear', 'WellFront', 'Spare', 'Wheels', 'Body',
         'DoorRear', 'DoorFront', 'Hood', 'Antenna', 'TurretShield', 'Gun', 'Turret']

def gun_on_canvas(gun, ang=0.0):
    img = np.zeros((H, W, 4), np.uint8)
    g = gun.render()
    px, py = GUN_PIVOT
    for yy in range(GUN_H):
        for xx in range(GUN_W):
            if g[yy, xx, 3] == 0: continue
            dx, dy = xx + 0.5 - px, yy + 0.5 - py
            rx = GUN_PIVOT_REF[0] + dx * np.cos(ang) - dy * np.sin(ang)
            ry = GUN_PIVOT_REF[1] + dx * np.sin(ang) + dy * np.cos(ang)
            img[int(np.floor(ry)) + OY, int(np.floor(rx)) + OX] = g[yy, xx]
    return img

def paste(out, tex, rx, ry):
    h, w = tex.shape[:2]
    x0, y0 = int(rx) + OX, int(ry) + OY
    a = tex[..., 3:4].astype(np.float32) / 255
    reg = out[y0:y0 + h, x0:x0 + w].astype(np.float32)
    reg[..., :3] = tex[..., :3] * a + reg[..., :3] * (1 - a)
    reg[..., 3:4] = np.maximum(reg[..., 3:4], tex[..., 3:4])
    out[y0:y0 + h, x0:x0 + w] = reg.astype(np.uint8)

WHEEL_TL = [(12, 31), (80, 31)]      # ref-cell top-left of the 21x21 wheel textures

def build_parts():
    body, sil = make_body()
    P = {'Frame': make_frame(), 'Engine': make_engine(), 'Cabin': make_cabin(), 'Interior': make_interior(),
         'WellRear': make_well(False), 'WellFront': make_well(True), 'Spare': make_spare(),
         'Body': body, 'DoorRear': make_door(False), 'DoorFront': make_door(True), 'Hood': make_hood(),
         'Antenna': make_antenna(), 'Turret': make_turret(), 'TurretShield': make_turret_shield()}
    vsil = np.zeros((H, W), bool)
    for k in ('WellRear', 'WellFront', 'Spare', 'Body', 'DoorRear', 'DoorFront', 'Hood', 'Turret', 'TurretShield'):
        vsil |= P[k].occ()
    for cx_ in (22.5, 90.5):
        vsil |= cov_ellipse(cx_, 41.5, 10.5, 10.5) >= 0.5
    for k in ('Spare', 'Body', 'DoorRear', 'DoorFront', 'Hood', 'Turret', 'TurretShield'):
        P[k].outline2(vsil, seam=1)
    for k in ('Frame', 'Engine', 'Interior'):
        P[k].outline()
    P['Cabin'].outline(tone=0)
    return P

def compose(P, wheels, gun, show, gun_ang=0.0, bg=None):
    out = np.zeros((H, W, 4), np.uint8)
    if bg is not None:
        out[..., :3] = bg; out[..., 3] = 255
    for k in ORDER:
        if k not in show: continue
        if k == 'Wheels':
            for (tx, ty) in WHEEL_TL:
                paste(out, wheels, tx, ty)
        elif k == 'Gun':
            out = composite([out, gun_on_canvas(gun, gun_ang)])
        else:
            out = composite([out, P[k]])
    return out

if __name__ == '__main__':
    P = build_parts()
    wf = [f.render() for f in make_wheel_frames()]
    gun = make_gun()
    BG = (118, 128, 140)
    full = compose(P, wf[0], gun, ORDER, bg=BG)
    save_scaled(full, 'out/v_full_x6.png', 6)
    save_scaled(full, 'out/v_full_flip_x3.png', 3, flip=True)
    cut = compose(P, wf[0], gun, [k for k in ORDER if k not in ('DoorRear', 'DoorFront', 'Hood')], bg=BG)
    save_scaled(cut, 'out/v_cut_flip_x3.png', 3, flip=True)
    skel = compose(P, wf[0], gun, ['Frame', 'Engine', 'Interior', 'Wheels'], bg=BG)
    save_scaled(skel, 'out/v_skel_flip_x3.png', 3, flip=True)
