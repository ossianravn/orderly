"""Open strokes: the hook of t f j g J, and the s curve of s S (and the figures that borrow it).

Both are edge pairs drawn through extremes with the compass and cut vertically at their terminals.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .geom import Contour, Path, line, tcurve
from .parts import Ell


def hook(x0: float, st: float, th: float, y_top: float, bot: float, rx: float, ry: float, x_cut: float,
         t: float, t_in: float) -> Contour:
    """A stem whose left edge is x0, running down from y_top and turning right along the bottom.

    The bottom outer extreme sits at y = bot; the curve's outer radii are rx, ry; the stroke is st wide in the
    stem and th thick at the bottom. The end is cut vertically at x_cut. Mirror it for j g J, flip it for f.
    """
    cx, cy = x0 + rx, bot + ry
    eo = Ell(cx, cy, rx, ry, t)
    ei = Ell(cx, cy, rx - st, ry - th, t_in)
    outer = line((x0, y_top), eo.p("W")).then(eo.arc("W", "S", "E")).cut_x(x_cut, "head", -1)
    inner = line((x0 + st, y_top), ei.p("W")).then(ei.arc("W", "S", "E")).cut_x(x_cut, "head", -1)
    return Contour.of(outer, line(outer.end, inner.end), inner.reversed())


@dataclass(frozen=True)
class SSpec:
    """The numbers of one s: box, weights and shape."""

    x0: float
    w: float  # width of the lower bowl (the widest part)
    bot: float  # outer bottom extreme (with overshoot)
    top: float  # outer top extreme (with overshoot)
    ym: float  # height of the spine's centre
    upper: float  # upper bowl width / lower bowl width
    th: float  # top and bottom thickness
    side: float  # thickness at the side extremes
    spine: float  # spine thickness, square to the stroke
    steep: float  # spine steepness: fraction of the steepest spine the bowls allow (0.5 to 0.85)
    ap: float  # terminal cut, degrees from each bowl's horizontal axis
    t: float
    t_in: float
    k: float = 0.47  # bowl centres: this fraction of the way from the spine centre to the top and bottom
    lean: float = 0.0  # upper bowl's centre lies this far right of the lower bowl's
    tilt: float = 0.7  # counters' side extremes move toward the spine by this fraction of its vertical offset


def s_curve(s: SSpec) -> Contour:
    """Upper bowl over a wider lower bowl, joined by a spine; both terminals cut vertically.

    The counters' side extremes sit nearer the spine than the outer ones (the stress tilts with the stroke),
    so both edges of the spine leave their bowls alike.
    """
    rxl = s.w / 2
    cxl = s.x0 + rxl
    rxu = rxl * s.upper
    cxu = cxl + s.lean
    cyu = s.ym + (s.top - s.ym) * s.k
    cyl = s.ym - (s.ym - s.bot) * s.k
    mx = s.x0 + s.w / 2 + s.lean / 2
    w1 = cxu - rxu + s.side / 2  # centre line of the stroke at the side extremes
    a = math.atan(s.steep * (cyu - s.ym) / (mx - w1))
    dy = s.spine * math.cos(a) * s.tilt
    uo = Ell(cxu, cyu, rxu, s.top - cyu, s.t)
    ui = Ell(cxu, cyu + dy, rxu - s.side, s.top - s.th - cyu - dy, s.t_in)
    lo = Ell(cxl, cyl, rxl, cyl - s.bot, s.t)
    li = Ell(cxl, cyl - dy, rxl - s.side, cyl - dy - s.bot - s.th, s.t_in)
    d = (math.cos(a), -math.sin(a))
    n = (math.sin(a), math.cos(a))
    m_up = (mx + n[0] * s.spine / 2, s.ym + n[1] * s.spine / 2)
    m_dn = (mx - n[0] * s.spine / 2, s.ym - n[1] * s.spine / 2)
    x1 = cxu + ui.rx * math.cos(math.radians(s.ap))
    x2 = cxl - li.rx * math.cos(math.radians(s.ap))
    down = (0.0, -1.0)

    def edge(top_e: Ell, mid, bot_e: Ell, side_w: Ell, side_e: Ell, t: float) -> Path:
        p = top_e.arc("E", "N", "W").cut_x(x1, "tail", 0)
        p.add(tcurve(side_w.p("W"), down, mid, d, t))
        p.add(tcurve(mid, d, side_e.p("E"), down, t))
        return p.then(bot_e.arc("E", "S", "W")).cut_x(x2, "head", -1)

    r = edge(uo, m_dn, li, uo, li, s.t)
    lft = edge(ui, m_up, lo, ui, lo, s.t_in)
    c = Contour.of(r, line(r.end, lft.end), lft.reversed())
    return c if c.area() > 0 else c.reversed()
