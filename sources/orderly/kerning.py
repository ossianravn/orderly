"""Kerning: class-based, computed per master for a list of class pairs, small values dropped.

On scanlines through the pair's zone the gap between the two inks is measured; the mean of the narrowest
eighth is how close the pair comes. Spacing alone would bring them as close as their sidebearings; a pair that
stays further apart (open, slanted or overhanging sides facing each other: AV, To, LT, quotes) closes by a share
(`STRENGTH`) of the difference. Pairs never open up. Accented
letters join their base letter's class; tabular figures (when they come) stay out of every class.
"""

from __future__ import annotations

from .font import Glyph
from .master import Master
from .spacing import profile

STRENGTH = 0.42
MIN_KERN = 8
CLEAR = 0.75  # pairs that collide outside the zone (ff, f), (j) open until their inks are this many stems apart

DASHES = ["hyphen", "endash", "emdash", "hyphen.case", "endash.case", "emdash.case"]
LEFT = {  # first glyph of a pair: its right side
    "A": ["A", "Aring", "AE"], "T": ["T", "Tbar"], "V": ["V"], "W": ["W"], "Y": ["Y"], "L": ["L", "Lslash"],
    "P": ["P", "Thorn"], "F": ["F"], "K": ["K"], "R": ["R"], "O": ["O", "D", "Q", "Dcroat", "Eth"], "X": ["X"],
    "quote": ["quotesingle", "quotedbl", "quoteright", "quotedblright"],
    "period": ["period", "comma", "ellipsis", "quotesinglbase", "quotedblbase"],
    "r": ["r"], "v": ["v", "w", "y"], "f": ["f"], "k": ["k", "kgreenlandic"], "o": ["o", "b", "p", "thorn"],
    "c": ["c", "e", "ae", "oe"], "hyphen": DASHES, "open": ["parenleft", "bracketleft", "braceleft"],
    "one": ["one"], "seven": ["seven"], "four": ["four"],
}
RIGHT = {  # second glyph of a pair: its left side
    "A": ["A", "Aring", "AE"], "T": ["T", "Tbar"], "V": ["V"], "W": ["W"], "Y": ["Y"], "J": ["J"], "X": ["X"],
    "O": ["O", "C", "G", "Q", "Oslash", "OE"], "S": ["S"],
    "a": ["a", "a.ss01", "ae", "aring", "aring.ss01"], "o": ["o", "c", "d", "e", "g", "q", "oslash", "oe", "eth"],
    "u": ["u"], "v": ["v", "w", "y"], "s": ["s"], "x": ["x", "z"], "period": ["period", "comma", "ellipsis"],
    "quote": ["quoteleft", "quotedblleft", "quotesingle", "quotedbl"], "hyphen": DASHES,
    "asc": ["b", "h", "k", "l", "l.ss02", "f", "germandbls", "thorn", "lslash", "hbar"], "idot": ["i", "dotlessi"],
    "close": ["parenright", "bracketright", "braceright", "exclam", "question", "quoteright", "quotedblright"],
    "jj": ["j", "uni0237"], "one": ["one"], "four": ["four"], "seven": ["seven"],
}
PAIRS = (
    [(a, b) for a in ("A", "L", "P", "F", "K", "R", "O", "T", "V", "W", "Y", "X")
     for b in ("A", "T", "V", "W", "Y", "J", "O", "S", "X", "period", "quote", "hyphen")]
    + [(a, b) for a in ("T", "V", "W", "Y", "P", "F", "K", "L") for b in ("a", "o", "u", "v", "s", "x")]
    + [(a, b) for a in ("r", "v", "f", "k", "o", "c") for b in ("a", "o", "v", "x", "period", "quote", "hyphen")]
    + [("quote", b) for b in ("A", "a", "o", "J")] + [("period", b) for b in ("quote", "T", "V", "W", "Y", "v", "one")]
    + [("hyphen", b) for b in ("A", "T", "V", "W", "Y", "X", "J")]
    + [("L", "quote"), ("A", "v"), ("A", "quote"), ("seven", "period"), ("seven", "four"), ("seven", "A"),
       ("one", "one"), ("one", "seven"), ("four", "one"), ("seven", "one"), ("one", "period")]
)
OPEN = [("f", "asc"), ("f", "idot"), ("f", "jj"), ("f", "close"), ("f", "quote"), ("open", "jj")]


