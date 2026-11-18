"""Drawn letters beyond the basic Latin: ı ȷ đ Đ Ð ð þ Þ ł Ł ŋ Ŋ ħ Ħ ŧ Ŧ ß ẞ ĸ œ Œ ʒ Ʒ ǥ Ǥ ŀ Ŀ (ß ẞ are in sharp_s.py).

Each is built from the parts of its relatives (stems, bowls, hooks, bars), so it reads as one of the family.
"""

from __future__ import annotations

import math

from ..diag import stroke
from ..geom import Contour, quad
from ..master import Master
from ..parts import Ell, box, dbowl, disc, mirror_x, ring, rotate180, shift
from ..rounds import cut_round
from ..shapes import lc_hook, lc_round, n_arch
from . import Drawing, glyph
from .control import H, O
from .lc_round import _bowled, d, e, g
from .lc_stem import f, j, kay, t
from .uc_round import D, G
from .uc_straight import E, L, T


def _xs(cs) -> tuple[float, float]:
    xs = [p[0] for c in cs for p in c.flat(6)]
    return min(xs), max(xs)


def slash_bar(xa: float, xb: float, yc: float, rise: float, t: float) -> Contour:
    """A short diagonal bar from xa to xb through height yc, cut vertically at both ends (ł Ł)."""
    v = t * math.hypot(xb - xa, rise) / (xb - xa)
    return quad((xa, yc - rise / 2 - v / 2), (xb, yc + rise / 2 - v / 2), (xb, yc + rise / 2 + v / 2),
                (xa, yc - rise / 2 + v / 2))


@glyph("dotlessi", 0x131, "lc")
def dotlessi(m: Master) -> Drawing:
    return Drawing([box(0, 0, m.stem, m.xh)])


@glyph("uni0237", 0x237, "lc")
def dotlessj(m: Master) -> Drawing:
    return Drawing(j(m).contours[:1])


@glyph("dcroat", 0x111, "lc")
def dcroat(m: Master) -> Drawing:
    cs = d(m).contours
    xr = _xs(cs)[1]
    yb = m.xh + (m.asc - m.xh) * m.g("bar.asc")
    return Drawing(cs + [box(xr - m.stem * 2.0, yb, xr + m.stem * 0.4, yb + m.bar * 0.9)])


def _d_bar(m: Master) -> list:
    cs = D(m).contours
    yc = m.cap / 2
    return cs + [box(-m.cstem * 0.45, yc - m.cbar * 0.45, m.cstem * 2.0, yc + m.cbar * 0.45)]


@glyph("Dcroat", 0x110, "uc")
def Dcroat(m: Master) -> Drawing:
    return Drawing(_d_bar(m))


@glyph("Eth", 0xD0, "uc")
def Eth(m: Master) -> Drawing:
    return Drawing(_d_bar(m))


@glyph("eth", 0xF0, "lc")
def eth(m: Master) -> Drawing:
    """The o's round with a stem rising from its upper right and bending left, crossed by a short bar."""
    from ..strokes import offsets

    eo, ei = lc_round(m)
    side, th = m.stem * m.rside, m.bar * m.rtop
    a = math.radians(m.g("eth.leave"))
    rmx, rmy = eo.rx - side / 2, eo.ry - th / 2
    p0 = (eo.cx + rmx * math.cos(a), eo.cy + rmy * math.sin(a))
    d0 = (-math.sin(a) * rmx, math.cos(a) * rmy)
    n = math.hypot(*d0)
    pe = (eo.cx - eo.rx * 0.1, m.asc - th / 2)
    left, right = offsets([(p0, (d0[0] / n, d0[1] / n), side * 0.97), (pe, (-1.0, 0.0), th)], [(0.55, 0.6)])
    xc = pe[0] + 1
    left, right = left.cut_x(xc, "head", -1), right.cut_x(xc, "head", -1)
    from ..geom import line

    st = Contour.of(left, line(left.end, right.end), right.reversed())
    yb = m.xh + (m.asc - m.xh) * 0.25
    bar = stroke((eo.cx - eo.rx * 0.35, yb - m.xh * 0.05), (eo.cx + eo.rx * 0.45, yb + m.xh * 0.12), m.bar * 0.85)
    return Drawing(ring(eo, ei) + [st if st.area() > 0 else st.reversed(), bar])


