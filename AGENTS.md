# AGENTS.md

Working instructions for coding agents in Orderly.

Orderly is an open-source geometric grotesk typeface, drawn in code, and a small website that shows it. The font is a
variable font with a weight axis and an optical-size axis. Its source is a Python program: a master is a set of
numbers, a glyph is a function of a master.

## Read the owning document

| When working on                                                     | Read                                                                 |
| ------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Scope, decisions, phases, the website's content and look, progress  | [Plan](docs/plan.md)                                                 |
| The shape of any letter, proportions, weights, optical sizes        | [Design brief](docs/design.md)                                       |
| Building fonts, tool versions, QA results and accepted warnings     | [Production](docs/production.md) (exists from Phase 0)               |

The plan is the source of truth for decisions. Mark a decision decided only when the maintainer has said so; record
your own choices as proposals with their reason. When a phase's work lands, add an entry to the plan's progress log.

## How the work is organised

- **Phases end at gates.** Do the phase you were given, stop at its gate, and report. The next phase starts after
  review.
- **The reviewer looks at proofs, not code.** Every change to a glyph, a master or spacing ends with fresh proof
  images, and you look at them yourself before reporting. An outline is judged by eye, large and small.
- **Draw by parameter.** A number that two glyphs share lives in the master or in a shared primitive. A glyph function
  takes the same path through its code for every master, so masters stay compatible.
- **Fix at the owner.** A clot at the join of `n` is a join-thinning problem, so fix the arch primitive and every
  sibling improves; adjust a single glyph only for what is particular to it.
- **The site's numbers come from the font build's JSON**, never from a hand-typed value.

## Design bar

- **Letters:** the design brief's rules and review checklist. When a proof and the brief disagree, the eye wins:
  change the number, then record the settled value in the generator.
- **Website:** before showing or reporting a screen, ask whether Apple would ship it. Size every control to its
  content; keep labels beside what they label; use a segmented control for two to four options, a switch for on and
  off, a select for long lists; let layout and labels explain the screen. Check 1440 and 390 px, light and dark, with
  realistic content.
- **Own face, own page.** The reference specimen (linked in the plan) is inspiration. Copy neither its outlines nor
  its page; section names are words, never numbers.

## Engineering constraints

- Python runs through `uv`; the site through `npm` in `site/`. Pin versions.
- Dev servers use the project's ports: site dev 4811, site preview 4812, proofs 4813 (`.claude/launch.json`). Never
  a framework's default port.
- Keep each hand-written code file at 300 lines or fewer; split glyph functions across files by family.
- `fonts/` is built output and is committed. Rebuild it with the build command; never edit a font binary by hand.
  `build/` and `proofs/` stay out of git.
- The generator is deterministic: the same sources give the same bytes. No clocks, no randomness, no network.
- Font tooling changes quickly. Check a tool's current documentation before relying on memory of its flags.

## Verification

Verify with the least total effort. Write no unit tests; the checks are tools and eyes.

1. After changing the generator: rebuild, run the interpolation check, regenerate the proofs for what changed, and
   look at them.
2. After changing features, names, metrics or the build: run the font QA tool and compare against the accepted list
   in `docs/production.md`.
3. After changing the site: typecheck, build, and look at the changed section at 1440 and 390 px, light and dark.
4. Report evidence by kind: checks run, what you looked at and saw, what is not covered.

## Git and publishing

Commit and push to `main` without asking when the change is non-destructive. A push to `main` redeploys the website
once Phase 6 has set that up. Ask before rewriting history, deleting published files, tagging a release or publishing
anywhere other than this repository's GitHub Pages.

Fonts are licensed under the SIL Open Font License 1.1 (`OFL.txt`); code and website under MIT (`LICENSE`).
