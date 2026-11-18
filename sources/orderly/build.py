"""Build: generator -> UFO masters and designspace in build/ -> fonts in fonts/ (fontc)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .export import export, woff2
from .features import features
from .font import build as build_glyphs
from .kerning import compute as kern_compute
from .master import Master
from .sizes import TEXT
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


MASTERS = TEXT + DISPLAY  # Regular Text (wght 400, opsz 12) is the default master

CPSP = "<10 0 20 0>"  # capital spacing: 10 units more on each side of a capital


def masters_ufos(masters: list[Master]) -> list[Path]:
    return [write_ufo(m, build_glyphs(m), ufo_path(m)) for m in masters]


def build_variable() -> Path:
    """Orderly: weight 100 to 900 and optical size 12 to 72 from six masters (Text and Display x three weights),
    then the web font and the site's data."""
    sets = [build_glyphs(m) for m in MASTERS]
    fea = features(sets[0], CPSP)
    (BUILD / "features.fea").parent.mkdir(parents=True, exist_ok=True)
    (BUILD / "features.fea").write_text(fea, encoding="utf-8", newline="\n")
    ufos = [write_ufo(m, g, ufo_path(m), features=fea, kerning=kern_compute(m, g)) for m, g in zip(MASTERS, sets)]
    ds = write_designspace(MASTERS, ufos, BUILD / "masters" / "Orderly.designspace", family="Orderly",
                           weight_map=WEIGHT_MAP, names=WEIGHT_NAMES)
    out = compile_font(ds, FONTS / "variable" / "Orderly[opsz,wght].ttf", BUILD / "fontc" / "variable")
    _write_metrics(MASTERS[1], sets[1])
    web = woff2(out, FONTS / "web" / "Orderly[opsz,wght].woff2")
    weights = [(u, n) for (u, _), n in zip(WEIGHT_MAP, WEIGHT_NAMES)]
    export(MASTERS, sets, out, FONTS / "data", weights, languages(), WEIGHT_MAP)
    print(f"built {out.relative_to(ROOT)}, {web.relative_to(ROOT)}, fonts/data/orderly.json, fonts/data/outlines.json")
    return out


def languages() -> list[dict]:
    try:
        from .coverage import supported
    except ImportError:
        return []
    return supported()


def _write_metrics(m: Master, glyphs) -> None:
    data = {n: {"advance": g.advance, "lsb": g.lsb, "rsb": g.rsb, "unicodes": list(g.unicodes)} for n, g in glyphs.items()}
    (BUILD / f"metrics-{m.name}.json").write_text(json.dumps(data, indent=1), encoding="utf-8", newline="\n")


def check_compat() -> bool:
    """Prove the masters interpolate (fontTools' interpolatable on all six) and that every corner instantiates."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    ufos = masters_ufos(MASTERS)
    r = subprocess.run([sys.executable, "-m", "fontTools.varLib.interpolatable", *map(str, ufos)], capture_output=True,
                       text=True)
    report = (r.stdout + r.stderr).strip()
    print("interpolatable check (six masters):")
    print(report or "  no problems reported")
    vf = FONTS / "variable" / "Orderly[opsz,wght].ttf"
    for wght in (100, 400, 900):
        for opsz in (12, 72):
            inst = instantiateVariableFont(TTFont(vf), {"wght": wght, "opsz": opsz})
            inst.save(BUILD / f"corner-{wght}-{opsz}.ttf")
    print("instantiated wght 100 / 400 / 900 x opsz 12 / 72 from the variable font")
    return r.returncode == 0 and not report
