// Shared by the build (Astro components) and the browser: the packed glyph data written by
// scripts/prepare-fonts.mjs, interpolation between the six masters, and SVG paths.

export interface Axis {
  tag: string;
  name: string;
  min: number;
  default: number;
  max: number;
  /** user -> design pairs, when the font build exports the axis map */
  map?: [number, number][];
}

export type Numbers = Record<string, number>;

export interface Master {
  id: string;
  name: string;
  wght: number;
  opsz: number;
  numbers: Numbers;
}

export interface Contour {
  p: string | null;
  o: string;
  x: number[][];
}

export interface Glyph {
  u: number | null;
  ch: string | null;
  c: string;
  m: [number, number, number][];
  k: Contour[];
}

export interface Packed {
  version: string;
  unitsPerEm: number;
  metrics: {
    ascender: number;
    capHeight: number;
    descender: number;
    xHeight: Record<string, number>;
  };
  axes: Axis[];
  masters: Master[];
  glyphs: Record<string, Glyph>;
}

export interface Location {
  wght: number;
  opsz: number;
}

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

function mapAxis(axis: Axis | undefined, v: number): number {
  const map = axis?.map;
  if (!map || map.length < 2) return v;
  for (let i = 1; i < map.length; i++) {
    const [u0, d0] = map[i - 1];
    const [u1, d1] = map[i];
    if (v <= u1) return d0 + ((v - u0) / (u1 - u0 || 1)) * (d1 - d0);
  }
  return map[map.length - 1][1];
}

/**
 * Weights of each master at a location. The masters form a full grid (weights x optical sizes),
 * so the font's variation model reduces to piecewise-bilinear interpolation inside one cell.
 */
export function masterWeights(data: Packed, loc: Location): number[] {
  const wAxis = data.axes.find((a) => a.tag === "wght");
  const oAxis = data.axes.find((a) => a.tag === "opsz");
  const ws = [...new Set(data.masters.map((m) => m.wght))].sort((a, b) => a - b);
  const os = [...new Set(data.masters.map((m) => m.opsz))].sort((a, b) => a - b);
  const pick = (stops: number[], v: number, axis: Axis | undefined): [number, number, number] => {
    const x = mapAxis(axis, clamp(v, stops[0], stops[stops.length - 1]));
    const d = stops.map((s) => mapAxis(axis, s));
    for (let i = 1; i < d.length; i++) {
      if (x <= d[i] || i === d.length - 1) {
        const t = d[i] === d[i - 1] ? 0 : (x - d[i - 1]) / (d[i] - d[i - 1]);
        return [stops[i - 1], stops[i], clamp(t, 0, 1)];
      }
    }
    return [stops[0], stops[0], 0];
  };
  const [w0, w1, tw] = pick(ws, loc.wght, wAxis);
  const [o0, o1, to] = os.length > 1 ? pick(os, loc.opsz, oAxis) : [os[0], os[0], 0];
  return data.masters.map((m) => {
    const fw = m.wght === w0 ? 1 - tw : 0;
    const fw1 = m.wght === w1 && w1 !== w0 ? tw : 0;
    const fo = m.opsz === o0 ? 1 - to : 0;
    const fo1 = m.opsz === o1 && o1 !== o0 ? to : 0;
    return (fw + fw1) * (fo + fo1);
  });
}

export function blend(values: number[], weights: number[]): number {
  let s = 0;
  for (let i = 0; i < values.length; i++) s += values[i] * weights[i];
  return s;
}

/** A master number (stem, bar, x-height...) at a location. */
export function numberAt(data: Packed, key: string, loc: Location): number {
  const w = masterWeights(data, loc);
  return blend(
    data.masters.map((m) => m.numbers[key] ?? 0),
    w,
  );
}

export interface Shape {
  advance: number;
  lsb: number;
  rsb: number;
  contours: { part: string | null; on: boolean[]; pts: number[] }[];
}

export function shapeAt(data: Packed, name: string, loc: Location): Shape | null {
  const g = data.glyphs[name];
  if (!g) return null;
  const w = masterWeights(data, loc);
  const mix = (i: number) => blend(g.m.map((m) => m[i]), w);
  return {
    advance: mix(0),
    lsb: mix(1),
    rsb: mix(2),
    contours: g.k.map((c) => {
      const n = c.x[0].length;
      const pts = new Array<number>(n);
      for (let j = 0; j < n; j++) {
        let s = 0;
        for (let m = 0; m < w.length; m++) if (w[m]) s += c.x[m][j] * w[m];
        pts[j] = s;
      }
      return { part: c.p, on: [...c.o].map((f) => f === "1"), pts };
    }),
  };
}

const r1 = (v: number) => Math.round(v * 10) / 10;

/** SVG path data for one contour, in font units (y up). */
export function contourPath(on: boolean[], pts: number[], dx = 0): string {
  const n = on.length;
  if (!n) return "";
  const X = (i: number) => r1(pts[(i % n) * 2] + dx);
  const Y = (i: number) => r1(pts[(i % n) * 2 + 1]);
  let d = `M${X(0)} ${Y(0)}`;
  let i = 1;
  while (i <= n) {
    if (on[i % n]) {
      d += `L${X(i)} ${Y(i)}`;
      i += 1;
    } else {
      d += `C${X(i)} ${Y(i)} ${X(i + 1)} ${Y(i + 1)} ${X(i + 2)} ${Y(i + 2)}`;
      i += 3;
    }
  }
  return d + "Z";
}

export function shapePath(shape: Shape, dx = 0, filter?: (part: string | null) => boolean): string {
  return shape.contours
    .filter((c) => !filter || filter(c.part))
    .map((c) => contourPath(c.on, c.pts, dx))
    .join("");
}

export function bounds(shape: Shape): { xMin: number; xMax: number; yMin: number; yMax: number } {
  let xMin = Infinity,
    xMax = -Infinity,
    yMin = Infinity,
    yMax = -Infinity;
  for (const c of shape.contours) {
    for (let i = 0; i < c.on.length; i++) {
      if (!c.on[i]) continue;
      const x = c.pts[i * 2],
        y = c.pts[i * 2 + 1];
      xMin = Math.min(xMin, x);
      xMax = Math.max(xMax, x);
      yMin = Math.min(yMin, y);
      yMax = Math.max(yMax, y);
    }
  }
  return { xMin, xMax, yMin, yMax };
}

/** opsz the browser would use for text drawn at `px` per em, when optical sizing is auto. */
export function autoOpsz(data: Packed, px: number): number {
  const a = data.axes.find((x) => x.tag === "opsz");
  return a ? clamp(px, a.min, a.max) : 12;
}
