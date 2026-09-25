import numpy as np
from dsp import *

# ---------------- source: kyles "engine idle van diesel exhaust ... side4 nearby" (CC0)
idle = to44(load('idle'))
idle = hp(idle, 28)
idle = low_shelf(idle, 140, 3.0)                       # a touch more chest, it is a boss truck
# loop: ~4.5 s from the steadiest stretch, seam aligned on the 60.7 Hz firing pulse
a = int(12.0 * SR)
X = int(0.30 * SR)
L0 = int(4.5 * SR)
y = idle[a:a + L0 + X + 4000]
L, c = best_loop_len(y, L0, X, 1500)
loop = make_loop(y, L, X, c)
loop = to_lufs(loop, -15.0)
print('idle loop', round(len(loop) / SR, 3), 's  seam corr', round(c, 3), ' seam jump / p99 step', [round(v, 4) for v in seam_report(loop)], lufs(loop))
save('HumveeIdleLoop', loop)

# ---------------- source: kyles "truck big diesel engine work up a hill sustained rev and pass by2" (CC0)
acc = to44(load('accel'))
acc = hp(acc, 30)
acc = low_shelf(acc, 160, 3.0)

# 2) sustained high-rev drive loop: 6.4 .. 9.7 s, approach swell flattened out before looping
d0, d1 = int(6.2 * SR), int(9.9 * SR)
drv = acc[d0:d1].copy()
e = env(drv, 0.45)
g = np.median(e) / e
drv = drv * g
X2 = int(0.25 * SR)
L0 = int(3.0 * SR)
L2, c2 = best_loop_len(drv, L0, X2, 1200)
dloop = make_loop(drv, L2, X2, c2)
dloop = to_lufs(dloop, -14.0)
print('drive loop', round(len(dloop) / SR, 3), 's  seam corr', round(c2, 3), [round(v, 4) for v in seam_report(dloop)], lufs(dloop))
save('HumveeDriveLoop', dloop)

# 3) pass-by: roars past and drops away (for dashes that go past the player)
p0, p1 = int(8.4 * SR), int(15.2 * SR)
pas = acc[p0:p1].copy()
pas = fade(pas, fin=0.25, fout=1.2)
pas = to_lufs(pas, -14.0)
print('passby', round(len(pas) / SR, 2), lufs(pas))
save('HumveePassBy', pas)

# 1) rev-up: idle revs up and hands over to the loaded engine, then settles at drive-loop pitch.
#    Built by varispeed on the two recordings, the way engine sounds are made in games.
T = 3.2
n = int(T * SR); t = np.arange(n) / SR
idle_src = np.tile(loop, 3)
drv_src = np.tile(dloop, 3)
r_idle = smooth(t, 0.0, 1.1, 1.0, 1.55)                              # idle flares up
r_drv = np.where(t < 1.9, smooth(t, 0.25, 1.9, 0.72, 1.12), smooth(t, 1.9, 2.7, 1.12, 1.0))   # load builds, overshoot, settle
A = varispeed(idle_src, r_idle)
B = varispeed(drv_src, r_drv)
xf = smooth(t, 0.35, 1.25, 0.0, 1.0)
rev = A * np.cos(xf * np.pi / 2) + B * np.sin(xf * np.pi / 2)
rev *= 10 ** (smooth(t, 0.2, 1.8, -4.0, 0.0) / 20)
rev = fade(rev, fin=0.02, fout=0.05)
rev = to_lufs(rev, -13.0)
print('accel (rev-up)', round(len(rev) / SR, 2), lufs(rev))
save('HumveeAccel', rev)
