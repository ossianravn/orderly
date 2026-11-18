"""The Text masters (opsz 12): their own design for 9 to 20 px, derived from each Display sibling by numbers.

Text has a larger x-height, sturdier stems, clearly looser spacing, open apertures, deeper joins, a little more
width in narrow letters, larger dots and punctuation, and its own word space. The Black Text is lighter than the
Black Display, as small type needs. The variable font's default master is Regular Text.
"""

from __future__ import annotations

from dataclasses import replace
from types import MappingProxyType

from .master import REGULAR_DISPLAY, Master
from .weights import BLACK_DISPLAY, THIN_DISPLAY, VSTEMS

# Width added to each glyph in Text on top of the stroke growth: narrow letters gain most, rounds follow the taller
# x-height so they stay near round.
TEXT_EXTRA = {
    "o": 16, "n": 10, "m": 14, "b": 16, "a": 14, "c": 18, "e": 16, "s": 16, "r": 16, "v": 10, "w": 14, "x": 10,
    "y": 10, "z": 12, "k": 12, "t": 14, "f": 14, "j": 10, "a.ss01": 14,
    "E": 12, "F": 12, "L": 12, "S": 14, "J": 12, "P": 10, "B": 10, "R": 10, "C": 8, "G": 6, "K": 8,
    "zero": 14, "one": 12, "two": 14, "three": 14, "four": 10, "five": 14, "six": 14, "seven": 12, "eight": 14,
    "nine": 14, "question": 14, "hyphen": 20,
}


def text_widths(display: Master, stem: float, cstem: float, k: float) -> MappingProxyType:
    out = {}
    for name, w in display.widths.items():
        if w == 0:
            out[name] = 0
            continue
        cap = name[:1].isupper() or name in ("zero", "one", "two", "three", "four", "five", "six", "seven",
                                             "eight", "nine", "ampersand")
        d = (cstem - display.cstem) if cap else (stem - display.stem)
        out[name] = round(w + VSTEMS.get(name, 1.0) * d * k + TEXT_EXTRA.get(name, 0))
    return MappingProxyType(out)


def _params(display: Master, **over) -> MappingProxyType:
    return MappingProxyType({**display.params, **over})


REGULAR_TEXT = replace(
    REGULAR_DISPLAY, name="RegularText", style="Regular Text", opsz=12,
    xh=516, stem=86, cstem=92, bar=76, cbar=82, rside=1.06, rtop=1.03,
    join=0.3, ap_c=50, ap_C=47, dot=1.32, sp_area=0.112, space=0.52,
    widths=text_widths(REGULAR_DISPLAY, 86, 92, 0.8),
    params=_params(REGULAR_DISPLAY, **{"e.ap": 50, "fig.ap": 26, "e.drop": 0.035, "join.deep": 0.22,
                                         "comma.len": 1.7, "quote.len": 0.32, "ring.uc": 0.29, "ring.lc": 0.36}),
)

THIN_TEXT = replace(
    THIN_DISPLAY, name="ThinText", style="Thin Text", opsz=12,
    xh=516, stem=28, cstem=30, bar=26, cbar=28, rside=1.07,
    join=0.12, ap_c=50, ap_C=47, dot=1.75, sp_area=0.132, space=0.54,
    widths=text_widths(THIN_DISPLAY, 28, 30, 0.6),
    params=_params(THIN_DISPLAY, **{"e.ap": 50, "fig.ap": 26, "t.left": 2.4, "t.right": 3.8, "t.rx": 4.8,
                                      "f.rx": 5.0, "j.rx": 5.8, "comma.len": 2.4, "excl.gap": 1.3}),
)

BLACK_TEXT = replace(
    BLACK_DISPLAY, name="BlackText", style="Black Text", opsz=12,
    xh=520, stem=148, cstem=156, bar=106, cbar=112, rside=1.04,
    join=0.46, bite=0.4, apex=0.56, ap_c=56, ap_C=54, dot=1.16, sp_area=0.094, space=0.48,
    widths=text_widths(BLACK_DISPLAY, 148, 156, 0.8),
    params=_params(BLACK_DISPLAY, **{"e.ap": 40, "e.drop": 0.09, "fig.ap": 14}),
)

TEXT = [THIN_TEXT, REGULAR_TEXT, BLACK_TEXT]
