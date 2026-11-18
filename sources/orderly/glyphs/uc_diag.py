"""Capital diagonals: A V W M N X Y Z. Flat apexes with a small overshoot; strokes thin toward the apex."""

from __future__ import annotations

from ..diag import Edges, centre, edges, peak_poly, placed, vee_poly, x_at
from ..master import Master
from ..parts import box
from . import Drawing, glyph
from .lc_diag import double, vee, zed


def _t(m: Master) -> float:
    return m.cstem * m.diag


@glyph("A", 0x41, "uc")
def A(m: Master) -> Drawing:
    w = m.w("A")
    t, thin = _t(m), _t(m) * m.diag_thin
    a = m.cstem * m.apex
    yt = m.cap + m.osa(m.cap)
    lb, lt = centre(("l", 0, 0), ("l", w / 2 - a / 2, yt), t, thin)
    rb, rt = centre(("r", w, 0), ("r", w / 2 + a / 2, yt), t, thin)
    y1 = m.cap * m.g("A.bar")
    y0 = y1 - m.cbar
    ym = (y0 + y1) / 2
    bar = box(x_at(lb, lt, ym), y0, x_at(rb, rt, ym), y1)
    return Drawing([peak_poly(Edges.of(lb, lt, t, thin), Edges.of(rb, rt, t, thin)), bar])


@glyph("V", 0x56, "uc")
def V(m: Master) -> Drawing:
    w = m.w("V")
    return Drawing([vee_poly(*vee(m, 0, w, w / 2, m.cap, -m.osa(m.cap), _t(m), apex=m.cstem * m.apex))])


@glyph("W", 0x57, "uc")
def W(m: Master) -> Drawing:
    t = _t(m) * m.g("w.weight")
    return Drawing([double(m, m.w("W"), m.cap, t, m.g("W.apex"), m.cstem * m.apex)])


@glyph("M", 0x4D, "uc")
def M(m: Master) -> Drawing:
    """Vertical stems; the diagonals leave their tops and meet in a flat apex on the baseline."""
    w = m.w("M")
    st = m.cstem * m.g("M.stem")
    t = _t(m) * m.g("M.weight")
    thin = t * m.diag_thin
    a = m.cstem * m.apex
    yb = -m.osa(m.cap)
    # thin at both ends: at the foot into the apex, at the head where each runs alongside a stem
    left = edges(("l", w / 2 - a / 2, yb), ("l", 0, m.cap), thin, thin)
    right = edges(("r", w / 2 + a / 2, yb), ("r", w, m.cap), thin, thin)
    return Drawing([box(0, 0, st, m.cap), box(w - st, 0, w, m.cap), vee_poly(left, right)])


@glyph("N", 0x4E, "uc")
def N(m: Master) -> Drawing:
    w = m.w("N")
    st = m.cstem * m.g("N.stem")
    t = _t(m) * m.g("N.weight")
    thin = t * m.diag_thin
    return Drawing([
        box(0, 0, st, m.cap),
        box(w - st, 0, w, m.cap),
        placed(("r", w, 0), ("l", 0, m.cap), thin, thin),
    ])


@glyph("X", 0x58, "uc")
def X(m: Master) -> Drawing:
    w = m.w("X")
    t = _t(m) * m.g("x.weight")
    inset = w * m.g("x.top")
    return Drawing([
        placed(("r", w, 0), ("l", inset, m.cap), t),
        placed(("l", 0, 0), ("r", w - inset, m.cap), t),
    ])


@glyph("Y", 0x59, "uc")
def Y(m: Master) -> Drawing:
    """A V whose flat apex is exactly the top of a centred stem."""
    w, st = m.w("Y"), m.cstem
    yj = m.cap * m.g("Y.join")
    arms = vee_poly(*vee(m, 0, w, w / 2, m.cap, yj, _t(m), apex=st))
    return Drawing([box((w - st) / 2, 0, (w + st) / 2, yj + st * 0.25), arms])


@glyph("Z", 0x5A, "uc")
def Z(m: Master) -> Drawing:
    return Drawing(zed(m.w("Z"), m.cap, m.cbar, _t(m) * m.g("z.weight"), m.w("Z") * m.g("z.top")))
