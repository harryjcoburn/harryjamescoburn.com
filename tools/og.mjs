// Render the social share card: node tools/og.mjs  (writes assets/og-image.jpg)
import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
const here = fileURLToPath(new URL('.', import.meta.url));
const b = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
const p = await (await b.newContext({ viewport: { width: 1200, height: 630 } })).newPage();
await p.goto('file://' + here + 'og.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({ path: here + '../assets/og-image.jpg', type: 'jpeg', quality: 88 });
await b.close();
