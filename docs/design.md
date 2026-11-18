# Orderly: design brief

Orderly is a geometric grotesk: letters built from a circle, a stem and a few cuts, kept in order. This brief says
what the letters should look like and how to judge them. The implementer draws to it; the reviewer reviews against it.

## Character

Clean, calm, Nordic. Classic in its capitals (Roman proportions: wide rounds, narrow `E F L`), modern in its
lowercase (large x-height, single-storey `a`, plain forms). Sophisticated through restraint: every detail that is
there repeats somewhere else. Nothing decorative.

Relatives, for orientation only: Futura and Avenir (the classical geometric line), Circular and Euclid (the modern
one). Orderly sits between them: stricter than Avenir, warmer and more readable than Futura.

## The rules that make it orderly

1. **One compass.** `O C G Q D o c e b d p q a g` and the round figures come from the same round. In Display the `O`
   is as near a true circle as the weight allows; the counter may go oval as weight grows.
2. **One stem.** A master has one lowercase stem, one capital stem (a little heavier) and one horizontal weight (a
   little lighter than the vertical). Every glyph uses these, so colour is even.
3. **Vertical cuts.** Every open curve ends in a vertical cut: `C G S c e s a r f j t 2 3 5 6 9`. Straight strokes
   end in horizontal or vertical cuts; diagonals are cut horizontally at the baseline and at their top line. No
   angled terminals anywhere.
4. **Flat apexes.** `A V W M N v w` end flat, as wide as the optical weight needs, on the baseline or the top line
   with a small overshoot. No points.
5. **Round dots.** `i j` dots, the period, colon, dieresis and their kin are circles from the same compass, slightly
   heavier than the stem.
6. **Thinned joins.** Where a curve meets a stem (`n h m r u b d p q a g`), the curve narrows into it.
7. **Overshoot.** Rounds pass the flat lines, top and bottom, by about 1.5 % of their height; flat apexes by less.

## Proportions (units per em: 1000)

| Measure            | Display | Text    | Note                                                         |
| ------------------ | ------- | ------- | ------------------------------------------------------------ |
| Cap height         | 700     | 700     |                                                              |
| x-height           | 500     | 516     | Text reads larger                                            |
| Ascender           | 740     | 740     | Above the capitals, the classical trait                      |
| Descender          | -200    | -200    |                                                              |
| Regular stem       | about 78 | about 86 | Lowercase vertical; capitals a few units more              |
| Thin stem          | about 20 | about 28 |                                                             |
| Black stem         | about 190 | about 176 |                                                           |
| Spacing            | tight   | open    | Text clearly looser, by something like 10 to 14 units a side |
| Apertures          | closer  | open    | `c e s a` and figures open up in Text                        |
| Join thinning      | light   | deeper  | Text and heavy weights need more                             |

These are starting values. Adjust them by eye from proofs and record the settled numbers in the generator, which is
their source of truth.

Capital widths are classical but moderated so text does not lurch: `O Q` about 1.1 times the cap height wide, `C G D`
a little less, `H N U` about 1.0, `A V` about 0.95, `B E F L P R S` 0.75 to 0.85, `M W` wide. `M` has vertical stems.

## Letter notes

- `a`: single-storey, the `o` with a stem. A double-storey `a` is the alternate (`ss01`), drawn with the same care,
  for text that needs `a` and `o` far apart.
- `g`: single-storey, bowl of the `o`, hook of the family.
- `l`: a plain stem by default; the alternate (`ss02`) has a curved foot, to tell it from `I` and `1`.
- `t f j`: one hook, three uses. `t` has a flat-cut top and a crossbar aligned with the x-height.
- `y`: straight diagonal tail, cut horizontally. `k K`: diagonals meet at the stem without a clot.
- `G`: no spur; a horizontal bar and a short vertical jaw. `Q`: a short straight diagonal tail. `R`: straight leg.
- `J`: sits on the baseline. `1`: with a flag, no foot. `4`: closed. `7`: straight. `0`: clearly narrower than `O`;
  slashed alternate (`zero`).
- `Æ Ø Å æ ø å` are first-class: draw them with the capitals and lowercase, not with the diacritics. The `Ø ø` slash
  runs at one angle and overshoots the round on both sides; the ring of `Å` sits clear of the apex.
- `ß`: without a descender; `ẞ` included. `&`: simple, built from the round.
- Figures are lining and proportional by default, with tabular alternates (`tnum`) on one shared width.
- Arrows match the stem weight and the cap height, drawn for signage.

## Optical sizes

**Text** (opsz 12, the default) is for 9 to 20 px: larger x-height, sturdier stem, open spacing, open apertures,
deeper join thinning, slightly larger dots and punctuation, a little more width in narrow letters. It may bend rule 1:
rounds can be a touch less than circular if reading improves.

**Display** (opsz 72) is for headlines: the pure geometry, tight spacing, finer joins, exact circles.

Between them the font interpolates; browsers pick the value from the font size.

## Weights

Thin 100, ExtraLight 200, Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, ExtraBold 800, Black 900.
Masters at Thin, Regular and Black. As weight grows: counters stay open (letters widen, contrast rises, joins thin
more), the x-height may rise a few units, dots and accents grow with the stem.

## Test strings

Control glyphs, in drawing order: `H O n o`, then `a d e s`, then `R S G g t k`, then the rest.

- `Hamburgefonstiv`, `HAMBURGEFONSTIV`, `Orderly`, `ORDERLY`
- `nnonn oonoo HHOHH OOHOO`, and each new glyph between `nn..nn`, `oo..oo`, `HH..HH`, `OO..OO`
- `Blåbærsyltetøj på rugbrød`, `Æ Ø Å æ ø å`, `Þjóðvegur`, `Žluťoučký kůň`, `Gdańsk Łódź`, `İstanbul ığdır`
- `0123456789`, `10:42 → Spor 7`, `1 234 567,89 kr.`
- `Illegal1 Il1 O0 rn m cl d`
- A paragraph of Danish and a paragraph of English at 9, 11, 13 and 16 px

## Review checklist

Look at proofs for each of these and say what you see; do not tick boxes from memory of the code.

- **Colour**: a paragraph at text size looks evenly grey, with no letter darker or lighter than its neighbours.
- **Rhythm**: `nnonn` and `HHOHH` look evenly spaced; no letter sits in a hole or crowds its neighbour.
- **Rounds**: curves are smooth with no flat spots or bumps at the extremes; `O` beside `H` looks the same height.
- **Joins**: no dark clots where curves meet stems, in any weight.
- **Cuts**: all terminals vertical or horizontal; cut ends at consistent heights within a letter family.
- **Family likeness**: `b d p q`, `n h m u r`, `c e o`, `C G O Q`, `v w y`, `3 5 6 9` each read as siblings.
- **Small sizes**: at 9 to 13 px, apertures stay open, `rn` does not read as `m`, `Il1` and `O0` can be told apart.
- **Large sizes**: at 200 px, the Display's rounds are true and nothing looks mechanical or lumpy.
- **Extremes**: Thin holds together; Black keeps its counters.
- **Own face**: nothing reads as a copy of the reference or of an existing typeface.
