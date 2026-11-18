"""Open strokes: the hook of t f j g J, and the s curve of s S (and the figures that borrow it).

Both are edge pairs drawn through extremes with the compass and cut vertically at their terminals.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .geom import Contour, Path, line, tcurve
from .parts import Ell


def hook(x0: float, st: float, th: float, y_top: float, bot: float, rx: float, ry: float, x_cut: float,
         t: float, t_in: float) -> Contour:
    """A stem whose left edge is x0, running down from y_top and turning right along the bottom.

    The bottom outer extreme sits at y = bot; the curve's outer radii are rx, ry; the stroke is st wide in the
    stem and th thick at the bottom. The end is cut vertically at x_cut. Mirror it for j g J, flip it for f.
    """
    cx, cy = x0 + rx, bot + ry
    eo = Ell(cx, cy, rx, ry, t)
    ei = Ell(cx, cy, rx - st, ry - th, t_in)
    outer = line((x0, y_top), eo.p("W")).then(eo.arc("W", "S", "E")).cut_x(x_cut, "head", -1)
    inner = line((x0 + st, y_top), ei.p("W")).then(ei.arc("W", "S", "E")).cut_x(x_cut, "head", -1)
    return Contour.of(outer, line(outer.end, inner.end), inner.reversed())


Node = tuple[tuple[float, float], tuple[float, float], float]


def offsets(nodes: list[Node], tens: list[tuple[float, float]], left_scale: float = 1.0) -> tuple[Path, Path]:
    """Both edges of a stroke drawn along a skeleton.

    Each node is (point, unit direction of travel, weight). The edges are the nodes offset square to the
    direction by half the weight, joined by tension curves; the left edge (left of travel) may use scaled
    tensions. Returns (left, right).
    """

    def edge(side: int, scale: float) -> Path:
        pts = [((p[0] - side * d[1] * w / 2, p[1] + side * d[0] * w / 2), d) for p, d, w in nodes]
        path = Path()
        for (p0, d0), (p1, d1), (t0, t1) in zip(pts, pts[1:], tens):
            path.add(tcurve(p0, d0, p1, d1, t0 * scale, t1 * scale))
        return path

    return edge(1, left_scale), edge(-1, 1.0)


@dataclass(frozen=True)
class SSpec:
    """The numbers of one s: box, weights and shape."""

    x0: float
    w: float  # width of the lower bowl (the widest part)
    bot: float  # outer bottom extreme (with overshoot)
    top: float  # outer top extreme (with overshoot)
    ym: float  # height of the spine's centre (the optical centre)
    upper: float  # upper bowl width / lower bowl width
    th: float  # top and bottom thickness
    side: float  # thickness at the side extremes
    spine: float  # spine thickness, square to the stroke (the heaviest part)
    ap: float  # terminal cut, degrees from each counter's horizontal axis (as c and C)
    t: float
    t_in: float
    hu: float = 0.72  # upper bowl's left extreme: fraction of the height
    hl: float = 0.28  # lower bowl's right extreme: fraction of the height
    lean: float = 0.0  # upper bowl's centre lies this far right of the lower bowl's
    steep: float = 0.8  # spine angle: fraction of the steepest the bowls allow
    t_bowl: float = 0.72  # tension where the spine leaves a bowl: high keeps the bowl round past its extreme
    t_mid: float = 0.4  # tension at the spine's centre: low keeps the passage short, with no straight run


def s_curve(s: SSpec) -> Contour:
    """Two stacked rounds joined by a short curved spine, drawn from a skeleton.

    The skeleton runs through seven nodes: the upper round's east, north and west extremes, the spine's centre,
    the lower round's east, south and west extremes. Each node has a direction and a weight; both edges are the
    nodes offset square to the direction, joined by tension curves. Terminals are vertical cuts. The same seven
    nodes in every master keep the s compatible from Thin to Black.
    """
    h = s.top - s.bot
    yn, ys = s.top - s.th / 2, s.bot + s.th / 2
    cyu, cyl = s.bot + h * s.hu, s.bot + h * s.hl
    rl = (s.w - s.side) / 2
    ru = (s.w * s.upper - s.side) / 2
    cl = s.x0 + s.w / 2
    cu = cl + s.lean
    mx = (cu - ru + cl + rl) / 2
    reach = min(cyu - s.ym, s.ym - cyl) / (mx - (cu - ru))
    a = math.atan(s.steep * reach)
    nodes = [
        ((cu + ru, cyu), (0.0, 1.0), s.side),
        ((cu, yn), (-1.0, 0.0), s.th),
        ((cu - ru, cyu), (0.0, -1.0), s.side),
        ((mx, s.ym), (math.cos(a), -math.sin(a)), s.spine),
        ((cl + rl, cyl), (0.0, -1.0), s.side),
        ((cl, ys), (-1.0, 0.0), s.th),
        ((cl - rl, cyl), (0.0, 1.0), s.side),
    ]
    tens = [(s.t, s.t), (s.t, s.t), (s.t_bowl, s.t_mid), (s.t_mid, s.t_bowl), (s.t, s.t), (s.t, s.t)]

    left, right = offsets(nodes, tens, s.t_in / s.t)  # left of travel: the counters' side of each round
    x1 = cu + (ru - s.side / 2) * math.cos(math.radians(s.ap))
    x2 = cl - (rl - s.side / 2) * math.cos(math.radians(s.ap))
    left = left.cut_x(x1, "tail", 0).cut_x(x2, "head", -1)
    right = right.cut_x(x1, "tail", 0).cut_x(x2, "head", -1)
    c = Contour.of(right, line(right.end, left.end), left.reversed())
    return c if c.area() > 0 else c.reversed()
