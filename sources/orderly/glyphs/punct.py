"""Basic punctuation: . , : ; ! ? - ' " ( ) / &. Dots are circles from the compass, a little heavier than the stem."""

from __future__ import annotations

import math

from ..diag import hwidth, placed, stroke
from ..geom import Contour, line, tcurve
from ..master import Master
from ..parts import Ell, box, disc, ring
from ..rounds import cut_round
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
    """Tail of the comma: leaves the dot's lower right and runs down-left, cut horizontally."""
    d = dot_d(m)
    top = (cx + d * m.g("comma.x0"), cy)
    bot = (cx - d * m.g("comma.x1"), cy - d * m.g("comma.len"))
    return stroke(bot, top, d * m.g("comma.thin"), d * m.g("comma.w"))


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
    st, side, th = m.stem, m.stem * m.rside, m.bar * m.rtop
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
    o.add(tcurve(eo.p("E"), (0, -1), (cx + st / 2, yv), (0, -1), m.tension)).to((cx + st / 2, ys))
    i = ei.arc("W", "N", "E").cut_x(xt, "tail", 0)
    i.add(tcurve(ei.p("E"), (0, -1), (cx - st / 2, yv), (0, -1), m.tension_in)).to((cx - st / 2, ys))
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
    """A small loop over a round opened to the right; a straight leg runs from the waist to the baseline."""
    w = m.w("ampersand")
    st, b = m.cstem * m.fig, m.cbar * m.fig
    side, th = st * m.rside, b * m.rtop
    t, ti = m.tension, m.tension_in
    top = m.cap + m.os(m.cap)
    ru = m.cap * m.g("amp.loop")
    uo = Ell(w * m.g("amp.loopx"), top - ru, ru * m.g("amp.loopw"), ru, t)
    ui = uo.inset(side * 0.92, th, ti)
    y_ln = uo.p("S")[1] + th - 2  # the round's top runs inside the loop's foot
    rl = w * m.g("amp.bowlw") / 2
    lo = Ell(uo.cx + w * m.g("amp.bowlx"), (y_ln - m.os(m.cap)) / 2, rl, (y_ln + m.os(m.cap)) / 2, t)
    li = lo.inset(side, th, ti)
    x_up = term_x(li, m.g("amp.ap"), 1)
    x_lo = lo.cx + li.rx * 0.5
    bowl = cut_round(lo, li, x_up, x_lo)
    a = math.radians(m.g("amp.legx"))
    top_c = (uo.cx + (uo.rx - side / 2) * math.cos(a), uo.cy + (uo.ry - th / 2) * math.sin(a))
    tl = st * m.diag
    bot_c = (w - hwidth(top_c, (w, 0), tl) / 2, 0)
    leg = stroke(bot_c, top_c, tl, tl * m.g("amp.legtop"))
    return Drawing(ring(uo, ui) + [bowl, leg])
