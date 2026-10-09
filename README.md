# harryjamescoburn.com

Static website for Harry James Coburn, built from the design canvas.

## How it works

- `source/Website.dc.html`: the home page design, exported from the canvas. Change the design on the canvas, then copy the new file here.
- `site.json`: the settings that are not design (colour scheme, catchline, booking link, prices, Impressum details).
- `tools/build.py`: turns the two into the finished site in `dist/`, and lists anything still missing before go-live.
- `tools/check.mjs`: opens the built site in a browser at desktop and phone width and checks for sideways scrolling, broken links, images, fonts and requests to other sites.

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
3. Optional: forward harrycoburn.com and hcoburn.com (website only) to https://harryjamescoburn.com.

## Before go-live

`python3 tools/build.py` prints the open items. At the time of writing: postal address for the Impressum, booking link, prices (or keep "Price on request") and permission for the second testimonial.
