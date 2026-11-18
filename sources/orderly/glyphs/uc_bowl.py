"""Capital bowls: P R B, and K. A bowl is a pair of arms closed by the right half of a round."""

from __future__ import annotations

from ..diag import hwidth, stroke
from ..geom import Contour, line
from ..master import Master
from ..parts import dbowl, half_round
from ..rounds import meet
from . import Drawing, glyph
from .lc_stem import kay


def _p_bowl(m: Master, w: float, yb: float) -> list[Contour]:
    rx = (m.cap - yb) / 2 * m.g("P.round")
    return dbowl(0, m.cstem, yb, m.cap, w, rx, m.cbar, m.cstem * m.rside, m.tension, m.tension_in, ystem=0)


@glyph("P", 0x50, "uc")
def P(m: Master) -> Drawing:
    return Drawing(_p_bowl(m, m.w("P"), m.cap * m.g("P.bowl")))


@glyph("R", 0x52, "uc")
def R(m: Master) -> Drawing:
    """P's bowl with a straight leg that leaves the bowl's lower arm."""
    w = m.w("R")
    yb = m.cap * m.g("R.bowl")
    wb = w * m.g("R.bowlw")
    parts = _p_bowl(m, wb, yb)
    t = m.cstem * m.diag
    top = (wb * m.g("R.legx"), yb + m.cbar / 2)
    bw = hwidth(top, (w, 0), t)
    return Drawing(parts + [stroke((w - bw / 2, 0), top, t, t * m.diag_thin)])


@glyph("B", 0x42, "uc")
def B(m: Master) -> Drawing:
    """Two bowls, the upper narrower; their rounds meet in a crotch on the middle bar."""
    w, st, b = m.w("B"), m.cstem, m.cbar
    side = st * m.rside
    t, ti = m.tension, m.tension_in
    wu = w * m.g("B.upper")
    yc = m.cap * m.g("B.mid")
    mb = b * m.g("B.midw")
    ymb, ymt = yc - mb / 2, yc + mb / 2
    rl = ymt / 2 * m.g("B.round")
    ru = (m.cap - ymb) / 2 * m.g("B.round")
    lower = half_round(w - rl, 0, ymt, w, t)
    upper = half_round(wu - ru, ymb, m.cap, wu, t)
    ia, ib, _ = meet(lower, upper)[-1]
    outer = line((0, 0), (w - rl, 0)).then(lower.piece(None, ia)).then(upper.piece(ib, None)).to((0, m.cap))
    low_in = line((st, b), (st, ymb), (w - rl, ymb))
    low_in.then(half_round(w - rl, b, ymb, w - side, ti).reversed()).to((st, b))
    up_in = line((st, ymt), (st, m.cap - b), (wu - ru, m.cap - b))
    up_in.then(half_round(wu - ru, ymt, m.cap - b, wu - side, ti).reversed()).to((st, ymt))
    return Drawing([Contour.of(outer), Contour(low_in.segs), Contour(up_in.segs)])


@glyph("K", 0x4B, "uc")
def K(m: Master) -> Drawing:
    return Drawing(kay(m, m.w("K"), m.cap, m.cstem, m.cap, m.g("K.join")))

