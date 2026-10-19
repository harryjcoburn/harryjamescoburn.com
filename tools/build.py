#!/usr/bin/env python3
"""Build harryjamescoburn.com.

Pages are hand-written HTML in source/ (index, work, about) with a shared stylesheet,
source/site.css. This script fills in the shared parts (head, nav, closing band, footer),
the booking link and prices from site.json, adds structured data for search and AI
assistants, and writes the finished site to dist/.

    python3 tools/build.py

Prints a checklist of anything still open before go-live.
"""
import json
import re
import shutil
import sys
from datetime import date
from html import escape, unescape
from pathlib import Path

from brand import mark as brand_mark

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
DIST = ROOT / "dist"
CFG = json.loads((ROOT / "site.json").read_text())
BASE = f"https://{CFG['domain']}/"
THEME = "#10372A"

UNUSED_ASSETS = ("tsb.svg", "british-army.svg", "wheely.svg", "adventure-peak.jpg", "adventure-hike.jpg", "SOURCES.md", "*.txt")

PAGES = {
    "index.html": ("Harry James Coburn: an AI sales engine you can trust",
                   "Harry James Coburn helps CEOs of VC-backed companies build AI into their sales engine without "
                   "losing trust: the right customer, price and pitch, AI trained and tested to their standard, "
                   "then scaled. Berlin and London, working across the UK, Europe and the US."),
    "work.html": ("Case studies: UXCam, Arbonics, Wheely and Pronto | Harry James Coburn",
                  "How Harry James Coburn rebuilt and scaled sales at UXCam, Arbonics, Wheely and Pronto: "
                  "before, what he did, and the results."),
    "services.html": ("Services: how I can help | Harry James Coburn",
                      "One problem, solved well: a sales engine that still runs through the founder, or stalls after the "
                      "raise. Teardown, Diagnostic, Build, fractional Head of Sales and advisory for VC-backed CEOs."),
    "scorecard.html": ("Sales engine scorecard | Harry James Coburn",
                       "A free 3-minute scorecard across eight of the 28 focus areas of the Coburn Commercial Engine, "
                       "with your three first moves."),
    "ideas.html": ("Ideas: find the formula, then scale it | Harry James Coburn",
                   "Harry James Coburn on commercial strategy, his selling principles and the state of AI in "
                   "go-to-market."),
    "engine.html": ("The Coburn Commercial Engine: revenue is momentum | Harry James Coburn",
                    "The Coburn Commercial Engine: how Harry James Coburn diagnoses, fixes and scales how a company "
                    "wins customers and keeps them. Five levers, seven layers, one standard."),
    "faq.html": ("FAQ: go-to-market, sales and AI | Harry James Coburn",
                 "Answers on how Harry James Coburn works, who he works with, what a GTM Teardown and Diagnostic are, "
                 "what it costs and how AI is changing B2B sales."),
    "speaking.html": ("Speaking, podcasts and portfolio workshops | Harry James Coburn",
                      "Invite Harry James Coburn to speak, join a podcast or run a portfolio workshop on commercial "
                      "strategy and go-to-market in the age of AI agents."),
    "about.html": ("About Harry James Coburn",
                   "Harry James Coburn: from IBM, Credit Suisse and Lloyds Banking Group to building sales "
                   "engines at start-ups. Based in Berlin."),
}

OFFERS = ["GTM Teardown", "GTM Diagnostic", "Commercial Systems Build", "Fractional Head of Sales", "Advisor"]

warnings = []


def booking():
    b = CFG["booking_url"].strip()
    if not b:
        warnings.append("No booking link yet: buttons open an email instead.")
        return f"mailto:{CFG['email']}?subject=Intro%20call"
    return b


def nav(current):
    def link(href, label):
        cur = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    home = "" if current == "index.html" else "./"
    return (f'<nav class="nav" aria-label="Main"><a class="name" href="./">{MARK}<span>Harry James Coburn</span></a>'
            f'<span class="links">{link("services.html", "Services")}{link("work.html", "Work")}{link("engine.html", "The Engine")}'
            f'{link("ideas.html", "Ideas")}{link("about.html", "About")}'
            f'<a class="btn" href="{{{{BOOK}}}}">Book a call</a></span></nav>')


