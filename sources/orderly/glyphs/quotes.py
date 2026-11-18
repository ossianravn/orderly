"""Dashes, quotes and the ellipsis: built from the hyphen's bar and the comma."""

from __future__ import annotations

from ..master import Master
from ..parts import box, rotate180, shift
from . import Drawing, glyph
from .punct import comma, low_dot


@glyph("endash", 0x2013, "pun")
def endash(m: Master) -> Drawing:
    y = m.xh * m.g("hyphen.y")
    return Drawing([box(0, y - m.bar / 2, m.g("dash.en") * 1000, y + m.bar / 2)])


@glyph("emdash", 0x2014, "pun")
def emdash(m: Master) -> Drawing:
    y = m.xh * m.g("hyphen.y")
    return Drawing([box(0, y - m.bar / 2, m.g("dash.em") * 1000, y + m.bar / 2)])


def _comma_at(m: Master, top: float, turned: bool) -> list:
    cs = comma(m).contours
    ys = [p[1] for c in cs for p in c.flat(6)]
    if turned:
        cs = rotate180(cs, 0, 0)
        ys = [p[1] for c in cs for p in c.flat(6)]
    return shift(cs, 0, top - max(ys))


@glyph("quoteleft", 0x2018, "pun")
def quoteleft(m: Master) -> Drawing:
    return Drawing(_comma_at(m, m.cap, True))


@glyph("quoteright", 0x2019, "pun")
def quoteright(m: Master) -> Drawing:
    return Drawing(_comma_at(m, m.cap, False))


@glyph("quotesinglbase", 0x201A, "pun")
def quotesinglbase(m: Master) -> Drawing:
    return Drawing(comma(m).contours)


def _double(cs: list, m: Master) -> list:
    return cs + shift(cs, m.stem * m.dot * 1.55)


@glyph("quotedblleft", 0x201C, "pun")
def quotedblleft(m: Master) -> Drawing:
    return Drawing(_double(_comma_at(m, m.cap, True), m))


@glyph("quotedblright", 0x201D, "pun")
def quotedblright(m: Master) -> Drawing:
    return Drawing(_double(_comma_at(m, m.cap, False), m))


@glyph("quotedblbase", 0x201E, "pun")
def quotedblbase(m: Master) -> Drawing:
    return Drawing(_double(comma(m).contours, m))


@glyph("ellipsis", 0x2026, "pun")
def ellipsis(m: Master) -> Drawing:
    step = m.stem * m.dot * 2.2
    return Drawing([low_dot(m, k * step) for k in range(3)])
