# Música para "Mito vs Realidad" — pop/lo-fi luminoso a 100 BPM, con SFX sincronizados.
import numpy as np, wave, sys
SR, DUR = 48000, 34.8
N = int(SR * DUR); mix = np.zeros((N, 2)); rs = np.random.default_rng(3)
def t_(d): return np.arange(int(SR * d)) / SR
def add(sig, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    s = sig[:N - i] * g
    mix[i:i + len(s)] += np.stack([s * np.sqrt(.5 * (1 - pan)), s * np.sqrt(.5 * (1 + pan))], 1)
def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    if lo: X *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: X *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X, len(x))
def kick():
    t = t_(0.3); return np.tanh(1.5 * np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t * 35)) / SR) * np.exp(-t * 10))
def snap():
    t = t_(0.18); return filt(rs.uniform(-1, 1, len(t)), lo=1200, hi=6000) * np.exp(-t * 28)
def hat():
    t = t_(0.04); return filt(rs.uniform(-1, 1, len(t)), lo=8000) * np.exp(-t * 90)
def pluck(f, d=0.35):
    t = t_(d); return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 9) * np.minimum(t / 0.004, 1)
def bell(f):
    t = t_(1.0); return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 5)
def whoosh(d=0.35):
    t = t_(d); return filt(rs.uniform(-1, 1, len(t)), lo=600, hi=5000) * np.sin(np.pi * t / d) ** 2
def stamp():
    t = t_(0.8); b = np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-t * 20)) / SR) * np.exp(-t * 5)
    return np.tanh(1.6 * b + 0.6 * filt(rs.uniform(-1, 1, len(t)), hi=3000) * np.exp(-t * 14))
def thud():
    t = t_(0.35); return np.sin(2 * np.pi * np.cumsum(90 + 80 * np.exp(-t * 30)) / SR) * np.exp(-t * 12)
def click():
    t = t_(0.03); return filt(rs.uniform(-1, 1, len(t)), lo=2000) * np.exp(-t * 200)
def pop():
    t = t_(0.15); return np.sin(2 * np.pi * np.cumsum(400 + 900 * t / 0.15) / SR) * np.exp(-t * 25)

B = 0.6
chords = [[261.6, 329.6, 392.0], [196.0, 246.9, 293.7], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6]]  # C G Am F
roots = [65.4, 49.0, 55.0, 43.65]
nb = int(DUR / B)
for b in range(nb):
    at = b * B; bar = (b // 4) % 4
    intro = at < 3.6
    if not intro or b % 2 == 0: add(kick(), at, 0.75 if not intro else 0.45)
    if b % 2 == 1 and not intro: add(snap(), at, 0.35)
    add(hat(), at + B / 2, 0.15, 0.3)
    for s in range(4):  # arpegio en semicorcheas
        f = chords[bar][(b * 4 + s) % 3] * (2 if s % 2 else 1)
        add(pluck(f), at + s * B / 4, 0.09, pan=-0.4 + 0.8 * (s % 2))
    if not intro:
        tt = t_(B * 0.9); add(filt(sum(np.sin(2 * np.pi * roots[bar] * k * tt) / k for k in range(1, 6)), hi=500) * np.exp(-tt * 3), at, 0.28)
# pad
for c in range(int(DUR / 2.4) + 1):
    tt = t_(2.5); env = np.minimum(tt / 0.4, 1) * np.clip((2.5 - tt) / 0.4, 0, 1)
    add(filt(sum(np.sin(2 * np.pi * f * tt) for f in chords[c % 4]), hi=1500) * env, c * 2.4, 0.04)
# SFX
for at in [3.5, 8.3, 13.7, 19.1, 23.9, 28.7]: add(whoosh(), at - 0.1, 0.35, rs.uniform(-.5, .5))
add(stamp(), 3.8, 0.9)
for k in range(3): add(click(), 6.1 + k * 0.18, 0.4)          # tachones
add(pop(), 6.9, 0.35)                                           # FALSO
add(bell(1046.5), 8.5, 0.18)                                    # REALIDAD ✓
add(thud(), 9.4, 0.5); add(thud(), 11.2, 0.5)                   # balanza
add(bell(784), 16.1, 0.15)                                      # = mismo resultado
for k in range(4): add(pop(), 19.65 + k * 0.32, 0.22)           # tarjetas beneficios
for k in range(4): add(bell(880 + k * 110), 24.5 + k * 0.45, 0.12)  # checks
add(click(), 26.4, 0.5)                                         # cruz
for k in range(6): add(click(), 30.0 + k * 0.15, 0.2)           # escribiendo...
add(pop(), 30.9, 0.5); add(bell(1318.5), 30.95, 0.15)           # "CENA" enviado
fade = np.clip((DUR - np.arange(N) / SR) / 0.6, 0, 1); mix *= fade[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.2); mix = mix / np.max(np.abs(mix)) * 0.93
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
