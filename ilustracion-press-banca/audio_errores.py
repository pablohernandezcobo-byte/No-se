# Phonk de gym · 130 BPM · 808 distorsionado + cencerro + hi-hat rolls + drops sincronizados al reel turbo
import numpy as np, wave, sys
SR = 48000; BPM = 130; B = 60 / BPM
BEATS = [4, 32, 6]   # intro · 4 errores de 8 beats · cierre
STARTS = np.concatenate([[0], np.cumsum(BEATS)]) * B      # inicio de cada escena
DUR = STARTS[-1]; N = int(SR * DUR); rs = np.random.default_rng(7)
drums = np.zeros((N, 2)); bass = np.zeros((N, 2)); mel = np.zeros((N, 2)); fx = np.zeros((N, 2))
def t_(d): return np.arange(int(SR * d)) / SR
def add(bus, sig, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    s = sig[:N - i] * g
    bus[i:i + len(s)] += np.stack([s * np.sqrt(.5 * (1 - pan)), s * np.sqrt(.5 * (1 + pan))], 1)
def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    if lo: X *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: X *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X, len(x))
def kick():
    t = t_(0.35); s = np.sin(2 * np.pi * np.cumsum(48 + 190 * np.exp(-t * 40)) / SR) * np.exp(-t * 8)
    s[:240] += rs.uniform(-1, 1, 240) * np.linspace(1, 0, 240); return np.tanh(2.2 * s)
def snare():
    t = t_(0.3); n = filt(rs.uniform(-1, 1, len(t)), lo=1500, hi=9000) * np.exp(-t * 16)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25); return np.tanh(1.6 * (n + 0.6 * body))
def hat(o=False):
    t = t_(0.18 if o else 0.035); return filt(rs.uniform(-1, 1, len(t)), lo=8500) * np.exp(-t * (18 if o else 110))
def b808(f, d):
    t = t_(d); fr = f * (1 + 1.2 * np.exp(-t * 30))
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.minimum(t / 0.005, 1) * np.clip((d - t) / 0.03, 0, 1)
    return np.tanh(3.5 * s) * 0.8 + 0.5 * np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.clip((d - t) / 0.03, 0, 1)
def cowbell(n, d=0.16):
    t = t_(d); k = 2 ** (n / 12)
    sq = np.sign(np.sin(2 * np.pi * 540 * k * t)) + np.sign(np.sin(2 * np.pi * 800 * k * t))
    return filt(sq, lo=400, hi=4500) * np.exp(-t * 20)
def impact(d=1.6):
    t = t_(d); boom = np.sin(2 * np.pi * np.cumsum(28 + 90 * np.exp(-t * 7)) / SR) * np.exp(-t * 2.5)
    return np.tanh(1.8 * boom + 0.7 * filt(rs.uniform(-1, 1, len(t)), hi=3000) * np.exp(-t * 7))
def riser(d):
    t = t_(d); k = t / d; n = rs.uniform(-1, 1, len(t)); out = np.zeros_like(n)
    for c in range(20):
        a, b = c * len(t) // 20, (c + 1) * len(t) // 20
        out[a:b] = filt(n, lo=400 + 7000 * (c / 20) ** 2)[a:b]
    sw = np.sign(np.sin(2 * np.pi * np.cumsum(150 + 1500 * k ** 2) / SR)) * 0.15
    return (out + sw) * k ** 2
def downlifter(d=0.9):
    t = t_(d); return filt(rs.uniform(-1, 1, len(t)), lo=300, hi=3000) * np.exp(-t * 4) * np.minimum(t / 0.01, 1)
def whoosh(d=0.26):
    t = t_(d); return filt(rs.uniform(-1, 1, len(t)), lo=700, hi=7000) * np.sin(np.pi * t / d) ** 2
def stab(fs, d=0.5):
    t = t_(d); s = sum(np.sign(np.sin(2 * np.pi * f * t)) + np.sign(np.sin(2 * np.pi * f * 1.007 * t)) for f in fs)
    return filt(s, hi=2500) * np.exp(-t * 5)

drop = STARTS[1]; half0 = half1 = -1
roots = [46.25, 36.71, 41.20, 34.65]           # F#1 D1 E1 C#1
mel_pat = [0, None, 0, 3, None, 0, 7, None, 5, None, 3, 0, None, 3, 5, 7]   # cencerro (semicorcheas)
bass_pat = [(0, 0.7), (1.5, 0.35), (2.5, 0.4), (3.0, 0.7)]                  # (beat, duración en beats)

