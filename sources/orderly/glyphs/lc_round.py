"""Lowercase rounds: c e s, and the bowl family b d p q a g. All come from the o's round."""

from __future__ import annotations

import math

from ..geom import Contour, line
from ..master import Master
from ..parts import box, mirror_x
from ..rounds import cut_round
from ..shapes import arch_top, lc_bowl, lc_hook, lc_round
from ..strokes import SSpec, s_curve
from . import Drawing, glyph


@glyph("c", 0x63, "lc")
def c(m: Master) -> Drawing:
    eo, ei = lc_round(m)
    x = ei.cx + ei.rx * math.cos(math.radians(m.ap_c))
    return Drawing([cut_round(eo, ei, x, x)])


@glyph("e", 0x65, "lc")
def e(m: Master) -> Drawing:
    eo, ei = lc_round(m)
    # the bar is placed by its lower edge, always below the round's east extreme, so every master has the same
    # points: the bar's lower edge meets the round on the same quadrant
    y0 = eo.cy - m.xh * m.g("e.drop")
    y1 = y0 + m.bar
    x = ei.cx + ei.rx * math.cos(math.radians(m.ap_c))
    outer = eo.arc("S", "E", "N", "W", "S", "E")
    o = outer.piece(outer.crossings(1, y0)[0], outer.crossings(0, x)[-1])
    inner = ei.arc("S", "E", "N", "W", "S", "E")
    i = inner.piece(inner.crossings(1, y0)[1], inner.crossings(0, x)[-1])
    body = Contour.of(o, line(o.end, i.end), i.reversed())
    eye_path = ei.arc("S", "W", "N", "E", "S")
    ey = eye_path.crossings(1, y1)
    return Drawing([body, Contour.of(eye_path.piece(ey[0], ey[1]))])


def s_spec(m: Master, x0: float = 0.0) -> SSpec:
    return SSpec(
        x0=x0, w=m.w("s"), bot=-m.os(m.xh), top=m.xh + m.os(m.xh), ym=m.xh * m.g("s.mid"), upper=m.g("s.upper"),
        th=arch_top(m) * m.g("s.thin"), side=m.stem * m.rside * m.g("s.thin"), spine=m.stem * m.g("s.spinew"),
        steep=m.g("s.steep"), ap=m.g("s.ap"), t=m.tension, t_in=m.tension_in, k=m.g("s.k"), tilt=m.g("s.tilt"), lean=m.g("s.lean") * m.w("s"),
    )


@glyph("s", 0x73, "lc")
def s(m: Master) -> Drawing:
    return Drawing([s_curve(s_spec(m))])


def _bowled(m: Master, y0: float, y1: float, flip: bool, width: float | None = None) -> list[Contour]:
    """A stem from y0 to y1 with the bowl on its right; flipped, the stem is on the right (d q a)."""
    bowl, xe = lc_bowl(m, 0, width)
    parts = [box(0, y0, m.stem, y1), bowl]
    return mirror_x(parts, xe / 2) if flip else parts


@glyph("b", 0x62, "lc")
def b(m: Master) -> Drawing:
    return Drawing(_bowled(m, 0, m.asc, False))


@glyph("d", 0x64, "lc")
def d(m: Master) -> Drawing:
    return Drawing(_bowled(m, 0, m.asc, True))


@glyph("p", 0x70, "lc")
def p(m: Master) -> Drawing:
    return Drawing(_bowled(m, m.desc, m.xh, False))


@glyph("q", 0x71, "lc")
def q(m: Master) -> Drawing:
    return Drawing(_bowled(m, m.desc, m.xh, True))


@glyph("a", 0x61, "lc")
def a(m: Master) -> Drawing:
    return Drawing(_bowled(m, 0, m.xh, True, m.w("a")))


@glyph("g", 0x67, "lc")
def g(m: Master) -> Drawing:
    bowl, xe = lc_bowl(m, 0)
    bot = m.desc - m.os(-m.desc)
    tail = lc_hook(m, 0, m.xh, bot, rx=xe * 0.5, ry=(xe * 0.5) * 0.72, ap=m.g("hook.ap"))
    return Drawing(mirror_x([bowl, tail], xe / 2))
