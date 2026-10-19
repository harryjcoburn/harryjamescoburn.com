// Render tools/_print/*.html to assets/downloads/*.pdf and report anything that overflows one A4 page.
import { chromium } from 'playwright';
import { readdirSync } from 'fs';
import { fileURLToPath } from 'url';
const here = fileURLToPath(new URL('.', import.meta.url));
const b = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
for (const f of readdirSync(here + '_print').filter(f => f.endsWith('.html'))) {
  const p = await (await b.newContext({ viewport: { width: 794, height: 1123 } })).newPage();
  await p.goto('file://' + here + '_print/' + f); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
  const over = await p.evaluate(() => { const pg = document.querySelector('.page'), f = pg.querySelector('.foot'); return Math.round(f.getBoundingClientRect().bottom - pg.getBoundingClientRect().bottom + 30) });
  const imgs = await p.evaluate(() => [...document.images].filter(i => !i.naturalWidth).map(i => i.src));
  await p.pdf({ path: here + '../assets/downloads/' + f.replace('.html', '.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  await p.screenshot({ path: here + '_print/' + f.replace('.html', '.png') });
  console.log(f, over > 0 ? `OVERFLOW ${over}px` : 'fits', imgs.length ? 'missing images ' + imgs : '');
  await p.close();
}
await b.close();
