"""A master is a set of numbers. Six masters ({Thin, Regular, Black} x {Text, Display}) differ only here.

Every glyph function reads its numbers from a Master and takes the same path through its code for every master,
so the masters are compatible by construction. Settled values live here; the design brief has the starting values.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import MappingProxyType


@dataclass(frozen=True)
class Master:
    name: str  # file-safe, e.g. "RegularDisplay"
    style: str  # human, e.g. "Regular Display"
    wght: int  # location on the weight axis
    opsz: int  # location on the optical-size axis

    # Vertical metrics (units per em 1000).
    cap: float = 700
    xh: float = 500
    asc: float = 740
    desc: float = -200
    over: float = 0.015  # rounds pass the flat lines by this fraction of the height they pass
    over_apex: float = 0.005  # flat apexes pass them by this fraction

    # Stroke weights.
    stem: float = 78  # lowercase vertical stem
    cstem: float = 84  # capital vertical stem
    bar: float = 70  # lowercase horizontal weight: bars, crossbars
    cbar: float = 76  # capital horizontal weight
    rside: float = 1.07  # side of a round (o, O at their vertical extremes) / the matching stem
    rtop: float = 1.03  # top and bottom of a round / the matching bar
    diag: float = 0.93  # diagonal stroke, measured square to the stroke / the matching stem
    fig: float = 0.98  # figure strokes / lowercase strokes, scaled toward the capitals

    # Curves.
    tension: float = 0.56  # outer edges: 0.552 is a circle, more is squarer
    tension_in: float = 0.56  # inner edges (counters)

    # Joins: where a curve enters a stem, the stroke narrows to (1 - join) of its weight.
    join: float = 0.24
    join_turn: float = 18.0  # degrees the outer edge swings toward the horizontal at a join (softer shoulder)
    bite: float = 0.45  # how far a counter's ellipse runs into the stem it joins, as a fraction of the stem
    ubar: float = 0.51  # centre of capital crossbars (H, E, F), as a fraction of the cap height
    apex: float = 0.32  # flat apex width of A V W M N v w, as a fraction of the stem
    diag_thin: float = 0.86  # diagonals narrow to this fraction of their weight where they meet

    # Apertures: where open rounds are cut, as an angle from the horizontal axis of their ellipse (degrees).
    ap_c: float = 42  # c e, upper and lower terminal
    ap_C: float = 40  # C G
    ap_s: float = 40  # s S figures

    # Dots: diameter / stem.
    dot: float = 1.2

    # Body widths (outer extremes, font units); each glyph reads its own.
    widths: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    # Spacing, area method: target white area per side as a fraction of the zone height squared, the depth
    # a profile may reach into an open shape (fraction of the zone height), and the overshoot of the zone.
    sp_area: float = 0.09
    sp_depth: float = 0.035
    sp_over: float = 0.0

    def w(self, key: str) -> float:
        return self.widths[key]

    def os(self, height: float) -> float:
        """Round overshoot for a shape of this flat height."""
        return round(height * self.over)

    def osa(self, height: float) -> float:
        return round(height * self.over_apex)


REGULAR_DISPLAY_WIDTHS = {
    # lowercase
    "o": 516, "n": 452, "m": 724, "b": 490, "a": 476, "c": 452, "e": 492, "s": 392, "r": 270,
    "v": 466, "w": 698, "x": 448, "y": 468, "z": 400, "k": 430, "t": 268, "f": 280, "j": 210,
    "i": 0, "l": 0,
    # capitals
    "O": 722, "H": 552, "C": 642, "G": 664, "D": 616, "Q": 722, "U": 560, "N": 590, "A": 664,
    "V": 664, "W": 940, "M": 700, "X": 616, "Y": 624, "Z": 560, "K": 576, "E": 456, "F": 440,
    "L": 432, "T": 548, "P": 528, "B": 532, "R": 556, "S": 492, "J": 420, "I": 0,
    # figures
    "zero": 500, "one": 300, "two": 466, "three": 456, "four": 512, "five": 458, "six": 486,
    "seven": 452, "eight": 486, "nine": 486,
}

REGULAR_DISPLAY = Master(
    name="RegularDisplay",
    style="Regular Display",
    wght=400,
    opsz=72,
    widths=MappingProxyType(REGULAR_DISPLAY_WIDTHS),
)


def scaled_master(base: Master, name: str, style: str, wght: int, stem_scale: float) -> Master:
    """A master with every weight scaled. Used only to prove compatibility, not a drawn master."""
    s = stem_scale
    return replace(
        base,
        name=name,
        style=style,
        wght=wght,
        stem=base.stem * s,
        cstem=base.cstem * s,
        bar=base.bar * s,
        cbar=base.cbar * s,
    )


MASTERS = [REGULAR_DISPLAY]
