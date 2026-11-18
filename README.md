# Orderly

Orderly is an open-source geometric grotesk: letters built from one circle, one stem and a few vertical cuts, calm
and Nordic in feel. It is a variable font with two axes, weight and optical size, and its source is a Python
program that draws every glyph from a handful of numbers.

- **Weight** (`wght`) 100 to 900, nine named weights: Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold,
  ExtraBold, Black.
- **Optical size** (`opsz`) 12 to 72. At 12 (the default) it is the Text design: larger x-height, sturdier stems,
  looser spacing and open apertures for 9 to 20 px. At 72 it is the Display design: pure geometry and tight spacing
  for headlines. Browsers choose the value from the font size by themselves.
- **Character set**: 528 glyphs. Google Fonts Latin Kernel and Latin Core complete; every Latin-script official
  language of the EU and the Nordic countries, Sámi and Greenlandic included, and Turkish (32 languages, checked
  with hyperglot). Currency, math, arrows for signage, fractions, superiors and inferiors.
- **OpenType features**: `kern` `mark` `mkmk` `ccmp` `locl` `case` `cpsp` `frac` `numr` `dnom` `sups` `subs` `ordn`
  `tnum` `pnum` `zero`, and two stylistic sets: `ss01` double-storey a, `ss02` l with a curved foot.
- **Specimen**: https://ossianravn.github.io/orderly/

## Files

| Folder | What |
| --- | --- |
| `fonts/variable/` | `Orderly[opsz,wght].ttf`, the variable font: use this on the desktop when your apps support variable fonts. |
| `fonts/static/` | Eighteen static TTFs: nine weights of **Orderly** (the Text design) and nine of **Orderly Display**. |
| `fonts/web/` | `Orderly[opsz,wght].woff2` (the whole variable font), the same split into `Orderly-latin.woff2` and `Orderly-latin-ext.woff2` with `orderly.css`, and the statics as WOFF2 in `static/`. |
| `fonts/data/` | `orderly.json` and `outlines.json`: metrics, features, languages and the master outlines, for the specimen site. |

## Use it on the web

Copy `fonts/web/` to your site and link the stylesheet; browsers download only the subsets a page needs:

```html
<link rel="stylesheet" href="/fonts/orderly.css">
<style>
  body { font-family: "Orderly", system-ui, sans-serif; }
  h1 { font-weight: 800; }                         /* any weight from 100 to 900 */
  .numbers { font-variant-numeric: tabular-nums slashed-zero; }
  .labels { text-transform: uppercase; font-feature-settings: "case", "cpsp"; }
  .alt { font-feature-settings: "ss01"; }          /* double-storey a */
</style>
```

Or a single file without subsets:

```css
@font-face {
  font-family: "Orderly";
  src: url("Orderly%5Bopsz%2Cwght%5D.woff2") format("woff2");
  font-weight: 100 900;
  font-display: swap;
}
```

Optical size follows the font size automatically (`font-optical-sizing: auto` is the default). To fix it, use
`font-variation-settings: "opsz" 72`.

## Install it on a computer

Install `fonts/variable/Orderly[opsz,wght].ttf`. Apps that do not support variable fonts take the statics from
`fonts/static/`: they appear as two families, Orderly and Orderly Display, each with nine weights.

## Build it

Orderly is built from `sources/` with [uv](https://docs.astral.sh/uv/) and the font compiler fontc:

```sh
uv sync
uv run orderly build    # sources -> fonts/ (variable, statics, web, data)
uv run orderly check    # all six masters interpolate; every corner of the design space instantiates
uv run orderly proof    # browser proofs -> proofs/browser/*.png
```

The same sources give the same bytes. A GitHub Actions workflow rebuilds the fonts on every push and pull request,
fails when `fonts/` differs from what the sources produce, and checks the fonts with fontspector. How the fonts are
made, checked and why is in [docs/production.md](docs/production.md); the letterforms are specified in
[docs/design.md](docs/design.md); decisions and progress are in [docs/plan.md](docs/plan.md).

## Licence

The fonts are licensed under the [SIL Open Font License 1.1](OFL.txt): free to use, study, modify and
redistribute, including commercially, but not to sell on their own. The code and the website are under the
[MIT License](LICENSE).

Designed by Ossian Ravn, drawn in code with Claude.
