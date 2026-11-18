"""Production: what the compiled variable font needs beyond fontc's output, and every file made from it.

- finish(): STAT with an axis value for every named weight and both optical sizes (Regular and Text elided),
  the names fontc leaves out (variations PostScript prefix, unique ID), and the current practice for an unhinted
  TrueType font: a gasp table asking for smoothing at every size and a prep program that turns on smart dropout
  control.
- statics(): nine weights of Orderly (the Text design, opsz 12) and nine of Orderly Display (opsz 72), cut from the
  variable font with overlaps removed, named so apps group them (name IDs 1, 2, 16, 17), as TTF and WOFF2.
- web(): the variable font split by script into Latin and Latin extended (with the symbols), and a stylesheet
  whose @font-face rules carry the matching unicode-range.
"""

from __future__ import annotations

from pathlib import Path

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram

from .ufo import FAMILY, VERSION
from .weights import WEIGHT_MAP, WEIGHT_NAMES

# fontTools packs GSUB and GPOS with HarfBuzz's repacker when uharfbuzz happens to be installed (the qa group
# brings it) and with its own packer otherwise; the two give different bytes. Always use fontTools' own, so the
# output does not depend on what else is installed (CI installs only the default dependencies).
CFG = {"fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER": False}

SIZES = [(12, FAMILY), (72, f"{FAMILY} Display")]  # optical size of each static family
SIZES_BY_FAMILY = [(f, o) for o, f in SIZES]
RIBBI = {"Regular", "Bold"}
# Google Fonts' Latin subset, as its CSS API serves it; everything else the font covers goes in Latin extended.
LATIN = ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, "
         "U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD")


def _set(font: TTFont, nid: int, text: str) -> None:
    font["name"].setName(text, nid, 3, 1, 0x409)


def _unhinted(font: TTFont) -> None:
    """gasp: grid-fit and smooth at every size; prep: smart dropout control (as gftools' fix-unhinted)."""
    gasp = newTable("gasp")
    gasp.version, gasp.gaspRange = 1, {0xFFFF: 0x000F}
    font["gasp"] = gasp
    prep = newTable("prep")
    prog = ttProgram.Program()
    prog.fromAssembly(["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4", "SCANTYPE[ ]"])
    prep.program = prog
    font["prep"] = prep
    font["maxp"].maxStackElements = max(font["maxp"].maxStackElements, 2)


def _flags(font: TTFont) -> None:
    """OVERLAP_SIMPLE / OVERLAP_COMPOUND on every glyph (renderers then draw any contours that touch or overlap
    with non-zero winding), and the WWS bit: the names follow the weight-width-slope model."""
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.isComposite():
            g.components[0].flags |= 0x0400
        elif g.numberOfContours > 0:
            g.flags[0] |= 0x40
    font["OS/2"].fsSelection |= 1 << 8


def finish(path: Path) -> None:
    font = TTFont(path, recalcTimestamp=False, cfg=CFG)  # keep fontc's fixed head.modified: same sources, same bytes
    weights = [{"value": u, "name": n, **({"flags": 0x2, "linkedValue": 700} if n == "Regular" else {})}
               for (u, _), n in zip(WEIGHT_MAP, WEIGHT_NAMES)]
    sizes = [{"value": 12, "name": "12pt"}, {"value": 72, "name": "72pt"}]  # GF axis registry; never elided
    buildStatTable(font, [{"tag": "wght", "name": "Weight", "values": weights},
                          {"tag": "opsz", "name": "Optical Size", "values": sizes}], elidedFallbackName=2,
                   macNames=False)
    version = f"{VERSION[0]}.{VERSION[1]:03d}"
    _set(font, 3, f"{version};NONE;{FAMILY}-Regular")
    _set(font, 5, f"Version {version}")  # fontc appends its own name and version; the statics carry the plain one
    _set(font, 25, FAMILY)
    _unhinted(font)
    _flags(font)
    meta = newTable("meta")
    meta.data = {"dlng": "Latn", "slng": "Latn"}  # designed for and supports the Latin script
    font["meta"] = meta
    font.save(path)


def _feature_names(font: TTFont) -> set[int]:
    """Name IDs the stylistic sets' names live in."""
    out = set()
    for fr in font["GSUB"].table.FeatureList.FeatureRecord:
        params = fr.Feature.FeatureParams
        if params is not None and hasattr(params, "UINameID"):
            out.add(params.UINameID)
    return out


def _name_static(font: TTFont, family: str, style: str) -> None:
    name = font["name"]
    keep = {0, 7, 8, 9, 11, 12, 13, 14} | _feature_names(font)
    for rec in list(name.names):
        if rec.nameID not in keep:
            name.removeNames(nameID=rec.nameID)
    ps = f"{family.replace(' ', '')}-{style}"
    version = f"{VERSION[0]}.{VERSION[1]:03d}"
    if style in RIBBI:
        _set(font, 1, family)
        _set(font, 2, style)
    else:
        _set(font, 1, f"{family} {style}")
        _set(font, 2, "Regular")
        _set(font, 16, family)
        _set(font, 17, style)
    _set(font, 3, f"{version};NONE;{ps}")
    _set(font, 4, f"{family} {style}")
    _set(font, 5, f"Version {version}")
    _set(font, 6, ps)
    os2 = font["OS/2"]
    sel = os2.fsSelection & ~(1 | 1 << 5 | 1 << 6)  # clear italic, bold, regular
    sel |= (1 << 5) if style == "Bold" else (1 << 6)  # REGULAR for every upright style but Bold
    os2.fsSelection = sel
    font["head"].macStyle = 1 if style == "Bold" else 0
    opsz = dict(SIZES_BY_FAMILY)[family]
    wv = {"value": font["OS/2"].usWeightClass, "name": style, **({"flags": 0x2} if style == "Regular" else {})}
    ov = {"value": opsz, "name": f"{opsz}pt"}
    buildStatTable(font, [{"tag": "wght", "name": "Weight", "values": [wv]},
                          {"tag": "opsz", "name": "Optical Size", "values": [ov]}], elidedFallbackName=2,
                   macNames=False)


