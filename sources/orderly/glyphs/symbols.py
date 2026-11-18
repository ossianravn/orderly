"""ASCII symbols and the Latin Core punctuation: # $ % * + - < = > @ [ \\ ] ^ _ ` { | } ~, ¡ ¿ « » ‹ › ° · – — ‘ ’ ‚
“ ” „ … −. Math sits on the figures' middle; strokes are the stem, bars the bar weight."""

from __future__ import annotations

import math

from ..diag import edges, peak_poly, placed, stroke, vee_poly
from ..geom import Contour, line, quad
from ..master import Master
from ..parts import Ell, box, disc, mirror_x, mirror_y, ring, rotate180, shift
from ..strokes import offsets, s_curve
from . import Drawing, glyph
from .marks import _shape
from .punct import comma, exclam, low_dot, question
from .uc_round import S_spec
from .lc_round import a


def mid(m: Master) -> float:
    """Height of the math axis: the middle of the figures, a little low."""
    return m.cap * m.g("math.axis")


def _w(m: Master) -> float:
    return m.cap * m.g("math.w")


def math_glyph(fn):
    """Math signs share one advance: the sign's width plus a fixed margin each side, drawn centred."""
    def wrap(m: Master) -> Drawing:
        d = fn(m)
        xs = [p[0] for c in d.contours for p in c.flat(6)]
        adv = _w(m) + 2 * m.cap * m.g("math.sb")
        return Drawing(shift(d.contours, (adv - (max(xs) + min(xs))) / 2), advance=adv)

    wrap.__name__ = fn.__name__
    return wrap


@glyph("plus", 0x2B, "uc")
@math_glyph
def plus(m: Master) -> Drawing:
    w, b, y = _w(m), m.bar, mid(m)
    return Drawing([box(0, y - b / 2, w, y + b / 2), box(w / 2 - m.stem * 0.47, y - w / 2, w / 2 + m.stem * 0.47, y + w / 2)])


@glyph("minus", 0x2212, "uc")
@math_glyph
def minus(m: Master) -> Drawing:
    w, b, y = _w(m), m.bar, mid(m)
    return Drawing([box(0, y - b / 2, w, y + b / 2)])


@glyph("equal", 0x3D, "uc")
@math_glyph
def equal(m: Master) -> Drawing:
    w, b, y, g = _w(m), m.bar, mid(m), m.cap * 0.1
    return Drawing([box(0, y + g - b / 2, w, y + g + b / 2), box(0, y - g - b / 2, w, y - g + b / 2)])


def _chevron(m: Master, w: float, h: float, y: float, t: float) -> list:
    """< : two strokes meeting at a flat point on the left, built as a vee turned on its side."""
    cs = [vee_poly(edges(("l", -t * 0.25, 0), ("l", -h / 2, w), t * 0.9, t), edges(("r", t * 0.25, 0), ("r", h / 2, w), t * 0.9, t))]
    return [c.map(lambda p: (p[1], y + p[0])) .reversed() for c in cs]


@glyph("less", 0x3C, "uc")
@math_glyph
def less(m: Master) -> Drawing:
    return Drawing(_chevron(m, _w(m), _w(m) * 0.95, mid(m), m.stem * 0.95))


@glyph("greater", 0x3E, "uc")
@math_glyph
def greater(m: Master) -> Drawing:
    return Drawing(mirror_x(_chevron(m, _w(m), _w(m) * 0.95, mid(m), m.stem * 0.95), _w(m) / 2))


def _guil(m: Master, s: float) -> list:
    """A guillemet: the < chevron at x-height scale; heavy masters draw it larger and lighter (`guil.*`)."""
    k = s * m.g("guil.size")
    return _chevron(m, m.xh * 0.4 * k, m.xh * 0.52 * k, m.xh * 0.5, m.stem * m.g("guil.w"))


@glyph("guilsinglleft", 0x2039, "pun")
def guilsinglleft(m: Master) -> Drawing:
    return Drawing(_guil(m, 1))


@glyph("guilsinglright", 0x203A, "pun")
def guilsinglright(m: Master) -> Drawing:
    return Drawing(mirror_x(_guil(m, 1), 0))


