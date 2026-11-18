"""Write masters as UFO sources and a designspace, for the font compiler. Output goes to build/ only."""

from __future__ import annotations

from pathlib import Path

import ufoLib2
from fontTools.designspaceLib import AxisDescriptor, DesignSpaceDocument, InstanceDescriptor, SourceDescriptor

from .font import Glyph
from .master import Master

FAMILY = "Orderly"
COPYRIGHT = "Copyright 2026 The Orderly Project Authors (https://github.com/ossianravn/orderly)"
VERSION = (0, 100)  # 0.100

# Placeholder vertical metrics until Phase 5 sets them by the Google Fonts specification.
LINE_ASC, LINE_DESC = 950, -250


def write_ufo(m: Master, glyphs: dict[str, Glyph], path: Path, family: str = FAMILY) -> Path:
    font = ufoLib2.Font()
    i = font.info
    i.familyName = family
    i.styleName = m.style
    i.unitsPerEm = 1000
    i.capHeight, i.xHeight = m.cap, m.xh
    i.ascender, i.descender = m.asc, m.desc
    i.versionMajor, i.versionMinor = VERSION
    i.copyright = COPYRIGHT
    i.openTypeNameLicense = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
    i.openTypeNameLicenseURL = "https://openfontlicense.org"
    i.openTypeHeadCreated = "2026/11/18 00:00:00"
    i.openTypeOS2WeightClass = m.wght
    i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender, i.openTypeOS2TypoLineGap = LINE_ASC, LINE_DESC, 0
    i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = LINE_ASC, LINE_DESC, 0
    i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = LINE_ASC, -LINE_DESC
    i.openTypeOS2Selection = [7]  # USE_TYPO_METRICS
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
        for k, (x, y) in g.anchors.items():
            ug.appendAnchor({"name": k, "x": x, "y": y})
    font.glyphOrder = order
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
    """Designspace with a weight axis. With weight_map (user weight -> lowercase stem) the design coordinates
    are stems, the axis map becomes the font's avar, and names gives one named instance per mapped weight."""
    doc = DesignSpaceDocument()
    w = AxisDescriptor()
    w.tag, w.name = "wght", "Weight"
    w.minimum = min(m.wght for m in masters)
    w.maximum = max(m.wght for m in masters)
    w.default = 400 if w.minimum <= 400 <= w.maximum else w.minimum
    if weight_map:
        w.map = [(float(u), float(d)) for u, d in weight_map]
    doc.addAxis(w)
    design = dict(weight_map or [])
    for m, ufo in zip(masters, ufos):
        s = SourceDescriptor()
        s.path = str(ufo)
        s.filename = ufo.name
        s.familyName, s.styleName = family, m.style
        s.location = {"Weight": design.get(m.wght, m.wght)}
        doc.addSource(s)
    for (u, d), name in zip(weight_map or [], names or []):
        i = InstanceDescriptor()
        i.familyName, i.styleName = family, name
        i.name = f"{family} {name}"
        i.location = {"Weight": d}
        doc.addInstance(i)
    doc.write(str(path))
    return path
