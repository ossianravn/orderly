"""Outline sheets straight from the generator (no compile): glyphs large with metric lines, points and handles,
sidebearings; filled strings for spacing; masters overlaid. PNG files under proofs/sheets/.
"""

from __future__ import annotations

from pathlib import Path

import skia

from ..build import ROOT
from ..font import Glyph, build
from ..master import REGULAR_DISPLAY, Master

OUT = ROOT / "proofs" / "sheets"
FONT = skia.Font(skia.Typeface("Segoe UI"), 15)
SMALL = skia.Font(skia.Typeface("Segoe UI"), 12)

INK = skia.Color(28, 28, 30)
FILL = skia.Color(214, 216, 222)
METRIC = skia.Color(120, 160, 220)
ZONE = skia.Color(232, 240, 252)
SB = skia.Color(220, 90, 80)
HANDLE = skia.Color(70, 130, 220)
ONC = skia.Color(220, 60, 50)
OVERLAY = [skia.Color(220, 60, 50), skia.Color(40, 110, 220), skia.Color(30, 150, 80)]


def to_path(g: Glyph, dx: float = 0.0, dy: float = 0.0, glyphs: dict | None = None) -> skia.Path:
    p = skia.Path()
    p.setFillType(skia.PathFillType.kWinding)
    for c in (g.outline(glyphs) if glyphs else g.contours):
        p.moveTo(c.segs[0][0][0] + dx, c.segs[0][0][1] + dy)
        for s in c.segs:
            if len(s) == 4:
                p.cubicTo(s[1][0] + dx, s[1][1] + dy, s[2][0] + dx, s[2][1] + dy, s[3][0] + dx, s[3][1] + dy)
            else:
                p.lineTo(s[1][0] + dx, s[1][1] + dy)
        p.close()
    return p


def paint(color, stroke: float | None = None) -> skia.Paint:
    pt = skia.Paint(AntiAlias=True, Color=color)
    if stroke is not None:
        pt.setStyle(skia.Paint.kStroke_Style)
        pt.setStrokeWidth(stroke)
    return pt


def _smooth(prev, cur, nxt) -> bool:
    a = (cur[0] - prev[0], cur[1] - prev[1])
    b = (nxt[0] - cur[0], nxt[1] - cur[1])
    cross = a[0] * b[1] - a[1] * b[0]
    dot = a[0] * b[0] + a[1] * b[1]
    na = (a[0] ** 2 + a[1] ** 2) ** 0.5 * (b[0] ** 2 + b[1] ** 2) ** 0.5
    return na > 0 and dot > 0 and abs(cross) / na < 0.02


def draw_points(canvas, g: Glyph, s: float) -> None:
    """On-curve points (circles where smooth, squares at corners), off-curve points and handles."""
    for c in g.contours:
        segs = c.segs
        for k, seg in enumerate(segs):
            if len(seg) == 4:
                canvas.drawLine(seg[0][0], seg[0][1], seg[1][0], seg[1][1], paint(HANDLE, 1.0 / s))
                canvas.drawLine(seg[3][0], seg[3][1], seg[2][0], seg[2][1], paint(HANDLE, 1.0 / s))
                for h in seg[1:3]:
                    canvas.drawCircle(h[0], h[1], 3.2 / s, paint(skia.ColorWHITE))
                    canvas.drawCircle(h[0], h[1], 3.2 / s, paint(HANDLE, 1.2 / s))
            nxt = segs[(k + 1) % len(segs)]
            p = seg[-1]
            if _smooth(seg[-2], p, nxt[1]):
                canvas.drawCircle(p[0], p[1], 4.2 / s, paint(ONC))
            else:
                r = 4.0 / s
                canvas.drawRect(skia.Rect(p[0] - r, p[1] - r, p[0] + r, p[1] + r), paint(ONC))
        st = segs[0][0]
        canvas.drawCircle(st[0], st[1], 8 / s, paint(ONC, 1.4 / s))


def glyph_sheet(m: Master, names: list[str], out: Path, cols: int = 4, scale: float = 0.5, points: bool = True,
                glyphs: dict[str, Glyph] | None = None) -> Path:
    glyphs = glyphs or build(m)
    names = [n for n in names if n in glyphs]
    top, bot = m.asc + 70, m.desc - 50
    cell_h = (top - bot) * scale + 40
    widths = [glyphs[n].advance * scale + 60 for n in names]
    rows = [names[i : i + cols] for i in range(0, len(names), cols)]
    w = int(max(sum(widths[i : i + cols]) for i in range(0, len(names), cols)) + 20)
    h = int(cell_h * len(rows) + 20)
    surface = skia.Surface(w, h)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)
    y = 10.0
    i = 0
    for row in rows:
        x = 10.0
        for n in row:
            g = glyphs[n]
            cw = widths[i]
            i += 1
            canvas.save()
            canvas.translate(x + 30, y + top * scale)
            canvas.scale(scale, -scale)
            for lo, hi in ((-m.os(m.xh), 0), (m.xh, m.xh + m.os(m.xh)), (m.cap, m.cap + m.os(m.cap))):
                canvas.drawRect(skia.Rect(-60, lo, g.advance + 60, hi), paint(ZONE))
            for yy in (0, m.xh, m.cap, m.asc, m.desc):
                canvas.drawLine(-60, yy, g.advance + 60, yy, paint(METRIC, 1.0 / scale))
            canvas.drawLine(0, bot, 0, top, paint(SB, 1.0 / scale))
            canvas.drawLine(g.advance, bot, g.advance, top, paint(SB, 1.0 / scale))
            path = to_path(g, glyphs=glyphs)
            canvas.drawPath(path, paint(FILL if points else INK))
            if points:
                canvas.drawPath(path, paint(INK, 1.3 / scale))
                draw_points(canvas, g, scale)
            canvas.restore()
            label = f"{n}  {g.advance}  ({g.lsb} | {g.rsb})"
            canvas.drawString(label, x + 30, y + cell_h - 14, FONT, paint(INK))
            x += cw
        y += cell_h
    return _save(surface, out)


