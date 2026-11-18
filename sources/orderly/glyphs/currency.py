"""Currency: ¢ £ ¥ € ƒ ¤ ₺ ₽ ₹. Built from the letters they come from (c, the f's hook, Y, C, P) with the
figures' weights; added strokes are bars of the bar weight or the dollar's thin vertical."""

from __future__ import annotations

import math
from dataclasses import replace
from types import MappingProxyType

from ..diag import placed
from ..geom import Contour, line, quad
from ..master import Master
from ..parts import Ell, box, half_round, mirror_x, mirror_y, ring
from ..rounds import cut_round
from ..shapes import lc_hook, lc_round, uc_round
from . import Drawing, glyph
from .figures import fw
from .letters_extra import slash_bar
from .uc_bowl import P
from .uc_diag import Y


def with_params(m: Master, **kv) -> Master:
    return replace(m, params=MappingProxyType({**m.params, **kv}))


def thin_bar(m: Master) -> float:
    """The vertical of $ and ¢: lighter than a stem, so the letter it crosses stays the main shape."""
    return m.stem * 0.84


@glyph("cent", 0xA2, "uc")
def cent(m: Master) -> Drawing:
    eo, ei = lc_round(m)
    x = ei.cx + ei.rx * math.cos(math.radians(m.ap_c))
    v = m.stem * m.g("cent.v")  # lighter in Black, where the c's counter is small
    return Drawing([cut_round(eo, ei, x, x), box(eo.cx - v / 2, -m.xh * 0.16, eo.cx + v / 2, m.xh * 1.16)])


@glyph("sterling", 0xA3, "uc")
def sterling(m: Master) -> Drawing:
    """A stem rising into the hook of f, a crossbar, and a flat foot."""
    st, b, side, th = fw(m)
    w = m.w("two") * 1.04
    x0 = w * 0.16
    top = m.cap + m.os(m.cap)
    rx = (w - x0) * 0.5
    hook = mirror_y([lc_hook(m, x0, top, 0, rx, rx * m.g("hook.ry"), 90 - m.ap_C, st=st, th=th)], top / 2)
    yb = m.cap * 0.44
    bar = box(0, yb - b / 2, x0 + st + w * 0.36, yb + b / 2)
    return Drawing(hook + [bar, box(x0, 0, w, b)])


@glyph("yen", 0xA5, "uc")
def yen(m: Master) -> Drawing:
    mm = with_params(m, **{"Y.join": 0.5})
    cs = Y(mm).contours
    w, b = m.w("Y"), m.cbar * 0.86
    bars = [box(w * 0.17, y - b / 2, w * 0.83, y + b / 2) for y in (m.cap * 0.34, m.cap * 0.14)]
    return Drawing(cs + bars)


@glyph("Euro", 0x20AC, "uc")
def euro(m: Master) -> Drawing:
    """C's round, narrower, crossed on the left by two bars."""
    st, b, side, th = fw(m)
    w = m.w("C") * 0.84
    eo, ei = uc_round(m, w)
    x = ei.cx + ei.rx * math.cos(math.radians(m.ap_C))
    bw = b * 0.86
    x0, x1 = -w * 0.1, eo.cx + eo.rx * 0.12
    bars = [box(x0, y - bw / 2, x1, y + bw / 2) for y in (m.cap * 0.39, m.cap * 0.6)]
    return Drawing([cut_round(eo, ei, x, x)] + bars)


def long_s(m: Master, st: float, th: float, y0: float, y1: float, rx: float) -> list[Contour]:
    """A stem from y0 to y1 with the f's hook at the top turning right and the j's hook at the bottom turning
    left (ƒ ∫). Both halves overlap in the middle."""
    ym = (y0 + y1) / 2
    ap = m.g("hook.ap")
    upper = mirror_y([lc_hook(m, 0, y1 - ym + st, 0, rx, rx * m.g("hook.ry"), ap, st=st, th=th)], 0)
    upper = [c.map(lambda p: (p[0], p[1] + y1)) for c in upper]
    lower = mirror_x([lc_hook(m, 0, ym + st, y0, rx, rx * m.g("hook.ry"), ap, st=st, th=th)], st / 2)
    return upper + lower


