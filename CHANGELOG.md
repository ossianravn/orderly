# Changelog

All notable changes to the Orderly fonts. Versions follow the font's version (`head.fontRevision`, name ID 5).

## 1.000 (2026-11-18)

The first complete version of the planned scope: one upright family with weight and optical-size axes.

- Variable font `Orderly[opsz,wght]`: weight 100 to 900 (nine named weights, `avar` for even steps), optical
  size 12 (Text, the default) to 72 (Display); six masters {Thin, Regular, Black} x {Text, Display}.
- Eighteen static fonts cut from it with overlaps removed: Orderly and Orderly Display, Thin to Black.
- Web fonts: the variable WOFF2, Latin and Latin-extended subsets with `orderly.css`, static WOFF2.
- Character set: Google Fonts Latin Kernel and Latin Core; the Latin-script official languages of the EU and the
  Nordic countries (Sámi and Greenlandic included) and Turkish; currency, math, arrows, fractions, superiors and
  inferiors, spacing accents, the dotted circle.
- Features: `kern mark mkmk ccmp locl case cpsp frac numr dnom sups subs ordn tnum pnum zero ss01 ss02`.
  `locl` covers Romanian and Moldovan comma-below letters, Turkish, Azeri and Crimean Tatar i, the Catalan punt
  volat, Dutch íj́, and the N-form Ŋ for Sámi.
- Polish after review: `Ω`, `∆` and `µ` also answer to Greek Ω Δ μ (shapers normalise the ohm sign to Ω, and
  without it the Thin Ω fell back to another font); `∞ ≈ ~` drawn at the size and weight of `+ =`; Black
  double-storey a and æ with an open lower counter; lighter vertical in Black ¢; Thin § closes its loop; `@`
  centred on the x-height, with an `@.case` for capitals; a longer hook on Black `ľ` in `ss02`.
- Vertical metrics by the Google Fonts specification: typo and hhea 1000 / -300 / 0 (line height 1.3), win
  1142 / 335, `USE_TYPO_METRICS`; `STAT` for both axes; `gasp` and smart-dropout `prep` for an unhinted font.
