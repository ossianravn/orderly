"""The control glyphs H O n o, and the space."""

from __future__ import annotations

from ..master import Master
from ..parts import box, ring
from ..shapes import lc_round, n_arch, uc_round
from . import Drawing, glyph


@glyph("space", 0x20, "pun")
def space(m: Master) -> Drawing:
    return Drawing([], advance=round(m.xh * m.space))


@glyph("uni00A0", 0xA0, "pun")  # no-break space; the AGL's "nbspace" is not a recommended production name
def nbspace(m: Master) -> Drawing:
    return space(m)


@glyph("uni2028", 0x2028, "pun")  # line separator: an empty glyph, so the character never shows as tofu
def line_separator(m: Master) -> Drawing:
    return Drawing([], advance=0)


@glyph("uni2029", 0x2029, "pun")  # paragraph separator
def paragraph_separator(m: Master) -> Drawing:
    return Drawing([], advance=0)


@glyph("H", 0x48, "uc")
def H(m: Master) -> Drawing:
    w, st = m.w("H"), m.cstem
    yc = m.cap * m.ubar
    return Drawing([
        box(0, 0, st, m.cap),
        box(w - st, 0, w, m.cap),
        box(st / 2, yc - m.cbar / 2, w - st / 2, yc + m.cbar / 2),
    ])


@glyph("O", 0x4F, "uc")
def O(m: Master) -> Drawing:
    return Drawing(ring(*uc_round(m)))


@glyph("n", 0x6E, "lc")
def n(m: Master) -> Drawing:
    c, _ = n_arch(m, 0, m.w("n"))
    return Drawing([box(0, 0, m.stem, m.xh), c])


@glyph("o", 0x6F, "lc")
def o(m: Master) -> Drawing:
    return Drawing(ring(*lc_round(m)))
