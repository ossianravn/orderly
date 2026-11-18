"""OpenType features, written as feature code from the glyph names.

fontc writes `kern`, `mark` and `mkmk` from the masters' kerning and anchors; everything else is here. A feature
follows from names: `x.case` is reached by `case`, `x.ss01` by `ss01`, `x.tf` by `tnum`, `x.numr` by `frac` and
`numr`. GSUB lookups apply in the order they are written: `locl` first (so a Turkish i is no longer an i when
`ccmp` looks for one), then `ccmp`, the figure features, `case`, and the stylistic sets last.
"""

from __future__ import annotations

import unicodedata

from .glyphs.marks import TOP
from .small import FIGURES

BOTTOM = ["cedillacomb", "ogonekcomb", "commaaccentcomb"]
SS_NAMES = {"ss01": "Double-storey a", "ss02": "l with a curved foot"}
SAMI = ["NSM", "ISM", "SKS", "LSM"]  # Northern, Inari, Skolt, Lule Sámi: the N-form Eng
LANGS = ["ROM", "MOL", "TRK", "AZE", "CRT", "CAT", "NLD"] + SAMI


def _cls(names: list[str]) -> str:
    return "[" + " ".join(names) + "]"


def caps(glyphs: dict) -> list[str]:
    out = [n for n, g in glyphs.items() if g.unicodes and unicodedata.category(chr(g.unicodes[0])) == "Lu"]
    return out + [n for n in glyphs if n[:1].isupper() and ".locl" in n]


def _frac() -> str:
    num = "@NUM"
    ignores = []
    for k in range(1, 5):  # dates and paths (1/2/2026, 3/4/5) keep their slashes
        seq = " ".join([num] * k)
        ignores += [f"    ignore sub slash {seq} slash';", f"    ignore sub slash' {seq} slash;"]
    return "\n".join([
        "lookup FRAC_BAR {", *ignores, f"    sub {num} slash' {num} by fraction;", "} FRAC_BAR;",
        "lookup FRAC_NUMR {", "    rsub @NUM' [fraction @NUMR] by @NUMR;", "} FRAC_NUMR;",
        "lookup FRAC_DNOM {", "    sub [fraction @DNOM] @NUM' by @DNOM;", "} FRAC_DNOM;",
    ])


def features(glyphs: dict, cpsp: str) -> str:
    """Feature code for a glyph set (names are the same in every master). `cpsp` is the capital spacing value
    record."""
    have = set(glyphs)
    top = [n for n in TOP if n in have and f"{n}.case" in have]
    sups = [n for n in glyphs if glyphs[n].unicodes and n not in FIGURES and glyphs[n].components
            and glyphs[n].components[0][0].endswith(".numr") and glyphs[n].unicodes[0] in
            (0x2070, 0xB9, 0xB2, 0xB3, *range(0x2074, 0x207A))]
    subs = [n for n in glyphs if glyphs[n].unicodes and 0x2080 <= glyphs[n].unicodes[0] <= 0x2089]
    sups.sort(key=lambda n: FIGURES.index(glyphs[n].components[0][0].split(".")[0]))
    subs.sort(key=lambda n: glyphs[n].unicodes[0])
    case = [n for n in glyphs if n.endswith(".case") and n[:-5] in have and "comb" not in n]
    out = ["languagesystem DFLT dflt;", "languagesystem latn dflt;"]
    out += [f"languagesystem latn {t};" for t in LANGS]
    out += [
        f"@NUM = {_cls(list(FIGURES))};", f"@NUMR = {_cls([f + '.numr' for f in FIGURES])};",
        f"@DNOM = {_cls([f + '.dnom' for f in FIGURES])};", f"@TF = {_cls([f + '.tf' for f in FIGURES])};",
        f"@SUPS = {_cls(sups)};", f"@SUBS = {_cls(subs)};",
        f"@TOP = {_cls(top)};", f"@TOP_CASE = {_cls([n + '.case' for n in top])};",
        f"@BOTTOM = {_cls([n for n in BOTTOM if n in have])};", f"@CAPS = {_cls(caps(glyphs))};",
        "",
        "lookup DOTLESS { sub i by dotlessi; sub j by uni0237; } DOTLESS;",
        "lookup CASEMARK { sub @TOP by @TOP_CASE; } CASEMARK;",
        "lookup ORDF { sub [a A] by ordfeminine; } ORDF;",
        "lookup ORDM { sub [o O] by ordmasculine; } ORDM;",
        "",
        "feature locl {",
        "    script latn;",
        "    language ROM;",
        "    lookup LOCL_ROM { sub Scedilla by uni0218; sub scedilla by uni0219; sub uni0162 by uni021A;"
        " sub uni0163 by uni021B; } LOCL_ROM;",
        "    language MOL; lookup LOCL_ROM;",
        "    language TRK; lookup LOCL_TRK { sub i by i.loclTRK; } LOCL_TRK;",
        "    language AZE; lookup LOCL_TRK;",
        "    language CRT; lookup LOCL_TRK;",
        "    language CAT; lookup LOCL_CAT { sub l periodcentered' l by periodcentered.loclCAT;"
        " sub L periodcentered' L by periodcentered.loclCAT.case; } LOCL_CAT;",
        "    language NLD; lookup LOCL_NLD { sub iacute j' by jacute; sub Iacute J' by Jacute; } LOCL_NLD;",
        f"    language {SAMI[0]}; lookup LOCL_SAMI {{ sub Eng by Eng.loclNSM; }} LOCL_SAMI;",
        *[f"    language {t}; lookup LOCL_SAMI;" for t in SAMI[1:]],
        "} locl;",
        "",
        "feature ccmp {",
        "    lookup CCMP_DOTLESS {",
        "        sub [i j]' lookup DOTLESS @TOP;",
        "        sub [i j]' lookup DOTLESS @BOTTOM @TOP;",
        "    } CCMP_DOTLESS;",
        "    lookup CCMP_CASE {",
        "        sub @CAPS @TOP' lookup CASEMARK;",
        "        sub @CAPS @BOTTOM @TOP' lookup CASEMARK;",
        "        sub @TOP_CASE @TOP' lookup CASEMARK;",
        "    } CCMP_CASE;",
        "} ccmp;",
        "",
        "feature frac {", _frac(), "} frac;",
        "feature numr { sub @NUM by @NUMR; } numr;",
        "feature dnom { sub @NUM by @DNOM; } dnom;",
        "feature sups { sub @NUM by @SUPS; } sups;",
        "feature subs { sub @NUM by @SUBS; } subs;",
        "feature ordn {",
        "    sub @NUM [a A]' lookup ORDF;",
        "    sub @NUM [o O]' lookup ORDM;",
        "    sub N o period by uni2116;",
        "} ordn;",
        "feature tnum { sub @NUM by @TF; sub zero.zero by zero.tf.zero; } tnum;",
        "feature pnum { sub @TF by @NUM; sub zero.tf.zero by zero.zero; } pnum;",
        "feature zero { sub zero by zero.zero; sub zero.tf by zero.tf.zero; } zero;",
        "feature case {", *[f"    sub {n[:-5]} by {n};" for n in case], "} case;",
    ]
    for ss, label in SS_NAMES.items():
        alts = [n for n in glyphs if n.endswith("." + ss)]
        out += [f"feature {ss} {{", f'    featureNames {{ name "{label}"; }};',
                *[f"    sub {n[: -len(ss) - 1]} by {n};" for n in alts], f"}} {ss};"]
    out += ["", f"feature cpsp {{ pos @CAPS {cpsp}; }} cpsp;", ""]
    return "\n".join(out)
