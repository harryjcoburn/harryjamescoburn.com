#!/usr/bin/env python3
"""Build harryjamescoburn.com from the canvas design.

Reads source/Website.dc.html (exported from the design canvas) and site.json,
and writes a static site to dist/. Re-run after every canvas change:

    python3 tools/build.py

Prints a checklist of anything still missing before go-live.
"""
import json
import re
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "Website.dc.html"
DIST = ROOT / "dist"
CFG = json.loads((ROOT / "site.json").read_text())

HERO_BLOB = "/_blob/e5ccdea59ff59b2acb793043fbb8b990"
ABOUT_BLOB = "/_blob/5dd1109b79b9cddc19643ec53afc895b"

warnings = []


def between(s, a, b):
    i = s.index(a) + len(a)
    return s[i:s.index(b, i)]


def load_design():
    raw = SRC.read_text()
    helmet = between(raw, "<helmet>", "</helmet>")
    markup = between(raw, "</helmet>", "</x-dc>").strip()
    script = raw[raw.index('data-dc-script'):]
    palettes = json.loads(between(script, "const P = ", ";\nconst c"))
    style = between(helmet, "<style>", "</style>")
    return markup, palettes, style


def apply_palette(markup, c):
    def sub(m):
        key = m.group(1)
        if key not in c:
            sys.exit(f"Unknown palette key: {key}")
        return c[key]
    markup = re.sub(r"\{\{c\.([A-Za-z]+)\}\}", sub, markup)
    markup = markup.replace("{{flairDisplay}}", "block" if CFG["flair"] else "none")
    markup = markup.replace("{{tagline}}", escape(CFG["tagline"]))
    left = re.findall(r"\{\{[^}]+\}\}", markup)
    if left:
        sys.exit(f"Unresolved template holes: {left}")
    return markup


def fix_images(markup):
    markup = markup.replace(
        f'<img src="{HERO_BLOB}"',
        '<img src="assets/hero-harry.webp" width="960" height="1200" fetchpriority="high"')
    markup = markup.replace(
        f'<img src="{ABOUT_BLOB}"',
        '<img src="assets/about-harry.webp" width="960" height="1200" loading="lazy" decoding="async"')
    if "/_blob/" in markup:
        sys.exit("An image still points at a canvas upload; add it to fix_images().")
    return markup


def fix_links(markup):
    booking = CFG["booking_url"].strip()
    if booking:
        markup = markup.replace('href="#book"', f'href="{escape(booking)}" target="_blank" rel="noopener"')
    else:
        warnings.append("No booking link yet: 'Book an intro call' opens an email instead.")
        mail = f'mailto:{CFG["email"]}?subject=Intro%20call'
        markup = markup.replace('href="#book"', f'href="{mail}"')
    markup = markup.replace('href="#imprint"', 'href="impressum.html"')
    markup = markup.replace('href="#privacy"', 'href="privacy.html"')
    return markup


def fix_prices(markup):
    for title, price in CFG["prices"].items():
        i = markup.find(f">{title}</h3>")
        if i < 0:
            sys.exit(f"Offer not found in design: {title}")
        j = markup.find("[PRICE]", i)
        text = escape(price) if price.strip() else "Price on request"
        markup = markup[:j] + text + markup[j + len("[PRICE]"):]
    if "[PRICE]" in markup:
        sys.exit("A [PRICE] placeholder has no matching offer in site.json.")
    if not any(p.strip() for p in CFG["prices"].values()):
        warnings.append("Prices are hidden: each offer shows 'Price on request'.")
    return markup


def drop_unconfirmed_quotes(markup):
    if CFG["show_unconfirmed_quotes"]:
        return markup
    out, n = re.subn(r'<figure[^>]*>(?:(?!</figure>).)*\[PERMISSION TO CONFIRM\](?:(?!</figure>).)*</figure>\s*',
                     "", markup, flags=re.S)
    if n:
        warnings.append(f"{n} testimonial(s) hidden until permission is confirmed.")
    return out


def check_placeholders(markup):
    left = re.findall(r"\[[A-Z][A-Z :'’-]{3,}\]", markup)
    if left:
        sys.exit(f"Placeholders still in the page: {sorted(set(left))}")


