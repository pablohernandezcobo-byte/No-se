# Hip-hop cinematográfico de gym · 90 BPM · Re menor · sincronizado con el Short (6 + 5×7 + 7 beats)
import numpy as np, wave, sys
SR = 48000; BPM = 90; B = 60 / BPM
SEGS = [6, 7, 7, 7, 7, 7, 7]; STARTS = np.concatenate([[0], np.cumsum(SEGS)]) * B; DUR = STARTS[-1]
N = int(SR * DUR); rs = np.random.default_rng(5)
drums, bass, music, fx = (np.zeros((N, 2)) for _ in range(4))
def t_(d): return np.arange(int(SR * d)) / SR
def add(bus, sig, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    s = sig[:N - i] * g; bus[i:i + len(s)] += np.stack([s * np.sqrt(.5 * (1 - pan)), s * np.sqrt(.5 * (1 + pan))], 1)
def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    if lo: X *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: X *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X, len(x))
def kick():
    t = t_(0.5); s = np.sin(2 * np.pi * np.cumsum(45 + 140 * np.exp(-t * 28)) / SR) * np.exp(-t * 6)
    s[:300] += rs.uniform(-1, 1, 300) * np.linspace(.8, 0, 300); return np.tanh(2 * s)
def snare():
    t = t_(0.45); n = filt(rs.uniform(-1, 1, len(t)), lo=1200, hi=8000) * np.exp(-t * 11)
    return np.tanh(1.5 * (n + 0.7 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 20)))
def hat(o=False):
    t = t_(0.2 if o else 0.04); return filt(rs.uniform(-1, 1, len(t)), lo=8000) * np.exp(-t * (14 if o else 90))
def saw(f, t, det=0.0):
    return sum(np.sin(2 * np.pi * f * (1 + det) * k * t) / k for k in range(1, 9))
def strings(fs, d):
    t = t_(d); env = np.minimum(t / 0.5, 1) * np.clip((d - t) / 0.4, 0, 1)
    s = sum(saw(f, t) + saw(f, t, 0.004) + saw(f, t, -0.004) for f in fs); return filt(s, hi=1800) * env
def brass(fs, d=0.9):
    t = t_(d); env = np.minimum(t / 0.02, 1) * np.exp(-t * 3)
    s = sum(saw(f, t) + saw(f, t, 0.006) for f in fs); return np.tanh(filt(s, hi=2600) * env * 0.6)
def piano(f, d=1.2):
    t = t_(d); return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 3.2) * np.minimum(t / 0.003, 1)
def sub(f, d):
    t = t_(d); s = np.sin(2 * np.pi * f * t) * np.minimum(t / 0.01, 1) * np.clip((d - t) / 0.05, 0, 1); return np.tanh(1.8 * s)
def impact(d=2.0):
    t = t_(d); return np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(30 + 70 * np.exp(-t * 6)) / SR) * np.exp(-t * 2) + 0.5 * filt(rs.uniform(-1, 1, len(t)), hi=2500) * np.exp(-t * 5))
def riser(d):
    t = t_(d); k = t / d; n = rs.uniform(-1, 1, len(t)); out = np.zeros_like(n)
    for c in range(16):
        a, b = c * len(t) // 16, (c + 1) * len(t) // 16; out[a:b] = filt(n, lo=300 + 6000 * (c / 16) ** 2)[a:b]
    return out * k ** 2
def whoosh(d=0.35):
    t = t_(d); return filt(rs.uniform(-1, 1, len(t)), lo=600, hi=6000) * np.sin(np.pi * t / d) ** 2

# Dm - Bb - Gm - A (progresión épica)
CH = [[293.7, 349.2, 440.0], [233.1, 293.7, 349.2], [196.0, 233.1, 293.7], [220.0, 277.2, 329.6]]
RT = [73.4, 58.3, 49.0, 55.0]
MEL = [587.3, 523.3, 440.0, 523.3, 587.3, 698.5, 659.3, 554.4]
nb = int(round(DUR / B)); intro = SEGS[0]
for b in range(nb):
    at = b * B; bar = (b // 4) % 4; pos = b % 4
    last = b >= nb - 3
    if b < intro:   # intro: cuerdas + piano, golpes graves en 1 y 3
        if pos in (0, 2): add(drums, kick(), at, 0.5)
    elif not last:
        swing = 0.04
        if pos == 0: add(drums, kick(), at, 1.0)
        if pos == 2: add(drums, kick(), at + B * 0.5, 0.8); add(drums, kick(), at + B * 0.75, 0.5)
        if pos in (1, 3): add(drums, snare(), at, 0.8)
        for s in range(2): add(drums, hat(), at + s * B / 2 + (swing if s else 0), 0.25 if s == 0 else 0.15, 0.3)
        if pos == 3: add(drums, hat(True), at + B * 0.5 + swing, 0.12, -0.3)
        add(bass, sub(RT[bar], B * 0.9), at, 0.55)
    if pos == 0 and not last: add(music, strings(CH[bar], 4 * B + 0.4), at, 0.045)
    if not last and b >= 2: add(music, piano(MEL[b % 8], 1.4), at, 0.10, -0.2)
    if not last and b >= intro and pos == 1: add(music, piano(MEL[(b + 3) % 8] / 2, 1.0), at + B * 0.5, 0.07, 0.2)

add(fx, riser(STARTS[1] - 0.2), 0.2, 0.3)
for k in range(1, len(STARTS) - 1):
    a = STARTS[k]
    add(fx, whoosh(), a - 0.17, 0.45, (-1) ** k * 0.5); add(fx, impact(), a, 0.5)
    add(music, brass([146.8, 220.0, 293.7] if k % 2 else [116.5, 174.6, 233.1]), a, 0.10)
end = STARTS[-1] - 3 * B
add(fx, impact(2.5), end, 0.9); add(music, brass([73.4, 146.8, 220.0, 293.7], 2.5), end, 0.14); add(bass, sub(36.7, 2.0), end, 0.6)

duck = np.ones(N)
for b in range(intro, nb):
    i = int(b * B * SR); L = int(0.15 * SR)
    if i + L < N and b % 4 == 0: duck[i:i + L] = np.minimum(duck[i:i + L], 0.5 + 0.5 * np.linspace(0, 1, L))
bass *= duck[:, None]; music *= (0.7 + 0.3 * duck)[:, None]
ir_t = t_(1.8); ir = rs.uniform(-1, 1, len(ir_t)) * np.exp(-ir_t * 3.5); ir[0] = 0; L = N + len(ir)
for bus, amt in [(music, 0.3), (drums, 0.08), (fx, 0.15)]:
    for ch in range(2):
        wet = np.fft.irfft(np.fft.rfft(bus[:, ch], L) * np.fft.rfft(ir, L), L)[:N]
        bus[:, ch] += wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(bus[:, ch])) * amt
mix = drums + bass * 1.1 + music * 1.0 + fx * 0.8
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.5)
fade = np.clip((DUR - np.arange(N) / SR) / 0.6, 0, 1); mix *= fade[:, None]; mix = mix / np.max(np.abs(mix)) * 0.95
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('DUR', DUR)
