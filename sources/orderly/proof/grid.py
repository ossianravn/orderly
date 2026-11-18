"""A grid sheet: named glyphs filled, one row per master (Thin, Regular, Black x Text, Display), with the
baseline, x-height and cap height drawn, so a drawing can be judged in every master at once.

uv run orderly grid cent sterling yen [--scale 0.16] [--out name] [--text "Hamburg|ORDERLY"]
"""

from __future__ import annotations

import skia

from ..build import ROOT
from ..font import build
from .sheets import FONT, INK, METRIC, OUT, _save, paint, to_path
from .text import names_for

ROWS = ["thin-text", "regular-text", "black-text", "thin", "regular", "black"]


def grid(args: list[str]) -> None:
    from .sheets import master_named

    scale, out, text, names = 0.16, "grid", None, []
    it = iter(args)
    for a in it:
        if a == "--scale":
            scale = float(next(it))
        elif a == "--out":
            out = next(it)
        elif a == "--text":
            text = next(it)
        else:
            names.append(a)
    masters = [master_named(k) for k in ROWS]
    sets = [build(m) for m in masters]
    if text:
        lines = text.split("|")
        rows = [(m, s, names_for(line, s)) for line in lines for m, s in zip(masters, sets)]
    else:
        rows = [(m, s, [n for n in names if n in s]) for m, s in zip(masters, sets)]
    top, bot = 980, -320
    row_h = (top - bot) * scale
    width = int(max(sum(s[n].advance for n in ns) * scale for _, s, ns in rows) + 140)
    surface = skia.Surface(width, int(row_h * len(rows) + 20))
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)
    y = 10.0
    for m, s, ns in rows:
        canvas.drawString(m.name.replace("Display", "D").replace("Text", "T"), 6, y + top * scale, FONT, paint(INK))
        x = 120.0
        canvas.save()
        canvas.translate(x, y + top * scale)
        canvas.scale(scale, -scale)
        total = sum(s[n].advance for n in ns)
        for yy in (0, m.xh, m.cap):
            canvas.drawLine(0, yy, total, yy, paint(METRIC, 0.8 / scale))
        dx = 0.0
        for n in ns:
            canvas.drawPath(to_path(s[n], dx, glyphs=s), paint(INK))
            canvas.drawLine(dx, bot * 0.6, dx, bot * 0.5, paint(METRIC, 0.8 / scale))
            dx += s[n].advance
        canvas.restore()
        y += row_h
    p = _save(surface, OUT / f"{out}.png")
    print(f"wrote {p.relative_to(ROOT)}")
