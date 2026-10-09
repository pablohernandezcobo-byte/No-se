# Banda sonora sintetizada, 120 BPM, sincronizada con los cortes del reel.
import numpy as np, wave, sys

SR, DUR = 48000, 30.0
N = int(SR * DUR)
mix = np.zeros((N, 2))
rs = np.random.default_rng(1)

def t_(d): return np.arange(int(SR * d)) / SR
def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    s = sig[: N - i] * gain
    if s.ndim == 1:
        l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
        s = np.stack([s * l, s * r], 1)
    mix[i:i + len(s)] += s
def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    if lo: X *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: X *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X, len(x))

def kick(big=False):
    t = t_(0.6 if big else 0.35)
    f = 45 + 120 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (5 if big else 9))
    s[:200] += rs.uniform(-1, 1, 200) * np.linspace(0.6, 0, 200)
    return np.tanh(s * 1.6)
def hat(d=0.05):
    t = t_(d); return fft_filter(rs.uniform(-1, 1, len(t)), lo=7000) * np.exp(-t * 70)
def clap():
    t = t_(0.25); n = fft_filter(rs.uniform(-1, 1, len(t)), lo=900, hi=5000)
    e = np.exp(-t * 18) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 40) * (t > 0.012)
    return n * e
def impact(d=1.8):
    t = t_(d)
    boom = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-t * 8)) / SR) * np.exp(-t * 2.2)
    noise = fft_filter(rs.uniform(-1, 1, len(t)), hi=2500) * np.exp(-t * 6)
    return np.tanh(1.4 * boom + 0.5 * noise)
def riser(d):
    t = t_(d); k = t / d
    n = rs.uniform(-1, 1, len(t)); out = np.zeros_like(n)
    chunks = 24
    for c in range(chunks):  # filtro que se abre por tramos
        a, b = c * len(t) // chunks, (c + 1) * len(t) // chunks
        out[a:b] = fft_filter(n, lo=300 + 6000 * (c / chunks) ** 2, hi=1200 + 12000 * (c / chunks) ** 2)[a:b]
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * k ** 2) / SR) * 0.25
    return (out + sweep) * k ** 2.5
def whoosh(d=0.45):
    t = t_(d); return fft_filter(rs.uniform(-1, 1, len(t)), lo=500, hi=4000) * np.sin(np.pi * t / d) ** 2
def glitch(d=0.5):
    t = t_(d); s = np.sign(np.sin(2 * np.pi * 880 * t)) * 0.3 + rs.uniform(-1, 1, len(t)) * 0.4
    gate = (np.floor(t * 40) % 3 != 0).astype(float); return s * gate * np.exp(-t * 3)

BEAT = 0.5
# --- Intro: drone + latidos ---
t = t_(3.6)
drone = sum(np.sin(2 * np.pi * f * t + p) for f, p in [(55, 0), (55.4, 1), (110.3, 2), (164.8, 0.5)])
drone = fft_filter(drone, hi=900) * np.minimum(t / 1.5, 1) * np.clip((3.6 - t) / 0.3, 0, 1)
add(drone, 0, 0.12)
add(kick(), 0.05, 0.6); add(kick(), 0.5, 0.8)
add(impact(), 1.0, 0.9); add(riser(1.0), 2.5, 0.35)

# --- Groove principal 3.5 → 27.5 ---
roots = [55.0, 43.65, 65.41, 49.0]  # A F C G
for b in range(int((27.5 - 3.5) / BEAT)):
    at = 3.5 + b * BEAT
    fast = at >= 25
    add(kick(), at, 0.9)
    if fast: add(kick(), at + 0.25, 0.55)
    add(hat(), at + 0.25, 0.25, pan=0.3)
    add(hat(0.03), at + 0.125, 0.12, pan=-0.3)
    if b % 2 == 1: add(clap(), at, 0.45)
    # bajo en corcheas con sidechain
    root = roots[int((at - 3.5) // 2) % 4]
    for h in (0.0, 0.25):
        tt = t_(0.24); env = np.minimum(tt / 0.04, 1) * np.exp(-tt * 4)
        saw = sum(np.sin(2 * np.pi * root * k * tt) / k for k in range(1, 7))
        add(fft_filter(saw, hi=600) * env, at + h + 0.02, 0.32 if h else 0.22)

# pad de acordes
chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [261.6, 329.6, 392], [196, 246.9, 293.7]]
for c in range(12):
    at = 3.5 + c * 2
    if at >= 27.5: break
    tt = t_(2.1); env = np.minimum(tt / 0.3, 1) * np.clip((2.1 - tt) / 0.3, 0, 1)
    s = sum(np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt) for f in chords[c % 4])
    add(fft_filter(s, hi=1800) * env, at, 0.035)

# --- Transiciones ---
for at, d in [(8, 1.0), (12.5, 1.0), (17, 1.2), (21, 0.8), (25, 0.8), (27.5, 1.5)]:
    add(riser(d), at - d, 0.4)
for at in [3.5, 8, 12.5, 17, 21, 25, 27.5]:
    add(impact(), at, 0.75 if at != 27.5 else 1.0)
for at in [3.25, 4.6, 5.85, 7.1, 13.3, 14.85, 20.8, 25.4, 25.9, 26.4, 26.9]:
    add(whoosh(), at, 0.3, pan=rs.uniform(-0.6, 0.6))
add(glitch(0.6), 16.75, 0.25); add(glitch(0.3), 24.9, 0.18)
add(kick(True), 12.5, 0.6); add(kick(True), 27.5, 0.8)

# outro: acorde final largo
tt = t_(2.5); env = np.minimum(tt / 0.05, 1) * np.exp(-tt * 1.4)
s = sum(np.sin(2 * np.pi * f * tt) for f in [110, 164.8, 220, 277.2, 329.6])
add(fft_filter(s, hi=2500) * env, 27.5, 0.12)

# reverb sencilla (convolución con cola de ruido)
ir_t = t_(1.6); ir = rs.uniform(-1, 1, len(ir_t)) * np.exp(-ir_t * 4); ir[0] = 0
L = N + len(ir)
for ch in range(2):
    wet = np.fft.irfft(np.fft.rfft(mix[:, ch], L) * np.fft.rfft(ir, L), L)[:N]
    mix[:, ch] += wet / np.max(np.abs(wet)) * np.max(np.abs(mix[:, ch])) * 0.12

fade = np.clip((DUR - np.arange(N) / SR) / 0.4, 0, 1)
mix *= fade[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.3)
mix = mix / np.max(np.abs(mix)) * 0.93
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'out/audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('audio ok')
