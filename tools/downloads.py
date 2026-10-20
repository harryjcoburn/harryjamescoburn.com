#!/usr/bin/env python3
"""Write the printable speaking kit and one-page case studies as HTML in tools/_print/.
Render them to PDF with:  node tools/render_downloads.mjs   (writes assets/downloads/*.pdf)
All copy is taken word for word from the live site (work.html, speaking.html)."""
from html import escape
from pathlib import Path

from brand import mark as brand_mark

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "_print"
MARK = '<svg class="mark" viewBox="0 0 70 32" aria-hidden="true">' + brand_mark("currentColor", "none") + "</svg>"

CASES = [
 {"slug": "uxcam", "logo": "uxcam.svg", "kicker": "The rebuild · 2026", "name": "UXCam",
  "ctx": "AI product analytics · Backed by Headline · Head of Sales, a six-month engagement",
  "nums": [("~25 → 40%", "inbound leads becoming sales-qualified"), ("1 day → 5 min", "first reply to every inbound lead, with AI agents"),
           ("5 regions", "forecast, quotas and performance framework, North America to APAC")],
  "before": "Inbound was manual and slow: every lead was checked and enriched by hand, so first replies took about a day. There was no outbound and no clear ICP. The team took any customer, in any market, on any tier, and discounted hard to win. Without a clear view of where the product created most value, nobody had the confidence to hold price. A new AI agent product was about to launch.",
  "did": ["Went through all the data and spoke to the whole team: which deals closed fastest, which brought the most value, and which customers got the most from the product.",
          "Found that value grew with scale: companies with large apps and many users saw returns many times their spend, while small accounts took as much effort for a fraction of the revenue.",
          "Reset the ICP around larger companies with apps, stepped back from markets where deals were small, slow and heavily discounted, and shifted focus quickly when regional demand changed.",
          "Rebuilt pricing for the AI product: from a model with many variables to a simple usage-based model, priced on AI usage the way the AI model providers price theirs, so it was easier to buy and grew with the value customers got.",
          "Built an AI agent on inbound with HubSpot, Claude Code and our own enrichment. Every form fill is researched, enriched, profiled and qualified within minutes, a reply is drafted and a call set up, and the best leads trigger an alert for an SDR to call straight away.",
          "Built outbound from zero, using app store data, Clay and AI to find companies where the product could make a big difference. In the first month, the first run reached about 500 accounts and 4,000 contacts. Then came a lot of testing and iteration on the message by person, company and timing, with results building over the months after.",
          "Owned the forecast, and set the quotas and performance framework for the team across five regions."],
  "after": "Inbound leads becoming sales-qualified went from ~25% to ~40%. First reply went from about a day to 5 minutes, which freed the SDRs to focus on outbound.", "note": ""},
 {"slug": "arbonics", "logo": "arbonics.svg", "kicker": "The scale · 2024–25", "name": "Arbonics",
  "ctx": "Forest carbon · Backed by Plural · Head of Sales & New Markets, through my consultancy",
  "nums": [("~€10M", "in estimated contract value won in 12 months, on the company's own model"), ("€0.1M → €5.4M", "sales a quarter in nine months (37×)"),
           ("75 → 16 days", "the average sales cycle"), ("2 → 12", "sales team hired and trained, SDRs and AEs in every market")],
  "before": "Three generalist salespeople, each working alone on round-robin inbound leads of poor quality. Outbound was meant to happen, but nobody knew how or who to target. The CRM was half-filled and nothing was documented. A new product in a traditional market, sold to people with a few hectares of forest on the side, on a long contract nobody wanted to sign.",
  "did": ["Qualified up. Small plots took as long to close as large ones, so we moved from part-time landowners to businesses and professional owners. For a team hungry for any sale, that was a real cultural shift.",
          "Used data to find the land that would qualify, found who owned it, and went to them with outbound.",
          "Sold it as an investment: return on investment, and carbon credit income on top of a forest they were already growing, with models that showed the return.",
          "Replaced a long 50-year contract with a one-page first step. Same commitment, but the owner kept control and could pull out. The detail moved to a second contract once the land was agreed.",
          "Rebuilt the team around an SDR and an AE in every market, plus a key account manager, a team lead, a head of expansion and quality checks on every deal. Grew it from 2 to 12, and moved from Pipedrive to HubSpot as one source of truth.",
          "Built a cross-market function selling to investment funds, which already think long-term about land and saw carbon credits as a new revenue stream. Senior meetings came faster, and several funds signed, each bringing roughly 700 to 5,000 hectares over time.",
          "Launched new markets with people on the ground: legal checks and an early outreach plan in each, and in Sweden a local partner who already knew most of the landowners, on shared commission."],
  "after": "I led the sales function as quarterly sales grew 37× in nine months: about €10M in estimated contract value won in 12 months, on the company's own model. In Latvia, where we piloted the SDR and AE split, the average deal grew from about 5–10 hectares to around 70 at its peak. The average sales cycle fell from 75 to 16 days. 85% of everything Arbonics had ever sold was won while I led sales.",
  "note": "Estimated contract value uses Arbonics' own model of about €1,000 per hectare contracted. Quarterly sales grew from 144 to 5,393 hectares in nine months."},
 {"slug": "wheely", "logo": "wheely-legacy.svg", "kicker": "The scale · 2019–21", "name": "Wheely",
  "ctx": "Premium chauffeur platform · Backed by Concentric · Global Head of B2B Sales & Customer Success",
  "nums": [("+75%", "UK sales in my first two months"), ("912%", "B2B recovery from the Covid low, April to December 2020"),
           ("~$500k", "a month in B2B revenue I owned, across the UK, France and Russia")],
  "before": "A small UK business-travel arm inside a consumer app. Then Covid emptied the roads.",
  "did": ["Started as a consultant on the UK market. Took on every stalled lead and deal in the CRM and ran follow-up campaigns until they signed and took their first journeys.",
          "Reused my Pronto playbook from the bottom up: found riders expensing trips to their employer, grouped them by company, and asked them to introduce the right person. Then went top down with the evidence: this many of your people already ride with us, even at companies signed with a competitor.",
          "Became Head of Sales UK, then Global Head of B2B Sales and Customer Success across the UK, France and Russia, adapting the approach to each market, and prepared the market plan for a Dubai launch.",
          "Through Covid, called every client and made safety the reason to choose us: cleaning after every journey, masks, sanitiser, and still a premium experience, so offices could reopen with confidence.",
          "Won investment funds and large companies by inviting them to try us on our account, then onboarding every level of the organisation, through legal and procurement sign-off, and proving reliability again and again.",
          "Moved 300+ corporate clients to a new UK entity."],
  "after": "UK sales up 75% and journeys up 118% in my first two months. B2B recovered 912% from the Covid low (April to December 2020). The biggest accounts spent around $30,000 a month.", "note": ""},
 {"slug": "pronto", "logo": "pronto.svg", "kicker": "Zero to one · 2015–16", "name": "Pronto",
  "ctx": "15-minute healthy food delivery, London · Backed by Playfair Capital and Seedcamp · Head of B2B Sales & Partnerships",
  "nums": [("0 → 60%", "of company revenue from the B2B business I built"), ("40%", "of early revenue through Seamless, one of its best-rated providers"),
           ("Wise · Telefónica", "among the business clients won")],
  "before": "A consumer app with a cult following and no business customers at all.",
  "did": ["Went in through the consumer and worked up. I looked at the work email domains of our biggest fans, found their employers, and pitched: “your team already orders from us, so how about lunch for the whole office?”, with offers to feed whole teams.",
          "Built an office lunch service around a gap nobody filled: staff ordered by a cut-off and everything arrived together at lunchtime, hot and healthy. For some offices it replaced the canteen.",
          "Won clients including Wise, a regular for team lunches, and Telefónica, which came in looking to replace its in-house canteen.",
          "Used my network to get Pronto onto Seamless years before others were allowed on. The clincher: many of Seamless's own clients were already ordering from us off the platform. We became one of its best-rated providers."],
  "after": "B2B grew from zero to 60% of company revenue, and Seamless alone brought 40% of early revenue. Pronto later closed when its next funding round didn't come through. The B2B playbook is one I've reused ever since.", "note": ""},
]