def _drop_repeats(font: TTFont) -> None:
    """Overlap removal rounds to the grid and can leave a point on top of its neighbour (a zero-length segment);
    drop the repeat, keeping the on-curve point of a pair, and drop contours left with fewer than three points."""
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates

    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.isComposite() or g.numberOfContours <= 0:
            continue
        coords, flags, start = list(g.coordinates), list(g.flags), 0
        pts, ends = [], []
        for end in g.endPtsOfContours:
            c = [(coords[i], flags[i]) for i in range(start, end + 1)]
            start = end + 1
            out = []
            for p in c:
                if out and p[0] == out[-1][0]:
                    if p[1] & 1 and not out[-1][1] & 1:
                        out[-1] = p
                    continue
                out.append(p)
            while len(out) > 1 and out[0][0] == out[-1][0]:
                last = out.pop()
                if last[1] & 1 and not out[0][1] & 1:
                    out[0] = last
            if len(out) >= 3:
                pts += out
                ends.append(len(pts) - 1)
        g.coordinates = GlyphCoordinates([p[0] for p in pts])
        g.flags = bytearray(p[1] for p in pts)
        g.endPtsOfContours = ends
        g.numberOfContours = len(ends)
        g.recalcBounds(glyf)


def statics(vf: Path, out_ttf: Path, out_woff2: Path) -> list[Path]:
    from fontTools.ttLib.woff2 import compress
    from fontTools.varLib.instancer import OverlapMode, instantiateVariableFont

    out_ttf.mkdir(parents=True, exist_ok=True)
    out_woff2.mkdir(parents=True, exist_ok=True)
    made = []
    for opsz, family in SIZES:
        for (wght, _), style in zip(WEIGHT_MAP, WEIGHT_NAMES):
            font = instantiateVariableFont(TTFont(vf, recalcTimestamp=False, cfg=CFG), {"wght": wght, "opsz": opsz},
                                           overlap=OverlapMode.REMOVE, updateFontNames=False)
            font.recalcTimestamp = False
            font.cfg.update(CFG)
            _drop_repeats(font)
            _flags(font)
            font["OS/2"].usWeightClass = wght
            del font["STAT"]
            _name_static(font, family, style)
            ttf = out_ttf / f"{family.replace(' ', '')}-{style}.ttf"
            font.save(ttf)
            compress(str(ttf), str(out_woff2 / ttf.with_suffix(".woff2").name))
            made.append(ttf)
    return made


def _ranges(codes: list[int]) -> str:
    out, i = [], 0
    codes = sorted(codes)
    while i < len(codes):
        j = i
        while j + 1 < len(codes) and codes[j + 1] == codes[j] + 1:
            j += 1
        out.append(f"U+{codes[i]:04X}" if i == j else f"U+{codes[i]:04X}-{codes[j]:04X}")
        i = j + 1
    return ", ".join(out)


def _parse(ranges: str) -> set[int]:
    out = set()
    for part in ranges.split(","):
        a, _, b = part.strip()[2:].partition("-")
        out |= set(range(int(a, 16), int(b or a, 16) + 1))
    return out


def web(vf: Path, out: Path) -> Path:
    """Latin and Latin-extended subsets of the variable font and `orderly.css` with their unicode-ranges."""
    from fontTools import subset

    cmap = set(TTFont(vf).getBestCmap())
    latin = _parse(LATIN)
    subsets = [("latin", "Latin", sorted(cmap & latin), LATIN),
               ("latin-ext", "Latin extended, symbols and arrows", sorted(cmap - latin), None)]
    rules = []
    for key, label, codes, rng in subsets:
        opts = subset.Options()
        opts.layout_features, opts.name_IDs, opts.name_languages = ["*"], ["*"], ["*"]
        opts.notdef_outline, opts.flavor = True, "woff2"
        font = TTFont(vf, recalcTimestamp=False, cfg=CFG)
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=codes)
        sub.subset(font)
        name = f"{FAMILY}-{key}.woff2"
        font.flavor = "woff2"
        font.save(out / name)
        rules.append(f"/* {label} */\n@font-face {{\n  font-family: \"{FAMILY}\";\n  font-style: normal;\n"
                     f"  font-weight: 100 900;\n  font-display: swap;\n  src: url(\"{name}\") format(\"woff2\");\n"
                     f"  unicode-range: {rng or _ranges(codes)};\n}}\n")
    css = out / "orderly.css"
    head = ("/* Orderly, variable (weight 100-900, optical size 12-72), split by script. Serve this file next to\n"
            "   the two .woff2 files; browsers fetch only the subsets a page uses. Optical size follows the font size\n"
            "   (font-optical-sizing: auto, the default). Licence: SIL Open Font License 1.1. */\n\n")
    css.write_text(head + "\n".join(rules), encoding="utf-8", newline="\n")
    return css
