"""The glyph registry. A glyph is a function of a master returning its drawing; spacing places it in its advance.

Glyph functions live in modules by family and register with @glyph. Each returns a Drawing whose contours sit at
any x; the spacing step measures the drawing and sets the sidebearings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..geom import Contour
from ..master import Master


@dataclass
class Drawing:
    contours: list[Contour]
    anchors: dict[str, tuple[float, float]] = field(default_factory=dict)
    advance: float | None = None  # fixed advance (space); otherwise spacing decides
    components: list[tuple[str, str | None]] = field(default_factory=list)  # composite: base, then (mark, anchor)


@dataclass(frozen=True)
class Spec:
    name: str
    unicodes: tuple[int, ...]
    zone: str  # spacing zone: "lc" lowercase, "uc" capitals, "fig" figures, "pun" punctuation
    fn: Callable[[Master], Drawing]


REGISTRY: dict[str, Spec] = {}


def glyph(name: str, uni: int | tuple[int, ...] | None, zone: str):
    unis = () if uni is None else (uni,) if isinstance(uni, int) else tuple(uni)

    def deco(fn: Callable[[Master], Drawing]):
        REGISTRY[name] = Spec(name, unis, zone, fn)
        return fn

    return deco


def load() -> dict[str, Spec]:
    """Import every glyph module (registration happens on import) and return the registry in drawing order."""
    from . import control, lc_arch, lc_diag, lc_round, lc_stem, uc_bowl, uc_diag, uc_round, uc_straight  # noqa: F401
    from . import figures, figures_round, nordic, punct  # noqa: F401
    from . import letters_extra, marks, quotes, symbols  # noqa: F401
    from . import composites  # noqa: F401  (last: composites refer to the glyphs above)

    return REGISTRY
