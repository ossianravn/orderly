"""Basic punctuation: . , : ; ! ? - ' " ( ) / &. Dots are circles from the compass, a little heavier than the stem."""

from __future__ import annotations

import math

from ..diag import hwidth, placed, stroke
from ..geom import Contour, line, tcurve
from ..master import Master
from ..parts import Ell, box, disc, ring
from ..strokes import offsets
from . import Drawing, glyph
from .figures import term_x


def dot_d(m: Master) -> float:
    return m.stem * m.dot


def low_dot(m: Master, cx: float) -> Contour:
    d = dot_d(m)
    return disc(cx, d / 2 - m.os(d), d, m.tension)


def high_dot(m: Master, cx: float) -> Contour:
    d = dot_d(m)
    return disc(cx, m.xh - d / 2 + m.os(d), d, m.tension)


def comma_tail(m: Master, cx: float, cy: float) -> Contour:
    """Tail of the comma: leaves the dot's lower right going down, bends gently left, cut horizontally."""
    d = dot_d(m)
    p0 = (cx + d * m.g("comma.x0"), cy)
    a = math.radians(m.g("comma.angle"))
    p1 = (cx - d * m.g("comma.x1"), cy - d * m.g("comma.len"))
    left, right = offsets([(p0, (0.0, -1.0), d * m.g("comma.w")), (p1, (-math.sin(a), -math.cos(a)), d * m.g("comma.thin"))],
                          [(0.5, 0.5)])
    yc = p1[1] + d * m.g("comma.thin") * 0.5
    left, right = left.cut_y(yc, "head", -1), right.cut_y(yc, "head", -1)
    c = Contour.of(left, line(left.end, right.end), right.reversed())
    return c if c.area() > 0 else c.reversed()


@glyph("period", 0x2E, "pun")
def period(m: Master) -> Drawing:
    return Drawing([low_dot(m, 0)])


@glyph("comma", 0x2C, "pun")
def comma(m: Master) -> Drawing:
    d = dot_d(m)
    return Drawing([low_dot(m, 0), comma_tail(m, 0, d / 2 - m.os(d))])


@glyph("colon", 0x3A, "pun")
def colon(m: Master) -> Drawing:
    return Drawing([low_dot(m, 0), high_dot(m, 0)])


@glyph("semicolon", 0x3B, "pun")
def semicolon(m: Master) -> Drawing:
    d = dot_d(m)
    return Drawing([low_dot(m, 0), comma_tail(m, 0, d / 2 - m.os(d)), high_dot(m, 0)])


@glyph("exclam", 0x21, "pun")
def exclam(m: Master) -> Drawing:
    d = dot_d(m)
    st = m.stem * m.g("excl.w")
    return Drawing([box(-st / 2, d * m.g("excl.gap") + d, st / 2, m.cap), low_dot(m, 0)])


@glyph("question", 0x3F, "pun")
def question(m: Master) -> Drawing:
    """The 2's round, carried down on its right into a short centred stem, over the dot."""
    w = m.w("question")
    k = m.g("q.w")  # the hook is drawn a little lighter than the stem in heavy weights
    st, side, th = m.stem * k, m.stem * m.rside * k, m.bar * m.rtop * k
    d = dot_d(m)
    rx = w / 2
    top = m.cap + m.os(m.cap)
    ry = rx * m.g("q.ry")
    eo = Ell(rx, top - ry, rx, ry, m.tension)
    ei = eo.inset(side, th, m.tension_in)
    xt = term_x(ei, m.g("fig.ap"), -1)
    yv = m.cap * m.g("q.stem")
    ys = d * m.g("excl.gap") + d
    cx = w * m.g("q.x")
    o = eo.arc("W", "N", "E").cut_x(xt, "tail", 0)
    i = ei.arc("W", "N", "E").cut_x(xt, "tail", 0)
    # the neck: from the round's east side down to the stem, offset square to its own direction
    e_mid = ((eo.p("E")[0] + ei.p("E")[0]) / 2, eo.cy)
    mid = ((e_mid[0] + cx) / 2, (eo.cy + yv) / 2)
    a = math.atan2(yv - eo.cy, cx - e_mid[0])
    nodes = [(e_mid, (0.0, -1.0), side), (mid, (math.cos(a), math.sin(a)), st * m.g("q.neck")), ((cx, yv), (0.0, -1.0), st)]
    nl, nr = offsets(nodes, [(0.6, 0.6), (0.6, 0.6)])
    o.then(nl).to((cx + st / 2, ys))  # travelling down, the left of travel is the outer (east) side
    i.then(nr).to((cx - st / 2, ys))
    c = Contour.of(o, i.reversed())
    return Drawing([c if c.area() > 0 else c.reversed(), low_dot(m, cx)])


@glyph("hyphen", 0x2D, "pun")
def hyphen(m: Master) -> Drawing:
    w = m.w("hyphen")
    yc = m.xh * m.g("hyphen.y")
    return Drawing([box(0, yc - m.bar / 2, w, yc + m.bar / 2)])