nbeats = int(round(DUR / B))
# --- Intro (antes del drop): cencerro filtrado + hats + build
for b in range(int(round(drop / B))):
    at = b * B
    for s in range(4):
        n = mel_pat[(b * 4 + s) % 16]
        if n is not None: add(mel, filt(cowbell(n), hi=1800), at + s * B / 4, 0.35, -0.2)
    add(drums, hat(), at + B / 2, 0.2)
    if b % 2 == 0: add(drums, kick(), at, 0.5)
add(fx, riser(drop - 0.3), 0.3, 0.45)

# --- Groove principal desde el drop
for b in range(int(round(drop / B)), nbeats):
    at = b * B; bar = (b - int(round(drop / B))) // 4; pos = (b - int(round(drop / B))) % 4
    half = half0 <= at < half1
    last = at >= STARTS[-1] - 2 * B
    if last: continue
    # bombo
    if half: 
        if pos == 0: add(drums, kick(), at, 1.0)
    else:
        if pos in (0, 2): add(drums, kick(), at, 1.0)
        if pos == 3: add(drums, kick(), at + B * 0.5, 0.7)
    # caja
    if (half and pos == 2) or (not half and pos in (1, 3)): add(drums, snare(), at, 0.7)
    # hi-hats con redobles
    for s in range(4 if not half else 2):
        add(drums, hat(), at + s * B / (4 if not half else 2), 0.22 if s % 2 == 0 else 0.13, 0.3)
    if pos == 3 and bar % 2 == 1 and not half:
        for r in range(6): add(drums, hat(), at + B / 2 + r * B / 12, 0.18, -0.3)
    if pos == 1: add(drums, hat(True), at + B / 2, 0.12, -0.3)
    # 808
    for bb, dd in bass_pat:
        if int(bb) == pos: add(bass, b808(roots[bar % 4], dd * B), at + (bb - int(bb)) * B, 0.55 if not half else 0.4)
    # cencerro
    for s in range(4):
        n = mel_pat[(pos * 4 + s) % 16]
        if n is not None: add(mel, cowbell(n + (0 if bar % 4 < 2 else -2)), at + s * B / 4, 0.32 if not half else 0.22, -0.25 + 0.5 * (s % 2))

# --- FX: cada error entra con impacto, zumbido de "incorrecto" y campana de "correcto"
def buzz():
    t = t_(0.28); s = np.sign(np.sin(2 * np.pi * 140 * t)) + np.sign(np.sin(2 * np.pi * 147 * t)); return filt(s, hi=1800) * np.exp(-t * 6)
def bell(f):
    t = t_(0.9); return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 5)
for k in range(4):
    s0 = drop + k * 8 * B
    add(fx, whoosh(), s0 - 0.13, 0.5, (-1) ** k * 0.5); add(fx, impact(), s0, 0.6); add(fx, stab([185, 277.2, 370]), s0, 0.07)
    add(fx, buzz(), s0 + 0.3, 0.22); add(fx, bell(1318.5), s0 + 0.45, 0.14)
    if k == 0:
        for r in range(2): add(fx, impact(0.5), s0 + B + r * 3 * B + 0.9 * B, 0.45)   # rebotes
add(fx, impact(2.2), STARTS[2], 0.8)
end = STARTS[-1] - 2 * B
add(fx, impact(2.2), end, 0.9); add(fx, stab([92.5, 138.6, 185, 277.2], 1.6), end, 0.12); add(bass, b808(46.25, 1.5), end, 0.6)

# --- Mezcla: sidechain del bajo y el cencerro con el bombo
duck = np.ones(N)
for b in range(int(round(drop / B)), nbeats):
    i = int(b * B * SR); L = int(0.18 * SR)
    if i + L < N: duck[i:i + L] = np.minimum(duck[i:i + L], 0.35 + 0.65 * np.linspace(0, 1, L) ** 0.7)
bass *= duck[:, None]; mel *= (0.5 + 0.5 * duck)[:, None]
ir_t = t_(1.2); ir = rs.uniform(-1, 1, len(ir_t)) * np.exp(-ir_t * 5); ir[0] = 0
L = N + len(ir)
for bus, amt in [(mel, 0.18), (drums, 0.06), (fx, 0.15)]:
    for ch in range(2):
        wet = np.fft.irfft(np.fft.rfft(bus[:, ch], L) * np.fft.rfft(ir, L), L)[:N]
        bus[:, ch] += wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(bus[:, ch])) * amt
mix = drums * 1.0 + bass * 1.1 + mel * 0.9 + fx * 0.9
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.8)                  # saturación del bus
fade = np.clip((DUR - np.arange(N) / SR) / 0.5, 0, 1); mix *= fade[:, None]
mix = mix / np.max(np.abs(mix)) * 0.95
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('DUR', DUR)