CLOSE = """<section class="close" aria-labelledby="h-close"><div class="wrap inner">
  <div class="mono">Think clearly. Move fast.</div>
  <h2 id="h-close">Tell me where your sales are <em>stuck.</em></h2>
  <p>A short intro call. You leave with at least one thing to fix this month, whether we work together or not.</p>
  <div class="cta"><a class="btn" href="{{BOOK}}">Book an intro call <span class="arr">→</span></a><span class="mail">{{EMAIL}}</span></div>
  <div class="alt"><a href="mailto:{{EMAIL}}?subject=Hello%20Harry">Or send a message</a><a href="speaking.html">Invite me to speak or on a podcast</a></div>
</div></section>"""

NEWSLETTER = """<section class="sec news" id="newsletter" aria-labelledby="h-news">
  <div class="news-copy">
    <div class="label mono">Newsletter · Free</div>
    <h2 id="h-news">The AI Go-to-Market <em>Formula.</em></h2>
    <p>One lever or one AI workflow per issue, what I'd change this month, and what happened when real companies did it. Short, practical, no hype.</p>
  </div>
  <div class="news-box"><iframe src="https://harryjamescoburn.substack.com/embed" title="Subscribe to The AI Go-to-Market Formula" width="480" height="200" loading="lazy" frameborder="0" scrolling="no"></iframe><a class="small-note" href="https://harryjamescoburn.substack.com" target="_blank" rel="noopener">Read it on Substack</a></div>
</section>"""

FOOTER = """<footer><div class="wrap">
  <span class="sign">{mark}<span>© {year} Harry James Coburn · Berlin · London</span></span>
  <nav aria-label="Footer"><a href="./#offers">Offers</a><a href="faq.html">FAQ</a><a href="speaking.html">Speaking</a><a href="https://harryjamescoburn.substack.com" target="_blank" rel="noopener">Newsletter</a><a href="{linkedin}" target="_blank" rel="noopener">LinkedIn</a><a href="mailto:{email}">Email</a><a href="impressum.html">Impressum</a><a href="privacy.html">Privacy</a></nav>
</div></footer>"""


def head(title, desc, path, extra=""):
    url = BASE + ("" if path == "index.html" else path)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="{THEME}">
