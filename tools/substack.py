"""Read the Substack feed saved at data/substack.xml (refreshed daily by .github/workflows/refresh.yml)."""
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

FEED = Path(__file__).resolve().parent.parent / "data" / "substack.xml"


def posts(limit=30):
    if not FEED.exists() or not FEED.read_text().strip():
        return []
    try:
        root = ET.fromstring(FEED.read_bytes())
    except ET.ParseError:
        return []
    out = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if not title or not link.startswith("https://"):
            continue
        desc = unescape(re.sub(r"<[^>]+>", "", it.findtext("description") or "")).strip()
        try:
            when = parsedate_to_datetime(it.findtext("pubDate") or "")
        except (TypeError, ValueError):
            when = None
        img = None
        enc = it.find("enclosure")
        if enc is not None and (enc.get("type") or "").startswith("image/"):
            img = enc.get("url")
        out.append({"title": title, "link": link, "desc": desc[:220], "date": when, "img": img})
    out.sort(key=lambda p: p["date"].timestamp() if p["date"] else 0, reverse=True)
    return out[:limit]