CSS = """@page{size:A4;margin:0}
@font-face{font-family:G;src:url(../../assets/fonts/schibsted-grotesk-latin-wght-normal.woff2);font-weight:400 900}
@font-face{font-family:S;src:url(../../assets/fonts/newsreader-latin-opsz-italic.woff2);font-style:italic}
@font-face{font-family:M;src:url(../../assets/fonts/roboto-mono-latin-500-normal.woff2)}
*{box-sizing:border-box}html,body{margin:0}
body{font-family:G,Arial,sans-serif;color:#0D1411;background:#FFFDF8;font-size:10pt;line-height:1.45}
.page{width:210mm;height:297mm;padding:16mm 16mm 12mm;display:flex;flex-direction:column;gap:6mm;overflow:hidden;page-break-after:always}
.mono{font-family:M,monospace;font-size:7.4pt;letter-spacing:.08em;text-transform:uppercase;color:#B8461C}
.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1.5pt solid #0D1411;padding-bottom:4mm}
.top .mark{width:16mm;height:auto;color:#0D1411}.top .mark .stn,.foot .mark circle:last-child{fill:#E2582B}
.top img{height:9mm;width:auto}
h1{font-size:28pt;line-height:1;letter-spacing:-.04em;margin:2mm 0 1mm}
h1 em{font-family:S,serif;font-weight:400;color:#B8461C}
.ctx{color:#5B6660;font-size:10.5pt}
.nums{display:grid;gap:3mm}.nums div{background:#F5F3EC;border-radius:3mm;padding:4mm}
.nums b{display:block;font-size:17pt;letter-spacing:-.03em;line-height:1.05;margin-bottom:1mm}
.nums span{color:#5B6660;font-size:8.6pt}
h2{font-size:12pt;margin:0 0 1.5mm;letter-spacing:-.01em}
p{margin:0}
ul{margin:0;padding-left:4.5mm;display:grid;gap:1.6mm}
.after{background:#10372A;color:#fff;border-radius:3mm;padding:5mm}.after h2{color:#fff}.after p{color:#D7E6DD}
.note{font-size:8pt;color:#5B6660}
.foot{margin-top:auto;display:flex;justify-content:space-between;align-items:center;border-top:.6pt solid #E4E8E4;padding-top:3mm;font-size:8.4pt;color:#5B6660}
.foot .mark{width:10mm;height:auto;color:#0D1411}
.foot a{color:#0D1411;text-decoration:none}
.photo{width:40mm;height:46mm;object-fit:cover;border-radius:3mm}
.bio{display:grid;grid-template-columns:40mm 1fr;gap:7mm;align-items:start}
.bio p{font-size:10.5pt}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:6mm}
.box{border:.8pt solid #E4E8E4;border-radius:3mm;padding:4mm;background:#fff}
.box h3{font-size:10.5pt;margin:0 0 1mm}.box p{color:#5B6660;font-size:9pt}
.stack{display:grid;gap:3mm}
.cols3{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.dense{font-size:9.2pt}.dense ul{gap:1.1mm}.dense .page{gap:4.5mm}
"""


