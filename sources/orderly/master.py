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
    diag: float = 0.96  # diagonal stroke, measured square to the stroke / the matching stem
    fig: float = 0.98  # figure strokes / lowercase strokes, scaled toward the capitals

    # Curves.
    tension: float = 0.56  # outer edges: 0.552 is a circle, more is squarer
    tension_in: float = 0.56  # inner edges (counters)

    # Joins: where a curve enters a stem, the stroke narrows to (1 - join) of its weight.
    join: float = 0.24
    join_turn: float = 18.0  # degrees the outer edge swings toward the horizontal at a join (softer shoulder)
    bite: float = 0.45  # how far a counter's ellipse runs into the stem it joins, as a fraction of the stem
    ubar: float = 0.51  # centre of capital crossbars (H, E, F), as a fraction of the cap height
    apex: float = 0.8  # flat apex width of A V W M N v w, as a fraction of the stem
    diag_thin: float = 0.9  # diagonals narrow to this fraction of their weight where they meet

    # Apertures: where open rounds are cut, as an angle from the horizontal axis of their ellipse (degrees).
    ap_c: float = 42  # c e, upper and lower terminal
    ap_C: float = 40  # C G

    # Dots: diameter / stem.
    dot: float = 1.2

    # Body widths (outer extremes, font units); each glyph reads its own.
    widths: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))
    # Numbers particular to one letter or one family ("e.bar", "s.spine"); each glyph reads its own.
    params: MappingProxyType = field(default_factory=lambda: MappingProxyType({}))

    # Spacing, area method: target white area per side as a fraction of the zone height squared, and the depth
    # a profile may reach into an open shape (fraction of the zone height).
    sp_area: float = 0.09
    sp_depth: float = 0.03

    def w(self, key: str) -> float:
        return self.widths[key]

    def g(self, key: str) -> float:
        return self.params[key]

    def os(self, height: float) -> float:
        """Round overshoot for a shape of this flat height."""
        return round(height * self.over)

    def osa(self, height: float) -> float:
        return round(height * self.over_apex)


REGULAR_DISPLAY_WIDTHS = {
    # lowercase
    "o": 516, "n": 452, "m": 724, "b": 490, "a": 476, "c": 452, "e": 492, "s": 356, "r": 270,
    "v": 466, "w": 698, "x": 448, "y": 468, "z": 400, "k": 430, "t": 268, "f": 280, "j": 210,
    "i": 0, "l": 0,
    # capitals
    "O": 722, "H": 552, "C": 642, "G": 640, "D": 616, "Q": 722, "U": 560, "N": 590, "A": 596,
    "V": 596, "W": 940, "M": 700, "X": 616, "Y": 624, "Z": 560, "K": 576, "E": 456, "F": 440,
    "L": 432, "T": 548, "P": 494, "B": 494, "R": 522, "S": 492, "J": 420, "I": 0,
    # figures
    "zero": 500, "one": 262, "two": 466, "three": 456, "four": 512, "five": 458, "six": 486,
    "seven": 452, "eight": 486, "nine": 486,
    # punctuation
    "AE.leg": 300,  # Æ: horizontal run of the A's leg
    "a.ss01": 410,
    "question": 380, "hyphen": 300, "paren": 230, "slash": 380, "ampersand": 600,
}

