"""Æ Ø Å æ ø å, drawn with the letters they belong to: rings from the compass, one slash angle for Ø ø."""

from __future__ import annotations

import math

from ..diag import centre, stroke, x_at
from ..geom import quad
from ..master import Master
from ..parts import Ell, box, ring, shift
from ..shapes import lc_round, uc_round
from . import Drawing, glyph
from .control import o
from .lc_round import a, e
from .uc_diag import A


def ring_mark(m: Master, cx: float, bottom: float, d: float, weight: float) -> list:
    eo = Ell(cx, bottom + d / 2, d / 2, d / 2, m.tension)
    return ring(eo, eo.inset(weight, weight, m.tension_in))


def _bounds_x(contours) -> tuple[float, float]:
    xs = [p[0] for c in contours for p in c.flat(8)]
    return min(xs), max(xs)


@glyph("Aring", 0xC5, "uc")
def Aring(m: Master) -> Drawing:
    base = A(m).contours
    x0, x1 = _bounds_x(base)
    top = m.cap + m.osa(m.cap) + m.cap * m.g("ring.gap")
    return Drawing(base + ring_mark(m, (x0 + x1) / 2, top, m.cap * m.g("ring.uc"), m.cbar * m.g("ring.w")))


@glyph("aring", 0xE5, "lc")
def aring(m: Master) -> Drawing:
    base = a(m).contours
    x0, x1 = _bounds_x(base)
    top = m.xh + m.os(m.xh) + m.xh * m.g("ring.gap")
    return Drawing(base + ring_mark(m, (x0 + x1) / 2, top, m.xh * m.g("ring.lc"), m.bar * m.g("ring.w")))


def _slash(m: Master, cx: float, cy: float, r: float, weight: float) -> list:
    """The stroke through Ø ø: one angle for both, passing the round by the same amount at each end."""
    ang = math.radians(m.g("slash.angle"))
    reach = r + m.cap * m.g("slash.over")
    dx, dy = math.cos(ang) * reach, math.sin(ang) * reach
    return [stroke((cx - dx, cy - dy), (cx + dx, cy + dy), weight)]


@glyph("Oslash", 0xD8, "uc")
def Oslash(m: Master) -> Drawing:
    eo, ei = uc_round(m)
    return Drawing(ring(eo, ei) + _slash(m, eo.cx, eo.cy, eo.ry, m.cbar * m.g("slash.weight")))


@glyph("oslash", 0xF8, "lc")
def oslash(m: Master) -> Drawing:
    eo, ei = lc_round(m)
    return Drawing(o(m).contours + _slash(m, eo.cx, eo.cy, eo.ry, m.bar * m.g("slash.weight")))


@glyph("AE", 0xC6, "uc")
def AE(m: Master) -> Drawing:
    """A's left leg rising to an E; the A's bar is the E's middle arm carried across."""
    st, b = m.cstem, m.cbar
    xe = m.w("AE.leg")
    w = xe + m.w("E")
    t = st * m.diag
    yc = m.cap * m.ubar
    y0, y1 = yc - b / 2, yc + b / 2
    lb, lt = centre(("l", 0, 0), ("l", xe - st * m.g("AE.top"), m.cap), t, t * m.diag_thin)
    leg = stroke(lb, lt, t, t * m.diag_thin)
    xl = x_at(lb, lt, yc)
    wt, wm = xe + m.w("E") * m.g("E.top"), xe + m.w("E") * m.g("E.mid")
    e_part = quad((xe, 0), (w, 0), (w, b), (xe + st, b), (xe + st, y0), (wm, y0), (wm, y1), (xe + st, y1),
                  (xe + st, m.cap - b), (wt, m.cap - b), (wt, m.cap), (xe, m.cap))
    return Drawing([leg, e_part, box(xl, y0, xe + st / 2, y1)])


@glyph("ae", 0xE6, "lc")
def ae(m: Master) -> Drawing:
    """a and e sharing the a's stem: the e's left side runs into it."""
    left = a(m).contours
    x0, x1 = _bounds_x(left)
    right = e(m).contours
    ex0, _ = _bounds_x(right)
    return Drawing(left + shift(right, x1 - m.stem * (1 - m.g("ae.into")) - ex0))
