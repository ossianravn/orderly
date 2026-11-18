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
    from . import control  # noqa: F401

    return REGISTRY
