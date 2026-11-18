"""Paths, contours and curves. Font units, y up. Filled contours run counter-clockwise, counters clockwise.

A Path is an open run of segments: a line is (p0, p1), a cubic is (p0, c1, c2, p1). Contours are closed Paths.
Curves are drawn the way type designers draw them: on-curve points at extremes with horizontal or vertical
handles, and one tension value setting each handle's length as a fraction of the way to the tangent intersection.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

Pt = tuple[float, float]


def lerp(a: Pt, b: Pt, t: float) -> Pt:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def unit(v: Pt) -> Pt:
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n)


def intersect(p: Pt, d: Pt, q: Pt, e: Pt) -> Pt | None:
    """Intersection of the lines p + s*d and q + u*e."""
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-9:
        return None
    s = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    return (p[0] + s * d[0], p[1] + s * d[1])


def tcurve(p0: Pt, d0: Pt, p1: Pt, d1: Pt, t: float, t1: float | None = None) -> tuple[Pt, Pt, Pt, Pt]:
    """Cubic leaving p0 in direction d0 and arriving at p1 travelling in direction d1.

    Each handle runs a fraction t of the way from its point to the tangent intersection (0.552 draws a circle).
    """
    t1 = t if t1 is None else t1
    i = intersect(p0, d0, p1, d1)
    if i is None or (i[0] - p0[0]) * d0[0] + (i[1] - p0[1]) * d0[1] <= 0:
        k = math.dist(p0, p1) / 3
        return (p0, (p0[0] + d0[0] * k, p0[1] + d0[1] * k), (p1[0] - d1[0] * k, p1[1] - d1[1] * k), p1)
    return (p0, lerp(p0, i, t), lerp(p1, i, t1), p1)


def bez(seg, t: float) -> Pt:
    if len(seg) == 2:
        return lerp(seg[0], seg[1], t)
    p0, c1, c2, p1 = seg
    u = 1 - t
    return (
        u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p1[0],
        u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p1[1],
    )


def tangent(seg, t: float) -> Pt:
    if len(seg) == 2:
        return unit((seg[1][0] - seg[0][0], seg[1][1] - seg[0][1]))
    p0, c1, c2, p1 = seg
    u = 1 - t
    dx = 3 * (u * u * (c1[0] - p0[0]) + 2 * u * t * (c2[0] - c1[0]) + t * t * (p1[0] - c2[0]))
    dy = 3 * (u * u * (c1[1] - p0[1]) + 2 * u * t * (c2[1] - c1[1]) + t * t * (p1[1] - c2[1]))
    if abs(dx) + abs(dy) < 1e-9:
        return unit((p1[0] - p0[0], p1[1] - p0[1]))
    return unit((dx, dy))


def split(seg, t: float):
    if len(seg) == 2:
        m = lerp(seg[0], seg[1], t)
        return (seg[0], m), (m, seg[1])
    p0, c1, c2, p1 = seg
    a, b, c = lerp(p0, c1, t), lerp(c1, c2, t), lerp(c2, p1, t)
    d, e = lerp(a, b, t), lerp(b, c, t)
    m = lerp(d, e, t)
    return (p0, a, d, m), (m, e, c, p1)


def roots(seg, axis: int, v: float) -> list[float]:
    """Parameters where a segment crosses coordinate v on an axis (0 = x, 1 = y), in order."""
    n = 96
    out: list[float] = []
    prev = bez(seg, 0)[axis] - v
    if abs(prev) < 1e-9:
        out.append(0.0)
    for i in range(1, n + 1):
        t = i / n
        cur = bez(seg, t)[axis] - v
        if abs(cur) < 1e-9:
            out.append(t)
        elif abs(prev) >= 1e-9 and (prev < 0) != (cur < 0):
            lo, hi, flo = (i - 1) / n, t, prev
            for _ in range(60):
                mid = (lo + hi) / 2
                fm = bez(seg, mid)[axis] - v
                if (flo < 0) != (fm < 0):
                    hi = mid
                else:
                    lo, flo = mid, fm
            out.append((lo + hi) / 2)
        prev = cur
    return out


@dataclass
class Path:
    segs: list = field(default_factory=list)

    @property
    def start(self) -> Pt:
        return self.segs[0][0]

    @property
    def end(self) -> Pt:
        return self.segs[-1][-1]

    def to(self, p: Pt) -> Path:
        """Straight line from the end to p."""
        if math.dist(self.end, p) > 1e-6:
            self.segs.append((self.end, p))
        return self

    def add(self, seg) -> Path:
        if self.segs and math.dist(self.end, seg[0]) > 1e-6:
            self.to(seg[0])
        self.segs.append(tuple(seg))
        return self

    def then(self, other: Path) -> Path:
        for s in other.segs:
            self.add(s)
        return self

    def reversed(self) -> Path:
        return Path([tuple(reversed(s)) for s in reversed(self.segs)])

    def map(self, fn) -> Path:
        return Path([tuple(fn(p) for p in s) for s in self.segs])

    def crossings(self, axis: int, v: float) -> list[tuple[int, float]]:
        """Every crossing of coordinate v (0 = x, 1 = y) as (segment index, t), in path order."""
        out: list[tuple[int, float]] = []
        for i, s in enumerate(self.segs):
            for t in roots(s, axis, v):
                if out and t < 1e-6 and out[-1][0] == i - 1 and out[-1][1] > 1 - 1e-6:
                    continue
                out.append((i, t))
        return out

    def piece(self, a: tuple[int, float] | None, b: tuple[int, float] | None) -> Path:
        """Sub-path between two positions (segment index, t); None is the path's start or end."""
        segs = self.segs
        a = a or (0, 0.0)
        b = b or (len(segs) - 1, 1.0)
        if a[0] == b[0]:
            head = split(segs[a[0]], b[1])[0] if b[1] < 1 else segs[a[0]]
            return Path([split(head, a[1] / b[1])[1] if a[1] > 0 else head])
        first = split(segs[a[0]], a[1])[1] if a[1] > 0 else segs[a[0]]
        last = split(segs[b[0]], b[1])[0] if b[1] < 1 else segs[b[0]]
        return Path([first] + list(segs[a[0] + 1 : b[0]]) + [last])

    def cut(self, axis: int, v: float, keep: str, nth: int = 0) -> Path:
        """Split at the nth crossing of coordinate v (0 = x, 1 = y); keep 'head' (before) or 'tail' (after)."""
        cs = self.crossings(axis, v)
        if len(cs) <= nth:
            raise ValueError(f"path does not cross {'xy'[axis]}={v:.1f} {nth + 1} times")
        return self.piece(None, cs[nth]) if keep == "head" else self.piece(cs[nth], None)

    def between(self, axis: int, v: float, i0: int = 0, i1: int = -1) -> Path:
        """The part between two crossings of coordinate v."""
        cs = self.crossings(axis, v)
        return self.piece(cs[i0], cs[i1])

    def cut_x(self, x: float, keep: str, nth: int = 0) -> Path:
        return self.cut(0, x, keep, nth)

    def cut_y(self, y: float, keep: str, nth: int = 0) -> Path:
        return self.cut(1, y, keep, nth)

    def at(self, pos: tuple[int, float]) -> tuple[Pt, Pt]:
        """Point and unit tangent at a position (segment index, t)."""
        s = self.segs[pos[0]]
        return bez(s, pos[1]), tangent(s, pos[1])

    def end_tangent(self) -> Pt:
        return tangent(self.segs[-1], 1.0)

    def start_tangent(self) -> Pt:
        return tangent(self.segs[0], 0.0)


