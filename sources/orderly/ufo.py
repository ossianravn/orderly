"""Write masters as UFO sources and a designspace, for the font compiler. Output goes to build/ only."""

from __future__ import annotations

from pathlib import Path

import ufoLib2
from ufoLib2.objects import Component
from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor

from .font import Glyph
from .master import Master

FAMILY = "Orderly"
COPYRIGHT = "Copyright 2026 The Orderly Project Authors (https://github.com/ossianravn/orderly)"
VERSION = (1, 0)  # 1.000: the first complete release of the planned scope (docs/production.md, "Version")
DESIGNER = "Ossian Ravn"
URL = "https://github.com/ossianravn/orderly"

# Vertical metrics by the Google Fonts specification: typo and hhea equal, no line gap, capitals centred in the
# line (ascender - cap height = -descender), 130 % of the em in all. 1000 clears every accented capital but the
# rare Ǻ; the win metrics (computed from the outlines of all masters at build time) cover everything.
LINE_ASC, LINE_DESC = 1000, -300


def write_ufo(m: Master, glyphs: dict[str, Glyph], path: Path, family: str = FAMILY, features: str = "",
              kerning: tuple[dict, dict] | None = None, win: tuple[int, int] = (-LINE_DESC, LINE_ASC)) -> Path:
    """win: (winDescent, winAscent), the same in every master so the font carries no MVAR delta for them."""
    font = ufoLib2.Font()
    i = font.info
    i.familyName = family
    i.styleName = m.style.removesuffix(" Text")  # the default master (Regular Text) names the font Regular
    i.unitsPerEm = 1000
    i.capHeight, i.xHeight = m.cap, m.xh
    i.ascender, i.descender = m.asc, m.desc
    i.versionMajor, i.versionMinor = VERSION
    i.copyright = COPYRIGHT
    i.openTypeNameLicense = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                             "This license is available with a FAQ at: https://openfontlicense.org")
    i.openTypeNameLicenseURL = "https://openfontlicense.org"
    i.openTypeHeadCreated = "2026/11/18 00:00:00"
    i.openTypeOS2WeightClass = m.wght
    i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender, i.openTypeOS2TypoLineGap = LINE_ASC, LINE_DESC, 0
    i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = LINE_ASC, LINE_DESC, 0
    i.openTypeOS2WinDescent, i.openTypeOS2WinAscent = win
    i.openTypeOS2Selection = [7]  # USE_TYPO_METRICS
    i.openTypeOS2Type = []  # installable embedding (fsType 0)
    i.openTypeNameDesigner, i.openTypeNameManufacturer = DESIGNER, DESIGNER
    i.openTypeNameDesignerURL, i.openTypeNameManufacturerURL = URL, URL
    i.openTypeNameVersion = f"Version {VERSION[0]}.{VERSION[1]:03d}"
    i.postscriptUnderlinePosition, i.postscriptUnderlineThickness = -100, 50
    order = [".notdef"] + [n for n in glyphs if n != ".notdef"]
    notdef = font.newGlyph(".notdef")
    notdef.width = 500
    _draw_notdef(notdef, m)
    for name, g in glyphs.items():
        ug = font.newGlyph(name)
        ug.width = g.advance
        ug.unicodes = list(g.unicodes)
        pen = ug.getPointPen()
        for c in g.contours:
            pen.beginPath()
            for seg in c.segs:
                for p in seg[1:-1]:
                    pen.addPoint(p, None)
                pen.addPoint(seg[-1], "curve" if len(seg) == 4 else "line")
            pen.endPath()
        for base, dx, dy in g.components:
            ug.components.append(Component(base, transformation=(1, 0, 0, 1, dx, dy)))
        for k, (x, y) in g.anchors.items():
            ug.appendAnchor({"name": k, "x": x, "y": y})
    font.glyphOrder = order
    font.lib["public.openTypeCategories"] = {n: ("mark" if g.zone == "mark" else "base") for n, g in glyphs.items()}
    if features:
        font.features.text = features
    if kerning:
        groups, pairs = kerning
        font.groups.update(groups)
        font.kerning.update(pairs)
    path.parent.mkdir(parents=True, exist_ok=True)
    font.save(path, overwrite=True)
    return path


def _draw_notdef(g, m: Master) -> None:
    pen = g.getPointPen()
    for pts in (((50, 0), (450, 0), (450, m.cap), (50, m.cap)), ((100, 50), (100, m.cap - 50), (400, m.cap - 50), (400, 50))):
        pen.beginPath()
        for p in pts:
            pen.addPoint(p, "line")
        pen.endPath()


def write_designspace(masters: list[Master], ufos: list[Path], path: Path, family: str = FAMILY,
                      weight_map: list[tuple[int, float]] | None = None, names: list[str] | None = None) -> Path:
    """Designspace with a weight axis and, when the masters differ in optical size, an opsz axis.

    With weight_map (user weight -> Display lowercase stem) the weight design coordinates are stems, the axis
    map becomes the font's avar, and `names` gives one named instance per mapped weight at the default size.
    """
    doc = DesignSpaceDocument()
    w = AxisDescriptor()
    w.tag, w.name = "wght", "Weight"
    w.minimum = min(m.wght for m in masters)
    w.maximum = max(m.wght for m in masters)
    w.default = 400 if w.minimum <= 400 <= w.maximum else w.minimum
    if weight_map:
        w.map = [(float(u), float(d)) for u, d in weight_map]
    doc.addAxis(w)
    sizes = sorted({m.opsz for m in masters})
    if len(sizes) > 1:
        o = AxisDescriptor()
        o.tag, o.name = "opsz", "Optical size"
        o.minimum, o.maximum, o.default = sizes[0], sizes[-1], sizes[0]
        doc.addAxis(o)
    design = dict(weight_map or [])
    for m, ufo in zip(masters, ufos):
        s = SourceDescriptor()
        s.path = str(ufo)
        s.filename = ufo.name
        s.familyName, s.styleName = family, m.style
        s.location = {"Weight": design.get(m.wght, m.wght)}
        if len(sizes) > 1:
            s.location["Optical size"] = m.opsz
        doc.addSource(s)
    for (u, d), name in zip(weight_map or [], names or []):
        i = InstanceDescriptor()
        i.familyName, i.styleName = family, name
        i.name = f"{family} {name}"
        i.postScriptFontName = f"{family}-{name}"
        i.location = {"Weight": d}
        if len(sizes) > 1:
            i.location["Optical size"] = sizes[0]
        doc.addInstance(i)
    doc.write(str(path))
    return path
