import numpy as np
from scipy.io import wavfile
from dsp import *

# close, dry crack: qubodup "50 Caliber MG" (CC0, US gov footage), clean single-fire part
close = to44(load('m2_loud'))
# exterior body + echo: klangfabrik "50 CAL Machine Gun" (CC0), 44.1k already
sr, far = wavfile.read('m2_quiet.wav')  # decoded at 48k by ffmpeg earlier
far = to44(far.astype(np.float64))
close = hp(close, 35); far = hp(far, 35)

def cut(x, t0, dur, pre=0.002):
    a = int((t0 - pre) * SR); return x[a:a + int(dur * SR)].copy()

def join_tail(body, tail, xf=0.012):
    """crossfade a body into a decay tail, matching level at the seam"""
    n = int(xf * SR)
    lb = np.sqrt(np.mean(body[-n:] ** 2)) + 1e-9
    lt = np.sqrt(np.mean(tail[:n] ** 2)) + 1e-9
    tail = tail * (lb / lt)
    u = np.linspace(0, 1, n)
    out = np.concatenate([body[:-n], body[-n:] * (1 - u) + tail[:n] * u, tail[n:]])
    return out

# exterior decay tails after the last round of each run
tail1 = cut(far, 8.358 + 0.100, 0.55, 0)
tail2 = cut(far, 17.886 + 0.100, 0.45, 0)

CLOSE_ON = [32.021, 32.155, 32.421, 33.752]
FAR_ON = [7.580, 7.693, 7.803, 7.914]
for k, (c_on, f_on) in enumerate(zip(CLOSE_ON, FAR_ON)):
    crack = cut(close, c_on, 0.118)
    crack = fade(crack, fin=0.0015, fout=0.03)
    body = cut(far, f_on, 0.104)
    body = fade(body, fin=0.0015)
    body = join_tail(body, tail1 if k % 2 == 0 else tail2)
    n = max(len(crack), len(body))
    mix = np.zeros(n)
    mix[:len(body)] += body * 0.85
    mix[:len(crack)] += crack * 1.0
    mix = low_shelf(mix, 170, 4.5)            # .50 cal weight
    mix = fade(mix, fout=0.12)
    mix = mix / np.max(np.abs(mix)) * 1.9
    mix = soft_limit(mix, 0.89)
    save(f'M2Shot{k + 1}', mix)
    print(f'M2Shot{k + 1}', round(len(mix) / SR, 3), 's', lufs(mix))

# burst-end echo (exterior slapback), played once when a burst stops
bt = cut(far, 8.358 + 0.090, 0.95, 0)
bt = fade(bt, fin=0.012, fout=0.25)
bt = low_shelf(bt, 170, 3.0)
bt = to_lufs(bt, -18.0)
save('M2BurstTail', bt); print('M2BurstTail', round(len(bt) / SR, 2), lufs(bt))

# distant single rounds with their own decay (long-range fire)
for k, on in enumerate([8.358, 17.886]):
    s = cut(far, on, 0.62)
    s = fade(s, fin=0.0015, fout=0.2)
    s = low_shelf(s, 170, 3.0)
    s = s / np.max(np.abs(s)) * 1.1
    s = soft_limit(s, 0.85)
    save(f'M2Far{k + 1}', s); print(f'M2Far{k + 1}', round(len(s) / SR, 2), lufs(s))
