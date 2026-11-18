"""Combining marks, lowercase and capital (.case) forms. Each is drawn about x = 0 on its attachment line:
`_top` at the x-height (or cap height), `_bottom` and `_ogonek` on the baseline; top marks carry a `top` anchor
for stacking (mkmk). Strokes come from the master's bar weight; dots are the font's round dots."""

from __future__ import annotations

import math

from ..diag import edges, peak_poly, stroke, vee_poly
from ..geom import Contour, line
from ..master import Master
from ..parts import Ell, box, disc, mirror_x, ring, rotate180
from ..strokes import hook, offsets
from . import Drawing, glyph
from .punct import comma_tail, dot_d

TOP = {"gravecomb": 0x300, "acutecomb": 0x301, "circumflexcomb": 0x302, "tildecomb": 0x303, "macroncomb": 0x304,
       "brevecomb": 0x306, "dotaccentcomb": 0x307, "dieresiscomb": 0x308, "ringcomb": 0x30A,
       "hungarumlautcomb": 0x30B, "caroncomb": 0x30C, "commaturnedabovecomb": 0x312}


def _frame(m: Master, case: bool):
    """Base line, gap above it, mark height, stroke weight, dot size."""
    base = m.cap if case else m.xh
    k = m.g("mark.case") if case else 1.0
    return base, m.xh * m.g("mark.gap") * k, m.xh * m.g("mark.h") * k, m.bar * m.g("mark.w"), dot_d(m) * m.g("mark.dot")


def _shape(name: str, m: Master, y0: float, h: float, w: float, d: float) -> list[Contour]:
    xh = m.xh
    if name in ("acutecomb", "gravecomb"):
        c = stroke((-0.3 * h, y0), (0.3 * h, y0 + h), w * 1.05)
        return [c] if name == "acutecomb" else mirror_x([c], 0)
    if name == "hungarumlautcomb":
        return [stroke((x - 0.27 * h, y0), (x + 0.27 * h, y0 + h), w) for x in (-0.13 * xh, 0.13 * xh)]
    if name in ("circumflexcomb", "caroncomb"):
        wc, a = xh * m.g("mark.hat"), w * 0.9
        if name == "circumflexcomb":
            return [peak_poly(edges(("l", -wc / 2, y0), ("l", -a / 2, y0 + h * 0.8), w, w * 0.85),
                              edges(("r", wc / 2, y0), ("r", a / 2, y0 + h * 0.8), w, w * 0.85))]
        return [vee_poly(edges(("l", -a / 2, y0), ("l", -wc / 2, y0 + h * 0.8), w * 0.85, w),
                         edges(("r", a / 2, y0), ("r", wc / 2, y0 + h * 0.8), w * 0.85, w))]
    if name == "dieresiscomb":
        return [disc(x, y0 + d / 2, d, m.tension) for x in (-xh * m.g("mark.dots"), xh * m.g("mark.dots"))]
    if name == "dotaccentcomb":
        return [disc(0, y0 + d / 2, d, m.tension)]
    if name == "ringcomb":
        r = xh * m.g("mark.ring") / 2
        eo = Ell(0, y0 + r, r, r, m.tension)
        k = min(w * 0.9, r * 0.42)  # heavy rings keep a counter
        return ring(eo, eo.inset(k, k, m.tension_in))
    if name == "macroncomb":
        return [box(-xh * 0.24, y0 + h * 0.2, xh * 0.24, y0 + h * 0.2 + w)]
    if name == "brevecomb":
        r = xh * 0.2
        eo = Ell(0, y0 + h * 0.7, r, h * 0.7, m.tension)
        ei = eo.inset(w * 1.05, w, m.tension_in)
        o, i = eo.arc("W", "S", "E"), ei.arc("W", "S", "E")
        return [Contour.of(o, line(o.end, i.end), i.reversed())]
    if name == "tildecomb":
        wt, ht = xh * 0.24, h * 0.5
        a = math.radians(48)
        nodes = [((-wt, y0 + ht * 0.25), (math.cos(a), math.sin(a)), w), ((-wt / 2, y0 + ht), (1.0, 0.0), w),
                 ((wt / 2, y0), (1.0, 0.0), w), ((wt, y0 + ht * 0.75), (math.cos(a), math.sin(a)), w)]
        left, right = offsets(nodes, [(0.56, 0.56)] * 3)
        x0, x1 = -wt + w * 0.4, wt - w * 0.4
        left, right = left.cut_x(x0, "tail", 0).cut_x(x1, "head", -1), right.cut_x(x0, "tail", 0).cut_x(x1, "head", -1)
        c = Contour.of(left, line(left.end, right.end), right.reversed())
        return [c if c.area() > 0 else c.reversed()]
    if name == "commaturnedabovecomb":  # the comma turned half round, its dot at the bottom
        return rotate180([disc(0, 0, d, m.tension), comma_tail(m, 0, 0)], 0, 0)
    raise KeyError(name)


def _top_mark(name: str, case: bool):
    def fn(m: Master) -> Drawing:
        base, gap, h, w, d = _frame(m, case)
        y0 = base + gap
        cs = _shape(name, m, y0, h, w, d)
        if name == "commaturnedabovecomb":
            from ..parts import shift

            cs = shift(cs, 0, y0 + d / 2)
        top = max(p[1] for c in cs for p in c.flat(6))
        return Drawing(cs, anchors={"_top": (0, base), "top": (0, top + gap)})

    return fn


for _n, _u in TOP.items():
    glyph(_n, _u, "mark")(_top_mark(_n, False))
    glyph(_n + ".case", None, "mark")(_top_mark(_n, True))


@glyph("cedillacomb", 0x327, "mark")
def cedillacomb(m: Master) -> Drawing:
    """A short stem from inside the letter's foot turning left in a small hook, cut vertically."""
    w = m.bar * m.g("mark.w")
    st = w * 1.1
    rx = max(st * 1.9, m.xh * 0.12)
    hk = hook(0, st, w, m.bar * 0.45, -m.xh * 0.3, rx, rx * 0.8, rx + (rx - st) * 0.75, m.tension, m.tension_in)
    return Drawing(mirror_x([hk], st / 2), anchors={"_bottom": (0, 0)})


@glyph("ogonekcomb", 0x328, "mark")
def ogonekcomb(m: Master) -> Drawing:
    """From the letter's right foot down, turning right in the hook of the family, cut vertically."""
    w = m.bar * m.g("mark.w")
    st = w * 1.1
    rx = max(st * 2.1, m.xh * 0.14)
    x0 = -st / 2
    hk = hook(x0, st, w, m.bar * 0.45, -m.xh * 0.32, rx, rx * 0.85, x0 + rx + (rx - st) * 0.8, m.tension, m.tension_in)
    return Drawing([hk], anchors={"_ogonek": (0, 0)})


@glyph("commaaccentcomb", 0x326, "mark")
def commaaccentcomb(m: Master) -> Drawing:
    d = dot_d(m) * m.g("mark.dot")
    cy = -m.xh * m.g("mark.gap") - d / 2
    return Drawing([disc(0, cy, d, m.tension), comma_tail(m, 0, cy)], anchors={"_bottom": (0, 0)})


@glyph("caroncomb.alt", None, "mark")
def caron_alt(m: Master) -> Drawing:
    """The caron of ď ľ ť Ľ: a short vertical comma beside the ascender."""
    d = dot_d(m) * m.g("mark.dot") * 0.9
    cy = m.asc - d / 2
    return Drawing([disc(0, cy, d, m.tension), comma_tail(m, 0, cy)], anchors={"_caronalt": (-d * 0.5, m.asc)})
