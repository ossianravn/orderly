// The Construction panels: real outlines at a location, with the rule each one shows marked.
// Pure functions returning SVG markup, so the build renders them and the browser redraws them.
import { bounds, numberAt, shapeAt, shapePath, type Location, type Packed, type Shape } from "./glyphs";

export const TOP = 900;
export const HEIGHT = 1200;
const PAD = 40;
const Y = (y: number) => Math.round((TOP - y) * 10) / 10;
const n0 = (v: number) => String(Math.round(v));

export interface Panel {
  w: number;
  body: string;
  facts: [string, string][];
}

interface Placed {
  name: string;
  s: Shape;
  x: number;
}

function lay(data: Packed, names: string[], loc: Location, gap = 90): { items: Placed[]; w: number } {
  let x = PAD;
  const items: Placed[] = [];
  for (const name of names) {
    const s = shapeAt(data, name, loc);
    if (!s) continue;
    items.push({ name, s, x });
    x += s.advance + gap;
  }
  return { items, w: x - gap + PAD };
}

const path = (p: Placed, cls: string, filter?: (part: string | null) => boolean) =>
  `<path class="${cls}" transform="translate(${n0(p.x)} ${TOP}) scale(1 -1)" d="${shapePath(p.s, 0, filter)}"/>`;

const hline = (y: number, w: number, cls = "m") => `<line class="${cls}" x1="0" x2="${n0(w)}" y1="${Y(y)}" y2="${Y(y)}"/>`;

const text = (x: number, y: number, s: string, anchor = "middle", cls = "t") =>
  `<text class="${cls}" x="${n0(x)}" y="${Y(y)}" text-anchor="${anchor}">${s}</text>`;

/** Metric lines with their values at the right edge. */
function metrics(data: Packed, loc: Location, w: number, which: ("base" | "x" | "cap")[]): string {
  const xh = numberAt(data, "xHeight", loc);
  const lines: [number, string][] = [];
  if (which.includes("cap")) lines.push([data.metrics.capHeight, n0(data.metrics.capHeight)]);
  if (which.includes("x")) lines.push([xh, n0(xh)]);
  if (which.includes("base")) lines.push([0, "0"]);
  return lines.map(([y, s]) => hline(y, w) + text(w - 8, y + 18, s, "end", "t dim")).join("");
}

function dimension(x0: number, x1: number, y: number, label: string): string {
  const t = 22;
  return (
    `<path class="mk" d="M${n0(x0)} ${Y(y)}H${n0(x1)}M${n0(x0)} ${Y(y - t)}V${Y(y + t)}M${n0(x1)} ${Y(y - t)}V${Y(y + t)}"/>` +
    text((x0 + x1) / 2, y + 40, label, "middle", "t mark")
  );
}

function partBox(p: Placed, part: string) {
  const c = p.s.contours.find((k) => k.part === part);
  if (!c) return null;
  const b = bounds({ ...p.s, contours: [c] });
  return { xMin: b.xMin + p.x, xMax: b.xMax + p.x, yMin: b.yMin, yMax: b.yMax };
}

function circle(b: { xMin: number; xMax: number; yMin: number; yMax: number }, centre = true): string {
  const cx = (b.xMin + b.xMax) / 2;
  const cy = (b.yMin + b.yMax) / 2;
  const r = (b.xMax - b.xMin) / 2;
  const plus = centre
    ? `<path class="mk" d="M${n0(cx - 24)} ${Y(cy)}H${n0(cx + 24)}M${n0(cx)} ${Y(cy - 24)}V${Y(cy + 24)}"/>`
    : "";
  return `<circle class="mk" cx="${n0(cx)}" cy="${Y(cy)}" r="${n0(r)}"/>${plus}`;
}

/** Straight segments between two on-curve points, as [x0, y0, x1, y1] in drawing units. */
function segments(p: Placed, keep: (part: string | null) => boolean) {
  const out: [number, number, number, number][] = [];
  for (const c of p.s.contours) {
    if (!keep(c.part)) continue;
    const n = c.on.length;
    for (let i = 0; i < n; i++) {
      const j = (i + 1) % n;
      if (!c.on[i] || !c.on[j]) continue;
      out.push([c.pts[i * 2] + p.x, c.pts[i * 2 + 1], c.pts[j * 2] + p.x, c.pts[j * 2 + 1]]);
    }
  }
  return out;
}

const seg = ([x0, y0, x1, y1]: number[]) => `<path class="cut" d="M${n0(x0)} ${Y(y0)}L${n0(x1)} ${Y(y1)}"/>`;

type Draw = (data: Packed, loc: Location) => Panel;