def groups(glyphs: dict[str, Glyph]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Classes with the accented letters added to their base letter's class."""
    def grow(spec: dict[str, list[str]]) -> dict[str, list[str]]:
        out = {k: [n for n in v if n in glyphs] for k, v in spec.items()}
        for n, g in glyphs.items():
            if g.components:
                base = g.components[0][0]
                if "." in n and "." not in base:  # hyphen.case, i.loclTRK: moved or local forms keep out
                    continue
                for k, v in out.items():
                    if base in v and n not in v:
                        v.append(n)
        return {k: v for k, v in out.items() if v}

    return grow(LEFT), grow(RIGHT)


def _gap(left: Glyph, right: Glyph, gl: dict, y0: float, y1: float) -> float:
    """How close the pair comes: the mean of the narrowest eighth of the gaps between their inks."""
    rows_l, _ = profile(left.outline(gl), y0, y1)
    rows_r, _ = profile(right.outline(gl), y0, y1)
    gaps = sorted(left.advance - a[1] + b[0] for a, b in zip(rows_l, rows_r) if a and b)
    if not gaps:  # no height where both have ink (a period beside a T): use their extremes in the zone
        xl = max(r[1] for r in rows_l if r) if any(rows_l) else left.advance
        xr = min(r[0] for r in rows_r if r) if any(rows_r) else 0
        return left.advance - xl + xr + (y1 - y0) * 0.15
    k = max(1, len(gaps) // 8)
    return sum(gaps[:k]) / k


def compute(m: Master, glyphs: dict[str, Glyph]) -> tuple[dict, dict]:
    """UFO groups and kerning for one master."""
    g1, g2 = groups(glyphs)
    ufo_groups = {f"public.kern1.{k}": v for k, v in g1.items()} | {f"public.kern2.{k}": v for k, v in g2.items()}
    pairs = {}
    for a, b in dict.fromkeys(PAIRS + OPEN):
        if a not in g1 or b not in g2:
            continue
        la, rb = glyphs[g1[a][0]], glyphs[g2[b][0]]
        k = 0
        if (a, b) in PAIRS:
            lc = (la.zone == "lc" and rb.zone in ("lc", "pun")) or (rb.zone == "lc" and la.zone == "pun")
            h = m.xh if lc else m.cap
            k = -(_gap(la, rb, glyphs, 0, h) - (la.rsb + rb.lsb)) * STRENGTH
            k = max(round(k / 2) * 2, -round(0.16 * h))
        if (a, b) in OPEN:  # never closer than CLEAR stems anywhere from the descender to above the ascender
            k += max(0.0, m.stem * CLEAR - (_closest(la, rb, glyphs, m.desc, m.asc + 60) + k))
            k = round(k / 2) * 2
        if abs(k) >= MIN_KERN:
            pairs[(f"public.kern1.{a}", f"public.kern2.{b}")] = k
    return ufo_groups, pairs


def _closest(left: Glyph, right: Glyph, gl: dict, y0: float, y1: float) -> float:
    """The smallest horizontal distance between the two inks at any height in y0..y1 (set side by side)."""
    rows_l, _ = profile(left.outline(gl), y0, y1)
    rows_r, _ = profile(right.outline(gl), y0, y1)
    gaps = [left.advance - a[1] + b[0] for a, b in zip(rows_l, rows_r) if a and b]
    return min(gaps) if gaps else 1e9
