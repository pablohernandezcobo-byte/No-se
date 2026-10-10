// Exporta window.EVENTS y DUR de una página de animación a JSON
import { createRequire } from 'module'; import path from 'path'; import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const b = await chromium.launch(); const p = await b.newPage();
await p.goto('file://' + path.resolve(process.argv[2])); await p.evaluate(() => window.ready);
fs.writeFileSync(process.argv[3], JSON.stringify(await p.evaluate(() => ({ dur: window.DUR, events: window.EVENTS }))));
await b.close();
