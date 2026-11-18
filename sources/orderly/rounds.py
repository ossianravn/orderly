"""Rounds that meet stems: bowls (b d p q a g), arches (n h m r u) and cut rounds (c e C G S).

A stroke is an outer and an inner edge. Where it enters a stem the inner (counter) edge is cut by the stem's
edge, which may be straight (x = s) or curved (another arch's shoulder, in m), and the outer edge is placed so the
stroke there measures the join weight. Both edges continue a little way into the stem, where they close.
"""

from __future__ import annotations

import math

from .geom import Contour, Path, Pt, bez, line, split, tcurve
from .parts import Ell, Join, neg, stem_join


def _flat(path: Path, steps: int = 160) -> list[tuple[Pt, int, float]]:
    out = []
    for i, s in enumerate(path.segs):
        n = steps if len(s) == 4 else 1
        for k in range(n + 1):
            if k == 0 and out:
                continue
            out.append((bez(s, k / n), i, k / n))
    return out


def meet(a: Path, b: Path) -> list[tuple[tuple[int, float], tuple[int, float], Pt]]:
    """Crossings of two paths: (position on a, position on b, point), in order along a."""
    fa, fb = _flat(a), _flat(b)
    hits = []
    for j in range(len(fa) - 1):
        p, q = fa[j][0], fa[j + 1][0]
        for k in range(len(fb) - 1):
            r, s = fb[k][0], fb[k + 1][0]
            d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
            if abs(d) < 1e-12:
                continue
            u = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
            v = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / d
            if 0 <= u < 1 and 0 <= v < 1:
                ia = (fa[j][1], fa[j][2] + u * ((fa[j + 1][2] if fa[j + 1][1] == fa[j][1] else 1.0) - fa[j][2]))
                ib = (fb[k][1], fb[k][2] + v * ((fb[k + 1][2] if fb[k + 1][1] == fb[k][1] else 1.0) - fb[k][2]))
                hits.append((ia, ib, (p[0] + u * (q[0] - p[0]), p[1] + u * (q[1] - p[1]))))
    return hits


def tangent_from(path: Path, p: Pt, nth: int = 0) -> tuple[int, float]:
    """Position on a path where the line from p touches it (the nth such point along the path)."""
    from .geom import tangent

    def f(i: int, t: float) -> float:
        q, d = bez(path.segs[i], t), tangent(path.segs[i], t)
        return (q[0] - p[0]) * d[1] - (q[1] - p[1]) * d[0]

    found = 0
    for i, s in enumerate(path.segs):
        n = 64
        prev = f(i, 0.0)
        for k in range(1, n + 1):
            cur = f(i, k / n)
            if (prev < 0) != (cur < 0):
                lo, hi = (k - 1) / n, k / n
                for _ in range(50):
                    mid = (lo + hi) / 2
                    if (f(i, lo) < 0) != (f(i, mid) < 0):
                        hi = mid
                    else:
                        lo = mid
                if found == nth:
                    return i, (lo + hi) / 2
                found += 1
            prev = cur
    raise ValueError("no tangent from point")


def join_into(inner: Path, host: float | Path, at_start: bool, weight: float, depth: float, side: int,
              turn: float, limit: tuple[float, float] | None = None) -> tuple[Path, Join]:
    """Cut the inner edge where it meets the host stem edge and place the outer edge for the join weight.

    at_start: the join is at the start of `inner` (the edge then runs away from the stem); otherwise at its end.
    Returns the trimmed inner edge and the Join.
    """
    if isinstance(host, (int, float)):
        cs = inner.crossings(0, host)
        pos = cs[0] if at_start else cs[-1]
        trimmed = inner.piece(pos, None) if at_start else inner.piece(None, pos)
        pt, tan = inner.at(pos)
        away = tan if at_start else neg(tan)
        return trimmed, stem_join(pt, away, host, depth, weight, side, turn, limit)
    hits = meet(inner, host)
    ia, ib, pt = hits[0] if at_start else hits[-1]
    trimmed = inner.piece(ia, None) if at_start else inner.piece(None, ia)
    _, tan = inner.at(ia)
    away = tan if at_start else neg(tan)
    a = math.atan2(away[1], away[0]) - side * math.copysign(math.radians(turn), away[0])
    d = (math.cos(a), math.sin(a))
    # walk the host edge from the crotch toward the outer side until the stroke measures `weight`
    flat = _flat(host)
    k0 = min(range(len(flat)), key=lambda k: math.dist(flat[k][0], pt))
    step = 1 if (flat[min(k0 + 1, len(flat) - 1)][0][1] - pt[1]) * side > 0 else -1
    outer = pt
    k = k0
    while 0 <= k < len(flat):
        q = flat[k][0]
        dist = abs((q[0] - pt[0]) * away[1] - (q[1] - pt[1]) * away[0])
        outer = q
        hi = limit[1] if limit is not None else 1e9  # on a shoulder (m) only the corner bound applies
        if dist >= weight or q[1] >= hi:
            break
        k += step
    depth *= 0.5  # a curved host is a shoulder, not a stem: bury the stubs less deep
    ko = depth / max(abs(d[0]), 0.2)
    ki = depth / max(abs(away[0]), 0.2)
    j = Join(outer, d, pt, (outer[0] - d[0] * ko, outer[1] - d[1] * ko), (pt[0] - away[0] * ki, pt[1] - away[1] * ki))
    return trimmed, j


