# Orderly: plan

Orderly is an open-source geometric grotesk typeface, drawn in code, with a small website that shows it. This plan
holds the decisions, the phases and the progress log. The letterforms are specified in the [design brief](design.md).

Inspiration: the [Halden Grotesk specimen](https://miaai-lab.github.io/Claude-Fable-5.2-HTML-Files/045-foundry-specimen-halden.html),
a page that draws a geometric grotesk from numbered points without shipping a font. Orderly takes its calm, its
construction logic and its editorial specimen layout, and ships the real font. Neither the letterforms nor the page
are copies.

## Decisions

Decided by the maintainer on 2026-11-18 unless marked otherwise.

| Topic         | Decision                                                                                                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Name          | Orderly. A web search found no typeface of that name (closest: "Order" by Typodermic). Phase 5 repeats the check against font catalogues.                                      |
| Family scope  | One upright variable font with two axes: weight (`wght`) and optical size (`opsz`). Italic is a later round.                                                                   |
| Licence       | Fonts: SIL Open Font License 1.1 (`OFL.txt`). Code and website: MIT (`LICENSE`).                                                                                               |
| Hosting       | GitHub Pages, deployed by a GitHub Action on push to `main`, at `https://ossianravn.github.io/orderly/`.                                                                       |
| Credits       | Honest colophon: by Ossian Ravn, drawn in code with Claude. Font copyright line: `Copyright 2026 The Orderly Project Authors (https://github.com/ossianravn/orderly)`.         |
| Site sections | Named with words. No "01, 02" numbering anywhere.                                                                                                                              |
| Git           | Commit and push to `main` without asking when the change is non-destructive.                                                                                                   |
| Capital widths | Planner's ruling after the Phase 1 review (2026-11-18): the brief's capital widths are advance widths over the cap height. `O Q` are true circles and so come to about 1.17; the circle wins. |
| Vertical metrics | Planner's ruling (2026-11-18): placeholder values (950 / -250) until Phase 5 sets them by the Google Fonts specification.                                                     |
| Weight range  | Planner's ruling after the Phase 2 review (2026-11-18): the top master is a lowercase stem of about 160, not 186 (an ultra the geometry cannot carry). Nine named weights and `wght` 100 to 900 stay; the map is tuned by eye for even steps. |
| QA tool       | Planner's ruling (2026-11-18): no downloaded executables. fontbakery from PyPI in the uv environment for local QA from Phase 4; fontspector only in CI through its official setup action (Phase 5). |

Everything below is the planner's proposal (Claude, 2026-11-18). The maintainer can overrule any of it; record the
change in this table.

## What "high quality in late 2026" means here

Each line is an acceptance criterion for the release, checked in Phase 5.

- **Variable first.** One TrueType-flavoured variable font with `fvar`, `STAT`, `avar` and named instances; static
  instances generated from it for apps that need them; WOFF2 for the web, also subset by script with `unicode-range`.
- **Sources build the fonts.** One command rebuilds every font file from the repository, and the same sources give the
  same bytes.
- **Masters interpolate.** Every glyph has the same contours, points and order in every master.
- **Points at extremes**, no stray points, no near-duplicate points, consistent contour direction.
- **Spacing before kerning.** Sidebearings carry the rhythm; kerning only fixes pairs that spacing cannot. Kerning is
  class-based.
- **Language support is tested**, not assumed: Google Fonts Latin Core complete, and every Latin-script official
  language of the EU and the Nordic countries (Sámi and Greenlandic included) plus Turkish, verified with a coverage
  tool.
- **Diacritics by anchors**: composites are components placed by anchors, and the font carries `mark` and `mkmk`.
- **OpenType features that people use**: `kern`, `mark`, `mkmk`, `ccmp`, `locl`, `case`, `cpsp`, `frac`, `numr`,
  `dnom`, `sups`, `subs`, `ordn`, `tnum`, `pnum`, `zero`, and a few stylistic sets (see the design brief).
- **Vertical metrics** follow the Google Fonts specification (typo and hhea equal, `USE_TYPO_METRICS` set, win
  metrics cover the bounding box), so lines sit the same on every platform.
- **Automated QA is clean**: no FAIL from the font QA tool's universal and Google Fonts profiles; every WARN either
  fixed or explained in `docs/production.md`.
- **Looked at.** Every glyph has been looked at large, and running text has been looked at small, in a real browser,
  in light and dark.

Tooling moves, so check current documentation before choosing: the Google Fonts toolchain has been moving from
`fontmake` and `fontbakery` (Python) to `fontc` and `fontspector` (Rust). Prefer the current tool when it installs and
works on Windows and in CI; fall back to the older one otherwise. Record the choice and the versions in
`docs/production.md`.

## Architecture

### The font is a program

Hand-placing thousands of points across six masters does not scale and does not stay consistent. Orderly's source is a
Python package that draws each glyph from parameters:

- **A master is a set of numbers** (`Master`): heights, stem widths, contrast, join thinning, apertures, spacing,
  curve tension. Six masters differ only in these numbers: {Thin, Regular, Black} x {Text, Display}.
- **A glyph is a function** of a master that returns contours, anchors and an advance. It builds from shared
  primitives: straight stems and bars, rings, variable-width strokes along a skeleton with cut terminals, diagonals.
  Shared parts are shared code: the bowl of `b d p q`, the arch of `n h m r u`, the hook of `f j t`.
- **Curves are drawn the way type designers draw them**: on-curve points at extremes, handles horizontal or vertical
  there, one tension value shaping how round or square a quadrant is.
- **A glyph function takes the same path through its code for every master**, so the masters are compatible by
  construction. Overlapping parts stay overlapping in the variable font (stem over bowl); static instances get their
  overlaps removed.
- **Joins are thinned.** Where a curve enters a stem, the stroke narrows, by a master parameter. Parts that merely
  overlap at full weight make dark clots, the mark of an amateur font.
- **Spacing is computed, then adjusted**: an area-based sidebearing calculation per glyph, with an explicit table of
  hand adjustments. Kerning likewise: computed for a pair list by class, small values dropped, then adjusted.

The generator writes UFO masters and a designspace into `build/` (not committed); the font compiler turns them into
binaries in `fonts/` (committed, so downloads and the site need no font toolchain).

### Layout

```
sources/orderly/    the generator: masters, primitives, glyphs, spacing, kerning, features, build
fonts/              built fonts: variable/, static/, web/
proofs/             rendered proof images (not committed)
site/               the showcase website (Astro)
docs/               plan.md, design.md, production.md (pipeline, QA results; written in Phase 0)
```

Python runs through `uv`; the site through `npm` inside `site/`. Dev server ports: site dev **4811**, site preview
**4812**, proof server **4813** (`.claude/launch.json`).

### Proofs

An agent cannot judge a letter from coordinates. Two proof tools are part of the pipeline from Phase 0:

- **Outline sheets** straight from the generator, no compile needed: glyphs large, with metric lines, on-curve and
  off-curve points, sidebearings; and masters overlaid. PNG files an agent can open.
- **Browser proofs** of the compiled font: words and text at 9 to 200 px, every weight, both optical sizes, light and
  dark, screenshotted from a real browser engine to PNG.

### Site data

The font build exports one JSON file for the site: axes, instances, metrics, features, languages, the glyph list with
Unicode values, advances and outlines per master. The site shows these numbers; none is typed by hand.

## Phases

One phase at a time. Each ends at a **gate**: the implementer stops, writes what was built and how it was checked in
the progress log, commits, pushes, and the reviewer looks before the next phase starts.

### Phase 0: pipeline proof

Repository skeleton, licences, `uv` environment, generator skeleton, both proof tools, and the control glyphs
`H O n o` of the Regular Display master compiled to a font.

Gate: one command builds a TTF containing `H O n o`; an outline sheet and a browser proof exist as PNG; tool choices
and versions are in `docs/production.md`.

### Phase 1: Regular Display

`A-Z a-z 0-9` and basic punctuation (`. , : ; ! ? - ' " ( ) / &`) plus `Æ Ø Å æ ø å`, spaced, in the Regular Display
master. Draw in the order of the design brief's control strings; settle the control glyphs before drawing the rest.

Gate: outline sheets for every glyph; browser proofs of the brief's test words and a paragraph at 16 to 200 px.
Every item on the brief's review checklist passes in the implementer's own judgement, with the weak spots named.

### Phase 2: weight

Thin and Black Display masters; the variable font with `wght` 100 to 900; `avar` so the named weights step evenly to
the eye.

Gate: masters interpolate cleanly (tool-checked); proofs of all nine weights; the Black's counters stay open and the
Thin's joins stay clean. If an extreme cannot meet the brief, propose a narrower range instead of shipping it.

### Phase 3: optical size

Three Text masters; the variable font with `opsz` 12 to 72 (default 12, the Text design).

Gate: browser proofs of running text at 9, 11, 13, 16 px with Text against Display at the same size, and headlines at
72 px and up the other way round. Text must be clearly easier to read small; Display clearly finer large.

### Phase 4: character set and features

Diacritics by anchors, punctuation, currency, math, arrows, fractions, superiors and inferiors, tabular figures,
alternates; `locl`; kerning.

Gate: language coverage verified by tool; a proof page per feature; kerning proofs (capitals, capital-lowercase,
punctuation, figures).

### Phase 5: production

Static instances, WOFF2 and subsets, names, `STAT`, vertical metrics, automated QA, name check, a CI workflow that
rebuilds the fonts and fails when `fonts/` differs from the sources, `README.md`, `CHANGELOG.md`, `OFL.txt`,
`FONTLOG` or equivalent.

Gate: every criterion under "What high quality means" is met or listed with its reason in `docs/production.md`.

### Phase 6: website

Build the site described below, then deploy it to GitHub Pages.

Gate: the site looked at with realistic content at 1440 and 390 px, light and dark; keyboard-operable; no third-party
requests; Lighthouse mobile performance and accessibility at 95 or more; live on GitHub Pages.

Phase 6 may start beside Phase 4 once Phase 3's variable font exists, since the two touch different folders.

## The website

A single-page specimen with one job: let a visitor see what Orderly is, try it, and download it.

**The idea the reference cannot have: the whole page is live.** The reference draws letters because it has no font.
Orderly has one, with two axes, so the page's own text is the specimen. A small fixed control bar holds weight,
optical size (auto or manual) and appearance; it changes the specimens on the page as it moves.

**What it borrows from the reference:** an editorial grid with a narrow label column, very large type that bleeds off
the edge, hairline rules, measurements shown beside the thing measured, a construction section, a full character grid,
a colophon written in a human voice.

**What makes it its own:**

- Set entirely in Orderly. Labels are Orderly, small, uppercase, tracked, with tabular figures (the reference uses a
  monospace). This is the proof that it works small.
- Its own palette: cool paper-white, near-black ink, one accent that is not the reference's cobalt blue. Light and
  dark, following the system, with a control to override.
- Sections named with words and no numbers. Working titles, in order: Orderly (cover), Weights, Sizes, Construction,
  In use, Reading, Features, Characters, Try it, Colophon.
- Real numbers from the font build's JSON, and real outlines: the Construction section and the glyph inspector draw
  the masters' actual points and interpolate between them in the browser.
- In-use pieces invented for Orderly's theme of things kept in order: a departure board (tabular figures, arrows), a
  library index card, a pharmacy label or a receipt (very small sizes), a poster (display). Nordic languages
  throughout, so `æ ø å` appear as a matter of course. No harbour, no ferry terminal, no kunsthall.

**Section contents:**

| Section      | Shows                                                                                                                              |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Cover        | The name, very large; one sentence saying what Orderly is; the download button; the facts (weights, axes, glyphs, languages, licence). |
| Weights      | The nine named weights as a ladder; dragging across it moves through the weight axis.                                              |
| Sizes        | The same word in Text and Display scaled to equal height, differences marked; a size waterfall with optical sizing on and off.     |
| Construction | The shared parts: one circle, one stem, vertical cuts, overshoot. Drawn from master data, with measurements.                       |
| In use       | The invented pieces above.                                                                                                         |
| Reading      | Paragraphs at text sizes in several languages.                                                                                     |
| Features     | OpenType features switched on and off beside an example each.                                                                      |
| Characters   | The whole character set as a grid; choosing one opens the inspector (outline, points, advance, sidebearings, Unicode).             |
| Try it       | Editable text with size, weight and optical-size controls.                                                                         |
| Colophon     | Who made it and how, the licence, the downloads, the repository.                                                                   |

**Build:** Astro, static output, TypeScript, plain CSS with custom properties, small vanilla islands for the
interactive parts. No UI framework and no CSS framework unless a section needs one. `base` is `/orderly/`.

**Bar:** the maintainer's rule is "would Apple ship this?". Controls are as wide as their content; two to four options
use a segmented control; labels sit beside what they label; the screen explains itself through layout, not through
sentences about the interface. Use the skills `emil-design-eng`, `apple-design`, `golden-ratio-ux` and `break-ui`
while building, and `mobile-native` for the phone pass.

## Outside this version

Italic, small capitals, old-style figures, CFF/OTF static fonts, Cyrillic, Greek, Vietnamese, manual TrueType hinting,
a monospace companion, submission to Google Fonts or Fontsource. Name a need before adding any of them.

## Progress log

Newest first. One entry per phase or review: date, what landed, how it was checked, what is open.

- 2026-11-18: Phase 3 (optical size) landed (Claude Opus 5.5). Three Text masters (`sources/orderly/sizes.py`)
  beside the three Display masters; one variable font `fonts/variable/Orderly[opsz,wght].ttf`, family Orderly,
  `wght` 100 to 900 and `opsz` 12 to 72, default Regular at opsz 12 (Text), nine named weights at opsz 12. The
  Display-only variable font and the lone static were removed. Checked: interpolatable on all six masters reports
  no problem; the corners wght 100 / 400 / 900 x opsz 12 / 72 instantiate; two builds give the same bytes; in
  Chrome 157, `font-optical-sizing: auto` renders each size from 9 to 96 px pixel-identical to the fixed opsz the
  size calls for (clamped to 12..72) and different from the other end (`uv run orderly proof optical-auto`
  prints the comparison). Looked at: Danish and English paragraphs at 9, 11, 13, 16 px in Text, Display and Segoe
  UI columns at device scale 1 and 2, headlines at 72 to 180 px, opsz steps 12 to 72 at 64 px. Text reads clearly
  better than Display at 9 to 13 px; next to Segoe UI it sets about 10 % wider and a shade lighter, and its
  geometric single-storey a and round o make it a little less familiar at 9 px, but it is comfortably readable
  from 11 px. Display is finer and tighter at 72 px and up.

  Settled numbers (implementer's choice; the generator is the source of truth):

  | Master          | stem / cap | bar / cap | x-height | join | dot / stem | apertures c, C | spacing area | n sidebearings | space |
  | --------------- | ---------- | --------- | -------- | ---- | ---------- | -------------- | ------------ | -------------- | ----- |
  | Thin Text       | 28 / 30    | 26 / 28   | 516      | 0.12 | 1.75       | 50, 47         | 0.132        | 68, 63         | 279   |
  | Regular Text    | 86 / 92    | 76 / 82   | 516      | 0.30 | 1.32       | 50, 47         | 0.112        | 58, 52         | 268   |
  | Black Text      | 148 / 156  | 106 / 112 | 520      | 0.46 | 1.16       | 56, 54         | 0.094        | 49, 42         | 250   |
  | Thin Display    | 20 / 22    | 19 / 20.5 | 500      | 0.08 | 1.9        | 42, 40         | 0.112        | 56, 51         | 230   |
  | Regular Display | 78 / 84    | 70 / 76   | 500      | 0.24 | 1.2        | 42, 40         | 0.09         | 45, 40         | 230   |
  | Black Display   | 160 / 168  | 114 / 120 | 504      | 0.40 | 1.12       | 52, 50         | 0.076        | 38, 31         | 232   |

  Text widths are the Display sibling's plus the stroke growth and `TEXT_EXTRA` (narrow letters and rounds gain
  10 to 18 units). Figure terminals open from 18 to 26 degrees in Regular Text. Open: the Text masters were judged
  in running text and character strings, not glyph by glyph at large size; Black Text `e` and `s` are tight at 9 px.

- 2026-11-18: Heavy end reworked after the Phase 2 review (Claude Opus 5.5). Black Display at a lowercase stem of
  160 (capital 168, bars 114 / 120, x-height 504, spacing area 0.076, widths re-derived with factor 0.95 plus
  extra room for a a.ss01 r s S 2 3 4 5 ?); weight map 100 20, 200 34, 300 52, 400 78, 500 94, 600 110, 700 127,
  800 143, 900 160. The join primitive now bounds the outer join point in a band (never past the stem's corner,
  never deeper than `join.deep` under the round's top) and draws the shoulder as one round arc (start angle 1.6 to
  2 times the chord's), so heavy joins are quiet notches; Thin and Regular joins are unchanged except a softer
  shoulder in Regular `m 5 a.ss01 æ`. Black `e` has a lighter bar and longer terminal, `c C G` open apertures,
  `s S` even weight, `?` keeps its weight through the neck (all weights), `g` a roomier hook, `r` a longer arc.

- 2026-11-18: Phase 2 (weight) landed (Claude Opus 5.5). Thin and Black Display masters (`sources/orderly/weights.py`)
  and the variable font `fonts/variable/OrderlyDisplay[wght].ttf`: `wght` 100 to 900, default 400, nine named
  instances Thin to Black, `avar` from a user-to-stem map, STAT and MVAR from fontc. Checked:
  `fontTools.varLib.interpolatable` on Thin, Regular and Black reports no problem; the ladder of nine weights (96
  and 32 px), words and character sets of Thin and Black (200, 96, 32 px), their spacing strings, and overlays of
  the three masters were looked at, light and dark. Weak spots: Black `e s a.ss01` have small but open counters;
  the Black `?` hook narrows where it turns into the stem; Black `3` and the `2 3 5` terminals cut close to the
  counter, so their arms are short; Thin `t`'s hook terminal is small and reads as a dot at 32 px.

  Settled numbers (implementer's choice, the generator is the source of truth):

  | Master  | stem / cap stem | bar / cap bar | round side, top | join | apex / stem | dot / stem | spacing area | x-height |
  | ------- | --------------- | ------------- | --------------- | ---- | ----------- | ---------- | ------------ | -------- |
  | Thin    | 20 / 22         | 19 / 20.5     | 1.08, 1.03      | 0.08 | 1.5         | 1.9        | 0.112        | 500      |
  | Regular | 78 / 84         | 70 / 76       | 1.07, 1.03      | 0.24 | 0.8         | 1.2        | 0.09         | 500      |
  | Black   | 186 / 196       | 128 / 134     | 1.03, 0.94      | 0.44 | 0.42        | 1.1        | 0.072        | 506      |

  Widths: each glyph's Regular width plus its count of vertical strokes (`VSTEMS`) times the stem change times 0.55
  (Thin) or 0.9 (Black); rounds count less, so `O` stays a circle in Black and its counter goes oval. Weight map
  (user weight to lowercase stem, the mean of an arithmetic and a geometric step): 100 20, 200 35, 300 54, 400 78,
  500 96, 600 116, 700 137, 800 160, 900 186. Black needs its own numbers for hook radii, `e`'s bar, the bowls'
  rounds of `P R B`, the `& ?` strokes and the ring of `Å å`; Thin for hook radii, dots, quotes and the comma.

- 2026-11-18: Phase 1 review fixes (Claude Opus 5.5). `s S` redrawn from a skeleton of two stacked rounds and a
  short curved spine (west extreme of the upper round at 72 %, east extreme of the lower at 28 %, spine 1.06 of
  the stem, apertures as c and C). Double-storey `a.ss01` drawn (feature wiring waits for Phase 4) and `æ` built
  from it. `6 9`: a full round with a stem that leaves its outer contour on the tangent and curves at full weight to
  a vertical cut. `&` redrawn: small loop, a bowl leaving the loop's lower right and rising to a vertical cut, a
  straight leg from the loop's left side. `Q`'s tail starts inside the round's stroke. `2`'s neck flows from the
  round's east extreme into the diagonal with no straight joint (this also removes the 2's structural limit found
  in Phase 1). The comma's tail is curved. Checked by outline sheets and browser proofs; interpolation check clean.

- 2026-11-18: Phase 1 (Regular Display) landed (Claude Opus 5.5, implementer). 81 glyphs plus space: `A-Z a-z 0-9`,
  `. , : ; ! ? - ' " ( ) / &`, `Æ Ø Å æ ø å`, spaced by the area method with one hand adjustment (J). Shared
  parts: the compass `Ell`, the n arch (also h m r u), the bowl (b d p q a g), one hook (t f j g J), the s curve
  (s S), apex polygons for v w y A V W M Y, cut rounds for c e C G. Checked: outline sheets of every group and
  browser proofs (words 16 to 200 px, paragraph 11 to 24 px, spacing strings, character set, light and dark) were
  looked at; `uv run orderly check` finds no interpolation problem against a throwaway light master and compiles
  a two-master variable font; two builds give the same bytes. Open, and the implementer's weak spots: `I` and `l`
  differ only by height (the `ss02` l is Phase 4); `rn` and `cl` close up at 11 to 13 px in this Display master;
  `fl` and `ff` nearly touch (kerning, Phase 4); `T` and `J` leave holes beside `S` and `H` (kerning); the `s S`
  spine is long and straight for a geometric face; `æ` is a little dark where the e meets the stem; the tall
  stroke of `6 9` meets its round in a sharp crotch on the left.

  Implementer's proposals for the reviewer, not decided:
  - Read the brief's capital widths as advance widths over the cap height. Settled: H 0.97, N 1.02, U 0.96, A V
    0.97, D 1.04, C 0.95, G 1.12, B P 0.86, R 0.89, E 0.81, F L S 0.77 to 0.78, M 1.18, W 1.46. `O Q` are true
    circles (722 by 722) and so come out at 1.17, not 1.1; narrowing them would break rule 1.
  - The brief's starting values are kept unchanged (cap 700, x-height 500, ascender 740, descender -200,
    lowercase stem 78). Numbers the brief leaves open are settled in `sources/orderly/master.py`: capital stem
    84, lowercase bar 70, capital bar 76, round sides 1.07 of the stem, round tops 1.03 of the bar, diagonals
    0.96 of the stem measured square, curve tension 0.56 outside and in, join thinning 0.24 of the stroke, flat
    apexes 0.8 of the stem, dots 1.2 of the stem, round overshoot 1.5 % and apex overshoot 0.5 %.
  - Masters must keep a few shapes in the same arrangement for interpolation to work: the e's bar sits below the
    round's centre, the 2's diagonal leaves the round below its east extreme, the counter of each joined round
    runs into its stem. The generator now places the e's bar by its lower edge and stops the build with a
    message when the 2 breaks its rule; the Thin and Black masters of Phase 2 need their own numbers for these
    (a throwaway master at 2.1 times the weights closes the e's eye).

- 2026-11-18: Phase 0 (pipeline proof) landed (Claude Opus 5.5, implementer). `uv` environment with pinned
  versions, the generator skeleton in `sources/orderly/`, both proof tools (outline sheets from the generator with
  skia; browser proofs of the compiled font with Playwright and Chrome on port 4813), `OFL.txt`, `.gitattributes`,
  `.claude/launch.json`, [production](production.md). `H O n o` of the Regular Display master compile with fontc
  2.0.1 to `fonts/static/OrderlyDisplay-Regular.ttf` with `uv run orderly build`. Checked: two builds give the same
  bytes; the outline sheet and the browser proof (200 to 16 px, light and dark) were looked at;
  `fontTools.varLib.interpolatable` finds no problem between the master and a throwaway light master, and the
  two-master designspace compiles to a variable font. Open: the QA tool (fontspector) is not installed yet; see
  production.

- 2026-11-18: Plan, design brief and AGENTS.md written (Claude Fable 5.2, planner and reviewer). Repository cloned
  from GitHub. Implementation is delegated phase by phase to Claude Opus 5.5.
