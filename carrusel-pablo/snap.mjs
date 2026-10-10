// Captura un SVG/HTML local a PNG: node snap.mjs entrada salida ancho alto
import { createRequire } from 'module'; import path from 'path';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const [inp, outp, w = 1000, h = 1100] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h } });
await p.goto('file://' + path.resolve(inp)); await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: outp, omitBackground: true }); await b.close();
