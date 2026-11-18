"""Capital rounds: C G Q D S. C G Q come from the O's round; D is a stem with a half round."""

from __future__ import annotations

import math

from ..diag import stroke
from ..geom import Contour, tcurve
from ..master import Master
from ..parts import dbowl, ring
from ..rounds import cut_round
from ..shapes import uc_round
from ..strokes import SSpec, s_curve
from . import Drawing, glyph


def _cut_x(m: Master, ei) -> float:
    return ei.cx + ei.rx * math.cos(math.radians(m.ap_C))


@glyph("C", 0x43, "uc")
def C(m: Master) -> Drawing:
    eo, ei = uc_round(m)
    x = _cut_x(m, ei)
    return Drawing([cut_round(eo, ei, x, x)])


@glyph("G", 0x47, "uc")
def G(m: Master) -> Drawing:
    """C's upper terminal; below, the round turns up into a short vertical jaw carrying a horizontal bar."""
    eo, ei = uc_round(m)
    xt = _cut_x(m, ei)
    xj = eo.cx + eo.rx * m.g("G.jaw")
    jaw = m.cstem
    yj = m.cap * m.g("G.foot")
    ybt = m.cap * m.g("G.bar")
    ybb = ybt - m.cbar
    xbl = eo.cx + eo.rx * m.g("G.barl")
    so, si = eo.p("S"), ei.p("S")
    outer = eo.arc("E", "N", "W", "S").cut_x(xt, "tail", 0)
    outer.add(tcurve(so, (1, 0), (xj, yj), (0, 1), m.tension))
    outer.to((xj, ybt)).to((xbl, ybt)).to((xbl, ybb)).to((xj - jaw, ybb))
    inner = ei.arc("E", "N", "W", "S").cut_x(xt, "tail", 0)
    inner.add(tcurve(si, (1, 0), (xj - jaw, yj), (0, 1), m.tension_in))
    inner.to((xj - jaw, ybb))
    return Drawing([Contour.of(outer, inner.reversed())])


@glyph("Q", 0x51, "uc")
def Q(m: Master) -> Drawing:
    eo, ei = uc_round(m)
    r = eo.rx
    top = (eo.cx + r * m.g("Q.x0"), m.cap * m.g("Q.y0"))
    bot = (eo.cx + r * m.g("Q.x1"), m.cap * m.g("Q.y1"))
    return Drawing(ring(eo, ei) + [stroke(bot, top, m.cstem * m.diag)])


@glyph("D", 0x44, "uc")
def D(m: Master) -> Drawing:
    w = m.w("D")
    return Drawing(dbowl(0, m.cstem, 0, m.cap, w, m.cap / 2 * m.g("D.round"), m.cbar, m.cstem * m.rside,
                         m.tension, m.tension_in))


def S_spec(m: Master) -> SSpec:
    return SSpec(
        x0=0, w=m.w("S"), bot=-m.os(m.cap), top=m.cap + m.os(m.cap), ym=m.cap * m.g("s.mid"),
        upper=m.g("s.upper"), th=m.cbar * m.rtop * m.g("s.thin"), side=m.cstem * m.rside * m.g("s.thin"),
        spine=m.cstem * m.g("s.spinew"), steep=m.g("s.steep"), ap=m.g("s.ap"), t=m.tension, t_in=m.tension_in,
        k=m.g("s.k"), tilt=m.g("s.tilt"), lean=m.g("s.lean") * m.w("S"),
    )


@glyph("S", 0x53, "uc")
def S(m: Master) -> Drawing:
    return Drawing([s_curve(S_spec(m))])

