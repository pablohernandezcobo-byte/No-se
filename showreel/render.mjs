// Uso:
//   node render.mjs stills 1.5 5 9.8 ...      -> PNG/JPG de control en ./stills
//   node render.mjs video [fps] [workers]     -> ./out/video_noaudio.mp4
import { createRequire } from 'module';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW_PATH || '/opt/node22/lib/node_modules/playwright');
const DIR = path.dirname(fileURLToPath(import.meta.url));
const URL = 'file://' + path.join(DIR, 'index.html');
const [mode = 'video', ...args] = process.argv.slice(2);

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(URL);
  await page.evaluate(() => window.ready);
  return page;
}
const toBuf = d => Buffer.from(d.slice(d.indexOf(',') + 1), 'base64');

const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-device-scale-factor=1'] });

if (mode === 'stills') {
  fs.mkdirSync(path.join(DIR, 'stills'), { recursive: true });
  const page = await openPage(browser);
  for (const t of args.map(Number)) {
    const d = await page.evaluate(t => window.frame(t, 0.9), t);
    fs.writeFileSync(path.join(DIR, 'stills', `t_${t.toFixed(2)}.jpg`), toBuf(d));
  }
} else {
  const fps = Number(args[0] || 60), workers = Number(args[1] || 3), DUR = 30;
  const total = Math.round(DUR * fps), per = Math.ceil(total / workers);
  fs.mkdirSync(path.join(DIR, 'out'), { recursive: true });
  const t0 = Date.now();
  const parts = await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const from = w * per, to = Math.min(total, from + per);
    const file = path.join(DIR, 'out', `part${w}.mp4`);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', String(fps), file], { stdio: ['pipe', 'inherit', 'inherit'] });
    const page = await openPage(browser);
    for (let f = from; f < to; f++) {
      const d = await page.evaluate(t => window.frame(t, 0.95), f / fps);
      if (!ff.stdin.write(toBuf(d))) await new Promise(r => ff.stdin.once('drain', r));
      if (w === 0 && f % 60 === 0) console.log(`worker0 ${f - from}/${to - from}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    return file;
  }));
  fs.writeFileSync(path.join(DIR, 'out', 'list.txt'), parts.map(p => `file '${p}'`).join('\n'));
  await new Promise(r => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(DIR, 'out', 'list.txt'), '-c', 'copy', path.join(DIR, 'out', 'video_noaudio.mp4')], { stdio: 'inherit' }).on('close', r));
  console.log('done in', ((Date.now() - t0) / 1000).toFixed(0), 's');
}
await browser.close();
