"""Math letters and large operators: µ π Ω ∂ ∆ ∏ ∑ √ ∫. Each is built from the letter or figure it comes from
(u, n, O, 6, A, H, the chevron of < >, the long s of ƒ)."""

from __future__ import annotations

import math

from ..diag import Edges, centre, edges, peak_poly, vee_poly
from ..master import Master
from ..parts import Ell, box, mirror_x
from ..rounds import cut_round
from ..shapes import uc_round
from . import Drawing, glyph
from .currency import long_s
from .figures import fw
from .figures_round import _six
from .lc_arch import u
from .symbols import _chevron


@glyph("mu", 0xB5, "lc")
def mu(m: Master) -> Drawing:
    """µ: the u with its left stem run down to the descender."""
    return Drawing(u(m).contours + [box(0, m.desc, m.stem, m.xh * 0.5)])


@glyph("pi", 0x3C0, "lc")
def pi(m: Master) -> Drawing:
    w, st = m.w("n") * 1.08, m.stem
    xl, xr = w * 0.14, w * 0.66
    return Drawing([box(0, m.xh - m.bar, w, m.xh), box(xl, 0, xl + st, m.xh), box(xr, 0, xr + st, m.xh)])


@glyph("Omega", 0x2126, "uc")
def Omega(m: Master) -> Drawing:
    """Ω: the O's round opened at the foot, its ends standing on two short feet that run outward."""
    st, b = m.cstem, m.cbar
    w = m.w("O") * 0.92
    eo, ei = uc_round(m, w)
    ang = math.radians(m.g("Omega.open"))
    # the round is built opened on the right (as C) with its radii swapped, then turned a quarter clockwise
    ro, ri = Ell(0, 0, eo.ry, eo.rx, eo.t), Ell(0, 0, ei.ry, ei.rx, ei.t)
    xc = ri.rx * math.cos(ang)
    c = cut_round(ro, ri, xc, xc).map(lambda p: (eo.cx + p[1], eo.cy - p[0]))
    yc = eo.cy - xc  # height of the cut ends
    x_in = ei.rx * math.sin(ang)  # the opening's half width
    x_out = eo.rx * math.sqrt(max(0.0, 1 - (xc / eo.ry) ** 2))
    feet = []
    for s in (-1, 1):
        a, z = eo.cx + s * x_in, eo.cx + s * (x_out + st * 0.4)
        feet.append(box(min(a, z), 0, max(a, z), b))
        a, z = eo.cx + s * x_in, eo.cx + s * x_out
        feet.append(box(min(a, z), b * 0.5, max(a, z), yc + 1))
    return Drawing([c] + feet)


@glyph("partialdiff", 0x2202, "uc")
def partialdiff(m: Master) -> Drawing:
    """∂: the 6 mirrored, its stem curving back to the left."""
    w = m.w("six")
    return Drawing(mirror_x(_six(m, w), w / 2))


@glyph("uni2206", 0x2206, "uc")
def increment(m: Master) -> Drawing:
    """∆: the A's two strokes with a flat apex, standing on a bar instead of crossing one."""
    w = m.w("A") * 1.02
    t = m.cstem * m.diag
    thin = t * m.diag_thin
    a = m.cstem * m.apex
    yt = m.cap + m.osa(m.cap)
    lb, lt = centre(("l", 0, 0), ("l", w / 2 - a / 2, yt), t, thin)
    rb, rt = centre(("r", w, 0), ("r", w / 2 + a / 2, yt), t, thin)
    return Drawing([peak_poly(Edges.of(lb, lt, t, thin), Edges.of(rb, rt, t, thin)), box(0, 0, w, m.cbar)])


def _tall(m: Master) -> tuple[float, float]:
    """Large operators run from under the baseline to the cap height."""
    return -m.cap * 0.16, m.cap + m.osa(m.cap)


@glyph("product", 0x220F, "uc")
def product(m: Master) -> Drawing:
    y0, y1 = _tall(m)
    w, st, b = m.w("H") * 1.08, m.cstem, m.cbar
    xs = w * 0.08
    return Drawing([box(0, y1 - b, w, y1), box(xs, y0, xs + st, y1), box(w - xs - st, y0, w - xs, y1)])


@glyph("summation", 0x2211, "uc")
def summation(m: Master) -> Drawing:
    """∑: top and bottom bars joined by the > chevron, its arms buried in the bars."""
    y0, y1 = _tall(m)
    w, b = m.w("E") * 1.2, m.cbar
    t = m.cstem * m.diag * 0.95
    h = (y1 - y0) - b
    ch = mirror_x(_chevron(m, w * 0.6, h, (y0 + y1) / 2, t), w * 0.3)
    return Drawing([box(0, y1 - b, w, y1), box(0, y0, w, y0 + b)] + ch)


@glyph("radical", 0x221A, "uc")
def radical(m: Master) -> Drawing:
    """√: a short tick down to a flat apex on the baseline, and a long stroke up to the cap height."""
    st, b, side, th = fw(m)
    w = m.w("V") * 0.95
    t = st * m.diag
    a = st * m.apex
    xc = w * 0.36
    yb = -m.osa(m.cap)
    left = edges(("l", xc - a / 2, yb), ("l", 0, m.cap * 0.44), t * 0.82, t * 0.82)
    right = edges(("r", xc + a / 2, yb), ("r", w, m.cap + m.osa(m.cap)), t * m.diag_thin, t)
    return Drawing([vee_poly(left, right)])


@glyph("integral", 0x222B, "uc")
def integral(m: Master) -> Drawing:
    st, th = m.stem, m.bar * m.rtop
    return Drawing(long_s(m, st, th, m.desc - m.os(-m.desc), m.asc + m.os(m.asc), st * m.g("f.rx")))
