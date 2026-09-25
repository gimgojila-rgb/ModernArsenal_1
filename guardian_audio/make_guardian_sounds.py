"""Guardian drone sounds from the two CC0 recordings the user fetched.

  eagle.wav  = clif_creates "Propeller Plane" (freesound 251971, CC0): a propeller plane passing overhead near LAX, 30.4 s
  shadow_src = Sheyvan "Drone Flying" (freesound 470127, CC0): a steady motor drone at ~207 Hz with harmonics, very quiet,
               heavy hiss above 6 kHz

Outputs (44.1 kHz mono OGG, loudness-matched to the Humvee loops):
  GrayEaglePass.ogg   one-shot flyby: only the loud stretch of the recording (13.4-16.3 s; outside it the plane is 15-25 dB
                      down in room tone), closest point ~1.2 s in, -14 LUFS
  GrayEagleLoop.ogg   engine loop built from the one steady second at the closest point (14.0-15.0 s, prop tone 143.6 Hz):
                      grains cut on whole periods, overlap-added round a circular buffer, so the loop has no seam, -15 LUFS
  ShadowLoop.ogg      cleaned motor drone (hiss cut, light saturation for a buzzier engine grit), seam on whole periods, -15 LUFS
  ShadowPass.ogg      a doppler pass built from ShadowLoop (pitch +/- ~1.5 semitones, 1/r level, air absorption), peak at 1.0 s, -14 LUFS
  guardian_drones_preview.mp3   everything in a row, with gaps, for listening

Run: python3 make_guardian_sounds.py <eagle.wav> <shadow.wav> <out_dir>
"""
import os, subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy import signal

SR = 44100

def load(p):
    x, sr = sf.read(p)
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = signal.resample_poly(x, SR, sr)
    return x.astype(np.float64)

def butter(x, kind, f, order=4):
    sos = signal.butter(order, f, kind, fs=SR, output='sos')
    return signal.sosfiltfilt(sos, x)

def lufs(x, target):
    m = pyln.Meter(SR, block_size=0.2)
    y = pyln.normalize.loudness(x, m.integrated_loudness(x), target)
    pk = np.abs(y).max()
    if pk > 0.89: y = np.tanh(y / 0.89) * 0.89          # soft ceiling at about -1 dBFS
    return y

def fade(x, fin, fout):
    y = x.copy()
    if fin: n = int(fin * SR); y[:n] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))
    if fout: n = int(fout * SR); y[-n:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, n))
    return y

def f0(x, lo, hi):
    N = 1 << 16
    sp = np.abs(np.fft.rfft(x[:N] * np.hanning(min(N, len(x))), N))
    f = np.fft.rfftfreq(N, 1 / SR); m = (f > lo) & (f < hi)
    i = np.flatnonzero(m)[sp[m].argmax()]
    a, b, c = np.log(sp[i - 1:i + 2] + 1e-12)
    return f[i] + 0.5 * (a - c) / (a - 2 * b + c) * (f[1] - f[0])

def flatten(x, win=0.35, lim_db=6):
    env = np.sqrt(signal.sosfiltfilt(signal.butter(2, 1 / win, 'low', fs=SR, output='sos'), x ** 2).clip(1e-12))
    g = np.median(env) / env
    g = np.clip(g, 10 ** (-lim_db / 20), 10 ** (lim_db / 20))
    return x * g

def loop(x, period_hz, length, xf):
    """a seamless loop: length rounded to whole periods, the tail crossfaded (equal power) into the head"""
    n = int(round(round(length * period_hz) * SR / period_hz))
    k = int(xf * SR)
    assert len(x) >= n + k
    y = x[:n].copy()
    t = np.linspace(0, np.pi / 2, k)
    y[:k] = x[:k] * np.sin(t) + x[n:n + k] * np.cos(t)
    return y

