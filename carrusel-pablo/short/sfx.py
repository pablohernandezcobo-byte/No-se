# Efectos de sonido sincronizados (sin música): lee events.json y sintetiza cada tipo de efecto
import json, sys, numpy as np, wave
d = json.load(open(sys.argv[1])); SR = 48000; DUR = d['dur']; N = int(SR * (DUR + 0.5))
mix = np.zeros((N, 2)); rs = np.random.default_rng(11)
def t_(x): return np.arange(int(SR * x)) / SR
def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    if lo: X *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: X *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X, len(x))
def noise(n): return rs.uniform(-1, 1, n)
def sweep_noise(d, f0, f1, shape):
    t = t_(d); n = noise(len(t)); out = np.zeros_like(n); c = 14
    for i in range(c):
        a, b = i * len(t) // c, (i + 1) * len(t) // c; fc = f0 * (f1 / f0) ** (i / c)
        out[a:b] = filt(n, lo=fc * 0.5, hi=fc * 2)[a:b]
    return out * shape(t / d)
S = {
  'whoosh':    lambda: sweep_noise(0.42, 400, 5000, lambda k: np.sin(np.pi * k) ** 2) * 1.2,
  'whoosh_up': lambda: sweep_noise(0.6, 200, 4000, lambda k: k ** 2 * (1 - k ** 8)),
  'impact':    lambda: (lambda t: np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(35 + 110 * np.exp(-t * 18)) / SR) * np.exp(-t * 5) + 0.5 * filt(noise(len(t)), hi=3500) * np.exp(-t * 14)))(t_(0.9)),
  'boom':      lambda: (lambda t: np.tanh(2 * np.sin(2 * np.pi * np.cumsum(28 + 90 * np.exp(-t * 8)) / SR) * np.exp(-t * 2) + 0.6 * filt(noise(len(t)), hi=2500) * np.exp(-t * 6)))(t_(2.2)),
  'shock':     lambda: sweep_noise(0.8, 3000, 300, lambda k: (1 - k) ** 2) * 0.8,
  'thud':      lambda: (lambda t: np.sin(2 * np.pi * np.cumsum(70 + 120 * np.exp(-t * 40)) / SR) * np.exp(-t * 16) + 0.3 * filt(noise(len(t)), lo=1500, hi=6000) * np.exp(-t * 60))(t_(0.3)),
  'pop':       lambda: (lambda t: np.sin(2 * np.pi * np.cumsum(380 + 1400 * t / 0.12) / SR) * np.exp(-t * 28))(t_(0.14)),
  'tick':      lambda: (lambda t: filt(noise(len(t)), lo=2500, hi=9000) * np.exp(-t * 180) + 0.4 * np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120))(t_(0.05)),
  'type':      lambda: (lambda t: filt(noise(len(t)), lo=1800, hi=7000) * np.exp(-t * 250))(t_(0.03)),
  'swipe':     lambda: sweep_noise(0.3, 1500, 9000, lambda k: np.sin(np.pi * k) ** 1.5) * 0.9,
  'shine':     lambda: (lambda t: sum(np.sin(2 * np.pi * f * t) for f in (2093, 2637, 3136)) * np.exp(-t * 4) * np.minimum(t / 0.05, 1) / 3)(t_(0.9)),
  'glitch':    lambda: (lambda t: (np.sign(np.sin(2 * np.pi * 220 * t * (1 + 3 * (np.floor(t * 60) % 3)))) * 0.4 + filt(noise(len(t)), lo=500) * 0.5) * (np.floor(t * 50) % 2) * np.exp(-t * 6))(t_(0.35)),
  'glitch_tr': lambda: (lambda t: (np.sign(np.sin(2 * np.pi * 110 * t * (1 + 4 * (np.floor(t * 40) % 4)))) * 0.5 + filt(noise(len(t)), lo=300) * 0.6) * (np.floor(t * 35) % 2) * np.sin(np.pi * t / 0.45))(t_(0.45)),
  'riser':     lambda: sweep_noise(0.75, 300, 6000, lambda k: k ** 2.5) * 0.7,
  'tap':       lambda: (lambda t: np.sin(2 * np.pi * np.cumsum(900 - 500 * t / 0.08) / SR) * np.exp(-t * 60) + 0.5 * filt(noise(len(t)), lo=3000) * np.exp(-t * 300))(t_(0.12)),
}
GAIN = {'whoosh': .55, 'whoosh_up': .5, 'impact': .7, 'boom': .9, 'shock': .35, 'thud': .45, 'pop': .35, 'tick': .25, 'type': .18,
        'swipe': .35, 'shine': .12, 'glitch': .22, 'glitch_tr': .4, 'riser': .3, 'tap': .45}
pan = 0
for e in d['events']:
    sig = S[e['type']]() * GAIN[e['type']] * e['g']
    i = int(e['t'] * SR)
    if i < 0 or i >= N: continue
    sig = sig[:N - i]; pan = -pan if pan else 0.35
    p = pan if e['type'] in ('whoosh', 'swipe', 'pop', 'tick', 'type') else 0
    mix[i:i + len(sig), 0] += sig * np.sqrt(0.5 * (1 - p)); mix[i:i + len(sig), 1] += sig * np.sqrt(0.5 * (1 + p))
# reverb corta para cohesión
ir_t = t_(0.9); ir = noise(len(ir_t)) * np.exp(-ir_t * 7); ir[0] = 0; L = N + len(ir)
for ch in range(2):
    wet = np.fft.irfft(np.fft.rfft(mix[:, ch], L) * np.fft.rfft(ir, L), L)[:N]
    mix[:, ch] += wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(mix[:, ch])) * 0.12
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.3); mix = mix[:int(SR * DUR)]
mix = mix / np.max(np.abs(mix)) * 0.7      # ~-3 dB de techo: deja sitio para la música
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('sfx ok', round(DUR, 2))