@glyph("guillemotleft", 0xAB, "pun")
def guillemotleft(m: Master) -> Drawing:
    one = _guil(m, 1)
    return Drawing(one + shift(one, m.xh * 0.4 * m.g("guil.size") + m.stem * 0.55))


@glyph("guillemotright", 0xBB, "pun")
def guillemotright(m: Master) -> Drawing:
    return Drawing(mirror_x(guillemotleft(m).contours, 0))


@glyph("numbersign", 0x23, "uc")
def numbersign(m: Master) -> Drawing:
    w, b, st = m.cap * 0.72, m.bar, m.stem * 0.92
    y0, y1 = m.cap * 0.04, m.cap * 0.86
    sl = (y1 - y0) * 0.14
    stems = [stroke((x, y0), (x + sl, y1), st) for x in (w * 0.28, w * 0.62)]
    bars = [box(0, y, w, y + b) for y in (m.cap * 0.28 - b / 2, m.cap * 0.6 - b / 2)]
    return Drawing(stems + bars)


@glyph("dollar", 0x24, "uc")
def dollar(m: Master) -> Drawing:
    from dataclasses import replace

    sp = replace(S_spec(m), w=m.w("S") * 0.86)
    cx = sp.w / 2
    return Drawing([s_curve(sp), box(cx - m.stem * 0.42, -m.cap * 0.1, cx + m.stem * 0.42, m.cap * 1.1)])


@glyph("percent", 0x25, "uc")
def percent(m: Master) -> Drawing:
    r = m.cap * 0.2
    side = min(m.stem * 0.9, r * 0.42)
    o1 = Ell(r, m.cap - r, r * 0.92, r, m.tension)
    o2 = Ell(r * 3.2, r, r * 0.92, r, m.tension)
    sl = placed(("l", r * 0.4, 0), ("r", r * 3.9, m.cap), m.stem * 0.9)
    return Drawing(ring(o1, o1.inset(side, side * 0.9)) + ring(o2, o2.inset(side, side * 0.9)) + [sl])


