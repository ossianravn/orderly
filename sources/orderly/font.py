"""Run every glyph function for a master, space the results, round them to the grid, place anchors, and assemble
composites (base plus marks, placed anchor to anchor)."""

from __future__ import annotations

from dataclasses import dataclass, field

from .geom import Contour
from .glyphs import load
from .master import Master
from .spacing import COPY, sidebearings


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
    components: list[tuple[str, int, int]] = field(default_factory=list)  # (glyph, dx, dy)

    def outline(self, glyphs: dict[str, Glyph]) -> list[Contour]:
        """Contours with components resolved (for proofs and the site's data)."""
        out = list(self.contours)
        for name, dx, dy in self.components:
            out += [c.map(lambda p, dx=dx, dy=dy: (p[0] + dx, p[1] + dy)) for c in glyphs[name].outline(glyphs)]
        return out


def _round(c: Contour, dx: float) -> Contour:
    return c.map(lambda p: (round(p[0] + dx), round(p[1])))


def _auto_anchors(m: Master, g: Glyph) -> dict[str, tuple[int, int]]:
    """top and bottom over the middle of the glyph's extent; ogonek near its right foot."""
    pts = [p for c in g.contours for p in c.flat(8)]
    if not pts:
        return {}
    xs = [p[0] for p in pts if 0 <= p[1] <= (m.xh if g.zone == "lc" else m.cap)] or [p[0] for p in pts]
    x0, x1 = min(xs), max(xs)
    top = m.xh if g.zone == "lc" else m.cap
    cx = round((x0 + x1) / 2)
    st = m.stem if g.zone == "lc" else m.cstem
    return {"top": (cx, round(top)), "bottom": (cx, 0), "ogonek": (round(x1 - st * 0.45), 0),
            "caronalt": (round(x1 + m.xh * 0.08), round(m.asc))}


def build(m: Master, only: list[str] | None = None) -> dict[str, Glyph]:
    specs = load()
    names = [n for n in specs if only is None or n in only]
    raw, drawn = {}, {}
    for n in names:
        spec = specs[n]
        d = spec.fn(m)
        drawn[n] = d
        if d.components or spec.zone == "mark" or d.advance is not None or not d.contours:
            continue
        left, right, zx0, zx1 = sidebearings(m, n, spec.zone, d.contours)
        raw[n] = [left, right, zx0, zx1]
    for n, (src_l, src_r) in COPY.items():
        if n in raw:
            if src_l in raw:
                raw[n][0] = raw[src_l][0]
            if src_r in raw:
                raw[n][1] = raw[src_r][1]
    out: dict[str, Glyph] = {}
    for n in names:
        spec, d = specs[n], drawn[n]
        if d.components:
            continue
        if spec.zone == "mark":  # combining marks: no advance, drawn about x = 0
            out[n] = Glyph(n, spec.unicodes, spec.zone, [_round(c, 0) for c in d.contours], 0,
                           anchors={k: (round(x), round(y)) for k, (x, y) in d.anchors.items()})
            continue
        if n not in raw:
            out[n] = Glyph(n, spec.unicodes, spec.zone, [_round(c, 0) for c in d.contours], round(d.advance or 0))
            continue
        left, right, xmin, xmax = raw[n]
        lsb, rsb = round(left), round(right)
        dx = lsb - xmin
        g = Glyph(n, spec.unicodes, spec.zone, [_round(c, dx) for c in d.contours], round(lsb + (xmax - xmin) + rsb),
                  lsb, rsb)
        g.anchors = {**_auto_anchors(m, g), **{k: (round(x + dx), round(y)) for k, (x, y) in d.anchors.items()}}
        out[n] = g
    for n in names:  # composites, once their parts exist
        d = drawn[n]
        if d.components:
            out[n] = _compose(n, specs[n], d.components, out)
    return out


def _compose(n: str, spec, parts: list[tuple[str, str | None]], glyphs: dict[str, Glyph]) -> Glyph:
    """Base first; each mark's `_name` anchor lands on the `name` anchor of the base, or of the previous mark."""
    base = glyphs[parts[0][0]]
    comps = [(base.name, 0, 0)]
    anchors = dict(base.anchors)
    for mark, at in parts[1:]:
        mk = glyphs[mark]
        if at is None:
            comps.append((mark, 0, 0))
            continue
        ax, ay = anchors[at]
        mx, my = mk.anchors["_" + at]
        dx, dy = ax - mx, ay - my
        comps.append((mark, dx, dy))
        if at in mk.anchors:  # stacking: the next mark sits on this one
            anchors[at] = (mk.anchors[at][0] + dx, mk.anchors[at][1] + dy)
    return Glyph(n, spec.unicodes, spec.zone, [], base.advance, base.lsb, base.rsb, anchors, comps)