FONT_CSS = """
@font-face{font-family:'Newsreader';src:url(assets/fonts/newsreader-latin-opsz-normal.woff2) format('woff2');font-weight:200 800;font-style:normal;font-display:swap}
@font-face{font-family:'Newsreader';src:url(assets/fonts/newsreader-latin-opsz-italic.woff2) format('woff2');font-weight:200 800;font-style:italic;font-display:swap}
@font-face{font-family:'Public Sans';src:url(assets/fonts/public-sans-latin-wght-normal.woff2) format('woff2');font-weight:100 900;font-style:normal;font-display:swap}
@font-face{font-family:'Public Sans';src:url(assets/fonts/public-sans-latin-wght-italic.woff2) format('woff2');font-weight:100 900;font-style:italic;font-display:swap}
@font-face{font-family:'Roboto Mono';src:url(assets/fonts/roboto-mono-latin-400-normal.woff2) format('woff2');font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:'Roboto Mono';src:url(assets/fonts/roboto-mono-latin-500-normal.woff2) format('woff2');font-weight:500;font-style:normal;font-display:swap}
"""

BASE_CSS = """
html{scroll-behavior:smooth}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
*,*::before,*::after{box-sizing:border-box}
img{max-width:100%%;height:auto}
section[id]{scroll-margin-top:16px}
a:focus-visible{outline:3px solid %(sun)s;outline-offset:3px}
.skip{position:absolute;left:-9999px;top:8px;background:#fff;color:%(deep)s;padding:10px 14px;z-index:10}
.skip:focus{left:8px}
footer a{display:inline-block;padding:12px 0}
footer > div{align-items:center !important}
"""

DESCRIPTION = ("Commercial adviser to funded B2B founders. Harry James Coburn turns founder-led, "
               "stalled or messy sales into a revenue engine that runs without the founder.")


def head(title, c, desc=DESCRIPTION, path="", extra=""):
    url = f"https://{CFG['domain']}/{path}"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="{c['green']}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="https://{CFG['domain']}/assets/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/newsreader-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/public-sans-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
{extra}<style>{FONT_CSS}{BASE_CSS % c}</style>
"""


def person_jsonld():
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Harry James Coburn",
        "jobTitle": "Commercial adviser to B2B founders",
        "url": f"https://{CFG['domain']}/",
        "email": f"mailto:{CFG['email']}",
        "image": f"https://{CFG['domain']}/assets/hero-harry.jpg",
        "sameAs": [CFG["linkedin"]],
        "address": {"@type": "PostalAddress", "addressLocality": "Berlin", "addressCountry": "DE"},
    }
    return f'<script type="application/ld+json">{json.dumps(data)}</script>\n'


def build_home(markup, style, c):
    style = style.replace("#1F4D36", c["green"]).replace("#A8431F", c["emberText"])
    page = head("Harry James Coburn: commercial adviser to B2B founders", c,
                extra='<link rel="preload" href="assets/hero-harry.webp" as="image" fetchpriority="high">\n' + person_jsonld())
    page += f"<style>{style}</style>\n</head>\n<body>\n"
    page += '<a class="skip" href="#top">Skip to content</a>\n<main>\n'
    page += markup + "\n</main>\n</body>\n</html>\n"
    return page


def simple_page(title, body_html, c, path):
    return head(f"{title} | Harry James Coburn", c, desc=f"{title} for harryjamescoburn.com", path=path) + f"""<meta name="robots" content="noindex">
<style>
body{{margin:0;background:{c['paper']};color:{c['body']};font-family:'Public Sans','Segoe UI',system-ui,sans-serif;font-size:17px;line-height:1.6}}
a{{color:{c['green']}}}a:hover{{color:{c['emberText']}}}
.wrap{{max-width:760px;margin:0 auto;padding:48px 24px 96px}}
h1{{font-family:'Newsreader',Georgia,serif;font-weight:500;font-size:44px;line-height:1.1;color:{c['deep']};margin:24px 0 24px}}
h2{{font-family:'Newsreader',Georgia,serif;font-weight:600;font-size:24px;color:{c['deep']};margin:36px 0 8px}}
.home{{font-family:'Newsreader',Georgia,serif;font-weight:600;font-size:22px;color:{c['deep']};text-decoration:none}}
</style>
</head>
<body>
<div class="wrap">
<a class="home" href="./">Harry James Coburn</a>
<h1>{title}</h1>
{body_html}
</div>
</body>
</html>
"""


def impressum_html():
    i = CFG["impressum"]
    missing = [k for k in ("street", "city") if not i[k].strip()]
    if missing:
        warnings.append("Impressum is missing your postal address (street, postcode and city). "
                        "German law requires it before the site goes live.")
    addr = "<br>".join(escape(x) for x in [i["name"], i["street"] or "[STREET AND NUMBER]",
                                             i["city"] or "[POSTCODE AND CITY]", i["country"]])
    phone = f"<br>Phone: {escape(i['phone'])}" if i["phone"].strip() else ""
    vat = (f"<h2>VAT ID</h2><p>{escape(i['vat_id'])}</p>" if i["vat_id"].strip() else "")
    return f"""<p>Information under § 5 DDG (Digitale-Dienste-Gesetz).</p>
