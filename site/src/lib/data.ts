// Build-time access to the font build's data. Everything the page states comes from here.
import { existsSync, readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";
import type { Packed } from "./glyphs";

const site = process.cwd();
const read = (p: string) => JSON.parse(readFileSync(resolve(site, p), "utf8"));

export interface Feature {
  tag: string;
  name: string;
  sample: string;
  /** Optional, from the font build: what the feature is for, whether it is on by default, a language. */
  group?: string;
  default?: boolean;
  lang?: string;
  /** Tags this feature is shown with (pnum with tnum). */
  with?: string[];
}

export interface Language {
  tag: string;
  name: string;
  [k: string]: unknown;
}

export interface Meta {
  family: string;
  version: string;
  glyphCount?: number;
  unitsPerEm: number;
  axes: Packed["axes"];
  instances: { name: string; wght: number }[];
  features: Feature[];
  languages: Language[];
  glyphs: { name: string; unicode: number | null; char: string | null; category: string }[];
}

// ORDERLY_META points the build at another copy of the data (worst-case checks); the default is the font build's.
export const meta: Meta = read(process.env.ORDERLY_META ?? "../fonts/data/orderly.json");
export const packed: Packed = read("public/data/glyphs.json");

export const base = import.meta.env.BASE_URL.replace(/\/?$/, "/");

export const files = {
  ttf: { href: `${base}fonts/orderly-variable.ttf`, name: "Orderly[opsz,wght].ttf" },
  woff2: { href: `${base}fonts/orderly.woff2`, name: "Orderly[opsz,wght].woff2" },
  /** The whole family as one zip; only once the font build writes static instances. */
  zip: existsSync(resolve(site, "public/downloads/orderly.zip"))
    ? { href: `${base}downloads/orderly.zip`, name: `Orderly-${meta.version}.zip` }
    : null,
};

/** A served file's size, in KB below a megabyte and in MB with one decimal above. */
export function kb(path: string): string {
  const bytes = statSync(resolve(site, "public", path)).size;
  const k = bytes / 1024;
  return k < 1000 ? `${Math.round(k)} KB` : `${(k / 1024).toFixed(1)} MB`;
}

export const axis = (tag: string) => meta.axes.find((a) => a.tag === tag)!;

/** Glyphs with an outline, which is what a visitor counts as the character set. */
export const drawn = meta.glyphs.filter((g) => g.category !== "space");
// The number of glyphs in the compiled font, as the README states it; the grid shows the drawn ones.
export const glyphTotal = meta.glyphCount ?? meta.glyphs.length;

export const cmap = new Set(meta.glyphs.filter((g) => g.char).map((g) => g.char!));

/** Width of a string in font units at a master, from advances alone (kerning off). */
export function widthAt(text: string, masterIndex: number): number {
  const byChar = new Map(meta.glyphs.filter((g) => g.char).map((g) => [g.char!, g.name]));
  let w = 0;
  for (const ch of text) {
    const name = byChar.get(ch);
    const g = name ? packed.glyphs[name] : undefined;
    if (g) w += g.m[masterIndex][0];
  }
  return w;
}

export const masterIndex = (id: string) => packed.masters.findIndex((m) => m.id === id);

export const repo = "https://github.com/ossianravn/orderly";

/** "1 language", "32 languages". */
export const count = (n: number, one: string, many = `${one}s`) => `${n} ${n === 1 ? one : many}`;

/** Groups for the character grid, in a reader's order. */
export const categories: [string, string][] = [
  ["uppercase", "Uppercase"],
  ["lowercase", "Lowercase"],
  ["figure", "Figures"],
  ["punctuation", "Punctuation"],
  ["symbol", "Symbols"],
  ["mark", "Marks"],
  ["alternate", "Alternates"],
];