<link rel="icon" href="favicon.ico?v=2" sizes="48x48">
<link rel="icon" href="favicon.svg?v=2" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png?v=2">
<script defer src="https://cloud.umami.is/script.js" data-website-id="e4b96f89-c3cd-4f41-be42-e9db07deec39" data-domains="harryjamescoburn.com"></script>
<script>document.addEventListener('DOMContentLoaded',function(){{document.querySelectorAll('a[href*="cal.com"]').forEach(function(a){{a.setAttribute('data-umami-event','Book a call')}});document.querySelectorAll('a[href^="mailto:"]').forEach(function(a){{if(!a.hasAttribute('data-umami-event'))a.setAttribute('data-umami-event','Email')}});document.querySelectorAll('a[href$="scorecard.html"]').forEach(function(a){{a.setAttribute('data-umami-event','Open scorecard')}});}});</script>
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{BASE}assets/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/schibsted-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/site.css">
{extra}</head>"""


def clean(t):
    return unescape(re.sub(r"<[^>]+>", "", re.sub(r"<!--.*?-->", "", t, flags=re.S))).strip()


def faq_ld(html):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in faq_entries(html)]}


def faq_entries(html):
    items = re.findall(r'<details class="faq-item"[^>]*>\s*<summary>(.*?)</summary>\s*<div class="faq-a">(.*?)</div>\s*</details>',
                       html, flags=re.S)
    if not items or len(items) != html.count('class="faq-item"'):
        sys.exit("FAQ items could not all be read for the structured data; check their markup.")
    return [(clean(q), clean(a)) for q, a in items]


def jsonld(html):
    person = {
        "@type": "Person", "@id": BASE + "#person", "name": "Harry James Coburn",
        "jobTitle": "Commercial strategy and go-to-market adviser",
        "description": ("Berlin-based commercial strategy and go-to-market adviser for growing tech companies. "
                        "Has led sales at UXCam, Arbonics, Wheely and Pronto, and trained at IBM, Credit Suisse "
                        "and Lloyds Banking Group."),
        "url": BASE, "email": f"mailto:{CFG['email']}", "image": BASE + "assets/photos/hero.jpg",
        "sameAs": [CFG["linkedin"]], "nationality": "British",
        "homeLocation": {"@type": "Place", "name": "Berlin, Germany"},
        "address": {"@type": "PostalAddress", "addressLocality": "Berlin", "addressCountry": "DE"},
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": "University of Manchester"},
                     {"@type": "CollegeOrUniversity", "name": "University of Melbourne"}],
        "worksFor": {"@id": BASE + "#service"},
        "knowsAbout": ["Go-to-market strategy", "Commercial strategy", "B2B sales", "Sales leadership",
                       "Fractional Head of Sales", "Pricing strategy", "Ideal customer profile (ICP)",
                       "Outbound sales", "Inbound lead conversion", "AI agents in sales", "Sales forecasting",
                       "CRM", "New market and product launches"],
    }
    service = {
        "@type": "ProfessionalService", "@id": BASE + "#service", "name": "Harry James Coburn",
        "description": PAGES["index.html"][1], "url": BASE, "email": CFG["email"],
        "image": BASE + "assets/og-image.jpg", "founder": {"@id": BASE + "#person"},
        "address": {"@type": "PostalAddress", "addressLocality": "Berlin", "addressCountry": "DE"},
        "areaServed": [{"@type": "Country", "name": "United Kingdom"}, {"@type": "Place", "name": "Europe"},
                       {"@type": "Country", "name": "United States"}],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Ways to work together",
                            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": o}}
                                                for o in OFFERS]},
    }
    faq = {"@type": "FAQPage", "@id": BASE + "#faq",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                          for q, a in faq_entries(html)]}
    data = {"@context": "https://schema.org", "@graph": [person, service]}
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>\n'


# The HJC mark, inline so it takes the text colour; the station dot is coloured in CSS.
MARK = ('<svg class="mark" viewBox="0 0 70 32" width="42" height="19" aria-hidden="true" focusable="false">'
        + brand_mark("currentColor", "none").replace('fill="none"/>', 'class="stn"/>') + "</svg>")


def adventure():
    """Small 'beyond work' photo strip, only if the photos are in assets/photos/."""
    shots = [("adventure-marathon", "Midnight marathon, Arctic Circle, 2022"),
             ("adventure-hac", "Army Reserve: HAC gun salute, London"), ("adventure-kayak", "Kayaking, Antarctica, 2014")]
    have = [(n, c) for n, c in shots if (ROOT / "assets" / "photos" / f"{n}.jpg").exists()]
    if not have:
        return ""
    figs = "".join(f'<figure><img src="assets/photos/{n}.jpg" width="800" height="600" alt="{escape(c)}" loading="lazy">'
                   f'<figcaption>{escape(c)}</figcaption></figure>' for n, c in have)
    return f'<div class="strip">{figs}</div>'


def prices(html):
    def sub(m):
        p = CFG["prices"].get(m.group(1))
        if p is None:
            sys.exit(f"No price entry in site.json for {m.group(1)!r}")
        return escape(p) if p.strip() else "Price on request"
    return re.sub(r"\{\{PRICE:([^}]+)\}\}", sub, html)


def fill(name, html):
    title, desc = PAGES[name]
    extra = ""
    if name == "index.html":
        extra = '<link rel="preload" href="assets/photos/hero.webp" as="image" fetchpriority="high">\n' + jsonld(html)
    if name == "faq.html":
        extra = f'<script type="application/ld+json">{json.dumps(faq_ld(html), ensure_ascii=False)}</script>\n'
    html = html.replace("{{HEAD}}", head(title, desc, name, extra))
    html = html.replace("{{NAV}}", nav(name)).replace("{{CLOSE}}", CLOSE)
    html = html.replace("{{FOOTER}}", FOOTER.format(mark=MARK, year=date.today().year, linkedin=escape(CFG["linkedin"]),
                                                    email=CFG["email"]))
    html = html.replace("{{NEWSLETTER}}", NEWSLETTER).replace("{{ADVENTURE}}", adventure())
    html = prices(html)
    book = booking()
    attrs = f'{escape(book)}" target="_blank" rel="noopener' if book.startswith("http") else escape(book)
    html = html.replace('href="{{BOOK}}"', f'href="{attrs}"').replace("{{EMAIL}}", CFG["email"])
    left = re.findall(r"\{\{[^}]+\}\}", html)
    if left:
        sys.exit(f"{name}: unfilled template holes {sorted(set(left))}")
    checks = re.findall(r"<!-- CHECK: ([^>]+?) -->", html)
    if checks:
        warnings.append(f"{name}: wording still to confirm: {', '.join(checks)}")
    return html


def simple_page(title, body_html, path):
    book = booking()
    page = head(f"{title} | Harry James Coburn", f"{title} for harryjamescoburn.com", path,
                '<meta name="robots" content="noindex">\n')
    return page + f"""
