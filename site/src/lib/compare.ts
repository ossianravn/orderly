// Sizes: one word drawn from the Text and the Display masters at the same scale, at the current
// weight, with the x-height and the word's width marked. Shared by the build and the browser.
import { numberAt, shapeAt, shapePath, type Location, type Packed } from "./glyphs";

const TOP = 800;
export const ROW_HEIGHT = 1040;
const Y = (y: number) => TOP - y;
const n0 = (v: number) => String(Math.round(v));

export interface Row {
  label: string;
  opsz: number;
  w: number;
  xh: number;
  stem: number;
  body: string;
}

function glyphNames(data: Packed, word: string): string[] {
  const byChar = new Map<string, string>();
  for (const [name, g] of Object.entries(data.glyphs)) if (g.ch) byChar.set(g.ch, name);
  return [...word].map((c) => byChar.get(c)).filter((n): n is string => !!n);
}

function draw(data: Packed, word: string, loc: Location): { paths: string; w: number } {
  let x = 0;
  let paths = "";
  for (const name of glyphNames(data, word)) {
    const s = shapeAt(data, name, loc);
    if (!s) continue;
    paths += `<path class="g" transform="translate(${n0(x)} ${TOP}) scale(1 -1)" d="${shapePath(s)}"/>`;
    x += s.advance;
  }
  return { paths, w: x };
}

/** Both rows, sharing one width so that the scale is the same. */
export function compare(data: Packed, word: string, wght: number): { rows: Row[]; width: number } {
  const sizes = data.masters.map((m) => m.opsz);
  const lo = Math.min(...sizes);
  const hi = Math.max(...sizes);
  const parts = [
    { label: "Text", opsz: lo },
    { label: "Display", opsz: hi },
  ].map((p) => {
    const loc = { wght, opsz: p.opsz };
    return { ...p, ...draw(data, word, loc), xh: numberAt(data, "xHeight", loc), stem: numberAt(data, "stem", loc) };
  });
  const width = Math.max(...parts.map((p) => p.w)) + 40;
  const other = (i: number) => parts[1 - i];
  const rows = parts.map((p, i) => {
    const o = other(i);
    let body = `<line class="m" x1="0" x2="${n0(width)}" y1="${Y(0)}" y2="${Y(0)}"/>`;
    body += `<line class="mk" x1="0" x2="${n0(p.w)}" y1="${n0(Y(p.xh))}" y2="${n0(Y(p.xh))}"/>`;
    body += p.paths;
    body += `<line class="mk" x1="${n0(p.w)}" x2="${n0(p.w)}" y1="${Y(-200)}" y2="${Y(760)}"/>`;
    if (Math.abs(o.w - p.w) > 4) {
      body += `<line class="ghost" x1="${n0(o.w)}" x2="${n0(o.w)}" y1="${Y(-200)}" y2="${Y(760)}"/>`;
    }
    return { label: p.label, opsz: p.opsz, w: p.w, xh: p.xh, stem: p.stem, body };
  });
  return { rows, width };
}

export const fmt = (v: number) => {
  const s = String(Math.round(v));
  return s.length > 4 ? s.replace(/\B(?=(\d{3})+(?!\d))/g, " ") : s;
};