@glyph("thorn", 0xFE, "lc")
def thorn(m: Master) -> Drawing:
    return Drawing(_bowled(m, m.desc, m.asc, False))


@glyph("Thorn", 0xDE, "uc")
def Thorn(m: Master) -> Drawing:
    w, st = m.w("P"), m.cstem
    y0, y1 = m.cap * 0.2, m.cap * 0.8
    bowl = dbowl(0, st, y0, y1, w, (y1 - y0) / 2 * m.g("P.round"), m.cbar, st * m.rside, m.tension, m.tension_in)
    return Drawing([box(0, 0, st, m.cap)] + bowl)


@glyph("lslash", 0x142, "lc")
def lslash(m: Master) -> Drawing:
    yc = m.xh * 0.62
    return Drawing([box(0, 0, m.stem, m.asc), slash_bar(-m.stem * 1.1, m.stem * 2.1, yc, m.xh * 0.28, m.bar * 0.9)])


@glyph("Lslash", 0x141, "uc")
def Lslash(m: Master) -> Drawing:
    cs = L(m).contours
    yc = m.cap * 0.5
    return Drawing(cs + [slash_bar(-m.cstem * 1.1, m.cstem * 2.1, yc, m.cap * 0.2, m.cbar * 0.9)])


def _eng_hook(m: Master, xr: float, st: float, y_top: float, rx: float) -> list:
    bot = m.desc - m.os(-m.desc)
    hk = lc_hook(m, 0, y_top, bot, rx, rx * m.g("hook.ry"), m.g("hook.ap"), st=st)
    return mirror_x([hk], xr / 2)


@glyph("eng", 0x14B, "lc")
def eng(m: Master) -> Drawing:
    w = m.w("n")
    c, _ = n_arch(m, 0, w)
    return Drawing([box(0, 0, m.stem, m.xh), c] + _eng_hook(m, w, m.stem, m.xh * 0.4, m.stem * m.g("j.rx")))


@glyph("Eng", 0x14A, "uc")
def Eng(m: Master) -> Drawing:
    from .uc_straight import U

    w = m.w("U")
    cs = rotate180(U(m).contours, w / 2, m.cap / 2)
    return Drawing(cs + _eng_hook(m, w, m.cstem, m.cap * 0.3, m.cstem * m.g("j.rx")))


@glyph("hbar", 0x127, "lc")
def hbar(m: Master) -> Drawing:
    from .lc_arch import h

    yb = m.xh + (m.asc - m.xh) * m.g("bar.asc")
    return Drawing(h(m).contours + [box(-m.stem * 0.45, yb, m.stem * 1.9, yb + m.bar * 0.9)])


@glyph("Hbar", 0x126, "uc")
def Hbar(m: Master) -> Drawing:
    w = m.w("H")
    yb = m.cap * 0.74
    return Drawing(H(m).contours + [box(-m.cstem * 0.35, yb, w + m.cstem * 0.35, yb + m.cbar * 0.85)])


@glyph("tbar", 0x167, "lc")
def tbar(m: Master) -> Drawing:
    cs = t(m).contours
    x0 = m.stem * m.g("t.left")
    yb = m.xh * 0.42
    return Drawing(cs + [box(x0 - m.stem * 0.6, yb, x0 + m.stem * 1.6, yb + m.bar * 0.9)])


@glyph("Tbar", 0x166, "uc")
def Tbar(m: Master) -> Drawing:
    w, st = m.w("T"), m.cstem
    xs = (w - st) / 2
    yb = m.cap * 0.45
    return Drawing(T(m).contours + [box(xs - st * 1.1, yb, xs + st * 2.1, yb + m.cbar * 0.9)])


@glyph("kgreenlandic", 0x138, "lc")
def kgreenlandic(m: Master) -> Drawing:
    return Drawing(kay(m, m.w("k"), m.xh, m.stem, m.xh, m.g("k.join")))