<body>
<header class="wrap">{nav(path).replace('{{BOOK}}', escape(book))}</header>
<main class="wrap"><div class="page-head"><h1>{title}</h1></div><div class="prose" style="padding-bottom:96px">{body_html}</div></main>
</body>
</html>
"""


def impressum_html():
    i = CFG["impressum"]
    if not (i["street"].strip() and i["city"].strip()):
        warnings.append("Impressum is missing the postal address. German law requires it before go-live.")
    addr = "<br>".join(escape(x) for x in [i["name"], i["street"], i["city"], i["country"]] if x)
    phone = f"<br>Phone: {escape(i['phone'])}" if i["phone"].strip() else ""
    vat = f"<h2>VAT ID</h2><p>{escape(i['vat_id'])}</p>" if i["vat_id"].strip() else ""
    return f"""<p>Information under § 5 DDG (Digitale-Dienste-Gesetz).</p>
<h2>Provider</h2><p>{addr}</p>
<h2>Contact</h2><p>Email: <a href="mailto:{CFG['email']}">{CFG['email']}</a>{phone}</p>
{vat}<h2>Responsible for content</h2><p>{escape(i['name'])}, address as above.</p>"""


def privacy_html():
    i = CFG["impressum"]
    return f"""<p>Last updated {date.today():%d %B %Y}.</p>
<h2>Who is responsible</h2>
<p>{escape(i['name'])}, contact details in the <a href="impressum.html">Impressum</a>. Email: <a href="mailto:{CFG['email']}">{CFG['email']}</a>.</p>
<h2>No cookies, privacy-friendly statistics</h2>
<p>This website sets no cookies and uses no advertising or cross-site tracking. Fonts are served from this website, not from a third party.</p>
<p>To see which pages are read and which links are clicked, I use Umami Cloud (Umami Software, Inc.), a cookieless analytics service. It records the page, the referring site, browser and device type, country and clicks on buttons such as "Book a call", without cookies and without storing your IP address or building a profile of you. The answers you give in the scorecard are not sent. The legal basis is my legitimate interest in understanding how the site is used (Art. 6(1)(f) GDPR). Umami's privacy policy applies.</p>
<h2>Hosting and server logs</h2>
<p>The site is hosted on GitHub Pages (GitHub, Inc., USA). When you visit, GitHub processes technical data such as your IP address, browser and the time of the request, to deliver the site and keep it secure. The legal basis is our legitimate interest in operating a secure website (Art. 6(1)(f) GDPR). See GitHub's privacy statement for details.</p>
<h2>Booking a call</h2>
<p>The “Book a call” buttons take you to my booking page on Cal.com (Cal.com, Inc.). If you book, Cal.com processes the name, email address and answers you enter, adds the meeting to my Google Calendar (Google Ireland Ltd) and creates a Google Meet link. I use them only to hold the call and follow up (Art. 6(1)(b) GDPR). Cal.com's and Google's privacy policies apply to that processing.</p>
<p>The newsletter sign-up box is provided by Substack, Inc. It loads from Substack only on pages that show it. If you subscribe, Substack processes your email address to send you the newsletter, based on your consent (Art. 6(1)(a) GDPR). You can unsubscribe from any issue. Substack's privacy policy applies.</p>
<h2>When you email me</h2>
<p>If you contact me by email, I use your details only to reply and to discuss working together (Art. 6(1)(b) and (f) GDPR). I keep them only as long as needed for that, or as the law requires.</p>
<h2>Your rights</h2>
<p>You can ask for access to, correction or deletion of your data, restriction of or objection to its processing, and data portability (Art. 15 to 21 GDPR). You can also complain to a data protection authority, such as the Berlin Commissioner for Data Protection and Freedom of Information.</p>"""


LLMS = """# Harry James Coburn

