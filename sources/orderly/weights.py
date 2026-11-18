"""The weight masters of the Display design: Thin and Black, derived from Regular by their own numbers.

A master differs from Regular only in numbers. Widths grow with the stem by how many vertical strokes a glyph
carries across its width (`VSTEMS`), scaled by how much of the extra weight the counters give up (`k`); rounds
grow less, so O stays near a circle and its counter goes oval. Per-letter numbers that cannot scale with the stem
(hook radii, bar heights, apertures, ring sizes) are set per master in `*_PARAMS`.
"""

from __future__ import annotations

from dataclasses import replace
from types import MappingProxyType

from .master import REGULAR_DISPLAY, REGULAR_DISPLAY_PARAMS, REGULAR_DISPLAY_WIDTHS, Master

# Vertical strokes a glyph carries across its width (rounds count less: their counters go oval instead).
VSTEMS = {
    "o": 1.0, "n": 2, "m": 3, "b": 2, "a": 1.6, "c": 1.0, "e": 1.0, "s": 2.0, "r": 1.0, "v": 1.6, "w": 2.6,
    "x": 1.6, "y": 1.6, "z": 1.3, "k": 1.6, "t": 0.6, "f": 0.6, "j": 0.6, "a.ss01": 2.4,
    "O": 0.4, "H": 2, "C": 0.4, "G": 0.6, "D": 1.2, "Q": 0.4, "U": 2, "N": 2.4, "A": 1.6, "V": 1.6, "W": 2.8,
    "M": 3.0, "X": 1.6, "Y": 1.4, "Z": 1.4, "K": 1.8, "E": 1.2, "F": 1.1, "L": 1.0, "T": 1.0, "P": 1.8, "B": 2.0,
    "R": 2.0, "S": 2.0, "J": 1.2, "AE.leg": 0.8,
    "zero": 1.4, "one": 1.0, "two": 1.4, "three": 1.5, "four": 1.6, "five": 1.5, "six": 1.4, "seven": 1.2,
    "eight": 1.4, "nine": 1.4,
    "question": 1.8, "hyphen": 0.5, "paren": 0.4, "slash": 0.8, "ampersand": 2.6,
}


def derived_widths(base: Master, stem: float, cstem: float, k: float, extra: dict | None = None) -> MappingProxyType:
    out = {}
    for name, w in REGULAR_DISPLAY_WIDTHS.items():
        if w == 0:
            out[name] = 0
            continue
        cap = name[:1].isupper() or name in ("zero", "one", "two", "three", "four", "five", "six", "seven",
                                             "eight", "nine", "ampersand")
        d = (cstem - base.cstem) if cap else (stem - base.stem)
        out[name] = round(w + VSTEMS.get(name, 1.0) * d * k + (extra or {}).get(name, 0))
    return MappingProxyType(out)


# Black letters whose counters or arms need more room than the stroke count gives them.
BLACK_EXTRA = {"a": 36, "a.ss01": -40, "r": 24, "two": 56, "three": 70, "five": 56, "four": 40, "question": 30,
               "s": 16, "S": 16}


THIN_PARAMS = {
    **REGULAR_DISPLAY_PARAMS,
    "e.drop": 0.02,
    "t.left": 3.2, "t.right": 5.0, "t.rx": 6.2, "f.rx": 6.6, "j.rx": 7.8,
    "excl.w": 1.4, "excl.gap": 1.6, "quote.w": 1.3, "quote.gap": 1.6,
    "comma.len": 2.6, "comma.w": 0.75, "comma.thin": 0.5,
    "ring.w": 1.25, "ring.uc": 0.25, "ring.lc": 0.3,
    "slash.weight": 1.1, "1.flagw": 1.1, "paren.w": 1.3,
    "Q.top": 0.95, "a2.bar": 1.0, "s.spinew": 1.08, "s.thin": 0.95,
    "join.deep": 0.5,
    "hook.ap": 40,  # a shorter tail, so the Thin t f j hooks do not end in a curl that reads as a dot
    "small.heavy": 1.45, "brace.r": 4.0,
}

THIN_DISPLAY = replace(
    REGULAR_DISPLAY,
    name="ThinDisplay", style="Thin Display", wght=100,
    stem=20, cstem=22, bar=19, cbar=20.5, rside=1.08, rtop=1.03, diag=1.0,
    tension=0.555, tension_in=0.555,
    join=0.08, join_turn=10.0, bite=1.0, apex=1.5, diag_thin=1.0, dot=1.9,
    sp_area=0.112, sp_depth=0.03,
    widths=derived_widths(REGULAR_DISPLAY, 20, 22, 0.55),
    params=MappingProxyType(THIN_PARAMS),
)

BLACK_PARAMS = {
    **REGULAR_DISPLAY_PARAMS,
    "e.drop": 0.065,
    "t.left": 0.42, "t.right": 0.62, "t.rx": 1.22, "f.rx": 1.15, "j.rx": 1.3,
    "excl.w": 0.92, "quote.w": 0.86, "quote.gap": 0.42,
    "comma.len": 1.35, "comma.w": 0.62, "comma.thin": 0.42,
    "ring.w": 0.62, "ring.uc": 0.36, "ring.lc": 0.46, "ring.gap": 0.045,
    "slash.weight": 0.8, "1.flagw": 0.9, "paren.w": 0.92,
    "s.thin": 0.88, "s.spinew": 0.94, "s.side": 0.96, "s.steep": 0.5,
    "Q.top": 0.6, "a2.bar": 0.74, "a2.bowl": 0.6, "B.midw": 0.82, "P.round": 1.4, "B.round": 1.4,
    "dot.drop": 0,
    "join.deep": 0.075,
    "e.barw": 0.8, "e.ap": 44, "g.ry": 0.62, "r.cut": 46, "fig.ap": 8,
    "4.bar": 0.17, "q.neck": 1.08,
    "k.cut": 0.8, "k.join": 0.4, "K.join": 0.4, "g.rx": 0.66,
    "q.w": 0.8, "q.ry": 0.86, "q.stem": 0.5, "excl.gap": 0.32, "amp.w": 0.8, "amp.loopk": 0.72,
    "amp.loop": 0.24, "amp.loopx": 0.38, "amp.loopw": 1.08, "amp.bowl": 0.6,
    "A.bar": 0.3,
    "small.heavy": 1.1, "guil.size": 1.2, "guil.w": 0.74, "brace.r": 1.0, "5.ap": 28,
}

BLACK_DISPLAY = replace(
    REGULAR_DISPLAY,
    name="BlackDisplay", style="Black Display", wght=900,
    xh=504,
    stem=160, cstem=168, bar=114, cbar=120, rside=1.04, rtop=0.95, diag=0.95,
    tension=0.575, tension_in=0.56,
    join=0.4, join_turn=16.0, bite=0.34, apex=0.5, diag_thin=0.85, dot=1.12, ap_c=52, ap_C=50,
    sp_area=0.076, sp_depth=0.03,
    widths=derived_widths(REGULAR_DISPLAY, 160, 168, 0.95, BLACK_EXTRA),
    params=MappingProxyType(BLACK_PARAMS),
)

# Named instances: user weight -> lowercase stem, stepped by the mean of an arithmetic and a geometric
# progression (Luciano), so the nine weights look evenly spaced. The variable font's avar comes from this map.
WEIGHT_MAP = [(100, 20), (200, 34), (300, 52), (400, 78), (500, 94), (600, 110), (700, 127), (800, 143), (900, 160)]
WEIGHT_NAMES = ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]

DISPLAY = [THIN_DISPLAY, REGULAR_DISPLAY, BLACK_DISPLAY]
