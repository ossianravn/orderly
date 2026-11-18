"""Arrows for signage: ← ↑ → ↓ ↖ ↗ ↘ ↙ ↔ ↕. A shaft and an open head of the figure stem. The straight arrows'
head is the chevron of < with arms at 45 degrees, ending on one cut square to the shaft; turned 45 degrees that
head becomes a corner of two straight arms, so the diagonal arrows are drawn that way, cut square, with the
shaft as a diagonal of the font. Every single arrow fills the same square, one cap height on each side."""

from __future__ import annotations

import math

from ..diag import hwidth, stroke
from ..geom import Contour
from ..master import Master
from ..parts import box, mirror_x, mirror_y, shift
from . import Drawing, glyph
from .figures import fw
from .symbols import _chevron


def _left(m: Master, length: float, head: float, double: bool) -> list[Contour]:
    """An arrow pointing left, its tip at the origin, its shaft along +x; head spans `head` across."""
    st = fw(m)[0] * m.g("arrow.w")
    ch = _chevron(m, head / 2, head, 0.0, st)
    out = ch + [box(st * 0.4, -st / 2, length - (st * 0.4 if double else 0), st / 2)]
    if double:
        out += mirror_x(ch, length / 2)
    return out


def _turned(cs: list[Contour], deg: float) -> list[Contour]:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [k.map(lambda p: (p[0] * c - p[1] * s, p[0] * s + p[1] * c)) for k in cs]


def _corner(m: Master) -> list[Contour]:
    """↗: the head turned 45 degrees is a corner of two straight arms, cut square; the shaft is a diagonal of
    the font, cut horizontally at the baseline and buried in the corner at the top."""
    st = fw(m)[0] * m.g("arrow.w")
    s, a = m.cap, m.cap * 0.62
    t = st * 1.0
    shaft = stroke((hwidth((0, 0), (s, s), t) / 2, 0), (s - st * 0.95, s - st * 0.95), t)
    return [box(s - a, s - st, s, s), box(s - st, s - a, s, s), shaft]


def _arrow(m: Master, direction: float, double: bool = False) -> Drawing:
    """direction: the way the arrow points, in degrees (0 right, 90 up)."""
    if direction % 90:
        cs = _corner(m)
        if direction in (135, 225):
            cs = mirror_x(cs, m.cap / 2)
        if direction in (225, 315):
            cs = mirror_y(cs, m.cap / 2)
    elif double:
        cs = _turned(_left(m, m.cap * 1.4, m.cap * 0.86, True), direction - 180)
    else:
        cs = _turned(_left(m, m.cap, m.cap, False), direction - 180)
    pts = [p for c in cs for p in c.flat(4)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    sb = m.cap * m.g("arrow.sb")
    cs = shift(cs, sb - x0, m.cap / 2 - (y0 + y1) / 2)
    return Drawing(cs, advance=x1 - x0 + 2 * sb)


ARROWS = {"arrowleft": (0x2190, 180), "arrowup": (0x2191, 90), "arrowright": (0x2192, 0), "arrowdown": (0x2193, 270),
          "uni2196": (0x2196, 135), "uni2197": (0x2197, 45), "uni2198": (0x2198, 315), "uni2199": (0x2199, 225)}

for _n, (_u, _d) in ARROWS.items():
    glyph(_n, _u, "uc")(lambda m, d=_d: _arrow(m, d))

glyph("arrowboth", 0x2194, "uc")(lambda m: _arrow(m, 180, True))
glyph("arrowupdn", 0x2195, "uc")(lambda m: _arrow(m, 90, True))
