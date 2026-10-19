// Browser check for the built site: run `node tools/check.mjs` with dist/ served on :8765.
import { chromium } from 'playwright';

const BASE = process.env.BASE || 'http://localhost:8765/';
const OUT = process.env.OUT || '/tmp';
const pages = ['', 'services.html', 'scorecard.html', 'work.html', 'engine.html', 'ideas.html', 'about.html', 'faq.html', 'speaking.html', 'impressum.html', 'privacy.html', '404.html'];
const viewports = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'phone', width: 390, height: 844 },
];

const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
let problems = 0;
const fail = (msg) => { problems++; console.log('FAIL', msg); };

for (const vp of viewports) {
  const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
  for (const p of pages) {
    const page = await ctx.newPage();
    const external = new Set();
    const broken = [];
    const errors = [];
    await page.route('https://cloud.umami.is/**', (r) => r.fulfill({ status: 200, contentType: 'application/javascript', body: '' }));
    await page.route('https://cloud.umami.is/**', (r) => r.fulfill({ status: 200, contentType: 'application/javascript', body: '' }));
    page.on('request', (r) => { const h = new URL(r.url()).host; if (!r.url().startsWith(BASE) && h !== 'cloud.umami.is' && !h.endsWith('substack.com')) external.add(h); });
    page.on('response', (r) => { if (r.status() >= 400 && !r.url().includes('nope-404')) broken.push(`${r.status()} ${r.url()}`); });
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('pageerror', (e) => errors.push(String(e)));
    await page.goto(BASE + p, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const label = `${vp.name} /${p}`;

    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    if (overflow > 0) fail(`${label}: page scrolls sideways by ${overflow}px`);
    if (external.size) fail(`${label}: requests to other hosts: ${[...external].join(', ')}`);
    if (broken.length) fail(`${label}: broken requests: ${broken.join('; ')}`);
    if (errors.length) fail(`${label}: console errors: ${errors.join('; ')}`);

    const imgs = await page.evaluate(() => [...document.images].map((i) => ({ src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0, alt: i.alt })));
    for (const i of imgs) {
      if (!i.alt) fail(`${label}: image without alt ${i.src}`);
    }
    if (!['impressum.html','privacy.html','404.html'].includes(p)) {
      // Lazy images: scroll through so they load, then check.
      await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); } });
      await page.waitForTimeout(400);
      const notLoaded = await page.evaluate(() => [...document.images].filter((i) => !(i.complete && i.naturalWidth > 0)).map((i) => i.src));
      if (notLoaded.length) fail(`${label}: images not loaded: ${notLoaded.join(', ')}`);
      const anchors = await page.evaluate(() => [...document.querySelectorAll('a[href^="#"]')].map((a) => a.getAttribute('href')).filter((h) => h.length > 1 && !document.querySelector(h)));
      if (anchors.length) fail(`${label}: links to missing sections: ${anchors.join(', ')}`);
      const fonts = await page.evaluate(() => [...document.fonts].filter((f) => f.status === 'loaded').map((f) => `${f.family} ${f.style}`));
      if (!fonts.some((f) => f.includes('Schibsted'))) fail(`${label}: Schibsted Grotesk did not load`);
      const small = await page.evaluate(() => [...document.querySelectorAll('a')].filter((a) => { const r = a.getBoundingClientRect(); return r.height > 0 && r.height < 24 && getComputedStyle(a).display !== 'inline'; }).map((a) => a.textContent.trim()).slice(0, 5));
      if (small.length) console.log(`note ${label}: small link targets: ${small.join(' | ')}`);
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({ path: `${OUT}/${(p || "home").replace(".html", "")}-${vp.name}.png`, fullPage: true });
      console.log(`ok ${label}: fonts ${[...new Set(fonts)].join(', ')}`);
    } else {
      await page.screenshot({ path: `${OUT}/${(p || 'home').replace('.html', '')}-${vp.name}.png`, fullPage: true });
      console.log(`ok ${label}`);
    }
    await page.close();
  }
  await ctx.close();
}
await browser.close();
console.log(problems ? `${problems} problem(s)` : 'All checks passed');
process.exit(problems ? 1 : 0);