def labelled(name: str):
    """Decorator: the contours a shape function returns carry this part name (for the site's outline data)."""

    def deco(fn):
        def wrap(*args, **kwargs):
            out = fn(*args, **kwargs)
            first = out[0] if isinstance(out, tuple) else out
            for c in first if isinstance(first, list) else [first]:
                if isinstance(c, Contour) and c.part is None:
                    c.part = name
            return out

        wrap.__name__, wrap.__doc__ = fn.__name__, fn.__doc__
        return wrap

    return deco


def chain(*paths: Path) -> Path:
    """Join paths end to start, bridging gaps with straight lines."""
    out = Path()
    for p in paths:
        out.then(p)
    return out


def line(*pts: Pt) -> Path:
    path = Path()
    for a, b in zip(pts, pts[1:]):
        path.add((a, b))
    return path


@dataclass
class Contour:
    segs: list
    part: str | None = None  # what the shape is (stem, bar, round, counter, arch, bowl, hook, diagonal, dot...)

    @classmethod
    def of(cls, *paths: Path) -> Contour:
        p = chain(*paths)
        p.to(p.start)
        return cls(p.segs)

    def map(self, fn) -> Contour:
        return Contour([tuple(fn(p) for p in s) for s in self.segs], self.part)

    def reversed(self) -> Contour:
        return Contour([tuple(reversed(s)) for s in reversed(self.segs)], self.part)

    def area(self) -> float:
        """Signed area, positive when counter-clockwise (curves flattened)."""
        pts = [bez(s, i / 16) for s in self.segs for i in range(16 if len(s) == 4 else 1)]
        return 0.5 * sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))

    def flat(self, steps: int = 24) -> list[Pt]:
        return [bez(s, i / steps) for s in self.segs for i in range(steps if len(s) == 4 else 1)]


def rect(x0: float, y0: float, x1: float, y1: float) -> Contour:
    """Counter-clockwise rectangle."""
    return Contour.of(line((x0, y0), (x1, y0), (x1, y1), (x0, y1)))


def quad(*pts: Pt) -> Contour:
    """Closed polygon from points, in the order given."""
    return Contour.of(line(*pts))
