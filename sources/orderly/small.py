"""Small forms: superiors, numerators, denominators, inferiors, ordinals, and the letters inside © ® ™ and №.

A small form is drawn by the ordinary glyph function from a master scaled down by `k`. Its strokes are scaled
less (`k * heavy`), so small forms keep the colour of the text instead of turning faint; widths grow by the
strokes' extra weight the same way the weight masters' widths do. `heavy` is a master number (`small.heavy`):
the Thin needs more help than the Black, whose counters would close.
"""

from __future__ import annotations

from dataclasses import replace
from types import MappingProxyType

from .geom import Contour
from .master import Master
from .parts import shift
from .spacing import sidebearings
from .weights import VSTEMS

FIGURES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
SUP = 0.6  # superiors, numerators, denominators, inferiors: height / cap height
INF_DROP = 0.14  # inferiors: bottom this far under the baseline / cap height

_cache: dict = {}


def small(m: Master, k: float = SUP) -> Master:
    """The master scaled to k of its size, strokes heavier than the scale by the master's `small.heavy`."""
    key = (id(m), k)
    if key not in _cache:
        sk = k * m.g("small.heavy")

        def width(n: str, w: float) -> float:
            cap = n[:1].isupper() or n in FIGURES or n == "ampersand"
            return w * k + VSTEMS.get(n, 1.0) * (m.cstem if cap else m.stem) * (sk - k)

        _cache[key] = (m, replace(
            m, name=f"{m.name}-small", cap=m.cap * k, xh=m.xh * k, asc=m.asc * k, desc=m.desc * k,
            stem=m.stem * sk, cstem=m.cstem * sk, bar=m.bar * sk, cbar=m.cbar * sk,
            widths=MappingProxyType({n: width(n, w) for n, w in m.widths.items()}),
        ))
    return _cache[key][1]


def bounds_x(contours: list[Contour]) -> tuple[float, float]:
    xs = [p[0] for c in contours for p in c.flat(6)]
    return min(xs), max(xs)


def spaced(sm: Master, name: str, zone: str, contours: list[Contour], loose: float = 1.1,
           dy: float = 0.0) -> tuple[list[Contour], float]:
    """Contours placed in their own advance by the small master's area spacing (a little looser, as small type
    wants), moved up by dy. Returns the contours and the advance."""
    left, right, x0, x1 = sidebearings(sm, name, zone, contours)
    left, right = left * loose, right * loose
    return shift(contours, left - x0, dy), left + (x1 - x0) + right
