"""Soundtrack for the showreel.
Music: the user's own "Low Altitude Assault" (120 BPM). Video 0-48.06 s = song 0-48.06 s, then the song's final phrase
(168.06 s to the end) so the ending lands on the real outro; the beat grid is continuous across the join (120 s apart).
SFX: synthesized cues from cues.json (written by the renderer from scenes.js) + the mod's own drone pass sounds,
Humvee engine and M2 recordings. Output: 48 kHz stereo WAV."""
import json, subprocess, sys, os
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

FF = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
REPO = '/home/user/ModernArsenal_1'
SR = 48000
DUR = 76.0
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)

def load(path, ch=2):
    raw = subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-i', path, '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).astype(np.float64)

def t(n): return np.arange(int(n * SR)) / SR
def env_exp(n, dec): return np.exp(-t(n) * dec)
def noise(n): return rng.standard_normal(int(n * SR))
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x)
def fade(x, a=0.005, b=0.02):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nb: x[-nb:] *= np.linspace(1, 0, nb)
    return x
def sweep(f0, f1, n, curve='exp'):
    tt = t(n); k = tt / n
    f = f0 * (f1 / f0) ** k if curve == 'exp' else f0 + (f1 - f0) * k
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def norm(x, peak=1.0): m = np.max(np.abs(x)) + 1e-12; return x / m * peak

# ---------------- synthesized sounds (mono unless noted) ----------------
def s_kick(f0=120, f1=42, n=0.7, dec=6):
    tt = t(n); f = f1 + (f0 - f1) * np.exp(-tt * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * dec)
def s_boom():
    body = s_kick(140, 38, 2.6, 2.2) * 1.0
    crack = hp(noise(0.25), 1500) * env_exp(0.25, 22) * 0.5
    rumble = lp(noise(2.6), 180) * env_exp(2.6, 1.6) * 0.9
    x = body; x[:len(crack)] += crack; x += rumble[:len(x)]
    return norm(x)
def s_hit():
    k = s_kick(160, 50, 0.5, 9); n = hp(noise(0.5), 2000) * env_exp(0.5, 35) * 0.45
    return norm(k + n) * 0.9
def s_stamp():
    k = s_kick(200, 70, 0.18, 22); n = bp(noise(0.18), 800, 6000) * env_exp(0.18, 30) * 0.6
    return norm(k + n)
def s_swish(n=0.4):
    x = noise(n); out = np.zeros_like(x); seg = 256
    for i in range(0, len(x), seg):
        k = i / len(x); fc = 400 + 3500 * np.sin(np.pi * k)
        out[i:i + seg] = bp(x[max(0, i - 2048):i + seg], fc * 0.7, min(fc * 1.4, 20000))[-len(x[i:i + seg]):]
    return fade(out * np.sin(np.pi * t(n) / n) ** 2, 0.001, 0.02)
def s_whoosh(n=0.7): return norm(s_swish(n) + lp(noise(n), 300) * np.sin(np.pi * t(n) / n) ** 3 * 0.6)
def s_riser(n):
    tt = t(n); k = tt / n
    x = hp(noise(n), 500) * k ** 2.5 * 0.5 + sweep(180, 1800, n) * k ** 2 * 0.35 + sweep(90, 900, n) * k ** 2 * 0.25
    return fade(x, 0.01, 0.004)
def s_beep(f=1760, n=0.06): return fade(np.sin(2 * np.pi * f * t(n)) * 0.6, 0.002, 0.01)
def s_chirp():
    x = np.zeros(int(0.16 * SR))
    for i, f in enumerate([2400, 3100, 2800]):
        b = np.sign(np.sin(2 * np.pi * f * t(0.03))) * 0.25; o = int(i * 0.045 * SR); x[o:o + len(b)] += fade(b, 0.001, 0.005)
    return lp(x, 7000)
def s_tick():
    x = s_kick(300, 120, 0.12, 30) * 0.8; c = hp(noise(0.03), 3000) * env_exp(0.03, 150); x[:len(c)] += c
    return norm(x)
