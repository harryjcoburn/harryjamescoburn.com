# harryjamescoburn.com

Static website for Harry James Coburn, built from the design canvas.

## How it works

- `source/index.html`, `source/work.html`, `source/about.html`: the pages, written by hand. `{{...}}` marks parts the build fills in (head, nav, closing band, footer, booking link, prices).
- `source/site.css`: the shared stylesheet (direction D "Ember": Schibsted Grotesk, Roboto Mono labels, Newsreader italic for Harry's own voice).
- `assets/photos/`: hero, about and avatar crops from Drive `Headshots_2025-09/Frame and edited`. Add `adventure-marathon.jpg`, `adventure-kayak.jpg` or `adventure-snow.jpg` (800x600) and the build shows a "beyond work" strip.
- `site.json`: booking link, prices, Impressum details.
- `tools/build.py`: builds `dist/`, adds Person, ProfessionalService and FAQPage structured data, and lists anything still open (including `<!-- CHECK: ... -->` wording markers).
- `tools/check.mjs`: opens every page at desktop and phone width and checks sideways scrolling, broken links and images, fonts and requests to other sites.
- `source/legacy/Website.dc.html`: the old canvas design, kept for reference only.

```
python3 tools/build.py
(cd dist && python3 -m http.server 8765) &
node tools/check.mjs        # add CHROME=/path/to/chrome if Playwright has no browser
```

## Privacy by design

No cookies, no analytics, no third-party requests. Fonts are self-hosted (Google Fonts embeds are a known GDPR issue in Germany). The privacy page says exactly this; update it if anything is added (analytics, a booking widget, a form).

## Going live on GitHub Pages

1. Push `dist/` to the `gh-pages` branch (or the repo root) of a public GitHub repo, and turn on Pages with the custom domain `harryjamescoburn.com` and "Enforce HTTPS".
2. In iwantmyname DNS for harryjamescoburn.com:
   - Remove the four Squarespace A records, the `www` CNAME to `ext-cust.squarespace.com` and the Squarespace verification CNAME.
   - Add A records for `@`: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153.
   - Add AAAA records for `@`: 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153.
   - Add a CNAME for `www` pointing to `<github-username>.github.io`.
   - Leave every MX and TXT record alone (email, SPF, DKIM, Google verification).
3. Done (10 Oct 2026): harrycoburn.com, hcoburn.com and their www versions forward to https://harryjamescoburn.com (iwantmyname URL Forward, 301, path not kept). hcoburn.com keeps its Google Workspace MX, SPF, DKIM and DMARC (p=none) records.

## Before go-live

`python3 tools/build.py` prints the open items. At the time of writing: postal address for the Impressum, booking link, prices (or keep "Price on request") and permission for the second testimonial.