def foot():
    return (f'<div class="foot">{MARK}<span>harry@harryjamescoburn.com · <a href="https://harryjamescoburn.com">harryjamescoburn.com</a>'
            f' · <a href="https://www.linkedin.com/in/hcoburn/">linkedin.com/in/hcoburn</a></span><span>Berlin · London</span></div>')


def case_page(c):
    n = len(c["nums"])
    nums = "".join(f"<div><b>{escape(a)}</b><span>{escape(b)}</span></div>" for a, b in c["nums"])
    did = "".join(f"<li>{escape(x)}</li>" for x in c["did"])
    note = f'<p class="note">{escape(c["note"])}</p>' if c["note"] else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{escape(c['name'])} case study · Harry James Coburn</title><style>{CSS}</style></head><body class="{'dense' if len(c['did'])>6 else ''}">
<section class="page">
 <div class="top">{MARK}<img src="../../assets/logos/{c['logo']}" alt="{escape(c['name'])}"></div>
 <div><div class="mono">Case study · {escape(c['kicker'])}</div><h1>{escape(c['name'])}</h1><p class="ctx">{escape(c['ctx'])}</p></div>
 <div class="nums" style="grid-template-columns:repeat({n},1fr)">{nums}</div>
 <div><h2>Before</h2><p>{escape(c['before'])}</p></div>
 <div><h2>What I did</h2><ul>{did}</ul></div>
 <div class="after"><h2>After</h2><p>{escape(c['after'])}</p></div>
 {note}
 {foot()}
