"""Figures, lining and proportional: 0 1 2 4 7 here; the stacked rounds 3 5 6 8 9 in figures_round.

Figures sit at the cap height with weights a little under the capitals' (the master's `fig`).
"""

from __future__ import annotations

import math

from ..diag import edges, hwidth, y_at
from ..geom import Contour, line, quad
from ..master import Master
from ..parts import Ell, ring
from ..rounds import tangent_from
from . import Drawing, glyph


def fw(m: Master) -> tuple[float, float, float, float]:
    """Figure stem, bar, round side and round top."""
    st, b = m.cstem * m.fig, m.cbar * m.fig
    return st, b, st * m.rside, b * m.rtop


@glyph("zero", 0x30, "uc")
def zero(m: Master) -> Drawing:
    """An upright ellipse, clearly narrower than O."""
    _, _, side, th = fw(m)
    w = m.w("zero")
    eo = Ell(w / 2, m.cap / 2, w / 2, m.cap / 2 + m.os(m.cap), m.tension)
    return Drawing(ring(eo, eo.inset(side, th, m.tension_in)))


@glyph("one", 0x31, "uc")
def one(m: Master) -> Drawing:
    """A stem with a flag and no foot; the flag ends in a vertical cut."""
    st, b, _, _ = fw(m)
    w = m.w("one")
    xs = w - st
    drop = m.cap * m.g("1.drop")
    a = math.atan2(drop, xs)
    voff = b * m.g("1.flagw") / math.cos(a)
    return Drawing([quad((xs, 0), (w, 0), (w, m.cap), (xs, m.cap), (0, m.cap - drop), (0, m.cap - drop - voff),
                         (xs, m.cap - voff))])


def top_round(m: Master, w: float, rx_k: float, ry_k: float) -> tuple[Ell, Ell]:
    """The upper round of 2 and 3: hangs from the cap height (with overshoot), centred in the width."""
    _, _, side, th = fw(m)
    rx = w / 2 * rx_k
    ry = rx * ry_k
    top = m.cap + m.os(m.cap)
    eo = Ell(w - rx, top - ry, rx, ry, m.tension)
    return eo, eo.inset(side, th, m.tension_in)


def term_x(ei: Ell, ap: float, side: int) -> float:
    """x of a vertical terminal cut on a counter's ellipse, ap degrees from its horizontal axis."""
    return ei.cx + side * ei.rx * math.cos(math.radians(ap))


@glyph("two", 0x32, "uc")
def two(m: Master) -> Drawing:
    """Round top with a vertical cut, a straight diagonal leaving the round on its tangent, a flat base."""
    st, b, _, _ = fw(m)
    w = m.w("two")
    eo, ei = top_round(m, w, m.g("2.rx"), m.g("2.ry"))
    xt = term_x(ei, m.g("fig.ap"), -1)
    outer = eo.arc("W", "N", "E", "S").cut_x(xt, "tail", 0)
    inner = ei.arc("W", "N", "E", "S").cut_x(xt, "tail", 0)
    t = st * m.diag * m.g("2.diag")
    ti = tangent_from(inner, (0, b))
    foot = hwidth((0, b), inner.at(ti)[0], t)  # the diagonal's foot: its weight measured along the base
    to = tangent_from(outer, (foot, b))
    # same points in every master: the diagonal must leave both edges below the round's east extreme
    assert ti[0] == len(inner.segs) - 1 and to[0] == len(outer.segs) - 1, "2: diagonal leaves the round above E"
    oi, oo = inner.piece(None, ti), outer.piece(None, to)
    c = line((0, 0), (w, 0), (w, b), (foot, b)).to(oo.end).then(oo.reversed()).to(oi.start).then(oi).to((0, b))
    return Drawing([Contour.of(c)])


@glyph("four", 0x34, "uc")
def four(m: Master) -> Drawing:
    """Closed: a diagonal from the crossbar's left end to a flat top shared with the stem."""
    st, b, _, _ = fw(m)
    w = m.w("four")
    xs = w - st - st * m.g("4.over")
    yb0 = m.cap * m.g("4.bar")
    yb1 = yb0 + b
    t = st * m.diag
    top_w = hwidth((0, yb1), (xs, m.cap), t)
    d = edges(("l", 0, yb1), ("l", xs - top_w * 0.5, m.cap), t, t * m.diag_thin)
    outer = quad((xs, 0), (xs + st, 0), (xs + st, yb0), (w, yb0), (w, yb1), (xs + st, yb1), (xs + st, m.cap),
                 d.l1, d.l0, (0, yb0), (xs, yb0))
    counter = quad(d.r0, (xs, y_at(d.r0, d.r1, xs)), (xs, yb1))
    return Drawing([outer, counter])


@glyph("seven", 0x37, "uc")
def seven(m: Master) -> Drawing:
    """Top bar and a straight diagonal cut horizontally at the baseline."""
    st, b, _, _ = fw(m)
    w = m.w("seven")
    t = st * m.diag
    xb = w * m.g("7.foot")
    wh = t
    for _ in range(8):
        wh = hwidth((xb + wh, 0), (w, m.cap), t)
    xl = xb + (w - wh - xb) * (m.cap - b) / m.cap
    return Drawing([quad((0, m.cap - b), (xl, m.cap - b), (xb, 0), (xb + wh, 0), (w, m.cap), (0, m.cap))])
