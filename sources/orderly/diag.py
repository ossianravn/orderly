"""Diagonal strokes: cut horizontally at both ends, measured square to the stroke.

A diagonal is given by its centre line between two heights and its weight square to the stroke at each end;
a weight that differs between the ends thins the stroke toward a join. Where two diagonals meet in an apex
(v w y A V W M) they are drawn as one polygon: outer edges, a flat apex, and the crotch where the inner edges
cross, so the apex is exactly as wide as asked and nothing pokes past it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .geom import Contour, Pt, intersect, quad, labelled


def hwidth(p0: Pt, p1: Pt, t: float) -> float:
    """Horizontal width of a stroke along p0-p1 whose weight square to the stroke is t."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    return t * math.hypot(dx, dy) / abs(dy)


@labelled("diagonal")
def stroke(p0: Pt, p1: Pt, t0: float, t1: float | None = None) -> Contour:
    """Diagonal from centre point p0 (lower) to p1 (upper), cut horizontally at both heights."""
    e = Edges.of(p0, p1, t0, t0 if t1 is None else t1)
    return quad(e.l0, e.r0, e.r1, e.l1)


@dataclass(frozen=True)
class Edges:
    """A diagonal's left and right edges, each from its lower end (0) to its upper end (1)."""

    l0: Pt
    l1: Pt
    r0: Pt
    r1: Pt

    @classmethod
    def of(cls, p0: Pt, p1: Pt, t0: float, t1: float) -> Edges:
        w0, w1 = hwidth(p0, p1, t0), hwidth(p0, p1, t1)
        return cls((p0[0] - w0 / 2, p0[1]), (p1[0] - w1 / 2, p1[1]), (p0[0] + w0 / 2, p0[1]), (p1[0] + w1 / 2, p1[1]))

    def contour(self) -> Contour:
        return quad(self.l0, self.r0, self.r1, self.l1)


def placed(bottom: tuple[str, float, float], top: tuple[str, float, float], t0: float, t1: float | None = None,
           ) -> Contour:
    """A diagonal placed by one edge point at each end: bottom and top are (edge, x, y), edge 'l', 'r' or 'c'.

    'l' puts the stroke's left edge through the point, 'r' its right edge, 'c' its centre line. The weights t0
    (bottom) and t1 (top) are square to the stroke; the centre line is solved so both constraints hold.
    """
    return edges(bottom, top, t0, t0 if t1 is None else t1).contour()


def edges(bottom: tuple[str, float, float], top: tuple[str, float, float], t0: float, t1: float) -> Edges:
    p0, p1 = centre(bottom, top, t0, t1)
    return Edges.of(p0, p1, t0, t1)


def centre(bottom: tuple[str, float, float], top: tuple[str, float, float], t0: float, t1: float) -> tuple[Pt, Pt]:
    """Centre line of a diagonal placed by edge points (see placed)."""
    sign = {"l": 1.0, "r": -1.0, "c": 0.0}
    cb, ct = bottom[1], top[1]
    for _ in range(12):
        p0, p1 = (cb, bottom[2]), (ct, top[2])
        cb = bottom[1] + sign[bottom[0]] * hwidth(p0, p1, t0) / 2
        ct = top[1] + sign[top[0]] * hwidth(p0, p1, t1) / 2
    return (cb, bottom[2]), (ct, top[2])


def cross(a0: Pt, a1: Pt, b0: Pt, b1: Pt) -> Pt:
    """Intersection of the lines a0-a1 and b0-b1."""
    p = intersect(a0, (a1[0] - a0[0], a1[1] - a0[1]), b0, (b1[0] - b0[0], b1[1] - b0[1]))
    assert p is not None, "parallel edges"
    return p


@labelled("diagonal")
def vee_poly(left: Edges, right: Edges) -> Contour:
    """V: left stroke falling to the apex, right stroke rising from it; flat apex between the outer edges."""
    c = cross(left.r0, left.r1, right.l0, right.l1)
    return quad(left.l1, left.l0, right.r0, right.r1, right.l1, c, left.r1)


@labelled("diagonal")
def peak_poly(left: Edges, right: Edges) -> Contour:
    """Inverted V (A): left stroke rising to the apex, right stroke falling from it; flat apex on top."""
    c = cross(left.r0, left.r1, right.l0, right.l1)
    return quad(left.l0, left.r0, c, right.l0, right.r0, right.r1, left.l1)


@labelled("diagonal")
def double_vee(s1: Edges, s2: Edges, s3: Edges, s4: Edges) -> Contour:
    """W: two vees sharing a middle apex at the top."""
    c12 = cross(s1.r0, s1.r1, s2.l0, s2.l1)
    c23 = cross(s2.r0, s2.r1, s3.l0, s3.l1)
    c34 = cross(s3.r0, s3.r1, s4.l0, s4.l1)
    return quad(s1.l1, s1.l0, s2.r0, c23, s3.l0, s4.r0, s4.r1, s4.l1, c34, s3.r1, s2.l1, c12, s1.r1)


@labelled("diagonal")
def branch(c0: Pt, c1: Pt, t0: float, t1: float, x_cut: float) -> Contour:
    """A diagonal from centre point c0 to c1, cut horizontally at c1 and vertically at x_cut near c0.

    Used where a diagonal ends inside a stem (k K): the vertical cut stays buried in the stem.
    """
    e = Edges.of(c0, c1, t0, t1)
    pa = (x_cut, y_at(e.l0, e.l1, x_cut))
    pb = (x_cut, y_at(e.r0, e.r1, x_cut))
    c = quad(pa, pb, e.r1, e.l1)
    return c if c.area() > 0 else c.reversed()


def y_at(p0: Pt, p1: Pt, x: float) -> float:
    return p0[1] + (p1[1] - p0[1]) * (x - p0[0]) / (p1[0] - p0[0])


def x_at(p0: Pt, p1: Pt, y: float) -> float:
    """x of the line p0-p1 at height y."""
    return p0[0] + (p1[0] - p0[0]) * (y - p0[1]) / (p1[1] - p0[1])
