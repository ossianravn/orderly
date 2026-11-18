"""Capital straights: I E F L T J U. Stems and arms are single contours; arms use the capital bar weight."""

from __future__ import annotations

from ..geom import Contour, line, quad, tcurve
from ..master import Master
from ..parts import box, mirror_x
from ..shapes import lc_hook
from . import Drawing, glyph


@glyph("I", 0x49, "uc")
def I(m: Master) -> Drawing:
    return Drawing([box(0, 0, m.cstem, m.cap)])


def _arm_y(m: Master) -> tuple[float, float]:
    yc = m.cap * m.ubar
    return yc - m.cbar / 2, yc + m.cbar / 2


@glyph("E", 0x45, "uc")
def E(m: Master) -> Drawing:
    w, st, b = m.w("E"), m.cstem, m.cbar
    wt, wm = w * m.g("E.top"), w * m.g("E.mid")
    y0, y1 = _arm_y(m)
    return Drawing([quad((0, 0), (w, 0), (w, b), (st, b), (st, y0), (wm, y0), (wm, y1), (st, y1), (st, m.cap - b),
                         (wt, m.cap - b), (wt, m.cap), (0, m.cap))])


@glyph("F", 0x46, "uc")
def F(m: Master) -> Drawing:
    w, st, b = m.w("F"), m.cstem, m.cbar
    wm = w * m.g("F.mid")
    y0, y1 = _arm_y(m)
    y0, y1 = y0 - m.g("F.drop") * m.cap, y1 - m.g("F.drop") * m.cap
    return Drawing([quad((0, 0), (st, 0), (st, y0), (wm, y0), (wm, y1), (st, y1), (st, m.cap - b), (w, m.cap - b),
                         (w, m.cap), (0, m.cap))])


@glyph("L", 0x4C, "uc")
def L(m: Master) -> Drawing:
    w, st, b = m.w("L"), m.cstem, m.cbar
    return Drawing([quad((0, 0), (w, 0), (w, b), (st, b), (st, m.cap), (0, m.cap))])


@glyph("T", 0x54, "uc")
def T(m: Master) -> Drawing:
    w, st, b = m.w("T"), m.cstem, m.cbar
    xs = (w - st) / 2
    return Drawing([quad((xs, 0), (xs + st, 0), (xs + st, m.cap - b), (w, m.cap - b), (w, m.cap), (0, m.cap),
                         (0, m.cap - b), (xs, m.cap - b))])


@glyph("J", 0x4A, "uc")
def J(m: Master) -> Drawing:
    """Sits on the baseline: a stem turning left into the hook of j, cut vertically."""
    w = m.w("J")
    rx = w * m.g("J.rx")
    hk = lc_hook(m, 0, m.cap, -m.os(m.cap), rx, rx * m.g("J.ry"), m.g("hook.ap"), st=m.cstem, th=m.cbar * m.rtop)
    return Drawing(mirror_x([hk], w / 2))


@glyph("U", 0x55, "uc")
def U(m: Master) -> Drawing:
    """Two stems joined by the lower half of a round."""
    w, st = m.w("U"), m.cstem
    rx = w / 2
    ry = rx * m.g("U.round")
    bot = -m.os(m.cap)
    cy = bot + ry
    th = m.cbar * m.rtop
    t, ti = m.tension, m.tension_in
    outer = line((0, m.cap), (0, cy))
    outer.add(tcurve((0, cy), (0, -1), (rx, bot), (1, 0), t))
    outer.add(tcurve((rx, bot), (1, 0), (w, cy), (0, 1), t))
    outer.to((w, m.cap)).to((w - st, m.cap)).to((w - st, cy))
    outer.add(tcurve((w - st, cy), (0, -1), (rx, bot + th), (-1, 0), ti))
    outer.add(tcurve((rx, bot + th), (-1, 0), (st, cy), (0, 1), ti))
    outer.to((st, m.cap))
    return Drawing([Contour.of(outer)])