</section></body></html>"""


def kit_page():
    topics = [("AI and sales", "Find the formula. Then scale it.", "AI will scale whatever you give it. What to automate, what not to, and why most AI sales projects scale the wrong thing."),
              ("New markets", "Launching where you're unknown", "Taking a product into a new country or segment: finding the first customers, the right partners and a motion that travels."),
              ("Building teams", "From founder-led to a sales engine", "When the founder is in every deal: the hires, the process and the numbers that let a team sell without them.")]
    formats = [("Talks and keynotes", "20 to 45 minutes, for founder, sales and investor audiences, in person in Berlin and London or remote"),
               ("Panels and fireside chats", "On go-to-market, AI in sales, pricing and launching into new markets"),
               ("Podcasts", "Interviews on building sales engines, the lessons from four VC-backed companies, and what AI changes"),
               ("Portfolio workshops", "Office hours and workshops for investors' portfolio companies, on getting the commercial formula right before they scale it.")]
    t = "".join(f'<div class="box"><div class="mono">{escape(a)}</div><h3>{escape(b)}</h3><p>{escape(c)}</p></div>' for a, b, c in topics)
    f = "".join(f'<div class="box"><h3>{escape(a)}</h3><p>{escape(b)}</p></div>' for a, b in formats)
    bio = ("Harry James Coburn is a Berlin-based commercial strategy and go-to-market adviser for growing tech companies. "
           "He has led sales at UXCam, Arbonics, Wheely and Pronto, companies backed by Headline, Plural, Concentric, Seedcamp "
           "and Playfair, and trained at IBM, Credit Suisse and Lloyds Banking Group. His work centres on one idea: find the "
           "commercial formula first, then use AI to scale it.")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Speaking kit · Harry James Coburn</title><style>{CSS}</style></head><body class="dense">
<section class="page">
 <div class="top">{MARK}<span class="mono">Speaking kit</span></div>
 <div><div class="mono">Talks · panels · podcasts · portfolio workshops</div><h1>Harry James <em>Coburn.</em></h1><p class="ctx">Commercial strategy in the age of AI agents. Practical, honest about what fails, and built on real numbers.</p></div>
 <div class="bio"><img class="photo" src="../../assets/photos/hero.jpg" alt="Harry James Coburn"><div class="stack"><div class="mono">Speaker bio</div><p>{escape(bio)}</p><p class="note">Feel free to use this bio and photo. For a high-resolution photo, email harry@harryjamescoburn.com.</p></div></div>
 <div><h2>What I talk about</h2><div class="cols3">{t}</div></div>
 <div><h2>Formats</h2><div class="cols">{f}</div></div>
 <div class="after"><h2>Invite me</h2><p>Email harry@harryjamescoburn.com with the date, audience and format.</p></div>
 {foot()}
</section></body></html>"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "speaking-kit.html").write_text(kit_page())
    for c in CASES:
        (OUT / f"case-study-{c['slug']}.html").write_text(case_page(c))
    print("Wrote", ", ".join(sorted(p.name for p in OUT.glob("*.html"))))


if __name__ == "__main__":
    main()
