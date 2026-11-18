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

# tag -> (name, group, on by default, sample[, extra fields]). Mark samples use combining sequences whose
# precomposed letter is not in the font (shapers recompose those that are), so mark, mkmk and ccmp visibly act.
FEATURES = {
    "kern": ("Kerning", "builtin", True, "AVATAR Tower Yacht"),
    "mark": ("Mark positioning", "builtin", True, "ẽ ỹ g̃ ḿ n̄"),
    "mkmk": ("Mark to mark", "builtin", True, "ẽ́ x̂̃ q̈̄"),
    "ccmp": ("Glyph composition", "builtin", True, "j́ ǰ X́ Q̈ M̀"),
    "locl": ("Localized forms", "builtin", True, "Ştefan Ţară", {"lang": "ro"}),
    "case": ("Case-sensitive forms", "capitals", False, "«(ORDERLY)» – ¿QUÉ?"),
    "cpsp": ("Capital spacing", "capitals", False, "ORDERLY"),
    "frac": ("Fractions", "figures", False, "1/2 3/4 7/16"),
    "numr": ("Numerators", "figures", False, "0123456789"),
    "dnom": ("Denominators", "figures", False, "0123456789"),
    "sups": ("Superiors", "figures", False, "E = mc2"),
    "subs": ("Inferiors", "figures", False, "H2O CO2"),
    "ordn": ("Ordinals", "figures", False, "1a 2o No. 5"),
    "tnum": ("Tabular figures", "figures", False, "11:11 20:48"),
    "pnum": ("Proportional figures", "figures", False, "11:11 20:48", {"with": ["tnum"]}),
    "zero": ("Slashed zero", "figures", False, "0 100 2007"),
    "ss01": ("Double-storey a", "alternates", False, "Blåbærsyltetøj på rugbrød"),
    "ss02": ("l with a curved foot", "alternates", False, "Illegal Il1 lille"),
}
FEATURE_NAMES = {t: (v[0], v[3]) for t, v in FEATURES.items()}  # tag -> (name, sample), for the proofs


def feature_entry(tag: str) -> dict:
    name, group, default, sample, *extra = FEATURES.get(tag, (tag, "builtin", False, ""))
    return {"tag": tag, "name": name, "sample": sample, "default": default, "group": group,
            **(extra[0] if extra else {})}


FIGURE_FORMS = (".tf", ".numr", ".dnom", ".zero")


def _category(name: str, uni: int | None) -> str:
    """uppercase lowercase figure punctuation symbol mark space alternate"""
    if uni is None:
        if "comb" in name:
            return "mark"
        return "figure" if any(f in name for f in FIGURE_FORMS) else "alternate"
    c = unicodedata.category(chr(uni))
    return {"Lu": "uppercase", "Ll": "lowercase", "Nd": "figure", "No": "figure", "Zs": "space",
            "Zl": "space", "Zp": "space", "Mn": "mark"}.get(c, "punctuation" if c.startswith("P") else "symbol")


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
           weight_names: list[tuple[int, str]], languages: list[dict], weight_map: list[tuple[int, float]]) -> None:
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
                  "max": a.maxValue, **({"map": [list(p) for p in weight_map]} if a.axisTag == "wght" else {})}
                 for a in fvar.axes],
        "instances": [{"name": name, "wght": w} for w, name in weight_names],
        "masters": [{"id": m.name, "name": m.style, "wght": m.wght, "opsz": m.opsz, "numbers": master_numbers(m)}
                    for m in masters],
        "features": [feature_entry(t) for t in sorted(tags)],
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
