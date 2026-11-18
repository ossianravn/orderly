# Orderly: production

How the fonts are built and checked: the tools, their versions, the commands, and QA results with the accepted
warnings. Decisions belong in the [plan](plan.md); this file records how they are carried out.

## Commands

Python runs through `uv`. From the repository root:

| Command                          | Does                                                                                     |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| `uv sync`                        | Installs the pinned environment (`pyproject.toml`, `uv.lock`).                           |
| `uv run orderly build`           | Generator -> UFOs and designspace in `build/masters/` -> `fonts/static/OrderlyDisplay-Regular.ttf` and `fonts/variable/OrderlyDisplay[wght].ttf`. |
| `uv run orderly sheets [group]`  | Outline sheets per master -> `proofs/sheets/{thin,regular,black}/`, overlays -> `proofs/sheets/overlay-*.png`. |
| `uv run orderly proof [page]`    | Browser proofs of the compiled font, light and dark -> `proofs/browser/*.png`.           |
| `uv run orderly look n o --text "nnonn"` | Quick look while drawing: named glyphs large with points, strings filled.        |
| `uv run orderly check`           | Interpolation check of the Thin, Regular and Black Display masters.                     |
| `uv run orderly serve`           | Serves the proof pages on port 4813 (also `.claude/launch.json`, configuration `proofs`). |
| `uv run orderly all`             | Build, sheets and browser proofs.                                                        |

`build/` (UFO masters, designspace, fontc work files, proof pages, metrics JSON) and `proofs/` are not committed.
`fonts/` is committed build output.

## Pipeline

`sources/orderly/` is the generator. `master.py` holds the numbers, `geom.py` the curve primitives (tension curves,
cutting paths at a coordinate), `parts.py` the compass (`Ell`), stems and joins, `rounds.py` the bowls, arches and
cut rounds, `shapes.py` the master-aware shared shapes, `glyphs/` the glyph functions by family, `spacing.py` the
area-based sidebearings, `font.py` runs the glyph functions and spaces and rounds the result, `ufo.py` writes UFO and
designspace, `build.py` calls the compiler. `proof/` holds both proof tools.

The generator writes UFO 3 masters with cubic outlines, outer contours counter-clockwise (PostScript direction);
fontc converts to quadratic TrueType outlines and reverses direction. Overlapping parts (stem over bowl) stay
separate contours.

## Tools and versions

Checked 2026-11-18 on Windows 11 with uv 0.8.15 and Python 3.13.2.

| Role                | Tool and version                         | Notes                                                                                                                                                                                                      |
| ------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Compiler            | **fontc 2.0.1** (PyPI wheel, `fontc.exe`) | Chosen over fontmake 3.12.2 by the plan's rule: it installs from PyPI with a Windows binary and builds a UFO to a static TTF and a designspace to a variable TTF in well under a second. Fallback: fontmake. |
| Sources             | fontTools 4.68.0, ufoLib2 0.19.1         | UFO and designspace writing; `fontTools.varLib.interpolatable` for the compatibility check.                                                                                                               |
| Outline sheets      | skia-python 144.1                        | Anti-aliased rendering with non-zero winding, so overlapping contours draw as the font will.                                                                                                              |
| Browser proofs      | playwright 1.65.2 (Python)               | Drives the installed Chrome (157 at the time of writing), else Edge, else Playwright's own Chromium (`uv run playwright install chromium`). Device scale factor 1, so 16 px is 16 screen pixels.            |
| Font QA             | fontbakery 1.1.0 (local), fontspector (CI) | See "QA tool" below. fontbakery is in the `qa` group; fontspector runs only in CI from Phase 5.                                                                                                            |

### Determinism

fontc writes the current time into `head.modified` unless `SOURCE_DATE_EPOCH` is set; `build.py` sets it to
2026-11-18 00:00 UTC (1794960000), the same date as `head.created`. Two builds of the same sources give the same
bytes (checked with SHA-256).

### QA tool

Ruled by the planner (2026-11-18): no downloaded executables.

- **Local QA: fontbakery 1.1.0** from PyPI, pinned in the `qa` dependency group of `pyproject.toml`. Run it with
  `uv run --group qa fontbakery check-universal fonts/...` (and `check-googlefonts`) from Phase 4 on.
- **CI: fontspector** (the Rust successor to fontbakery), installed only in GitHub Actions through its official
  `fonttools/setup-fontspector` action, from Phase 5. It is not on PyPI, and its Windows binary is a download.

## Spacing

`spacing.py` sets sidebearings by an area method in the manner of HT Letterspacer. On scanlines through the glyph's
zone (baseline to x-height for lowercase, to cap height otherwise) it measures the outline's distance from the
glyph's own extreme in that zone, clipped to a depth (`sp_depth`, 3 % of the zone height); the sidebearing makes
up the difference to a target area (`sp_area`, 0.09 of the zone height squared). Parts outside the zone (the
hooks of j and f, the tails of g and y) may reach into the sidebearing. `ADJUST` holds hand corrections in units;
in Phase 1 only J (-15 on the left). Resulting Regular Display values: n 45 | 40, o 34 | 34, H 63 | 63, O 47 | 47.

## Weight axis

`weights.py` defines the Thin and Black Display masters from Regular's numbers. The designspace's design
coordinates are the lowercase stem (20, 78, 186); its axis map takes user weights to stems (100 20, 200 35, 300 54,
400 78, 500 96, 600 116, 700 137, 800 160, 900 186), which fontc writes as `avar`, and the nine named instances
come from the same map. fontc also writes `STAT` (basic, to be reviewed in Phase 5) and `MVAR` (the Black x-height
is 506).

## Interpolation check

`uv run orderly check` writes the three Display masters to `build/masters/` and runs
`fontTools.varLib.interpolatable` on them. A glyph function that would draw different points in another master
fails here (or, for the cases the code guards, at build time with a message).

## Vertical metrics

Placeholders until Phase 5: typo and hhea ascender 950, descender -250, line gap 0, `USE_TYPO_METRICS` set, win
ascent 950 and descent 250. Phase 5 sets them by the Google Fonts specification once accents exist.

## QA results

None yet. Accepted warnings will be listed here with their reasons.
