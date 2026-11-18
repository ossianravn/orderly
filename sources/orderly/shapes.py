"""Shared shapes read from a master: the lowercase and capital rounds, the n arch, the bowl.

These are the "shared parts are shared code" of the plan: the bowl of b d p q, the arch of n h m r u, the round
of o c e and O C G Q. A change here changes every sibling.
"""

from __future__ import annotations

import math

from .master import Master
from .parts import Ell
from .rounds import arch, arm, bowl
from .strokes import hook


def lc_round(m: Master, width: float | None = None, cx: float | None = None) -> tuple[Ell, Ell]:
    """The lowercase round: the o's outer and inner ellipse, centred at cx (default: half its width)."""
    h = m.xh + 2 * m.os(m.xh)
    w = m.w("o") if width is None else width
    cx = w / 2 if cx is None else cx
    eo = Ell(cx, m.xh / 2, w / 2, h / 2, m.tension)
    ei = eo.inset(m.stem * m.rside, m.bar * m.rtop, m.tension_in)
    return eo, ei


def uc_round(m: Master, width: float | None = None, cx: float | None = None) -> tuple[Ell, Ell]:
    h = m.cap + 2 * m.os(m.cap)
    w = m.w("O") if width is None else width
    cx = w / 2 if cx is None else cx
    eo = Ell(cx, m.cap / 2, w / 2, h / 2, m.tension)
    ei = eo.inset(m.cstem * m.rside, m.cbar * m.rtop, m.tension_in)
    return eo, ei


def arch_top(m: Master) -> float:
    """Thickness of an arch or bowl at its top extreme."""
    return m.bar * m.rtop


def n_arch(m: Master, x0: float, width: float, host=None, base: float = 0.0, cut: float | None = None):
    """The arch of n h m: joins the stem whose left edge is x0 and comes down as the right stem.

    The counter is an ellipse whose west extreme runs `bite` of a stem into the left stem; its proportions follow
    the o's counter so the arch is drawn by the same compass. With `cut` (degrees, measured on the counter from
    its top toward the east) the arch stops there in a vertical cut: the arm of r.
    """
    eo, ei, s, th = _arch_ellipses(m, x0, width)
    if cut is not None:
        x = ei.cx + ei.rx * math.sin(math.radians(cut))
        return arm(eo, ei, s, x, th * (1 - m.join), m.stem * 0.5, m.join_turn, m.tension), None
    return arch(eo, ei, s if host is None else host, base, th * (1 - m.join), m.stem * 0.5, m.join_turn, m.tension)


def _arch_ellipses(m: Master, x0: float, width: float):
    s = x0 + m.stem
    xr = x0 + width
    top = m.xh + m.os(m.xh)
    th = arch_top(m)
    xri = xr - m.stem
    xli = s - m.bite * m.stem
    rxi = (xri - xli) / 2
    cxi = xli + rxi
    _, oi = lc_round(m)
    ryi = rxi * oi.ry / oi.rx
    cy = top - th - ryi
    ei = Ell(cxi, cy, rxi, ryi, m.tension_in)
    eo = Ell(cxi, cy, xr - cxi, top - cy, m.tension)
    return eo, ei, s, th


def lc_bowl(m: Master, x0: float, width: float | None = None):
    """The bowl of b p (stem on the left, left edge x0); mirror it for d q a g.

    The bowl is the o's round, moved so its counter runs `bite` of a stem into the stem, as the n's arch does.
    Pass a width to narrow the round (a). Returns the contour and the outer east x.
    """
    s = x0 + m.stem
    eo, ei = lc_round(m, width)
    dx = s - m.bite * m.stem - ei.p("W")[0]
    eo = Ell(eo.cx + dx, eo.cy, eo.rx, eo.ry, eo.t)
    ei = Ell(ei.cx + dx, ei.cy, ei.rx, ei.ry, ei.t)
    th = arch_top(m)
    c = bowl(eo, ei, s, th * (1 - m.join), th * (1 - m.join), m.stem * 0.5, m.join_turn, m.tension)
    return c, eo.p("E")[0]


def lc_hook(m: Master, x0: float, y_top: float, bot: float, rx: float, ry: float, ap: float,
            st: float | None = None, th: float | None = None):
    """The hook of t j g f J: stem from y_top, turning right at the bottom; cut ap degrees past the bottom."""
    st = m.stem if st is None else st
    th = arch_top(m) if th is None else th
    cx = x0 + rx
    x_cut = cx + (rx - st) * math.sin(math.radians(ap))
    return hook(x0, st, th, y_top, bot, rx, ry, x_cut, m.tension, m.tension_in)
