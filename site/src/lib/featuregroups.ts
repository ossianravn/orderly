// Features grouped by what a designer uses them for. The font build's `group`, `default`, `lang` and
// `with` fields decide when present; without them the tag decides.
import type { Feature } from "./data";
import { featureDiff, type Diff } from "./featurediff";

export interface Shown {
  tag: string;
  name: string;
  sample: string;
  lang?: string;
  diff: Diff;
  /** Features shown inside this one's example, such as numerators and denominators under fractions. */
  folded: Shown[];
}

export interface Group {
  id: string;
  title: string;
  items: Shown[];
}

const TITLES: [string, string][] = [
  ["figures", "Figures"],
  ["alternates", "Alternates"],
  ["capitals", "Capitals"],
  ["other", "More"],
  ["always", "Always on"],
];

const BY_TAG: Record<string, string> = {
  tnum: "figures", pnum: "figures", lnum: "figures", onum: "figures", zero: "figures", frac: "figures",
  afrc: "figures", numr: "figures", dnom: "figures", sups: "figures", subs: "figures", sinf: "figures",
  ordn: "figures",
  case: "capitals", cpsp: "capitals", smcp: "capitals", c2sc: "capitals", titl: "capitals",
  kern: "always", mark: "always", mkmk: "always", ccmp: "always", locl: "always", liga: "always",
  calt: "always", clig: "always", rlig: "always", rclt: "always",
};

/** Within a group, a reader's order; anything else follows in tag order. */
const ORDER = ["tnum", "zero", "frac", "sups", "subs", "ordn", "case", "cpsp", "kern", "mark", "mkmk", "ccmp", "locl"];

/** Shown inside another feature's example rather than on their own (when the data has no `with`). */
const FOLD: Record<string, string> = { numr: "frac", dnom: "frac", pnum: "tnum" };

type Input = Feature & { with?: string[] };

function groupOf(f: Input): string {
  const g = f.group?.toLowerCase().trim();
  if (g) {
    if (/always|default|required|built-?in/.test(g)) return "always";
    const known = TITLES.find(([id, title]) => g === id || g === title.toLowerCase());
    if (known) return known[0];
    return g;
  }
  if (f.default === true) return "always";
  if (/^(ss\d\d|cv\d\d|salt)$/.test(f.tag)) return "alternates";
  return BY_TAG[f.tag] ?? "other";
}

export function groupFeatures(features: Input[]): Group[] {
  const usable = features.filter((f) => f.sample && f.sample.trim());
  const shown = new Map<string, Shown>();
  for (const f of usable) {
    shown.set(f.tag, {
      tag: f.tag,
      name: f.name,
      sample: f.sample,
      lang: f.lang,
      diff: featureDiff(f.sample, f.tag, f.lang),
      folded: [],
    });
  }
  const folds = new Map(Object.entries(FOLD));
  for (const f of usable) if (f.with?.length) folds.set(f.tag, f.with[0]);
  for (const [tag, host] of folds) {
    const item = shown.get(tag);
    const into = shown.get(host);
    if (item && into) {
      into.folded.push(item);
      shown.delete(tag);
    }
  }
  const rank = (t: string) => (ORDER.includes(t) ? ORDER.indexOf(t) : ORDER.length);
  const groups = new Map<string, Shown[]>();
  for (const f of usable) {
    const s = shown.get(f.tag);
    if (!s) continue;
    const g = groupOf(f);
    groups.set(g, [...(groups.get(g) ?? []), s]);
  }
  const ids = [...TITLES.map(([id]) => id), ...[...groups.keys()].filter((k) => !TITLES.some(([id]) => id === k))];
  return ids
    .filter((id) => groups.get(id)?.length)
    .map((id) => ({
      id,
      title: TITLES.find(([g]) => g === id)?.[1] ?? id.charAt(0).toUpperCase() + id.slice(1),
      items: groups.get(id)!.sort((a, b) => rank(a.tag) - rank(b.tag) || a.tag.localeCompare(b.tag)),
    }));
}
