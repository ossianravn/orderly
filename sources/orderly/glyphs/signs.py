"""Signs: © ® ™ § ¶ † ‡ ‰ № ª º • ¦, and the spacing accents ¨ ¯ ´ ¸ ˆ ˇ ˘ ˙ ˚ ˛ ˜ ˝.

Letters inside signs (the C of ©, the R of ®, TM, the ordinals' a and o) are the font's own letters drawn by a
small master (`small.py`), so their strokes keep the text's colour."""

from __future__ import annotations

from ..geom import Contour
from ..master import Master
from ..parts import Ell, box, disc, ring, shift
from ..small import bounds_x, small, spaced
from ..strokes import SSpec, s_curve
from . import REGISTRY, Drawing, glyph
from .control import o
from .figures import fw
from .lc_round import a
from .punct import dot_d
from .symbols import percent
from .uc_bowl import R
from .uc_diag import M
from .uc_round import C
from .uc_straight import T


def _ringed(m: Master, letter) -> Drawing:
    """A ring one cap height across with a small capital centred in it (© ®)."""
    sm = small(m, 0.52)
    inner = letter(sm).contours
    x0, x1 = bounds_x(inner)
    rw = sm.cstem * 0.92
    r = m.cap / 2 + m.os(m.cap)
    eo = Ell(r, m.cap / 2, r, r, m.tension)
    return Drawing(ring(eo, eo.inset(rw, rw, m.tension_in)) + shift(inner, r - (x0 + x1) / 2, m.cap / 2 - sm.cap / 2))


@glyph("copyright", 0xA9, "uc")
def copyright(m: Master) -> Drawing:
    return _ringed(m, C)


@glyph("registered", 0xAE, "uc")
def registered(m: Master) -> Drawing:
    return _ringed(m, R)


@glyph("trademark", 0x2122, "uc")
def trademark(m: Master) -> Drawing:
    sm = small(m, 0.44)
    t, mm = T(sm).contours, M(sm).contours
    dy = m.cap - sm.cap
    return Drawing(shift(t, 0, dy) + shift(mm, sm.w("T") + sm.cstem * 0.75, dy))


def _ordinal(m: Master, letter, name: str) -> Drawing:
    """A small lowercase letter hanging from the cap height over a short bar (ª º)."""
    sm = small(m)
    cs, adv = spaced(sm, name, "lc", letter(sm).contours, dy=m.cap - sm.xh)
    x0, x1 = bounds_x(cs)
    yb = m.cap - sm.xh - sm.xh * 0.16
    return Drawing(cs + [box(x0, yb - sm.bar, x1, yb)], advance=adv)


@glyph("ordfeminine", 0xAA, "uc")
def ordfeminine(m: Master) -> Drawing:
    return _ordinal(m, a, "a")


@glyph("ordmasculine", 0xBA, "uc")
def ordmasculine(m: Master) -> Drawing:
    return _ordinal(m, o, "o")


@glyph("uni2116", 0x2116, "uc")
def numero(m: Master) -> Drawing:
    from .uc_diag import N

    n = N(m).contours
    sup = _ordinal(m, o, "o").contours
    x0, _ = bounds_x(sup)
    return Drawing(n + shift(sup, m.w("N") + m.cstem * 0.5 - x0))


@glyph("section", 0xA7, "uc")
def section(m: Master) -> Drawing:
    """§: two s curves, the upper one's foot lapping over the lower one's head."""
    sm = small(m, 0.7)
    st, b, side, th = fw(sm)
    w = sm.w("S") * 0.96
    y0, y1 = -m.cap * 0.12, m.cap + m.os(m.cap)
    hs = (y1 - y0) * 0.62

    def one(bot: float, top: float):
        return s_curve(SSpec(
            x0=0, w=w, bot=bot, top=top, ym=bot + (top - bot) * m.g("s.mid"), upper=m.g("s.upper"),
            th=th * m.g("s.thin"), side=side * m.g("s.side"), spine=st * m.g("s.spinew"), ap=m.ap_C, t=m.tension,
            t_in=m.tension_in, hu=m.g("s.hu"), hl=m.g("s.hl"), lean=m.g("s.lean") * w, steep=m.g("s.steep"),
            t_bowl=m.g("s.tbowl"), t_mid=m.g("s.tmid")))

    return Drawing([one(y1 - hs, y1), one(y0, y0 + hs)])


