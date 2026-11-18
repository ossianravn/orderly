"""The site's data: the web font, `fonts/data/orderly.json` and `fonts/data/outlines.json`.

The contract is in the plan ("Site data"); the exact shapes are in docs/production.md. Every number comes from the
generator and the compiled font; none is typed here.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont

from .font import Glyph
from .master import Master
from .ufo import FAMILY, LINE_ASC, LINE_DESC, VERSION

FEATURE_NAMES = {
    "kern": ("Kerning", "AVATAR Tower Yacht"), "mark": ("Mark positioning", "Å Ø Č ŋ"),
    "mkmk": ("Mark to mark", "ǘ"), "ccmp": ("Glyph composition", "i̇ j́"), "locl": ("Localized forms", "ș ț İ"),
    "case": ("Case-sensitive forms", "(HELLO) [NO]"), "cpsp": ("Capital spacing", "ORDERLY"),
    "frac": ("Fractions", "1/2 3/4 5/8"), "numr": ("Numerators", "12345"), "dnom": ("Denominators", "12345"),
    "sups": ("Superiors", "x2 m3"), "subs": ("Inferiors", "H2O"), "ordn": ("Ordinals", "1a 2o No"),
    "tnum": ("Tabular figures", "1111 2048"), "pnum": ("Proportional figures", "1111 2048"),
    "zero": ("Slashed zero", "0 100"), "ss01": ("Double-storey a", "Blåbærsyltetøj"),
    "ss02": ("l with a curved foot", "Illegal Il1"),
}


def _category(name: str, uni: int | None) -> str:
    if uni is None:
        base = name.split(".")[0]
        return "lowercase" if base.islower() else "alternate"
    c = unicodedata.category(chr(uni))
    return {"Lu": "uppercase", "Ll": "lowercase", "Lo": "lowercase", "Nd": "figure", "Zs": "space",
            "Mn": "mark", "Sk": "mark"}.get(c, "punctuation" if c.startswith("P") else "symbol")


def _points(c) -> list[dict]:
    pts = [{"x": c.segs[0][0][0], "y": c.segs[0][0][1], "on": True}]
    for s in c.segs:
        pts += [{"x": p[0], "y": p[1], "on": False} for p in s[1:-1]]
        pts.append({"x": s[-1][0], "y": s[-1][1], "on": True})
    return pts[:-1]  # the last on-curve point closes the contour on the first


def master_numbers(m: Master) -> dict:
    return {"stem": m.stem, "capStem": m.cstem, "bar": m.bar, "capBar": m.cbar, "xHeight": m.xh, "capHeight": m.cap,
            "overshoot": m.over, "join": m.join, "spacingArea": m.sp_area, "dot": m.dot}


def export(masters: list[Master], sets: list[dict[str, Glyph]], vf: Path, out_dir: Path,
           weight_names: list[tuple[int, str]], languages: list[dict]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    font = TTFont(vf)
    fvar = font["fvar"]
    names = {a.axisTag: font["name"].getDebugName(a.axisNameID) for a in fvar.axes}
    tags = set()
    for table in ("GSUB", "GPOS"):
        if table in font:
            tags |= {fr.FeatureTag for fr in font[table].table.FeatureList.FeatureRecord}
    order = list(sets[0])
    glyphs = []
    for n in order:
        g = sets[0][n]
        uni = g.unicodes[0] if g.unicodes else None
        glyphs.append({
            "name": n, "unicode": uni, "char": chr(uni) if uni is not None else None,
            "category": _category(n, uni),
            "metrics": {m.name: {"advance": s[n].advance, "lsb": s[n].lsb, "rsb": s[n].rsb} for m, s in zip(masters, sets)},
        })
    data = {
        "family": FAMILY, "version": f"{VERSION[0]}.{VERSION[1]:03d}", "unitsPerEm": 1000,
        "metrics": {
            "ascender": masters[0].asc, "capHeight": masters[0].cap, "descender": masters[0].desc,
            "xHeight": {str(m.opsz): m.xh for m in masters if m.wght == 400},
            "line": {"ascender": LINE_ASC, "descender": LINE_DESC, "lineGap": 0},
        },
        "axes": [{"tag": a.axisTag, "name": names[a.axisTag], "min": a.minValue, "default": a.defaultValue,
                  "max": a.maxValue} for a in fvar.axes],
        "instances": [{"name": name, "wght": w} for w, name in weight_names],
        "masters": [{"id": m.name, "name": m.style, "wght": m.wght, "opsz": m.opsz, "numbers": master_numbers(m)}
                    for m in masters],
        "features": [{"tag": t, "name": FEATURE_NAMES.get(t, (t, ""))[0], "sample": FEATURE_NAMES.get(t, ("", ""))[1]}
                     for t in sorted(tags)],
        "languages": languages,
        "glyphs": glyphs,
    }
    (out_dir / "orderly.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    outlines = {
        "unitsPerEm": 1000,
        "masters": [m.name for m in masters],
        "glyphs": {n: {m.name: [{"part": c.part, "points": _points(c)} for c in s[n].outline(s)]
                       for m, s in zip(masters, sets)} for n in order},
    }
    (out_dir / "outlines.json").write_text(json.dumps(outlines, separators=(",", ":")), encoding="utf-8", newline="\n")


def woff2(ttf: Path, out: Path) -> Path:
    from fontTools.ttLib.woff2 import compress

    out.parent.mkdir(parents=True, exist_ok=True)
    compress(str(ttf), str(out))
    return out
