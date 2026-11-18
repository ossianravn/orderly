"""Shared parts: the compass (ellipses), stems, joins, rings and transforms.

Every round in the font is an Ell: four on-curve extremes with horizontal and vertical handles and one tension.
Strokes are pairs of edges (outer and inner) that run the same way; a join carries both edges into a stem, where
the stroke narrows by the master's join value. Parts that meet a stem overlap it as separate contours.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .geom import Contour, Path, Pt, line, tcurve

CCW = "ENWS"
CCW_DIR = {"E": (0.0, 1.0), "N": (-1.0, 0.0), "W": (0.0, -1.0), "S": (1.0, 0.0)}


@dataclass(frozen=True)
class Ell:
    cx: float
    cy: float
    rx: float
    ry: float
    t: float = 0.56

    def p(self, k: str) -> Pt:
        return {
            "E": (self.cx + self.rx, self.cy),
            "N": (self.cx, self.cy + self.ry),
            "W": (self.cx - self.rx, self.cy),
            "S": (self.cx, self.cy - self.ry),
        }[k]

    def arc(self, *ks: str) -> Path:
        """Path through the named extremes, quadrant by quadrant (each step to a neighbouring extreme)."""
        path = Path()
        for a, b in zip(ks, ks[1:]):
            sign = 1.0 if CCW[(CCW.index(a) + 1) % 4] == b else -1.0
            da = (CCW_DIR[a][0] * sign, CCW_DIR[a][1] * sign)
            db = (CCW_DIR[b][0] * sign, CCW_DIR[b][1] * sign)
            path.add(tcurve(self.p(a), da, self.p(b), db, self.t))
        return path

    def inset(self, dx: float, dy: float, t: float | None = None) -> Ell:
        return Ell(self.cx, self.cy, self.rx - dx, self.ry - dy, self.t if t is None else t)

    def at_angle(self, deg: float) -> Pt:
        """Point on the true ellipse at a polar angle (for placing cuts; outlines use the arcs)."""
        a = math.radians(deg)
        return (self.cx + self.rx * math.cos(a), self.cy + self.ry * math.sin(a))


def box(x0: float, y0: float, x1: float, y1: float) -> Contour:
    """Counter-clockwise rectangle: a stem or a bar."""
    return Contour.of(line((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


def ring(eo: Ell, ei: Ell) -> list[Contour]:
    return [Contour.of(eo.arc("S", "E", "N", "W", "S")), Contour.of(ei.arc("S", "W", "N", "E", "S"))]


def disc(cx: float, cy: float, d: float, t: float = 0.56) -> Contour:
    e = Ell(cx, cy, d / 2, d / 2, t)
    return Contour.of(e.arc("S", "E", "N", "W", "S"))


@dataclass
class Join:
    """Where a stroke enters a stem edge at x = s: outer point and direction, inner point, and both stubs."""

    outer: Pt
    d: Pt  # outer edge direction, travelling away from the stem
    inner: Pt
    outer_in: Pt  # stubs, buried in the stem
    inner_in: Pt


def stem_join(inner_pt: Pt, inner_dir: Pt, s: float, depth: float, weight: float, side: int,
              turn: float = 0.0) -> Join:
    """Join an edge pair to the stem edge x = s.

    inner_pt is where the counter's edge crosses the stem edge and inner_dir its direction travelling away from
    the stem. The outer edge is placed so the stroke there measures `weight` square to the edges; `side` is +1
    when the outer edge lies above the inner (a top join) and -1 below. `turn` (degrees) swings the outer edge's
    direction toward the horizontal, which softens the shoulder.
    """
    a = math.atan2(inner_dir[1], inner_dir[0])
    a -= side * math.copysign(math.radians(turn), inner_dir[0])
    d = (math.cos(a), math.sin(a))
    dxa = max(abs(inner_dir[0]), 0.2)
    outer = (s, inner_pt[1] + side * weight / dxa)
    ko = depth / max(abs(d[0]), 0.2)
    ki = depth / dxa
    outer_in = (outer[0] - d[0] * ko, outer[1] - d[1] * ko)
    inner_in = (inner_pt[0] - inner_dir[0] * ki, inner_pt[1] - inner_dir[1] * ki)
    return Join(outer, d, inner_pt, outer_in, inner_in)


def neg(v: Pt) -> Pt:
    return (-v[0], -v[1])


def mirror_x(contours: list[Contour], axis: float) -> list[Contour]:
    """Mirror about the vertical line x = axis, keeping contour direction."""
    return [c.map(lambda p: (2 * axis - p[0], p[1])).reversed() for c in contours]


def mirror_y(contours: list[Contour], axis: float) -> list[Contour]:
    return [c.map(lambda p: (p[0], 2 * axis - p[1])).reversed() for c in contours]


def rotate180(contours: list[Contour], cx: float, cy: float) -> list[Contour]:
    return [c.map(lambda p: (2 * cx - p[0], 2 * cy - p[1])) for c in contours]


def shift(contours: list[Contour], dx: float, dy: float = 0.0) -> list[Contour]:
    return [c.map(lambda p: (p[0] + dx, p[1] + dy)) for c in contours]