def shoulder(j: Join, top: Pt, t: float) -> Path:
    """Outer edge from a join up to a horizontal top extreme (the shoulder of n, the top of b).

    The edge leaves the stem at between 1.6 and 2 times the angle of its chord to the top (2 is a circular arc),
    so the shoulder is one round arc. Steeper, it climbs and turns sharply; at the chord's own angle the curve
    goes straight and breaks at the top. Either is the beak heavy joins otherwise grow.
    """
    sense = 1.0 if top[0] > j.outer[0] else -1.0
    a_d = math.atan2(abs(j.d[1]), abs(j.d[0]))
    a_c = math.atan2(abs(top[1] - j.outer[1]), abs(top[0] - j.outer[0]))
    a = min(max(a_d, 1.6 * a_c), 2.0 * a_c)
    d = (math.copysign(math.cos(a), j.d[0]), math.copysign(math.sin(a), j.d[1]))
    return Path([tcurve(j.outer, d, top, (sense, 0.0), t)])


def arch(eo: Ell, ei: Ell, host: float | Path, base: float, w_join: float, depth: float, turn: float,
         t: float, limit: tuple[float, float] | None = None) -> tuple[Contour, Path]:
    """n-shoulder: joins a stem on the left, rises to the top, and comes down as a straight stem to y = base.

    Returns the contour and its outer right edge (the host for a following arch, as in m).
    """
    inner = ei.arc("W", "N", "E")
    inner, j = join_into(inner, host, True, w_join, depth, +1, turn, limit)
    xr, xri = eo.p("E")[0], ei.p("E")[0]
    inner.to((xri, base))
    outer = shoulder(j, eo.p("N"), t).then(eo.arc("N", "E")).to((xr, base))
    c = Contour.of(outer.reversed(), line(j.outer, j.outer_in, j.inner_in, j.inner), inner)
    return c, outer


def arm(eo: Ell, ei: Ell, s: float, x_cut: float, w_join: float, depth: float, turn: float, t: float,
        limit: tuple[float, float] | None = None) -> Contour:
    """The arm of r: the n's shoulder from the stem, over the top, cut vertically at x_cut."""
    inner = ei.arc("W", "N", "E")
    inner, j = join_into(inner, s, True, w_join, depth, +1, turn, limit)
    inner = inner.cut_x(x_cut, "head", -1)
    outer = shoulder(j, eo.p("N"), t).then(eo.arc("N", "E")).cut_x(x_cut, "head", -1)
    return Contour.of(outer.reversed(), line(j.outer, j.outer_in, j.inner_in, j.inner), inner)


def bowl(eo: Ell, ei: Ell, s: float, w_top: float, w_bot: float, depth: float, turn: float, t: float,
         top_limit: tuple[float, float] | None = None, bot_limit: tuple[float, float] | None = None) -> Contour:
    """A round joined at top and bottom to a stem whose right edge is x = s (the bowl of b and p)."""
    inner = ei.arc("W", "N", "E", "S", "W")
    cs = inner.crossings(0, s)
    inner = inner.piece(cs[0], cs[-1])
    pt, tan = inner.at((0, 0.0))
    jt = stem_join(pt, tan, s, depth, w_top, +1, turn, top_limit)
    pb, tb = inner.at((len(inner.segs) - 1, 1.0))
    jb = stem_join(pb, neg(tb), s, depth, w_bot, -1, turn, bot_limit)
    top = shoulder(jt, eo.p("N"), t)
    bottom = shoulder(jb, eo.p("S"), t).reversed()
    outer = top.then(eo.arc("N", "E", "S")).then(bottom)
    return Contour.of(
        line(jb.outer_in, jb.outer), outer.reversed(), line(jt.outer, jt.outer_in, jt.inner_in, jt.inner), inner,
        line(jb.inner, jb.inner_in),
    )


def cut_round(eo: Ell, ei: Ell, x_top: float, x_bot: float) -> Contour:
    """A round opened on the right by two vertical cuts (c, C): upper terminal at x_top, lower at x_bot."""
    outer = eo.arc("E", "N", "W", "S", "E")
    inner = ei.arc("E", "N", "W", "S", "E")
    oc, ic = outer.crossings(0, x_top), inner.crossings(0, x_top)
    ob, ib = outer.crossings(0, x_bot), inner.crossings(0, x_bot)
    o = outer.piece(oc[0], ob[-1])
    i = inner.piece(ic[0], ib[-1])
    return Contour.of(o, line(o.end, i.end), i.reversed())


def terminal_cut(path_o: Path, path_i: Path, x: float, keep: str) -> tuple[Path, Path]:
    """Cut an edge pair at the vertical line x (a vertical terminal)."""
    return path_o.cut_x(x, keep), path_i.cut_x(x, keep)