@glyph("paragraph", 0xB6, "uc")
def paragraph(m: Master) -> Drawing:
    """¶: a solid half round hanging from a top bar beside two stems."""
    st, b, _, _ = fw(m)
    st, b = st * 0.9, b * 0.9
    y0, y1 = m.desc * 0.7, m.cap
    xb, yb = m.cap * 0.3, m.cap * 0.38
    bowl = Ell(xb, (y1 + yb) / 2, xb, (y1 - yb) / 2, m.tension)
    x2 = xb + st + st * 0.9
    return Drawing([Contour.of(bowl.arc("N", "W", "S")), box(xb - 1, y0, xb + st, y1), box(x2, y0, x2 + st, y1),
                    box(xb, y1 - b, x2 + st, y1)])


def _dagger(m: Master, bars: tuple[float, ...]) -> Drawing:
    st, b, _, _ = fw(m)
    st, b = st * 0.9, b * 0.9
    y0, y1 = m.desc * 0.7, m.cap
    w = m.cap * 0.5
    h = y1 - y0
    return Drawing([box(w / 2 - st / 2, y0, w / 2 + st / 2, y1)] +
                   [box(0, y0 + h * f - b / 2, w, y0 + h * f + b / 2) for f in bars])


@glyph("dagger", 0x2020, "uc")
def dagger(m: Master) -> Drawing:
    return _dagger(m, (0.72,))


@glyph("daggerdbl", 0x2021, "uc")
def daggerdbl(m: Master) -> Drawing:
    return _dagger(m, (0.75, 0.25))


@glyph("perthousand", 0x2030, "uc")
def perthousand(m: Master) -> Drawing:
    """‰: the % with a third round beside its lower one."""
    cs = percent(m).contours
    r = m.cap * 0.2
    side = min(m.stem * 0.9, r * 0.42)
    o3 = Ell(r * 3.2 + r * 1.84 + side * 0.7, r, r * 0.92, r, m.tension)
    return Drawing(cs + ring(o3, o3.inset(side, side * 0.9)))


@glyph("bullet", 0x2022, "pun")
def bullet(m: Master) -> Drawing:
    return Drawing([disc(0, m.xh * 0.5, dot_d(m) * 1.6, m.tension)])


@glyph("brokenbar", 0xA6, "pun")
def brokenbar(m: Master) -> Drawing:
    y0, y1 = m.desc * 0.72, m.asc + 20
    ym, g = (y0 + y1) / 2, m.bar * 0.8
    st = m.stem * 0.95
    return Drawing([box(0, y0, st, ym - g), box(0, ym + g, st, y1)])


SPACING = {"dieresis": (0xA8, "dieresiscomb"), "macron": (0xAF, "macroncomb"), "acute": (0xB4, "acutecomb"),
           "cedilla": (0xB8, "cedillacomb"), "circumflex": (0x2C6, "circumflexcomb"), "caron": (0x2C7, "caroncomb"),
           "breve": (0x2D8, "brevecomb"), "dotaccent": (0x2D9, "dotaccentcomb"), "ring": (0x2DA, "ringcomb"),
           "ogonek": (0x2DB, "ogonekcomb"), "tilde": (0x2DC, "tildecomb"), "hungarumlaut": (0x2DD, "hungarumlautcomb")}


def _spacing_accent(mark: str):
    def fn(m: Master) -> Drawing:
        cs = REGISTRY[mark].fn(m).contours
        x0, x1 = bounds_x(cs)
        sb = m.xh * 0.08
        return Drawing(shift(cs, sb - x0), advance=x1 - x0 + 2 * sb)

    return fn


for _n, (_u, _mk) in SPACING.items():
    glyph(_n, _u, "pun")(_spacing_accent(_mk))
