"""Build: generator -> UFO masters and designspace in build/ -> fonts in fonts/ (fontc)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .font import build as build_glyphs
from .master import MASTERS, REGULAR_DISPLAY, Master, scaled_master
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


def check_compat() -> bool:
    """Prove the masters interpolate: a throwaway light master beside each real one, checked and compiled."""
    real = MASTERS[0]
    light = scaled_master(real, "CompatLight", "Compat Light", 100, 0.35)
    ufos = []
    for m in (light, real):
        ufos.append(write_ufo(m, build_glyphs(m), BUILD / "compat" / f"Orderly-{m.name}.ufo"))
    ds = write_designspace([light, real], ufos, BUILD / "compat" / "Orderly-compat.designspace")
    print("interpolatable check:")
    r = subprocess.run([sys.executable, "-m", "fontTools.varLib.interpolatable", *map(str, ufos)], capture_output=True,
                       text=True)
    report = (r.stdout + r.stderr).strip()
    print(report or "  no problems reported")
    out = compile_font(ds, BUILD / "compat" / "Orderly-compat-VF.ttf", BUILD / "compat" / "fontc")
    print(f"compiled variable font {out.relative_to(ROOT)}")
    return r.returncode == 0 and not report