> Berlin-based commercial strategy and go-to-market (GTM) adviser for growing, VC-backed tech companies across the UK, Europe and the US. Finds the commercial formula (customer, price, pitch, process), builds the sales engine, then uses AI to scale it.

## Track record
- UXCam (AI product analytics, Headline-backed), Head of Sales, 2026: inbound leads becoming sales-qualified from ~25% to ~40%, first reply from about a day to 5 minutes with AI agents.
- Arbonics (forest carbon, Plural-backed), Head of Sales & New Markets, 2024-25: quarterly sales up 37x in nine months, from about EUR 0.1M to EUR 5.4M in estimated contract value; about EUR 10M won in 12 months; sales cycle from 75 to 16 days.
- Wheely (premium chauffeurs, Concentric-backed), Global Head of B2B Sales & Customer Success, 2019-21: B2B recovered 912% from the Covid low.
- Pronto (food delivery, Playfair and Seedcamp-backed), Head of B2B Sales & Partnerships, 2015-16: B2B built from zero to 60% of company revenue.
- Earlier: IBM, Credit Suisse, Lloyds Banking Group (helped create TSB Bank).

## Services
- GTM Teardown: 90-minute session on site, pricing, pitch and funnel; at least three fixes or no fee.
- GTM Diagnostic: 2-3 week review of the whole sales engine; fee credited against a Build within 30 days.
- Commercial Systems Build: 8-12 weeks; ICP, messaging, pricing, AI-assisted inbound and outbound, CRM, forecasting, hiring.
- Fractional Head of Sales and Advisor roles.
- Speaking, podcasts and portfolio workshops.

## Pages
- [Home]({base})
- [Case studies]({base}work.html)
- [Services]({base}services.html)
- [Sales engine scorecard]({base}scorecard.html)
- [The Coburn Commercial Engine]({base}engine.html)
- [Ideas and the state of AI in GTM]({base}ideas.html)
- [About]({base}about.html)
- [Speaking and podcasts]({base}speaking.html)
- [FAQ]({base}faq.html)

## Contact
- Email: {email}
- LinkedIn: {linkedin}
- Newsletter: The AI Go-to-Market Formula, https://harryjamescoburn.substack.com
"""


def write_static():
    (DIST / "CNAME").write_text(CFG["domain"] + "\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
    urls = "".join(f"<url><loc>{BASE}{'' if p == 'index.html' else p}</loc><lastmod>{date.today()}</lastmod></url>\n"
                   for p in PAGES)
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    shutil.copy(ROOT / "assets" / "brand" / "hjc-tile.svg", DIST / "favicon.svg")
    for src, dst in [("favicon.ico", "favicon.ico"), ("apple-touch-icon.png", "apple-touch-icon.png"), ("icon-192.png", "icon-192.png")]:
        shutil.copy(ROOT / "assets" / "brand" / src, DIST / dst)
    (DIST / "404.html").write_text(simple_page(
        "Page not found", '<p>That page doesn\'t exist. <a href="./">Back to the home page</a>.</p>', "404.html"))
    (DIST / ".nojekyll").write_text("")
    (DIST / "llms.txt").write_text(LLMS.format(base=BASE, email=CFG["email"], linkedin=CFG["linkedin"]))


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets", ignore=shutil.ignore_patterns(*UNUSED_ASSETS))
    shutil.copy(SRC / "site.css", DIST / "assets" / "site.css")
    for name in PAGES:
        (DIST / name).write_text(fill(name, (SRC / name).read_text()))
    (DIST / "impressum.html").write_text(simple_page("Impressum", impressum_html(), "impressum.html"))
    (DIST / "privacy.html").write_text(simple_page("Privacy policy", privacy_html(), "privacy.html"))
    write_static()
    if not any(p.strip() for p in CFG["prices"].values()):
        warnings.append("Prices are hidden: each offer shows 'Price on request'.")
    print(f"Built {DIST}: {', '.join(PAGES)}, impressum.html, privacy.html")
    if warnings:
        print("\nBefore go-live:")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
