"""Compare the fonts in fonts/ with the committed ones (git HEAD), table by table, and glyph by glyph where the
outlines differ: the CI prints this when a rebuild does not reproduce the committed bytes.

uv run orderly fontdiff [paths...]   (default: every font file git reports as changed under fonts/)
"""

from __future__ import annotations

import io
import subprocess

from fontTools.ttLib import TTFont

from .build import ROOT


def _changed() -> list[str]:
    out = subprocess.run(["git", "status", "--porcelain", "--", "fonts/"], cwd=ROOT, capture_output=True, text=True)
    return [line[3:] for line in out.stdout.splitlines() if line.endswith((".ttf", ".woff2"))]


def compare(path: str, limit: int = 5) -> None:
    old = TTFont(io.BytesIO(subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)))
    new = TTFont(ROOT / path)
    tags = sorted(set(old.keys()) | set(new.keys()))
    diff = [t for t in tags if t != "GlyphOrder" and (t not in old or t not in new
                                                    or old.reader[t] != new.reader[t])]
    print(f"{path}: tables that differ: {', '.join(diff) or 'none'}")
    if "glyf" in diff:
        shown = 0
        for name in old.getGlyphOrder():
            a, b = old["glyf"][name], new["glyf"][name]
            ca = list(a.getCoordinates(old["glyf"])[0]) if a.numberOfContours else []
            cb = list(b.getCoordinates(new["glyf"])[0]) if b.numberOfContours else []
            if ca != cb:
                pairs = [(p, q) for p, q in zip(ca, cb) if p != q][:3]
                print(f"  glyf {name}: {len(ca)} -> {len(cb)} points; first differences {pairs}")
                shown += 1
                if shown >= limit:
                    break


def main(paths: list[str]) -> None:
    for p in paths or _changed():
        compare(p)
