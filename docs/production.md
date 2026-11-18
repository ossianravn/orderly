# Orderly: production

How the fonts are built and checked: the tools, their versions, the commands, and QA results with the accepted
warnings. Decisions belong in the [plan](plan.md); this file records how they are carried out.

## Commands

Python runs through `uv`. From the repository root:

| Command                          | Does                                                                                     |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| `uv sync`                        | Installs the pinned environment (`pyproject.toml`, `uv.lock`).                           |
| `uv run orderly build`           | Generator -> six UFO masters and a designspace in `build/masters/` -> `fonts/variable/Orderly[opsz,wght].ttf` (fontc), finished (`production.py`) -> 18 statics in `fonts/static/`, web fonts and `orderly.css` in `fonts/web/`, site data in `fonts/data/`. About 25 s. |
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
area-based sidebearings, `font.py` runs the glyph functions and spaces and rounds the result (and places composites:
by anchor, by offset, or one after another), `small.py` the scaled master for small forms, `kerning.py` and
`features.py` the kerning and feature code, `ufo.py` writes UFO and designspace, `build.py` calls the compiler,
`production.py` finishes the variable font and makes the statics and web fonts, `export.py` the site data.
`proof/` holds the proof tools (outline sheets, the six-master grid, browser pages).

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
| Font QA             | fontbakery 1.1.0 (local), fontspector (CI) | See "QA tool" below. fontbakery is in the `qa` group; fontspector runs only in CI.                                                                                                                         |
| Overlap removal     | skia-pathops 0.9.2                       | Used by fontTools' instancer to remove overlaps in the statics.                                                                                                                                           |

### Determinism

fontc writes the current time into `head.modified` unless `SOURCE_DATE_EPOCH` is set; `build.py` sets it to
2026-11-18 00:00 UTC (1794960000), the same date as `head.created`. Two builds of the same sources give the same
bytes (checked with SHA-256).

### QA tool

Ruled by the planner (2026-11-18): no downloaded executables.

- **Local QA: fontbakery 1.1.0** from PyPI, pinned in the `qa` dependency group of `pyproject.toml`:
  `uv run --group qa fontbakery check-universal -l WARN --succinct <fonts>`. The Google Fonts profile needs the
  `googlefonts` extra, which does not resolve inside the project environment (gfmetadata wants protobuf 6.33 or
  later against gflanguages' pins), so it runs in its own tool environment:
  `uvx --from "fontbakery[googlefonts]==1.1.0" fontbakery check-googlefonts -l WARN --succinct <fonts>`
  (set `PYTHONIOENCODING=utf-8` on Windows, or its report crashes printing ſ). Check each family on its own
  (`fonts/static/Orderly-*.ttf`, `fonts/static/OrderlyDisplay-*.ttf`, the variable font): run together, the
  family checks report Orderly and Orderly Display as one inconsistent family.
- **CI: fontspector** (the Rust successor to fontbakery), installed only in GitHub Actions through its official
  `fonttools/setup-fontspector` action. It is not on PyPI, and its Windows binary is a download.

### Continuous integration

`.github/workflows/fonts.yml`, on every push and pull request: install uv 0.8.15, `uv run --frozen orderly build`,
fail when `git status -- fonts/` shows any change (the committed fonts must be what the sources produce), then
fontspector: the universal profile on the variable font and both static families fails the job on any FAIL; the
Google Fonts profile on the variable font is reported in the job summary without failing it, because fontspector
could not be run locally to confirm its results match fontbakery's. Not yet verified on Linux: the build is
byte-identical run to run on Windows, but whether Linux gives the same bytes (fontc and skia-pathops are native
code) is first known from the first CI run. If only the statics differ, overlap removal is the place to look.

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
               "line": { "ascender": 1000, "descender": -300, "lineGap": 0 } },   // typo = hhea; line height 1.3
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

By the Google Fonts specification (gf-guide, "Vertical Metrics", read 2026-11-18): typo and hhea equal, line gaps
0, `USE_TYPO_METRICS` set, capitals centred in the line (typo ascender minus cap height equals the absolute typo
descender), about 130 % of the em in all, win metrics covering the bounding box of every master.

Measured from the outlines of all six corners: the tallest glyphs are Ǻ 1142 (Black: ring and acute), Å 988, Ů 919,
the dieresis capitals 903; the deepest are the comma-accented letters at -335 (Ķ ļ ș, Black) and the descenders
at -203 (g j). Set:

| Field | Value | Why |
| --- | --- | --- |
| typo and hhea ascender | 1000 | Clears every accented capital but the rare Ǻ (Å, the tallest in Nordic text, is 988). |
| typo and hhea descender | -300 | Capitals centred: 1000 - 700 = 300; deeper than the descenders (-203). |
| typo and hhea line gap | 0 | |
| win ascent, win descent | 1142, 335 | The outlines' extremes over all masters, computed at build time (`build.win_metrics`). |

Default line height: (1000 + 300 + 0) / 1000 = **1.3**. `orderly.json` carries these as `metrics.line`.

## Names, version and the rest of the variable font

`production.finish()` runs after fontc. Version **1.000** (`head.fontRevision` 1.0, name ID 5 "Version 1.000"):
the glyph set, features and production meet every criterion the plan set for the first release, and a version
under 1.0 tells apps and catalogues the family is unfinished. The maintainer tags the release; a later italic
or Cyrillic would be 1.100 or 2.000.

- Names: family Orderly, style Regular, `Orderly-Regular`, unique ID `1.000;NONE;Orderly-Regular`, designer and
  manufacturer Ossian Ravn, vendor and designer URL the repository, the OFL description and URL, variations
  PostScript name prefix (ID 25) Orderly. `fvar`: nine named instances Thin to Black at opsz 12, each with its
  PostScript name (`Orderly-Thin` ...).
- `STAT` (format 1 values): weight 100 Thin to 900 Black, Regular elided and linked to Bold; optical size 12pt
  and 72pt (the names the Google Fonts axis registry uses; optical-size values are never elided). Axis names
  Weight and Optical Size, as registered. Elided fallback name ID 2.
- Glyphs whose contours overlap (234 in the variable font: stem over bowl and the like; none in the statics,
  whose overlaps are removed) carry the overlap flag (OVERLAP_SIMPLE, or OVERLAP_COMPOUND on the first
  component), found by comparing each outline's area with that of its union (pathops). fsSelection has the WWS
  bit (the names follow the weight-width-slope model), in the statics too.
- Layout tables are packed by fontTools' own packer, never HarfBuzz's (`production.CFG`): fontTools uses the
  HarfBuzz repacker whenever `uharfbuzz` is importable, which the `qa` group installs, and the two give different
  bytes. Before this was pinned, local builds and CI disagreed on the statics and subsets (GSUB, GPOS only).
- `avar` from the weight map; `MVAR` (x-heights, from fontc).
- Unhinted TrueType: `gasp` 0xFFFF -> 0x000F (grid-fit and smoothing at every size) and a `prep` program setting
  smart dropout control (`PUSHW 511 SCANCTRL PUSHB 4 SCANTYPE`), as gftools' fix-unhinted does.
- `meta`: dlng and slng Latn. OS/2 fsType 0 (installable), usWeightClass 400, vendor ID blank (no registered ID).

## Statics

`production.statics()` cuts each named weight at opsz 12 (family **Orderly**) and opsz 72 (family **Orderly
Display**) with fontTools' instancer, removes overlaps (skia-pathops), drops points that overlap removal left on top
of their neighbour, and names them so apps group them: Regular and Bold are a style-linked pair under name ID 1
(Orderly, Orderly Display); the other weights carry their weight in name ID 1 (Orderly Thin) with name IDs 16 and
17 (Orderly / Thin). OS/2 weight class, fsSelection (REGULAR for every weight but Bold, BOLD for Bold) and
macStyle follow; each static has a one-value `STAT`. Files: `fonts/static/Orderly-Thin.ttf` ...
`OrderlyDisplay-Black.ttf`, and the same as WOFF2 in `fonts/web/static/`.

## Web

