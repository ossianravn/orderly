"""Lowercase diagonals: v w x y z. Apexes are flat and pass their line by a small overshoot; strokes thin
toward the apex so the crotch does not clot."""

from __future__ import annotations

from ..diag import Edges, cross, double_vee, edges, hwidth, placed, vee_poly
from ..geom import Contour, quad
from ..master import Master
from . import Drawing, glyph


def vee(m: Master, xl: float, xr: float, xc: float, y_top: float, y_ap: float, t: float,
        apex: float | None = None) -> tuple[Edges, Edges]:
    """The two strokes of a V from the top corners xl and xr down to a flat apex centred at xc."""
    a = m.stem * m.apex if apex is None else apex
    thin = t * m.diag_thin
    left = edges(("l", xc - a / 2, y_ap), ("l", xl, y_top), thin, t)
    right = edges(("r", xc + a / 2, y_ap), ("r", xr, y_top), thin, t)
    return left, right


def double(m: Master, w: float, h: float, t: float, apex_x: float, apex: float) -> Contour:
    """W: outer strokes full weight at the top, all four thinning into the three apexes."""
    thin = t * m.diag_thin
    yb, yt = -m.osa(h), h + m.osa(h)
    x1, x2 = w * apex_x, w * (1 - apex_x)
    a = apex
    return double_vee(
        edges(("l", x1 - a / 2, yb), ("l", 0, h), thin, t),
        edges(("r", x1 + a / 2, yb), ("l", w / 2 - a / 2, yt), thin, thin),
        edges(("l", x2 - a / 2, yb), ("r", w / 2 + a / 2, yt), thin, thin),
        edges(("r", x2 + a / 2, yb), ("r", w, h), thin, t),
    )


@glyph("v", 0x76, "lc")
def v(m: Master) -> Drawing:
    w = m.w("v")
    return Drawing([vee_poly(*vee(m, 0, w, w / 2, m.xh, -m.osa(m.xh), m.stem * m.diag))])


@glyph("w", 0x77, "lc")
def w_(m: Master) -> Drawing:
    t = m.stem * m.diag * m.g("w.weight")
    return Drawing([double(m, m.w("w"), m.xh, t, m.g("w.apex"), m.stem * m.apex)])


@glyph("x", 0x78, "lc")
def x(m: Master) -> Drawing:
    w = m.w("x")
    t = m.stem * m.diag * m.g("x.weight")
    inset = w * m.g("x.top")
    return Drawing([
        placed(("r", w, 0), ("l", inset, m.xh), t),
        placed(("l", 0, 0), ("r", w - inset, m.xh), t),
    ])


@glyph("y", 0x79, "lc")
def y(m: Master) -> Drawing:
    """v whose right stroke runs straight on to the descender; the left arm ends inside it."""
    w, t = m.w("y"), m.stem * m.diag
    xc = w * m.g("y.apex")
    a = m.stem * m.apex
    arm = edges(("l", xc - a / 2, 0), ("l", 0, m.xh), t * m.diag_thin, t)
    bx = w + (xc + a / 2 - w) * (m.xh - m.desc) / m.xh
    tail = edges(("r", bx, m.desc), ("r", w, m.xh), t, t)
    p1 = cross(arm.l0, arm.l1, tail.l0, tail.l1)
    c = cross(arm.r0, arm.r1, tail.l0, tail.l1)
    return Drawing([quad(arm.l1, p1, tail.l0, tail.r0, tail.r1, tail.l1, c, arm.r1)])


def zed(w: float, h: float, bar: float, t: float, inset: float) -> list:
    """Z shape as one contour: top bar (inset by `inset` overall), diagonal, bottom bar."""
    xl, xr = inset / 2, w - inset / 2
    wh = t
    for _ in range(12):
        wh = hwidth((0, bar), (xr - wh, h - bar), t)
    return [quad((0, 0), (w, 0), (w, bar), (wh, bar), (xr, h - bar), (xr, h), (xl, h), (xl, h - bar),
                 (xr - wh, h - bar), (0, bar))]


@glyph("z", 0x7A, "lc")
def z(m: Master) -> Drawing:
    return Drawing(zed(m.w("z"), m.xh, m.bar, m.stem * m.diag * m.g("z.weight"), m.w("z") * m.g("z.top")))
