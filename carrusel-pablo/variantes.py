# Variantes de color del personaje: cambia el tono de la camiseta y del resplandor (píxeles azules saturados)
import numpy as np, sys
from PIL import Image, ImageDraw
src = Image.open('assets/personaje.png').convert('RGB')
a = np.asarray(src).astype(np.float32) / 255
r, g, b = a[..., 0], a[..., 1], a[..., 2]
mx, mn = a.max(-1), a.min(-1); d = mx - mn + 1e-6
h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
s = np.where(mx > 0, d / (mx + 1e-6), 0); v = mx
# máscara suave: tonos azules (195°–260°) con saturación
hm = np.clip(1 - np.maximum(0, np.abs(h - 228) - 30) / 12, 0, 1)
sm = np.clip((s - 0.18) / 0.15, 0, 1)
m = hm * sm
def hsv2rgb(h, s, v):
    c = v * s; x = c * (1 - np.abs((h / 60) % 2 - 1)); z = v - c; hh = (h // 60) % 6
    rr = np.select([hh == 0, hh == 1, hh == 2, hh == 3, hh == 4, hh == 5], [c, x, 0 * c, 0 * c, x, c])
    gg = np.select([hh == 0, hh == 1, hh == 2, hh == 3, hh == 4, hh == 5], [x, c, c, x, 0 * c, 0 * c])
    bb = np.select([hh == 0, hh == 1, hh == 2, hh == 3, hh == 4, hh == 5], [0 * c, 0 * c, x, c, c, x])
    return np.stack([rr + z, gg + z, bb + z], -1)
VARS = {  # nombre: (tono, factor saturación, factor brillo)
    'rojo': (358, 1.0, 0.95), 'naranja': (24, 1.0, 1.05), 'verde': (150, 0.95, 0.9),
    'morado': (275, 0.9, 0.95), 'negro': (225, 0.15, 0.32), 'dorado': (44, 0.85, 1.05),
}
for name, (th, sf, vf) in VARS.items():
    nh = th + (h - 228) * 0.3
    rgb = hsv2rgb(nh % 360, np.clip(s * sf, 0, 1), np.clip(v * vf, 0, 1))
    outp = a * (1 - m[..., None]) + rgb * m[..., None]
    Image.fromarray((np.clip(outp, 0, 1) * 255).astype(np.uint8)).save(f'variantes/personaje_{name}.png')
src.save('variantes/personaje_azul.png')
# foto de perfil circular (1080x1080) y primer plano
face = src.crop((236, 470, 886, 1120)).resize((1080, 1080), Image.LANCZOS)
face.save('variantes/primer_plano.png')
mask = Image.new('L', (1080, 1080), 0); ImageDraw.Draw(mask).ellipse((0, 0, 1079, 1079), fill=255)
pp = Image.new('RGBA', (1080, 1080)); pp.paste(face, (0, 0), mask); pp.save('variantes/foto_perfil_circular.png')
print('ok')
