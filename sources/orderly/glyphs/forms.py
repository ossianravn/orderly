"""Alternate forms reached by features: `.case` punctuation, the stylistic sets' letters and their accented
composites, and the localized forms.

- case: punctuation moved up to sit with capitals and figures (components of the base, moved).
- ss01: the double-storey a in every accented a. ss02: l with a curved foot (the t's hook) in every l.
- locl: Turkish i (dotted under marks), Catalan punt volat, Dutch íj́, and the N-form Eng for Sámi.
"""

from __future__ import annotations

from ..diag import placed
from ..master import Master
from ..parts import box, disc, mirror_x, shift
from ..shapes import lc_hook
from . import REGISTRY, Drawing, glyph
from .composites import PARTS
from .letters_extra import slash_bar
from .nordic import ring_mark, _bounds_x
from .lc_round import a_ss01


def _bounds_y(m: Master, name: str) -> tuple[float, float]:
    ys = [p[1] for c in REGISTRY[name].fn(m).contours for p in c.flat(6)]
    return min(ys), max(ys)


def _centre_on_caps(name: str):
    def dy(m: Master) -> float:
        y0, y1 = _bounds_y(m, name)
        return m.cap / 2 - (y0 + y1) / 2

    return dy


CASE = {
    "hyphen": lambda m: m.cap * m.g("math.axis") - m.xh * m.g("hyphen.y"),
    "endash": lambda m: m.cap * m.g("math.axis") - m.xh * m.g("hyphen.y"),
    "emdash": lambda m: m.cap * m.g("math.axis") - m.xh * m.g("hyphen.y"),
    "parenleft": _centre_on_caps("parenleft"), "parenright": _centre_on_caps("parenright"),
    "bracketleft": _centre_on_caps("bracketleft"), "bracketright": _centre_on_caps("bracketright"),
    "braceleft": _centre_on_caps("braceleft"), "braceright": _centre_on_caps("braceright"),
    "guillemotleft": lambda m: (m.cap - m.xh) / 2, "guillemotright": lambda m: (m.cap - m.xh) / 2,
    "guilsinglleft": lambda m: (m.cap - m.xh) / 2, "guilsinglright": lambda m: (m.cap - m.xh) / 2,
    "exclamdown": lambda m: m.cap - m.xh, "questiondown": lambda m: m.cap - m.xh,
    "colon": lambda m: (m.cap - m.xh) / 2, "periodcentered": lambda m: (m.cap - m.xh) / 2,
    "bullet": lambda m: (m.cap - m.xh) / 2,
}

for _n, _dy in CASE.items():
    glyph(f"{_n}.case", None, "pun")(lambda m, n=_n, dy=_dy: Drawing([], components=[(n, (0, dy(m)))]))


# ss02: l with a curved foot


def l_foot(m: Master) -> list:
    rx = m.stem * m.g("t.rx")
    return [lc_hook(m, 0, m.asc, -m.os(m.xh), rx, rx * m.g("hook.ry"), m.g("hook.ap"))]


@glyph("l.ss02", None, "lc")
def l_ss02(m: Master) -> Drawing:
    return Drawing(l_foot(m), anchors={"top": (m.stem / 2, m.asc), "caronalt": (m.stem + m.xh * 0.08, m.asc)})


@glyph("lslash.ss02", None, "lc")
def lslash_ss02(m: Master) -> Drawing:
    return Drawing(l_foot(m) + [slash_bar(-m.stem * 1.1, m.stem * 2.1, m.xh * 0.62, m.xh * 0.28, m.bar * 0.9)])


@glyph("ldot.ss02", None, "lc")
def ldot_ss02(m: Master) -> Drawing:
    dd = m.stem * m.dot
    return Drawing(l_foot(m) + [disc(m.stem + dd * 0.9, m.xh * 0.62, dd, m.tension)])


@glyph("aring.ss01", None, "lc")
def aring_ss01(m: Master) -> Drawing:
    base = a_ss01(m).contours
    x0, x1 = _bounds_x(base)
    top = m.xh + m.os(m.xh) + m.xh * m.g("ring.gap")
    d = m.xh * m.g("ring.lc")
    return Drawing(base + ring_mark(m, (x0 + x1) / 2, top, d, m.bar * m.g("ring.w")),
                   anchors={"top": ((x0 + x1) / 2, top + d)})


def _alternate(bases: dict[str, str], suffix: str) -> None:
    """Every composite on one of `bases` gets a twin on its alternate, named with the suffix (aacute.ss01)."""
    for name, parts in list(PARTS.items()):
        b = parts[0][0]
        if b in bases:
            new = [(bases[b], parts[0][1])] + list(parts[1:])
            glyph(f"{name}{suffix}", None, "lc")(lambda m, p=new: Drawing([], components=list(p)))


_alternate({"a": "a.ss01", "aring": "aring.ss01"}, ".ss01")
_alternate({"l": "l.ss02"}, ".ss02")


# locl


glyph("iogonek.dotless", None, "lc")(  # Lithuanian į̀ į́ į̃: ccmp swaps it in before a top mark
    lambda m: Drawing([], components=[("dotlessi", None), ("ogonekcomb", "ogonek")]))


@glyph("i.loclTRK", None, "lc")
def i_trk(m: Master) -> Drawing:
    return Drawing([], components=[("i", None)])


def _punt(m: Master, y: float) -> Drawing:
    """The Catalan punt volat (l·l): the middle dot with tight sides, so l·l keeps the rhythm of ll."""
    d = m.stem * m.dot
    gap = m.stem * 0.35
    return Drawing([disc(gap + d / 2, y, d, m.tension)], advance=d + 2 * gap)


@glyph("periodcentered.loclCAT", None, "pun")
def punt(m: Master) -> Drawing:
    return _punt(m, m.xh * 0.55)


@glyph("periodcentered.loclCAT.case", None, "pun")
def punt_case(m: Master) -> Drawing:
    return _punt(m, m.cap * 0.5)


glyph("jacute", None, "lc")(lambda m: Drawing([], components=[("uni0237", None), ("acutecomb", "top")]))
glyph("Jacute", None, "uc")(lambda m: Drawing([], components=[("J", None), ("acutecomb.case", "top")]))


@glyph("Eng.loclNSM", None, "uc")
def eng_n(m: Master) -> Drawing:
    """The N-form Eng preferred in Sámi: N whose right stem runs on below the baseline into the hook of J."""
    w = m.w("N")
    st = m.cstem * m.g("N.stem")
    thin = m.cstem * m.diag * m.g("N.weight") * m.diag_thin
    rx = m.cstem * m.g("j.rx")
    hk = lc_hook(m, 0, m.cap, m.desc - m.os(-m.desc), rx, rx * m.g("hook.ry"), m.g("hook.ap"), st=st,
                 th=m.cbar * m.rtop)
    hook = shift(mirror_x([hk], st / 2), w - st)  # the stem stays upright on the right, the hook turns left
    return Drawing([box(0, 0, st, m.cap), placed(("r", w, 0), ("l", 0, m.cap), thin, thin)] + hook)
