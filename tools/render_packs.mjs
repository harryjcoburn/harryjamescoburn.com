// Render tools/_print/packs/*.html to assets/downloads/packs/*.pdf (multi-page, A4) with page numbers.
import { chromium } from 'playwright';
import { readdirSync, mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
const here = fileURLToPath(new URL('.', import.meta.url));
mkdirSync(here + '../assets/downloads/packs', { recursive: true });
const b = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
for (const f of readdirSync(here + '_print/packs').filter(f => f.endsWith('.html'))) {
  const p = await b.newPage();
  await p.goto('file://' + here + '_print/packs/' + f); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
  await p.pdf({ path: here + '../assets/downloads/packs/' + f.replace('.html', '.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:7px;font-family:monospace;color:#5B6660;padding:0 16mm;display:flex;justify-content:space-between"><span>Harry James Coburn · harryjamescoburn.com</span><span class="pageNumber"></span></div>' });
  console.log('rendered', f);
  await p.close();
}
await b.close();