def s_lock():
    tt = t(0.6); f = np.where((tt * 12).astype(int) % 2 == 0, 1250, 1650)
    return fade(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5, 0.003, 0.05)
def s_ping():
    x = np.sin(2 * np.pi * 1320 * t(1.2)) * env_exp(1.2, 4.5) * 0.6 + np.sin(2 * np.pi * 2640 * t(1.2)) * env_exp(1.2, 9) * 0.2
    y = x.copy(); d = int(0.18 * SR); y[d:] += x[:-d] * 0.35; y[2 * d:] += x[:-2 * d] * 0.15
    return y
def s_shot():
    return norm(s_kick(180, 60, 0.18, 20) + bp(noise(0.18), 400, 5000) * env_exp(0.18, 26) * 0.9)
def s_gun30():
    x = np.zeros(int(1.2 * SR))
    for i in range(7):
        s = s_shot() * (0.9 + 0.1 * rng.random()); o = int(i * 0.096 * SR); x[o:o + len(s)] += s
    return norm(x) * 0.9
def s_flares():
    x = np.zeros(int(1.4 * SR))
    for i in range(10):
        p = bp(noise(0.08), 1200, 7000) * env_exp(0.08, 50); o = int(i * 0.07 * SR); x[o:o + len(p)] += p * 0.8
    x += hp(noise(1.4), 3000) * env_exp(1.4, 2.5) * 0.15
    return norm(x) * 0.8
def s_eject2():
    k = s_kick(110, 50, 0.35, 12); c = np.zeros_like(k); cl = bp(noise(0.06), 1500, 6000) * env_exp(0.06, 70); c[int(0.02 * SR):int(0.02 * SR) + len(cl)] += cl
    return norm(k + c * 0.7)
def s_missile(n=2.0):
    tt = t(n); a = np.minimum(1, tt / 0.04) * np.exp(-tt * 1.2)
    roar = lp(noise(n), 900) * 1.0 + bp(noise(n), 900, 5000) * 0.35
    return norm(roar * a)
def s_static(n=0.6):
    tt = t(n); return hp(noise(n), 1500) * (tt / n) ** 2 * 0.6 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 31 * tt)))
def s_explode():
    b = s_boom(); d = np.zeros(int(3.0 * SR))
    for i in range(24):
        p = bp(noise(0.03), 1500, 8000) * env_exp(0.03, 80) * rng.uniform(0.1, 0.35); o = int(rng.uniform(0.1, 1.6) * SR); d[o:o + len(p)] += p
    x = np.zeros(max(len(b), len(d))); x[:len(b)] += b; x[:len(d)] += d
    return norm(x)
def s_laser(): tt = t(0.5); return fade(np.sin(2 * np.pi * (2800 + 60 * np.sin(2 * np.pi * 30 * tt)) * tt) * 0.2 * np.exp(-tt * 3), 0.01, 0.1)
def s_clank(i):
    base = [620, 740, 820, 980][i % 4]; n = 0.45; tt = t(n)
    x = sum(np.sin(2 * np.pi * base * r * tt) * np.exp(-tt * d) * g for r, d, g in [(1, 14, 0.6), (1.71, 18, 0.45), (2.93, 26, 0.3), (4.1, 40, 0.2)])
    x += bp(noise(n), 2000, 9000) * env_exp(n, 90) * 0.5 + s_kick(160, 70, n, 25) * 0.6
    return norm(x)
def s_crank():
    x = np.zeros(int(0.55 * SR))
    for i in range(4):
        tt = t(0.13); c = np.sin(2 * np.pi * (180 + 80 * tt / 0.13) * tt) * np.sin(np.pi * tt / 0.13) * 0.5 + lp(noise(0.13), 400) * 0.3
        o = int(i * 0.125 * SR); x[o:o + len(c)] += c
    return x
def s_rocket():
    n = 0.35; tt = t(n); a = np.minimum(1, tt / 0.01) * np.exp(-tt * 7)
    return norm(bp(noise(n), 600, 6000) * a + lp(noise(n), 400) * a * 0.6)
