"""Run every glyph function for a master, space the results and round them to the grid."""

from __future__ import annotations

from dataclasses import dataclass, field

from .geom import Contour
from .glyphs import load
from .master import Master
from .spacing import COPY, bounds, sidebearings


@dataclass
class Glyph:
    name: str
    unicodes: tuple[int, ...]
    zone: str
    contours: list[Contour]  # placed in the advance, rounded
    advance: int
    lsb: int = 0
    rsb: int = 0
    anchors: dict[str, tuple[int, int]] = field(default_factory=dict)


def _round(c: Contour, dx: float) -> Contour:
    return c.map(lambda p: (round(p[0] + dx), round(p[1])))


def build(m: Master, only: list[str] | None = None) -> dict[str, Glyph]:
    specs = load()
    names = [n for n in specs if only is None or n in only]
    raw = {}
    for n in names:
        spec = specs[n]
        d = spec.fn(m)
        if d.advance is not None or not d.contours:
            raw[n] = (spec, d, None, None, None)
            continue
        left, right = sidebearings(m, n, spec.zone, d.contours)
        raw[n] = (spec, d, left, right, bounds(d.contours))
    # copied sides: a glyph may take its left or right sidebearing from another glyph
    for n, (src_l, src_r) in COPY.items():
        if n not in raw or raw[n][2] is None:
            continue
        spec, d, left, right, bb = raw[n]
        if src_l and src_l in raw:
            left = raw[src_l][2]
        if src_r and src_r in raw:
            right = raw[src_r][3]
        raw[n] = (spec, d, left, right, bb)
    out = {}
    for n, (spec, d, left, right, bb) in raw.items():
        if bb is None:
            adv = round(d.advance or 0)
            out[n] = Glyph(n, spec.unicodes, spec.zone, [], adv)
            continue
        xmin, _, xmax, _ = bb
        lsb, rsb = round(left), round(right)
        dx = lsb - xmin
        contours = [_round(c, dx) for c in d.contours]
        adv = round(lsb + (xmax - xmin) + rsb)
        anchors = {k: (round(x + dx), round(y)) for k, (x, y) in d.anchors.items()}
        out[n] = Glyph(n, spec.unicodes, spec.zone, contours, adv, lsb, rsb, anchors)
    return out