<h2>Provider</h2>
<p>{addr}</p>
<h2>Contact</h2>
<p>Email: <a href="mailto:{CFG['email']}">{CFG['email']}</a>{phone}</p>
{vat}
<h2>Responsible for content</h2>
<p>{escape(i['name'])}, address as above.</p>
"""


def privacy_html():
    i = CFG["impressum"]
    return f"""<p>Last updated {date.today():%d %B %Y}.</p>
<h2>Who is responsible</h2>
<p>{escape(i['name'])}, contact details in the <a href="impressum.html">Impressum</a>. Email: <a href="mailto:{CFG['email']}">{CFG['email']}</a>.</p>
<h2>No cookies, no tracking</h2>
<p>This website sets no cookies and uses no analytics, advertising or tracking tools. Fonts are served from this website, not from a third party.</p>
<h2>Hosting and server logs</h2>
<p>The site is hosted on GitHub Pages (GitHub, Inc., USA). When you visit, GitHub processes technical data such as your IP address, browser and the time of the request, to deliver the site and keep it secure. The legal basis is our legitimate interest in operating a secure website (Art. 6(1)(f) GDPR). See GitHub's privacy statement for details.</p>
<h2>Booking a call</h2>
<p>The “Book an intro call” button takes you to my booking page on Google Calendar (Google Ireland Ltd). If you book, Google processes the name and email address you enter and adds the meeting to my calendar. I use them only to hold the call and follow up (Art. 6(1)(b) GDPR). Google's privacy policy applies on that page.</p>
<h2>When you email me</h2>
<p>If you contact me by email, I use your details only to reply and to discuss working together (Art. 6(1)(b) and (f) GDPR). I keep them only as long as needed for that, or as the law requires.</p>
<h2>Your rights</h2>
<p>You can ask for access to, correction or deletion of your data, restriction of or objection to its processing, and data portability (Art. 15 to 21 GDPR). You can also complain to a data protection authority, such as the Berlin Commissioner for Data Protection and Freedom of Information.</p>
"""


def write_static(c):
    (DIST / "CNAME").write_text(CFG["domain"] + "\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: https://{CFG['domain']}/sitemap.xml\n")
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'<url><loc>https://{CFG["domain"]}/</loc><lastmod>{date.today()}</lastmod></url>\n</urlset>\n')
    (DIST / "favicon.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="{c["green"]}"/>'
        f'<text x="32" y="44" text-anchor="middle" font-family="Georgia,serif" font-size="34" font-weight="700" fill="#fff">HC</text>'
        f'<rect x="14" y="50" width="36" height="4" rx="2" fill="{c["sun"]}"/></svg>\n')
    (DIST / "404.html").write_text(simple_page(
        "Page not found", '<p>That page doesn\'t exist. <a href="./">Back to the home page</a>.</p>', c, "404.html"))
    (DIST / ".nojekyll").write_text("")


def main():
    markup, palettes, style = load_design()
    if CFG["palette"] not in palettes:
        sys.exit(f"Unknown palette {CFG['palette']!r}; options: {list(palettes)}")
    c = palettes[CFG["palette"]]
    markup = apply_palette(markup, c)
    markup = fix_images(markup)
    markup = fix_links(markup)
    markup = fix_prices(markup)
    markup = drop_unconfirmed_quotes(markup)
    check_placeholders(markup)

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", DIST / "assets", dirs_exist_ok=True)
    (DIST / "index.html").write_text(build_home(markup, style, c))
    (DIST / "impressum.html").write_text(simple_page("Impressum", impressum_html(), c, "impressum.html"))
    (DIST / "privacy.html").write_text(simple_page("Privacy policy", privacy_html(), c, "privacy.html"))
    write_static(c)

    print(f"Built {DIST} with palette {CFG['palette']!r}.")
    if warnings:
        print("\nBefore go-live:")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
