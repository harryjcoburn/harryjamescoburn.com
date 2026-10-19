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

No cookies and no cross-site tracking. Fonts are self-hosted (Google Fonts embeds are a known GDPR issue in Germany). The only third parties are Umami Cloud (cookieless page and click statistics, added 19 Oct 2026), Cal.com behind the "Book a call" links and the Substack newsletter sign-up. The privacy page describes each one; update it whenever anything is added or removed.

This repo is public. CVs, cover letters and job applications live in the private `job-engine` repo, and `cv/` is ignored here so they can't be committed by accident.

## Deploying

The site is live at https://harryjamescoburn.com, served by GitHub Pages from the `gh-pages` branch, which holds the contents of `dist/`. To publish a change: run `python3 tools/build.py`, commit to `main`, then push the new `dist/` to `gh-pages`.

## How the domain was set up (done)

1. GitHub Pages is on, with the custom domain `harryjamescoburn.com` and "Enforce HTTPS".
2. In iwantmyname DNS for harryjamescoburn.com:
   - Remove the four Squarespace A records, the `www` CNAME to `ext-cust.squarespace.com` and the Squarespace verification CNAME.
   - Add A records for `@`: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153.
   - Add AAAA records for `@`: 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153.
   - Add a CNAME for `www` pointing to `<github-username>.github.io`.
   - Leave every MX and TXT record alone (email, SPF, DKIM, Google verification).
3. Done (10 Oct 2026): harrycoburn.com, hcoburn.com and their www versions forward to https://harryjamescoburn.com (iwantmyname URL Forward, 301, path not kept). hcoburn.com keeps its Google Workspace MX, SPF, DKIM and DMARC (p=none) records.

## Open items

`python3 tools/build.py` prints anything still open, including `<!-- CHECK: ... -->` wording markers. As of 19 Oct 2026 it reports none.
