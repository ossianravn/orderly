"""Spacing: sidebearings by an area method, then a table of hand adjustments.

In the manner of HT Letterspacer: in the glyph's zone (x-height for lowercase, cap height for capitals) the white
between the sidebearing line and the outline should be the same for every glyph. The outline's profile is measured
on horizontal scanlines from the glyph's own extreme, clipped to a depth, so white deep inside open shapes does
not count. The sidebearing then makes up the difference to the master's target area.
"""

from __future__ import annotations

from .geom import Contour
from .master import Master

# Hand adjustments in font units at the Regular weight, added to the computed sidebearing: name -> (left, right).
ADJUST: dict[str, tuple[float, float]] = {
    "J": (-15, 0),  # the open top left of J reads as a hole beside H
    "T": (-12, -12),  # the white under T's arms reads as a hole beside H in HHTHH
}

# Glyphs whose sidebearings copy another glyph's side: name -> (left source, right source); None keeps computed.
COPY: dict[str, tuple[str | None, str | None]] = {}


def zone(m: Master, z: str) -> tuple[float, float]:
    if z == "lc":
        return 0.0, m.xh
    return 0.0, m.cap


def profile(contours: list[Contour], y0: float, y1: float, step: float = 4.0):
    """Leftmost and rightmost outline x on each scanline between y0 and y1 (None where the line is empty)."""
    polys = [c.flat(32) for c in contours]
    rows = []
    y = y0 + step / 2
    while y < y1:
        xs = []
        for pts in polys:
            for a, b in zip(pts, pts[1:] + pts[:1]):
                if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                    xs.append(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
        rows.append((min(xs), max(xs)) if xs else None)
        y += step
    return rows, step


def bounds(contours: list[Contour]) -> tuple[float, float, float, float]:
    pts = [p for c in contours for p in c.flat(32)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def sidebearings(m: Master, name: str, z: str, contours: list[Contour]) -> tuple[float, float, float, float]:
    """Area-method sidebearings, measured from the outline's extremes inside the zone.

    Parts outside the zone (the hook of j below the baseline, the hook of f above the x-height) may reach into
    the sidebearing, as they do in hand-spaced fonts. Returns left, right and the zone extremes they hang from.
    """
    y0, y1 = zone(m, z)
    h = y1 - y0
    rows, step = profile(contours, y0, y1)
    filled = [r for r in rows if r]
    if filled:
        xmin, xmax = min(r[0] for r in filled), max(r[1] for r in filled)
    else:
        xmin, _, xmax, _ = bounds(contours)
    depth = m.sp_depth * h
    white_l = sum(min(r[0] - xmin, depth) if r else depth for r in rows) * step
    white_r = sum(min(xmax - r[1], depth) if r else depth for r in rows) * step
    target = m.sp_area * h * h
    left = (target - white_l) / h
    right = (target - white_r) / h
    dl, dr = ADJUST.get(name, (0.0, 0.0))
    return left + dl, right + dr, xmin, xmax
