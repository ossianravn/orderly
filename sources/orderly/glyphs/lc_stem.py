"""Lowercase stems: i j l t f k. One hook serves t f j (and g); one dot serves i j and the punctuation."""

from __future__ import annotations

from ..diag import branch, hwidth, stroke
from ..master import Master
from ..parts import box, disc, mirror_x, mirror_y
from ..shapes import lc_hook
from . import Drawing, glyph


def dot_d(m: Master) -> float:
    return m.stem * m.dot


def i_dot(m: Master, cx: float) -> list:
    """The dot of i and j: a circle slightly heavier than the stem, its top a little under the ascender."""
    d = dot_d(m)
    return [disc(cx, m.asc - m.g("dot.drop") - d / 2, d, m.tension)]


@glyph("i", 0x69, "lc")
def i(m: Master) -> Drawing:
    return Drawing([box(0, 0, m.stem, m.xh)] + i_dot(m, m.stem / 2))


@glyph("l", 0x6C, "lc")
def l_(m: Master) -> Drawing:
    return Drawing([box(0, 0, m.stem, m.asc)])


@glyph("j", 0x6A, "lc")
def j(m: Master) -> Drawing:
    rx = m.stem * m.g("j.rx")
    bot = m.desc - m.os(-m.desc)
    tail = lc_hook(m, 0, m.xh, bot, rx, rx * m.g("hook.ry"), m.g("hook.ap"))
    axis = rx / 2
    return Drawing(mirror_x([tail], axis) + i_dot(m, 2 * axis - m.stem / 2))


@glyph("t", 0x74, "lc")
def t(m: Master) -> Drawing:
    """Flat-cut top, crossbar whose top is the x-height, hook to the right."""
    x0 = m.stem * m.g("t.left")
    rx = m.stem * m.g("t.rx")
    top = m.xh + (m.asc - m.xh) * m.g("t.top")
    stem = lc_hook(m, x0, top, -m.os(m.xh), rx, rx * m.g("hook.ry"), m.g("hook.ap"))
    bar = box(0, m.xh - m.bar, x0 + m.stem + m.stem * m.g("t.right"), m.xh)
    return Drawing([stem, bar])


@glyph("f", 0x66, "lc")
def f(m: Master) -> Drawing:
    """The t's hook turned over: stem from the baseline, hook at the ascender, crossbar at the x-height."""
    x0 = m.stem * m.g("t.left")
    rx = m.stem * m.g("f.rx")
    top = m.asc + m.os(m.asc)
    stem = mirror_y([lc_hook(m, x0, top, 0, rx, rx * m.g("hook.ry"), m.g("hook.ap"))], top / 2)
    bar = box(0, m.xh - m.bar, x0 + m.stem + m.stem * m.g("t.right"), m.xh)
    return Drawing(stem + [bar])


def kay(m: Master, w: float, h: float, st: float, top: float, join: float) -> list:
    """Stem, arm and leg of k K. The arm runs from the stem up to height h; the leg leaves the arm, not the
    stem, so neither join clots. Both thin toward their joins."""
    t = st * m.diag
    thin = m.diag_thin
    y0 = h * join
    top_w = hwidth((st, y0), (w, h), t)
    c1 = (w - m.g("k.armin") * st - top_w / 2, h)
    c0 = (st, y0)
    arm = branch(c0, c1, t * thin, t, st * 0.45)
    f_ = m.g("k.leg")
    l1 = (c0[0] + (c1[0] - c0[0]) * f_, c0[1] + (c1[1] - c0[1]) * f_)
    bot_w = hwidth(l1, (w, 0), t)
    leg = stroke((w - bot_w / 2, 0), l1, t, t * thin)
    return [box(0, 0, st, top), arm, leg]


@glyph("k", 0x6B, "lc")
def k(m: Master) -> Drawing:
    return Drawing(kay(m, m.w("k"), m.xh, m.stem, m.asc, m.g("k.join")))
