"""Math operators beyond ASCII: × ÷ ≠ ≤ ≥ ± ≈ ¬ ∞ ◊. All share the math width and sit on the figures' centre
(see symbols.math_glyph); bars are the bar weight, verticals and diagonals the stem."""

from __future__ import annotations

from ..diag import stroke
from ..geom import Contour, quad
from ..master import Master
from ..parts import Ell, box, disc, mirror_x, shift
from ..rounds import meet
from . import Drawing, glyph
from .punct import dot_d
from .symbols import _chevron, _w, math_glyph, mid, tilde_shape


def _cross(m: Master) -> list:
    w, y, t = _w(m), mid(m), m.stem * 0.92
    s = w * 0.76 / 2
    cx = w / 2
    return [stroke((cx - s, y - s), (cx + s, y + s), t), stroke((cx + s, y - s), (cx - s, y + s), t)]


@glyph("multiply", 0xD7, "uc")
@math_glyph
def multiply(m: Master) -> Drawing:
    return Drawing(_cross(m))


@glyph("divide", 0xF7, "uc")
@math_glyph
def divide(m: Master) -> Drawing:
    w, b, y = _w(m), m.bar, mid(m)
    d = dot_d(m) * 0.95
    off = b / 2 + d * 0.55 + d / 2
    return Drawing([box(0, y - b / 2, w, y + b / 2), disc(w / 2, y + off, d, m.tension), disc(w / 2, y - off, d, m.tension)])


def _equal_bars(m: Master) -> list:
    w, b, y, g = _w(m), m.bar, mid(m), m.cap * 0.1
    return [box(0, y + g - b / 2, w, y + g + b / 2), box(0, y - g - b / 2, w, y - g + b / 2)]


@glyph("notequal", 0x2260, "uc")
@math_glyph
def notequal(m: Master) -> Drawing:
    w, y = _w(m), mid(m)
    h = w * 0.44
    return Drawing(_equal_bars(m) + [stroke((w * 0.32, y - h), (w * 0.68, y + h), m.stem * 0.88)])


def _less_bar(m: Master, flip: bool) -> list:
    w, b, y = _w(m), m.bar, mid(m)
    h = w * 0.7
    gap = m.cap * 0.07
    yb = y - w * 0.42  # the bar's centre
    yc = yb + b / 2 + gap + h / 2
    ch = _chevron(m, w, h, yc, (m.stem + m.bar) / 2 * 0.95)  # flatter than <, so a little lighter
    if flip:
        ch = mirror_x(ch, w / 2)
    return ch + [box(0, yb - b / 2, w, yb + b / 2)]


@glyph("lessequal", 0x2264, "uc")
@math_glyph
def lessequal(m: Master) -> Drawing:
    return Drawing(_less_bar(m, False))


@glyph("greaterequal", 0x2265, "uc")
@math_glyph
def greaterequal(m: Master) -> Drawing:
    return Drawing(_less_bar(m, True))


@glyph("plusminus", 0xB1, "uc")
@math_glyph
def plusminus(m: Master) -> Drawing:
    w, b, y = _w(m), m.bar, mid(m)
    yb = y - w * 0.42
    arm = w * 0.38
    yp = yb + b / 2 + m.cap * 0.06 + arm
    v = m.stem * 0.47
    return Drawing([box(0, yp - b / 2, w, yp + b / 2), box(w / 2 - v, yp - arm, w / 2 + v, yp + arm),
                    box(0, yb - b / 2, w, yb + b / 2)])


@glyph("approxequal", 0x2248, "uc")
@math_glyph
def approxequal(m: Master) -> Drawing:
    t = tilde_shape(m, 0.34, 0.9)
    g = m.cap * 0.125
    return Drawing(shift(t, 0, g) + shift(t, 0, -g))


@glyph("logicalnot", 0xAC, "uc")
@math_glyph
def logicalnot(m: Master) -> Drawing:
    w, b, y = _w(m), m.bar, mid(m)
    st = m.stem * 0.94
    return Drawing([box(0, y - b / 2, w, y + b / 2), box(w - st, y - m.cap * 0.2, w, y + b / 2)])


@glyph("infinity", 0x221E, "uc")
@math_glyph
def infinity(m: Master) -> Drawing:
    """Two rounds side by side whose outlines cross at the waist; their counters stay apart (the 8 lying down)."""
    w, y = _w(m), mid(m)
    side, th = m.stem * 0.88, m.bar * 0.9  # the + and = weights: stem-like sides, bar-like tops
    gap = side * 0.55  # the counters' distance from the waist
    r = (w * 0.62 + side / 2 + gap / 2) / 2  # so the sign is 1.24 of the math width in every master
    ry = r * 0.94
    cl, cr = w / 2 - (r - side / 2 - gap / 2), w / 2 + (r - side / 2 - gap / 2)
    lo, ro = Ell(cl, y, r, ry, m.tension), Ell(cr, y, r, ry, m.tension)
    lp, rp = lo.arc("E", "N", "W", "S", "E"), ro.arc("W", "S", "E", "N", "W")
    hits = meet(lp, rp)
    (ta, tb, _), (ba, bb, _) = hits[0], hits[-1]
    outer = Contour.of(lp.piece(ta, ba).then(rp.piece(bb, tb)))
    li, ri = lo.inset(side, th, m.tension_in), ro.inset(side, th, m.tension_in)
    counters = [Contour.of(e.arc("S", "W", "N", "E", "S")) for e in (li, ri)]
    return Drawing([outer] + counters)


@glyph("lozenge", 0x25CA, "uc")
@math_glyph
def lozenge(m: Master) -> Drawing:
    w, y = _w(m), mid(m)
    a, h = w * 0.4, m.cap * 0.47
    t = m.stem * 0.92
    k = (a * a + h * h) ** 0.5
    ai, hi = a - t * k / h, h - t * k / a
    cx = w / 2
    outer = quad((cx - a, y), (cx, y - h), (cx + a, y), (cx, y + h))
    inner = quad((cx - ai, y), (cx, y + hi), (cx + ai, y), (cx, y - hi))
    return Drawing([outer, inner])
