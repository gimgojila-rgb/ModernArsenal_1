// node render.mjs --frames 0:3600:1 --out frames --workers 3 [--cues cues.json] [--q 0.95]
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const [f0, f1, step] = arg('frames', '0:3600:1').split(':').map(Number);
const OUTDIR = path.resolve(arg('out', 'frames'));
const WORKERS = Number(arg('workers', 3));
const Q = Number(arg('q', 0.95));
const LIST = arg('list', null);        // comma separated frame numbers
fs.mkdirSync(OUTDIR, { recursive: true });

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.json': 'application/json', '.woff2': 'font/woff2' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' }); fs.createReadStream(p).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${server.address().port}/index.html`;

const browser = await chromium.launch({ args: ['--disable-web-security', '--font-render-hinting=none'] });
let frames = [];
if (LIST) frames = LIST.split(',').map(Number); else for (let f = f0; f < f1; f += step) frames.push(f);

async function worker(id, mine) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.error(`[w${id}] pageerror`, e.message));
  page.on('console', m => { if (m.type() === 'error') console.error(`[w${id}]`, m.text()); });
  await page.goto(url);
  await page.evaluate(() => window.boot());
  if (id === 0 && arg('cues', null)) {
    const cues = await page.evaluate(() => window.CUES);
    fs.writeFileSync(arg('cues'), JSON.stringify(cues, null, 1));
  }
  let n = 0; const t0 = Date.now();
  for (const f of mine) {
    const data = await page.evaluate(([f, q]) => { window.renderFrame(f); return window.grab(q); }, [f, Q]);
    fs.writeFileSync(path.join(OUTDIR, `f${String(f).padStart(5, '0')}.jpg`), Buffer.from(data.split(',')[1], 'base64'));
    if (++n % 100 === 0) console.log(`[w${id}] ${n}/${mine.length}  ${((Date.now() - t0) / n).toFixed(0)} ms/frame`);
  }
  await page.close();
}
// contiguous chunks per worker
const per = Math.ceil(frames.length / WORKERS);
await Promise.all(Array.from({ length: WORKERS }, (_, i) => worker(i, frames.slice(i * per, (i + 1) * per))));
await browser.close(); server.close();
console.log('done', frames.length, 'frames');