@glyph("oe", 0x153, "lc")
def oe(m: Master) -> Drawing:
    """o and e sharing a stroke: e's left side lies on o's right side."""
    left = lc_round(m)
    o_cs = ring(*left)
    e_cs = e(m).contours
    ex0, _ = _xs(e_cs)
    return Drawing(o_cs + shift(e_cs, left[0].p("E")[0] - m.stem * m.rside - ex0))


@glyph("OE", 0x152, "uc")
def OE(m: Master) -> Drawing:
    o_cs = O(m).contours
    xr = _xs(o_cs)[1]
    return Drawing(o_cs + shift(E(m).contours, xr - m.cstem * m.rside))


def _ezh(m: Master, h: float, bot: float, w: float, st: float, bar: float) -> list:
    """z's top bar and diagonal, falling into a lower round open on the left (ʒ Ʒ)."""
    ym = bot + (h - bot) * 0.48
    top = box(0, h - bar, w * 0.95, h)
    ry = (ym - bot) / 2 + bar * 0.4
    eo = Ell(w * 0.5, bot + ry, w * 0.5, ry, m.tension)
    ei = eo.inset(st * m.rside, bar * m.rtop, m.tension_in)
    x = ei.cx + ei.rx * math.cos(math.radians(m.g("fig.ap") + 20))
    bowl = mirror_x([cut_round(eo, ei, x, x)], w * 0.5)
    diag = stroke((w * 0.42, ym + bar * 0.2), (w * 0.95 - st * 0.55, h - bar * 0.5), st * m.diag)
    return [top, diag] + bowl


@glyph("ezh", 0x292, "lc")
def ezh(m: Master) -> Drawing:
    return Drawing(_ezh(m, m.xh, m.desc - m.os(-m.desc), m.w("z") * 1.05, m.stem, m.bar))


@glyph("Ezh", 0x1B7, "uc")
def Ezh(m: Master) -> Drawing:
    return Drawing(_ezh(m, m.cap, -m.os(m.cap), m.w("Z") * 0.95, m.cstem, m.cbar))


@glyph("gstroke", 0x1E5, "lc")
def gstroke(m: Master) -> Drawing:
    cs = g(m).contours
    xr = _xs(cs)[1]
    yb = m.desc * 0.42
    return Drawing(cs + [box(xr - m.stem * 2.0, yb, xr + m.stem * 0.45, yb + m.bar * 0.85)])


@glyph("Gstroke", 0x1E4, "uc")
def Gstroke(m: Master) -> Drawing:
    cs = G(m).contours
    xr = _xs(cs)[1]
    yb = m.cap * 0.18
    return Drawing(cs + [box(xr - m.cstem * 1.6, yb, xr + m.cstem * 0.45, yb + m.cbar * 0.85)])


@glyph("ldot", 0x140, "lc")
def ldot(m: Master) -> Drawing:
    dd = m.stem * m.dot
    return Drawing([box(0, 0, m.stem, m.asc), disc(m.stem + dd * 0.9, m.xh * 0.55, dd, m.tension)])


@glyph("Ldot", 0x13F, "uc")
def Ldot(m: Master) -> Drawing:
    dd = m.stem * m.dot
    return Drawing(L(m).contours + [disc(m.cstem + dd * 1.1, m.cap * 0.5, dd, m.tension)])


@glyph("IJ", 0x132, "uc")
def IJ(m: Master) -> Drawing:
    from .uc_straight import I, J

    jc = J(m).contours
    return Drawing(I(m).contours + shift(jc, m.cstem + m.cstem * 0.9 - _xs(jc)[0]))


@glyph("ij", 0x133, "lc")
def ij(m: Master) -> Drawing:
    from .lc_stem import i

    jc = j(m).contours
    xs = [p[0] for p in jc[0].flat(6) if p[1] > 0]
    return Drawing(i(m).contours + shift(jc, m.stem + m.stem * 0.85 - min(xs)))


@glyph("uni02B9", 0x2B9, "pun")
def primemod(m: Master) -> Drawing:
    return Drawing([stroke((0, m.cap * 0.66), (m.stem * 0.55, m.cap), m.stem * 0.85)])
