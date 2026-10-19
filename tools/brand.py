#!/usr/bin/env python3
"""Draw the Harry James Coburn mark and lockups as standalone SVG files in assets/brand/.

The mark is H, J and C, with an ember dot in the C: a station on the line, the "you are here"
of the Commercial Engine. The wordmark is Schibsted Grotesk Bold, turned into outlines so the
files look the same anywhere (LinkedIn, CV, slides) without the font installed.

    python3 tools/brand.py
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "brand"
INK, PAPER, EMBER, SUN, DEEP = "#0D1411", "#FFFDF8", "#E2582B", "#F4B63F", "#10372A"
NAME = "Harry James Coburn"
MARK_W, MARK_H = 70, 32


def mark(ink, dot):
    """The HJC mark in a 70 x 32 box: H, a J, and a C with the station dot."""
    cx, r, sw, a = 57, 13, 6, 45
    x = cx + r * math.cos(math.radians(a))
    y1, y2 = 16 - r * math.sin(math.radians(a)), 16 + r * math.sin(math.radians(a))
    return (f'<rect width="6" height="32" fill="{ink}"/><rect x="14" width="6" height="32" fill="{ink}"/>'
            f'<rect x="6" y="13" width="8" height="6" fill="{ink}"/>'
            f'<path d="M35 0V23A6 6 0 0 1 29 29H26" fill="none" stroke="{ink}" stroke-width="6"/>'
            f'<path d="M{x:.2f} {y1:.2f}A{r} {r} 0 1 0 {x:.2f} {y2:.2f}" fill="none" stroke="{ink}" stroke-width="{sw}"/>'
            f'<circle cx="{cx}" cy="16" r="3.8" fill="{dot}"/>')


def wordmark(text, size):
    """Outline text in Schibsted Grotesk Bold. Returns (path data, width, cap height) in px."""
    font = TTFont(ROOT / "assets" / "fonts" / "schibsted-grotesk-latin-wght-normal.woff2")
    font = instantiateVariableFont(font, {"wght": 700})
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    upm = font["head"].unitsPerEm
    scale = size / upm
    tracking = -0.015 * upm
    cap = font["OS/2"].sCapHeight * scale
    pen = SVGPathPen(gs)
    x = 0
    for ch in text:
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (scale, 0, 0, -scale, x * scale, cap))
        gs[g].draw(tp)
        x += hmtx[g][0] + tracking
    return pen.getCommands(), (x - tracking) * scale, cap


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def lockup(ink, dot, bg=None, size=40):
    d, tw, cap = wordmark(NAME, size)
    mh = cap * 1.18                      # mark a touch taller than the capitals
    mw = mh * MARK_W / MARK_H
    gap, pad = size * 0.42, (size * 0.6 if bg else 0)
    desc = size * 0.24                   # room for the y's descender
    w, h = pad * 2 + mw + gap + tw, pad * 2 + max(mh, (mh - cap) / 2 + cap + desc)
    s = mh / MARK_H
    body = (f'<rect width="100%" height="100%" rx="{size*.3:.1f}" fill="{bg}"/>' if bg else "")
    body += f'<g transform="translate({pad:.2f} {pad:.2f}) scale({s:.4f})">{mark(ink, dot)}</g>'
    body += f'<path transform="translate({pad + mw + gap:.2f} {pad + (mh - cap) / 2:.2f})" d="{d}" fill="{ink}"/>'
    return svg(w, h, body, NAME)


def tile(size=64):
    return svg(size, size, f'<rect width="64" height="64" rx="14" fill="{INK}"/>'
                           f'<g transform="translate(7 20.5) scale(.7143)">{mark(PAPER, EMBER)}</g>', "HJC")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "hjc-mark.svg").write_text(svg(MARK_W, MARK_H, mark(INK, EMBER), NAME))
    (OUT / "hjc-mark-light.svg").write_text(svg(MARK_W, MARK_H, mark(PAPER, SUN), NAME))
    (OUT / "hjc-lockup.svg").write_text(lockup(INK, EMBER))
    (OUT / "hjc-lockup-light.svg").write_text(lockup(PAPER, SUN))
    (OUT / "hjc-lockup-deep.svg").write_text(lockup(PAPER, SUN, bg=DEEP))
    (OUT / "hjc-tile.svg").write_text(tile())
    print("Wrote", ", ".join(p.name for p in sorted(OUT.glob("*.svg"))))


if __name__ == "__main__":
    main()
