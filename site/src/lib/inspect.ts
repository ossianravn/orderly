// The glyph inspector: one glyph's outline at a location, with its points, handles, metric lines
// and sidebearings. Shared by the build (first glyph) and the browser (any glyph, live).
import { numberAt, shapeAt, shapePath, type Location, type Packed, type Shape } from "./glyphs";

export const BOX_W = 1320;
export const BOX_TOP = 880;
export const BOX_H = 1180;
const Y = (y: number) => Math.round((BOX_TOP - y) * 10) / 10;
const r = (v: number) => Math.round(v * 10) / 10;

export interface Inspected {
  body: string;
  facts: [string, string][];
}

function points(s: Shape, dx: number): string {
  let handles = "";
  let on = "";
  let off = "";
  for (const c of s.contours) {
    const n = c.on.length;
    const X = (i: number) => r(c.pts[(i % n) * 2] + dx);
    const Yp = (i: number) => Y(c.pts[(i % n) * 2 + 1]);
    for (let i = 0; i < n; i++) {
      if (c.on[i]) {
        on += `M${X(i) - 9} ${Yp(i) - 9}h18v18h-18Z`;
        continue;
      }
      // An off-curve point hangs from the on-curve point next to it on its side of the curve.
      const anchor = c.on[(i + n - 1) % n] ? i + n - 1 : i + 1;
      handles += `M${X(i)} ${Yp(i)}L${X(anchor)} ${Yp(anchor)}`;
      off += `<circle cx="${X(i)}" cy="${Yp(i)}" r="8"/>`;
    }
  }
  return `<path class="hd" d="${handles}"/><path class="on" d="${on}"/><g class="off">${off}</g>`;
}

export function inspect(data: Packed, name: string, loc: Location): Inspected | null {
  const s = shapeAt(data, name, loc);
  const g = data.glyphs[name];
  if (!s || !g) return null;
  const dx = Math.round((BOX_W - s.advance) / 2);
  const xh = numberAt(data, "xHeight", loc);
  const m = data.metrics;
  // [height, label, label at the right end] (ascender and cap height sit too close for one side)
  const lines: [number, string, boolean][] = [
    [m.ascender, `Ascender ${m.ascender}`, true],
    [m.capHeight, `Cap height ${m.capHeight}`, false],
    [xh, `x-height ${Math.round(xh)}`, false],
    [0, "Baseline 0", false],
    [m.descender, `Descender ${m.descender}`, false],
  ];
  let body = lines
    .map(
      ([y, label, right]) =>
        `<line class="m" x1="0" x2="${BOX_W}" y1="${Y(y)}" y2="${Y(y)}"/>` +
        `<text class="t" x="${right ? BOX_W - 10 : 10}" y="${Y(y) - 14}" text-anchor="${right ? "end" : "start"}">${label}</text>`,
    )
    .join("");
  body += `<rect class="adv" x="${dx}" y="${Y(m.ascender + 60)}" width="${r(s.advance)}" height="${Y(m.descender - 60) - Y(m.ascender + 60)}"/>`;
  body += `<path class="g" transform="translate(${dx} ${BOX_TOP}) scale(1 -1)" d="${shapePath(s)}"/>`;
  body += points(s, dx);
  const unicode = g.u == null ? "None" : `U+${g.u.toString(16).toUpperCase().padStart(4, "0")}`;
  const facts: [string, string][] = [
    ["Name", name],
    ["Unicode", unicode],
    ["Advance", String(Math.round(s.advance))],
    ["Left side", String(Math.round(s.lsb))],
    ["Right side", String(Math.round(s.rsb))],
    ["Points", String(s.contours.reduce((a, c) => a + c.on.length, 0))],
  ];
  return { body, facts };
}

/** A small drawing for a grid cell, for glyphs that cannot be typed (marks, alternates). */
export function cellDrawing(data: Packed, name: string, loc: Location): string {
  const s = shapeAt(data, name, loc);
  if (!s) return "";
  let xMin = Infinity,
    xMax = -Infinity;
  for (const c of s.contours) for (let i = 0; i < c.on.length; i++) {
    xMin = Math.min(xMin, c.pts[i * 2]);
    xMax = Math.max(xMax, c.pts[i * 2]);
  }
  const w = Math.max(s.advance, xMax - xMin, 1);
  const dx = Math.round((1000 - (xMax + xMin)) / 2);
  return `<svg viewBox="0 0 1000 1000" aria-hidden="true" data-w="${w}"><path transform="translate(${dx} 800) scale(1 -1)" d="${shapePath(s)}"/></svg>`;
}
