"""Build: generator -> UFO masters and designspace in build/ -> fonts in fonts/ (fontc)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .font import build as build_glyphs
from .master import REGULAR_DISPLAY, Master
from .weights import DISPLAY, WEIGHT_MAP, WEIGHT_NAMES
from .ufo import write_designspace, write_ufo

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"
FONTS = ROOT / "fonts"
SOURCE_DATE_EPOCH = 1794960000  # 2026-11-18 00:00 UTC, the head table's created date


def fontc() -> str:
    exe = Path(sys.executable).parent / ("fontc.exe" if sys.platform == "win32" else "fontc")
    return str(exe) if exe.exists() else (shutil.which("fontc") or "fontc")


def compile_font(source: Path, out: Path, work: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    # a fixed timestamp keeps the output byte-identical between builds (fontc honours SOURCE_DATE_EPOCH)
    env = dict(os.environ, SOURCE_DATE_EPOCH=str(SOURCE_DATE_EPOCH))
    subprocess.run([fontc(), str(source), "-o", str(out), "-b", str(work)], check=True, env=env)
    return out


def ufo_path(m: Master) -> Path:
    return BUILD / "masters" / f"Orderly-{m.name}.ufo"


def build_static(m: Master = REGULAR_DISPLAY) -> Path:
    """The working font of Phases 0 and 1: one master compiled as a static TTF."""
    glyphs = build_glyphs(m)
    ufo = write_ufo(m, glyphs, ufo_path(m))
    out = FONTS / "static" / f"OrderlyDisplay-{m.style.split()[0]}.ttf"
    compile_font(ufo, out, BUILD / "fontc" / m.name)
    _write_metrics(m, glyphs)
    print(f"built {out.relative_to(ROOT)} ({len(glyphs)} glyphs)")
    return out


def _write_metrics(m: Master, glyphs) -> None:
    data = {n: {"advance": g.advance, "lsb": g.lsb, "rsb": g.rsb, "unicodes": list(g.unicodes)} for n, g in glyphs.items()}
    (BUILD / f"metrics-{m.name}.json").write_text(json.dumps(data, indent=1), encoding="utf-8")


def masters_ufos(masters: list[Master]) -> list[Path]:
    return [write_ufo(m, build_glyphs(m), ufo_path(m)) for m in masters]


def build_variable() -> Path:
    """The Display design on a weight axis, 100 to 900, from the Thin, Regular and Black masters."""
    ufos = masters_ufos(DISPLAY)
    ds = write_designspace(DISPLAY, ufos, BUILD / "masters" / "OrderlyDisplay.designspace", family="Orderly Display",
                           weight_map=WEIGHT_MAP, names=WEIGHT_NAMES)
    out = compile_font(ds, FONTS / "variable" / "OrderlyDisplay[wght].ttf", BUILD / "fontc" / "variable")
    print(f"built {out.relative_to(ROOT)}")
    return out


def check_compat() -> bool:
    """Prove the masters interpolate: fontTools' interpolatable check on the three Display masters."""
    ufos = masters_ufos(DISPLAY)
    r = subprocess.run([sys.executable, "-m", "fontTools.varLib.interpolatable", *map(str, ufos)], capture_output=True,
                       text=True)
    report = (r.stdout + r.stderr).strip()
    print("interpolatable check (Thin, Regular, Black):")
    print(report or "  no problems reported")
    return r.returncode == 0 and not report