def _quote(m: Master, x: float) -> Contour:
    st = m.stem * m.g("quote.w")
    return box(x, m.cap - m.cap * m.g("quote.len"), x + st, m.cap)


@glyph("quotesingle", 0x27, "pun")
def quotesingle(m: Master) -> Drawing:
    return Drawing([_quote(m, 0)])


@glyph("quotedbl", 0x22, "pun")
def quotedbl(m: Master) -> Drawing:
    st = m.stem * m.g("quote.w")
    return Drawing([_quote(m, 0), _quote(m, st * (1 + m.g("quote.gap")))])


def _paren(m: Master) -> Contour:
    """Left parenthesis: the west side of a tall round, cut horizontally, thinning toward its ends."""
    y0, y1 = m.desc * m.g("paren.low"), m.asc + m.g("paren.high")
    cy = (y0 + y1) / 2
    ry = (y1 - y0) / 2 * m.g("paren.ry")
    rx = m.w("paren")
    eo = Ell(rx, cy, rx, ry, m.tension)
    ei = Ell(rx, cy, rx - m.stem * m.g("paren.w"), ry, m.tension_in)
    o = eo.arc("N", "W", "S").cut_y(y1, "tail", 0).cut_y(y0, "head", -1)
    i = ei.arc("N", "W", "S").cut_y(y1, "tail", 0).cut_y(y0, "head", -1)
    return Contour.of(o, line(o.end, i.end), i.reversed())


@glyph("parenleft", 0x28, "pun")
def parenleft(m: Master) -> Drawing:
    return Drawing([_paren(m)])


@glyph("parenright", 0x29, "pun")
def parenright(m: Master) -> Drawing:
    from ..parts import mirror_x

    return Drawing(mirror_x([_paren(m)], 0))


@glyph("slash", 0x2F, "pun")
def slash(m: Master) -> Drawing:
    w = m.w("slash")
    t = m.stem * m.diag * m.g("slash.w")
    return Drawing([placed(("l", 0, m.desc * m.g("slash.low")), ("r", w, m.cap + m.g("slash.high")), t)])


@glyph("ampersand", 0x26, "uc")
def ampersand(m: Master) -> Drawing:
    """A small loop; from its lower right a larger bowl runs down the left, round the bottom and up the right to a
    vertical cut; a straight leg runs from the loop's left side to the baseline at the bottom right."""
    w = m.w("ampersand")
    st, b = m.cstem * m.fig * m.g("amp.w"), m.cbar * m.fig * m.g("amp.w")
    side, th = st * m.rside, b * m.rtop
    t, ti = m.tension, m.tension_in
    os = m.os(m.cap)
    ru = m.cap * m.g("amp.loop")
    uo = Ell(w * m.g("amp.loopx"), m.cap + os - ru, ru * m.g("amp.loopw"), ru, t)
    lk = m.g("amp.loopk")  # the small loop is drawn lighter in heavy weights so its counter stays open
    us, uth = side * 0.92 * lk, th * lk
    ui = uo.inset(us, uth, ti)
    um = uo.inset(us / 2, uth / 2, t)  # the loop's skeleton
    hb = m.cap * m.g("amp.bowl")
    lo = Ell(w * m.g("amp.bowlx"), (hb - os) / 2, w * m.g("amp.bowlw") / 2, (hb + os) / 2, t)
    q = um.arc("E", "S")
    pj, dj = q.at(q.crossings(0, um.cx + um.rx * m.g("amp.leave"))[0])
    wj = (us + uth) / 2 * 0.9
    nodes = [
        (pj, dj, wj),
        ((lo.cx - lo.rx + side / 2, lo.cy), (0.0, -1.0), side),
        ((lo.cx, -os + th / 2), (1.0, 0.0), th),
        ((lo.cx + lo.rx - side / 2, lo.cy), (0.0, 1.0), side),
        ((lo.cx, hb + os - th / 2), (-1.0, 0.0), th),
    ]
    left, right = offsets(nodes, [(0.55, 0.6), (t, t), (t, t), (t, t)], ti / t)
    xt = lo.cx + (lo.rx - side) * math.cos(math.radians(m.g("amp.ap")))
    left, right = left.cut_x(xt, "head", -1), right.cut_x(xt, "head", -1)
    bowl = Contour.of(left, line(left.end, right.end), right.reversed())
    bowl = bowl if bowl.area() > 0 else bowl.reversed()
    top_c = um.p("W")
    tl = st * m.diag
    t_top = side * 0.85 * cap_ratio(top_c, (w, 0))
    bot_c = (w - hwidth(top_c, (w, 0), tl) / 2, 0)
    leg = stroke(bot_c, top_c, tl, t_top)
    return Drawing(ring(uo, ui) + [bowl, leg])


def cap_ratio(p0, p1) -> float:
    """Weight square to a stroke along p0-p1 per unit of horizontal width."""
    return abs(p1[1] - p0[1]) / math.hypot(p1[0] - p0[0], p1[1] - p0[1])