def granular_loop(src, period_hz, length, grain):
    """a seamless loop from a short steady recording: Hann grains taken at random whole-period offsets, each levelled,
    overlap-added at 50 % round a circular buffer that is itself a whole number of periods long"""
    rng = np.random.default_rng(3)
    P = SR / period_hz
    n = int(round(round(length * period_hz) * P))
    g = int(round(round(grain * period_hz) * P))
    hop = g // 2
    w = np.hanning(g)
    out = np.zeros(n)
    max_k = int((len(src) - g) // P)
    ref = np.sqrt((src ** 2).mean())
    for start in range(0, n, hop):
        k = rng.integers(0, max_k + 1)
        # keep the grain in phase with the loop's own period grid: offset in whole periods relative to where it lands
        off = int(round(k * P + ((start % P) - (start % P))))
        gr = src[off:off + g]
        gr = gr * (ref / (np.sqrt((gr ** 2).mean()) + 1e-9))
        idx = (start + np.arange(g)) % n
        np.add.at(out, idx, gr * w)
    return out

def write_ogg(x, path):
    tmp = path + '.wav'
    sf.write(tmp, x.astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-c:a', 'libvorbis', '-q:a', '6', path], check=True)
    os.remove(tmp)

def main(eagle_p, shadow_p, out):
    os.makedirs(out, exist_ok=True)
    e = butter(load(eagle_p), 'highpass', 30, 2)
    s = load(shadow_p)

    # --- Gray Eagle ---
    pass_e = fade(e[int(13.4 * SR):int(16.3 * SR)], 0.25, 0.9)          # closest point ~1.2 s in (the cutscene starts it ~70 ticks early)
    pass_e = lufs(pass_e, -14)
    core = e[int(14.0 * SR):int(15.0 * SR)]
    fe = f0(core, 130, 160)
    loop_e = lufs(granular_loop(core, fe, 3.0, 0.30), -15)

    # --- Shadow: cut the hiss, give it some engine grit, loop on whole periods ---
    body = s[int(2.0 * SR):int(20.0 * SR)]
    body = butter(butter(body, 'highpass', 70, 2), 'lowpass', 5200, 6)
    body = body / np.abs(body).max()
    body = np.tanh(body * 2.2) / np.tanh(2.2)                      # harmonics: a buzzier, more combustion-like drone
    body = butter(body, 'lowpass', 7500, 4)
    body = flatten(body, 0.5, 4)
    fs_ = f0(body, 180, 240)
    loop_s = lufs(loop(body, fs_, 4.0, 0.4), -15)

    # --- Shadow pass: doppler from the loop ---
    T, tc, half = 2.6, 1.0, 0.22                                   # length, closest point, how tight the pass is
    t = np.arange(int(T * SR)) / SR
    u = (t - tc) / half
    r = np.sqrt(1 + u ** 2)
    beta = 0.085                                                   # v/c: about +/- 1.4 semitones
    ratio = 1 / (1 - beta * (-u / r))
    src = np.tile(loop_s, int(np.ceil(T * 1.2 * SR / len(loop_s))) + 1)
    pos = np.cumsum(ratio)
    y = np.interp(pos, np.arange(len(src)), src)
    near = 1 / r
    dull = butter(y, 'lowpass', 1800, 2)
    y = (y * near ** 1.5 + dull * (1 - near ** 1.5)) * near
    pass_s = lufs(fade(y, 0.15, 0.6), -14)

    for name, x in (('GrayEaglePass', pass_e), ('GrayEagleLoop', loop_e), ('ShadowLoop', loop_s), ('ShadowPass', pass_s)):
        write_ogg(x, os.path.join(out, name + '.ogg'))
        print(name, round(len(x) / SR, 3), 's')
    print('f0 eagle %.2f Hz, shadow %.2f Hz' % (fe, fs_))

    gap = np.zeros(int(0.7 * SR))
    prev = np.concatenate([pass_e, gap, np.tile(loop_e, 2), gap, np.tile(loop_s, 2), gap, pass_s, gap, pass_s * 0.8])
    tmp = os.path.join(out, 'prev.wav'); sf.write(tmp, prev.astype(np.float32), SR)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp, '-b:a', '160k', os.path.join(out, 'guardian_drones_preview.mp3')], check=True)
    os.remove(tmp)

if __name__ == '__main__':
    main(*sys.argv[1:4])