@glyph("florin", 0x192, "lc")
def florin(m: Master) -> Drawing:
    st, th = m.stem, m.bar * m.rtop
    rx = st * m.g("f.rx")
    cs = long_s(m, st, th, m.desc - m.os(-m.desc), m.asc + m.os(m.asc), rx)
    bar = box(-st * m.g("t.left") * 1.2, m.xh - m.bar, st + st * m.g("t.right") * 1.2, m.xh)
    return Drawing(cs + [bar])


@glyph("currency", 0xA4, "uc")
def currency(m: Master) -> Drawing:
    """A ring with four short diagonal spokes."""
    st, b, side, th = fw(m)
    r = m.cap * 0.27
    cy = m.cap * 0.42
    k = min(b * 0.9, r * 0.4)
    eo = Ell(0, cy, r, r, m.tension)
    out = ring(eo, eo.inset(k, k, m.tension_in))
    t, r0, r1 = b * 0.9, r - k / 2, r * 1.4
    for a in (45, 135, 225, 315):  # spokes cut square, so all four read alike
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        out.append(quad(*[(c * u - s * v, cy + s * u + c * v) for u, v in ((r0, -t / 2), (r1, -t / 2), (r1, t / 2),
                                                                          (r0, t / 2))]))
    return Drawing(out)


@glyph("uni20BA", 0x20BA, "uc")
def lira(m: Master) -> Drawing:
    """Turkish lira: a stem turning right at the foot into a rising round, crossed by two slanted bars."""
    st, b, side, th = fw(m)
    w = m.w("L") * 1.32
    x0 = w * 0.2
    rx = (w - x0) / 2
    hk = lc_hook(m, x0, m.cap, -m.os(m.cap), rx, m.cap * 0.42, 62, st=st, th=th)
    bars = [slash_bar(x0 - st * 1.05, x0 + st * 2.3, y, m.cap * 0.1, b * 0.9) for y in (m.cap * 0.42, m.cap * 0.62)]
    return Drawing([hk] + bars)


@glyph("uni20BD", 0x20BD, "uc")
def ruble(m: Master) -> Drawing:
    """Ruble: P crossed below its bowl by a bar that runs out to the left."""
    yb = m.cap * 0.22
    b = m.cbar * 0.92
    return Drawing(P(m).contours + [box(-m.cstem * 1.0, yb - b / 2, m.w("P") * 0.62, yb + b / 2)])


@glyph("uni20B9", 0x20B9, "uc")
def rupee(m: Master) -> Drawing:
    """Indian rupee: two bars; a half round hangs from the top bar and returns to a straight leg."""
    st, b, side, th = fw(m)
    w = m.w("P") * 1.12
    yb = m.cap * 0.36  # the bowl's bottom
    xa = w * 0.1  # where the bowl's arms end on the left
    rx = (m.cap - yb) / 2 * 0.95
    xr = w * 0.86
    cx = xr - rx
    outer = line((xa, yb), (cx, yb)).then(half_round(cx, yb, m.cap, xr, m.tension)).to((xa, m.cap))
    inner = line((xa, m.cap - b), (cx, m.cap - b))
    inner.then(half_round(cx, yb + b, m.cap - b, xr - side, m.tension_in).reversed()).to((xa, yb + b))
    bowl = Contour.of(outer, inner)
    y2 = m.cap * 0.68
    leg = placed(("r", w * 0.92, 0), ("l", xa, yb + b), st * m.diag, st * m.diag * m.diag_thin)
    return Drawing([box(0, m.cap - b, w, m.cap), box(0, y2 - b / 2, w, y2 + b / 2),
                    bowl if bowl.area() > 0 else bowl.reversed(), leg])