`production.web()` subsets the variable font (all layout features kept) into **Latin** (Google Fonts' Latin range)
and **Latin extended** (everything else the font covers: Latin Extended-A and B, symbols, arrows, math), WOFF2,
and writes `fonts/web/orderly.css` with one `@font-face` per subset and its `unicode-range`. The whole variable
font stays at `fonts/web/Orderly[opsz,wght].woff2` (the specimen site uses it).

## QA results

2026-11-18, Phase 5 gate (fontbakery 1.1.0; fontspector runs in CI only).

| Fonts | Universal profile | Google Fonts profile |
| --- | --- | --- |
| `Orderly[opsz,wght].ttf` | 0 FAIL, 0 WARN, 104 PASS | 0 FAIL, 4 WARN, 135 PASS |
| `Orderly-*.ttf` (9) | 0 FAIL, 9 WARN (contour_count) | 0 FAIL, 67 WARN |
| `OrderlyDisplay-*.ttf` (9) | 0 FAIL, 9 WARN (contour_count) | 0 FAIL, 71 WARN |

Accepted warnings and why:

| Check | Where | Why it stays |
| --- | --- | --- |
| `contour_count` | statics | Design, not defects: `@` (the a stands free in the ring), `§` (the two s overlap into a loop, or not in Thin), `ẞ` (a closed counter under the diagonal), Thin `&` (leg and bowl cross: four counters), Black `ǥ` (the bar closes a counter). Every other divergence it found was a real collision and was fixed (see below). |
| `googlefonts/article/images` | all | No Google Fonts article; Orderly is not submitted to Google Fonts. |
| `googlefonts/metadata/unreachable_subsetting` | all | Spacing accents, combining marks and symbols outside Google's subset definitions; our own subsets cover them. |
| `googlefonts/glyphsets/shape_languages` | all | Auxiliary (optional) characters of some languages, such as ſ for German and ʻ for English. |
| `googlefonts/vendor_id` | all | No registered vendor ID. |
| `outline_colinear_vectors`, `outline_short_segments`, `outline_jaggy_segments`, `outline_alignment_miss` | statics | Points where overlap removal joined two shapes (stem and bowl, diagonal and bar) and the 1-unit steps rounding leaves there. The two that were real spurs (Ʒ and ẞ: a diagonal poking out of its bar) were fixed. |

fontspector (CI, latest release, run 2026-11-18 on commit f45b5a4 before the fixes in the next paragraph):
universal profile 0 FAIL on the variable font and Orderly statics (31 WARN) and on Orderly Display (23 WARN);
Google Fonts profile on the variable font 0 FAIL, 12 WARN. Its warnings beyond fontbakery's were then fixed:
`valid_glyphnames` (nbspace renamed uni00A0), `opentype/fsselection_wws` (WWS bit), `overlaps_bit` (overlap flags, only where contours overlap),
`opentype/fvar/registered_axis_tags` ("Optical Size"), `googlefonts/STAT/opsz_not_elided`,
`googlefonts/separator_glyphs` (empty U+2028 and U+2029 added). Left: `suspicious_sidebearings` on a few glyphs
whose right side changes more than most across weights by design (the Black `l.ss02` hook is shorter, so its
advance drops; the ring and acute of `å Ǻ`; `↙`; `Ʒ`; `six.numr`), `contour_count` as above, and the Google
Fonts warnings above. `fontdata_namecheck` (fontbakery, online) sometimes errors when its web service answers
oddly; it is not about the font.

Fixed during Phase 5, found by these checks: tilde touching its letter in Black (`ñ ã õ ĩ`), Black breve with an
inverted counter, Black `5` whose foot closed onto its stem, `⅔` numerator touching the slash, floating ogonek on
`ę Ų`, the caron of `ǩ` on the ascender, Lithuanian `į̀ į́ į̃` keeping the dot (dotless `iogonek` in `ccmp`),
missing dotted circle, missing `meta`, Mac name records from STAT, the licence description, STAT names for
optical size, ss01/ss02 names lost in the statics, zero-length segments after overlap removal, non-reproducible
timestamps in post-processed files.

Languages and glyph sets:

- `uv run --group qa orderly languages` (hyperglot 0.8.2): all 32 listed languages supported.
- Glyph sets (glyphsets 1.1.3): GF Latin Kernel and GF Latin Core complete. GF Latin Plus is not a target; of it
  the font has ¦ ¬ ± ² ³ µ ¹ ¼ ½ ¾ π † ‡ ‰ ⁄ ⁴–⁹ ₀–₉ ₹ ₺ ₽ № Ω ⅓ ⅔ ← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙ ∂ ∆ ∏ ∑ √ ∞ ∫ ≈ ≠ ≤ ≥ ◊.
  (The previous implementer's Phase 4 note said Latin Core was complete before the spacing accents and
  ¢ £ ¥ © ® × ÷ • € ™ § ¶ ª º existed; it was not.)

The Phase 4 gate's open items are closed: `family/win_ascent_and_descent` (vertical metrics),
`inconsistencies_between_fvar_STAT` (STAT), `smart_dropout` (prep), and `name/family_and_style_max_length`, which
crashed under fontc's names and passes now.

Fixed during Phase 4: `whitespace_glyphs` (nbspace added), `math_signs_width` (math signs share one advance),
`unreachable_glyphs` (every glyph is reached by a feature or a component, and every glyph has a GDEF class),
`nested_components` (½ ¼ ¾ ⅓ ⅔ use the numerator glyph moved down, not the denominator composite),
`overlapping_path_segments` (the braces' halves overlap in the nose without sharing an edge).

