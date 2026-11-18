"""Figures built from stacked rounds: 3 5 6 8 9. 6 and 9 are one drawing turned half round."""

from __future__ import annotations

import math

from ..geom import Contour, line
from ..master import Master
from ..parts import Ell, ring, rotate180
from ..rounds import join_into, meet, shoulder
from ..strokes import offsets
from . import Drawing, glyph
from .figures import fw, term_x, top_round


@glyph("three", 0x33, "uc")
def three(m: Master) -> Drawing:
    """Upper round over a wider lower round; they share a straight middle stroke cut vertically on the left."""
    st, b, side, th = fw(m)
    w = m.w("three")
    ym = m.cap * m.g("3.mid")
    ymb, ymt = ym - th / 2, ym + th / 2
    t, ti = m.tension, m.tension_in
    top = m.cap + m.os(m.cap)
    rxu = w / 2 * m.g("3.upper")
    uo = Ell(w - rxu - w * m.g("3.inset"), (top + ymb) / 2, rxu, (top - ymb) / 2, t)
    ui = uo.inset(side, th, ti)
    lo = Ell(w / 2, (ymt - m.os(m.cap)) / 2, w / 2, (ymt + m.os(m.cap)) / 2, t)
    li = lo.inset(side, th, ti)
    ap = m.g("fig.ap")
    xu, xl = term_x(ui, ap, -1), term_x(li, ap, -1)
    xm = w * m.g("3.waist")
    lo_path = lo.arc("W", "S", "E", "N").cut_x(xl, "tail", 0)
    uo_path = uo.arc("S", "E", "N", "W").cut_x(xu, "head", -1)
    ia, ib, _ = meet(lo_path, uo_path)[-1]
    outer = lo_path.piece(None, ia).then(uo_path.piece(ib, None))
    up_in = ui.arc("W", "N", "E", "S").cut_x(xu, "tail", 0).to((xm, ymt)).to((xm, ymb)).to(li.p("N"))
    lo_in = li.arc("N", "E", "S", "W").cut_x(xl, "head", -1)
    return Drawing([Contour.of(outer, up_in.then(lo_in))])


@glyph("five", 0x35, "uc")
def five(m: Master) -> Drawing:
    """A short stem under a flat top bar; the round springs from the stem with a thinned join."""
    st, b, side, th = fw(m)
    w = m.w("five")
    x0 = w * m.g("5.stem")
    s = x0 + st
    ytop = m.cap * m.g("5.bowl")
    lo = Ell(w / 2, (ytop - m.os(m.cap)) / 2, w / 2, (ytop + m.os(m.cap)) / 2, m.tension)
    li = lo.inset(side, th, m.tension_in)
    xl = term_x(li, m.g("fig.ap"), -1)
    inner = li.arc("W", "N", "E", "S", "W").cut_x(xl, "head", -1)
    inner, j = join_into(inner, s, True, th * (1 - m.join), st * 0.5, +1, m.join_turn)
    outer = shoulder(j, lo.p("N"), m.tension).then(lo.arc("N", "E", "S", "W").cut_x(xl, "head", -1))
    bowl = Contour.of(outer.reversed(), line(j.outer, j.outer_in, j.inner_in, j.inner), inner)
    ys = min(j.inner_in[1], j.outer_in[1]) - st * 0.15
    wt = w * m.g("5.top")
    flag = Contour.of(line((x0, ys), (s, ys), (s, m.cap - b), (wt, m.cap - b), (wt, m.cap), (x0, m.cap)))
    return Drawing([flag, bowl])


def _six(m: Master, w: float) -> list[Contour]:
    """6: a full round at the foot; the stem leaves the round's outer contour on its tangent and curves gently,
    at full weight, to a vertical cut near the top right."""
    st, b, side, th = fw(m)
    os = m.os(m.cap)
    hb = m.cap * m.g("6.bowl")
    bo = Ell(w / 2, (hb - os) / 2, w / 2, (hb + os) / 2, m.tension)
    bi = bo.inset(side, th, m.tension_in)
    quad_wn = bo.arc("W", "N")
    pos = quad_wn.crossings(0, bo.cx - bo.rx * m.g("6.leave"))[0]
    po, d0 = quad_wn.at(pos)
    w0 = side * 0.97  # a hair inside the round's stroke, so the stem never touches the counter
    n0 = (-d0[1], d0[0])
    p0 = (po[0] - n0[0] * w0 / 2, po[1] - n0[1] * w0 / 2)
    fe = math.radians(m.g("6.end"))
    de = (math.cos(fe), math.sin(fe))
    we = (side + th) / 2
    pe = (w * m.g("6.endx"), m.cap + os - math.cos(fe) * we / 2)
    left, right = offsets([(p0, d0, w0), (pe, de, we)], [(m.g("6.t0"), m.g("6.t1"))])
    xc = pe[0] - math.sin(fe) * we / 2 - 1
    left, right = left.cut_x(xc, "head", -1), right.cut_x(xc, "head", -1)
    stem = Contour.of(left, line(left.end, right.end), right.reversed())
    return ring(bo, bi) + [stem if stem.area() > 0 else stem.reversed()]


@glyph("six", 0x36, "uc")
def six(m: Master) -> Drawing:
    return Drawing(_six(m, m.w("six")))


@glyph("nine", 0x39, "uc")
def nine(m: Master) -> Drawing:
    w = m.w("nine")
    return Drawing(rotate180(_six(m, w), w / 2, m.cap / 2))


@glyph("eight", 0x38, "uc")
def eight(m: Master) -> Drawing:
    """Two rounds, the upper narrower; their outlines cross at the waist, their counters stay apart."""
    st, b, side, th = fw(m)
    w = m.w("eight")
    os = m.os(m.cap)
    t, ti = m.tension, m.tension_in
    ym = m.cap * m.g("8.mid")
    waist = b * m.g("8.waist")
    y_ln = ym - waist / 2 + th
    y_us = ym + waist / 2 - th
    rxu = w / 2 * m.g("8.upper")
    uo = Ell(w / 2, (m.cap + os + y_us) / 2, rxu, (m.cap + os - y_us) / 2, t)
    lo = Ell(w / 2, (y_ln - os) / 2, w / 2, (y_ln + os) / 2, t)
    up = uo.arc("S", "E", "N", "W", "S")
    low = lo.arc("N", "W", "S", "E", "N")
    hits = meet(up, low)
    (ra, rb, _), (la, lb, _) = hits[0], hits[-1]
    outer = up.piece(ra, la).then(low.piece(lb, rb))
    return Drawing([Contour.of(outer), ring(uo, uo.inset(side, th, ti))[1], ring(lo, lo.inset(side, th, ti))[1]])
