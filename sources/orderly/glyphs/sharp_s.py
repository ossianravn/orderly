"""ß and ẞ.

ß is a stem that rises into an upper round (the stem is that round's west side, as in the f's hook), comes down
the right into a short waist cut vertically on the left, and runs on into a wider lower round that ends in a
vertical cut at the bottom left, clear of the stem: the 3 standing on a stem. It reads as two bowls, not as a b
with a flag.
"""

from __future__ import annotations

import math

from ..diag import placed, stroke
from ..geom import Contour, line, quad
from ..master import Master
from ..parts import Ell, dbowl
from ..rounds import meet
from . import Drawing, glyph


@glyph("germandbls", 0xDF, "lc")
def germandbls(m: Master) -> Drawing:
    st, side, th = m.stem, m.stem * m.rside, m.bar * m.rtop
    w = m.w("n")
    t, ti = m.tension, m.tension_in
    os = m.os(m.xh)
    top = m.asc + m.os(m.asc)
    ym = m.xh * m.g("ss.waist")
    ymb, ymt = ym - th / 2, ym + th / 2
    xur = w * 0.84  # the upper round's east extreme
    uo = Ell(xur / 2, (top + ymb) / 2, xur / 2, (top - ymb) / 2, t)
    ui = uo.inset(st, th, ti)
    x0l = st * 0.25  # the lower round's west extreme, inside the stem; the part left of the cut is cut away
    lo = Ell((x0l + w) / 2, (ymt - os) / 2, (w - x0l) / 2, (ymt + os) / 2, t)
    li = lo.inset(side, th, ti)
    xl = li.cx - li.rx * math.cos(math.radians(40))  # the bottom terminal's vertical cut
    xm = st + (w - st) * 0.25  # the waist's vertical cut
    up = uo.arc("W", "N", "E", "S")
    low = lo.arc("N", "E", "S", "W").cut_x(xl, "head", -1)
    ia, ib, _ = meet(up, low)[-1]
    outer = line((0, 0), uo.p("W")).then(up.piece(None, ia)).then(low.piece(ib, None))
    lo_in = li.arc("N", "E", "S", "W").cut_x(xl, "head", -1)
    up_in = ui.arc("W", "N", "E", "S")
    inner = lo_in.reversed().to((xm, ymb)).to((xm, ymt)).to(ui.p("S")).then(up_in.reversed()).to((st, 0))
    c = Contour.of(outer, line(outer.end, inner.start), inner)
    return Drawing([c if c.area() > 0 else c.reversed()])


@glyph("uni1E9E", 0x1E9E, "uc")
def Germandbls(m: Master) -> Drawing:
    """Capital sharp s: stem, flat top, a diagonal into a lower bowl."""
    w, st, b = m.w("B"), m.cstem, m.cbar
    ym = m.cap * 0.56
    top = quad((0, 0), (st, 0), (st, m.cap - b), (w * 0.86, m.cap - b), (w * 0.86, m.cap), (0, m.cap))
    diag = placed(("c", w * 0.5, ym - b * 0.3), ("r", w * 0.86, m.cap - b * 0.5), st * m.diag)  # inside the bar
    bowl = dbowl(0, st, 0, ym, w, ym / 2 * 1.05, b, st * m.rside, m.tension, m.tension_in)
    return Drawing([top, diag] + bowl)
