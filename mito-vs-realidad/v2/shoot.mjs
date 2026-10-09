// Exporta cada <section class="slide"> de carrusel.html como PNG 1080x1350
import { createRequire } from 'module'; import path from 'path'; import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const dir = path.resolve('carrusel'); fs.mkdirSync(dir, { recursive: true });
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
await p.goto('file://' + path.resolve('carrusel.html')); await p.evaluate(() => document.fonts.ready);
const els = await p.$$('section.slide');
for (let i = 0; i < els.length; i++) await els[i].screenshot({ path: path.join(dir, `Mito01_slide_${i + 1}.png`) });
await b.close(); console.log(els.length, 'slides');
