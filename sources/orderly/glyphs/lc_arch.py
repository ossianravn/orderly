"""Lowercase arches: h m r u, siblings of n. One arch primitive draws them all."""

from __future__ import annotations

from ..master import Master
from ..parts import box, rotate180
from ..shapes import n_arch
from . import Drawing, glyph


@glyph("h", 0x68, "lc")
def h(m: Master) -> Drawing:
    c, _ = n_arch(m, 0, m.w("n"))
    return Drawing([box(0, 0, m.stem, m.asc), c])


@glyph("m", 0x6D, "lc")
def m_(m: Master) -> Drawing:
    """Two arches; the second joins the first arch's shoulder, which is its stem."""
    a = (m.w("m") + m.stem) / 2
    first, outer = n_arch(m, 0, a)
    second, _ = n_arch(m, a - m.stem, a, host=outer)
    return Drawing([box(0, 0, m.stem, m.xh), first, second])


@glyph("r", 0x72, "lc")
def r(m: Master) -> Drawing:
    c, _ = n_arch(m, 0, m.w("n"), cut=m.g("r.cut"))
    return Drawing([box(0, 0, m.stem, m.xh), c])


@glyph("u", 0x75, "lc")
def u(m: Master) -> Drawing:
    """The n turned half round, so u and n share one arch."""
    c, _ = n_arch(m, 0, m.w("n"))
    return Drawing(rotate180([box(0, 0, m.stem, m.xh), c], m.w("n") / 2, m.xh / 2))
