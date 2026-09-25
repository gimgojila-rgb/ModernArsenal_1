import numpy as np, subprocess, json, re
from scipy.io import wavfile
from scipy.signal import butter, sosfiltfilt, resample_poly

SR = 44100

def load(n, sr=48000):
    s, x = wavfile.read(f'{n}.wav'); assert s == sr
    return x.astype(np.float64)

def to44(x):  # 48k -> 44.1k
    return resample_poly(x, 147, 160)

def hp(x, f, sr=SR, o=2):
    return sosfiltfilt(butter(o, f, 'hp', fs=sr, output='sos'), x)

def lp(x, f, sr=SR, o=2):
    return sosfiltfilt(butter(o, f, 'lp', fs=sr, output='sos'), x)

def low_shelf(x, f, gain_db, sr=SR):
    """simple shelf: add a low-passed copy"""
    g = 10 ** (gain_db / 20) - 1
    return x + g * lp(x, f, sr, 2)

def fade(x, fin=0.0, fout=0.0, sr=SR):
    y = x.copy()
    if fin > 0:
        n = int(fin * sr); y[:n] *= np.sin(np.linspace(0, np.pi / 2, n)) ** 2
    if fout > 0:
        n = int(fout * sr); y[-n:] *= np.cos(np.linspace(0, np.pi / 2, n)) ** 2
    return y

def env(x, w, sr=SR):
    n = max(1, int(w * sr))
    return np.sqrt(np.convolve(x ** 2, np.ones(n) / n, 'same') + 1e-12)

def soft_limit(x, ceiling=0.89):
    """gentle tanh knee above 70% of ceiling; keeps peaks under the ceiling"""
    k = 0.7 * ceiling
    y = x.copy()
    over = np.abs(y) > k
    y[over] = np.sign(y[over]) * (k + (ceiling - k) * np.tanh((np.abs(y[over]) - k) / (ceiling - k)))
    return y

def lufs(x, sr=SR):
    wavfile.write('/tmp/_m.wav', sr, x.astype(np.float32))
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', '/tmp/_m.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])
    tp = re.findall(r'Peak:\s+(-?[\d.inf]+) dBFS', r)
    return I, (float(tp[-1]) if tp else None)

def to_lufs(x, target, ceiling=0.89, sr=SR):
    """gain to a loudness target, soft-limit peaks, re-trim"""
    for _ in range(3):
        I, _ = lufs(x, sr)
        x = x * 10 ** ((target - I) / 20)
        x = soft_limit(x, ceiling)
    return x

def make_loop(y, L, X, corr=0.0):
    """y has at least L+X samples; returns a loop of length L whose end flows into its start.
    correlated seams get an equal-gain fade (no +3 dB bump), noisy ones an equal-power fade"""
    z = y[X:L + X].copy()
    u = np.linspace(0, 1, X)
    if corr > 0.5:
        fi = 0.5 - 0.5 * np.cos(np.pi * u); fo = 1 - fi
    else:
        fi = np.sin(u * np.pi / 2); fo = np.cos(u * np.pi / 2)
    z[-X:] = y[L:L + X] * fo + y[0:X] * fi
    return z

def varispeed(x, rate, sr=SR):
    """play x with a per-output-sample rate curve (cubic interpolation); rate array sets output length"""
    pos = np.concatenate([[0.0], np.cumsum(rate[:-1])])
    pos = np.clip(pos, 1, len(x) - 3)
    i = np.floor(pos).astype(int); f = pos - i
    xm1, x0, x1, x2 = x[i - 1], x[i], x[i + 1], x[i + 2]
    return x0 + 0.5 * f * (x1 - xm1 + f * (2 * xm1 - 5 * x0 + 4 * x1 - x2 + f * (3 * (x0 - x1) + x2 - xm1)))

def smooth(t, t0, t1, v0, v1):
    u = np.clip((t - t0) / (t1 - t0), 0, 1); u = u * u * (3 - 2 * u)
    return v0 + (v1 - v0) * u

def best_loop_len(y, L0, X, search):
    """pick L near L0 whose y[L:L+X] best matches y[0:X] (phase-aligned seam)"""
    a = y[0:X]; best, bl = -2, L0
    for L in range(L0 - search, L0 + search):
        b = y[L:L + X]
        c = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12)
        if c > best: best, bl = c, L
    return bl, best

def seam_report(z, sr=SR):
    """jump at the wrap vs typical sample-to-sample step"""
    d = np.abs(np.diff(z)); wrap = abs(z[0] - z[-1])
    return wrap, np.percentile(d, 99)

def save(name, x, sr=SR):
    wavfile.write(f'out/{name}.wav', sr, x.astype(np.float32))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'out/{name}.wav', '-c:a', 'libvorbis', '-q:a', '6', f'out/{name}.ogg'], check=True)
