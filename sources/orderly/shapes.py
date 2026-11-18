"""Shared shapes read from a master: the lowercase and capital rounds, the n arch, the bowl.

These are the "shared parts are shared code" of the plan: the bowl of b d p q, the arch of n h m r u, the round
of o c e and O C G Q. A change here changes every sibling.
"""

from __future__ import annotations

from .master import Master
from .parts import Ell
from .rounds import arch, bowl


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


def n_arch(m: Master, x0: float, width: float, host=None, base: float = 0.0):
    """The arch of n h m: joins the stem whose left edge is x0 and comes down as the right stem.

    The counter is an ellipse whose west extreme runs `bite` of a stem into the left stem; its proportions follow
    the o's counter so the arch is drawn by the same compass.
    """
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
    return arch(eo, ei, s if host is None else host, base, th * (1 - m.join), m.stem * 0.5, m.join_turn, m.tension)


def lc_bowl(m: Master, x0: float, width: float, ycenter: float | None = None):
    """The bowl of b p (stem on the left, left edge x0); mirror it for d q a g."""
    s = x0 + m.stem
    w = m.w("o")
    eo, ei = lc_round(m)
    # the bowl is the o's round, moved so its outer east extreme lands at x0 + width
    dx = x0 + width - eo.p("E")[0]
    dy = 0.0 if ycenter is None else ycenter - eo.cy
    eo = Ell(eo.cx + dx, eo.cy + dy, eo.rx, eo.ry, eo.t)
    ei = Ell(ei.cx + dx, ei.cy + dy, ei.rx, ei.ry, ei.t)
    th = arch_top(m)
    del w
    return bowl(eo, ei, s, th * (1 - m.join), th * (1 - m.join), m.stem * 0.5, m.join_turn, m.tension)
