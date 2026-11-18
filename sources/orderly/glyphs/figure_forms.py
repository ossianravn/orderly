"""Figure forms: tabular figures on one width, the slashed zero, numerators drawn by the small master, and the
superiors, denominators and inferiors placed from them; the fraction slash and ½ ¼ ¾ ⅓ ⅔.

Numerators are the drawn small figures (top on the cap height). Superiors are the same glyphs encoded; the
denominators sit on the baseline and the inferiors drop below it, both as components moved down, so all four
forms share one drawing."""

from __future__ import annotations

from ..diag import placed
from ..master import Master
from ..parts import Ell, ring, shift
from ..small import FIGURES, INF_DROP, bounds_x, small, spaced
from ..spacing import sidebearings
from fontTools.agl import UV2AGL

from . import REGISTRY, Drawing, glyph
from .figures import fw


def name_of(cp: int) -> str:
    return UV2AGL.get(cp, f"uni{cp:04X}")

SUPS = {"zero": 0x2070, "one": 0xB9, "two": 0xB2, "three": 0xB3, "four": 0x2074, "five": 0x2075, "six": 0x2076,
        "seven": 0x2077, "eight": 0x2078, "nine": 0x2079}

_tab: dict = {}


def tab_width(m: Master) -> float:
    """One advance for every tabular figure: the widest figure with a margin of `tf.sb` times the zero's own
    sidebearing on each side."""
    if id(m) not in _tab:
        bodies = [bounds_x(REGISTRY[n].fn(m).contours) for n in FIGURES]
        zl, zr, _, _ = sidebearings(m, "zero", "uc", REGISTRY["zero"].fn(m).contours)
        margin = (zl + zr) / 2 * m.g("tf.sb")
        _tab[id(m)] = (m, max(x1 - x0 for x0, x1 in bodies) + 2 * margin)
    return _tab[id(m)][1]


def _centred(m: Master, cs: list) -> Drawing:
    x0, x1 = bounds_x(cs)
    adv = tab_width(m)
    return Drawing(shift(cs, (adv - (x1 - x0)) / 2 - x0), advance=adv)


for _f in FIGURES:
    glyph(f"{_f}.tf", None, "uc")(lambda m, f=_f: _centred(m, REGISTRY[f].fn(m).contours))


def slashed(m: Master) -> list:
    """The zero with a short diagonal across its counter, both ends buried in the ring."""
    _, b, side, th = fw(m)
    w = m.w("zero")
    eo = Ell(w / 2, m.cap / 2, w / 2, m.cap / 2 + m.os(m.cap), m.tension)
    ei = eo.inset(side, th, m.tension_in)
    mid = eo.inset(side * 0.55, th * 0.55)
    p0, p1 = mid.at_angle(243), mid.at_angle(63)
    return ring(eo, ei) + [placed(("c", p0[0], p0[1]), ("c", p1[0], p1[1]), b * 0.86)]


@glyph("zero.zero", None, "uc")
def zero_slash(m: Master) -> Drawing:
    zl, zr, x0, x1 = sidebearings(m, "zero", "uc", REGISTRY["zero"].fn(m).contours)
    return Drawing(shift(slashed(m), zl - x0), advance=zl + (x1 - x0) + zr)


@glyph("zero.tf.zero", None, "uc")
def zero_tf_slash(m: Master) -> Drawing:
    return _centred(m, slashed(m))


def _numr(f: str):
    def fn(m: Master) -> Drawing:
        sm = small(m)
        cs, adv = spaced(sm, f, "uc", REGISTRY[f].fn(sm).contours, dy=m.cap - sm.cap)
        return Drawing(cs, advance=adv)

    return fn


def _down(m: Master) -> float:
    return m.cap - small(m).cap


for _f in FIGURES:
    glyph(f"{_f}.numr", None, "uc")(_numr(_f))
    glyph(f"{_f}.dnom", None, "uc")(lambda m, f=_f: Drawing([], components=[(f"{f}.numr", (0, -_down(m)))]))
    glyph(name_of(SUPS[_f]), SUPS[_f], "uc")(lambda m, f=_f: Drawing([], components=[(f"{f}.numr", None)]))
    glyph(name_of(0x2080 + FIGURES.index(_f)), 0x2080 + FIGURES.index(_f), "uc")(
        lambda m, f=_f: Drawing([], components=[(f"{f}.numr", (0, -_down(m) - INF_DROP * m.cap))]))


@glyph("fraction", 0x2044, "uc")
def fraction(m: Master) -> Drawing:
    """A steep diagonal from the baseline to the cap height, with negative sidebearings so the numerator and
    denominator tuck in beside it."""
    st = fw(small(m))[0]
    run = m.cap * 0.42
    c = placed(("l", 0, 0), ("r", run, m.cap), st * m.diag)
    adv = run * 0.3
    return Drawing(shift([c], adv / 2 - run / 2), advance=adv)


FRACTIONS = {0xBD: ("one", "two"), 0xBC: ("one", "four"), 0xBE: ("three", "four"), 0x2153: ("one", "three"),
             0x2154: ("two", "three")}

for _u, (_n, _d) in FRACTIONS.items():
    glyph(name_of(_u), _u, "uc")(lambda m, n=_n, d=_d: Drawing([], components=[
        (f"{n}.numr", None), ("fraction", ">"), (f"{d}.numr", (">", -_down(m)))]))  # no nested components