def overlay_sheet(masters: list[Master], names: list[str], out: Path, cols: int = 4, scale: float = 0.5) -> Path:
    sets = [build(m) for m in masters]
    base = masters[0]
    top, bot = base.asc + 70, base.desc - 50
    cell_h = (top - bot) * scale + 40
    adv = {n: max(s[n].advance for s in sets) for n in names}
    rows = [names[i : i + cols] for i in range(0, len(names), cols)]
    w = int(max(sum(adv[n] * scale + 60 for n in r) for r in rows) + 20)
    surface = skia.Surface(w, int(cell_h * len(rows) + 20))
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)
    y = 10.0
    for row in rows:
        x = 10.0
        for n in row:
            canvas.save()
            canvas.translate(x + 30, y + top * scale)
            canvas.scale(scale, -scale)
            for yy in (0, base.xh, base.cap):
                canvas.drawLine(-60, yy, adv[n] + 60, yy, paint(METRIC, 1.0 / scale))
            for k, s in enumerate(sets):
                canvas.drawPath(to_path(s[n], glyphs=s), paint(OVERLAY[k % 3], 1.6 / scale))
            canvas.restore()
            canvas.drawString(n, x + 30, y + cell_h - 14, FONT, paint(INK))
            x += adv[n] * scale + 60
        y += cell_h
    return _save(surface, out)


def text_sheet(m: Master, lines: list[str], out: Path, sizes=(48, 96), glyphs: dict[str, Glyph] | None = None,
               width: int = 1800) -> Path:
    """Filled strings laid out by advance (no kerning, no compile): a quick look at spacing."""
    from .text import names_for

    glyphs = glyphs or build(m)
    total = sum(int(sz * 1.35) for sz in sizes) * len(lines) + 40
    surface = skia.Surface(width, total)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorWHITE)
    y = 20.0
    for line in lines:
        for sz in sizes:
            s = sz / 1000
            y += sz * 1.0
            x = 30.0
            for n in names_for(line, glyphs):
                g = glyphs[n]
                canvas.save()
                canvas.translate(x, y)
                canvas.scale(s, -s)
                canvas.drawPath(to_path(g, glyphs=glyphs), paint(INK))
                canvas.restore()
                x += g.advance * s
            y += sz * 0.35
    return _save(surface, out)


def _save(surface, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    surface.makeImageSnapshot().save(str(out), skia.kPNG)
    return out


MASTER_KEYS = {"thin": "THIN_DISPLAY", "regular": "REGULAR_DISPLAY", "black": "BLACK_DISPLAY",
               "thin-text": "THIN_TEXT", "regular-text": "REGULAR_TEXT", "black-text": "BLACK_TEXT"}


def master_named(key: str) -> Master:
    from .. import sizes, weights

    if key == "regular":
        return REGULAR_DISPLAY
    return getattr(sizes if key.endswith("-text") else weights, MASTER_KEYS[key])


def look(args: list[str]) -> None:
    """Quick look while drawing: the named glyphs large with points, and strings of them filled.

    uv run orderly look n o [--text "nnonn|oonoo"] [--scale 0.8] [--master thin|regular|black|all]
    """
    scale, text, key = 0.8, None, "regular"
    names = []
    it = iter(args)
    for a in it:
        if a == "--scale":
            scale = float(next(it))
        elif a == "--text":
            text = next(it)
        elif a == "--master":
            key = next(it)
        else:
            names.append(a)
    keys = list(MASTER_KEYS) if key == "all" else [key]
    for k in keys:
        m = master_named(k)
        glyphs = build(m)
        tag = "" if len(keys) == 1 else f"-{k}"
        if names:
            p = glyph_sheet(m, names, OUT / f"look{tag}.png", cols=max(1, int(1500 / (scale * 900))), scale=scale,
                            glyphs=glyphs)
            print(f"wrote {p.relative_to(ROOT)}")
        if text:
            p = text_sheet(m, text.split("|"), OUT / f"look-text{tag}.png", sizes=(40, 110), glyphs=glyphs)
            print(f"wrote {p.relative_to(ROOT)}")


def render_all(names: list[str] | None = None) -> None:
    """Every sheet for each Display master (points, filled), strings, and the three masters overlaid."""
    from .text import GROUPS, SPACING_LINES

    for key in MASTER_KEYS:
        m = master_named(key)
        glyphs = build(m)
        out = OUT / key
        groups = {k: v for k, v in GROUPS.items() if names is None or k in names}
        for gk, members in groups.items():
            present = [n for n in members if n in glyphs]
            if present:
                glyph_sheet(m, present, out / f"{gk}.png", glyphs=glyphs)
                glyph_sheet(m, present, out / f"{gk}-fill.png", cols=8, scale=0.22, points=False, glyphs=glyphs)
        text_sheet(m, SPACING_LINES, out / "strings.png", glyphs=glyphs)
        print(f"wrote {out.relative_to(ROOT)}/*.png")
    for tag, keys in (("", ("thin", "regular", "black")), ("-text", ("thin-text", "regular-text", "black-text")),
                      ("-sizes", ("regular-text", "regular"))):
        masters = [master_named(k) for k in keys]
        for gk in ("control", "lc-rounds", "uc-rounds", "uc-diagonal", "figures"):
            overlay_sheet(masters, GROUPS[gk], OUT / f"overlay{tag}-{gk}.png", cols=5, scale=0.42)
    print(f"wrote {OUT.relative_to(ROOT)}/overlay-*.png")
