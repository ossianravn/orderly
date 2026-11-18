// Copies what the site serves from ../fonts into public/ (git-ignored) and packs the outlines
// for the browser. Runs before dev and build. The font build owns ../fonts; this only reads it.
import { copyFileSync, mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const site = process.cwd();
const fonts = resolve(site, "../fonts");
const out = resolve(site, "public");

const need = [
  ["web/Orderly[opsz,wght].woff2", "fonts/orderly.woff2"],
  ["variable/Orderly[opsz,wght].ttf", "fonts/orderly-variable.ttf"],
];
mkdirSync(resolve(out, "fonts"), { recursive: true });
mkdirSync(resolve(out, "data"), { recursive: true });
for (const [from, to] of need) {
  const src = resolve(fonts, from);
  if (!existsSync(src)) throw new Error(`prepare-fonts: missing ${src}; run the font build first`);
  copyFileSync(src, resolve(out, to));
}

const meta = JSON.parse(readFileSync(resolve(fonts, "data/orderly.json"), "utf8"));
const outlines = JSON.parse(readFileSync(resolve(fonts, "data/outlines.json"), "utf8"));
const order = outlines.masters;

// Packed glyph: u unicode, c category, m [advance, lsb, rsb] per master,
// k contours: p part, o on-curve flags ("1"/"0" per point), x flat [x, y, ...] per master.
const glyphs = {};
for (const g of meta.glyphs) {
  const shape = outlines.glyphs[g.name] ?? {};
  const first = shape[order[0]] ?? [];
  glyphs[g.name] = {
    u: g.unicode,
    ch: g.char,
    c: g.category,
    m: order.map((id) => {
      const m = g.metrics[id];
      return [m.advance, m.lsb, m.rsb];
    }),
    k: first.map((contour, i) => ({
      p: contour.part,
      o: contour.points.map((p) => (p.on ? "1" : "0")).join(""),
      x: order.map((id) => shape[id][i].points.flatMap((p) => [p.x, p.y])),
    })),
  };
}

const packed = {
  version: meta.version,
  unitsPerEm: meta.unitsPerEm,
  metrics: meta.metrics,
  axes: meta.axes,
  masters: order.map((id) => {
    const m = meta.masters.find((x) => x.id === id);
    return { id, name: m.name, wght: m.wght, opsz: m.opsz, numbers: m.numbers };
  }),
  glyphs,
};
writeFileSync(resolve(out, "data/glyphs.json"), JSON.stringify(packed));
console.log(`prepare-fonts: ${Object.keys(glyphs).length} glyphs, version ${meta.version}`);