@glyph("asterisk", 0x2A, "uc")
def asterisk(m: Master) -> Drawing:
    cy, r, t = m.cap * 0.74, m.cap * 0.17, m.bar * 0.95
    out = []
    for k in range(3):
        a = math.radians(90 + 60 * k)
        ca, sa = math.cos(a), math.sin(a)
        pts = [(-r, -t / 2), (r, -t / 2), (r, t / 2), (-r, t / 2)]
        out.append(quad(*[(r + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]))
    return Drawing(out)


@glyph("at", 0x40, "uc")
def at(m: Master) -> Drawing:
    k = 0.58
    inner = [c.map(lambda p: (p[0] * k, p[1] * k)) for c in a(m).contours]
    xs = [p[0] for c in inner for p in c.flat(6)]
    cx, r = (min(xs) + max(xs)) / 2, m.cap * 0.5
    eo = Ell(cx, m.xh * k / 2, r, r, m.tension)
    return Drawing(ring(eo, eo.inset(m.bar * 0.85, m.bar * 0.8)) + inner)


def _bracket(m: Master) -> Contour:
    st, b, w = m.stem, m.bar, m.xh * 0.42
    y0, y1 = m.desc * 0.72, m.asc + 20
    return quad((0, y0), (w, y0), (w, y0 + b), (st, y0 + b), (st, y1 - b), (w, y1 - b), (w, y1), (0, y1))


@glyph("bracketleft", 0x5B, "pun")
def bracketleft(m: Master) -> Drawing:
    return Drawing([_bracket(m)])


@glyph("bracketright", 0x5D, "pun")
def bracketright(m: Master) -> Drawing:
    return Drawing(mirror_x([_bracket(m)], 0))


@glyph("backslash", 0x5C, "pun")
def backslash(m: Master) -> Drawing:
    w = m.w("slash")
    return Drawing(mirror_x([placed(("l", 0, m.desc * m.g("slash.low")), ("r", w, m.cap + m.g("slash.high")),
                                    m.stem * m.diag * m.g("slash.w"))], w / 2))


@glyph("bar", 0x7C, "pun")
def bar(m: Master) -> Drawing:
    return Drawing([box(0, m.desc * 0.72, m.stem * 0.95, m.asc + 20)])


@glyph("underscore", 0x5F, "pun")
def underscore(m: Master) -> Drawing:
    return Drawing([box(0, m.desc * 0.55 - m.bar / 2, m.xh * 0.95, m.desc * 0.55 + m.bar / 2)])


@glyph("asciicircum", 0x5E, "uc")
def asciicircum(m: Master) -> Drawing:
    w, h, t = _w(m), m.cap * 0.42, m.stem * 0.9
    y0 = m.cap * 0.42
    return Drawing([peak_poly(edges(("l", 0, y0), ("l", w / 2 - t * 0.45, y0 + h), t, t * 0.9),
                              edges(("r", w, y0), ("r", w / 2 + t * 0.45, y0 + h), t, t * 0.9))])


def tilde_shape(m: Master, h: float = 0.32) -> list:
    """The tilde's wave at math width, centred on the math axis (~ and ≈)."""
    from dataclasses import replace

    big = replace(m, xh=m.cap * 1.25, bar=m.bar * 1.05)
    cs = _shape("tildecomb", big, 0, m.cap * h, m.bar * 1.0, 0)
    ys = [p[1] for c in cs for p in c.flat(6)]
    return shift(cs, 0, mid(m) - (min(ys) + max(ys)) / 2)


@glyph("asciitilde", 0x7E, "uc")
@math_glyph
def asciitilde(m: Master) -> Drawing:
    return Drawing(tilde_shape(m))


@glyph("grave", 0x60, "uc")
def grave(m: Master) -> Drawing:
    return Drawing(_shape("gravecomb", m, m.cap - m.xh * 0.26, m.xh * 0.26, m.bar * m.g("mark.w"), 0))


def _brace(m: Master) -> list:
    """{ : a stroke from the top terminal turning down into a straight stem, then turning left into the nose; the
    lower half is the upper mirrored, and the two meet in the nose. Turns are quarter rounds of the compass;
    both ends are vertical cuts, the nose is where the halves' horizontal ends overlap."""
    st, b = m.stem * 0.94, m.bar * 0.94
    w = m.xh * 0.3 + m.stem * 1.4
    y0, y1 = m.desc * 0.72, m.asc + 20
    ym, xs = (y0 + y1) / 2, w * 0.5
    nodes = [((w, y1 - b / 2), (-1.0, 0.0), b), ((xs, y1 - b / 2 - (w - xs)), (0.0, -1.0), st),
             ((xs, ym + xs), (0.0, -1.0), st), ((0.0, ym + b * 0.12), (-1.0, 0.0), b)]  # halves overlap in the
    # nose without sharing an edge
    left, right = offsets(nodes, [(m.tension, m.tension), (0.34, 0.34), (m.tension, m.tension)], m.tension_in / m.tension)
    upper = Contour.of(right, line(right.end, left.end), left.reversed())
    upper = upper if upper.area() > 0 else upper.reversed()
    return [upper] + mirror_y([upper], ym)


@glyph("braceleft", 0x7B, "pun")
def braceleft(m: Master) -> Drawing:
    return Drawing(_brace(m))


@glyph("braceright", 0x7D, "pun")
def braceright(m: Master) -> Drawing:
    return Drawing(mirror_x(_brace(m), 0))


@glyph("exclamdown", 0xA1, "pun")
def exclamdown(m: Master) -> Drawing:
    return Drawing(rotate180(exclam(m).contours, 0, m.xh / 2))


@glyph("questiondown", 0xBF, "pun")
def questiondown(m: Master) -> Drawing:
    return Drawing(rotate180(question(m).contours, 0, m.xh / 2))


@glyph("degree", 0xB0, "uc")
def degree(m: Master) -> Drawing:
    r = m.cap * 0.14
    eo = Ell(r, m.cap - r, r, r, m.tension)
    k = min(m.bar * 0.85, r * 0.45)
    return Drawing(ring(eo, eo.inset(k, k)))


@glyph("periodcentered", 0xB7, "pun")
def periodcentered(m: Master) -> Drawing:
    d = m.stem * m.dot
    return Drawing([disc(0, m.xh * 0.5, d, m.tension)])