const compass: Draw = (data, loc) => {
  const { items, w } = lay(data, ["O", "o"], loc, 120);
  let body = metrics(data, loc, w, ["base", "x", "cap"]);
  const facts: [string, string][] = [];
  for (const p of items) {
    body += path(p, "g");
    const b = partBox(p, "round") ?? partBox(p, "bowl");
    if (!b) continue;
    body += circle(b);
    const kind = p.name === p.name.toUpperCase() ? "Capital" : "Lowercase";
    facts.push([kind, `${n0(b.xMax - b.xMin)} × ${n0(b.yMax - b.yMin)}`]);
  }
  return { w, body, facts };
};

const stem: Draw = (data, loc) => {
  const { items, w } = lay(data, ["H", "n"], loc, 110);
  let body = metrics(data, loc, w, ["base", "x", "cap"]);
  for (const p of items) {
    body += path(p, "g");
    const b = partBox(p, "stem");
    if (b) body += dimension(b.xMin, b.xMax, b.yMax + 70, n0(b.xMax - b.xMin));
  }
  const facts: [string, string][] = [
    ["Capital stem", n0(numberAt(data, "capStem", loc))],
    ["Lowercase stem", n0(numberAt(data, "stem", loc))],
    ["Bar", n0(numberAt(data, "bar", loc))],
  ];
  return { w, body, facts };
};

const cuts: Draw = (data, loc) => {
  const { items, w } = lay(data, ["c", "e", "s"], loc, 70);
  let body = metrics(data, loc, w, ["base", "x"]);
  let count = 0;
  for (const p of items) {
    body += path(p, "g");
    for (const s of segments(p, (part) => part !== "stem" && part !== "bar")) {
      if (Math.abs(s[0] - s[2]) < 1 && Math.abs(s[1] - s[3]) > 20) {
        body += seg(s);
        count += 1;
      }
    }
  }
  return { w, body, facts: [["Vertical cuts", String(count)]] };
};

const apexes: Draw = (data, loc) => {
  const { items, w } = lay(data, ["A", "v"], loc, 100);
  let body = metrics(data, loc, w, ["base", "x", "cap"]);
  const facts: [string, string][] = [];
  for (const p of items) {
    body += path(p, "g");
    const flat = segments(p, (part) => part === "diagonal" || part === null).filter(
      (s) => Math.abs(s[1] - s[3]) < 1 && Math.abs(s[0] - s[2]) > 10,
    );
    const top = p.name === p.name.toUpperCase();
    const apex = flat.sort((a, b) => (top ? b[1] - a[1] : a[1] - b[1]))[0];
    if (!apex) continue;
    body += seg(apex);
    facts.push([top ? "Capital apex" : "Lowercase apex", n0(Math.abs(apex[2] - apex[0]))]);
  }
  return { w, body, facts };
};

const dots: Draw = (data, loc) => {
  const { items, w } = lay(data, ["i", "j", "period"], loc, 80);
  let body = metrics(data, loc, w, ["base", "x"]);
  let d = 0;
  for (const p of items) {
    body += path(p, "g");
    const b = partBox(p, "dot");
    if (b) {
      body += circle(b, false);
      d = b.xMax - b.xMin;
    }
  }
  return { w, body, facts: [["Dot", n0(d)], ["Stem", n0(numberAt(data, "stem", loc))]] };
};

const joins: Draw = (data, loc) => {
  const { items, w } = lay(data, ["n", "u"], loc, 110);
  let body = metrics(data, loc, w, ["base", "x"]);
  for (const p of items) {
    body += path(p, "g");
    body += path(p, "line", (part) => part === "arch");
  }
  const j = numberAt(data, "join", loc);
  return { w, body, facts: [["Thinned by", `${Math.round(j * 100)} %`]] };
};

const overshoot: Draw = (data, loc) => {
  const { items, w } = lay(data, ["H", "O"], loc, 110);
  let body = metrics(data, loc, w, ["base", "cap"]);
  let over = 0;
  for (const p of items) {
    body += path(p, "g");
    if (p.name !== "O") continue;
    const b = bounds(p.s);
    over = -b.yMin;
    const cx = p.x + (b.xMin + b.xMax) / 2;
    body += text(cx, b.yMax + 40, `+${n0(b.yMax - data.metrics.capHeight)}`, "middle", "t mark");
    body += text(cx, b.yMin - 80, `-${n0(-b.yMin)}`, "middle", "t mark");
  }
  const share = numberAt(data, "overshoot", loc) * 100;
  return { w, body, facts: [["Overshoot", n0(over)], ["Of the height", `${share.toFixed(1)} %`]] };
};

const alternate: Draw = (data, loc) => {
  const { items, w } = lay(data, ["a", "a.ss01"], loc, 140);
  let body = metrics(data, loc, w, ["base", "x"]);
  for (const p of items) {
    body += path(p, "g");
    body += text(p.x + p.s.advance / 2, -150, p.name === "a" ? "a" : "ss01", "middle", "t dim");
  }
  return { w, body, facts: [] };
};

export const panels: Record<string, Draw> = { compass, stem, cuts, apexes, dots, joins, overshoot, alternate };