def s_pop():
    k = s_kick(130, 45, 0.5, 8); n = bp(noise(0.5), 300, 4000) * env_exp(0.5, 14) * 0.8
    return norm(k + n)
def s_alarm():
    tt = t(0.24); f = np.where(tt < 0.12, 880, 660)
    return fade(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.18, 0.003, 0.02)
def s_shimmer():
    x = np.zeros(int(2.0 * SR))
    for i in range(18):
        f = rng.uniform(3000, 9000); o = int(rng.uniform(0, 1.0) * SR); n = 0.9
        s = np.sin(2 * np.pi * f * t(n)) * env_exp(n, 5) * 0.08; x[o:o + len(s)] += s
    return x
def s_rotor(n=2.6):
    tt = t(n); chop = (0.5 + 0.5 * np.cos(2 * np.pi * 19.5 * tt)) ** 6
    x = lp(noise(n), 500) * (0.25 + 0.9 * chop) + np.sin(2 * np.pi * 39 * tt) * chop * 0.4
    return x * np.sin(np.pi * tt / n) ** 1.5

# ---------------- the mod's recordings ----------------
def mono(path): return load(path, 1)[:, 0]
eagle_pass = mono(f'{REPO}/guardian_audio/GrayEaglePass.ogg')
shadow_pass = mono(f'{REPO}/guardian_audio/ShadowPass.ogg')
engine = mono(f'{REPO}/humvee_sounds/preview_engine.mp3')
m2 = mono(f'{REPO}/humvee_sounds/preview_m2.mp3')
PEAK = {'passEagle': 1.3, 'passShadow': 1.0}

def sound(k, i, cues, idx):
    if k == 'boot': return norm(sweep(60, 2400, 0.35) * np.linspace(1, 0, int(0.35 * SR)) * 0.5 + hp(noise(0.35), 3000) * env_exp(0.35, 20) * 0.3)
    if k == 'chirp': return s_chirp()
    if k == 'hit': return s_hit()
    if k == 'swish': return s_swish()
    if k == 'whoosh': return s_whoosh()
    if k == 'riser':
        nxt = [c['t'] for c in cues[idx + 1:] if c['k'] in ('boom', 'explode') and c['t'] > cues[idx]['t'] + 0.2]
        return s_riser(min(1.6, (nxt[0] if nxt else cues[idx]['t'] + 1) - cues[idx]['t']))
    if k == 'boom': return s_boom()
    if k == 'beep': return s_beep()
    if k == 'tick': return s_tick()
    if k == 'lock': return s_lock()
    if k == 'stamp': return s_stamp()
    if k == 'rotor': return s_rotor()
    if k == 'ping': return s_ping()
    if k == 'gun30': return s_gun30()
    if k == 'flares': return s_flares()
    if k == 'eject': return s_eject2()
    if k == 'missile': return s_missile()
    if k == 'static': return s_static()
    if k == 'explode': return s_explode()
    if k == 'passEagle': return norm(eagle_pass)
    if k == 'passShadow': return norm(shadow_pass)
    if k == 'laser': return s_laser()
    if k == 'clank': return s_clank(i)
    if k == 'crank': return s_crank()
    if k == 'engine': return fade(norm(engine[int(0.0 * SR):int(1.6 * SR)]), 0.005, 0.4)
    if k == 'm2': return fade(norm(m2[int(0.22 * SR):int(1.35 * SR)]), 0.002, 0.08)
    if k == 'drive': return fade(norm(engine[int(14.2 * SR):int(15.4 * SR)]), 0.02, 0.3)
    if k == 'alarm': return s_alarm()
    if k == 'rocket': return s_rocket()
    if k == 'pop': return s_pop()
    if k == 'shimmer': return s_shimmer()
    raise KeyError(k)

