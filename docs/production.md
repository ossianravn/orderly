# Orderly: production

How the fonts are built and checked: the tools, their versions, the commands, and QA results with the accepted
warnings. Decisions belong in the [plan](plan.md); this file records how they are carried out.

## Commands

Python runs through `uv`. From the repository root:

| Command                          | Does                                                                                     |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| `uv sync`                        | Installs the pinned environment (`pyproject.toml`, `uv.lock`).                           |
| `uv run orderly build`           | Generator -> six UFO masters and a designspace in `build/masters/` -> `fonts/variable/Orderly[opsz,wght].ttf`. |
| `uv run orderly sheets [group]`  | Outline sheets per master -> `proofs/sheets/{thin,regular,black}[-text]/`, overlays -> `proofs/sheets/overlay*-*.png`. |
| `uv run orderly proof [page]`    | Browser proofs of the compiled font, light and dark -> `proofs/browser/*.png`.           |
| `uv run orderly look n o --text "nnonn"` | Quick look while drawing: named glyphs large with points, strings filled.        |
| `uv run orderly grid cent yen --text "HHTHH"` | Named glyphs (or strings) filled, one row per master, all six masters -> `proofs/sheets/grid.png`. The fastest way to judge a drawing everywhere. |
| `uv run --group qa orderly languages` | hyperglot check of every listed language against the compiled font.                |
| `uv run orderly check`           | Interpolation check of all six masters; instantiates the six weight and size corners.   |
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
hooks of j and f, the tails of g and y) may reach into the sidebearing. `ADJUST` holds hand corrections in units:
J (-15 left), T (-12 each side, Phase 4). Resulting Regular Display values: n 45 | 40, o 34 | 34, H 63 | 63, O 47 | 47.

Glyphs with a fixed advance instead of area spacing: math signs (one width: 0.72 cap height plus 0.08 each side),
arrows (their square plus 0.07 each side), tabular figures (`tf.sb`: the widest figure plus 0.62 of the zero's own
sidebearing each side), the fraction slash (negative sidebearings), spacing accents (0.08 x-height each side), the
Catalan punt volat. Small forms (numerators, ordinals) are spaced by the area method of the small master
(`small.py`) and opened by 10 %.

## Kerning

`kerning.py`, class-based, computed per master from the outlines. Two rules:

- **Closing** (`PAIRS`): on scanlines through the pair's zone the gap between the inks is measured; a pair that
  stays further apart than its sidebearings would bring it (open, slanted or overhanging sides: AV, To, LT, 7.)
  closes by 0.42 of the difference, capped at 0.16 of the zone height; values under 8 units are dropped.
- **Clearing** (`OPEN`): pairs that collide outside the zone (`ff fl fi fb fh fk fj`, `f) f? f’`, `(j [j`) open
  until their inks are at least 0.75 of a stem apart anywhere from the descender to above the ascender.

Classes: capitals (A T V W Y L P F K R X, the O family), lowercase (r v f k o c on the left; a o u v s x, the
ascenders, i and j on the right), quotes, period and comma, dashes (with their `.case` forms), parentheses and
brackets, and the figures 1 4 7. Accented letters join their base letter's class; moved and local forms
(`hyphen.case`, `i.loclTRK`) and tabular figures stay out of every class, so tabular figures are never kerned.
About 230 to 245 class pairs per master.

## Features

`features.py` writes the feature code from the glyph names (written to `build/features.fea` on every build);
fontc adds `kern`, `mark` and `mkmk` from the masters' kerning and anchors. GSUB lookups apply in this order:

| Feature | What it does |
| --- | --- |
| `locl` | Romanian and Moldovan (ROM MOL): Ş ş Ţ ţ to the comma-below Ș ș Ț ț. Turkish, Azeri, Crimean Tatar (TRK AZE CRT): i to `i.loclTRK`, so a following mark keeps its dot. Catalan (CAT): l·l and L·L take the tighter punt volat. Dutch (NLD): í j and Í J take the accented j (íj́ ÍJ́). Northern, Inari, Skolt and Lule Sámi (NSM ISM SKS LSM): Ŋ takes the N-form `Eng.loclNSM`. |
| `ccmp` | i and j before a top mark become dotless; a top mark after a capital (or after another capital mark) takes its `.case` form. |
| `frac` | Contextual: figure / figure becomes numerator ⁄ denominator; slashes in dates and paths (1/2/2026) are left alone. |
| `numr` `dnom` `sups` `subs` | Figures to numerators, denominators, superiors (⁰¹²³⁴⁵⁶⁷⁸⁹), inferiors (₀…₉). |
| `ordn` | a and o after a figure become ª º; `No.` becomes №. |
| `tnum` `pnum` | Tabular figures on one width; back to proportional (the default). |
| `zero` | Slashed zero, proportional and tabular. |
| `case` | Hyphens, dashes, parentheses, brackets, braces, guillemets, ¡ ¿, colon, middle dot and bullet move up to sit with capitals and figures. |
| `ss01` | Double-storey a (named "Double-storey a"), with every accented a. |
| `ss02` | l with a curved foot (named "l with a curved foot"), with ĺ ľ ļ ł ŀ. |
| `cpsp` | GPOS: 10 units more on each side of every capital. |