REGULAR_DISPLAY_PARAMS = {
    "e.drop": 0.04,  # e's bar: its lower edge lies this far under the round's centre / x-height
    "s.mid": 0.51,  # s S spine centre / height (the optical centre)
    "s.upper": 0.92,  # upper round's width / lower round's
    "s.thin": 0.92, "s.side": 0.98, "s.spinew": 1.06,  # top-bottom, sides, spine / the round's weights and stem
    "s.hu": 0.72, "s.hl": 0.28,  # upper round's west extreme, lower round's east extreme / height
    "s.lean": 0.03,  # upper round's centre right of the lower's / width
    "s.steep": 0.5, "s.tbowl": 0.58, "s.tmid": 0.56,  # spine angle; tensions leaving the rounds and at the centre
    "hook.ap": 55,
    "G.jaw": 0.9,  # G jaw's outer edge / O radius from the centre
    "G.foot": 0.26,  # where the G's round turns into the jaw / cap height
    "G.bar": 0.5,  # top of the G's bar (and jaw) / cap height
    "G.barl": 0.12,  # left end of the G's bar / O radius from the centre
    "Q.at": -52, "Q.top": 0.7,  # Q tail starts mid-stroke at this angle on the round; weight there / full
    "Q.x1": 0.98, "Q.y1": -0.11,  # Q tail, lower end: x / O radius from the centre, y / cap height
    "D.round": 1.0,
    "r.cut": 32,  # r's arm ends this many degrees past the top of the n's counter
    "dot.drop": 6,  # i j dots: top this far under the ascender
    "hook.ry": 0.85,  # hooks of t f j: vertical / horizontal outer radius
    "j.rx": 2.3,  # j hook's outer horizontal radius / stem
    "t.left": 0.75, "t.right": 1.25,  # t f crossbar beyond the stem, left and right / stem
    "t.rx": 2.2, "f.rx": 1.9,  # hook radius / stem
    "t.top": 0.55,  # t's flat top: this fraction of the way from the x-height to the ascender
    "k.join": 0.3,  # k arm's centre line meets the stem edge at this fraction of the x-height
    "k.armin": 0.1,  # k arm's top stops this many stems short of the leg's foot
    "k.cut": 0.45,  # k K arm's buried end: vertical cut this fraction of the stem from its left edge
    "g.rx": 0.5,  # g tail's outer radius / the bowl's width
    "q.w": 1.0, "amp.w": 1.0, "amp.loopk": 1.0,  # ? and & stroke weights / the stem; & loop / & stroke
    "k.leg": 0.34,  # k leg leaves the arm this fraction of the way up from the stem
    "w.weight": 0.95, "x.weight": 0.96, "z.weight": 1.0,  # diagonal weight / the diagonal weight
    "w.apex": 0.25,  # w's bottom apexes: centre / width
    "x.top": 0.05,  # x is narrower at the top by this fraction of its width
    "y.apex": 0.47,  # y: where the arms meet / width
    "z.top": 0.05,  # z's top bar is narrower by this fraction of the width
    "E.top": 0.97, "E.mid": 0.9, "F.mid": 0.9,  # arm lengths / width
    "F.drop": 0.02,  # F's middle arm sits this fraction of the cap height below E's
    "J.rx": 0.5, "J.ry": 0.9,  # J hook: outer horizontal radius / width; vertical / horizontal
    "U.round": 0.95,  # U's bottom: vertical / horizontal radius
    "P.round": 1.0, "P.bowl": 0.42,  # P bowl: round's horizontal / half vertical radius; bowl bottom / cap
    "R.bowl": 0.44, "R.bowlw": 0.92,  # R bowl bottom / cap; bowl width / R width
    "R.legx": 0.5,  # R leg leaves the bowl's lower arm at this fraction of the bowl width
    "B.upper": 0.9, "B.mid": 0.53, "B.midw": 0.95, "B.round": 1.0,  # B: upper bowl width, middle bar centre, weight
    "K.join": 0.36,  # K arm meets the stem at this fraction of the cap height
    "A.bar": 0.32,  # top of A's bar / cap height
    "W.apex": 0.22,  # W bottom apexes: centre / width
    "M.stem": 0.94, "M.weight": 0.92, "N.stem": 0.92, "N.weight": 1.0,  # stems and diagonals / capital weights
    "Y.join": 0.44,  # Y arms meet the stem at this fraction of the cap height
    "fig.ap": 18,  # terminals of 2 3 5: degrees from the round's horizontal axis
    "1.drop": 0.2, "1.flagw": 1.0,  # 1 flag: drop / cap height; weight / figure bar
    "2.rx": 1.0, "2.ry": 1.0, "2.diag": 1.0, "2.flat": 0.72, "2.te": 0.5, "2.tf": 0.62,  # 2 round: radius / half width, vertical / horizontal; diagonal weight
    "3.mid": 0.55, "3.upper": 0.88, "3.inset": 0.02, "3.waist": 0.3,  # 3: middle height, upper round, waist end
    "4.over": 0.55, "4.bar": 0.2,  # 4: crossbar beyond the stem / stem; crossbar bottom / cap
    "5.stem": 0.06, "5.bowl": 0.6, "5.top": 0.92,  # 5: stem left / width; round top / cap; top bar / width
    "6.bowl": 0.64, "6.leave": 0.97, "6.end": 22, "6.endx": 0.8, "6.t0": 0.62, "6.t1": 0.5,  # 6 9 stem
    "7.foot": 0.2,  # 7 diagonal's foot / width
    "comma.x0": 0.2, "comma.x1": 0.18, "comma.len": 1.55, "comma.w": 0.6, "comma.thin": 0.4, "comma.angle": 28,  # / dot
    "excl.w": 0.95, "excl.gap": 0.55,  # ! ?: stroke / stem; gap above the dot / dot
    "q.ry": 0.92, "q.stem": 0.36, "q.x": 0.46,  # ?: round shape, where its stem starts / cap, stem x / width
    "hyphen.y": 0.53,  # hyphen centre / x-height
    "quote.w": 0.95, "quote.len": 0.3, "quote.gap": 0.7,  # quotes: weight / stem, length / cap, gap / weight
    "paren.low": 0.8, "paren.high": 20, "paren.ry": 1.25, "paren.w": 1.0,  # ( ): reach, curvature, weight
    "slash.w": 0.95, "slash.low": 0.6, "slash.high": 40,  # /: weight; reach below and above
    "amp.loop": 0.2, "amp.loopx": 0.4, "amp.loopw": 0.95,  # &: loop radius / cap; loop centre / width; shape
    "amp.bowl": 0.6, "amp.bowlx": 0.42, "amp.bowlw": 0.8,  # &: bowl height / cap, centre / width, width / width
    "amp.leave": 0.55, "amp.ap": 38,  # &: bowl leaves the loop's skeleton here / radius; terminal cut
    "ring.gap": 0.05, "ring.uc": 0.27, "ring.lc": 0.34, "ring.w": 0.8,  # Å å ring: gap, size / cap or x-height
    "slash.angle": 58, "slash.over": 0.05, "slash.weight": 0.92,  # Ø ø: degrees, reach past the round / cap
    "AE.top": 0.2, "ae.into": 0.03,  # Æ leg top inset / stem; æ: e's left extreme into the a's stem / stem
    "a2.hook": 0.5, "a2.hookry": 0.8,  # double-storey a: top hook radius / width, vertical / horizontal
    "a2.bowl": 0.6, "a2.bar": 0.92,  # its bowl's top / x-height; the bowl's top stroke / round top
    "8.mid": 0.54, "8.waist": 1.0, "8.upper": 0.9,  # 8: waist height / cap; waist weight / bar; upper width  # D's round: horizontal radius / half the cap height  # hook terminals of t f j g J, degrees past the bottom extreme
}

REGULAR_DISPLAY = Master(
    name="RegularDisplay",
    style="Regular Display",
    wght=400,
    opsz=72,
    widths=MappingProxyType(REGULAR_DISPLAY_WIDTHS),
    params=MappingProxyType(REGULAR_DISPLAY_PARAMS),
)