# per-cue stereo pan (-1 left .. 1 right)
PAN = {'rocket': 0.2, 'passEagle': 'sweepRL', 'passShadow': 'sweepRL', 'whoosh': 'sweepRL', 'gun30': -0.3, 'm2': -0.35, 'flares': 0.3, 'missile': -0.1, 'rotor': 0.25, 'ping': -0.1}
GAIN = {'boom': 0.9, 'explode': 0.95, 'hit': 0.6, 'stamp': 0.5, 'beep': 0.35, 'chirp': 0.3, 'tick': 0.5, 'lock': 0.35, 'riser': 0.55, 'swish': 0.5,
        'whoosh': 0.6, 'rotor': 0.5, 'ping': 0.45, 'gun30': 0.6, 'flares': 0.4, 'eject': 0.6, 'missile': 0.6, 'static': 0.35, 'passEagle': 0.8,
        'passShadow': 0.8, 'laser': 0.3, 'clank': 0.42, 'crank': 0.45, 'engine': 0.6, 'm2': 0.6, 'drive': 0.55, 'alarm': 0.35, 'rocket': 0.5, 'pop': 0.55, 'shimmer': 0.5, 'boot': 0.5}

def main():
    cues = json.load(open(os.path.join(HERE, 'cues.json')))
    cues.sort(key=lambda c: c['t'])
    N = int(DUR * SR)
    # ---- music edit
    song = load(f'{REPO}/guardian_audio/Low_Altitude_Assault.mp3', 2)
    J1, J2 = 64.06, 168.06
    a = song[:int(J1 * SR)]
    b = song[int(J2 * SR):]
    xf = int(0.012 * SR)
    ramp = np.linspace(0, 1, xf)[:, None]
    music = np.zeros((N, 2))
    na = len(a) - xf
    music[:na] = a[:na]
    music[na:na + xf] = a[na:] * (1 - ramp) + b[:xf] * ramp
    rest = b[xf:][:N - na - xf]
    music[na + xf:na + xf + len(rest)] = rest
    # ---- sfx bus
    sfx = np.zeros((N + SR * 4, 2))
    counts = {}
    for idx, c in enumerate(cues):
        k = c['k']; i = counts.get(k, 0); counts[k] = i + 1
        x = sound(k, i, cues, idx) * GAIN[k] * c.get('g', 1)
        start = c['t'] - PEAK.get(k, 0)
        o = int(round(start * SR))
        if o < 0: x = x[-o:]; o = 0
        pan = PAN.get(k, 0.0)
        if pan == 'sweepRL':
            p = np.linspace(0.8, -0.8, len(x))
        else:
            p = np.full(len(x), pan)
        gl, gr = np.sqrt((1 - p) / 2), np.sqrt((1 + p) / 2)
        sfx[o:o + len(x), 0] += x * gl * 1.41; sfx[o:o + len(x), 1] += x * gr * 1.41
    sfx = sfx[:N]
    # room: short synthetic IR, 18% wet
    irn = int(1.1 * SR); ir = rng.standard_normal((irn, 2)) * np.exp(-np.arange(irn) / SR * 5.5)[:, None]
    ir = np.stack([lp(ir[:, 0], 6000), lp(ir[:, 1], 6000)], 1); ir /= np.sqrt(np.sum(ir ** 2, 0))
    wet = np.stack([fftconvolve(sfx[:, ch], ir[:, ch])[:N] for ch in range(2)], 1)
    sfx = sfx + wet * 0.18
    # duck the score a little under the big hits
    duck = np.ones(N)
    for c in cues:
        if c['k'] in ('boom', 'explode'):
            o = int(c['t'] * SR); L = int(1.2 * SR); d = 1 - 0.35 * np.exp(-np.arange(L) / SR * 4)
            duck[o:o + L] = np.minimum(duck[o:o + L], d[:max(0, min(L, N - o))])
    mix = music * 0.82 * duck[:, None] + sfx * 0.5
    # tail: fade the last 0.6 s to silence
    fl = int(0.6 * SR); mix[-fl:] *= np.linspace(1, 0, fl)[:, None]
    # master: soft clip then peak -1 dBFS
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = mix / np.max(np.abs(mix)) * 10 ** (-1 / 20)
    out = os.path.join(HERE, 'mix.wav')
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_s16le', out],
                   input=mix.astype(np.float32).tobytes(), check=True)
    print('wrote', out, 'cues', len(cues), {k: v for k, v in sorted(counts.items())})

if __name__ == '__main__':
    main()