Precomposed letters are composites (base plus marks placed by anchors), so `mark` and `mkmk` act only on combining
sequences the font has no precomposed glyph for; shapers recompose the others.

## Axes

Six masters: {Thin, Regular, Black} x {Text (opsz 12), Display (opsz 72)} in `weights.py` and `sizes.py`. The
weight axis's design coordinates are the Display lowercase stem (20, 78, 160); its map (100 20, 200 34, 300 52,
400 78, 500 94, 600 110, 700 127, 800 143, 900 160) becomes `avar`, and the nine named instances (at opsz 12) come
from the same map. The optical-size axis runs 12 to 72 in its own units (CSS px), default 12. The default master
is Regular Text; its UFO style name is "Regular", so the font names itself Orderly Regular. fontc writes `STAT`
(basic, Phase 5 reviews it) and `MVAR` (x-heights 500 to 520).

## Site data

`uv run orderly build` writes, after compiling the variable font (contract: the plan's "Site data"):

- `fonts/web/Orderly[opsz,wght].woff2`: the variable font, WOFF2 (fontTools with brotli 1.2.1).
- `fonts/data/orderly.json` and `fonts/data/outlines.json`, UTF-8 JSON, written by `sources/orderly/export.py`.

`orderly.json`:

```
{
  "family": "Orderly", "version": "0.100", "unitsPerEm": 1000,
  "metrics": { "ascender": 740, "capHeight": 700, "descender": -200,
               "xHeight": { "12": 516, "72": 500 },          // per optical size, Regular masters
               "line": { "ascender": 950, "descender": -250, "lineGap": 0 } },
  "axes": [ { "tag": "wght", "name": "Weight", "min": 100, "default": 400, "max": 900,
              "map": [ [100, 20], [200, 34], ..., [900, 160] ] },   // user weight -> design coordinate (avar)
            { "tag": "opsz", "name": "Optical size", "min": 12, "default": 12, "max": 72 } ],
  "instances": [ { "name": "Thin", "wght": 100 }, ... nine, at the default optical size ],
  "masters": [ { "id": "RegularText", "name": "Regular Text", "wght": 400, "opsz": 12,
                 "numbers": { "stem", "capStem", "bar", "capBar", "xHeight", "capHeight", "overshoot", "join",
                              "spacingArea", "dot" } }, ... six ],
  "features": [ { "tag": "kern", "name": "Kerning", "sample": "AVATAR Tower Yacht",
                  "default": true,                                // on unless switched off
                  "group": "builtin",                             // builtin capitals figures alternates
                  "lang": "ro",                                   // optional: BCP 47 tag the sample needs (locl)
                  "with": ["tnum"] }, ... as compiled ],          // optional: features to keep on (pnum)
  "languages": [ { "tag": "da", "iso639_3": "dan", "name": "Danish",
                   "sample": "Høj bly gom vandt fræk sexquiz på wc. ..." } ],   // a line of real words
  "glyphs": [ { "name": "a", "unicode": 97, "char": "a",        // unicode and char are null when unencoded
                "category": "lowercase",
                "metrics": { "RegularText": { "advance": 535, "lsb": 39, "rsb": 50 }, ... per master id } } ]
}
```

The weight map's design coordinates are the Regular Display lowercase stem in font units: the masters sit at 20
(Thin, user 100), 78 (Regular, 400) and 160 (Black, 900). To draw a user weight from the master outlines, map it
through `map` (piecewise linear) and interpolate the outlines linearly in that design coordinate. The optical size
axis is linear (user = design, 12 to 72).

Glyph categories: `uppercase` (Lu), `lowercase` (Ll), `figure` (Nd, No such as ² ½, and unencoded figure forms:
`.tf`, `.numr`, `.dnom`, `zero.zero`), `punctuation` (P*), `symbol` (everything else encoded, including spacing
accents ^ ` ¨ ´ and the ordinals ª º), `mark` (combining marks and their unencoded `.case` and `.alt` forms),
`space`, `alternate` (other unencoded glyphs: `a.ss01` and its composites, `l.ss02`, `.case` punctuation, `.locl`
forms).

Feature samples show a difference when the feature is switched alone, except where `lang` or `with` says what else
the sample needs. The `mark`, `mkmk` and `ccmp` samples are combining sequences whose precomposed letter the font
does not have (ẽ ỹ j́ X́): shapers recompose sequences the font has a precomposed glyph for, and those never reach
the mark features.

`outlines.json`:

```
{
  "unitsPerEm": 1000,
  "masters": [ "ThinText", "RegularText", "BlackText", "ThinDisplay", "RegularDisplay", "BlackDisplay" ],
  "glyphs": { "a": { "RegularText": [ { "part": "bowl",                 // or stem, bar, round, counter, arch,
                                         "points": [ { "x": 0, "y": 0, "on": true }, ... ] }, ... ],
                     ... every master } }
}
```

Contours are closed and start on an on-curve point; between two on-curve points there are zero (a line) or two
(a cubic) off-curve points. Outer contours run counter-clockwise, counters clockwise; overlapping parts are
separate contours. Every master has the same contours and points in the same order, so the page can interpolate
them. `part` is null where the generator has no name for the shape. Glyphs and features are added to these
shapes as they are drawn; the shapes themselves stay as documented here.

## Browser proofs

`uv run orderly proof` renders every page light and dark at device scale 1, and the small-size page also at 2.
The `optical-auto` page checks, in Chrome, that `font-optical-sizing: auto` draws each size exactly as the fixed
`opsz` of that size (clamped to 12..72) and differently from the far end of the axis, and prints the result.

## Interpolation check

`uv run orderly check` writes the six masters to `build/masters/`, runs
`fontTools.varLib.interpolatable` on them and instantiates the corners. A glyph function that would draw different points in another master
fails here (or, for the cases the code guards, at build time with a message).

## Vertical metrics

Placeholders until Phase 5: typo and hhea ascender 950, descender -250, line gap 0, `USE_TYPO_METRICS` set, win
ascent 950 and descent 250. Phase 5 sets them by the Google Fonts specification once accents exist.

## QA results

2026-11-18, Phase 4 gate, `Orderly[opsz,wght].ttf`, 524 glyphs (437 encoded).

- `uv run --group qa fontbakery check-universal -l WARN --succinct fonts/variable/Orderly[opsz,wght].ttf`:
  100 PASS, 3 FAIL, 1 ERROR, 0 WARN. The Google Fonts profile is Phase 5's.
- `uv run --group qa orderly languages` (hyperglot 0.8.2): all 32 listed languages supported.
- Glyph sets (glyphsets 1.1.3): GF Latin Kernel and GF Latin Core complete. GF Latin Plus is not a target; of it
  the font has ¦ ¬ ± ² ³ µ ¹ ¼ ½ ¾ π † ‡ ‰ ⁄ ⁴–⁹ ₀–₉ ₹ ₺ ₽ № Ω ⅓ ⅔ ← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙ ∂ ∆ ∏ ∑ √ ∞ ∫ ≈ ≠ ≤ ≥ ◊.
  (The Phase 4 progress note of the previous implementer said Latin Core was complete before the spacing accents
  and ¢ £ ¥ © ® × ÷ • € ™ § ¶ ª º existed; it was not.)

Open findings and their status:

| Check | Result | Status |
| --- | --- | --- |
| `family/win_ascent_and_descent` | FAIL | Phase 5 sets vertical metrics by the Google Fonts specification. |
| `inconsistencies_between_fvar_STAT` | FAIL | fontc's basic STAT lacks axis values for the instances; Phase 5 writes STAT. |
| `smart_dropout` | FAIL | No `prep` program yet; Phase 5 adds the smart-dropout instructions. |
| `name/family_and_style_max_length` | ERROR | The check itself crashes on this font; recheck in Phase 5. |

Fixed during Phase 4: `whitespace_glyphs` (nbspace added), `math_signs_width` (math signs share one advance),
`unreachable_glyphs` (every glyph is reached by a feature or a component, and every glyph has a GDEF class),
`nested_components` (½ ¼ ¾ ⅓ ⅔ use the numerator glyph moved down, not the denominator composite),
`overlapping_path_segments` (the braces' halves overlap in the nose without sharing an edge).

